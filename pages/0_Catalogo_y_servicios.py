#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vista tipo Vue: catálogo con iconos + centro de servicios (Iniciar / Detener / Abrir).

Equivalente a frontend/vue → /modulos y /servicios.
En Streamlit Cloud: catálogo sí; arranque de puertos solo en PC local con API.
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

import metgo_paths

metgo_paths.setup_paths("05_api_rest", "01_meteo")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if _apis and str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

import os

import streamlit as st
from api_rest import catalog, streamlit_launcher
from api_rest.streamlit_launcher import _api_en_nube
from metgo.streamlit_bootstrap import bootstrap
from metgo.streamlit_theme import (
    ACCENT,
    PRIMARY,
    TEXT_SECONDARY,
    inject_theme,
    is_streamlit_cloud,
    module_card_html,
)

bootstrap()
inject_theme()

ICON_EMOJI = {
    "layout-dashboard": "📊",
    "cloud-sun": "🌤️",
    "sprout": "🌱",
    "bell-ring": "🔔",
    "settings": "⚙️",
    "grid-3x3": "📋",
    "server": "🖧",
    "monitor": "🖥️",
    "thermometer": "🌡️",
    "activity": "📡",
    "cpu": "🤖",
    "bar-chart-3": "📊",
    "gauge": "📈",
    "map": "🗺️",
    "git-compare": "↔️",
    "shield-alert": "🛡️",
    "layers": "📚",
    "box": "📦",
}

st.set_page_config(
    page_title="METGO — Catálogo y servicios",
    page_icon="🌤️",
    layout="wide",
)

st.markdown(
    f'<div class="main-header"><h2 style="margin:0;color:white;">Catálogo y centro de servicios</h2>'
    f'<p style="margin:0.5rem 0 0;opacity:0.95;">Misma lógica que la app Vue (iconos · puertos · Iniciar)</p></div>',
    unsafe_allow_html=True,
)

en_nube = _api_en_nube() or is_streamlit_cloud()
if en_nube:
    st.info(
        "Modo **nube**: cada puerto (8501–8513) indica qué hace el módulo en su PC. "
        "Use **Activar en nube** para volver al portal con el módulo seleccionado, "
        "o **Ver en Vue** cuando exista equivalente. **Iniciar PC** solo en desarrollo local."
    )
else:
    st.success(
        "Modo local: puede iniciar cada dashboard Streamlit desde la pestaña **Servicios Streamlit**."
    )

tab_cat, tab_srv = st.tabs(["📋 Catálogo de módulos", "🖧 Servicios Streamlit"])

