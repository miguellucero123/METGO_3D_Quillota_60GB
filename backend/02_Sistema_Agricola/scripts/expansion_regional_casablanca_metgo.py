"""
SISTEMA DE EXPANSIÓN REGIONAL CASABLANCA - METGO 3D QUILLOTA
Sistema especializado para viñedos de uva blanca en el Valle de Casablanca
Incluye: Estaciones meteorológicas costeras, análisis de brisas marinas, 
         recomendaciones específicas para uva blanca y gestión de riesgos costeros
"""

import pandas as pd
import numpy as np
import json
import logging
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import os
import uuid
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class ExpansionRegionalCasablancaMetgo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "expansion_casablanca_metgo.db"
        self.directorio_datos = "datos_casablanca"
        self.directorio_reportes = "reportes_casablanca"
        self.directorio_modelos = "modelos_casablanca"
        
        # Crear directorios necesarios
        self._crear_directorios()
        
        # Inicializar base de datos
        self._inicializar_base_datos()
        
        # Configuración específica de Casablanca
        self.configuracion_casablanca = {
            'region': 'Valle de Casablanca',
            'provincia': 'Valparaíso',
            'comuna': 'Casablanca',
            'tipo_clima': 'Mediterráneo con influencia costera',
            'cultivo_principal': 'Uva blanca para vino',
            'variedades_principales': [
                'Chardonnay', 'Sauvignon Blanc', 'Pinot Grigio', 
                'Viognier', 'Riesling', 'Gewürztraminer'
            ],
            'caracteristicas_climaticas': {
                'brisas_marinas': True,
                'humedad_relativa_alta': True,
                'amplitud_termica_moderada': True,
                'vientos_constantes': True,
                'influencia_pacifico': True
            }
        }
        
        # Estaciones meteorológicas específicas de Casablanca
        self.estaciones_casablanca = {
            'casablanca_centro': {
                'nombre': 'Casablanca Centro',
                'latitud': -33.3167,
                'longitud': -71.4167,
                'altitud': 230,
                'tipo': 'Estación principal',
                'cultivo': 'Uva blanca - Chardonnay',
                'caracteristicas': 'Zona central del valle',
                'influencia_marina': 'Media'
            },
            'collihuay': {
                'nombre': 'Collihuay',
                'latitud': -33.2833,
                'longitud': -71.4500,
                'altitud': 180,
                'tipo': 'Zona costera',
                'cultivo': 'Uva blanca - Sauvignon Blanc',
                'caracteristicas': 'Fuerte influencia marina',
                'influencia_marina': 'Alta'
            },
            'lagunillas': {
                'nombre': 'Lagunillas',
                'latitud': -33.3500,
                'longitud': -71.3833,
                'altitud': 280,
                'tipo': 'Zona interior',
                'cultivo': 'Uva blanca - Pinot Grigio',
                'caracteristicas': 'Menor influencia marina',
                'influencia_marina': 'Baja'
            },
            'algarrobo': {
                'nombre': 'Algarrobo',
                'latitud': -33.3667,
                'longitud': -71.6667,
                'altitud': 15,
                'tipo': 'Zona costera extrema',
                'cultivo': 'Uva blanca - Riesling',
                'caracteristicas': 'Máxima influencia marina',
                'influencia_marina': 'Muy Alta'
            },
            'curacavi': {
                'nombre': 'Curacaví',
                'latitud': -33.4167,
                'longitud': -71.1333,
                'altitud': 320,
                'tipo': 'Zona interior alta',
                'cultivo': 'Uva blanca - Viognier',
                'caracteristicas': 'Alta altitud, continental',
                'influencia_marina': 'Muy Baja'
            }
        }
        
        # Configuración específica para uva blanca
        self.configuracion_uva_blanca = {
            'fases_fenologicas': {
                'reposo_invernal': {'meses': [6, 7, 8], 'temperatura_optima': [0, 10]},
                'brotacion': {'meses': [9], 'temperatura_optima': [10, 15]},
                'floracion': {'meses': [11, 12], 'temperatura_optima': [15, 25]},
                'cuajado': {'meses': [1], 'temperatura_optima': [18, 28]},
                'desarrollo': {'meses': [2, 3], 'temperatura_optima': [20, 30]},
                'madurez': {'meses': [4, 5], 'temperatura_optima': [18, 25]},
                'cosecha': {'meses': [4, 5], 'temperatura_optima': [15, 22]}
            },
            'requerimientos_climaticos': {
                'temperatura_minima_invierno': -5,  # °C
                'temperatura_maxima_verano': 35,    # °C
                'humedad_optima': [60, 80],         # %
                'precipitacion_anual': [400, 800],  # mm
                'horas_frio': [400, 800],           # horas < 7°C
                'horas_sol': [2500, 3000]           # horas/año
            },
            'riesgos_especificos': {
                'heladas_tardias': {'periodo': 'Sep-Oct', 'riesgo': 'Alto'},
                'exceso_humedad': {'periodo': 'Nov-Ene', 'riesgo': 'Medio'},
                'vientos_fuertes': {'periodo': 'Todo el año', 'riesgo': 'Medio'},
                'estres_hidrico': {'periodo': 'Dic-Mar', 'riesgo': 'Bajo'},
                'enfermedades_fungicas': {'periodo': 'Nov-Feb', 'riesgo': 'Alto'}
            },
            'recomendaciones_especificas': {
                'manejo_canopia': 'Controlar vigor para evitar sombreado excesivo',
                'riego': 'Riego deficitario controlado en post-cuajado',
                'fertilizacion': 'Nitrógeno moderado, potasio alto',
                'proteccion_heladas': 'Sistemas de calefacción o aspersión',
                'control_enfermedades': 'Tratamientos preventivos con cobre'
            }
        }
        
        # Parámetros de brisas marinas
        self.parametros_brisas_marinas = {
            'velocidad_brisa_optima': [8, 15],      # km/h
            'direccion_brisa_optima': [180, 270],   # grados (S-SO)
            'humedad_brisa': [75, 90],              # %
            'temperatura_diferencial': [-3, -8],    # °C vs interior
            'frecuencia_brisa': [60, 80],           # % de días con brisa
            'intensidad_por_estacion': {
                'verano': 'Alta',
                'otoño': 'Media',
                'invierno': 'Baja',
                'primavera': 'Media-Alta'
            }
        }
        
        self.logger.info("Sistema de Expansión Regional Casablanca inicializado")
    
    def _crear_directorios(self):
        """Crear directorios necesarios para el sistema"""
        try:
            directorios = [
                self.directorio_datos,
                self.directorio_reportes,
                self.directorio_modelos,
                f"{self.directorio_datos}/meteorologicos",
                f"{self.directorio_datos}/fenologicos",
                f"{self.directorio_datos}/brisas_marinas",
                f"{self.directorio_reportes}/analisis_vinedos",
                f"{self.directorio_reportes}/recomendaciones",
                f"{self.directorio_reportes}/tendencias_climaticas",
                f"{self.directorio_modelos}/predicciones",
                f"{self.directorio_modelos}/clasificacion"
            ]
            
            for directorio in directorios:
                os.makedirs(directorio, exist_ok=True)
                
            print("[OK] Directorios del sistema Casablanca creados")
            
        except Exception as e:
            print(f"[ERROR] Error creando directorios: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para Casablanca"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de estaciones meteorológicas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estaciones_casablanca (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    latitud REAL NOT NULL,
                    longitud REAL NOT NULL,
                    altitud REAL NOT NULL,
                    tipo TEXT NOT NULL,
                    cultivo TEXT NOT NULL,
                    caracteristicas TEXT,
                    influencia_marina TEXT,
                    activa BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de datos meteorológicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_meteorologicos_casablanca (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    fecha DATETIME NOT NULL,
                    temperatura_max REAL,
                    temperatura_min REAL,
                    temperatura_promedio REAL,
                    humedad_relativa REAL,
                    precipitacion REAL,
                    velocidad_viento REAL,
                    direccion_viento REAL,
                    presion_atmosferica REAL,
                    radiacion_solar REAL,
                    temperatura_mar REAL,
                    humedad_marina REAL,
                    velocidad_brisa REAL,
                    direccion_brisa REAL,
                    intensidad_brisa TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_casablanca (estacion_id)
                )
            ''')
            
            # Tabla de análisis fenológicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analisis_fenologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    fecha_analisis DATETIME NOT NULL,
                    fase_fenologica TEXT NOT NULL,
                    porcentaje_avance REAL,
                    temperatura_acumulada REAL,
                    horas_frio_acumuladas REAL,
                    grado_dias_crecimiento REAL,
                    riesgo_helada REAL,
                    riesgo_estres_hidrico REAL,
                    recomendacion TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_casablanca (estacion_id)
                )
            ''')
            
            # Tabla de análisis de brisas marinas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analisis_brisas_marinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    fecha_analisis DATETIME NOT NULL,
                    velocidad_brisa_promedio REAL,
                    direccion_brisa_dominante REAL,
                    frecuencia_brisa REAL,
                    intensidad_brisa TEXT,
                    temperatura_diferencial REAL,
                    humedad_diferencial REAL,
                    efecto_refrescante REAL,
                    beneficio_uvas REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_casablanca (estacion_id)
                )
            ''')
            
            # Tabla de recomendaciones específicas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recomendaciones_casablanca (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    fecha_recomendacion DATETIME NOT NULL,
                    tipo_recomendacion TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    prioridad TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    accion_requerida TEXT,
                    plazo_ejecucion TEXT,
                    parametros_climaticos TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_casablanca (estacion_id)
                )
            ''')
            
            # Tabla de predicciones específicas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones_casablanca (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion_id TEXT NOT NULL,
                    fecha_prediccion DATETIME NOT NULL,
                    horizonte_prediccion INTEGER NOT NULL,
                    tipo_prediccion TEXT NOT NULL,
                    valor_predicho REAL,
                    confianza REAL,
                    parametros_entrada TEXT,
                    modelo_utilizado TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (estacion_id) REFERENCES estaciones_casablanca (estacion_id)
                )
            ''')
            
            # Insertar estaciones de Casablanca
            for estacion_id, datos in self.estaciones_casablanca.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO estaciones_casablanca 
                    (estacion_id, nombre, latitud, longitud, altitud, tipo, cultivo, caracteristicas, influencia_marina)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    estacion_id, datos['nombre'], datos['latitud'], datos['longitud'],
                    datos['altitud'], datos['tipo'], datos['cultivo'], 
                    datos['caracteristicas'], datos['influencia_marina']
                ))
            
            conn.commit()
            conn.close()
            
            print("[OK] Base de datos de Casablanca inicializada")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {e}")
    
    def generar_datos_casablanca(self, dias: int = 365) -> Dict:
        """Generar datos meteorológicos específicos para Casablanca con brisas marinas"""
        try:
            print(f"[CASABLANCA] Generando datos meteorológicos para {dias} días...")
            
            # Configurar semilla para reproducibilidad
            np.random.seed(42)
            
            # Generar fechas
            fecha_inicio = datetime.now() - timedelta(days=dias)
            fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
            
            datos_totales = []
            
            for estacion_id, config_estacion in self.estaciones_casablanca.items():
                print(f"[ESTACION] Generando datos para {config_estacion['nombre']}...")
                
                datos_estacion = []
                
                for fecha in fechas:
                    # Generar datos base según la estación
                    datos_dia = self._generar_datos_dia_casablanca(
                        fecha, estacion_id, config_estacion
                    )
                    datos_estacion.append(datos_dia)
                
                # Guardar datos de la estación
                self._guardar_datos_estacion(estacion_id, datos_estacion)
                datos_totales.extend(datos_estacion)
                
                print(f"[OK] {len(datos_estacion)} registros generados para {config_estacion['nombre']}")
            
            # Generar análisis fenológicos
            print("[FENOLOGIA] Generando análisis fenológicos...")
            self._generar_analisis_fenologicos(fechas)
            
            # Generar análisis de brisas marinas
            print("[BRISAS] Generando análisis de brisas marinas...")
            self._generar_analisis_brisas_marinas(fechas)
            
            # Generar recomendaciones
            print("[RECOMENDACIONES] Generando recomendaciones específicas...")
            self._generar_recomendaciones_casablanca(fechas)
            
            resultado = {
                'total_registros': len(datos_totales),
                'estaciones_procesadas': len(self.estaciones_casablanca),
                'periodo_datos': f"{fechas[0].strftime('%Y-%m-%d')} a {fechas[-1].strftime('%Y-%m-%d')}",
                'analisis_generados': ['fenologicos', 'brisas_marinas', 'recomendaciones'],
                'estaciones': list(self.estaciones_casablanca.keys())
            }
            
            print(f"[OK] Datos de Casablanca generados: {len(datos_totales)} registros")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error generando datos de Casablanca: {e}")
            return {'error': str(e)}
    
    def _generar_datos_dia_casablanca(self, fecha: datetime, estacion_id: str, config_estacion: Dict) -> Dict:
        """Generar datos meteorológicos para un día específico en Casablanca"""
        try:
            # Parámetros base según influencia marina
            influencia = config_estacion['influencia_marina']
            altitud = config_estacion['altitud']
            mes = fecha.month
            
            # Temperatura base según mes y altitud
            temp_base_mensual = {
                1: 20, 2: 20, 3: 18, 4: 15, 5: 12, 6: 10,
                7: 10, 8: 12, 9: 15, 10: 17, 11: 19, 12: 20
            }
            
            temp_base = temp_base_mensual[mes]
            
            # Ajustar por altitud (-0.6°C por cada 100m)
            temp_base -= (altitud - 100) * 0.006
            
            # Ajustar por influencia marina
            if influencia == 'Muy Alta':
                temp_base -= 2  # Efecto refrescante máximo
                amplitud_termica = 8  # Menor amplitud
            elif influencia == 'Alta':
                temp_base -= 1.5
                amplitud_termica = 10
            elif influencia == 'Media':
                temp_base -= 1
                amplitud_termica = 12
            elif influencia == 'Baja':
                temp_base -= 0.5
                amplitud_termica = 14
            else:  # Muy Baja
                temp_base -= 0.2
                amplitud_termica = 16
            
            # Generar temperaturas
            temp_max = temp_base + amplitud_termica/2 + np.random.normal(0, 2)
            temp_min = temp_base - amplitud_termica/2 + np.random.normal(0, 1.5)
            temp_promedio = (temp_max + temp_min) / 2
            
            # Humedad relativa (mayor con influencia marina)
            if influencia in ['Muy Alta', 'Alta']:
                humedad_base = 85
            elif influencia == 'Media':
                humedad_base = 75
            else:
                humedad_base = 65
            
            humedad_relativa = humedad_base + np.random.normal(0, 10)
            humedad_relativa = np.clip(humedad_relativa, 40, 95)
            
            # Precipitación (patrón mediterráneo)
            prob_lluvia = {
                1: 0.05, 2: 0.03, 3: 0.08, 4: 0.15, 5: 0.25, 6: 0.35,
                7: 0.40, 8: 0.30, 9: 0.20, 10: 0.15, 11: 0.10, 12: 0.08
            }
            
            if np.random.random() < prob_lluvia[mes]:
                precipitacion = np.random.exponential(5) + np.random.normal(0, 2)
                precipitacion = max(0, precipitacion)
            else:
                precipitacion = 0
            
            # Viento y brisas marinas
            if influencia in ['Muy Alta', 'Alta']:
                velocidad_viento = np.random.uniform(12, 25)  # Brisas más fuertes
                direccion_viento = np.random.uniform(180, 270)  # S-SO dominante
            elif influencia == 'Media':
                velocidad_viento = np.random.uniform(8, 18)
                direccion_viento = np.random.uniform(150, 300)
            else:
                velocidad_viento = np.random.uniform(5, 15)
                direccion_viento = np.random.uniform(0, 360)
            
            # Parámetros de brisa marina
            temperatura_mar = 16 + 4 * np.sin(2 * np.pi * (mes - 2) / 12)  # Temperatura del mar
            humedad_marina = 90 + np.random.normal(0, 5)
            
            velocidad_brisa = velocidad_viento if influencia in ['Muy Alta', 'Alta'] else velocidad_viento * 0.7
            direccion_brisa = direccion_viento
            
            # Clasificar intensidad de brisa
            if velocidad_brisa > 20:
                intensidad_brisa = 'Muy Fuerte'
            elif velocidad_brisa > 15:
                intensidad_brisa = 'Fuerte'
            elif velocidad_brisa > 10:
                intensidad_brisa = 'Moderada'
            elif velocidad_brisa > 5:
                intensidad_brisa = 'Suave'
            else:
                intensidad_brisa = 'Muy Suave'
            
            # Presión atmosférica
            presion_base = 1013.25 - (altitud * 0.12)
            presion_atmosferica = presion_base + np.random.normal(0, 5)
            
            # Radiación solar
            radiacion_base = 800 - (precipitacion * 20) - (humedad_relativa * 2)
            radiacion_solar = max(0, radiacion_base + np.random.normal(0, 100))
            
            return {
                'estacion_id': estacion_id,
                'fecha': fecha,
                'temperatura_max': round(temp_max, 1),
                'temperatura_min': round(temp_min, 1),
                'temperatura_promedio': round(temp_promedio, 1),
                'humedad_relativa': round(humedad_relativa, 1),
                'precipitacion': round(precipitacion, 1),
                'velocidad_viento': round(velocidad_viento, 1),
                'direccion_viento': round(direccion_viento, 1),
                'presion_atmosferica': round(presion_atmosferica, 1),
                'radiacion_solar': round(radiacion_solar, 1),
                'temperatura_mar': round(temperatura_mar, 1),
                'humedad_marina': round(humedad_marina, 1),
                'velocidad_brisa': round(velocidad_brisa, 1),
                'direccion_brisa': round(direccion_brisa, 1),
                'intensidad_brisa': intensidad_brisa
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando datos del día: {e}")
            return {}
    
    def _guardar_datos_estacion(self, estacion_id: str, datos: List[Dict]):
        """Guardar datos de una estación en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            for dato in datos:
                cursor.execute('''
                    INSERT INTO datos_meteorologicos_casablanca 
                    (estacion_id, fecha, temperatura_max, temperatura_min, temperatura_promedio,
                     humedad_relativa, precipitacion, velocidad_viento, direccion_viento,
                     presion_atmosferica, radiacion_solar, temperatura_mar, humedad_marina,
                     velocidad_brisa, direccion_brisa, intensidad_brisa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dato['estacion_id'], dato['fecha'], dato['temperatura_max'],
                    dato['temperatura_min'], dato['temperatura_promedio'],
                    dato['humedad_relativa'], dato['precipitacion'], dato['velocidad_viento'],
                    dato['direccion_viento'], dato['presion_atmosferica'], dato['radiacion_solar'],
                    dato['temperatura_mar'], dato['humedad_marina'], dato['velocidad_brisa'],
                    dato['direccion_brisa'], dato['intensidad_brisa']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando datos de estación: {e}")
    
    def _generar_analisis_fenologicos(self, fechas: pd.DatetimeIndex):
        """Generar análisis fenológicos para uva blanca"""
        try:
            for estacion_id in self.estaciones_casablanca.keys():
                for fecha in fechas:
                    # Determinar fase fenológica según el mes
                    fase_fenologica = self._determinar_fase_fenologica(fecha.month)
                    
                    # Calcular parámetros fenológicos
                    analisis = self._calcular_parametros_fenologicos(
                        estacion_id, fecha, fase_fenologica
                    )
                    
                    # Guardar análisis
                    self._guardar_analisis_fenologico(estacion_id, fecha, analisis)
            
            print("[OK] Análisis fenológicos generados")
            
        except Exception as e:
            print(f"[ERROR] Error generando análisis fenológicos: {e}")
    
    def _determinar_fase_fenologica(self, mes: int) -> str:
        """Determinar fase fenológica según el mes"""
        fases = self.configuracion_uva_blanca['fases_fenologicas']
        
        for fase, config in fases.items():
            if mes in config['meses']:
                return fase
        
        return 'reposo_invernal'  # Default
    
    def _calcular_parametros_fenologicos(self, estacion_id: str, fecha: datetime, fase: str) -> Dict:
        """Calcular parámetros fenológicos específicos"""
        try:
            # Obtener datos meteorológicos del día
            datos_meteo = self._obtener_datos_meteo_dia(estacion_id, fecha)
            
            if not datos_meteo:
                return {}
            
            # Calcular temperatura acumulada (desde inicio de ciclo)
            temperatura_acumulada = self._calcular_temperatura_acumulada(estacion_id, fecha)
            
            # Calcular horas de frío acumuladas
            horas_frio = self._calcular_horas_frio_acumuladas(estacion_id, fecha)
            
            # Calcular grados-día de crecimiento
            grado_dias = self._calcular_grado_dias_crecimiento(estacion_id, fecha)
            
            # Calcular porcentaje de avance en la fase
            porcentaje_avance = self._calcular_porcentaje_avance_fase(fase, fecha, datos_meteo)
            
            # Calcular riesgos
            riesgo_helada = self._calcular_riesgo_helada(datos_meteo, fase)
            riesgo_estres_hidrico = self._calcular_riesgo_estres_hidrico(datos_meteo, fase)
            
            # Generar recomendación
            recomendacion = self._generar_recomendacion_fenologica(
                fase, porcentaje_avance, riesgo_helada, riesgo_estres_hidrico
            )
            
            return {
                'fase_fenologica': fase,
                'porcentaje_avance': round(porcentaje_avance, 1),
                'temperatura_acumulada': round(temperatura_acumulada, 1),
                'horas_frio_acumuladas': round(horas_frio, 1),
                'grado_dias_crecimiento': round(grado_dias, 1),
                'riesgo_helada': round(riesgo_helada, 1),
                'riesgo_estres_hidrico': round(riesgo_estres_hidrico, 1),
                'recomendacion': recomendacion
            }
            
        except Exception as e:
            print(f"[ERROR] Error calculando parámetros fenológicos: {e}")
            return {}
    
    def _obtener_datos_meteo_dia(self, estacion_id: str, fecha: datetime) -> Optional[Dict]:
        """Obtener datos meteorológicos de un día específico"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM datos_meteorologicos_casablanca 
                WHERE estacion_id = ? AND DATE(fecha) = DATE(?)
            ''', (estacion_id, fecha.strftime('%Y-%m-%d')))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'temperatura_max': row[3],
                    'temperatura_min': row[4],
                    'temperatura_promedio': row[5],
                    'humedad_relativa': row[6],
                    'precipitacion': row[7],
                    'velocidad_viento': row[8],
                    'presion_atmosferica': row[10]
                }
            return None
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo datos meteorológicos: {e}")
            return None
    
    def _calcular_temperatura_acumulada(self, estacion_id: str, fecha: datetime) -> float:
        """Calcular temperatura acumulada desde inicio del ciclo"""
        try:
            # Simular cálculo de temperatura acumulada
            # En implementación real, se sumarían las temperaturas desde inicio del ciclo
            dias_desde_inicio = (fecha - datetime(fecha.year, 6, 1)).days
            return max(0, dias_desde_inicio * np.random.uniform(15, 25))
            
        except Exception as e:
            print(f"[ERROR] Error calculando temperatura acumulada: {e}")
            return 0.0
    
    def _calcular_horas_frio_acumuladas(self, estacion_id: str, fecha: datetime) -> float:
        """Calcular horas de frío acumuladas"""
        try:
            # Simular cálculo de horas de frío
            # En implementación real, se contarían horas < 7°C
            dias_invierno = (fecha - datetime(fecha.year, 6, 1)).days
            return max(0, dias_invierno * np.random.uniform(8, 12))
            
        except Exception as e:
            print(f"[ERROR] Error calculando horas de frío: {e}")
            return 0.0
    
    def _calcular_grado_dias_crecimiento(self, estacion_id: str, fecha: datetime) -> float:
        """Calcular grados-día de crecimiento"""
        try:
            datos_meteo = self._obtener_datos_meteo_dia(estacion_id, fecha)
            if not datos_meteo:
                return 0.0
            
            temp_base = 10  # Temperatura base para uva
            temp_promedio = datos_meteo['temperatura_promedio']
            
            if temp_promedio > temp_base:
                return temp_promedio - temp_base
            else:
                return 0.0
                
        except Exception as e:
            print(f"[ERROR] Error calculando grados-día: {e}")
            return 0.0
    
    def _calcular_porcentaje_avance_fase(self, fase: str, fecha: datetime, datos_meteo: Dict) -> float:
        """Calcular porcentaje de avance en la fase fenológica actual"""
        try:
            config_fase = self.configuracion_uva_blanca['fases_fenologicas'].get(fase, {})
            meses = config_fase.get('meses', [])
            
            if not meses:
                return 0.0
            
            # Calcular avance basado en el mes y condiciones meteorológicas
            mes_actual = fecha.month
            mes_inicio = min(meses)
            mes_fin = max(meses)
            
            if mes_actual < mes_inicio:
                return 0.0
            elif mes_actual > mes_fin:
                return 100.0
            else:
                # Avance proporcional dentro del rango
                rango_total = mes_fin - mes_inicio + 1
                posicion_actual = mes_actual - mes_inicio + 1
                avance_base = (posicion_actual / rango_total) * 100
                
                # Ajustar según condiciones meteorológicas
                temp_ajuste = (datos_meteo['temperatura_promedio'] - 15) * 2
                avance_ajustado = avance_base + temp_ajuste
                
                return np.clip(avance_ajustado, 0, 100)
                
        except Exception as e:
            print(f"[ERROR] Error calculando porcentaje de avance: {e}")
            return 0.0
    
    def _calcular_riesgo_helada(self, datos_meteo: Dict, fase: str) -> float:
        """Calcular riesgo de helada"""
        try:
            temp_min = datos_meteo['temperatura_min']
            
            # Riesgo base según temperatura mínima
            if temp_min < -2:
                riesgo_base = 90
            elif temp_min < 0:
                riesgo_base = 70
            elif temp_min < 2:
                riesgo_base = 40
            elif temp_min < 5:
                riesgo_base = 20
            else:
                riesgo_base = 5
            
            # Ajustar según fase fenológica
            if fase in ['brotacion', 'floracion']:
                riesgo_base *= 1.5  # Mayor riesgo en fases sensibles
            elif fase == 'cuajado':
                riesgo_base *= 1.3
            
            return min(100, riesgo_base)
            
        except Exception as e:
            print(f"[ERROR] Error calculando riesgo de helada: {e}")
            return 0.0
    
    def _calcular_riesgo_estres_hidrico(self, datos_meteo: Dict, fase: str) -> float:
        """Calcular riesgo de estrés hídrico"""
        try:
            temp_max = datos_meteo['temperatura_max']
            humedad = datos_meteo['humedad_relativa']
            precipitacion = datos_meteo['precipitacion']
            
            # Riesgo base según temperatura y humedad
            riesgo_temp = max(0, (temp_max - 25) * 3)  # Riesgo por temperatura alta
            riesgo_humedad = max(0, (60 - humedad) * 0.5)  # Riesgo por humedad baja
            riesgo_lluvia = max(0, (5 - precipitacion) * 2)  # Riesgo por falta de lluvia
            
            riesgo_total = riesgo_temp + riesgo_humedad + riesgo_lluvia
            
            # Ajustar según fase fenológica
            if fase in ['desarrollo', 'madurez']:
                riesgo_total *= 1.2  # Mayor sensibilidad en desarrollo
            
            return min(100, riesgo_total)
            
        except Exception as e:
            print(f"[ERROR] Error calculando riesgo de estrés hídrico: {e}")
            return 0.0
    
    def _generar_recomendacion_fenologica(self, fase: str, porcentaje_avance: float, 
                                        riesgo_helada: float, riesgo_estres: float) -> str:
        """Generar recomendación específica según fase fenológica y riesgos"""
        try:
            recomendaciones = []
            
            # Recomendaciones por fase
            if fase == 'brotacion':
                recomendaciones.append("Iniciar aplicaciones preventivas de cobre")
                recomendaciones.append("Preparar sistemas de protección contra heladas")
            elif fase == 'floracion':
                recomendaciones.append("Evitar tratamientos durante floración")
                recomendaciones.append("Monitorear condiciones para cuajado")
            elif fase == 'cuajado':
                recomendaciones.append("Aplicar fertilizantes foliares")
                recomendaciones.append("Controlar vigor vegetativo")
            elif fase == 'desarrollo':
                recomendaciones.append("Iniciar riego deficitario controlado")
                recomendaciones.append("Aplicar fertilizantes potásicos")
            elif fase == 'madurez':
                recomendaciones.append("Suspender riego para concentración de azúcares")
                recomendaciones.append("Monitorear parámetros de madurez")
            elif fase == 'cosecha':
                recomendaciones.append("Programar cosecha según parámetros óptimos")
                recomendaciones.append("Preparar equipos de cosecha")
            
            # Recomendaciones por riesgos
            if riesgo_helada > 70:
                recomendaciones.append("ACTIVAR SISTEMAS DE PROTECCIÓN CONTRA HELADAS")
            elif riesgo_helada > 40:
                recomendaciones.append("Preparar sistemas de protección")
            
            if riesgo_estres > 60:
                recomendaciones.append("Aumentar frecuencia de riego")
            elif riesgo_estres > 30:
                recomendaciones.append("Monitorear humedad del suelo")
            
            return "; ".join(recomendaciones)
            
        except Exception as e:
            print(f"[ERROR] Error generando recomendación fenológica: {e}")
            return "Consultar con especialista"
    
    def _guardar_analisis_fenologico(self, estacion_id: str, fecha: datetime, analisis: Dict):
        """Guardar análisis fenológico en la base de datos"""
        try:
            if not analisis:
                return
                
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analisis_fenologicos 
                (estacion_id, fecha_analisis, fase_fenologica, porcentaje_avance,
                 temperatura_acumulada, horas_frio_acumuladas, grado_dias_crecimiento,
                 riesgo_helada, riesgo_estres_hidrico, recomendacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estacion_id, fecha, analisis['fase_fenologica'],
                analisis['porcentaje_avance'], analisis['temperatura_acumulada'],
                analisis['horas_frio_acumuladas'], analisis['grado_dias_crecimiento'],
                analisis['riesgo_helada'], analisis['riesgo_estres_hidrico'],
                analisis['recomendacion']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando análisis fenológico: {e}")
    
    def _generar_analisis_brisas_marinas(self, fechas: pd.DatetimeIndex):
        """Generar análisis específico de brisas marinas"""
        try:
            for estacion_id in self.estaciones_casablanca.keys():
                config_estacion = self.estaciones_casablanca[estacion_id]
                influencia = config_estacion['influencia_marina']
                
                for fecha in fechas:
                    # Calcular parámetros de brisa marina
                    analisis_brisa = self._calcular_parametros_brisa_marina(
                        estacion_id, fecha, influencia
                    )
                    
                    # Guardar análisis
                    self._guardar_analisis_brisa_marina(estacion_id, fecha, analisis_brisa)
            
            print("[OK] Análisis de brisas marinas generados")
            
        except Exception as e:
            print(f"[ERROR] Error generando análisis de brisas marinas: {e}")
    
    def _calcular_parametros_brisa_marina(self, estacion_id: str, fecha: datetime, influencia: str) -> Dict:
        """Calcular parámetros específicos de brisa marina"""
        try:
            datos_meteo = self._obtener_datos_meteo_dia(estacion_id, fecha)
            if not datos_meteo:
                return {}
            
            # Parámetros base según influencia marina
            if influencia == 'Muy Alta':
                velocidad_base = np.random.uniform(15, 25)
                frecuencia_base = np.random.uniform(80, 95)
                temp_diferencial = np.random.uniform(-6, -8)
                humedad_diferencial = np.random.uniform(15, 25)
            elif influencia == 'Alta':
                velocidad_base = np.random.uniform(12, 20)
                frecuencia_base = np.random.uniform(70, 85)
                temp_diferencial = np.random.uniform(-4, -6)
                humedad_diferencial = np.random.uniform(10, 20)
            elif influencia == 'Media':
                velocidad_base = np.random.uniform(8, 15)
                frecuencia_base = np.random.uniform(50, 70)
                temp_diferencial = np.random.uniform(-2, -4)
                humedad_diferencial = np.random.uniform(5, 15)
            elif influencia == 'Baja':
                velocidad_base = np.random.uniform(5, 12)
                frecuencia_base = np.random.uniform(30, 50)
                temp_diferencial = np.random.uniform(-1, -2)
                humedad_diferencial = np.random.uniform(2, 8)
            else:  # Muy Baja
                velocidad_base = np.random.uniform(3, 8)
                frecuencia_base = np.random.uniform(10, 30)
                temp_diferencial = np.random.uniform(0, -1)
                humedad_diferencial = np.random.uniform(0, 5)
            
            # Dirección dominante de brisa (S-SO)
            direccion_dominante = np.random.uniform(200, 250)
            
            # Clasificar intensidad
            if velocidad_base > 20:
                intensidad = 'Muy Fuerte'
            elif velocidad_base > 15:
                intensidad = 'Fuerte'
            elif velocidad_base > 10:
                intensidad = 'Moderada'
            elif velocidad_base > 5:
                intensidad = 'Suave'
            else:
                intensidad = 'Muy Suave'
            
            # Calcular efecto refrescante
            efecto_refrescante = abs(temp_diferencial) * (velocidad_base / 10)
            
            # Calcular beneficio para uvas
            beneficio_uvas = self._calcular_beneficio_uvas_brisa(
                velocidad_base, temp_diferencial, humedad_diferencial
            )
            
            return {
                'velocidad_brisa_promedio': round(velocidad_base, 1),
                'direccion_brisa_dominante': round(direccion_dominante, 1),
                'frecuencia_brisa': round(frecuencia_base, 1),
                'intensidad_brisa': intensidad,
                'temperatura_diferencial': round(temp_diferencial, 1),
                'humedad_diferencial': round(humedad_diferencial, 1),
                'efecto_refrescante': round(efecto_refrescante, 1),
                'beneficio_uvas': round(beneficio_uvas, 1)
            }
            
        except Exception as e:
            print(f"[ERROR] Error calculando parámetros de brisa marina: {e}")
            return {}
    
    def _calcular_beneficio_uvas_brisa(self, velocidad: float, temp_diff: float, humedad_diff: float) -> float:
        """Calcular beneficio de la brisa marina para las uvas"""
        try:
            # Beneficio por efecto refrescante
            beneficio_temp = abs(temp_diff) * 2
            
            # Beneficio por humedad (evita deshidratación)
            beneficio_humedad = humedad_diff * 0.5
            
            # Beneficio por ventilación (reduce enfermedades)
            beneficio_ventilacion = min(20, velocidad * 0.8)
            
            # Beneficio por limpieza del aire
            beneficio_aire = min(15, velocidad * 0.5)
            
            beneficio_total = beneficio_temp + beneficio_humedad + beneficio_ventilacion + beneficio_aire
            
            return min(100, beneficio_total)
            
        except Exception as e:
            print(f"[ERROR] Error calculando beneficio para uvas: {e}")
            return 0.0
    
    def _guardar_analisis_brisa_marina(self, estacion_id: str, fecha: datetime, analisis: Dict):
        """Guardar análisis de brisa marina en la base de datos"""
        try:
            if not analisis:
                return
                
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analisis_brisas_marinas 
                (estacion_id, fecha_analisis, velocidad_brisa_promedio, direccion_brisa_dominante,
                 frecuencia_brisa, intensidad_brisa, temperatura_diferencial, humedad_diferencial,
                 efecto_refrescante, beneficio_uvas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estacion_id, fecha, analisis['velocidad_brisa_promedio'],
                analisis['direccion_brisa_dominante'], analisis['frecuencia_brisa'],
                analisis['intensidad_brisa'], analisis['temperatura_diferencial'],
                analisis['humedad_diferencial'], analisis['efecto_refrescante'],
                analisis['beneficio_uvas']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando análisis de brisa marina: {e}")
    
    def _generar_recomendaciones_casablanca(self, fechas: pd.DatetimeIndex):
        """Generar recomendaciones específicas para Casablanca"""
        try:
            for estacion_id in self.estaciones_casablanca.keys():
                config_estacion = self.estaciones_casablanca[estacion_id]
                
                for fecha in fechas:
                    # Generar recomendaciones específicas
                    recomendaciones = self._generar_recomendaciones_estacion(
                        estacion_id, fecha, config_estacion
                    )
                    
                    # Guardar recomendaciones
                    for rec in recomendaciones:
                        self._guardar_recomendacion_casablanca(estacion_id, fecha, rec)
            
            print("[OK] Recomendaciones específicas de Casablanca generadas")
            
        except Exception as e:
            print(f"[ERROR] Error generando recomendaciones: {e}")
    
    def _generar_recomendaciones_estacion(self, estacion_id: str, fecha: datetime, config_estacion: Dict) -> List[Dict]:
        """Generar recomendaciones específicas para una estación"""
        try:
            recomendaciones = []
            
            # Obtener datos del día
            datos_meteo = self._obtener_datos_meteo_dia(estacion_id, fecha)
            if not datos_meteo:
                return []
            
            # Recomendaciones por influencia marina
            influencia = config_estacion['influencia_marina']
            cultivo = config_estacion['cultivo']
            
            # Recomendaciones de manejo de canopia
            if influencia in ['Muy Alta', 'Alta']:
                recomendaciones.append({
                    'tipo_recomendacion': 'manejo_canopia',
                    'categoria': 'viticultura',
                    'prioridad': 'media',
                    'mensaje': 'Aprovechar brisas marinas para control natural de enfermedades',
                    'accion_requerida': 'Mantener canopia abierta para máxima ventilación',
                    'plazo_ejecucion': 'inmediato',
                    'parametros_climaticos': json.dumps({
                        'influencia_marina': influencia,
                        'velocidad_brisa': datos_meteo.get('velocidad_viento', 0)
                    })
                })
            
            # Recomendaciones de riego
            if influencia in ['Muy Baja', 'Baja']:
                recomendaciones.append({
                    'tipo_recomendacion': 'riego',
                    'categoria': 'hidrica',
                    'prioridad': 'alta',
                    'mensaje': 'Zona con menor influencia marina - mayor demanda de riego',
                    'accion_requerida': 'Implementar riego deficitario controlado',
                    'plazo_ejecucion': '1 semana',
                    'parametros_climaticos': json.dumps({
                        'temperatura_promedio': datos_meteo.get('temperatura_promedio', 0),
                        'humedad_relativa': datos_meteo.get('humedad_relativa', 0)
                    })
                })
            
            # Recomendaciones de protección contra heladas
            if datos_meteo['temperatura_min'] < 3:
                recomendaciones.append({
                    'tipo_recomendacion': 'proteccion_heladas',
                    'categoria': 'riesgo_climatico',
                    'prioridad': 'alta',
                    'mensaje': 'Riesgo de helada detectado',
                    'accion_requerida': 'Activar sistemas de protección contra heladas',
                    'plazo_ejecucion': 'inmediato',
                    'parametros_climaticos': json.dumps({
                        'temperatura_minima': datos_meteo['temperatura_min'],
                        'fase_fenologica': self._determinar_fase_fenologica(fecha.month)
                    })
                })
            
            # Recomendaciones de fertilización
            if fecha.month in [9, 10, 11]:  # Primavera
                recomendaciones.append({
                    'tipo_recomendacion': 'fertilizacion',
                    'categoria': 'nutricion',
                    'prioridad': 'media',
                    'mensaje': 'Aplicar fertilizantes de primavera para uva blanca',
                    'accion_requerida': 'Aplicar nitrógeno y micronutrientes',
                    'plazo_ejecucion': '2 semanas',
                    'parametros_climaticos': json.dumps({
                        'mes': fecha.month,
                        'temperatura_promedio': datos_meteo.get('temperatura_promedio', 0)
                    })
                })
            
            # Recomendaciones específicas por variedad
            if 'Chardonnay' in cultivo:
                recomendaciones.append({
                    'tipo_recomendacion': 'manejo_varietal',
                    'categoria': 'especifica',
                    'prioridad': 'baja',
                    'mensaje': 'Chardonnay: Controlar vigor vegetativo en zonas costeras',
                    'accion_requerida': 'Poda verde y manejo de brotes',
                    'plazo_ejecucion': '1 mes',
                    'parametros_climaticos': json.dumps({
                        'variedad': 'Chardonnay',
                        'influencia_marina': influencia
                    })
                })
            
            return recomendaciones
            
        except Exception as e:
            print(f"[ERROR] Error generando recomendaciones de estación: {e}")
            return []
    
    def _guardar_recomendacion_casablanca(self, estacion_id: str, fecha: datetime, recomendacion: Dict):
        """Guardar recomendación específica de Casablanca"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recomendaciones_casablanca 
                (estacion_id, fecha_recomendacion, tipo_recomendacion, categoria,
                 prioridad, mensaje, accion_requerida, plazo_ejecucion, parametros_climaticos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estacion_id, fecha, recomendacion['tipo_recomendacion'],
                recomendacion['categoria'], recomendacion['prioridad'],
                recomendacion['mensaje'], recomendacion['accion_requerida'],
                recomendacion['plazo_ejecucion'], recomendacion['parametros_climaticos']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando recomendación: {e}")
    
    def generar_reporte_casablanca_completo(self) -> Dict:
        """Generar reporte completo de la expansión a Casablanca"""
        try:
            print("[REPORTE] Generando reporte completo de Casablanca...")
            
            # Obtener estadísticas generales
            estadisticas = self._obtener_estadisticas_casablanca()
            
            # Generar análisis por estación
            analisis_estaciones = {}
            for estacion_id, config in self.estaciones_casablanca.items():
                analisis_estaciones[estacion_id] = self._generar_analisis_estacion(estacion_id, config)
            
            # Generar análisis de brisas marinas
            analisis_brisas = self._generar_analisis_brisas_consolidado()
            
            # Generar recomendaciones consolidadas
            recomendaciones_consolidadas = self._generar_recomendaciones_consolidadas()
            
            # Generar visualizaciones
            rutas_graficos = self._generar_visualizaciones_casablanca()
            
            reporte = {
                'fecha_reporte': datetime.now().isoformat(),
                'region': 'Valle de Casablanca',
                'configuracion_region': self.configuracion_casablanca,
                'estadisticas_generales': estadisticas,
                'analisis_por_estacion': analisis_estaciones,
                'analisis_brisas_marinas': analisis_brisas,
                'recomendaciones_consolidadas': recomendaciones_consolidadas,
                'visualizaciones': rutas_graficos,
                'resumen_ejecutivo': self._generar_resumen_ejecutivo_casablanca(estadisticas, analisis_brisas)
            }
            
            # Guardar reporte
            self._guardar_reporte_completo(reporte)
            
            print("[OK] Reporte completo de Casablanca generado")
            return reporte
            
        except Exception as e:
            print(f"[ERROR] Error generando reporte completo: {e}")
            return {'error': str(e)}
    
    def _obtener_estadisticas_casablanca(self) -> Dict:
        """Obtener estadísticas generales de Casablanca"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Estadísticas de datos meteorológicos
            cursor.execute('SELECT COUNT(*) FROM datos_meteorologicos_casablanca')
            total_registros = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT estacion_id) FROM datos_meteorologicos_casablanca')
            estaciones_activas = cursor.fetchone()[0]
            
            # Estadísticas por estación
            cursor.execute('''
                SELECT estacion_id, 
                       AVG(temperatura_promedio) as temp_promedio,
                       AVG(humedad_relativa) as humedad_promedio,
                       AVG(velocidad_brisa) as brisa_promedio
                FROM datos_meteorologicos_casablanca 
                GROUP BY estacion_id
            ''')
            estadisticas_estaciones = {row[0]: {
                'temperatura_promedio': round(row[1], 1),
                'humedad_promedio': round(row[2], 1),
                'velocidad_brisa_promedio': round(row[3], 1)
            } for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_registros': total_registros,
                'estaciones_activas': estaciones_activas,
                'periodo_analisis': 'Último año',
                'estadisticas_por_estacion': estadisticas_estaciones
            }
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo estadísticas: {e}")
            return {}
    
    def _generar_analisis_estacion(self, estacion_id: str, config_estacion: Dict) -> Dict:
        """Generar análisis específico para una estación"""
        try:
            # Obtener datos de la estación
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Datos meteorológicos recientes
            cursor.execute('''
                SELECT * FROM datos_meteorologicos_casablanca 
                WHERE estacion_id = ? 
                ORDER BY fecha DESC 
                LIMIT 30
            ''', (estacion_id,))
            
            datos_recientes = cursor.fetchall()
            
            # Análisis fenológicos recientes
            cursor.execute('''
                SELECT * FROM analisis_fenologicos 
                WHERE estacion_id = ? 
                ORDER BY fecha_analisis DESC 
                LIMIT 7
            ''', (estacion_id,))
            
            analisis_fenologicos = cursor.fetchall()
            
            conn.close()
            
            # Calcular métricas
            if datos_recientes:
                temp_promedio = np.mean([row[5] for row in datos_recientes])
                humedad_promedio = np.mean([row[6] for row in datos_recientes])
                brisa_promedio = np.mean([row[13] for row in datos_recientes])
            else:
                temp_promedio = humedad_promedio = brisa_promedio = 0
            
            # Estado fenológico actual
            estado_fenologico = 'desconocido'
            if analisis_fenologicos:
                estado_fenologico = analisis_fenologicos[0][3]  # Última fase fenológica
            
            return {
                'configuracion': config_estacion,
                'metricas_recientes': {
                    'temperatura_promedio': round(temp_promedio, 1),
                    'humedad_promedio': round(humedad_promedio, 1),
                    'velocidad_brisa_promedio': round(brisa_promedio, 1)
                },
                'estado_fenologico_actual': estado_fenologico,
                'registros_recientes': len(datos_recientes)
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando análisis de estación: {e}")
            return {}
    
    def _generar_analisis_brisas_consolidado(self) -> Dict:
        """Generar análisis consolidado de brisas marinas"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Análisis por nivel de influencia marina
            cursor.execute('''
                SELECT e.influencia_marina,
                       AVG(b.velocidad_brisa_promedio) as velocidad_promedio,
                       AVG(b.frecuencia_brisa) as frecuencia_promedio,
                       AVG(b.efecto_refrescante) as efecto_promedio,
                       AVG(b.beneficio_uvas) as beneficio_promedio
                FROM analisis_brisas_marinas b
                JOIN estaciones_casablanca e ON b.estacion_id = e.estacion_id
                GROUP BY e.influencia_marina
            ''')
            
            analisis_por_influencia = {}
            for row in cursor.fetchall():
                analisis_por_influencia[row[0]] = {
                    'velocidad_promedio': round(row[1], 1),
                    'frecuencia_promedio': round(row[2], 1),
                    'efecto_refrescante': round(row[3], 1),
                    'beneficio_uvas': round(row[4], 1)
                }
            
            conn.close()
            
            return {
                'analisis_por_influencia_marina': analisis_por_influencia,
                'conclusiones': self._generar_conclusiones_brisas(analisis_por_influencia)
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando análisis de brisas: {e}")
            return {}
    
    def _generar_conclusiones_brisas(self, analisis_por_influencia: Dict) -> List[str]:
        """Generar conclusiones sobre el efecto de las brisas marinas"""
        try:
            conclusiones = []
            
            for influencia, datos in analisis_por_influencia.items():
                beneficio = datos['beneficio_uvas']
                
                if beneficio > 70:
                    conclusiones.append(f"Zonas con influencia {influencia}: Excelente beneficio para uvas ({beneficio:.1f}%)")
                elif beneficio > 50:
                    conclusiones.append(f"Zonas con influencia {influencia}: Buen beneficio para uvas ({beneficio:.1f}%)")
                else:
                    conclusiones.append(f"Zonas con influencia {influencia}: Beneficio moderado para uvas ({beneficio:.1f}%)")
            
            return conclusiones
            
        except Exception as e:
            print(f"[ERROR] Error generando conclusiones: {e}")
            return []
    
    def _generar_recomendaciones_consolidadas(self) -> Dict:
        """Generar recomendaciones consolidadas para Casablanca"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Recomendaciones por categoría
            cursor.execute('''
                SELECT categoria, COUNT(*) as cantidad, 
                       AVG(CASE WHEN prioridad = 'alta' THEN 1 ELSE 0 END) * 100 as porcentaje_alta
                FROM recomendaciones_casablanca 
                WHERE fecha_recomendacion >= date('now', '-30 days')
                GROUP BY categoria
            ''')
            
            recomendaciones_por_categoria = {}
            for row in cursor.fetchall():
                recomendaciones_por_categoria[row[0]] = {
                    'cantidad': row[1],
                    'porcentaje_prioridad_alta': round(row[2], 1)
                }
            
            conn.close()
            
            return {
                'recomendaciones_por_categoria': recomendaciones_por_categoria,
                'recomendaciones_generales': [
                    "Aprovechar brisas marinas para control natural de enfermedades",
                    "Implementar riego deficitario controlado en zonas de menor influencia marina",
                    "Mantener sistemas de protección contra heladas tardías",
                    "Optimizar manejo de canopia según influencia marina",
                    "Aplicar fertilizaciones específicas para uva blanca"
                ]
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando recomendaciones consolidadas: {e}")
            return {}
    
    def _generar_visualizaciones_casablanca(self) -> Dict:
        """Generar visualizaciones específicas para Casablanca"""
        try:
            rutas_graficos = {}
            
            # Gráfico de distribución de estaciones
            ruta_estaciones = self._crear_grafico_estaciones()
            if ruta_estaciones:
                rutas_graficos['distribucion_estaciones'] = ruta_estaciones
            
            # Gráfico de análisis de brisas marinas
            ruta_brisas = self._crear_grafico_brisas_marinas()
            if ruta_brisas:
                rutas_graficos['analisis_brisas'] = ruta_brisas
            
            # Gráfico de recomendaciones por prioridad
            ruta_recomendaciones = self._crear_grafico_recomendaciones()
            if ruta_recomendaciones:
                rutas_graficos['recomendaciones'] = ruta_recomendaciones
            
            return rutas_graficos
            
        except Exception as e:
            print(f"[ERROR] Error generando visualizaciones: {e}")
            return {}
    
    def _crear_grafico_estaciones(self) -> str:
        """Crear gráfico de distribución de estaciones en Casablanca"""
        try:
            fig = go.Figure()
            
            # Agregar estaciones
            for estacion_id, config in self.estaciones_casablanca.items():
                # Color según influencia marina
                color_map = {
                    'Muy Alta': 'darkblue',
                    'Alta': 'blue',
                    'Media': 'lightblue',
                    'Baja': 'orange',
                    'Muy Baja': 'red'
                }
                color = color_map.get(config['influencia_marina'], 'gray')
                
                fig.add_trace(go.Scatter(
                    x=[config['longitud']],
                    y=[config['latitud']],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=color,
                        symbol='circle'
                    ),
                    name=config['nombre'],
                    text=f"{config['nombre']}<br>Influencia: {config['influencia_marina']}<br>Cultivo: {config['cultivo']}",
                    hovertemplate='%{text}<extra></extra>'
                ))
            
            fig.update_layout(
                title='Estaciones Meteorológicas - Valle de Casablanca',
                xaxis_title='Longitud',
                yaxis_title='Latitud',
                showlegend=True,
                width=800,
                height=600
            )
            
            ruta_archivo = os.path.join(self.directorio_reportes, 'analisis_vinedos', 'distribucion_estaciones.html')
            fig.write_html(ruta_archivo)
            
            return ruta_archivo
            
        except Exception as e:
            print(f"[ERROR] Error creando gráfico de estaciones: {e}")
            return ""
    
    def _crear_grafico_brisas_marinas(self) -> str:
        """Crear gráfico de análisis de brisas marinas"""
        try:
            # Obtener datos de brisas marinas
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.influencia_marina, e.nombre,
                       AVG(b.velocidad_brisa_promedio) as velocidad,
                       AVG(b.beneficio_uvas) as beneficio
                FROM analisis_brisas_marinas b
                JOIN estaciones_casablanca e ON b.estacion_id = e.estacion_id
                GROUP BY e.estacion_id, e.influencia_marina, e.nombre
            ''')
            
            datos = cursor.fetchall()
            conn.close()
            
            if not datos:
                return ""
            
            # Crear gráfico
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Velocidad de Brisa Marina', 'Beneficio para Uvas'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            influencias = [row[0] for row in datos]
            velocidades = [row[2] for row in datos]
            beneficios = [row[3] for row in datos]
            nombres = [row[1] for row in datos]
            
            fig.add_trace(
                go.Bar(x=nombres, y=velocidades, name='Velocidad (km/h)', marker_color='lightblue'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=nombres, y=beneficios, name='Beneficio (%)', marker_color='lightgreen'),
                row=1, col=2
            )
            
            fig.update_layout(
                title='Análisis de Brisas Marinas - Valle de Casablanca',
                showlegend=True,
                width=1000,
                height=500
            )
            
            ruta_archivo = os.path.join(self.directorio_reportes, 'analisis_vinedos', 'analisis_brisas_marinas.html')
            fig.write_html(ruta_archivo)
            
            return ruta_archivo
            
        except Exception as e:
            print(f"[ERROR] Error creando gráfico de brisas: {e}")
            return ""
    
    def _crear_grafico_recomendaciones(self) -> str:
        """Crear gráfico de recomendaciones por prioridad"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT prioridad, COUNT(*) as cantidad
                FROM recomendaciones_casablanca 
                WHERE fecha_recomendacion >= date('now', '-30 days')
                GROUP BY prioridad
            ''')
            
            datos = cursor.fetchall()
            conn.close()
            
            if not datos:
                return ""
            
            prioridades = [row[0] for row in datos]
            cantidades = [row[1] for row in datos]
            
            # Colores según prioridad
            color_map = {'alta': 'red', 'media': 'orange', 'baja': 'green'}
            colores = [color_map.get(p, 'gray') for p in prioridades]
            
            fig = go.Figure(data=[
                go.Bar(x=prioridades, y=cantidades, marker_color=colores)
            ])
            
            fig.update_layout(
                title='Recomendaciones por Prioridad - Últimos 30 días',
                xaxis_title='Prioridad',
                yaxis_title='Cantidad',
                width=600,
                height=400
            )
            
            ruta_archivo = os.path.join(self.directorio_reportes, 'recomendaciones', 'recomendaciones_por_prioridad.html')
            fig.write_html(ruta_archivo)
            
            return ruta_archivo
            
        except Exception as e:
            print(f"[ERROR] Error creando gráfico de recomendaciones: {e}")
            return ""
    
    def _generar_resumen_ejecutivo_casablanca(self, estadisticas: Dict, analisis_brisas: Dict) -> Dict:
        """Generar resumen ejecutivo de la expansión a Casablanca"""
        try:
            return {
                'expansion_completada': True,
                'region_expandida': 'Valle de Casablanca',
                'estaciones_configuradas': len(self.estaciones_casablanca),
                'cultivo_principal': 'Uva blanca para vino',
                'caracteristica_principal': 'Influencia de brisas marinas',
                'beneficios_principales': [
                    'Control natural de enfermedades por brisas marinas',
                    'Temperaturas moderadas por influencia costera',
                    'Menor riesgo de estrés hídrico',
                    'Condiciones óptimas para uva blanca'
                ],
                'desafios_identificados': [
                    'Protección contra heladas tardías',
                    'Manejo de humedad alta en zonas costeras',
                    'Optimización de riego según influencia marina'
                ],
                'recomendaciones_estrategicas': [
                    'Aprovechar microclimas creados por brisas marinas',
                    'Implementar sistemas de monitoreo específicos',
                    'Desarrollar protocolos de manejo diferenciados por zona'
                ],
                'estado_expansion': 'Operativa y funcional'
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando resumen ejecutivo: {e}")
            return {}
    
    def _guardar_reporte_completo(self, reporte: Dict):
        """Guardar reporte completo de Casablanca"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_casablanca_completo_{timestamp}.json"
            ruta_archivo = os.path.join(self.directorio_reportes, nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Reporte completo guardado: {ruta_archivo}")
            
        except Exception as e:
            print(f"[ERROR] Error guardando reporte: {e}")

def main():
    """Función principal para demostrar la expansión a Casablanca"""
    try:
        print("="*80)
        print("EXPANSIÓN REGIONAL CASABLANCA - METGO 3D QUILLOTA")
        print("="*80)
        
        # Inicializar sistema de expansión
        expansion = ExpansionRegionalCasablancaMetgo()
        
        print("\n[1] GENERANDO DATOS ESPECÍFICOS DE CASABLANCA...")
        
        # Generar datos para Casablanca
        resultado_datos = expansion.generar_datos_casablanca(dias=365)
        
        if 'error' in resultado_datos:
            print(f"[ERROR] Error generando datos: {resultado_datos['error']}")
            return
        
        print(f"[OK] Datos generados:")
        print(f"    - Total registros: {resultado_datos['total_registros']}")
        print(f"    - Estaciones: {resultado_datos['estaciones_procesadas']}")
        print(f"    - Período: {resultado_datos['periodo_datos']}")
        print(f"    - Análisis: {', '.join(resultado_datos['analisis_generados'])}")
        
        print("\n[2] GENERANDO REPORTE COMPLETO...")
        
        # Generar reporte completo
        reporte_completo = expansion.generar_reporte_casablanca_completo()
        
        if 'error' in reporte_completo:
            print(f"[ERROR] Error generando reporte: {reporte_completo['error']}")
        else:
            print(f"[OK] Reporte completo generado")
            resumen = reporte_completo['resumen_ejecutivo']
            print(f"    - Región: {resumen['region_expandida']}")
            print(f"    - Estaciones: {resumen['estaciones_configuradas']}")
            print(f"    - Cultivo: {resumen['cultivo_principal']}")
            print(f"    - Estado: {resumen['estado_expansion']}")
        
        print("\n[3] INFORMACIÓN DE ESTACIONES CONFIGURADAS...")
        
        for estacion_id, config in expansion.estaciones_casablanca.items():
            print(f"    - {config['nombre']}")
            print(f"      Ubicación: {config['latitud']:.4f}, {config['longitud']:.4f}")
            print(f"      Altitud: {config['altitud']}m")
            print(f"      Cultivo: {config['cultivo']}")
            print(f"      Influencia marina: {config['influencia_marina']}")
        
        print("\n[4] CARACTERÍSTICAS ESPECÍFICAS DE CASABLANCA...")
        
        print("    - Brisas marinas: Control natural de enfermedades")
        print("    - Temperaturas moderadas: Ideal para uva blanca")
        print("    - Humedad alta: Manejo especializado requerido")
        print("    - Variedades: Chardonnay, Sauvignon Blanc, Pinot Grigio")
        print("    - Microclimas: Diferenciados por influencia marina")
        
        print("\n" + "="*80)
        print("EXPANSIÓN REGIONAL CASABLANCA COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("[OK] Sistema expandido a Valle de Casablanca")
        print("[OK] 5 estaciones meteorológicas configuradas")
        print("[OK] Análisis de brisas marinas implementado")
        print("[OK] Recomendaciones específicas para uva blanca")
        print("[OK] Sistema de monitoreo fenológico activo")
        print("[OK] Reporte completo generado")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] Error en función principal: {e}")

if __name__ == "__main__":
    main()
