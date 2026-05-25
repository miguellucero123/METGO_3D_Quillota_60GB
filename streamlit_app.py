#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint Streamlit Cloud — METGO 3D.

Con METGO_VUE_URL en Secrets muestra la UI Vue (Netlify) a pantalla completa.
Main file en Cloud debe ser: streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from metgo_streamlit_bootstrap import bootstrap
from metgo_streamlit_theme import inject_theme, is_streamlit_cloud
from metgo_vue_embed import get_vue_base_url, render_vue_iframe, show_vue_fullscreen_on_cloud

st.set_page_config(
    page_title="METGO 3D — Quillota",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap("01_meteo", "05_api_rest", "07_monitoreo")
inject_theme()

# Cloud: pantalla Vue por defecto (no la home con tablas legacy)
show_vue_fullscreen_on_cloud("/servicios", height=920)

_vue_url = get_vue_base_url()
if _vue_url:
    st.link_button("Abrir Vue en pestaña nueva", f"{_vue_url}/servicios")
    render_vue_iframe("/servicios", height=920)
    st.stop()

st.markdown(
    '<div class="main-header"><h1 style="margin:0;color:white;">METGO 3D — Sistema Integrado Quillota</h1></div>',
    unsafe_allow_html=True,
)
st.caption("Layout v4 · backend · frontend · site-web")

st.error(
    "**Streamlit Cloud:** agregue en Secrets: "
    '`METGO_VUE_URL = "https://metgo3d.netlify.app"` y pulse Reboot.'
)

st.markdown(
    """
| Página (menú lateral) | Uso |
|------------------------|-----|
| **Panel Vue embebido** | Vue en iframe (requiere secret) |
| **Catálogo y servicios** | Versión Python |
| **Panel operadores** | Legacy (gráficas antiguas) |

**Main file** debe ser `streamlit_app.py` (Settings → General).
"""
)

if not is_streamlit_cloud():
    st.info("Local: `streamlit run streamlit_app.py` o Vue en http://127.0.0.1:5173")
