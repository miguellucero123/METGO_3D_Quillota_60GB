#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cola ligera de re-entrenamiento ML (módulo 06) — Fase 7."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _queue_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d / "ml_training_queue.json"
    return Path("ml_training_queue.json")


def _load() -> dict[str, Any]:
    path = _queue_path()
    if not path.is_file():
        return {"jobs": [], "historial": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"jobs": [], "historial": []}


def _save(data: dict[str, Any]) -> None:
    _queue_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def encolar_job(
    variables: list[str] | None = None,
    estacion_id: str = "quillota",
    notas: str = "",
    modo: str = "sync",
) -> dict[str, Any]:
    modo_norm = "train" if modo == "train" else "sync"
    data = _load()
    job = {
        "id": str(uuid.uuid4())[:8],
        "estado": "pendiente",
        "modo": modo_norm,
        "variables": variables or [],
        "estacion_id": estacion_id,
        "notas": notas,
        "creado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    data.setdefault("jobs", []).append(job)
    _save(data)
    return job


def estado_cola() -> dict[str, Any]:
    data = _load()
    jobs = data.get("jobs", [])
    pendientes = [j for j in jobs if j.get("estado") == "pendiente"]
    return {
        "pendientes": len(pendientes),
        "total_jobs": len(jobs),
        "historial": data.get("historial", [])[-10:],
        "jobs": jobs,
    }


def ejecutar_siguiente() -> dict[str, Any]:
    """sync: registro MLOps; train: entrenamiento ligero Quillota + sync."""
    from api_rest.integracion import ml_registry, ml_train_runner

    data = _load()
    jobs = data.get("jobs", [])
    pendiente = next((j for j in jobs if j.get("estado") == "pendiente"), None)
    if not pendiente:
        return {"ok": False, "error": "No hay trabajos pendientes"}

    pendiente["estado"] = "en_proceso"
    pendiente["inicio"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _save(data)

    try:
        if pendiente.get("modo") == "train":
            train_res = ml_train_runner.entrenar_quillota(
                estacion_id=pendiente.get("estacion_id", "quillota"),
                variables=pendiente.get("variables") or None,
            )
            pendiente["resultado"] = train_res
        else:
            reg = ml_registry.sincronizar_registro()
            pendiente["resultado"] = {
                "registry_total": reg.get("total"),
                "registry_servibles": reg.get("servibles"),
            }
        pendiente["estado"] = "completado"
        pendiente["fin"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception as e:
        pendiente["estado"] = "error"
        pendiente["error"] = str(e)

    data = _load()
    data["jobs"] = [j for j in data.get("jobs", []) if j.get("id") != pendiente.get("id")]
    hist = data.get("historial", [])
    hist.append(pendiente)
    data["historial"] = hist[-30:]
    _save(data)
    return {"ok": pendiente.get("estado") == "completado", "job": pendiente}
