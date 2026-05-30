import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import time
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout

# Configuración de la página
st.set_page_config(
    page_title="Monitoreo en Tiempo Real - METGO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap_dashboard(
    "Monitoreo en Tiempo Real",
    "Supervisión continua de sensores y alertas",
    module="monitoreo",
)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control")

# Configuración de sensores
sensores_config = {
    "Sensores Meteorológicos": {
        "Temperatura": {"unidad": "°C", "rango": (-5, 40), "critico": (35, 40)},
        "Humedad": {"unidad": "%", "rango": (0, 100), "critico": (90, 100)},
        "Presión": {"unidad": "hPa", "rango": (950, 1050), "critico": (950, 970)},
        "Viento": {"unidad": "km/h", "rango": (0, 100), "critico": (60, 100)},
        "Precipitación": {"unidad": "mm/h", "rango": (0, 50), "critico": (30, 50)},
        "Radiación": {"unidad": "W/m²", "rango": (0, 1200), "critico": (1000, 1200)}
    },
    "Sensores Agrícolas": {
        "Humedad del Suelo": {"unidad": "%", "rango": (0, 100), "critico": (90, 100)},
        "Temperatura del Suelo": {"unidad": "°C", "rango": (-10, 50), "critico": (40, 50)},
        "pH del Suelo": {"unidad": "pH", "rango": (3, 10), "critico": (8, 10)},
        "Conductividad": {"unidad": "mS/cm", "rango": (0, 10), "critico": (8, 10)},
        "Nivel de Agua": {"unidad": "cm", "rango": (0, 200), "critico": (180, 200)}
    },
    "Sensores IoT": {
        "Calidad del Aire": {"unidad": "AQI", "rango": (0, 500), "critico": (300, 500)},
        "Ruido": {"unidad": "dB", "rango": (0, 120), "critico": (100, 120)},
        "Movimiento": {"unidad": "Detectado", "rango": (0, 1), "critico": (1, 1)},
        "Puerta": {"unidad": "Abierta", "rango": (0, 1), "critico": (1, 1)}
    }
}

categoria_sensor = st.sidebar.selectbox("📡 Categoría de Sensores:", list(sensores_config.keys()))
actualizacion_automatica = st.sidebar.checkbox("🔄 Actualización Automática", value=True)
intervalo_actualizacion = st.sidebar.slider("⏱️ Intervalo (segundos):", 1, 60, 5)

# Función para generar datos de sensores en tiempo real
@st.cache_data(ttl=1)  # Cache por 1 segundo para simular tiempo real
def generar_datos_tiempo_real(categoria):
    """Genera datos de sensores en tiempo real"""
    
    sensores = sensores_config[categoria]
    datos = []
    timestamp = datetime.now()
    
    for sensor, config in sensores.items():
        # Generar valor dentro del rango
        valor_min, valor_max = config["rango"]
        valor = random.uniform(valor_min, valor_max)
        
        # Determinar estado
        critico_min, critico_max = config["critico"]
        if valor >= critico_min:
            estado = "🔴 Crítico"
        elif valor >= critico_min * 0.8:
            estado = "🟡 Advertencia"
        else:
            estado = "🟢 Normal"
        
        datos.append({
            'Sensor': sensor,
            'Valor': round(valor, 2),
            'Unidad': config["unidad"],
            'Estado': estado,
            'Timestamp': timestamp,
            'Rango': f"{valor_min}-{valor_max}",
            'Crítico': f"{critico_min}-{critico_max}"
        })
    
    return pd.DataFrame(datos)

# Función para generar alertas
def generar_alertas(datos):
    """Genera alertas basadas en los datos de sensores"""
    
    alertas = []
    timestamp = datetime.now()
    
    for _, row in datos.iterrows():
        if "🔴 Crítico" in row['Estado']:
            alertas.append({
                'Timestamp': timestamp,
                'Sensor': row['Sensor'],
                'Tipo': 'Crítico',
                'Mensaje': f"Valor crítico: {row['Valor']} {row['Unidad']}",
                'Severidad': 'Alta',
                'Accion': 'Intervención inmediata requerida'
            })
        elif "🟡 Advertencia" in row['Estado']:
            alertas.append({
                'Timestamp': timestamp,
                'Sensor': row['Sensor'],
                'Tipo': 'Advertencia',
                'Mensaje': f"Valor en rango de advertencia: {row['Valor']} {row['Unidad']}",
                'Severidad': 'Media',
                'Accion': 'Monitorear de cerca'
            })
    
    return pd.DataFrame(alertas)

