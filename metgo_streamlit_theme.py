#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema Streamlit METGO — alineado con frontend/vue (main.css).
"""

from __future__ import annotations

import os

# Paleta Vue (main.css)
PRIMARY = "#3d6b52"
PRIMARY_HOVER = "#325a45"
ACCENT = "#5a9b72"
ACCENT_LIGHT = "#c5e0ce"
BG = "#f5f9f6"
SURFACE = "#ffffff"
BORDER = "#d8e8dc"
TEXT = "#1a2e22"
TEXT_SECONDARY = "#3d5248"
MUTED = "#6b7f74"
SUCCESS = "#2d6a4f"
WARNING = "#9a6b2e"
DANGER = "#9b3d3d"
INFO_BG = "#e8f2eb"

# Acentos por módulo (familia verde, distinguibles)
MODULE_COLORS = {
    "meteo": PRIMARY,
    "agricola": ACCENT,
    "visual": SUCCESS,
    "monitoreo": "#4a7c59",
    "ml": PRIMARY_HOVER,
    "global": "#5a9b72",
    "precision": "#3d6b52",
    "comparativo": MUTED,
    "alertas": WARNING,
    "simple": "#8fa895",
    "unificado": PRIMARY,
}

METGO_THEME_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', 'Segoe UI', system-ui, sans-serif !important;
}}

.stApp {{
    background-color: {BG};
    color: {TEXT};
}}

.block-container {{
    padding-top: 1.5rem;
    max-width: 1200px;
}}

.main-header {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%);
    padding: 2rem 1rem;
    border-radius: 14px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    box-shadow: 0 12px 40px rgba(26, 46, 34, 0.08);
}}

.metric-card {{
    background: {SURFACE};
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(26, 46, 34, 0.06);
    margin: 0.5rem 0;
    border-left: 4px solid {PRIMARY};
    border: 1px solid {BORDER};
    border-left: 4px solid {PRIMARY};
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(26, 46, 34, 0.1);
}}

.metric-number {{
    font-size: 2rem;
    font-weight: 700;
    color: {TEXT};
    margin: 0;
}}

.metric-label {{
    color: {MUTED};
    font-size: 0.9rem;
    margin: 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.metric-positive {{
    background: {SUCCESS};
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
}}

.metric-negative {{
    background: {DANGER};
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
}}

.metric-neutral {{
    background: {ACCENT};
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
}}

.chart-container {{
    background: {SURFACE};
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(26, 46, 34, 0.06);
    margin: 1rem 0;
    border: 1px solid {BORDER};
}}

.section-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {TEXT};
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid {PRIMARY};
    display: inline-block;
}}

.dashboard-card {{
    background: {SURFACE};
    padding: 2rem;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(26, 46, 34, 0.06);
    margin: 1.5rem 0;
    border: 1px solid {BORDER};
    position: relative;
    overflow: hidden;
}}

.dashboard-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {PRIMARY}, {ACCENT}, {ACCENT_LIGHT});
}}

.metgo-module-card {{
    background: {SURFACE};
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid {BORDER};
    box-shadow: 0 1px 2px rgba(26, 46, 34, 0.04);
}}

.metgo-btn {{
    background-color: {PRIMARY};
    color: white;
    padding: 8px 16px;
    text-decoration: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 5px 0;
}}

.metgo-btn:hover {{
    background-color: {PRIMARY_HOVER};
}}

.alert-card {{
    background: linear-gradient(135deg, {DANGER} 0%, #b83232 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
}}

.success-card {{
    background: linear-gradient(135deg, {SUCCESS} 0%, {PRIMARY} 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
}}

.info-card {{
    background: {INFO_BG};
    color: {TEXT};
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border: 1px solid {BORDER};
}}

.stButton > button {{
    background: {PRIMARY} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}}

.stButton > button:hover {{
    background: {PRIMARY_HOVER} !important;
    border-color: {PRIMARY_HOVER} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

@media (max-width: 768px) {{
    .main-header {{ padding: 1.5rem 0.75rem; }}
    .metric-number {{ font-size: 1.5rem; }}
}}
"""


def is_streamlit_cloud() -> bool:
    """Detecta despliegue en Streamlit Community Cloud."""
    env = os.environ
    if env.get("STREAMLIT_RUNTIME_ENV") == "cloud":
        return True
    host = (env.get("HOSTNAME") or env.get("STREAMLIT_SERVER_ADDRESS") or "").lower()
    return "streamlit.app" in host


def inject_theme() -> None:
    """Inyecta CSS global (llamar tras st.set_page_config)."""
    import streamlit as st

    st.markdown(f"<style>{METGO_THEME_CSS}</style>", unsafe_allow_html=True)


def module_card_html(
    nombre: str,
    color: str,
    descripcion: str,
    *,
    puerto: str = "",
    url: str = "",
    cloud: bool = False,
) -> str:
    """Tarjeta de módulo con estilo Vue."""
    if cloud:
        return f"""
        <div class="metgo-module-card" style="border-left: 4px solid {color};">
            <h5 style="color: {color}; margin: 0 0 10px 0;">{nombre}</h5>
            <p style="margin: 0 0 10px 0; font-size: 12px; color: {TEXT_SECONDARY};">{descripcion}</p>
            <p style="margin: 0; font-size: 11px; color: {MUTED};">Vista en Streamlit Cloud · datos vía panel principal</p>
        </div>
        """
    btn = (
        f'<a href="{url}" target="_blank" class="metgo-btn" style="background-color:{color};">🚀 Acceder</a>'
        if url.startswith("http")
        else ""
    )
    return f"""
    <div class="metgo-module-card" style="border-left: 4px solid {color};">
        <h5 style="color: {color}; margin: 0 0 10px 0;">{nombre}</h5>
        <p style="margin: 0 0 8px 0; font-size: 12px; color: {TEXT_SECONDARY};">{descripcion}</p>
        <p style="margin: 0 0 8px 0; font-size: 10px; color: {MUTED};">Puerto: {puerto}</p>
        {btn}
        <p style="margin: 8px 0 0; font-size: 11px; color: {MUTED};">Red local · compatible móvil</p>
    </div>
    """
