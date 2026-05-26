#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Health extendido para operación y dashboard /estado."""

from __future__ import annotations

import os
import subprocess
import time
import os
from typing import Any

_APP_START = time.time()


def _git_sha() -> str:
    sha = os.getenv("METGO_GIT_SHA", "").strip()
    if sha:
        return sha[:7]
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()[:7]
    except Exception:
        pass
    return "dev"


def build_health_payload(services_health_fn) -> dict[str, Any]:
    base = dict(services_health_fn())
    base["version"] = _git_sha()
    base["uptime_s"] = int(time.time() - _APP_START)
    base["servicio"] = "METGO API REST"
    try:
        from api_rest.observability import observability_payload

        base["observabilidad"] = observability_payload()
    except ImportError:
        base["observabilidad"] = {"logging": "basic"}
    base["fase"] = "10"
    base["features"] = [
        "iot",
        "mqtt_bridge",
        "mqtt_worker",
        "mlops",
        "ml_train_queue",
        "ml_train_runner",
        "workers_status",
        "notificaciones_multicanal",
        "notificaciones_outbox",
        "prometheus_metrics",
        "mqtt_tls",
        "ml_train_deep",
        "tenants",
        "rbac",
        "alertas_config",
        "integracion_01_08",
        "agricola_avanzado",
        "meteo_store",
        "etl_nightly",
    ]
    try:
        from api_rest.integracion.estado_integracion import estado_modulos

        base["integracion"] = estado_modulos()
    except ImportError:
        pass
    if os.getenv("METGO_SENTRY_DSN"):
        base["observabilidad"]["sentry"] = True
    return base
