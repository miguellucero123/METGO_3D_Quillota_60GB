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

    # ---- Faena genérica (Paipote / Mantos) + aliases /paipote/* ----

    def _faena_o_404(faena_id: str):
        from api_rest.faena_catalogo import get_faena

        f = get_faena(faena_id)
        if not f:
            return None, (jsonify({"error": "Faena no encontrada", "faena_id": faena_id}), 404)
        return f, None

    @app.get("/api/public/operaciones/faenas")
    def public_operaciones_faenas():
        from api_rest.faena_catalogo import listar_faenas

        return jsonify({"faenas": listar_faenas()})

    @app.get("/api/public/operaciones/faena/<faena_id>/ventilacion")
    def public_faena_ventilacion(faena_id: str):
        from api_rest import ventilacion_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        horizonte = (request.args.get("horizonte") or "horaria").strip().lower()
        forzar = (request.args.get("forzar") or "").strip().lower() in ("1", "true", "yes")
        estacion = (request.args.get("estacion") or f["estacion_ancla"]).strip().lower()
        try:
            data = ventilacion_service.ventilacion_horizonte(
                horizonte=horizonte, estacion_id=estacion, forzar=forzar
            )
            if data is None:
                return jsonify({"error": "Estación no encontrada", "estacion_id": estacion}), 404
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("faena_ventilacion %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/paquete")
    def public_faena_paquete(faena_id: str):
        from api_rest import ventilacion_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        forzar = (request.args.get("forzar") or "").strip().lower() in ("1", "true", "yes")
        estacion = (request.args.get("estacion") or f["estacion_ancla"]).strip().lower()
        try:
            data = ventilacion_service.construir_paquete(estacion, forzar_recalculo=forzar)
            if data is None:
                return jsonify(_ERROR_503), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("faena_paquete %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/historico")
    def public_faena_historico(faena_id: str):
        from api_rest import ventilacion_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        anios = max(1, min(request.args.get("anios", default=7, type=int) or 7, 10))
        estacion = (request.args.get("estacion") or f["estacion_ancla"]).strip().lower()
        try:
            data = ventilacion_service.historico_diario(estacion, anios=anios)
            if data is None:
                return jsonify({"error": "Estación no encontrada"}), 404
            if not data.get("filas"):
                return jsonify(data), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("faena_historico %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/olas-calor")
    def public_faena_olas_calor(faena_id: str):
        from api_rest import olas_calor_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        estacion = (request.args.get("estacion") or f["estacion_ancla"]).strip().lower()
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
            app.logger.warning("faena_olas_calor %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/satelite")
    def public_faena_satelite(faena_id: str):
        from api_rest import satelite_atmos_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        estacion = (request.args.get("estacion") or f["estacion_ancla"]).strip().lower()
        raw = (request.args.get("bandas") or "vis,ir,wv").strip().lower()
        bandas = [b.strip() for b in raw.split(",") if b.strip()]
        try:
            data = satelite_atmos_service.satelite_atmos(estacion, bandas=bandas)
            if data is None:
                return jsonify({"error": "Estación no encontrada"}), 404
            data["faena"] = f["id"]
            data["faena_nombre"] = f["nombre"]
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("faena_satelite %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/paipote/ventilacion")
    def public_paipote_ventilacion():
        """Alias legacy → faena/paipote/ventilacion."""
        return public_faena_ventilacion("paipote")

    @app.get("/api/public/operaciones/paipote/paquete")
    def public_paipote_paquete():
        return public_faena_paquete("paipote")

    @app.get("/api/public/operaciones/paipote/historico")
    def public_paipote_historico():
        return public_faena_historico("paipote")

    @app.get("/api/public/operaciones/paipote/olas-calor")
    def public_paipote_olas_calor():
        return public_faena_olas_calor("paipote")

    @app.get("/api/public/operaciones/paipote/satelite")
    def public_paipote_satelite():
        return public_faena_satelite("paipote")

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

    @app.post("/api/cron/faena/<faena_id>/ventilacion")
    def cron_faena_ventilacion(faena_id: str):
        from api_rest import ventilacion_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        token = request.args.get("token") or request.headers.get("X-Cron-Token") or ""
        import os

        secret = (os.getenv("CRON_SECRET") or "").strip()
        if secret and token != secret:
            return jsonify({"error": "no autorizado"}), 401
        try:
            return jsonify(ventilacion_service.sincronizar_corrida(f["estacion_ancla"]))
        except Exception as exc:
            app.logger.warning("cron_faena_ventilacion %s error: %s", faena_id, exc)
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
