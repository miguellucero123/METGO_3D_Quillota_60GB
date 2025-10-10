#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 DASHBOARD DE MONITOREO METGO 3D
Sistema Meteorológico Agrícola Quillota - Dashboard de Monitoreo en Tiempo Real
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
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
import threading
import queue

# Configuración
warnings.filterwarnings('ignore')

class DashboardMonitoreoMETGO:
    """Dashboard de monitoreo en tiempo real para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/monitoreo',
            'directorio_graficos': 'graficos/monitoreo',
            'directorio_html': 'dashboard_html/monitoreo',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Inicializar Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            title='METGO 3D - Dashboard de Monitoreo'
        )
        
        # Configurar layout
        self._configurar_layout()
        
        # Configurar callbacks
        self._configurar_callbacks()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Colores para el dashboard
        self.colores = {
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
        
        # Cache de datos
        self.cache_datos = {}
        self.ultima_actualizacion = datetime.now()
        
        # Hilo de actualización
        self.hilo_actualizacion = None
        self.detener_hilo = threading.Event()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar conexión a la base de datos"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/monitoreo_avanzado.db"
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")
    
    def _configurar_layout(self):
        """Configurar layout del dashboard"""
        try:
            self.app.layout = dbc.Container([
                # Header
                dbc.Row([
                    dbc.Col([
                        html.H1("📊 METGO 3D - Dashboard de Monitoreo", 
                               className="text-center mb-4",
                               style={'color': self.colores['primario']}),
                        html.P("Sistema Meteorológico Agrícola Quillota - Monitoreo en Tiempo Real",
                               className="text-center text-muted mb-4")
                    ])
                ]),
                
                # Métricas principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🖥️ CPU", className="card-title"),
                                html.H2(id="metric-cpu", className="text-center"),
                                html.P("%", className="text-center text-muted")
                            ])
                        ], color="primary", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("💾 Memoria", className="card-title"),
                                html.H2(id="metric-memoria", className="text-center"),
                                html.P("%", className="text-center text-muted")
                            ])
                        ], color="info", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("💿 Disco", className="card-title"),
                                html.H2(id="metric-disco", className="text-center"),
                                html.P("%", className="text-center text-muted")
                            ])
                        ], color="success", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🌐 Red", className="card-title"),
                                html.H2(id="metric-red", className="text-center"),
                                html.P("MB/s", className="text-center text-muted")
                            ])
                        ], color="warning", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("⚡ Procesos", className="card-title"),
                                html.H2(id="metric-procesos", className="text-center"),
                                html.P("activos", className="text-center text-muted")
                            ])
                        ], color="secondary", outline=True)
                    ], width=2),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🐍 Python", className="card-title"),
                                html.H2(id="metric-python", className="text-center"),
                                html.P("MB", className="text-center text-muted")
                            ])
                        ], color="danger", outline=True)
                    ], width=2)
                ], className="mb-4"),
                
                # Gráficos principales
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("📈 Métricas del Sistema", className="card-title"),
                                dcc.Graph(id="grafico-metricas-sistema")
                            ])
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🚨 Alertas Activas", className="card-title"),
                                html.Div(id="lista-alertas-monitoreo")
                            ])
                        ])
                    ], width=4)
                ], className="mb-4"),
                
                # Gráficos secundarios
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🔧 Estado de Servicios", className="card-title"),
                                dcc.Graph(id="grafico-servicios")
                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("📊 Distribución de Métricas", className="card-title"),
                                dcc.Graph(id="grafico-distribucion-metricas")
                            ])
                        ])
                    ], width=6)
                ], className="mb-4"),
                
                # Gráficos de tendencias
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("📈 Tendencias de CPU y Memoria", className="card-title"),
                                dcc.Graph(id="grafico-tendencias")
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Tabla de servicios
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("🔧 Detalles de Servicios", className="card-title"),
                                html.Div(id="tabla-servicios")
                            ])
                        ])
                    ], width=12)
                ], className="mb-4"),
                
                # Footer
                dbc.Row([
                    dbc.Col([
                        html.Hr(),
                        html.P("📊 METGO 3D - Dashboard de Monitoreo | Versión 2.0",
                               className="text-center text-muted"),
                        html.P(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                               className="text-center text-muted")
                    ])
                ]),
                
                # Intervalo de actualización
                dcc.Interval(
                    id='intervalo-actualizacion-monitoreo',
                    interval=30*1000,  # 30 segundos
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
                [Output('metric-cpu', 'children'),
                 Output('metric-memoria', 'children'),
                 Output('metric-disco', 'children'),
                 Output('metric-red', 'children'),
                 Output('metric-procesos', 'children'),
                 Output('metric-python', 'children')],
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_metricas_principales(n):
                return self._obtener_metricas_principales()
            
            # Callback para gráfico de métricas del sistema
            @self.app.callback(
                Output('grafico-metricas-sistema', 'figure'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_grafico_metricas_sistema(n):
                return self._crear_grafico_metricas_sistema()
            
            # Callback para lista de alertas
            @self.app.callback(
                Output('lista-alertas-monitoreo', 'children'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_alertas_monitoreo(n):
                return self._crear_lista_alertas_monitoreo()
            
            # Callback para gráfico de servicios
            @self.app.callback(
                Output('grafico-servicios', 'figure'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_grafico_servicios(n):
                return self._crear_grafico_servicios()
            
            # Callback para gráfico de distribución
            @self.app.callback(
                Output('grafico-distribucion-metricas', 'figure'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_grafico_distribucion(n):
                return self._crear_grafico_distribucion_metricas()
            
            # Callback para gráfico de tendencias
            @self.app.callback(
                Output('grafico-tendencias', 'figure'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_grafico_tendencias(n):
                return self._crear_grafico_tendencias()
            
            # Callback para tabla de servicios
            @self.app.callback(
                Output('tabla-servicios', 'children'),
                [Input('intervalo-actualizacion-monitoreo', 'n_intervals')]
            )
            def actualizar_tabla_servicios(n):
                return self._crear_tabla_servicios()
            
        except Exception as e:
            print(f"Error configurando callbacks: {e}")
    
    def _obtener_metricas_principales(self) -> Tuple[str, str, str, str, str, str]:
        """Obtener métricas principales del sistema"""
        try:
            # Obtener métricas de la base de datos
            self.cursor_bd.execute('''
                SELECT nombre, valor, unidad FROM metricas 
                WHERE timestamp > datetime('now', '-1 minute')
                ORDER BY timestamp DESC
            ''')
            
            metricas_db = self.cursor_bd.fetchall()
            metricas_dict = {nombre: (valor, unidad) for nombre, valor, unidad in metricas_db}
            
            # CPU
            cpu = metricas_dict.get('cpu_uso', (0, '%'))[0]
            cpu_str = f"{cpu:.1f}" if cpu else "0.0"
            
            # Memoria
            memoria = metricas_dict.get('memoria_uso', (0, '%'))[0]
            memoria_str = f"{memoria:.1f}" if memoria else "0.0"
            
            # Disco
            disco = metricas_dict.get('disco_uso', (0, '%'))[0]
            disco_str = f"{disco:.1f}" if disco else "0.0"
            
            # Red (simplificado)
            red = 0.0  # Se calcularía basado en métricas de red
            red_str = f"{red:.1f}"
            
            # Procesos
            procesos = metricas_dict.get('procesos_activos', (0, 'count'))[0]
            procesos_str = f"{int(procesos)}" if procesos else "0"
            
            # Python
            python = metricas_dict.get('python_memoria', (0, 'bytes'))[0]
            python_mb = python / (1024 * 1024) if python else 0
            python_str = f"{python_mb:.1f}" if python_mb else "0.0"
            
            return cpu_str, memoria_str, disco_str, red_str, procesos_str, python_str
            
        except Exception as e:
            print(f"Error obteniendo métricas principales: {e}")
            return "0.0", "0.0", "0.0", "0.0", "0", "0.0"
    
    def _crear_grafico_metricas_sistema(self) -> go.Figure:
        """Crear gráfico de métricas del sistema"""
        try:
            # Obtener datos de la base de datos
            self.cursor_bd.execute('''
                SELECT nombre, valor, timestamp FROM metricas 
                WHERE timestamp > datetime('now', '-1 hour')
                AND nombre IN ('cpu_uso', 'memoria_uso', 'disco_uso')
                ORDER BY timestamp ASC
            ''')
            
            datos = self.cursor_bd.fetchall()
            
            if not datos:
                # Datos sintéticos si no hay datos reales
                fechas = pd.date_range(end=datetime.now(), periods=60, freq='1min')
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=fechas,
                    y=np.random.uniform(20, 80, len(fechas)),
                    mode='lines',
                    name='CPU',
                    line=dict(color=self.colores['primario'])
                ))
                
                fig.add_trace(go.Scatter(
                    x=fechas,
                    y=np.random.uniform(30, 70, len(fechas)),
                    mode='lines',
                    name='Memoria',
                    line=dict(color=self.colores['secundario'])
                ))
                
                fig.add_trace(go.Scatter(
                    x=fechas,
                    y=np.random.uniform(40, 90, len(fechas)),
                    mode='lines',
                    name='Disco',
                    line=dict(color=self.colores['acento'])
                ))
            else:
                # Procesar datos reales
                df = pd.DataFrame(datos, columns=['nombre', 'valor', 'timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = go.Figure()
                
                for nombre in ['cpu_uso', 'memoria_uso', 'disco_uso']:
                    datos_metricas = df[df['nombre'] == nombre]
                    if not datos_metricas.empty:
                        color = self.colores['primario'] if nombre == 'cpu_uso' else \
                               self.colores['secundario'] if nombre == 'memoria_uso' else \
                               self.colores['acento']
                        
                        fig.add_trace(go.Scatter(
                            x=datos_metricas['timestamp'],
                            y=datos_metricas['valor'],
                            mode='lines',
                            name=nombre.replace('_', ' ').title(),
                            line=dict(color=color)
                        ))
            
            fig.update_layout(
                title="Métricas del Sistema (Última Hora, showlegend=False)",
                xaxis_title="Tiempo",
                yaxis_title="Porcentaje (%)",
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de métricas: {e}")
            return go.Figure()
    
    def _crear_lista_alertas_monitoreo(self) -> List[html.Div]:
        """Crear lista de alertas de monitoreo"""
        try:
            # Obtener alertas activas
            self.cursor_bd.execute('''
                SELECT nivel, mensaje, timestamp, valor, umbral FROM alertas 
                WHERE resuelta = FALSE 
                AND timestamp > datetime('now', '-1 hour')
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            
            alertas_db = self.cursor_bd.fetchall()
            
            lista_alertas = []
            
            for nivel, mensaje, timestamp, valor, umbral in alertas_db:
                color = self.colores['peligro'] if nivel == 'critical' else \
                       self.colores['advertencia'] if nivel == 'warning' else \
                       self.colores['info']
                
                lista_alertas.append(
                    dbc.Alert(
                        [
                            html.Strong(f"{nivel.upper()}"),
                            html.Br(),
                            mensaje,
                            html.Br(),
                            html.Small(f"Valor: {valor:.2f} | Umbral: {umbral:.2f}"),
                            html.Br(),
                            html.Small(f"Tiempo: {timestamp}")
                        ],
                        color="danger" if nivel == 'critical' else 
                              "warning" if nivel == 'warning' else "info",
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
    
    def _crear_grafico_servicios(self) -> go.Figure:
        """Crear gráfico de estado de servicios"""
        try:
            # Obtener datos de servicios
            self.cursor_bd.execute('''
                SELECT nombre, estado, COUNT(*) as count FROM servicios 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY nombre, estado
                ORDER BY nombre
            ''')
            
            datos = self.cursor_bd.fetchall()
            
            if not datos:
                # Datos sintéticos
                servicios = ['API Principal', 'API Meteorología', 'API Agrícola', 'Dashboard', 'PostgreSQL', 'Redis']
                estados = ['healthy', 'degraded', 'down']
                
                fig = go.Figure()
                
                for estado in estados:
                    valores = np.random.randint(0, 10, len(servicios))
                    color = self.colores['exito'] if estado == 'healthy' else \
                           self.colores['advertencia'] if estado == 'degraded' else \
                           self.colores['peligro']
                    
                    fig.add_trace(go.Bar(
                        x=servicios,
                        y=valores,
                        name=estado.title(),
                        marker_color=color
                    ))
            else:
                # Procesar datos reales
                df = pd.DataFrame(datos, columns=['nombre', 'estado', 'count'])
                
                fig = go.Figure()
                
                for estado in df['estado'].unique():
                    datos_estado = df[df['estado'] == estado]
                    color = self.colores['exito'] if estado == 'healthy' else \
                           self.colores['advertencia'] if estado == 'degraded' else \
                           self.colores['peligro']
                    
                    fig.add_trace(go.Bar(
                        x=datos_estado['nombre'],
                        y=datos_estado['count'],
                        name=estado.title(),
                        marker_color=color
                    ))
            
            fig.update_layout(
                title="Estado de Servicios (Última Hora, showlegend=False)",
                xaxis_title="Servicios",
                yaxis_title="Cantidad",
                barmode='stack',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de servicios: {e}")
            return go.Figure()
    
    def _crear_grafico_distribucion_metricas(self) -> go.Figure:
        """Crear gráfico de distribución de métricas"""
        try:
            # Obtener datos de métricas
            self.cursor_bd.execute('''
                SELECT nombre, valor FROM metricas 
                WHERE timestamp > datetime('now', '-1 hour')
                AND nombre IN ('cpu_uso', 'memoria_uso', 'disco_uso')
            ''')
            
            datos = self.cursor_bd.fetchall()
            
            if not datos:
                # Datos sintéticos
                fig = go.Figure()
                
                for nombre, color in [('cpu_uso', self.colores['primario']), 
                                    ('memoria_uso', self.colores['secundario']), 
                                    ('disco_uso', self.colores['acento'])]:
                    valores = np.random.normal(50, 15, 100)
                    valores = np.clip(valores, 0, 100)
                    
                    fig.add_trace(go.Histogram(
                        x=valores,
                        name=nombre.replace('_', ' ').title(),
                        marker_color=color,
                        opacity=0.7
                    ))
            else:
                # Procesar datos reales
                df = pd.DataFrame(datos, columns=['nombre', 'valor'])
                
                fig = go.Figure()
                
                for nombre in df['nombre'].unique():
                    datos_metricas = df[df['nombre'] == nombre]['valor']
                    color = self.colores['primario'] if nombre == 'cpu_uso' else \
                           self.colores['secundario'] if nombre == 'memoria_uso' else \
                           self.colores['acento']
                    
                    fig.add_trace(go.Histogram(
                        x=datos_metricas,
                        name=nombre.replace('_', ' ').title(),
                        marker_color=color,
                        opacity=0.7
                    ))
            
            fig.update_layout(
                title="Distribución de Métricas (Última Hora, showlegend=False)",
                xaxis_title="Valor",
                yaxis_title="Frecuencia",
                barmode='overlay',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de distribución: {e}")
            return go.Figure()
    
    def _crear_grafico_tendencias(self) -> go.Figure:
        """Crear gráfico de tendencias"""
        try:
            # Obtener datos de tendencias
            self.cursor_bd.execute('''
                SELECT nombre, valor, timestamp FROM metricas 
                WHERE timestamp > datetime('now', '-6 hours')
                AND nombre IN ('cpu_uso', 'memoria_uso')
                ORDER BY timestamp ASC
            ''')
            
            datos = self.cursor_bd.fetchall()
            
            if not datos:
                # Datos sintéticos
                fechas = pd.date_range(end=datetime.now(), periods=360, freq='1min')
                fig = go.Figure()
                
                # CPU con tendencia
                cpu_tendencia = 50 + 20 * np.sin(2 * np.pi * np.arange(len(fechas)) / 60) + np.random.normal(0, 5, len(fechas))
                cpu_tendencia = np.clip(cpu_tendencia, 0, 100)
                
                fig.add_trace(go.Scatter(
                    x=fechas,
                    y=cpu_tendencia,
                    mode='lines',
                    name='CPU',
                    line=dict(color=self.colores['primario'], width=2)
                ))
                
                # Memoria con tendencia
                memoria_tendencia = 60 + 15 * np.sin(2 * np.pi * np.arange(len(fechas)) / 120) + np.random.normal(0, 3, len(fechas))
                memoria_tendencia = np.clip(memoria_tendencia, 0, 100)
                
                fig.add_trace(go.Scatter(
                    x=fechas,
                    y=memoria_tendencia,
                    mode='lines',
                    name='Memoria',
                    line=dict(color=self.colores['secundario'], width=2)
                ))
            else:
                # Procesar datos reales
                df = pd.DataFrame(datos, columns=['nombre', 'valor', 'timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = go.Figure()
                
                for nombre in ['cpu_uso', 'memoria_uso']:
                    datos_metricas = df[df['nombre'] == nombre]
                    if not datos_metricas.empty:
                        color = self.colores['primario'] if nombre == 'cpu_uso' else self.colores['secundario']
                        
                        fig.add_trace(go.Scatter(
                            x=datos_metricas['timestamp'],
                            y=datos_metricas['valor'],
                            mode='lines',
                            name=nombre.replace('_', ' ').title(),
                            line=dict(color=color, width=2)
                        ))
            
            fig.update_layout(
                title="Tendencias de CPU y Memoria (Últimas 6 Horas, showlegend=False)",
                xaxis_title="Tiempo",
                yaxis_title="Porcentaje (%)",
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creando gráfico de tendencias: {e}")
            return go.Figure()
    
    def _crear_tabla_servicios(self) -> html.Div:
        """Crear tabla de servicios"""
        try:
            # Obtener datos de servicios
            self.cursor_bd.execute('''
                SELECT nombre, estado, latencia, errores, timestamp FROM servicios 
                WHERE timestamp > datetime('now', '-1 hour')
                ORDER BY timestamp DESC
                LIMIT 20
            ''')
            
            datos = self.cursor_bd.fetchall()
            
            if not datos:
                # Datos sintéticos
                servicios = [
                    {'nombre': 'API Principal', 'estado': 'healthy', 'latencia': 0.05, 'errores': 0},
                    {'nombre': 'API Meteorología', 'estado': 'healthy', 'latencia': 0.08, 'errores': 0},
                    {'nombre': 'API Agrícola', 'estado': 'degraded', 'latencia': 2.5, 'errores': 2},
                    {'nombre': 'Dashboard', 'estado': 'healthy', 'latencia': 0.12, 'errores': 0},
                    {'nombre': 'PostgreSQL', 'estado': 'healthy', 'latencia': 0.03, 'errores': 0},
                    {'nombre': 'Redis', 'estado': 'healthy', 'latencia': 0.01, 'errores': 0}
                ]
            else:
                # Procesar datos reales
                servicios = []
                for nombre, estado, latencia, errores, timestamp in datos:
                    servicios.append({
                        'nombre': nombre,
                        'estado': estado,
                        'latencia': latencia,
                        'errores': errores,
                        'timestamp': timestamp
                    })
            
            # Crear tabla
            filas = []
            for servicio in servicios:
                color_estado = "success" if servicio['estado'] == 'healthy' else \
                             "warning" if servicio['estado'] == 'degraded' else "danger"
                
                filas.append(
                    html.Tr([
                        html.Td(servicio['nombre']),
                        html.Td(
                            dbc.Badge(servicio['estado'].title(), color=color_estado)
                        ),
                        html.Td(f"{servicio['latencia']:.3f}s"),
                        html.Td(servicio['errores']),
                        html.Td(servicio.get('timestamp', 'N/A'))
                    ])
                )
            
            tabla = dbc.Table(
                [
                    html.Thead([
                        html.Tr([
                            html.Th("Servicio"),
                            html.Th("Estado"),
                            html.Th("Latencia"),
                            html.Th("Errores"),
                            html.Th("Última Actualización")
                        ])
                    ]),
                    html.Tbody(filas)
                ],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True
            )
            
            return tabla
            
        except Exception as e:
            print(f"Error creando tabla de servicios: {e}")
            return html.Div("Error cargando tabla de servicios")
    
    def generar_dashboard_html(self) -> str:
        """Generar dashboard como archivo HTML estático"""
        try:
            print("📊 Generando dashboard HTML estático...")
            
            # Crear datos de ejemplo
            fechas = pd.date_range(end=datetime.now(), periods=60, freq='1min')
            
            # Crear figura principal
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=fechas,
                y=np.random.uniform(20, 80, len(fechas)),
                mode='lines',
                name='CPU',
                line=dict(color=self.colores['primario'])
            ))
            
            fig.add_trace(go.Scatter(
                x=fechas,
                y=np.random.uniform(30, 70, len(fechas)),
                mode='lines',
                name='Memoria',
                line=dict(color=self.colores['secundario'])
            ))
            
            fig.update_layout(
                title="METGO 3D - Dashboard de Monitoreo",
                xaxis_title="Tiempo",
                yaxis_title="Porcentaje (%, showlegend=False)",
                template='plotly_white',
                height=600
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/dashboard_monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(archivo_html)
            
            print(f"✅ Dashboard HTML generado: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error generando dashboard HTML: {e}")
            return ""
    
    def ejecutar_dashboard(self, puerto: int = 8051, debug: bool = False) -> bool:
        """Ejecutar dashboard en modo servidor"""
        try:
            print(f"🚀 Iniciando dashboard de monitoreo en puerto {puerto}...")
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
            print("📋 Generando reporte del dashboard de monitoreo...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Dashboard de Monitoreo',
                'version': self.configuracion['version'],
                'resumen': {
                    'componentes': [
                        'Métricas del sistema en tiempo real',
                        'Gráfico de métricas del sistema',
                        'Lista de alertas activas',
                        'Estado de servicios',
                        'Distribución de métricas',
                        'Tendencias de CPU y memoria',
                        'Tabla detallada de servicios'
                    ],
                    'frecuencia_actualizacion': '30 segundos',
                    'colores_tema': self.colores
                },
                'configuracion': self.configuracion,
                'recomendaciones': [
                    "El dashboard se actualiza automáticamente cada 30 segundos",
                    "Monitorear regularmente las alertas activas",
                    "Revisar el estado de servicios críticos",
                    "Analizar tendencias de métricas del sistema",
                    "Configurar umbrales de alerta apropiados"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"dashboard_monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte del dashboard generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del dashboard de monitoreo"""
    print("📊 DASHBOARD DE MONITOREO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Dashboard de Monitoreo en Tiempo Real")
    print("=" * 80)
    
    try:
        # Crear dashboard
        dashboard = DashboardMonitoreoMETGO()
        
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
        print(f"   Luego accede a: http://localhost:8051")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en dashboard de monitoreo: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--servidor':
            # Ejecutar dashboard en modo servidor
            dashboard = DashboardMonitoreoMETGO()
            dashboard.ejecutar_dashboard()
        else:
            # Ejecutar función principal
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
