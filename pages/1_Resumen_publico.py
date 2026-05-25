#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Streamlit Cloud — capa pública (site-web)."""

from __future__ import annotations

import runpy

from metgo_streamlit_bootstrap import bootstrap
import metgo_paths

bootstrap("01_meteo", "05_api_rest")

runpy.run_path(
    str(metgo_paths.site_web_streamlit_path("dashboard_web_publico.py")),
    run_name="__main__",
)
