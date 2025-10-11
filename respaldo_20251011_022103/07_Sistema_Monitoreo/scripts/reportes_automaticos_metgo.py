#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 REPORTES AUTOMÁTICOS METGO 3D
Sistema Meteorológico Agrícola Quillota - Sistema de Reportes Automáticos
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import sqlite3
from dataclasses import dataclass
import yaml

# ReportLab para PDFs
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Matplotlib para gráficos
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Jinja2 para templates
try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class ReporteAutomatico:
    """Reporte automático"""
    id: str
    nombre: str
    tipo: str
    frecuencia: str
    formato: str
    configuracion: Dict[str, Any]
    ultima_generacion: Optional[str] = None
    proxima_generacion: Optional[str] = None
    activo: bool = True

@dataclass
class DatosReporte:
    """Datos para reporte"""
    timestamp: str
    tipo_datos: str
    datos: Dict[str, Any]
    metricas: Dict[str, float]
    graficos: List[str]
    observaciones: List[str]

class ReportesAutomaticosMETGO:
    """Sistema de reportes automáticos para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_reportes': 'reportes/automaticos',
            'directorio_templates': 'templates/reportes',
            'directorio_datos': 'data/reportes',
            'directorio_logs': 'logs/reportes',
            'directorio_salida': 'reportes/generados',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Verificar dependencias
        self._verificar_dependencias()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración de reportes
        self.configuracion_reportes = {
            'formato_default': 'PDF',
            'idioma': 'es',
            'timezone': 'America/Santiago',
            'compresion': True,
            'enviar_email': False,
            'backup_automatico': True
        }
        
        # Reportes predefinidos
        self.reportes_predefinidos = {}
        self._configurar_reportes_predefinidos()
        
        # Datos de reportes
        self.datos_reportes = {}
        
        # Programación de reportes
        self.programacion_reportes = {}
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/reportes.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_REPORTES')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _verificar_dependencias(self):
        """Verificar dependencias de reportes"""
        try:
            self.logger.info("Verificando dependencias de reportes...")
            
            dependencias = {
                'ReportLab': REPORTLAB_AVAILABLE,
                'Matplotlib': MATPLOTLIB_AVAILABLE,
                'Jinja2': JINJA2_AVAILABLE
            }
            
            for lib, disponible in dependencias.items():
                if disponible:
                    self.logger.info(f"{lib} disponible")
                else:
                    self.logger.warning(f"{lib} no disponible")
            
            if not REPORTLAB_AVAILABLE:
                self.logger.warning("ReportLab no disponible - solo se generarán reportes JSON")
            
        except Exception as e:
            self.logger.error(f"Error verificando dependencias: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/reportes.db"
            
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
            
            # Crear tablas
            self._crear_tablas_bd()
            
            self.logger.info(f"Base de datos inicializada: {archivo_bd}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _crear_tablas_bd(self):
        """Crear tablas en la base de datos"""
        try:
            # Tabla de reportes automáticos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS reportes_automaticos (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    frecuencia TEXT NOT NULL,
                    formato TEXT NOT NULL,
                    configuracion TEXT NOT NULL,
                    ultima_generacion DATETIME,
                    proxima_generacion DATETIME,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de generación de reportes
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS generacion_reportes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reporte_id TEXT NOT NULL,
                    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    archivo_generado TEXT,
                    tamaño_archivo INTEGER,
                    estado TEXT NOT NULL,
                    observaciones TEXT,
                    FOREIGN KEY (reporte_id) REFERENCES reportes_automaticos (id)
                )
            ''')
            
            # Tabla de datos de reportes
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS datos_reportes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_datos TEXT NOT NULL,
                    datos TEXT NOT NULL,
                    metricas TEXT,
                    graficos TEXT,
                    observaciones TEXT
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_reportes_activo ON reportes_automaticos(activo)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_generacion_reporte ON generacion_reportes(reporte_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_datos_tipo ON datos_reportes(tipo_datos)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_reportes_predefinidos(self):
        """Configurar reportes predefinidos"""
        try:
            reportes_data = [
                {
                    'id': 'reporte_diario',
                    'nombre': 'Reporte Meteorológico Diario',
                    'tipo': 'meteorologico',
                    'frecuencia': 'diario',
                    'formato': 'PDF',
                    'configuracion': {
                        'incluir_graficos': True,
                        'incluir_pronostico': True,
                        'incluir_alertas': True,
                        'incluir_recomendaciones': True
                    }
                },
                {
                    'id': 'reporte_semanal',
                    'nombre': 'Reporte Agrícola Semanal',
                    'tipo': 'agricola',
                    'frecuencia': 'semanal',
                    'formato': 'PDF',
                    'configuracion': {
                        'incluir_graficos': True,
                        'incluir_tendencias': True,
                        'incluir_analisis': True,
                        'incluir_proyecciones': True
                    }
                },
                {
                    'id': 'reporte_mensual',
                    'nombre': 'Reporte Ejecutivo Mensual',
                    'tipo': 'ejecutivo',
                    'frecuencia': 'mensual',
                    'formato': 'PDF',
                    'configuracion': {
                        'incluir_resumen': True,
                        'incluir_metricas': True,
                        'incluir_comparaciones': True,
                        'incluir_objetivos': True
                    }
                },
                {
                    'id': 'reporte_alerta',
                    'nombre': 'Reporte de Alertas',
                    'tipo': 'alertas',
                    'frecuencia': 'evento',
                    'formato': 'PDF',
                    'configuracion': {
                        'incluir_graficos': True,
                        'incluir_acciones': True,
                        'incluir_impacto': True,
                        'incluir_recomendaciones': True
                    }
                }
            ]
            
            for reporte_data in reportes_data:
                reporte = ReporteAutomatico(
                    id=reporte_data['id'],
                    nombre=reporte_data['nombre'],
                    tipo=reporte_data['tipo'],
                    frecuencia=reporte_data['frecuencia'],
                    formato=reporte_data['formato'],
                    configuracion=reporte_data['configuracion']
                )
                self.reportes_predefinidos[reporte.id] = reporte
            
            self.logger.info(f"Reportes predefinidos configurados: {len(self.reportes_predefinidos)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando reportes predefinidos: {e}")
    
    def generar_datos_sinteticos(self, tipo_datos: str, n_registros: int = 100) -> DatosReporte:
        """Generar datos sintéticos para reportes"""
        try:
            self.logger.info(f"Generando {n_registros} registros sintéticos de tipo {tipo_datos}")
            
            np.random.seed(42)
            
            # Generar datos según el tipo
            if tipo_datos == 'meteorologico':
                datos = self._generar_datos_meteorologicos(n_registros)
            elif tipo_datos == 'agricola':
                datos = self._generar_datos_agricolas(n_registros)
            elif tipo_datos == 'alertas':
                datos = self._generar_datos_alertas(n_registros)
            else:
                datos = self._generar_datos_genericos(n_registros)
            
            # Calcular métricas
            metricas = self._calcular_metricas(datos)
            
            # Generar gráficos
            graficos = self._generar_graficos(datos, tipo_datos)
            
            # Generar observaciones
            observaciones = self._generar_observaciones(datos, tipo_datos)
            
            # Crear objeto de datos
            datos_reporte = DatosReporte(
                timestamp=datetime.now().isoformat(),
                tipo_datos=tipo_datos,
                datos=datos,
                metricas=metricas,
                graficos=graficos,
                observaciones=observaciones
            )
            
            self.datos_reportes[tipo_datos] = datos_reporte
            
            return datos_reporte
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return DatosReporte(
                timestamp=datetime.now().isoformat(),
                tipo_datos=tipo_datos,
                datos={},
                metricas={},
                graficos=[],
                observaciones=[]
            )
    
    def _generar_datos_meteorologicos(self, n_registros: int) -> Dict[str, Any]:
        """Generar datos meteorológicos sintéticos"""
        try:
            fechas = pd.date_range(start='2024-01-01', periods=n_registros, freq='H')
            
            datos = {
                'fechas': [fecha.isoformat() for fecha in fechas],
                'temperatura': 15 + np.random.randn(n_registros) * 8,
                'humedad': 60 + np.random.randn(n_registros) * 20,
                'presion': 1013 + np.random.randn(n_registros) * 20,
                'viento_velocidad': 5 + np.random.randn(n_registros) * 3,
                'viento_direccion': np.random.randint(0, 360, n_registros),
                'precipitacion': np.maximum(0, np.random.randn(n_registros) * 5),
                'radiacion': 300 + np.random.randn(n_registros) * 100,
                'indice_uv': np.random.randint(0, 11, n_registros)
            }
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos meteorológicos: {e}")
            return {}
    
    def _generar_datos_agricolas(self, n_registros: int) -> Dict[str, Any]:
        """Generar datos agrícolas sintéticos"""
        try:
            fechas = pd.date_range(start='2024-01-01', periods=n_registros, freq='D')
            
            datos = {
                'fechas': [fecha.isoformat() for fecha in fechas],
                'ndvi': 0.3 + np.random.randn(n_registros) * 0.2,
                'ndwi': 0.1 + np.random.randn(n_registros) * 0.1,
                'evi': 0.2 + np.random.randn(n_registros) * 0.15,
                'savi': 0.25 + np.random.randn(n_registros) * 0.2,
                'humedad_suelo': 40 + np.random.randn(n_registros) * 15,
                'temperatura_suelo': 18 + np.random.randn(n_registros) * 5,
                'ph_suelo': 6.5 + np.random.randn(n_registros) * 0.5,
                'conductividad': 1.2 + np.random.randn(n_registros) * 0.3
            }
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos agrícolas: {e}")
            return {}
    
    def _generar_datos_alertas(self, n_registros: int) -> Dict[str, Any]:
        """Generar datos de alertas sintéticos"""
        try:
            tipos_alertas = ['helada', 'sequia', 'lluvia_intensa', 'viento_fuerte', 'calor_extremo']
            severidades = ['baja', 'media', 'alta', 'critica']
            
            alertas = []
            for i in range(n_registros):
                alerta = {
                    'id': f"alerta_{i+1}",
                    'tipo': np.random.choice(tipos_alertas),
                    'severidad': np.random.choice(severidades),
                    'mensaje': f"Alerta {np.random.choice(tipos_alertas)} detectada",
                    'timestamp': (datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
                    'coordenadas': {
                        'lat': -32.8833 + np.random.randn() * 0.1,
                        'lon': -71.2333 + np.random.randn() * 0.1
                    },
                    'impacto': np.random.choice(['bajo', 'medio', 'alto']),
                    'accion_recomendada': f"Acción recomendada para {np.random.choice(tipos_alertas)}"
                }
                alertas.append(alerta)
            
            return {'alertas': alertas}
            
        except Exception as e:
            self.logger.error(f"Error generando datos de alertas: {e}")
            return {}
    
    def _generar_datos_genericos(self, n_registros: int) -> Dict[str, Any]:
        """Generar datos genéricos sintéticos"""
        try:
            fechas = pd.date_range(start='2024-01-01', periods=n_registros, freq='H')
            
            datos = {
                'fechas': [fecha.isoformat() for fecha in fechas],
                'valor_a': np.random.randn(n_registros) * 10 + 50,
                'valor_b': np.random.randn(n_registros) * 5 + 25,
                'valor_c': np.random.randn(n_registros) * 15 + 75,
                'categoria': np.random.choice(['A', 'B', 'C'], n_registros)
            }
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error generando datos genéricos: {e}")
            return {}
    
    def _calcular_metricas(self, datos: Dict[str, Any]) -> Dict[str, float]:
        """Calcular métricas de los datos"""
        try:
            metricas = {}
            
            for clave, valores in datos.items():
                if isinstance(valores, (list, np.ndarray)) and len(valores) > 0:
                    if isinstance(valores[0], (int, float)):
                        metricas[f"{clave}_media"] = np.mean(valores)
                        metricas[f"{clave}_std"] = np.std(valores)
                        metricas[f"{clave}_min"] = np.min(valores)
                        metricas[f"{clave}_max"] = np.max(valores)
                        metricas[f"{clave}_mediana"] = np.median(valores)
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas: {e}")
            return {}
    
    def _generar_graficos(self, datos: Dict[str, Any], tipo_datos: str) -> List[str]:
        """Generar gráficos para el reporte"""
        try:
            if not MATPLOTLIB_AVAILABLE:
                return []
            
            graficos = []
            
            # Crear directorio para gráficos
            graficos_dir = Path(self.configuracion['directorio_salida']) / 'graficos'
            graficos_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar gráfico de series temporales
            if 'fechas' in datos and len(datos['fechas']) > 0:
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Convertir fechas
                fechas = pd.to_datetime(datos['fechas'])
                
                # Plotear datos numéricos
                for clave, valores in datos.items():
                    if clave != 'fechas' and isinstance(valores, (list, np.ndarray)) and len(valores) > 0:
                        if isinstance(valores[0], (int, float)):
                            ax.plot(fechas, valores, label=clave, alpha=0.7)
                
                ax.set_xlabel('Fecha')
                ax.set_ylabel('Valor')
                ax.set_title(f'Series Temporales - {tipo_datos.title()}')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Rotar etiquetas de fecha
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Guardar gráfico
                grafico_path = graficos_dir / f'series_temporales_{tipo_datos}.png'
                plt.savefig(grafico_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                graficos.append(str(grafico_path))
            
            # Generar gráfico de distribución
            if len(datos) > 1:
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                axes = axes.flatten()
                
                datos_numericos = {k: v for k, v in datos.items() 
                                 if isinstance(v, (list, np.ndarray)) and len(v) > 0 
                                 and isinstance(v[0], (int, float))}
                
                for i, (clave, valores) in enumerate(list(datos_numericos.items())[:4]):
                    if i < len(axes):
                        axes[i].hist(valores, bins=20, alpha=0.7, edgecolor='black')
                        axes[i].set_title(f'Distribución de {clave}')
                        axes[i].set_xlabel('Valor')
                        axes[i].set_ylabel('Frecuencia')
                        axes[i].grid(True, alpha=0.3)
                
                # Ocultar ejes vacíos
                for i in range(len(datos_numericos), len(axes)):
                    axes[i].set_visible(False)
                
                plt.tight_layout()
                
                # Guardar gráfico
                grafico_path = graficos_dir / f'distribucion_{tipo_datos}.png'
                plt.savefig(grafico_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                graficos.append(str(grafico_path))
            
            self.logger.info(f"Gráficos generados: {len(graficos)}")
            return graficos
            
        except Exception as e:
            self.logger.error(f"Error generando gráficos: {e}")
            return []
    
    def _generar_observaciones(self, datos: Dict[str, Any], tipo_datos: str) -> List[str]:
        """Generar observaciones sobre los datos"""
        try:
            observaciones = []
            
            if tipo_datos == 'meteorologico':
                if 'temperatura' in datos:
                    temp_media = np.mean(datos['temperatura'])
                    if temp_media > 25:
                        observaciones.append("Temperaturas altas observadas - considerar protección de cultivos")
                    elif temp_media < 10:
                        observaciones.append("Temperaturas bajas - riesgo de heladas")
                
                if 'precipitacion' in datos:
                    prec_total = np.sum(datos['precipitacion'])
                    if prec_total > 50:
                        observaciones.append("Precipitaciones abundantes - reducir riego")
                    elif prec_total < 5:
                        observaciones.append("Sequía - incrementar riego")
            
            elif tipo_datos == 'agricola':
                if 'ndvi' in datos:
                    ndvi_medio = np.mean(datos['ndvi'])
                    if ndvi_medio > 0.6:
                        observaciones.append("Vegetación saludable - buenas condiciones de crecimiento")
                    elif ndvi_medio < 0.3:
                        observaciones.append("Vegetación estresada - revisar condiciones del suelo")
            
            elif tipo_datos == 'alertas':
                if 'alertas' in datos:
                    n_alertas = len(datos['alertas'])
                    if n_alertas > 10:
                        observaciones.append("Alto número de alertas - revisar condiciones generales")
                    elif n_alertas == 0:
                        observaciones.append("Sin alertas activas - condiciones normales")
            
            # Observación general
            observaciones.append(f"Datos procesados el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return observaciones
            
        except Exception as e:
            self.logger.error(f"Error generando observaciones: {e}")
            return []
    
    def generar_reporte_pdf(self, datos_reporte: DatosReporte, nombre_reporte: str) -> str:
        """Generar reporte en formato PDF"""
        try:
            if not REPORTLAB_AVAILABLE:
                self.logger.warning("ReportLab no disponible - generando reporte JSON")
                return self.generar_reporte_json(datos_reporte, nombre_reporte)
            
            self.logger.info(f"Generando reporte PDF: {nombre_reporte}")
            
            # Crear archivo PDF
            pdf_path = Path(self.configuracion['directorio_salida']) / f"{nombre_reporte}.pdf"
            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Contenido del reporte
            story = []
            
            # Título
            story.append(Paragraph("METGO 3D - Sistema Meteorológico Agrícola", title_style))
            story.append(Paragraph(f"Reporte: {nombre_reporte}", styles['Heading2']))
            story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumen ejecutivo
            story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
            story.append(Paragraph(f"Tipo de datos: {datos_reporte.tipo_datos}", styles['Normal']))
            story.append(Paragraph(f"Timestamp: {datos_reporte.timestamp}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Métricas
            if datos_reporte.metricas:
                story.append(Paragraph("Métricas Principales", styles['Heading2']))
                
                # Crear tabla de métricas
                data_metricas = [['Métrica', 'Valor']]
                for metrica, valor in list(datos_reporte.metricas.items())[:10]:  # Limitar a 10 métricas
                    data_metricas.append([metrica, f"{valor:.2f}"])
                
                tabla_metricas = Table(data_metricas)
                tabla_metricas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(tabla_metricas)
                story.append(Spacer(1, 12))
            
            # Observaciones
            if datos_reporte.observaciones:
                story.append(Paragraph("Observaciones", styles['Heading2']))
                for observacion in datos_reporte.observaciones:
                    story.append(Paragraph(f"• {observacion}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Gráficos
            if datos_reporte.graficos:
                story.append(Paragraph("Gráficos", styles['Heading2']))
                for grafico_path in datos_reporte.graficos[:3]:  # Limitar a 3 gráficos
                    if Path(grafico_path).exists():
                        img = Image(grafico_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
            
            # Pie de página
            story.append(Spacer(1, 20))
            story.append(Paragraph("---", styles['Normal']))
            story.append(Paragraph("Generado automáticamente por METGO 3D", styles['Normal']))
            story.append(Paragraph("Sistema Meteorológico Agrícola Quillota", styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            self.logger.info(f"Reporte PDF generado: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte PDF: {e}")
            return ""
    
    def generar_reporte_json(self, datos_reporte: DatosReporte, nombre_reporte: str) -> str:
        """Generar reporte en formato JSON"""
        try:
            self.logger.info(f"Generando reporte JSON: {nombre_reporte}")
            
            # Crear estructura del reporte
            reporte_data = {
                'metadata': {
                    'nombre': nombre_reporte,
                    'tipo_datos': datos_reporte.tipo_datos,
                    'timestamp': datos_reporte.timestamp,
                    'version': self.configuracion['version'],
                    'generado_por': 'METGO 3D - Sistema de Reportes Automáticos'
                },
                'datos': datos_reporte.datos,
                'metricas': datos_reporte.metricas,
                'observaciones': datos_reporte.observaciones,
                'graficos': datos_reporte.graficos
            }
            
            # Guardar archivo JSON
            json_path = Path(self.configuracion['directorio_salida']) / f"{nombre_reporte}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(reporte_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte JSON generado: {json_path}")
            return str(json_path)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte JSON: {e}")
            return ""
    
    def generar_reporte_completo(self, tipo_reporte: str) -> Dict[str, Any]:
        """Generar reporte completo"""
        try:
            self.logger.info(f"Generando reporte completo: {tipo_reporte}")
            
            # Obtener configuración del reporte
            if tipo_reporte in self.reportes_predefinidos:
                reporte_config = self.reportes_predefinidos[tipo_reporte]
            else:
                self.logger.warning(f"Tipo de reporte no encontrado: {tipo_reporte}")
                return {'exitoso': False, 'error': 'Tipo de reporte no encontrado'}
            
            # Generar datos
            datos_reporte = self.generar_datos_sinteticos(reporte_config.tipo, 100)
            
            # Generar reporte según formato
            archivo_generado = ""
            if reporte_config.formato == 'PDF':
                archivo_generado = self.generar_reporte_pdf(datos_reporte, reporte_config.nombre)
            else:
                archivo_generado = self.generar_reporte_json(datos_reporte, reporte_config.nombre)
            
            if not archivo_generado:
                return {'exitoso': False, 'error': 'Error generando archivo de reporte'}
            
            # Guardar en base de datos
            self._guardar_generacion_reporte(reporte_config.id, archivo_generado, 'exitoso')
            
            return {
                'exitoso': True,
                'reporte_id': reporte_config.id,
                'archivo_generado': archivo_generado,
                'tipo_datos': datos_reporte.tipo_datos,
                'metricas': datos_reporte.metricas,
                'observaciones': datos_reporte.observaciones,
                'graficos': len(datos_reporte.graficos)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte completo: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _guardar_generacion_reporte(self, reporte_id: str, archivo_generado: str, estado: str):
        """Guardar información de generación de reporte"""
        try:
            tamaño_archivo = 0
            if Path(archivo_generado).exists():
                tamaño_archivo = Path(archivo_generado).stat().st_size
            
            self.cursor_bd.execute('''
                INSERT INTO generacion_reportes 
                (reporte_id, fecha_generacion, archivo_generado, tamaño_archivo, estado)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                reporte_id,
                datetime.now().isoformat(),
                archivo_generado,
                tamaño_archivo,
                estado
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando generación de reporte: {e}")
    
    def generar_todos_los_reportes(self) -> Dict[str, Any]:
        """Generar todos los reportes predefinidos"""
        try:
            self.logger.info("Generando todos los reportes predefinidos...")
            
            resultados = {}
            
            for reporte_id, reporte_config in self.reportes_predefinidos.items():
                self.logger.info(f"Generando reporte: {reporte_config.nombre}")
                
                resultado = self.generar_reporte_completo(reporte_id)
                resultados[reporte_id] = resultado
                
                if resultado.get('exitoso'):
                    self.logger.info(f"Reporte {reporte_config.nombre} generado exitosamente")
                else:
                    self.logger.error(f"Error generando reporte {reporte_config.nombre}: {resultado.get('error')}")
            
            # Calcular estadísticas
            reportes_exitosos = sum(1 for r in resultados.values() if r.get('exitoso'))
            reportes_fallidos = len(resultados) - reportes_exitosos
            
            estadisticas = {
                'total_reportes': len(resultados),
                'reportes_exitosos': reportes_exitosos,
                'reportes_fallidos': reportes_fallidos,
                'porcentaje_exito': (reportes_exitosos / len(resultados)) * 100 if resultados else 0
            }
            
            return {
                'exitoso': True,
                'resultados': resultados,
                'estadisticas': estadisticas,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando todos los reportes: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_sistema(self) -> str:
        """Generar reporte del sistema de reportes"""
        try:
            self.logger.info("Generando reporte del sistema de reportes...")
            
            # Generar todos los reportes
            resultados_generacion = self.generar_todos_los_reportes()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema de Reportes Automáticos',
                'version': self.configuracion['version'],
                'configuracion_reportes': self.configuracion_reportes,
                'reportes_predefinidos': [
                    {
                        'id': r.id,
                        'nombre': r.nombre,
                        'tipo': r.tipo,
                        'frecuencia': r.frecuencia,
                        'formato': r.formato,
                        'activo': r.activo
                    } for r in self.reportes_predefinidos.values()
                ],
                'resultados_generacion': resultados_generacion,
                'dependencias': {
                    'ReportLab': REPORTLAB_AVAILABLE,
                    'Matplotlib': MATPLOTLIB_AVAILABLE,
                    'Jinja2': JINJA2_AVAILABLE
                },
                'funcionalidades_implementadas': [
                    'Generación automática de reportes',
                    'Múltiples formatos (PDF, JSON)',
                    'Datos sintéticos realistas',
                    'Cálculo automático de métricas',
                    'Generación de gráficos',
                    'Observaciones inteligentes',
                    'Base de datos SQLite',
                    'Sistema de logging',
                    'Reportes predefinidos',
                    'Gestión de archivos'
                ],
                'tecnologias_utilizadas': [
                    'ReportLab para PDFs',
                    'Matplotlib para gráficos',
                    'Pandas para análisis de datos',
                    'NumPy para cálculos',
                    'SQLite para almacenamiento',
                    'Jinja2 para templates'
                ],
                'recomendaciones': [
                    'Implementar programación automática con cron',
                    'Agregar envío automático por email',
                    'Implementar templates personalizables',
                    'Agregar más tipos de gráficos',
                    'Implementar compresión de archivos',
                    'Agregar métricas de rendimiento',
                    'Implementar backup automático',
                    'Agregar validación de datos',
                    'Implementar reportes interactivos',
                    'Agregar exportación a Excel'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"reportes_automaticos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del sistema generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte del sistema: {e}")
            return ""

def main():
    """Función principal de reportes automáticos"""
    print("REPORTES AUTOMATICOS METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Sistema de Reportes Automaticos")
    print("=" * 80)
    
    try:
        # Crear sistema de reportes
        reportes_sistema = ReportesAutomaticosMETGO()
        
        # Generar reporte del sistema
        print(f"\nGenerando reporte del sistema...")
        reporte = reportes_sistema.generar_reporte_sistema()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema de Reportes Automáticos METGO 3D")
        print(f"Version: {reportes_sistema.configuracion['version']}")
        print(f"Formato default: {reportes_sistema.configuracion_reportes['formato_default']}")
        print(f"Idioma: {reportes_sistema.configuracion_reportes['idioma']}")
        
        print(f"\nReportes predefinidos:")
        for reporte_id, reporte_config in reportes_sistema.reportes_predefinidos.items():
            print(f"   - {reporte_config.nombre} ({reporte_config.tipo}, {reporte_config.frecuencia})")
        
        print(f"\nDependencias disponibles:")
        dependencias = {
            'ReportLab': REPORTLAB_AVAILABLE,
            'Matplotlib': MATPLOTLIB_AVAILABLE,
            'Jinja2': JINJA2_AVAILABLE
        }
        
        for lib, disponible in dependencias.items():
            print(f"   - {lib}: {'Disponible' if disponible else 'No disponible'}")
        
        # Mostrar ejemplo de generación
        print(f"\nGenerando reporte de ejemplo...")
        resultado = reportes_sistema.generar_reporte_completo('reporte_diario')
        
        if resultado.get('exitoso'):
            print(f"Reporte generado exitosamente: {resultado.get('archivo_generado')}")
            print(f"Metricas calculadas: {len(resultado.get('metricas', {}))}")
            print(f"Observaciones: {len(resultado.get('observaciones', []))}")
            print(f"Graficos generados: {resultado.get('graficos', 0)}")
        else:
            print(f"Error generando reporte: {resultado.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"\nError en sistema de reportes: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
