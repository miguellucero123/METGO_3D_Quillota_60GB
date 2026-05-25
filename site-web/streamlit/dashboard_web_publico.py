#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard público METGO — resumen meteorológico (OpenMeteo) sin autenticación.
Capa site-web; operadores usan frontend/dashboards + Vue.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve()
for _p in _root.parents:
    if (_p / "metgo_paths.py").exists():
        PROJECT_ROOT = _p
        break
else:
    raise RuntimeError("No se encontró metgo_paths.py en ancestros del proyecto.")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if _apis and str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

import pandas as pd
import plotly.express as px
import streamlit as st

from api_rest.services import ESTACIONES_PRINCIPALES, pronostico_meteo, resumen_meteo, slug_a_nombre

st.set_page_config(
    page_title="METGO 3D — Quillota (público)",
    page_icon="🌤️",
    layout="wide",
)

st.title("METGO 3D — Monitoreo público")
st.caption(
    "Datos vía OpenMeteo · Valle de Quillota y estaciones del Valle Central. "
    "Para operación completa (agrícola, alertas, ML) use la aplicación con login."
)

slug = st.selectbox(
    "Estación",
    ESTACIONES_PRINCIPALES,
    format_func=lambda s: slug_a_nombre(s),
)

resumen = resumen_meteo(slug)
if not resumen:
    st.warning("No hay datos disponibles para esta estación. Intente más tarde.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperatura", f"{resumen['temperatura']} °C")
c2.metric("Humedad", f"{resumen['humedad']} %")
c3.metric("Viento", f"{resumen['viento']} km/h")
c4.metric("Precipitación", f"{resumen['precipitacion']} mm")

st.subheader(f"Pronóstico — {resumen['estacion']}")
pron = pronostico_meteo(slug, 7)
if pron:
    df = pd.DataFrame(pron)
    fig = px.line(
        df,
        x="fecha",
        y=["temperatura_max", "temperatura_min"],
        labels={"value": "°C", "fecha": "Fecha", "variable": "Serie"},
        title="Temperaturas máx / mín (7 días)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sin serie de pronóstico para graficar.")

st.divider()
st.markdown(
    f"**Fuente:** {resumen.get('fuente', 'OpenMeteo')} · "
    f"**Actualizado:** {resumen.get('actualizado', '—')}"
)
st.markdown(
    "[Repositorio](https://github.com/miguellucero123/METGO_3D_Quillota_60GB) · "
    "Panel operativo: `streamlit run streamlit_app.py` (raíz del proyecto)"
)
