#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Puente al sistema IoT del módulo 03."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def _setup_iot() -> bool:
    for p in Path(__file__).resolve().parents:
        scripts = p / "backend" / "03_Sistema_IoT_Drones" / "scripts"
        if scripts.is_dir():
            if str(scripts) not in sys.path:
                sys.path.insert(0, str(scripts))
            return True
    return False


def generar_lecturas_modulo03(cantidad: int = 4) -> list[dict[str, Any]]:
    if not _setup_iot():
        return []
    try:
        from sistema_iot_metgo import SensorIoT
    except ImportError:
        return []

    sensores_cfg = [
        ("iot-q-temp", "temperatura", {"lat": -32.88, "lon": -71.26}, "quillota"),
        ("iot-q-hum", "humedad", {"lat": -32.88, "lon": -71.26}, "quillota"),
        ("iot-hij-viento", "viento_velocidad", {"lat": -32.78, "lon": -71.15}, "hijuelas"),
    ]
    lecturas = []
    for sid, tipo, ubic, est in sensores_cfg[:cantidad]:
        sensor = SensorIoT(sid, tipo, ubic, {})
        lectura = sensor.leer_sensor()
        lecturas.append(
            {
                "id": lectura.get("sensor_id", sid),
                "sensor_id": sid,
                "tipo": tipo,
                "estacion_id": est,
                "valor": round(float(lectura.get("valor", 0)), 2),
                "unidad": lectura.get("unidad", ""),
                "fuente": "modulo_03_iot",
                "timestamp": lectura.get("timestamp"),
            }
        )
    return lecturas
