import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import io

# Importar datos reales de OpenMeteo
try:
    from datos_reales_openmeteo import obtener_datos_meteorologicos_reales, OpenMeteoData
    DATOS_REALES_DISPONIBLES = True
except ImportError:
    DATOS_REALES_DISPONIBLES = False

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="📊 Visualizaciones Avanzadas - METGO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Colapsado para móviles
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    
    # Selector de estación
    estacion = st.selectbox(
        "🌍 Estación:",
        ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue", "Santiago", "Valparaiso", "Vina del Mar", "Todas las Estaciones"],
        key="estacion_selector"
    )

# Función para generar datos avanzados con OpenMeteo
@st.cache_data
def generar_datos_visualizaciones_avanzados(periodo, estacion):
    """Genera datos avanzados para visualizaciones usando OpenMeteo"""
    
    # Mapeo de períodos a días
    dias_map = {
        "Últimos 7 días": 7,
        "Últimos 30 días": 30,
        "Últimos 3 meses": 90,
        "Últimos 6 meses": 180,
        "Último año": 365,
        "Últimos 5 años": 1825
    }
    
    dias = dias_map[periodo]
    
    # Lista de estaciones disponibles
    estaciones_disponibles = ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue", "Santiago", "Valparaiso", "Vina del Mar"]
    
    datos_completos = []
    
    # Obtener datos para cada estación
    for est in estaciones_disponibles:
        if estacion != "Todas las Estaciones" and est != estacion:
            continue
        
        try:
            if DATOS_REALES_DISPONIBLES:
                # Obtener datos reales de OpenMeteo
                datos_reales = obtener_datos_meteorologicos_reales(est, 'historicos', min(dias, 92))
                
                if datos_reales is not None and len(datos_reales) > 0:
                    # Procesar datos reales
                    for _, row in datos_reales.iterrows():
                        # Generar datos horarios si es período corto
                        if dias <= 7:
                            for hora in range(0, 24, 3):  # Cada 3 horas
                                fecha_hora = row['fecha'] + timedelta(hours=hora)
                                
                                # Variación horaria simulada
                                variacion_hora = np.sin(2 * np.pi * hora / 24) * 2
                                temp_hora = row['temperatura_promedio'] + variacion_hora + np.random.normal(0, 1)
                                
                                datos_completos.append({
                                    'Fecha': fecha_hora,
                                    'Estacion': est,
                                    'Temperatura': round(temp_hora, 1),
                                    'Precipitacion': round(row['precipitacion'] / 24, 2),  # Distribuir precipitación diaria
                                    'Humedad': round(row['humedad_relativa'] + np.random.normal(0, 5), 1),
                                    'Presion': round(row['presion_atmosferica'] + np.random.normal(0, 2), 1),
                                    'Viento': round(row['velocidad_viento'] + np.random.normal(0, 2), 1),
                                    'Nubosidad': round(np.random.uniform(0, 100), 1),  # Simulado
                                    'Probabilidad_Niebla': round(np.random.uniform(0, 30) if row['humedad_relativa'] > 80 else 0, 1),
                                    'Indice_Helada': round(max(0, 32 - temp_hora) if temp_hora < 5 else 0, 1),
                                    'Rendimiento': round(20 + temp_hora * 0.5 + row['humedad_relativa'] * 0.1, 1),
                                    'Calidad': round(min(100, max(0, 70 + temp_hora * 0.3 + row['humedad_relativa'] * 0.2)), 1),
                                    'Mes': fecha_hora.month,
                                    'DiaSemana': fecha_hora.strftime('%A'),
                                    'Hora': hora,
                                    'Fuente': 'OpenMeteo Real'
                                })
                        else:
                            # Para períodos largos, usar datos diarios
                            datos_completos.append({
                                'Fecha': row['fecha'],
                                'Estacion': est,
                                'Temperatura': round(row['temperatura_promedio'], 1),
                                'Precipitacion': round(row['precipitacion'], 2),
                                'Humedad': round(row['humedad_relativa'], 1),
                                'Presion': round(row['presion_atmosferica'], 1),
                                'Viento': round(row['velocidad_viento'], 1),
                                'Nubosidad': round(np.random.uniform(20, 80), 1),
                                'Probabilidad_Niebla': round(np.random.uniform(0, 40) if row['humedad_relativa'] > 75 else 0, 1),
                                'Indice_Helada': round(max(0, 32 - row['temperatura_min']) if row['temperatura_min'] < 5 else 0, 1),
                                'Rendimiento': round(20 + row['temperatura_promedio'] * 0.5 + row['humedad_relativa'] * 0.1, 1),
                                'Calidad': round(min(100, max(0, 70 + row['temperatura_promedio'] * 0.3 + row['humedad_relativa'] * 0.2)), 1),
                                'Mes': row['fecha'].month,
                                'DiaSemana': row['fecha'].strftime('%A'),
                                'Hora': 12,
                                'Fuente': 'OpenMeteo Real'
                            })
                else:
                    # Fallback a datos simulados si no hay datos reales
                    datos_simulados = generar_datos_simulados(est, dias)
                    datos_completos.extend(datos_simulados)
            else:
                # Usar datos simulados si OpenMeteo no está disponible
                datos_simulados = generar_datos_simulados(est, dias)
                datos_completos.extend(datos_simulados)
                
        except Exception as e:
            st.warning(f"No se pudieron obtener datos reales para {est}: {e}")
            # Fallback a datos simulados
            datos_simulados = generar_datos_simulados(est, dias)
            datos_completos.extend(datos_simulados)
    
    return pd.DataFrame(datos_completos)

