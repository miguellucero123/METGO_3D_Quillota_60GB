import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("05_api_rest")

from api_rest.services import (
    ESTACIONES_PRINCIPALES,
    historico_meteo,
    metricas_globales,
    slug_a_nombre,
)
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from meteo_dashboard_utils import dia_iso, filtrar_historico_hasta_hoy, hoy_chile

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="Dashboard Global de Métricas - METGO",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap_dashboard(
    "Dashboard Global de Métricas",
    "KPIs integrados del ecosistema METGO 3D",
    module="global",
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional */
    .global-header {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-global-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        margin: 1rem 0;
        border: 1px solid #334155;
        position: relative;
        overflow: hidden;
    }
    
    .metric-global-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00b894, #10b981, #38bdf8, #0ea5e9);
    }
    
    .kpi-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f8fafc;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 1rem;
        color: #94a3b8;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .kpi-positive {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .kpi-negative {
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
    }
    
    .kpi-neutral {
        background: linear-gradient(135deg, #334155, #475569);
        color: #f8fafc;
    }
    
    .chart-container-global {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #f8fafc;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00b894;
        display: inline-block;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .global-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .metric-global-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .kpi-number {
            font-size: 2rem;
        }
        
        .chart-container-global {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="global-header">
    <h1> Dashboard Global de Métricas</h1>
    <h3>Sistema METGO — Valle de Aconcagua</h3>
    <p>KPIs en vivo y series históricas desde API / OpenMeteo (máx. 92 días por estación)</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Panel de Control Global")
    
    # Selector de período
    periodo_global = st.selectbox(
        "Período de Análisis:",
        ["Últimos 5 años", "Últimos 3 años", "Últimos 2 años", "Último año", "Últimos 6 meses"],
        key="periodo_global"
    )
    
    granularidad = st.selectbox(
        "Granularidad:",
        ["Diaria", "Semanal", "Mensual", "Anual"],
        key="granularidad",
    )


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_historico_global(periodo: str) -> pd.DataFrame:
    """Series meteorológicas reales agregadas por estación principal."""
    periodos_dias = {
        "Últimos 5 años": 1825,
        "Últimos 3 años": 1095,
        "Últimos 2 años": 730,
        "Último año": 365,
        "Últimos 6 meses": 183,
    }
    dias_periodo = periodos_dias.get(periodo, 365)
    dias = min(dias_periodo, 92)
    filas: list[dict] = []

    for slug in ESTACIONES_PRINCIPALES:
        hist = filtrar_historico_hasta_hoy(historico_meteo(slug, dias) or [])
        nombre = slug_a_nombre(slug)
        for row in hist:
            fecha = pd.to_datetime(dia_iso(row.get("fecha")))
            temp = float(row.get("temperatura") or row.get("temperatura_max") or 0)
            filas.append(
                {
                    "Fecha": fecha,
                    "Estacion": nombre,
                    "Temperatura": temp,
                    "Precipitacion": float(row.get("precipitacion") or 0),
                    "Humedad": float(row.get("humedad") or 0),
                    "Viento": float(row.get("viento") or 0),
                }
            )

    if not filas:
        return pd.DataFrame()
    df = pd.DataFrame(filas)
    df = df.sort_values("Fecha")
    return df


def _agregar_granularidad(df: pd.DataFrame, granularidad: str) -> pd.DataFrame:
    if df.empty:
        return df
    freq_map = {"Diaria": "D", "Semanal": "W", "Mensual": "ME", "Anual": "YE"}
    freq = freq_map.get(granularidad, "D")
    if freq == "D":
        return df
    out = (
        df.set_index("Fecha")
        .groupby(["Estacion", pd.Grouper(freq=freq)])
        .agg(
            {
                "Temperatura": "mean",
                "Precipitacion": "sum",
                "Humedad": "mean",
                "Viento": "mean",
            }
        )
        .reset_index()
    )
    return out


# KPIs en vivo (API) — mismo contrato que Vue /metricas
try:
    mg = metricas_globales()
    if mg.get("estaciones_activas", 0) > 0:
        st.markdown("### Valle de Aconcagua · datos en vivo")
        st.caption(f"Día de referencia **{mg.get('referencia_fecha', hoy_chile())}** · Vue http://127.0.0.1:5173/metricas")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Estaciones", mg["estaciones_activas"])
        c2.metric("T° máx media", f"{mg.get('temperatura_media_max')}°C")
        c3.metric("T° mín media", f"{mg.get('temperatura_media_min')}°C")
        c4.metric("Precip. total", f"{mg.get('precipitacion_total')} mm")
        c5.metric("Viento máx", f"{mg.get('viento_max')} km/h")
        c6.metric("Alertas", mg.get("alertas_activas", 0))
        if mg.get("detalle_estaciones"):
            st.dataframe(
                pd.DataFrame(mg["detalle_estaciones"])[
                    [
                        "estacion",
                        "temperatura_max",
                        "temperatura_min",
                        "precipitacion",
                        "viento",
                        "humedad",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
except Exception as e:
    st.warning(f"API METGO no disponible para KPIs en vivo: {e}")

with st.spinner("Cargando histórico meteorológico…"):
    df_global = cargar_historico_global(periodo_global)

if df_global.empty:
    st.warning("Sin datos históricos — requiere ETL Archive")
    st.stop()

df_plot = _agregar_granularidad(df_global, granularidad)

st.markdown("### Indicadores históricos (meteorología real)")

col1, col2, col3, col4 = st.columns(4)

temp_prom = df_global["Temperatura"].mean()
precip_total = df_global["Precipitacion"].sum()
humedad_prom = df_global["Humedad"].mean()
viento_prom = df_global["Viento"].mean()

with col1:
    st.markdown(f"""<div class="metric-global-card">
        <div class="kpi-label"> Temperatura media</div>
        <div class="kpi-number">{temp_prom:.1f}°C</div>
        <div class="kpi-change kpi-neutral">{len(df_global):,} registros</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-global-card">
        <div class="kpi-label"> Precipitación acumulada</div>
        <div class="kpi-number">{precip_total:.1f} mm</div>
        <div class="kpi-change kpi-neutral">{df_global['Estacion'].nunique()} estaciones</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-global-card">
        <div class="kpi-label"> Humedad media</div>
        <div class="kpi-number">{humedad_prom:.1f}%</div>
        <div class="kpi-change kpi-neutral">OpenMeteo / API</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-global-card">
        <div class="kpi-label"> Viento medio</div>
        <div class="kpi-number">{viento_prom:.1f} km/h</div>
        <div class="kpi-change kpi-neutral">Período: {periodo_global}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<h2 class="section-title"> Tendencias históricas</h2>', unsafe_allow_html=True)

fig_tendencias = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "Temperatura media",
        "Precipitación",
        "Humedad media",
        "Viento medio",
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.08,
)

for est in df_plot["Estacion"].unique():
    dfe = df_plot[df_plot["Estacion"] == est]
    fig_tendencias.add_trace(
        go.Scatter(x=dfe["Fecha"], y=dfe["Temperatura"], name=f"T° {est}", mode="lines"),
        row=1,
        col=1,
    )
    fig_tendencias.add_trace(
        go.Bar(x=dfe["Fecha"], y=dfe["Precipitacion"], name=f"Precip. {est}", showlegend=False),
        row=1,
        col=2,
    )
    fig_tendencias.add_trace(
        go.Scatter(x=dfe["Fecha"], y=dfe["Humedad"], name=f"Humedad {est}", mode="lines", showlegend=False),
        row=2,
        col=1,
    )
    fig_tendencias.add_trace(
        go.Scatter(x=dfe["Fecha"], y=dfe["Viento"], name=f"Viento {est}", mode="lines", showlegend=False),
        row=2,
        col=2,
    )

fig_tendencias.update_layout(
    **plotly_layout(
        "Series meteorológicas por estación",
        height=620,
        showlegend=True,
        hovermode="x unified",
    )
)
fig_tendencias.update_xaxes(title_text="Fecha")
fig_tendencias.update_yaxes(title_text="°C", row=1, col=1)
fig_tendencias.update_yaxes(title_text="mm", row=1, col=2)
fig_tendencias.update_yaxes(title_text="%", row=2, col=1)
fig_tendencias.update_yaxes(title_text="km/h", row=2, col=2)

st.plotly_chart(fig_tendencias, config=PLOTLY_CONFIG, use_container_width=True)

st.markdown('<h2 class="section-title"> Comparación por estación</h2>', unsafe_allow_html=True)

df_est = (
    df_global.groupby("Estacion")
    .agg(
        Temperatura=("Temperatura", "mean"),
        Precipitacion=("Precipitacion", "sum"),
        Humedad=("Humedad", "mean"),
        Viento=("Viento", "mean"),
    )
    .reset_index()
)

fig_comp = px.bar(
    df_est.melt(id_vars="Estacion", var_name="Variable", value_name="Valor"),
    x="Estacion",
    y="Valor",
    color="Variable",
    barmode="group",
    title="Promedios y acumulados por estación",
)
fig_comp.update_layout(**plotly_layout(height=420))
st.plotly_chart(fig_comp, config=PLOTLY_CONFIG, use_container_width=True)

st.markdown('<h2 class="section-title"> Información del análisis</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    dias_cargados = min(
        92,
        {
            "Últimos 5 años": 1825,
            "Últimos 3 años": 1095,
            "Últimos 2 años": 730,
            "Último año": 365,
            "Últimos 6 meses": 183,
        }.get(periodo_global, 365),
    )
    st.info(f"""** Período solicitado:** {periodo_global}
    **Ventana cargada:** {dias_cargados} días (máx. API)
    ** Granularidad:** {granularidad}
    ** Registros:** {len(df_global):,}""")

with col2:
    st.info(f"""** Última carga:** {datetime.now().strftime("%H:%M:%S")}
    **Estaciones:** {', '.join(sorted(df_global['Estacion'].unique()))}
    **Fuente:** API METGO / OpenMeteo""")

with col3:
    st.info(f"""** Temp. media:** {temp_prom:.1f}°C
    ** Precip. total:** {precip_total:.1f} mm
    ** Humedad media:** {humedad_prom:.1f}%
    ** Viento medio:** {viento_prom:.1f} km/h""")

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #94a3b8; padding: 20px;">
    <p> <strong>Sistema METGO</strong> — Dashboard Global de Métricas</p>
    <p>Última actualización: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
</div>
""", unsafe_allow_html=True)
