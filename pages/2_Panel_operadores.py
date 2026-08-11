#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Streamlit Cloud — panel operadores (legacy retirado; redirige a portal / Vue / visor)."""

from __future__ import annotations

from pathlib import Path

import runpy
import streamlit as st

from metgo.streamlit_bootstrap import bootstrap
import metgo_paths
from metgo.vue_embed import get_vue_base_url

bootstrap("01_meteo", "05_apis", "07_monitoreo")

_vue = (get_vue_base_url() or "https://metgo-quillota.pages.dev").rstrip("/")
_api = (os.getenv("METGO_API_URL") or "https://metgo-api.onrender.com").rstrip("/")
_legacy = metgo_paths.streamlit_dashboard_path("sistema_auth_dashboard_principal_metgo.py")

st.warning(
    "Panel **legacy** retirado del despliegue en nube. "
    f"Use el [portal de inicio](.) , el **Visor de puerto** o Vue: {_vue}/"
)
st.link_button("Abrir aplicación Vue", f"{_vue}/", use_container_width=True)
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Ir al portal de inicio", use_container_width=True):
        st.switch_page("streamlit_app.py")
with col_b:
    if st.button("Abrir Visor de puerto", use_container_width=True):
        st.switch_page("pages/4_Visor_de_puerto.py")

if Path(_legacy).is_file():
    st.divider()
    st.caption("Script legacy local detectado — cargando solo en este entorno.")
    runpy.run_path(str(_legacy), run_name="__main__")
else:
    st.info(
        "El archivo `frontend/dashboards/sistema_auth_dashboard_principal_metgo.py` "
        "ya no forma parte del árbol desplegado (movido a respaldos). "
        "Los dashboards 8502–8513 se abren desde **Visor de puerto**."
    )
