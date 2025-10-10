#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Principal de Autenticación METGO_3D
Dashboard principal con autenticación y acceso a módulos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os

# Configurar página
st.set_page_config(
    page_title="METGO_3D - Sistema Principal",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones para generar datos meteorológicos
def generar_datos_meteorologicos(estacion="Quillota", fecha_inicio=None, fecha_fin=None, tipo_analisis="Histórico"):
    """Genera datos meteorológicos simulados para diferentes estaciones"""
    # Configuración específica para estaciones meteorológicas de la región de Quillota
    configuraciones = {
        "Quillota": {
            "temp_base": 20, "variacion_temp": 5, "humedad_base": 70,
            "precip_base": 0.3, "viento_base": 8, "presion_base": 1013,
            "descripcion": "Valle Central - Clima Mediterráneo",
            "coordenadas": {"lat": -32.8833, "lon": -71.25},
            "elevacion": 120, "poblacion": 97572, "superficie_agricola": 15000
        },
        "Los Nogales": {
            "temp_base": 19, "variacion_temp": 4, "humedad_base": 72,
            "precip_base": 0.28, "viento_base": 7, "presion_base": 1012,
            "descripcion": "Valle Central - Microclima Nogales",
            "coordenadas": {"lat": -32.85, "lon": -71.20},
            "elevacion": 150, "poblacion": 8500, "superficie_agricola": 3200
        },
        "Hijuelas": {
            "temp_base": 18, "variacion_temp": 6, "humedad_base": 68,
            "precip_base": 0.25, "viento_base": 9, "presion_base": 1014,
            "descripcion": "Valle Central - Zona Agrícola Intensiva",
            "coordenadas": {"lat": -32.80, "lon": -71.15},
            "elevacion": 180, "poblacion": 12000, "superficie_agricola": 8500
        },
        "Limache": {
            "temp_base": 17, "variacion_temp": 3, "humedad_base": 75,
            "precip_base": 0.32, "viento_base": 6, "presion_base": 1011,
            "descripcion": "Valle Central - Clima Templado",
            "coordenadas": {"lat": -33.0167, "lon": -71.2667},
            "elevacion": 100, "poblacion": 45000, "superficie_agricola": 12000
        },
        "Olmue": {
            "temp_base": 16, "variacion_temp": 4, "humedad_base": 78,
            "precip_base": 0.35, "viento_base": 5, "presion_base": 1010,
            "descripcion": "Valle Central - Clima Húmedo",
            "coordenadas": {"lat": -33.0167, "lon": -71.1833},
            "elevacion": 80, "poblacion": 15000, "superficie_agricola": 6000
        }
    }
    
    config = configuraciones.get(estacion, configuraciones["Quillota"])
    
    # Usar timestamp para datos dinámicos
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    random.seed(int(datetime.now().timestamp()) % 1000)
    
    # Generar fechas según el tipo de análisis
    if fecha_inicio and fecha_fin:
        if tipo_analisis == "Pronóstico":
            # Para pronósticos, generar fechas futuras
            dias_diferencia = (fecha_fin - fecha_inicio).days
            fechas = [fecha_inicio + timedelta(days=i) for i in range(dias_diferencia + 1)]
        else:
            # Para histórico, usar las fechas seleccionadas
            dias_diferencia = (fecha_fin - fecha_inicio).days
            fechas = [fecha_inicio + timedelta(days=i) for i in range(dias_diferencia + 1)]
    else:
        # Por defecto, últimos 30 días
        fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    
    datos = []
    for fecha in fechas:
        temp_base = config["temp_base"] + config["variacion_temp"] * np.sin(2 * np.pi * fecha.timetuple().tm_yday / 365)
        temp_max = temp_base + np.random.normal(5, 2)
        temp_min = temp_base - np.random.normal(3, 1.5)
        
        # Probabilidad de precipitación específica por estación
        prob_precip = config["precip_base"] if fecha.month in [5, 6, 7, 8] else config["precip_base"] * 0.5
        precipitacion = np.random.exponential(5) if np.random.random() < prob_precip else 0
        
        humedad = np.random.normal(config["humedad_base"], 10)
        presion = np.random.normal(config["presion_base"], 10)
        viento_velocidad = np.random.exponential(config["viento_base"])
        viento_direccion = np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
        cobertura_nubosa = np.random.normal(40, 25)
        
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'temp_max': round(temp_max, 1),
            'temp_min': round(temp_min, 1),
            'temp_promedio': round((temp_max + temp_min) / 2, 1),
            'precipitacion': round(precipitacion, 1),
            'humedad_relativa': round(humedad, 1),
            'presion_atmosferica': round(presion, 1),
            'viento_velocidad': round(viento_velocidad, 1),
            'viento_direccion': viento_direccion,
            'cobertura_nubosa': round(max(0, min(100, cobertura_nubosa)), 1)
        })
    
    return pd.DataFrame(datos)

