#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas calidad del aire (E7 — Copiapó). Contrato en openapi.yaml."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest import aire_service
from api_rest.auth_routes import auth_required

_ERROR_503 = {"error": "Servicio de calidad del aire temporalmente no disponible"}


def _responder(data, estacion_id: str):
    if data is None:
        if aire_service._coords_de(estacion_id) is None:
            return jsonify({"error": "Estación no encontrada", "estacion_id": estacion_id}), 404
        return jsonify(_ERROR_503), 503
    return jsonify(data)


def register_aire_routes(app: Flask) -> None:
    @app.get("/api/public/aire/<estacion_id>")
    def public_aire_actual(estacion_id: str):
        """Calidad del aire actual (CAMS) + ICAP, sin JWT."""
        try:
            data = aire_service.aire_actual(estacion_id)
        except Exception as exc:
            app.logger.warning("public_aire %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/pronostico")
    def public_aire_pronostico(estacion_id: str):
        dias = max(1, min(request.args.get("dias", default=5, type=int), 7))
        try:
            data = aire_service.aire_pronostico(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("public_aire_pronostico %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/historico")
    def public_aire_historico(estacion_id: str):
        dias = max(1, min(request.args.get("dias", default=7, type=int), 92))
        try:
            data = aire_service.aire_historico(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("public_aire_historico %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/aire/<estacion_id>")
    @auth_required
    def aire_actual_auth(estacion_id: str):
        try:
            data = aire_service.aire_actual(estacion_id)
        except Exception as exc:
            app.logger.warning("aire %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)
