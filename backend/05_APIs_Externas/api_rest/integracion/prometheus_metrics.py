#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Métricas estilo Prometheus (Fase 10 / E10) — sin dependencia obligatoria de prometheus_client."""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

_APP_START = time.time()
_lock = threading.Lock()

# Histograma simple in-memory (ms): buckets fijos
_BUCKETS_MS = (50, 100, 200, 400, 800, 1600, 3200, 8000, float("inf"))
_req_count = 0
_req_sum_ms = 0.0
_req_buckets: dict[float, int] = {b: 0 for b in _BUCKETS_MS}
_req_by_status: dict[int, int] = defaultdict(int)


def observar_request(duration_ms: float, status: int = 200) -> None:
    """Registra latencia HTTP para histograma Prometheus (E10 SLO p95)."""
    global _req_count, _req_sum_ms
    ms = max(0.0, float(duration_ms))
    with _lock:
        _req_count += 1
        _req_sum_ms += ms
        _req_by_status[int(status)] += 1
        for b in _BUCKETS_MS:
            if ms <= b:
                _req_buckets[b] += 1
                break


def _gauge(name: str, help_text: str, value: float | int, labels: dict[str, str] | None = None) -> str:
    lines = [f"# HELP {name} {help_text}", f"# TYPE {name} gauge"]
    if labels:
        lbl = ",".join(f'{k}="{v}"' for k, v in labels.items())
        lines.append(f"{name}{{{lbl}}} {value}")
    else:
        lines.append(f"{name} {value}")
    return "\n".join(lines)


def _histogram_lines() -> str:
    with _lock:
        count = _req_count
        total = _req_sum_ms
        buckets = dict(_req_buckets)
        by_status = dict(_req_by_status)
    lines = [
        "# HELP metgo_http_request_duration_ms Latencia HTTP API (ms)",
        "# TYPE metgo_http_request_duration_ms histogram",
    ]
    cumulative = 0
    for b in _BUCKETS_MS:
        cumulative += buckets.get(b, 0)
        le = "+Inf" if b == float("inf") else str(int(b) if b == int(b) else b)
        lines.append(f'metgo_http_request_duration_ms_bucket{{le="{le}"}} {cumulative}')
    lines.append(f"metgo_http_request_duration_ms_sum {total:.3f}")
    lines.append(f"metgo_http_request_duration_ms_count {count}")
    lines.append("# HELP metgo_http_requests_total Requests por status")
    lines.append("# TYPE metgo_http_requests_total counter")
    for st, n in sorted(by_status.items()):
        lines.append(f'metgo_http_requests_total{{status="{st}"}} {n}')
    return "\n".join(lines)


def _frescura_metrics() -> tuple[dict[str, Any], list[str]]:
    """Gauges de frescura / estado por sitio."""
    bloques: list[str] = []
    resumen: dict[str, Any] = {"sitios": {}}
    try:
        from api_rest.health_sitios import listar_health_sitios

        data = listar_health_sitios(incluir_plantilla=False)
        estado_map = {"ok": 0, "degradado": 1, "critico": 2, "sin_datos": 1}
        for s in data.get("sitios") or []:
            slug = s.get("sitio") or "unknown"
            est = estado_map.get(s.get("estado"), 1)
            resumen["sitios"][slug] = s.get("estado")
            bloques.append(
                _gauge(
                    "metgo_sitio_estado",
                    "0=ok 1=degradado 2=critico",
                    est,
                    {"sitio": slug},
                )
            )
            for dominio, fr in (s.get("frescura") or {}).items():
                edad = fr.get("edad_horas")
                if edad is not None:
                    bloques.append(
                        _gauge(
                            "metgo_frescura_horas",
                            "Edad del último dato (horas)",
                            float(edad),
                            {"sitio": slug, "dominio": dominio},
                        )
                    )
        resumen["estado_global"] = data.get("estado")
    except Exception as exc:
        resumen["error"] = str(exc)
    return resumen, bloques


def recopilar_metricas() -> dict[str, Any]:
    out: dict[str, Any] = {
        "fase": "10",
        "uptime_s": int(time.time() - _APP_START),
        "entorno": os.getenv("RENDER", "local"),
    }
    with _lock:
        out["http_requests"] = _req_count
        out["http_duration_ms_sum"] = round(_req_sum_ms, 2)
        out["http_duration_ms_avg"] = (
            round(_req_sum_ms / _req_count, 2) if _req_count else 0
        )

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

    fr, _ = _frescura_metrics()
    out["frescura"] = fr
    out["sentry"] = bool(os.getenv("METGO_SENTRY_DSN", "").strip())
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
        _gauge("metgo_sentry_configurado", "1 si METGO_SENTRY_DSN definido", 1 if m.get("sentry") else 0),
        _histogram_lines(),
    ]
    _, fr_bloques = _frescura_metrics()
    bloques.extend(fr_bloques)
    return "\n\n".join(bloques) + "\n"
