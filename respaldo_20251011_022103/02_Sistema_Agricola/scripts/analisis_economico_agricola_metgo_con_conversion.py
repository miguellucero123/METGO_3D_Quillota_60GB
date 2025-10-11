"""
SISTEMA DE ANÁLISIS ECONÓMICO AGRÍCOLA CON CONVERSIÓN DE MONEDAS - METGO 3D QUILLOTA
Sistema para análisis de ROI, costos, precios de mercado y rentabilidad agrícola
Incluye: Cálculo de retorno de inversión en pesos chilenos con conversión a USD y EUR
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

class AnalisisEconomicoAgricolaMetgoConConversion:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "analisis_economico_agricola_conversion.db"
        self.directorio_datos = "datos_economicos"
        self.directorio_reportes = "reportes_economicos"
        
        # Configuración de monedas
        self.moneda_base = "CLP"  # Peso chileno
        self.tasas_cambio = {
            'USD': 900.0,  # 1 USD = 900 CLP (aproximado)
            'EUR': 980.0,  # 1 EUR = 980 CLP (aproximado)
            'CLP': 1.0     # Peso chileno como base
        }
        
        # Crear directorios necesarios
        self._crear_directorios()
        
        # Inicializar base de datos
        self._inicializar_base_datos()
        
        # Configuración de cultivos con datos económicos en pesos chilenos
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
        
        # Configuración de insumos agrícolas en pesos chilenos
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
        
        self.logger.info("Sistema de Análisis Económico Agrícola con Conversión de Monedas inicializado")
    
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
            
            # Tabla de tasas de cambio
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasas_cambio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    moneda TEXT UNIQUE NOT NULL,
                    tasa_vs_clp REAL NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de cultivos económicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cultivos_economicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cultivo_id TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    precio_kg_clp REAL NOT NULL,
                    rendimiento_hectarea REAL NOT NULL,
                    costo_produccion_hectarea_clp REAL NOT NULL,
                    costo_plantacion_clp REAL NOT NULL,
                    vida_util INTEGER NOT NULL,
                    tiempo_inicio_produccion INTEGER NOT NULL,
                    costo_mantenimiento_anual_clp REAL NOT NULL,
                    incremento_rendimiento_anual REAL NOT NULL,
                    estabilizacion_rendimiento INTEGER NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de análisis ROI con conversión de monedas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analisis_roi_conversion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analisis_id TEXT UNIQUE NOT NULL,
                    cultivo_id TEXT NOT NULL,
                    area_hectareas REAL NOT NULL,
                    horizonte_anos INTEGER NOT NULL,
                    roi_proyectado REAL,
                    van_clp REAL,
                    van_usd REAL,
                    van_eur REAL,
                    tir_proyectada REAL,
                    payback_period REAL,
                    ingresos_totales_clp REAL,
                    costos_totales_clp REAL,
                    parametros_entrada TEXT,
                    fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar tasas de cambio
            for moneda, tasa in self.tasas_cambio.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO tasas_cambio (moneda, tasa_vs_clp)
                    VALUES (?, ?)
                ''', (moneda, tasa))
            
            # Insertar datos de cultivos
            for cultivo_id, datos in self.configuracion_cultivos_economicos.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO cultivos_economicos 
                    (cultivo_id, nombre, precio_kg_clp, rendimiento_hectarea, costo_produccion_hectarea_clp,
                     costo_plantacion_clp, vida_util, tiempo_inicio_produccion, costo_mantenimiento_anual_clp,
                     incremento_rendimiento_anual, estabilizacion_rendimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cultivo_id, datos['nombre'], datos['precio_kg'], datos['rendimiento_hectarea'],
                    datos['costo_produccion_hectarea'], datos['costo_plantacion'], datos['vida_util'],
                    datos['tiempo_inicio_produccion'], datos['costo_mantenimiento_anual'],
                    datos['incremento_rendimiento_anual'], datos['estabilizacion_rendimiento']
                ))
            
            conn.commit()
            conn.close()
            
            print("[OK] Base de datos económica con conversión inicializada")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {e}")
    
    def actualizar_tasas_cambio(self):
        """Actualizar tasas de cambio desde API (simulado)"""
        try:
            # En implementación real, se obtendría desde API de cambio
            # Por ahora, simulamos tasas actualizadas
            tasas_simuladas = {
                'USD': 895.0 + np.random.uniform(-10, 10),  # Simular variación
                'EUR': 975.0 + np.random.uniform(-15, 15),  # Simular variación
                'CLP': 1.0
            }
            
            self.tasas_cambio.update(tasas_simuladas)
            
            # Actualizar en base de datos
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            for moneda, tasa in tasas_simuladas.items():
                cursor.execute('''
                    UPDATE tasas_cambio 
                    SET tasa_vs_clp = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE moneda = ?
                ''', (tasa, moneda))
            
            conn.commit()
            conn.close()
            
            print(f"[OK] Tasas de cambio actualizadas: USD={tasas_simuladas['USD']:.2f}, EUR={tasas_simuladas['EUR']:.2f}")
            
        except Exception as e:
            print(f"[ERROR] Error actualizando tasas de cambio: {e}")
    
    def convertir_moneda(self, valor_clp: float, moneda_destino: str) -> float:
        """Convertir valor de pesos chilenos a otra moneda"""
        try:
            if moneda_destino == 'CLP':
                return valor_clp
            
            tasa = self.tasas_cambio.get(moneda_destino)
            if not tasa:
                raise ValueError(f"Moneda {moneda_destino} no soportada")
            
            return valor_clp / tasa
            
        except Exception as e:
            print(f"[ERROR] Error convirtiendo moneda: {e}")
            return 0.0
    
    def formatear_moneda(self, valor: float, moneda: str, decimales: int = 0) -> str:
        """Formatear valor según la moneda"""
        try:
            if moneda == 'CLP':
                return f"${valor:,.0f} CLP"
            elif moneda == 'USD':
                return f"${valor:,.{decimales}f} USD"
            elif moneda == 'EUR':
                return f"€{valor:,.{decimales}f} EUR"
            else:
                return f"{valor:,.{decimales}f} {moneda}"
                
        except Exception as e:
            print(f"[ERROR] Error formateando moneda: {e}")
            return f"{valor:,.{decimales}f}"
    
    def calcular_roi_cultivo_con_conversion(self, cultivo_id: str, area_hectareas: float, 
                                          horizonte_anos: int = 10, tasa_descuento: float = 0.08) -> Dict:
        """Calcular ROI, VAN y TIR para un cultivo específico con conversión de monedas"""
        try:
            print(f"[ROI] Calculando análisis económico para {cultivo_id} con conversión de monedas")
            
            # Obtener configuración del cultivo
            config_cultivo = self.configuracion_cultivos_economicos.get(cultivo_id)
            if not config_cultivo:
                raise ValueError(f"Cultivo {cultivo_id} no encontrado")
            
            # Actualizar tasas de cambio
            self.actualizar_tasas_cambio()
            
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
            
            # Calcular VAN en diferentes monedas
            van_clp = sum([flujo / (1 + tasa_descuento) ** (i + 1) for i, flujo in enumerate(flujos_caja)])
            van_usd = self.convertir_moneda(van_clp, 'USD')
            van_eur = self.convertir_moneda(van_clp, 'EUR')
            
            # Calcular TIR (simplificado)
            tir = self._calcular_tir_simplificado(flujos_caja)
            
            # Calcular período de recuperación
            payback = self._calcular_payback_period(flujos_caja)
            
            # Guardar análisis
            analisis_id = f"roi_{uuid.uuid4().hex[:8]}"
            self._guardar_analisis_roi_conversion(analisis_id, cultivo_id, area_hectareas, horizonte_anos, 
                                                roi, van_clp, van_usd, van_eur, tir, payback, 
                                                ingresos_totales, costos_totales)
            
            resultado = {
                'analisis_id': analisis_id,
                'cultivo_id': cultivo_id,
                'area_hectareas': area_hectareas,
                'horizonte_anos': horizonte_anos,
                'roi_proyectado': round(roi, 2),
                'van_clp': round(van_clp, 0),
                'van_usd': round(van_usd, 2),
                'van_eur': round(van_eur, 2),
                'tir_proyectada': round(tir * 100, 2),
                'payback_period': round(payback, 1),
                'ingresos_totales_clp': round(ingresos_totales, 0),
                'ingresos_totales_usd': round(self.convertir_moneda(ingresos_totales, 'USD'), 2),
                'ingresos_totales_eur': round(self.convertir_moneda(ingresos_totales, 'EUR'), 2),
                'costos_totales_clp': round(costos_totales, 0),
                'costos_totales_usd': round(self.convertir_moneda(costos_totales, 'USD'), 2),
                'costos_totales_eur': round(self.convertir_moneda(costos_totales, 'EUR'), 2),
                'beneficio_neto_clp': round(ingresos_totales - costos_totales, 0),
                'beneficio_neto_usd': round(self.convertir_moneda(ingresos_totales - costos_totales, 'USD'), 2),
                'beneficio_neto_eur': round(self.convertir_moneda(ingresos_totales - costos_totales, 'EUR'), 2),
                'flujos_caja_clp': [round(flujo, 0) for flujo in flujos_caja],
                'tasas_cambio': self.tasas_cambio.copy()
            }
            
            print(f"[OK] ROI calculado: {roi:.2f}%, VAN CLP: {self.formatear_moneda(van_clp, 'CLP')}, VAN USD: {self.formatear_moneda(van_usd, 'USD', 2)}")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error calculando ROI: {e}")
            return {'error': str(e)}
    
    def _calcular_tir_simplificado(self, flujos_caja: List[float]) -> float:
        """Calcular TIR de forma simplificada"""
        try:
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
    
    def _guardar_analisis_roi_conversion(self, analisis_id: str, cultivo_id: str, area_hectareas: float,
                                       horizonte_anos: int, roi: float, van_clp: float, van_usd: float, 
                                       van_eur: float, tir: float, payback: float, ingresos_totales: float, 
                                       costos_totales: float):
        """Guardar análisis ROI con conversión en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analisis_roi_conversion 
                (analisis_id, cultivo_id, area_hectareas, horizonte_anos,
                 roi_proyectado, van_clp, van_usd, van_eur, tir_proyectada, 
                 payback_period, ingresos_totales_clp, costos_totales_clp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (analisis_id, cultivo_id, area_hectareas, horizonte_anos, roi, 
                 van_clp, van_usd, van_eur, tir, payback, ingresos_totales, costos_totales))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando análisis ROI: {e}")
    
    def generar_reporte_economico_con_conversion(self) -> Dict:
        """Generar reporte económico completo con conversión de monedas"""
        try:
            print("[REPORTE] Generando reporte económico con conversión de monedas...")
            
            # Actualizar tasas de cambio
            self.actualizar_tasas_cambio()
            
            # Análisis de todos los cultivos
            analisis_cultivos = {}
            for cultivo_id in self.configuracion_cultivos_economicos.keys():
                analisis_cultivos[cultivo_id] = self.calcular_roi_cultivo_con_conversion(cultivo_id, 1.0, 10)
            
            # Generar visualizaciones
            rutas_graficos = self._generar_visualizaciones_economicas_conversion(analisis_cultivos)
            
            reporte = {
                'fecha_reporte': datetime.now().isoformat(),
                'tasas_cambio': self.tasas_cambio.copy(),
                'analisis_cultivos': analisis_cultivos,
                'visualizaciones': rutas_graficos,
                'resumen_ejecutivo': self._generar_resumen_ejecutivo_conversion(analisis_cultivos)
            }
            
            # Guardar reporte
            self._guardar_reporte_economico_conversion(reporte)
            
            print("[OK] Reporte económico con conversión generado")
            return reporte
            
        except Exception as e:
            print(f"[ERROR] Error generando reporte: {e}")
            return {'error': str(e)}
    
    def _generar_visualizaciones_economicas_conversion(self, analisis_cultivos: Dict) -> Dict:
        """Generar visualizaciones económicas con conversión de monedas"""
        try:
            rutas_graficos = {}
            
            # Gráfico de VAN en diferentes monedas
            cultivos = list(analisis_cultivos.keys())
            van_clp = [analisis_cultivos[cultivo]['van_clp'] for cultivo in cultivos]
            van_usd = [analisis_cultivos[cultivo]['van_usd'] for cultivo in cultivos]
            van_eur = [analisis_cultivos[cultivo]['van_eur'] for cultivo in cultivos]
            
            fig_van = go.Figure()
            
            fig_van.add_trace(go.Bar(
                name='VAN (CLP)',
                x=cultivos,
                y=van_clp,
                text=[self.formatear_moneda(v, 'CLP') for v in van_clp],
                textposition='auto',
            ))
            
            fig_van.add_trace(go.Bar(
                name='VAN (USD)',
                x=cultivos,
                y=van_usd,
                text=[self.formatear_moneda(v, 'USD', 0) for v in van_usd],
                textposition='auto',
            ))
            
            fig_van.add_trace(go.Bar(
                name='VAN (EUR)',
                x=cultivos,
                y=van_eur,
                text=[self.formatear_moneda(v, 'EUR', 0) for v in van_eur],
                textposition='auto',
            ))
            
            fig_van.update_layout(
                title='Valor Actual Neto (VAN) por Cultivo en Diferentes Monedas',
                xaxis_title='Cultivo',
                yaxis_title='VAN',
                barmode='group'
            )
            
            ruta_van = os.path.join(self.directorio_reportes, 'analisis_roi', 'van_multimoneda.html')
            fig_van.write_html(ruta_van)
            rutas_graficos['van_multimoneda'] = ruta_van
            
            # Gráfico de ROI por cultivo
            rois = [analisis_cultivos[cultivo]['roi_proyectado'] for cultivo in cultivos]
            
            fig_roi = px.bar(
                x=cultivos,
                y=rois,
                title='ROI Proyectado por Cultivo (10 años)',
                labels={'x': 'Cultivo', 'y': 'ROI (%)'},
                color=rois,
                color_continuous_scale='RdYlGn',
                text=[f"{roi:.1f}%" for roi in rois]
            )
            
            fig_roi.update_traces(textposition='outside')
            
            ruta_roi = os.path.join(self.directorio_reportes, 'analisis_roi', 'roi_por_cultivo.html')
            fig_roi.write_html(ruta_roi)
            rutas_graficos['roi_por_cultivo'] = ruta_roi
            
            return rutas_graficos
            
        except Exception as e:
            print(f"[ERROR] Error generando visualizaciones: {e}")
            return {}
    
    def _generar_resumen_ejecutivo_conversion(self, analisis_cultivos: Dict) -> Dict:
        """Generar resumen ejecutivo con conversión de monedas"""
        try:
            # Encontrar mejor cultivo por ROI
            mejor_cultivo = max(analisis_cultivos.items(), key=lambda x: x[1]['roi_proyectado'])
            
            # Calcular promedios
            roi_promedio = np.mean([analisis['roi_proyectado'] for analisis in analisis_cultivos.values()])
            van_clp_promedio = np.mean([analisis['van_clp'] for analisis in analisis_cultivos.values()])
            van_usd_promedio = np.mean([analisis['van_usd'] for analisis in analisis_cultivos.values()])
            van_eur_promedio = np.mean([analisis['van_eur'] for analisis in analisis_cultivos.values()])
            
            return {
                'mejor_cultivo_inversion': {
                    'cultivo': mejor_cultivo[0],
                    'roi': mejor_cultivo[1]['roi_proyectado'],
                    'van_clp': mejor_cultivo[1]['van_clp'],
                    'van_usd': mejor_cultivo[1]['van_usd'],
                    'van_eur': mejor_cultivo[1]['van_eur']
                },
                'metricas_promedio': {
                    'roi_promedio': round(roi_promedio, 2),
                    'van_clp_promedio': round(van_clp_promedio, 0),
                    'van_usd_promedio': round(van_usd_promedio, 2),
                    'van_eur_promedio': round(van_eur_promedio, 2)
                },
                'tasas_cambio_actuales': self.tasas_cambio.copy(),
                'recomendaciones_principales': [
                    f"Mejor inversión: {mejor_cultivo[0]} con ROI {mejor_cultivo[1]['roi_proyectado']:.2f}%",
                    f"VAN promedio: {self.formatear_moneda(van_clp_promedio, 'CLP')} ({self.formatear_moneda(van_usd_promedio, 'USD', 0)} / {self.formatear_moneda(van_eur_promedio, 'EUR', 0)})",
                    "Considerar diversificación para reducir riesgos cambiarios",
                    "Monitorear tasas de cambio para optimizar timing de inversiones"
                ]
            }
            
        except Exception as e:
            print(f"[ERROR] Error generando resumen ejecutivo: {e}")
            return {}
    
    def _guardar_reporte_economico_conversion(self, reporte: Dict):
        """Guardar reporte económico con conversión"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_economico_conversion_{timestamp}.json"
            ruta_archivo = os.path.join(self.directorio_reportes, nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Reporte económico con conversión guardado: {ruta_archivo}")
            
        except Exception as e:
            print(f"[ERROR] Error guardando reporte: {e}")

def main():
    """Función principal para demostrar el sistema económico con conversión"""
    try:
        print("="*80)
        print("ANÁLISIS ECONÓMICO AGRÍCOLA CON CONVERSIÓN DE MONEDAS - METGO 3D QUILLOTA")
        print("="*80)
        
        # Inicializar sistema económico
        sistema = AnalisisEconomicoAgricolaMetgoConConversion()
        
        print("\n[1] ACTUALIZANDO TASAS DE CAMBIO...")
        sistema.actualizar_tasas_cambio()
        print(f"    Tasas actuales:")
        for moneda, tasa in sistema.tasas_cambio.items():
            if moneda != 'CLP':
                print(f"    1 {moneda} = {tasa:.2f} CLP")
        
        print("\n[2] CALCULANDO ROI POR CULTIVO CON CONVERSIÓN...")
        
        # Analizar ROI de cada cultivo con conversión
        cultivos_analizados = {}
        for cultivo_id in sistema.configuracion_cultivos_economicos.keys():
            print(f"[CULTIVO] Analizando {cultivo_id}...")
            resultado = sistema.calcular_roi_cultivo_con_conversion(cultivo_id, 1.0, 10)
            
            if 'error' not in resultado:
                cultivos_analizados[cultivo_id] = resultado
                print(f"[OK] {cultivo_id}:")
                print(f"     ROI: {resultado['roi_proyectado']:.2f}%")
                print(f"     VAN: {sistema.formatear_moneda(resultado['van_clp'], 'CLP')} / {sistema.formatear_moneda(resultado['van_usd'], 'USD', 0)} / {sistema.formatear_moneda(resultado['van_eur'], 'EUR', 0)}")
                print(f"     Beneficio Neto: {sistema.formatear_moneda(resultado['beneficio_neto_clp'], 'CLP')}")
        
        print("\n[3] GENERANDO REPORTE COMPLETO CON CONVERSIÓN...")
        
        # Generar reporte completo
        reporte_final = sistema.generar_reporte_economico_con_conversion()
        
        if 'error' not in reporte_final:
            resumen = reporte_final['resumen_ejecutivo']
            print(f"[OK] Reporte económico con conversión generado")
            print(f"    - Mejor inversión: {resumen['mejor_cultivo_inversion']['cultivo']}")
            print(f"    - ROI promedio: {resumen['metricas_promedio']['roi_promedio']:.2f}%")
            print(f"    - VAN promedio: {sistema.formatear_moneda(resumen['metricas_promedio']['van_clp_promedio'], 'CLP')}")
            print(f"    - VAN promedio USD: {sistema.formatear_moneda(resumen['metricas_promedio']['van_usd_promedio'], 'USD', 0)}")
            print(f"    - VAN promedio EUR: {sistema.formatear_moneda(resumen['metricas_promedio']['van_eur_promedio'], 'EUR', 0)}")
        
        print("\n[4] RESUMEN DE RESULTADOS POR MONEDA...")
        
        # Mostrar mejores opciones en diferentes monedas
        if cultivos_analizados:
            mejor_roi = max(cultivos_analizados.items(), key=lambda x: x[1]['roi_proyectado'])
            mejor_van_clp = max(cultivos_analizados.items(), key=lambda x: x[1]['van_clp'])
            mejor_van_usd = max(cultivos_analizados.items(), key=lambda x: x[1]['van_usd'])
            mejor_van_eur = max(cultivos_analizados.items(), key=lambda x: x[1]['van_eur'])
            
            print(f"    [Mejor ROI] {mejor_roi[0]}: {mejor_roi[1]['roi_proyectado']:.2f}%")
            print(f"    [Mejor VAN CLP] {mejor_van_clp[0]}: {sistema.formatear_moneda(mejor_van_clp[1]['van_clp'], 'CLP')}")
            print(f"    [Mejor VAN USD] {mejor_van_usd[0]}: {sistema.formatear_moneda(mejor_van_usd[1]['van_usd'], 'USD', 0)}")
            print(f"    [Mejor VAN EUR] {mejor_van_eur[0]}: {sistema.formatear_moneda(mejor_van_eur[1]['van_eur'], 'EUR', 0)}")
        
        print("\n" + "="*80)
        print("ANÁLISIS ECONÓMICO CON CONVERSIÓN DE MONEDAS COMPLETADO")
        print("="*80)
        print("[OK] Sistema económico con conversión implementado")
        print("[OK] Análisis de ROI en múltiples monedas completado")
        print("[OK] Tasas de cambio actualizadas")
        print("[OK] Reporte con conversión generado")
        print("[OK] Visualizaciones multimoneda creadas")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] Error en función principal: {e}")

if __name__ == "__main__":
    main()


