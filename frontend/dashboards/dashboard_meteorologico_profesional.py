#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dashboard meteorológico profesional (puerto 8502) — datos OpenMeteo vía API METGO."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_DASH = Path(__file__).resolve().parent
_ROOT = _DASH.parents[1]
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")

from api_rest.services import historico_meteo, nombre_a_slug, pronostico_meteo, resumen_meteo
from datos_reales_openmeteo import obtener_datos_meteorologicos_reales
from meteo_dashboard_utils import hoy_chile as _hoy_chile_util

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Análisis Meteorológico Profesional",
    "Quillota y región · histórico y pronóstico (OpenMeteo)",
    module="meteo",
    page_icon="M",
)

ESTACIONES = {
    "Quillota": {"lat": -32.8834, "lon": -71.2489, "altura": 120},
    "Los Nogales": {"lat": -32.8500, "lon": -71.2000, "altura": 150},
    "Hijuelas": {"lat": -32.8167, "lon": -71.1833, "altura": 200},
    "Limache": {"lat": -33.0167, "lon": -71.2667, "altura": 80},
    "Olmue": {"lat": -33.0000, "lon": -71.2167, "altura": 100},
}

DIAS_MAP = {
    "Últimos 30 días": 30,
    "Últimos 3 meses": 90,
    "Últimos 6 meses": 180,
    "Último año": 365,
    "Últimos 5 años": 92,
}


def _hoy_chile() -> str:
    return _hoy_chile_util()


def _to_celsius_display(value_c: float, unidad: str) -> float:
    if unidad == "F":
        return value_c * 9 / 5 + 32
    return value_c


def _unidad_suffix(unidad: str) -> str:
    return "°F" if unidad == "F" else "°C"


def _punto_rocio_c(temp_c: float, rh: float) -> float:
    if rh <= 0:
        return temp_c
    a, b = 17.27, 237.7
    alpha = (a * temp_c) / (b + temp_c) + np.log(rh / 100.0)
    return (b * alpha) / (a - alpha)


def _indice_calor_c(temp_c: float, rh: float) -> float:
    """Aproximación índice de calor (solo relevante T > 27 °C)."""
    if temp_c < 27:
        return temp_c
    t_f = temp_c * 9 / 5 + 32
    hi = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * rh
        - 0.22475541 * t_f * rh
        - 0.00683783 * t_f**2
        - 0.05481717 * rh**2
        + 0.00122874 * t_f**2 * rh
        + 0.00085282 * t_f * rh**2
        - 0.00000199 * t_f**2 * rh**2
    )
    return (hi - 32) * 5 / 9


