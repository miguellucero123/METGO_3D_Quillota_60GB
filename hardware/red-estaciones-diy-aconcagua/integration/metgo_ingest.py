#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reenvía lecturas Influx (o MQTT raw) hacia la API METGO IoT.

Compatible con el schema de iot_services.py:
  sensor_id, tipo, estacion_id, valor, unidad, fuente, timestamp

Uso:
  export METGO_API_URL=https://metgo-api.onrender.com/api
  export METGO_JWT=<token>
  export INFLUX_URL=http://localhost:8086
  export INFLUX_TOKEN=...
  python metgo_ingest.py --once
  python metgo_ingest.py --loop --interval 60
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests

try:
    from influxdb_client import InfluxDBClient
except ImportError:
    InfluxDBClient = None  # type: ignore


# tipos alineados con iot_services._unidad / API POST /api/iot/lecturas
FIELD_MAP = [
    ("temp_c", "temperatura", "°C"),
    ("rh", "humedad", "%"),
    ("pressure_hpa", "presion", "hPa"),
    ("wind_ms", "viento_velocidad", "m/s"),
    ("wind_dir", "viento_direccion", "deg"),
    ("rain_mm", "precipitacion", "mm"),
    ("uv", "uv", "UVI"),
]


def fetch_latest(influx_url: str, token: str, org: str, bucket: str) -> list[dict[str, Any]]:
    if InfluxDBClient is None:
        raise RuntimeError("pip install influxdb-client")
    q = f'''
from(bucket: "{bucket}")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "meteo")
  |> filter(fn: (r) => r.qc_ok == "1")
  |> last()
'''
    client = InfluxDBClient(url=influx_url, token=token, org=org)
    tables = client.query_api().query(q, org=org)
    # Agrupar por station_id + field
    by_station: dict[str, dict[str, Any]] = {}
    for table in tables:
        for rec in table.records:
            sid = rec.values.get("station_id") or "unknown"
            field = rec.get_field()
            by_station.setdefault(sid, {})[field] = rec.get_value()
            by_station[sid]["_time"] = rec.get_time()
    return [{"station_id": k, **v} for k, v in by_station.items()]


def to_metgo_payloads(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        sid = row["station_id"]
        ts = row.get("_time")
        if isinstance(ts, datetime):
            ts_iso = ts.astimezone(timezone.utc).isoformat()
        else:
            ts_iso = datetime.now(timezone.utc).isoformat()
        for field, tipo, unidad in FIELD_MAP:
            if field not in row:
                continue
            out.append(
                {
                    "sensor_id": f"lora-{sid}-{field}",
                    "tipo": tipo,
                    "estacion_id": sid.lower().replace("_", "-"),
                    "valor": float(row[field]),
                    "unidad": unidad,
                    "fuente": "lora_diy",
                    "timestamp": ts_iso,
                }
            )
    return out


def post_metgo(api_url: str, jwt: str, items: list[dict[str, Any]]) -> None:
    """POST /api/iot/lecturas acepta una lectura por request (fase3_routes)."""
    url = api_url.rstrip("/") + "/iot/lecturas"
    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    ok = 0
    for item in items:
        r = requests.post(url, json=item, headers=headers, timeout=30)
        r.raise_for_status()
        ok += 1
    print(f"OK → {ok}/{len(items)} lecturas en {url}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    api = os.environ.get("METGO_API_URL", "https://metgo-api.onrender.com/api")
    jwt = os.environ.get("METGO_JWT", "")
    influx_url = os.environ.get("INFLUX_URL", "http://localhost:8086")
    token = os.environ.get("INFLUX_TOKEN", "")
    org = os.environ.get("INFLUX_ORG", "metgo")
    bucket = os.environ.get("INFLUX_BUCKET", "estaciones")

    def tick() -> None:
        rows = fetch_latest(influx_url, token, org, bucket)
        payloads = to_metgo_payloads(rows)
        print(f"{len(rows)} estaciones → {len(payloads)} puntos")
        if args.dry_run or not jwt:
            print("(dry-run o sin METGO_JWT) ejemplo:", payloads[:2])
            return
        post_metgo(api, jwt, payloads)

    if args.loop:
        while True:
            try:
                tick()
            except Exception as e:
                print(f"error: {e}", file=sys.stderr)
            time.sleep(args.interval)
    else:
        tick()


if __name__ == "__main__":
    main()
