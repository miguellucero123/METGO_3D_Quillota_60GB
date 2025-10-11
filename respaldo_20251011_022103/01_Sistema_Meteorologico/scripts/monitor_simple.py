#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Simple de Calidad de Datos Meteorológicos METGO 3D
Sistema de monitoreo simplificado y funcional
"""

import sqlite3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import os
from pathlib import Path

# Importar validador flexible
from validador_flexible import ValidadorFlexible

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitorSimple:
    """Monitor simple de calidad de datos"""
    
    def __init__(self, config_path: str = "scripts/config_monitor_calidad.json"):
        self.config_path = config_path
        self.config = self._cargar_configuracion()
        self.validador = ValidadorFlexible()
        self.metricas_historicas = []
        self.alertas_activas = []
        
        # Crear directorios necesarios
        Path('logs').mkdir(exist_ok=True)
        Path('reportes').mkdir(exist_ok=True)
        Path('alertas').mkdir(exist_ok=True)
    
    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Cargar configuración del monitor"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}")
            return self._configuracion_por_defecto()
    
    def _configuracion_por_defecto(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'intervalo_monitoreo_segundos': 300,
            'umbrales_alertas': {
                'calidad_minima': 80.0,
                'errores_maximos_por_hora': 10
            },
            'base_datos': 'scripts/datos_meteorologicos.db',
            'usar_validador_flexible': True
        }
    
    def ejecutar_monitoreo(self) -> Dict[str, Any]:
        """Ejecutar un ciclo de monitoreo"""
        logger.info("Iniciando ciclo de monitoreo")
        
        try:
            # Obtener métricas actuales
            metricas = self._obtener_metricas_actuales()
            
            # Evaluar alertas
            alertas_nuevas = self._evaluar_alertas(metricas)
            
            # Guardar métricas
            self._guardar_metricas(metricas)
            
            # Procesar alertas
            if alertas_nuevas:
                self._procesar_alertas(alertas_nuevas)
            
            logger.info(f"Monitoreo completado. Calidad: {metricas['porcentaje_calidad']:.1f}%")
            
            return {
                'exito': True,
                'metricas': metricas,
                'alertas_generadas': len(alertas_nuevas)
            }
            
        except Exception as e:
            logger.error(f"Error en monitoreo: {e}")
            return {'exito': False, 'error': str(e)}
    
    def _obtener_metricas_actuales(self) -> Dict[str, Any]:
        """Obtener métricas actuales de calidad"""
        timestamp = datetime.now()
        
        # Probar con ambas bases de datos
        bases_datos = [
            "scripts/datos_meteorologicos.db",
            "scripts/datos_meteorologicos_reales.db"
        ]
        
        total_registros = 0
        registros_validos = 0
        puntuaciones = []
        errores_totales = 0
        
        for db_path in bases_datos:
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    
                    # Obtener datos recientes (últimas 24 horas)
                    fecha_limite = timestamp - timedelta(hours=24)
                    query = """
                        SELECT * FROM datos_meteorologicos 
                        WHERE datetime(fecha) >= datetime(?)
                        ORDER BY fecha DESC
                        LIMIT 100
                    """
                    
                    df = pd.read_sql_query(query, conn, params=[fecha_limite.isoformat()])
                    conn.close()
                    
                    if not df.empty:
                        # Validar con validador flexible
                        resultado = self.validador.validar_dataset_completo(df)
                        
                        total_registros += resultado['total_registros']
                        registros_validos += resultado['registros_validos']
                        puntuaciones.extend([r['puntuacion'] for r in resultado['resultados_individuales']])
                        errores_totales += resultado['total_errores']
                        
                except Exception as e:
                    logger.warning(f"Error procesando {db_path}: {e}")
        
        # Calcular métricas finales
        porcentaje_calidad = (registros_validos / total_registros * 100) if total_registros > 0 else 0
        puntuacion_promedio = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
        
        return {
            'timestamp': timestamp.isoformat(),
            'total_registros': total_registros,
            'registros_validos': registros_validos,
            'registros_con_errores': total_registros - registros_validos,
            'porcentaje_calidad': round(porcentaje_calidad, 2),
            'puntuacion_promedio': round(puntuacion_promedio, 2),
            'total_errores': errores_totales,
            'bases_disponibles': sum(1 for db in bases_datos if os.path.exists(db))
        }
    
    def _evaluar_alertas(self, metricas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluar métricas y generar alertas"""
        alertas = []
        umbrales = self.config['umbrales_alertas']
        
        # Alerta de calidad mínima
        if metricas['porcentaje_calidad'] < umbrales['calidad_minima']:
            alertas.append({
                'timestamp': metricas['timestamp'],
                'tipo': 'critica',
                'mensaje': f"Calidad de datos crítica: {metricas['porcentaje_calidad']:.1f}%",
                'metrica_afectada': 'porcentaje_calidad',
                'valor_actual': metricas['porcentaje_calidad'],
                'umbral': umbrales['calidad_minima']
            })
        
        # Alerta de muchos errores
        if metricas['total_errores'] > umbrales.get('errores_maximos_por_hora', 10):
            alertas.append({
                'timestamp': metricas['timestamp'],
                'tipo': 'advertencia',
                'mensaje': f"Muchos errores detectados: {metricas['total_errores']}",
                'metrica_afectada': 'total_errores',
                'valor_actual': metricas['total_errores'],
                'umbral': umbrales.get('errores_maximos_por_hora', 10)
            })
        
        # Alerta de bases de datos no disponibles
        if metricas['bases_disponibles'] == 0:
            alertas.append({
                'timestamp': metricas['timestamp'],
                'tipo': 'critica',
                'mensaje': "Ninguna base de datos disponible",
                'metrica_afectada': 'bases_disponibles',
                'valor_actual': metricas['bases_disponibles'],
                'umbral': 1
            })
        
        return alertas
    
    def _guardar_metricas(self, metricas: Dict[str, Any]):
        """Guardar métricas en archivo"""
        self.metricas_historicas.append(metricas)
        
        # Guardar en archivo JSON
        archivo_metricas = f"reportes/metricas_calidad_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Leer métricas existentes
            if os.path.exists(archivo_metricas):
                with open(archivo_metricas, 'r', encoding='utf-8') as f:
                    datos_existentes = json.load(f)
            else:
                datos_existentes = {'metricas': []}
            
            # Agregar nueva métrica
            datos_existentes['metricas'].append(metricas)
            
            # Mantener solo las últimas 100 métricas
            if len(datos_existentes['metricas']) > 100:
                datos_existentes['metricas'] = datos_existentes['metricas'][-100:]
            
            # Guardar
            with open(archivo_metricas, 'w', encoding='utf-8') as f:
                json.dump(datos_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def _procesar_alertas(self, alertas: List[Dict[str, Any]]):
        """Procesar alertas generadas"""
        for alerta in alertas:
            # Agregar a lista de alertas activas
            self.alertas_activas.append(alerta)
            
            # Log de alerta
            logger.warning(f"ALERTA {alerta['tipo'].upper()}: {alerta['mensaje']}")
            
            # Guardar alerta
            self._guardar_alerta(alerta)
    
    def _guardar_alerta(self, alerta: Dict[str, Any]):
        """Guardar alerta en archivo"""
        archivo_alertas = f"alertas/alertas_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Leer alertas existentes
            if os.path.exists(archivo_alertas):
                with open(archivo_alertas, 'r', encoding='utf-8') as f:
                    alertas_existentes = json.load(f)
            else:
                alertas_existentes = {'alertas': []}
            
            # Agregar nueva alerta
            alertas_existentes['alertas'].append(alerta)
            
            # Mantener solo las últimas 50 alertas
            if len(alertas_existentes['alertas']) > 50:
                alertas_existentes['alertas'] = alertas_existentes['alertas'][-50:]
            
            # Guardar
            with open(archivo_alertas, 'w', encoding='utf-8') as f:
                json.dump(alertas_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando alerta: {e}")
    
    def generar_reporte_calidad(self, horas: int = 24) -> Dict[str, Any]:
        """Generar reporte de calidad de datos"""
        fecha_limite = datetime.now() - timedelta(hours=horas)
        
        # Filtrar métricas del período
        metricas_periodo = [
            m for m in self.metricas_historicas 
            if datetime.fromisoformat(m['timestamp']) > fecha_limite
        ]
        
        if not metricas_periodo:
            return {'error': 'No hay métricas para el período solicitado'}
        
        # Calcular estadísticas
        calidades = [m['porcentaje_calidad'] for m in metricas_periodo]
        total_registros = sum(m['total_registros'] for m in metricas_periodo)
        total_errores = sum(m['total_errores'] for m in metricas_periodo)
        
        return {
            'periodo_horas': horas,
            'fecha_inicio': fecha_limite.isoformat(),
            'fecha_fin': datetime.now().isoformat(),
            'estadisticas': {
                'calidad_promedio': round(sum(calidades) / len(calidades), 2),
                'calidad_minima': round(min(calidades), 2),
                'calidad_maxima': round(max(calidades), 2),
                'total_registros': total_registros,
                'total_errores': total_errores,
                'porcentaje_errores': round((total_errores / total_registros) * 100, 2) if total_registros > 0 else 0
            },
            'alertas': {
                'total_alertas': len(self.alertas_activas),
                'alertas_criticas': len([a for a in self.alertas_activas if a['tipo'] == 'critica']),
                'alertas_advertencia': len([a for a in self.alertas_activas if a['tipo'] == 'advertencia'])
            }
        }

def main():
    """Función principal"""
    print("=" * 70)
    print("MONITOR SIMPLE DE CALIDAD DE DATOS METEOROLOGICOS")
    print("=" * 70)
    
    monitor = MonitorSimple()
    
    # Ejecutar monitoreo una vez
    print("Ejecutando monitoreo...")
    resultado = monitor.ejecutar_monitoreo()
    
    if resultado['exito']:
        metricas = resultado['metricas']
        print(f"Monitoreo completado exitosamente:")
        print(f"  Total registros: {metricas['total_registros']}")
        print(f"  Registros validos: {metricas['registros_validos']}")
        print(f"  Porcentaje calidad: {metricas['porcentaje_calidad']}%")
        print(f"  Puntuacion promedio: {metricas['puntuacion_promedio']}/100")
        print(f"  Total errores: {metricas['total_errores']}")
        print(f"  Alertas generadas: {resultado['alertas_generadas']}")
        
        # Generar reporte
        reporte = monitor.generar_reporte_calidad(24)
        if 'error' not in reporte:
            print(f"\nReporte de calidad (24h):")
            print(f"  Calidad promedio: {reporte['estadisticas']['calidad_promedio']}%")
            print(f"  Total alertas: {reporte['alertas']['total_alertas']}")
    else:
        print(f"Error en monitoreo: {resultado['error']}")

if __name__ == "__main__":
    main()

