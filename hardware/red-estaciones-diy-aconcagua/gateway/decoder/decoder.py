#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decoder MQTT → calibración lineal → QC (4 tests) → InfluxDB 2.x

Payload CSV (texto LoRa / base64 ChirpStack):
  STATION_ID,epoch,temp_c,rh,pressure_hpa,wind_ms,wind_dir,rain_mm,uv
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("metgo-decoder")

# Calibración lineal: y = a * x + b  (actualizar tras Fase 2)
CALIBRATION: dict[str, dict[str, tuple[float, float]]] = {
    "ACQ-01": {
        "temp_c": (1.0, 0.0),
        "rh": (1.0, 0.0),
        "pressure_hpa": (1.0, 0.0),
        "wind_ms": (1.0, 0.0),
        "uv": (1.0, 0.0),
    },
    "ACQ-02": {
        "temp_c": (1.0, 0.0),
        "rh": (1.0, 0.0),
        "pressure_hpa": (1.0, 0.0),
        "wind_ms": (1.0, 0.0),
        "uv": (1.0, 0.0),
    },
    "_default": {
        "temp_c": (1.0, 0.0),
        "rh": (1.0, 0.0),
        "pressure_hpa": (1.0, 0.0),
        "wind_ms": (1.0, 0.0),
        "uv": (1.0, 0.0),
    },
}

RANGES = {
    "temp_c": (-20.0, 50.0),
    "rh": (0.0, 100.0),
    "pressure_hpa": (850.0, 1050.0),
    "wind_ms": (0.0, 60.0),
    "wind_dir": (0.0, 360.0),
    "rain_mm": (0.0, 500.0),
    "uv": (0.0, 20.0),
}


@dataclass
class Reading:
    station_id: str
    epoch: int
    temp_c: float
    rh: float
    pressure_hpa: float
    wind_ms: float
    wind_dir: int
    rain_mm: float
    uv: float
    qc_flags: dict[str, bool]


def apply_cal(station: str, field: str, value: float) -> float:
    table = CALIBRATION.get(station) or CALIBRATION["_default"]
    a, b = table.get(field, (1.0, 0.0))
    return a * value + b


def qc_range(field: str, value: float) -> bool:
    lo, hi = RANGES[field]
    return lo <= value <= hi


def qc_rate_of_change(prev: float | None, value: float, max_delta: float) -> bool:
    if prev is None:
        return True
    return abs(value - prev) <= max_delta


def qc_stuck(history: list[float], value: float, n: int = 5) -> bool:
    """True = OK (no stuck). False = stuck."""
    if len(history) < n:
        return True
    window = history[-n:] + [value]
    return len(set(round(x, 2) for x in window)) > 1


def qc_internal_consistency(temp_c: float, rh: float, pressure: float) -> bool:
    """HR alta + temp muy baja o presión absurda → fail suave."""
    if rh > 99.5 and temp_c > 40:
        return False
    if pressure < 870 and temp_c > 35:
        return False
    return True


_prev_temp: dict[str, float] = {}
_hist_temp: dict[str, list[float]] = {}


def parse_csv_payload(text: str) -> Reading | None:
    parts = [p.strip() for p in text.strip().split(",")]
    if len(parts) < 9:
        log.warning("payload corto: %s", text[:80])
        return None
    try:
        station = parts[0]
        epoch = int(float(parts[1]))
        raw = {
            "temp_c": float(parts[2]),
            "rh": float(parts[3]),
            "pressure_hpa": float(parts[4]),
            "wind_ms": float(parts[5]),
            "wind_dir": int(float(parts[6])),
            "rain_mm": float(parts[7]),
            "uv": float(parts[8]),
        }
    except (ValueError, IndexError) as e:
        log.error("parse error: %s (%s)", e, text[:80])
        return None

    cal = {
        k: apply_cal(station, k, v) if k != "wind_dir" and k != "rain_mm" else v
        for k, v in raw.items()
    }
    cal["wind_ms"] = apply_cal(station, "wind_ms", raw["wind_ms"])
    cal["rain_mm"] = raw["rain_mm"]  # acumulado; no calibrar lineal aquí
    cal["wind_dir"] = raw["wind_dir"] % 360

    flags = {
        "range_ok": all(qc_range(k, cal[k]) for k in RANGES if k in cal),
        "roc_ok": qc_rate_of_change(_prev_temp.get(station), cal["temp_c"], max_delta=8.0),
        "stuck_ok": qc_stuck(_hist_temp.setdefault(station, []), cal["temp_c"]),
        "consistency_ok": qc_internal_consistency(
            cal["temp_c"], cal["rh"], cal["pressure_hpa"]
        ),
    }

    _prev_temp[station] = cal["temp_c"]
    _hist_temp[station].append(cal["temp_c"])
    _hist_temp[station] = _hist_temp[station][-20:]

    return Reading(
        station_id=station,
        epoch=epoch,
        temp_c=cal["temp_c"],
        rh=cal["rh"],
        pressure_hpa=cal["pressure_hpa"],
        wind_ms=cal["wind_ms"],
        wind_dir=int(cal["wind_dir"]),
        rain_mm=cal["rain_mm"],
        uv=cal["uv"],
        qc_flags=flags,
    )