# Generar datos
datos_sensores = generar_datos_tiempo_real(categoria_sensor)
alertas = generar_alertas(datos_sensores)

# Métricas principales
st.markdown("### 📊 Estado del Sistema en Tiempo Real")

col1, col2, col3, col4 = st.columns(4)

# Contar estados
estados_normales = len(datos_sensores[datos_sensores['Estado'].str.contains('🟢')])
estados_advertencia = len(datos_sensores[datos_sensores['Estado'].str.contains('🟡')])
estados_criticos = len(datos_sensores[datos_sensores['Estado'].str.contains('🔴')])
total_sensores = len(datos_sensores)

with col1:
    st.metric(
        label="📡 Total Sensores",
        value=total_sensores,
        delta=f"{categoria_sensor}"
    )

with col2:
    st.metric(
        label="🟢 Estado Normal",
        value=estados_normales,
        delta=f"{estados_normales/total_sensores*100:.1f}%"
    )

with col3:
    st.metric(
        label="🟡 Advertencias",
        value=estados_advertencia,
        delta=f"{estados_advertencia/total_sensores*100:.1f}%"
    )

with col4:
    st.metric(
        label="🔴 Críticos",
        value=estados_criticos,
        delta=f"{estados_criticos/total_sensores*100:.1f}%"
    )

# Alertas activas
if not alertas.empty:
    st.markdown("### 🚨 Alertas Activas")
    
    for _, alerta in alertas.iterrows():
        if alerta['Severidad'] == 'Alta':
            st.error(f"🔴 **{alerta['Tipo']}** - {alerta['Sensor']}: {alerta['Mensaje']}")
        elif alerta['Severidad'] == 'Media':
            st.warning(f"🟡 **{alerta['Tipo']}** - {alerta['Sensor']}: {alerta['Mensaje']}")

# Visualización de datos de sensores
st.markdown("### 📈 Datos de Sensores en Tiempo Real")

# Gráfico de barras para valores actuales
fig_barras = px.bar(datos_sensores, x='Sensor', y='Valor', 
                   color='Estado',
                   color_discrete_map={
                       '🟢 Normal': '#4CAF50',
                       '🟡 Advertencia': '#FF9800',
                       '🔴 Crítico': '#F44336'
                   },
                   title=f'Valores Actuales - {categoria_sensor}',
                   text='Valor')

fig_barras.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig_barras.update_layout(height=500)
st.plotly_chart(fig_barras, use_container_width=True)

# Gráfico de evolución temporal (simulado)
st.markdown("### 📊 Evolución Temporal de Sensores")

# Generar datos históricos simulados
horas = pd.date_range(end=datetime.now(), periods=24, freq='h')
datos_historicos = []

for sensor in datos_sensores['Sensor'].unique():
    for hora in horas:
        config = sensores_config[categoria_sensor][sensor]
        valor_min, valor_max = config["rango"]
        valor = random.uniform(valor_min, valor_max)
        
        datos_historicos.append({
            'Timestamp': hora,
            'Sensor': sensor,
            'Valor': valor,
            'Unidad': config["unidad"]
        })

df_historico = pd.DataFrame(datos_historicos)

# Gráfico de líneas
fig_evolucion = px.line(df_historico, x='Timestamp', y='Valor', 
                       color='Sensor',
                       title=f'Evolución 24h - {categoria_sensor}')

fig_evolucion.update_layout(height=400)
st.plotly_chart(fig_evolucion, use_container_width=True)

# Tabla detallada de sensores
st.markdown("### 📋 Estado Detallado de Sensores")

