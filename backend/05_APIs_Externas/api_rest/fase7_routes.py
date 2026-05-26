#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 7 — MQTT IoT (adaptador) y cola entrenamiento ML."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest.auth_routes import auth_required, requiere_rol
from api_rest.integracion import mqtt_bridge, ml_training_queue


def register_fase7_routes(app: Flask) -> None:
    @app.get("/api/iot/mqtt/status")
    def iot_mqtt_status():
        """Público: estado del adaptador MQTT (sin credenciales broker)."""
        return jsonify(mqtt_bridge.estado_conexion())

    @app.post("/api/iot/mqtt/ingestar")
    @auth_required
    def iot_mqtt_ingestar():
        body = request.get_json(silent=True) or {}
        topic = body.get("topic", "metgo/quillota/temperatura")
        payload = body.get("payload", body.get("valor", 0))
        return jsonify(mqtt_bridge.ingestar_mensaje(topic, payload)), 201

    @app.post("/api/iot/mqtt/inbox/procesar")
    @requiere_rol("admin", "operador")
    def iot_mqtt_inbox():
        return jsonify(mqtt_bridge.procesar_inbox())

    @app.get("/api/ml/train/status")
    @auth_required
    def ml_train_status():
        return jsonify(ml_training_queue.estado_cola())

    @app.post("/api/ml/train/queue")
    @auth_required
    def ml_train_queue():
        body = request.get_json(silent=True) or {}
        job = ml_training_queue.encolar_job(
            variables=body.get("variables"),
            estacion_id=body.get("estacion_id", "quillota"),
            notas=body.get("notas", ""),
            modo=body.get("modo", "sync"),
        )
        return jsonify(job), 201

    @app.post("/api/ml/train/run-next")
    @requiere_rol("admin")
    def ml_train_run_next():
        return jsonify(ml_training_queue.ejecutar_siguiente())
