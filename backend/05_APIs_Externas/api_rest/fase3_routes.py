#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 3: IoT, ML, tenants, observabilidad."""

from __future__ import annotations

from flask import Flask, g, jsonify, request

from api_rest.auth_routes import auth_required, requiere_rol
from api_rest import iot_services, ml_services, services, tenants
from api_rest.observability import observability_payload


def register_fase3_routes(app: Flask) -> None:
    @app.get("/api/tenants")
    @auth_required
    def api_tenants():
        return jsonify(tenants.listar_tenants())

    @app.get("/api/tenants/me")
    @auth_required
    def api_tenant_me():
        tid = getattr(g, "tenant_id", None)
        if tid is None:
            return jsonify({"tenant_id": None, "acceso": "global", "tenants": tenants.listar_tenants()})
        cfg = tenants.TENANTS.get(tid)
        return jsonify(
            {
                "tenant_id": tid,
                "nombre": cfg["nombre"] if cfg else tid,
                "estaciones": tenants.estaciones_de_tenant(tid),
            }
        )

    @app.get("/api/iot/sensores")
    @auth_required
    def iot_sensores():
        return jsonify(iot_services.listar_sensores())

    @app.get("/api/iot/lecturas")
    @auth_required
    def iot_lecturas():
        estacion = request.args.get("estacion")
        limite = request.args.get("limite", 50, type=int)
        return jsonify(iot_services.listar_lecturas(estacion, limite))

    @app.post("/api/iot/lecturas")
    @requiere_rol("admin", "agronomo", "operador")
    def iot_registrar():
        data = request.get_json(silent=True) or {}
        return jsonify(iot_services.registrar_lectura(data)), 201

    @app.post("/api/iot/simular")
    @requiere_rol("admin", "agronomo")
    def iot_simular():
        n = iot_services.refrescar_simulacion()
        return jsonify({"ok": True, "lecturas_nuevas": n})

    @app.get("/api/ml/modelos")
    @auth_required
    def ml_modelos():
        solo = request.args.get("solo_servibles", "0") == "1"
        data = ml_services.listar_modelos()
        if solo:
            data = [m for m in data if m.get("servible")]
        return jsonify(data)

    @app.get("/api/ml/resumen")
    @auth_required
    def ml_resumen():
        return jsonify(ml_services.resumen_mlops())

    @app.get("/api/ml/prediccion/<variable>")
    @auth_required
    def ml_prediccion(variable: str):
        estacion = request.args.get("estacion", "quillota")
        result = ml_services.predecir(variable, estacion)
        if result.get("error"):
            return jsonify(result), 400
        return jsonify(result)
