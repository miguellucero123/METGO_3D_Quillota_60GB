#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panel Vue embebido en Streamlit (iframe).

Local: http://127.0.0.1:5173 (con `npm run dev`).
Cloud: requiere METGO_VUE_URL en Secrets (Vercel/Netlify).
"""

from __future__ import annotations

import streamlit as st

from metgo_streamlit_bootstrap import bootstrap
from metgo_streamlit_theme import inject_theme
from metgo_vue_embed import ROUTES, get_vue_base_url, render_vue_iframe, vue_url_config_hint

bootstrap()
inject_theme()

st.title("Panel Vue (embebido)")
st.markdown(
    "Interfaz **Vue 3** con iconos Lucide dentro de Streamlit. "
    "En Cloud necesita Vue desplegado en Netlify (ver `docs/manuales/DESPLIEGUE_VUE_NETLIFY.md`)."
)

base = get_vue_base_url()
if base:
    st.success(f"URL Vue: `{base}`")
else:
    vue_url_config_hint()

ruta_label = st.selectbox("Vista", list(ROUTES.keys()), index=0)
altura = st.slider("Altura del panel (px)", 500, 1200, 820, 20)

if st.button("Abrir en pestaña nueva", type="secondary"):
    from metgo_vue_embed import build_vue_url

    url = build_vue_url(ROUTES[ruta_label], embed=False)
    if url:
        st.markdown(f"[Abrir Vue]({url})")

render_vue_iframe(ROUTES[ruta_label], height=altura)
