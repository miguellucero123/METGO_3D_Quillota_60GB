#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRUD alertas configurables (Fase 2.2)."""

from __future__ import annotations

from flask import Flask, g, jsonify, request

from api_rest.alertas_config import actualizar, crear, eliminar, listar_por_usuario
from api_rest.auth_routes import auth_required, requiere_rol


def register_alertas_routes(app: Flask) -> None:
    @app.get("/api/alertas/config")
    @auth_required
    def alertas_config_list():
        return jsonify(listar_por_usuario(g.current_user))

    @app.post("/api/alertas/config")
    @requiere_rol("admin", "agronomo", "operador")
    def alertas_config_create():
        data = request.get_json(silent=True) or {}
        try:
            return jsonify(crear(g.current_user, data)), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.put("/api/alertas/config/<alerta_id>")
    @requiere_rol("admin", "agronomo", "operador")
    def alertas_config_update(alerta_id: str):
        data = request.get_json(silent=True) or {}
        try:
            item = actualizar(g.current_user, alerta_id, data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        if not item:
            return jsonify({"error": "Alerta no encontrada"}), 404
        return jsonify(item)

    @app.delete("/api/alertas/config/<alerta_id>")
    @requiere_rol("admin", "agronomo")
    def alertas_config_delete(alerta_id: str):
        if not eliminar(g.current_user, alerta_id):
            return jsonify({"error": "Alerta no encontrada"}), 404
        return jsonify({"ok": True})
