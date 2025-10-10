import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="📊 Análisis Comparativo - METGO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional para análisis comparativo */
    .comparativo-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .comparativo-card {
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
    
    .comparativo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #74b9ff, #0984e3, #6c5ce7, #a29bfe);
    }
    
    .comparativo-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .comparativo-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .comparativo-change {
        font-size: 0.9rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .comparativo-positive {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .comparativo-negative {
        background: linear-gradient(135deg, #e17055, #d63031);
        color: white;
    }
    
    .comparativo-neutral {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    
    .chart-comparativo-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-comparativo {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #74b9ff;
        display: inline-block;
    }
    
    .comparison-badge {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.25rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .comparativo-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .comparativo-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .comparativo-number {
            font-size: 2rem;
        }
        
        .chart-comparativo-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="comparativo-header">
    <h1>📊 Análisis Comparativo</h1>
    <h3>Sistema METGO - Comparación de 5 Años</h3>
    <p>Análisis comparativo detallado entre períodos, estaciones y métricas</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Comparación")
    
    # Selector de tipo de comparación
    tipo_comparacion = st.selectbox(
        "📊 Tipo de Comparación:",
        ["Año vs Año", "Mes vs Mes", "Estación vs Estación", "Cultivo vs Cultivo", "Zona vs Zona"],
        key="tipo_comparacion"
    )
    
    # Selector de métricas a comparar
    metricas_comparar = st.multiselect(
        "📈 Métricas a Comparar:",
        ["Temperatura", "Precipitación", "Humedad", "Rendimiento", "Calidad", "Eficiencia", "Ingresos"],
        default=["Temperatura", "Rendimiento", "Eficiencia"],
        key="metricas_comparar"
    )
    
    # Selector de período base
    periodo_base = st.selectbox(
        "📅 Período Base:",
        ["2020", "2021", "2022", "2023", "2024"],
        key="periodo_base"
    )

# Función para generar datos comparativos de 5 años
@st.cache_data
def generar_datos_comparativos(tipo_comparacion, metricas_comparar, periodo_base):
    """Genera datos comparativos de 5 años"""
    
    # Generar datos históricos de 5 años
    años = [2020, 2021, 2022, 2023, 2024]
    meses = list(range(1, 13))
    estaciones = ["Quillota", "Los Nogales", "Hijuelas", "Limache", "Olmue"]
    cultivos = ["Palta", "Cítricos", "Vid", "Tomate", "Lechuga"]
    zonas = ["Zona A", "Zona B", "Zona C", "Zona D", "Zona E"]
    
    datos = []
    
    for año in años:
        for mes in meses:
            for estacion in estaciones:
                for cultivo in cultivos:
                    for zona in zonas:
                        # Tendencias de crecimiento por año
                        crecimiento_año = (año - 2020) * 0.05
                        
                        # Variación estacional
                        estacional = np.sin(2 * np.pi * mes / 12) * 0.3
                        
                        # Datos meteorológicos con tendencias
                        temperatura = 18.5 + crecimiento_año + estacional + np.random.normal(0, 3)
                        precipitacion = max(0, 0.3 - crecimiento_año * 0.1 + np.random.exponential(1))
                        humedad = 65 + estacional * 10 + np.random.normal(0, 8)
                        
                        # Datos agrícolas con mejoras tecnológicas
                        rendimiento_base = 20 + crecimiento_año * 2
                        rendimiento = rendimiento_base + temperatura * 0.3 + humedad * 0.1 + np.random.normal(0, 2)
                        
                        calidad_base = 75 + crecimiento_año * 3
                        calidad = min(100, max(0, calidad_base + np.random.normal(0, 5)))
                        
                        # Eficiencia mejorando con tecnología
                        eficiencia_base = 70 + crecimiento_año * 4
                        eficiencia = min(100, max(0, eficiencia_base + np.random.normal(0, 5)))
                        
                        # Ingresos con inflación y mejoras
                        precio_base = 1000 + crecimiento_año * 100
                        precio = precio_base + np.random.normal(0, 100)
                        ingresos = rendimiento * precio / 1000
                        
                        datos.append({
                            'Año': año,
                            'Mes': mes,
                            'Estacion': estacion,
                            'Cultivo': cultivo,
                            'Zona': zona,
                            'Temperatura': round(temperatura, 1),
                            'Precipitacion': round(precipitacion, 2),
                            'Humedad': round(humedad, 1),
                            'Rendimiento': round(rendimiento, 1),
                            'Calidad': round(calidad, 1),
                            'Eficiencia': round(eficiencia, 1),
                            'Ingresos': round(ingresos, 0),
                            'Fecha': datetime(año, mes, 15)
                        })
    
    return pd.DataFrame(datos)

# Generar datos
with st.spinner('📊 Generando datos comparativos...'):
    df_comparativo = generar_datos_comparativos(tipo_comparacion, metricas_comparar, periodo_base)

# Métricas comparativas
st.markdown("### 🎯 Métricas Comparativas")

# Calcular comparaciones según el tipo seleccionado
if tipo_comparacion == "Año vs Año":
    df_comparison = df_comparativo.groupby('Año')[metricas_comparar].mean().reset_index()
    periodo_actual = 2024
    periodo_anterior = int(periodo_base)
    
    col1, col2, col3, col4 = st.columns(4)
    
    for i, metrica in enumerate(metricas_comparar[:4]):
        with [col1, col2, col3, col4][i]:
            valor_actual = df_comparison[df_comparison['Año'] == periodo_actual][metrica].iloc[0]
            valor_anterior = df_comparison[df_comparison['Año'] == periodo_anterior][metrica].iloc[0]
            cambio = valor_actual - valor_anterior
            cambio_pct = (cambio / valor_anterior) * 100 if valor_anterior != 0 else 0
            
            st.markdown(f"""
            <div class="comparativo-card">
                <div class="comparativo-label">{metrica}</div>
                <div class="comparativo-number">{valor_actual:.1f}</div>
                <div class="comparativo-change {'comparativo-positive' if cambio > 0 else 'comparativo-negative' if cambio < 0 else 'comparativo-neutral'}">
                    {cambio_pct:+.1f}% vs {periodo_anterior}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Gráficos comparativos
st.markdown('<h2 class="section-title-comparativo">📈 Visualizaciones Comparativas</h2>', unsafe_allow_html=True)

if tipo_comparacion == "Año vs Año":
    # Comparación anual
    fig_comparacion_anual = px.line(df_comparison, x='Año', y=metricas_comparar,
                                   title='📊 Evolución Anual de Métricas',
                                   markers=True)
    fig_comparacion_anual.update_layout(height=500)
    st.plotly_chart(fig_comparacion_anual, use_container_width=True)
    
    # Gráfico de barras comparativo
    fig_barras_comparacion = px.bar(df_comparison, x='Año', y=metricas_comparar,
                                   title='📊 Comparación Anual - Gráfico de Barras',
                                   barmode='group')
    fig_barras_comparacion.update_layout(height=500)
    st.plotly_chart(fig_barras_comparacion, use_container_width=True)

elif tipo_comparacion == "Estación vs Estación":
    # Comparación por estaciones
    df_estaciones = df_comparativo.groupby('Estacion')[metricas_comparar].mean().reset_index()
    
    fig_estaciones = px.bar(df_estaciones, x='Estacion', y=metricas_comparar,
                           title='🌍 Comparación por Estaciones Meteorológicas',
                           barmode='group')
    fig_estaciones.update_layout(height=500)
    st.plotly_chart(fig_estaciones, use_container_width=True)

elif tipo_comparacion == "Cultivo vs Cultivo":
    # Comparación por cultivos
    df_cultivos = df_comparativo.groupby('Cultivo')[metricas_comparar].mean().reset_index()
    
    fig_cultivos = px.bar(df_cultivos, x='Cultivo', y=metricas_comparar,
                         title='🌱 Comparación por Tipos de Cultivo',
                         barmode='group')
    fig_cultivos.update_layout(height=500)
    st.plotly_chart(fig_cultivos, use_container_width=True)

# Análisis de correlaciones
st.markdown('<h2 class="section-title-comparativo">🔗 Análisis de Correlaciones</h2>', unsafe_allow_html=True)

# Matriz de correlación
numeric_cols = [col for col in metricas_comparar if col in df_comparativo.columns]
corr_matrix = df_comparativo[numeric_cols].corr()

fig_corr = px.imshow(corr_matrix, 
                    text_auto=True,
                    aspect="auto",
                    title="🔗 Matriz de Correlación entre Métricas",
                    color_continuous_scale='RdBu_r')
fig_corr.update_layout(height=600)
st.plotly_chart(fig_corr, use_container_width=True)

# Análisis de tendencias
st.markdown('<h2 class="section-title-comparativo">📈 Análisis de Tendencias</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Tendencias por año
    df_tendencias_anual = df_comparativo.groupby('Año')[metricas_comparar].mean().reset_index()
    
    fig_tendencias = px.line(df_tendencias_anual, x='Año', y=metricas_comparar,
                            title='📈 Tendencias Anuales',
                            markers=True)
    fig_tendencias.update_layout(height=400)
    st.plotly_chart(fig_tendencias, use_container_width=True)

with col2:
    # Tendencias estacionales
    df_tendencias_mensual = df_comparativo.groupby('Mes')[metricas_comparar].mean().reset_index()
    
    fig_estacional = px.line(df_tendencias_mensual, x='Mes', y=metricas_comparar,
                            title='🌍 Tendencias Estacionales',
                            markers=True)
    fig_estacional.update_layout(height=400)
    st.plotly_chart(fig_estacional, use_container_width=True)

# Análisis de variabilidad
st.markdown('<h2 class="section-title-comparativo">📊 Análisis de Variabilidad</h2>', unsafe_allow_html=True)

# Box plots para mostrar variabilidad
fig_variabilidad = make_subplots(
    rows=2, cols=2,
    subplot_titles=[f'Variabilidad {metrica}' for metrica in metricas_comparar[:4]],
    vertical_spacing=0.1
)

for i, metrica in enumerate(metricas_comparar[:4]):
    row = (i // 2) + 1
    col = (i % 2) + 1
    
    fig_variabilidad.add_trace(
        go.Box(y=df_comparativo[metrica], name=metrica, showlegend=False),
        row=row, col=col
    )

fig_variabilidad.update_layout(height=600, title_text="📊 Distribución y Variabilidad de Métricas")
st.plotly_chart(fig_variabilidad, use_container_width=True)

# Análisis de outliers
st.markdown('<h2 class="section-title-comparativo">🎯 Análisis de Valores Extremos</h2>', unsafe_allow_html=True)

# Identificar outliers usando IQR
outliers_data = []
for metrica in metricas_comparar:
    Q1 = df_comparativo[metrica].quantile(0.25)
    Q3 = df_comparativo[metrica].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df_comparativo[
        (df_comparativo[metrica] < lower_bound) | 
        (df_comparativo[metrica] > upper_bound)
    ]
    
    outliers_data.append({
        'Metrica': metrica,
        'Outliers': len(outliers),
        'Porcentaje': (len(outliers) / len(df_comparativo)) * 100
    })

df_outliers = pd.DataFrame(outliers_data)

fig_outliers = px.bar(df_outliers, x='Metrica', y='Porcentaje',
                     title='🎯 Porcentaje de Valores Extremos por Métrica',
                     color='Porcentaje',
                     color_continuous_scale='Reds')
fig_outliers.update_layout(height=400)
st.plotly_chart(fig_outliers, use_container_width=True)

# Resumen estadístico comparativo
st.markdown('<h2 class="section-title-comparativo">📋 Resumen Estadístico Comparativo</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Estadísticas Descriptivas")
    stats_comparativo = df_comparativo[metricas_comparar].describe()
    st.dataframe(stats_comparativo.round(2), use_container_width=True)

with col2:
    st.markdown("#### 📈 Análisis por Año")
    stats_anual = df_comparativo.groupby('Año')[metricas_comparar].agg(['mean', 'std', 'min', 'max'])
    st.dataframe(stats_anual.round(2), use_container_width=True)

# Conclusiones y recomendaciones
st.markdown('<h2 class="section-title-comparativo">💡 Conclusiones y Recomendaciones</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📈 Tendencias Positivas")
    tendencias_positivas = [
        "🌾 Mejora continua en rendimientos",
        "💧 Incremento en eficiencia de riego",
        "⭐ Mejora en calidad de productos",
        "💰 Crecimiento sostenido de ingresos"
    ]
    
    for tendencia in tendencias_positivas:
        st.success(tendencia)

with col2:
    st.markdown("#### ⚠️ Áreas de Atención")
    areas_atencion = [
        "🌡️ Variabilidad en temperaturas",
        "🌧️ Fluctuaciones en precipitación",
        "📊 Dispersión en algunos indicadores",
        "🎯 Necesidad de optimización"
    ]
    
    for area in areas_atencion:
        st.warning(area)

with col3:
    st.markdown("#### 🎯 Recomendaciones")
    recomendaciones = [
        "📊 Monitorear tendencias de cerca",
        "🔄 Implementar mejoras continuas",
        "📈 Optimizar procesos identificados",
        "🎯 Enfocar en métricas clave"
    ]
    
    for rec in recomendaciones:
        st.info(rec)

# Información del análisis comparativo
st.markdown('<h2 class="section-title-comparativo">ℹ️ Información del Análisis</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **📊 Tipo de Comparación:** {tipo_comparacion}
    **📅 Período Base:** {periodo_base}
    **📈 Métricas Analizadas:** {len(metricas_comparar)}
    **🕐 Registros:** {len(df_comparativo):,} mediciones
    """)

with col2:
    st.info(f"""
    **📊 Datos Generados:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Actualización:** Automática
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Profesional Comparativo
    """)

with col3:
    st.info(f"""
    **📅 Período:** 5 años (2020-2024)
    **🌍 Estaciones:** 5
    **🌱 Cultivos:** 5
    **📍 Zonas:** 5
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>📊 <strong>Sistema METGO</strong> - Análisis Comparativo</p>
    <p>Comparación detallada de métricas y tendencias de 5 años</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
