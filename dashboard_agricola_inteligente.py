import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="🌾 Gestión Agrícola Inteligente - METGO",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
    <h1>🌾 Gestión Agrícola Inteligente</h1>
    <h3>Sistema METGO - Recomendaciones por IA</h3>
    <p>Análisis inteligente de cultivos, plagas, riego y factores climáticos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control Agrícola")

# Configuración de cultivos
cultivos_config = {
    "Palta": {
        "temp_optima": (20, 25), "humedad_optima": (60, 80), "precipitacion_optima": (800, 1200),
        "fases": ["Floración", "Crecimiento", "Maduración", "Cosecha"],
        "plagas_comunes": ["Arañita roja", "Trips", "Mosca de la fruta", "Pulgones"],
        "enfermedades": ["Antracnosis", "Mancha negra", "Podredumbre de raíz"],
        "riego_frecuencia": 3, "riego_cantidad": 25
    },
    "Cítricos": {
        "temp_optima": (15, 30), "humedad_optima": (50, 70), "precipitacion_optima": (600, 1000),
        "fases": ["Floración", "Cuajado", "Crecimiento", "Maduración"],
        "plagas_comunes": ["Minador de hojas", "Ácaros", "Cochinillas", "Pulgones"],
        "enfermedades": ["Gomosis", "Cancro", "Mancha grasienta"],
        "riego_frecuencia": 2, "riego_cantidad": 30
    },
    "Vid": {
        "temp_optima": (18, 28), "humedad_optima": (40, 60), "precipitacion_optima": (400, 800),
        "fases": ["Brotes", "Floración", "Cuajado", "Envero", "Maduración"],
        "plagas_comunes": ["Lobesia", "Polilla del racimo", "Arañita roja", "Mosca de la fruta"],
        "enfermedades": ["Mildiu", "Oídio", "Botritis", "Podredumbre"],
        "riego_frecuencia": 2, "riego_cantidad": 20
    },
    "Tomate": {
        "temp_optima": (20, 30), "humedad_optima": (60, 80), "precipitacion_optima": (500, 800),
        "fases": ["Siembra", "Crecimiento", "Floración", "Fructificación", "Cosecha"],
        "plagas_comunes": ["Tuta absoluta", "Mosca blanca", "Ácaros", "Trips"],
        "enfermedades": ["Tizón tardío", "Tizón temprano", "Fusarium", "Verticilosis"],
        "riego_frecuencia": 1, "riego_cantidad": 15
    },
    "Lechuga": {
        "temp_optima": (15, 22), "humedad_optima": (70, 90), "precipitacion_optima": (300, 500),
        "fases": ["Siembra", "Crecimiento", "Cabeceo", "Cosecha"],
        "plagas_comunes": ["Pulgones", "Gusanos cortadores", "Ácaros", "Trips"],
        "enfermedades": ["Mildiu", "Sclerotinia", "Rhizoctonia"],
        "riego_frecuencia": 1, "riego_cantidad": 10
    }
}

