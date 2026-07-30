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


_CACHED_GIT_SHA = None

def _git_sha() -> str:
    global _CACHED_GIT_SHA
    if _CACHED_GIT_SHA is not None:
        return _CACHED_GIT_SHA
        
    sha = os.getenv("METGO_GIT_SHA", "").strip()
    if sha:
        _CACHED_GIT_SHA = sha[:7]
        return _CACHED_GIT_SHA
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode == 0:
            _CACHED_GIT_SHA = out.stdout.strip()[:7]
            return _CACHED_GIT_SHA
    except Exception:
        pass
    _CACHED_GIT_SHA = "dev"
    return _CACHED_GIT_SHA


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
        from api_rest.integracion.estado_integracion import resumen_integracion_health

        base["integracion"] = resumen_integracion_health()
    except ImportError:
        pass
    if os.getenv("METGO_SENTRY_DSN"):
        base["observabilidad"]["sentry"] = True

    # S5 readiness (sin secretos): qué falta configurar en Render
    smtp_host = (os.getenv("METGO_SMTP_HOST") or "").strip()
    stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    pii_kek = (os.getenv("METGO_PII_KEK") or "").strip()
    base["s5_ops"] = {
        "fase": "S5",
        "smtp_configurado": bool(smtp_host),
        "stripe_configurado": bool(stripe_key),
        "pii_kek_configurado": bool(pii_kek),
        "email_dev": (os.getenv("METGO_EMAIL_DEV") or "").strip() not in ("0", "false", "no"),
        "identity_store": (os.getenv("METGO_IDENTITY_STORE") or "supabase").strip().lower(),
        "m10_ops_board": True,
        "pendiente": [
            k
            for k, ok in (
                ("METGO_SMTP_HOST", bool(smtp_host)),
                ("STRIPE_SECRET_KEY", bool(stripe_key)),
                ("METGO_PII_KEK", bool(pii_kek)),
            )
            if not ok
        ],
    }
    if "ops_board" not in base["features"]:
        base["features"] = list(base["features"]) + ["ops_board", "spati_m10"]
    return base
