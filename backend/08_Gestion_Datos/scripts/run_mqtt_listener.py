#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker MQTT (Fase 8) — proceso separado de la API Flask.

Sin broker: procesa inbox JSON cada METGO_MQTT_INBOX_INTERVAL segundos.
Con broker: METGO_MQTT_ENABLED=1 + METGO_MQTT_HOST + paho-mqtt instalado.

    python backend/08_Gestion_Datos/scripts/run_mqtt_listener.py
    python backend/08_Gestion_Datos/scripts/run_mqtt_listener.py --once
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("No se encontró metgo_paths.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="METGO MQTT listener worker")
    parser.add_argument("--once", action="store_true", help="Un ciclo inbox y salir")
    args = parser.parse_args()

    root = _repo_root()
    sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if apis:
        sys.path.insert(0, str(apis))

    from api_rest.integracion.mqtt_listener_core import main_loop

    res = main_loop(una_vez=args.once)
    if isinstance(res, dict) and res.get("error"):
        print(res["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
