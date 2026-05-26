#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 4-5 — integración módulos 01-11."""

from __future__ import annotations

from flask import Flask, g, jsonify, request

from api_rest.auth_routes import auth_required
from api_rest import services
from api_rest.integracion.estado_integracion import estado_modulos
from api_rest.integracion import (
    alertas_store,
    meteo_store,
    reportes_bridge,
    etl_sync,
    agricola_extra,
    notificaciones,
    drones_bridge,
    deploy_info,
    docs_index,
    testing_info,
    ml_registry,
)
from api_rest import ml_services


def register_fase4_routes(app: Flask) -> None:
    @app.get("/api/integracion/estado")
    def integracion_estado():
        """Público: grado de integración por módulo (checks dinámicos)."""
        return jsonify(estado_modulos())

    @app.get("/api/agricola/<estacion_id>/avanzado")
    @auth_required
    def agricola_avanzado(estacion_id: str):
        return jsonify(services.reporte_agricola_avanzado(estacion_id))

    @app.get("/api/agricola/cultivos")
    @auth_required
    def agricola_cultivos():
        return jsonify(agricola_extra.listar_cultivos())

    @app.get("/api/agricola/<estacion_id>/riego")
    @auth_required
    def agricola_riego(estacion_id: str):
        cultivo = request.args.get("cultivo", "palto")
        resumen = services.resumen_meteo(estacion_id)
        return jsonify(agricola_extra.recomendacion_riego(resumen, cultivo))

    @app.get("/api/agricola/<estacion_id>/economico")
    @auth_required
    def agricola_economico(estacion_id: str):
        return jsonify(agricola_extra.analisis_economico(estacion_id))

    @app.get("/api/alertas/historial")
    @auth_required
    def alertas_historial():
        estacion = request.args.get("estacion")
        limite = request.args.get("limite", 50, type=int)
        return jsonify(alertas_store.listar_historial(estacion, limite))

    @app.get("/api/datos/meteo/store")
    @auth_required
    def datos_meteo_store():
        return jsonify(meteo_store.estadisticas_store())

    @app.get("/api/datos/fuentes")
    @auth_required
    def datos_fuentes():
        return jsonify(etl_sync.fuentes_datos())

    @app.post("/api/datos/etl/sync")
    @auth_required
    def datos_etl_sync():
        body = request.get_json(silent=True) or {}
        dias = body.get("dias", 14)
        incluir_csv = body.get("incluir_csv", True)
        return jsonify(
            etl_sync.sincronizar_estaciones(
                dias=int(dias), incluir_csv=bool(incluir_csv), origen="rest"
            )
        )

    @app.get("/api/datos/etl/status")
    def datos_etl_status():
        """Público: último ETL sin secretos (monitoreo / cron smoke)."""
        m = etl_sync.leer_etl_metrics()
        fuentes = etl_sync.fuentes_datos()
        return jsonify({
            "ultimo": m.get("ultimo"),
            "runs_en_historial": len(m.get("historial") or []),
            "fuentes": {k: v for k, v in fuentes.items() if k != "sqlite_meteo"},
            "sqlite_meteo_presente": bool(fuentes.get("sqlite_meteo")),
        })

    @app.get("/api/reportes/ultimos")
    @auth_required
    def reportes_ultimos():
        limite = request.args.get("limite", 10, type=int)
        return jsonify(reportes_bridge.listar_ultimos_reportes(limite))

    @app.get("/api/reportes/<nombre>")
    @auth_required
    def reporte_detalle(nombre: str):
        return jsonify(reportes_bridge.leer_reporte(nombre))

    @app.get("/api/notificaciones/config")
    @auth_required
    def notif_config_get():
        return jsonify(notificaciones.leer_config())

    @app.put("/api/notificaciones/config")
    @auth_required
    def notif_config_put():
        body = request.get_json(silent=True) or {}
        return jsonify(notificaciones.guardar_config(body))

    @app.post("/api/notificaciones/probar")
    @auth_required
    def notif_probar():
        msg = (request.get_json(silent=True) or {}).get("mensaje", "Prueba METGO")
        return jsonify(notificaciones.enviar_prueba(msg))

    @app.get("/api/iot/drones")
    @auth_required
    def iot_drones():
        return jsonify(drones_bridge.resumen_drones())

    @app.get("/api/iot/satelital")
    @auth_required
    def iot_satelital():
        return jsonify(drones_bridge.info_satelital())

    @app.get("/api/ml/registry")
    @auth_required
    def ml_registry_get():
        return jsonify(ml_registry.leer_registro())

    @app.post("/api/ml/registry/sync")
    @auth_required
    def ml_registry_sync():
        return jsonify(ml_registry.sincronizar_registro())

    @app.post("/api/ml/predict/batch")
    @auth_required
    def ml_predict_batch():
        body = request.get_json(silent=True) or {}
        vars_ = body.get("variables")
        estacion = body.get("estacion_id", "quillota")
        return jsonify(ml_registry.prediccion_batch(vars_, estacion))

    @app.get("/api/testing/resumen")
    def testing_resumen():
        return jsonify(testing_info.resumen_tests())

    @app.get("/api/deploy/info")
    def deploy_info_route():
        return jsonify(deploy_info.resumen_deploy())

    @app.get("/api/docs/indice")
    def docs_indice():
        return jsonify(docs_index.indice_documentacion())

    @app.get("/api/modulos/streamlit/cobertura")
    def streamlit_cobertura():
        from api_rest.catalog import MODULOS_SISTEMA

        st = [m for m in MODULOS_SISTEMA if m.get("tipo_acceso") == "streamlit"]
        migrados = [m for m in st if m.get("migrado_vue") or m.get("ruta_vue_alternativa")]
        return jsonify({
            "total_streamlit": len(st),
            "con_ruta_vue": len(migrados),
            "cobertura_pct": round(100 * len(migrados) / len(st)) if st else 100,
            "modulos": st,
        })
