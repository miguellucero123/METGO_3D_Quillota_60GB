#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONECTOR IOT Y SATELITAL - METGO 3D
Conectores para sensores IoT y datos satelitales
"""

import os
import json
import time
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import sqlite3
import threading
import queue
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import requests
from io import BytesIO

class ConectorSensoresIoT:
    """Conector para sensores IoT del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('IOT_CONNECTOR')
        self.sensores_activos = {}
        self.datos_sensores = queue.Queue()
        self.simulacion_activa = False
        
        # Configuracion de sensores
        self.sensores_config = {
            'temperatura': {
                'rango': (-5, 40),
                'precision': 0.1,
                'frecuencia': 1,  # segundos
                'unidad': '°C'
            },
            'humedad': {
                'rango': (0, 100),
                'precision': 1,
                'frecuencia': 2,
                'unidad': '%'
            },
            'presion': {
                'rango': (950, 1050),
                'precision': 0.1,
                'frecuencia': 5,
                'unidad': 'hPa'
            },
            'viento_velocidad': {
                'rango': (0, 50),
                'precision': 0.1,
                'frecuencia': 1,
                'unidad': 'km/h'
            },
            'viento_direccion': {
                'rango': (0, 360),
                'precision': 1,
                'frecuencia': 1,
                'unidad': '°'
            },
            'radiacion_solar': {
                'rango': (0, 1000),
                'precision': 1,
                'frecuencia': 3,
                'unidad': 'W/m²'
            },
            'precipitacion': {
                'rango': (0, 50),
                'precision': 0.1,
                'frecuencia': 10,
                'unidad': 'mm/h'
            },
            'suelo_humedad': {
                'rango': (0, 100),
                'precision': 1,
                'frecuencia': 5,
                'unidad': '%'
            },
            'suelo_temperatura': {
                'rango': (-10, 35),
                'precision': 0.1,
                'frecuencia': 5,
                'unidad': '°C'
            },
            'ph_suelo': {
                'rango': (4.0, 9.0),
                'precision': 0.1,
                'frecuencia': 30,
                'unidad': 'pH'
            }
        }
        
        # Estaciones IoT en Quillota
        self.estaciones_iot = {
            'estacion_central': {
                'id': 'IOT_001',
                'nombre': 'Estacion Central Quillota',
                'coordenadas': {'lat': -32.8833, 'lon': -71.25},
                'elevacion': 120,
                'sensores': ['temperatura', 'humedad', 'presion', 'viento_velocidad', 'viento_direccion', 'radiacion_solar']
            },
            'estacion_norte': {
                'id': 'IOT_002',
                'nombre': 'Estacion Norte Quillota',
                'coordenadas': {'lat': -32.85, 'lon': -71.20},
                'elevacion': 150,
                'sensores': ['temperatura', 'humedad', 'precipitacion', 'suelo_humedad', 'suelo_temperatura']
            },
            'estacion_sur': {
                'id': 'IOT_003',
                'nombre': 'Estacion Sur Quillota',
                'coordenadas': {'lat': -32.92, 'lon': -71.30},
                'elevacion': 100,
                'sensores': ['temperatura', 'humedad', 'presion', 'viento_velocidad', 'ph_suelo']
            },
            'estacion_este': {
                'id': 'IOT_004',
                'nombre': 'Estacion Este Quillota',
                'coordenadas': {'lat': -32.88, 'lon': -71.15},
                'elevacion': 200,
                'sensores': ['temperatura', 'humedad', 'radiacion_solar', 'precipitacion', 'suelo_humedad']
            }
        }
    
    def simular_datos_sensor(self, sensor: str, estacion: str) -> Dict[str, Any]:
        """Simular datos de un sensor especifico"""
        try:
            config = self.sensores_config[sensor]
            estacion_info = self.estaciones_iot[estacion]
            
            # Generar valor simulado con variacion realista
            valor_base = random.uniform(*config['rango'])
            
            # Aplicar variacion temporal (dia/noche, estacional)
            hora_actual = datetime.now().hour
            if sensor in ['temperatura', 'suelo_temperatura']:
                # Temperatura mas baja en la noche
                variacion_temporal = -5 * np.sin((hora_actual - 6) * np.pi / 12)
                valor_base += variacion_temporal
            
            if sensor == 'radiacion_solar':
                # Radiacion solar solo durante el dia
                if 6 <= hora_actual <= 18:
                    valor_base = random.uniform(200, 1000)
                else:
                    valor_base = random.uniform(0, 50)
            
            # Aplicar precision
            valor = round(valor_base, 1) if config['precision'] < 1 else int(valor_base)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'estacion_id': estacion_info['id'],
                'estacion_nombre': estacion_info['nombre'],
                'sensor': sensor,
                'valor': valor,
                'unidad': config['unidad'],
                'coordenadas': estacion_info['coordenadas'],
                'elevacion': estacion_info['elevacion'],
                'calidad': random.choice(['excelente', 'buena', 'regular']),
                'bateria': random.randint(20, 100),
                'senal': random.randint(60, 100)
            }
            
        except Exception as e:
            self.logger.error(f"Error simulando sensor {sensor}: {e}")
            return None
    
    def iniciar_simulacion_iot(self):
        """Iniciar simulacion de sensores IoT"""
        try:
            self.simulacion_activa = True
            self.logger.info("Iniciando simulacion de sensores IoT")
            
            def simular_estacion(estacion_id):
                while self.simulacion_activa:
                    estacion_info = self.estaciones_iot[estacion_id]
                    
                    for sensor in estacion_info['sensores']:
                        datos = self.simular_datos_sensor(sensor, estacion_id)
                        if datos:
                            self.datos_sensores.put(datos)
                    
                    # Esperar antes de la siguiente lectura
                    time.sleep(5)
            
            # Crear hilos para cada estacion
            for estacion_id in self.estaciones_iot.keys():
                thread = threading.Thread(target=simular_estacion, args=(estacion_id,))
                thread.daemon = True
                thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando simulacion IoT: {e}")
            return False
    
    def detener_simulacion_iot(self):
        """Detener simulacion de sensores IoT"""
        self.simulacion_activa = False
        self.logger.info("Simulacion IoT detenida")
    
    def obtener_datos_iot(self, limite=100) -> List[Dict[str, Any]]:
        """Obtener datos de sensores IoT"""
        try:
            datos = []
            contador = 0
            
            while not self.datos_sensores.empty() and contador < limite:
                dato = self.datos_sensores.get_nowait()
                datos.append(dato)
                contador += 1
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos IoT: {e}")
            return []
    
    def obtener_estadisticas_iot(self) -> Dict[str, Any]:
        """Obtener estadisticas de sensores IoT"""
        try:
            datos = self.obtener_datos_iot(1000)
            
            if not datos:
                return {'error': 'No hay datos disponibles'}
            
            df = pd.DataFrame(datos)
            
            estadisticas = {
                'total_lecturas': len(df),
                'estaciones_activas': df['estacion_id'].nunique(),
                'sensores_activos': df['sensor'].nunique(),
                'ultima_lectura': df['timestamp'].max(),
                'estaciones': {}
            }
            
            for estacion in df['estacion_id'].unique():
                datos_estacion = df[df['estacion_id'] == estacion]
                estadisticas['estaciones'][estacion] = {
                    'lecturas': len(datos_estacion),
                    'sensores': datos_estacion['sensor'].nunique(),
                    'bateria_promedio': datos_estacion['bateria'].mean(),
                    'senal_promedio': datos_estacion['senal'].mean()
                }
            
            return estadisticas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadisticas IoT: {e}")
            return {'error': str(e)}

