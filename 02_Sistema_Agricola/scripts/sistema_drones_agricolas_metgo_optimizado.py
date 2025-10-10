"""
SISTEMA DE INTEGRACIÓN CON DRONES AGRÍCOLAS - METGO 3D QUILLOTA (VERSIÓN OPTIMIZADA)
Sistema simplificado y eficiente para monitoreo aéreo de cultivos con drones
Incluye: Simulación rápida, análisis básico de índices vegetativos y recomendaciones
"""

import pandas as pd
import numpy as np
import json
import logging
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class SistemaDronesAgricolasMetgoOptimizado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "sistema_drones_agricolas_optimizado.db"
        self.directorio_datos = "datos_drones_optimizado"
        
        # Crear directorios necesarios
        self._crear_directorios()
        
        # Inicializar base de datos simplificada
        self._inicializar_base_datos()
        
        # Configuración simplificada de drones
        self.drones_configuracion = {
            'dji_mini_3': {
                'nombre': 'DJI Mini 3',
                'autonomia': 25,  # minutos
                'alcance': 5,     # km
                'resolucion': '4K',
                'altura_vuelo': 100,  # metros
                'cobertura_hectareas': 20,   # por vuelo
            },
            'dji_air_2s': {
                'nombre': 'DJI Air 2S',
                'autonomia': 31,
                'alcance': 12,
                'resolucion': '5.4K',
                'altura_vuelo': 120,
                'cobertura_hectareas': 30,
            },
            'dji_phantom_4': {
                'nombre': 'DJI Phantom 4',
                'autonomia': 28,
                'alcance': 7,
                'resolucion': '4K',
                'altura_vuelo': 150,
                'cobertura_hectareas': 50,
            }
        }
        
        # Configuración simplificada de cultivos
        self.cultivos_configuracion = {
            'palto': {
                'nombre': 'Palto (Aguacate)',
                'densidad_plantas_hectarea': 200,
                'altura_promedio': 8,
                'distancia_entre_filas': 6,
                'frecuencia_monitoreo': 15,  # días
                'indices_relevantes': ['NDVI', 'NDWI']
            },
            'uva': {
                'nombre': 'Uva de Mesa',
                'densidad_plantas_hectarea': 2500,
                'altura_promedio': 2,
                'distancia_entre_filas': 3,
                'frecuencia_monitoreo': 10,
                'indices_relevantes': ['NDVI', 'SAVI']
            },
            'citricos': {
                'nombre': 'Cítricos',
                'densidad_plantas_hectarea': 400,
                'altura_promedio': 4,
                'distancia_entre_filas': 5,
                'frecuencia_monitoreo': 20,
                'indices_relevantes': ['NDVI', 'GCI']
            }
        }
        
        self.logger.info("Sistema de Drones Agrícolas METGO 3D Optimizado inicializado")
    
    def _crear_directorios(self):
        """Crear directorios necesarios para el sistema"""
        try:
            directorios = [
                self.directorio_datos,
                f"{self.directorio_datos}/vuelos",
                f"{self.directorio_datos}/analisis",
                f"{self.directorio_datos}/reportes"
            ]
            
            for directorio in directorios:
                os.makedirs(directorio, exist_ok=True)
                
            print("[OK] Directorios del sistema de drones optimizado creados")
            
        except Exception as e:
            print(f"[ERROR] Error creando directorios: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos simplificada para el sistema de drones"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla simplificada de vuelos de drones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vuelos_drones_optimizado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vuelo_id TEXT UNIQUE NOT NULL,
                    drone_tipo TEXT NOT NULL,
                    fecha_vuelo DATETIME NOT NULL,
                    ubicacion TEXT NOT NULL,
                    cultivo_tipo TEXT NOT NULL,
                    area_hectareas REAL,
                    duracion_vuelo INTEGER,
                    numero_fotos INTEGER,
                    estado TEXT DEFAULT 'completado',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla simplificada de análisis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analisis_drones_optimizado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vuelo_id TEXT NOT NULL,
                    fecha_analisis DATETIME NOT NULL,
                    ndvi_promedio REAL,
                    salud_general TEXT,
                    areas_problema INTEGER,
                    recomendaciones TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vuelo_id) REFERENCES vuelos_drones_optimizado (vuelo_id)
                )
            ''')
            
            # Tabla de recomendaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recomendaciones_drones_optimizado (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vuelo_id TEXT NOT NULL,
                    fecha_recomendacion DATETIME NOT NULL,
                    tipo_recomendacion TEXT NOT NULL,
                    prioridad TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    accion_requerida TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vuelo_id) REFERENCES vuelos_drones_optimizado (vuelo_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("[OK] Base de datos del sistema de drones optimizado inicializada")
            
        except Exception as e:
            print(f"[ERROR] Error inicializando base de datos: {e}")
    
    def simular_vuelo_drone_rapido(self, drone_tipo: str, ubicacion: str, cultivo_tipo: str, 
                                  area_hectareas: float) -> Dict:
        """Simular un vuelo de drone de forma rápida y eficiente"""
        try:
            print(f"[DRONE] Simulando vuelo rápido con {drone_tipo} en {ubicacion}")
            
            # Generar ID único para el vuelo
            vuelo_id = f"vuelo_{uuid.uuid4().hex[:8]}"
            
            # Obtener configuración del drone
            config_drone = self.drones_configuracion.get(drone_tipo, {})
            config_cultivo = self.cultivos_configuracion.get(cultivo_tipo, {})
            
            if not config_drone or not config_cultivo:
                raise ValueError(f"Configuración no encontrada para drone {drone_tipo} o cultivo {cultivo_tipo}")
            
            # Calcular parámetros del vuelo de forma simplificada
            cobertura_por_vuelo = config_drone.get('cobertura_hectareas', 30)
            autonomia = config_drone.get('autonomia', 25)
            
            # Calcular duración del vuelo
            tiempo_por_hectarea = autonomia / cobertura_por_vuelo
            duracion_vuelo = int(area_hectareas * tiempo_por_hectarea)
            
            # Calcular número de fotos (simplificado)
            fotos_por_hectarea = 10  # Reducido para optimización
            numero_fotos = int(area_hectareas * fotos_por_hectarea)
            
            # Guardar información del vuelo
            vuelo_data = {
                'vuelo_id': vuelo_id,
                'drone_tipo': drone_tipo,
                'fecha_vuelo': datetime.now(),
                'ubicacion': ubicacion,
                'cultivo_tipo': cultivo_tipo,
                'area_hectareas': area_hectareas,
                'duracion_vuelo': duracion_vuelo,
                'numero_fotos': numero_fotos,
                'estado': 'completado'
            }
            
            self._guardar_vuelo_drone(vuelo_data)
            
            # Análisis rápido
            analisis = self._analisis_rapido_cultivo(cultivo_tipo, area_hectareas)
            
            # Generar recomendaciones básicas
            recomendaciones = self._generar_recomendaciones_basicas(cultivo_tipo, analisis)
            
            resultado = {
                'vuelo_id': vuelo_id,
                'drone_tipo': drone_tipo,
                'ubicacion': ubicacion,
                'cultivo_tipo': cultivo_tipo,
                'area_hectareas': area_hectareas,
                'duracion_vuelo_minutos': duracion_vuelo,
                'numero_fotos': numero_fotos,
                'estado': 'completado',
                'fecha_vuelo': datetime.now().isoformat(),
                'analisis': analisis,
                'recomendaciones': recomendaciones
            }
            
            print(f"[OK] Vuelo simulado completado: {numero_fotos} fotos en {duracion_vuelo} minutos")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error simulando vuelo de drone: {e}")
            return {'error': str(e)}
    
    def _analisis_rapido_cultivo(self, cultivo_tipo: str, area_hectareas: float) -> Dict:
        """Análisis rápido y simplificado del cultivo"""
        try:
            # Generar valores simulados pero realistas
            np.random.seed(42)
            
            # NDVI promedio según tipo de cultivo
            ndvi_base = {
                'palto': 0.75,
                'uva': 0.65,
                'citricos': 0.70
            }
            
            ndvi_promedio = ndvi_base.get(cultivo_tipo, 0.70)
            ndvi_variacion = np.random.uniform(-0.1, 0.1)
            ndvi_final = max(0.3, min(0.9, ndvi_promedio + ndvi_variacion))
            
            # Clasificar salud general
            if ndvi_final > 0.7:
                salud_general = "Excelente"
            elif ndvi_final > 0.5:
                salud_general = "Buena"
            elif ndvi_final > 0.3:
                salud_general = "Regular"
            else:
                salud_general = "Mala"
            
            # Estimar áreas con problemas (simplificado)
            areas_problema = int(area_hectareas * np.random.uniform(0.05, 0.25))
            
            # Calcular porcentajes de salud
            porcentaje_saludable = min(100, ndvi_final * 100 + np.random.uniform(-10, 10))
            porcentaje_estres = max(0, 100 - porcentaje_saludable - np.random.uniform(5, 15))
            porcentaje_enfermo = max(0, 100 - porcentaje_saludable - porcentaje_estres)
            
            return {
                'ndvi_promedio': round(ndvi_final, 3),
                'salud_general': salud_general,
                'areas_problema_hectareas': areas_problema,
                'porcentaje_saludable': round(porcentaje_saludable, 1),
                'porcentaje_estres': round(porcentaje_estres, 1),
                'porcentaje_enfermo': round(porcentaje_enfermo, 1),
                'area_total_analizada': area_hectareas
            }
            
        except Exception as e:
            print(f"[ERROR] Error en análisis rápido: {e}")
            return {}
    
    def _generar_recomendaciones_basicas(self, cultivo_tipo: str, analisis: Dict) -> List[Dict]:
        """Generar recomendaciones básicas basadas en el análisis"""
        try:
            recomendaciones = []
            
            salud = analisis.get('salud_general', 'Regular')
            ndvi = analisis.get('ndvi_promedio', 0.5)
            areas_problema = analisis.get('areas_problema_hectareas', 0)
            
            # Recomendaciones según salud general
            if salud == "Mala" or ndvi < 0.4:
                recomendaciones.append({
                    'tipo_recomendacion': 'urgencia',
                    'prioridad': 'alta',
                    'mensaje': 'Estado crítico detectado - Acción inmediata requerida',
                    'accion_requerida': 'Evaluar riego, fertilización y posibles plagas'
                })
            elif salud == "Regular" or ndvi < 0.6:
                recomendaciones.append({
                    'tipo_recomendacion': 'mejora',
                    'prioridad': 'media',
                    'mensaje': 'Mejoras recomendadas para optimizar producción',
                    'accion_requerida': 'Revisar programa de fertilización y riego'
                })
            
            # Recomendaciones según áreas con problemas
            if areas_problema > 0:
                recomendaciones.append({
                    'tipo_recomendacion': 'areas_problema',
                    'prioridad': 'media',
                    'mensaje': f'{areas_problema} hectáreas con problemas detectados',
                    'accion_requerida': 'Inspección detallada de áreas específicas'
                })
            
            # Recomendaciones específicas por cultivo
            if cultivo_tipo == 'palto':
                recomendaciones.append({
                    'tipo_recomendacion': 'especifica',
                    'prioridad': 'baja',
                    'mensaje': 'Palto: Monitorear humedad del suelo y nutrición',
                    'accion_requerida': 'Verificar sistema de riego y aplicar fertilizantes'
                })
            elif cultivo_tipo == 'uva':
                recomendaciones.append({
                    'tipo_recomendacion': 'especifica',
                    'prioridad': 'baja',
                    'mensaje': 'Uva: Controlar vigor vegetativo y enfermedades',
                    'accion_requerida': 'Poda verde y tratamientos preventivos'
                })
            elif cultivo_tipo == 'citricos':
                recomendaciones.append({
                    'tipo_recomendacion': 'especifica',
                    'prioridad': 'baja',
                    'mensaje': 'Cítricos: Monitorear plagas y nutrición',
                    'accion_requerida': 'Inspección de hojas y aplicación de micronutrientes'
                })
            
            return recomendaciones
            
        except Exception as e:
            print(f"[ERROR] Error generando recomendaciones: {e}")
            return []
    
    def _guardar_vuelo_drone(self, vuelo_data: Dict):
        """Guardar información del vuelo en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vuelos_drones_optimizado 
                (vuelo_id, drone_tipo, fecha_vuelo, ubicacion, cultivo_tipo, 
                 area_hectareas, duracion_vuelo, numero_fotos, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vuelo_data['vuelo_id'],
                vuelo_data['drone_tipo'],
                vuelo_data['fecha_vuelo'],
                vuelo_data['ubicacion'],
                vuelo_data['cultivo_tipo'],
                vuelo_data['area_hectareas'],
                vuelo_data['duracion_vuelo'],
                vuelo_data['numero_fotos'],
                vuelo_data['estado']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando vuelo de drone: {e}")
    
    def _guardar_analisis_drone(self, vuelo_id: str, analisis: Dict):
        """Guardar análisis del drone en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analisis_drones_optimizado 
                (vuelo_id, fecha_analisis, ndvi_promedio, salud_general, 
                 areas_problema, recomendaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                vuelo_id,
                datetime.now(),
                analisis.get('ndvi_promedio', 0),
                analisis.get('salud_general', 'Regular'),
                analisis.get('areas_problema_hectareas', 0),
                json.dumps(analisis)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando análisis: {e}")
    
    def _guardar_recomendaciones_drone(self, vuelo_id: str, recomendaciones: List[Dict]):
        """Guardar recomendaciones del drone en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            for rec in recomendaciones:
                cursor.execute('''
                    INSERT INTO recomendaciones_drones_optimizado 
                    (vuelo_id, fecha_recomendacion, tipo_recomendacion, 
                     prioridad, mensaje, accion_requerida)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    vuelo_id,
                    datetime.now(),
                    rec['tipo_recomendacion'],
                    rec['prioridad'],
                    rec['mensaje'],
                    rec['accion_requerida']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error guardando recomendaciones: {e}")
    
    def generar_reporte_drones_optimizado(self) -> Dict:
        """Generar reporte optimizado del sistema de drones"""
        try:
            print("[REPORTE] Generando reporte optimizado de drones...")
            
            # Obtener estadísticas de vuelos
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute('SELECT COUNT(*) FROM vuelos_drones_optimizado')
            total_vuelos = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT cultivo_tipo) FROM vuelos_drones_optimizado')
            tipos_cultivo = cursor.fetchone()[0]
            
            # Estadísticas por drone
            cursor.execute('''
                SELECT drone_tipo, COUNT(*) as cantidad, 
                       AVG(duracion_vuelo) as duracion_promedio,
                       AVG(numero_fotos) as fotos_promedio
                FROM vuelos_drones_optimizado 
                GROUP BY drone_tipo
            ''')
            
            estadisticas_drones = {}
            for row in cursor.fetchall():
                estadisticas_drones[row[0]] = {
                    'cantidad_vuelos': row[1],
                    'duracion_promedio': round(row[2], 1),
                    'fotos_promedio': round(row[3], 1)
                }
            
            # Estadísticas por cultivo
            cursor.execute('''
                SELECT cultivo_tipo, COUNT(*) as cantidad, 
                       AVG(area_hectareas) as area_promedio
                FROM vuelos_drones_optimizado 
                GROUP BY cultivo_tipo
            ''')
            
            estadisticas_cultivos = {}
            for row in cursor.fetchall():
                estadisticas_cultivos[row[0]] = {
                    'cantidad_vuelos': row[1],
                    'area_promedio': round(row[2], 1)
                }
            
            # Análisis recientes
            cursor.execute('''
                SELECT v.cultivo_tipo, a.ndvi_promedio, a.salud_general, a.areas_problema
                FROM vuelos_drones_optimizado v
                JOIN analisis_drones_optimizado a ON v.vuelo_id = a.vuelo_id
                ORDER BY a.fecha_analisis DESC
                LIMIT 10
            ''')
            
            analisis_recientes = []
            for row in cursor.fetchall():
                analisis_recientes.append({
                    'cultivo_tipo': row[0],
                    'ndvi_promedio': round(row[1], 3),
                    'salud_general': row[2],
                    'areas_problema': row[3]
                })
            
            conn.close()
            
            # Generar visualizaciones
            rutas_graficos = self._generar_visualizaciones_optimizadas()
            
            reporte = {
                'fecha_reporte': datetime.now().isoformat(),
                'estadisticas_generales': {
                    'total_vuelos': total_vuelos,
                    'tipos_cultivo_monitoreados': tipos_cultivo,
                    'drones_disponibles': len(self.drones_configuracion)
                },
                'estadisticas_por_drone': estadisticas_drones,
                'estadisticas_por_cultivo': estadisticas_cultivos,
                'analisis_recientes': analisis_recientes,
                'visualizaciones': rutas_graficos,
                'configuracion_drones': self.drones_configuracion,
                'configuracion_cultivos': self.cultivos_configuracion
            }
            
            # Guardar reporte
            self._guardar_reporte_optimizado(reporte)
            
            print("[OK] Reporte optimizado de drones generado")
            return reporte
            
        except Exception as e:
            print(f"[ERROR] Error generando reporte: {e}")
            return {'error': str(e)}
    
    def _generar_visualizaciones_optimizadas(self) -> Dict:
        """Generar visualizaciones optimizadas para el reporte"""
        try:
            rutas_graficos = {}
            
            # Obtener datos para gráficos
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Gráfico de vuelos por drone
            cursor.execute('''
                SELECT drone_tipo, COUNT(*) as cantidad
                FROM vuelos_drones_optimizado 
                GROUP BY drone_tipo
            ''')
            
            datos_drones = cursor.fetchall()
            if datos_drones:
                fig_drones = px.bar(
                    x=[row[0] for row in datos_drones],
                    y=[row[1] for row in datos_drones],
                    title='Vuelos por Tipo de Drone',
                    labels={'x': 'Tipo de Drone', 'y': 'Cantidad de Vuelos'}
                )
                
                ruta_drones = os.path.join(self.directorio_datos, 'reportes', 'vuelos_por_drone.html')
                fig_drones.write_html(ruta_drones)
                rutas_graficos['vuelos_por_drone'] = ruta_drones
            
            # Gráfico de salud por cultivo
            cursor.execute('''
                SELECT v.cultivo_tipo, a.salud_general, COUNT(*) as cantidad
                FROM vuelos_drones_optimizado v
                JOIN analisis_drones_optimizado a ON v.vuelo_id = a.vuelo_id
                GROUP BY v.cultivo_tipo, a.salud_general
            ''')
            
            datos_salud = cursor.fetchall()
            if datos_salud:
                df_salud = pd.DataFrame(datos_salud, columns=['cultivo', 'salud', 'cantidad'])
                fig_salud = px.bar(
                    df_salud, 
                    x='cultivo', 
                    y='cantidad', 
                    color='salud',
                    title='Estado de Salud por Cultivo',
                    labels={'cultivo': 'Tipo de Cultivo', 'cantidad': 'Cantidad de Análisis'}
                )
                
                ruta_salud = os.path.join(self.directorio_datos, 'reportes', 'salud_por_cultivo.html')
                fig_salud.write_html(ruta_salud)
                rutas_graficos['salud_por_cultivo'] = ruta_salud
            
            conn.close()
            
            return rutas_graficos
            
        except Exception as e:
            print(f"[ERROR] Error generando visualizaciones: {e}")
            return {}
    
    def _guardar_reporte_optimizado(self, reporte: Dict):
        """Guardar reporte optimizado"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_drones_optimizado_{timestamp}.json"
            ruta_archivo = os.path.join(self.directorio_datos, 'reportes', nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[OK] Reporte optimizado guardado: {ruta_archivo}")
            
        except Exception as e:
            print(f"[ERROR] Error guardando reporte: {e}")
    
    def ejecutar_demonstracion_rapida(self) -> Dict:
        """Ejecutar demostración rápida del sistema optimizado"""
        try:
            print("="*80)
            print("DEMOSTRACIÓN SISTEMA DE DRONES AGRÍCOLAS OPTIMIZADO")
            print("="*80)
            
            # Simular varios vuelos rápidos
            vuelos_demostracion = [
                {'drone': 'dji_mini_3', 'ubicacion': 'Quillota Centro', 'cultivo': 'palto', 'area': 5.0},
                {'drone': 'dji_air_2s', 'ubicacion': 'La Cruz', 'cultivo': 'uva', 'area': 8.0},
                {'drone': 'dji_phantom_4', 'ubicacion': 'Hijuelas', 'cultivo': 'citricos', 'area': 12.0}
            ]
            
            resultados_vuelos = []
            
            for vuelo in vuelos_demostracion:
                print(f"\n[VUELO] Simulando vuelo en {vuelo['ubicacion']}...")
                
                resultado = self.simular_vuelo_drone_rapido(
                    vuelo['drone'],
                    vuelo['ubicacion'],
                    vuelo['cultivo'],
                    vuelo['area']
                )
                
                if 'error' not in resultado:
                    # Guardar análisis y recomendaciones
                    self._guardar_analisis_drone(resultado['vuelo_id'], resultado['analisis'])
                    self._guardar_recomendaciones_drone(resultado['vuelo_id'], resultado['recomendaciones'])
                    
                    resultados_vuelos.append(resultado)
                    print(f"[OK] Vuelo completado: {resultado['numero_fotos']} fotos en {resultado['duracion_vuelo_minutos']} min")
                else:
                    print(f"[ERROR] Error en vuelo: {resultado['error']}")
            
            # Generar reporte final
            print("\n[REPORTE] Generando reporte consolidado...")
            reporte_final = self.generar_reporte_drones_optimizado()
            
            return {
                'vuelos_completados': len(resultados_vuelos),
                'vuelos_simulados': vuelos_demostracion,
                'resultados_vuelos': resultados_vuelos,
                'reporte_final': reporte_final
            }
            
        except Exception as e:
            print(f"[ERROR] Error en demostración: {e}")
            return {'error': str(e)}

def main():
    """Función principal para demostrar el sistema optimizado"""
    try:
        print("="*80)
        print("SISTEMA DE DRONES AGRÍCOLAS METGO 3D - VERSIÓN OPTIMIZADA")
        print("="*80)
        
        # Inicializar sistema optimizado
        sistema = SistemaDronesAgricolasMetgoOptimizado()
        
        print("\n[1] EJECUTANDO DEMOSTRACIÓN RÁPIDA...")
        
        # Ejecutar demostración
        resultado = sistema.ejecutar_demonstracion_rapida()
        
        if 'error' in resultado:
            print(f"[ERROR] Error en demostración: {resultado['error']}")
            return
        
        print(f"\n[OK] Demostración completada:")
        print(f"    - Vuelos completados: {resultado['vuelos_completados']}")
        print(f"    - Sistema optimizado: Funcional")
        
        print("\n[2] RESUMEN DE VUELOS...")
        
        for vuelo in resultado['resultados_vuelos']:
            print(f"    - {vuelo['ubicacion']} ({vuelo['cultivo_tipo']}):")
            print(f"      Drone: {vuelo['drone_tipo']}")
            print(f"      Área: {vuelo['area_hectareas']} ha")
            print(f"      Fotos: {vuelo['numero_fotos']}")
            print(f"      Duración: {vuelo['duracion_vuelo_minutos']} min")
            print(f"      Salud: {vuelo['analisis']['salud_general']}")
            print(f"      NDVI: {vuelo['analisis']['ndvi_promedio']}")
        
        print("\n[3] CONFIGURACIÓN DEL SISTEMA...")
        
        print("    Drones disponibles:")
        for drone_id, config in sistema.drones_configuracion.items():
            print(f"      - {config['nombre']}: {config['autonomia']}min, {config['cobertura_hectareas']}ha")
        
        print("    Cultivos configurados:")
        for cultivo_id, config in sistema.cultivos_configuracion.items():
            print(f"      - {config['nombre']}: Monitoreo cada {config['frecuencia_monitoreo']} días")
        
        print("\n" + "="*80)
        print("SISTEMA DE DRONES AGRÍCOLAS OPTIMIZADO COMPLETADO")
        print("="*80)
        print("[OK] Sistema optimizado y funcional")
        print("[OK] Demostración ejecutada exitosamente")
        print("[OK] Reportes y análisis generados")
        print("[OK] Base de datos optimizada creada")
        print("="*80)
        
    except Exception as e:
        print(f"[ERROR] Error en función principal: {e}")

if __name__ == "__main__":
    main()


