#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema Streamlit METGO — alineado con frontend/vue (main.css).
"""

from __future__ import annotations

import os

# Paleta Vue (Dark Mode)
PRIMARY = "#059669"
PRIMARY_HOVER = "#047857"
ACCENT = "#10b981"
ACCENT_LIGHT = "#34d399"
BG = "#0f172a"
SURFACE = "#1e293b"
BORDER = "#334155"
TEXT = "#f8fafc"
TEXT_SECONDARY = "#cbd5e1"
MUTED = "#94a3b8"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"
INFO_BG = "#334155"

# Light blue (meteo / ML — alineado con Vue main.css)
SKY = "#38bdf8"
SKY_DEEP = "#0ea5e9"
SKY_LIGHT = "#0284c7"
SKY_MUTED = "#0369a1"

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

.stApp, [data-testid="stAppViewContainer"], .main {{
    background-color: {BG} !important;
    color: {TEXT} !important;
}}

[data-testid="stHeader"] {{
    background: {SURFACE} !important;
    border-bottom: 1px solid {BORDER};
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

/* —— Ilustraciones meteorológicas (CSS, mismo lenguaje que Vue) —— */
.weather-scene-st {{
    position: relative;
    width: 100%;
    max-width: 320px;
    height: 130px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid {BORDER};
    margin: 0.5rem 0 1rem;
    background: linear-gradient(180deg, {SKY_LIGHT} 0%, {SKY_MUTED} 100%);
}}
.weather-scene-st__sun {{
    position: absolute; top: 18px; right: 24px; width: 48px; height: 48px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #ffeaa7, #f4c430);
    box-shadow: 0 0 20px rgba(244,196,48,0.45);
    animation: metgo-sun 4s ease-in-out infinite;
}}
.weather-scene-st__cloud {{
    position: absolute; background: rgba(255,255,255,0.92); border-radius: 999px;
    animation: metgo-cloud 12s ease-in-out infinite alternate;
}}
.weather-scene-st__cloud--a {{ width: 68px; height: 26px; top: 34px; left: 16%; }}
.weather-scene-st__cloud--b {{ width: 80px; height: 28px; top: 54px; right: 10%; opacity: 0.88; }}
.weather-scene-st__rain span {{
    position: absolute; top: 55%; width: 2px; height: 12px; border-radius: 2px;
    background: linear-gradient(180deg, transparent, {SKY});
    animation: metgo-rain 0.85s linear infinite;
}}
.weather-scene-st__label {{
    position: absolute; bottom: 0; left: 0; right: 0; margin: 0; padding: 0.4rem;
    font-size: 0.72rem; font-weight: 600; text-align: center; color: {TEXT_SECONDARY};
    background: linear-gradient(180deg, transparent, rgba(255,255,255,0.85));
}}
.frost-badge-st {{
    display: inline-flex; align-items: center; gap: 0.35rem;
    color: {SKY_DEEP}; font-weight: 700; font-size: 0.75rem;
}}
.frost-badge-st svg {{ width: 1.4rem; height: 1.4rem; animation: metgo-frost 3s ease-in-out infinite; }}
@keyframes metgo-sun {{
    0%,100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.06); }}
}}
@keyframes metgo-cloud {{
    from {{ transform: translateX(-5px); }}
    to {{ transform: translateX(8px); }}
}}
@keyframes metgo-rain {{
    from {{ transform: translateY(-6px); opacity: 0; }}
    30% {{ opacity: 0.8; }}
    to {{ transform: translateY(22px); opacity: 0; }}
}}
@keyframes metgo-frost {{
    0%,100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.88; transform: scale(1.05) rotate(4deg); }}
}}
"""

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

PLOTLY_COLOR_SEQUENCE = [PRIMARY, SKY, ACCENT, SKY_DEEP, SUCCESS, MUTED, WARNING, DANGER]


def plotly_layout(title: str = "", **extra) -> dict:
    """Layout Plotly alineado al design system METGO.

    Acepta `title` (str) como primer argumento y cualquier kwarg extra de
    Plotly (height, margin, showlegend, barmode, hovermode, *_title, ...).
    Los kwargs extra SIEMPRE deben pasarse aquí dentro y no como argumentos
    separados de `update_layout`, para evitar `TypeError: got multiple
    values for keyword argument`.
    Uso correcto: `fig.update_layout(**plotly_layout("Título", height=400))`.
    """
    # Permitir plotly_layout(height=..., title="X") además del posicional.
    if not title and isinstance(extra.get("title"), str):
        title = extra.pop("title")

    base = {
        "paper_bgcolor": BG,
        "plot_bgcolor": SURFACE,
        "font": {"family": "DM Sans", "color": TEXT_SECONDARY},
        "colorway": PLOTLY_COLOR_SEQUENCE,
        "margin": {"l": 48, "r": 24, "t": 48 if title else 24, "b": 40},
        "xaxis": {"gridcolor": BORDER, "linecolor": BORDER},
        "yaxis": {"gridcolor": BORDER, "linecolor": BORDER},
    }
    if title:
        base["title"] = {"text": title, "font": {"family": "DM Sans", "color": TEXT, "size": 16}}
    base.update(extra)
    return base


FROST_SVG = (
    '<svg viewBox="0 0 64 64" aria-hidden="true">'
    '<path d="M32 4 L32 60 M32 32 L8 18 M32 32 L56 18 M32 32 L8 46 M32 32 L56 46 '
    'M32 16 L20 32 M32 16 L44 32 M32 48 L20 32 M32 48 L44 32" fill="none" '
    f'stroke="{SKY_DEEP}" stroke-width="2.5" stroke-linecap="round"/>'
    f'<circle cx="32" cy="32" r="4" fill="{SKY_DEEP}"/></svg>'
)


