import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import ensure_repo_path

ensure_repo_path()
from metgo.streamlit_theme import plotly_layout

def generar_datos_agricolas():
    """Genera datos agrícolas simulados para Quillota"""
    np.random.seed(42)
    random.seed(42)
    
    # Cultivos típicos de Quillota
    cultivos = ['Palto', 'Citricos', 'Vid', 'Hortalizas', 'Maiz', 'Trigo']
    
    datos_cultivos = []
    for cultivo in cultivos:
        # Generar datos para cada cultivo
        superficie = np.random.uniform(50, 500)  # hectáreas
        rendimiento = np.random.uniform(15, 45)  # ton/ha
        precio = np.random.uniform(800, 2500)  # $/ton
        
        # Estado del cultivo
        estados = ['Excelente', 'Bueno', 'Regular', 'Malo']
        estado = np.random.choice(estados, p=[0.4, 0.35, 0.2, 0.05])
        
        # Fase fenológica
        fases = ['Crecimiento', 'Floración', 'Fructificación', 'Maduración', 'Cosecha']
        fase = np.random.choice(fases)
        
        # Recomendaciones basadas en el estado
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

def generar_datos_climaticos_agricolas():
    """Genera datos climáticos relevantes para agricultura"""
    fechas = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
    
    datos_clima = []
    for fecha in fechas:
        # Índice de estrés hídrico
        estres_hidrico = np.random.uniform(0, 100)
        
        # Índice de humedad del suelo
        humedad_suelo = np.random.uniform(30, 80)
        
        # Horas de sol
        horas_sol = np.random.uniform(6, 14)
        
        # Temperatura del suelo
        temp_suelo = np.random.uniform(15, 25)
        
        # Riesgo de plagas (0-100)
        riesgo_plagas = np.random.uniform(0, 60)
        
        datos_clima.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'estres_hidrico': round(estres_hidrico, 1),
            'humedad_suelo': round(humedad_suelo, 1),
            'horas_sol': round(horas_sol, 1),
            'temp_suelo': round(temp_suelo, 1),
            'riesgo_plagas': round(riesgo_plagas, 1)
        })
    
    return pd.DataFrame(datos_clima)

def crear_grafico_rendimientos(datos):
    """Crea gráfico de rendimientos por cultivo"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=datos['cultivo'],
        y=datos['rendimiento_ton_ha'],
        text=datos['rendimiento_ton_ha'],
        textposition='auto',
        marker=dict(
            color=datos['rendimiento_ton_ha'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Ton/ha")
        )
    ))
    
    fig.update_layout(
        **plotly_layout(height=400),
        title='Rendimiento por Cultivo',
        xaxis_title='Cultivo',
        yaxis_title='Rendimiento (Ton/Ha)',
        showlegend=False,
    )
    
    return fig

def crear_grafico_valor_produccion(datos):
    """Crea gráfico de valor de producción"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=datos['cultivo'],
        y=datos['valor_estimado'],
        text=[f"${valor:,.0f}" for valor in datos['valor_estimado']],
        textposition='auto',
        marker=dict(
            color=datos['valor_estimado'],
            colorscale='Greens',
            showscale=True,
            colorbar=dict(title="Valor ($)")
        )
    ))
    
    fig.update_layout(
        **plotly_layout(height=400),
        title='Valor Estimado de Producción',
        xaxis_title='Cultivo',
        yaxis_title='Valor ($)',
        showlegend=False,
    )
    
    return fig

def crear_grafico_estado_cultivos(datos):
    """Crea gráfico de estado de cultivos"""
    estado_counts = datos['estado'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=estado_counts.index,
        values=estado_counts.values,
        hole=0.3
    )])
    
    fig.update_layout(
        **plotly_layout(height=400),
        title='Distribución del Estado de Cultivos',
    )
    
    return fig

def crear_tabla_recomendaciones(datos):
    """Crea tabla de recomendaciones"""
    tabla_data = []
    for _, row in datos.iterrows():
        # Determinar color de prioridad
        color_prioridad = {
            'Crítica': '🔴',
            'Alta': '🟠', 
            'Media': '🟡',
            'Baja': '🟢'
        }
        
        tabla_data.append({
            'Cultivo': row['cultivo'],
            'Estado': row['estado'],
            'Fase': row['fase_fenologica'],
            'Recomendación': row['recomendacion'],
            'Prioridad': f"{color_prioridad.get(row['prioridad'], '⚪')} {row['prioridad']}"
        })
    
    return pd.DataFrame(tabla_data)