def extract_payload(msg_payload: bytes) -> str | None:
    """Acepta CSV plano o JSON ChirpStack (data base64 / object)."""
    text = msg_payload.decode("utf-8", errors="replace").strip()
    if text and text[0].isalnum() and "," in text and not text.startswith("{"):
        return text
    try:
        obj: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        return text if "," in text else None

    # ChirpStack v4: object ya decodificado, o data base64
    if isinstance(obj.get("object"), dict):
        o = obj["object"]
        # Si el codec ChirpStack ya parseó campos, reconstruir CSV
        if "station_id" in o:
            return (
                f"{o['station_id']},{o.get('epoch', 0)},{o.get('temp_c', 0)},"
                f"{o.get('rh', 0)},{o.get('pressure_hpa', 0)},{o.get('wind_ms', 0)},"
                f"{o.get('wind_dir', 0)},{o.get('rain_mm', 0)},{o.get('uv', 0)}"
            )
    data_b64 = obj.get("data")
    if data_b64:
        import base64

        return base64.b64decode(data_b64).decode("utf-8", errors="replace")
    return None


class Writer:
    def __init__(self) -> None:
        url = os.environ.get("INFLUX_URL", "http://localhost:8086")
        token = os.environ["INFLUX_TOKEN"]
        org = os.environ.get("INFLUX_ORG", "metgo")
        self.bucket = os.environ.get("INFLUX_BUCKET", "estaciones")
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.org = org

    def write(self, r: Reading) -> None:
        qc_ok = all(r.qc_flags.values())
        p = (
            Point("meteo")
            .tag("station_id", r.station_id)
            .tag("qc_ok", "1" if qc_ok else "0")
            .field("temp_c", r.temp_c)
            .field("rh", r.rh)
            .field("pressure_hpa", r.pressure_hpa)
            .field("wind_ms", r.wind_ms)
            .field("wind_dir", r.wind_dir)
            .field("rain_mm", r.rain_mm)
            .field("uv", r.uv)
            .field("qc_range", int(r.qc_flags["range_ok"]))
            .field("qc_roc", int(r.qc_flags["roc_ok"]))
            .field("qc_stuck", int(r.qc_flags["stuck_ok"]))
            .field("qc_consistency", int(r.qc_flags["consistency_ok"]))
            .time(r.epoch, write_precision="s")
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=p)
        log.info("wrote %s qc=%s", r.station_id, qc_ok)


def main() -> None:
    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    topic = os.environ.get("MQTT_TOPIC", "application/+/device/+/event/up")
    # También aceptar pub directo de laboratorio
    topics = [topic, "metgo/estaciones/+/raw"]

    writer = Writer()

    def on_connect(client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any = None) -> None:
        log.info("MQTT connected rc=%s", reason_code)
        for t in topics:
            client.subscribe(t)
            log.info("subscribed %s", t)

    def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        raw = extract_payload(msg.payload)
        if not raw:
            return
        reading = parse_csv_payload(raw)
        if reading:
            try:
                writer.write(reading)
            except Exception as e:
                log.exception("influx write failed: %s", e)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="metgo-decoder")
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(host, port, keepalive=60)
            client.loop_forever()
        except Exception as e:
            log.error("MQTT loop error: %s — retry in 5s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
