#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heartbeats de workers Fase 8 (MQTT listener, ML training)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _runtime_dir() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d
    return Path(".")


def _heartbeat_path(worker: str) -> Path:
    return _runtime_dir() / f"worker_{worker}.json"


def registrar_heartbeat(worker: str, payload: dict[str, Any] | None = None) -> None:
    data = {
        "worker": worker,
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **(payload or {}),
    }
    _heartbeat_path(worker).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def leer_heartbeat(worker: str) -> dict[str, Any] | None:
    path = _heartbeat_path(worker)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def estado_workers() -> dict[str, Any]:
    mqtt = leer_heartbeat("mqtt_listener")
    ml = leer_heartbeat("ml_training")
    return {
        "mqtt_listener": mqtt or {"estado": "sin_heartbeat", "worker": "mqtt_listener"},
        "ml_training": ml or {"estado": "sin_heartbeat", "worker": "ml_training"},
        "runtime": str(_runtime_dir()),
    }
