import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")

from api_rest.services import (
    comparativo_estaciones,
    historico_meteo,
    nombre_a_slug,
)
from datos_reales_openmeteo import obtener_datos_meteorologicos_reales
from meteo_dashboard_utils import (
    dia_iso,
    filtrar_historico_hasta_hoy,
    hoy_chile,
    nubosidad_estimada,
    probabilidad_niebla,
)

DATOS_REALES_DISPONIBLES = True

from metgo.streamlit_theme import bootstrap_dashboard, weather_scene_html, classify_weather_from_row, PLOTLY_CONFIG, plotly_layout

# Estaciones alineadas con API (valle) + referencia regional (OpenMeteo)
ESTACIONES_VALLE = ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"]
ESTACIONES_EXTRA = ["Santiago", "Valparaiso", "Vina del Mar", "Casablanca"]
ESTACIONES_TODAS = ESTACIONES_VALLE + ESTACIONES_EXTRA
OPCIONES_ESTACION = ["Todas las Estaciones"] + ESTACIONES_TODAS

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="Visualizaciones Avanzadas - METGO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bootstrap_dashboard(
    "Visualizaciones Avanzadas",
    "Gráficos meteorológicos, heladas y análisis agrícola",
    module="visual",
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional */
    .main-header {
        background: linear-gradient(135deg, #3d6b52 0%, #5a9b72 55%, #5b9bd5 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .info-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
            margin: 0.25rem 0;
        }
        
        .chart-container {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal con diseño profesional
st.markdown("""
<div class="main-header">
    <h1>📊 Visualizaciones Avanzadas</h1>
    <h3>Sistema METGO - Análisis Interactivo</h3>
    <p>Visualizaciones profesionales optimizadas para dispositivos móviles</p>
</div>
""", unsafe_allow_html=True)

# Sidebar colapsado para móviles
with st.sidebar:
    st.markdown("### 🎛️ Controles")
    
    # Selector de período
    periodo = st.selectbox(
        "📅 Período de Análisis:",
        ["Últimos 7 días", "Últimos 30 días", "Últimos 3 meses", "Últimos 6 meses", "Último año", "Últimos 5 años"],
        key="periodo_selector"
    )
    
    # Selector de tipo de visualización
    tipo_viz = st.selectbox(
        "📊 Tipo de Visualización:",
        ["Tendencias Temporales", "Comparaciones", "Distribuciones", "Correlaciones", "Mapas de Calor", "Análisis 3D"],
        key="viz_selector"
    )
    
    # Selector de estación (por defecto: todas)
    estacion = st.selectbox(
        "🌍 Estación:",
        OPCIONES_ESTACION,
        index=0,
        key="estacion_selector",
    )

# Función para generar datos avanzados (API valle + OpenMeteo regional)
@st.cache_data(ttl=600, show_spinner=False)
def generar_datos_visualizaciones_avanzados(periodo, estacion):
    """Genera datos avanzados para visualizaciones multi-estación."""

    dias_map = {
        "Últimos 7 días": 7,
        "Últimos 30 días": 30,
        "Últimos 3 meses": 90,
        "Últimos 6 meses": 180,
        "Último año": 365,
        "Últimos 5 años": 1825,
    }

    dias = min(dias_map[periodo], 92)
    hoy = hoy_chile()
    if estacion == "Todas las Estaciones":
        estaciones_objetivo = list(ESTACIONES_TODAS)
    else:
        estaciones_objetivo = [estacion]

    datos_completos = []

    for est in estaciones_objetivo:
        try:
            if est in ESTACIONES_VALLE:
                slug = nombre_a_slug(est)
                hist = filtrar_historico_hasta_hoy(historico_meteo(slug, dias) or [])
                fuente_base = "API METGO"
                if not hist and DATOS_REALES_DISPONIBLES:
                    df_om = obtener_datos_meteorologicos_reales(est, "historicos", dias)
                    if df_om is not None and not df_om.empty:
                        for _, row in df_om.iterrows():
                            if dia_iso(row.get("fecha")) > hoy:
                                continue
                            tp = float(row.get("temperatura_promedio") or 0)
                            datos_completos.append(
                                _fila_visual(
                                    row["fecha"],
                                    est,
                                    tp,
                                    float(row.get("temperatura_min") or tp - 4),
                                    float(row.get("temperatura_max") or tp + 4),
                                    float(row.get("precipitacion") or 0),
                                    float(row.get("humedad_relativa") or 0),
                                    float(row.get("presion_atmosferica") or 1013),
                                    float(row.get("velocidad_viento") or 0),
                                    tp,
                                    "OpenMeteo",
                                )
                            )
                        continue
                if not hist:
                    continue
                for row in hist:
                    fecha = pd.to_datetime(dia_iso(row.get("fecha")))
                    temp_prom = float(row.get("temperatura") or row.get("temperatura_max") or 0)
                    temp_min = float(row.get("temperatura_min") or temp_prom - 4)
                    temp_max = float(row.get("temperatura_max") or temp_prom + 4)
                    humedad = float(row.get("humedad") or 0)
                    viento = float(row.get("viento") or 0)
                    sensacion = temp_prom * (1 + (humedad - 50) * 0.01) * (1 + (viento / 10) * 0.1)
                    sensacion = max(-10, min(50, sensacion))
                    datos_completos.append(
                        _fila_visual(
                            fecha,
                            est,
                            temp_prom,
                            temp_min,
                            temp_max,
                            float(row.get("precipitacion") or 0),
                            humedad,
                            float(row.get("presion") or 1013),
                            viento,
                            sensacion,
                            fuente_base,
                            hora=12,
                        )
                    )
            elif DATOS_REALES_DISPONIBLES:
                datos_reales = obtener_datos_meteorologicos_reales(est, "historicos", min(dias, 92))
                if datos_reales is not None and len(datos_reales) > 0:
                    for _, row in datos_reales.iterrows():
                        if dia_iso(row.get("fecha")) > hoy:
                            continue
                        sensacion = row["temperatura_promedio"] * (
                            1 + (row["humedad_relativa"] - 50) * 0.01
                        ) * (1 + (row["velocidad_viento"] / 10) * 0.1)
                        sensacion = max(-10, min(50, sensacion))
                        datos_completos.append(
                            _fila_visual(
                                row["fecha"],
                                est,
                                row["temperatura_promedio"],
                                row["temperatura_min"],
                                row["temperatura_max"],
                                row["precipitacion"],
                                row["humedad_relativa"],
                                row["presion_atmosferica"],
                                row["velocidad_viento"],
                                sensacion,
                                "OpenMeteo",
                                hora=12,
                            )
                        )
        except Exception as e:
            st.warning(f"No se pudieron obtener datos para {est}: {e}")

    if not datos_completos:
        return pd.DataFrame()
    return pd.DataFrame(datos_completos)


def _fila_visual(
    fecha,
    estacion,
    temp_prom,
    temp_min,
    temp_max,
    precipitacion,
    humedad,
    presion,
    viento,
    sensacion,
    fuente,
    hora=12,
):
    """Fila normalizada para gráficos Plotly del dashboard 8506."""
    fecha = pd.to_datetime(fecha)
    return {
        "Fecha": fecha,
        "Estacion": estacion,
        "Temperatura": round(float(temp_prom), 1),
        "Temperatura_Min": round(float(temp_min), 1),
        "Temperatura_Max": round(float(temp_max), 1),
        "Precipitacion": round(float(precipitacion), 2),
        "Humedad": round(float(humedad), 1),
        "Presion": round(float(presion), 1),
        "Viento": round(float(viento), 1),
        "Nubosidad": nubosidad_estimada(humedad),
        "Probabilidad_Niebla": probabilidad_niebla(humedad),
        "Indice_Helada": round(max(0, 32 - temp_min) if temp_min < 5 else 0, 1),
        "Sensacion_Termica_Agricola": round(float(sensacion), 1),
        "Rendimiento": round(20 + temp_prom * 0.5 + humedad * 0.1, 1),
        "Calidad": round(min(100, max(0, 70 + temp_prom * 0.3 + humedad * 0.2)), 1),
        "Mes": fecha.month,
        "DiaSemana": fecha.strftime("%A"),
        "Hora": hora,
        "Fuente": fuente,
    }

# Información sobre datos reales
st.success(
    f"🌐 **Valle de Aconcagua:** API METGO + OpenMeteo · histórico hasta **{hoy_chile()}** (Chile). "
    "Interfaz principal: Vue http://127.0.0.1:5173/meteo/comparativo"
)

# Resumen actual multi-estación (siempre visible)
try:
    resumen_valle = comparativo_estaciones()
    if resumen_valle:
        st.markdown("### 🌍 Resumen actual · Valle de Aconcagua")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Estación": r.get("estacion"),
                        "T° máx": f"{r.get('temperatura_max')}°C",
                        "T° mín": f"{r.get('temperatura_min')}°C",
                        "Lluvia": f"{r.get('precipitacion')} mm",
                        "Viento": f"{r.get('viento')} km/h",
                        "Humedad": f"{r.get('humedad')}%",
                    }
                    for r in resumen_valle
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.caption(f"No se pudo cargar resumen multi-estación: {e}")

# Generar datos
with st.spinner('📊 Generando datos para visualizaciones...'):
    df = generar_datos_visualizaciones_avanzados(periodo, estacion)

if df.empty:
    st.error("Sin datos para la selección actual. Pruebe «Todas las Estaciones» o sincronice ETL en la API.")
    st.stop()

estaciones_cargadas = sorted(df["Estacion"].unique())
st.info(
    f"**Estaciones con datos:** {', '.join(estaciones_cargadas)} "
    f"({len(estaciones_cargadas)} de {len(ESTACIONES_TODAS) if estacion == 'Todas las Estaciones' else 1})"
)

# Botón de descarga de datos
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"**📊 Datos Generados:** {len(df)} registros para {estacion}")