def _filas_a_dataframe(filas: list[dict], unidad_temp: str) -> pd.DataFrame:
    datos = []
    for row in filas:
        fecha = pd.to_datetime(str(row.get("fecha", ""))[:10])
        temp_c = float(row.get("temperatura") or 0)
        tmax_c = float(row.get("temperatura_max") or temp_c)
        tmin_c = float(row.get("temperatura_min") or temp_c)
        humedad = float(row.get("humedad") or 0)
        temp_show = _to_celsius_display(temp_c, unidad_temp)
        tmax_show = _to_celsius_display(tmax_c, unidad_temp)
        tmin_show = _to_celsius_display(tmin_c, unidad_temp)
        pr = _punto_rocio_c(temp_c, humedad)
        pr_show = _to_celsius_display(pr, unidad_temp)
        calor_c = _indice_calor_c(tmax_c, humedad)
        calor_show = _to_celsius_display(calor_c, unidad_temp)
        datos.append(
            {
                "Fecha": fecha,
                "Temperatura_C": round(temp_show, 1),
                "Temperatura_Max_C": round(tmax_show, 1),
                "Temperatura_Min_C": round(tmin_show, 1),
                "Humedad_%": round(humedad, 1),
                "Presion_hPa": round(float(row.get("presion") or 0), 1),
                "Viento_kmh": round(float(row.get("viento") or 0), 1),
                "Precipitacion_mm": round(float(row.get("precipitacion") or 0), 2),
                "Punto_Rocio_C": round(pr_show, 1),
                "Indice_Calor_C": round(calor_show, 1),
                "Fuente": row.get("fuente", "METGO"),
            }
        )
    return pd.DataFrame(datos).sort_values("Fecha").reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_datos_meteorologicos(estacion: str, periodo: str, tipo_datos: str) -> tuple[pd.DataFrame, str]:
    """Datos reales: API METGO (store + OpenMeteo) o fallback directo OpenMeteo."""
    slug = nombre_a_slug(estacion)
    dias = min(DIAS_MAP.get(periodo, 30), 92)
    hoy = _hoy_chile()
    filas: list[dict] = []
    fuente = "API METGO + OpenMeteo"

    try:
        if tipo_datos.startswith("Pronóstico"):
            pron_dias = 7 if "7" in tipo_datos else 15
            filas = pronostico_meteo(slug, pron_dias) or []
            filas = [r for r in filas if str(r.get("fecha", ""))[:10] >= hoy]
            fuente = "OpenMeteo pronóstico (America/Santiago)"
        else:
            filas = historico_meteo(slug, dias) or []
            filas = [r for r in filas if str(r.get("fecha", ""))[:10] <= hoy]
            fuente = "Histórico METGO (OpenMeteo + store local)"
    except Exception:
        filas = []

    if not filas:
        buf = io.StringIO()
        tipo_om = "pronostico" if tipo_datos.startswith("Pronóstico") else "historicos"
        with redirect_stdout(buf):
            df_om = obtener_datos_meteorologicos_reales(
                estacion, tipo_om, min(dias, 92)
            )
        if df_om is not None and not df_om.empty:
            fuente = "OpenMeteo directo"
            for _, row in df_om.sort_values("fecha").iterrows():
                dia = str(row["fecha"])[:10]
                if tipo_om == "historicos" and dia > hoy:
                    continue
                if tipo_om == "pronostico" and dia < hoy:
                    continue
                filas.append(
                    {
                        "fecha": dia,
                        "temperatura": row.get("temperatura_promedio"),
                        "temperatura_max": row.get("temperatura_max"),
                        "temperatura_min": row.get("temperatura_min"),
                        "humedad": row.get("humedad_relativa"),
                        "viento": row.get("velocidad_viento"),
                        "precipitacion": row.get("precipitacion"),
                        "presion": row.get("presion_atmosferica"),
                        "fuente": row.get("fuente_datos", "openmeteo"),
                    }
                )

    if not filas:
        return pd.DataFrame(), "sin_datos"

    return _filas_a_dataframe(filas, "C"), fuente


def _metricas_actuales(estacion: str, df: pd.DataFrame, unidad_temp: str) -> dict:
    """Valores del día en Chile y delta vs día anterior (misma unidad que Vue)."""
    slug = nombre_a_slug(estacion)
    resumen = resumen_meteo(slug)
    suf = _unidad_suffix(unidad_temp)

    def conv(c):
        return _to_celsius_display(float(c), unidad_temp)

    if resumen:
        temp = conv(resumen.get("temperatura") or 0)
        hum = float(resumen.get("humedad") or 0)
        pres = float(resumen.get("presion") or 0)
        viento = float(resumen.get("viento") or 0)
        fuente_hoy = resumen.get("fuente", "METGO")
    elif len(df) >= 1:
        last = df.iloc[-1]
        temp = float(last["Temperatura_C"])
        hum = float(last["Humedad_%"])
        pres = float(last["Presion_hPa"])
        viento = float(last["Viento_kmh"])
        fuente_hoy = str(last.get("Fuente", "histórico"))
    else:
        return {}

    delta_temp = delta_hum = delta_pres = delta_viento = None
    if len(df) >= 2:
        prev = df.iloc[-2]
        delta_temp = temp - float(prev["Temperatura_C"])
        delta_hum = hum - float(prev["Humedad_%"])
        delta_pres = pres - float(prev["Presion_hPa"])
        delta_viento = viento - float(prev["Viento_kmh"])

    return {
        "temp": (temp, delta_temp, suf),
        "hum": (hum, delta_hum, "%"),
        "pres": (pres, delta_pres, " hPa"),
        "viento": (viento, delta_viento, " km/h"),
        "fuente": fuente_hoy,
    }


# --- Sidebar ---
st.sidebar.markdown("### Panel de Control")
estacion_seleccionada = st.sidebar.selectbox(
    "Estación Meteorológica:", list(ESTACIONES.keys())
)
periodo_analisis = st.sidebar.selectbox(
    "Período de Análisis:",
    list(DIAS_MAP.keys()),
)
tipo_datos = st.sidebar.selectbox(
    "Tipo de Datos:",
    ["Datos Históricos", "Pronóstico 7 días", "Pronóstico 15 días", "Análisis Comparativo"],
)
unidad_temp = st.sidebar.radio(
    "Unidad de temperatura",
    options=["C", "F"],
    format_func=lambda u: "Celsius (°C)" if u == "C" else "Fahrenheit (°F)",
    horizontal=True,
    help="Misma preferencia que la SPA Vue (Configuración → Preferencias).",
)

