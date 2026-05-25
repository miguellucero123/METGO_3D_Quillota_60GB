#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Streamlit Cloud — panel operadores (frontend/dashboards)."""

from __future__ import annotations

import runpy

from metgo_streamlit_bootstrap import bootstrap
import metgo_paths

bootstrap("01_meteo", "05_apis", "07_monitoreo")

runpy.run_path(
    str(metgo_paths.streamlit_dashboard_path("sistema_auth_dashboard_principal_metgo.py")),
    run_name="__main__",
)
