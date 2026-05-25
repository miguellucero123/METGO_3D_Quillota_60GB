# -*- coding: utf-8 -*-
"""Página de inicio METGO en Streamlit (portal con enlaces a Vue, API y módulos)."""

from __future__ import annotations

import streamlit as st

from metgo_streamlit_theme import (
    ACCENT,
    PRIMARY,
    TEXT_SECONDARY,
    inject_theme,
    is_streamlit_cloud,
    module_card_html,
)
from metgo_vue_embed import get_vue_base_url

DEFAULT_VUE_PROD = "https://metgo3d.netlify.app"
DEFAULT_API_PROD = "https://metgo-api.onrender.com"


def _vue_url() -> str:
    return get_vue_base_url() or DEFAULT_VUE_PROD


def _api_health_url() -> str:
    base = DEFAULT_API_PROD
    return f"{base.rstrip('/')}/api/health"


def _mostrar_modulo_activado() -> None:
    """Si la URL trae ?activar=id (desde Vue/API), muestra utilidad del puerto/módulo."""
    try:
        from api_rest import catalog
    except ImportError:
        return
    activar = st.query_params.get("activar")
    if not activar:
        return
    m = catalog.obtener_modulo(str(activar))
    if not m:
        st.warning(f"Módulo «{activar}» no encontrado en el catálogo.")
        return
    puerto = m.get("puerto", "—")
    util = m.get("utilidad") or m.get("descripcion", "")
    st.info(
        f"**{m.get('nombre')}** · puerto local **:{puerto}** · {util}\n\n"
        "En la nube este portal no levanta el proceso en ese puerto; use la app Vue o "
        "ejecute METGO en su PC para el dashboard Plotly completo."
    )
    if m.get("ruta_vue_alternativa"):
        vue = _vue_url().rstrip("/") + m["ruta_vue_alternativa"]
        st.link_button("Abrir equivalente en Vue", vue, use_container_width=False)
    if st.button("Ir a catálogo y servicios", type="secondary"):
        st.switch_page("pages/0_Catalogo_y_servicios.py")


def render_inicio_page() -> None:
    """Portal de acceso: enlaces a la SPA Vue (index) y al resto del ecosistema."""
    inject_theme()
    _mostrar_modulo_activado()
    vue = _vue_url()
    vue_index = vue.rstrip("/") + "/"
    vue_login = vue.rstrip("/") + "/login"
    vue_servicios = vue.rstrip("/") + "/servicios"

    st.markdown(
        """
<div class="main-header">
  <h1 style="margin:0;color:white;">METGO 3D — Inicio</h1>
  <p style="margin:0.5rem 0 0 0;opacity:0.9;">Monitoreo meteorológico y agrícola · Quillota</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="info-card">
  <p style="margin:0;"><strong>Aplicación principal (Vue)</strong> — interfaz con iconos, paneles y datos en tiempo real.<br>
  Equivale al <code>index.html</code> de la SPA desplegada en Netlify.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button(
            "Abrir aplicación Vue (inicio)",
            vue_index,
            type="primary",
            use_container_width=True,
            help="Abre la SPA en Netlify (index / dashboard)",
        )
    with c2:
        st.link_button(
            "Iniciar sesión (Vue)",
            vue_login,
            use_container_width=True,
        )
    with c3:
        st.link_button(
            "Centro de servicios",
            vue_servicios,
            use_container_width=True,
        )

    st.markdown("##### También dentro de Streamlit")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Vue embebido (iframe)", use_container_width=True, type="secondary"):
            st.switch_page("pages/3_Panel_Vue_embebido.py")
    with b2:
        if st.button("Catálogo y servicios", use_container_width=True):
            st.switch_page("pages/0_Catalogo_y_servicios.py")
    with b3:
        if st.button("Resumen público", use_container_width=True):
            st.switch_page("pages/1_Resumen_publico.py")

    st.divider()
    st.subheader("Accesos rápidos")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            module_card_html(
                "Aplicación Vue (Netlify)",
                PRIMARY,
                "SPA principal · index.html, login, módulos meteorología y agricultura.",
                url=vue_index,
            ),
            unsafe_allow_html=True,
        )
        st.link_button("URL index (SPA)", vue_index, use_container_width=True)
    with col_b:
        st.markdown(
            module_card_html(
                "API REST (Render)",
                ACCENT,
                "Backend Flask · health, meteo, alertas, JWT.",
                url=_api_health_url(),
            ),
            unsafe_allow_html=True,
        )
        st.link_button("Probar API /health", _api_health_url(), use_container_width=True)

    with st.expander("Credenciales de demostración (API / Vue login)"):
        st.markdown(
            """
| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |
| `user` | `user123` |
| `metgo` | `metgo2025` |
            """
        )

    if is_streamlit_cloud():
        st.caption(
            f"Cloud · Vue configurado: `{vue}` · Secret opcional: `METGO_VUE_URL`"
        )
    else:
        st.caption(
            "Local · Vue: `npm run dev` en `frontend/vue` → http://127.0.0.1:5173 · "
            "API: `iniciar_api_rest.py` → :8080"
        )

    with st.expander("Panel Streamlit legacy (gráficas antiguas)"):
        st.warning("Solo si necesita el dashboard histórico con Plotly/Streamlit nativo.")
        if st.button("Abrir panel operadores (legacy)"):
            st.switch_page("pages/2_Panel_operadores.py")