with st.spinner("Cargando datos meteorológicos (OpenMeteo)…"):
    df_raw, fuente_datos = cargar_datos_meteorologicos(
        estacion_seleccionada, periodo_analisis, tipo_datos
    )

if df_raw.empty or fuente_datos == "sin_datos":
    st.error(
        "No hay datos disponibles para esta estación. "
        "Verifique la API en :8080 o sincronice ETL desde Vue (/meteo/historico)."
    )
    st.stop()


def _aplicar_unidad_temp(df: pd.DataFrame, unidad: str) -> pd.DataFrame:
    out = df.copy()
    if unidad != "F":
        return out
    for col in (
        "Temperatura_C",
        "Temperatura_Max_C",
        "Temperatura_Min_C",
        "Punto_Rocio_C",
        "Indice_Calor_C",
    ):
        if col in out.columns:
            out[col] = out[col].apply(lambda v: round(v * 9 / 5 + 32, 1))
    return out


df_meteo = _aplicar_unidad_temp(df_raw, unidad_temp)

st.success(f"**{fuente_datos}** · {len(df_meteo)} registros diarios · hoy {_hoy_chile()} (Chile)")

metricas = _metricas_actuales(estacion_seleccionada, df_meteo, unidad_temp)
suf_temp = _unidad_suffix(unidad_temp)

col1, col2, col3, col4 = st.columns(4)
if metricas:
    t, dt, _ = metricas["temp"]
    h, dh, _ = metricas["hum"]
    p, dp, us_p = metricas["pres"]
    v, dv, us_v = metricas["viento"]
    with col1:
        st.metric(
            "Temperatura Actual",
            f"{t:.1f}{suf_temp}",
            f"{dt:+.1f}{suf_temp}" if dt is not None else None,
        )
    with col2:
        st.metric("Humedad Relativa", f"{h:.1f}%", f"{dh:+.1f}%"if dh is not None else None)
    with col3:
        st.metric("Presión Atmosférica", f"{p:.1f}{us_p}", f"{dp:+.1f}{us_p}"if dp is not None else None)
    with col4:
        st.metric("Velocidad del Viento", f"{v:.1f}{us_v}", f"{dv:+.1f}{us_v}"if dv is not None else None)
    st.caption(f"Condición del día · fuente: **{metricas.get('fuente', 'METGO')}**")

st.markdown("### Análisis Meteorológico Avanzado")

fig_temp_hum = make_subplots(
    rows=2,
    cols=1,
    subplot_titles=(
        f"Temperatura diaria ({suf_temp})",
        "Humedad relativa",
    ),
    vertical_spacing=0.12,
)
fig_temp_hum.add_trace(
    go.Scatter(
        x=df_meteo["Fecha"],
        y=df_meteo["Temperatura_C"],
        name=f"Media ({suf_temp})",
        line=dict(color="#1a5f4a", width=2),
    ),
    row=1,
    col=1,
)
fig_temp_hum.add_trace(
    go.Scatter(
        x=df_meteo["Fecha"],
        y=df_meteo["Temperatura_Max_C"],
        name=f"Máx ({suf_temp})",
        line=dict(color="#FF6B35", width=1, dash="dot"),
    ),
    row=1,
    col=1,
)
fig_temp_hum.add_trace(
    go.Scatter(
        x=df_meteo["Fecha"],
        y=df_meteo["Temperatura_Min_C"],
        name=f"Mín ({suf_temp})",
        line=dict(color="#5b9bd5", width=1, dash="dot"),
    ),
    row=1,
    col=1,
)
fig_temp_hum.add_trace(
    go.Scatter(
        x=df_meteo["Fecha"],
        y=df_meteo["Humedad_%"],
        name="Humedad (%)",
        line=dict(color="#4ECDC4", width=2),
    ),
    row=2,
    col=1,
)
fig_temp_hum.update_layout(**plotly_layout(height=520), showlegend=True, title_text="Variables principales")
fig_temp_hum.update_yaxes(title_text=f"Temperatura ({suf_temp})", row=1, col=1)
fig_temp_hum.update_yaxes(title_text="Humedad (%)", row=2, col=1)
st.plotly_chart(fig_temp_hum, use_container_width=True, config=PLOTLY_CONFIG)

