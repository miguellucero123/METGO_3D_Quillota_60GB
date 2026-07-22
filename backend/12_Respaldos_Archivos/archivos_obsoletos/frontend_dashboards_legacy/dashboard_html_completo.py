#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dashboard completo dinámico — reemplaza dashboard_html_completo.html."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Completo METGO",
    "Vista integral meteorología + agrícola + ML",
    module="unificado",
    page_icon="📊",
)

tab_m, tab_a, tab_ml = st.tabs(["Meteorología", "Agrícola", "ML"])

with tab_m:
    st.markdown("Ejecute el módulo dedicado o embeba Vue:")
    st.code("streamlit run frontend/dashboards/dashboard_meteorologico_metgo.py --server.port 8502", language="bash")

with tab_a:
    st.code("streamlit run frontend/dashboards/dashboard_agricola_inteligente.py --server.port 8503", language="bash")

with tab_ml:
    st.code("streamlit run frontend/dashboards/dashboard_ia_ml_avanzado.py --server.port 8505", language="bash")

st.info(
    "Este launcher unifica accesos. Para análisis completo use "
    "`dashboard_completo_metgo.py` o el SPA Vue en https://metgo3d.netlify.app"
)
