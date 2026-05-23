#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrypoint Streamlit Cloud — redirige al dashboard principal."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import metgo_paths

metgo_paths.setup_all_paths()

runpy.run_path(
    str(metgo_paths.streamlit_dashboard_path("sistema_auth_dashboard_principal_metgo.py")),
    run_name="__main__",
)
