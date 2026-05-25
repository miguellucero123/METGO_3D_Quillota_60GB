#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint Streamlit Cloud — inicio METGO 3D (layout por capas).

Use el menú lateral (pages/) para:
  - Catálogo y servicios (como Vue: iconos + Iniciar)
  - Resumen público (site-web)
  - Panel operadores (legacy)
"""

from __future__ import annotations

import streamlit as st

from metgo_streamlit_bootstrap import bootstrap
from metgo_streamlit_theme import inject_theme

bootstrap("01_meteo", "05_api_rest", "07_monitoreo")
inject_theme()

st.markdown(
    '<div class="main-header"><h1 style="margin:0;color:white;">METGO 3D — Sistema Integrado Quillota</h1></div>',
    unsafe_allow_html=True,
)
st.caption("Layout v4 · backend · frontend · site-web")

st.markdown(
    """
Elige una vista en el **menú lateral**:

| Página | Descripción |
|--------|-------------|
| **Catálogo y servicios** | Iconos, puertos, Iniciar/Detener (equivalente Vue) |
| **Resumen público** | OpenMeteo, sin login (`site-web/`) |
| **Panel operadores** | Vista anterior con tarjetas HTML |

**La app Vue** (sidebar, iconos Lucide, `/servicios`): solo en PC → `iniciar_metgo_desarrollo.bat` → http://127.0.0.1:5173
"""
)

st.info(
    "Si no ve estas opciones en el menú, en Streamlit Cloud confirme "
    "**Main file** = `streamlit_app.py` y pulse **Reboot app** tras el último push a GitHub."
)
