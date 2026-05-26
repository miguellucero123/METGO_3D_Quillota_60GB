#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Métricas estilo Prometheus (Fase 10) — sin dependencia obligatoria de prometheus_client."""

from __future__ import annotations

import os
import time
from typing import Any

_APP_START = time.time()


def _gauge(name: str, help_text: str, value: float | int, labels: dict[str, str] | None = None) -> str:
    lines = [f"# HELP {name} {help_text}", f"# TYPE {name} gauge"]
    if labels:
        lbl = ",".join(f'{k}="{v}"' for k, v in labels.items())
        lines.append(f"{name}{{{lbl}}} {value}")
    else:
        lines.append(f"{name} {value}")
    return "\n".join(lines)


def recopilar_metricas() -> dict[str, Any]:
    out: dict[str, Any] = {
        "fase": "10",
        "uptime_s": int(time.time() - _APP_START),
        "entorno": os.getenv("RENDER", "local"),
    }
    try:
        from api_rest.integracion.estado_integracion import estado_modulos

        est = estado_modulos()
        out["integracion_promedio_pct"] = est.get("promedio_integracion", 0)
        out["integracion_fase"] = est.get("fase")
    except Exception:
        out["integracion_promedio_pct"] = 0

    try:
        from api_rest.integracion import meteo_store, ml_registry, notificaciones, workers_status

        ms = meteo_store.estadisticas_store()
        out["meteo_registros"] = ms.get("registros", 0)
        out["meteo_estaciones"] = ms.get("estaciones", 0)
        reg = ml_registry.leer_registro()
        out["ml_total"] = reg.get("total", 0)
        out["ml_servibles"] = reg.get("servibles", 0)
        ch = notificaciones.estado_canales()
        out["notif_outbox_pendientes"] = ch.get("outbox_pendientes", 0)
        out["notif_smtp"] = 1 if ch.get("smtp_configurado") else 0
        out["notif_webhook"] = 1 if ch.get("webhook_activo") else 0
        w = workers_status.estado_workers()
        for k, v in (w or {}).items():
            if isinstance(v, dict):
                out[f"worker_{k}_ok"] = 0 if v.get("estado") == "sin_heartbeat" else 1
    except Exception:
        pass

    try:
        from api_rest.integracion import ml_training_queue

        cola = ml_training_queue.estado_cola()
        out["ml_cola_pendientes"] = cola.get("pendientes", 0)
    except Exception:
        out["ml_cola_pendientes"] = 0

    try:
        from api_rest import iot_services

        out["iot_lecturas"] = len(iot_services.listar_lecturas(limite=5000))
    except Exception:
        out["iot_lecturas"] = 0

    return out


def formato_prometheus() -> str:
    m = recopilar_metricas()
    bloques = [
        _gauge("metgo_uptime_seconds", "Segundos desde arranque API", m.get("uptime_s", 0)),
        _gauge(
            "metgo_integracion_promedio",
            "Porcentaje integración módulos 01-11",
            m.get("integracion_promedio_pct", 0),
        ),
        _gauge("metgo_meteo_registros", "Registros SQLite meteo_historico", m.get("meteo_registros", 0)),
        _gauge("metgo_ml_modelos_total", "Modelos en registro MLOps", m.get("ml_total", 0)),
        _gauge("metgo_ml_modelos_servibles", "Modelos servibles (sanity-check OK)", m.get("ml_servibles", 0)),
        _gauge("metgo_notif_outbox_pendientes", "Mensajes outbox pendientes SMTP", m.get("notif_outbox_pendientes", 0)),
        _gauge("metgo_ml_cola_pendientes", "Trabajos ML en cola", m.get("ml_cola_pendientes", 0)),
        _gauge("metgo_iot_lecturas", "Lecturas IoT almacenadas (muestra)", m.get("iot_lecturas", 0)),
        _gauge("metgo_notif_smtp_configurado", "1 si SMTP configurado", m.get("notif_smtp", 0)),
        _gauge("metgo_notif_webhook_activo", "1 si webhook activo", m.get("notif_webhook", 0)),
    ]
    return "\n\n".join(bloques) + "\n"
