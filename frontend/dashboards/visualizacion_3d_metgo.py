#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 VISUALIZACIÓN 3D PARA METGO 3D
Sistema Meteorológico Agrícola Quillota - Visualizaciones 3D e Inmersivas
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# Configuración
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class Visualizacion3DMETGO:
    """Clase para visualizaciones 3D e inmersivas del sistema METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/processed',
            'directorio_graficos': 'graficos/3d',
            'directorio_html': 'visualizaciones_html',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Variables meteorológicas
        self.variables_meteorologicas = [
            'temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion',
            'humedad', 'presion', 'radiacion_solar', 'punto_rocio'
        ]
        
        # Colores para Quillota
        self.colores_quillota = {
            'primario': '#2E8B57',      # Verde mar
            'secundario': '#FFD700',    # Dorado
            'acento': '#FF6347',        # Tomate
            'neutro': '#708090',        # Gris pizarra
            'fondo': '#F5F5DC'          # Beige
        }
        
        # Resultados de visualizaciones
        self.visualizaciones = {}
        self.graficos_3d = {}
        self.dashboards = {}
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def cargar_datos_meteorologicos(self, archivo: str = None) -> pd.DataFrame:
        """Cargar datos meteorológicos para visualización"""
        try:
            if archivo is None:
                archivo = f"{self.configuracion['directorio_datos']}/datos_meteorologicos_quillota.csv"
            
            if not Path(archivo).exists():
                print(f"Archivo no encontrado: {archivo}")
                return self._generar_datos_sinteticos()
            
            datos = pd.read_csv(archivo)
            datos['fecha'] = pd.to_datetime(datos['fecha'])
            datos.set_index('fecha', inplace=True)
            
            print(f"✅ Datos cargados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return self._generar_datos_sinteticos()
    
    def _generar_datos_sinteticos(self) -> pd.DataFrame:
        """Generar datos sintéticos para visualización"""
        try:
            print("🔄 Generando datos sintéticos...")
            
            # Generar fechas (2 años de datos)
            fechas = pd.date_range(
                start='2022-01-01',
                end='2024-01-01',
                freq='H'
            )
            
            # Generar datos sintéticos realistas
            np.random.seed(42)
            datos = pd.DataFrame(index=fechas)
            
            # Temperatura (patrón estacional)
            datos['temperatura'] = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
            
            # Precipitación (eventos esporádicos)
            datos['precipitacion'] = np.random.exponential(0.5, len(fechas))
            datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, datos['precipitacion'], 0)
            
            # Viento
            datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
            datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
            
            # Humedad (inversamente relacionada con temperatura)
            datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
            datos['humedad'] = np.clip(datos['humedad'], 0, 100)
            
            # Presión
            datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
            
            # Radiación solar
            datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
            
            # Punto de rocío
            datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
            
            print(f"✅ Datos sintéticos generados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def crear_visualizacion_3d_temperatura(self, datos: pd.DataFrame) -> str:
        """Crear visualización 3D de temperatura"""
        try:
            print("🎨 Creando visualización 3D de temperatura...")
            
            if 'temperatura' not in datos.columns:
                print("Variable temperatura no encontrada")
                return ""
            
            # Preparar datos
            fechas = datos.index
            dias = fechas.dayofyear
            horas = fechas.hour
            temperaturas = datos['temperatura'].values
            
            # Crear gráfico 3D
            fig = go.Figure(data=[go.Scatter3d(
                x=dias,
                y=horas,
                z=temperaturas,
                mode='markers',
                marker=dict(
                    size=3,
                    color=temperaturas,
                    colorscale='RdYlBu_r',
                    colorbar=dict(title="Temperatura (°C)"),
                    opacity=0.8
                ),
                text=[f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M')}<br>Temperatura: {temp:.1f}°C" 
                      for fecha, temp in zip(fechas, temperaturas)],
                hovertemplate='%{text}<extra></extra>'
            )])
            
            # Configurar layout
            fig.update_layout(
                title='Visualización 3D de Temperatura - Quillota',
                scene=dict(
                    xaxis_title='Día del Año',
                    yaxis_title='Hora del Día',
                    zaxis_title='Temperatura (°C)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1000,
                height=800,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/temperatura_3d.html"
            fig.write_html(archivo_html)
            
            self.visualizaciones['temperatura_3d'] = archivo_html
            print(f"✅ Visualización 3D de temperatura creada: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando visualización 3D de temperatura: {e}")
            return ""
    
    def crear_visualizacion_3d_viento(self, datos: pd.DataFrame) -> str:
        """Crear visualización 3D de viento"""
        try:
            print("🎨 Creando visualización 3D de viento...")
            
            if 'viento_velocidad' not in datos.columns or 'viento_direccion' not in datos.columns:
                print("Variables de viento no encontradas")
                return ""
            
            # Preparar datos
            fechas = datos.index
            dias = fechas.dayofyear
            horas = fechas.hour
            velocidades = datos['viento_velocidad'].values
            direcciones = datos['viento_direccion'].values
            
            # Convertir dirección a coordenadas
            x_viento = velocidades * np.cos(np.radians(direcciones))
            y_viento = velocidades * np.sin(np.radians(direcciones))
            
            # Crear gráfico 3D
            fig = go.Figure(data=[go.Scatter3d(
                x=dias,
                y=horas,
                z=velocidades,
                mode='markers',
                marker=dict(
                    size=4,
                    color=velocidades,
                    colorscale='Blues',
                    colorbar=dict(title="Velocidad (m/s)"),
                    opacity=0.8
                ),
                text=[f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M')}<br>Velocidad: {vel:.1f} m/s<br>Dirección: {dir:.1f}°" 
                      for fecha, vel, dir in zip(fechas, velocidades, direcciones)],
                hovertemplate='%{text}<extra></extra>'
            )])
            
            # Configurar layout
            fig.update_layout(
                title='Visualización 3D de Viento - Quillota',
                scene=dict(
                    xaxis_title='Día del Año',
                    yaxis_title='Hora del Día',
                    zaxis_title='Velocidad del Viento (m/s)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1000,
                height=800,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/viento_3d.html"
            fig.write_html(archivo_html)
            
            self.visualizaciones['viento_3d'] = archivo_html
            print(f"✅ Visualización 3D de viento creada: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando visualización 3D de viento: {e}")
            return ""
    
    def crear_visualizacion_3d_multivariable(self, datos: pd.DataFrame) -> str:
        """Crear visualización 3D multivariable"""
        try:
            print("🎨 Creando visualización 3D multivariable...")
            
            # Preparar datos
            fechas = datos.index
            dias = fechas.dayofyear
            horas = fechas.hour
            
            # Crear subplots 3D
            fig = make_subplots(
                rows=2, cols=2,
                specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}],
                       [{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
                subplot_titles=('Temperatura', 'Humedad', 'Presión', 'Radiación Solar'),
                vertical_spacing=0.1,
                horizontal_spacing=0.1
            )
            
            # Temperatura
            if 'temperatura' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['temperatura'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['temperatura'].values, colorscale='RdYlBu_r'),
                        name='Temperatura',
                        hovertemplate='Temperatura: %{z:.1f}°C<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Humedad
            if 'humedad' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['humedad'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['humedad'].values, colorscale='Blues'),
                        name='Humedad',
                        hovertemplate='Humedad: %{z:.1f}%<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # Presión
            if 'presion' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['presion'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['presion'].values, colorscale='Greens'),
                        name='Presión',
                        hovertemplate='Presión: %{z:.1f} hPa<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # Radiación solar
            if 'radiacion_solar' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['radiacion_solar'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['radiacion_solar'].values, colorscale='Oranges'),
                        name='Radiación Solar',
                        hovertemplate='Radiación: %{z:.1f} W/m²<extra></extra>'
                    ),
                    row=2, col=2
                )
            
            # Configurar layout
            fig.update_layout(
                title='Visualización 3D Multivariable - Quillota',
                height=1200,
                width=1400,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            # Configurar ejes para cada subplot
            for i in range(1, 3):
                for j in range(1, 3):
                    fig.update_scenes(
                        xaxis_title='Día del Año',
                        yaxis_title='Hora del Día',
                        zaxis_title='Valor',
                        row=i, col=j
                    )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/multivariable_3d.html"
            fig.write_html(archivo_html)
            
            self.visualizaciones['multivariable_3d'] = archivo_html
            print(f"✅ Visualización 3D multivariable creada: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando visualización 3D multivariable: {e}")
            return ""
    
    def crear_dashboard_interactivo_3d(self, datos: pd.DataFrame) -> str:
        """Crear dashboard interactivo 3D"""
        try:
            print("🎨 Creando dashboard interactivo 3D...")
            
            # Crear figura principal
            fig = go.Figure()
            
            # Agregar múltiples trazas
            if 'temperatura' in datos.columns:
                fig.add_trace(go.Scatter3d(
                    x=datos.index.dayofyear,
                    y=datos.index.hour,
                    z=datos['temperatura'].values,
                    mode='markers',
                    marker=dict(
                        size=3,
                        color=datos['temperatura'].values,
                        colorscale='RdYlBu_r',
                        colorbar=dict(title="Temperatura (°C)")
                    ),
                    name='Temperatura',
                    hovertemplate='Temperatura: %{z:.1f}°C<extra></extra>'
                ))
            
            if 'humedad' in datos.columns:
                fig.add_trace(go.Scatter3d(
                    x=datos.index.dayofyear,
                    y=datos.index.hour,
                    z=datos['humedad'].values,
                    mode='markers',
                    marker=dict(
                        size=3,
                        color=datos['humedad'].values,
                        colorscale='Blues',
                        colorbar=dict(title="Humedad (%)")
                    ),
                    name='Humedad',
                    hovertemplate='Humedad: %{z:.1f}%<extra></extra>'
                ))
            
            if 'viento_velocidad' in datos.columns:
                fig.add_trace(go.Scatter3d(
                    x=datos.index.dayofyear,
                    y=datos.index.hour,
                    z=datos['viento_velocidad'].values,
                    mode='markers',
                    marker=dict(
                        size=3,
                        color=datos['viento_velocidad'].values,
                        colorscale='Greens',
                        colorbar=dict(title="Viento (m/s)")
                    ),
                    name='Viento',
                    hovertemplate='Viento: %{z:.1f} m/s<extra></extra>'
                ))
            
            # Configurar layout
            fig.update_layout(
                title='Dashboard Interactivo 3D - METGO 3D Quillota',
                scene=dict(
                    xaxis_title='Día del Año',
                    yaxis_title='Hora del Día',
                    zaxis_title='Valor',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1200,
                height=800,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white',
                showlegend=True
            )
            
            # Agregar controles interactivos
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=list([
                            dict(
                                args=["visible", [True, False, False]],
                                label="Temperatura",
                                method="restyle"
                            ),
                            dict(
                                args=["visible", [False, True, False]],
                                label="Humedad",
                                method="restyle"
                            ),
                            dict(
                                args=["visible", [False, False, True]],
                                label="Viento",
                                method="restyle"
                            ),
                            dict(
                                args=["visible", [True, True, True]],
                                label="Todas",
                                method="restyle"
                            )
                        ]),
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.01,
                        xanchor="left",
                        y=1.02,
                        yanchor="top"
                    ),
                ]
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/dashboard_interactivo_3d.html"
            fig.write_html(archivo_html)
            
            self.dashboards['interactivo_3d'] = archivo_html
            print(f"✅ Dashboard interactivo 3D creado: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando dashboard interactivo 3D: {e}")
            return ""
    
    def crear_visualizacion_estacional_3d(self, datos: pd.DataFrame) -> str:
        """Crear visualización estacional 3D"""
        try:
            print("🎨 Creando visualización estacional 3D...")
            
            # Preparar datos estacionales
            datos_estacionales = datos.copy()
            datos_estacionales['mes'] = datos_estacionales.index.month
            datos_estacionales['dia'] = datos_estacionales.index.day
            datos_estacionales['hora'] = datos_estacionales.index.hour
            
            # Crear gráfico 3D estacional
            fig = go.Figure()
            
            # Colores por estación
            colores_estacion = {
                12: 'blue', 1: 'blue', 2: 'blue',    # Verano
                3: 'green', 4: 'green', 5: 'green',  # Otoño
                6: 'orange', 7: 'orange', 8: 'orange', # Invierno
                9: 'red', 10: 'red', 11: 'red'       # Primavera
            }
            
            for mes in range(1, 13):
                datos_mes = datos_estacionales[datos_estacionales['mes'] == mes]
                
                if 'temperatura' in datos_mes.columns and len(datos_mes) > 0:
                    fig.add_trace(go.Scatter3d(
                        x=datos_mes['dia'],
                        y=datos_mes['hora'],
                        z=datos_mes['temperatura'].values,
                        mode='markers',
                        marker=dict(
                            size=2,
                            color=colores_estacion.get(mes, 'gray'),
                            opacity=0.7
                        ),
                        name=f'Mes {mes}',
                        hovertemplate=f'Mes {mes}<br>Temperatura: %{{z:.1f}}°C<extra></extra>'
                    ))
            
            # Configurar layout
            fig.update_layout(
                title='Visualización Estacional 3D - Temperatura Quillota',
                scene=dict(
                    xaxis_title='Día del Mes',
                    yaxis_title='Hora del Día',
                    zaxis_title='Temperatura (°C)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1000,
                height=800,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white',
                showlegend=True
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/estacional_3d.html"
            fig.write_html(archivo_html)
            
            self.visualizaciones['estacional_3d'] = archivo_html
            print(f"✅ Visualización estacional 3D creada: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando visualización estacional 3D: {e}")
            return ""
    
    def crear_visualizacion_correlaciones_3d(self, datos: pd.DataFrame) -> str:
        """Crear visualización 3D de correlaciones"""
        try:
            print("🎨 Creando visualización 3D de correlaciones...")
            
            # Seleccionar variables numéricas
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Calcular matriz de correlación
            matriz_correlacion = datos_numericos.corr()
            
            # Crear gráfico 3D de correlaciones
            fig = go.Figure(data=[go.Surface(
                z=matriz_correlacion.values,
                x=matriz_correlacion.columns,
                y=matriz_correlacion.columns,
                colorscale='RdBu',
                colorbar=dict(title="Correlación")
            )])
            
            # Configurar layout
            fig.update_layout(
                title='Matriz de Correlaciones 3D - Variables Meteorológicas',
                scene=dict(
                    xaxis_title='Variable 1',
                    yaxis_title='Variable 2',
                    zaxis_title='Correlación',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=1000,
                height=800,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/correlaciones_3d.html"
            fig.write_html(archivo_html)
            
            self.visualizaciones['correlaciones_3d'] = archivo_html
            print(f"✅ Visualización 3D de correlaciones creada: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando visualización 3D de correlaciones: {e}")
            return ""
    
    def crear_dashboard_completo_3d(self, datos: pd.DataFrame) -> str:
        """Crear dashboard completo 3D"""
        try:
            print("🎨 Creando dashboard completo 3D...")
            
            # Crear subplots
            fig = make_subplots(
                rows=2, cols=2,
                specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}],
                       [{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
                subplot_titles=('Temperatura 3D', 'Humedad 3D', 'Viento 3D', 'Presión 3D'),
                vertical_spacing=0.1,
                horizontal_spacing=0.1
            )
            
            # Preparar datos
            dias = datos.index.dayofyear
            horas = datos.index.hour
            
            # Temperatura 3D
            if 'temperatura' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['temperatura'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['temperatura'].values, colorscale='RdYlBu_r'),
                        name='Temperatura',
                        hovertemplate='Temperatura: %{z:.1f}°C<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Humedad 3D
            if 'humedad' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['humedad'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['humedad'].values, colorscale='Blues'),
                        name='Humedad',
                        hovertemplate='Humedad: %{z:.1f}%<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # Viento 3D
            if 'viento_velocidad' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['viento_velocidad'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['viento_velocidad'].values, colorscale='Greens'),
                        name='Viento',
                        hovertemplate='Viento: %{z:.1f} m/s<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # Presión 3D
            if 'presion' in datos.columns:
                fig.add_trace(
                    go.Scatter3d(
                        x=dias, y=horas, z=datos['presion'].values,
                        mode='markers',
                        marker=dict(size=2, color=datos['presion'].values, colorscale='Oranges'),
                        name='Presión',
                        hovertemplate='Presión: %{z:.1f} hPa<extra></extra>'
                    ),
                    row=2, col=2
                )
            
            # Configurar layout
            fig.update_layout(
                title='Dashboard Completo 3D - METGO 3D Quillota',
                height=1200,
                width=1400,
                font=dict(family="Arial", size=12),
                paper_bgcolor='white',
                plot_bgcolor='white',
                showlegend=True
            )
            
            # Configurar ejes para cada subplot
            for i in range(1, 3):
                for j in range(1, 3):
                    fig.update_scenes(
                        xaxis_title='Día del Año',
                        yaxis_title='Hora del Día',
                        zaxis_title='Valor',
                        row=i, col=j
                    )
            
            # Guardar como HTML
            archivo_html = f"{self.configuracion['directorio_html']}/dashboard_completo_3d.html"
            fig.write_html(archivo_html)
            
            self.dashboards['completo_3d'] = archivo_html
            print(f"✅ Dashboard completo 3D creado: {archivo_html}")
            return archivo_html
            
        except Exception as e:
            print(f"Error creando dashboard completo 3D: {e}")
            return ""
    
    def generar_reporte_visualizaciones_3d(self) -> str:
        """Generar reporte de visualizaciones 3D"""
        try:
            print("📋 Generando reporte de visualizaciones 3D...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Visualizaciones 3D',
                'version': self.configuracion['version'],
                'resumen': {
                    'total_visualizaciones': len(self.visualizaciones),
                    'total_dashboards': len(self.dashboards),
                    'archivos_html_generados': len(self.visualizaciones) + len(self.dashboards)
                },
                'visualizaciones': self.visualizaciones,
                'dashboards': self.dashboards,
                'recomendaciones': [
                    "Las visualizaciones 3D proporcionan una perspectiva única de los datos meteorológicos",
                    "Los dashboards interactivos permiten explorar los datos de manera dinámica",
                    "Las visualizaciones estacionales muestran patrones temporales claros",
                    "Las correlaciones 3D facilitan la identificación de relaciones entre variables",
                    "Se recomienda usar estas visualizaciones para presentaciones y análisis detallados"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"visualizaciones_3d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte de visualizaciones 3D generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de visualizaciones 3D"""
    print("🎨 VISUALIZACIÓN 3D PARA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Visualizaciones 3D e Inmersivas")
    print("=" * 80)
    
    try:
        # Crear instancia de visualizaciones 3D
        visualizaciones = Visualizacion3DMETGO()
        
        # Cargar datos
        print("\n📊 Cargando datos meteorológicos...")
        datos = visualizaciones.cargar_datos_meteorologicos()
        
        if datos.empty:
            print("❌ No se pudieron cargar los datos")
            return False
        
        # Crear visualizaciones 3D
        print("\n🎨 Creando visualizaciones 3D...")
        
        # Visualización 3D de temperatura
        visualizaciones.crear_visualizacion_3d_temperatura(datos)
        
        # Visualización 3D de viento
        visualizaciones.crear_visualizacion_3d_viento(datos)
        
        # Visualización 3D multivariable
        visualizaciones.crear_visualizacion_3d_multivariable(datos)
        
        # Dashboard interactivo 3D
        visualizaciones.crear_dashboard_interactivo_3d(datos)
        
        # Visualización estacional 3D
        visualizaciones.crear_visualizacion_estacional_3d(datos)
        
        # Visualización 3D de correlaciones
        visualizaciones.crear_visualizacion_correlaciones_3d(datos)
        
        # Dashboard completo 3D
        visualizaciones.crear_dashboard_completo_3d(datos)
        
        # Generar reporte
        print("\n📋 Generando reporte...")
        reporte = visualizaciones.generar_reporte_visualizaciones_3d()
        
        if reporte:
            print(f"\n✅ Visualizaciones 3D completadas exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print("\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en visualizaciones 3D: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

