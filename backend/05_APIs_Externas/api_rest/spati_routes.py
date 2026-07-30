#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas públicas SPATI (izaje 72 h × 15 min). Contrato en openapi.yaml."""

from __future__ import annotations

from flask import Flask, jsonify, request

_ERROR_503 = {"error": "Servicio SPATI temporalmente no disponible"}


def register_spati_routes(app: Flask) -> None:
    @app.get("/api/public/spati/sitios")
    def public_spati_sitios():
        from api_rest.spati import listar_sitios

        solo = (request.args.get("alta_montana") or "").strip().lower() in ("1", "true", "yes")
        return jsonify({"sitios": listar_sitios(solo_alta_montana=solo), "n": len(listar_sitios(solo_alta_montana=solo))})

    @app.get("/api/public/spati/sitios/<sitio_id>")
    def public_spati_sitio(sitio_id: str):
        from api_rest.spati import get_sitio

        s = get_sitio(sitio_id)
        if not s:
            return jsonify({"error": "Sitio no encontrado", "sitio_id": sitio_id}), 404
        return jsonify(s)

    @app.get("/api/public/spati/<sitio_id>/pronostico")
    def public_spati_pronostico(sitio_id: str):
        """Pronóstico 72 h / 15 min con física, MOS (si hay) y alertas 0–3."""
        from api_rest.spati import run_spati

        try:
            data = run_spati(sitio_id)
        except Exception as exc:
            app.logger.warning("spati_pronostico %s: %s", sitio_id, exc)
            return jsonify({**_ERROR_503, "detalle": str(exc)}), 503
        if data.get("error") == "sitio_no_encontrado":
            return jsonify(data), 404
        if data.get("error"):
            return jsonify(data), 503
        return jsonify(data)

    @app.post("/api/public/spati/<sitio_id>/pronostico")
    def public_spati_pronostico_con_dron(sitio_id: str):
        """Igual que GET, pero acepta JSON de perfil de dron en el body."""
        from api_rest.spati import run_spati

        body = request.get_json(silent=True) or {}
        perfil = body.get("perfil_dron") or body.get("perfil")
        tau = float(body.get("tau_horas") or 6.0)
        try:
            data = run_spati(sitio_id, perfil_dron=perfil, tau_dron_h=tau)
        except Exception as exc:
            app.logger.warning("spati_pronostico_post %s: %s", sitio_id, exc)
            return jsonify(_ERROR_503), 503
        if data.get("error") == "sitio_no_encontrado":
            return jsonify(data), 404
        if data.get("error"):
            return jsonify(data), 503
        return jsonify(data)

    @app.post("/api/public/spati/physics/extrapolar")
    def public_spati_physics_extrapolar():
        """Utilidad: extrapolar un valor de viento a altura de pluma."""
        from api_rest.spati.physics_engine import PhysicsEngine

        body = request.get_json(silent=True) or {}
        try:
            pe = PhysicsEngine()
            v = pe.extrapolar_altura(
                float(body["v_ref"]),
                float(body["h_objetivo"]),
                float(body["z0"]),
                float(body.get("h_ref") or 10),
            )
            return jsonify({"v_kmh": round(v, 2)})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/public/spati/physics/alta-montana")
    def public_spati_physics_alta_montana():
        """Densidad ISA, FR, velocidad equivalente y GF por altitud/sitio."""
        from api_rest.spati.high_altitude_engine import HighAltitudeEngine
        from api_rest.spati.sitios_catalogo import get_sitio

        body = request.get_json(silent=True) or {}
        ha = HighAltitudeEngine()
        try:
            sitio = get_sitio(body.get("sitio_id")) if body.get("sitio_id") else None
            alt = float(body.get("altitud_msnm") or (sitio or {}).get("altitud_msnm") or 0)
            temp = body.get("temp_celsius")
            params = ha.parametros_sitio(alt)
            rho_real = None
            if temp is not None:
                rho_real = ha.calcular_densidad_altitud(alt, float(temp))
                params["rho_real_kg_m3"] = round(rho_real, 4)
                params["factor_reduccion_real"] = round(
                    ha.factor_reduccion_densidad(rho_real), 4
                )
                params["v_equiv_36_real_kmh"] = round(
                    ha.umbral_velocidad_equivalente(36.0, rho_real), 1
                )
            tipo = (sitio or {}).get("tipo_terreno_eolico") or body.get("tipo_terreno_eolico") or "rajo_minero"
            zona = (sitio or {}).get("zona_climatica") or body.get("zona_climatica") or "altiplano"
            params["gust_factor"] = ha.factor_rafaga_terreno(str(tipo), str(zona))
            params["altitud_msnm"] = alt
            if sitio:
                params["sitio_id"] = sitio["sitio_id"]
                params["nombre"] = sitio["nombre"]
                params["z0_terreno"] = sitio["z0_terreno"]
                params["requiere_autorizacion_dgac"] = sitio.get("requiere_autorizacion_dgac")
            return jsonify(params)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/public/spati/<sitio_id>/umbrales")
    def public_spati_umbrales(sitio_id: str):
        """M9: umbrales efectivos de izaje (default + override por faena/cliente)."""
        from api_rest.spati import get_sitio
        from api_rest.spati.umbrales_service import alertas_destino_publico, umbrales_efectivos

        s = get_sitio(sitio_id)
        if not s:
            return jsonify({"error": "Sitio no encontrado", "sitio_id": sitio_id}), 404
        sid = s.get("sitio_id") or sitio_id
        # Detalle (emails/webhook) si Bearer o ?detalle=1 (UI edición autenticada)
        auth = request.headers.get("Authorization") or ""
        detallado = auth.startswith("Bearer ") or (
            (request.args.get("detalle") or "").strip().lower() in ("1", "true", "yes")
        )
        return jsonify(
            {
                "sitio_id": sid,
                "nombre": s.get("nombre"),
                "umbrales": umbrales_efectivos(sid),
                "alertas": alertas_destino_publico(sid, detallado=detallado),
            }
        )

    @app.put("/api/public/spati/<sitio_id>/umbrales")
    def put_spati_umbrales(sitio_id: str):
        """M9: guardar override umbrales y/o alertas_destino. Token CRON o Bearer."""
        import os

        from api_rest.spati import get_sitio
        from api_rest.spati.umbrales_service import (
            alertas_destino_publico,
            guardar_alertas_destino,
            guardar_umbrales_local,
            umbrales_efectivos,
        )

        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        cron = (os.getenv("CRON_SECRET") or "").strip()
        auth = request.headers.get("Authorization") or ""
        if cron and secret != cron and not auth.startswith("Bearer "):
            return jsonify({"error": "No autorizado"}), 401
        s = get_sitio(sitio_id)
        if not s:
            return jsonify({"error": "Sitio no encontrado", "sitio_id": sitio_id}), 404
        body = request.get_json(silent=True) or {}
        sid = s.get("sitio_id") or sitio_id
        try:
            umb_out = None
            alertas_out = None
            if "alertas" in body and isinstance(body.get("alertas"), dict):
                alertas_out = guardar_alertas_destino(sid, body["alertas"])
            umb_in = body.get("umbrales")
            if umb_in is None and "alertas" not in body:
                umb_in = body
            if isinstance(umb_in, dict) and any(
                k in umb_in
                for k in (
                    "rojo_min_kmh",
                    "verde_max_kmh",
                    "amarillo",
                    "naranja",
                    "flag_critico_kmh",
                )
            ):
                umb_out = guardar_umbrales_local(sid, umb_in)
            return jsonify(
                {
                    "sitio_id": sid,
                    "umbrales": umb_out or umbrales_efectivos(sid),
                    "alertas": alertas_destino_publico(
                        sid, detallado=True
                    )
                    if alertas_out is not None
                    else alertas_destino_publico(sid, detallado=auth.startswith("Bearer ")),
                    "ok": True,
                }
            )
        except Exception as exc:
            app.logger.warning("put umbrales %s: %s", sid, exc)
            return jsonify(_ERROR_503), 503
    @app.post("/api/cron/spati/alertas")
    def cron_spati_alertas():
        """M9: evalúa niveles SPATI y notifica transiciones (CRON_SECRET)."""
        import os

        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        if not secret or secret != os.getenv("CRON_SECRET"):
            if os.getenv("CRON_SECRET"):
                return jsonify({"error": "No autorizado"}), 401
        solo = (request.args.get("sitio") or "").strip() or None
        forzar = (request.args.get("forzar") or "").strip().lower() in ("1", "true", "yes")
        try:
            from api_rest.spati_alert_job import evaluar_sitios, evaluar_y_notificar

            if solo:
                return jsonify(evaluar_y_notificar(solo, forzar=forzar))
            return jsonify(evaluar_sitios(forzar=forzar))
        except Exception as exc:
            app.logger.warning("cron spati alertas: %s", exc)
            return jsonify(_ERROR_503), 503