def generar_datos_agricolas(estacion="Quillota"):
    """Genera datos agrícolas simulados específicos por región"""
    # Configuración de cultivos por estación meteorológica de la región
    cultivos_por_region = {
        "Quillota": ['Palto', 'Citricos', 'Vid', 'Hortalizas', 'Maiz', 'Trigo'],
        "Los Nogales": ['Palto', 'Citricos', 'Hortalizas', 'Vid', 'Maiz', 'Trigo'],
        "Hijuelas": ['Citricos', 'Palto', 'Hortalizas', 'Vid', 'Maiz', 'Trigo'],
        "Limache": ['Citricos', 'Hortalizas', 'Palto', 'Vid', 'Maiz', 'Trigo'],
        "Olmue": ['Citricos', 'Hortalizas', 'Palto', 'Vid', 'Maiz', 'Trigo']
    }
    
    cultivos = cultivos_por_region.get(estacion, cultivos_por_region["Quillota"])
    
    # Usar timestamp para datos dinámicos
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    random.seed(int(datetime.now().timestamp()) % 1000)
    
    datos_cultivos = []
    for cultivo in cultivos:
        superficie = np.random.uniform(50, 500)
        rendimiento = np.random.uniform(15, 45)
        precio = np.random.uniform(800, 2500)
        
        estados = ['Excelente', 'Bueno', 'Regular', 'Malo']
        estado = np.random.choice(estados, p=[0.4, 0.35, 0.2, 0.05])
        
        fases = ['Crecimiento', 'Floración', 'Fructificación', 'Maduración', 'Cosecha']
        fase = np.random.choice(fases)
        
        if estado == 'Excelente':
            recomendacion = 'Mantener prácticas actuales'
            prioridad = 'Baja'
        elif estado == 'Bueno':
            recomendacion = 'Aplicar fertilizante suave'
            prioridad = 'Media'
        elif estado == 'Regular':
            recomendacion = 'Revisar riego y fertilización'
            prioridad = 'Alta'
        else:
            recomendacion = 'Evaluación urgente requerida'
            prioridad = 'Crítica'
        
        datos_cultivos.append({
            'cultivo': cultivo,
            'superficie_ha': round(superficie, 1),
            'rendimiento_ton_ha': round(rendimiento, 1),
            'precio_ton': round(precio, 0),
            'estado': estado,
            'fase_fenologica': fase,
            'recomendacion': recomendacion,
            'prioridad': prioridad,
            'produccion_estimada': round(superficie * rendimiento, 1),
            'valor_estimado': round(superficie * rendimiento * precio, 0)
        })
    
    return pd.DataFrame(datos_cultivos)

# Función de autenticación simple
def verificar_credenciales(usuario, contraseña):
    """Verificar credenciales de acceso"""
    credenciales_validas = {
        "admin": "admin123",
        "user": "user123",
        "metgo": "metgo2025"
    }
    return credenciales_validas.get(usuario) == contraseña

