#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync local Etapa E: histórico corto + Archive 1 año → Supabase."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")

from api_rest.integracion import etl_sync  # noqa: E402


def main() -> int:
    print("=== sync dias=7 archive=1anio ===")
    res = etl_sync.sincronizar_estaciones(
        dias=7,
        incluir_csv=False,
        incluir_archive=True,
        anios_archive=1,
        origen="local_plan_calidad",
    )
    print("estaciones_sync", res.get("estaciones_sync"))
    print("pronostico_sync", res.get("pronostico_sync"))
    arch = res.get("archive_sync") or {}
    print("archive_sync", json.dumps({k: arch.get(k) for k in ("guardados", "errores", "estaciones", "param_anios", "error", "detalle") if True}, default=str)[:2000])
    print("store", res.get("store"))
    errs = res.get("errores") or []
    if errs:
        print("errores", errs[:10])
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
