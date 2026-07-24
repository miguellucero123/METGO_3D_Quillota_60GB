#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Logs estructurados, Sentry opcional y métricas de latencia (E10)."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any

from flask import Flask, g, request

logger = logging.getLogger("metgo.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

_SENTRY_INIT = False


def sentry_configurado() -> bool:
    return bool(os.getenv("METGO_SENTRY_DSN", "").strip())


def init_sentry() -> bool:
    """Inicializa sentry-sdk si hay DSN (dependencia opcional)."""
    global _SENTRY_INIT
    dsn = os.getenv("METGO_SENTRY_DSN", "").strip()
    if not dsn or _SENTRY_INIT:
        return _SENTRY_INIT
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=float(os.getenv("METGO_SENTRY_TRACES", "0.05")),
            environment=os.getenv("RENDER", "local"),
        )
        _SENTRY_INIT = True
    except Exception as exc:
        logger.warning(json.dumps({"event": "sentry_init_failed", "error": str(exc)}))
        _SENTRY_INIT = False
    return _SENTRY_INIT


def observability_payload() -> dict[str, Any]:
    return {
        "logging": "structured",
        "sentry": sentry_configurado(),
        "sentry_sdk": _SENTRY_INIT,
        "entorno": os.getenv("RENDER", "local"),
        "slo_ref": "docs/roadmap/SLO_E10.md",
    }


def register_observability(app: Flask) -> None:
    init_sentry()

    @app.before_request
    def _before():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:12])
        g._req_start = time.perf_counter()

    @app.after_request
    def _after(response):
        if request.path.startswith("/api/"):
            ms = int((time.perf_counter() - getattr(g, "_req_start", time.perf_counter())) * 1000)
            entry = {
                "event": "api_request",
                "request_id": getattr(g, "request_id", ""),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": ms,
                "user": getattr(g, "current_user", None),
            }
            logger.info(json.dumps(entry, ensure_ascii=False))
            response.headers["X-Request-ID"] = getattr(g, "request_id", "")
            try:
                from api_rest.integracion import prometheus_metrics

                # No contar scrape de metrics para no sesgar el histograma
                if not request.path.startswith("/api/metrics"):
                    prometheus_metrics.observar_request(ms, response.status_code)
            except Exception:
                pass
        return response
