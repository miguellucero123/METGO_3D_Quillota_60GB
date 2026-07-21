#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dashboard global dinámico — reemplaza dashboard_global_html.html."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Global METGO",
    "KPIs integrados · reemplazo HTML estático",
    module="global",
    page_icon="🌍",
)

rng = np.random.default_rng(42)
fechas = pd.date_range(end=pd.Timestamp.today(), periods=30, freq="D")
df = pd.DataFrame(
    {
        "fecha": fechas,
        "temperatura": 18 + 6 * np.sin(np.arange(30) / 5) + rng.normal(0, 1, 30),
        "humedad": 60 + 10 * np.cos(np.arange(30) / 4) + rng.normal(0, 3, 30),
        "lluvia": rng.exponential(1.2, 30),
    }
)

c1, c2, c3 = st.columns(3)
c1.metric("Temp. media 30d", f"{df['temperatura'].mean():.1f} °C")
c2.metric("Humedad media", f"{df['humedad'].mean():.0f} %")
c3.metric("Lluvia acum.", f"{df['lluvia'].sum():.1f} mm")

fig = px.line(df, x="fecha", y=["temperatura", "humedad"], title="Series globales (demo dinámica)")
fig.update_layout(**plotly_layout("Métricas globales"))
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.caption("Para datos reales use dashboard_global_metricas.py (8507) o la API METGO.")