cultivo_seleccionado = st.sidebar.selectbox("🌱 Cultivo:", list(cultivos_config.keys()))
fase_actual = st.sidebar.selectbox("📅 Fase Actual:", cultivos_config[cultivo_seleccionado]["fases"])
superficie = st.sidebar.number_input("📏 Superficie (hectáreas):", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

# Función para generar recomendaciones IA
def generar_recomendaciones_ia(cultivo, fase, superficie, temp_actual, humedad_actual, precipitacion_actual):
    """Genera recomendaciones inteligentes basadas en IA"""
    
    config = cultivos_config[cultivo]
    recomendaciones = []
    alertas = []
    
    # Análisis de temperatura
    temp_min, temp_max = config["temp_optima"]
    if temp_actual < temp_min:
        recomendaciones.append(f"🌡️ **Temperatura baja**: Considerar protección contra heladas o calefacción")
        alertas.append({"tipo": "Helada", "severidad": "Alta", "mensaje": "Riesgo de helada detectado"})
    elif temp_actual > temp_max:
        recomendaciones.append(f"🌡️ **Temperatura alta**: Incrementar riego y considerar sombreado")
        alertas.append({"tipo": "Calor", "severidad": "Media", "mensaje": "Estrés térmico en cultivos"})
    else:
        recomendaciones.append(f"🌡️ **Temperatura óptima**: Condiciones ideales para {cultivo}")
    
    # Análisis de humedad
    hum_min, hum_max = config["humedad_optima"]
    if humedad_actual < hum_min:
        recomendaciones.append(f"💧 **Humedad baja**: Incrementar frecuencia de riego")
        alertas.append({"tipo": "Sequía", "severidad": "Media", "mensaje": "Condiciones de sequía"})
    elif humedad_actual > hum_max:
        recomendaciones.append(f"💧 **Humedad alta**: Reducir riego y mejorar ventilación")
        alertas.append({"tipo": "Exceso Humedad", "severidad": "Baja", "mensaje": "Riesgo de enfermedades fúngicas"})
    
    # Recomendaciones de riego
    riego_cantidad = config["riego_cantidad"] * superficie
    riego_frecuencia = config["riego_frecuencia"]
    recomendaciones.append(f"💧 **Riego**: {riego_cantidad:.1f}L cada {riego_frecuencia} días")
    
    # Recomendaciones de plagas
    plagas_activas = random.sample(config["plagas_comunes"], min(2, len(config["plagas_comunes"])))
    for plaga in plagas_activas:
        recomendaciones.append(f"🐛 **Control de {plaga}**: Monitorear y aplicar tratamiento preventivo")
        alertas.append({"tipo": "Plaga", "severidad": "Media", "mensaje": f"Presencia de {plaga}"})
    
    # Recomendaciones de enfermedades
    enfermedades_activas = random.sample(config["enfermedades"], min(1, len(config["enfermedades"])))
    for enfermedad in enfermedades_activas:
        recomendaciones.append(f"🦠 **Prevención {enfermedad}**: Aplicar fungicida preventivo")
        alertas.append({"tipo": "Enfermedad", "severidad": "Alta", "mensaje": f"Riesgo de {enfermedad}"})
    
    # Recomendaciones específicas por fase
    if fase == "Floración":
        recomendaciones.append("🌸 **Fase de Floración**: Evitar riego excesivo y aplicar fertilizante rico en fósforo")
    elif fase == "Crecimiento":
        recomendaciones.append("🌱 **Fase de Crecimiento**: Mantener riego constante y aplicar fertilizante balanceado")
    elif fase == "Maduración":
        recomendaciones.append("🍎 **Fase de Maduración**: Reducir riego y preparar para cosecha")
    elif fase == "Cosecha":
        recomendaciones.append("🚜 **Cosecha**: Programar cosecha en condiciones óptimas de humedad")
    
    return recomendaciones, alertas

# Simular datos ambientales actuales
temp_actual = 22.5 + np.random.normal(0, 3)
humedad_actual = 65 + np.random.normal(0, 10)
precipitacion_actual = np.random.exponential(0.5)

# Generar recomendaciones
recomendaciones, alertas = generar_recomendaciones_ia(
    cultivo_seleccionado, fase_actual, superficie, 
    temp_actual, humedad_actual, precipitacion_actual
)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌡️ Temperatura Actual",
        value=f"{temp_actual:.1f}°C",
        delta=f"{temp_actual - cultivos_config[cultivo_seleccionado]['temp_optima'][0]:.1f}°C"
    )

with col2:
    st.metric(
        label="💧 Humedad Relativa",
        value=f"{humedad_actual:.1f}%",
        delta=f"{humedad_actual - cultivos_config[cultivo_seleccionado]['humedad_optima'][0]:.1f}%"
    )

with col3:
    st.metric(
        label="🌧️ Precipitación 24h",
        value=f"{precipitacion_actual:.1f} mm",
        delta="+0.2 mm"
    )

