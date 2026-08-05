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
    try:
        from api_rest.identity.email_notify import smtp_configurado as _smtp_ok

        smtp_ready = _smtp_ok()
    except Exception:
        smtp_ready = bool((os.getenv("METGO_SMTP_HOST") or "").strip()) and bool(
            (os.getenv("METGO_SMTP_FROM") or "").strip()
        )
    stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    pii_kek = (os.getenv("METGO_PII_KEK") or "").strip()
    smtp_from = (os.getenv("METGO_SMTP_FROM") or "").strip()
    base["s5_ops"] = {
        "fase": "S5",
        "smtp_configurado": smtp_ready,
        "stripe_configurado": bool(stripe_key),
        "pii_kek_configurado": bool(pii_kek),
        "email_dev": (os.getenv("METGO_EMAIL_DEV") or "").strip() not in ("0", "false", "no"),
        "require_email_verify": (os.getenv("METGO_REQUIRE_EMAIL_VERIFY") or "1").strip().lower()
        not in ("0", "false", "no", "off"),
        "identity_store": (os.getenv("METGO_IDENTITY_STORE") or "supabase").strip().lower(),
        "m10_ops_board": True,
        "pendiente": [
            k
            for k, ok in (
                ("METGO_SMTP_HOST", bool((os.getenv("METGO_SMTP_HOST") or "").strip())),
                ("METGO_SMTP_FROM", bool(smtp_from)),
                ("STRIPE_SECRET_KEY", bool(stripe_key)),
                ("METGO_PII_KEK", bool(pii_kek)),
            )
            if not ok
        ],
    }
    try:
        from api_rest import security_hardening as sec

        base["s5_ops"]["rate_limit_enabled"] = sec.rate_limit_enabled()
        base["s5_ops"]["turnstile_configured"] = sec.turnstile_configured()
        base["s5_ops"]["turnstile_required"] = sec.turnstile_required()
        if not sec.turnstile_configured():
            base["s5_ops"]["pendiente"].append("METGO_TURNSTILE_SECRET")
    except Exception:
        pass
    try:
        from api_rest.identity import identity_store, pii_crypto

        base["s5_ops"]["kyc_gate_paid"] = identity_store.kyc_gate_enabled()
        base["s5_ops"]["pii_kek_fp"] = pii_crypto.kek_fingerprint()
        base["s5_ops"]["session_idle_s"] = int(os.getenv("METGO_SESSION_IDLE_S") or "0")
    except Exception:
        pass
    if "ops_board" not in base["features"]:
        base["features"] = list(base["features"]) + ["ops_board", "spati_m10"]

    # E12 readiness: CSV ejemplos o env (sin secretos)
    try:
        from api_rest import oficiales_service, sinca_service

        st_s = sinca_service.estado_sinca()
        st_o = oficiales_service.estado_fuentes()
        base["e12_ops"] = {
            "fase": "E12.1",
            "sinca_estado": st_s.get("estado"),
            "sinca_csv_origen": st_s.get("csv_dir_origen"),
            "sinca_csv_archivos": st_s.get("csv_archivos"),
            "sinca_codigos": st_s.get("estaciones_con_codigo"),
            "agromet_disponible": bool((st_o.get("agromet") or {}).get("disponible")),
            "dmc_disponible": bool((st_o.get("dmc") or {}).get("disponible")),
            "pendiente": [
                k
                for k, ok in (
                    ("METGO_SINCA_IDS", int(st_s.get("estaciones_con_codigo") or 0) > 0),
                    (
                        "METGO_SINCA_CSV_DIR_prod",
                        st_s.get("csv_dir_origen") == "env",
                    ),
                    (
                        "METGO_AGROMET_IDS",
                        int((st_o.get("agromet") or {}).get("estaciones_con_codigo") or 0) > 0,
                    ),
                    (
                        "METGO_DMC_IDS",
                        int((st_o.get("dmc") or {}).get("estaciones_con_codigo") or 0) > 0,
                    ),
                )
                if not ok
            ],
        }
    except Exception as exc:
        base["e12_ops"] = {"fase": "E12.1", "error": str(exc)[:160]}

    return base
