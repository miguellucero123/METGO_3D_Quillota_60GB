import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Dashboard Unificado",
    page_icon="🚀",
    layout="wide"
)

def generar_datos_meteorologicos():
    """Genera datos meteorológicos simulados para Quillota"""
    np.random.seed(42)
    random.seed(42)
    
    fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    
    datos = []
    for fecha in fechas:
        temp_base = 20 + 5 * np.sin(2 * np.pi * fecha.timetuple().tm_yday / 365)
        temp_max = temp_base + np.random.normal(5, 2)
        temp_min = temp_base - np.random.normal(3, 1.5)
        
        prob_precip = 0.3 if fecha.month in [5, 6, 7, 8] else 0.1
        precipitacion = np.random.exponential(5) if np.random.random() < prob_precip else 0
        
        humedad = np.random.normal(70, 10)
        presion = np.random.normal(1013, 10)
        viento_velocidad = np.random.exponential(8)
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

def generar_datos_agricolas():
    """Genera datos agrícolas simulados para Quillota"""
    np.random.seed(42)
    random.seed(42)
    
    cultivos = ['Palto', 'Citricos', 'Vid', 'Hortalizas', 'Maiz', 'Trigo']
    
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

def main():
    st.title("🚀 METGO 3D - Dashboard Unificado")
    st.markdown("### Sistema Integrado de Monitoreo Meteorológico y Agrícola para Quillota")
    st.markdown("---")
    
    # Sidebar para navegación
    st.sidebar.title("📋 Navegación")
    seccion = st.sidebar.selectbox(
        "Seleccionar Módulo:",
        ["🏠 Inicio", "🌤️ Sistema Meteorológico", "🌾 Sistema Agrícola", "📊 Resumen General"]
    )
    
    if seccion == "🏠 Inicio":
        st.markdown("### 🎯 Bienvenido al Sistema METGO 3D")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌤️ Sistema Meteorológico")
            st.markdown("""
            - **Pronósticos de temperatura** (máxima, mínima, promedio)
            - **Precipitación diaria** y acumulada
            - **Humedad relativa** y presión atmosférica
            - **Velocidad y dirección del viento**
            - **Cobertura nubosa**
            - **Análisis climático** detallado
            """)
        
        with col2:
            st.markdown("#### 🌾 Sistema Agrícola")
            st.markdown("""
            - **Monitoreo de cultivos** (Palto, Cítricos, Vid, etc.)
            - **Rendimientos y valor** de producción
            - **Estado de cultivos** y recomendaciones
            - **Condiciones climáticas** agrícolas
            - **Estrés hídrico** y humedad del suelo
            - **Alertas y recomendaciones** automáticas
            """)
        
        st.markdown("---")
        st.info("💡 **Selecciona un módulo en la barra lateral para acceder a las funcionalidades específicas.**")
    
    elif seccion == "🌤️ Sistema Meteorológico":
        st.markdown("### 🌤️ Sistema Meteorológico")
        
        # Generar datos meteorológicos
        datos_met = generar_datos_meteorologicos()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🌡️ Temp. Actual",
                value=f"{datos_met.iloc[-1]['temp_promedio']:.1f}°C",
                delta=f"{datos_met.iloc[-1]['temp_max']:.1f}°C / {datos_met.iloc[-1]['temp_min']:.1f}°C"
            )
        
        with col2:
            st.metric(
                label="🌧️ Precip. Hoy",
                value=f"{datos_met.iloc[-1]['precipitacion']:.1f} mm",
                delta="Lluvia" if datos_met.iloc[-1]['precipitacion'] > 0 else "Sin lluvia"
            )
        
        with col3:
            st.metric(
                label="💧 Humedad",
                value=f"{datos_met.iloc[-1]['humedad_relativa']:.1f}%",
                delta="Confortable" if 40 <= datos_met.iloc[-1]['humedad_relativa'] <= 60 else "Extrema"
            )
        
        with col4:
            st.metric(
                label="💨 Viento",
                value=f"{datos_met.iloc[-1]['viento_velocidad']:.1f} km/h",
                delta=datos_met.iloc[-1]['viento_direccion']
            )
        
        # Gráficos meteorológicos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de temperaturas
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=datos_met['fecha'], y=datos_met['temp_max'], 
                                        mode='lines+markers', name='Temp. Máxima', line=dict(color='red')))
            fig_temp.add_trace(go.Scatter(x=datos_met['fecha'], y=datos_met['temp_min'], 
                                        mode='lines+markers', name='Temp. Mínima', line=dict(color='blue')))
            fig_temp.update_layout(title='Evolución de Temperaturas', height=400)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Gráfico de precipitación
            fig_precip = go.Figure()
            fig_precip.add_trace(go.Bar(x=datos_met['fecha'], y=datos_met['precipitacion'], 
                                       name='Precipitación', marker=dict(color='lightblue')))
            fig_precip.update_layout(title='Precipitación Diaria', height=400)
            st.plotly_chart(fig_precip, use_container_width=True)
        
        # Tabla de pronóstico
        st.markdown("#### 📊 Pronóstico Detallado (Últimos 7 días)")
        ultimos_datos = datos_met.tail(7)[['fecha', 'temp_max', 'temp_min', 'precipitacion', 
                                          'humedad_relativa', 'viento_velocidad', 'viento_direccion', 'cobertura_nubosa']]
        st.dataframe(ultimos_datos, use_container_width=True, hide_index=True)
    
    elif seccion == "🌾 Sistema Agrícola":
        st.markdown("### 🌾 Sistema Agrícola")
        
        # Generar datos agrícolas
        datos_agri = generar_datos_agricolas()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_superficie = datos_agri['superficie_ha'].sum()
            st.metric(
                label="🌍 Superficie Total",
                value=f"{total_superficie:.1f} Ha",
                delta=f"{len(datos_agri)} cultivos"
            )
        
        with col2:
            total_produccion = datos_agri['produccion_estimada'].sum()
            st.metric(
                label="📦 Producción Total",
                value=f"{total_produccion:.1f} Ton",
                delta="Estimada"
            )
        
        with col3:
            total_valor = datos_agri['valor_estimado'].sum()
            st.metric(
                label="💰 Valor Total",
                value=f"${total_valor:,.0f}",
                delta="Estimado"
            )
        
        with col4:
            cultivos_excelentes = (datos_agri['estado'] == 'Excelente').sum()
            st.metric(
                label="✅ Estado Excelente",
                value=f"{cultivos_excelentes}",
                delta=f"de {len(datos_agri)} cultivos"
            )
        
        # Gráficos agrícolas
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de rendimientos
            fig_rend = go.Figure()
            fig_rend.add_trace(go.Bar(x=datos_agri['cultivo'], y=datos_agri['rendimiento_ton_ha'],
                                     name='Rendimiento', marker=dict(color='green')))
            fig_rend.update_layout(title='Rendimiento por Cultivo (Ton/Ha)', height=400)
            st.plotly_chart(fig_rend, use_container_width=True)
        
        with col2:
            # Gráfico de estado de cultivos
            estado_counts = datos_agri['estado'].value_counts()
            fig_estado = go.Figure(data=[go.Pie(labels=estado_counts.index, values=estado_counts.values, hole=0.3)])
            fig_estado.update_layout(title='Distribución del Estado de Cultivos', height=400)
            st.plotly_chart(fig_estado, use_container_width=True)
        
        # Tabla de recomendaciones
        st.markdown("#### 🎯 Recomendaciones por Cultivo")
        tabla_recom = datos_agri[['cultivo', 'estado', 'fase_fenologica', 'recomendacion', 'prioridad']]
        st.dataframe(tabla_recom, use_container_width=True, hide_index=True)
    
    elif seccion == "📊 Resumen General":
        st.markdown("### 📊 Resumen General del Sistema")
        
        # Generar ambos conjuntos de datos
        datos_met = generar_datos_meteorologicos()
        datos_agri = generar_datos_agricolas()
        
        # Resumen ejecutivo
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌤️ Estado Meteorológico")
            st.write(f"**Temperatura promedio:** {datos_met['temp_promedio'].mean():.1f}°C")
            st.write(f"**Precipitación total:** {datos_met['precipitacion'].sum():.1f} mm")
            st.write(f"**Humedad promedio:** {datos_met['humedad_relativa'].mean():.1f}%")
            st.write(f"**Viento promedio:** {datos_met['viento_velocidad'].mean():.1f} km/h")
        
        with col2:
            st.markdown("#### 🌾 Estado Agrícola")
            st.write(f"**Total de cultivos:** {len(datos_agri)}")
            st.write(f"**Superficie total:** {datos_agri['superficie_ha'].sum():.1f} Ha")
            st.write(f"**Producción estimada:** {datos_agri['produccion_estimada'].sum():.1f} Ton")
            st.write(f"**Valor total:** ${datos_agri['valor_estimado'].sum():,.0f}")
        
        # Alertas
        st.markdown("#### 🚨 Alertas del Sistema")
        
        alertas = []
        
        # Alertas meteorológicas
        if datos_met.iloc[-1]['temp_max'] > 35:
            alertas.append("🔴 **Temperatura alta** - Riesgo de estrés térmico en cultivos")
        
        if datos_met.iloc[-1]['precipitacion'] > 20:
            alertas.append("🟠 **Lluvia intensa** - Posible encharcamiento en campos")
        
        if datos_met.iloc[-1]['viento_velocidad'] > 30:
            alertas.append("🟡 **Viento fuerte** - Riesgo de daños en cultivos")
        
        # Alertas agrícolas
        cultivos_malos = datos_agri[datos_agri['estado'] == 'Malo']
        if len(cultivos_malos) > 0:
            alertas.append(f"🔴 **{len(cultivos_malos)} cultivo(s) en estado crítico**")
        
        cultivos_altos = datos_agri[datos_agri['prioridad'] == 'Alta']
        if len(cultivos_altos) > 0:
            alertas.append(f"🟠 **{len(cultivos_altos)} cultivo(s) requieren atención**")
        
        if alertas:
            for alerta in alertas:
                st.warning(alerta)
        else:
            st.success("✅ **Todas las condiciones están dentro de parámetros normales**")
    
    # Footer
    st.markdown("---")
    st.markdown("**METGO 3D - Sistema Integrado de Monitoreo Meteorológico y Agrícola**")
    st.markdown("*Datos simulados para demostración - Quillota, Chile*")

if __name__ == "__main__":
    main()
