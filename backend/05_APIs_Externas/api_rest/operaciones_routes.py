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
