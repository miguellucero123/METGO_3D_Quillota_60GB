#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 DASHBOARD UNIFICADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Dashboard Integrado
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import warnings

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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

# Configuración
warnings.filterwarnings('ignore')

class DashboardUnificadoMETGO:
    """Dashboard unificado para el sistema METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/dashboard',
            'directorio_graficos': 'graficos/dashboard',
            'directorio_html': 'dashboard_html',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Inicializar Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            title='METGO 3D - Dashboard Unificado'
        )
        
        # Configurar layout
        self._configurar_layout()
        
        # Configurar callbacks
        self._configurar_callbacks()
        
        # Datos del dashboard
        self.datos_dashboard = {}
        self.metricas_tiempo_real = {}
        self.alertas_activas = []
        
        # Colores para Quillota
        self.colores_quillota = {
            'primario': '#2E8B57',
            'secundario': '#FFD700',
            'acento': '#FF6347',
            'neutro': '#708090',
            'fondo': '#F5F5DC',
            'exito': '#28a745',
            'advertencia': '#ffc107',
            'peligro': '#dc3545',
            'info': '#17a2b8'
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_layout(self):
        """Configurar layout del dashboard"""
        try:
            self.app.layout = dbc.Container([
                # Header
                dbc.Row([
                    dbc.Col([
                        html.H1("🌾 METGO 3D - Dashboard Unificado", 
                               className="text-center mb-4",
                               style={'color': self.colores_quillota['primario']}),
                        html.P("Sistema Meteorológico Agrícola Quillota - Monitoreo en Tiempo Real",
                               className="text-center text-muted mb-4")
                    ])
                ]),
                
                # Filtros y controles
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🎛️ Controles", className="card-title"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Período de Tiempo:"),
                                        dcc.Dropdown(
                                            id='filtro-periodo',
                                            options=[
                                                {'label': 'Últimas 24 horas', 'value': '24h'},
                                                {'label': 'Últimos 7 días', 'value': '7d'},
                                                {'label': 'Último mes', 'value': '1m'},
                                                {'label': 'Último año', 'value': '1y'}
                                            ],
                                            value='24h',
                                            clearable=False
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Variable Meteorológica:"),
                                        dcc.Dropdown(
                                            id='filtro-variable',
                                            options=[
                                                {'label': 'Temperatura', 'value': 'temperatura'},
                                                {'label': 'Precipitación', 'value': 'precipitacion'},
                                                {'label': 'Viento', 'value': 'viento_velocidad'},
                                                {'label': 'Humedad', 'value': 'humedad'},
                                                {'label': 'Presión', 'value': 'presion'},
                                                {'label': 'Radiación Solar', 'value': 'radiacion_solar'}
                                            ],
                                            value='temperatura',
                                            clearable=False
                                        )
                                    ], width=6)
                                ])
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Métricas principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🌡️ Temperatura Actual", className="card-title"),
                                html.H2(id="metric-temperatura", className="text-center"),
                                html.P("°C", className="text-center text-muted")
                            ])
                        ], color="primary", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("💧 Precipitación", className="card-title"),
                                html.H2(id="metric-precipitacion", className="text-center"),
                                html.P("mm", className="text-center text-muted")
                            ])
                        ], color="info", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("💨 Viento", className="card-title"),
                                html.H2(id="metric-viento", className="text-center"),
                                html.P("m/s", className="text-center text-muted")
                            ])
                        ], color="success", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("💧 Humedad", className="card-title"),
                                html.H2(id="metric-humedad", className="text-center"),
                                html.P("%", className="text-center text-muted")
                            ])
                        ], color="warning", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("📊 Presión", className="card-title"),
                                html.H2(id="metric-presion", className="text-center"),
                                html.P("hPa", className="text-center text-muted")
                            ])
                        ], color="secondary", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("☀️ Radiación", className="card-title"),
                                html.H2(id="metric-radiacion", className="text-center"),
                                html.P("W/m²", className="text-center text-muted")
                            ])
                        ], color="danger", outline=True)
                    ], width=2)
                ], className="mb-4"),
                
                # Gráficos principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("📈 Serie Temporal", className="card-title"),
                                dcc.Graph(id="grafico-serie-temporal")
                            ])
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🎯 Alertas Activas", className="card-title"),
                                html.Div(id="lista-alertas")
                            ])
                        ])
                    ], width=4)
                ], className="mb-4"),
                
                # Gráficos secundarios
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🌡️ Distribución de Temperaturas", className="card-title"),
                                dcc.Graph(id="grafico-distribucion")
                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🔗 Correlaciones", className="card-title"),
                                dcc.Graph(id="grafico-correlaciones")
                            ])
                        ])
                    ], width=6)
                ], className="mb-4"),
                
                # Gráficos 3D
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🌐 Visualización 3D", className="card-title"),
                                dcc.Graph(id="grafico-3d")
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Predicciones ML
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🤖 Predicciones ML", className="card-title"),
                                dcc.Graph(id="grafico-predicciones")
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Footer
                dbc.Row([
                    dbc.Col([
                        html.Hr(),
                        html.P("🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota | Versión 2.0",
                               className="text-center text-muted"),
                        html.P(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                               className="text-center text-muted")
                    ])
                ]),
                
                # Intervalo de actualización
                dcc.Interval(
                    id='intervalo-actualizacion',
                    interval=60*1000,  # 60 segundos
                    n_intervals=0
                )
                
            ], fluid=True)
            
        except Exception as e:
            print(f"Error configurando layout: {e}")
    
    def _configurar_callbacks(self):
        """Configurar callbacks del dashboard"""
        try:
            # Callback para métricas principales
            @self.app.callback(
                [Output('metric-temperatura', 'children'),
                 Output('metric-precipitacion', 'children'),
                 Output('metric-viento', 'children'),
                 Output('metric-humedad', 'children'),
                 Output('metric-presion', 'children'),
                 Output('metric-radiacion', 'children')],
                [Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_metricas(n):
                return self._obtener_metricas_tiempo_real()
            
            # Callback para gráfico de serie temporal
            @self.app.callback(
                Output('grafico-serie-temporal', 'figure'),
                [Input('filtro-periodo', 'value'),
                 Input('filtro-variable', 'value'),
                 Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_serie_temporal(periodo, variable, n):
                return self._crear_grafico_serie_temporal(periodo, variable)
            
            # Callback para lista de alertas
            @self.app.callback(
                Output('lista-alertas', 'children'),
                [Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_alertas(n):
                return self._crear_lista_alertas()
            
            # Callback para gráfico de distribución
            @self.app.callback(
                Output('grafico-distribucion', 'figure'),
                [Input('filtro-periodo', 'value'),
                 Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_distribucion(periodo, n):
                return self._crear_grafico_distribucion(periodo)
            
            # Callback para gráfico de correlaciones
            @self.app.callback(
                Output('grafico-correlaciones', 'figure'),
                [Input('filtro-periodo', 'value'),
                 Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_correlaciones(periodo, n):
                return self._crear_grafico_correlaciones(periodo)
            
            # Callback para gráfico 3D
            @self.app.callback(
                Output('grafico-3d', 'figure'),
                [Input('filtro-periodo', 'value'),
                 Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_3d(periodo, n):
                return self._crear_grafico_3d(periodo)
            
            # Callback para gráfico de predicciones
            @self.app.callback(
                Output('grafico-predicciones', 'figure'),
                [Input('filtro-variable', 'value'),
                 Input('intervalo-actualizacion', 'n_intervals')]
            )
            def actualizar_predicciones(variable, n):
                return self._crear_grafico_predicciones(variable)
            
        except Exception as e:
            print(f"Error configurando callbacks: {e}")
    
    def _obtener_metricas_tiempo_real(self) -> Tuple[str, str, str, str, str, str]:
        """Obtener métricas en tiempo real"""
        try:
            # Simular datos en tiempo real
            temperatura = 22.5 + np.random.normal(0, 2)
            precipitacion = max(0, np.random.exponential(0.5))
            viento = np.random.gamma(2, 2)
            humedad = 65 + np.random.normal(0, 5)
            presion = 1013 + np.random.normal(0, 10)
            radiacion = max(0, 800 * np.sin(np.pi * datetime.now().hour / 24) + np.random.normal(0, 50))
            
            return (
                f"{temperatura:.1f}",
                f"{precipitacion:.1f}",
                f"{viento:.1f}",
                f"{humedad:.1f}",
                f"{presion:.1f}",
                f"{radiacion:.1f}"
            )
            
        except Exception as e:
            print(f"Error obteniendo métricas: {e}")
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    
    def _crear_grafico_serie_temporal(self, periodo: str, variable: str) -> go.Figure:
        """Crear gráfico de serie temporal"""
        try:
            # Generar datos sintéticos
            if periodo == '24h':
                fechas = pd.date_range(end=datetime.now(), periods=24, freq='H')
            elif periodo == '7d':
                fechas = pd.date_range(end=datetime.now(), periods=7, freq='D')
            elif periodo == '1m':
                fechas = pd.date_range(end=datetime.now(), periods=30, freq='D')
            else:  # 1y
                fechas = pd.date_range(end=datetime.now(), periods=365, freq='D')
            
            # Generar datos según la variable
            if variable == 'temperatura':
                valores = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
            elif variable == 'precipitacion':
                valores = np.where(np.random.random(len(fechas)) > 0.9, np.random.exponential(0.5, len(fechas)), 0)
            elif variable == 'viento_velocidad':
                valores = np.random.gamma(2, 2, len(fechas))
            elif variable == 'humedad':
                valores = 60 + 20 * np.sin(2 * np.pi * fechas.hour / 24) + np.random.normal(0, 5, len(fechas))
                valores = np.clip(valores, 0, 100)
            elif variable == 'presion':
                valores = 1013 + np.random.normal(0, 10, len(fechas))
            elif variable == 'radiacion_solar':
                valores = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
            else:
                valores = np.random.uniform(0, 100, len(fechas))
            
            # Crear gráfico
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=fechas,
                y=valores,
                mode='lines+markers',
                name=variable.title(),
                line=dict(color=self.colores_quillota['primario'], width=2),
                marker=dict(size=4)
            ))
            
            fig.update_layout(
                title=f"Serie Temporal - {variable.title(, showlegend=False)}",
                xaxis_title="Tiempo",
                yaxis_title=variable.title(),
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de serie temporal: {e}")
            return go.Figure()
    
    def _crear_lista_alertas(self) -> List[html.Div]:
        """Crear lista de alertas activas"""
        try:
            # Simular alertas
            alertas = [
                {'tipo': 'heladas', 'nivel': 'critica', 'mensaje': 'Temperatura crítica: -2.1°C'},
                {'tipo': 'viento_fuerte', 'nivel': 'alta', 'mensaje': 'Viento fuerte: 25.3 m/s'},
                {'tipo': 'humedad_excesiva', 'nivel': 'media', 'mensaje': 'Humedad excesiva: 92.5%'}
            ]
            
            lista_alertas = []
            
            for alerta in alertas:
                color = self.colores_quillota['peligro'] if alerta['nivel'] == 'critica' else \
                       self.colores_quillota['advertencia'] if alerta['nivel'] == 'alta' else \
                       self.colores_quillota['info']
                
                lista_alertas.append(
                    dbc.Alert(
                        [
                            html.Strong(f"{alerta['tipo'].replace('_', ' ').title()}"),
                            html.Br(),
                            alerta['mensaje']
                        ],
                        color="danger" if alerta['nivel'] == 'critica' else 
                              "warning" if alerta['nivel'] == 'alta' else "info",
                        className="mb-2"
                    )
                )
            
            if not lista_alertas:
                lista_alertas.append(
                    dbc.Alert("✅ No hay alertas activas", color="success")
                )
            
            return lista_alertas
            
        except Exception as e:
            print(f"Error creando lista de alertas: {e}")
            return [html.Div("Error cargando alertas")]
    
    def _crear_grafico_distribucion(self, periodo: str) -> go.Figure:
        """Crear gráfico de distribución"""
        try:
            # Generar datos sintéticos
            temperaturas = np.random.normal(20, 5, 1000)
            
            # Crear histograma
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=temperaturas,
                nbinsx=30,
                name='Temperatura',
                marker_color=self.colores_quillota['primario'],
                opacity=0.7
            ))
            
            fig.update_layout(
                title="Distribución de Temperaturas",
                xaxis_title="Temperatura (°C, showlegend=False)",
                yaxis_title="Frecuencia",
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de distribución: {e}")
            return go.Figure()
    
    def _crear_grafico_correlaciones(self, periodo: str) -> go.Figure:
        """Crear gráfico de correlaciones"""
        try:
            # Generar datos sintéticos
            variables = ['Temperatura', 'Humedad', 'Viento', 'Presión', 'Radiación']
            correlaciones = np.random.uniform(-1, 1, (5, 5))
            np.fill_diagonal(correlaciones, 1)
            
            # Crear heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlaciones,
                x=variables,
                y=variables,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlaciones, 2),
                texttemplate="%{text}",
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title="Matriz de Correlaciones",
                template='plotly_white',
                height=400
            , showlegend=False)
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de correlaciones: {e}")
            return go.Figure()
    
    def _crear_grafico_3d(self, periodo: str) -> go.Figure:
        """Crear gráfico 3D"""
        try:
            # Generar datos sintéticos
            fechas = pd.date_range(end=datetime.now(), periods=24, freq='H')
            dias = fechas.dayofyear
            horas = fechas.hour
            temperaturas = 15 + 10 * np.sin(2 * np.pi * dias / 365) + np.random.normal(0, 3, len(fechas))
            
            # Crear gráfico 3D
            fig = go.Figure(data=[go.Scatter3d(
                x=dias,
                y=horas,
                z=temperaturas,
                mode='markers',
                marker=dict(
                    size=5,
                    color=temperaturas,
                    colorscale='RdYlBu_r',
                    colorbar=dict(title="Temperatura (°C)"),
                    opacity=0.8
                ),
                text=[f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M')}<br>Temperatura: {temp:.1f}°C" 
                      for fecha, temp in zip(fechas, temperaturas)],
                hovertemplate='%{text}<extra></extra>'
            )])
            
            fig.update_layout(
                title="Visualización 3D - Temperatura",
                scene=dict(
                    xaxis_title='Día del Año',
                    yaxis_title='Hora del Día',
                    zaxis_title='Temperatura (°C, showlegend=False)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                template='plotly_white',
                height=500
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico 3D: {e}")
            return go.Figure()
    
    def _crear_grafico_predicciones(self, variable: str) -> go.Figure:
        """Crear gráfico de predicciones ML"""
        try:
            # Generar datos históricos y predicciones
            fechas_historicas = pd.date_range(end=datetime.now(), periods=24, freq='H')
            fechas_predicciones = pd.date_range(start=datetime.now(), periods=24, freq='H')
            
            # Datos históricos
            if variable == 'temperatura':
                valores_historicos = 15 + 10 * np.sin(2 * np.pi * fechas_historicas.dayofyear / 365) + np.random.normal(0, 3, len(fechas_historicas))
                valores_predicciones = 15 + 10 * np.sin(2 * np.pi * fechas_predicciones.dayofyear / 365) + np.random.normal(0, 3, len(fechas_predicciones))
            else:
                valores_historicos = np.random.uniform(0, 100, len(fechas_historicas))
                valores_predicciones = np.random.uniform(0, 100, len(fechas_predicciones))
            
            # Crear gráfico
            fig = go.Figure()
            
            # Datos históricos
            fig.add_trace(go.Scatter(
                x=fechas_historicas,
                y=valores_historicos,
                mode='lines+markers',
                name='Datos Históricos',
                line=dict(color=self.colores_quillota['primario'], width=2)
            ))
            
            # Predicciones
            fig.add_trace(go.Scatter(
                x=fechas_predicciones,
                y=valores_predicciones,
                mode='lines+markers',
                name='Predicciones ML',
                line=dict(color=self.colores_quillota['acento'], width=2, dash='dash')
            ))
            
            # Línea vertical para separar histórico de predicciones
            fig.add_vline(
                x=datetime.now(),
                line_dash="dot",
                line_color="gray",
                annotation_text="Ahora"
            )
            
            fig.update_layout(
                title=f"Predicciones ML - {variable.title(, showlegend=False)}",
                xaxis_title="Tiempo",
                yaxis_title=variable.title(),
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de predicciones: {e}")
            return go.Figure()
    
    def generar_dashboard_html(self) -> str:
        """Generar dashboard como archivo HTML estático"""
        try:
            print("📊 Generando dashboard HTML estático...")
            
            # Crear datos de ejemplo
            fechas = pd.date_range(end=datetime.now(), periods=24, freq='H')
            temperaturas = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
            
            # Crear figura principal
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=fechas,
                y=temperaturas,
                mode='lines+markers',
                name='Temperatura',
                line=dict(color=self.colores_quillota['primario'], width=2)
            ))
            
            fig.update_layout(
                title="METGO 3D - Dashboard Unificado",
                xaxis_title="Tiempo",
                yaxis_title="Temperatura (°C, showlegend=False)",
                template='plotly_white',
                height=600
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/dashboard_unificado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(archivo_html)
            
            print(f"✅ Dashboard HTML generado: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error generando dashboard HTML: {e}")
            return ""
    
    def ejecutar_dashboard(self, puerto: int = 8050, debug: bool = False) -> bool:
        """Ejecutar dashboard en modo servidor"""
        try:
            print(f"🚀 Iniciando dashboard en puerto {puerto}...")
            print(f"📊 Accede a: http://localhost:{puerto}")
            
            self.app.run_server(
                host='0.0.0.0',
                port=puerto,
                debug=debug
            )
            
            return True
            
        except Exception as e:
            print(f"Error ejecutando dashboard: {e}")
            return False
    
    def generar_reporte_dashboard(self) -> str:
        """Generar reporte del dashboard"""
        try:
            print("📋 Generando reporte del dashboard...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Dashboard Unificado',
                'version': self.configuracion['version'],
                'resumen': {
                    'componentes': [
                        'Métricas en tiempo real',
                        'Gráfico de serie temporal',
                        'Lista de alertas activas',
                        'Gráfico de distribución',
                        'Matriz de correlaciones',
                        'Visualización 3D',
                        'Predicciones ML'
                    ],
                    'frecuencia_actualizacion': '60 segundos',
                    'colores_tema': self.colores_quillota
                },
                'configuracion': self.configuracion,
                'recomendaciones': [
                    "El dashboard se actualiza automáticamente cada 60 segundos",
                    "Utiliza los filtros para personalizar la visualización",
                    "Las alertas se muestran en tiempo real",
                    "Las predicciones ML se actualizan automáticamente",
                    "El dashboard es responsive y funciona en dispositivos móviles"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"dashboard_unificado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte del dashboard generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del dashboard unificado"""
    print("📊 DASHBOARD UNIFICADO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Dashboard Integrado")
    print("=" * 80)
    
    try:
        # Crear dashboard
        dashboard = DashboardUnificadoMETGO()
        
        # Generar dashboard HTML estático
        print(f"\n📊 Generando dashboard HTML estático...")
        archivo_html = dashboard.generar_dashboard_html()
        
        if archivo_html:
            print(f"✅ Dashboard HTML generado: {archivo_html}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = dashboard.generar_reporte_dashboard()
        
        if reporte:
            print(f"✅ Reporte generado: {reporte}")
        
        # Mostrar instrucciones
        print(f"\n🚀 Para ejecutar el dashboard interactivo:")
        print(f"   python {__file__} --servidor")
        print(f"   Luego accede a: http://localhost:8050")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en dashboard unificado: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--servidor':
            # Ejecutar dashboard en modo servidor
            dashboard = DashboardUnificadoMETGO()
            dashboard.ejecutar_dashboard()
        else:
            # Ejecutar función principal
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