def generar_datos_simulados(estacion, dias):
    """Genera datos simulados como fallback"""
    datos_simulados = []
    
    # Configuración por estación
    config_estacion = {
        "Quillota": {"temp_base": 18.5, "precip_base": 0.3, "humedad_base": 65},
        "Los Nogales": {"temp_base": 17.8, "precip_base": 0.4, "humedad_base": 70},
        "Hijuelas": {"temp_base": 16.2, "precip_base": 0.5, "humedad_base": 75},
        "Limache": {"temp_base": 19.0, "precip_base": 0.2, "humedad_base": 60},
        "Olmue": {"temp_base": 18.8, "precip_base": 0.35, "humedad_base": 68},
        "Santiago": {"temp_base": 20.0, "precip_base": 0.2, "humedad_base": 55},
        "Valparaiso": {"temp_base": 16.5, "precip_base": 0.4, "humedad_base": 75},
        "Vina del Mar": {"temp_base": 16.0, "precip_base": 0.5, "humedad_base": 80}
    }
    
    config = config_estacion.get(estacion, config_estacion["Quillota"])
    
    frec = 'H' if dias <= 7 else 'D'
    fechas = pd.date_range(end=datetime.now(), periods=dias, freq=frec)
    
    for fecha in fechas:
        # Variación estacional
        mes = fecha.month
        estacional = np.sin(2 * np.pi * mes / 12) * 3
        
        # Datos meteorológicos
        temperatura = config["temp_base"] + estacional + np.random.normal(0, 4)
        precipitacion = max(0, config["precip_base"] + np.random.exponential(1))
        humedad = max(10, min(100, config["humedad_base"] + np.random.normal(0, 15)))
        presion = 1013 + np.random.normal(0, 12)
        viento = max(0, 8 + np.random.exponential(3))
        nubosidad = np.random.uniform(0, 100)
        probabilidad_niebla = np.random.uniform(0, 40) if humedad > 75 else 0
        indice_helada = max(0, 32 - temperatura) if temperatura < 5 else 0
        
        # Datos agrícolas simulados
        rendimiento = 20 + temperatura * 0.5 + humedad * 0.1 + np.random.normal(0, 3)
        calidad = min(100, max(0, 70 + temperatura * 0.3 + humedad * 0.2 + np.random.normal(0, 10)))
        
        datos_simulados.append({
            'Fecha': fecha,
            'Estacion': estacion,
            'Temperatura': round(temperatura, 1),
            'Precipitacion': round(precipitacion, 2),
            'Humedad': round(humedad, 1),
            'Presion': round(presion, 1),
            'Viento': round(viento, 1),
            'Nubosidad': round(nubosidad, 1),
            'Probabilidad_Niebla': round(probabilidad_niebla, 1),
            'Indice_Helada': round(indice_helada, 1),
            'Rendimiento': round(rendimiento, 1),
            'Calidad': round(calidad, 1),
            'Mes': mes,
            'DiaSemana': fecha.strftime('%A'),
            'Hora': fecha.hour if frec == 'H' else 12,
            'Fuente': 'Simulado'
        })
    
    return datos_simulados