def main():
    import sys
    from pathlib import Path

    _DASH = Path(__file__).resolve().parent
    if str(_DASH) not in sys.path:
        sys.path.insert(0, str(_DASH))
    from metgo_dashboard_init import page_config_and_theme

    st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
        "Sistema Agrícola METGO",
        "Gestión y monitoreo agrícola · Quillota",
        module="agricola",
        page_icon="🌾",
    )

    # Generar datos
    datos_cultivos = generar_datos_agricolas()
    datos_clima = generar_datos_climaticos_agricolas()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_superficie = datos_cultivos['superficie_ha'].sum()
        st.metric(
            label="🌍 Superficie Total",
            value=f"{total_superficie:.1f} Ha",
            delta=f"{len(datos_cultivos)} cultivos"
        )
    
    with col2:
        total_produccion = datos_cultivos['produccion_estimada'].sum()
        st.metric(
            label="📦 Producción Total",
            value=f"{total_produccion:.1f} Ton",
            delta="Estimada"
        )
    
    with col3:
        total_valor = datos_cultivos['valor_estimado'].sum()
        st.metric(
            label="💰 Valor Total",
            value=f"${total_valor:,.0f}",
            delta="Estimado"
        )
    
    with col4:
        cultivos_excelentes = (datos_cultivos['estado'] == 'Excelente').sum()
        st.metric(
            label="✅ Estado Excelente",
            value=f"{cultivos_excelentes}",
            delta=f"de {len(datos_cultivos)} cultivos"
        )
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(crear_grafico_rendimientos(datos_cultivos), config=PLOTLY_CONFIG, use_container_width=True)
    
    with col2:
        st.plotly_chart(crear_grafico_valor_produccion(datos_cultivos), config=PLOTLY_CONFIG, use_container_width=True)
    
    # Gráfico de estado de cultivos
    st.plotly_chart(crear_grafico_estado_cultivos(datos_cultivos), config=PLOTLY_CONFIG, use_container_width=True)
    
    # Tabla de recomendaciones
    st.markdown("### 🎯 Recomendaciones por Cultivo")
    tabla_recomendaciones = crear_tabla_recomendaciones(datos_cultivos)
    st.dataframe(tabla_recomendaciones, use_container_width=True, hide_index=True)
    
    # Información climática para agricultura
    st.markdown("---")
    st.markdown("### 🌡️ Condiciones Climáticas Agrícolas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Datos Actuales:**")
        ultimo_dato = datos_clima.iloc[-1]
        st.write(f"- Estrés Hídrico: {ultimo_dato['estres_hidrico']:.1f}%")
        st.write(f"- Humedad del Suelo: {ultimo_dato['humedad_suelo']:.1f}%")
        st.write(f"- Horas de Sol: {ultimo_dato['horas_sol']:.1f}h")
        st.write(f"- Temperatura del Suelo: {ultimo_dato['temp_suelo']:.1f}°C")
        st.write(f"- Riesgo de Plagas: {ultimo_dato['riesgo_plagas']:.1f}%")
    
    with col2:
        st.markdown("**Promedios del Período:**")
        st.write(f"- Estrés Hídrico Promedio: {datos_clima['estres_hidrico'].mean():.1f}%")
        st.write(f"- Humedad del Suelo Promedio: {datos_clima['humedad_suelo'].mean():.1f}%")
        st.write(f"- Horas de Sol Promedio: {datos_clima['horas_sol'].mean():.1f}h")
        st.write(f"- Temperatura del Suelo Promedio: {datos_clima['temp_suelo'].mean():.1f}°C")
        st.write(f"- Riesgo de Plagas Promedio: {datos_clima['riesgo_plagas'].mean():.1f}%")
    
    # Alertas y recomendaciones generales
    st.markdown("---")
    st.markdown("### 🚨 Alertas y Recomendaciones Generales")
    
    alertas = []
    
    # Verificar condiciones críticas
    if ultimo_dato['estres_hidrico'] > 70:
        alertas.append("🔴 **Alto estrés hídrico detectado** - Considerar riego suplementario")
    
    if ultimo_dato['humedad_suelo'] < 40:
        alertas.append("🟠 **Humedad del suelo baja** - Revisar sistema de riego")
    
    if ultimo_dato['riesgo_plagas'] > 50:
        alertas.append("🟡 **Riesgo de plagas elevado** - Monitorear cultivos")
    
    cultivos_malos = datos_cultivos[datos_cultivos['estado'] == 'Malo']
    if len(cultivos_malos) > 0:
        alertas.append(f"🔴 **{len(cultivos_malos)} cultivo(s) en estado crítico** - Evaluación urgente requerida")
    
    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ **Todas las condiciones están dentro de parámetros normales**")
    
    # Información del sistema
    st.markdown("---")
    st.info("ℹ️ **Sistema Agrícola METGO** - Datos simulados para demostración. Para datos reales, configurar sensores y sistemas de monitoreo agrícola.")

if __name__ == "__main__":
    main()
