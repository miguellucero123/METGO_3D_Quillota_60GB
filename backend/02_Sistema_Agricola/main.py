#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Agrícola METGO_3D - Script Principal
Gestión agrícola y recomendaciones de cultivo
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
    page_title="Sistema Agrícola METGO_3D",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_datos_agricolas():
    """Cargar datos agrícolas desde archivos disponibles"""
    datos = {}
    
    # Intentar cargar desde diferentes fuentes
    archivos_datos = [
        "scripts/metgo_agricola.db",
        "scripts/ml_avanzado_agricola.db",
        "scripts/analisis_economico_agricola.db"
    ]
    
    for archivo in archivos_datos:
        if os.path.exists(archivo):
            try:
                if archivo.endswith('.db'):
                    import sqlite3
                    conn = sqlite3.connect(archivo)
                    df = pd.read_sql_query("SELECT * FROM datos_agricolas LIMIT 100", conn)
                    conn.close()
                    if not df.empty:
                        datos = df.to_dict('records')
                        break
            except Exception as e:
                st.warning(f"Error cargando {archivo}: {e}")
    
    return datos

def generar_datos_demo():
    """Generar datos de demostración agrícolas"""
    cultivos = ['Tomate', 'Lechuga', 'Pimiento', 'Zanahoria', 'Cebolla']
    fechas = pd.date_range(start='2025-01-01', end='2025-01-30', freq='D')
    
    datos = []
    for fecha in fechas:
        for cultivo in cultivos:
            datos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'cultivo': cultivo,
                'temperatura_suelo': np.random.normal(20, 3),
                'humedad_suelo': np.random.normal(60, 10),
                'ph_suelo': np.random.normal(6.5, 0.5),
                'nutrientes_n': np.random.normal(50, 10),
                'nutrientes_p': np.random.normal(30, 5),
                'nutrientes_k': np.random.normal(40, 8),
                'rendimiento_esperado': np.random.normal(100, 20),
                'costo_produccion': np.random.normal(500, 100)
            })
    
    return datos

def main():
    st.title("🌾 Sistema Agrícola METGO_3D")
    st.markdown("### Gestión Agrícola y Recomendaciones de Cultivo")
    
    # Cargar datos
    datos = cargar_datos_agricolas()
    
    if not datos:
        st.info("Generando datos de demostración agrícolas...")
        datos = generar_datos_demo()
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Sidebar con controles
    st.sidebar.header("Controles Agrícolas")
    
    # Selector de cultivo
    if 'cultivo' in df.columns:
        cultivos_disponibles = df['cultivo'].unique()
        cultivo_seleccionado = st.sidebar.selectbox("Seleccionar cultivo", cultivos_disponibles)
        df_filtrado = df[df['cultivo'] == cultivo_seleccionado]
    else:
        df_filtrado = df
    
    # Selector de parámetro
    parametros_agricolas = [col for col in df.columns if col not in ['fecha', 'cultivo']]
    parametro = st.sidebar.selectbox("Seleccionar parámetro", parametros_agricolas)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if parametro in df_filtrado.columns:
            valor_actual = df_filtrado[parametro].iloc[-1] if len(df_filtrado) > 0 else 0
            st.metric(
                label=f"{parametro.replace('_', ' ').title()} Actual",
                value=f"{valor_actual:.1f}"
            )
    
    with col2:
        if parametro in df_filtrado.columns:
            valor_promedio = df_filtrado[parametro].mean() if len(df_filtrado) > 0 else 0
            st.metric(
                label=f"{parametro.replace('_', ' ').title()} Promedio",
                value=f"{valor_promedio:.1f}"
            )
    
    with col3:
        if parametro in df_filtrado.columns:
            valor_max = df_filtrado[parametro].max() if len(df_filtrado) > 0 else 0
            st.metric(
                label=f"{parametro.replace('_', ' ').title()} Máximo",
                value=f"{valor_max:.1f}"
            )
    
    with col4:
        if parametro in df_filtrado.columns:
            valor_min = df_filtrado[parametro].min() if len(df_filtrado) > 0 else 0
            st.metric(
                label=f"{parametro.replace('_', ' ').title()} Mínimo",
                value=f"{valor_min:.1f}"
            )
    
    # Recomendaciones agrícolas
    st.header("🤖 Recomendaciones Inteligentes")
    
    if len(df_filtrado) > 0:
        # Análisis de condiciones del suelo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Análisis de Suelo")
            
            if 'ph_suelo' in df_filtrado.columns:
                ph_actual = df_filtrado['ph_suelo'].iloc[-1]
                if ph_actual < 6.0:
                    st.error("⚠️ pH del suelo bajo. Recomendación: Aplicar cal")
                elif ph_actual > 7.5:
                    st.warning("⚠️ pH del suelo alto. Recomendación: Aplicar azufre")
                else:
                    st.success("✅ pH del suelo óptimo")
            
            if 'humedad_suelo' in df_filtrado.columns:
                humedad_actual = df_filtrado['humedad_suelo'].iloc[-1]
                if humedad_actual < 40:
                    st.error("⚠️ Humedad del suelo baja. Recomendación: Riego")
                elif humedad_actual > 80:
                    st.warning("⚠️ Humedad del suelo alta. Recomendación: Drenaje")
                else:
                    st.success("✅ Humedad del suelo óptima")
        
        with col2:
            st.subheader("Análisis de Nutrientes")
            
            if 'nutrientes_n' in df_filtrado.columns:
                n_actual = df_filtrado['nutrientes_n'].iloc[-1]
                if n_actual < 30:
                    st.error("⚠️ Nitrógeno bajo. Recomendación: Fertilizante nitrogenado")
                else:
                    st.success("✅ Nitrógeno adecuado")
            
            if 'rendimiento_esperado' in df_filtrado.columns:
                rendimiento = df_filtrado['rendimiento_esperado'].iloc[-1]
                st.info(f"📈 Rendimiento esperado: {rendimiento:.1f} kg/ha")
    
    # Gráficos
    st.header("📊 Análisis Agrícola")
    
    if parametro in df_filtrado.columns and len(df_filtrado) > 0:
        # Gráfico de línea temporal
        fig_linea = px.line(
            df_filtrado, 
            x='fecha' if 'fecha' in df_filtrado.columns else df_filtrado.index,
            y=parametro,
            title=f"Evolución de {parametro.replace('_', ' ').title()}",
            labels={'x': 'Fecha', 'y': parametro.replace('_', ' ').title()}
        )
        st.plotly_chart(fig_linea, use_container_width=True)
        
        # Gráfico de barras por cultivo
        if 'cultivo' in df.columns:
            df_promedio = df.groupby('cultivo')[parametro].mean().reset_index()
            fig_barras = px.bar(
                df_promedio,
                x='cultivo',
                y=parametro,
                title=f"{parametro.replace('_', ' ').title()} por Cultivo"
            )
            st.plotly_chart(fig_barras, use_container_width=True)
    
    # Tabla de datos
    st.header("📋 Datos Agrícolas")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Información del Sistema")
    st.sidebar.info(f"Total de registros: {len(df)}")
    st.sidebar.info(f"Cultivos: {len(df['cultivo'].unique()) if 'cultivo' in df.columns else 'N/A'}")
    st.sidebar.info(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
