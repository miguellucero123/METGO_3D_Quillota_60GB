#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inicia la API REST METGO (Flask) en el puerto 8080 por defecto (METGO_API_PORT)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for p in Path(__file__).resolve().parents:
    if (p / "metgo_paths.py").exists():
        ROOT = p
        break
sys.path.insert(0, str(ROOT))
import metgo_paths

sys.path.insert(0, str(metgo_paths.MODULE_PATHS["05_api_rest"]))

metgo_paths.setup_paths("01_meteo", "05_apis")

from api_rest.app import main

if __name__ == "__main__":
    main()