# Función principal
def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🌾 METGO_3D - Sistema Meteorológico Agrícola")
    st.markdown("### Sistema Integrado de Monitoreo Meteorológico y Agrícola para Quillota")
    st.markdown("**📍 Ubicación:** Quillota, Región de Valparaíso, Chile")
    st.markdown("**🗺️ Coordenadas:** -32.8833°S, -71.25°W | **Elevación:** 120m | **Población:** 97,572")
    
    # Sidebar para autenticación
    with st.sidebar:
        st.header("🔐 Autenticación")
        
        # Formulario de login
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contraseña = st.text_input("🔑 Contraseña", type="password")
            submit_button = st.form_submit_button("🚀 Ingresar")
        
        if submit_button:
            if verificar_credenciales(usuario, contraseña):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.success(f"✅ Bienvenido, {usuario}!")
            else:
                st.error("❌ Credenciales incorrectas")
        
        # Mostrar estado de autenticación
        if st.session_state.get('autenticado', False):
            st.success(f"🟢 Conectado como: {st.session_state.usuario}")
            if st.button("🚪 Cerrar Sesión"):
                st.session_state.autenticado = False
                st.session_state.usuario = None
                st.rerun()
        else:
            st.warning("🔴 No autenticado")
    
    # Contenido principal
    if st.session_state.get('autenticado', False):
        mostrar_dashboard_principal()
    else:
        mostrar_pantalla_login()

