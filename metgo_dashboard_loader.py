#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carga un dashboard Streamlit (script en frontend/dashboards) dentro del visor multipágina.

Evita conflicto de st.set_page_config al ejecutar scripts pensados para puertos 850x sueltos.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def _setup() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest", "04_dashboards", "07_monitoreo")
    metgo_paths.ensure_runtime_dirs()


def obtener_script_modulo(modulo_id: str) -> dict[str, Any] | None:
    _setup()
    from api_rest import catalog

    m = catalog.obtener_modulo(modulo_id)
    if not m or m.get("tipo_acceso") != "streamlit":
        return None
    if m.get("id") == "streamlit_principal":
        return m
    script = ROOT / m["script"]
    if not script.is_file():
        return None
    return {**m, "script_path": script}


def ejecutar_dashboard(modulo_id: str) -> None:
    """Ejecuta el .py del módulo dentro de la página Visor (mismo proceso Streamlit)."""
    import streamlit as st

    info = obtener_script_modulo(modulo_id)
    if not info:
        st.error(f"Módulo «{modulo_id}» no encontrado o no es Streamlit.")
        return

    if info.get("id") == "streamlit_principal":
        st.info(
            "El dashboard **principal** es este portal multipágina. "
            "Use el menú lateral o abra otro puerto (8502–8513)."
        )
        return

    script: Path = info["script_path"]
    st.caption(
        f"Puerto local de referencia **:{info.get('puerto')}** · "
        f"{info.get('utilidad') or info.get('descripcion', '')}"
    )

    noop = lambda *args, **kwargs: None  # noqa: E731
    original = st.set_page_config
    st.set_page_config = noop
    try:
        runpy.run_path(str(script), run_name=f"metgo_vis_{modulo_id}")
    except Exception as exc:
        st.error(f"No se pudo cargar el dashboard: {exc}")
        st.code(str(script), language="text")
    finally:
        st.set_page_config = original


# Slug de la página multipágina (pages/4_Visor_de_puerto.py → /Visor_de_puerto)
VISOR_PAGE_SLUG = "Visor_de_puerto"


def url_visor(base_url: str, modulo_id: str, *, embed: bool = True) -> str:
    base = base_url.rstrip("/")
    q = f"id={modulo_id}"
    if embed:
        q += "&embed=true"
    return f"{base}/{VISOR_PAGE_SLUG}?{q}"
