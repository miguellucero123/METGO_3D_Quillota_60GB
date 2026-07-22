#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visor METGO — unifica acceso a los dashboards de los puertos 8501–8513 en la nube.

Uso: /Visor_de_puerto?id=visualizaciones&embed=true
La app Vue embebe esta URL para «ver el puerto» sin abrir 127.0.0.1 desde internet.
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
    raise RuntimeError("No se encontró metgo_paths.py")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from metgo.dashboard_loader import ejecutar_dashboard, obtener_script_modulo
from metgo.streamlit_bootstrap import bootstrap
from metgo.streamlit_theme import inject_theme, PRIMARY

bootstrap("01_meteo", "05_api_rest", "04_dashboards", "07_monitoreo")
inject_theme()

if str(PROJECT_ROOT / "backend" / "05_APIs_Externas") not in sys.path:
    _apis = PROJECT_ROOT / "backend" / "05_APIs_Externas"
    if _apis.is_dir():
        sys.path.insert(0, str(_apis))

from api_rest import catalog

modulo_id = (st.query_params.get("id") or st.session_state.get("visor_modulo_id") or "").strip()

st.markdown(
    f'<p style="color:{PRIMARY};font-weight:600;margin-bottom:0.5rem;">'
    "Visor de puertos METGO · acceso integrado</p>",
    unsafe_allow_html=True,
)

if not modulo_id:
    from metgo.streamlit_theme import is_streamlit_cloud

    st.subheader("Elija un dashboard Streamlit")
    if is_streamlit_cloud():
        st.caption(
            "Los códigos :8501–:8513 son la referencia del PC local. "
            "En Streamlit Cloud el visor carga el script en esta misma app (no abre ese puerto)."
        )
    opciones = [
        m
        for m in catalog.MODULOS_SISTEMA
        if m.get("tipo_acceso") == "streamlit"
    ]
    labels = {
        m["id"]: f"{m.get('nombre')} (ref. local :{m.get('puerto')})"
        for m in opciones
    }
    elegido = st.selectbox(
        "Dashboard",
        options=[m["id"] for m in opciones],
        format_func=lambda i: labels.get(i, i),
    )
    if st.button("Abrir en visor", type="primary"):
        st.query_params["id"] = elegido
        st.session_state["visor_modulo_id"] = elegido
        st.rerun()
    for m in opciones:
        util = m.get("utilidad") or m.get("descripcion", "")
        st.markdown(
            f"**{m.get('nombre')}** · ref. local `:{m.get('puerto')}` — {util}"
        )
else:
    info = obtener_script_modulo(modulo_id)
    if info:
        st.session_state["visor_modulo_id"] = modulo_id
        if st.button("← Cambiar módulo"):
            st.query_params.clear()
            st.session_state.pop("visor_modulo_id", None)
            st.rerun()
        ejecutar_dashboard(modulo_id)
    else:
        st.error(f"Módulo «{modulo_id}» no válido.")
        if st.button("Volver al selector"):
            st.query_params.clear()
            st.rerun()
