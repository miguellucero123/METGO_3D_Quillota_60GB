#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingesta IoT simulada + persistencia JSON (Fase 3.1)."""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _store_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "iot_lecturas.json"
    return Path("iot_lecturas.json")


def _load() -> list[dict[str, Any]]:
    path = _store_path()
    if not path.is_file():
        return _seed()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else _seed()
    except (json.JSONDecodeError, OSError):
        return _seed()


def _save(items: list[dict[str, Any]]) -> None:
    _store_path().write_text(
        json.dumps(items[-500:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _seed() -> list[dict[str, Any]]:
    sensores = listar_sensores()
    items = []
    for s in sensores[:3]:
        items.append(_generar_lectura(s["id"], s["tipo"], s["estacion_id"]))
    _save(items)
    return items


def listar_sensores() -> list[dict[str, Any]]:
    return [
        {
            "id": "iot-q-temp",
            "tipo": "temperatura",
            "estacion_id": "quillota",
            "ubicacion": "Fundo demo Quillota",
            "activo": True,
        },
        {
            "id": "iot-q-hum",
            "tipo": "humedad",
            "estacion_id": "quillota",
            "ubicacion": "Invernadero Quillota",
            "activo": True,
        },
        {
            "id": "iot-hij-viento",
            "tipo": "viento_velocidad",
            "estacion_id": "hijuelas",
            "ubicacion": "Parcela Hijuelas",
            "activo": True,
        },
        {
            "id": "iot-cas-temp",
            "tipo": "temperatura",
            "estacion_id": "casablanca",
            "ubicacion": "Casablanca costa",
            "activo": True,
        },
    ]


def _generar_lectura(sensor_id: str, tipo: str, estacion_id: str) -> dict[str, Any]:
    base = {
        "temperatura": 18 + random.uniform(-3, 8),
        "humedad": 55 + random.uniform(-15, 25),
        "viento_velocidad": random.uniform(0, 35),
        "precipitacion": random.choice([0, 0, 0, 0.2, 1.5]),
        "presion": 1013 + random.uniform(-5, 5),
    }
    valor = round(float(base.get(tipo.replace("viento_velocidad", "viento_velocidad"), 20)), 2)
    if tipo == "humedad":
        valor = max(0, min(100, valor))
    return {
        "id": str(uuid.uuid4()),
        "sensor_id": sensor_id,
        "tipo": tipo,
        "estacion_id": estacion_id,
        "valor": valor,
        "unidad": _unidad(tipo),
        "fuente": "iot_simulado",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _unidad(tipo: str) -> str:
    return {
        "temperatura": "°C",
        "humedad": "%",
        "viento_velocidad": "km/h",
        "precipitacion": "mm",
        "presion": "hPa",
    }.get(tipo, "")


def listar_lecturas(
    estacion_id: str | None = None,
    limite: int = 50,
) -> list[dict[str, Any]]:
    items = _load()
    if estacion_id:
        items = [x for x in items if x.get("estacion_id") == estacion_id]
    return sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)[:limite]


def registrar_lectura(payload: dict[str, Any]) -> dict[str, Any]:
    sensor_id = payload.get("sensor_id") or "iot-manual"
    tipo = payload.get("tipo", "temperatura")
    estacion_id = payload.get("estacion_id", "quillota")
    valor = float(payload.get("valor", 0))
    item = {
        "id": str(uuid.uuid4()),
        "sensor_id": sensor_id,
        "tipo": tipo,
        "estacion_id": estacion_id,
        "valor": valor,
        "unidad": payload.get("unidad") or _unidad(tipo),
        "fuente": payload.get("fuente", "iot_api"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    items = _load()
    items.append(item)
    _save(items)
    return item


def refrescar_simulacion() -> int:
    items = _load()
    try:
        from api_rest.integracion.iot_bridge import generar_lecturas_modulo03

        lecturas = generar_lecturas_modulo03(6)
        if lecturas:
            items.extend(lecturas)
            _save(items)
            return len(lecturas)
    except ImportError:
        pass
    for s in listar_sensores():
        if s.get("activo"):
            items.append(_generar_lectura(s["id"], s["tipo"], s["estacion_id"]))
    _save(items)
    return len(listar_sensores())
