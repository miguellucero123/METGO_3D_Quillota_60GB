#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ EXPANSIÓN REGIONAL METGO 3D
Sistema Meteorológico Agrícola Quillota - Expansión a Otras Regiones de Chile
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

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class RegionChile:
    """Región de Chile"""
    id: str
    nombre: str
    codigo: str
    capital: str
    coordenadas: Tuple[float, float]
    superficie: float
    poblacion: int
    clima: str
    cultivos_principales: List[str]
    configuracion: Dict[str, Any]

@dataclass
class EstacionMeteorologica:
    """Estación meteorológica regional"""
    id: str
    nombre: str
    region_id: str
    coordenadas: Tuple[float, float]
    altitud: float
    activa: bool
    sensores: List[str]
    ultima_actualizacion: str
    configuracion: Dict[str, Any]

@dataclass
class CultivoRegional:
    """Cultivo específico de una región"""
    id: str
    nombre: str
    region_id: str
    temporada_siembra: str
    temporada_cosecha: str
    requerimientos_climaticos: Dict[str, Any]
    rendimiento_promedio: float
    configuracion: Dict[str, Any]

class ExpansionRegionalMETGO:
    """Sistema de expansión regional para METGO 3D"""
    
    def __init__(self):
        # Inicializar logger primero
        self.logger = logging.getLogger('METGO_REGIONAL')
        
        self.configuracion = {
            'directorio_datos': 'data/regional',
            'directorio_logs': 'logs/regional',
            'directorio_reportes': 'reportes/regional',
            'directorio_configuracion': 'config/regional',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración regional
        self.configuracion_regional = {
            'region_principal': 'Valparaíso',
            'regiones_objetivo': [
                'Metropolitana',
                'O\'Higgins',
                'Maule',
                'Biobío',
                'La Araucanía'
            ],
            'expansion_prioritaria': True,
            'sincronizacion_datos': True,
            'analisis_comparativo': True
        }
        
        # Regiones, estaciones y cultivos
        self.regiones = {}
        self.estaciones = {}
        self.cultivos = {}
        
        # Configurar regiones de Chile
        self._configurar_regiones_chile()
        self._configurar_estaciones_regionales()
        self._configurar_cultivos_regionales()
    
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
            # Configurar logging solo si no está ya configurado
            if not self.logger.handlers:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"{self.configuracion['directorio_logs']}/regional.log"),
                        logging.StreamHandler()
                    ]
                )
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/regional.db"
            
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
            # Tabla de regiones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS regiones_chile (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    codigo TEXT NOT NULL,
                    capital TEXT NOT NULL,
                    coordenadas TEXT NOT NULL,
                    superficie REAL NOT NULL,
                    poblacion INTEGER NOT NULL,
                    clima TEXT NOT NULL,
                    cultivos_principales TEXT NOT NULL,
                    configuracion TEXT,
                    activa BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de estaciones meteorológicas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS estaciones_meteorologicas (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    region_id TEXT NOT NULL,
                    coordenadas TEXT NOT NULL,
                    altitud REAL NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    sensores TEXT NOT NULL,
                    ultima_actualizacion DATETIME,
                    configuracion TEXT,
                    FOREIGN KEY (region_id) REFERENCES regiones_chile (id)
                )
            ''')
            
            # Tabla de cultivos regionales
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS cultivos_regionales (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    region_id TEXT NOT NULL,
                    temporada_siembra TEXT NOT NULL,
                    temporada_cosecha TEXT NOT NULL,
                    requerimientos_climaticos TEXT NOT NULL,
                    rendimiento_promedio REAL NOT NULL,
                    configuracion TEXT,
                    FOREIGN KEY (region_id) REFERENCES regiones_chile (id)
                )
            ''')
            
            # Tabla de datos meteorológicos regionales
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos_regionales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperatura REAL NOT NULL,
                    humedad REAL NOT NULL,
                    precipitacion REAL NOT NULL,
                    viento REAL NOT NULL,
                    presion REAL NOT NULL,
                    radiacion REAL NOT NULL,
                    calidad_datos REAL,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_meteorologicas (id)
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_regiones_activa ON regiones_chile(activa)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_estaciones_region ON estaciones_meteorologicas(region_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_cultivos_region ON cultivos_regionales(region_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_datos_estacion ON datos_meteorologicos_regionales(estacion_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_regiones_chile(self):
        """Configurar regiones de Chile"""
        try:
            regiones_data = [
                {
                    'id': 'region_05',
                    'nombre': 'Valparaíso',
                    'codigo': 'V',
                    'capital': 'Valparaíso',
                    'coordenadas': (-33.0458, -71.6197),
                    'superficie': 16396.1,
                    'poblacion': 1815902,
                    'clima': 'Mediterráneo',
                    'cultivos_principales': ['Palta', 'Cítricos', 'Vid', 'Hortalizas'],
                    'configuracion': {
                        'temperatura_promedio': 16.5,
                        'precipitacion_anual': 400,
                        'estacion_lluvias': 'invierno'
                    }
                },
                {
                    'id': 'region_13',
                    'nombre': 'Metropolitana',
                    'codigo': 'RM',
                    'capital': 'Santiago',
                    'coordenadas': (-33.4489, -70.6693),
                    'superficie': 15403.2,
                    'poblacion': 7112808,
                    'clima': 'Mediterráneo continental',
                    'cultivos_principales': ['Vid', 'Frutales', 'Hortalizas', 'Cereales'],
                    'configuracion': {
                        'temperatura_promedio': 14.0,
                        'precipitacion_anual': 350,
                        'estacion_lluvias': 'invierno'
                    }
                },
                {
                    'id': 'region_06',
                    'nombre': 'O\'Higgins',
                    'codigo': 'VI',
                    'capital': 'Rancagua',
                    'coordenadas': (-34.1708, -70.7444),
                    'superficie': 16387.0,
                    'poblacion': 914555,
                    'clima': 'Mediterráneo',
                    'cultivos_principales': ['Vid', 'Frutales', 'Cereales', 'Hortalizas'],
                    'configuracion': {
                        'temperatura_promedio': 15.0,
                        'precipitacion_anual': 500,
                        'estacion_lluvias': 'invierno'
                    }
                },
                {
                    'id': 'region_07',
                    'nombre': 'Maule',
                    'codigo': 'VII',
                    'capital': 'Talca',
                    'coordenadas': (-35.4264, -71.6554),
                    'superficie': 30296.1,
                    'poblacion': 1044950,
                    'clima': 'Mediterráneo',
                    'cultivos_principales': ['Vid', 'Frutales', 'Cereales', 'Forestal'],
                    'configuracion': {
                        'temperatura_promedio': 14.5,
                        'precipitacion_anual': 700,
                        'estacion_lluvias': 'invierno'
                    }
                },
                {
                    'id': 'region_08',
                    'nombre': 'Biobío',
                    'codigo': 'VIII',
                    'capital': 'Concepción',
                    'coordenadas': (-36.8201, -73.0444),
                    'superficie': 23890.2,
                    'poblacion': 1556805,
                    'clima': 'Mediterráneo oceánico',
                    'cultivos_principales': ['Forestal', 'Cereales', 'Hortalizas', 'Frutales'],
                    'configuracion': {
                        'temperatura_promedio': 13.0,
                        'precipitacion_anual': 1200,
                        'estacion_lluvias': 'invierno'
                    }
                },
                {
                    'id': 'region_09',
                    'nombre': 'La Araucanía',
                    'codigo': 'IX',
                    'capital': 'Temuco',
                    'coordenadas': (-38.7359, -72.5904),
                    'superficie': 31842.3,
                    'poblacion': 957224,
                    'clima': 'Templado oceánico',
                    'cultivos_principales': ['Forestal', 'Cereales', 'Hortalizas', 'Frutales'],
                    'configuracion': {
                        'temperatura_promedio': 12.0,
                        'precipitacion_anual': 1400,
                        'estacion_lluvias': 'invierno'
                    }
                }
            ]
            
            for region_data in regiones_data:
                region = RegionChile(
                    id=region_data['id'],
                    nombre=region_data['nombre'],
                    codigo=region_data['codigo'],
                    capital=region_data['capital'],
                    coordenadas=region_data['coordenadas'],
                    superficie=region_data['superficie'],
                    poblacion=region_data['poblacion'],
                    clima=region_data['clima'],
                    cultivos_principales=region_data['cultivos_principales'],
                    configuracion=region_data['configuracion']
                )
                self.regiones[region.id] = region
            
            self.logger.info(f"Regiones configuradas: {len(self.regiones)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando regiones: {e}")
    
    def _configurar_estaciones_regionales(self):
        """Configurar estaciones meteorológicas regionales"""
        try:
            estaciones_data = [
                {
                    'id': 'estacion_valparaiso',
                    'nombre': 'Estación Valparaíso',
                    'region_id': 'region_05',
                    'coordenadas': (-33.0458, -71.6197),
                    'altitud': 10,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.95
                    }
                },
                {
                    'id': 'estacion_santiago',
                    'nombre': 'Estación Santiago',
                    'region_id': 'region_13',
                    'coordenadas': (-33.4489, -70.6693),
                    'altitud': 520,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.98
                    }
                },
                {
                    'id': 'estacion_rancagua',
                    'nombre': 'Estación Rancagua',
                    'region_id': 'region_06',
                    'coordenadas': (-34.1708, -70.7444),
                    'altitud': 572,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.92
                    }
                },
                {
                    'id': 'estacion_talca',
                    'nombre': 'Estación Talca',
                    'region_id': 'region_07',
                    'coordenadas': (-35.4264, -71.6554),
                    'altitud': 102,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.90
                    }
                },
                {
                    'id': 'estacion_concepcion',
                    'nombre': 'Estación Concepción',
                    'region_id': 'region_08',
                    'coordenadas': (-36.8201, -73.0444),
                    'altitud': 12,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.88
                    }
                },
                {
                    'id': 'estacion_temuco',
                    'nombre': 'Estación Temuco',
                    'region_id': 'region_09',
                    'coordenadas': (-38.7359, -72.5904),
                    'altitud': 114,
                    'sensores': ['temperatura', 'humedad', 'precipitacion', 'viento', 'presion'],
                    'configuracion': {
                        'intervalo_lectura': 300,
                        'calidad_datos': 0.85
                    }
                }
            ]
            
            for estacion_data in estaciones_data:
                estacion = EstacionMeteorologica(
                    id=estacion_data['id'],
                    nombre=estacion_data['nombre'],
                    region_id=estacion_data['region_id'],
                    coordenadas=estacion_data['coordenadas'],
                    altitud=estacion_data['altitud'],
                    activa=True,
                    sensores=estacion_data['sensores'],
                    ultima_actualizacion=datetime.now().isoformat(),
                    configuracion=estacion_data['configuracion']
                )
                self.estaciones[estacion.id] = estacion
            
            self.logger.info(f"Estaciones configuradas: {len(self.estaciones)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando estaciones: {e}")
    
    def _configurar_cultivos_regionales(self):
        """Configurar cultivos regionales"""
        try:
            cultivos_data = [
                {
                    'id': 'cultivo_vid_valparaiso',
                    'nombre': 'Vid de Mesa',
                    'region_id': 'region_05',
                    'temporada_siembra': 'septiembre',
                    'temporada_cosecha': 'febrero-marzo',
                    'requerimientos_climaticos': {
                        'temperatura_min': 10,
                        'temperatura_max': 35,
                        'precipitacion_anual': 400,
                        'horas_frio': 200
                    },
                    'rendimiento_promedio': 15.5,
                    'configuracion': {
                        'tipo': 'frutal',
                        'ciclo': 'anual'
                    }
                },
                {
                    'id': 'cultivo_palta_valparaiso',
                    'nombre': 'Palta Hass',
                    'region_id': 'region_05',
                    'temporada_siembra': 'agosto',
                    'temporada_cosecha': 'mayo-septiembre',
                    'requerimientos_climaticos': {
                        'temperatura_min': 15,
                        'temperatura_max': 30,
                        'precipitacion_anual': 600,
                        'horas_frio': 100
                    },
                    'rendimiento_promedio': 12.0,
                    'configuracion': {
                        'tipo': 'frutal',
                        'ciclo': 'perenne'
                    }
                },
                {
                    'id': 'cultivo_vid_santiago',
                    'nombre': 'Vid para Vino',
                    'region_id': 'region_13',
                    'temporada_siembra': 'septiembre',
                    'temporada_cosecha': 'marzo-abril',
                    'requerimientos_climaticos': {
                        'temperatura_min': 8,
                        'temperatura_max': 32,
                        'precipitacion_anual': 350,
                        'horas_frio': 300
                    },
                    'rendimiento_promedio': 8.5,
                    'configuracion': {
                        'tipo': 'frutal',
                        'ciclo': 'anual'
                    }
                },
                {
                    'id': 'cultivo_maiz_ohiggins',
                    'nombre': 'Maíz',
                    'region_id': 'region_06',
                    'temporada_siembra': 'septiembre',
                    'temporada_cosecha': 'marzo-abril',
                    'requerimientos_climaticos': {
                        'temperatura_min': 12,
                        'temperatura_max': 30,
                        'precipitacion_anual': 500,
                        'horas_frio': 0
                    },
                    'rendimiento_promedio': 10.0,
                    'configuracion': {
                        'tipo': 'cereal',
                        'ciclo': 'anual'
                    }
                },
                {
                    'id': 'cultivo_forestal_maule',
                    'nombre': 'Pino Radiata',
                    'region_id': 'region_07',
                    'temporada_siembra': 'junio',
                    'temporada_cosecha': '15-20 años',
                    'requerimientos_climaticos': {
                        'temperatura_min': 5,
                        'temperatura_max': 25,
                        'precipitacion_anual': 700,
                        'horas_frio': 500
                    },
                    'rendimiento_promedio': 25.0,
                    'configuracion': {
                        'tipo': 'forestal',
                        'ciclo': 'perenne'
                    }
                },
                {
                    'id': 'cultivo_trigo_biobio',
                    'nombre': 'Trigo',
                    'region_id': 'region_08',
                    'temporada_siembra': 'mayo',
                    'temporada_cosecha': 'diciembre-enero',
                    'requerimientos_climaticos': {
                        'temperatura_min': 8,
                        'temperatura_max': 25,
                        'precipitacion_anual': 1200,
                        'horas_frio': 200
                    },
                    'rendimiento_promedio': 6.5,
                    'configuracion': {
                        'tipo': 'cereal',
                        'ciclo': 'anual'
                    }
                }
            ]
            
            for cultivo_data in cultivos_data:
                cultivo = CultivoRegional(
                    id=cultivo_data['id'],
                    nombre=cultivo_data['nombre'],
                    region_id=cultivo_data['region_id'],
                    temporada_siembra=cultivo_data['temporada_siembra'],
                    temporada_cosecha=cultivo_data['temporada_cosecha'],
                    requerimientos_climaticos=cultivo_data['requerimientos_climaticos'],
                    rendimiento_promedio=cultivo_data['rendimiento_promedio'],
                    configuracion=cultivo_data['configuracion']
                )
                self.cultivos[cultivo.id] = cultivo
            
            self.logger.info(f"Cultivos configurados: {len(self.cultivos)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando cultivos: {e}")
    
    def generar_datos_meteorologicos_regionales(self) -> Dict[str, Any]:
        """Generar datos meteorológicos para todas las regiones"""
        try:
            self.logger.info("Generando datos meteorológicos regionales...")
            
            datos_regionales = {}
            
            for estacion_id, estacion in self.estaciones.items():
                if estacion.activa:
                    # Generar datos sintéticos basados en la región
                    region = self.regiones.get(estacion.region_id)
                    if region:
                        # Ajustar datos según configuración regional
                        temp_base = region.configuracion.get('temperatura_promedio', 15)
                        prec_base = region.configuracion.get('precipitacion_anual', 500) / 365
                        
                        # Generar variación diaria
                        np.random.seed(hash(estacion_id) % 2**32)
                        
                        datos_estacion = {
                            'estacion_id': estacion_id,
                            'region_id': estacion.region_id,
                            'timestamp': datetime.now().isoformat(),
                            'temperatura': temp_base + np.random.randn() * 3,
                            'humedad': 60 + np.random.randn() * 15,
                            'precipitacion': max(0, prec_base + np.random.randn() * 2),
                            'viento': 8 + np.random.randn() * 4,
                            'presion': 1013 + np.random.randn() * 8,
                            'radiacion': 300 + np.random.randn() * 100,
                            'calidad_datos': estacion.configuracion.get('calidad_datos', 0.9)
                        }
                        
                        # Guardar en base de datos
                        self._guardar_datos_meteorologicos(datos_estacion)
                        
                        datos_regionales[estacion_id] = datos_estacion
            
            self.logger.info(f"Datos generados para {len(datos_regionales)} estaciones")
            return datos_regionales
            
        except Exception as e:
            self.logger.error(f"Error generando datos meteorológicos: {e}")
            return {}
    
    def _guardar_datos_meteorologicos(self, datos: Dict[str, Any]):
        """Guardar datos meteorológicos en base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO datos_meteorologicos_regionales 
                (estacion_id, timestamp, temperatura, humedad, precipitacion, viento, presion, radiacion, calidad_datos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos['estacion_id'],
                datos['timestamp'],
                datos['temperatura'],
                datos['humedad'],
                datos['precipitacion'],
                datos['viento'],
                datos['presion'],
                datos['radiacion'],
                datos['calidad_datos']
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando datos meteorológicos: {e}")
    
    def analizar_comparativo_regional(self) -> Dict[str, Any]:
        """Analizar datos comparativos entre regiones"""
        try:
            self.logger.info("Realizando análisis comparativo regional...")
            
            # Generar datos actuales
            datos_actuales = self.generar_datos_meteorologicos_regionales()
            
            # Análisis por región
            analisis_regional = {}
            
            for region_id, region in self.regiones.items():
                # Obtener estaciones de la región
                estaciones_region = [
                    est for est in self.estaciones.values() 
                    if est.region_id == region_id and est.activa
                ]
                
                if estaciones_region:
                    # Calcular promedios regionales
                    temperaturas = []
                    humedades = []
                    precipitaciones = []
                    
                    for estacion in estaciones_region:
                        datos_estacion = datos_actuales.get(estacion.id, {})
                        if datos_estacion:
                            temperaturas.append(datos_estacion.get('temperatura', 0))
                            humedades.append(datos_estacion.get('humedad', 0))
                            precipitaciones.append(datos_estacion.get('precipitacion', 0))
                    
                    if temperaturas:
                        analisis_regional[region_id] = {
                            'region': region.nombre,
                            'capital': region.capital,
                            'clima': region.clima,
                            'estaciones_activas': len(estaciones_region),
                            'temperatura_promedio': np.mean(temperaturas),
                            'humedad_promedio': np.mean(humedades),
                            'precipitacion_promedio': np.mean(precipitaciones),
                            'cultivos_principales': region.cultivos_principales,
                            'superficie': region.superficie,
                            'poblacion': region.poblacion
                        }
            
            # Análisis comparativo
            analisis_comparativo = {
                'timestamp': datetime.now().isoformat(),
                'regiones_analizadas': len(analisis_regional),
                'analisis_por_region': analisis_regional,
                'ranking_temperatura': sorted(
                    analisis_regional.items(),
                    key=lambda x: x[1]['temperatura_promedio'],
                    reverse=True
                ),
                'ranking_precipitacion': sorted(
                    analisis_regional.items(),
                    key=lambda x: x[1]['precipitacion_promedio'],
                    reverse=True
                ),
                'resumen': {
                    'region_mas_calida': max(analisis_regional.items(), key=lambda x: x[1]['temperatura_promedio'])[0],
                    'region_mas_fria': min(analisis_regional.items(), key=lambda x: x[1]['temperatura_promedio'])[0],
                    'region_mas_lluviosa': max(analisis_regional.items(), key=lambda x: x[1]['precipitacion_promedio'])[0],
                    'region_mas_seca': min(analisis_regional.items(), key=lambda x: x[1]['precipitacion_promedio'])[0]
                }
            }
            
            self.logger.info("Análisis comparativo regional completado")
            return analisis_comparativo
            
        except Exception as e:
            self.logger.error(f"Error en análisis comparativo: {e}")
            return {}
    
    def generar_reporte_expansion(self) -> str:
        """Generar reporte de expansión regional"""
        try:
            self.logger.info("Generando reporte de expansión regional...")
            
            # Análisis comparativo
            analisis_comparativo = self.analizar_comparativo_regional()
            
            # Datos meteorológicos actuales
            datos_actuales = self.generar_datos_meteorologicos_regionales()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Expansión Regional',
                'version': self.configuracion['version'],
                'configuracion_regional': self.configuracion_regional,
                'regiones': [
                    {
                        'id': r.id,
                        'nombre': r.nombre,
                        'codigo': r.codigo,
                        'capital': r.capital,
                        'coordenadas': r.coordenadas,
                        'superficie': r.superficie,
                        'poblacion': r.poblacion,
                        'clima': r.clima,
                        'cultivos_principales': r.cultivos_principales
                    } for r in self.regiones.values()
                ],
                'estaciones': [
                    {
                        'id': e.id,
                        'nombre': e.nombre,
                        'region_id': e.region_id,
                        'coordenadas': e.coordenadas,
                        'altitud': e.altitud,
                        'activa': e.activa,
                        'sensores': e.sensores
                    } for e in self.estaciones.values()
                ],
                'cultivos': [
                    {
                        'id': c.id,
                        'nombre': c.nombre,
                        'region_id': c.region_id,
                        'temporada_siembra': c.temporada_siembra,
                        'temporada_cosecha': c.temporada_cosecha,
                        'rendimiento_promedio': c.rendimiento_promedio
                    } for c in self.cultivos.values()
                ],
                'datos_meteorologicos_actuales': datos_actuales,
                'analisis_comparativo': analisis_comparativo,
                'funcionalidades_implementadas': [
                    'Expansión a 6 regiones de Chile',
                    'Estaciones meteorológicas regionales',
                    'Cultivos específicos por región',
                    'Análisis comparativo regional',
                    'Base de datos SQLite regional',
                    'Generación de datos sintéticos',
                    'Sistema de logging estructurado',
                    'Configuración por región',
                    'Análisis climático comparativo',
                    'Ranking de condiciones meteorológicas'
                ],
                'tecnologias_utilizadas': [
                    'SQLite para base de datos regional',
                    'NumPy para análisis estadístico',
                    'Pandas para manejo de datos',
                    'Logging estructurado',
                    'Configuración por región'
                ],
                'recomendaciones': [
                    'Integrar con estaciones meteorológicas reales',
                    'Implementar pronósticos regionales',
                    'Agregar análisis de tendencias climáticas',
                    'Implementar alertas regionales',
                    'Agregar mapas interactivos',
                    'Implementar sincronización en tiempo real',
                    'Agregar análisis de impacto agrícola',
                    'Implementar recomendaciones por región',
                    'Agregar métricas de rendimiento',
                    'Implementar sistema de notificaciones regional'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"expansion_regional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de expansión regional generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de expansión regional"""
    print("EXPANSION REGIONAL METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Expansion a Otras Regiones de Chile")
    print("=" * 80)
    
    try:
        # Crear sistema de expansión regional
        expansion_sistema = ExpansionRegionalMETGO()
        
        # Generar reporte
        print(f"\nGenerando reporte de expansion regional...")
        reporte = expansion_sistema.generar_reporte_expansion()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema de Expansion Regional METGO 3D")
        print(f"Version: {expansion_sistema.configuracion['version']}")
        print(f"Region principal: {expansion_sistema.configuracion_regional['region_principal']}")
        print(f"Regiones objetivo: {len(expansion_sistema.configuracion_regional['regiones_objetivo'])}")
        
        print(f"\nRegiones configuradas:")
        for region in expansion_sistema.regiones.values():
            print(f"   - {region.nombre} ({region.codigo}): {region.capital}")
            print(f"     Clima: {region.clima} | Superficie: {region.superficie:,.0f} km²")
            print(f"     Cultivos: {', '.join(region.cultivos_principales)}")
        
        print(f"\nEstaciones meteorologicas:")
        for estacion in expansion_sistema.estaciones.values():
            region = expansion_sistema.regiones.get(estacion.region_id)
            region_nombre = region.nombre if region else 'Desconocida'
            print(f"   - {estacion.nombre} ({region_nombre}): {estacion.altitud}m")
            print(f"     Sensores: {', '.join(estacion.sensores)}")
        
        print(f"\nCultivos regionales:")
        for cultivo in expansion_sistema.cultivos.values():
            region = expansion_sistema.regiones.get(cultivo.region_id)
            region_nombre = region.nombre if region else 'Desconocida'
            print(f"   - {cultivo.nombre} ({region_nombre})")
            print(f"     Siembra: {cultivo.temporada_siembra} | Cosecha: {cultivo.temporada_cosecha}")
            print(f"     Rendimiento: {cultivo.rendimiento_promedio} t/ha")
        
        # Mostrar análisis comparativo
        print(f"\nAnalizando datos comparativos regionales...")
        analisis = expansion_sistema.analizar_comparativo_regional()
        
        if analisis:
            print(f"Regiones analizadas: {analisis.get('regiones_analizadas', 0)}")
            
            print(f"\nRanking de temperatura:")
            for i, (region_id, datos) in enumerate(analisis.get('ranking_temperatura', [])[:3], 1):
                print(f"   {i}. {datos['region']}: {datos['temperatura_promedio']:.1f}°C")
            
            print(f"\nRanking de precipitacion:")
            for i, (region_id, datos) in enumerate(analisis.get('ranking_precipitacion', [])[:3], 1):
                print(f"   {i}. {datos['region']}: {datos['precipitacion_promedio']:.1f} mm")
            
            resumen = analisis.get('resumen', {})
            print(f"\nResumen:")
            print(f"   Region mas calida: {resumen.get('region_mas_calida', 'N/A')}")
            print(f"   Region mas fria: {resumen.get('region_mas_fria', 'N/A')}")
            print(f"   Region mas lluviosa: {resumen.get('region_mas_lluviosa', 'N/A')}")
            print(f"   Region mas seca: {resumen.get('region_mas_seca', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\nError en expansion regional: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