# —— Catálogo (como /modulos en Vue) ——
with tab_cat:
    mods_all = catalog.listar_modulos()
    oficiales = [m for m in mods_all if not m.get("deprecado")]
    legacy = [m for m in mods_all if m.get("deprecado")]
    vue_mods = [m for m in mods_all if m.get("tipo_acceso") == "vue"]
    stl_mods = [m for m in mods_all if m.get("tipo_acceso") == "streamlit"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Módulos oficiales", len(oficiales))
    c2.metric("Módulos legacy", len(legacy))
    c3.metric("Vue / oficiales", len(vue_mods))
    c4.metric("Streamlit / soporte", len(stl_mods))

    resumen_texto = (
        f"{len(oficiales)} oficiales · {len(legacy)} legacy · "
        f"{len(vue_mods)} en Vue · {len(stl_mods)} en Streamlit"
    )
    st.caption(f"Resumen ejecutivo: {resumen_texto}")

    filtro = st.selectbox(
        "Filtrar categoría",
        ["todos"] + [c["id"] for c in catalog.resumen_sistema().get("categorias", [])],
        format_func=lambda x: "Todos" if x == "todos" else next(
            (c["nombre"] for c in catalog.resumen_sistema().get("categorias", []) if c["id"] == x), x
        ),
    )
    mods = catalog.listar_modulos(None if filtro == "todos" else filtro)

    def _render_grid(items, heading, empty_msg):
        st.markdown(f"#### {heading}")
        if not items:
            st.info(empty_msg)
            return
        cols = st.columns(3)
        for i, m in enumerate(items):
            icon = ICON_EMOJI.get(m.get("icono", "box"), "📦")
            puerto = m.get("puerto", "")
            desc = m.get("utilidad") or m.get("descripcion", "")
            tipo = m.get("tipo_acceso", "")
            attrs = ", ".join((m.get("atributos") or [])[:3])
            if attrs:
                desc = f"{desc} · {attrs}"
            estado = "LEGACY" if m.get("deprecado") else "OFICIAL"
            if m.get("deprecado") and m.get("nota_deprecacion"):
                desc = f"{desc} · {m['nota_deprecacion']}"
            nombre = f"{icon} [{estado}] {m.get('nombre', m.get('id'))}"
            color = PRIMARY if tipo == "vue" else ACCENT
            url = ""
            if tipo == "streamlit" and puerto and not is_streamlit_cloud():
                url = f"http://127.0.0.1:{puerto}"
            with cols[i % 3]:
                st.markdown(
                    module_card_html(
                        nombre,
                        color,
                        f"Módulo {m.get('modulo_num', '')} · {tipo} — {desc}",
                        puerto=str(puerto) if puerto else "—",
                        url=url,
                        cloud=is_streamlit_cloud(),
                    ),
                    unsafe_allow_html=True,
                )

    _render_grid([m for m in mods if not m.get("deprecado")], "Módulos oficiales", "No hay módulos oficiales para este filtro.")
    if legacy:
        st.divider()
        _render_grid([m for m in mods if m.get("deprecado")], "Legacy / soporte", "No hay módulos legacy para este filtro.")
# —— Centro de servicios (como /servicios en Vue) ——
with tab_srv:
    st.markdown(
        f'<p style="color:{TEXT_SECONDARY};">Cada fila es un proceso Streamlit en un puerto. '
        "Use <strong>Iniciar</strong> solo en desarrollo local.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Detener todos (gestionados por esta sesión)", type="secondary"):
        streamlit_launcher.detener_todos()
        st.rerun()

    servicios = streamlit_launcher.listar_estados()
    for s in servicios:
        col_a, col_b, col_c = st.columns([3, 1, 2])
        icon = ICON_EMOJI.get(s.get("icono", "monitor"), "🖥️")
        with col_a:
            st.markdown(f"**{icon} {s.get('nombre', s.get('id'))}**")
            st.caption(f"Módulo {s.get('modulo_num')} · puerto **{s.get('puerto')}**")
            if s.get("utilidad"):
                st.caption(s["utilidad"])
        with col_b:
            estado = s.get("estado", "detenido")
            st.markdown(
                f'<span style="font-size:0.75rem;font-weight:600;color:{PRIMARY if estado == "corriendo" else "#6b7f74"};">'
                f"{estado.upper()}</span>",
                unsafe_allow_html=True,
            )
        with col_c:
            sid = s["id"]
            if s.get("ruta_vue_alternativa"):
                vue_base = os.getenv("METGO_VUE_URL", "https://metgo3d.netlify.app").rstrip("/")
                st.link_button(
                    "Vue",
                    f"{vue_base}{s['ruta_vue_alternativa']}",
                    key=f"vue_{sid}",
                )
            visor = s.get("url_visor") or s.get("url_embed")
            if visor:
                st.link_button("👁 Visor", visor, key=f"visor_{sid}")
            elif estado == "disponible_nube" and s.get("url"):
                st.link_button("☁ Nube", s["url"], key=f"cloud_{sid}")
            if estado != "corriendo" and not _api_en_nube():
                if st.button("▶ PC", key=f"start_{sid}", disabled=is_streamlit_cloud()):
                    r = streamlit_launcher.iniciar(sid)
                    if r.get("ok"):
                        st.toast(r.get("mensaje", "Iniciado"))
                    else:
                        st.error(r.get("error", "Error"))
                    st.rerun()
            elif estado == "corriendo" and not _api_en_nube():
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("■ Detener", key=f"stop_{sid}"):
                        streamlit_launcher.detener(sid)
                        st.rerun()
                with b2:
                    if s.get("url"):
                        st.link_button("↗ Abrir", s["url"])
            elif _api_en_nube() and estado != "disponible_nube":
                st.caption("Configure METGO_STREAMLIT_CLOUD_URL en la API")
        st.divider()

    st.markdown("---")
    st.markdown(
        "**App Vue completa (recomendada):** ejecute en su PC `iniciar_metgo_desarrollo.bat` "
        "y abra [http://127.0.0.1:5173/servicios](http://127.0.0.1:5173/servicios) — iconos Lucide, "
        "misma API y mejor experiencia."
    )
