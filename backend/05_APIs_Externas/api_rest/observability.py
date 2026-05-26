#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Logs estructurados y metadatos de observabilidad (Fase 3.4)."""

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


def sentry_configurado() -> bool:
    return bool(os.getenv("METGO_SENTRY_DSN", "").strip())


def observability_payload() -> dict[str, Any]:
    return {
        "logging": "structured",
        "sentry": sentry_configurado(),
        "entorno": os.getenv("RENDER", "local"),
    }


def register_observability(app: Flask) -> None:
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
        return response
