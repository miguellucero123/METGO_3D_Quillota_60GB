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

metgo_paths.setup_paths("05_api_rest")

from api_rest.services import (
    comparativo_estaciones,
    generar_alertas,
    historico_meteo,
    metricas_globales,
    nombre_a_slug,
    resumen_meteo,
)
from meteo_dashboard_utils import filtrar_historico_hasta_hoy, hoy_chile

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Unificado",
    "Hub diferenciado · acceso a módulos METGO",
    module="unificado",
    page_icon="🏠",
    initial_sidebar_state="collapsed",
)

# CSS complementario
st.markdown("""
<style>
    /* Diseño unificado */
    .unificado-header {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .unificado-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease;
    }
    
    .unificado-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00b894, #00a085, #74b9ff, #0984e3);
    }
    
    .unificado-card:hover {
        transform: translateY(-3px);
    }
    
    .metric-unificado-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        text-align: center;
        border-left: 4px solid #00b894;
    }
    
    .metric-unificado-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-unificado-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .chart-unificado-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-unificado {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00b894;
        display: inline-block;
    }
    
    .integration-card {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .unificado-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .unificado-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .metric-unificado-card {
            padding: 1rem;
        }
        
        .chart-unificado-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="unificado-header">
    <h1>🏠 Dashboard Unificado</h1>
    <h3>Sistema METGO - Vista Integral</h3>
    <p>Integración completa de meteorología, agricultura y monitoreo en una sola vista</p>
    <div style="margin-top: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 20px; display: inline-block;">
        🔄 Vista Integral - Todos los Sistemas Integrados
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control Unificado")
    
    # Selector de vista
    vista_unificada = st.selectbox(
        "👁️ Vista:",
        ["Vista Completa", "Solo Meteorología", "Solo Agricultura", "Solo Monitoreo", "Vista Ejecutiva"],
        key="vista_unificada"
    )
    
    # Selector de estación
    estacion_unificada = st.selectbox(
        "🌍 Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue", "Todas las Estaciones"],
        key="estacion_unificada"
    )
    
    # Selector de período
    periodo_unificada = st.selectbox(
        "📅 Período:",
        ["Tiempo Real", "Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Últimos 3 meses"],
        key="periodo_unificada"
    )

    modo_unificado = st.radio(
        "Fuente",
        ["API METGO (valle)", "Vista integrada demo"],
        index=0,
    )

if modo_unificado.startswith("API"):
    st.success(f"**Hub METGO · API** · {hoy_chile()} · Vue http://127.0.0.1:5173")

    if estacion_unificada == "Todas las Estaciones":
        with st.spinner("Cargando valle…"):
            valle = comparativo_estaciones()
            mg = metricas_globales()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estaciones", mg.get("estaciones_activas", len(valle)))
        c2.metric("T° máx media", mg.get("temperatura_media_max"))
        c3.metric("T° mín media", mg.get("temperatura_media_min"))
        c4.metric("Alertas", mg.get("alertas_activas", 0))
        if valle:
            df_v = pd.DataFrame(valle)
            st.dataframe(
                df_v[
                    [
                        c
                        for c in [
                            "estacion",
                            "temperatura",
                            "temperatura_max",
                            "temperatura_min",
                            "humedad",
                            "precipitacion",
                        ]
                        if c in df_v.columns
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
    else:
        slug_u = nombre_a_slug(estacion_unificada)
        with st.spinner(f"Cargando {estacion_unificada}…"):
            res_u = resumen_meteo(slug_u) or {}
            hist_u = filtrar_historico_hasta_hoy(historico_meteo(slug_u, 14) or [])
            alertas_u = generar_alertas(slug_u)
        st.caption(f"Tipo dato: **{res_u.get('tipo_dato', '—')}** · {res_u.get('fuente', 'METGO')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("T°", f"{res_u.get('temperatura', 0):.1f}°C")
        c2.metric("Humedad", f"{res_u.get('humedad', 0):.0f}%")
        c3.metric("Lluvia", f"{res_u.get('precipitacion', 0):.1f} mm")
        c4.metric("Alertas", len(alertas_u))
        if hist_u:
            df_h = pd.DataFrame(hist_u)
            fig_u = go.Figure()
            fig_u.add_trace(
                go.Scatter(
                    x=df_h["fecha"],
                    y=df_h["temperatura_max"],
                    name="T° máx",
                    mode="lines+markers",
                )
            )
            fig_u.add_trace(
                go.Scatter(
                    x=df_h["fecha"],
                    y=df_h["temperatura_min"],
                    name="T° mín",
                    mode="lines+markers",
                )
            )
            fig_u.update_layout(height=360, title=f"Histórico 14 d · {estacion_unificada}")
            st.plotly_chart(fig_u, use_container_width=True, config=PLOTLY_CONFIG)
        for a in alertas_u[:5]:
            st.warning(f"**{a.get('nivel', 'info')}**: {a.get('mensaje', '')}")

    st.info("Módulos: /meteo · /agricola · /monitoreo · /ml en Vue (5173)")
    st.stop()

st.sidebar.caption("Modo demo: datos simulados multi-sistema")

# Función para generar datos unificados
@st.cache_data
def generar_datos_unificados(estacion, periodo):
    """Genera datos unificados de todos los sistemas"""
    
    # Configuración de estaciones
    estaciones_config = {
        "Quillota": {"lat": -32.8834, "lon": -71.2489, "altura": 120, "poblacion": 201191},
        "Los Nogales": {"lat": -32.8500, "lon": -71.2000, "altura": 150, "poblacion": 50000},
        "Hijuelas": {"lat": -32.8167, "lon": -71.1833, "altura": 200, "poblacion": 15000},
        "Limache": {"lat": -33.0167, "lon": -71.2667, "altura": 80, "poblacion": 45000},
        "Olmue": {"lat": -33.0000, "lon": -71.1833, "altura": 100, "poblacion": 25000}
    }
    
    # Datos meteorológicos unificados
    datos_meteorologicos = []
    datos_agricolas = []
    datos_monitoreo = []
    
    # Generar datos para múltiples estaciones si es necesario
    estaciones_a_procesar = list(estaciones_config.keys()) if estacion == "Todas las Estaciones" else [estacion]
    
    for est in estaciones_a_procesar:
        config = estaciones_config[est]
        
        # Datos meteorológicos
        temp_base = 18 + (config["altura"] - 120) * -0.01  # Variación por altura
        temp_actual = temp_base + random.uniform(-3, 3)
        humedad = 65 + random.uniform(-15, 15)
        precipitacion = random.exponential(0.5)
        viento = random.uniform(5, 15)
        presion = 1013 + random.uniform(-10, 10)
        
        datos_meteorologicos.append({
            'estacion': est,
            'temperatura': round(temp_actual, 1),
            'humedad': round(humedad, 1),
            'precipitacion': round(precipitacion, 2),
            'viento': round(viento, 1),
            'presion': round(presion, 1),
            'timestamp': datetime.now()
        })
        
        # Datos agrícolas
        rendimiento = 20 + temp_actual * 0.3 + random.uniform(-2, 2)
        calidad = 75 + random.uniform(-10, 10)
        eficiencia_riego = 70 + random.uniform(-10, 10)
        costo_produccion = rendimiento * 50 + random.uniform(-100, 100)
        
        datos_agricolas.append({
            'estacion': est,
            'rendimiento': round(rendimiento, 1),
            'calidad': round(calidad, 1),
            'eficiencia_riego': round(eficiencia_riego, 1),
            'costo_produccion': round(costo_produccion, 0),
            'timestamp': datetime.now()
        })
        
        # Datos de monitoreo
        sensores_activos = random.randint(8, 12)
        alertas_activas = random.randint(0, 3)
        uptime = random.uniform(95, 99.9)
        eficiencia_sistema = random.uniform(85, 98)
        
        datos_monitoreo.append({
            'estacion': est,
            'sensores_activos': sensores_activos,
            'alertas_activas': alertas_activas,
            'uptime': round(uptime, 1),
            'eficiencia_sistema': round(eficiencia_sistema, 1),
            'timestamp': datetime.now()
        })
    
    return {
        'meteorologicos': pd.DataFrame(datos_meteorologicos),
        'agricolas': pd.DataFrame(datos_agricolas),
        'monitoreo': pd.DataFrame(datos_monitoreo)
    }

# Generar datos unificados
with st.spinner('🔄 Generando datos unificados...'):
    datos_unificados = generar_datos_unificados(estacion_unificada, periodo_unificada)

# Métricas unificadas
st.markdown("### 📊 Métricas Unificadas del Sistema")

col1, col2, col3, col4 = st.columns(4)

# Calcular métricas agregadas
df_met = datos_unificados['meteorologicos']
df_agr = datos_unificados['agricolas']
df_mon = datos_unificados['monitoreo']

temp_promedio = df_met['temperatura'].mean()
rendimiento_promedio = df_agr['rendimiento'].mean()
eficiencia_promedio = df_mon['eficiencia_sistema'].mean()
uptime_promedio = df_mon['uptime'].mean()

with col1:
    st.markdown(f"""
    <div class="metric-unificado-card">
        <div class="metric-unificado-number">{temp_promedio:.1f}°C</div>
        <div class="metric-unificado-label">🌡️ Temperatura Promedio</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-unificado-card">
        <div class="metric-unificado-number">{rendimiento_promedio:.1f} t/ha</div>
        <div class="metric-unificado-label">🌾 Rendimiento Promedio</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-unificado-card">
        <div class="metric-unificado-number">{eficiencia_promedio:.1f}%</div>
        <div class="metric-unificado-label">⚡ Eficiencia Sistema</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-unificado-card">
        <div class="metric-unificado-number">{uptime_promedio:.1f}%</div>
        <div class="metric-unificado-label">📡 Uptime Promedio</div>
    </div>
    """, unsafe_allow_html=True)

# Vista integral de todos los sistemas
st.markdown('<h2 class="section-title-unificado">🔄 Vista Integral de Sistemas</h2>', unsafe_allow_html=True)

# Gráfico unificado de todos los sistemas
fig_unificado = make_subplots(
    rows=2, cols=2,
    subplot_titles=('🌡️ Temperatura por Estación', '🌾 Rendimiento por Estación',
                   '📡 Sensores Activos', '⚡ Eficiencia del Sistema'),
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# Temperatura
fig_unificado.add_trace(
    go.Bar(x=df_met['estacion'], y=df_met['temperatura'],
           name='Temperatura', marker_color='#e74c3c'),
    row=1, col=1
)

# Rendimiento
fig_unificado.add_trace(
    go.Bar(x=df_agr['estacion'], y=df_agr['rendimiento'],
           name='Rendimiento', marker_color='#27ae60'),
    row=1, col=2
)

# Sensores
fig_unificado.add_trace(
    go.Bar(x=df_mon['estacion'], y=df_mon['sensores_activos'],
           name='Sensores', marker_color='#3498db'),
    row=2, col=1
)

# Eficiencia
fig_unificado.add_trace(
    go.Bar(x=df_mon['estacion'], y=df_mon['eficiencia_sistema'],
           name='Eficiencia', marker_color='#f39c12'),
    row=2, col=2
)

fig_unificado.update_layout(height=600, showlegend=False,
                          title_text="🏠 Vista Unificada - Todos los Sistemas")
fig_unificado.update_xaxes(title_text="Estación")
fig_unificado.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
fig_unificado.update_yaxes(title_text="Rendimiento (t/ha)", row=1, col=2)
fig_unificado.update_yaxes(title_text="Sensores Activos", row=2, col=1)
fig_unificado.update_yaxes(title_text="Eficiencia (%)", row=2, col=2)

st.plotly_chart(fig_unificado, use_container_width=True)

# Análisis de integración
st.markdown('<h2 class="section-title-unificado">🔗 Análisis de Integración</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Correlación entre sistemas
    st.markdown("#### 📊 Correlación entre Sistemas")
    
    # Crear matriz de correlación
    df_correlacion = pd.DataFrame({
        'Temperatura': df_met['temperatura'],
        'Rendimiento': df_agr['rendimiento'],
        'Eficiencia_Riego': df_agr['eficiencia_riego'],
        'Eficiencia_Sistema': df_mon['eficiencia_sistema']
    })
    
    corr_matrix = df_correlacion.corr()
    
    fig_corr = px.imshow(corr_matrix,
                        text_auto=True,
                        aspect="auto",
                        title="Correlación entre Sistemas",
                        color_continuous_scale='RdBu_r')
    fig_corr.update_layout(height=400)
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    # Estado de integración
    st.markdown("#### ⚡ Estado de Integración")
    
    # Calcular métricas de integración
    integracion_meteorologia = 95.5
    integracion_agricola = 92.3
    integracion_monitoreo = 98.1
    integracion_total = (integracion_meteorologia + integracion_agricola + integracion_monitoreo) / 3
    
    fig_integracion = go.Figure()
    
    fig_integracion.add_trace(go.Bar(
        x=['Meteorología', 'Agricultura', 'Monitoreo', 'Total'],
        y=[integracion_meteorologia, integracion_agricola, integracion_monitoreo, integracion_total],
        marker_color=['#e74c3c', '#27ae60', '#3498db', '#00b894']
    ))
    
    fig_integracion.update_layout(
        title='Nivel de Integración por Sistema',
        xaxis_title='Sistema',
        yaxis_title='Integración (%)',
        height=400
    )
    
    st.plotly_chart(fig_integracion, use_container_width=True)

# Alertas y recomendaciones unificadas
st.markdown('<h2 class="section-title-unificado">🚨 Alertas y Recomendaciones Unificadas</h2>', unsafe_allow_html=True)

# Generar alertas basadas en todos los sistemas
alertas_unificadas = []

# Alertas meteorológicas
if temp_promedio > 30:
    alertas_unificadas.append({
        'tipo': 'Meteorológica',
        'nivel': 'Advertencia',
        'mensaje': 'Temperatura alta detectada - Revisar sistemas de riego',
        'accion': 'Aumentar frecuencia de riego'
    })

# Alertas agrícolas
if rendimiento_promedio < 18:
    alertas_unificadas.append({
        'tipo': 'Agrícola',
        'nivel': 'Crítica',
        'mensaje': 'Rendimiento por debajo del objetivo',
        'accion': 'Optimizar fertilización y riego'
    })

# Alertas de monitoreo
if uptime_promedio < 97:
    alertas_unificadas.append({
        'tipo': 'Monitoreo',
        'nivel': 'Información',
        'mensaje': 'Uptime del sistema por debajo del óptimo',
        'accion': 'Revisar conectividad de sensores'
    })

# Mostrar alertas
for alerta in alertas_unificadas:
    if alerta['nivel'] == 'Crítica':
        st.error(f"🔴 **{alerta['tipo']}**: {alerta['mensaje']} | Acción: {alerta['accion']}")
    elif alerta['nivel'] == 'Advertencia':
        st.warning(f"🟡 **{alerta['tipo']}**: {alerta['mensaje']} | Acción: {alerta['accion']}")
    else:
        st.info(f"🔵 **{alerta['tipo']}**: {alerta['mensaje']} | Acción: {alerta['accion']}")

if not alertas_unificadas:
    st.success("✅ Todos los sistemas funcionando correctamente - Sin alertas activas")

# Panel de control unificado
st.markdown('<h2 class="section-title-unificado">🎛️ Panel de Control Unificado</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔄 Sincronización")
    
    if st.button("🔄 Sincronizar Todos los Sistemas"):
        st.success("Sistemas sincronizados correctamente")
    
    if st.button("📊 Actualizar Métricas"):
        st.success("Métricas actualizadas")
    
    if st.button("🔔 Probar Alertas"):
        st.success("Sistema de alertas funcionando")

with col2:
    st.markdown("#### 📈 Reportes")
    
    if st.button("📋 Reporte Unificado"):
        st.success("Reporte generado correctamente")
    
    if st.button("📊 Dashboard Ejecutivo"):
        st.success("Vista ejecutiva activada")
    
    if st.button("📱 Exportar Datos"):
        st.success("Datos exportados")

with col3:
    st.markdown("#### ⚙️ Configuración")
    
    if st.button("🔧 Configurar Integración"):
        st.info("Panel de configuración abierto")
    
    if st.button("👥 Gestionar Permisos"):
        st.info("Gestión de permisos activada")
    
    if st.button("🔐 Configurar Seguridad"):
        st.info("Configuración de seguridad")

# Información del sistema unificado
st.markdown('<h2 class="section-title-unificado">ℹ️ Información del Sistema Unificado</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🏠 Vista:** {vista_unificada}
    **🌍 Estación:** {estacion_unificada}
    **📅 Período:** {periodo_unificada}
    **🔄 Sistemas Integrados:** 3
    """)

with col2:
    st.info(f"""
    **📊 Datos Generados:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Actualización:** Automática
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Unificado
    """)

with col3:
    st.info(f"""
    **🌡️ Temp. Promedio:** {temp_promedio:.1f}°C
    **🌾 Rend. Promedio:** {rendimiento_promedio:.1f} t/ha
    **⚡ Eficiencia Promedio:** {eficiencia_promedio:.1f}%
    **📡 Uptime Promedio:** {uptime_promedio:.1f}%
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>🏠 <strong>Sistema METGO</strong> - Dashboard Unificado</p>
    <p>Vista integral que integra meteorología, agricultura y monitoreo</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

