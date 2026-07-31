#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Punto de entrada WSGI para gunicorn (Render).

Uso: gunicorn wsgi_api:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120
Con threads, una llamada lenta a OpenMeteo no bloquea el resto de peticiones
del SPA (antes el proxy de Render las cortaba sin cabeceras CORS).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import metgo_paths

sys.path.insert(0, str(metgo_paths.MODULE_PATHS["05_api_rest"]))
metgo_paths.setup_paths("01_meteo", "05_apis")

from api_rest.app import app, ml_bootstrap, demo_preview_bootstrap

demo_preview_bootstrap()
ml_bootstrap()
