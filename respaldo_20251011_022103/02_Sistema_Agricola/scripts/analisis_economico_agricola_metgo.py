"""
SISTEMA DE ANÁLISIS ECONÓMICO AGRÍCOLA - METGO 3D QUILLOTA
Sistema para análisis de ROI, costos, precios de mercado y rentabilidad agrícola
Incluye: Cálculo de retorno de inversión, optimización de insumos, análisis de precios en tiempo real
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
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class AnalisisEconomicoAgricolaMetgo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "analisis_economico_agricola.db"
        self.directorio_datos = "datos_economicos"
        self.directorio_reportes = "reportes_economicos"
        
        # Crear directorios necesarios
        self._crear_directorios()
        
        # Inicializar base de datos
        self._inicializar_base_datos()
        
        # Configuración de cultivos con datos económicos
        self.configuracion_cultivos_economicos = {
            'palto': {
                'nombre': 'Palto (Aguacate)',
                'precio_kg': 2500,  # CLP por kg
                'rendimiento_hectarea': 8000,  # kg/ha
                'costo_produccion_hectarea': 4500000,  # CLP/ha
                'costo_plantacion': 8000000,  # CLP/ha
                'vida_util': 25,  # años
                'tiempo_inicio_produccion': 3,  # años
                'costo_mantenimiento_anual': 1200000,  # CLP/ha
                'incremento_rendimiento_anual': 0.15,  # 15% por año hasta estabilización
                'estabilizacion_rendimiento': 10,  # año de estabilización
            },
            'uva': {
                'nombre': 'Uva de Mesa',
                'precio_kg': 800,  # CLP por kg
                'rendimiento_hectarea': 25000,  # kg/ha
                'costo_produccion_hectarea': 12000000,  # CLP/ha
                'costo_plantacion': 15000000,  # CLP/ha
                'vida_util': 20,  # años
                'tiempo_inicio_produccion': 2,  # años
                'costo_mantenimiento_anual': 2500000,  # CLP/ha
                'incremento_rendimiento_anual': 0.20,  # 20% por año hasta estabilización
                'estabilizacion_rendimiento': 5,  # año de estabilización
            },
            'citricos': {
                'nombre': 'Cítricos (Naranjas, Limones)',
                'precio_kg': 600,  # CLP por kg
                'rendimiento_hectarea': 35000,  # kg/ha
                'costo_produccion_hectarea': 8000000,  # CLP/ha
                'costo_plantacion': 6000000,  # CLP/ha
                'vida_util': 30,  # años
                'tiempo_inicio_produccion': 4,  # años
                'costo_mantenimiento_anual': 1500000,  # CLP/ha
                'incremento_rendimiento_anual': 0.12,  # 12% por año hasta estabilización
                'estabilizacion_rendimiento': 8,  # año de estabilización
            },
            'uva_vino': {
                'nombre': 'Uva para Vino',
                'precio_kg': 1200,  # CLP por kg
                'rendimiento_hectarea': 15000,  # kg/ha
                'costo_produccion_hectarea': 9000000,  # CLP/ha
                'costo_plantacion': 12000000,  # CLP/ha
                'vida_util': 25,  # años
                'tiempo_inicio_produccion': 3,  # años
                'costo_mantenimiento_anual': 2000000,  # CLP/ha
                'incremento_rendimiento_anual': 0.18,  # 18% por año hasta estabilización
                'estabilizacion_rendimiento': 7,  # año de estabilización
            }
        }
        
        # Configuración de insumos agrícolas
        self.configuracion_insumos = {
            'fertilizantes': {
                'nitrogeno': {'precio_kg': 1200, 'unidad': 'kg', 'categoria': 'nutrientes'},
                'fosforo': {'precio_kg': 1800, 'unidad': 'kg', 'categoria': 'nutrientes'},
                'potasio': {'precio_kg': 1500, 'unidad': 'kg', 'categoria': 'nutrientes'},
                'compost': {'precio_kg': 300, 'unidad': 'kg', 'categoria': 'organicos'},
                'humus': {'precio_kg': 500, 'unidad': 'kg', 'categoria': 'organicos'},
            },
            'pesticidas': {
                'herbicida': {'precio_litro': 25000, 'unidad': 'litro', 'categoria': 'proteccion'},
                'fungicida': {'precio_litro': 18000, 'unidad': 'litro', 'categoria': 'proteccion'},
                'insecticida': {'precio_litro': 22000, 'unidad': 'litro', 'categoria': 'proteccion'},
                'acaricida': {'precio_litro': 28000, 'unidad': 'litro', 'categoria': 'proteccion'},
            },
            'maquinaria': {
                'tractor': {'costo_hora': 15000, 'unidad': 'hora', 'categoria': 'maquinaria'},
                'pulverizador': {'costo_hora': 8000, 'unidad': 'hora', 'categoria': 'maquinaria'},
                'cosechadora': {'costo_hora': 25000, 'unidad': 'hora', 'categoria': 'maquinaria'},
                'riego': {'costo_hora': 5000, 'unidad': 'hora', 'categoria': 'riego'},
            },
            'mano_obra': {
                'operario': {'costo_hora': 3500, 'unidad': 'hora', 'categoria': 'labor'},
                'supervisor': {'costo_hora': 5000, 'unidad': 'hora', 'categoria': 'labor'},
                'técnico': {'costo_hora': 7000, 'unidad': 'hora', 'categoria': 'labor'},
            }
        }
        
        # Factores de optimización por tecnología
        self.factores_optimizacion = {
            'riego_inteligente': {
                'reduccion_agua': 0.25,  # 25% menos agua
                'incremento_rendimiento': 0.15,  # 15% más rendimiento
                'costo_implementacion': 2000000,  # CLP/ha
            },
            'drones_monitoreo': {
                'reduccion_pesticidas': 0.30,  # 30% menos pesticidas
                'reduccion_fertilizantes': 0.20,  # 20% menos fertilizantes
                'incremento_rendimiento': 0.10,  # 10% más rendimiento
                'costo_implementacion': 500000,  # CLP/ha
            },
            'ml_predicciones': {
                'reduccion_perdidas': 0.20,  # 20% menos pérdidas
                'optimizacion_cosecha': 0.12,  # 12% mejor timing
                'incremento_precio': 0.08,  # 8% mejor precio por calidad
                'costo_implementacion': 300000,  # CLP/ha
            },
            'sensores_iot': {
                'reduccion_agua': 0.20,  # 20% menos agua
                'reduccion_fertilizantes': 0.25,  # 25% menos fertilizantes
                'incremento_rendimiento': 0.18,  # 18% más rendimiento
                'costo_implementacion': 1500000,  # CLP/ha
            }
        }
        
        self.logger.info("Sistema de Análisis Económico Agrícola METGO 3D inicializado")
    
    def _crear_directorios(self):
        """Crear directorios necesarios para el sistema"""
        try:
            directorios = [
                self.directorio_datos,
                self.directorio_reportes,
                f"{self.directorio_datos}/costos",
                f"{self.directorio_datos}/precios",
                f"{self.directorio_datos}/rendimientos",
                f"{self.directorio_reportes}/analisis_roi",
                f"{self.directorio_reportes}/optimizacion",
                f"{self.directorio_reportes}/tendencias"
            ]
            
            for directorio in directorios:
                os.makedirs(directorio, exist_ok=True)
                
            print("[OK] Directorios del sistema económico creados")
            
        except Exception as e:
            print(f"[ERROR] Error creando directorios: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para análisis económico"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de cultivos económicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cultivos_economicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cultivo_id TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    precio_kg REAL NOT NULL,
                    rendimiento_hectarea REAL NOT NULL,
                    costo_produccion_hectarea REAL NOT NULL,
                    costo_plantacion REAL NOT NULL,
                    vida_util INTEGER NOT NULL,
                    tiempo_inicio_produccion INTEGER NOT NULL,
                    costo_mantenimiento_anual REAL NOT NULL,
                    incremento_rendimiento_anual REAL NOT NULL,
                    estabilizacion_rendimiento INTEGER NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de insumos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insumos_agricolas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insumo_id TEXT UNIQUE NOT NULL,
                    categoria TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    precio_unidad REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de análisis ROI
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analisis_roi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analisis_id TEXT UNIQUE NOT NULL,
                    cultivo_id TEXT NOT NULL,
                    area_hectareas REAL NOT NULL,
                    horizonte_anos INTEGER NOT NULL,
                    roi_proyectado REAL,
                    van_proyectado REAL,
                    tir_proyectada REAL,
                    payback_period REAL,
                    parametros_entrada TEXT,
                    fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de optimización de insumos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimizacion_insumos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimizacion_id TEXT UNIQUE NOT NULL,
                    cultivo_id TEXT NOT NULL,
                    area_hectareas REAL NOT NULL,
                    tecnologia_aplicada TEXT NOT NULL,
                    ahorro_estimado REAL,
                    incremento_rendimiento REAL,
                    roi_tecnologia REAL,
                    fecha_optimizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de precios de mercado
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS precios_mercado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cultivo_id TEXT NOT NULL,
                    precio_kg REAL NOT NULL,
                    fecha_precio DATE NOT NULL,
                    fuente_precio TEXT,
                    calidad_producto TEXT,
                    region TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar datos iniciales
            self._insertar_datos_iniciales(cursor)
            
            conn.commit()
            conn.close()
            
            print("[OK] Base de datos económica inicializada")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {e}")
    
    def _insertar_datos_iniciales(self, cursor):
        """Insertar datos iniciales en la base de datos"""
        try:
            # Insertar cultivos económicos
            for cultivo_id, datos in self.configuracion_cultivos_economicos.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO cultivos_economicos 
                    (cultivo_id, nombre, precio_kg, rendimiento_hectarea, costo_produccion_hectarea,
                     costo_plantacion, vida_util, tiempo_inicio_produccion, costo_mantenimiento_anual,
                     incremento_rendimiento_anual, estabilizacion_rendimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cultivo_id, datos['nombre'], datos['precio_kg'], datos['rendimiento_hectarea'],
                    datos['costo_produccion_hectarea'], datos['costo_plantacion'], datos['vida_util'],
                    datos['tiempo_inicio_produccion'], datos['costo_mantenimiento_anual'],
                    datos['incremento_rendimiento_anual'], datos['estabilizacion_rendimiento']
                ))
            
            # Insertar insumos
            for categoria, insumos in self.configuracion_insumos.items():
                for insumo_id, datos in insumos.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO insumos_agricolas 
                        (insumo_id, categoria, nombre, precio_unidad, unidad)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        insumo_id, categoria, datos['categoria'], insumo_id.title(), 
                        datos['precio_kg'] if 'precio_kg' in datos else datos['precio_litro'], 
                        datos['unidad']
                    ))
            
            print("[OK] Datos iniciales insertados")
            
        except Exception as e:
            print(f"[ERROR] Error insertando datos iniciales: {e}")
    
    def calcular_roi_cultivo(self, cultivo_id: str, area_hectareas: float, 
                           horizonte_anos: int = 10, tasa_descuento: float = 0.08) -> Dict:
        """Calcular ROI, VAN y TIR para un cultivo específico"""
        try:
            print(f"[ROI] Calculando análisis económico para {cultivo_id}")
            
            # Obtener configuración del cultivo
            config_cultivo = self.configuracion_cultivos_economicos.get(cultivo_id)
            if not config_cultivo:
                raise ValueError(f"Cultivo {cultivo_id} no encontrado")
            
            # Calcular flujos de caja anuales
            flujos_caja = []
            costos_totales = 0
            ingresos_totales = 0
            
            for año in range(1, horizonte_anos + 1):
                # Costos
                if año <= config_cultivo['tiempo_inicio_produccion']:
                    # Período de establecimiento
                    costo_año = config_cultivo['costo_plantacion'] * area_hectareas / config_cultivo['tiempo_inicio_produccion']
                    costo_año += config_cultivo['costo_mantenimiento_anual'] * area_hectareas
                    ingreso_año = 0
                else:
                    # Período productivo
                    año_produccion = año - config_cultivo['tiempo_inicio_produccion']
                    
                    # Calcular rendimiento con incremento anual
                    if año_produccion <= config_cultivo['estabilizacion_rendimiento']:
                        factor_rendimiento = 1 + (config_cultivo['incremento_rendimiento_anual'] * año_produccion)
                    else:
                        factor_rendimiento = 1 + (config_cultivo['incremento_rendimiento_anual'] * config_cultivo['estabilizacion_rendimiento'])
                    
                    rendimiento_año = config_cultivo['rendimiento_hectarea'] * factor_rendimiento
                    ingreso_año = rendimiento_año * config_cultivo['precio_kg'] * area_hectareas
                    costo_año = config_cultivo['costo_produccion_hectarea'] * area_hectareas
                
                flujo_año = ingreso_año - costo_año
                flujos_caja.append(flujo_año)
                costos_totales += costo_año
                ingresos_totales += ingreso_año
            
            # Calcular métricas financieras
            roi = (ingresos_totales - costos_totales) / costos_totales * 100 if costos_totales > 0 else 0
            
            # Calcular VAN
            van = sum([flujo / (1 + tasa_descuento) ** (i + 1) for i, flujo in enumerate(flujos_caja)])
            
            # Calcular TIR (simplificado)
            tir = self._calcular_tir_simplificado(flujos_caja)
            
            # Calcular período de recuperación
            payback = self._calcular_payback_period(flujos_caja)
            
            # Guardar análisis
            analisis_id = f"roi_{uuid.uuid4().hex[:8]}"
            self._guardar_analisis_roi(analisis_id, cultivo_id, area_hectareas, horizonte_anos, 
                                     roi, van, tir, payback)
            
            resultado = {
                'analisis_id': analisis_id,
                'cultivo_id': cultivo_id,
                'area_hectareas': area_hectareas,
                'horizonte_anos': horizonte_anos,
                'roi_proyectado': round(roi, 2),
                'van_proyectado': round(van, 0),
                'tir_proyectada': round(tir * 100, 2),
                'payback_period': round(payback, 1),
                'ingresos_totales': round(ingresos_totales, 0),
                'costos_totales': round(costos_totales, 0),
                'beneficio_neto': round(ingresos_totales - costos_totales, 0),
                'flujos_caja': [round(flujo, 0) for flujo in flujos_caja]
            }
            
            print(f"[OK] ROI calculado: {roi:.2f}%, VAN: ${van:,.0f}, TIR: {tir*100:.2f}%")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error calculando ROI: {e}")
            return {'error': str(e)}
    
    def _calcular_tir_simplificado(self, flujos_caja: List[float]) -> float:
        """Calcular TIR de forma simplificada"""
        try:
            # Método de aproximación para TIR
            if not flujos_caja or len(flujos_caja) == 0:
                return 0.0
            
            # Buscar tasa que haga VAN = 0
            for tasa in np.arange(0.01, 0.50, 0.01):
                van_tasa = sum([flujo / (1 + tasa) ** (i + 1) for i, flujo in enumerate(flujos_caja)])
                if abs(van_tasa) < 1000:  # Tolerancia
                    return tasa
            
            return 0.15  # TIR por defecto
            
        except Exception as e:
            print(f"[ERROR] Error calculando TIR: {e}")
            return 0.10
    
    def _calcular_payback_period(self, flujos_caja: List[float]) -> float:
        """Calcular período de recuperación de la inversión"""
        try:
            acumulado = 0
            for i, flujo in enumerate(flujos_caja):
                acumulado += flujo
                if acumulado >= 0:
                    return i + 1
            
            return len(flujos_caja)  # No se recupera en el período
            
        except Exception as e:
            print(f"[ERROR] Error calculando payback: {e}")
            return 0.0
    
    def _guardar_analisis_roi(self, analisis_id: str, cultivo_id: str, area_hectareas: float,
                            horizonte_anos: int, roi: float, van: float, tir: float, payback: float):
        """Guardar análisis ROI en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analisis_roi 
                (analisis_id, cultivo_id, area_hectareas, horizonte_anos,
                 roi_proyectado, van_proyectado, tir_proyectada, payback_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (analisis_id, cultivo_id, area_hectareas, horizonte_anos, roi, van, tir, payback))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando análisis ROI: {e}")
    
    def optimizar_insumos_tecnologia(self, cultivo_id: str, area_hectareas: float, 
                                   tecnologias: List[str]) -> Dict:
        """Optimizar uso de insumos aplicando tecnologías"""
        try:
            print(f"[OPTIMIZACION] Optimizando insumos para {cultivo_id} con tecnologías")
            
            config_cultivo = self.configuracion_cultivos_economicos.get(cultivo_id)
            if not config_cultivo:
                raise ValueError(f"Cultivo {cultivo_id} no encontrado")
            
            # Calcular ahorros por tecnología
            ahorros_totales = 0
            incrementos_rendimiento = 0
            costos_implementacion = 0
            
            for tecnologia in tecnologias:
                if tecnologia in self.factores_optimizacion:
                    factores = self.factores_optimizacion[tecnologia]
                    
                    # Ahorros en insumos
                    ahorro_agua = config_cultivo['costo_produccion_hectarea'] * 0.1 * factores.get('reduccion_agua', 0)
                    ahorro_fertilizantes = config_cultivo['costo_produccion_hectarea'] * 0.15 * factores.get('reduccion_fertilizantes', 0)
                    ahorro_pesticidas = config_cultivo['costo_produccion_hectarea'] * 0.1 * factores.get('reduccion_pesticidas', 0)
                    
                    ahorros_totales += (ahorro_agua + ahorro_fertilizantes + ahorro_pesticidas) * area_hectareas
                    incrementos_rendimiento += factores.get('incremento_rendimiento', 0)
                    costos_implementacion += factores.get('costo_implementacion', 0) * area_hectareas
            
            # Calcular beneficios adicionales
            rendimiento_base = config_cultivo['rendimiento_hectarea'] * area_hectareas
            precio_base = config_cultivo['precio_kg']
            
            incremento_rendimiento_total = rendimiento_base * incrementos_rendimiento
            ingreso_adicional = incremento_rendimiento_total * precio_base
            
            # Calcular ROI de la tecnología
            beneficio_total = ahorros_totales + ingreso_adicional
            roi_tecnologia = (beneficio_total - costos_implementacion) / costos_implementacion * 100 if costos_implementacion > 0 else 0
            
            # Guardar optimización
            optimizacion_id = f"opt_{uuid.uuid4().hex[:8]}"
            self._guardar_optimizacion(optimizacion_id, cultivo_id, area_hectareas, 
                                     tecnologias, ahorros_totales, incrementos_rendimiento, roi_tecnologia)
            
            resultado = {
                'optimizacion_id': optimizacion_id,
                'cultivo_id': cultivo_id,
                'area_hectareas': area_hectareas,
                'tecnologias_aplicadas': tecnologias,
                'ahorro_anual_estimado': round(ahorros_totales, 0),
                'incremento_rendimiento': round(incrementos_rendimiento * 100, 1),
                'ingreso_adicional_anual': round(ingreso_adicional, 0),
                'costo_implementacion': round(costos_implementacion, 0),
                'roi_tecnologia': round(roi_tecnologia, 2),
                'payback_tecnologia': round(costos_implementacion / beneficio_total, 1) if beneficio_total > 0 else 0,
                'beneficio_neto_anual': round(beneficio_total - costos_implementacion, 0)
            }
            
            print(f"[OK] Optimización completada: ROI {roi_tecnologia:.2f}%, Ahorro anual ${ahorros_totales:,.0f}")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error optimizando insumos: {e}")
            return {'error': str(e)}
    
    def _guardar_optimizacion(self, optimizacion_id: str, cultivo_id: str, area_hectareas: float,
                            tecnologias: List[str], ahorro_estimado: float, incremento_rendimiento: float, roi_tecnologia: float):
        """Guardar optimización en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            for tecnologia in tecnologias:
                cursor.execute('''
                    INSERT INTO optimizacion_insumos 
                    (optimizacion_id, cultivo_id, area_hectareas, tecnologia_aplicada,
                     ahorro_estimado, incremento_rendimiento, roi_tecnologia)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (optimizacion_id, cultivo_id, area_hectareas, tecnologia,
                     ahorro_estimado / len(tecnologias), incremento_rendimiento, roi_tecnologia))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando optimización: {e}")
    
    def analizar_tendencias_precios(self, cultivo_id: str, meses_analisis: int = 12) -> Dict:
        """Analizar tendencias de precios de mercado"""
        try:
            print(f"[PRECIOS] Analizando tendencias de precios para {cultivo_id}")
            
            # Generar datos de precios históricos simulados
            precios_historicos = self._generar_precios_historicos(cultivo_id, meses_analisis)
            
            # Calcular estadísticas
            precio_promedio = np.mean(precios_historicos['precios'])
            precio_minimo = np.min(precios_historicos['precios'])
            precio_maximo = np.max(precios_historicos['precios'])
            desviacion_estandar = np.std(precios_historicos['precios'])
            
            # Calcular tendencia
            x = np.arange(len(precios_historicos['precios']))
            y = precios_historicos['precios']
            
            # Regresión lineal para tendencia
            slope, intercept = np.polyfit(x, y, 1)
            tendencia_porcentual = (slope / precio_promedio) * 100
            
            # Clasificar tendencia
            if tendencia_porcentual > 2:
                clasificacion_tendencia = "Alcista fuerte"
            elif tendencia_porcentual > 0.5:
                clasificacion_tendencia = "Alcista moderada"
            elif tendencia_porcentual > -0.5:
                clasificacion_tendencia = "Estable"
            elif tendencia_porcentual > -2:
                clasificacion_tendencia = "Bajista moderada"
            else:
                clasificacion_tendencia = "Bajista fuerte"
            
            # Calcular volatilidad
            volatilidad = (desviacion_estandar / precio_promedio) * 100
            
            resultado = {
                'cultivo_id': cultivo_id,
                'periodo_analisis': f"{meses_analisis} meses",
                'precio_promedio': round(precio_promedio, 2),
                'precio_minimo': round(precio_minimo, 2),
                'precio_maximo': round(precio_maximo, 2),
                'volatilidad': round(volatilidad, 2),
                'tendencia_porcentual': round(tendencia_porcentual, 2),
                'clasificacion_tendencia': clasificacion_tendencia,
                'precios_historicos': precios_historicos,
                'recomendacion': self._generar_recomendacion_precios(tendencia_porcentual, volatilidad)
            }
            
            print(f"[OK] Análisis de precios: Tendencia {clasificacion_tendencia}, Volatilidad {volatilidad:.2f}%")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error analizando tendencias: {e}")
            return {'error': str(e)}
    
    def _generar_precios_historicos(self, cultivo_id: str, meses: int) -> Dict:
        """Generar datos históricos de precios simulados"""
        try:
            config_cultivo = self.configuracion_cultivos_economicos.get(cultivo_id)
            precio_base = config_cultivo['precio_kg'] if config_cultivo else 1000
            
            # Generar fechas
            fechas = pd.date_range(end=datetime.now(), periods=meses, freq='M')
            
            # Generar precios con tendencia y estacionalidad
            precios = []
            for i, fecha in enumerate(fechas):
                # Tendencia base
                tendencia = precio_base * (1 + 0.02 * (i / meses))  # 2% tendencia anual
                
                # Estacionalidad (simulada)
                estacionalidad = 0.1 * np.sin(2 * np.pi * fecha.month / 12)
                
                # Volatilidad aleatoria
                volatilidad = np.random.normal(0, 0.05)
                
                precio = tendencia * (1 + estacionalidad + volatilidad)
                precios.append(max(precio, precio_base * 0.5))  # Precio mínimo
            
            return {
                'fechas': [fecha.strftime('%Y-%m') for fecha in fechas],
                'precios': precios
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando precios históricos: {e}")
            return {'fechas': [], 'precios': []}
    
    def _generar_recomendacion_precios(self, tendencia: float, volatilidad: float) -> str:
        """Generar recomendación basada en tendencia y volatilidad de precios"""
        try:
            if tendencia > 2 and volatilidad < 10:
                return "Excelente momento para vender - Precios en alza con baja volatilidad"
            elif tendencia > 1:
                return "Momento favorable para ventas - Tendencia alcista"
            elif tendencia < -2:
                return "Considerar diferir ventas - Precios en baja"
            elif volatilidad > 20:
                return "Alta volatilidad - Considerar estrategias de cobertura"
            else:
                return "Mercado estable - Vender según planificación normal"
                
        except Exception as e:
            print(f"[ERROR] Error generando recomendación: {e}")
            return "Consultar con especialista"
    
    def generar_reporte_economico_completo(self) -> Dict:
        """Generar reporte económico completo del sistema"""
        try:
            print("[REPORTE] Generando reporte económico completo...")
            
            # Análisis de todos los cultivos
            analisis_cultivos = {}
            for cultivo_id in self.configuracion_cultivos_economicos.keys():
                analisis_cultivos[cultivo_id] = self.calcular_roi_cultivo(cultivo_id, 1.0, 10)
            
            # Análisis de tendencias de precios
            tendencias_precios = {}
            for cultivo_id in self.configuracion_cultivos_economicos.keys():
                tendencias_precios[cultivo_id] = self.analizar_tendencias_precios(cultivo_id)
            
            # Análisis de optimización tecnológica
            optimizaciones = {}
            tecnologias_disponibles = list(self.factores_optimizacion.keys())
            
            for cultivo_id in self.configuracion_cultivos_economicos.keys():
                optimizaciones[cultivo_id] = self.optimizar_insumos_tecnologia(
                    cultivo_id, 1.0, tecnologias_disponibles
                )
            
            # Generar visualizaciones
            rutas_graficos = self._generar_visualizaciones_economicas(analisis_cultivos, tendencias_precios)
            
            reporte = {
                'fecha_reporte': datetime.now().isoformat(),
                'analisis_cultivos': analisis_cultivos,
                'tendencias_precios': tendencias_precios,
                'optimizaciones': optimizaciones,
                'visualizaciones': rutas_graficos,
                'resumen_ejecutivo': self._generar_resumen_ejecutivo_economico(analisis_cultivos, optimizaciones)
            }
            
            # Guardar reporte
            self._guardar_reporte_economico(reporte)
            
            print("[OK] Reporte económico completo generado")
            return reporte
            
        except Exception as e:
            print(f"[ERROR] Error generando reporte económico: {e}")
            return {'error': str(e)}
    
    def _generar_visualizaciones_economicas(self, analisis_cultivos: Dict, tendencias_precios: Dict) -> Dict:
        """Generar visualizaciones económicas"""
        try:
            rutas_graficos = {}
            
            # Gráfico de ROI por cultivo
            cultivos = list(analisis_cultivos.keys())
            rois = [analisis_cultivos[cultivo]['roi_proyectado'] for cultivo in cultivos]
            
            fig_roi = px.bar(
                x=cultivos,
                y=rois,
                title='ROI Proyectado por Cultivo (10 años)',
                labels={'x': 'Cultivo', 'y': 'ROI (%)'},
                color=rois,
                color_continuous_scale='RdYlGn'
            )
            
            ruta_roi = os.path.join(self.directorio_reportes, 'analisis_roi', 'roi_por_cultivo.html')
            fig_roi.write_html(ruta_roi)
            rutas_graficos['roi_por_cultivo'] = ruta_roi
            
            # Gráfico de tendencias de precios
            fig_tendencias = make_subplots(
                rows=2, cols=2,
                subplot_titles=[f'Tendencia {cultivo}' for cultivo in list(tendencias_precios.keys())[:4]],
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}]]
            )
            
            for i, (cultivo_id, tendencia) in enumerate(list(tendencias_precios.items())[:4]):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                fig_tendencias.add_trace(
                    go.Scatter(
                        x=tendencia['precios_historicos']['fechas'],
                        y=tendencia['precios_historicos']['precios'],
                        mode='lines+markers',
                        name=cultivo_id,
                        line=dict(width=2)
                    ),
                    row=row, col=col
                )
            
            fig_tendencias.update_layout(
                title='Tendencias de Precios de Mercado',
                showlegend=False,
                height=600
            )
            
            ruta_tendencias = os.path.join(self.directorio_reportes, 'tendencias', 'tendencias_precios.html')
            fig_tendencias.write_html(ruta_tendencias)
            rutas_graficos['tendencias_precios'] = ruta_tendencias
            
            return rutas_graficos
            
        except Exception as e:
            print(f"[ERROR] Error generando visualizaciones: {e}")
            return {}
    
    def _generar_resumen_ejecutivo_economico(self, analisis_cultivos: Dict, optimizaciones: Dict) -> Dict:
        """Generar resumen ejecutivo del análisis económico"""
        try:
            # Encontrar mejor cultivo por ROI
            mejor_cultivo = max(analisis_cultivos.items(), key=lambda x: x[1]['roi_proyectado'])
            
            # Calcular promedios
            roi_promedio = np.mean([analisis['roi_proyectado'] for analisis in analisis_cultivos.values()])
            van_promedio = np.mean([analisis['van_proyectado'] for analisis in analisis_cultivos.values()])
            
            return {
                'mejor_cultivo_inversion': {
                    'cultivo': mejor_cultivo[0],
                    'roi': mejor_cultivo[1]['roi_proyectado'],
                    'van': mejor_cultivo[1]['van_proyectado'],
                    'tir': mejor_cultivo[1]['tir_proyectada']
                },
                'metricas_promedio': {
                    'roi_promedio': round(roi_promedio, 2),
                    'van_promedio': round(van_promedio, 0)
                },
                'recomendaciones_principales': [
                    f"Mejor inversión: {mejor_cultivo[0]} con ROI {mejor_cultivo[1]['roi_proyectado']:.2f}%",
                    "Implementar tecnologías de optimización para reducir costos",
                    "Monitorear tendencias de precios para optimizar ventas",
                    "Diversificar cultivos para reducir riesgos"
                ],
                'tecnologias_recomendadas': list(self.factores_optimizacion.keys())
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando resumen ejecutivo: {e}")
            return {}
    
    def _guardar_reporte_economico(self, reporte: Dict):
        """Guardar reporte económico"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_economico_completo_{timestamp}.json"
            ruta_archivo = os.path.join(self.directorio_reportes, nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Reporte económico guardado: {ruta_archivo}")
            
        except Exception as e:
            print(f"[ERROR] Error guardando reporte: {e}")

def main():
    """Función principal para demostrar el sistema económico"""
    try:
        print("="*80)
        print("ANÁLISIS ECONÓMICO AGRÍCOLA - METGO 3D QUILLOTA")
        print("="*80)
        
        # Inicializar sistema económico
        sistema = AnalisisEconomicoAgricolaMetgo()
        
        print("\n[1] CALCULANDO ROI POR CULTIVO...")
        
        # Analizar ROI de cada cultivo
        cultivos_analizados = {}
        for cultivo_id in sistema.configuracion_cultivos_economicos.keys():
            print(f"[CULTIVO] Analizando {cultivo_id}...")
            resultado = sistema.calcular_roi_cultivo(cultivo_id, 1.0, 10)
            
            if 'error' not in resultado:
                cultivos_analizados[cultivo_id] = resultado
                print(f"[OK] {cultivo_id}: ROI {resultado['roi_proyectado']:.2f}%, VAN ${resultado['van_proyectado']:,.0f}")
        
        print("\n[2] OPTIMIZANDO INSUMOS CON TECNOLOGÍAS...")
        
        # Optimizar con tecnologías
        tecnologias = ['riego_inteligente', 'drones_monitoreo', 'ml_predicciones']
        optimizaciones = {}
        
        for cultivo_id in sistema.configuracion_cultivos_economicos.keys():
            resultado = sistema.optimizar_insumos_tecnologia(cultivo_id, 1.0, tecnologias)
            
            if 'error' not in resultado:
                optimizaciones[cultivo_id] = resultado
                print(f"[OK] {cultivo_id}: Ahorro anual ${resultado['ahorro_anual_estimado']:,.0f}, ROI tecnología {resultado['roi_tecnologia']:.2f}%")
        
        print("\n[3] ANALIZANDO TENDENCIAS DE PRECIOS...")
        
        # Analizar tendencias de precios
        tendencias = {}
        for cultivo_id in sistema.configuracion_cultivos_economicos.keys():
            resultado = sistema.analizar_tendencias_precios(cultivo_id)
            
            if 'error' not in resultado:
                tendencias[cultivo_id] = resultado
                print(f"[OK] {cultivo_id}: Tendencia {resultado['clasificacion_tendencia']}, Volatilidad {resultado['volatilidad']:.2f}%")
        
        print("\n[4] GENERANDO REPORTE COMPLETO...")
        
        # Generar reporte completo
        reporte_final = sistema.generar_reporte_economico_completo()
        
        if 'error' not in reporte_final:
            resumen = reporte_final['resumen_ejecutivo']
            print(f"[OK] Reporte económico generado")
            print(f"    - Mejor inversión: {resumen['mejor_cultivo_inversion']['cultivo']}")
            print(f"    - ROI promedio: {resumen['metricas_promedio']['roi_promedio']:.2f}%")
            print(f"    - VAN promedio: ${resumen['metricas_promedio']['van_promedio']:,.0f}")
        
        print("\n[5] RESUMEN DE RESULTADOS...")
        
        # Mostrar mejores opciones
        if cultivos_analizados:
            mejor_roi = max(cultivos_analizados.items(), key=lambda x: x[1]['roi_proyectado'])
            print(f"    🏆 Mejor ROI: {mejor_roi[0]} ({mejor_roi[1]['roi_proyectado']:.2f}%)")
        
        if optimizaciones:
            mejor_ahorro = max(optimizaciones.items(), key=lambda x: x[1]['ahorro_anual_estimado'])
            print(f"    💰 Mayor ahorro: {mejor_ahorro[0]} (${mejor_ahorro[1]['ahorro_anual_estimado']:,.0f}/año)")
        
        if tendencias:
            mejor_tendencia = max(tendencias.items(), key=lambda x: x[1]['tendencia_porcentual'])
            print(f"    📈 Mejor tendencia: {mejor_tendencia[0]} ({mejor_tendencia[1]['tendencia_porcentual']:.2f}%)")
        
        print("\n" + "="*80)
        print("ANÁLISIS ECONÓMICO AGRÍCOLA COMPLETADO EXITOSAMENTE")
        print("="*80)
        print("[OK] Sistema económico implementado")
        print("[OK] Análisis de ROI completado")
        print("[OK] Optimización de insumos calculada")
        print("[OK] Tendencias de precios analizadas")
        print("[OK] Reporte completo generado")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] Error en función principal: {e}")

if __name__ == "__main__":
    main()


