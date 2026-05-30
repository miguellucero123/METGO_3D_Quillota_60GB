#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema unificado dinámico — reemplaza dashboard_sistema_unificado.html."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Sistema Unificado METGO",
    "Navegación central a dashboards dinámicos",
    module="unificado",
    page_icon="🔗",
)

from metgo.streamlit_theme import MODULE_COLORS, module_card_html, is_streamlit_cloud

cloud = is_streamlit_cloud()
catalogo = [
    ("Meteorológico", "8502", "meteo", "dashboard_meteorologico_metgo.py"),
    ("Agrícola inteligente", "8503", "agricola", "dashboard_agricola_inteligente.py"),
    ("Monitoreo", "8504", "monitoreo", "dashboard_monitoreo_tiempo_real.py"),
    ("IA / ML", "8505", "ml", "dashboard_ia_ml_avanzado.py"),
    ("Visualizaciones", "8506", "visual", "dashboard_visualizaciones_avanzadas.py"),
    ("Global métricas", "8507", "global", "dashboard_global_metricas.py"),
    ("Precisión agrícola", "8508", "precision", "dashboard_agricultura_precision.py"),
    ("Comparativo", "8509", "comparativo", "dashboard_analisis_comparativo.py"),
    ("Alertas", "8510", "alertas", "dashboard_alertas_automaticas.py"),
    ("Simple", "8511", "simple", "dashboard_simple_optimizado.py"),
    ("Unificado", "8512", "unificado", "dashboard_unificado_diferenciado.py"),
    ("Portal 3D", "8513", "unificado", "dashboard_metgo_3d.py"),
]

cols = st.columns(2)
for i, (nombre, puerto, mod, script) in enumerate(catalogo):
    color = MODULE_COLORS.get(mod, MODULE_COLORS["meteo"])
    url = f"http://localhost:{puerto}" if not cloud else ""
    with cols[i % 2]:
        st.markdown(
            module_card_html(
                nombre,
                color,
                f"Streamlit dinámico · {script}",
                puerto=puerto,
                url=url,
                cloud=cloud,
            ),
            unsafe_allow_html=True,
        )