with col4:
    config = cultivos_config[cultivo_seleccionado]
    riego_total = config["riego_cantidad"] * superficie
    st.metric(
        label="💧 Riego Recomendado",
        value=f"{riego_total:.1f} L",
        delta=f"Cada {config['riego_frecuencia']} días"
    )

# Alertas y recomendaciones
st.markdown("### 🚨 Sistema de Alertas y Recomendaciones IA")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🚨 Alertas Activas")
    for alerta in alertas:
        color = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}[alerta["severidad"]]
        st.warning(f"{color} **{alerta['tipo']}** ({alerta['severidad']}): {alerta['mensaje']}")

with col2:
    st.markdown("#### 💡 Recomendaciones IA")
    for i, rec in enumerate(recomendaciones, 1):
        st.info(f"{i}. {rec}")

# Análisis de cultivos
st.markdown("### 📊 Análisis de Cultivos")

# Gráfico de condiciones óptimas vs actuales
fig_condiciones = go.Figure()

config = cultivos_config[cultivo_seleccionado]

# Condiciones óptimas
variables = ['Temperatura', 'Humedad', 'Precipitación']
optimas = [
    (config['temp_optima'][0] + config['temp_optima'][1]) / 2,
    (config['humedad_optima'][0] + config['humedad_optima'][1]) / 2,
    (config['precipitacion_optima'][0] + config['precipitacion_optima'][1]) / 2
]

# Condiciones actuales (normalizadas)
actuales = [
    temp_actual,
    humedad_actual,
    precipitacion_actual * 100  # Escalar precipitación
]

fig_condiciones.add_trace(go.Bar(
    name='Condiciones Óptimas',
    x=variables,
    y=optimas,
    marker_color='#4CAF50'
))

fig_condiciones.add_trace(go.Bar(
    name='Condiciones Actuales',
    x=variables,
    y=actuales,
    marker_color='#FF6B35'
))

fig_condiciones.update_layout(
    title=f'🌾 Condiciones para {cultivo_seleccionado} - {fase_actual}',
    barmode='group',
    height=400
)

st.plotly_chart(fig_condiciones, use_container_width=True)

# Análisis de plagas y enfermedades
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🐛 Análisis de Plagas")
    
    plagas_data = []
    for plaga in config["plagas_comunes"]:
        riesgo = random.choice(["Bajo", "Medio", "Alto"])
        plagas_data.append({
            "Plaga": plaga,
            "Riesgo": riesgo,
            "Probabilidad": random.randint(20, 90)
        })
    
    df_plagas = pd.DataFrame(plagas_data)
    
    fig_plagas = px.bar(df_plagas, x='Plaga', y='Probabilidad', 
                       color='Riesgo', 
                       color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                       title='Probabilidad de Aparición de Plagas')
    st.plotly_chart(fig_plagas, use_container_width=True)

with col2:
    st.markdown("#### 🦠 Análisis de Enfermedades")
    
    enfermedades_data = []
    for enfermedad in config["enfermedades"]:
        riesgo = random.choice(["Bajo", "Medio", "Alto"])
        enfermedades_data.append({
            "Enfermedad": enfermedad,
            "Riesgo": riesgo,
            "Probabilidad": random.randint(15, 85)
        })
    
    df_enfermedades = pd.DataFrame(enfermedades_data)
    
    fig_enfermedades = px.bar(df_enfermedades, x='Enfermedad', y='Probabilidad', 
                             color='Riesgo',
                             color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                             title='Probabilidad de Aparición de Enfermedades')
    st.plotly_chart(fig_enfermedades, use_container_width=True)

# Cronograma de actividades
st.markdown("### 📅 Cronograma de Actividades Agrícolas")

# Generar cronograma para los próximos 30 días
fechas = pd.date_range(start=datetime.now(), periods=30, freq='D')
actividades = []

