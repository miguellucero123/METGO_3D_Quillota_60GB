#!/usr/bin/env python3
"""
Sistema de Alertas Visuales Integrado METGO 3D
Integra alertas meteorológicas con recomendaciones agrícolas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import json

class SistemaAlertasVisualesIntegrado:
    def __init__(self, db_path="datos_meteorologicos.db"):
        self.db_path = db_path
        self.estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
        
        # Umbrales de alerta
        self.umbrales = {
            'helada_critica': 2,
            'helada_moderada': 5,
            'temperatura_alta': 35,
            'humedad_alta': 85,
            'humedad_baja': 30,
            'viento_fuerte': 25,
            'precipitacion_intensa': 15
        }
        
        # Colores para alertas
        self.colores_alertas = {
            'critica': '#FF0000',      # Rojo
            'alta': '#FF6600',         # Naranja
            'moderada': '#FFCC00',     # Amarillo
            'baja': '#00CC66',         # Verde
            'info': '#0066CC'          # Azul
        }
    
    def obtener_datos_actuales(self):
        """Obtener datos meteorológicos actuales"""
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
            
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def analizar_alertas_meteorologicas(self, datos):
        """Analizar y generar alertas meteorológicas"""
        if datos.empty:
            return []
        
        alertas = []
        
        for _, row in datos.iterrows():
            estacion = row['estacion']
            temp = row['temperatura']
            humedad = row['humedad']
            viento = row['velocidad_viento']
            precipitacion = row['precipitacion']
            
            # Alerta de helada crítica
            if temp <= self.umbrales['helada_critica']:
                alertas.append({
                    'tipo': 'helada',
                    'nivel': 'critica',
                    'estacion': estacion,
                    'valor': temp,
                    'mensaje': f'Helada crítica en {estacion}: {temp:.1f}°C',
                    'accion': 'Activar protección inmediata',
                    'icono': '❄️'
                })
            
            # Alerta de helada moderada
            elif temp <= self.umbrales['helada_moderada']:
                alertas.append({
                    'tipo': 'helada',
                    'nivel': 'alta',
                    'estacion': estacion,
                    'valor': temp,
                    'mensaje': f'Riesgo de helada en {estacion}: {temp:.1f}°C',
                    'accion': 'Preparar sistemas de protección',
                    'icono': '⚠️'
                })
            
            # Alerta de temperatura alta
            if temp >= self.umbrales['temperatura_alta']:
                alertas.append({
                    'tipo': 'temperatura',
                    'nivel': 'alta',
                    'estacion': estacion,
                    'valor': temp,
                    'mensaje': f'Temperatura alta en {estacion}: {temp:.1f}°C',
                    'accion': 'Aumentar riego y sombreado',
                    'icono': '🌡️'
                })
            
            # Alerta de humedad alta
            if humedad >= self.umbrales['humedad_alta']:
                alertas.append({
                    'tipo': 'humedad',
                    'nivel': 'moderada',
                    'estacion': estacion,
                    'valor': humedad,
                    'mensaje': f'Humedad alta en {estacion}: {humedad:.1f}%',
                    'accion': 'Mejorar ventilación',
                    'icono': '💧'
                })
            
            # Alerta de humedad baja
            elif humedad <= self.umbrales['humedad_baja']:
                alertas.append({
                    'tipo': 'humedad',
                    'nivel': 'moderada',
                    'estacion': estacion,
                    'valor': humedad,
                    'mensaje': f'Humedad baja en {estacion}: {humedad:.1f}%',
                    'accion': 'Considerar riego foliar',
                    'icono': '💧'
                })
            
            # Alerta de viento fuerte
            if viento >= self.umbrales['viento_fuerte']:
                alertas.append({
                    'tipo': 'viento',
                    'nivel': 'alta',
                    'estacion': estacion,
                    'valor': viento,
                    'mensaje': f'Viento fuerte en {estacion}: {viento:.1f} km/h',
                    'accion': 'Revisar estructuras de protección',
                    'icono': '💨'
                })
            
            # Alerta de precipitación intensa
            if precipitacion >= self.umbrales['precipitacion_intensa']:
                alertas.append({
                    'tipo': 'precipitacion',
                    'nivel': 'alta',
                    'estacion': estacion,
                    'valor': precipitacion,
                    'mensaje': f'Precipitación intensa en {estacion}: {precipitacion:.1f}mm',
                    'accion': 'Revisar drenaje',
                    'icono': '🌧️'
                })
        
        return alertas
    
    def generar_recomendaciones_agricolas(self, alertas):
        """Generar recomendaciones agrícolas basadas en alertas"""
        recomendaciones = []
        
        # Agrupar alertas por tipo
        alertas_por_tipo = {}
        for alerta in alertas:
            tipo = alerta['tipo']
            if tipo not in alertas_por_tipo:
                alertas_por_tipo[tipo] = []
            alertas_por_tipo[tipo].append(alerta)
        
        # Recomendaciones para heladas
        if 'helada' in alertas_por_tipo:
            heladas = alertas_por_tipo['helada']
            criticas = [h for h in heladas if h['nivel'] == 'critica']
            
            if criticas:
                recomendaciones.append({
                    'tipo': 'proteccion_helada',
                    'nivel': 'critica',
                    'titulo': 'Protección Crítica contra Heladas',
                    'descripcion': f'Se detectaron {len(criticas)} heladas críticas. Acción inmediata requerida.',
                    'acciones': [
                        'Activar sistemas de calefacción',
                        'Aplicar riego por aspersión',
                        'Usar cubiertas de protección',
                        'Considerar ventiladores'
                    ],
                    'icono': '🚨'
                })
            else:
                recomendaciones.append({
                    'tipo': 'proteccion_helada',
                    'nivel': 'moderada',
                    'titulo': 'Preparación contra Heladas',
                    'descripcion': 'Riesgo moderado de heladas detectado.',
                    'acciones': [
                        'Revisar sistemas de protección',
                        'Preparar cubiertas',
                        'Monitorear temperaturas nocturnas'
                    ],
                    'icono': '⚠️'
                })
        
        # Recomendaciones para temperatura
        if 'temperatura' in alertas_por_tipo:
            recomendaciones.append({
                'tipo': 'gestion_termica',
                'nivel': 'alta',
                'titulo': 'Gestión de Estrés Térmico',
                'descripcion': 'Temperaturas altas detectadas. Proteger cultivos del estrés térmico.',
                'acciones': [
                    'Aumentar frecuencia de riego',
                    'Aplicar sombreado',
                    'Usar mulch para conservar humedad',
                    'Evitar labores en horas de máximo calor'
                ],
                'icono': '🌡️'
            })
        
        # Recomendaciones para humedad
        if 'humedad' in alertas_por_tipo:
            humedad_alta = [h for h in alertas_por_tipo['humedad'] if h['valor'] >= self.umbrales['humedad_alta']]
            humedad_baja = [h for h in alertas_por_tipo['humedad'] if h['valor'] <= self.umbrales['humedad_baja']]
            
            if humedad_alta:
                recomendaciones.append({
                    'tipo': 'gestion_humedad',
                    'nivel': 'moderada',
                    'titulo': 'Control de Humedad Alta',
                    'descripcion': 'Humedad alta detectada. Riesgo de enfermedades fúngicas.',
                    'acciones': [
                        'Mejorar ventilación',
                        'Aplicar fungicidas preventivos',
                        'Evitar riego foliar',
                        'Espaciar plantas para mejor circulación'
                    ],
                    'icono': '💧'
                })
            
            if humedad_baja:
                recomendaciones.append({
                    'tipo': 'gestion_humedad',
                    'nivel': 'moderada',
                    'titulo': 'Control de Humedad Baja',
                    'descripcion': 'Humedad baja detectada. Riesgo de estrés hídrico.',
                    'acciones': [
                        'Aumentar frecuencia de riego',
                        'Aplicar riego foliar en horas frescas',
                        'Usar mulch para conservar humedad',
                        'Considerar nebulización'
                    ],
                    'icono': '💧'
                })
        
        # Recomendaciones para viento
        if 'viento' in alertas_por_tipo:
            recomendaciones.append({
                'tipo': 'proteccion_viento',
                'nivel': 'alta',
                'titulo': 'Protección contra Viento Fuerte',
                'descripcion': 'Vientos fuertes detectados. Proteger estructuras y cultivos.',
                'acciones': [
                    'Revisar y reforzar tutores',
                    'Asegurar cubiertas de invernadero',
                    'Proteger plantas jóvenes',
                    'Evitar aplicaciones foliares'
                ],
                'icono': '💨'
            })
        
        return recomendaciones
    
    def crear_grafico_alertas_tiempo_real(self, alertas):
        """Crear gráfico de alertas en tiempo real"""
        if not alertas:
            # Crear gráfico vacío
            fig = go.Figure()
            fig.add_annotation(
                text="✅ No hay alertas activas",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="green")
            )
            fig.update_layout(
                title="Estado de Alertas Meteorológicas",
                xaxis=dict(showgrid=False, showticklabels=False, showlegend=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                height=300
            )
            return fig
        
        # Preparar datos para el gráfico
        tipos = [alerta['tipo'] for alerta in alertas]
        niveles = [alerta['nivel'] for alerta in alertas]
        estaciones = [alerta['estacion'] for alerta in alertas]
        valores = [alerta['valor'] for alerta in alertas]
        
        # Crear colores según el nivel de alerta
        colores = [self.colores_alertas.get(nivel, '#666666') for nivel in niveles]
        
        # Crear gráfico de barras
        fig = go.Figure(data=[
            go.Bar(
                x=estaciones,
                y=valores,
                marker_color=colores,
                text=[f"{tipo}<br>{valor:.1f}" for tipo, valor in zip(tipos, valores)],
                textposition='auto',
                hovertemplate="<b>%{x}</b><br>Tipo: %{text}<br>Valor: %{y}<br><extra></extra>"
            )
        ])
        
        fig.update_layout(
            title="Alertas Meteorológicas por Estación",
            xaxis_title="Estaciones",
            yaxis_title="Valor",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def crear_mapa_calor_alertas(self, datos):
        """Crear mapa de calor de alertas por estación"""
        if datos.empty:
            return go.Figure()
        
        # Preparar matriz de datos
        variables = ['temperatura', 'humedad', 'velocidad_viento', 'precipitacion']
        estaciones = datos['estacion'].tolist()
        
        matriz_alertas = []
        for estacion in estaciones:
            fila = []
            row_data = datos[datos['estacion'] == estacion].iloc[0]
            
            for var in variables:
                valor = row_data[var]
                # Normalizar valores para el mapa de calor (0-1)
                if var == 'temperatura':
                    # Helada crítica = 1, normal = 0
                    alerta = 1 if valor <= 2 else 0.5 if valor <= 5 else 0
                elif var == 'humedad':
                    # Humedad extrema = 1, normal = 0
                    alerta = 1 if valor >= 85 or valor <= 30 else 0
                elif var == 'velocidad_viento':
                    # Viento fuerte = 1, normal = 0
                    alerta = 1 if valor >= 25 else 0
                elif var == 'precipitacion':
                    # Precipitación intensa = 1, normal = 0
                    alerta = 1 if valor >= 15 else 0
                
                fila.append(alerta)
            matriz_alertas.append(fila)
        
        fig = go.Figure(data=go.Heatmap(
            z=matriz_alertas,
            x=variables,
            y=estaciones,
            colorscale='Reds',
            showscale=True,
            hovertemplate="Estación: %{y}<br>Variable: %{x}<br>Nivel de Alerta: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Mapa de Calor - Nivel de Alertas por Estación y Variable",
            xaxis_title="Variables Meteorológicas",
            yaxis_title="Estaciones",
            height=400
        , showlegend=False)
        
        return fig
    
    def mostrar_panel_alertas(self, alertas):
        """Mostrar panel de alertas visual"""
        if not alertas:
            st.success("✅ **No hay alertas activas** - Condiciones meteorológicas normales")
            return
        
        # Agrupar alertas por nivel
        alertas_criticas = [a for a in alertas if a['nivel'] == 'critica']
        alertas_altas = [a for a in alertas if a['nivel'] == 'alta']
        alertas_moderadas = [a for a in alertas if a['nivel'] == 'moderada']
        
        # Mostrar alertas críticas
        if alertas_criticas:
            st.error("🚨 **ALERTAS CRÍTICAS**")
            for alerta in alertas_criticas:
                with st.container():
                    st.error(f"{alerta['icono']} **{alerta['mensaje']}**")
                    st.error(f"🚨 **Acción inmediata:** {alerta['accion']}")
        
        # Mostrar alertas altas
        if alertas_altas:
            st.warning("⚠️ **ALERTAS ALTAS**")
            for alerta in alertas_altas:
                with st.container():
                    st.warning(f"{alerta['icono']} **{alerta['mensaje']}**")
                    st.warning(f"⚠️ **Acción recomendada:** {alerta['accion']}")
        
        # Mostrar alertas moderadas
        if alertas_moderadas:
            st.info("ℹ️ **ALERTAS MODERADAS**")
            for alerta in alertas_moderadas:
                with st.container():
                    st.info(f"{alerta['icono']} **{alerta['mensaje']}**")
                    st.info(f"ℹ️ **Acción recomendada:** {alerta['accion']}")
    
    def mostrar_panel_recomendaciones(self, recomendaciones):
        """Mostrar panel de recomendaciones"""
        if not recomendaciones:
            st.success("✅ **No se requieren acciones especiales** - Condiciones normales")
            return
        
        st.subheader("💡 Recomendaciones Agrícolas")
        
        for rec in recomendaciones:
            with st.expander(f"{rec['icono']} **{rec['titulo']}** - Nivel: {rec['nivel'].upper()}"):
                st.write(f"**Descripción:** {rec['descripcion']}")
                
                st.write("**Acciones recomendadas:**")
                for accion in rec['acciones']:
                    st.write(f"• {accion}")

def main():
    """Función principal para probar el sistema"""
    st.title("🚨 Sistema de Alertas Visuales Integrado METGO 3D")
    
    sistema = SistemaAlertasVisualesIntegrado()
    
    # Obtener datos actuales
    datos_actuales = sistema.obtener_datos_actuales()
    
    if datos_actuales.empty:
        st.warning("⚠️ No hay datos meteorológicos disponibles")
        return
    
    # Analizar alertas
    alertas = sistema.analizar_alertas_meteorologicas(datos_actuales)
    recomendaciones = sistema.generar_recomendaciones_agricolas(alertas)
    
    # Mostrar resumen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🚨 Alertas Críticas", len([a for a in alertas if a['nivel'] == 'critica']))
    
    with col2:
        st.metric("⚠️ Alertas Altas", len([a for a in alertas if a['nivel'] == 'alta']))
    
    with col3:
        st.metric("💡 Recomendaciones", len(recomendaciones))
    
    # Mostrar gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Alertas por Estación")
        fig_alertas = sistema.crear_grafico_alertas_tiempo_real(alertas)
        st.plotly_chart(fig_alertas, config=PLOTLY_CONFIG, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ Mapa de Calor de Alertas")
        fig_mapa = sistema.crear_mapa_calor_alertas(datos_actuales)
        st.plotly_chart(fig_mapa, config=PLOTLY_CONFIG, use_container_width=True)
    
    # Mostrar paneles de alertas y recomendaciones
    sistema.mostrar_panel_alertas(alertas)
    sistema.mostrar_panel_recomendaciones(recomendaciones)

if __name__ == "__main__":
    main()
