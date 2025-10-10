#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Calidad de Datos Meteorológicos METGO 3D
Sistema de monitoreo continuo y alertas proactivas
"""

import time
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import threading
from dataclasses import dataclass, asdict
import os
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor_calidad_datos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MetricasCalidad:
    """Métricas de calidad de datos"""
    timestamp: datetime
    total_registros: int
    registros_validos: int
    registros_con_errores: int
    porcentaje_calidad: float
    campos_faltantes: int
    valores_nulos: int
    outliers_detectados: int
    latencia_promedio: float
    disponibilidad_fuentes: Dict[str, bool]

@dataclass
class AlertaCalidad:
    """Alerta de calidad de datos"""
    timestamp: datetime
    tipo: str  # 'critica', 'advertencia', 'info'
    mensaje: str
    metrica_afectada: str
    valor_actual: float
    umbral: float
    recomendacion: str

class MonitorCalidadDatos:
    """Monitor de calidad de datos meteorológicos"""
    
    def __init__(self, config_path: str = "scripts/config_monitor_calidad.json"):
        self.config_path = config_path
        self.config = self._cargar_configuracion()
        self.metricas_historicas = []
        self.alertas_activas = []
        self.monitoreo_activo = False
        self.thread_monitoreo = None
        
        # Configurar directorios
        self.directorios = {
            'logs': Path('logs'),
            'reportes': Path('reportes'),
            'alertas': Path('alertas')
        }
        
        for directorio in self.directorios.values():
            directorio.mkdir(exist_ok=True)
    
    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Cargar configuración del monitor"""
        config_default = {
            'intervalo_monitoreo_segundos': 300,  # 5 minutos
            'umbrales_alertas': {
                'calidad_minima': 80.0,
                'disponibilidad_minima': 95.0,
                'latencia_maxima': 30.0,
                'errores_maximos_por_hora': 10,
                'campos_faltantes_maximos': 5
            },
            'fuentes_datos': [
                'openmeteo',
                'openweathermap',
                'sensor_local',
                'simulado'
            ],
            'campos_criticos': [
                'temperatura_promedio',
                'humedad_relativa',
                'precipitacion_diaria',
                'timestamp'
            ],
            'base_datos': 'scripts/datos_meteorologicos.db',
            'retencion_metricas_dias': 30,
            'retencion_alertas_dias': 7
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    config_default.update(config_cargada)
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}. Usando configuración por defecto.")
        
        return config_default
    
    def iniciar_monitoreo_continuo(self):
        """Iniciar monitoreo continuo en hilo separado"""
        if self.monitoreo_activo:
            logger.warning("Monitoreo ya está activo")
            return
        
        self.monitoreo_activo = True
        self.thread_monitoreo = threading.Thread(target=self._ciclo_monitoreo)
        self.thread_monitoreo.daemon = True
        self.thread_monitoreo.start()
        
        logger.info("✅ Monitor de calidad iniciado")
    
    def detener_monitoreo(self):
        """Detener monitoreo continuo"""
        self.monitoreo_activo = False
        if self.thread_monitoreo:
            self.thread_monitoreo.join(timeout=10)
        logger.info("⏹️ Monitor de calidad detenido")
    
    def _ciclo_monitoreo(self):
        """Ciclo principal de monitoreo"""
        while self.monitoreo_activo:
            try:
                # Ejecutar monitoreo
                metricas = self._ejecutar_monitoreo()
                
                # Evaluar alertas
                alertas_nuevas = self._evaluar_alertas(metricas)
                
                # Guardar métricas
                self._guardar_metricas(metricas)
                
                # Procesar alertas
                if alertas_nuevas:
                    self._procesar_alertas(alertas_nuevas)
                
                # Limpiar datos antiguos
                self._limpiar_datos_antiguos()
                
                logger.info(f"Monitoreo completado. Calidad: {metricas.porcentaje_calidad:.1f}%")
                
            except Exception as e:
                logger.error(f"Error en ciclo de monitoreo: {e}")
            
            # Esperar siguiente ciclo
            time.sleep(self.config['intervalo_monitoreo_segundos'])
    
    def _ejecutar_monitoreo(self) -> MetricasCalidad:
        """Ejecutar monitoreo y obtener métricas actuales"""
        timestamp = datetime.now()
        
        try:
            # Conectar a base de datos
            conn = sqlite3.connect(self.config['base_datos'])
            
            # Obtener datos recientes (últimas 24 horas)
            fecha_limite = timestamp - timedelta(hours=24)
            query = """
                SELECT * FROM datos_meteorologicos 
                WHERE datetime(timestamp) >= datetime(?)
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            
            df = pd.read_sql_query(query, conn, params=[fecha_limite.isoformat()])
            conn.close()
            
            if df.empty:
                logger.warning("No hay datos recientes para monitorear")
                return self._crear_metricas_vacias(timestamp)
            
            # Calcular métricas
            total_registros = len(df)
            registros_validos = self._contar_registros_validos(df)
            registros_con_errores = total_registros - registros_validos
            porcentaje_calidad = (registros_validos / total_registros) * 100
            
            # Campos faltantes
            campos_faltantes = self._contar_campos_faltantes(df)
            
            # Valores nulos
            valores_nulos = df.isnull().sum().sum()
            
            # Outliers
            outliers = self._contar_outliers(df)
            
            # Latencia (simulada - en producción vendría de logs de APIs)
            latencia_promedio = self._calcular_latencia_promedio()
            
            # Disponibilidad de fuentes
            disponibilidad_fuentes = self._verificar_disponibilidad_fuentes()
            
            return MetricasCalidad(
                timestamp=timestamp,
                total_registros=total_registros,
                registros_validos=registros_validos,
                registros_con_errores=registros_con_errores,
                porcentaje_calidad=round(porcentaje_calidad, 2),
                campos_faltantes=campos_faltantes,
                valores_nulos=valores_nulos,
                outliers_detectados=outliers,
                latencia_promedio=latencia_promedio,
                disponibilidad_fuentes=disponibilidad_fuentes
            )
            
        except Exception as e:
            logger.error(f"Error ejecutando monitoreo: {e}")
            return self._crear_metricas_vacias(timestamp)
    
    def _contar_registros_validos(self, df: pd.DataFrame) -> int:
        """Contar registros válidos en el dataset"""
        campos_criticos = self.config['campos_criticos']
        
        # Un registro es válido si tiene todos los campos críticos
        registros_validos = 0
        for _, row in df.iterrows():
            es_valido = True
            for campo in campos_criticos:
                if campo in df.columns and pd.isna(row[campo]):
                    es_valido = False
                    break
            
            if es_valido:
                registros_validos += 1
        
        return registros_validos
    
    def _contar_campos_faltantes(self, df: pd.DataFrame) -> int:
        """Contar campos críticos faltantes"""
        campos_criticos = self.config['campos_criticos']
        campos_faltantes = 0
        
        for campo in campos_criticos:
            if campo not in df.columns:
                campos_faltantes += 1
            else:
                # Contar registros con este campo faltante
                nulos_en_campo = df[campo].isnull().sum()
                campos_faltantes += nulos_en_campo
        
        return campos_faltantes
    
    def _contar_outliers(self, df: pd.DataFrame) -> int:
        """Contar outliers en datos numéricos"""
        outliers = 0
        
        # Definir rangos para detección de outliers
        rangos_outliers = {
            'temperatura_promedio': (-40, 45),
            'precipitacion_diaria': (0, 200),
            'humedad_relativa': (0, 100),
            'viento_velocidad': (0, 100)
        }
        
        for campo, (min_val, max_val) in rangos_outliers.items():
            if campo in df.columns:
                valores_extremos = df[(df[campo] < min_val) | (df[campo] > max_val)]
                outliers += len(valores_extremos)
        
        return outliers
    
    def _calcular_latencia_promedio(self) -> float:
        """Calcular latencia promedio (simulada)"""
        # En producción, esto vendría de logs de APIs
        # Por ahora, simulamos una latencia típica
        return np.random.normal(2.5, 0.5)  # 2.5 segundos promedio
    
    def _verificar_disponibilidad_fuentes(self) -> Dict[str, bool]:
        """Verificar disponibilidad de fuentes de datos"""
        disponibilidad = {}
        
        # Simular verificación de APIs (en producción sería real)
        for fuente in self.config['fuentes_datos']:
            # Simular disponibilidad con probabilidad alta
            disponibilidad[fuente] = np.random.random() > 0.1  # 90% disponible
        
        return disponibilidad
    
    def _crear_metricas_vacias(self, timestamp: datetime) -> MetricasCalidad:
        """Crear métricas vacías cuando no hay datos"""
        return MetricasCalidad(
            timestamp=timestamp,
            total_registros=0,
            registros_validos=0,
            registros_con_errores=0,
            porcentaje_calidad=0.0,
            campos_faltantes=len(self.config['campos_criticos']),
            valores_nulos=0,
            outliers_detectados=0,
            latencia_promedio=0.0,
            disponibilidad_fuentes={fuente: False for fuente in self.config['fuentes_datos']}
        )
    
    def _evaluar_alertas(self, metricas: MetricasCalidad) -> List[AlertaCalidad]:
        """Evaluar métricas y generar alertas si es necesario"""
        alertas = []
        umbrales = self.config['umbrales_alertas']
        
        # Alerta de calidad mínima
        if metricas.porcentaje_calidad < umbrales['calidad_minima']:
            alertas.append(AlertaCalidad(
                timestamp=metricas.timestamp,
                tipo='critica',
                mensaje=f"Calidad de datos crítica: {metricas.porcentaje_calidad:.1f}%",
                metrica_afectada='porcentaje_calidad',
                valor_actual=metricas.porcentaje_calidad,
                umbral=umbrales['calidad_minima'],
                recomendacion="Revisar fuentes de datos y validaciones"
            ))
        
        # Alerta de campos faltantes
        if metricas.campos_faltantes > umbrales['campos_faltantes_maximos']:
            alertas.append(AlertaCalidad(
                timestamp=metricas.timestamp,
                tipo='advertencia',
                mensaje=f"Muchos campos faltantes: {metricas.campos_faltantes}",
                metrica_afectada='campos_faltantes',
                valor_actual=metricas.campos_faltantes,
                umbral=umbrales['campos_faltantes_maximos'],
                recomendacion="Verificar configuración de recolección de datos"
            ))
        
        # Alerta de latencia alta
        if metricas.latencia_promedio > umbrales['latencia_maxima']:
            alertas.append(AlertaCalidad(
                timestamp=metricas.timestamp,
                tipo='advertencia',
                mensaje=f"Latencia alta: {metricas.latencia_promedio:.1f}s",
                metrica_afectada='latencia_promedio',
                valor_actual=metricas.latencia_promedio,
                umbral=umbrales['latencia_maxima'],
                recomendacion="Optimizar conexiones a APIs externas"
            ))
        
        # Alerta de disponibilidad de fuentes
        fuentes_disponibles = sum(metricas.disponibilidad_fuentes.values())
        total_fuentes = len(metricas.disponibilidad_fuentes)
        porcentaje_disponibilidad = (fuentes_disponibles / total_fuentes) * 100
        
        if porcentaje_disponibilidad < umbrales['disponibilidad_minima']:
            alertas.append(AlertaCalidad(
                timestamp=metricas.timestamp,
                tipo='critica',
                mensaje=f"Disponibilidad de fuentes baja: {porcentaje_disponibilidad:.1f}%",
                metrica_afectada='disponibilidad_fuentes',
                valor_actual=porcentaje_disponibilidad,
                umbral=umbrales['disponibilidad_minima'],
                recomendacion="Verificar conectividad y configuración de APIs"
            ))
        
        return alertas
    
    def _procesar_alertas(self, alertas: List[AlertaCalidad]):
        """Procesar alertas generadas"""
        for alerta in alertas:
            # Agregar a lista de alertas activas
            self.alertas_activas.append(alerta)
            
            # Log de alerta
            logger.warning(f"🚨 ALERTA {alerta.tipo.upper()}: {alerta.mensaje}")
            
            # Guardar alerta
            self._guardar_alerta(alerta)
            
            # En producción, aquí se enviarían notificaciones (email, SMS, etc.)
            self._enviar_notificacion(alerta)
    
    def _guardar_metricas(self, metricas: MetricasCalidad):
        """Guardar métricas en archivo"""
        self.metricas_historicas.append(metricas)
        
        # Guardar en archivo JSON
        archivo_metricas = self.directorios['reportes'] / f"metricas_calidad_{datetime.now().strftime('%Y%m%d')}.json"
        
        metricas_dict = {
            'timestamp': metricas.timestamp.isoformat(),
            'total_registros': metricas.total_registros,
            'registros_validos': metricas.registros_validos,
            'registros_con_errores': metricas.registros_con_errores,
            'porcentaje_calidad': metricas.porcentaje_calidad,
            'campos_faltantes': metricas.campos_faltantes,
            'valores_nulos': metricas.valores_nulos,
            'outliers_detectados': metricas.outliers_detectados,
            'latencia_promedio': metricas.latencia_promedio,
            'disponibilidad_fuentes': metricas.disponibilidad_fuentes
        }
        
        try:
            # Leer métricas existentes
            if archivo_metricas.exists():
                with open(archivo_metricas, 'r', encoding='utf-8') as f:
                    datos_existentes = json.load(f)
            else:
                datos_existentes = {'metricas': []}
            
            # Agregar nueva métrica
            datos_existentes['metricas'].append(metricas_dict)
            
            # Guardar
            with open(archivo_metricas, 'w', encoding='utf-8') as f:
                json.dump(datos_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def _guardar_alerta(self, alerta: AlertaCalidad):
        """Guardar alerta en archivo"""
        archivo_alertas = self.directorios['alertas'] / f"alertas_{datetime.now().strftime('%Y%m%d')}.json"
        
        alerta_dict = asdict(alerta)
        alerta_dict['timestamp'] = alerta.timestamp.isoformat()
        
        try:
            # Leer alertas existentes
            if archivo_alertas.exists():
                with open(archivo_alertas, 'r', encoding='utf-8') as f:
                    alertas_existentes = json.load(f)
            else:
                alertas_existentes = {'alertas': []}
            
            # Agregar nueva alerta
            alertas_existentes['alertas'].append(alerta_dict)
            
            # Guardar
            with open(archivo_alertas, 'w', encoding='utf-8') as f:
                json.dump(alertas_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando alerta: {e}")
    
    def _enviar_notificacion(self, alerta: AlertaCalidad):
        """Enviar notificación de alerta (simulado)"""
        # En producción, aquí se implementaría el envío real de notificaciones
        logger.info(f"📧 Notificación enviada: {alerta.mensaje}")
        
        # Ejemplo de implementación con email (requiere configuración adicional)
        # self._enviar_email(alerta)
    
    def _limpiar_datos_antiguos(self):
        """Limpiar datos antiguos según configuración de retención"""
        try:
            # Limpiar métricas antiguas
            dias_retencion_metricas = self.config['retencion_metricas_dias']
            fecha_limite_metricas = datetime.now() - timedelta(days=dias_retencion_metricas)
            
            self.metricas_historicas = [
                m for m in self.metricas_historicas 
                if m.timestamp > fecha_limite_metricas
            ]
            
            # Limpiar alertas antiguas
            dias_retencion_alertas = self.config['retencion_alertas_dias']
            fecha_limite_alertas = datetime.now() - timedelta(days=dias_retencion_alertas)
            
            self.alertas_activas = [
                a for a in self.alertas_activas 
                if a.timestamp > fecha_limite_alertas
            ]
            
        except Exception as e:
            logger.error(f"Error limpiando datos antiguos: {e}")
    
    def generar_reporte_calidad(self, horas: int = 24) -> Dict[str, Any]:
        """Generar reporte de calidad de datos"""
        fecha_limite = datetime.now() - timedelta(hours=horas)
        
        # Filtrar métricas del período
        metricas_periodo = [
            m for m in self.metricas_historicas 
            if m.timestamp > fecha_limite
        ]
        
        if not metricas_periodo:
            return {'error': 'No hay métricas para el período solicitado'}
        
        # Calcular estadísticas
        calidades = [m.porcentaje_calidad for m in metricas_periodo]
        total_registros = sum(m.total_registros for m in metricas_periodo)
        total_errores = sum(m.registros_con_errores for m in metricas_periodo)
        
        # Alertas del período
        alertas_periodo = [
            a for a in self.alertas_activas 
            if a.timestamp > fecha_limite
        ]
        
        return {
            'periodo_horas': horas,
            'fecha_inicio': fecha_limite.isoformat(),
            'fecha_fin': datetime.now().isoformat(),
            'estadisticas': {
                'calidad_promedio': round(np.mean(calidades), 2),
                'calidad_minima': round(np.min(calidades), 2),
                'calidad_maxima': round(np.max(calidades), 2),
                'total_registros': total_registros,
                'total_errores': total_errores,
                'porcentaje_errores': round((total_errores / total_registros) * 100, 2) if total_registros > 0 else 0
            },
            'alertas': {
                'total_alertas': len(alertas_periodo),
                'alertas_criticas': len([a for a in alertas_periodo if a.tipo == 'critica']),
                'alertas_advertencia': len([a for a in alertas_periodo if a.tipo == 'advertencia']),
                'ultimas_alertas': [
                    {
                        'timestamp': a.timestamp.isoformat(),
                        'tipo': a.tipo,
                        'mensaje': a.mensaje
                    } for a in alertas_periodo[-5:]  # Últimas 5 alertas
                ]
            },
            'tendencias': {
                'calidad_mejorando': self._calcular_tendencia_calidad(metricas_periodo),
                'alertas_aumentando': self._calcular_tendencia_alertas(alertas_periodo)
            }
        }
    
    def _calcular_tendencia_calidad(self, metricas: List[MetricasCalidad]) -> bool:
        """Calcular si la calidad está mejorando"""
        if len(metricas) < 2:
            return False
        
        # Regresión lineal simple
        x = np.arange(len(metricas))
        y = [m.porcentaje_calidad for m in metricas]
        
        pendiente = np.polyfit(x, y, 1)[0]
        return pendiente > 0  # Tendencia positiva
    
    def _calcular_tendencia_alertas(self, alertas: List[AlertaCalidad]) -> bool:
        """Calcular si las alertas están aumentando"""
        if len(alertas) < 2:
            return False
        
        # Contar alertas por hora
        alertas_por_hora = {}
        for alerta in alertas:
            hora = alerta.timestamp.hour
            alertas_por_hora[hora] = alertas_por_hora.get(hora, 0) + 1
        
        # Tendencia simple
        horas = sorted(alertas_por_hora.keys())
        if len(horas) < 2:
            return False
        
        conteos = [alertas_por_hora[h] for h in horas]
        pendiente = np.polyfit(horas[:len(conteos)], conteos, 1)[0]
        return pendiente > 0  # Tendencia positiva

def main():
    """Función principal para pruebas"""
    print("📊 MONITOR DE CALIDAD DE DATOS METEOROLÓGICOS")
    print("=" * 60)
    
    monitor = MonitorCalidadDatos()
    
    # Ejecutar monitoreo una vez
    print("🔍 Ejecutando monitoreo...")
    metricas = monitor._ejecutar_monitoreo()
    
    print(f"📊 Métricas obtenidas:")
    print(f"   Total registros: {metricas.total_registros}")
    print(f"   Registros válidos: {metricas.registros_validos}")
    print(f"   Porcentaje calidad: {metricas.porcentaje_calidad}%")
    print(f"   Campos faltantes: {metricas.campos_faltantes}")
    print(f"   Valores nulos: {metricas.valores_nulos}")
    
    # Evaluar alertas
    alertas = monitor._evaluar_alertas(metricas)
    if alertas:
        print(f"\n🚨 Alertas generadas: {len(alertas)}")
        for alerta in alertas:
            print(f"   - {alerta.tipo.upper()}: {alerta.mensaje}")
    else:
        print("\n✅ Sin alertas - Sistema funcionando correctamente")
    
    # Generar reporte
    reporte = monitor.generar_reporte_calidad(24)
    print(f"\n📈 Reporte de calidad generado")
    print(f"   Calidad promedio: {reporte['estadisticas']['calidad_promedio']}%")

if __name__ == "__main__":
    main()

