#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker cola ML (Fase 8): procesa trabajos pendientes (sync o train).

    python backend/08_Gestion_Datos/scripts/run_ml_training_worker.py
    python backend/08_Gestion_Datos/scripts/run_ml_training_worker.py --max 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("No se encontró metgo_paths.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="METGO ML training queue worker")
    parser.add_argument("--max", type=int, default=1, help="Máximo trabajos a procesar")
    args = parser.parse_args()

    root = _repo_root()
    sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if apis:
        sys.path.insert(0, str(apis))

    from api_rest.integracion import ml_training_queue, workers_status

    procesados = 0
    for _ in range(max(1, args.max)):
        res = ml_training_queue.ejecutar_siguiente()
        if not res.get("ok") and res.get("error") == "No hay trabajos pendientes":
            break
        procesados += 1
        print(json.dumps(res, ensure_ascii=False, indent=2, default=str))

    workers_status.registrar_heartbeat(
        "ml_training",
        {"estado": "idle", "procesados_en_corrida": procesados},
    )
    return 0 if procesados else 0


if __name__ == "__main__":
    raise SystemExit(main())
