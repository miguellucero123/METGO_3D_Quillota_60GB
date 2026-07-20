import streamlit as st
from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("02_agricola", "05_api_rest")

from api_rest.services import (
    comparativo_estaciones,
    historico_meteo,
    nombre_a_slug,
    reporte_agricola_avanzado,
)
from agricola_dashboard_utils import CULTIVO_A_SLUG, ESTACIONES_VALLE, cargar_contexto_agricola
from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Agricultura de Precisión",
    "Análisis de cultivos con datos históricos Quillota",
    module="precision",
    page_icon="🌾",
    initial_sidebar_state="collapsed",
)

# CSS complementario
st.markdown("""
<style>
    /* Diseño móvil profesional para agricultura */
    .precision-header {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .precision-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
    }
    
    .precision-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #27ae60, #2ecc71, #16a085, #1abc9c);
    }
    
    .precision-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .precision-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .precision-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .precision-positive {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
    }
    
    .precision-negative {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
    }
    
    .precision-neutral {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
    }
    
    .chart-precision-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-precision {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #27ae60;
        display: inline-block;
    }
    
    .zone-card {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .precision-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .precision-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .precision-number {
            font-size: 2rem;
        }
        
        .chart-precision-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="precision-header">
    <h1>🌾 Agricultura de Precisión</h1>
    <h3>Sistema METGO - Tecnología Avanzada</h3>
    <p>Monitoreo preciso, análisis de zonas y optimización inteligente de cultivos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control de Precisión")
    
    # Selector de cultivo
    cultivo_precision = st.selectbox(
        "🌱 Cultivo:",
        ["Palta", "Cítricos", "Vid", "Tomate", "Lechuga", "Todos los Cultivos"],
        key="cultivo_precision"
    )
    
    # Selector de zona
    zona_precision = st.selectbox(
        "📍 Zona de Análisis:",
        ["Zona A - Norte", "Zona B - Centro", "Zona C - Sur", "Zona D - Este", "Zona E - Oeste", "Todas las Zonas"],
        key="zona_precision"
    )
    
    # Selector de tecnología
    tecnologia = st.selectbox(
        "🤖 Tecnología:",
        ["Sensores IoT", "Drones", "Satélites", "IA/ML", "Sistema Integrado"],
        key="tecnologia"
    )

    modo_precision = st.radio(
        "Fuente de datos",
        ["API METGO (valle)", "Series ilustrativas (5 años)"],
        index=0,
    )

    if modo_precision.startswith("API"):
        est_p = st.selectbox("🌍 Estación", ESTACIONES_VALLE, key="est_api_p")
        cult_p = st.selectbox("🌱 Cultivo", list(CULTIVO_A_SLUG.keys()), key="cult_api_p")

if modo_precision.startswith("API"):
    slug_p = nombre_a_slug(est_p)

    with st.spinner("Cargando precisión agrícola (API)…"):
        ctx_p = cargar_contexto_agricola(est_p, cult_p)
        hist_p = filtrar_historico_hasta_hoy(historico_meteo(slug_p, 30) or [])
        valle_p = comparativo_estaciones()
        rep_p = reporte_agricola_avanzado(slug_p)

    st.success(f"**API METGO** · {est_p} · {hoy_chile()} · Vue http://127.0.0.1:5173/agricola")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T° actual", f"{ctx_p['temperatura']:.1f}°C")
    c2.metric("Humedad", f"{ctx_p['humedad']:.0f}%")
    c3.metric("Riego sugerido", f"{ctx_p.get('riego', {}).get('mm_sugeridos_hoy', '—')} mm")
    c4.metric("Lluvia hoy", f"{ctx_p['precipitacion']:.1f} mm")

    if hist_p:
        df_h = pd.DataFrame(
            [
                {
                    "fecha": r["fecha"],
                    "humedad": r.get("humedad"),
                    "precipitacion": r.get("precipitacion"),
                    "temperatura": r.get("temperatura"),
                }
                for r in hist_p
            ]
        )
        fig_h = make_subplots(rows=2, cols=1, subplot_titles=("Humedad (%)", "Precipitación (mm)"))
        fig_h.add_trace(
            go.Scatter(x=df_h["fecha"], y=df_h["humedad"], name="Humedad"),
            row=1,
            col=1,
        )
        fig_h.add_trace(
            go.Bar(x=df_h["fecha"], y=df_h["precipitacion"], name="Lluvia"),
            row=2,
            col=1,
        )
        fig_h.update_layout(height=420, title=f"Histórico 30 días · {est_p}")
        st.plotly_chart(fig_h, use_container_width=True, config=PLOTLY_CONFIG)

    if valle_p:
        st.markdown("### Comparación por estación (hoy)")
        st.dataframe(
            pd.DataFrame(valle_p)[
                ["estacion", "temperatura_max", "temperatura_min", "humedad", "precipitacion"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    if rep_p and not rep_p.get("error"):
        with st.expander("Reporte integral módulo 02", expanded=True):
            st.json(rep_p)
    elif rep_p:
        st.warning(rep_p.get("error", "Sin reporte avanzado"))

    for rec in ctx_p.get("recomendaciones_api") or []:
        st.info(f"**{rec.get('cultivo')}**: {rec.get('accion')} — {rec.get('motivo')}")

    st.stop()

st.sidebar.markdown("---")
st.sidebar.caption("Modo ilustrativo: series semanales simuladas")

# Función para generar datos de agricultura de precisión
@st.cache_data
def generar_datos_precision(cultivo, zona, tecnologia):
    """Genera datos de agricultura de precisión con 5 años de historia"""
    
    # Configuración de zonas
    zonas_config = {
        "Zona A - Norte": {"lat": -32.85, "lon": -71.20, "suelo": "arcilloso", "elevacion": 150},
        "Zona B - Centro": {"lat": -32.88, "lon": -71.25, "suelo": "franco", "elevacion": 120},
        "Zona C - Sur": {"lat": -32.90, "lon": -71.30, "suelo": "arenoso", "elevacion": 100},
        "Zona D - Este": {"lat": -32.87, "lon": -71.22, "suelo": "limoso", "elevacion": 180},
        "Zona E - Oeste": {"lat": -32.89, "lon": -71.28, "suelo": "franco-arenoso", "elevacion": 90}
    }
    
    # Configuración de cultivos
    cultivos_config = {
        "Palta": {"densidad": 150, "riego_optimo": 65, "ph_optimo": 6.5, "profundidad": 80},
        "Cítricos": {"densidad": 200, "riego_optimo": 70, "ph_optimo": 6.0, "profundidad": 60},
        "Vid": {"densidad": 300, "riego_optimo": 55, "ph_optimo": 6.8, "profundidad": 100},
        "Tomate": {"densidad": 2500, "riego_optimo": 75, "ph_optimo": 6.2, "profundidad": 40},
        "Lechuga": {"densidad": 4000, "riego_optimo": 80, "ph_optimo": 6.5, "profundidad": 20}
    }
    
    # Generar datos históricos de 5 años
    inicio = datetime.now() - timedelta(days=5*365)
    fechas = pd.date_range(start=inicio, end=datetime.now(), freq='W')  # Datos semanales
    
    datos = []
    
    for fecha in fechas:
        # Determinar qué zonas y cultivos incluir
        zonas_analizar = list(zonas_config.keys()) if zona == "Todas las Zonas" else [zona]
        cultivos_analizar = list(cultivos_config.keys()) if cultivo == "Todos los Cultivos" else [cultivo]
        
        for zona_act in zonas_analizar:
            for cultivo_act in cultivos_analizar:
                config_zona = zonas_config[zona_act]
                config_cultivo = cultivos_config[cultivo_act]
                
                # Variación estacional
                mes = fecha.month
                estacional = np.sin(2 * np.pi * mes / 12) * 0.3
                
                # Datos de suelo por zona
                humedad_suelo = config_cultivo["riego_optimo"] + estacional + np.random.normal(0, 8)
                ph_suelo = config_cultivo["ph_optimo"] + np.random.normal(0, 0.5)
                conductividad = 1.5 + np.random.normal(0, 0.3)
                materia_organica = 3.5 + np.random.normal(0, 0.8)
                
                # Datos de nutrientes
                nitrogeno = 45 + np.random.normal(0, 10)
                fosforo = 25 + np.random.normal(0, 8)
                potasio = 180 + np.random.normal(0, 30)
                
                # Datos de rendimiento por zona y cultivo
                rendimiento_base = {
                    "Palta": 15, "Cítricos": 25, "Vid": 12, "Tomate": 40, "Lechuga": 30
                }
                
                rendimiento = rendimiento_base[cultivo_act] * (1 + estacional) + np.random.normal(0, 2)
                
                # Datos de calidad
                calidad = 75 + estacional * 5 + np.random.normal(0, 8)
                calidad = max(0, min(100, calidad))
                
                # Eficiencia de riego por tecnología
                eficiencia_riego = {
                    "Sensores IoT": 85 + np.random.normal(0, 5),
                    "Drones": 80 + np.random.normal(0, 6),
                    "Satélites": 75 + np.random.normal(0, 7),
                    "IA/ML": 90 + np.random.normal(0, 4),
                    "Sistema Integrado": 95 + np.random.normal(0, 3)
                }
                
                eficiencia = eficiencia_riego[tecnologia]
                eficiencia = max(0, min(100, eficiencia))
                
                # Datos de plagas y enfermedades
                indice_plagas = np.random.uniform(0, 100)
                indice_enfermedades = np.random.uniform(0, 100)
                
                # Datos económicos
                costo_produccion = rendimiento * 50 + np.random.normal(0, 100)
                precio_venta = 800 + np.random.normal(0, 150)
                margen_ganancia = (precio_venta - costo_produccion / rendimiento) if rendimiento > 0 else 0
                
                datos.append({
                    'Fecha': fecha,
                    'Año': fecha.year,
                    'Mes': fecha.month,
                    'Zona': zona_act,
                    'Cultivo': cultivo_act,
                    'Latitud': config_zona["lat"] + np.random.normal(0, 0.01),
                    'Longitud': config_zona["lon"] + np.random.normal(0, 0.01),
                    'Elevacion': config_zona["elevacion"],
                    'Tipo_Suelo': config_zona["suelo"],
                    'Humedad_Suelo': round(humedad_suelo, 1),
                    'PH_Suelo': round(ph_suelo, 2),
                    'Conductividad': round(conductividad, 2),
                    'Materia_Organica': round(materia_organica, 2),
                    'Nitrogeno': round(nitrogeno, 1),
                    'Fosforo': round(fosforo, 1),
                    'Potasio': round(potasio, 1),
                    'Rendimiento': round(rendimiento, 1),
                    'Calidad': round(calidad, 1),
                    'Eficiencia_Riego': round(eficiencia, 1),
                    'Indice_Plagas': round(indice_plagas, 1),
                    'Indice_Enfermedades': round(indice_plagas, 1),
                    'Costo_Produccion': round(costo_produccion, 0),
                    'Precio_Venta': round(precio_venta, 0),
                    'Margen_Ganancia': round(margen_ganancia, 0),
                    'Tecnologia': tecnologia
                })
    
    return pd.DataFrame(datos)

st.warning(
    "Modo **ilustrativo**: series semanales simuladas (5 años). "
    "Use **API METGO** en el panel lateral para datos OpenMeteo reales."
)

# Generar datos
with st.spinner('🌾 Generando datos de agricultura de precisión...'):
    df_precision = generar_datos_precision(cultivo_precision, zona_precision, tecnologia)

# KPIs de precisión
st.markdown("### 🎯 Indicadores de Precisión")

col1, col2, col3, col4 = st.columns(4)

with col1:
    rendimiento_actual = df_precision['Rendimiento'].iloc[-1]
    rendimiento_promedio = df_precision['Rendimiento'].mean()
    variacion = ((rendimiento_actual - rendimiento_promedio) / rendimiento_promedio) * 100
    
    st.markdown(f"""
    <div class="precision-card">
        <div class="precision-label">🌾 Rendimiento Actual</div>
        <div class="precision-number">{rendimiento_actual:.1f} t/ha</div>
        <div class="precision-change {'precision-positive' if variacion > 0 else 'precision-negative' if variacion < 0 else 'precision-neutral'}">
            {variacion:+.1f}% vs promedio
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    eficiencia_actual = df_precision['Eficiencia_Riego'].iloc[-1]
    eficiencia_promedio = df_precision['Eficiencia_Riego'].mean()
    variacion_ef = eficiencia_actual - eficiencia_promedio
    
    st.markdown(f"""
    <div class="precision-card">
        <div class="precision-label">💧 Eficiencia Riego</div>
        <div class="precision-number">{eficiencia_actual:.1f}%</div>
        <div class="precision-change {'precision-positive' if variacion_ef > 0 else 'precision-negative' if variacion_ef < 0 else 'precision-neutral'}">
            {variacion_ef:+.1f}% vs promedio
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    calidad_actual = df_precision['Calidad'].iloc[-1]
    calidad_promedio = df_precision['Calidad'].mean()
    variacion_cal = calidad_actual - calidad_promedio
    
    st.markdown(f"""
    <div class="precision-card">
        <div class="precision-label">⭐ Calidad Producto</div>
        <div class="precision-number">{calidad_actual:.1f}%</div>
        <div class="precision-change {'precision-positive' if variacion_cal > 0 else 'precision-negative' if variacion_cal < 0 else 'precision-neutral'}">
            {variacion_cal:+.1f}% vs promedio
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    margen_actual = df_precision['Margen_Ganancia'].iloc[-1]
    margen_promedio = df_precision['Margen_Ganancia'].mean()
    variacion_marg = margen_actual - margen_promedio
    
    st.markdown(f"""
    <div class="precision-card">
        <div class="precision-label">💰 Margen Ganancia</div>
        <div class="precision-number">${margen_actual:.0f}</div>
        <div class="precision-change {'precision-positive' if variacion_marg > 0 else 'precision-negative' if variacion_marg < 0 else 'precision-neutral'}">
            ${variacion_marg:+.0f} vs promedio
        </div>
    </div>
    """, unsafe_allow_html=True)

# Análisis por zonas
st.markdown('<h2 class="section-title-precision">📍 Análisis por Zonas</h2>', unsafe_allow_html=True)

# Mapa de calor por zonas
df_zonas = df_precision.groupby('Zona').agg({
    'Rendimiento': 'mean',
    'Eficiencia_Riego': 'mean',
    'Calidad': 'mean',
    'Humedad_Suelo': 'mean',
    'PH_Suelo': 'mean'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    # Rendimiento por zona
    fig_rendimiento_zonas = px.bar(df_zonas, x='Zona', y='Rendimiento',
                                  title='🌾 Rendimiento Promedio por Zona',
                                  color='Rendimiento',
                                  color_continuous_scale='Greens')
    fig_rendimiento_zonas.update_layout(height=400)
    st.plotly_chart(fig_rendimiento_zonas, use_container_width=True)

with col2:
    # Eficiencia por zona
    fig_eficiencia_zonas = px.bar(df_zonas, x='Zona', y='Eficiencia_Riego',
                                 title='💧 Eficiencia de Riego por Zona',
                                 color='Eficiencia_Riego',
                                 color_continuous_scale='Blues')
    fig_eficiencia_zonas.update_layout(height=400)
    st.plotly_chart(fig_eficiencia_zonas, use_container_width=True)

# Análisis de suelos
st.markdown('<h2 class="section-title-precision">🌱 Análisis de Suelos</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Humedad del suelo por zona
    fig_humedad = px.box(df_precision, x='Zona', y='Humedad_Suelo',
                        title='💧 Distribución de Humedad del Suelo por Zona',
                        color='Zona')
    fig_humedad.update_layout(height=400)
    st.plotly_chart(fig_humedad, use_container_width=True)

with col2:
    # pH del suelo por zona
    fig_ph = px.box(df_precision, x='Zona', y='PH_Suelo',
                   title='🧪 Distribución de pH del Suelo por Zona',
                   color='Zona')
    fig_ph.update_layout(height=400)
    st.plotly_chart(fig_ph, use_container_width=True)

# Análisis de nutrientes
st.markdown('<h2 class="section-title-precision">🧪 Análisis de Nutrientes</h2>', unsafe_allow_html=True)

# Mapa de calor de nutrientes
nutrientes = df_precision[['Zona', 'Nitrogeno', 'Fosforo', 'Potasio', 'Materia_Organica']].groupby('Zona').mean()

fig_nutrientes = px.imshow(nutrientes.T,
                          text_auto=True,
                          aspect="auto",
                          title="🧪 Matriz de Nutrientes por Zona",
                          color_continuous_scale='YlOrRd')
fig_nutrientes.update_layout(height=500)
st.plotly_chart(fig_nutrientes, use_container_width=True)

# Tendencias históricas
st.markdown('<h2 class="section-title-precision">📈 Tendencias Históricas</h2>', unsafe_allow_html=True)

# Gráfico de tendencias
fig_tendencias = make_subplots(
    rows=2, cols=2,
    subplot_titles=('🌾 Evolución del Rendimiento', '💧 Eficiencia de Riego',
                   '⭐ Calidad del Producto', '💰 Margen de Ganancia'),
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# Agrupar por fecha para tendencias
df_tendencias = df_precision.groupby('Fecha').agg({
    'Rendimiento': 'mean',
    'Eficiencia_Riego': 'mean',
    'Calidad': 'mean',
    'Margen_Ganancia': 'mean'
}).reset_index()

# Rendimiento
fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Fecha'], y=df_tendencias['Rendimiento'],
              name='Rendimiento', line=dict(color='#27ae60', width=3)),
    row=1, col=1
)

# Eficiencia
fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Fecha'], y=df_tendencias['Eficiencia_Riego'],
              name='Eficiencia', line=dict(color='#3498db', width=3)),
    row=1, col=2
)

# Calidad
fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Fecha'], y=df_tendencias['Calidad'],
              name='Calidad', line=dict(color='#f39c12', width=3)),
    row=2, col=1
)

