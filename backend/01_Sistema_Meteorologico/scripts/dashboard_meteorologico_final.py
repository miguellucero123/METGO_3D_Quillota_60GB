#!/usr/bin/env python3
"""
Dashboard Meteorológico METGO 3D - Versión Final Funcional
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Dashboard Meteorológico",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
.main {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.stMetric {
    background-color: #f0f2f6;
    border: 1px solid #d0d0d0;
    padding: 1rem;
    border-radius: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

class DashboardMeteorologicoFinal:
    def __init__(self, db_path="datos_meteorologicos.db"):
        self.db_path = db_path
        self.inicializar_db()
    
    def inicializar_db(self):
        """Inicializar base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datos_meteorologicos'")
            if not cursor.fetchone():
                # Crear tabla si no existe
                cursor.execute('''
                    CREATE TABLE datos_meteorologicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        estacion TEXT NOT NULL,
                        fecha TEXT NOT NULL,
                        temperatura REAL,
                        humedad REAL,
                        presion REAL,
                        precipitacion REAL,
                        velocidad_viento REAL,
                        direccion_viento REAL,
                        nubosidad REAL,
                        indice_uv REAL
                    )
                ''')
                conn.commit()
                # Insertar datos de ejemplo
                self.insertar_datos_ejemplo()
            
            conn.close()
        except Exception as e:
            st.error(f"Error inicializando base de datos: {e}")
    
    def insertar_datos_ejemplo(self):
        """Insertar datos de ejemplo si no hay datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generar datos para los últimos 7 días con datos cada hora
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
            fecha_base = datetime.now() - timedelta(days=7)
            
            # Generar datos cada hora para los últimos 7 días
            for i in range(7 * 24):  # 7 días * 24 horas = 168 horas
                fecha = fecha_base + timedelta(hours=i)
                fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
                
                for estacion in estaciones:
                    # Simular variación diurna de temperatura
                    hora = fecha.hour
                    temp_base = 15 + 5 * np.sin(2 * np.pi * (hora - 6) / 24)  # Temperatura que varía según la hora
                    
                    # Datos realistas para Chile central con variación horaria
                    temperatura = temp_base + np.random.normal(0, 1.5)  # Variación alrededor de la temperatura base
                    humedad = np.random.normal(70, 10)     # 70% promedio
                    presion = np.random.normal(1015, 2)    # 1015 hPa promedio
                    precipitacion = np.random.exponential(0.5) if np.random.random() < 0.1 else 0  # Menos probabilidad de lluvia
                    velocidad_viento = np.random.exponential(8)  # 8 km/h promedio
                    direccion_viento = np.random.uniform(0, 360)
                    nubosidad = np.random.uniform(0, 100)
                    indice_uv = max(0, min(10, np.random.uniform(0, 8)))  # UV entre 0 y 10
                    
                    cursor.execute('''
                        INSERT INTO datos_meteorologicos 
                        (estacion, fecha, temperatura, humedad, presion, precipitacion,
                         velocidad_viento, direccion_viento, nubosidad, indice_uv)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (estacion, fecha_str, temperatura, humedad, presion, precipitacion,
                          velocidad_viento, direccion_viento, nubosidad, indice_uv))
            
            conn.commit()
            conn.close()
            st.success("✅ Datos de ejemplo insertados correctamente (datos cada hora)")
        except Exception as e:
            st.error(f"Error insertando datos de ejemplo: {e}")
    
    def obtener_datos_historicos(self, dias=7):
        """Obtener datos históricos de los últimos N días"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Obtener todos los datos y filtrar por fecha
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                ORDER BY fecha ASC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Convertir fecha a datetime
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                
                # Filtrar por el período especificado
                if dias < 1:  # Para períodos menores a 1 día
                    if dias == 0.25:  # 6 horas
                        fecha_limite = datetime.now() - timedelta(hours=6)
                    elif dias == 0.5:  # 12 horas
                        fecha_limite = datetime.now() - timedelta(hours=12)
                    else:
                        fecha_limite = datetime.now() - timedelta(hours=24)
                else:  # Para días completos
                    fecha_limite = datetime.now() - timedelta(days=dias)
                
                df = df[df['fecha'] >= fecha_limite]
                
                # Eliminar filas con fechas inválidas
                df = df.dropna(subset=['fecha'])
            
            return df
            
        except Exception as e:
            st.error(f"Error obteniendo datos históricos: {e}")
            return pd.DataFrame()
    
    def obtener_datos_actuales(self):
        """Obtener los datos más recientes por estación"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                WHERE fecha = (
                    SELECT MAX(fecha) 
                    FROM datos_meteorologicos d2 
                    WHERE d2.estacion = datos_meteorologicos.estacion
                )
                ORDER BY estacion
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Error obteniendo datos actuales: {e}")
            return pd.DataFrame()
    
    def generar_pronostico_14_dias(self):
        """Generar pronóstico meteorológico para los próximos 14 días"""
        try:
            # Obtener datos históricos para análisis de tendencias
            datos_historicos = self.obtener_datos_historicos(7)  # Últimos 7 días
            
            if datos_historicos.empty:
                return pd.DataFrame()
            
            # Calcular promedios históricos por estación
            promedios_historicos = datos_historicos.groupby('estacion').agg({
                'temperatura': ['mean', 'std'],
                'humedad': ['mean', 'std'],
                'presion': ['mean', 'std'],
                'precipitacion': 'mean',
                'velocidad_viento': 'mean',
                'nubosidad': 'mean',
                'indice_uv': 'mean'
            }).reset_index()
            
            # Aplanar nombres de columnas
            promedios_historicos.columns = ['estacion', 'temp_mean', 'temp_std', 
                                          'humedad_mean', 'humedad_std', 'presion_mean', 'presion_std',
                                          'precipitacion_mean', 'viento_mean', 'nubosidad_mean', 'uv_mean']
            
            # Generar pronóstico para 14 días
            pronosticos = []
            fecha_base = datetime.now() + timedelta(days=1)
            
            for dia in range(14):
                fecha_pronostico = fecha_base + timedelta(days=dia)
                
                for _, estacion_data in promedios_historicos.iterrows():
                    estacion = estacion_data['estacion']
                    
                    # Simular variación estacional y tendencias
                    factor_estacional = np.sin(2 * np.pi * (fecha_pronostico.timetuple().tm_yday) / 365)
                    factor_aleatorio = np.random.normal(0, 1)
                    
                    # Pronóstico de temperatura con variación estacional y Tmax/Tmin
                    temp_base = estacion_data['temp_mean']
                    temp_pronostico = temp_base + (factor_estacional * 3) + (factor_aleatorio * estacion_data['temp_std'])
                    
                    # Calcular Tmax y Tmin basado en la temperatura promedio
                    temp_max = temp_pronostico + np.random.uniform(3, 8)  # 3-8°C más alta
                    temp_min = temp_pronostico - np.random.uniform(2, 6)  # 2-6°C más baja
                    
                    # Pronóstico de humedad
                    humedad_base = estacion_data['humedad_mean']
                    humedad_pronostico = max(0, min(100, humedad_base + (factor_aleatorio * estacion_data['humedad_std'])))
                    
                    # Pronóstico de presión
                    presion_base = estacion_data['presion_mean']
                    presion_pronostico = presion_base + (factor_aleatorio * estacion_data['presion_std'])
                    
                    # Pronóstico de precipitación (probabilidad baja)
                    precipitacion_pronostico = 0
                    if np.random.random() < 0.2:  # 20% probabilidad de lluvia
                        precipitacion_pronostico = np.random.exponential(estacion_data['precipitacion_mean'])
                    
                    # Otros parámetros
                    viento_pronostico = max(0, estacion_data['viento_mean'] + np.random.normal(0, 2))
                    nubosidad_pronostico = max(0, min(100, estacion_data['nubosidad_mean'] + np.random.normal(0, 15)))
                    uv_pronostico = max(0, min(10, estacion_data['uv_mean'] + np.random.normal(0, 1)))
                    direccion_viento = np.random.uniform(0, 360)
                    
                    pronosticos.append({
                        'estacion': estacion,
                        'fecha': fecha_pronostico.strftime('%Y-%m-%d'),
                        'dia_semana': fecha_pronostico.strftime('%A'),
                        'temperatura': round(temp_pronostico, 1),
                        'temperatura_max': round(temp_max, 1),
                        'temperatura_min': round(temp_min, 1),
                        'humedad': round(humedad_pronostico, 1),
                        'presion': round(presion_pronostico, 1),
                        'precipitacion': round(precipitacion_pronostico, 1),
                        'velocidad_viento': round(viento_pronostico, 1),
                        'direccion_viento': round(direccion_viento, 0),
                        'nubosidad': round(nubosidad_pronostico, 1),
                        'indice_uv': round(uv_pronostico, 1)
                    })
            
            return pd.DataFrame(pronosticos)
            
        except Exception as e:
            st.error(f"Error generando pronóstico: {e}")
            return pd.DataFrame()

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🌤️ METGO 3D Quillota | Dashboard Meteorológico")
    
    # Inicializar dashboard
    dashboard = DashboardMeteorologicoFinal()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de período
        st.subheader("📅 Período de Análisis")
        periodo = st.selectbox(
            "Selecciona el período",
            ["Últimas 6 horas", "Últimas 12 horas", "Último día", "Últimos 3 días", "Última semana"],
            index=3  # Por defecto "Últimos 3 días"
        )
        
        # Mapeo de períodos a días
        dias_map = {
            "Últimas 6 horas": 0.25,
            "Últimas 12 horas": 0.5,
            "Último día": 1,
            "Últimos 3 días": 3,
            "Última semana": 7
        }
        
        dias = dias_map[periodo]
        
        # Selector de estación
        st.subheader("📍 Estación")
        estaciones = ['Todas las Estaciones', 'Quillota Centro', 'La Cruz', 'Nogueira', 'Colliguay', 'Hijuelas', 'Calera']
        estacion_seleccionada = st.selectbox("Selecciona una estación", estaciones)
        
        # Botón de actualización
        if st.button("🔄 Actualizar Datos"):
            st.rerun()
    
    # Obtener datos
    datos_historicos = dashboard.obtener_datos_historicos(int(dias))
    
    if datos_historicos.empty:
        st.warning("⚠️ No hay datos meteorológicos disponibles. El sistema está generando datos de ejemplo...")
        return
    
    # Filtrar por estación si se selecciona una específica
    if estacion_seleccionada != 'Todas las Estaciones':
        # Mapear nombres de estaciones
        estacion_map = {
            'Quillota Centro': 'quillota_centro',
            'La Cruz': 'la_cruz',
            'Nogueira': 'nogueira',
            'Colliguay': 'colliguay',
            'Hijuelas': 'hijuelas',
            'Calera': 'calera'
        }
        estacion_id = estacion_map[estacion_seleccionada]
        datos_historicos = datos_historicos[datos_historicos['estacion'] == estacion_id]
    
    # Obtener datos actuales
    datos_actuales = dashboard.obtener_datos_actuales()
    
    # Métricas principales
    st.subheader("📊 Métricas Actuales y Extremos")
    
    if not datos_actuales.empty:
        # Primera fila - Valores actuales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp_actual = datos_actuales['temperatura'].mean()
            st.metric("🌡️ Temperatura Actual", f"{temp_actual:.1f}°C")
        
        with col2:
            humedad_actual = datos_actuales['humedad'].mean()
            st.metric("💧 Humedad Actual", f"{humedad_actual:.1f}%")
        
        with col3:
            presion_actual = datos_actuales['presion'].mean()
            st.metric("🔽 Presión Actual", f"{presion_actual:.1f} hPa")
        
        with col4:
            viento_actual = datos_actuales['velocidad_viento'].mean()
            st.metric("💨 Viento Actual", f"{viento_actual:.1f} km/h")
        
        # Segunda fila - Extremos del período seleccionado
        if not datos_historicos.empty:
            st.subheader("📈 Extremos del Período")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                temp_max = datos_historicos['temperatura'].max()
                temp_min = datos_historicos['temperatura'].min()
                st.metric("🌡️ Temperatura", 
                         f"Max: {temp_max:.1f}°C", 
                         f"Min: {temp_min:.1f}°C")
            
            with col6:
                humedad_max = datos_historicos['humedad'].max()
                humedad_min = datos_historicos['humedad'].min()
                st.metric("💧 Humedad", 
                         f"Max: {humedad_max:.1f}%", 
                         f"Min: {humedad_min:.1f}%")
            
            with col7:
                presion_max = datos_historicos['presion'].max()
                presion_min = datos_historicos['presion'].min()
                st.metric("🔽 Presión", 
                         f"Max: {presion_max:.1f} hPa", 
                         f"Min: {presion_min:.1f} hPa")
            
            with col8:
                viento_max = datos_historicos['velocidad_viento'].max()
                viento_min = datos_historicos['velocidad_viento'].min()
                st.metric("💨 Viento", 
                         f"Max: {viento_max:.1f} km/h", 
                         f"Min: {viento_min:.1f} km/h")
    
    # Alertas meteorológicas
    st.subheader("⚠️ Alertas Meteorológicas")
    
    alertas = []
    if not datos_actuales.empty:
        # Alerta de temperatura
        temp_max = datos_actuales['temperatura'].max()
        temp_min = datos_actuales['temperatura'].min()
        
        if temp_max > 30:
            alertas.append("🔥 Temperatura alta detectada (>30°C)")
        if temp_min < 5:
            alertas.append("❄️ Riesgo de heladas detectado (<5°C)")
        
        # Alerta de precipitación
        prec_total = datos_actuales['precipitacion'].sum()
        if prec_total > 10:
            alertas.append("🌧️ Precipitación intensa detectada")
        
        # Alerta de viento
        viento_max = datos_actuales['velocidad_viento'].max()
        if viento_max > 50:
            alertas.append("💨 Vientos fuertes detectados (>50 km/h)")
        
        # Alerta de humedad
        humedad_min = datos_actuales['humedad'].min()
        if humedad_min < 30:
            alertas.append("🏜️ Humedad muy baja detectada (<30%)")
    
    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ Condiciones meteorológicas normales")
    
    # Gráficos principales
    if not datos_historicos.empty:
        st.subheader("📈 Análisis Temporal")
        
        # Gráfico de temperatura
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp = px.line(
                datos_historicos, 
                x='fecha', 
                y='temperatura',
                color='estacion',
                title='🌡️ Evolución de la Temperatura',
                labels={'temperatura': 'Temperatura (°C)', 'fecha': 'Fecha'}
            )
            fig_temp.update_layout(height=400, showlegend=True)
            
            # Configuración moderna de Plotly
            PLOTLY_CONFIG = {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'grafico_metgo',
                    'height': 600,
                    'width': 900,
                    'scale': 2
                },
                'responsive': True,
                'staticPlot': False
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(fig_temp, config=PLOTLY_CONFIG, width='stretch')
    
    with col2:
        fig_humedad = px.line(
            datos_historicos, 
            x='fecha', 
            y='humedad',
            color='estacion',
            title='💧 Evolución de la Humedad',
            labels={'humedad': 'Humedad (%)', 'fecha': 'Fecha'}
        )
        fig_humedad.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_humedad, config=PLOTLY_CONFIG, width='stretch')
        
        # Gráfico de presión
        col3, col4 = st.columns(2)
        
        with col3:
            fig_presion = px.line(
                datos_historicos, 
                x='fecha', 
                y='presion',
                color='estacion',
                title='🔽 Evolución de la Presión',
                labels={'presion': 'Presión (hPa)', 'fecha': 'Fecha'}
            )
            fig_presion.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig_presion, config=PLOTLY_CONFIG, width='stretch')
        
        with col4:
            fig_viento = px.line(
                datos_historicos, 
                x='fecha', 
                y='velocidad_viento',
                color='estacion',
                title='💨 Evolución del Viento',
                labels={'velocidad_viento': 'Velocidad (km/h)', 'fecha': 'Fecha'}
            )
            fig_viento.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig_viento, config=PLOTLY_CONFIG, width='stretch')
    
    # Sección de Pronósticos de 14 días
    st.subheader("🔮 Pronóstico Meteorológico - Próximos 14 Días")
    
    if st.button("📊 Generar Pronóstico"):
        with st.spinner("Generando pronóstico meteorológico..."):
            pronosticos = dashboard.generar_pronostico_14_dias()
            
            if not pronosticos.empty:
                # Mostrar pronóstico por estación seleccionada
                if estacion_seleccionada != 'Todas las Estaciones':
                    estacion_map = {
                        'Quillota Centro': 'quillota_centro',
                        'La Cruz': 'la_cruz',
                        'Nogueira': 'nogueira',
                        'Colliguay': 'colliguay',
                        'Hijuelas': 'hijuelas',
                        'Calera': 'calera'
                    }
                    estacion_id = estacion_map[estacion_seleccionada]
                    pronosticos_filtrados = pronosticos[pronosticos['estacion'] == estacion_id]
                else:
                    # Promedio de todas las estaciones
                    pronosticos_filtrados = pronosticos.groupby(['fecha', 'dia_semana']).agg({
                        'temperatura': 'mean',
                        'humedad': 'mean',
                        'presion': 'mean',
                        'precipitacion': 'mean',
                        'velocidad_viento': 'mean',
                        'nubosidad': 'mean',
                        'indice_uv': 'mean'
                    }).reset_index()
                    pronosticos_filtrados['estacion'] = 'Promedio Regional'
                
                # Gráficos de pronóstico mejorados
                st.subheader("📊 Gráficos de Pronóstico")
                
                # Gráfico de temperatura con Tmax, Tmin y Tprom
                fig_pronostico_temp = go.Figure()
                
                # Verificar que las columnas existan antes de usarlas
                if 'temperatura_max' in pronosticos_filtrados.columns:
                    fig_pronostico_temp.add_trace(go.Scatter(
                        x=pronosticos_filtrados['fecha'],
                        y=pronosticos_filtrados['temperatura_max'],
                        mode='lines+markers',
                        name='Temperatura Máxima',
                        line=dict(color='red', width=2),
                        marker=dict(size=6)
                    ))
                
                if 'temperatura_min' in pronosticos_filtrados.columns:
                    fig_pronostico_temp.add_trace(go.Scatter(
                        x=pronosticos_filtrados['fecha'],
                        y=pronosticos_filtrados['temperatura_min'],
                        mode='lines+markers',
                        name='Temperatura Mínima',
                        line=dict(color='blue', width=2),
                        marker=dict(size=6)
                    ))
                
                if 'temperatura' in pronosticos_filtrados.columns:
                    fig_pronostico_temp.add_trace(go.Scatter(
                        x=pronosticos_filtrados['fecha'],
                        y=pronosticos_filtrados['temperatura'],
                        mode='lines+markers',
                        name='Temperatura Promedio',
                        line=dict(color='green', width=3),
                        marker=dict(size=8)
                    ))
                
                fig_pronostico_temp.update_layout(
                    title='🌡️ Pronóstico de Temperaturas (14 días)',
                    xaxis_title='Fecha',
                    yaxis_title='Temperatura (°C)',
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_pronostico_temp, config=PLOTLY_CONFIG, width='stretch')
                
                # Gráficos de otras variables meteorológicas
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pronostico_precip = px.bar(
                        pronosticos_filtrados,
                        x='fecha',
                        y='precipitacion',
                        title='🌧️ Precipitación',
                        labels={'precipitacion': 'Precipitación (mm)', 'fecha': 'Fecha'}
                    )
                    fig_pronostico_precip.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_pronostico_precip, config=PLOTLY_CONFIG, width='stretch')
                
                with col2:
                    fig_pronostico_nubosidad = px.bar(
                        pronosticos_filtrados,
                        x='fecha',
                        y='nubosidad',
                        title='☁️ Cobertura Nubosa',
                        labels={'nubosidad': 'Cobertura (%)', 'fecha': 'Fecha'},
                        color='nubosidad',
                        color_continuous_scale='Blues'
                    )
                    fig_pronostico_nubosidad.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_pronostico_nubosidad, config=PLOTLY_CONFIG, width='stretch')
                
                # Gráficos de presión y viento
                col3, col4 = st.columns(2)
                
                with col3:
                    fig_pronostico_presion = px.line(
                        pronosticos_filtrados,
                        x='fecha',
                        y='presion',
                        title='📊 Presión Atmosférica',
                        labels={'presion': 'Presión (hPa)', 'fecha': 'Fecha'}
                    )
                    fig_pronostico_presion.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_pronostico_presion, config=PLOTLY_CONFIG, width='stretch')
                
                with col4:
                    fig_pronostico_viento = px.line(
                        pronosticos_filtrados,
                        x='fecha',
                        y='velocidad_viento',
                        title='💨 Velocidad del Viento',
                        labels={'velocidad_viento': 'Velocidad (km/h)', 'fecha': 'Fecha'}
                    )
                    fig_pronostico_viento.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_pronostico_viento, config=PLOTLY_CONFIG, width='stretch')
                
                # Tabla de pronóstico detallado
                st.subheader("📋 Pronóstico Detallado")
                st.write("**Pronóstico por Día:**")
                
                # Formatear tabla para mostrar
                tabla_pronostico = pronosticos_filtrados.copy()
                tabla_pronostico = tabla_pronostico.round(1)
                
                # Mostrar tabla con columnas específicas incluyendo Tmax y Tmin
                columnas_base = ['fecha', 'dia_semana', 'temperatura', 'humedad', 'presion', 'precipitacion', 'velocidad_viento', 'nubosidad', 'indice_uv']
                columnas_adicionales = ['temperatura_max', 'temperatura_min', 'direccion_viento']
                
                # Construir lista de columnas que existen
                columnas_mostrar = [col for col in columnas_base if col in tabla_pronostico.columns]
                columnas_mostrar.extend([col for col in columnas_adicionales if col in tabla_pronostico.columns])
                
                if 'estacion' in tabla_pronostico.columns:
                    columnas_mostrar.insert(2, 'estacion')
                
                # Filtrar solo las columnas que existen
                columnas_disponibles = [col for col in columnas_mostrar if col in tabla_pronostico.columns]
                
                st.dataframe(tabla_pronostico[columnas_disponibles], width='stretch')
                
                # Resumen del pronóstico
                st.subheader("📊 Resumen del Pronóstico")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    temp_max_pronostico = pronosticos_filtrados['temperatura'].max()
                    temp_min_pronostico = pronosticos_filtrados['temperatura'].min()
                    st.metric("🌡️ Temperatura", f"Max: {temp_max_pronostico:.1f}°C", f"Min: {temp_min_pronostico:.1f}°C")
                
                with col2:
                    precip_total = pronosticos_filtrados['precipitacion'].sum()
                    dias_lluvia = (pronosticos_filtrados['precipitacion'] > 0).sum()
                    st.metric("🌧️ Precipitación", f"Total: {precip_total:.1f}mm", f"Días lluvia: {dias_lluvia}")
                
                with col3:
                    viento_max_pronostico = pronosticos_filtrados['velocidad_viento'].max()
                    viento_promedio = pronosticos_filtrados['velocidad_viento'].mean()
                    st.metric("💨 Viento", f"Max: {viento_max_pronostico:.1f} km/h", f"Prom: {viento_promedio:.1f} km/h")
            else:
                st.warning("⚠️ No se pudieron generar pronósticos. Verifica que haya datos históricos disponibles.")
        
        # Tabla de datos detallados
        st.subheader("📋 Datos Detallados")
        st.write("**Datos Más Recientes por Estación:**")
        
        # Mostrar datos actuales en tabla
        if not datos_actuales.empty:
            # Formatear datos para mostrar
            datos_tabla = datos_actuales.copy()
            
            # Verificar si la columna fecha es datetime antes de formatear
            if 'fecha' in datos_tabla.columns:
                if pd.api.types.is_datetime64_any_dtype(datos_tabla['fecha']):
                    datos_tabla['fecha'] = datos_tabla['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # Si no es datetime, convertir primero y luego formatear
                    fecha_convertida = pd.to_datetime(datos_tabla['fecha'], errors='coerce')
                    datos_tabla['fecha'] = fecha_convertida.dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Redondear valores numéricos
            for col in ['temperatura', 'humedad', 'presion', 'precipitacion', 'velocidad_viento', 'direccion_viento', 'nubosidad', 'indice_uv']:
                if col in datos_tabla.columns:
                    datos_tabla[col] = datos_tabla[col].round(2)
            
            st.dataframe(datos_tabla, width='stretch')
    
    # Información del sistema
    with st.expander("ℹ️ Información del Sistema"):
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Período mostrado:** {periodo}")
        st.write(f"**Estación:** {estacion_seleccionada}")
        st.write(f"**Total de registros:** {len(datos_historicos)}")
        
        if not datos_historicos.empty:
            st.write(f"**Rango de fechas:** {datos_historicos['fecha'].min()} a {datos_historicos['fecha'].max()}")

if __name__ == "__main__":
    main()
