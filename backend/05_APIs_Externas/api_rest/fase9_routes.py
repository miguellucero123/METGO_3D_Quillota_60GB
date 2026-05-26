#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 9 — notificaciones multicanal y outbox."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest.auth_routes import auth_required, requiere_rol
from api_rest.integracion import notificaciones


def register_fase9_routes(app: Flask) -> None:
    @app.get("/api/notificaciones/status")
    @auth_required
    def notificaciones_status():
        return jsonify(notificaciones.estado_canales())

    @app.get("/api/notificaciones/outbox")
    @auth_required
    def notificaciones_outbox():
        limite = request.args.get("limite", 30, type=int)
        return jsonify({"items": notificaciones.listar_outbox(limite)})

    @app.post("/api/notificaciones/outbox/retry")
    @requiere_rol("admin")
    def notificaciones_outbox_retry():
        body = request.get_json(silent=True) or {}
        max_items = int(body.get("max", 10))
        return jsonify(notificaciones.reintentar_outbox(max_items=max_items))