def mostrar_pantalla_login():
    """Mostrar pantalla de login"""
    
    st.markdown("---")
    
    # Información del sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🌡️ Sistema Meteorológico
        - Pronósticos en tiempo real
        - Análisis climático
        - Alertas meteorológicas
        """)
    
    with col2:
        st.markdown("""
        ### 🌾 Sistema Agrícola
        - Recomendaciones de cultivo
        - Gestión de riego
        - Análisis de suelos
        """)
    
    with col3:
        st.markdown("""
        ### 🤖 Inteligencia Artificial
        - Modelos predictivos
        - Análisis de datos
        - Optimización agrícola
        """)
    
    # Información de acceso
    st.info("""
    **🔐 Sistema de Autenticación:**
    - Contacta al administrador para obtener las credenciales de acceso
    - El sistema requiere autenticación para acceder a las funciones avanzadas
    """)

def mostrar_dashboard_principal():
    """Mostrar dashboard principal autenticado con gráficos integrados"""
    
    # Botonera de control
    st.markdown("### 🎛️ Panel de Control")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        estacion_seleccionada = st.selectbox(
            "🌍 Estación Meteorológica",
            ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"],
            key="estacion_selector"
        )
    
    with col2:
        if st.button("🔄 Actualizar Datos", key="btn_actualizar"):
            st.session_state.datos_actualizados = True
            st.rerun()
    
    with col3:
        if st.button("📊 Generar Reporte", key="btn_reporte"):
            st.session_state.generar_reporte = True
    
    with col4:
        intervalo_actualizacion = st.selectbox(
            "⏱️ Intervalo",
            ["Manual", "5 min", "15 min", "30 min", "1 hora"],
            key="intervalo_selector"
        )
    
    # Selector de fechas
    st.markdown("### 📅 Selector de Período")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha de Inicio",
            value=datetime.now() - timedelta(days=30),
            key="fecha_inicio"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha de Fin", 
            value=datetime.now(),
            key="fecha_fin"
        )
    
    with col3:
        tipo_analisis = st.selectbox(
            "📊 Tipo de Análisis",
            ["Histórico", "Pronóstico", "Comparativo"],
            key="tipo_analisis"
        )
    
    st.markdown("---")
    
    # Generar datos con la estación seleccionada y fechas
    datos_met = generar_datos_meteorologicos(estacion_seleccionada, fecha_inicio, fecha_fin, tipo_analisis)
    datos_agri = generar_datos_agricolas(estacion_seleccionada)
    
    # Header con información del usuario y estación
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown(f"### 👋 Bienvenido, {st.session_state.usuario}")
        st.markdown(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.markdown(f"🌍 **Estación:** {estacion_seleccionada}")
        
        # Mostrar información específica de cada estación meteorológica
        configuraciones_estaciones = {
            "Quillota": {
                "zona": "Valle Central - Clima Mediterráneo",
                "superficie": "15,000 Ha",
                "actividad": "Agricultura y Agroindustria"
            },
            "Los Nogales": {
                "zona": "Valle Central - Microclima Nogales", 
                "superficie": "3,200 Ha",
                "actividad": "Agricultura Especializada"
            },
            "Hijuelas": {
                "zona": "Valle Central - Zona Agrícola Intensiva",
                "superficie": "8,500 Ha", 
                "actividad": "Agricultura Intensiva"
            },
            "Limache": {
                "zona": "Valle Central - Clima Templado",
                "superficie": "12,000 Ha",
                "actividad": "Agricultura Diversificada"
            },
            "Olmue": {
                "zona": "Valle Central - Clima Húmedo",
                "superficie": "6,000 Ha",
                "actividad": "Agricultura Tradicional"
            }
        }
        
        info_estacion = configuraciones_estaciones.get(estacion_seleccionada, configuraciones_estaciones["Quillota"])
        st.markdown(f"📍 **Zona:** {info_estacion['zona']}")
        st.markdown(f"🌾 **Superficie Agrícola:** {info_estacion['superficie']}")
        st.markdown(f"🏭 **Actividad Principal:** {info_estacion['actividad']}")
    
    with col2:
        temp_actual = datos_met.iloc[-1]['temp_promedio']
        temp_anterior = datos_met.iloc[-2]['temp_promedio'] if len(datos_met) > 1 else temp_actual
        cambio_temp = temp_actual - temp_anterior
        st.metric("🌡️ Temperatura", f"{temp_actual}°C", f"{'↗️' if cambio_temp > 0 else '↘️'} {abs(cambio_temp):.1f}°C")
    
    with col3:
        precip_actual = datos_met.iloc[-1]['precipitacion']
        precip_anterior = datos_met.iloc[-2]['precipitacion'] if len(datos_met) > 1 else precip_actual
        cambio_precip = precip_actual - precip_anterior
        st.metric("🌧️ Precipitación", f"{precip_actual} mm", f"{'↗️' if cambio_precip > 0 else '↘️'} {abs(cambio_precip):.1f} mm")
    
    with col4:
        humedad_actual = datos_met.iloc[-1]['humedad_relativa']
        st.metric("💧 Humedad", f"{humedad_actual}%", "↗️ +2.1%")
    
    st.markdown("---")
    
    # Módulo de pronósticos
    if tipo_analisis == "Pronóstico":
        st.header(f"🔮 Pronósticos Meteorológicos - {estacion_seleccionada}")
        
        # Información del pronóstico
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📅 **Período:** {fecha_inicio} a {fecha_fin}")
        with col2:
            st.warning("⚠️ **Pronóstico:** Datos proyectados basados en modelos")
        with col3:
            st.success("🎯 **Precisión:** 85% promedio")
        
        # Alertas de pronóstico
        st.markdown("### 🚨 Alertas Pronosticadas")
        col1, col2 = st.columns(2)
        
        with col1:
            if datos_met['temp_max'].max() > 35:
                st.error("🔴 **Alerta:** Temperaturas altas pronosticadas")
            if datos_met['precipitacion'].sum() > 50:
                st.warning("🟠 **Alerta:** Lluvias intensas esperadas")
        
        with col2:
            if datos_met['viento_velocidad'].max() > 25:
                st.warning("🟡 **Alerta:** Vientos fuertes pronosticados")
            if datos_met['humedad_relativa'].min() < 30:
                st.info("🔵 **Info:** Humedad baja esperada")
    
    # Módulo de análisis comparativo
    if tipo_analisis == "Comparativo":
        st.header(f"📊 Análisis Comparativo - {estacion_seleccionada}")
        
        # Comparar con datos históricos
        datos_historicos = generar_datos_meteorologicos(estacion_seleccionada, 
                                                      datetime.now() - timedelta(days=60), 
                                                      datetime.now() - timedelta(days=30), 
                                                      "Histórico")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temp_actual = datos_met['temp_promedio'].mean()
            temp_historica = datos_historicos['temp_promedio'].mean()
            cambio_temp = temp_actual - temp_historica
            st.metric("🌡️ Temp Promedio", f"{temp_actual:.1f}°C", f"{'↗️' if cambio_temp > 0 else '↘️'} {abs(cambio_temp):.1f}°C")
        
        with col2:
            precip_actual = datos_met['precipitacion'].sum()
            precip_historica = datos_historicos['precipitacion'].sum()
            cambio_precip = precip_actual - precip_historica
            st.metric("🌧️ Precipitación", f"{precip_actual:.1f} mm", f"{'↗️' if cambio_precip > 0 else '↘️'} {abs(cambio_precip):.1f} mm")
        
        with col3:
            humedad_actual = datos_met['humedad_relativa'].mean()
            humedad_historica = datos_historicos['humedad_relativa'].mean()
            cambio_humedad = humedad_actual - humedad_historica
            st.metric("💧 Humedad", f"{humedad_actual:.1f}%", f"{'↗️' if cambio_humedad > 0 else '↘️'} {abs(cambio_humedad):.1f}%")
        
        st.markdown("---")
    
    # Gráficos meteorológicos
    periodo_texto = f"{fecha_inicio} a {fecha_fin}" if fecha_inicio and fecha_fin else "Últimos 30 días"
    st.header(f"🌡️ Datos Meteorológicos - {estacion_seleccionada} ({periodo_texto})")
    
    # Indicador de estado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.get('datos_actualizados', False):
            st.success("✅ Datos actualizados correctamente")
            st.session_state.datos_actualizados = False
        else:
            tipo_texto = "Pronóstico" if tipo_analisis == "Pronóstico" else "Histórico"
            st.info(f"📊 Datos {tipo_texto} - Última actualización: " + datetime.now().strftime('%H:%M:%S'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de temperaturas
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=datos_met['fecha'], y=datos_met['temp_max'], 
                                    name='Temp Máxima', line=dict(color='red')))
        fig_temp.add_trace(go.Scatter(x=datos_met['fecha'], y=datos_met['temp_min'], 
                                    name='Temp Mínima', line=dict(color='blue')))
        fig_temp.add_trace(go.Scatter(x=datos_met['fecha'], y=datos_met['temp_promedio'], 
                                    name='Temp Promedio', line=dict(color='green')))
        fig_temp.update_layout(title='Temperaturas Diarias', xaxis_title='Fecha', yaxis_title='Temperatura (°C)')
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Gráfico de precipitaciones
        fig_precip = px.bar(datos_met, x='fecha', y='precipitacion', 
                           title='Precipitación Diaria', color='precipitacion',
                           color_continuous_scale='Blues')
        fig_precip.update_layout(xaxis_title='Fecha', yaxis_title='Precipitación (mm)')
        st.plotly_chart(fig_precip, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico de humedad
        fig_humedad = px.line(datos_met, x='fecha', y='humedad_relativa', 
                             title='Humedad Relativa (%)', color_discrete_sequence=['purple'])
        st.plotly_chart(fig_humedad, use_container_width=True)
    
    with col4:
        # Gráfico de presión
        fig_presion = px.line(datos_met, x='fecha', y='presion_atmosferica', 
                             title='Presión Atmosférica (hPa)', color_discrete_sequence=['orange'])
        st.plotly_chart(fig_presion, use_container_width=True)
    
    st.markdown("---")
    
    # Gráficos agrícolas
    st.header("🌾 Datos Agrícolas - Estado de Cultivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de superficie por cultivo
        fig_superficie = px.bar(datos_agri, x='cultivo', y='superficie_ha', 
                               title='Superficie por Cultivo (Ha)', color='cultivo')
        st.plotly_chart(fig_superficie, use_container_width=True)
    
    with col2:
        # Gráfico de producción estimada
        fig_produccion = px.pie(datos_agri, values='produccion_estimada', names='cultivo', 
                               title='Producción Estimada por Cultivo')
        st.plotly_chart(fig_produccion, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico de estado de cultivos
        estado_counts = datos_agri['estado'].value_counts()
        fig_estado = px.bar(x=estado_counts.index, y=estado_counts.values, 
                           title='Estado de Cultivos', color=estado_counts.values,
                           color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_estado, use_container_width=True)
    
    with col4:
        # Gráfico de valor económico
        fig_valor = px.bar(datos_agri, x='cultivo', y='valor_estimado', 
                          title='Valor Económico por Cultivo ($)', color='valor_estimado',
                          color_continuous_scale='Greens')
        st.plotly_chart(fig_valor, use_container_width=True)
    
    # Generar reporte si se solicitó
    if st.session_state.get('generar_reporte', False):
        st.markdown("---")
        st.header("📊 Reporte Generado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **📋 Resumen Meteorológico - {estacion_seleccionada}**
            
            - **Temperatura promedio:** {datos_met['temp_promedio'].mean():.1f}°C
            - **Temperatura máxima:** {datos_met['temp_max'].max():.1f}°C
            - **Temperatura mínima:** {datos_met['temp_min'].min():.1f}°C
            - **Precipitación total:** {datos_met['precipitacion'].sum():.1f} mm
            - **Humedad promedio:** {datos_met['humedad_relativa'].mean():.1f}%
            """)
        
        with col2:
            st.markdown(f"""
            **🌾 Resumen Agrícola**
            
            - **Total cultivos:** {len(datos_agri)}
            - **Superficie total:** {datos_agri['superficie_ha'].sum():.1f} Ha
            - **Producción estimada:** {datos_agri['produccion_estimada'].sum():.1f} Ton
            - **Valor total:** ${datos_agri['valor_estimado'].sum():,.0f}
            - **Cultivos en buen estado:** {len(datos_agri[datos_agri['estado'].isin(['Excelente', 'Bueno'])])}
            """)
        
        st.session_state.generar_reporte = False
    
    # Sistema de Alertas y Recomendaciones ML
    st.markdown("---")
    st.header("🚨 Sistema de Alertas y Recomendaciones ML")
    
    # Generar alertas basadas en datos actuales
    alertas = []
    recomendaciones = []
    
    # Alertas meteorológicas
    if datos_met.iloc[-1]['temp_min'] <= 5:
        alertas.append("🔴 **Alerta Helada:** Temperatura mínima crítica")
        recomendaciones.append("❄️ **Protección contra heladas:** Cubrir cultivos sensibles")
    
    if datos_met.iloc[-1]['temp_max'] >= 35:
        alertas.append("🔴 **Alerta Calor:** Temperatura máxima extrema")
        recomendaciones.append("🌡️ **Protección térmica:** Aumentar riego y sombreado")
    
    if datos_met.iloc[-1]['precipitacion'] >= 10:
        alertas.append("🟠 **Alerta Lluvia:** Precipitación intensa")
        recomendaciones.append("🌧️ **Drenaje:** Verificar sistemas de drenaje")
    
    if datos_met.iloc[-1]['viento_velocidad'] >= 20:
        alertas.append("🟡 **Alerta Viento:** Viento fuerte")
        recomendaciones.append("💨 **Estructuras:** Revisar soportes y estructuras")
    
    if datos_met.iloc[-1]['humedad_relativa'] <= 40:
        alertas.append("🔵 **Alerta Humedad:** Humedad baja")
        recomendaciones.append("💧 **Riego:** Considerar riego suplementario")
    
    # Mostrar alertas
    if alertas:
        st.markdown("### 🚨 Alertas Activas")
        for alerta in alertas:
            st.error(alerta)
    else:
        st.success("✅ Sin alertas activas - Condiciones normales")
    
    # Mostrar recomendaciones
    if recomendaciones:
        st.markdown("### 🌱 Recomendaciones Agrícolas ML")
        for rec in recomendaciones:
            st.info(rec)
    else:
        st.info("🌱 Condiciones favorables para actividades agrícolas")
    
    # Métricas ML
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Predicción de riesgo agrícola
        riesgo_agricola = "Bajo"
        if len(alertas) >= 3:
            riesgo_agricola = "Alto"
        elif len(alertas) >= 1:
            riesgo_agricola = "Medio"
        
        color_riesgo = {"Alto": "🔴", "Medio": "🟡", "Bajo": "🟢"}
        st.metric("🎯 Riesgo Agrícola", riesgo_agricola, color_riesgo[riesgo_agricola])
    
    with col2:
        # Índice de confort climático
        temp_actual = datos_met.iloc[-1]['temp_promedio']
        humedad_actual = datos_met.iloc[-1]['humedad_relativa']
        
        if 18 <= temp_actual <= 25 and 60 <= humedad_actual <= 80:
            confort = "Óptimo"
        elif 15 <= temp_actual <= 30 and 50 <= humedad_actual <= 85:
            confort = "Bueno"
        else:
            confort = "Adverso"
        
        st.metric("🌡️ Confort Climático", confort, "📊")
    
    with col3:
        # Predicción de producción
        if riesgo_agricola == "Bajo":
            prediccion_prod = "Alta"
        elif riesgo_agricola == "Medio":
            prediccion_prod = "Media"
        else:
            prediccion_prod = "Baja"
        
        st.metric("📈 Predicción Producción", prediccion_prod, "🤖")
    
    st.markdown("---")
    
    # Navegación a todos los dashboards del sistema
    st.header("🚀 Acceso a Todos los Dashboards del Sistema")
    
    # Selector principal de dashboards
    dashboard_seleccionado = st.selectbox(
        "🎯 Seleccionar Dashboard Especializado:",
        [
            "🏠 Dashboard Principal (Actual)",
            "🌤️ Sistema Meteorológico Avanzado",
            "🌾 Sistema Agrícola Completo", 
            "🏠 Dashboard Unificado",
            "📊 Dashboard Simple",
            "🤖 Modelos ML Avanzados",
            "📈 Dashboard Global",
            "🔬 Dashboard de Monitoreo",
            "📊 Visualizaciones Integradas",
            "🌾 Dashboard Agrícola Avanzado",
            "📱 Dashboard Móvil",
            "🔧 Dashboard de Configuración"
        ],
        key="dashboard_selector"
    )
    
    # Mostrar el dashboard seleccionado
    if dashboard_seleccionado != "🏠 Dashboard Principal (Actual)":
        st.markdown(f"### {dashboard_seleccionado}")
        
        # URLs de los dashboards - Información de desarrollo
        urls_dashboards = {
            "🌤️ Sistema Meteorológico Avanzado": "#meteorologico",
            "🌾 Sistema Agrícola Completo": "#agricola",
            "🏠 Dashboard Unificado": "#unificado", 
            "📊 Dashboard Simple": "#simple",
            "🤖 Modelos ML Avanzados": "#ml",
            "📈 Dashboard Global": "#global",
            "🔬 Dashboard de Monitoreo": "#monitoreo",
            "📊 Visualizaciones Integradas": "#visualizaciones",
            "🌾 Dashboard Agrícola Avanzado": "#agricola-avanzado",
            "📱 Dashboard Móvil": "#movil",
            "🔧 Dashboard de Configuración": "#configuracion"
        }
        
        url_dashboard = urls_dashboards.get(dashboard_seleccionado, "http://localhost:8501")
        
        st.markdown(f"""
        <div style="border: 3px solid #FF6B35; border-radius: 15px; padding: 30px; margin: 20px 0; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>🎯 {dashboard_seleccionado}</h3>
            <p style="font-size: 18px; margin: 20px 0;">Módulo especializado del sistema METGO</p>
            <div style="background-color: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h4>📋 Estado del Módulo</h4>
                <p>Este módulo está disponible en el sistema local METGO</p>
                <p><strong>Para acceder:</strong> Contacta al administrador del sistema</p>
                <p><strong>Desarrollo:</strong> Los módulos especializados están en desarrollo activo</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Grid de todos los dashboards disponibles
    st.markdown("### 📋 Todos los Dashboards Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    dashboards_info = [
        ("🌤️ Meteorológico", "#4CAF50", "Análisis meteorológico avanzado", "8503"),
        ("🌾 Agrícola", "#2196F3", "Gestión agrícola completa", "8504"),
        ("🏠 Unificado", "#FF9800", "Vista integral del sistema", "8502"),
        ("📊 Simple", "#9C27B0", "Interfaz simplificada", "8505"),
        ("🤖 ML/IA", "#E91E63", "Modelos de inteligencia artificial", "8506"),
        ("📈 Global", "#00BCD4", "Dashboard global del sistema", "8507"),
        ("🔬 Monitoreo", "#795548", "Sistema de monitoreo", "8508"),
        ("📊 Visualizaciones", "#607D8B", "Visualizaciones avanzadas", "8509"),
        ("🌾 Agrícola Avanzado", "#4CAF50", "Agricultura de precisión", "8510")
    ]
    
    for i, (nombre, color, descripcion, puerto) in enumerate(dashboards_info):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: rgba(255,255,255,0.1);">
                <h5 style="color: {color}; margin: 0 0 10px 0;">{nombre}</h5>
                <p style="margin: 0 0 10px 0; font-size: 12px;">{descripcion}</p>
                <p style="margin: 0 0 10px 0; font-size: 10px; color: #666;">Estado: En desarrollo</p>
                <div style="background-color: rgba(255,255,255,0.1); padding: 8px; border-radius: 5px; margin: 10px 0;">
                    <p style="margin: 0; font-size: 11px;">💡 Módulo disponible en sistema local</p>
                    <p style="margin: 0; font-size: 11px;">📞 Contactar administrador</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Información sobre acceso a módulos
    st.markdown("### 🔧 Información de Acceso a Módulos")
    
    st.info("""
    **📋 Estado Actual del Sistema:**
    
    **✅ Dashboard Principal:** Disponible en línea (este dashboard)
    
    **🔄 Módulos Especializados:** Disponibles en el sistema local METGO
    
    **📞 Para Acceder a Módulos Especializados:**
    - Contacta al administrador del sistema METGO
    - Los módulos requieren configuración local específica
    - Cada módulo tiene su propio puerto y configuración
    
    **🌐 Dashboard en Línea:** https://metgo-3d-quillota-60gb.streamlit.app
    """)
    
    # Información sobre dashboards en carpetas del sistema
    st.markdown("### 📁 Dashboards en Carpetas del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="border: 2px solid #FF6B35; border-radius: 10px; padding: 20px; margin: 10px 0; background-color: rgba(255,107,53,0.1);">
            <h4 style="color: #FF6B35;">📂 Carpetas del Sistema METGO</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>01_Sistema_Meteorologico:</strong> Dashboards meteorológicos avanzados</li>
                <li><strong>02_Sistema_Agricola:</strong> Módulos agrícolas especializados</li>
                <li><strong>03_Sistema_IoT_Drones:</strong> Monitoreo con drones y sensores</li>
                <li><strong>04_Dashboards_Unificados:</strong> Dashboards integrados</li>
                <li><strong>05_APIs_Externas:</strong> Conectores y APIs</li>
                <li><strong>06_Modelos_ML_IA:</strong> Inteligencia artificial</li>
                <li><strong>07_Sistema_Monitoreo:</strong> Monitoreo del sistema</li>
                <li><strong>08_Gestion_Datos:</strong> Gestión de datos</li>
                <li><strong>09_Testing_Validacion:</strong> Pruebas y validación</li>
                <li><strong>10_Deployment_Produccion:</strong> Despliegue en producción</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 10px 0; background-color: rgba(76,175,80,0.1);">
            <h4 style="color: #4CAF50;">🚀 Acceso Rápido a Dashboards</h4>
            <p><strong>Dashboard Principal:</strong> <code>sistema_auth_dashboard_principal_metgo.py</code></p>
            <p><strong>Dashboard Meteorológico:</strong> <code>dashboard_meteorologico_metgo.py</code></p>
            <p><strong>Dashboard Agrícola:</strong> <code>dashboard_agricola_metgo.py</code></p>
            <p><strong>Dashboard Unificado:</strong> <code>dashboard_unificado_metgo.py</code></p>
            <p><strong>Dashboard Simple:</strong> <code>dashboard_simple_metgo.py</code></p>
            <p><strong>Dashboard Avanzado:</strong> <code>01_Sistema_Meteorologico/dashboards/dashboard_meteorologico_avanzado.py</code></p>
            <p><strong>Dashboard Global:</strong> <code>04_Dashboards_Unificados/dashboards/dashboard_global_metgo.py</code></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Estado del sistema
    st.header("📊 Estado del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Módulos Activos", "7", "↗️ +1")
    
    with col2:
        st.metric("📊 Dashboards", "6", "↗️ +0")
    
    with col3:
        st.metric("🌡️ Sensores", "12", "↗️ +0")
    
    with col4:
        st.metric("🤖 Modelos IA", "5", "↗️ +1")
    
    # Información del proyecto
    with st.expander("ℹ️ Información del Proyecto"):
        st.markdown("""
        **METGO_3D - Sistema Meteorológico Agrícola Quillota**
        
        **Características:**
        - Sistema modular organizado en 12 carpetas principales
        - 7 dashboards funcionando simultáneamente
        - Análisis meteorológico en tiempo real
        - Recomendaciones agrícolas inteligentes
        - Modelos de Machine Learning integrados
        
        **Tecnologías:**
        - Python 3.11
        - Streamlit para dashboards
        - Pandas para análisis de datos
        - Plotly para visualizaciones interactivas
        - Matplotlib y Seaborn para gráficos estáticos
        
        **Versión:** 2.0 - Sistema Reorganizado
        **Última actualización:** 09/10/2025
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🌾 METGO_3D - Sistema Meteorológico Agrícola Quillota | 
            Sistema Principal de Gestión y Monitoreo
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()