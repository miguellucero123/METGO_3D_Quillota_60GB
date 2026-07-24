#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync local E7/E8 → Supabase (aire, dispersión, operaciones).

Uso (PowerShell):
  cd d:\\METGO_3D_Quillota_60GB
  python scratch/sync_e7_e8.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(apis) not in sys.path:
    sys.path.insert(0, str(apis))


def main() -> int:
    from api_rest import aire_service, dispersion_service, operaciones_service

    print("=== E7: sincronizar_aire (CAMS -> aire_registros) ===")
    t0 = time.time()
    aire = aire_service.sincronizar_aire()
    print(json.dumps(aire, ensure_ascii=False, indent=2))
    print(f"  ({time.time() - t0:.1f}s)\n")

    # Pausa breve para no saturar OpenMeteo (free tier / Render cooldown).
    time.sleep(2)

    print("=== E7: sincronizar_dispersion -> aire_dispersion ===")
    t0 = time.time()
    disp = dispersion_service.sincronizar_dispersion()
    print(json.dumps(disp, ensure_ascii=False, indent=2))
    print(f"  ({time.time() - t0:.1f}s)\n")

    time.sleep(2)

    print("=== E8: sincronizar_operaciones -> operaciones_ventanas ===")
    t0 = time.time()
    ops = operaciones_service.sincronizar_operaciones()
    print(json.dumps(ops, ensure_ascii=False, indent=2))
    print(f"  ({time.time() - t0:.1f}s)\n")

    print("=== conteos Supabase ===")
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        c = get_supabase_client()
        if not c:
            print("cliente Supabase inactivo")
            return 1
        for tabla in ("aire_registros", "aire_dispersion", "operaciones_ventanas"):
            r = c.table(tabla).select("*", count="exact").limit(1).execute()
            print(f"  {tabla}: {r.count}")
    except Exception as exc:
        print(f"verificación falló: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
