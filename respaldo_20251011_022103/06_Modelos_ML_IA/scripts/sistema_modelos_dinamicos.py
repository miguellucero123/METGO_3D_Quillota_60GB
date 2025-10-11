"""
SISTEMA DE MODELOS DINÁMICOS - METGO 3D QUILLOTA
Sistema avanzado para crear, entrenar y ejecutar nuevos modelos de ML dinámicamente
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Tuple, Optional, Any
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

class SistemaModelosDinamicos:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "modelos_dinamicos.db"
        self.modelos_dir = "modelos_dinamicos"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos_activos = {}
        self.scalers = {}
        self.metricas_modelos = {}
        self.configuraciones_modelos = {}
        
        # Catálogo de modelos disponibles
        self.catalogo_modelos = {
            'RandomForest': {
                'clase': RandomForestRegressor,
                'parametros_base': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 15, 20],
                    'min_samples_split': [5, 10, 15],
                    'random_state': 42,
                    'n_jobs': -1
                },
                'descripcion': 'Bosque aleatorio para datos complejos'
            },
            'GradientBoosting': {
                'clase': GradientBoostingRegressor,
                'parametros_base': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'max_depth': [6, 8, 10],
                    'random_state': 42
                },
                'descripcion': 'Gradient boosting para relaciones no lineales'
            },
            'SVR': {
                'clase': SVR,
                'parametros_base': {
                    'kernel': ['rbf', 'linear', 'poly'],
                    'C': [0.1, 1, 10, 100],
                    'gamma': ['scale', 'auto'],
                    'epsilon': [0.01, 0.1, 0.2]
                },
                'descripcion': 'Máquinas de soporte vectorial'
            },
            'MLP': {
                'clase': MLPRegressor,
                'parametros_base': {
                    'hidden_layer_sizes': [(50,), (100,), (100, 50), (100, 50, 25)],
                    'activation': ['relu', 'tanh'],
                    'solver': ['adam', 'lbfgs'],
                    'alpha': [0.001, 0.01, 0.1],
                    'random_state': 42,
                    'max_iter': 1000
                },
                'descripcion': 'Red neuronal multicapa'
            },
            'Ridge': {
                'clase': Ridge,
                'parametros_base': {
                    'alpha': [0.1, 1.0, 10.0, 100.0],
                    'solver': ['auto', 'svd', 'cholesky']
                },
                'descripcion': 'Regresión Ridge con regularización'
            },
            'Lasso': {
                'clase': Lasso,
                'parametros_base': {
                    'alpha': [0.01, 0.1, 1.0, 10.0],
                    'max_iter': [1000, 2000, 3000]
                },
                'descripcion': 'Regresión Lasso con selección de características'
            },
            'ElasticNet': {
                'clase': ElasticNet,
                'parametros_base': {
                    'alpha': [0.01, 0.1, 1.0],
                    'l1_ratio': [0.1, 0.5, 0.7, 0.9],
                    'max_iter': [1000, 2000]
                },
                'descripcion': 'Regresión ElasticNet combinando Ridge y Lasso'
            },
            'DecisionTree': {
                'clase': DecisionTreeRegressor,
                'parametros_base': {
                    'max_depth': [5, 10, 15, 20],
                    'min_samples_split': [5, 10, 20],
                    'min_samples_leaf': [2, 5, 10],
                    'random_state': 42
                },
                'descripcion': 'Árbol de decisión interpretable'
            },
            'ExtraTrees': {
                'clase': ExtraTreesRegressor,
                'parametros_base': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 15, 20],
                    'min_samples_split': [5, 10, 15],
                    'random_state': 42,
                    'n_jobs': -1
                },
                'descripcion': 'Árboles extra aleatorios'
            }
        }
        
        # Variables objetivo disponibles
        self.variables_objetivo = {
            'temperatura_promedio': {
                'nombre': 'Temperatura Promedio',
                'unidad': '°C',
                'descripcion': 'Temperatura promedio diaria'
            },
            'temperatura_max': {
                'nombre': 'Temperatura Máxima',
                'unidad': '°C',
                'descripcion': 'Temperatura máxima diaria'
            },
            'temperatura_min': {
                'nombre': 'Temperatura Mínima',
                'unidad': '°C',
                'descripcion': 'Temperatura mínima diaria'
            },
            'humedad_relativa': {
                'nombre': 'Humedad Relativa',
                'unidad': '%',
                'descripcion': 'Humedad relativa promedio'
            },
            'precipitacion': {
                'nombre': 'Precipitación',
                'unidad': 'mm',
                'descripcion': 'Precipitación diaria'
            },
            'velocidad_viento': {
                'nombre': 'Velocidad del Viento',
                'unidad': 'km/h',
                'descripcion': 'Velocidad promedio del viento'
            },
            'presion_atmosferica': {
                'nombre': 'Presión Atmosférica',
                'unidad': 'hPa',
                'descripcion': 'Presión atmosférica promedio'
            },
            'radiacion_solar': {
                'nombre': 'Radiación Solar',
                'unidad': 'W/m²',
                'descripcion': 'Radiación solar diaria'
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.modelos_dir, 'logs', 'data_historica', 'proyecciones']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para modelos dinámicos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de modelos creados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS modelos_creados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_modelo TEXT UNIQUE NOT NULL,
                    tipo_modelo TEXT NOT NULL,
                    variable_objetivo TEXT NOT NULL,
                    parametros TEXT NOT NULL,
                    metricas TEXT NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo',
                    descripcion TEXT
                )
            ''')
            
            # Tabla de datos históricos (3 años)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datos_historicos_3_anos (
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
                    calidad_aire REAL,
                    uv_index REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de proyecciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyecciones_modelos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo_id INTEGER NOT NULL,
                    fecha_proyeccion DATETIME NOT NULL,
                    variable TEXT NOT NULL,
                    valor_proyectado REAL NOT NULL,
                    intervalo_confianza_inferior REAL,
                    intervalo_confianza_superior REAL,
                    confianza REAL,
                    horizonte_dias INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (modelo_id) REFERENCES modelos_creados (id)
                )
            ''')
            
            # Tabla de evaluaciones de modelos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluaciones_modelos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo_id INTEGER NOT NULL,
                    fecha_evaluacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metrica TEXT NOT NULL,
                    valor REAL NOT NULL,
                    conjunto_datos TEXT NOT NULL,
                    FOREIGN KEY (modelo_id) REFERENCES modelos_creados (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Base de datos modelos dinámicos inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def generar_datos_historicos_3_anos(self) -> pd.DataFrame:
        """Generar datos históricos realistas para 3 años"""
        try:
            print("[GENERANDO] Datos históricos de 3 años...")
            np.random.seed(42)
            
            # Generar fechas para los últimos 3 años (por días)
            fecha_inicio = datetime.now() - timedelta(days=3 * 365)
            fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
            
            datos = []
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            
            for fecha in fechas:
                for estacion in estaciones:
                    # Patrones estacionales más realistas
                    mes = fecha.month
                    año = fecha.year
                    
                    # Temperatura base con variación estacional
                    temp_base = 16 + 7 * np.sin(2 * np.pi * (mes - 1) / 12)
                    
                    # Variación anual (años más cálidos/fríos)
                    variacion_anual = np.sin(2 * np.pi * (año - 2021) / 3) * 0.5
                    
                    # Variación por estación
                    variacion_estacion = {
                        'quillota_centro': 0,
                        'la_cruz': -1.5,
                        'nogueira': -2.0,
                        'colliguay': -3.0,
                        'san_isidro': 1.0,
                        'hijuelas': -1.0
                    }
                    
                    temp_base += variacion_anual + variacion_estacion.get(estacion, 0)
                    
                    # Temperaturas con variabilidad realista
                    temp_max = temp_base + np.random.normal(6, 2)
                    temp_min = temp_base - np.random.normal(6, 1.5)
                    temp_promedio = (temp_max + temp_min) / 2
                    
                    # Humedad relativa (más realista)
                    humedad_base = 75 - (temp_promedio - 15) * 1.5
                    humedad = humedad_base + np.random.normal(0, 8)
                    humedad = np.clip(humedad, 25, 95)
                    
                    # Viento con patrones estacionales
                    viento_base = 8 + 3 * np.sin(2 * np.pi * (mes - 6) / 12)  # Más viento en invierno
                    velocidad_viento = max(0, viento_base + np.random.normal(0, 4))
                    direccion_viento = np.random.uniform(0, 360)
                    
                    # Precipitación con patrones realistas de Chile central
                    prob_lluvia_base = {
                        1: 0.02, 2: 0.02, 3: 0.05, 4: 0.15, 5: 0.25, 6: 0.35,
                        7: 0.30, 8: 0.25, 9: 0.15, 10: 0.08, 11: 0.03, 12: 0.02
                    }
                    prob_lluvia = prob_lluvia_base.get(mes, 0.1)
                    
                    if np.random.random() < prob_lluvia:
                        precipitacion = np.random.exponential(3) + np.random.normal(0, 1)
                        precipitacion = max(0, precipitacion)
                    else:
                        precipitacion = 0
                    
                    # Presión atmosférica (más realista)
                    presion_base = 1013.25
                    presion = presion_base + np.random.normal(0, 8)
                    
                    # Nubosidad relacionada con precipitación y humedad
                    nubosidad_base = min(100, humedad * 0.8 + precipitacion * 5)
                    nubosidad = nubosidad_base + np.random.normal(0, 15)
                    nubosidad = np.clip(nubosidad, 0, 100)
                    
                    # Radiación solar (inversamente relacionada con nubosidad)
                    radiacion_base = 800 - nubosidad * 3
                    radiacion = radiacion_base + np.random.normal(0, 80)
                    radiacion = max(0, radiacion)
                    
                    # Punto de rocío
                    punto_rocio = temp_promedio - (100 - humedad) / 5
                    
                    # Índices térmicos
                    indice_calor = temp_promedio + (humedad - 50) * 0.08
                    indice_frio = temp_promedio - np.sqrt(velocidad_viento) * 0.7
                    
                    # Nuevas variables
                    calidad_aire = 50 + np.random.normal(0, 15)  # Simulado
                    calidad_aire = np.clip(calidad_aire, 0, 100)
                    
                    uv_index = 8 - nubosidad / 15 + np.random.normal(0, 1)
                    uv_index = max(0, min(11, uv_index))
                    
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
                        'indice_frio': round(indice_frio, 1),
                        'calidad_aire': round(calidad_aire, 1),
                        'uv_index': round(uv_index, 1)
                    })
            
            df = pd.DataFrame(datos)
            
            # Guardar en base de datos
            self._guardar_datos_historicos_3_anos(df)
            
            print(f"[OK] Datos históricos de 3 años generados: {len(df)} registros")
            return df
            
        except Exception as e:
            print(f"[ERROR] Error generando datos históricos de 3 años: {e}")
            return pd.DataFrame()
    
    def _guardar_datos_historicos_3_anos(self, df: pd.DataFrame):
        """Guardar datos históricos de 3 años en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            
            df.to_sql('datos_historicos_3_anos', conn, if_exists='replace', index=False)
            
            conn.commit()
            conn.close()
            
            print("[OK] Datos históricos de 3 años guardados")
            
        except Exception as e:
            print(f"[ERROR] Error guardando datos históricos de 3 años: {e}")
    
    def crear_nuevo_modelo(self, nombre_modelo: str, tipo_modelo: str, 
                          variable_objetivo: str, parametros_personalizados: Dict = None,
                          descripcion: str = "") -> Dict:
        """Crear y entrenar un nuevo modelo dinámicamente"""
        try:
            print(f"[CREANDO] Nuevo modelo: {nombre_modelo}")
            
            # Validar parámetros
            if tipo_modelo not in self.catalogo_modelos:
                raise ValueError(f"Tipo de modelo '{tipo_modelo}' no disponible")
            
            if variable_objetivo not in self.variables_objetivo:
                raise ValueError(f"Variable objetivo '{variable_objetivo}' no disponible")
            
            # Cargar datos históricos
            df = self._cargar_datos_historicos_3_anos()
            
            if df.empty:
                print("[GENERANDO] Datos históricos de 3 años...")
                df = self.generar_datos_historicos_3_anos()
            
            # Preparar datos
            X, y = self._preparar_datos_entrenamiento_avanzado(df, variable_objetivo)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No hay datos válidos para entrenar")
            
            # Configurar parámetros del modelo
            config_modelo = self.catalogo_modelos[tipo_modelo].copy()
            parametros = {}
            
            # Usar parámetros personalizados si se proporcionaron
            if parametros_personalizados:
                parametros = parametros_personalizados.copy()
            else:
                # Usar parámetros base con valores por defecto (primer elemento de listas)
                for param, valor in config_modelo['parametros_base'].items():
                    if isinstance(valor, list):
                        parametros[param] = valor[0]  # Usar primer valor de la lista
                    else:
                        parametros[param] = valor
            
            # Agregar parámetros fijos (solo si el modelo los acepta)
            if tipo_modelo not in ['SVR']:  # SVR no acepta random_state
                parametros['random_state'] = 42
            if 'n_jobs' in config_modelo['parametros_base']:
                parametros['n_jobs'] = -1
            
            # Crear y entrenar modelo
            modelo_clase = config_modelo['clase']
            modelo = modelo_clase(**parametros)
            
            print(f"[ENTRENANDO] {tipo_modelo} para {variable_objetivo}...")
            modelo.fit(X, y)
            
            # Evaluar modelo
            metricas = self._evaluar_modelo_completo(modelo, X, y, variable_objetivo)
            
            # Guardar modelo
            modelo_id = self._guardar_modelo_en_bd(
                nombre_modelo, tipo_modelo, variable_objetivo, 
                parametros, metricas, descripcion
            )
            
            # Guardar modelo en disco
            ruta_modelo = os.path.join(self.modelos_dir, f"{nombre_modelo}.joblib")
            joblib.dump(modelo, ruta_modelo)
            
            # Guardar scaler
            if variable_objetivo in self.scalers:
                ruta_scaler = os.path.join(self.modelos_dir, f"{nombre_modelo}_scaler.joblib")
                joblib.dump(self.scalers[variable_objetivo], ruta_scaler)
            
            # Actualizar modelos activos
            self.modelos_activos[nombre_modelo] = {
                'modelo': modelo,
                'tipo': tipo_modelo,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas,
                'modelo_id': modelo_id,
                'fecha_creacion': datetime.now()
            }
            
            print(f"[OK] Modelo '{nombre_modelo}' creado exitosamente")
            print(f"    R² = {metricas['r2']:.4f}")
            print(f"    RMSE = {metricas['rmse']:.4f}")
            
            return {
                'modelo_id': modelo_id,
                'nombre_modelo': nombre_modelo,
                'tipo_modelo': tipo_modelo,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas,
                'estado': 'creado_exitosamente'
            }
            
        except Exception as e:
            print(f"[ERROR] Error creando modelo: {e}")
            return {'error': str(e)}
    
    def _preparar_datos_entrenamiento_avanzado(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento con características avanzadas"""
        try:
            # Crear características temporales avanzadas
            df['año'] = df['fecha'].dt.year
            df['mes'] = df['fecha'].dt.month
            df['dia'] = df['fecha'].dt.day
            df['dia_semana'] = df['fecha'].dt.dayofweek
            df['dia_año'] = df['fecha'].dt.dayofyear
            df['trimestre'] = df['fecha'].dt.quarter
            
            # Características cíclicas
            df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
            df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
            df['dia_año_sin'] = np.sin(2 * np.pi * df['dia_año'] / 365)
            df['dia_año_cos'] = np.cos(2 * np.pi * df['dia_año'] / 365)
            
            # Características de tendencia
            df['año_normalizado'] = (df['año'] - df['año'].min()) / (df['año'].max() - df['año'].min())
            
            # Características derivadas
            df['amplitud_termica'] = df['temperatura_max'] - df['temperatura_min']
            df['presion_normalizada'] = (df['presion_atmosferica'] - 1000) / 50
            
            # Codificar estación
            if 'estacion' in df.columns:
                estacion_encoded = pd.get_dummies(df['estacion'], prefix='estacion')
                df = pd.concat([df, estacion_encoded], axis=1)
            
            # Seleccionar características
            caracteristicas_base = [
                'temperatura_max', 'temperatura_min', 'humedad_relativa',
                'velocidad_viento', 'direccion_viento', 'precipitacion',
                'presion_atmosferica', 'nubosidad', 'radiacion_solar',
                'punto_rocio', 'indice_calor', 'indice_frio',
                'calidad_aire', 'uv_index',
                'año', 'mes', 'dia', 'dia_semana', 'dia_año', 'trimestre',
                'mes_sin', 'mes_cos', 'dia_año_sin', 'dia_año_cos',
                'año_normalizado', 'amplitud_termica', 'presion_normalizada'
            ]
            
            # Agregar columnas de estación
            caracteristicas_estacion = [col for col in df.columns if col.startswith('estacion_')]
            caracteristicas = [col for col in caracteristicas_base if col in df.columns] + caracteristicas_estacion
            
            if not caracteristicas:
                raise ValueError("No se encontraron características válidas")
            
            X = df[caracteristicas].fillna(df[caracteristicas].mean())
            y = df[variable_objetivo].fillna(df[variable_objetivo].mean())
            
            # Escalar características
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers[variable_objetivo] = scaler
            
            return X_scaled, y.values
            
        except Exception as e:
            self.logger.error(f"Error preparando datos de entrenamiento avanzado: {e}")
            return np.array([]), np.array([])
    
    def _evaluar_modelo_completo(self, modelo, X: np.ndarray, y: np.ndarray, 
                                variable_objetivo: str) -> Dict:
        """Evaluar modelo con múltiples métricas"""
        try:
            # Validación cruzada temporal
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Métricas de validación cruzada
            scores_r2 = cross_val_score(modelo, X, y, cv=tscv, scoring='r2')
            scores_rmse = cross_val_score(modelo, X, y, cv=tscv, scoring='neg_mean_squared_error')
            scores_mae = cross_val_score(modelo, X, y, cv=tscv, scoring='neg_mean_absolute_error')
            
            # Métricas en conjunto completo
            y_pred = modelo.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mae = mean_absolute_error(y, y_pred)
            
            # Métricas adicionales
            mape = np.mean(np.abs((y - y_pred) / y)) * 100  # MAPE
            
            return {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'cv_r2_mean': scores_r2.mean(),
                'cv_r2_std': scores_r2.std(),
                'cv_rmse_mean': np.sqrt(-scores_rmse.mean()),
                'cv_rmse_std': np.sqrt(scores_rmse).std(),
                'cv_mae_mean': -scores_mae.mean(),
                'cv_mae_std': scores_mae.std(),
                'variable_objetivo': variable_objetivo,
                'fecha_evaluacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando modelo: {e}")
            return {}
    
    def generar_proyecciones(self, nombre_modelo: str, horizonte_dias: int = 30,
                           incluir_intervalos: bool = True) -> List[Dict]:
        """Generar proyecciones usando un modelo específico"""
        try:
            print(f"[PROYECTANDO] Usando modelo '{nombre_modelo}' para {horizonte_dias} días...")
            
            if nombre_modelo not in self.modelos_activos:
                raise ValueError(f"Modelo '{nombre_modelo}' no está activo")
            
            modelo_info = self.modelos_activos[nombre_modelo]
            modelo = modelo_info['modelo']
            variable_objetivo = modelo_info['variable_objetivo']
            
            # Generar proyecciones
            proyecciones = []
            fecha_actual = datetime.now()
            
            for i in range(horizonte_dias):
                fecha_proyeccion = fecha_actual + timedelta(days=i)
                
                # Preparar características para predicción
                X_pred = self._preparar_caracteristicas_proyeccion(
                    fecha_proyeccion, variable_objetivo
                )
                
                # Realizar predicción
                valor_proyectado = modelo.predict(X_pred.reshape(1, -1))[0]
                
                # Calcular intervalos de confianza (simplificado)
                if incluir_intervalos:
                    # Usar métricas del modelo para estimar incertidumbre
                    rmse = modelo_info['metricas']['rmse']
                    intervalo = rmse * 1.96  # 95% de confianza
                    confianza = max(0.1, 1.0 - (i / horizonte_dias) * 0.5)
                    
                    intervalo_inf = valor_proyectado - intervalo * confianza
                    intervalo_sup = valor_proyectado + intervalo * confianza
                else:
                    intervalo_inf = intervalo_sup = None
                    confianza = 1.0
                
                proyeccion = {
                    'fecha': fecha_proyeccion.strftime('%Y-%m-%d'),
                    'dias_futuro': i + 1,
                    'variable': variable_objetivo,
                    'valor_proyectado': round(valor_proyectado, 2),
                    'intervalo_confianza_inferior': round(intervalo_inf, 2) if intervalo_inf else None,
                    'intervalo_confianza_superior': round(intervalo_sup, 2) if intervalo_sup else None,
                    'confianza': round(confianza, 3),
                    'modelo_usado': nombre_modelo
                }
                
                proyecciones.append(proyeccion)
                
                # Guardar proyección en base de datos
                self._guardar_proyeccion_en_bd(
                    modelo_info['modelo_id'], proyeccion
                )
            
            print(f"[OK] {len(proyecciones)} proyecciones generadas")
            return proyecciones
            
        except Exception as e:
            print(f"[ERROR] Error generando proyecciones: {e}")
            return []
    
    def _preparar_caracteristicas_proyeccion(self, fecha: datetime, variable_objetivo: str) -> np.ndarray:
        """Preparar características para proyección futura"""
        try:
            # Características temporales
            año = fecha.year
            mes = fecha.month
            dia = fecha.day
            dia_semana = fecha.weekday()
            dia_año = fecha.timetuple().tm_yday
            trimestre = (mes - 1) // 3 + 1
            
            # Características cíclicas
            mes_sin = np.sin(2 * np.pi * mes / 12)
            mes_cos = np.cos(2 * np.pi * mes / 12)
            dia_año_sin = np.sin(2 * np.pi * dia_año / 365)
            dia_año_cos = np.cos(2 * np.pi * dia_año / 365)
            
            # Características de tendencia
            año_normalizado = (año - 2021) / 3  # Normalizar para 3 años
            
            # Simular características meteorológicas (en producción vendrían de modelos de pronóstico)
            temp_max = 20 + 5 * np.sin(2 * np.pi * mes / 12) + np.random.normal(0, 2)
            temp_min = 15 + 5 * np.sin(2 * np.pi * mes / 12) + np.random.normal(0, 1.5)
            humedad = 70 - (temp_max - 15) * 1.5 + np.random.normal(0, 5)
            viento = 10 + np.random.normal(0, 3)
            precipitacion = 0 if np.random.random() > 0.1 else np.random.exponential(2)
            presion = 1013 + np.random.normal(0, 5)
            nubosidad = min(100, humedad * 0.8 + precipitacion * 5)
            radiacion = max(0, 800 - nubosidad * 3)
            
            # Características derivadas
            amplitud_termica = temp_max - temp_min
            presion_normalizada = (presion - 1000) / 50
            punto_rocio = (temp_max + temp_min) / 2 - (100 - humedad) / 5
            indice_calor = (temp_max + temp_min) / 2 + (humedad - 50) * 0.08
            indice_frio = (temp_max + temp_min) / 2 - np.sqrt(viento) * 0.7
            calidad_aire = 50 + np.random.normal(0, 10)
            uv_index = 8 - nubosidad / 15 + np.random.normal(0, 1)
            
            # Características básicas
            caracteristicas = [
                temp_max, temp_min, humedad, viento, 0, precipitacion,  # direccion_viento = 0
                presion, nubosidad, radiacion, punto_rocio, indice_calor, indice_frio,
                calidad_aire, uv_index,
                año, mes, dia, dia_semana, dia_año, trimestre,
                mes_sin, mes_cos, dia_año_sin, dia_año_cos,
                año_normalizado, amplitud_termica, presion_normalizada
            ]
            
            # Agregar codificación de estación (usar quillota_centro por defecto)
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            for est in estaciones:
                caracteristicas.append(1 if est == 'quillota_centro' else 0)
            
            return np.array(caracteristicas)
            
        except Exception as e:
            self.logger.error(f"Error preparando características de proyección: {e}")
            return np.array([])
    
    def listar_modelos_activos(self) -> List[Dict]:
        """Listar todos los modelos activos"""
        try:
            modelos = []
            for nombre, info in self.modelos_activos.items():
                modelos.append({
                    'nombre': nombre,
                    'tipo': info['tipo'],
                    'variable_objetivo': info['variable_objetivo'],
                    'r2': info['metricas']['r2'],
                    'rmse': info['metricas']['rmse'],
                    'fecha_creacion': info['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S'),
                    'modelo_id': info['modelo_id']
                })
            return modelos
        except Exception as e:
            self.logger.error(f"Error listando modelos: {e}")
            return []
    
    def obtener_catalogo_modelos(self) -> Dict:
        """Obtener catálogo completo de modelos disponibles"""
        return self.catalogo_modelos
    
    def obtener_variables_objetivo(self) -> Dict:
        """Obtener variables objetivo disponibles"""
        return self.variables_objetivo
    
    # Métodos auxiliares de base de datos
    def _cargar_datos_historicos_3_anos(self) -> pd.DataFrame:
        """Cargar datos históricos de 3 años"""
        try:
            conn = sqlite3.connect(self.base_datos)
            df = pd.read_sql_query(
                "SELECT * FROM datos_historicos_3_anos ORDER BY fecha",
                conn,
                parse_dates=['fecha']
            )
            conn.close()
            return df
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos de 3 años: {e}")
            return pd.DataFrame()
    
    def _guardar_modelo_en_bd(self, nombre: str, tipo: str, variable: str, 
                             parametros: Dict, metricas: Dict, descripcion: str) -> int:
        """Guardar modelo en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO modelos_creados 
                (nombre_modelo, tipo_modelo, variable_objetivo, parametros, metricas, descripcion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                nombre, tipo, variable, 
                json.dumps(parametros), 
                json.dumps(metricas), 
                descripcion
            ))
            
            modelo_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return modelo_id
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo en BD: {e}")
            return 0
    
    def _guardar_proyeccion_en_bd(self, modelo_id: int, proyeccion: Dict):
        """Guardar proyección en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO proyecciones_modelos 
                (modelo_id, fecha_proyeccion, variable, valor_proyectado, 
                 intervalo_confianza_inferior, intervalo_confianza_superior, 
                 confianza, horizonte_dias)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                modelo_id,
                proyeccion['fecha'],
                proyeccion['variable'],
                proyeccion['valor_proyectado'],
                proyeccion['intervalo_confianza_inferior'],
                proyeccion['intervalo_confianza_superior'],
                proyeccion['confianza'],
                proyeccion['dias_futuro']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando proyección: {e}")

def main():
    """Función principal para demostración"""
    print("="*80)
    print("SISTEMA DE MODELOS DINÁMICOS - METGO 3D QUILLOTA")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaModelosDinamicos()
    
    # Generar datos históricos de 3 años
    print("\n[1] GENERANDO DATOS HISTÓRICOS DE 3 AÑOS...")
    df = sistema.generar_datos_historicos_3_anos()
    
    # Crear modelos dinámicos
    print("\n[2] CREANDO MODELOS DINÁMICOS...")
    
    # Modelo 1: RandomForest para temperatura promedio
    resultado1 = sistema.crear_nuevo_modelo(
        nombre_modelo="RF_Temp_Promedio",
        tipo_modelo="RandomForest",
        variable_objetivo="temperatura_promedio",
        parametros_personalizados={'n_estimators': 100, 'max_depth': 15, 'min_samples_split': 10},
        descripcion="RandomForest optimizado para temperatura promedio"
    )
    
    # Modelo 2: GradientBoosting para precipitación
    resultado2 = sistema.crear_nuevo_modelo(
        nombre_modelo="GB_Precipitacion",
        tipo_modelo="GradientBoosting",
        variable_objetivo="precipitacion",
        parametros_personalizados={'n_estimators': 150, 'learning_rate': 0.1, 'max_depth': 8},
        descripcion="GradientBoosting para predicción de precipitación"
    )
    
    # Modelo 3: SVR para humedad relativa
    resultado3 = sistema.crear_nuevo_modelo(
        nombre_modelo="SVR_Humedad",
        tipo_modelo="SVR",
        variable_objetivo="humedad_relativa",
        parametros_personalizados={'C': 10, 'kernel': 'rbf', 'epsilon': 0.1},
        descripcion="SVR para humedad relativa"
    )
    
    # Generar proyecciones
    print("\n[3] GENERANDO PROYECCIONES...")
    
    proyecciones_temp = sistema.generar_proyecciones("RF_Temp_Promedio", 30)
    proyecciones_precip = sistema.generar_proyecciones("GB_Precipitacion", 15)
    proyecciones_humedad = sistema.generar_proyecciones("SVR_Humedad", 20)
    
    # Listar modelos activos
    print("\n[4] MODELOS ACTIVOS:")
    modelos_activos = sistema.listar_modelos_activos()
    for modelo in modelos_activos:
        print(f"    - {modelo['nombre']}: {modelo['tipo']} (R²={modelo['r2']:.4f})")
    
    print("\n" + "="*80)
    print("SISTEMA DE MODELOS DINÁMICOS COMPLETADO")
    print("="*80)
    print(f"Modelos creados: {len(modelos_activos)}")
    print(f"Proyecciones temperatura: {len(proyecciones_temp)}")
    print(f"Proyecciones precipitación: {len(proyecciones_precip)}")
    print(f"Proyecciones humedad: {len(proyecciones_humedad)}")
    print("="*80)

if __name__ == "__main__":
    main()
