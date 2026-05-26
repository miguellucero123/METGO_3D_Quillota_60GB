#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loop del listener MQTT (proceso separado, Fase 8)."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from api_rest.integracion import mqtt_bridge, workers_status


def _paho_disponible() -> bool:
    try:
        import paho.mqtt.client as mqtt  # noqa: F401

        return True
    except ImportError:
        return False


def _on_message(client, userdata, msg):  # noqa: ARG001
    try:
        payload_raw = msg.payload.decode("utf-8")
        try:
            payload = json.loads(payload_raw)
        except json.JSONDecodeError:
            payload = {"valor": payload_raw}
        mqtt_bridge.ingestar_mensaje(msg.topic, payload)
        userdata["mensajes"] = userdata.get("mensajes", 0) + 1
    except Exception as exc:
        userdata["ultimo_error"] = str(exc)


def ejecutar_ciclo_inbox(intervalo_s: float = 30.0, max_iter: int | None = None) -> dict[str, Any]:
    """Sin broker: procesa inbox periódicamente."""
    n = 0
    iteraciones = 0
    while max_iter is None or iteraciones < max_iter:
        res = mqtt_bridge.procesar_inbox()
        n += res.get("procesados", 0)
        workers_status.registrar_heartbeat(
            "mqtt_listener",
            {
                "estado": "inbox_loop",
                "modo": "sin_broker",
                "procesados_acum": n,
                "ultimo_inbox": res,
            },
        )
        iteraciones += 1
        if max_iter is not None and iteraciones >= max_iter:
            break
        time.sleep(intervalo_s)
    return {"procesados": n, "iteraciones": iteraciones}


def _aplicar_tls(client, cfg: dict[str, Any]) -> None:
    if not cfg.get("tls"):
        return
    ca = os.environ.get("METGO_MQTT_CA_CERT", "")
    if ca:
        client.tls_set(ca_certs=ca)
    else:
        client.tls_set()
    if cfg.get("tls_insecure"):
        client.tls_insecure_set(True)


def ejecutar_listener_broker() -> None:
    import paho.mqtt.client as mqtt

    cfg = mqtt_bridge.mqtt_config()
    host = cfg["host"]
    port = cfg["port"]
    topic = os.environ.get("METGO_MQTT_TOPIC", "metgo/#")
    client_id = cfg["client_id"]
    user = os.environ.get("METGO_MQTT_USER", "")
    password = os.environ.get("METGO_MQTT_PASSWORD", "")

    userdata: dict[str, Any] = {"mensajes": 0}
    client = mqtt.Client(client_id=client_id, userdata=userdata)
    if user:
        client.username_pw_set(user, password)
    _aplicar_tls(client, cfg)
    client.on_message = _on_message

    def on_connect(c, _u, _f, rc):
        if rc == 0:
            c.subscribe(topic)
            workers_status.registrar_heartbeat(
                "mqtt_listener",
                {"estado": "conectado", "host": host, "topic": topic},
            )
        else:
            workers_status.registrar_heartbeat(
                "mqtt_listener",
                {"estado": "error_conexion", "rc": rc},
            )

    client.on_connect = on_connect
    client.connect(host, port, keepalive=60)
    workers_status.registrar_heartbeat(
        "mqtt_listener",
        {"estado": "iniciando", "host": host, "port": port},
    )
    client.loop_forever()


def main_loop(una_vez: bool = False) -> dict[str, Any]:
    """Punto de entrada del worker."""
    if mqtt_bridge.mqtt_habilitado() and mqtt_bridge.mqtt_config().get("host") and _paho_disponible():
        if una_vez:
            return {"error": "broker requiere loop continuo; use sin --once"}
        ejecutar_listener_broker()
        return {"ok": True}
    return ejecutar_ciclo_inbox(
        intervalo_s=float(os.environ.get("METGO_MQTT_INBOX_INTERVAL", "15")),
        max_iter=1 if una_vez else None,
    )
