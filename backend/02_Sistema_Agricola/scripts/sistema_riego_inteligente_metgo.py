"""
SISTEMA DE RIEGO INTELIGENTE - METGO 3D QUILLOTA
Sistema avanzado de riego automatizado con IoT y Machine Learning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sqlite3
import logging
import time
import schedule
from typing import Dict, List, Tuple, Optional, Any
import os
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# Simulación de sensores IoT (en producción serían librerías reales)
class SensorHumedad:
    def __init__(self, pin: int):
        self.pin = pin
        self.ultima_lectura = 45.0  # Simulación
    
    def leer_humedad(self) -> float:
        """Leer humedad del suelo"""
        # Simular lectura del sensor
        humedad = 45 + np.random.normal(0, 5)
        humedad = max(0, min(100, humedad))
        self.ultima_lectura = humedad
        return humedad

class SensorTemperatura:
    def __init__(self, pin: int):
        self.pin = pin
        self.ultima_lectura = 20.0  # Simulación
    
    def leer_temperatura(self) -> float:
        """Leer temperatura del aire"""
        # Simular lectura del sensor
        temp = 20 + np.random.normal(0, 2)
        self.ultima_lectura = temp
        return temp

class ActuadorRiego:
    def __init__(self, pin: int):
        self.pin = pin
        self.estado = False
        self.tiempo_activacion = 0
    
    def activar(self, duracion_segundos: int):
        """Activar sistema de riego"""
        self.estado = True
        self.tiempo_activacion = time.time()
        print(f"💧 Sistema de riego activado por {duracion_segundos} segundos")
        # En producción: GPIO.output(self.pin, GPIO.HIGH)
        
        # Simular desactivación después del tiempo
        threading.Timer(duracion_segundos, self.desactivar).start()
    
    def desactivar(self):
        """Desactivar sistema de riego"""
        self.estado = False
        print("💧 Sistema de riego desactivado")
        # En producción: GPIO.output(self.pin, GPIO.LOW)

class TipoCultivo(Enum):
    PALTO = "palto"
    UVA = "uva"
    CITRICOS = "citricos"
    HORTALIZAS = "hortalizas"
    CEREALES = "cereales"

@dataclass
class ConfiguracionCultivo:
    """Configuración específica para cada tipo de cultivo"""
    tipo: TipoCultivo
    humedad_optima_min: float
    humedad_optima_max: float
    humedad_critica_min: float
    temperatura_optima_min: float
    temperatura_optima_max: float
    frecuencia_riego_dias: int
    duracion_riego_minutos: int
    profundidad_raiz_cm: int
    coeficiente_cultivo: float

class SistemaRiegoInteligente:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "sistema_riego_inteligente.db"
        self.configuracion_dir = "config_riego"
        self._crear_directorios()
        self._inicializar_base_datos()
        self._cargar_configuraciones_cultivos()
        
        # Sensores IoT
        self.sensores_humedad = {}
        self.sensores_temperatura = {}
        self.actuadores_riego = {}
        
        # Estado del sistema
        self.estado_sistema = {
            'activo': True,
            'modo_automatico': True,
            'ultima_evaluacion': None,
            'riego_activo': False
        }
        
        # Cola de eventos
        self.cola_eventos = queue.Queue()
        
        # Inicializar sensores y actuadores
        self._inicializar_dispositivos_iot()
        
        # Cargar modelos ML (si están disponibles)
        self.modelos_ml = self._cargar_modelos_ml()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.configuracion_dir, 'logs', 'datos_sensores', 'reportes_riego']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para sistema de riego"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de sensores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    pin INTEGER,
                    ultima_lectura REAL,
                    fecha_ultima_lectura DATETIME,
                    estado TEXT DEFAULT 'activo'
                )
            ''')
            
            # Tabla de lecturas de sensores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lecturas_sensores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER,
                    tipo_sensor TEXT NOT NULL,
                    valor REAL NOT NULL,
                    unidad TEXT NOT NULL,
                    fecha_lectura DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ubicacion TEXT,
                    FOREIGN KEY (sensor_id) REFERENCES sensores (id)
                )
            ''')
            
            # Tabla de eventos de riego
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eventos_riego (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actuador_id INTEGER,
                    tipo_evento TEXT NOT NULL,
                    duracion_segundos INTEGER,
                    humedad_inicial REAL,
                    humedad_final REAL,
                    temperatura REAL,
                    cultivo TEXT,
                    fecha_evento DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'completado'
                )
            ''')
            
            # Tabla de configuración de cultivos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_cultivos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_cultivo TEXT UNIQUE NOT NULL,
                    configuracion TEXT NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de predicciones de riego
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones_riego (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cultivo TEXT NOT NULL,
                    ubicacion TEXT NOT NULL,
                    fecha_prediccion DATETIME NOT NULL,
                    humedad_predicha REAL,
                    necesidad_riego BOOLEAN,
                    duracion_recomendada INTEGER,
                    confianza REAL,
                    modelo_usado TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Base de datos sistema de riego inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _cargar_configuraciones_cultivos(self):
        """Cargar configuraciones específicas para cada tipo de cultivo"""
        self.configuraciones_cultivos = {
            TipoCultivo.PALTO: ConfiguracionCultivo(
                tipo=TipoCultivo.PALTO,
                humedad_optima_min=60.0,
                humedad_optima_max=80.0,
                humedad_critica_min=45.0,
                temperatura_optima_min=15.0,
                temperatura_optima_max=30.0,
                frecuencia_riego_dias=3,
                duracion_riego_minutos=45,
                profundidad_raiz_cm=60,
                coeficiente_cultivo=0.8
            ),
            TipoCultivo.UVA: ConfiguracionCultivo(
                tipo=TipoCultivo.UVA,
                humedad_optima_min=50.0,
                humedad_optima_max=70.0,
                humedad_critica_min=35.0,
                temperatura_optima_min=18.0,
                temperatura_optima_max=35.0,
                frecuencia_riego_dias=4,
                duracion_riego_minutos=60,
                profundidad_raiz_cm=80,
                coeficiente_cultivo=0.7
            ),
            TipoCultivo.CITRICOS: ConfiguracionCultivo(
                tipo=TipoCultivo.CITRICOS,
                humedad_optima_min=55.0,
                humedad_optima_max=75.0,
                humedad_critica_min=40.0,
                temperatura_optima_min=20.0,
                temperatura_optima_max=32.0,
                frecuencia_riego_dias=2,
                duracion_riego_minutos=30,
                profundidad_raiz_cm=50,
                coeficiente_cultivo=0.9
            ),
            TipoCultivo.HORTALIZAS: ConfiguracionCultivo(
                tipo=TipoCultivo.HORTALIZAS,
                humedad_optima_min=70.0,
                humedad_optima_max=85.0,
                humedad_critica_min=50.0,
                temperatura_optima_min=15.0,
                temperatura_optima_max=28.0,
                frecuencia_riego_dias=1,
                duracion_riego_minutos=20,
                profundidad_raiz_cm=30,
                coeficiente_cultivo=1.1
            ),
            TipoCultivo.CEREALES: ConfiguracionCultivo(
                tipo=TipoCultivo.CEREALES,
                humedad_optima_min=45.0,
                humedad_optima_max=65.0,
                humedad_critica_min=30.0,
                temperatura_optima_min=12.0,
                temperatura_optima_max=25.0,
                frecuencia_riego_dias=5,
                duracion_riego_minutos=90,
                profundidad_raiz_cm=40,
                coeficiente_cultivo=0.6
            )
        }
    
    def _inicializar_dispositivos_iot(self):
        """Inicializar sensores y actuadores IoT"""
        try:
            # Configurar sensores de humedad (simulados)
            ubicaciones_sensores = [
                'sector_a', 'sector_b', 'sector_c', 'sector_d'
            ]
            
            for i, ubicacion in enumerate(ubicaciones_sensores):
                pin_humedad = 18 + i  # GPIO pins simulados
                pin_temp = 22 + i
                pin_riego = 4 + i
                
                self.sensores_humedad[ubicacion] = SensorHumedad(pin_humedad)
                self.sensores_temperatura[ubicacion] = SensorTemperatura(pin_temp)
                self.actuadores_riego[ubicacion] = ActuadorRiego(pin_riego)
                
                # Registrar sensores en base de datos
                self._registrar_sensor('humedad', ubicacion, pin_humedad)
                self._registrar_sensor('temperatura', ubicacion, pin_temp)
            
            print(f"[IOT] {len(self.sensores_humedad)} sensores de humedad inicializados")
            print(f"[IOT] {len(self.sensores_temperatura)} sensores de temperatura inicializados")
            print(f"[IOT] {len(self.actuadores_riego)} actuadores de riego inicializados")
            
        except Exception as e:
            self.logger.error(f"Error inicializando dispositivos IoT: {e}")
    
    def _cargar_modelos_ml(self) -> Dict[str, Any]:
        """Cargar modelos de Machine Learning para predicciones"""
        try:
            modelos = {}
            
            # Intentar cargar modelos híbridos si están disponibles
            if os.path.exists('modelos_ultra_optimizados'):
                try:
                    import joblib
                    for archivo in os.listdir('modelos_ultra_optimizados'):
                        if archivo.endswith('.joblib'):
                            nombre_modelo = archivo.replace('.joblib', '')
                            ruta_modelo = os.path.join('modelos_ultra_optimizados', archivo)
                            modelos[nombre_modelo] = joblib.load(ruta_modelo)
                            print(f"[ML] Modelo cargado: {nombre_modelo}")
                except Exception as e:
                    print(f"[ML] Error cargando modelos: {e}")
            
            return modelos
            
        except Exception as e:
            self.logger.error(f"Error cargando modelos ML: {e}")
            return {}
    
    def _registrar_sensor(self, tipo: str, ubicacion: str, pin: int):
        """Registrar sensor en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO sensores (tipo, ubicacion, pin, ultima_lectura, fecha_ultima_lectura)
                VALUES (?, ?, ?, ?, ?)
            ''', (tipo, ubicacion, pin, 0.0, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando sensor: {e}")
    
    def leer_sensores(self) -> Dict[str, Dict[str, float]]:
        """Leer todos los sensores y almacenar datos"""
        try:
            datos_sensores = {}
            
            for ubicacion in self.sensores_humedad.keys():
                # Leer humedad
                humedad = self.sensores_humedad[ubicacion].leer_humedad()
                
                # Leer temperatura
                temperatura = self.sensores_temperatura[ubicacion].leer_temperatura()
                
                datos_sensores[ubicacion] = {
                    'humedad': humedad,
                    'temperatura': temperatura,
                    'timestamp': datetime.now()
                }
                
                # Almacenar en base de datos
                self._almacenar_lectura_sensor('humedad', ubicacion, humedad, '%')
                self._almacenar_lectura_sensor('temperatura', ubicacion, temperatura, '°C')
            
            return datos_sensores
            
        except Exception as e:
            self.logger.error(f"Error leyendo sensores: {e}")
            return {}
    
    def _almacenar_lectura_sensor(self, tipo_sensor: str, ubicacion: str, valor: float, unidad: str):
        """Almacenar lectura de sensor en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Obtener ID del sensor
            cursor.execute('SELECT id FROM sensores WHERE tipo = ? AND ubicacion = ?', 
                         (tipo_sensor, ubicacion))
            sensor_id = cursor.fetchone()
            
            if sensor_id:
                cursor.execute('''
                    INSERT INTO lecturas_sensores 
                    (sensor_id, tipo_sensor, valor, unidad, ubicacion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sensor_id[0], tipo_sensor, valor, unidad, ubicacion))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error almacenando lectura de sensor: {e}")
    
    def evaluar_necesidad_riego(self, ubicacion: str, cultivo: TipoCultivo) -> Dict[str, Any]:
        """Evaluar si es necesario regar en una ubicación específica"""
        try:
            # Leer sensores de la ubicación
            humedad_actual = self.sensores_humedad[ubicacion].leer_humedad()
            temperatura_actual = self.sensores_temperatura[ubicacion].leer_temperatura()
            
            # Obtener configuración del cultivo
            config = self.configuraciones_cultivos[cultivo]
            
            # Evaluar condiciones
            necesidad_riego = False
            urgencia = 'normal'
            duracion_recomendada = config.duracion_riego_minutos
            
            # Lógica de decisión
            if humedad_actual < config.humedad_critica_min:
                necesidad_riego = True
                urgencia = 'critica'
                duracion_recomendada = int(config.duracion_riego_minutos * 1.5)
            elif humedad_actual < config.humedad_optima_min:
                necesidad_riego = True
                urgencia = 'alta'
                duracion_recomendada = int(config.duracion_riego_minutos * 1.2)
            elif humedad_actual > config.humedad_optima_max:
                necesidad_riego = False
                urgencia = 'baja'
            
            # Ajustar según temperatura
            if temperatura_actual > config.temperatura_optima_max:
                if necesidad_riego:
                    duracion_recomendada = int(duracion_recomendada * 1.1)
            elif temperatura_actual < config.temperatura_optima_min:
                if necesidad_riego:
                    duracion_recomendada = int(duracion_recomendada * 0.9)
            
            resultado = {
                'ubicacion': ubicacion,
                'cultivo': cultivo.value,
                'humedad_actual': humedad_actual,
                'temperatura_actual': temperatura_actual,
                'necesidad_riego': necesidad_riego,
                'urgencia': urgencia,
                'duracion_recomendada_segundos': duracion_recomendada * 60,
                'configuracion_usada': {
                    'humedad_optima_min': config.humedad_optima_min,
                    'humedad_optima_max': config.humedad_optima_max,
                    'humedad_critica_min': config.humedad_critica_min
                },
                'timestamp': datetime.now()
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error evaluando necesidad de riego: {e}")
            return {}
    
    def ejecutar_riego_inteligente(self, ubicacion: str, duracion_segundos: int, motivo: str = "automatico"):
        """Ejecutar riego en ubicación específica"""
        try:
            if ubicacion not in self.actuadores_riego:
                raise ValueError(f"Ubicación '{ubicacion}' no encontrada")
            
            actuador = self.actuadores_riego[ubicacion]
            
            # Verificar si ya hay riego activo
            if actuador.estado:
                print(f"⚠️ Riego ya activo en {ubicacion}")
                return False
            
            # Leer humedad antes del riego
            humedad_inicial = self.sensores_humedad[ubicacion].leer_humedad()
            temperatura = self.sensores_temperatura[ubicacion].leer_temperatura()
            
            # Activar riego
            actuador.activar(duracion_segundos)
            
            # Registrar evento
            self._registrar_evento_riego(ubicacion, 'inicio', duracion_segundos, 
                                       humedad_inicial, temperatura, motivo)
            
            print(f"💧 Riego iniciado en {ubicacion} por {duracion_segundos}s ({motivo})")
            
            # Programar lectura post-riego
            threading.Timer(duracion_segundos + 300, self._finalizar_riego, 
                          args=[ubicacion]).start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando riego: {e}")
            return False
    
    def _finalizar_riego(self, ubicacion: str):
        """Finalizar riego y registrar resultados"""
        try:
            # Leer humedad después del riego
            humedad_final = self.sensores_humedad[ubicacion].leer_humedad()
            temperatura = self.sensores_temperatura[ubicacion].leer_temperatura()
            
            # Registrar evento de finalización
            self._registrar_evento_riego(ubicacion, 'finalizado', 0, 
                                       humedad_final, temperatura, 'automatico')
            
            print(f"✅ Riego finalizado en {ubicacion}. Humedad: {humedad_final:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error finalizando riego: {e}")
    
    def _registrar_evento_riego(self, ubicacion: str, tipo_evento: str, 
                              duracion_segundos: int, humedad: float, 
                              temperatura: float, motivo: str):
        """Registrar evento de riego en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO eventos_riego 
                (actuador_id, tipo_evento, duracion_segundos, humedad_inicial, 
                 humedad_final, temperatura, cultivo, fecha_evento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (1, tipo_evento, duracion_segundos, humedad, humedad, 
                  temperatura, ubicacion, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando evento de riego: {e}")
    
    def generar_prediccion_riego_ml(self, ubicacion: str, cultivo: TipoCultivo, 
                                   horizonte_horas: int = 24) -> Dict[str, Any]:
        """Generar predicción de necesidad de riego usando ML"""
        try:
            if not self.modelos_ml:
                return {'error': 'No hay modelos ML disponibles'}
            
            # Leer datos actuales
            datos_actuales = self.leer_sensores()
            if ubicacion not in datos_actuales:
                return {'error': f'Ubicación {ubicacion} no encontrada'}
            
            humedad_actual = datos_actuales[ubicacion]['humedad']
            temperatura_actual = datos_actuales[ubicacion]['temperatura']
            
            # Simular predicción (en producción usaría modelos ML reales)
            config = self.configuraciones_cultivos[cultivo]
            
            # Calcular tendencia de humedad
            tendencia_humedad = -0.5  # Porcentaje por hora (simulado)
            humedad_predicha = humedad_actual + (tendencia_humedad * horizonte_horas)
            
            # Determinar necesidad de riego
            necesidad_riego = humedad_predicha < config.humedad_optima_min
            
            # Calcular duración recomendada
            duracion_recomendada = 0
            if necesidad_riego:
                deficit_humedad = config.humedad_optima_min - humedad_predicha
                duracion_recomendada = int((deficit_humedad / 10) * 60)  # Minutos
            
            prediccion = {
                'ubicacion': ubicacion,
                'cultivo': cultivo.value,
                'horizonte_horas': horizonte_horas,
                'humedad_actual': humedad_actual,
                'temperatura_actual': temperatura_actual,
                'humedad_predicha': max(0, humedad_predicha),
                'necesidad_riego': necesidad_riego,
                'duracion_recomendada_minutos': duracion_recomendada,
                'confianza': 0.85,
                'modelo_usado': 'simulado_ml',
                'timestamp': datetime.now()
            }
            
            # Almacenar predicción
            self._almacenar_prediccion(prediccion)
            
            return prediccion
            
        except Exception as e:
            self.logger.error(f"Error generando predicción ML: {e}")
            return {'error': str(e)}
    
    def _almacenar_prediccion(self, prediccion: Dict[str, Any]):
        """Almacenar predicción en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predicciones_riego 
                (cultivo, ubicacion, fecha_prediccion, humedad_predicha, 
                 necesidad_riego, duracion_recomendada, confianza, modelo_usado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediccion['cultivo'],
                prediccion['ubicacion'],
                datetime.now() + timedelta(hours=prediccion['horizonte_horas']),
                prediccion['humedad_predicha'],
                prediccion['necesidad_riego'],
                prediccion['duracion_recomendada_minutos'],
                prediccion['confianza'],
                prediccion['modelo_usado']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error almacenando predicción: {e}")
    
    def ejecutar_ciclo_riego_automatico(self):
        """Ejecutar ciclo automático de evaluación y riego"""
        try:
            print(f"[CICLO] Iniciando evaluación automática - {datetime.now()}")
            
            # Configuración de cultivos por ubicación (simulado)
            cultivos_ubicacion = {
                'sector_a': TipoCultivo.PALTO,
                'sector_b': TipoCultivo.UVA,
                'sector_c': TipoCultivo.CITRICOS,
                'sector_d': TipoCultivo.HORTALIZAS
            }
            
            for ubicacion, cultivo in cultivos_ubicacion.items():
                # Evaluar necesidad de riego
                evaluacion = self.evaluar_necesidad_riego(ubicacion, cultivo)
                
                if evaluacion['necesidad_riego']:
                    print(f"[RIEGO] {ubicacion} ({cultivo.value}): Humedad {evaluacion['humedad_actual']:.1f}% - Riego necesario")
                    
                    # Ejecutar riego si está en modo automático
                    if self.estado_sistema['modo_automatico']:
                        duracion = evaluacion['duracion_recomendada_segundos']
                        self.ejecutar_riego_inteligente(ubicacion, duracion, 'automatico')
                    else:
                        print(f"[RIEGO] Modo automático desactivado - Riego no ejecutado")
                else:
                    print(f"[RIEGO] {ubicacion} ({cultivo.value}): Humedad {evaluacion['humedad_actual']:.1f}% - No requiere riego")
            
            self.estado_sistema['ultima_evaluacion'] = datetime.now()
            print(f"[CICLO] Evaluación completada")
            
        except Exception as e:
            self.logger.error(f"Error en ciclo automático: {e}")
    
    def iniciar_monitoreo_continuo(self):
        """Iniciar monitoreo continuo del sistema"""
        try:
            print("[SISTEMA] Iniciando monitoreo continuo...")
            
            # Programar evaluación cada 2 horas
            schedule.every(2).hours.do(self.ejecutar_ciclo_riego_automatico)
            
            # Programar lectura de sensores cada 30 minutos
            schedule.every(30).minutes.do(self.leer_sensores)
            
            # Programar generación de reportes diarios
            schedule.every().day.at("06:00").do(self.generar_reporte_diario)
            
            print("[SISTEMA] Monitoreo programado:")
            print("  - Evaluación de riego: cada 2 horas")
            print("  - Lectura de sensores: cada 30 minutos")
            print("  - Reportes diarios: 06:00 AM")
            
            # Ejecutar primera evaluación
            self.ejecutar_ciclo_riego_automatico()
            
            # Mantener el sistema ejecutándose
            while self.estado_sistema['activo']:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            print("[SISTEMA] Deteniendo monitoreo continuo...")
            self.estado_sistema['activo'] = False
        except Exception as e:
            self.logger.error(f"Error en monitoreo continuo: {e}")
    
    def generar_reporte_diario(self):
        """Generar reporte diario del sistema de riego"""
        try:
            fecha = datetime.now().strftime('%Y-%m-%d')
            print(f"[REPORTE] Generando reporte diario para {fecha}")
            
            conn = sqlite3.connect(self.base_datos)
            
            # Estadísticas de riego del día
            query_riego = '''
                SELECT ubicacion, COUNT(*) as eventos, 
                       SUM(duracion_segundos) as duracion_total
                FROM eventos_riego 
                WHERE DATE(fecha_evento) = DATE('now')
                GROUP BY ubicacion
            '''
            
            df_riego = pd.read_sql_query(query_riego, conn)
            
            # Estadísticas de sensores
            query_sensores = '''
                SELECT ubicacion, AVG(valor) as promedio_humedad
                FROM lecturas_sensores 
                WHERE tipo_sensor = 'humedad' 
                AND DATE(fecha_lectura) = DATE('now')
                GROUP BY ubicacion
            '''
            
            df_sensores = pd.read_sql_query(query_sensores, conn)
            
            conn.close()
            
            # Crear reporte
            reporte = {
                'fecha': fecha,
                'eventos_riego': df_riego.to_dict('records') if not df_riego.empty else [],
                'estadisticas_sensores': df_sensores.to_dict('records') if not df_sensores.empty else [],
                'estado_sistema': self.estado_sistema.copy(),
                'configuraciones_cultivos': len(self.configuraciones_cultivos),
                'sensores_activos': len(self.sensores_humedad),
                'actuadores_activos': len(self.actuadores_riego)
            }
            
            # Guardar reporte
            ruta_reporte = os.path.join('reportes_riego', f'reporte_{fecha}.json')
            with open(ruta_reporte, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, default=str)
            
            print(f"[REPORTE] Reporte guardado en {ruta_reporte}")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte diario: {e}")
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        try:
            estado = {
                'sistema': self.estado_sistema.copy(),
                'sensores': {},
                'actuadores': {},
                'configuraciones': {}
            }
            
            # Estado de sensores
            for ubicacion in self.sensores_humedad.keys():
                estado['sensores'][ubicacion] = {
                    'humedad': self.sensores_humedad[ubicacion].ultima_lectura,
                    'temperatura': self.sensores_temperatura[ubicacion].ultima_lectura
                }
            
            # Estado de actuadores
            for ubicacion in self.actuadores_riego.keys():
                actuador = self.actuadores_riego[ubicacion]
                estado['actuadores'][ubicacion] = {
                    'activo': actuador.estado,
                    'tiempo_activacion': actuador.tiempo_activacion
                }
            
            # Configuraciones de cultivos
            for cultivo, config in self.configuraciones_cultivos.items():
                estado['configuraciones'][cultivo.value] = {
                    'humedad_optima_min': config.humedad_optima_min,
                    'humedad_optima_max': config.humedad_optima_max,
                    'duracion_riego_minutos': config.duracion_riego_minutos
                }
            
            return estado
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {}

def main():
    """Función principal para demostración del sistema de riego"""
    print("="*80)
    print("SISTEMA DE RIEGO INTELIGENTE - METGO 3D QUILLOTA")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaRiegoInteligente()
    
    # Demostración del sistema
    print("\n[1] LECTURA DE SENSORES...")
    datos_sensores = sistema.leer_sensores()
    for ubicacion, datos in datos_sensores.items():
        print(f"  {ubicacion}: Humedad {datos['humedad']:.1f}%, Temp {datos['temperatura']:.1f}°C")
    
    print("\n[2] EVALUACIÓN DE NECESIDAD DE RIEGO...")
    cultivos_ubicacion = {
        'sector_a': TipoCultivo.PALTO,
        'sector_b': TipoCultivo.UVA,
        'sector_c': TipoCultivo.CITRICOS,
        'sector_d': TipoCultivo.HORTALIZAS
    }
    
    for ubicacion, cultivo in cultivos_ubicacion.items():
        evaluacion = sistema.evaluar_necesidad_riego(ubicacion, cultivo)
        if evaluacion:
            estado = "RIEGO NECESARIO" if evaluacion['necesidad_riego'] else "OK"
            print(f"  {ubicacion} ({cultivo.value}): {estado} - Humedad {evaluacion['humedad_actual']:.1f}%")
    
    print("\n[3] PREDICCIONES ML...")
    for ubicacion, cultivo in list(cultivos_ubicacion.items())[:2]:  # Solo 2 para demo
        prediccion = sistema.generar_prediccion_riego_ml(ubicacion, cultivo, 24)
        if 'error' not in prediccion:
            print(f"  {ubicacion}: Humedad predicha {prediccion['humedad_predicha']:.1f}% en 24h")
    
    print("\n[4] ESTADO DEL SISTEMA...")
    estado = sistema.obtener_estado_sistema()
    print(f"  Sistema activo: {estado['sistema']['activo']}")
    print(f"  Modo automático: {estado['sistema']['modo_automatico']}")
    print(f"  Sensores activos: {len(estado['sensores'])}")
    print(f"  Actuadores activos: {len(estado['actuadores'])}")
    
    print("\n" + "="*80)
    print("SISTEMA DE RIEGO INTELIGENTE LISTO")
    print("="*80)
    print("Para iniciar monitoreo continuo:")
    print("sistema.iniciar_monitoreo_continuo()")
    print("="*80)

if __name__ == "__main__":
    main()



