#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL nocturno módulo 08 → SQLite `meteo_historico.db` (OpenMeteo + CSV opcional).

Uso local / Task Scheduler Windows / cron Linux:
    python backend/08_Gestion_Datos/scripts/run_etl_meteo_nightly.py

Variables de entorno (opcional):
    METGO_ETL_DIAS_SYNC       default 30
    METGO_ETL_SKIP_CSV=1     no importar CSV estático 5 años
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("No se encontró metgo_paths.py (ejecutar desde repo METGO)")


def main() -> int:
    root = _repo_root()
    sys.path.insert(0, str(root))

    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis_root = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if not apis_root or not Path(apis_root).is_dir():
        print("MODULE_PATHS 05_api_rest no válido", file=sys.stderr)
        return 2
    sys.path.insert(0, str(apis_root))

    from api_rest.integracion import etl_sync

    dias, incluir_csv = etl_sync.etl_parametros_defaults()
    res = etl_sync.sincronizar_estaciones(
        dias=dias, incluir_csv=incluir_csv, origen="cron_nightly"
    )
    print(json.dumps(res, indent=2, ensure_ascii=False, default=str))

    errores = res.get("errores") or []
    from api_rest.services import ESTACIONES_PRINCIPALES

    sync_ok_any = any(
        (res.get("estaciones_sync") or {}).get(s, 0) > 0 for s in ESTACIONES_PRINCIPALES
    )
    if errores and not sync_ok_any:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
