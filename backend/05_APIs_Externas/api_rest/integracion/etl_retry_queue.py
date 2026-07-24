#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cola de reintento ETL ligera (E10) — JSONL en disco, sin Redis.

Jobs soportados: ``sinca``, ``oficiales``, ``aire``, ``dispersion``, ``operaciones``.
El cron encola fallos y drena hasta ``METGO_ETL_RETRY_MAX`` por corrida.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

_JOBS: dict[str, Callable[[], Any]] = {}


def _queue_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists() or (p / "metgo" / "paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d / "etl_retry_queue.jsonl"
    return Path("etl_retry_queue.jsonl")


def _max_attempts() -> int:
    return max(1, int(os.getenv("METGO_ETL_RETRY_ATTEMPTS", "5")))


def _drain_limit() -> int:
    return max(1, int(os.getenv("METGO_ETL_RETRY_MAX", "8")))


def enqueue(job: str, error: str, payload: dict[str, Any] | None = None) -> None:
    """Añade un job fallido a la cola (append-only)."""
    path = _queue_path()
    row = {
        "job": job,
        "error": str(error)[:500],
        "payload": payload or {},
        "attempts": 0,
        "enqueued_at": time.time(),
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _leer_cola() -> list[dict[str, Any]]:
    path = _queue_path()
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _escribir_cola(rows: list[dict[str, Any]]) -> None:
    path = _queue_path()
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _resolver_job(name: str) -> Callable[[], Any] | None:
    if name == "sinca":
        from api_rest import sinca_service

        return sinca_service.sincronizar_sinca
    if name == "oficiales":
        from api_rest import oficiales_service

        return oficiales_service.sincronizar_oficiales
    if name == "aire":
        from api_rest import aire_service

        return aire_service.sincronizar_aire
    if name == "dispersion":
        from api_rest import dispersion_service

        return dispersion_service.sincronizar_dispersion
    if name == "operaciones":
        from api_rest import operaciones_service

        return operaciones_service.sincronizar_operaciones
    return None


def drain() -> dict[str, Any]:
    """Procesa hasta N jobs pendientes. Devuelve resumen."""
    rows = _leer_cola()
    if not rows:
        return {"procesados": 0, "ok": 0, "fallidos": 0, "restantes": 0}

    limit = _drain_limit()
    max_att = _max_attempts()
    pendientes = rows[:]
    ok = 0
    fallidos = 0
    procesados = 0
    detalle: list[dict[str, Any]] = []

    keep: list[dict[str, Any]] = []
    for row in pendientes:
        if procesados >= limit:
            keep.append(row)
            continue
        job = str(row.get("job") or "")
        fn = _resolver_job(job)
        procesados += 1
        if not fn:
            fallidos += 1
            detalle.append({"job": job, "ok": False, "motivo": "job_desconocido"})
            continue
        attempts = int(row.get("attempts") or 0) + 1
        try:
            result = fn()
            omitido = isinstance(result, dict) and result.get("omitido")
            # omitido por falta de CSV no es fallo de red → no reencolar
            if omitido and result.get("motivo") in (
                "sin_csv_dir",
                "sin_codigos_sinca",
                "sin_csv_ni_filas",
                "csv_sin_filas",
            ):
                ok += 1
                detalle.append({"job": job, "ok": True, "omitido": True})
                continue
            ok += 1
            detalle.append({"job": job, "ok": True})
        except Exception as exc:
            fallidos += 1
            detalle.append({"job": job, "ok": False, "error": str(exc)[:200]})
            if attempts < max_att:
                row["attempts"] = attempts
                row["error"] = str(exc)[:500]
                row["last_try"] = time.time()
                keep.append(row)

    _escribir_cola(keep)
    return {
        "procesados": procesados,
        "ok": ok,
        "fallidos": fallidos,
        "restantes": len(keep),
        "detalle": detalle,
    }


def estado_cola() -> dict[str, Any]:
    rows = _leer_cola()
    return {
        "pendientes": len(rows),
        "path": str(_queue_path()),
        "jobs": [r.get("job") for r in rows[:20]],
    }
