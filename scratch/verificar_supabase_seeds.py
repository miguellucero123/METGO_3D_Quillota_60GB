#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Muestra seeds E7/E8 en Supabase tras las migraciones."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")


def main() -> int:
    c = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client").get_supabase_client()
    if not c:
        print("cliente inactivo")
        return 1
    print("=== sitios ===")
    for r in c.table("sitios").select("slug,dominio,estado").order("slug").execute().data:
        print(f"  {r['slug']:18} {r['dominio']:12} {r['estado']}")
    print("=== estaciones por sitio ===")
    for sitio in ("quillota", "paine", "copiapo", "mantos_blancos", "demo"):
        rows = c.table("estaciones").select("id").eq("sitio", sitio).execute().data
        ids = [x["id"] for x in rows]
        print(f"  {sitio}: {len(ids)} -> {ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