# Información sobre datos reales
if DATOS_REALES_DISPONIBLES:
    st.success("🌐 **Datos Reales Disponibles:** Conectado a OpenMeteo API")
else:
    st.info("ℹ️ **Datos:** Usando datos simulados (OpenMeteo no disponible)")

# Generar datos
with st.spinner('📊 Generando datos para visualizaciones...'):
    df = generar_datos_visualizaciones_avanzados(periodo, estacion)

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
        title="☁️ Evolución de Nubosidad (%)",
        xaxis_title="Fecha",
        yaxis_title="Nubosidad (%)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_nubosidad, use_container_width=True)

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
        title="🌫️ Probabilidad de Niebla (%)",
        xaxis_title="Fecha",
        yaxis_title="Probabilidad de Niebla (%)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_niebla, use_container_width=True)

# Gráfico de índice de heladas
st.markdown("#### ❄️ Análisis Detallado de Heladas")

fig_heladas = go.Figure()

for estacion in df['Estacion'].unique():
    df_est = df[df['Estacion'] == estacion]
    
    # Crear barras para días con heladas
    heladas_dias = df_est[df_est['Indice_Helada'] > 0]
    if len(heladas_dias) > 0:
        fig_heladas.add_trace(go.Bar(
            x=heladas_dias['Fecha'],
            y=heladas_dias['Indice_Helada'],
            name=f'Heladas {estacion}',
            marker=dict(color='#4169E1', opacity=0.7),
            text=[f"{idx:.1f}°C" for idx in heladas_dias['Indice_Helada']],
            textposition='auto'
        ))

fig_heladas.update_layout(
    title="❄️ Índice de Heladas por Estación",
    xaxis_title="Fecha",
    yaxis_title="Índice de Helada (°C)",
    height=500,
    barmode='group',
    hovermode='x unified'
)

st.plotly_chart(fig_heladas, use_container_width=True)

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
        st.plotly_chart(fig_temp_hora, use_container_width=True)
    
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
        st.plotly_chart(fig_hum_hora, use_container_width=True)
    
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

st.plotly_chart(fig_comparacion, use_container_width=True)

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
    
    st.plotly_chart(fig_tendencias, use_container_width=True)

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
        st.plotly_chart(fig_comparacion, use_container_width=True)
    
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
        
        st.plotly_chart(fig_radar, use_container_width=True)

elif tipo_viz == "Distribuciones":
    st.markdown("### 📊 Análisis de Distribuciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histograma de temperaturas
        fig_hist = px.histogram(df, x='Temperatura', nbins=30,
                               title='📈 Distribución de Temperaturas',
                               color_discrete_sequence=['#e74c3c'])
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot por estación
        fig_box = px.box(df, x='Estacion', y='Temperatura',
                        title='📦 Distribución de Temperaturas por Estación',
                        color='Estacion')
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)

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
    st.plotly_chart(fig_corr, use_container_width=True)

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
    st.plotly_chart(fig_heatmap, use_container_width=True)

elif tipo_viz == "Análisis 3D":
    st.markdown("### 🎯 Análisis Tridimensional")
    
    # Gráfico 3D
    fig_3d = px.scatter_3d(df, x='Temperatura', y='Humedad', z='Rendimiento',
                          color='Estacion',
                          title="🎯 Análisis 3D: Temperatura vs Humedad vs Rendimiento",
                          size='Calidad',
                          opacity=0.7)
    fig_3d.update_layout(height=600)
    st.plotly_chart(fig_3d, use_container_width=True)

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
