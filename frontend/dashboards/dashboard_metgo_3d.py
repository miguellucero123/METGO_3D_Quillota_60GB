#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portal METGO 3D dinámico — reemplaza dashboard_metgo_3d.html (estático).

Puerto sugerido: 8513
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "METGO 3D Portal",
    "Panel principal dinámico · Valle de Aconcagua",
    module="unificado",
    page_icon="🌾",
)

try:
    from datos_reales_openmeteo import obtener_datos_meteorologicos_reales

    df = obtener_datos_meteorologicos_reales("Quillota", tipo="pronostico")
    datos_ok = df is not None and not df.empty
except Exception:
    df = None
    datos_ok = False

if datos_ok:
    from metgo.streamlit_theme import classify_weather_from_row, weather_scene_html

    row = df.iloc[-1].to_dict() if hasattr(df.iloc[-1], "to_dict") else {}
    cond = classify_weather_from_row(row)
    st.markdown(weather_scene_html(cond), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    tmax = row.get("temperatura_max") or row.get("temp_max")
    tmin = row.get("temperatura_min") or row.get("temp_min")
    c1.metric("T. máx", f"{float(tmax or 0):.1f} °C")
    c2.metric("T. mín", f"{float(tmin or 0):.1f} °C")
    c3.metric("Humedad", f"{float(row.get('humedad') or row.get('humedad_relativa') or 0):.0f} %")
    c4.metric("Lluvia", f"{float(row.get('precipitacion') or 0):.1f} mm")
    if "fecha" in df.columns and "temperatura_max" in df.columns:
        fig = px.line(df, x="fecha", y="temperatura_max", title="Pronóstico temperatura máxima")
        fig.update_layout(**plotly_layout(height=400), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
else:
    st.info("Conecte OpenMeteo (módulo 01) o use el panel Vue en Netlify para datos en vivo.")

st.markdown("### Módulos Streamlit (puertos locales)")
modulos = [
    ("8502", "Meteorológico", "dashboard_meteorologico_metgo.py"),
    ("8503", "Agrícola", "dashboard_agricola_inteligente.py"),
    ("8505", "IA / ML", "dashboard_ia_ml_avanzado.py"),
    ("8506", "Visualizaciones", "dashboard_visualizaciones_avanzadas.py"),
    ("8507", "Global métricas", "dashboard_global_metricas.py"),
    ("8512", "Unificado", "dashboard_unificado_diferenciado.py"),
]
for puerto, nombre, script in modulos:
    st.markdown(f"- **{puerto}** — {nombre} · `streamlit run frontend/dashboards/{script} --server.port {puerto}`")
