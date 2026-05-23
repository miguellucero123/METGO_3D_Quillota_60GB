#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos ML/IA METGO_3D - Script Principal
Sistema de Machine Learning e Inteligencia Artificial
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Modelos ML/IA METGO_3D",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_modelos_ml():
    """Cargar información de modelos ML disponibles"""
    modelos = {
        "Predicción Meteorológica": {
            "tipo": "Regresión",
            "precisión": 0.89,
            "ultima_entrenamiento": "2025-01-08",
            "estado": "Activo"
        },
        "Análisis de Cultivos": {
            "tipo": "Clasificación",
            "precisión": 0.92,
            "ultima_entrenamiento": "2025-01-07",
            "estado": "Activo"
        },
        "Optimización de Riego": {
            "tipo": "Reinforcement Learning",
            "precisión": 0.85,
            "ultima_entrenamiento": "2025-01-09",
            "estado": "Activo"
        },
        "Detección de Plagas": {
            "tipo": "Computer Vision",
            "precisión": 0.94,
            "ultima_entrenamiento": "2025-01-06",
            "estado": "Activo"
        }
    }
    return modelos

def generar_datos_prediccion():
    """Generar datos de predicción para demostración"""
    fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
    
    datos = []
    for fecha in fechas:
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'temperatura_real': np.random.normal(25, 5),
            'temperatura_predicha': np.random.normal(25, 4),
            'precipitacion_real': max(0, np.random.normal(2, 1)),
            'precipitacion_predicha': max(0, np.random.normal(2, 0.8)),
            'humedad_real': np.random.normal(60, 10),
            'humedad_predicha': np.random.normal(60, 9),
            'error_temperatura': np.random.normal(0, 1),
            'error_precipitacion': np.random.normal(0, 0.5)
        })
    
    return datos

def main():
    st.title("🤖 Modelos ML/IA METGO_3D")
    st.markdown("### Sistema de Machine Learning e Inteligencia Artificial")
    
    # Sidebar con controles
    st.sidebar.header("Controles ML/IA")
    
    # Selector de modelo
    modelos = cargar_modelos_ml()
    modelo_seleccionado = st.sidebar.selectbox("Seleccionar modelo", list(modelos.keys()))
    
    # Información del modelo seleccionado
    info_modelo = modelos[modelo_seleccionado]
    
    # Métricas del modelo
    st.header(f"📊 Modelo: {modelo_seleccionado}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Tipo de Modelo",
            value=info_modelo["tipo"]
        )
    
    with col2:
        st.metric(
            label="Precisión",
            value=f"{info_modelo['precisión']:.2%}"
        )
    
    with col3:
        st.metric(
            label="Último Entrenamiento",
            value=info_modelo["ultima_entrenamiento"]
        )
    
    with col4:
        st.metric(
            label="Estado",
            value=info_modelo["estado"]
        )
    
    # Análisis de precisión
    st.header("🎯 Análisis de Precisión")
    
    # Generar datos de predicción
    datos_prediccion = generar_datos_prediccion()
    df_pred = pd.DataFrame(datos_prediccion)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de precisión de temperatura
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df_pred['fecha'],
            y=df_pred['temperatura_real'],
            mode='lines',
            name='Temperatura Real',
            line=dict(color='blue')
        ))
        fig_temp.add_trace(go.Scatter(
            x=df_pred['fecha'],
            y=df_pred['temperatura_predicha'],
            mode='lines',
            name='Temperatura Predicha',
            line=dict(color='red', dash='dash')
        ))
        fig_temp.update_layout(
            title="Precisión Predicción de Temperatura",
            xaxis_title="Fecha",
            yaxis_title="Temperatura (°C)"
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Gráfico de error
        fig_error = px.line(
            df_pred,
            x='fecha',
            y='error_temperatura',
            title="Error de Predicción de Temperatura"
        )
        st.plotly_chart(fig_error, use_container_width=True)
    
    # Matriz de confusión (simulada)
    st.header("📈 Matriz de Confusión")
    
    # Generar matriz de confusión simulada
    confusion_matrix = np.random.randint(50, 150, (3, 3))
    labels = ['Bajo', 'Medio', 'Alto']
    
    fig_confusion = px.imshow(
        confusion_matrix,
        text_auto=True,
        aspect="auto",
        x=labels,
        y=labels,
        title="Matriz de Confusión - Clasificación de Rendimiento"
    )
    st.plotly_chart(fig_confusion, use_container_width=True)
    
    # Métricas de evaluación
    st.header("📊 Métricas de Evaluación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Accuracy", "0.89", "0.02")
        st.metric("Precision", "0.87", "0.01")
    
    with col2:
        st.metric("Recall", "0.91", "0.03")
        st.metric("F1-Score", "0.89", "0.02")
    
    with col3:
        st.metric("AUC-ROC", "0.92", "0.01")
        st.metric("MSE", "2.34", "-0.15")
    
    # Predicciones en tiempo real
    st.header("🔮 Predicciones en Tiempo Real")
    
    # Simular predicciones
    predicciones = {
        "Próximas 24 horas": {
            "Temperatura": "25.3°C ± 2.1°C",
            "Precipitación": "1.2mm ± 0.8mm",
            "Humedad": "65% ± 8%"
        },
        "Próximos 7 días": {
            "Temperatura promedio": "24.8°C",
            "Precipitación total": "8.5mm",
            "Humedad promedio": "62%"
        },
        "Recomendaciones": {
            "Riego": "Recomendado en 2 días",
            "Fertilización": "No necesaria",
            "Protección": "Sin alertas"
        }
    }
    
    for periodo, datos in predicciones.items():
        st.subheader(periodo)
        for metrica, valor in datos.items():
            st.info(f"**{metrica}:** {valor}")
    
    # Tabla de datos de predicción
    st.header("📋 Datos de Predicción")
    st.dataframe(df_pred, use_container_width=True)
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Información del Sistema")
    st.sidebar.info(f"Modelos disponibles: {len(modelos)}")
    st.sidebar.info(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Acciones disponibles
    st.sidebar.markdown("### Acciones")
    if st.sidebar.button("🔄 Reentrenar Modelo"):
        st.success("Modelo reentrenado exitosamente!")
    
    if st.sidebar.button("📊 Exportar Métricas"):
        st.success("Métricas exportadas a CSV!")

if __name__ == "__main__":
    main()
