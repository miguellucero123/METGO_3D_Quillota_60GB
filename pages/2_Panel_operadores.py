#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Streamlit Cloud — panel operadores (frontend/dashboards)."""

from __future__ import annotations

import runpy

from metgo_streamlit_bootstrap import bootstrap
import metgo_paths
import streamlit as st

from metgo_vue_embed import get_vue_base_url

bootstrap("01_meteo", "05_apis", "07_monitoreo")

_vue = get_vue_base_url() or "https://metgo3d.netlify.app"
st.warning(
    "Panel **legacy** (gráficas Streamlit). La aplicación principal está en la "
    f"[página de inicio](.) o en Vue: {_vue}/"
)
st.link_button("Ir a aplicación Vue (index)", _vue + "/", use_container_width=True)

runpy.run_path(
    str(metgo_paths.streamlit_dashboard_path("sistema_auth_dashboard_principal_metgo.py")),
    run_name="__main__",
)
