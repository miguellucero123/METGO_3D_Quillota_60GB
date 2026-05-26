#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 10 — métricas Prometheus, MQTT TLS, ML profundo."""

from __future__ import annotations

import os

from flask import Flask, Response, jsonify, request

from api_rest.auth_routes import auth_required, requiere_rol
from api_rest.integracion import prometheus_metrics, ml_train_deep


def register_fase10_routes(app: Flask) -> None:
    @app.get("/api/metrics")
    def metrics_prometheus():
        """Scrape Prometheus (público si METGO_METRICS_PUBLIC=1, default sí)."""
        if os.environ.get("METGO_METRICS_PUBLIC", "1") == "0":
            return jsonify({"error": "Métricas no públicas"}), 403
        fmt = request.args.get("format", "prometheus")
        if fmt == "json":
            return jsonify(prometheus_metrics.recopilar_metricas())
        return Response(
            prometheus_metrics.formato_prometheus(),
            mimetype="text/plain; version=0.0.4; charset=utf-8",
        )

    @app.get("/api/metrics/json")
    @auth_required
    def metrics_json():
        return jsonify(prometheus_metrics.recopilar_metricas())

    @app.get("/api/ml/train/deep/status")
    @auth_required
    def ml_deep_status():
        return jsonify(ml_train_deep.estado_ultimo())

    @app.post("/api/ml/train/deep")
    @requiere_rol("admin")
    def ml_deep_run():
        body = request.get_json(silent=True) or {}
        timeout = int(body.get("timeout_s", 300))
        return jsonify(ml_train_deep.ejecutar_entrenamiento_profundo(timeout_s=timeout))