for fecha in fechas:
    dia_semana = fecha.strftime('%A')
    
    # Actividades regulares
    if dia_semana in ['Monday', 'Wednesday', 'Friday']:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Riego programado',
            'Prioridad': 'Alta',
            'Tipo': 'Riego'
        })
    
    # Actividades semanales
    if fecha.day % 7 == 0:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Monitoreo de plagas',
            'Prioridad': 'Media',
            'Tipo': 'Monitoreo'
        })
    
    # Actividades mensuales
    if fecha.day == 15:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Aplicación de fertilizante',
            'Prioridad': 'Alta',
            'Tipo': 'Fertilización'
        })

df_cronograma = pd.DataFrame(actividades)

if not df_cronograma.empty:
    fig_cronograma = px.timeline(df_cronograma, x_start='Fecha', x_end='Fecha', 
                                y='Actividad', color='Prioridad',
                                color_discrete_map={'Alta': '#F44336', 'Media': '#FF9800', 'Baja': '#4CAF50'},
                                title='Cronograma de Actividades - Próximos 30 días')
    fig_cronograma.update_layout(height=400)
    st.plotly_chart(fig_cronograma, use_container_width=True)

# Análisis de rendimiento
st.markdown("### 📈 Análisis de Rendimiento Predicho")

col1, col2 = st.columns(2)

with col1:
    # Factores que afectan el rendimiento
    factores = {
        'Temperatura': temp_actual,
        'Humedad': humedad_actual,
        'Precipitación': precipitacion_actual,
        'Control de Plagas': 85,
        'Fertilización': 90,
        'Riego': 88
    }
    
    fig_factores = px.pie(values=list(factores.values()), 
                         names=list(factores.keys()),
                         title='Factores de Rendimiento (%)')
    st.plotly_chart(fig_factores, use_container_width=True)

with col2:
    # Predicción de rendimiento
    rendimiento_base = {
        "Palta": 15,
        "Cítricos": 25,
        "Vid": 12,
        "Tomate": 40,
        "Lechuga": 30
    }
    
    rendimiento_estimado = rendimiento_base[cultivo_seleccionado] * (1 + random.uniform(-0.2, 0.3))
    
    st.markdown("#### 📊 Rendimiento Estimado")
    st.metric(
        label=f"Producción de {cultivo_seleccionado}",
        value=f"{rendimiento_estimado:.1f} ton/ha",
        delta=f"{rendimiento_estimado - rendimiento_base[cultivo_seleccionado]:.1f} ton/ha"
    )
    
    st.markdown("#### 💰 Análisis Económico")
    precio_estimado = random.uniform(800, 1500)  # $ por tonelada
    ingreso_estimado = rendimiento_estimado * precio_estimado * superficie
    
    st.metric(
        label="Ingreso Estimado",
        value=f"${ingreso_estimado:,.0f}",
        delta=f"Precio: ${precio_estimado:.0f}/ton"
    )

# Información del cultivo
st.markdown("### 🌱 Información del Cultivo Seleccionado")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🌱 Cultivo:** {cultivo_seleccionado}
    **📅 Fase Actual:** {fase_actual}
    **📏 Superficie:** {superficie} hectáreas
    **🌡️ Temp. Óptima:** {config['temp_optima'][0]}-{config['temp_optima'][1]}°C
    """)

with col2:
    st.info(f"""
    **💧 Humedad Óptima:** {config['humedad_optima'][0]}-{config['humedad_optima'][1]}%
    **🌧️ Precip. Anual:** {config['precipitacion_optima'][0]}-{config['precipitacion_optima'][1]} mm
    **💧 Riego:** {config['riego_cantidad']}L cada {config['riego_frecuencia']} días
    """)

with col3:
    st.info(f"""
    **🐛 Plagas Comunes:** {len(config['plagas_comunes'])}
    **🦠 Enfermedades:** {len(config['enfermedades'])}
    **📅 Fases:** {len(config['fases'])}
    **⏱️ Última Actualización:** {datetime.now().strftime("%H:%M")}
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌾 <strong>Sistema METGO</strong> - Gestión Agrícola Inteligente</p>
    <p>Recomendaciones generadas por Inteligencia Artificial</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
