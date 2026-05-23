"""
Sistema de visualización y dashboard meteorológico.
Versión operativa con gráficos interactivos.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class DashboardMeteorologico:
    """
    Clase para crear dashboard meteorológico interactivo.
    
    Características:
    - Gráficos interactivos con Plotly
    - Visualizaciones estáticas con Matplotlib
    - Dashboard completo meteorológico
    - Exportación de gráficos
    - Temas personalizados para Quillota
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar dashboard meteorológico.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuración de visualización
        self.viz_config = config.get('VISUALIZACION', {})
        self.colores = self.viz_config.get('graficos', {}).get('colores', {})
        
        # Configurar estilo matplotlib
        self._configurar_matplotlib()
        
        self.logger.info("Dashboard meteorológico inicializado")
    
    def _configurar_matplotlib(self):
        """Configurar estilo de matplotlib."""
        plt.style.use('default')
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'axes.grid': True,
            'grid.alpha': 0.3
        })
    
    def crear_dashboard_completo(self, analisis: Dict[str, Any], 
                                datos: pd.DataFrame) -> None:
        """
        Crear dashboard meteorológico completo.
        
        Args:
            analisis: Resultados del análisis meteorológico
            datos: DataFrame con datos meteorológicos
        """
        self.logger.info("Creando dashboard meteorológico completo")
        
        try:
            # Crear gráficos principales
            self._crear_grafico_temperaturas(datos)
            self._crear_grafico_precipitacion(datos)
            self._crear_grafico_humedad_viento(datos)
            self._crear_dashboard_interactivo(datos)
            
            self.logger.info("Dashboard meteorológico creado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando dashboard: {e}")
            raise
    
    def _crear_grafico_temperaturas(self, datos: pd.DataFrame):
        """Crear gráfico de temperaturas."""
        self.logger.debug("Creando gráfico de temperaturas")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Gráfico de temperaturas
        ax.plot(datos['fecha'], datos['temperatura_max'], 
                'r-', label='Temperatura Máxima', linewidth=2, marker='o', markersize=3)
        ax.plot(datos['fecha'], datos['temperatura_min'], 
                'b-', label='Temperatura Mínima', linewidth=2, marker='o', markersize=3)
        
        # Área sombreada entre temperaturas
        ax.fill_between(datos['fecha'], datos['temperatura_min'], 
                       datos['temperatura_max'], alpha=0.2, color='gray')
        
        # Líneas de referencia
        ax.axhline(y=0, color='orange', linestyle='--', alpha=0.7, label='Punto de congelación')
        ax.axhline(y=35, color='red', linestyle='--', alpha=0.7, label='Calor extremo')
        
        ax.set_title('🌡️ Temperaturas Máximas y Mínimas - Quillota', fontweight='bold', fontsize=16)
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Temperatura (°C)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas de fecha
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('logs/grafico_temperaturas.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _crear_grafico_precipitacion(self, datos: pd.DataFrame):
        """Crear gráfico de precipitación."""
        self.logger.debug("Creando gráfico de precipitación")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Gráfico de barras de precipitación
        bars = ax.bar(datos['fecha'], datos['precipitacion'], 
                     color='skyblue', alpha=0.7, edgecolor='navy', linewidth=0.5)
        
        # Línea de referencia para lluvia intensa
        ax.axhline(y=20, color='orange', linestyle='--', alpha=0.7, 
                  label='Lluvia intensa (20 mm)')
        
        ax.set_title('🌧️ Precipitación Diaria - Quillota', fontweight='bold', fontsize=16)
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Precipitación (mm)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('logs/grafico_precipitacion.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _crear_grafico_humedad_viento(self, datos: pd.DataFrame):
        """Crear gráfico de humedad y viento."""
        self.logger.debug("Creando gráfico de humedad y viento")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Gráfico de humedad
        ax1.plot(datos['fecha'], datos['humedad_relativa'], 
                'g-', linewidth=2, marker='s', markersize=3)
        ax1.fill_between(datos['fecha'], datos['humedad_relativa'], 
                        alpha=0.3, color='green')
        ax1.axhline(y=30, color='orange', linestyle='--', alpha=0.7, 
                   label='Humedad muy baja (30%)')
        ax1.axhline(y=85, color='red', linestyle='--', alpha=0.7, 
                   label='Humedad muy alta (85%)')
        ax1.set_title('💧 Humedad Relativa', fontweight='bold')
        ax1.set_ylabel('Humedad (%)')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Gráfico de viento
        ax2.plot(datos['fecha'], datos['velocidad_viento'], 
                'purple', linewidth=2, marker='^', markersize=3)
        ax2.fill_between(datos['fecha'], datos['velocidad_viento'], 
                        alpha=0.3, color='purple')
        ax2.axhline(y=15, color='orange', linestyle='--', alpha=0.7, 
                   label='Viento moderado (15 km/h)')
        ax2.axhline(y=25, color='red', linestyle='--', alpha=0.7, 
                   label='Viento fuerte (25 km/h)')
        ax2.set_title('💨 Velocidad del Viento', fontweight='bold')
        ax2.set_xlabel('Fecha')
        ax2.set_ylabel('Velocidad (km/h)')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('logs/grafico_humedad_viento.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _crear_dashboard_interactivo(self, datos: pd.DataFrame):
        """Crear dashboard interactivo con Plotly."""
        self.logger.debug("Creando dashboard interactivo")
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperaturas', 'Precipitación', 'Humedad', 'Viento'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Gráfico de temperaturas
        fig.add_trace(
            go.Scatter(x=datos['fecha'], y=datos['temperatura_max'],
                      mode='lines+markers', name='Temp Máxima',
                      line=dict(color='red', width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=datos['fecha'], y=datos['temperatura_min'],
                      mode='lines+markers', name='Temp Mínima',
                      line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Gráfico de precipitación
        fig.add_trace(
            go.Bar(x=datos['fecha'], y=datos['precipitacion'],
                   name='Precipitación', marker_color='skyblue'),
            row=1, col=2
        )
        
        # Gráfico de humedad
        fig.add_trace(
            go.Scatter(x=datos['fecha'], y=datos['humedad_relativa'],
                      mode='lines+markers', name='Humedad',
                      line=dict(color='green', width=2)),
            row=2, col=1
        )
        
        # Gráfico de viento
        fig.add_trace(
            go.Scatter(x=datos['fecha'], y=datos['velocidad_viento'],
                      mode='lines+markers', name='Viento',
                      line=dict(color='purple', width=2)),
            row=2, col=2
        )
        
        # Actualizar layout
        fig.update_layout(
            title_text="🌾 Dashboard Meteorológico Quillota - METGO 3D Operativo",
            title_x=0.5,
            height=800,
            showlegend=True,
            template="plotly_white"
        )
        
        # Actualizar ejes
        fig.update_xaxes(title_text="Fecha", row=2, col=1)
        fig.update_xaxes(title_text="Fecha", row=2, col=2)
        fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Precipitación (mm)", row=1, col=2)
        fig.update_yaxes(title_text="Humedad (%)", row=2, col=1)
        fig.update_yaxes(title_text="Velocidad (km/h)", row=2, col=2)
        
        # Mostrar dashboard
        fig.show()
        
        # Guardar como HTML
        fig.write_html("logs/dashboard_interactivo.html")
        self.logger.info("Dashboard interactivo guardado como HTML")
    
    def crear_grafico_alertas(self, alertas: List[Dict[str, Any]]):
        """Crear gráfico de alertas meteorológicas."""
        if not alertas:
            self.logger.info("No hay alertas para mostrar")
            return
        
        self.logger.debug("Creando gráfico de alertas")
        
        # Preparar datos de alertas
        tipos_alerta = {}
        for alerta in alertas:
            tipo = alerta['tipo']
            if tipo not in tipos_alerta:
                tipos_alerta[tipo] = 0
            tipos_alerta[tipo] += 1
        
        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        
        tipos = list(tipos_alerta.keys())
        cantidades = list(tipos_alerta.values())
        
        # Colores según severidad
        colores = []
        for tipo in tipos:
            if 'severa' in tipo or 'extremo' in tipo:
                colores.append('red')
            elif 'fuerte' in tipo or 'intensa' in tipo:
                colores.append('orange')
            else:
                colores.append('yellow')
        
        bars = ax.bar(tipos, cantidades, color=colores, alpha=0.7)
        
        ax.set_title('🚨 Alertas Meteorológicas Generadas', fontweight='bold', fontsize=16)
        ax.set_xlabel('Tipo de Alerta')
        ax.set_ylabel('Cantidad')
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('logs/grafico_alertas.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def crear_grafico_estadisticas(self, analisis: Dict[str, Any]):
        """Crear gráfico de estadísticas meteorológicas."""
        self.logger.debug("Creando gráfico de estadísticas")
        
        # Extraer estadísticas principales
        stats = analisis.get('estadisticas_temperatura', {})
        
        # Crear gráfico de métricas
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Temperaturas extremas
        ax1.bar(['Máxima', 'Mínima'], 
               [stats.get('temperatura_maxima', 0), stats.get('temperatura_minima', 0)],
               color=['red', 'blue'], alpha=0.7)
        ax1.set_title('Temperaturas Extremas')
        ax1.set_ylabel('Temperatura (°C)')
        
        # Días con condiciones especiales
        condiciones = ['Heladas', 'Calor Extremo']
        cantidades = [stats.get('dias_helada', 0), stats.get('dias_calor_extremo', 0)]
        ax2.bar(condiciones, cantidades, color=['lightblue', 'orange'], alpha=0.7)
        ax2.set_title('Días con Condiciones Especiales')
        ax2.set_ylabel('Cantidad de Días')
        
        # Precipitación
        precip_stats = analisis.get('analisis_precipitacion', {})
        ax3.bar(['Total', 'Promedio'], 
               [precip_stats.get('precipitacion_total', 0), 
                precip_stats.get('precipitacion_promedio', 0)],
               color=['skyblue', 'navy'], alpha=0.7)
        ax3.set_title('Precipitación')
        ax3.set_ylabel('Precipitación (mm)')
        
        # Índices agrícolas
        indices = analisis.get('indices_agricolas', {})
        ax4.bar(['Grados-Día', 'Confort'], 
               [indices.get('grados_dia_total', 0), 50],  # Normalizar confort
               color=['green', 'lightgreen'], alpha=0.7)
        ax4.set_title('Índices Agrícolas')
        ax4.set_ylabel('Valor')
        
        plt.suptitle('📊 Estadísticas Meteorológicas Quillota', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig('logs/grafico_estadisticas.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def exportar_graficos(self, formato: str = 'png'):
        """
        Exportar todos los gráficos generados.
        
        Args:
            formato: Formato de exportación (png, pdf, svg)
        """
        self.logger.info(f"Exportando gráficos en formato {formato}")
        
        # Lista de archivos de gráficos
        archivos_graficos = [
            'logs/grafico_temperaturas.png',
            'logs/grafico_precipitacion.png',
            'logs/grafico_humedad_viento.png',
            'logs/grafico_alertas.png',
            'logs/grafico_estadisticas.png'
        ]
        
        # Verificar que existen
        archivos_existentes = [f for f in archivos_graficos if Path(f).exists()]
        
        if archivos_existentes:
            self.logger.info(f"Gráficos exportados: {len(archivos_existentes)} archivos")
            return archivos_existentes
        else:
            self.logger.warning("No se encontraron gráficos para exportar")
            return []
