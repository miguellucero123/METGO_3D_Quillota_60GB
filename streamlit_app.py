#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint Streamlit Cloud — inicio METGO 3D (layout por capas).

Use el menú lateral (pages/) para:
  - Resumen público (site-web)
  - Panel operadores (frontend/dashboards)
"""

from __future__ import annotations

import streamlit as st

from metgo_streamlit_bootstrap import bootstrap

bootstrap("01_meteo", "05_api_rest", "07_monitoreo")

st.title("METGO 3D — Sistema Integrado Quillota")
st.caption("Layout v4 · backend · frontend · site-web")

st.markdown(
    """
Elige una vista en el **menú lateral**:

| Página | Descripción |
|--------|-------------|
| **Resumen público** | OpenMeteo, sin login (`site-web/`) |
| **Panel operadores** | Dashboard principal con acceso a módulos |

Para uso diario con Vue + API JWT: clone el repo y ejecute `iniciar_metgo_desarrollo.bat`.
"""
)

st.info(
    "Si no ve estas opciones en el menú, en Streamlit Cloud confirme "
    "**Main file** = `streamlit_app.py` y pulse **Reboot app** tras el último push a GitHub."
)
