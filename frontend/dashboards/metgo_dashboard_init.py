#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bootstrap común para dashboards Streamlit METGO (tema Vue + Plotly)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]


def ensure_repo_path() -> Path:
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    return _REPO


def page_config_and_theme(
    title: str,
    subtitle: str = "",
    *,
    module: str = "meteo",
    page_title: str | None = None,
    page_icon: str = "🌤️",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded",
) -> tuple[Any, dict[str, Any], Any]:
    """set_page_config + inject_theme + cabecera unificada."""
    ensure_repo_path()
    import streamlit as st
    from metgo.streamlit_theme import PLOTLY_CONFIG, bootstrap_dashboard, plotly_layout

    st.set_page_config(
        page_title=page_title or f"{title} - METGO",
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )
    bootstrap_dashboard(title, subtitle, module=module)
    return st, PLOTLY_CONFIG, plotly_layout


def theme_only() -> tuple[dict[str, Any], Any]:
    """Solo CSS global + helpers Plotly (set_page_config ya aplicado)."""
    ensure_repo_path()
    from metgo.streamlit_theme import PLOTLY_CONFIG, inject_theme, plotly_layout

    inject_theme()
    return PLOTLY_CONFIG, plotly_layout