col1, col2 = st.columns(2)
with col1:
    fig_presion = go.Figure()
    fig_presion.add_trace(
        go.Scatter(
            x=df_meteo["Fecha"],
            y=df_meteo["Presion_hPa"],
            name="Presión",
            line=dict(color="#667eea", width=2),
            fill="tozeroy",
        )
    )
    fig_presion.update_layout(**plotly_layout("Presión atmosférica", height=400, yaxis_title="hPa"))
    st.plotly_chart(fig_presion, use_container_width=True, config=PLOTLY_CONFIG)

with col2:
    fig_viento = go.Figure()
    fig_viento.add_trace(
        go.Scatter(
            x=df_meteo["Fecha"],
            y=df_meteo["Viento_kmh"],
            name="Viento",
            line=dict(color="#764ba2", width=2),
            fill="tozeroy",
        )
    )
    fig_viento.update_layout(**plotly_layout("Velocidad del viento", height=400, yaxis_title="km/h"))
    st.plotly_chart(fig_viento, use_container_width=True, config=PLOTLY_CONFIG)

fig_precip = go.Figure()
fig_precip.add_trace(
    go.Bar(
        x=df_meteo["Fecha"],
        y=df_meteo["Precipitacion_mm"],
        name="Precipitación",
        marker_color="#4ECDC4",
    )
)
fig_precip.update_layout(**plotly_layout("Precipitación diaria (mm)", height=380))
st.plotly_chart(fig_precip, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("### Variables derivadas")
col1, col2, col3 = st.columns(3)
with col1:
    fig_rocio = px.line(df_meteo, x="Fecha", y="Punto_Rocio_C", title=f"Punto de rocío ({suf_temp})")
    fig_rocio.update_layout(**plotly_layout(height=380))
    st.plotly_chart(fig_rocio, use_container_width=True, config=PLOTLY_CONFIG)
with col2:
    fig_calor = px.line(df_meteo, x="Fecha", y="Indice_Calor_C", title=f"Índice de calor ({suf_temp})")
    fig_calor.update_layout(**plotly_layout(height=380))
    st.plotly_chart(fig_calor, use_container_width=True, config=PLOTLY_CONFIG)
with col3:
    st.info(
        "Radiación e índice UV no están en la serie diaria OpenMeteo de este módulo. "
        "Use Vue `/meteo` o amplíe el ETL (fase 3+)."
    )

st.markdown("### Análisis estadístico")
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Estadísticas descriptivas")
    stats = df_meteo[
        ["Temperatura_C", "Humedad_%", "Presion_hPa", "Viento_kmh", "Precipitacion_mm"]
    ].describe()
    st.dataframe(stats.round(2))
with col2:
    st.markdown(f"#### Distribución de temperaturas ({suf_temp})")
    fig_hist = px.histogram(
        df_meteo,
        x="Temperatura_C",
        nbins=min(30, max(5, len(df_meteo) // 2)),
        title="Distribución temperatura media diaria",
        color_discrete_sequence=["#34d399"],
    )
    fig_hist.update_layout(**plotly_layout(height=380))
    st.plotly_chart(fig_hist, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("### Información de la estación")
col1, col2, col3 = st.columns(3)
info = ESTACIONES[estacion_seleccionada]
with col1:
    st.info(
        f"** Estación:** {estacion_seleccionada}\n\n"
        f"** Coordenadas:** {info['lat']:.4f}, {info['lon']:.4f}\n\n"
        f"** Altura:** {info['altura']} m.s.n.m."
    )
with col2:
    st.info(
        f"** Período:** {periodo_analisis}\n\n"
        f"** Tipo:** {tipo_datos}\n\n"
        f"** Registros:** {len(df_meteo):,} días\n\n"
        f"** Frecuencia:** Diaria (OpenMeteo)"
    )
with col3:
    st.info(
        f"** Temp. promedio:** {df_meteo['Temperatura_C'].mean():.1f}{suf_temp}\n\n"
        f"** Humedad promedio:** {df_meteo['Humedad_%'].mean():.1f}%\n\n"
        f"** Presión promedio:** {df_meteo['Presion_hPa'].mean():.1f} hPa\n\n"
        f"** Viento promedio:** {df_meteo['Viento_kmh'].mean():.1f} km/h"
    )

st.markdown("---")
st.markdown(
    f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <p> <strong>Sistema METGO</strong> - Análisis Meteorológico Profesional</p>
    <p>Datos: <strong>{fuente_datos}</strong> · alineado con API REST y SPA Vue</p>
    <p>Última actualización: {datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m-%d %H:%M:%S")} (Chile)</p>
</div>
""",
    unsafe_allow_html=True,
)

