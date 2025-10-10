"""
SISTEMA DE RECOMENDACIONES AGRÍCOLAS AVANZADO - METGO 3D QUILLOTA
Sistema sofisticado para recomendaciones de heladas, cosechas y plagas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
import logging

class SistemaRecomendacionesAvanzado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.estaciones_meteorologicas = self._cargar_estaciones_quillota()
        self.cultivos_quillota = self._cargar_cultivos_quillota()
        self.plagas_quillota = self._cargar_plagas_quillota()
        self.estaciones_heladas = self._configurar_estaciones_heladas()
        
    def _cargar_estaciones_quillota(self) -> Dict:
        """Cargar configuración de estaciones meteorológicas del Valle de Quillota"""
        return {
            "quillota_centro": {
                "nombre": "Quillota Centro",
                "coordenadas": {"lat": -32.8833, "lon": -71.2667},
                "altitud": 462,
                "sector": "centro_valle",
                "cultivos_principales": ["paltos", "citricos", "vides"],
                "riesgo_helada": "medio"
            },
            "la_cruz": {
                "nombre": "La Cruz",
                "coordenadas": {"lat": -32.8167, "lon": -71.2167},
                "altitud": 380,
                "sector": "valle_bajo",
                "cultivos_principales": ["paltos", "citricos"],
                "riesgo_helada": "bajo"
            },
            "nogueira": {
                "nombre": "Nogales",
                "coordenadas": {"lat": -32.9333, "lon": -71.2167},
                "altitud": 520,
                "sector": "valle_medio",
                "cultivos_principales": ["vides", "paltos", "citricos"],
                "riesgo_helada": "medio_alto"
            },
            "colliguay": {
                "nombre": "Colliguay",
                "coordenadas": {"lat": -32.9500, "lon": -71.1833},
                "altitud": 680,
                "sector": "valle_alto",
                "cultivos_principales": ["vides", "frutales_templados"],
                "riesgo_helada": "alto"
            },
            "hijuelas": {
                "nombre": "Hijuelas",
                "coordenadas": {"lat": -32.7833, "lon": -71.1500},
                "altitud": 420,
                "sector": "valle_bajo",
                "cultivos_principales": ["paltos", "citricos", "vides"],
                "riesgo_helada": "medio"
            },
            "calera": {
                "nombre": "La Calera",
                "coordenadas": {"lat": -32.7833, "lon": -71.2167},
                "altitud": 400,
                "sector": "valle_bajo",
                "cultivos_principales": ["citricos", "paltos"],
                "riesgo_helada": "bajo"
            }
        }
    
    def _cargar_cultivos_quillota(self) -> Dict:
        """Cargar información detallada de cultivos del Valle de Quillota"""
        return {
            "paltos": {
                "nombre": "Palta Hass",
                "temporada_plantacion": "septiembre_noviembre",
                "temporada_cosecha": "abril_julio",
                "temperatura_optima": {"min": 10, "max": 35},
                "humedad_optima": {"min": 60, "max": 80},
                "suelo_optimo": "franco_arenoso",
                "ph_optimo": {"min": 6.0, "max": 7.0},
                "riego_requerido": "alto",
                "sensibilidad_helada": "alta",
                "temperatura_critica_helada": 0,
                "dias_maduracion": 180,
                "rendimiento_esperado": "15-25 ton/ha",
                "precio_mercado": "alto",
                "estaciones_aptas": ["quillota_centro", "la_cruz", "nogueira", "hijuelas", "calera"]
            },
            "citricos": {
                "nombre": "Cítricos (Naranjas, Limones)",
                "temporada_plantacion": "marzo_mayo",
                "temporada_cosecha": "mayo_septiembre",
                "temperatura_optima": {"min": 12, "max": 32},
                "humedad_optima": {"min": 65, "max": 85},
                "suelo_optimo": "franco_arcilloso",
                "ph_optimo": {"min": 5.5, "max": 6.5},
                "riego_requerido": "medio_alto",
                "sensibilidad_helada": "media",
                "temperatura_critica_helada": -2,
                "dias_maduracion": 240,
                "rendimiento_esperado": "30-50 ton/ha",
                "precio_mercado": "medio",
                "estaciones_aptas": ["quillota_centro", "la_cruz", "hijuelas", "calera"]
            },
            "vides": {
                "nombre": "Vides (Uva de Mesa)",
                "temporada_plantacion": "julio_septiembre",
                "temporada_cosecha": "enero_abril",
                "temperatura_optima": {"min": 8, "max": 30},
                "humedad_optima": {"min": 50, "max": 70},
                "suelo_optimo": "franco_arenoso",
                "ph_optimo": {"min": 6.0, "max": 7.5},
                "riego_requerido": "medio",
                "sensibilidad_helada": "baja",
                "temperatura_critica_helada": -4,
                "dias_maduracion": 120,
                "rendimiento_esperado": "20-35 ton/ha",
                "precio_mercado": "alto",
                "estaciones_aptas": ["nogueira", "colliguay", "quillota_centro", "hijuelas"]
            },
            "frutales_templados": {
                "nombre": "Frutales Templados (Manzanas, Peras)",
                "temporada_plantacion": "junio_agosto",
                "temporada_cosecha": "febrero_mayo",
                "temperatura_optima": {"min": 5, "max": 25},
                "humedad_optima": {"min": 60, "max": 80},
                "suelo_optimo": "franco_arcilloso",
                "ph_optimo": {"min": 6.0, "max": 7.0},
                "riego_requerido": "medio",
                "sensibilidad_helada": "baja",
                "temperatura_critica_helada": -6,
                "dias_maduracion": 150,
                "rendimiento_esperado": "25-40 ton/ha",
                "precio_mercado": "medio",
                "estaciones_aptas": ["colliguay", "nogueira"]
            }
        }
    
    def _cargar_plagas_quillota(self) -> Dict:
        """Cargar información de plagas comunes en Quillota"""
        return {
            "araña_roja": {
                "nombre": "Araña Roja (Tetranychus urticae)",
                "cultivos_afectados": ["paltos", "citricos", "vides"],
                "condiciones_favorables": {
                    "temperatura": {"min": 25, "max": 35},
                    "humedad": {"min": 30, "max": 60},
                    "estacion": "verano_otono"
                },
                "sintomas": "Hojas amarillentas, telarañas finas, caída prematura de hojas",
                "daño_economico": "alto",
                "tratamiento": {
                    "preventivo": "Riego foliar, control biológico con Phytoseiulus",
                    "curativo": "Acaricidas específicos, azufre micronizado"
                },
                "umbral_alerta": {
                    "temperatura": 28,
                    "humedad": 50
                }
            },
            "pulgon": {
                "nombre": "Pulgón (Aphis spp.)",
                "cultivos_afectados": ["paltos", "citricos", "vides"],
                "condiciones_favorables": {
                    "temperatura": {"min": 15, "max": 25},
                    "humedad": {"min": 60, "max": 80},
                    "estacion": "primavera_verano"
                },
                "sintomas": "Enrollamiento de hojas, melaza, fumagina",
                "daño_economico": "medio",
                "tratamiento": {
                    "preventivo": "Control biológico con mariquitas, trampas amarillas",
                    "curativo": "Insecticidas sistémicos, jabón potásico"
                },
                "umbral_alerta": {
                    "temperatura": 20,
                    "humedad": 70
                }
            },
            "mosca_blanca": {
                "nombre": "Mosca Blanca (Bemisia tabaci)",
                "cultivos_afectados": ["paltos", "citricos"],
                "condiciones_favorables": {
                    "temperatura": {"min": 22, "max": 30},
                    "humedad": {"min": 50, "max": 70},
                    "estacion": "verano"
                },
                "sintomas": "Amarillamiento de hojas, melaza, fumagina",
                "daño_economico": "alto",
                "tratamiento": {
                    "preventivo": "Trampas amarillas, control biológico",
                    "curativo": "Insecticidas específicos, aceites minerales"
                },
                "umbral_alerta": {
                    "temperatura": 26,
                    "humedad": 60
                }
            },
            "tizón_tardío": {
                "nombre": "Tizón Tardío (Phytophthora infestans)",
                "cultivos_afectados": ["vides", "frutales_templados"],
                "condiciones_favorables": {
                    "temperatura": {"min": 10, "max": 20},
                    "humedad": {"min": 80, "max": 95},
                    "estacion": "otono_invierno"
                },
                "sintomas": "Manchas oscuras en hojas, pudrición de frutos",
                "daño_economico": "muy_alto",
                "tratamiento": {
                    "preventivo": "Fungicidas cúpricos, buena ventilación",
                    "curativo": "Fungicidas sistémicos, eliminación de material infectado"
                },
                "umbral_alerta": {
                    "temperatura": 15,
                    "humedad": 85
                }
            }
        }
    
    def _configurar_estaciones_heladas(self) -> Dict:
        """Configurar sistema de alertas de heladas por estación"""
        return {
            "umbrales_helada": {
                "leve": -1,      # Daño menor
                "moderada": -3,  # Daño significativo
                "severa": -5     # Daño severo
            },
            "tiempos_anticipacion": {
                "alerta_temprana": 72,    # 3 días
                "alerta_inmediata": 24,   # 1 día
                "alerta_critica": 6       # 6 horas
            },
            "medidas_proteccion": {
                "riego_aspersion": {
                    "efectividad": 85,
                    "costo": "medio",
                    "tiempo_instalacion": "2 horas",
                    "requisitos": "agua abundante, sistema de bombeo"
                },
                "calefactores": {
                    "efectividad": 90,
                    "costo": "alto",
                    "tiempo_instalacion": "1 hora",
                    "requisitos": "combustible, ventilación"
                },
                "cubiertas_plasticas": {
                    "efectividad": 75,
                    "costo": "medio",
                    "tiempo_instalacion": "4 horas",
                    "requisitos": "estructura de soporte"
                },
                "ventiladores": {
                    "efectividad": 60,
                    "costo": "bajo",
                    "tiempo_instalacion": "1 hora",
                    "requisitos": "energía eléctrica"
                }
            }
        }
    
    def analizar_riesgo_heladas(self, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Analizar riesgo de heladas para todas las estaciones"""
        analisis = {}
        
        for estacion_id, estacion_info in self.estaciones_meteorologicas.items():
            # Simular datos específicos para cada estación
            datos_estacion = self._simular_datos_estacion(datos_meteorologicos, estacion_info)
            
            # Calcular riesgo de helada
            riesgo = self._calcular_riesgo_helada(datos_estacion, estacion_info)
            
            # Generar recomendaciones
            recomendaciones = self._generar_recomendaciones_helada(riesgo, estacion_info)
            
            analisis[estacion_id] = {
                "estacion": estacion_info,
                "riesgo": riesgo,
                "recomendaciones": recomendaciones,
                "datos_actuales": datos_estacion.iloc[-1].to_dict() if not datos_estacion.empty else {}
            }
        
        return analisis
    
    def _simular_datos_estacion(self, datos_base: pd.DataFrame, estacion_info: Dict) -> pd.DataFrame:
        """Simular datos específicos para cada estación meteorológica"""
        datos_estacion = datos_base.copy()
        
        # Ajustar datos según altitud y ubicación
        factor_altitud = estacion_info["altitud"] / 462  # Quillota centro como referencia
        
        # Ajustar temperatura según altitud (gradiente de -0.6°C por cada 100m)
        ajuste_temp = (estacion_info["altitud"] - 462) * -0.006
        datos_estacion["temperatura"] += ajuste_temp
        datos_estacion["temperatura_min"] += ajuste_temp
        datos_estacion["temperatura_max"] += ajuste_temp
        
        # Ajustar humedad según sector
        if estacion_info["sector"] == "valle_alto":
            datos_estacion["humedad_relativa"] *= 1.1
        elif estacion_info["sector"] == "valle_bajo":
            datos_estacion["humedad_relativa"] *= 0.95
        
        return datos_estacion
    
    def _calcular_riesgo_helada(self, datos: pd.DataFrame, estacion_info: Dict) -> Dict:
        """Calcular nivel de riesgo de heladas"""
        if datos.empty:
            return {"nivel": "desconocido", "probabilidad": 0, "intensidad": "leve"}
        
        temp_min = datos["temperatura_min"].min()
        temp_actual = datos["temperatura_min"].iloc[-1]
        humedad = datos["humedad_relativa"].mean()
        
        # Calcular probabilidad de helada
        if temp_min <= -2:
            probabilidad = 90
            intensidad = "severa"
        elif temp_min <= 0:
            probabilidad = 70
            intensidad = "moderada"
        elif temp_min <= 2:
            probabilidad = 40
            intensidad = "leve"
        else:
            probabilidad = 10
            intensidad = "leve"
        
        # Ajustar según humedad
        if humedad > 80:
            probabilidad *= 0.8  # Menor riesgo con alta humedad
        elif humedad < 50:
            probabilidad *= 1.2  # Mayor riesgo con baja humedad
        
        # Determinar nivel de riesgo
        if probabilidad >= 70:
            nivel = "alto"
        elif probabilidad >= 40:
            nivel = "medio"
        elif probabilidad >= 20:
            nivel = "bajo"
        else:
            nivel = "muy_bajo"
        
        return {
            "nivel": nivel,
            "probabilidad": min(probabilidad, 100),
            "intensidad": intensidad,
            "temperatura_minima": temp_min,
            "temperatura_actual": temp_actual,
            "humedad_promedio": humedad,
            "tiempo_anticipacion": self._calcular_tiempo_anticipacion(probabilidad)
        }
    
    def _calcular_tiempo_anticipacion(self, probabilidad: float) -> str:
        """Calcular tiempo de anticipación según probabilidad"""
        if probabilidad >= 70:
            return "crítico"
        elif probabilidad >= 40:
            return "inmediato"
        elif probabilidad >= 20:
            return "temprano"
        else:
            return "monitoreo"
    
    def _generar_recomendaciones_helada(self, riesgo: Dict, estacion_info: Dict) -> List[Dict]:
        """Generar recomendaciones específicas para heladas"""
        recomendaciones = []
        
        if riesgo["nivel"] == "alto":
            # Recomendaciones críticas
            for medida, info in self.estaciones_heladas["medidas_proteccion"].items():
                recomendaciones.append({
                    "tipo": "crítico",
                    "medida": medida.replace("_", " ").title(),
                    "descripcion": f"Implementar {medida.replace('_', ' ')} inmediatamente",
                    "efectividad": info["efectividad"],
                    "costo": info["costo"],
                    "tiempo_instalacion": info["tiempo_instalacion"],
                    "prioridad": 1
                })
        
        elif riesgo["nivel"] == "medio":
            # Recomendaciones preventivas
            recomendaciones.extend([
                {
                    "tipo": "preventivo",
                    "medida": "Monitoreo Intensivo",
                    "descripcion": "Verificar condiciones cada 2 horas",
                    "prioridad": 1
                },
                {
                    "tipo": "preventivo",
                    "medida": "Preparar Sistemas",
                    "descripcion": "Tener listos sistemas de protección",
                    "prioridad": 2
                }
            ])
        
        # Recomendaciones específicas por cultivo
        for cultivo in estacion_info["cultivos_principales"]:
            cultivo_info = self.cultivos_quillota[cultivo]
            if riesgo["temperatura_minima"] <= cultivo_info["temperatura_critica_helada"]:
                recomendaciones.append({
                    "tipo": "específico",
                    "medida": f"Protección {cultivo_info['nombre']}",
                    "descripcion": f"Temperatura crítica alcanzada para {cultivo_info['nombre']}",
                    "cultivo": cultivo,
                    "temperatura_critica": cultivo_info["temperatura_critica_helada"],
                    "prioridad": 1
                })
        
        return recomendaciones
    
    def analizar_recomendaciones_cosecha(self, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Analizar y generar recomendaciones de cosecha"""
        recomendaciones = {}
        
        for cultivo_id, cultivo_info in self.cultivos_quillota.items():
            # Simular estado del cultivo
            estado_cultivo = self._simular_estado_cultivo(datos_meteorologicos, cultivo_info)
            
            # Generar recomendaciones específicas
            recs = self._generar_recomendaciones_cosecha_cultivo(estado_cultivo, cultivo_info)
            
            recomendaciones[cultivo_id] = {
                "cultivo": cultivo_info,
                "estado": estado_cultivo,
                "recomendaciones": recs
            }
        
        return recomendaciones
    
    def _simular_estado_cultivo(self, datos: pd.DataFrame, cultivo_info: Dict) -> Dict:
        """Simular estado actual del cultivo"""
        if datos.empty:
            return {"estado": "desconocido", "madurez": 0}
        
        # Calcular días desde plantación (simulado)
        dias_plantacion = 120  # Simulado
        
        # Calcular madurez
        madurez = min((dias_plantacion / cultivo_info["dias_maduracion"]) * 100, 100)
        
        # Determinar estado
        if madurez >= 90:
            estado = "listo_cosecha"
        elif madurez >= 70:
            estado = "cerca_cosecha"
        elif madurez >= 40:
            estado = "desarrollo"
        else:
            estado = "crecimiento_inicial"
        
        # Analizar condiciones meteorológicas
        temp_promedio = datos["temperatura"].mean()
        humedad_promedio = datos["humedad_relativa"].mean()
        precipitacion_total = datos["precipitacion"].sum()
        
        # Evaluar calidad
        calidad_temp = "excelente" if cultivo_info["temperatura_optima"]["min"] <= temp_promedio <= cultivo_info["temperatura_optima"]["max"] else "regular"
        calidad_humedad = "excelente" if cultivo_info["humedad_optima"]["min"] <= humedad_promedio <= cultivo_info["humedad_optima"]["max"] else "regular"
        
        return {
            "estado": estado,
            "madurez": madurez,
            "dias_plantacion": dias_plantacion,
            "temperatura_promedio": temp_promedio,
            "humedad_promedio": humedad_promedio,
            "precipitacion_total": precipitacion_total,
            "calidad_temperatura": calidad_temp,
            "calidad_humedad": calidad_humedad,
            "rendimiento_esperado": cultivo_info["rendimiento_esperado"],
            "precio_mercado": cultivo_info["precio_mercado"]
        }
    
    def _generar_recomendaciones_cosecha_cultivo(self, estado: Dict, cultivo_info: Dict) -> List[Dict]:
        """Generar recomendaciones específicas de cosecha para un cultivo"""
        recomendaciones = []
        
        if estado["estado"] == "listo_cosecha":
            recomendaciones.extend([
                {
                    "tipo": "cosecha",
                    "accion": "Iniciar Cosecha",
                    "descripcion": f"Cultivo listo para cosecha. Madurez: {estado['madurez']:.1f}%",
                    "prioridad": 1,
                    "tiempo_recomendado": "inmediato"
                },
                {
                    "tipo": "calidad",
                    "accion": "Control de Calidad",
                    "descripcion": "Realizar muestreo para determinar calidad óptima",
                    "prioridad": 2
                }
            ])
        
        elif estado["estado"] == "cerca_cosecha":
            dias_restantes = cultivo_info["dias_maduracion"] - estado["dias_plantacion"]
            recomendaciones.extend([
                {
                    "tipo": "monitoreo",
                    "accion": "Monitoreo Intensivo",
                    "descripcion": f"Aproximadamente {dias_restantes} días para cosecha óptima",
                    "prioridad": 1
                },
                {
                    "tipo": "preparacion",
                    "accion": "Preparar Infraestructura",
                    "descripcion": "Preparar equipos y personal para cosecha",
                    "prioridad": 2
                }
            ])
        
        # Recomendaciones según condiciones meteorológicas
        if estado["calidad_temperatura"] == "regular":
            recomendaciones.append({
                "tipo": "ambiental",
                "accion": "Ajustar Manejo",
                "descripcion": "Condiciones de temperatura no óptimas, ajustar riego y fertilización",
                "prioridad": 2
            })
        
        if estado["calidad_humedad"] == "regular":
            recomendaciones.append({
                "tipo": "ambiental",
                "accion": "Control de Humedad",
                "descripcion": "Ajustar programa de riego según humedad ambiental",
                "prioridad": 2
            })
        
        # Recomendaciones de mercado
        if cultivo_info["precio_mercado"] == "alto":
            recomendaciones.append({
                "tipo": "mercado",
                "accion": "Estrategia Comercial",
                "descripcion": "Precios de mercado favorables, considerar cosecha escalonada",
                "prioridad": 3
            })
        
        return recomendaciones
    
    def analizar_riesgo_plagas(self, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Analizar riesgo de plagas para todos los cultivos"""
        analisis_plagas = {}
        
        for plaga_id, plaga_info in self.plagas_quillota.items():
            # Calcular riesgo de la plaga
            riesgo = self._calcular_riesgo_plaga(datos_meteorologicos, plaga_info)
            
            # Generar recomendaciones
            recomendaciones = self._generar_recomendaciones_plaga(riesgo, plaga_info)
            
            analisis_plagas[plaga_id] = {
                "plaga": plaga_info,
                "riesgo": riesgo,
                "recomendaciones": recomendaciones
            }
        
        return analisis_plagas
    
    def _calcular_riesgo_plaga(self, datos: pd.DataFrame, plaga_info: Dict) -> Dict:
        """Calcular nivel de riesgo para una plaga específica"""
        if datos.empty:
            return {"nivel": "desconocido", "probabilidad": 0}
        
        temp_promedio = datos["temperatura"].mean()
        humedad_promedio = datos["humedad_relativa"].mean()
        
        condiciones = plaga_info["condiciones_favorables"]
        
        # Evaluar temperatura
        temp_favorable = condiciones["temperatura"]["min"] <= temp_promedio <= condiciones["temperatura"]["max"]
        temp_score = 1 if temp_favorable else 0
        
        # Evaluar humedad
        humedad_favorable = condiciones["humedad"]["min"] <= humedad_promedio <= condiciones["humedad"]["max"]
        humedad_score = 1 if humedad_favorable else 0
        
        # Calcular probabilidad
        probabilidad = (temp_score + humedad_score) * 50
        
        # Determinar nivel de riesgo
        if probabilidad >= 80:
            nivel = "alto"
        elif probabilidad >= 50:
            nivel = "medio"
        elif probabilidad >= 20:
            nivel = "bajo"
        else:
            nivel = "muy_bajo"
        
        return {
            "nivel": nivel,
            "probabilidad": probabilidad,
            "temperatura_favorable": temp_favorable,
            "humedad_favorable": humedad_favorable,
            "temperatura_actual": temp_promedio,
            "humedad_actual": humedad_promedio
        }
    
    def _generar_recomendaciones_plaga(self, riesgo: Dict, plaga_info: Dict) -> List[Dict]:
        """Generar recomendaciones específicas para control de plagas"""
        recomendaciones = []
        
        if riesgo["nivel"] == "alto":
            # Recomendaciones urgentes
            recomendaciones.extend([
                {
                    "tipo": "urgente",
                    "accion": "Tratamiento Curativo",
                    "descripcion": f"Aplicar {plaga_info['tratamiento']['curativo']}",
                    "plaga": plaga_info["nombre"],
                    "prioridad": 1,
                    "tiempo": "inmediato"
                },
                {
                    "tipo": "monitoreo",
                    "accion": "Monitoreo Intensivo",
                    "descripcion": "Revisar cultivos cada 24 horas",
                    "prioridad": 1
                }
            ])
        
        elif riesgo["nivel"] == "medio":
            # Recomendaciones preventivas
            recomendaciones.extend([
                {
                    "tipo": "preventivo",
                    "accion": "Tratamiento Preventivo",
                    "descripcion": f"Implementar {plaga_info['tratamiento']['preventivo']}",
                    "plaga": plaga_info["nombre"],
                    "prioridad": 2
                },
                {
                    "tipo": "monitoreo",
                    "accion": "Monitoreo Regular",
                    "descripcion": "Revisar cultivos cada 48 horas",
                    "prioridad": 2
                }
            ])
        
        # Recomendaciones específicas por síntomas
        recomendaciones.append({
            "tipo": "identificacion",
            "accion": "Identificar Síntomas",
            "descripcion": f"Buscar: {plaga_info['sintomas']}",
            "sintomas": plaga_info["sintomas"],
            "prioridad": 3
        })
        
        return recomendaciones
    
    def generar_reporte_integral(self, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Generar reporte integral con todas las recomendaciones"""
        return {
            "fecha_generacion": datetime.now().isoformat(),
            "datos_meteorologicos": {
                "periodo": {
                    "inicio": datos_meteorologicos["fecha"].min().isoformat() if not datos_meteorologicos.empty else None,
                    "fin": datos_meteorologicos["fecha"].max().isoformat() if not datos_meteorologicos.empty else None
                },
                "resumen": {
                    "temperatura_promedio": datos_meteorologicos["temperatura"].mean() if not datos_meteorologicos.empty else 0,
                    "humedad_promedio": datos_meteorologicos["humedad_relativa"].mean() if not datos_meteorologicos.empty else 0,
                    "precipitacion_total": datos_meteorologicos["precipitacion"].sum() if not datos_meteorologicos.empty else 0
                }
            },
            "analisis_heladas": self.analizar_riesgo_heladas(datos_meteorologicos),
            "recomendaciones_cosecha": self.analizar_recomendaciones_cosecha(datos_meteorologicos),
            "analisis_plagas": self.analizar_riesgo_plagas(datos_meteorologicos),
            "resumen_ejecutivo": self._generar_resumen_ejecutivo(datos_meteorologicos)
        }
    
    def _generar_resumen_ejecutivo(self, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Generar resumen ejecutivo del reporte"""
        if datos_meteorologicos.empty:
            return {"estado_general": "sin_datos", "alertas": [], "recomendaciones_principales": []}
        
        alertas = []
        recomendaciones_principales = []
        
        # Analizar heladas
        temp_min = datos_meteorologicos["temperatura_min"].min()
        if temp_min <= 0:
            alertas.append({
                "tipo": "helada",
                "nivel": "crítico",
                "mensaje": f"Riesgo de helada detectado. Temperatura mínima: {temp_min:.1f}°C"
            })
            recomendaciones_principales.append("Implementar medidas de protección contra heladas inmediatamente")
        
        # Analizar plagas
        temp_promedio = datos_meteorologicos["temperatura"].mean()
        if temp_promedio >= 28:
            alertas.append({
                "tipo": "plagas",
                "nivel": "alto",
                "mensaje": "Condiciones favorables para desarrollo de plagas"
            })
            recomendaciones_principales.append("Intensificar monitoreo de plagas y aplicar tratamientos preventivos")
        
        return {
            "estado_general": "monitoreo_activo" if not alertas else "alertas_activas",
            "alertas": alertas,
            "recomendaciones_principales": recomendaciones_principales,
            "temperatura_minima": temp_min,
            "temperatura_promedio": temp_promedio,
            "humedad_promedio": datos_meteorologicos["humedad_relativa"].mean()
        }