def frost_badge_html(label: str = "Helada") -> str:
    return f'<div class="frost-badge-st">{FROST_SVG}<span>{label}</span></div>'


def weather_scene_html(condition: str = "soleado", label: str = "") -> str:
    """condition: soleado | parcial | nublado | lluvioso | helada"""
    labels = {
        "soleado": "Soleado",
        "parcial": "Parcialmente nublado",
        "nublado": "Nublado",
        "lluvioso": "Lluvioso",
        "helada": "Riesgo de heladas",
    }
    lbl = label or labels.get(condition, condition)
    sun = '<div class="weather-scene-st__sun"></div>' if condition in ("soleado", "parcial") else ""
    cloud_a = ""
    cloud_b = ""
    if condition in ("parcial", "nublado", "lluvioso", "helada"):
        cloud_a = '<div class="weather-scene-st__cloud weather-scene-st__cloud--a"></div>'
    if condition in ("nublado", "lluvioso", "helada"):
        cloud_b = '<div class="weather-scene-st__cloud weather-scene-st__cloud--b"></div>'
    rain = ""
    if condition == "lluvioso":
        drops = "".join(
            f'<span style="left:{12 + i * 9}%; animation-delay:{-i * 0.1:.1f}s"></span>'
            for i in range(8)
        )
        rain = f'<div class="weather-scene-st__rain">{drops}</div>'
    frost = frost_badge_html(lbl) if condition == "helada" else ""
    return f"""
    <div class="weather-scene-st weather-scene-st--{condition}">
        {sun}{cloud_a}{cloud_b}{rain}{frost}
        <p class="weather-scene-st__label">{lbl}</p>
    </div>
    """


def main_header_html(title: str, subtitle: str = "", module: str = "meteo") -> str:
    color = MODULE_COLORS.get(module, PRIMARY)
    sub = f"<p style='margin:0.5rem 0 0; opacity:0.92; font-size:1rem;'>{subtitle}</p>" if subtitle else ""
    return f"""
    <div class="main-header" style="background: linear-gradient(135deg, {color} 0%, {ACCENT} 55%, {SKY} 100%);">
        <h1 style="margin:0; font-size:1.75rem;">{title}</h1>
        {sub}
    </div>
    """


def bootstrap_dashboard(title: str, subtitle: str = "", *, module: str = "meteo") -> None:
    """Inyecta tema METGO + cabecera unificada (llamar tras set_page_config)."""
    import streamlit as st

    inject_theme()
    st.markdown(main_header_html(title, subtitle, module), unsafe_allow_html=True)


def classify_weather_from_row(row: dict) -> str:
    """Clasificación visual compatible con Vue weatherCondition.js."""
    try:
        tmin = float(row.get("temperatura_min") or row.get("temp_min") or row.get("temperatura") or 15)
        precip = float(row.get("precipitacion") or 0)
        hum = float(row.get("humedad") or row.get("humedad_relativa") or 60)
        nub = float(row.get("nubosidad") or row.get("cobertura_nubosa") or max(0, min(100, 100 - hum + precip * 8)))
    except (TypeError, ValueError):
        return "parcial"
    if tmin <= 2:
        return "helada"
    if precip >= 2:
        return "lluvioso"
    if nub >= 70 or hum >= 88:
        return "nublado"
    if nub >= 35 or hum >= 68 or precip >= 0.3:
        return "parcial"
    return "soleado"


def is_streamlit_cloud() -> bool:
    """Detecta despliegue en Streamlit Community Cloud."""
    env = os.environ
    if env.get("STREAMLIT_RUNTIME_ENV") == "cloud":
        return True
    if env.get("IS_STREAMLIT_CLOUD", "").lower() in {"1", "true", "yes"}:
        return True
    # Community Cloud monta el repo en /mount/src/<repo>
    if os.path.isdir("/mount/src"):
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
    """Tarjeta de módulo con estilo Vue.

    Importante: sin indentación Markdown (4+ espacios = bloque de código y se ve el HTML crudo).
    """
    if cloud:
        return (
            f'<div class="metgo-module-card" style="border-left:4px solid {color};">'
            f'<h5 style="color:{color};margin:0 0 10px 0;">{nombre}</h5>'
            f'<p style="margin:0 0 10px 0;font-size:12px;color:{TEXT_SECONDARY};">{descripcion}</p>'
            f'<p style="margin:0;font-size:11px;color:{MUTED};">'
            "En la nube: use Vue (Netlify) o Visor de puerto — los :850x solo existen en PC local."
            "</p></div>"
        )
    btn = (
        f'<a href="{url}" target="_blank" class="metgo-btn" style="background-color:{color};">Acceder</a>'
        if url.startswith("http")
        else ""
    )
    puerto_line = (
        f'<p style="margin:0 0 8px 0;font-size:10px;color:{MUTED};">Puerto local: {puerto}</p>'
        if puerto and puerto != "—"
        else ""
    )
    return (
        f'<div class="metgo-module-card" style="border-left:4px solid {color};">'
        f'<h5 style="color:{color};margin:0 0 10px 0;">{nombre}</h5>'
        f'<p style="margin:0 0 8px 0;font-size:12px;color:{TEXT_SECONDARY};">{descripcion}</p>'
        f"{puerto_line}{btn}"
        f'<p style="margin:8px 0 0;font-size:11px;color:{MUTED};">Red local · compatible móvil</p>'
        "</div>"
    )
