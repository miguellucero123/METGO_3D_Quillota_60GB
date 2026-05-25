#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint Streamlit Cloud — página de inicio METGO 3D.

Portal con enlaces a la SPA Vue (index en Netlify), iframe, catálogo y resumen público.
"""

from __future__ import annotations

import streamlit as st

from metgo.streamlit_bootstrap import bootstrap
from metgo.streamlit_portal import render_inicio_page

st.set_page_config(
    page_title="METGO 3D — Inicio",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap("01_meteo", "05_api_rest", "07_monitoreo")
render_inicio_page()
