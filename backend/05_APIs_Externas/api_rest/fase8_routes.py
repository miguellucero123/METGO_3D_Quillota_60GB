#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 8 — workers y entrenamiento ML real."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest.auth_routes import auth_required, requiere_rol
from api_rest.integracion import workers_status, ml_train_runner, ml_training_queue


def register_fase8_routes(app: Flask) -> None:
    @app.get("/api/workers/status")
    def workers_status_route():
        """Público: heartbeats MQTT / ML workers (sin secretos)."""
        return jsonify(workers_status.estado_workers())

    @app.post("/api/ml/train/run")
    @requiere_rol("admin")
    def ml_train_run_inline():
        """Entrenamiento ligero inmediato (admin, puede tardar varios segundos)."""
        body = request.get_json(silent=True) or {}
        return jsonify(
            ml_train_runner.entrenar_todos(
                estacion_id=body.get("estacion_id", "quillota"),
                dias_datos=int(body.get("dias_datos", 365)),
            )
        )

    @app.post("/api/ml/train/process-queue")
    @requiere_rol("admin")
    def ml_train_process_queue():
        max_jobs = int((request.get_json(silent=True) or {}).get("max", 1))
        resultados = []
        for _ in range(max(1, min(max_jobs, 10))):
            res = ml_training_queue.ejecutar_siguiente()
            resultados.append(res)
            if res.get("error") == "No hay trabajos pendientes":
                break
        workers_status.registrar_heartbeat(
            "ml_training",
            {"estado": "api_batch", "procesados": len(resultados)},
        )
        return jsonify({"procesados": len(resultados), "resultados": resultados})
