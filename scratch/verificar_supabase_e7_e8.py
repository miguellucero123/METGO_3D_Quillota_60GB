#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita tablas E7/E8 multi-sitio en Supabase (solo lectura)."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

TABLAS = [
    "sitios",
    "estaciones",
    "aire_registros",
    "aire_dispersion",
    "operaciones_ventanas",
    "meteo_registros",
    "meteo_pronostico",
    "ml_registry",
]


def main() -> int:
    print("URL set:", bool(os.getenv("SUPABASE_URL")), "| KEY set:", bool(os.getenv("SUPABASE_KEY")))
    client_mod = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
    c = client_mod.get_supabase_client()
    if not c:
        print("cliente: INACTIVO")
        return 1
    print("cliente: OK")
    ok = 0
    for tabla in TABLAS:
        try:
            r = c.table(tabla).select("*", count="exact").limit(1).execute()
            print(f"  {tabla:24} OK  count={r.count}")
            ok += 1
        except Exception as e:
            msg = str(e)
            if "PGRST205" in msg or "Could not find the table" in msg or "42P01" in msg:
                print(f"  {tabla:24} FALTA")
            else:
                print(f"  {tabla:24} ERROR: {msg[:120]}")
    print(f"Resumen: {ok}/{len(TABLAS)} accesibles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
