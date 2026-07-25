#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas operaciones de faena (E8 — Mantos Blancos). Contrato en openapi.yaml."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest import operaciones_service

_ERROR_503 = {"error": "Servicio de operaciones temporalmente no disponible"}


def _responder(data, estacion_id: str):
    if data is None:
        if operaciones_service._coords(estacion_id) is None:
            return jsonify({"error": "Estación no encontrada", "estacion_id": estacion_id}), 404
        return jsonify(_ERROR_503), 503
    return jsonify(data)


def register_operaciones_routes(app: Flask) -> None:
    @app.get("/api/public/operaciones/umbrales")
    def public_operaciones_umbrales():
        """Umbrales efectivos del semáforo (defaults + sitio + env)."""
        sitio = (request.args.get("sitio") or "mantos_blancos").strip().lower()
        try:
            return jsonify(operaciones_service.umbrales_publicos(sitio))
        except Exception as exc:
            app.logger.warning("operaciones_umbrales %s error: %s", sitio, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/alertas")
    def public_operaciones_alertas():
        """Alertas por turno (día/noche) de la faena."""
        sitio = (request.args.get("sitio") or "mantos_blancos").strip().lower()
        turno = (request.args.get("turno") or "dia").strip().lower()
        try:
            return jsonify(operaciones_service.alertas_turno(sitio, turno))
        except Exception as exc:
            app.logger.warning("operaciones_alertas %s error: %s", sitio, exc)
            return jsonify(_ERROR_503), 503

    # ---- Paipote: ventilación N/R/M + informe + histórico ----

    @app.get("/api/public/operaciones/paipote/ventilacion")
    def public_paipote_ventilacion():
        """Ventilación operativa N/R/M — corridas 06/18 UTC."""
        from api_rest import ventilacion_service

        horizonte = (request.args.get("horizonte") or "horaria").strip().lower()
        forzar = (request.args.get("forzar") or "").strip().lower() in ("1", "true", "yes")
        estacion = (request.args.get("estacion") or "paipote").strip().lower()
        try:
            data = ventilacion_service.ventilacion_horizonte(
                horizonte=horizonte, estacion_id=estacion, forzar=forzar
            )
            if data is None:
                return jsonify({"error": "Estación no encontrada", "estacion_id": estacion}), 404
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("paipote_ventilacion error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/paipote/paquete")
    def public_paipote_paquete():
        """Paquete completo (72h + 14d + 30-90 + tramos 3h + sinóptica)."""
        from api_rest import ventilacion_service

        forzar = (request.args.get("forzar") or "").strip().lower() in ("1", "true", "yes")
        try:
            data = ventilacion_service.construir_paquete("paipote", forzar_recalculo=forzar)
            if data is None:
                return jsonify(_ERROR_503), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("paipote_paquete error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/paipote/historico")
    def public_paipote_historico():
        """Histórico diario Archive (~7 años) para estudios."""
        from api_rest import ventilacion_service

        anios = max(1, min(request.args.get("anios", default=7, type=int) or 7, 10))
        estacion = (request.args.get("estacion") or "paipote").strip().lower()
        try:
            data = ventilacion_service.historico_diario(estacion, anios=anios)
            if data is None:
                return jsonify({"error": "Estación no encontrada"}), 404
            if not data.get("filas"):
                return jsonify(data), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("paipote_historico error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/paipote/olas-calor")
    def public_paipote_olas_calor():
        """Olas de calor otoño/invierno (P90 climatológico 7 años)."""
        from api_rest import olas_calor_service

        estacion = (request.args.get("estacion") or "paipote").strip().lower()
        estacion_ano = (request.args.get("estacion_ano") or "otono").strip().lower()
        anios = max(3, min(request.args.get("anios", default=7, type=int) or 7, 10))
        try:
            data = olas_calor_service.analizar_olas_calor(
                estacion_id=estacion, estacion_ano=estacion_ano, anios=anios
            )
            if data is None:
                return jsonify({"error": "Estación no encontrada"}), 404
            if data.get("error") == "sin_historico":
                return jsonify(data), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("paipote_olas_calor error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/paipote/satelite")
    def public_paipote_satelite():
        """GOES VIS / IR / WV + diagnóstico incursión nubosa valle."""
        from api_rest import satelite_atmos_service

        estacion = (request.args.get("estacion") or "paipote").strip().lower()
        raw = (request.args.get("bandas") or "vis,ir,wv").strip().lower()
        bandas = [b.strip() for b in raw.split(",") if b.strip()]
        try:
            data = satelite_atmos_service.satelite_atmos(estacion, bandas=bandas)
            if data is None:
                return jsonify({"error": "Estación no encontrada"}), 404
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("paipote_satelite error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/conjunto/catalogo")
    def public_conjunto_catalogo():
        """Catálogo de series activables (panel variables en conjunto)."""
        from api_rest import variables_conjunto_service

        return jsonify(variables_conjunto_service.catalogo_publico())

    @app.get("/api/public/operaciones/<estacion_id>/conjunto")
    def public_operaciones_conjunto(estacion_id: str):
        """Series horarias multi-variable (Combo extensible)."""
        from api_rest import variables_conjunto_service

        horas = max(6, min(request.args.get("horas", default=72, type=int) or 72, 168))
        raw = (request.args.get("series") or "").strip()
        series = [s.strip() for s in raw.split(",") if s.strip()] or None
        try:
            data = variables_conjunto_service.armar_conjunto(
                estacion_id, horas=horas, series=series
            )
        except Exception as exc:
            app.logger.warning("conjunto %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/operaciones/paipote/informe")
    def public_paipote_informe():
        """Informe HTML (imprimible) o PDF (?formato=pdf)."""
        from flask import Response

        from api_rest import informe_paipote_service

        formato = (request.args.get("formato") or "html").strip().lower()
        try:
            if formato == "pdf":
                raw = informe_paipote_service.construir_informe_pdf_bytes("paipote")
                if not raw:
                    return jsonify(_ERROR_503), 503
                return Response(
                    raw,
                    mimetype="application/pdf",
                    headers={
                        "Content-Disposition": "attachment; filename=informe_paipote_ventilacion.pdf"
                    },
                )
            html_doc = informe_paipote_service.construir_informe_html("paipote")
            if not html_doc:
                return jsonify(_ERROR_503), 503
            return Response(
                html_doc,
                mimetype="text/html; charset=utf-8",
                headers={
                    "Content-Disposition": "inline; filename=informe_paipote_ventilacion.html"
                },
            )
        except Exception as exc:
            app.logger.warning("paipote_informe error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.post("/api/cron/paipote/ventilacion")
    def cron_paipote_ventilacion():
        """Recálculo forzado corrida (proteger con CRON_SECRET)."""
        from api_rest import ventilacion_service

        token = request.args.get("token") or request.headers.get("X-Cron-Token") or ""
        import os

        secret = (os.getenv("CRON_SECRET") or "").strip()
        if secret and token != secret:
            return jsonify({"error": "no autorizado"}), 401
        try:
            return jsonify(ventilacion_service.sincronizar_corrida("paipote"))
        except Exception as exc:
            app.logger.warning("cron_paipote_ventilacion error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/<estacion_id>/ventanas")
    def public_operaciones_ventanas(estacion_id: str):
        """Serie horaria de ventanas operacionales (semáforo por actividad)."""
        horas = max(1, min(request.args.get("horas", default=48, type=int), 168))
        try:
            data = operaciones_service.ventanas_operacionales(estacion_id, horas)
        except Exception as exc:
            app.logger.warning("operaciones_ventanas %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)
