#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dashboard IA/ML — solo registry METGO (datos reales). Sin demo sintético."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest", "06_ml")

from api_rest.services import ESTACIONES_PRINCIPALES, nombre_a_slug, slug_a_nombre
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from ml_dashboard_utils import cargar_estado_ml
from meteo_dashboard_utils import hoy_chile

st.set_page_config(
    page_title="Sistema de Inteligencia Artificial - METGO",
    page_icon="METGO",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _ml_deps_ok() -> tuple[bool, str | None]:
    try:
        import sklearn  # noqa: F401
        import joblib  # noqa: F401

        return True, None
    except ImportError as exc:
        return False, str(exc)


_ml_ok, _ml_err = _ml_deps_ok()
if not _ml_ok:
    st.error(f"Dependencias ML no instaladas: {_ml_err}")
    st.info(
        "En Render (servicio metgo-streamlit): Manual Deploy tras el push "
        "con scikit-learn y joblib en requirements.txt. "
        "Comando de build: pip install -r requirements.txt."
    )
    st.stop()

bootstrap_dashboard(
    "Sistema de Inteligencia Artificial",
    "Machine Learning avanzado · proyecciones METGO 3D",
    module="ml",
)

st.sidebar.markdown("### Panel de Control IA")
st.sidebar.caption("Modo producción: registry MLOps (misma API que Vue /ml).")

estaciones_ml = [slug_a_nombre(s) for s in ESTACIONES_PRINCIPALES]
estacion_ml = st.sidebar.selectbox("Estación", estaciones_ml)
slug_ml = nombre_a_slug(estacion_ml)
sync_now = st.sidebar.button("Sincronizar registry")

with st.spinner("Cargando registry MLOps…"):
    estado = cargar_estado_ml(slug_ml, sincronizar=sync_now)

st.success(
    f"**Registry METGO** · {estado['servibles']}/{estado['total']} modelos servibles · "
    f"estación {estacion_ml} · {hoy_chile()}"
)
st.caption("Interfaz principal: http://127.0.0.1:5173/ml")

ro = estado["resumen_ops"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Modelos servibles", estado["servibles"])
c2.metric("Total registry", estado["total"])
c3.metric("Variables OK", len(ro.get("variables", [])))
c4.metric("Última sync", str(ro.get("actualizado", "—"))[:19])

if estado["modelos"]:
    df_m = pd.DataFrame(estado["modelos"])
    cols = [c for c in ("variable", "servible", "archivo", "r2", "mse", "modo_prediccion") if c in df_m.columns]
    st.dataframe(df_m[cols].head(20), use_container_width=True, hide_index=True)

if estado["proyecciones"]:
    st.markdown("### Proyección ML vs condición actual")
    st.caption("Un panel por variable (escala propia °C, %, mm…) — alineado con Vue.")
    df_p = pd.DataFrame(estado["proyecciones"])
    n = len(df_p)
    cols = st.columns(min(n, 3))
    for i, row in df_p.iterrows():
        with cols[i % len(cols)]:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    name="Observado",
                    x=["Observado"],
                    y=[row["actual"]],
                    marker_color="#1a5f4a",
                    text=[f"{row['actual']:.1f}" if row["actual"] is not None else "—"],
                    textposition="outside",
                )
            )
            fig.add_trace(
                go.Bar(
                    name="Modelo ML",
                    x=["Modelo ML"],
                    y=[row["prediccion"]],
                    marker_color="#3d7ab8",
                    text=[f"{row['prediccion']:.1f}"],
                    textposition="outside",
                )
            )
            fig.update_layout(
                **plotly_layout(
                    str(row["variable"]),
                    height=280,
                    barmode="group",
                    yaxis_title=str(row.get("unidad") or "").strip() or "valor",
                    showlegend=False,
                    margin=dict(l=48, r=24, t=48, b=32),
                )
            )
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
else:
    st.warning(
        "Sin modelos servibles. Ejecute entrenamiento desde Vue /ml o "
        "POST /api/ml/train/run con la API en :8080."
    )

m = estado["meteo"]
if m:
    st.info(
        f"Meteo hoy: T° {m.get('temperatura')}°C · "
        f"máx {m.get('temperatura_max')} · mín {m.get('temperatura_min')} · "
        f"lluvia {m.get('precipitacion')} mm"
    )

st.markdown("---")
st.caption(
    f"Sistema METGO — Inteligencia Artificial · datos reales del registry · "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
