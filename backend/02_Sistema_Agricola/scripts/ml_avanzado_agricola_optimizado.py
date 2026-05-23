"""
MACHINE LEARNING AVANZADO AGRÍCOLA OPTIMIZADO - METGO 3D QUILLOTA
Versión optimizada para entrenamiento rápido con menos datos
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Tuple, Optional
import os

warnings.filterwarnings('ignore')

class MLAvanzadoAgricolaOptimizado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "ml_avanzado_agricola_optimizado.db"
        self.modelos_dir = "modelos_ml_avanzados"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos = {}
        self.scalers = {}
        self.metricas_modelos = {}
        
        # Configuración de cultivos específicos de Quillota
        self.cultivos_quillota = {
            'paltos': {
                'nombre': 'Paltos',
                'temp_optima_min': 15,
                'temp_optima_max': 25,
                'temp_helada_critica': 2,
                'temp_helada_advertencia': 5,
                'humedad_optima_min': 60,
                'humedad_optima_max': 80,
                'periodo_sensible_helada': ['mayo', 'junio', 'julio', 'agosto'],
                'periodo_cosecha': ['enero', 'febrero', 'marzo', 'abril']
            },
            'citricos': {
                'nombre': 'Cítricos',
                'temp_optima_min': 12,
                'temp_optima_max': 28,
                'temp_helada_critica': -2,
                'temp_helada_advertencia': 3,
                'humedad_optima_min': 50,
                'humedad_optima_max': 70,
                'periodo_sensible_helada': ['mayo', 'junio', 'julio'],
                'periodo_cosecha': ['abril', 'mayo', 'junio', 'julio']
            },
            'uvas': {
                'nombre': 'Uvas',
                'temp_optima_min': 18,
                'temp_optima_max': 30,
                'temp_helada_critica': 0,
                'temp_helada_advertencia': 4,
                'humedad_optima_min': 40,
                'humedad_optima_max': 60,
                'periodo_sensible_helada': ['agosto', 'septiembre'],
                'periodo_cosecha': ['febrero', 'marzo', 'abril']
            },
            'nogales': {
                'nombre': 'Nogales',
                'temp_optima_min': 10,
                'temp_optima_max': 25,
                'temp_helada_critica': -3,
                'temp_helada_advertencia': 2,
                'humedad_optima_min': 45,
                'humedad_optima_max': 65,
                'periodo_sensible_helada': ['mayo', 'junio', 'julio', 'agosto'],
                'periodo_cosecha': ['marzo', 'abril', 'mayo']
            }
        }
        
        # Patrones de plagas comunes en Quillota
        self.patrones_plagas = {
            'araña_roja': {
                'condiciones_favorables': {
                    'temp_min': 20,
                    'temp_max': 35,
                    'humedad_max': 60,
                    'viento_max': 15
                },
                'cultivos_afectados': ['paltos', 'citricos'],
                'sintomas': 'Puntos amarillos en hojas, telarañas'
            },
            'pulgones': {
                'condiciones_favorables': {
                    'temp_min': 15,
                    'temp_max': 25,
                    'humedad_min': 70,
                    'viento_max': 10
                },
                'cultivos_afectados': ['paltos', 'citricos', 'uvas'],
                'sintomas': 'Hojas enrolladas, melaza en hojas'
            },
            'mosca_blanca': {
                'condiciones_favorables': {
                    'temp_min': 18,
                    'temp_max': 30,
                    'humedad_min': 60,
                    'viento_max': 12
                },
                'cultivos_afectados': ['paltos', 'citricos'],
                'sintomas': 'Nubes de insectos blancos, hojas amarillas'
            },
            'oidio': {
                'condiciones_favorables': {
                    'temp_min': 15,
                    'temp_max': 25,
                    'humedad_min': 80,
                    'viento_max': 8
                },
                'cultivos_afectados': ['uvas', 'nogales'],
                'sintomas': 'Polvo blanco en hojas y frutos'
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.modelos_dir, 'logs', 'data_historica']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para ML avanzado"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de datos históricos meteorológicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_historicos_meteorologicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATETIME NOT NULL,
                    estacion TEXT NOT NULL,
                    temperatura_max REAL,
                    temperatura_min REAL,
                    temperatura_promedio REAL,
                    humedad_relativa REAL,
                    velocidad_viento REAL,
                    direccion_viento REAL,
                    precipitacion REAL,
                    presion_atmosferica REAL,
                    nubosidad REAL,
                    radiacion_solar REAL,
                    punto_rocio REAL,
                    indice_calor REAL,
                    indice_frio REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas de heladas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_heladas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_alerta DATETIME NOT NULL,
                    estacion TEXT NOT NULL,
                    cultivo TEXT NOT NULL,
                    probabilidad_helada REAL NOT NULL,
                    temperatura_predicha REAL NOT NULL,
                    dias_anticipacion INTEGER NOT NULL,
                    severidad TEXT NOT NULL,
                    recomendaciones TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de predicciones de cosecha
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones_cosecha (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_prediccion DATETIME NOT NULL,
                    cultivo TEXT NOT NULL,
                    estacion TEXT NOT NULL,
                    fecha_optima_cosecha DATETIME,
                    calidad_predicha TEXT,
                    rendimiento_estimado REAL,
                    factores_clave TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas de plagas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_plagas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_alerta DATETIME NOT NULL,
                    cultivo TEXT NOT NULL,
                    plaga TEXT NOT NULL,
                    probabilidad_aparicion REAL NOT NULL,
                    condiciones_favorables TEXT,
                    recomendaciones TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Base de datos ML avanzado optimizado inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def generar_datos_historicos_optimizados(self, meses: int = 12) -> pd.DataFrame:
        """Generar datos históricos optimizados (por días, no por horas)"""
        try:
            np.random.seed(42)
            
            # Generar fechas para los últimos meses (por días, no por horas)
            fecha_inicio = datetime.now() - timedelta(days=meses * 30)
            fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
            
            datos = []
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            
            for fecha in fechas:
                for estacion in estaciones:
                    # Patrones estacionales
                    mes = fecha.month
                    
                    # Temperatura con patrones estacionales
                    temp_base = 15 + 8 * np.sin(2 * np.pi * (mes - 1) / 12)  # Variación estacional
                    temp_max = temp_base + np.random.normal(5, 2)
                    temp_min = temp_base - np.random.normal(5, 1.5)
                    temp_promedio = (temp_max + temp_min) / 2
                    
                    # Humedad relativa (inversamente relacionada con temperatura)
                    humedad = 80 - (temp_promedio - 15) * 2 + np.random.normal(0, 10)
                    humedad = np.clip(humedad, 20, 95)
                    
                    # Viento
                    velocidad_viento = np.random.exponential(8) + np.random.normal(0, 3)
                    direccion_viento = np.random.uniform(0, 360)
                    
                    # Precipitación (más común en invierno)
                    prob_lluvia = 0.3 if mes in [6, 7, 8] else 0.1
                    precipitacion = np.random.exponential(2) if np.random.random() < prob_lluvia else 0
                    
                    # Presión atmosférica
                    presion = 1013 + np.random.normal(0, 5)
                    
                    # Nubosidad
                    nubosidad = min(100, max(0, humedad / 2 + np.random.normal(0, 20)))
                    
                    # Radiación solar
                    radiacion = max(0, 800 - nubosidad * 4 + np.random.normal(0, 50))
                    
                    # Punto de rocío
                    punto_rocio = temp_promedio - (100 - humedad) / 5
                    
                    # Índices térmicos
                    indice_calor = temp_promedio + (humedad - 50) * 0.1
                    indice_frio = temp_promedio - np.sqrt(velocidad_viento) * 0.5
                    
                    datos.append({
                        'fecha': fecha,
                        'estacion': estacion,
                        'temperatura_max': round(temp_max, 1),
                        'temperatura_min': round(temp_min, 1),
                        'temperatura_promedio': round(temp_promedio, 1),
                        'humedad_relativa': round(humedad, 1),
                        'velocidad_viento': round(velocidad_viento, 1),
                        'direccion_viento': round(direccion_viento, 1),
                        'precipitacion': round(precipitacion, 1),
                        'presion_atmosferica': round(presion, 1),
                        'nubosidad': round(nubosidad, 1),
                        'radiacion_solar': round(radiacion, 1),
                        'punto_rocio': round(punto_rocio, 1),
                        'indice_calor': round(indice_calor, 1),
                        'indice_frio': round(indice_frio, 1)
                    })
            
            df = pd.DataFrame(datos)
            
            # Guardar en base de datos
            self._guardar_datos_historicos(df)
            
            self.logger.info(f"Datos históricos optimizados generados: {len(df)} registros para {meses} meses")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generando datos históricos optimizados: {e}")
            return pd.DataFrame()
    
    def _guardar_datos_historicos(self, df: pd.DataFrame):
        """Guardar datos históricos en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            
            df.to_sql('datos_historicos_meteorologicos', conn, if_exists='replace', index=False)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Datos históricos guardados en base de datos")
            
        except Exception as e:
            self.logger.error(f"Error guardando datos históricos: {e}")
    
    def entrenar_modelos_rapidos(self, variable_objetivo: str = 'temperatura_promedio'):
        """Entrenar modelos rápidos y optimizados"""
        try:
            print(f"[ENTRENANDO] Modelos optimizados para {variable_objetivo}...")
            
            # Cargar datos históricos
            df = self._cargar_datos_historicos()
            
            if df.empty:
                print("[GENERANDO] Datos históricos optimizados...")
                df = self.generar_datos_historicos_optimizados(12)  # Solo 12 meses
            
            # Preparar datos
            X, y = self._preparar_datos_entrenamiento(df, variable_objetivo)
            
            # Verificar que tenemos datos válidos
            if len(X) == 0 or len(y) == 0:
                print("[ERROR] No hay datos válidos para entrenar")
                return {}
            
            print(f"[DATOS] {len(X)} muestras, {X.shape[1]} características")
            
            # Definir modelos optimizados (menos complejos, más rápidos)
            modelos = {
                'RandomForest_Rapido': RandomForestRegressor(
                    n_estimators=50,  # Menos árboles
                    max_depth=10,     # Menor profundidad
                    min_samples_split=10,
                    random_state=42,
                    n_jobs=-1
                ),
                'GradientBoosting_Rapido': GradientBoostingRegressor(
                    n_estimators=50,  # Menos árboles
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                ),
                'Ridge_Optimizado': Ridge(
                    alpha=1.0,
                    solver='auto'
                )
            }
            
            # Entrenar modelos con validación cruzada temporal
            resultados = {}
            tscv = TimeSeriesSplit(n_splits=3)  # Menos divisiones
            
            for nombre, modelo in modelos.items():
                print(f"[ENTRENANDO] {nombre}...")
                
                # Entrenar modelo
                modelo.fit(X, y)
                
                # Validación cruzada
                scores = cross_val_score(modelo, X, y, cv=tscv, scoring='neg_mean_squared_error')
                rmse_scores = np.sqrt(-scores)
                
                # Métricas
                y_pred = modelo.predict(X)
                r2 = r2_score(y, y_pred)
                rmse = np.sqrt(mean_squared_error(y, y_pred))
                
                resultados[nombre] = {
                    'modelo': modelo,
                    'r2': r2,
                    'rmse': rmse,
                    'cv_rmse_mean': rmse_scores.mean(),
                    'cv_rmse_std': rmse_scores.std()
                }
                
                print(f"[OK] {nombre}: R²={r2:.4f}, RMSE={rmse:.4f}")
            
            # Guardar mejores modelos
            self.modelos[variable_objetivo] = resultados
            self.metricas_modelos[variable_objetivo] = resultados
            
            # Guardar modelos en disco
            for nombre, resultado in resultados.items():
                if resultado['r2'] > 0.7:  # Umbral más bajo
                    ruta_modelo = os.path.join(self.modelos_dir, f"{nombre}_{variable_objetivo}.joblib")
                    joblib.dump(resultado['modelo'], ruta_modelo)
                    print(f"[GUARDADO] {nombre}")
            
            return resultados
            
        except Exception as e:
            print(f"[ERROR] Error entrenando modelos: {e}")
            return {}
    
    def _cargar_datos_historicos(self) -> pd.DataFrame:
        """Cargar datos históricos de la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            df = pd.read_sql_query(
                "SELECT * FROM datos_historicos_meteorologicos ORDER BY fecha",
                conn,
                parse_dates=['fecha']
            )
            conn.close()
            return df
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos: {e}")
            return pd.DataFrame()
    
    def _preparar_datos_entrenamiento(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento (versión simplificada)"""
        try:
            # Crear características temporales básicas
            df['mes'] = df['fecha'].dt.month
            df['dia_año'] = df['fecha'].dt.dayofyear
            
            # Características cíclicas básicas
            df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
            df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
            
            # Codificar estación
            if 'estacion' in df.columns:
                estacion_encoded = pd.get_dummies(df['estacion'], prefix='estacion')
                df = pd.concat([df, estacion_encoded], axis=1)
            
            # Seleccionar características básicas
            caracteristicas_base = [
                'temperatura_max', 'temperatura_min', 'humedad_relativa',
                'velocidad_viento', 'precipitacion', 'presion_atmosferica',
                'mes', 'dia_año', 'mes_sin', 'mes_cos'
            ]
            
            # Agregar columnas de estación si existen
            caracteristicas_estacion = [col for col in df.columns if col.startswith('estacion_')]
            caracteristicas = [col for col in caracteristicas_base if col in df.columns] + caracteristicas_estacion
            
            # Verificar que tenemos al menos algunas características
            if not caracteristicas:
                self.logger.error("No se encontraron características válidas")
                return np.array([]), np.array([])
            
            X = df[caracteristicas].fillna(df[caracteristicas].mean())
            y = df[variable_objetivo].fillna(df[variable_objetivo].mean())
            
            # Escalar características
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers[variable_objetivo] = scaler
            
            return X_scaled, y.values
            
        except Exception as e:
            self.logger.error(f"Error preparando datos de entrenamiento: {e}")
            return np.array([]), np.array([])
    
    def predecir_heladas_7_dias_rapido(self, estacion: str = 'quillota_centro') -> List[Dict]:
        """Predecir heladas con 7 días de anticipación (versión rápida)"""
        try:
            print(f"[PREDICIENDO] Heladas para {estacion}...")
            
            if 'temperatura_promedio' not in self.modelos:
                print("[ENTRENANDO] Modelos rápidos...")
                self.entrenar_modelos_rapidos('temperatura_promedio')
            
            # Obtener mejor modelo
            mejor_modelo = self._obtener_mejor_modelo('temperatura_promedio')
            
            if mejor_modelo is None:
                print("[ERROR] No hay modelos entrenados")
                return []
            
            # Generar predicciones para 7 días
            predicciones = []
            fecha_actual = datetime.now()
            
            for i in range(7):
                fecha_prediccion = fecha_actual + timedelta(days=i)
                
                # Preparar características simplificadas para predicción
                X_pred = self._preparar_caracteristicas_prediccion_simple(fecha_prediccion, estacion)
                
                # Predecir temperatura
                temp_predicha = mejor_modelo.predict(X_pred.reshape(1, -1))[0]
                
                # Evaluar riesgo de helada por cultivo
                alertas_helada = self._evaluar_riesgo_helada(temp_predicha, fecha_prediccion)
                
                prediccion = {
                    'fecha': fecha_prediccion.strftime('%Y-%m-%d'),
                    'dias_anticipacion': i + 1,
                    'temperatura_predicha': round(temp_predicha, 1),
                    'estacion': estacion,
                    'alertas_helada': alertas_helada,
                    'confianza': self._calcular_confianza_prediccion(i + 1)
                }
                
                predicciones.append(prediccion)
                
                # Guardar predicción en base de datos
                self._guardar_prediccion_helada(prediccion)
            
            print(f"[OK] Predicciones generadas: {len(predicciones)}")
            return predicciones
            
        except Exception as e:
            print(f"[ERROR] Error prediciendo heladas: {e}")
            return []
    
    def _preparar_caracteristicas_prediccion_simple(self, fecha: datetime, estacion: str) -> np.ndarray:
        """Preparar características simplificadas para predicción"""
        # Características básicas
        mes = fecha.month
        dia_año = fecha.timetuple().tm_yday
        
        # Simular datos meteorológicos actuales
        datos_actuales = {
            'temperatura_max': 22.0,
            'temperatura_min': 12.0,
            'humedad_relativa': 65.0,
            'velocidad_viento': 10.0,
            'precipitacion': 0.0,
            'presion_atmosferica': 1013.0
        }
        
        # Características básicas
        caracteristicas = [
            datos_actuales['temperatura_max'],
            datos_actuales['temperatura_min'],
            datos_actuales['humedad_relativa'],
            datos_actuales['velocidad_viento'],
            datos_actuales['precipitacion'],
            datos_actuales['presion_atmosferica'],
            mes,
            dia_año,
            np.sin(2 * np.pi * mes / 12),
            np.cos(2 * np.pi * mes / 12)
        ]
        
        # Agregar codificación de estación
        estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
        for est in estaciones:
            caracteristicas.append(1 if est == estacion else 0)
        
        return np.array(caracteristicas)
    
    def _evaluar_riesgo_helada(self, temperatura: float, fecha: datetime) -> List[Dict]:
        """Evaluar riesgo de helada por cultivo"""
        alertas = []
        mes = fecha.strftime('%B').lower()
        
        for cultivo, config in self.cultivos_quillota.items():
            # Verificar si está en período sensible
            if mes in config['periodo_sensible_helada']:
                if temperatura <= config['temp_helada_critica']:
                    severidad = 'CRÍTICA'
                    probabilidad = 0.9
                elif temperatura <= config['temp_helada_advertencia']:
                    severidad = 'ALTA'
                    probabilidad = 0.7
                elif temperatura <= config['temp_helada_advertencia'] + 2:
                    severidad = 'MEDIA'
                    probabilidad = 0.4
                else:
                    severidad = 'BAJA'
                    probabilidad = 0.1
                
                alertas.append({
                    'cultivo': cultivo,
                    'nombre_cultivo': config['nombre'],
                    'probabilidad_helada': probabilidad,
                    'severidad': severidad,
                    'temperatura_critica': config['temp_helada_critica'],
                    'recomendaciones': self._generar_recomendaciones_helada(cultivo, severidad)
                })
        
        return alertas
    
    def _generar_recomendaciones_helada(self, cultivo: str, severidad: str) -> List[str]:
        """Generar recomendaciones específicas para heladas"""
        recomendaciones = {
            'CRÍTICA': [
                "ACTIVAR INMEDIATAMENTE sistemas de riego por aspersión",
                "Cubrir cultivos con mallas antiheladas",
                "Encender calefactores en invernaderos",
                "Aplicar protectores foliares",
                "Monitorear temperatura cada hora"
            ],
            'ALTA': [
                "Preparar sistemas de riego por aspersión",
                "Tener mallas antiheladas listas",
                "Verificar funcionamiento de calefactores",
                "Aplicar protectores foliares preventivos"
            ],
            'MEDIA': [
                "Monitorear pronósticos meteorológicos",
                "Preparar medidas de protección",
                "Verificar estado de los cultivos"
            ],
            'BAJA': [
                "Monitoreo rutinario",
                "Verificar pronósticos actualizados"
            ]
        }
        
        return recomendaciones.get(severidad, ["Monitoreo continuo"])
    
    def optimizar_fechas_cosecha_rapido(self, cultivo: str, estacion: str = 'quillota_centro') -> Dict:
        """Optimizar fechas de cosecha por cultivo (versión rápida)"""
        try:
            print(f"[OPTIMIZANDO] Fechas de cosecha para {cultivo}...")
            
            if cultivo not in self.cultivos_quillota:
                raise ValueError(f"Cultivo {cultivo} no está configurado")
            
            config_cultivo = self.cultivos_quillota[cultivo]
            
            # Generar predicciones para el período de cosecha (solo 30 días)
            fecha_inicio = datetime.now()
            fecha_fin = fecha_inicio + timedelta(days=30)
            
            fechas_optimas = []
            fecha_actual = fecha_inicio
            
            while fecha_actual <= fecha_fin:
                mes = fecha_actual.strftime('%B').lower()
                
                if mes in config_cultivo['periodo_cosecha']:
                    # Simular predicción de temperatura
                    temp_predicha = 20 + np.random.normal(0, 3)
                    
                    # Calcular calidad de cosecha
                    calidad = self._calcular_calidad_cosecha(
                        temp_predicha, config_cultivo, fecha_actual
                    )
                    
                    fechas_optimas.append({
                        'fecha': fecha_actual.strftime('%Y-%m-%d'),
                        'temperatura_predicha': round(temp_predicha, 1),
                        'calidad_esperada': calidad['nivel'],
                        'score_calidad': calidad['score'],
                        'factores_clave': calidad['factores']
                    })
                
                fecha_actual += timedelta(days=1)
            
            # Ordenar por calidad
            fechas_optimas.sort(key=lambda x: x['score_calidad'], reverse=True)
            
            resultado = {
                'cultivo': cultivo,
                'nombre_cultivo': config_cultivo['nombre'],
                'fecha_optima': fechas_optimas[0]['fecha'] if fechas_optimas else None,
                'fechas_recomendadas': fechas_optimas[:5],  # Top 5
                'periodo_cosecha': config_cultivo['periodo_cosecha'],
                'condiciones_optimas': {
                    'temp_min': config_cultivo['temp_optima_min'],
                    'temp_max': config_cultivo['temp_optima_max'],
                    'humedad_min': config_cultivo['humedad_optima_min'],
                    'humedad_max': config_cultivo['humedad_optima_max']
                }
            }
            
            print(f"[OK] Optimización completada: {resultado['fecha_optima']}")
            return resultado
            
        except Exception as e:
            print(f"[ERROR] Error optimizando fechas de cosecha: {e}")
            return {}
    
    def _calcular_calidad_cosecha(self, temperatura: float, config_cultivo: Dict, fecha: datetime) -> Dict:
        """Calcular calidad esperada de cosecha"""
        # Score base por temperatura
        if config_cultivo['temp_optima_min'] <= temperatura <= config_cultivo['temp_optima_max']:
            score_temp = 100
        else:
            distancia_min = abs(temperatura - config_cultivo['temp_optima_min'])
            distancia_max = abs(temperatura - config_cultivo['temp_optima_max'])
            score_temp = max(0, 100 - min(distancia_min, distancia_max) * 5)
        
        # Score por época del año
        mes = fecha.strftime('%B').lower()
        if mes in config_cultivo['periodo_cosecha']:
            score_epoca = 100
        else:
            score_epoca = 50
        
        # Score final
        score_final = (score_temp * 0.7 + score_epoca * 0.3)
        
        # Determinar nivel de calidad
        if score_final >= 90:
            nivel = "EXCELENTE"
        elif score_final >= 80:
            nivel = "MUY BUENA"
        elif score_final >= 70:
            nivel = "BUENA"
        elif score_final >= 60:
            nivel = "REGULAR"
        else:
            nivel = "DEFICIENTE"
        
        factores = []
        if score_temp < 80:
            factores.append("Temperatura subóptima")
        if score_epoca < 80:
            factores.append("Fuera del período óptimo")
        
        return {
            'score': score_final,
            'nivel': nivel,
            'factores': factores
        }
    
    def detectar_patrones_plagas_rapido(self, cultivo: str, estacion: str = 'quillota_centro') -> List[Dict]:
        """Detectar patrones tempranos de plagas (versión rápida)"""
        try:
            print(f"[DETECTANDO] Patrones de plagas para {cultivo}...")
            
            alertas_plagas = []
            
            # Simular datos meteorológicos actuales
            datos_actuales = {
                'temperatura_promedio': 20.0,
                'humedad_relativa': 70.0,
                'velocidad_viento': 8.0
            }
            
            # Evaluar cada plaga
            for plaga, config in self.patrones_plagas.items():
                if cultivo in config['cultivos_afectados']:
                    probabilidad = self._calcular_probabilidad_plaga_simple(datos_actuales, config)
                    
                    if probabilidad > 0.3:  # Umbral de alerta
                        alerta = {
                            'plaga': plaga,
                            'cultivo': cultivo,
                            'probabilidad_aparicion': probabilidad,
                            'sintomas': config['sintomas'],
                            'recomendaciones': self._generar_recomendaciones_plagas_simple(plaga, probabilidad)
                        }
                        
                        alertas_plagas.append(alerta)
            
            print(f"[OK] Alertas detectadas: {len(alertas_plagas)}")
            return alertas_plagas
            
        except Exception as e:
            print(f"[ERROR] Error detectando patrones de plagas: {e}")
            return []
    
    def _calcular_probabilidad_plaga_simple(self, datos: Dict, config_plaga: Dict) -> float:
        """Calcular probabilidad de aparición de plaga (versión simplificada)"""
        try:
            condiciones = config_plaga['condiciones_favorables']
            probabilidad = 0.0
            
            # Evaluar temperatura
            if 'temp_min' in condiciones and 'temp_max' in condiciones:
                temp_actual = datos.get('temperatura_promedio', 20)
                if condiciones['temp_min'] <= temp_actual <= condiciones['temp_max']:
                    probabilidad += 0.4
                else:
                    probabilidad += 0.1
            
            # Evaluar humedad
            if 'humedad_min' in condiciones:
                humedad_actual = datos.get('humedad_relativa', 60)
                if humedad_actual >= condiciones['humedad_min']:
                    probabilidad += 0.3
                else:
                    probabilidad += 0.1
            
            if 'humedad_max' in condiciones:
                humedad_actual = datos.get('humedad_relativa', 60)
                if humedad_actual <= condiciones['humedad_max']:
                    probabilidad += 0.3
                else:
                    probabilidad += 0.1
            
            return min(1.0, probabilidad)
            
        except Exception as e:
            self.logger.error(f"Error calculando probabilidad de plaga: {e}")
            return 0.0
    
    def _generar_recomendaciones_plagas_simple(self, plaga: str, probabilidad: float) -> List[str]:
        """Generar recomendaciones específicas para plagas (versión simplificada)"""
        recomendaciones = {
            'araña_roja': [
                "Aumentar humedad ambiental con riego foliar",
                "Aplicar acaricidas preventivos",
                "Monitorear hojas inferiores"
            ],
            'pulgones': [
                "Liberar depredadores naturales (mariquitas)",
                "Aplicar jabones insecticidas",
                "Eliminar malas hierbas"
            ],
            'mosca_blanca': [
                "Colocar trampas amarillas pegajosas",
                "Aplicar insecticidas sistémicos",
                "Mantener limpieza del cultivo"
            ],
            'oidio': [
                "Mejorar ventilación del cultivo",
                "Aplicar fungicidas preventivos",
                "Evitar riego foliar"
            ]
        }
        
        base_recomendaciones = recomendaciones.get(plaga, ["Monitoreo continuo"])
        
        if probabilidad > 0.7:
            return ["URGENTE: "] + base_recomendaciones
        elif probabilidad > 0.5:
            return ["ALTA PRIORIDAD: "] + base_recomendaciones
        else:
            return ["PREVENTIVO: "] + base_recomendaciones
    
    # Métodos auxiliares
    def _obtener_mejor_modelo(self, variable: str):
        """Obtener el mejor modelo para una variable"""
        if variable not in self.modelos:
            return None
        
        modelos = self.modelos[variable]
        mejor_modelo = None
        mejor_r2 = -1
        
        for nombre, resultado in modelos.items():
            if resultado['r2'] > mejor_r2:
                mejor_r2 = resultado['r2']
                mejor_modelo = resultado['modelo']
        
        return mejor_modelo
    
    def _calcular_confianza_prediccion(self, dias_anticipacion: int) -> float:
        """Calcular confianza de predicción basada en días de anticipación"""
        return max(0.3, 1.0 - (dias_anticipacion - 1) * 0.1)
    
    def _guardar_prediccion_helada(self, prediccion: Dict):
        """Guardar predicción de helada en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            for alerta in prediccion['alertas_helada']:
                cursor.execute('''
                    INSERT INTO alertas_heladas 
                    (fecha_alerta, estacion, cultivo, probabilidad_helada, temperatura_predicha, 
                     dias_anticipacion, severidad, recomendaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prediccion['fecha'],
                    prediccion['estacion'],
                    alerta['cultivo'],
                    alerta['probabilidad_helada'],
                    prediccion['temperatura_predicha'],
                    prediccion['dias_anticipacion'],
                    alerta['severidad'],
                    json.dumps(alerta['recomendaciones'])
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando predicción de helada: {e}")
    
    def generar_reporte_rapido(self) -> Dict:
        """Generar reporte rápido del sistema"""
        try:
            reporte = {
                'fecha_generacion': datetime.now().isoformat(),
                'modelos_entrenados': len(self.modelos),
                'metricas_modelos': self.metricas_modelos,
                'sistema_optimizado': True,
                'version': 'Rápida'
            }
            
            return reporte
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}

def main():
    """Función principal para testing rápido"""
    print("="*80)
    print("MACHINE LEARNING AVANZADO OPTIMIZADO - METGO 3D QUILLOTA")
    print("="*80)
    
    # Inicializar sistema optimizado
    ml_avanzado = MLAvanzadoAgricolaOptimizado()
    
    # Entrenar modelos rápidos
    print("\n[ENTRENANDO] Modelos optimizados...")
    resultados = ml_avanzado.entrenar_modelos_rapidos('temperatura_promedio')
    
    # Predecir heladas
    print("\n[PREDICIENDO] Heladas 7 días...")
    heladas = ml_avanzado.predecir_heladas_7_dias_rapido()
    
    # Optimizar cosecha
    print("\n[OPTIMIZANDO] Fechas de cosecha...")
    cosecha = ml_avanzado.optimizar_fechas_cosecha_rapido('paltos')
    
    # Detectar plagas
    print("\n[DETECTANDO] Patrones de plagas...")
    plagas = ml_avanzado.detectar_patrones_plagas_rapido('paltos')
    
    # Generar reporte
    print("\n[GENERANDO] Reporte rápido...")
    reporte = ml_avanzado.generar_reporte_rapido()
    
    print("\n" + "="*80)
    print("MACHINE LEARNING OPTIMIZADO COMPLETADO")
    print("="*80)
    print(f"Modelos entrenados: {reporte.get('modelos_entrenados', 0)}")
    print(f"Predicciones de heladas: {len(heladas)}")
    print(f"Optimizaciones de cosecha: {1 if cosecha else 0}")
    print(f"Alertas de plagas: {len(plagas)}")
    print(f"Versión: {reporte.get('version', 'N/A')}")

if __name__ == "__main__":
    main()