class ConectorDatosSatelitales:
    """Conector para datos satelitales del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('SATELITAL_CONNECTOR')
        self.directorio_imagenes = Path('data/satelitales/imagenes')
        self.directorio_metadatos = Path('data/satelitales/metadatos')
        
        # Crear directorios
        self.directorio_imagenes.mkdir(parents=True, exist_ok=True)
        self.directorio_metadatos.mkdir(parents=True, exist_ok=True)
        
        # Configuracion de satelites
        self.satelites_config = {
            'landsat_8': {
                'nombre': 'Landsat 8',
                'resolucion': '30m',
                'bandas': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11'],
                'frecuencia': 16,  # dias
                'cobertura': 'global'
            },
            'sentinel_2': {
                'nombre': 'Sentinel-2',
                'resolucion': '10m',
                'bandas': ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'],
                'frecuencia': 5,  # dias
                'cobertura': 'global'
            },
            'modis': {
                'nombre': 'MODIS',
                'resolucion': '250m-1000m',
                'bandas': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
                'frecuencia': 1,  # dia
                'cobertura': 'global'
            }
        }
        
        # Area de interes - Quillota
        self.area_interes = {
            'nombre': 'Quillota, Chile',
            'coordenadas': {
                'norte': -32.7,
                'sur': -33.1,
                'este': -71.0,
                'oeste': -71.4
            },
            'centro': {'lat': -32.8833, 'lon': -71.25}
        }
    
    def simular_imagen_satelital(self, satelite: str, fecha: datetime = None) -> Dict[str, Any]:
        """Simular imagen satelital"""
        try:
            if fecha is None:
                fecha = datetime.now()
            
            config = self.satelites_config[satelite]
            
            # Generar imagen sintetica
            if config['resolucion'] == '10m':
                tamaño = (100, 100)
            elif config['resolucion'] == '30m':
                tamaño = (50, 50)
            else:
                tamaño = (25, 25)
            
            # Crear imagen RGB sintetica
            imagen_rgb = np.random.randint(0, 255, (*tamaño, 3), dtype=np.uint8)
            
            # Aplicar patrones realistas (vegetacion, suelo, agua)
            for i in range(tamaño[0]):
                for j in range(tamaño[1]):
                    # Simular vegetacion (verde)
                    if random.random() < 0.3:
                        imagen_rgb[i, j] = [random.randint(50, 150), random.randint(100, 200), random.randint(30, 100)]
                    # Simular suelo (marron)
                    elif random.random() < 0.5:
                        imagen_rgb[i, j] = [random.randint(100, 180), random.randint(80, 150), random.randint(40, 120)]
                    # Simular agua (azul)
                    elif random.random() < 0.1:
                        imagen_rgb[i, j] = [random.randint(20, 80), random.randint(50, 120), random.randint(150, 255)]
            
            # Guardar imagen
            nombre_archivo = f"{satelite}_{fecha.strftime('%Y%m%d_%H%M%S')}.png"
            ruta_imagen = self.directorio_imagenes / nombre_archivo
            
            if PIL_AVAILABLE:
                imagen_pil = Image.fromarray(imagen_rgb)
                imagen_pil.save(ruta_imagen)
            else:
                # Guardar como archivo de texto si PIL no esta disponible
                with open(ruta_imagen.with_suffix('.txt'), 'w') as f:
                    f.write(f"Imagen satelital simulada: {satelite}\n")
                    f.write(f"Tamaño: {tamaño}\n")
                    f.write(f"Fecha: {fecha.isoformat()}\n")
            
            # Crear metadatos
            metadatos = {
                'archivo': nombre_archivo,
                'ruta': str(ruta_imagen),
                'satelite': satelite,
                'fecha_adquisicion': fecha.isoformat(),
                'resolucion': config['resolucion'],
                'tamaño': tamaño,
                'bandas': config['bandas'],
                'area_interes': self.area_interes,
                'procesado': False,
                'indices_calculados': [],
                'timestamp_procesamiento': datetime.now().isoformat()
            }
            
            # Guardar metadatos
            nombre_metadatos = f"{satelite}_{fecha.strftime('%Y%m%d_%H%M%S')}_metadata.json"
            ruta_metadatos = self.directorio_metadatos / nombre_metadatos
            
            with open(ruta_metadatos, 'w', encoding='utf-8') as f:
                json.dump(metadatos, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Imagen satelital simulada: {nombre_archivo}")
            return metadatos
            
        except Exception as e:
            self.logger.error(f"Error simulando imagen satelital: {e}")
            return None
    
    def procesar_imagen_satelital(self, ruta_imagen: str) -> Dict[str, Any]:
        """Procesar imagen satelital para extraer indices"""
        try:
            if not CV2_AVAILABLE:
                return {'error': 'OpenCV no disponible', 'procesado': False}
            
            # Cargar imagen
            imagen = cv2.imread(ruta_imagen)
            if imagen is None:
                return {'error': 'No se pudo cargar la imagen'}
            
            # Convertir a RGB
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            
            # Calcular indices espectrales
            r = imagen_rgb[:, :, 0].astype(np.float32)
            g = imagen_rgb[:, :, 1].astype(np.float32)
            b = imagen_rgb[:, :, 2].astype(np.float32)
            
            # NDVI (Normalized Difference Vegetation Index)
            ndvi = np.where((r + b) != 0, (r - b) / (r + b), 0)
            
            # GNDVI (Green Normalized Difference Vegetation Index)
            gndvi = np.where((g + b) != 0, (g - b) / (g + b), 0)
            
            # SAVI (Soil Adjusted Vegetation Index)
            savi = np.where((r + b + 0.5) != 0, (r - b) / (r + b + 0.5) * 1.5, 0)
            
            # EVI (Enhanced Vegetation Index)
            evi = np.where((r + 6*b - 7.5*g + 1) != 0, 2.5 * (r - b) / (r + 6*b - 7.5*g + 1), 0)
            
            # Calcular estadisticas
            indices = {
                'ndvi': {
                    'media': float(np.mean(ndvi)),
                    'desviacion': float(np.std(ndvi)),
                    'min': float(np.min(ndvi)),
                    'max': float(np.max(ndvi))
                },
                'gndvi': {
                    'media': float(np.mean(gndvi)),
                    'desviacion': float(np.std(gndvi)),
                    'min': float(np.min(gndvi)),
                    'max': float(np.max(gndvi))
                },
                'savi': {
                    'media': float(np.mean(savi)),
                    'desviacion': float(np.std(savi)),
                    'min': float(np.min(savi)),
                    'max': float(np.max(savi))
                },
                'evi': {
                    'media': float(np.mean(evi)),
                    'desviacion': float(np.std(evi)),
                    'min': float(np.min(evi)),
                    'max': float(np.max(evi))
                }
            }
            
            return {
                'procesado': True,
                'indices': indices,
                'timestamp_procesamiento': datetime.now().isoformat(),
                'resumen': {
                    'vegetacion_saludable': float(np.mean(ndvi > 0.3)),
                    'vegetacion_moderada': float(np.mean((ndvi > 0.1) & (ndvi <= 0.3))),
                    'vegetacion_baja': float(np.mean(ndvi <= 0.1))
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando imagen satelital: {e}")
            return {'error': str(e)}
    
    def obtener_imagenes_disponibles(self) -> List[Dict[str, Any]]:
        """Obtener lista de imagenes satelitales disponibles"""
        try:
            imagenes = []
            
            for archivo in self.directorio_imagenes.glob('*.png'):
                # Buscar metadatos correspondientes
                nombre_base = archivo.stem
                metadatos_archivo = self.directorio_metadatos / f"{nombre_base}_metadata.json"
                
                if metadatos_archivo.exists():
                    with open(metadatos_archivo, 'r', encoding='utf-8') as f:
                        metadatos = json.load(f)
                    imagenes.append(metadatos)
                else:
                    # Crear metadatos basicos
                    imagenes.append({
                        'archivo': archivo.name,
                        'ruta': str(archivo),
                        'satelite': 'desconocido',
                        'fecha_adquisicion': datetime.fromtimestamp(archivo.stat().st_mtime).isoformat(),
                        'procesado': False
                    })
            
            return sorted(imagenes, key=lambda x: x['fecha_adquisicion'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo imagenes disponibles: {e}")
            return []
    
    def generar_imagenes_satelitales(self, dias=7):
        """Generar imagenes satelitales simuladas para los ultimos dias"""
        try:
            imagenes_generadas = []
            
            for i in range(dias):
                fecha = datetime.now() - timedelta(days=i)
                
                # Generar imagen para cada satelite
                for satelite in self.satelites_config.keys():
                    metadatos = self.simular_imagen_satelital(satelite, fecha)
                    if metadatos:
                        imagenes_generadas.append(metadatos)
            
            self.logger.info(f"Generadas {len(imagenes_generadas)} imagenes satelitales")
            return imagenes_generadas
            
        except Exception as e:
            self.logger.error(f"Error generando imagenes satelitales: {e}")
            return []

def main():
    """Funcion principal para probar conectores IoT y Satelitales"""
    print("CONECTORES IOT Y SATELITALES - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Probar conector IoT
        print("\n1. Probando Conector IoT...")
        conector_iot = ConectorSensoresIoT()
        
        # Iniciar simulacion
        conector_iot.iniciar_simulacion_iot()
        time.sleep(10)  # Esperar datos
        
        # Obtener datos
        datos_iot = conector_iot.obtener_datos_iot(50)
        print(f"   Datos IoT obtenidos: {len(datos_iot)} registros")
        
        # Obtener estadisticas
        stats_iot = conector_iot.obtener_estadisticas_iot()
        print(f"   Estaciones activas: {stats_iot.get('estaciones_activas', 0)}")
        print(f"   Sensores activos: {stats_iot.get('sensores_activos', 0)}")
        
        # Detener simulacion
        conector_iot.detener_simulacion_iot()
        
        # Probar conector Satelital
        print("\n2. Probando Conector Satelital...")
        conector_satelital = ConectorDatosSatelitales()
        
        # Generar imagenes
        imagenes = conector_satelital.generar_imagenes_satelitales(3)
        print(f"   Imagenes generadas: {len(imagenes)}")
        
        # Obtener imagenes disponibles
        imagenes_disponibles = conector_satelital.obtener_imagenes_disponibles()
        print(f"   Imagenes disponibles: {len(imagenes_disponibles)}")
        
        # Procesar una imagen
        if imagenes_disponibles:
            primera_imagen = imagenes_disponibles[0]
            resultado_procesamiento = conector_satelital.procesar_imagen_satelital(primera_imagen['ruta'])
            print(f"   Imagen procesada: {resultado_procesamiento.get('procesado', False)}")
        
        print("\nConectores IoT y Satelitales probados exitosamente")
        return True
        
    except Exception as e:
        print(f"\nError probando conectores: {e}")
        return False

if __name__ == "__main__":
    main()