# Crear tabla con información detallada
tabla_detallada = datos_sensores.copy()
tabla_detallada['Última Actualización'] = tabla_detallada['Timestamp'].dt.strftime('%H:%M:%S')
tabla_detallada = tabla_detallada[['Sensor', 'Valor', 'Unidad', 'Estado', 'Rango', 'Crítico', 'Última Actualización']]

st.dataframe(tabla_detallada, use_container_width=True)

# Mapa de calor de estados
st.markdown("### 🗺️ Mapa de Calor de Estados")

# Crear matriz de estados para diferentes categorías
categorias = list(sensores_config.keys())
estados_matrix = []

for cat in categorias:
    datos_cat = generar_datos_tiempo_real(cat)
    estados_cat = {
        'Categoría': cat,
        'Normal': len(datos_cat[datos_cat['Estado'].str.contains('🟢')]),
        'Advertencia': len(datos_cat[datos_cat['Estado'].str.contains('🟡')]),
        'Crítico': len(datos_cat[datos_cat['Estado'].str.contains('🔴')])
    }
    estados_matrix.append(estados_cat)

df_estados = pd.DataFrame(estados_matrix)

fig_mapa_calor = px.bar(df_estados, x='Categoría', y=['Normal', 'Advertencia', 'Crítico'],
                       title='Distribución de Estados por Categoría',
                       color_discrete_map={
                           'Normal': '#4CAF50',
                           'Advertencia': '#FF9800',
                           'Crítico': '#F44336'
                       })

st.plotly_chart(fig_mapa_calor, use_container_width=True)

# Panel de control de sensores
st.markdown("### 🎛️ Panel de Control de Sensores")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔧 Configuración de Sensores")
    
    sensor_seleccionado = st.selectbox("Seleccionar Sensor:", datos_sensores['Sensor'].tolist())
    
    if sensor_seleccionado:
        sensor_data = datos_sensores[datos_sensores['Sensor'] == sensor_seleccionado].iloc[0]
        
        st.info(f"""
        **Sensor:** {sensor_data['Sensor']}
        **Valor Actual:** {sensor_data['Valor']} {sensor_data['Unidad']}
        **Estado:** {sensor_data['Estado']}
        **Rango Normal:** {sensor_data['Rango']}
        **Rango Crítico:** {sensor_data['Crítico']}
        """)

with col2:
    st.markdown("#### 📊 Acciones Disponibles")
    
    if st.button("🔄 Actualizar Datos"):
        st.rerun()
    
    if st.button("🔔 Enviar Alertas"):
        st.success("Alertas enviadas a todos los usuarios registrados")
    
    if st.button("📊 Generar Reporte"):
        st.success("Reporte generado y enviado por email")
    
    if st.button("🔧 Mantenimiento"):
        st.info("Programando mantenimiento preventivo")

# Información del sistema
st.markdown("### ℹ️ Información del Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **📡 Categoría:** {categoria_sensor}
    **🕐 Última Actualización:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Auto-actualización:** {'Activada' if actualizacion_automatica else 'Desactivada'}
    **⏱️ Intervalo:** {intervalo_actualizacion} segundos
    """)

with col2:
    st.info(f"""
    **📊 Total Sensores:** {total_sensores}
    **🟢 Estado Normal:** {estados_normales} ({estados_normales/total_sensores*100:.1f}%)
    **🟡 Advertencias:** {estados_advertencia} ({estados_advertencia/total_sensores*100:.1f}%)
    **🔴 Críticos:** {estados_criticos} ({estados_criticos/total_sensores*100:.1f}%)
    """)

with col3:
    st.info(f"""
    **🚨 Alertas Activas:** {len(alertas)}
    **📈 Uptime:** 99.9%
    **🔗 Conectividad:** Estable
    **💾 Almacenamiento:** 85% disponible
    """)

# Auto-refresh si está activado
if actualizacion_automatica:
    time.sleep(intervalo_actualizacion)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🔍 <strong>Sistema METGO</strong> - Monitoreo en Tiempo Real</p>
    <p>Sistema de supervisión continua de sensores y alertas</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
