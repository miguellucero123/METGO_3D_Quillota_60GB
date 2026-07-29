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

        raw = (request.args.get("incluir_izaje") or "1").strip().lower()
        incluir = raw not in ("0", "false", "no")
        return jsonify({"faenas": listar_faenas(incluir_izaje=incluir)})

    @app.get("/api/public/operaciones/faena/<faena_id>/paquete-ambiental")
    def public_faena_paquete_ambiental(faena_id: str):
        """Meteo + aire + nieve + viento + flags operativos (M1–M3)."""
        from api_rest import paquete_ambiental_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        horas = max(6, min(request.args.get("horas", default=72, type=int) or 72, 168))
        incluir_obs = (request.args.get("incluir_observado") or "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        try:
            data = paquete_ambiental_service.construir_paquete_ambiental(
                f["id"], horas=horas
            )
            if data is None:
                return jsonify({**_ERROR_503, "detalle": "sin_paquete"}), 503
            if data.get("error") == "sin_coordenadas":
                return jsonify(data), 422
            # Paquete degradado / lastgood: 200 con aviso (no 503)
            if incluir_obs:
                try:
                    from api_rest import modelo_vs_observado_service

                    data["modelo_vs_observado"] = (
                        modelo_vs_observado_service.reporte_modelo_vs_observado(
                            f["id"], dias=14
                        )
                    )
                except Exception as exc_obs:
                    data["modelo_vs_observado"] = {"error": str(exc_obs)}
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("faena_paquete_ambiental %s error: %s", faena_id, exc)
            return jsonify({**_ERROR_503, "detalle": str(exc)}), 503

    @app.get("/api/public/operaciones/umbrales-operativos")
    def public_umbrales_operativos():
        """Umbrales M3 izaje/caminos/botaderos (defaults + factor env)."""
        from api_rest.umbrales_faena_service import umbrales_efectivos

        return jsonify(
            {
                "umbrales": umbrales_efectivos(),
                "actividades": ["izaje", "caminos", "botaderos"],
                "nota": "Aplicados en paquete-ambiental.flags / operaciones",
            }
        )

    @app.get("/api/public/operaciones/faena/<faena_id>/estaciones-area")
    def public_faena_estaciones_area(faena_id: str):
        """Puntos meteo por área (catálogo + Supabase M4)."""
        from api_rest.faena_catalogo import estaciones_area_faena

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        pts = estaciones_area_faena(f["id"])
        return jsonify(
            {
                "faena_id": f["id"],
                "nombre": f.get("nombre"),
                "estaciones_area": pts,
                "n": len(pts),
            }
        )

    @app.post("/api/cron/faena/estaciones-area")
    def cron_faena_estaciones_area():
        """Sync catálogo → Supabase faena_estaciones_area (CRON_SECRET)."""
        import os

        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        if not secret or secret != os.getenv("CRON_SECRET"):
            # Permitir en local sin secret si no hay CRON_SECRET configurado
            if os.getenv("CRON_SECRET"):
                return jsonify({"error": "No autorizado"}), 401
        solo = (request.args.get("faena") or "").strip() or None
        try:
            from api_rest.integracion import estaciones_area_store, estaciones_catalog_store

            area = estaciones_area_store.sincronizar_desde_catalogo(solo_faena=solo)
            pub = estaciones_catalog_store.sincronizar_estaciones_publicas(solo_faena=solo)
            return jsonify({"estaciones_area": area, "estaciones_publicas": pub})
        except Exception as exc:
            app.logger.warning("cron estaciones-area: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.post("/api/cron/faena/sync-estaciones")
    def cron_faena_sync_estaciones():
        """M8: sync catálogo → public.estaciones (FK aire_registros)."""
        import os

        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        if not secret or secret != os.getenv("CRON_SECRET"):
            if os.getenv("CRON_SECRET"):
                return jsonify({"error": "No autorizado"}), 401
        solo = (request.args.get("faena") or "").strip() or None
        try:
            from api_rest.integracion import estaciones_catalog_store

            return jsonify(
                estaciones_catalog_store.sincronizar_estaciones_publicas(solo_faena=solo)
            )
        except Exception as exc:
            app.logger.warning("cron sync-estaciones: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/informe")
    def public_faena_informe(faena_id: str):
        """Informe ambiental: CSV o PDF (documentos) · HTML vista previa."""
        from flask import Response

        from api_rest import informe_faena_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        formato = (request.args.get("formato") or "pdf").strip().lower()
        try:
            if formato == "csv":
                csv_doc = informe_faena_service.construir_informe_csv(f["id"])
                if not csv_doc:
                    return jsonify(_ERROR_503), 503
                return Response(
                    csv_doc.encode("utf-8"),
                    mimetype="text/csv; charset=utf-8",
                    headers={
                        "Content-Disposition": (
                            f"attachment; filename=informe_{f['id']}_ambiental.csv"
                        )
                    },
                )
            if formato == "pdf":
                raw = informe_faena_service.construir_informe_pdf_bytes(f["id"])
                if not raw:
                    return jsonify(_ERROR_503), 503
                return Response(
                    raw,
                    mimetype="application/pdf",
                    headers={
                        "Content-Disposition": (
                            f"attachment; filename=informe_{f['id']}_ambiental.pdf"
                        )
                    },
                )
            if formato not in ("html", "htm"):
                return jsonify(
                    {
                        "error": "formato_no_soportado",
                        "formatos": ["csv", "pdf", "html"],
                        "nota": "Documentos oficiales: csv y pdf",
                    }
                ), 400
            html_doc = informe_faena_service.construir_informe_html(f["id"])
            if not html_doc:
                return jsonify(_ERROR_503), 503
            return Response(
                html_doc,
                mimetype="text/html; charset=utf-8",
                headers={
                    "Content-Disposition": (
                        f"inline; filename=informe_{f['id']}_ambiental.html"
                    )
                },
            )
        except Exception as exc:
            app.logger.warning("faena_informe %s error: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/modelo-vs-observado")
    def public_faena_modelo_vs_observado(faena_id: str):
        """M5: sesgo modelo vs observado (JSON o CSV)."""
        from flask import Response

        from api_rest import informe_faena_service, modelo_vs_observado_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        dias = max(3, min(request.args.get("dias", default=14, type=int) or 14, 60))
        formato = (request.args.get("formato") or "json").strip().lower()
        try:
            if formato == "csv":
                csv_doc = informe_faena_service.construir_mvo_csv(f["id"], dias=dias)
                if not csv_doc:
                    return jsonify(_ERROR_503), 503
                return Response(
                    csv_doc.encode("utf-8"),
                    mimetype="text/csv; charset=utf-8",
                    headers={
                        "Content-Disposition": (
                            f"attachment; filename=mvo_{f['id']}.csv"
                        )
                    },
                )
            data = modelo_vs_observado_service.reporte_modelo_vs_observado(
                f["id"], dias=dias
            )
            if data is None:
                return jsonify(_ERROR_503), 503
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("modelo_vs_observado %s: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/operaciones/faena/<faena_id>/observado-status")
    def public_faena_observado_status(faena_id: str):
        """M7 readiness: conteos MVO + enlaces CSV/PDF."""
        from api_rest import m7_observado_service

        f, err = _faena_o_404(faena_id)
        if err:
            return err
        dias = max(3, min(request.args.get("dias", default=14, type=int) or 14, 60))
        try:
            return jsonify(m7_observado_service.estado_observado_faena(f["id"], dias=dias))
        except Exception as exc:
            app.logger.warning("observado-status %s: %s", faena_id, exc)
            return jsonify(_ERROR_503), 503

    @app.post("/api/cron/faena/demo-observado")
    def cron_faena_demo_observado():
        """M7: carga demo observado+modelo+IoT (CRON_SECRET si está definido)."""
        import os

        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        if os.getenv("CRON_SECRET") and (
            not secret or secret != os.getenv("CRON_SECRET")
        ):
            return jsonify({"error": "No autorizado"}), 401
        solo = (request.args.get("faena") or "").strip() or None
        dias = max(3, min(request.args.get("dias", default=7, type=int) or 7, 30))
        try:
            from api_rest import m7_observado_service

            return jsonify(
                m7_observado_service.activar_demo_observado(solo, dias=dias)
            )
        except Exception as exc:
            app.logger.warning("demo-observado: %s", exc)
            return jsonify(_ERROR_503), 503

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