# Margen
fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Fecha'], y=df_tendencias['Margen_Ganancia'],
              name='Margen', line=dict(color='#e74c3c', width=3)),
    row=2, col=2
)

fig_tendencias.update_layout(height=600, showlegend=False,
                           title_text="📊 Tendencias de Agricultura de Precisión")
fig_tendencias.update_xaxes(title_text="Fecha")
fig_tendencias.update_yaxes(title_text="Rendimiento (t/ha)", row=1, col=1)
fig_tendencias.update_yaxes(title_text="Eficiencia (%)", row=1, col=2)
fig_tendencias.update_yaxes(title_text="Calidad (%)", row=2, col=1)
fig_tendencias.update_yaxes(title_text="Margen ($)", row=2, col=2)

st.plotly_chart(fig_tendencias, use_container_width=True)

# Recomendaciones de precisión
st.markdown('<h2 class="section-title-precision">🎯 Recomendaciones de Precisión</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🌱 Recomendaciones de Suelo")
    recomendaciones_suelo = [
        "💧 Ajustar riego según humedad del suelo",
        "🧪 Corregir pH si está fuera del rango óptimo",
        "🌿 Aumentar materia orgánica en zonas bajas",
        "⚖️ Balancear nutrientes según análisis"
    ]
    
    for rec in recomendaciones_suelo:
        st.info(rec)

with col2:
    st.markdown("#### 🤖 Optimización Tecnológica")
    recomendaciones_tech = [
        "📡 Implementar más sensores IoT",
        "🚁 Usar drones para monitoreo aéreo",
        "🛰️ Integrar datos satelitales",
        "🧠 Aplicar algoritmos de IA/ML"
    ]
    
    for rec in recomendaciones_tech:
        st.info(rec)

with col3:
    st.markdown("#### 💰 Optimización Económica")
    recomendaciones_econ = [
        "📊 Optimizar costos por zona",
        "🎯 Enfocar en cultivos de alto margen",
        "📈 Mejorar eficiencia de recursos",
        "🔄 Implementar rotación de cultivos"
    ]
    
    for rec in recomendaciones_econ:
        st.info(rec)

# Información del sistema de precisión
st.markdown('<h2 class="section-title-precision">ℹ️ Información del Sistema</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🌱 Cultivo:** {cultivo_precision}
    **📍 Zona:** {zona_precision}
    **🤖 Tecnología:** {tecnologia}
    **📊 Registros:** {len(df_precision):,} mediciones
    """)

with col2:
    st.info(f"""
    **📅 Período:** 5 años históricos
    **🔄 Frecuencia:** Datos semanales
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Profesional
    """)

with col3:
    st.info(f"""
    **🌾 Rend. Promedio:** {df_precision['Rendimiento'].mean():.1f} t/ha
    **💧 Eficiencia Promedio:** {df_precision['Eficiencia_Riego'].mean():.1f}%
    **⭐ Calidad Promedio:** {df_precision['Calidad'].mean():.1f}%
    **💰 Margen Promedio:** ${df_precision['Margen_Ganancia'].mean():.0f}
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>🌾 <strong>Sistema METGO</strong> - Agricultura de Precisión</p>
    <p>Tecnología avanzada para optimización inteligente de cultivos</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