with col2:
    # Convertir DataFrame a CSV
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Descargar CSV",
        data=csv_data,
        file_name=f"datos_meteorologicos_{estacion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    # Convertir DataFrame a Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos_Meteorologicos', index=False)
    excel_data = excel_buffer.getvalue()
    
    st.download_button(
        label="📊 Descargar Excel",
        data=excel_data,
        file_name=f"datos_meteorologicos_{estacion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Métricas principales con diseño profesional
st.markdown("### 📈 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    temp_prom = df['Temperatura'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: #e74c3c; margin: 0;">🌡️ Temperatura</h4>
        <h2 style="color: #2c3e50; margin: 0.5rem 0;">{temp_prom:.1f}°C</h2>
        <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Promedio del período</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    precip_total = df['Precipitacion'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: #3498db; margin: 0;">🌧️ Precipitación</h4>
        <h2 style="color: #2c3e50; margin: 0.5rem 0;">{precip_total:.1f} mm</h2>
        <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Total acumulado</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    humedad_prom = df['Humedad'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: #9b59b6; margin: 0;">💧 Humedad</h4>
        <h2 style="color: #2c3e50; margin: 0.5rem 0;">{humedad_prom:.1f}%</h2>
        <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Promedio del período</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    rendimiento_prom = df['Rendimiento'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: #27ae60; margin: 0;">🌾 Rendimiento</h4>
        <h2 style="color: #2c3e50; margin: 0.5rem 0;">{rendimiento_prom:.1f} t/ha</h2>
        <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Producción estimada</p>
    </div>
    """, unsafe_allow_html=True)

# Nueva sección: Análisis de Nubosidad, Niebla y Heladas
st.markdown("### 🌤️ Análisis Avanzado de Condiciones Atmosféricas")

# Métricas específicas para nubosidad, niebla y heladas
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    nubosidad_prom = df['Nubosidad'].mean()
    st.metric("☁️ Nubosidad Promedio", f"{nubosidad_prom:.1f}%")

with col2:
    nubosidad_max = df['Nubosidad'].max()
    st.metric("☁️ Nubosidad Máxima", f"{nubosidad_max:.1f}%")

with col3:
    niebla_prom = df['Probabilidad_Niebla'].mean()
    st.metric("🌫️ Prob. Niebla Prom.", f"{niebla_prom:.1f}%")

with col4:
    niebla_max = df['Probabilidad_Niebla'].max()
    st.metric("🌫️ Prob. Niebla Máx.", f"{niebla_max:.1f}%")

with col5:
    heladas_dias = len(df[df['Indice_Helada'] > 0])
    st.metric("❄️ Días con Helada", f"{heladas_dias}")

with col6:
    helada_max = df['Indice_Helada'].max()
    st.metric("❄️ Índice Helada Máx.", f"{helada_max:.1f}")

# Gráficos específicos para nubosidad, niebla y heladas
col1, col2 = st.columns(2)

with col1:
    # Gráfico de nubosidad
    fig_nubosidad = go.Figure()
    
    for estacion in df['Estacion'].unique():
        df_est = df[df['Estacion'] == estacion]
        fig_nubosidad.add_trace(go.Scatter(
            x=df_est['Fecha'], 
            y=df_est['Nubosidad'],
            name=f'Nubosidad {estacion}',
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=6)
        ))
    
    fig_nubosidad.update_layout(
        **plotly_layout(
            "☁️ Evolución de Nubosidad (%)",
            xaxis_title="Fecha",
            yaxis_title="Nubosidad (%)",
            height=400,
            hovermode="x unified",
        )
    )
    
    st.plotly_chart(fig_nubosidad, config=PLOTLY_CONFIG, use_container_width=True)

with col2:
    # Gráfico de probabilidad de niebla
    fig_niebla = go.Figure()
    
    for estacion in df['Estacion'].unique():
        df_est = df[df['Estacion'] == estacion]
        fig_niebla.add_trace(go.Scatter(
            x=df_est['Fecha'], 
            y=df_est['Probabilidad_Niebla'],
            name=f'Prob. Niebla {estacion}',
            mode='lines+markers',
            line=dict(width=3, color='#87CEEB'),
            marker=dict(size=6)
        ))
    
    fig_niebla.update_layout(
        **plotly_layout(
            "🌫️ Probabilidad de Niebla (%)",
            xaxis_title="Fecha",
            yaxis_title="Probabilidad de Niebla (%)",
            height=400,
            hovermode="x unified",
        )
    )
    
    st.plotly_chart(fig_niebla, config=PLOTLY_CONFIG, use_container_width=True)

# Análisis detallado de heladas con explicaciones
st.markdown("#### ❄️ Análisis Detallado de Heladas y Sensación Térmica Agrícola")

# Explicación del índice de heladas
st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #2196f3;">
    <h4 style="color: #1976d2; margin: 0 0 15px 0;">📚 ¿Qué es el Índice de Helada?</h4>
    <p style="margin: 5px 0; color: #424242;"><strong>• Índice de Helada:</strong> Mide qué tan severa es una helada basándose en la temperatura mínima del día.</p>
    <p style="margin: 5px 0; color: #424242;"><strong>• Cálculo:</strong> Índice = 32°C - Temperatura Mínima (cuando la temperatura mínima es menor a 5°C)</p>
    <p style="margin: 5px 0; color: #424242;"><strong>• Interpretación:</strong></p>
    <ul style="margin: 5px 0; color: #424242;">
        <li><strong>0-5°C:</strong> Helada leve - Daño mínimo a cultivos resistentes</li>
        <li><strong>5-10°C:</strong> Helada moderada - Daño a cultivos sensibles</li>
        <li><strong>10-15°C:</strong> Helada severa - Daño extenso a la mayoría de cultivos</li>
        <li><strong>>15°C:</strong> Helada extrema - Destrucción total de cultivos</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Asegurar min/máx diarios (sin aleatoriedad; datos API ya traen el rango)
if "Temperatura_Min" not in df.columns:
    df["Temperatura_Min"] = df["Temperatura"] - 4
if "Temperatura_Max" not in df.columns:
    df["Temperatura_Max"] = df["Temperatura"] + 4
df["Temperatura_Min"] = df["Temperatura_Min"].fillna(df["Temperatura"] - 4)
df["Temperatura_Max"] = df["Temperatura_Max"].fillna(df["Temperatura"] + 4)

# Recalcular el índice de heladas usando temperatura mínima
df['Indice_Helada_Corregido'] = df.apply(lambda row: max(0, 32 - row['Temperatura_Min']) if row['Temperatura_Min'] < 5 else 0, axis=1)

# Calcular sensación térmica agrícola
def calcular_sensacion_termica_agricola(temp, humedad, viento):
    """Calcula la sensación térmica específica para el sector agrícola"""
    # Factor de humedad para agricultura (mayor humedad = mayor sensación de frío)
    factor_humedad = 1 + (humedad - 50) * 0.01
    
    # Factor de viento para agricultura (viento = mayor pérdida de calor)
    factor_viento = 1 + (viento / 10) * 0.1
    
    # Sensación térmica agrícola
    sensacion = temp * factor_humedad * factor_viento
    
    # Aplicar límites realistas
    sensacion = max(-10, min(50, sensacion))
    
    return round(sensacion, 1)

df['Sensacion_Termica_Agricola'] = df.apply(
    lambda row: calcular_sensacion_termica_agricola(row['Temperatura'], row['Humedad'], row['Viento']), 
    axis=1
)

# Métricas de heladas corregidas
col1, col2, col3, col4 = st.columns(4)

with col1:
    heladas_dias_corregido = len(df[df['Indice_Helada_Corregido'] > 0])
    st.metric("❄️ Días con Helada", f"{heladas_dias_corregido}")

with col2:
    helada_max_corregido = df['Indice_Helada_Corregido'].max()
    st.metric("❄️ Helada Más Severa", f"{helada_max_corregido:.1f}°C")

with col3:
    temp_min_global = df['Temperatura_Min'].min()
    st.metric("🌡️ Temp. Mínima Registrada", f"{temp_min_global:.1f}°C")

with col4:
    sensacion_min = df['Sensacion_Termica_Agricola'].min()
    st.metric("🥶 Sensación Térmica Mín", f"{sensacion_min:.1f}°C")

# Gráfico de heladas corregido
fig_heladas = go.Figure()

for estacion in df['Estacion'].unique():
    df_est = df[df['Estacion'] == estacion]
    
    # Crear barras para días con heladas (usando índice corregido)
    heladas_dias = df_est[df_est['Indice_Helada_Corregido'] > 0]
    if len(heladas_dias) > 0:
        fig_heladas.add_trace(go.Bar(
            x=heladas_dias['Fecha'],
            y=heladas_dias['Indice_Helada_Corregido'],
            name=f'Heladas {estacion}',
            marker=dict(color='#4169E1', opacity=0.7),
            text=[f"Temp. Min: {row['Temperatura_Min']:.1f}°C<br>Índice: {row['Indice_Helada_Corregido']:.1f}°C" 
                  for _, row in heladas_dias.iterrows()],
            textposition='auto',
            hovertemplate=f"<b>{estacion}</b><br>" +
                         "Fecha: %{x}<br>" +
                         "Índice de Helada: %{y:.1f}°C<br>" +
                         "Temp. Mínima: %{customdata[0]:.1f}°C<br>" +
                         "Sensación Térmica: %{customdata[1]:.1f}°C<br>" +
                         "<extra></extra>",
            customdata=list(zip(heladas_dias['Temperatura_Min'], heladas_dias['Sensacion_Termica_Agricola']))
        ))

fig_heladas.update_layout(
    **plotly_layout(
        "❄️ Índice de Heladas por Estación (Basado en Temperatura Mínima)",
        xaxis_title="Fecha",
        yaxis_title="Índice de Helada (°C)",
        height=500,
        barmode="group",
        hovermode="closest",
    )
)

st.plotly_chart(fig_heladas, config=PLOTLY_CONFIG, use_container_width=True)

# Gráfico de sensación térmica agrícola
st.markdown("##### 🌡️ Sensación Térmica Agrícola")

fig_sensacion = go.Figure()

for estacion in df['Estacion'].unique():
    df_est = df[df['Estacion'] == estacion]
    
    fig_sensacion.add_trace(go.Scatter(
        x=df_est['Fecha'],
        y=df_est['Sensacion_Termica_Agricola'],
        name=f'Sensación {estacion}',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=6),
        hovertemplate=f"<b>{estacion}</b><br>" +
                     "Fecha: %{x}<br>" +
                     "Sensación Térmica: %{y:.1f}°C<br>" +
                     "Temp. Real: %{customdata[0]:.1f}°C<br>" +
                     "Humedad: %{customdata[1]:.1f}%<br>" +
                     "Viento: %{customdata[2]:.1f} km/h<br>" +
                     "<extra></extra>",
        customdata=list(zip(df_est['Temperatura'], df_est['Humedad'], df_est['Viento']))
    ))

fig_sensacion.update_layout(
    **plotly_layout(
        "🌡️ Sensación Térmica Agrícola por Estación",
        xaxis_title="Fecha",
        yaxis_title="Sensación Térmica (°C)",
        height=400,
        hovermode="x unified",
    )
)

st.plotly_chart(fig_sensacion, config=PLOTLY_CONFIG, use_container_width=True)

# Explicación de la sensación térmica agrícola
st.markdown("""
<div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #9c27b0;">
    <h4 style="color: #7b1fa2; margin: 0 0 15px 0;">🌡️ Sensación Térmica Agrícola</h4>
    <p style="margin: 5px 0; color: #424242;"><strong>¿Qué es?</strong> La temperatura que realmente "sienten" los cultivos considerando humedad y viento.</p>
    <p style="margin: 5px 0; color: #424242;"><strong>Factores que influyen:</strong></p>
    <ul style="margin: 5px 0; color: #424242;">
        <li><strong>Humedad alta:</strong> Aumenta la sensación de frío (mayor conductividad térmica)</li>
        <li><strong>Viento:</strong> Aumenta la pérdida de calor por convección</li>
        <li><strong>Temperatura base:</strong> Punto de partida para el cálculo</li>
    </ul>
    <p style="margin: 5px 0; color: #424242;"><strong>Impacto agrícola:</strong> Ayuda a predecir mejor el daño por frío en cultivos, especialmente en condiciones de alta humedad y viento.</p>
</div>
""", unsafe_allow_html=True)

# Tabla de resumen de heladas por estación
st.markdown("##### 📊 Resumen de Heladas por Estación")

resumen_heladas = df.groupby('Estacion').agg({
    'Temperatura_Min': ['min', 'mean'],
    'Indice_Helada_Corregido': ['max', 'mean', 'sum'],
    'Sensacion_Termica_Agricola': ['min', 'mean']
}).round(2)

# Flatten column names
resumen_heladas.columns = ['_'.join(col).strip() for col in resumen_heladas.columns]
resumen_heladas = resumen_heladas.reset_index()

# Renombrar columnas para mejor comprensión
resumen_heladas = resumen_heladas.rename(columns={
    'Estacion': 'Estación',
    'Temperatura_Min_min': 'Temp. Mín. Absoluta (°C)',
    'Temperatura_Min_mean': 'Temp. Mín. Promedio (°C)',
    'Indice_Helada_Corregido_max': 'Helada Más Severa (°C)',
    'Indice_Helada_Corregido_mean': 'Índice Helada Promedio (°C)',
    'Indice_Helada_Corregido_sum': 'Índice Helada Total (°C)',
    'Sensacion_Termica_Agricola_min': 'Sensación Térmica Mín (°C)',
    'Sensacion_Termica_Agricola_mean': 'Sensación Térmica Promedio (°C)'
})

st.dataframe(resumen_heladas, use_container_width=True)

# Análisis horario detallado (si hay datos horarios)
if 'Hora' in df.columns and df['Hora'].nunique() > 1:
    st.markdown("#### 🕐 Análisis Horario Detallado")
    
    # Seleccionar estación para análisis horario
    estacion_horaria = st.selectbox(
        "Seleccionar estación para análisis horario:",
        df['Estacion'].unique(),
        key="estacion_horaria"
    )
    
    df_horario = df[df['Estacion'] == estacion_horaria]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de temperatura por hora
        fig_temp_hora = px.box(
            df_horario, 
            x='Hora', 
            y='Temperatura',
            title=f"🌡️ Distribución de Temperatura por Hora - {estacion_horaria}",
            labels={'Hora': 'Hora del Día', 'Temperatura': 'Temperatura (°C)'}
        )
        fig_temp_hora.update_layout(height=400)
        st.plotly_chart(fig_temp_hora, config=PLOTLY_CONFIG, use_container_width=True)
    
    with col2:
        # Gráfico de humedad por hora
        fig_hum_hora = px.box(
            df_horario, 
            x='Hora', 
            y='Humedad',
            title=f"💧 Distribución de Humedad por Hora - {estacion_horaria}",
            labels={'Hora': 'Hora del Día', 'Humedad': 'Humedad Relativa (%)'}
        )
        fig_hum_hora.update_layout(height=400)
        st.plotly_chart(fig_hum_hora, config=PLOTLY_CONFIG, use_container_width=True)
    
    # Análisis de patrones horarios
    st.markdown("##### 📊 Patrones Horarios Detectados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hora_temp_min = df_horario.loc[df_horario['Temperatura'].idxmin(), 'Hora']
        st.metric("🕐 Hora Temperatura Mínima", f"{hora_temp_min:02d}:00")
    
    with col2:
        hora_temp_max = df_horario.loc[df_horario['Temperatura'].idxmax(), 'Hora']
        st.metric("🕐 Hora Temperatura Máxima", f"{hora_temp_max:02d}:00")
    
    with col3:
        hora_hum_max = df_horario.loc[df_horario['Humedad'].idxmax(), 'Hora']
        st.metric("🕐 Hora Humedad Máxima", f"{hora_hum_max:02d}:00")

# Análisis de localidades (estaciones)
st.markdown("#### 🌍 Análisis Comparativo por Localidades")

# Crear gráfico de comparación entre estaciones
fig_comparacion = make_subplots(
    rows=2, cols=2,
    subplot_titles=('🌡️ Temperatura por Estación', '💧 Humedad por Estación', 
                   '☁️ Nubosidad por Estación', '🌫️ Prob. Niebla por Estación'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]]
)

for i, variable in enumerate(['Temperatura', 'Humedad', 'Nubosidad', 'Probabilidad_Niebla']):
    row = (i // 2) + 1
    col = (i % 2) + 1
    
    for estacion in df['Estacion'].unique():
        df_est = df[df['Estacion'] == estacion]
        fig_comparacion.add_trace(
            go.Scatter(
                x=df_est['Fecha'], 
                y=df_est[variable],
                name=f'{estacion}',
                mode='lines+markers',
                line=dict(width=2)
            ),
            row=row, col=col
        )

fig_comparacion.update_layout(
    height=800,
    title_text="🌍 Comparación de Variables Meteorológicas por Localidad",
    showlegend=True
)

fig_comparacion.update_xaxes(title_text="Fecha")
fig_comparacion.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
fig_comparacion.update_yaxes(title_text="Humedad (%)", row=1, col=2)
fig_comparacion.update_yaxes(title_text="Nubosidad (%)", row=2, col=1)
fig_comparacion.update_yaxes(title_text="Prob. Niebla (%)", row=2, col=2)

st.plotly_chart(fig_comparacion, config=PLOTLY_CONFIG, use_container_width=True)

# Resumen estadístico por localidad
st.markdown("##### 📊 Resumen Estadístico por Localidad")

estadisticas_por_estacion = df.groupby('Estacion').agg({
    'Temperatura': ['mean', 'min', 'max', 'std'],
    'Humedad': ['mean', 'min', 'max', 'std'],
    'Nubosidad': ['mean', 'min', 'max', 'std'],
    'Probabilidad_Niebla': ['mean', 'min', 'max', 'std'],
    'Indice_Helada': ['mean', 'min', 'max', 'std']
}).round(2)

# Flatten column names
estadisticas_por_estacion.columns = ['_'.join(col).strip() for col in estadisticas_por_estacion.columns]
estadisticas_por_estacion = estadisticas_por_estacion.reset_index()

st.dataframe(estadisticas_por_estacion, use_container_width=True)

# Visualizaciones según tipo seleccionado
if tipo_viz == "Tendencias Temporales":
    st.markdown("### 📈 Análisis de Tendencias Temporales")
    
    # Gráfico de líneas múltiples
    fig_tendencias = make_subplots(
        rows=2, cols=1,
        subplot_titles=('🌡️ Evolución de Temperatura', '🌧️ Precipitación Acumulada'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
    )
    
    # Temperatura
    for estacion in df['Estacion'].unique():
        df_est = df[df['Estacion'] == estacion]
        fig_tendencias.add_trace(
            go.Scatter(x=df_est['Fecha'], y=df_est['Temperatura'], 
                      name=f'Temperatura {estacion}', mode='lines+markers',
                      line=dict(width=3)),
            row=1, col=1
        )
    
    # Precipitación
    for estacion in df['Estacion'].unique():
        df_est = df[df['Estacion'] == estacion]
        fig_tendencias.add_trace(
            go.Scatter(x=df_est['Fecha'], y=df_est['Precipitacion'], 
                      name=f'Precipitación {estacion}', mode='lines+markers',
                      line=dict(width=3), yaxis='y2'),
            row=2, col=1
        )
    
    fig_tendencias.update_layout(height=800, title_text="📊 Tendencias Temporales - Análisis Avanzado")
    fig_tendencias.update_xaxes(title_text="Fecha")
    fig_tendencias.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
    fig_tendencias.update_yaxes(title_text="Precipitación (mm)", row=2, col=1)
    
    st.plotly_chart(fig_tendencias, config=PLOTLY_CONFIG, use_container_width=True)

elif tipo_viz == "Comparaciones":
    st.markdown("### 🔄 Análisis Comparativo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparación por estación
        df_estaciones = df.groupby('Estacion').agg({
            'Temperatura': 'mean',
            'Precipitacion': 'sum',
            'Humedad': 'mean',
            'Rendimiento': 'mean'
        }).reset_index()
        
        fig_comparacion = px.bar(df_estaciones, x='Estacion', y=['Temperatura', 'Precipitacion', 'Humedad'],
                                title='📊 Comparación por Estación',
                                color_discrete_sequence=['#e74c3c', '#3498db', '#9b59b6'])
        fig_comparacion.update_layout(height=400)
        st.plotly_chart(fig_comparacion, config=PLOTLY_CONFIG, use_container_width=True)
    
    with col2:
        # Radar chart
        fig_radar = go.Figure()
        
        for estacion in df['Estacion'].unique()[:3]:  # Limitamos a 3 para claridad
            df_est = df[df['Estacion'] == estacion]
            valores = [
                df_est['Temperatura'].mean(),
                df_est['Precipitacion'].sum(),
                df_est['Humedad'].mean(),
                df_est['Rendimiento'].mean(),
                df_est['Calidad'].mean()
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=valores,
                theta=['Temperatura', 'Precipitación', 'Humedad', 'Rendimiento', 'Calidad'],
                fill='toself',
                name=estacion
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title="📊 Análisis Multivariable",
            height=400
        )
        
        st.plotly_chart(fig_radar, config=PLOTLY_CONFIG, use_container_width=True)

elif tipo_viz == "Distribuciones":
    st.markdown("### 📊 Análisis de Distribuciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histograma de temperaturas
        fig_hist = px.histogram(df, x='Temperatura', nbins=30,
                               title='📈 Distribución de Temperaturas',
                               color_discrete_sequence=['#e74c3c'])
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, config=PLOTLY_CONFIG, use_container_width=True)
    
    with col2:
        # Box plot por estación
        fig_box = px.box(df, x='Estacion', y='Temperatura',
                        title='📦 Distribución de Temperaturas por Estación',
                        color='Estacion')
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, config=PLOTLY_CONFIG, use_container_width=True)

elif tipo_viz == "Correlaciones":
    st.markdown("### 🔗 Análisis de Correlaciones")
    
    # Matriz de correlación
    numeric_cols = ['Temperatura', 'Precipitacion', 'Humedad', 'Presion', 'Viento', 'Rendimiento', 'Calidad']
    corr_matrix = df[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_matrix, 
                        text_auto=True,
                        aspect="auto",
                        title="🔗 Matriz de Correlación",
                        color_continuous_scale='RdBu_r')
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, config=PLOTLY_CONFIG, use_container_width=True)

elif tipo_viz == "Mapas de Calor":
    st.markdown("### 🗺️ Mapas de Calor")
    
    # Mapa de calor temporal
    df_heatmap = df.pivot_table(values='Temperatura', 
                               index='Estacion', 
                               columns=df['Fecha'].dt.date, 
                               aggfunc='mean')
    
    fig_heatmap = px.imshow(df_heatmap,
                           title="🌡️ Mapa de Calor - Temperaturas por Estación y Fecha",
                           color_continuous_scale='RdYlBu_r')
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, config=PLOTLY_CONFIG, use_container_width=True)

elif tipo_viz == "Análisis 3D":
    st.markdown("### 🎯 Análisis Tridimensional")
    
    # Gráfico 3D
    fig_3d = px.scatter_3d(df, x='Temperatura', y='Humedad', z='Rendimiento',
                          color='Estacion',
                          title="🎯 Análisis 3D: Temperatura vs Humedad vs Rendimiento",
                          size='Calidad',
                          opacity=0.7)
    fig_3d.update_layout(height=600)
    st.plotly_chart(fig_3d, config=PLOTLY_CONFIG, use_container_width=True)

# Análisis estadístico avanzado
st.markdown("### 📊 Análisis Estadístico Avanzado")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Estadísticas Descriptivas")
    stats = df[['Temperatura', 'Precipitacion', 'Humedad', 'Rendimiento']].describe()
    st.dataframe(stats.round(2), use_container_width=True)

with col2:
    st.markdown("#### 📊 Análisis por Estación")
    estacion_stats = df.groupby('Estacion')[['Temperatura', 'Precipitacion', 'Humedad', 'Rendimiento']].mean()
    st.dataframe(estacion_stats.round(2), use_container_width=True)

# Alertas y recomendaciones
st.markdown("### 🚨 Alertas y Recomendaciones")

col1, col2, col3 = st.columns(3)

with col1:
    # Alertas basadas en datos
    temp_max = df['Temperatura'].max()
    if temp_max > 35:
        st.markdown(f"""
        <div class="alert-card">
            <h4>🌡️ Alerta de Temperatura</h4>
            <p>Temperatura máxima: {temp_max:.1f}°C</p>
            <p>Recomendación: Monitorear cultivos</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-card">
            <h4>✅ Temperatura Normal</h4>
            <p>Temperatura máxima: {temp_max:.1f}°C</p>
            <p>Condiciones óptimas</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # Análisis de precipitación
    precip_total = df['Precipitacion'].sum()
    if precip_total > 50:
        st.markdown(f"""
        <div class="info-card">
            <h4>🌧️ Alta Precipitación</h4>
            <p>Total: {precip_total:.1f} mm</p>
            <p>Verificar drenaje</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-card">
            <h4>💧 Precipitación Adecuada</h4>
            <p>Total: {precip_total:.1f} mm</p>
            <p>Niveles normales</p>
        </div>
        """, unsafe_allow_html=True)

with col3:
    # Análisis de rendimiento
    rendimiento_prom = df['Rendimiento'].mean()
    if rendimiento_prom > 25:
        st.markdown(f"""
        <div class="success-card">
            <h4>🌾 Excelente Rendimiento</h4>
            <p>Promedio: {rendimiento_prom:.1f} t/ha</p>
            <p>Producción óptima</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-card">
            <h4>📈 Mejorable</h4>
            <p>Promedio: {rendimiento_prom:.1f} t/ha</p>
            <p>Optimizar condiciones</p>
        </div>
        """, unsafe_allow_html=True)

# Información del análisis
st.markdown("### ℹ️ Información del Análisis")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **📅 Período:** {periodo}
    **🌍 Estación:** {estacion}
    **📊 Tipo:** {tipo_viz}
    **🕐 Registros:** {len(df):,} mediciones
    """)

with col2:
    st.info(f"""
    **📈 Datos Generados:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Actualización:** Automática
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Profesional
    """)

with col3:
    st.info(f"""
    **🌡️ Temp. Promedio:** {df['Temperatura'].mean():.1f}°C
    **🌧️ Precip. Total:** {df['Precipitacion'].sum():.1f} mm
    **💧 Humedad Promedio:** {df['Humedad'].mean():.1f}%
    **🌾 Rendimiento Promedio:** {df['Rendimiento'].mean():.1f} t/ha
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>📊 <strong>Sistema METGO</strong> - Visualizaciones Avanzadas</p>
    <p>Análisis interactivo profesional optimizado para dispositivos móviles</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
