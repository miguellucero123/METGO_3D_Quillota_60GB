#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas REST de precipitación calibrada, heladas y acumulados."""

from __future__ import annotations

from datetime import datetime, timedelta

from flask import jsonify, request

from api_rest import services
from api_rest.auth_routes import auth_required


def register_precipitacion_routes(app) -> None:
    @app.get("/api/meteo/<estacion_id>/precipitacion-calibrada")
    @auth_required
    def meteo_precipitacion_calibrada(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        data = services.pronostico_precipitacion_calibrado(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Sin pronostico de precipitacion"}), 404
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/heladas")
    @auth_required
    def meteo_heladas(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        return jsonify(services.pronostico_heladas(estacion_id, dias))

    @app.get("/api/precip/<estacion_id>/pronostico")
    @auth_required
    def precip_pronostico(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        data = services.pronostico_precipitacion_bruto(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Sin pronostico"}), 404
        return jsonify(data)

    @app.get("/api/precip/<estacion_id>/calibrado")
    @auth_required
    def precip_calibrado(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        data = services.pronostico_precipitacion_calibrado(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Sin pronostico calibrado"}), 404
        return jsonify(data)

    @app.get("/api/precip/<estacion_id>/alertas")
    @auth_required
    def precip_alertas(estacion_id: str):
        cultivo = request.args.get("cultivo")
        alertas = services.generar_alertas_precipitacion(estacion_id, cultivo)
        resumen = {
            "total_alertas": len(alertas),
            "rojas": sum(1 for a in alertas if a.get("nivel_severidad") == "rojo"),
            "naranjas": sum(1 for a in alertas if a.get("nivel_severidad") == "naranja"),
        }
        return jsonify(
            {
                "estacion_id": estacion_id,
                "alertas_activas": alertas,
                "resumen": resumen,
            }
        )

    @app.get("/api/alertas/precipitacion")
    @auth_required
    def alertas_precipitacion_global():
        estacion_id = request.args.get("estacion")
        estaciones = [estacion_id] if estacion_id else services.ESTACIONES_PRINCIPALES
        todas: list[dict] = []
        for eid in estaciones:
            todas.extend(services.generar_alertas_precipitacion(eid))
        return jsonify({"alertas": todas, "total": len(todas)})

    @app.get("/api/alertas/helada")
    @auth_required
    def alertas_helada_global():
        estacion_id = request.args.get("estacion")
        estaciones = [estacion_id] if estacion_id else services.ESTACIONES_PRINCIPALES
        todas: list[dict] = []
        for eid in estaciones:
            todas.extend(services.generar_alertas_helada(eid))
        return jsonify({"alertas": todas, "total": len(todas)})

    @app.get("/api/precip/<estacion_id>/acumulado")
    @auth_required
    def precip_acumulado(estacion_id: str):
        rango = request.args.get("rango", "7d")
        dias = int(rango.replace("d", "")) if rango.endswith("d") else 7
        return jsonify(services.obtener_acumulado_precipitacion(estacion_id, dias))

    @app.get("/api/precip/<estacion_id>/historico")
    @auth_required
    def precip_historico(estacion_id: str):
        desde = request.args.get(
            "desde", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        )
        hasta = request.args.get("hasta", datetime.now().strftime("%Y-%m-%d"))
        return jsonify(
            services.obtener_historico_precipitacion(estacion_id, desde, hasta)
        )

    @app.get("/api/agricola/<estacion_id>/cronograma-riego")
    @auth_required
    def agricola_cronograma_riego(estacion_id: str):
        cultivo = request.args.get("cultivo", "palto")
        return jsonify(services.cronograma_riego_inteligente(estacion_id, cultivo))
