#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptador MQTT módulo 03 (Fase 7).

- Sin broker: ingesta vía REST (`POST /api/iot/mqtt/ingestar`) o carpeta inbox JSON.
- Con broker: variables METGO_MQTT_* (requiere paho-mqtt instalado).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api_rest import iot_services


def _runtime_dir() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d
    return Path(".")


def _inbox_dir() -> Path:
    d = _runtime_dir() / "mqtt_inbox"
    d.mkdir(parents=True, exist_ok=True)
    return d


def mqtt_habilitado() -> bool:
    return os.environ.get("METGO_MQTT_ENABLED", "").lower() in ("1", "true", "yes")


def mqtt_tls_habilitado() -> bool:
    return os.environ.get("METGO_MQTT_TLS", "").lower() in ("1", "true", "yes")


def mqtt_config() -> dict[str, Any]:
    tls = mqtt_tls_habilitado()
    port_default = "8883" if tls else "1883"
    return {
        "habilitado": mqtt_habilitado(),
        "host": os.environ.get("METGO_MQTT_HOST", ""),
        "port": int(os.environ.get("METGO_MQTT_PORT", port_default)),
        "tls": tls,
        "tls_insecure": os.environ.get("METGO_MQTT_TLS_INSECURE", "").lower() in ("1", "true"),
        "topic_base": os.environ.get("METGO_MQTT_TOPIC", "metgo/+/+"),
        "client_id": os.environ.get("METGO_MQTT_CLIENT_ID", "metgo-api"),
        "inbox": str(_inbox_dir()),
        "paho_disponible": _paho_disponible(),
    }


def _paho_disponible() -> bool:
    try:
        import paho.mqtt.client as mqtt  # noqa: F401

        return True
    except ImportError:
        return False


def _parse_topic(topic: str) -> dict[str, str]:
    """
    metgo/<estacion>/<tipo>  o  metgo/sensores/<estacion>/<tipo>
    """
    parts = [p for p in (topic or "").strip("/").split("/") if p]
    if len(parts) >= 3 and parts[0].lower() == "metgo":
        if parts[1].lower() == "sensores" and len(parts) >= 4:
            return {"estacion_id": parts[2], "tipo": parts[3]}
        return {"estacion_id": parts[1], "tipo": parts[2]}
    return {"estacion_id": "quillota", "tipo": "temperatura"}


def _payload_a_lectura(
    topic: str,
    payload: dict[str, Any] | str | float,
) -> dict[str, Any]:
    meta = _parse_topic(topic)
    if isinstance(payload, dict):
        return {
            "sensor_id": payload.get("sensor_id") or f"mqtt-{meta['estacion_id']}-{meta['tipo']}",
            "tipo": payload.get("tipo") or meta["tipo"],
            "estacion_id": payload.get("estacion_id") or meta["estacion_id"],
            "valor": float(payload.get("valor", payload.get("value", 0))),
            "unidad": payload.get("unidad"),
            "fuente": "mqtt",
        }
    return {
        "sensor_id": f"mqtt-{meta['estacion_id']}-{meta['tipo']}",
        "tipo": meta["tipo"],
        "estacion_id": meta["estacion_id"],
        "valor": float(payload),
        "fuente": "mqtt",
    }


def ingestar_mensaje(topic: str, payload: Any) -> dict[str, Any]:
    """Convierte mensaje MQTT (o equivalente REST) en lectura IoT persistida."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"valor": payload}
    body = _payload_a_lectura(topic, payload)
    lectura = iot_services.registrar_lectura(body)
    return {"ok": True, "topic": topic, "lectura": lectura}


def procesar_inbox() -> dict[str, Any]:
    """Lee archivos *.json del inbox (uno por mensaje) y los mueve a procesados/."""
    inbox = _inbox_dir()
    proc = inbox / "procesados"
    proc.mkdir(exist_ok=True)
    ok = 0
    errores: list[str] = []
    for f in sorted(inbox.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            topic = data.get("topic", "metgo/quillota/temperatura")
            payload = data.get("payload", data)
            ingestar_mensaje(topic, payload)
            dest = proc / f.name
            f.rename(dest)
            ok += 1
        except (json.JSONDecodeError, OSError, ValueError) as e:
            errores.append(f"{f.name}: {e}")
    return {"procesados": ok, "errores": errores, "inbox": str(inbox)}


def estado_conexion() -> dict[str, Any]:
    cfg = mqtt_config()
    estado = "deshabilitado"
    if cfg["habilitado"] and cfg["host"]:
        estado = "configurado_sin_listener" if not cfg["paho_disponible"] else "listo_para_conectar"
    elif cfg["habilitado"]:
        estado = "habilitado_sin_host"
    return {
        **cfg,
        "estado": estado,
        "modo_mvp": "REST + inbox JSON (sin daemon MQTT en API)",
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
