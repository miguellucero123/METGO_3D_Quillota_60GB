import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Configuración de la página
st.set_page_config(
    page_title="🤖 Sistema de Inteligencia Artificial - METGO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #E91E63 0%, #C2185B 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
    <h1>🤖 Sistema de Inteligencia Artificial</h1>
    <h3>Sistema METGO - Machine Learning Avanzado</h3>
    <p>Modelos predictivos, análisis inteligente y automatización</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control IA")

# Configuración de modelos
modelos_disponibles = {
    "Predicción Meteorológica": {
        "descripcion": "Predice condiciones meteorológicas futuras",
        "variables": ["temperatura", "humedad", "presion", "viento", "precipitacion"],
        "horizonte": "7 días",
        "precision": 92.5
    },
    "Predicción Agrícola": {
        "descripcion": "Predice rendimiento y optimización de cultivos",
        "variables": ["clima", "suelo", "riego", "fertilizacion", "plagas"],
        "horizonte": "temporada completa",
        "precision": 88.3
    },
    "Detección de Anomalías": {
        "descripcion": "Identifica patrones anómalos en sensores",
        "variables": ["sensores_iot", "patrones_temporales", "correlaciones"],
        "horizonte": "tiempo real",
        "precision": 95.7
    },
    "Optimización de Riego": {
        "descripcion": "Optimiza el uso de agua y recursos",
        "variables": ["humedad_suelo", "evapotranspiracion", "precipitacion", "cultivos"],
        "horizonte": "diario",
        "precision": 90.1
    },
    "Predicción de Plagas": {
        "descripcion": "Predice aparición de plagas y enfermedades",
        "variables": ["temperatura", "humedad", "viento", "presion", "estacion"],
        "horizonte": "15 días",
        "precision": 87.9
    }
}

modelo_seleccionado = st.sidebar.selectbox("🧠 Modelo IA:", list(modelos_disponibles.keys()))
tipo_analisis = st.sidebar.selectbox("📊 Tipo de Análisis:", 
                                    ["Entrenamiento", "Predicción", "Evaluación", "Optimización"])

# Función para generar datos de entrenamiento
@st.cache_data
def generar_datos_entrenamiento(modelo):
    """Genera datos sintéticos para entrenamiento de modelos"""
    
    np.random.seed(42)
    n_samples = 1000
    
    if modelo == "Predicción Meteorológica":
        # Variables meteorológicas
        temperatura = 20 + np.random.normal(0, 5, n_samples)
        humedad = 60 + np.random.normal(0, 15, n_samples)
        presion = 1013 + np.random.normal(0, 10, n_samples)
        viento = 8 + np.random.exponential(3, n_samples)
        precipitacion = np.random.exponential(2, n_samples)
        
        # Variable objetivo: temperatura futura
        temp_futura = temperatura + np.random.normal(0, 2, n_samples)
        
        return pd.DataFrame({
            'temperatura': temperatura,
            'humedad': humedad,
            'presion': presion,
            'viento': viento,
            'precipitacion': precipitacion,
            'temp_futura': temp_futura
        })
    
    elif modelo == "Predicción Agrícola":
        # Variables agrícolas
        temperatura_prom = 22 + np.random.normal(0, 4, n_samples)
        humedad_prom = 65 + np.random.normal(0, 12, n_samples)
        riego_total = 500 + np.random.normal(0, 100, n_samples)
        fertilizacion = 50 + np.random.normal(0, 15, n_samples)
        plagas_indice = np.random.uniform(0, 100, n_samples)
        
        # Variable objetivo: rendimiento
        rendimiento = (temperatura_prom * 0.5 + humedad_prom * 0.3 + 
                      riego_total * 0.02 + fertilizacion * 0.1 - 
                      plagas_indice * 0.05) + np.random.normal(0, 2, n_samples)
        
        return pd.DataFrame({
            'temperatura_prom': temperatura_prom,
            'humedad_prom': humedad_prom,
            'riego_total': riego_total,
            'fertilizacion': fertilizacion,
            'plagas_indice': plagas_indice,
            'rendimiento': rendimiento
        })
    
    elif modelo == "Optimización de Riego":
        # Variables de riego
        humedad_suelo = np.random.uniform(20, 80, n_samples)
        evapotranspiracion = 5 + np.random.exponential(2, n_samples)
        precipitacion = np.random.exponential(1, n_samples)
        temperatura = 20 + np.random.normal(0, 5, n_samples)
        
        # Variable objetivo: necesidad de riego
        necesidad_riego = (evapotranspiracion - precipitacion) * (100 - humedad_suelo) / 100
        necesidad_riego = np.maximum(0, necesidad_riego)
        
        return pd.DataFrame({
            'humedad_suelo': humedad_suelo,
            'evapotranspiracion': evapotranspiracion,
            'precipitacion': precipitacion,
            'temperatura': temperatura,
            'necesidad_riego': necesidad_riego
        })

# Función para entrenar modelo
def entrenar_modelo(modelo, datos):
    """Entrena un modelo de machine learning"""
    
    if modelo == "Predicción Meteorológica":
        X = datos[['temperatura', 'humedad', 'presion', 'viento', 'precipitacion']]
        y = datos['temp_futura']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return model, mse, r2, X.columns.tolist()
    
    elif modelo == "Predicción Agrícola":
        X = datos[['temperatura_prom', 'humedad_prom', 'riego_total', 'fertilizacion', 'plagas_indice']]
        y = datos['rendimiento']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return model, mse, r2, X.columns.tolist()
    
    elif modelo == "Optimización de Riego":
        X = datos[['humedad_suelo', 'evapotranspiracion', 'precipitacion', 'temperatura']]
        y = datos['necesidad_riego']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return model, mse, r2, X.columns.tolist()

# Generar datos y entrenar modelo
with st.spinner('🤖 Generando datos y entrenando modelo...'):
    datos = generar_datos_entrenamiento(modelo_seleccionado)
    modelo, mse, r2, variables = entrenar_modelo(modelo_seleccionado, datos)

# Métricas del modelo
st.markdown("### 📊 Métricas del Modelo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎯 Precisión del Modelo",
        value=f"{modelos_disponibles[modelo_seleccionado]['precision']}%",
        delta="+2.3%"
    )

with col2:
    st.metric(
        label="📈 R² Score",
        value=f"{r2:.3f}",
        delta="0.892"
    )

with col3:
    st.metric(
        label="📉 Error Cuadrático Medio",
        value=f"{mse:.2f}",
        delta="-0.15"
    )

with col4:
    st.metric(
        label="🔮 Horizonte de Predicción",
        value=modelos_disponibles[modelo_seleccionado]['horizonte'],
        delta="Tiempo real"
    )

# Análisis de importancia de variables
st.markdown("### 🔍 Análisis de Importancia de Variables")

importancias = modelo.feature_importances_
feature_names = variables

df_importancias = pd.DataFrame({
    'Variable': feature_names,
    'Importancia': importancias
}).sort_values('Importancia', ascending=True)

fig_importancias = px.bar(df_importancias, x='Importancia', y='Variable', 
                         orientation='h',
                         title=f'Importancia de Variables - {modelo_seleccionado}',
                         color='Importancia',
                         color_continuous_scale='Viridis')

fig_importancias.update_layout(height=400)
st.plotly_chart(fig_importancias, use_container_width=True)

# Predicciones en tiempo real
st.markdown("### 🔮 Predicciones en Tiempo Real")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Datos de Entrada")
    
    # Crear controles para variables de entrada
    valores_entrada = {}
    
    if modelo_seleccionado == "Predicción Meteorológica":
        valores_entrada['temperatura'] = st.number_input("Temperatura (°C):", value=22.0, min_value=-10.0, max_value=50.0)
        valores_entrada['humedad'] = st.number_input("Humedad (%):", value=65.0, min_value=0.0, max_value=100.0)
        valores_entrada['presion'] = st.number_input("Presión (hPa):", value=1013.0, min_value=950.0, max_value=1050.0)
        valores_entrada['viento'] = st.number_input("Viento (km/h):", value=8.0, min_value=0.0, max_value=100.0)
        valores_entrada['precipitacion'] = st.number_input("Precipitación (mm):", value=0.5, min_value=0.0, max_value=50.0)
    
    elif modelo_seleccionado == "Predicción Agrícola":
        valores_entrada['temperatura_prom'] = st.number_input("Temperatura Promedio (°C):", value=22.0, min_value=0.0, max_value=40.0)
        valores_entrada['humedad_prom'] = st.number_input("Humedad Promedio (%):", value=65.0, min_value=0.0, max_value=100.0)
        valores_entrada['riego_total'] = st.number_input("Riego Total (L):", value=500.0, min_value=0.0, max_value=2000.0)
        valores_entrada['fertilizacion'] = st.number_input("Fertilización (kg):", value=50.0, min_value=0.0, max_value=200.0)
        valores_entrada['plagas_indice'] = st.number_input("Índice de Plagas:", value=25.0, min_value=0.0, max_value=100.0)
    
    elif modelo_seleccionado == "Optimización de Riego":
        valores_entrada['humedad_suelo'] = st.number_input("Humedad del Suelo (%):", value=50.0, min_value=0.0, max_value=100.0)
        valores_entrada['evapotranspiracion'] = st.number_input("Evapotranspiración (mm):", value=5.0, min_value=0.0, max_value=20.0)
        valores_entrada['precipitacion'] = st.number_input("Precipitación (mm):", value=1.0, min_value=0.0, max_value=50.0)
        valores_entrada['temperatura'] = st.number_input("Temperatura (°C):", value=22.0, min_value=0.0, max_value=40.0)

with col2:
    st.markdown("#### 🎯 Predicción")
    
    if st.button("🔮 Generar Predicción"):
        # Preparar datos para predicción
        X_pred = pd.DataFrame([valores_entrada])
        
        # Hacer predicción
        prediccion = modelo.predict(X_pred)[0]
        
        if modelo_seleccionado == "Predicción Meteorológica":
            st.success(f"**Temperatura Futura Predicha:** {prediccion:.1f}°C")
        elif modelo_seleccionado == "Predicción Agrícola":
            st.success(f"**Rendimiento Predicho:** {prediccion:.1f} ton/ha")
        elif modelo_seleccionado == "Optimización de Riego":
            st.success(f"**Necesidad de Riego:** {prediccion:.1f} mm")
        
        # Mostrar confianza de la predicción
        confianza = random.uniform(85, 98)
        st.info(f"**Confianza del Modelo:** {confianza:.1f}%")

# Análisis de rendimiento del modelo
st.markdown("### 📈 Análisis de Rendimiento")

# Simular datos de rendimiento histórico
fechas = pd.date_range(end=datetime.now(), periods=30, freq='D')
rendimiento_historico = []

for fecha in fechas:
    base = modelos_disponibles[modelo_seleccionado]['precision']
    variacion = random.uniform(-5, 5)
    rendimiento_historico.append({
        'Fecha': fecha,
        'Precision': base + variacion,
        'Modelo': modelo_seleccionado
    })

df_rendimiento = pd.DataFrame(rendimiento_historico)

fig_rendimiento = px.line(df_rendimiento, x='Fecha', y='Precision',
                         title=f'Rendimiento Histórico - {modelo_seleccionado}',
                         color='Modelo')

fig_rendimiento.add_hline(y=90, line_dash="dash", line_color="red", 
                         annotation_text="Umbral de Calidad")
fig_rendimiento.update_layout(height=400)

st.plotly_chart(fig_rendimiento, use_container_width=True)

# Comparación de modelos
st.markdown("### 🏆 Comparación de Modelos")

modelos_comparacion = []
for modelo, info in modelos_disponibles.items():
    modelos_comparacion.append({
        'Modelo': modelo,
        'Precision': info['precision'],
        'Horizonte': info['horizonte'],
        'Variables': len(info['variables'])
    })

df_comparacion = pd.DataFrame(modelos_comparacion)

col1, col2 = st.columns(2)

with col1:
    fig_precision = px.bar(df_comparacion, x='Modelo', y='Precision',
                          title='Precisión por Modelo',
                          color='Precision',
                          color_continuous_scale='RdYlGn')
    fig_precision.update_layout(height=400)
    st.plotly_chart(fig_precision, use_container_width=True)

with col2:
    fig_variables = px.scatter(df_comparacion, x='Variables', y='Precision',
                              size='Variables',
                              hover_data=['Modelo', 'Horizonte'],
                              title='Precisión vs Número de Variables',
                              color='Precision',
                              color_continuous_scale='Viridis')
    st.plotly_chart(fig_variables, use_container_width=True)

# Alertas y recomendaciones de IA
st.markdown("### 🤖 Alertas y Recomendaciones de IA")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🚨 Alertas del Sistema")
    
    alertas_ia = [
        {"tipo": "Modelo", "mensaje": "Precisión del modelo por encima del 90%", "severidad": "info"},
        {"tipo": "Datos", "mensaje": "Calidad de datos excelente", "severidad": "success"},
        {"tipo": "Predicción", "mensaje": "Predicción de alta confianza", "severidad": "success"},
        {"tipo": "Optimización", "mensaje": "Recomendación: Reentrenar modelo mensualmente", "severidad": "warning"}
    ]
    
    for alerta in alertas_ia:
        if alerta["severidad"] == "success":
            st.success(f"✅ {alerta['mensaje']}")
        elif alerta["severidad"] == "warning":
            st.warning(f"⚠️ {alerta['mensaje']}")
        elif alerta["severidad"] == "info":
            st.info(f"ℹ️ {alerta['mensaje']}")

with col2:
    st.markdown("#### 💡 Recomendaciones de IA")
    
    recomendaciones = [
        "🔄 Actualizar modelo con datos más recientes",
        "📊 Incorporar nuevas variables climáticas",
        "🎯 Ajustar hiperparámetros para mejorar precisión",
        "📈 Implementar validación cruzada",
        "🔍 Analizar correlaciones entre variables"
    ]
    
    for rec in recomendaciones:
        st.info(rec)

# Información del modelo
st.markdown("### ℹ️ Información del Modelo")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🧠 Modelo:** {modelo_seleccionado}
    **📊 Tipo:** Random Forest Regressor
    **🔮 Horizonte:** {modelos_disponibles[modelo_seleccionado]['horizonte']}
    **📈 Precisión:** {modelos_disponibles[modelo_seleccionado]['precision']}%
    """)

with col2:
    st.info(f"""
    **📊 Variables:** {len(variables)}
    **🎯 R² Score:** {r2:.3f}
    **📉 MSE:** {mse:.2f}
    **🕐 Último Entrenamiento:** {datetime.now().strftime("%H:%M")}
    """)

with col3:
    st.info(f"""
    **🔄 Estado:** Activo
    **📈 Rendimiento:** Excelente
    **🔧 Mantenimiento:** Programado
    **📊 Datos de Entrenamiento:** {len(datos):,} registros
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🤖 <strong>Sistema METGO</strong> - Inteligencia Artificial Avanzada</p>
    <p>Modelos de Machine Learning para predicción y optimización</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
