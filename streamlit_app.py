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
from metgo_vue_embed import get_vue_base_url

bootstrap("01_meteo", "05_api_rest", "07_monitoreo")
inject_theme()

_vue_url = get_vue_base_url()
if _vue_url:
    st.success(f"Interfaz Vue (Netlify) configurada: `{_vue_url}`")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Abrir Panel Vue embebido", type="primary", use_container_width=True):
            st.switch_page("pages/3_Panel_Vue_embebido.py")
    with c2:
        st.link_button(
            "Abrir Vue en pestaña nueva",
            f"{_vue_url}/servicios",
            use_container_width=True,
        )
    st.warning(
        "Si ve el panel antiguo con emojis y graficas, no use **Panel operadores**; "
        "use **Panel Vue embebido** en el menu lateral."
    )

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
| **Catálogo y servicios** | Iconos (emoji), Iniciar/Detener en Python |
| **Panel Vue embebido** | Misma UI Vue en iframe (requiere `METGO_VUE_URL` en Cloud) |
| **Resumen público** | OpenMeteo, sin login (`site-web/`) |
| **Panel operadores** | Vista anterior con tarjetas HTML |

**Vue en produccion:** https://metgo3d.netlify.app — Secret `METGO_VUE_URL` + menu **Panel Vue embebido**
"""
)

st.info(
    "Si no ve estas opciones en el menú, en Streamlit Cloud confirme "
    "**Main file** = `streamlit_app.py` y pulse **Reboot app** tras el último push a GitHub."
)
