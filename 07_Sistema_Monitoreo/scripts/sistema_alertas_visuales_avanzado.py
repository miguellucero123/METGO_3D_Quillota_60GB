"""
SISTEMA DE ALERTAS VISUALES AVANZADO - METGO 3D QUILLOTA
Sistema de alertas visuales con indicadores, colores y animaciones
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging

class SistemaAlertasVisualesAvanzado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.umbrales_alertas = {
            'helada_critica': {'temp_max': 2.0, 'color': '#FF0000', 'icon': '🚨'},
            'helada_advertencia': {'temp_max': 5.0, 'color': '#FFA500', 'icon': '⚠️'},
            'viento_fuerte': {'velocidad': 50.0, 'color': '#FF8C00', 'icon': '💨'},
            'alta_humedad': {'humedad': 90.0, 'color': '#4169E1', 'icon': '💧'},
            'precipitacion_intensa': {'precipitacion': 10.0, 'color': '#0000FF', 'icon': '🌧️'},
            'presion_baja': {'presion': 1000.0, 'color': '#8A2BE2', 'icon': '📉'},
            'temperatura_alta': {'temp_max': 35.0, 'color': '#FF4500', 'icon': '🌡️'}
        }
        
        self.colores_estado = {
            'normal': '#00FF00',
            'advertencia': '#FFA500', 
            'critico': '#FF0000',
            'sin_datos': '#808080'
        }
    
    def evaluar_alertas(self, datos_meteorologicos: Dict) -> List[Dict]:
        """Evaluar alertas basadas en datos meteorológicos"""
        try:
            alertas = []
            
            # Evaluar helada crítica
            if 'temperatura' in datos_meteorologicos:
                temp = datos_meteorologicos['temperatura']
                if temp <= self.umbrales_alertas['helada_critica']['temp_max']:
                    alertas.append({
                        'tipo': 'helada_critica',
                        'mensaje': f'TEMPERATURA CRÍTICA: {temp}°C - RIESGO DE HELADA',
                        'severidad': 'critica',
                        'color': self.umbrales_alertas['helada_critica']['color'],
                        'icono': self.umbrales_alertas['helada_critica']['icon']
                    })
                elif temp <= self.umbrales_alertas['helada_advertencia']['temp_max']:
                    alertas.append({
                        'tipo': 'helada_advertencia',
                        'mensaje': f'TEMPERATURA BAJA: {temp}°C - RIESGO DE HELADA',
                        'severidad': 'advertencia',
                        'color': self.umbrales_alertas['helada_advertencia']['color'],
                        'icono': self.umbrales_alertas['helada_advertencia']['icon']
                    })
            
            # Evaluar viento fuerte
            if 'viento' in datos_meteorologicos:
                viento = datos_meteorologicos['viento']
                if viento >= self.umbrales_alertas['viento_fuerte']['velocidad']:
                    alertas.append({
                        'tipo': 'viento_fuerte',
                        'mensaje': f'VIENTO FUERTE: {viento} km/h',
                        'severidad': 'advertencia',
                        'color': self.umbrales_alertas['viento_fuerte']['color'],
                        'icono': self.umbrales_alertas['viento_fuerte']['icon']
                    })
            
            # Evaluar alta humedad
            if 'humedad' in datos_meteorologicos:
                humedad = datos_meteorologicos['humedad']
                if humedad >= self.umbrales_alertas['alta_humedad']['humedad']:
                    alertas.append({
                        'tipo': 'alta_humedad',
                        'mensaje': f'HUMEDAD ALTA: {humedad}%',
                        'severidad': 'advertencia',
                        'color': self.umbrales_alertas['alta_humedad']['color'],
                        'icono': self.umbrales_alertas['alta_humedad']['icon']
                    })
            
            # Evaluar precipitación intensa
            if 'precipitacion' in datos_meteorologicos:
                precip = datos_meteorologicos['precipitacion']
                if precip >= self.umbrales_alertas['precipitacion_intensa']['precipitacion']:
                    alertas.append({
                        'tipo': 'precipitacion_intensa',
                        'mensaje': f'PRECIPITACIÓN INTENSA: {precip} mm',
                        'severidad': 'advertencia',
                        'color': self.umbrales_alertas['precipitacion_intensa']['color'],
                        'icono': self.umbrales_alertas['precipitacion_intensa']['icon']
                    })
            
            # Evaluar temperatura alta
            if 'temperatura' in datos_meteorologicos:
                temp = datos_meteorologicos['temperatura']
                if temp >= self.umbrales_alertas['temperatura_alta']['temp_max']:
                    alertas.append({
                        'tipo': 'temperatura_alta',
                        'mensaje': f'TEMPERATURA ALTA: {temp}°C',
                        'severidad': 'advertencia',
                        'color': self.umbrales_alertas['temperatura_alta']['color'],
                        'icono': self.umbrales_alertas['temperatura_alta']['icon']
                    })
            
            return alertas
            
        except Exception as e:
            self.logger.error(f"Error evaluando alertas: {e}")
            return []
    
    def generar_indicador_estado(self, valor: float, umbral_normal: float, 
                                umbral_advertencia: float, umbral_critico: float,
                                unidad: str = "") -> Dict:
        """Generar indicador de estado con colores"""
        try:
            if valor is None or np.isnan(valor):
                return {
                    'estado': 'sin_datos',
                    'color': self.colores_estado['sin_datos'],
                    'icono': '❓',
                    'texto': 'Sin datos',
                    'severidad': 0
                }
            
            if valor <= umbral_critico:
                estado = 'critico'
                color = self.colores_estado['critico']
                icono = '🚨'
                texto = 'CRÍTICO'
                severidad = 3
            elif valor <= umbral_advertencia:
                estado = 'advertencia'
                color = self.colores_estado['advertencia']
                icono = '⚠️'
                texto = 'ADVERTENCIA'
                severidad = 2
            else:
                estado = 'normal'
                color = self.colores_estado['normal']
                icono = '✅'
                texto = 'NORMAL'
                severidad = 1
            
            return {
                'estado': estado,
                'color': color,
                'icono': icono,
                'texto': texto,
                'severidad': severidad,
                'valor': valor,
                'unidad': unidad
            }
            
        except Exception as e:
            self.logger.error(f"Error generando indicador: {e}")
            return {
                'estado': 'sin_datos',
                'color': self.colores_estado['sin_datos'],
                'icono': '❓',
                'texto': 'Error',
                'severidad': 0
            }
    
    def crear_tablero_alertas(self, datos_estaciones: Dict) -> go.Figure:
        """Crear tablero visual de alertas"""
        try:
            # Crear subplots
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=list(datos_estaciones.keys()),
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            estaciones = list(datos_estaciones.keys())
            
            for i, estacion in enumerate(estaciones):
                datos = datos_estaciones[estacion]
                
                # Calcular nivel de alerta general
                alertas = self._calcular_alertas_estacion(datos)
                nivel_alerta = max([alerta['severidad'] for alerta in alertas.values()])
                
                # Determinar color y texto
                if nivel_alerta >= 3:
                    color = self.colores_estado['critico']
                    texto = 'CRÍTICO'
                elif nivel_alerta >= 2:
                    color = self.colores_estado['advertencia']
                    texto = 'ADVERTENCIA'
                else:
                    color = self.colores_estado['normal']
                    texto = 'NORMAL'
                
                # Crear indicador circular
                fig.add_trace(go.Indicator(
                    mode="gauge+number+delta",
                    value=nivel_alerta,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': estacion.replace('_', ' ')},
                    gauge={
                        'axis': {'range': [None, 3]},
                        'bar': {'color': color},
                        'steps': [
                            {'range': [0, 1], 'color': self.colores_estado['normal']},
                            {'range': [1, 2], 'color': self.colores_estado['advertencia']},
                            {'range': [2, 3], 'color': self.colores_estado['critico']}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 2
                        }
                    }
                ), row=(i//3)+1, col=(i%3)+1)
            
            fig.update_layout(
                height=600,
                title_text="🚨 Tablero de Alertas Meteorológicas - Valle de Quillota",
                title_x=0.5,
                font=dict(size=12)
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creando tablero de alertas: {e}")
            return go.Figure()
    
    def _calcular_alertas_estacion(self, datos: Dict) -> Dict:
        """Calcular alertas para una estación específica"""
        alertas = {}
        
        try:
            # Alerta de helada crítica
            temp = datos.get('temperatura_actual', datos.get('temperatura', None))
            if temp is not None:
                if temp <= self.umbrales_alertas['helada_critica']['temp_max']:
                    alertas['helada_critica'] = {
                        'tipo': 'helada_critica',
                        'severidad': 3,
                        'valor': temp,
                        'umbral': self.umbrales_alertas['helada_critica']['temp_max']
                    }
                elif temp <= self.umbrales_alertas['helada_advertencia']['temp_max']:
                    alertas['helada_advertencia'] = {
                        'tipo': 'helada_advertencia',
                        'severidad': 2,
                        'valor': temp,
                        'umbral': self.umbrales_alertas['helada_advertencia']['temp_max']
                    }
            
            # Alerta de viento fuerte
            viento = datos.get('velocidad_viento', datos.get('viento', None))
            if viento is not None and viento >= self.umbrales_alertas['viento_fuerte']['velocidad']:
                alertas['viento_fuerte'] = {
                    'tipo': 'viento_fuerte',
                    'severidad': 2,
                    'valor': viento,
                    'umbral': self.umbrales_alertas['viento_fuerte']['velocidad']
                }
            
            # Alerta de alta humedad
            humedad = datos.get('humedad_relativa', datos.get('humedad', None))
            if humedad is not None and humedad >= self.umbrales_alertas['alta_humedad']['humedad']:
                alertas['alta_humedad'] = {
                    'tipo': 'alta_humedad',
                    'severidad': 1,
                    'valor': humedad,
                    'umbral': self.umbrales_alertas['alta_humedad']['humedad']
                }
            
            # Alerta de precipitación intensa
            precip = datos.get('precipitacion', datos.get('lluvia', None))
            if precip is not None and precip >= self.umbrales_alertas['precipitacion_intensa']['precipitacion']:
                alertas['precipitacion_intensa'] = {
                    'tipo': 'precipitacion_intensa',
                    'severidad': 2,
                    'valor': precip,
                    'umbral': self.umbrales_alertas['precipitacion_intensa']['precipitacion']
                }
            
            # Alerta de presión baja
            presion = datos.get('presion_atmosferica', datos.get('presion', None))
            if presion is not None and presion <= self.umbrales_alertas['presion_baja']['presion']:
                alertas['presion_baja'] = {
                    'tipo': 'presion_baja',
                    'severidad': 1,
                    'valor': presion,
                    'umbral': self.umbrales_alertas['presion_baja']['presion']
                }
            
            # Alerta de temperatura alta
            if temp is not None and temp >= self.umbrales_alertas['temperatura_alta']['temp_max']:
                alertas['temperatura_alta'] = {
                    'tipo': 'temperatura_alta',
                    'severidad': 2,
                    'valor': temp,
                    'umbral': self.umbrales_alertas['temperatura_alta']['temp_max']
                }
        
        except Exception as e:
            self.logger.error(f"Error calculando alertas: {e}")
        
        return alertas
    
    def crear_grafico_alertas_temporales(self, datos_historicos: List[Dict]) -> go.Figure:
        """Crear gráfico de alertas a lo largo del tiempo"""
        try:
            if not datos_historicos:
                return go.Figure()
            
            df = pd.DataFrame(datos_historicos)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Crear subplots
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=['Temperatura', 'Humedad', 'Viento'],
                vertical_spacing=0.1
            )
            
            # Gráfico de temperatura con zonas de alerta
            if 'temperatura' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['fecha'],
                    y=df['temperatura'],
                    mode='lines+markers',
                    name='Temperatura',
                    line=dict(color='blue', width=2),
                    marker=dict(size=6)
                ), row=1, col=1)
                
                # Agregar zonas de alerta
                fig.add_hrect(
                    y0=0, y1=self.umbrales_alertas['helada_advertencia']['temp_max'],
                    fillcolor="red", opacity=0.2, line_width=0,
                    annotation_text="Zona Crítica", annotation_position="top left",
                    row=1, col=1
                )
                
                fig.add_hrect(
                    y0=self.umbrales_alertas['helada_advertencia']['temp_max'],
                    y1=self.umbrales_alertas['helada_advertencia']['temp_max'] + 3,
                    fillcolor="orange", opacity=0.2, line_width=0,
                    annotation_text="Zona Advertencia", annotation_position="top left",
                    row=1, col=1
                )
            
            # Gráfico de humedad
            if 'humedad' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['fecha'],
                    y=df['humedad'],
                    mode='lines+markers',
                    name='Humedad',
                    line=dict(color='green', width=2),
                    marker=dict(size=6)
                ), row=2, col=1)
            
            # Gráfico de viento
            if 'viento' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['fecha'],
                    y=df['viento'],
                    mode='lines+markers',
                    name='Viento',
                    line=dict(color='purple', width=2),
                    marker=dict(size=6)
                ), row=3, col=1)
            
            fig.update_layout(
                height=800,
                title_text="📊 Evolución Temporal de Variables Meteorológicas",
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creando gráfico temporal: {e}")
            return go.Figure()
    
    def crear_mapa_alertas(self, datos_estaciones: Dict) -> go.Figure:
        """Crear mapa de alertas geográfico"""
        try:
            # Coordenadas de las estaciones
            coordenadas = {
                "Quillota_Centro": {"lat": -32.8833, "lon": -71.2667},
                "La_Cruz": {"lat": -32.8167, "lon": -71.2167},
                "Nogales": {"lat": -32.7500, "lon": -71.2167},
                "San_Isidro": {"lat": -32.9167, "lon": -71.2333},
                "Pocochay": {"lat": -32.8500, "lon": -71.3000},
                "Valle_Hermoso": {"lat": -32.9333, "lon": -71.2833}
            }
            
            # Preparar datos para el mapa
            lats, lons, texts, colors, sizes = [], [], [], [], []
            
            for estacion, datos in datos_estaciones.items():
                if estacion in coordenadas:
                    coord = coordenadas[estacion]
                    
                    # Calcular nivel de alerta
                    alertas = self._calcular_alertas_estacion(datos)
                    nivel_alerta = max([alerta['severidad'] for alerta in alertas.values()]) if alertas else 0
                    
                    lats.append(coord['lat'])
                    lons.append(coord['lon'])
                    
                    # Crear texto informativo
                    temp = datos.get('temperatura_actual', datos.get('temperatura', 'N/A'))
                    humedad = datos.get('humedad_relativa', datos.get('humedad', 'N/A'))
                    viento = datos.get('velocidad_viento', datos.get('viento', 'N/A'))
                    
                    texto = f"""
                    <b>{estacion.replace('_', ' ')}</b><br>
                    Temperatura: {temp}°C<br>
                    Humedad: {humedad}%<br>
                    Viento: {viento} km/h<br>
                    Nivel Alerta: {nivel_alerta}
                    """
                    texts.append(texto)
                    
                    # Asignar color y tamaño según nivel de alerta
                    if nivel_alerta >= 3:
                        colors.append('red')
                        sizes.append(20)
                    elif nivel_alerta >= 2:
                        colors.append('orange')
                        sizes.append(15)
                    else:
                        colors.append('green')
                        sizes.append(10)
            
            # Crear mapa
            fig = go.Figure(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=colors,
                    opacity=0.8
                ),
                text=texts,
                hovertemplate='%{text}<extra></extra>'
            ))
            
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=-32.8833, lon=-71.2667),
                    zoom=10
                ),
                height=500,
                title_text="🗺️ Mapa de Alertas - Valle de Quillota",
                title_x=0.5
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creando mapa de alertas: {e}")
            return go.Figure()
    
    def crear_indicadores_kpi(self, datos_estaciones: Dict) -> List[go.Figure]:
        """Crear indicadores KPI visuales"""
        try:
            indicadores = []
            
            # Calcular KPIs generales
            total_estaciones = len(datos_estaciones)
            alertas_criticas = 0
            alertas_advertencia = 0
            estaciones_normales = 0
            
            for estacion, datos in datos_estaciones.items():
                alertas = self._calcular_alertas_estacion(datos)
                nivel_alerta = max([alerta['severidad'] for alerta in alertas.values()]) if alertas else 0
                
                if nivel_alerta >= 3:
                    alertas_criticas += 1
                elif nivel_alerta >= 2:
                    alertas_advertencia += 1
                else:
                    estaciones_normales += 1
            
            # KPI 1: Estado General
            fig1 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=estaciones_normales,
                title={'text': "Estaciones Normales"},
                gauge={
                    'axis': {'range': [None, total_estaciones]},
                    'bar': {'color': self.colores_estado['normal']},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': total_estaciones * 0.8
                    }
                }
            ))
            fig1.update_layout(height=300)
            indicadores.append(fig1)
            
            # KPI 2: Alertas Críticas
            fig2 = go.Figure(go.Indicator(
                mode="number+gauge",
                value=alertas_criticas,
                title={'text': "Alertas Críticas"},
                gauge={
                    'axis': {'range': [None, total_estaciones]},
                    'bar': {'color': self.colores_estado['critico']},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 1
                    }
                }
            ))
            fig2.update_layout(height=300)
            indicadores.append(fig2)
            
            # KPI 3: Alertas de Advertencia
            fig3 = go.Figure(go.Indicator(
                mode="number+gauge",
                value=alertas_advertencia,
                title={'text': "Alertas Advertencia"},
                gauge={
                    'axis': {'range': [None, total_estaciones]},
                    'bar': {'color': self.colores_estado['advertencia']},
                    'threshold': {
                        'line': {'color': "orange", 'width': 4},
                        'thickness': 0.75,
                        'value': total_estaciones * 0.5
                    }
                }
            ))
            fig3.update_layout(height=300)
            indicadores.append(fig3)
            
            return indicadores
            
        except Exception as e:
            self.logger.error(f"Error creando indicadores KPI: {e}")
            return []
    
    def generar_reporte_alertas_visual(self, datos_estaciones: Dict) -> Dict:
        """Generar reporte completo de alertas visuales"""
        try:
            reporte = {
                'fecha_generacion': datetime.now().isoformat(),
                'total_estaciones': len(datos_estaciones),
                'resumen_alertas': {},
                'estaciones_criticas': [],
                'estaciones_advertencia': [],
                'estaciones_normales': []
            }
            
            # Analizar cada estación
            for estacion, datos in datos_estaciones.items():
                alertas = self._calcular_alertas_estacion(datos)
                nivel_alerta = max([alerta['severidad'] for alerta in alertas.values()]) if alertas else 0
                
                estacion_info = {
                    'nombre': estacion,
                    'nivel_alerta': nivel_alerta,
                    'alertas': list(alertas.keys()),
                    'datos': datos
                }
                
                if nivel_alerta >= 3:
                    reporte['estaciones_criticas'].append(estacion_info)
                elif nivel_alerta >= 2:
                    reporte['estaciones_advertencia'].append(estacion_info)
                else:
                    reporte['estaciones_normales'].append(estacion_info)
            
            # Resumen general
            reporte['resumen_alertas'] = {
                'criticas': len(reporte['estaciones_criticas']),
                'advertencia': len(reporte['estaciones_advertencia']),
                'normales': len(reporte['estaciones_normales'])
            }
            
            return reporte
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}

def main():
    """Función principal para pruebas"""
    logging.basicConfig(level=logging.INFO)
    
    sistema = SistemaAlertasVisualesAvanzado()
    
    # Datos de prueba
    datos_prueba = {
        "Quillota_Centro": {
            "temperatura_actual": 1.5,  # Crítico
            "humedad_relativa": 85,
            "velocidad_viento": 25,
            "precipitacion": 0.5
        },
        "La_Cruz": {
            "temperatura_actual": 8.5,  # Normal
            "humedad_relativa": 65,
            "velocidad_viento": 15,
            "precipitacion": 2.0
        }
    }
    
    print("Probando sistema de alertas visuales...")
    
    # Generar reporte
    reporte = sistema.generar_reporte_alertas_visual(datos_prueba)
    print(f"Reporte generado: {reporte['resumen_alertas']}")

if __name__ == "__main__":
    main()
