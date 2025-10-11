"""
SISTEMA DE MODELOS HÍBRIDOS INNOVADORES - METGO 3D QUILLOTA
Sistema avanzado que combina múltiples algoritmos para máxima exactitud y rapidez
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor, StackingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler, PolynomialFeatures
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.decomposition import PCA
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
from scipy import stats
from scipy.optimize import minimize
import concurrent.futures
from functools import partial

warnings.filterwarnings('ignore')

class SistemaModelosHibridosInnovadores:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "modelos_hibridos_innovadores.db"
        self.modelos_dir = "modelos_hibridos_innovadores"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos_hibridos = {}
        self.ensembles = {}
        self.metricas_modelos = {}
        self.pesos_optimizados = {}
        
        # Configuración de modelos base optimizados
        self.modelos_base_optimizados = {
            'RandomForest_Ultra': {
                'clase': RandomForestRegressor,
                'parametros': {
                    'n_estimators': 300,
                    'max_depth': 25,
                    'min_samples_split': 3,
                    'min_samples_leaf': 1,
                    'max_features': 'sqrt',
                    'bootstrap': True,
                    'random_state': 42,
                    'n_jobs': -1
                },
                'peso_inicial': 0.25
            },
            'GradientBoosting_Ultra': {
                'clase': GradientBoostingRegressor,
                'parametros': {
                    'n_estimators': 500,
                    'learning_rate': 0.03,
                    'max_depth': 12,
                    'min_samples_split': 3,
                    'min_samples_leaf': 1,
                    'subsample': 0.8,
                    'random_state': 42
                },
                'peso_inicial': 0.25
            },
            'ExtraTrees_Ultra': {
                'clase': ExtraTreesRegressor,
                'parametros': {
                    'n_estimators': 400,
                    'max_depth': 30,
                    'min_samples_split': 2,
                    'min_samples_leaf': 1,
                    'max_features': 'log2',
                    'bootstrap': True,
                    'random_state': 42,
                    'n_jobs': -1
                },
                'peso_inicial': 0.25
            },
            'SVR_Ultra': {
                'clase': SVR,
                'parametros': {
                    'kernel': 'rbf',
                    'C': 1000,
                    'gamma': 'scale',
                    'epsilon': 0.01
                },
                'peso_inicial': 0.15
            },
            'MLP_Ultra': {
                'clase': MLPRegressor,
                'parametros': {
                    'hidden_layer_sizes': (200, 100, 50),
                    'activation': 'relu',
                    'solver': 'adam',
                    'alpha': 0.0001,
                    'learning_rate': 'adaptive',
                    'max_iter': 2000,
                    'early_stopping': True,
                    'validation_fraction': 0.1,
                    'random_state': 42
                },
                'peso_inicial': 0.10
            }
        }
        
        # Técnicas de optimización avanzadas
        self.tecnicas_optimizacion = {
            'feature_selection': {
                'SelectKBest': SelectKBest(score_func=f_regression),
                'RFE': RFE(RandomForestRegressor(n_estimators=50, random_state=42)),
                'PCA': PCA(n_components=0.95)
            },
            'preprocessing': {
                'RobustScaler': RobustScaler(),
                'StandardScaler': StandardScaler(),
                'PolynomialFeatures': PolynomialFeatures(degree=2, include_bias=False)
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.modelos_dir, 'logs', 'ensembles', 'optimizaciones']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para modelos híbridos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de modelos híbridos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS modelos_hibridos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_modelo TEXT UNIQUE NOT NULL,
                    tipo_hibrido TEXT NOT NULL,
                    variable_objetivo TEXT NOT NULL,
                    modelos_base TEXT NOT NULL,
                    pesos_optimizados TEXT NOT NULL,
                    metricas TEXT NOT NULL,
                    tiempo_entrenamiento REAL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo',
                    descripcion TEXT
                )
            ''')
            
            # Tabla de optimizaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimizaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo_id INTEGER NOT NULL,
                    tecnica_optimizacion TEXT NOT NULL,
                    parametros TEXT NOT NULL,
                    mejora_metricas TEXT NOT NULL,
                    fecha_optimizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (modelo_id) REFERENCES modelos_hibridos (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Base de datos modelos híbridos inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def crear_modelo_hibrido_innovador(self, nombre_modelo: str, variable_objetivo: str,
                                     tipo_hibrido: str = 'ensemble_optimizado',
                                     descripcion: str = "") -> Dict:
        """Crear modelo híbrido innovador con máxima exactitud y rapidez"""
        try:
            print(f"[CREANDO] Modelo híbrido innovador: {nombre_modelo}")
            inicio_tiempo = datetime.now()
            
            # Cargar datos
            df = self._cargar_datos_historicos()
            if df.empty:
                raise ValueError("No hay datos históricos disponibles")
            
            # Preparar datos con optimizaciones
            X, y, preprocessor = self._preparar_datos_ultra_optimizados(df, variable_objetivo)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No hay datos válidos para entrenar")
            
            print(f"[DATOS] {len(X)} muestras, {X.shape[1]} características")
            
            # Crear modelo híbrido según tipo
            if tipo_hibrido == 'ensemble_optimizado':
                modelo_hibrido, metricas = self._crear_ensemble_optimizado(X, y, variable_objetivo)
            elif tipo_hibrido == 'stacking_avanzado':
                modelo_hibrido, metricas = self._crear_stacking_avanzado(X, y, variable_objetivo)
            elif tipo_hibrido == 'voting_inteligente':
                modelo_hibrido, metricas = self._crear_voting_inteligente(X, y, variable_objetivo)
            elif tipo_hibrido == 'hibrido_adaptativo':
                modelo_hibrido, metricas = self._crear_hibrido_adaptativo(X, y, variable_objetivo)
            else:
                raise ValueError(f"Tipo de híbrido '{tipo_hibrido}' no soportado")
            
            # Optimizar pesos del ensemble
            pesos_optimizados = self._optimizar_pesos_ensemble(modelo_hibrido, X, y)
            
            # Evaluación final
            metricas_finales = self._evaluar_modelo_hibrido(modelo_hibrido, X, y, variable_objetivo)
            
            tiempo_entrenamiento = (datetime.now() - inicio_tiempo).total_seconds()
            metricas_finales['tiempo_entrenamiento'] = tiempo_entrenamiento
            
            # Guardar modelo
            modelo_id = self._guardar_modelo_hibrido_en_bd(
                nombre_modelo, tipo_hibrido, variable_objetivo,
                list(self.modelos_base_optimizados.keys()),
                pesos_optimizados, metricas_finales, descripcion
            )
            
            # Guardar modelo en disco
            ruta_modelo = os.path.join(self.modelos_dir, f"{nombre_modelo}.joblib")
            joblib.dump({
                'modelo': modelo_hibrido,
                'preprocessor': preprocessor,
                'pesos': pesos_optimizados,
                'metricas': metricas_finales,
                'tipo_hibrido': tipo_hibrido
            }, ruta_modelo)
            
            # Actualizar modelos híbridos activos
            self.modelos_hibridos[nombre_modelo] = {
                'modelo': modelo_hibrido,
                'preprocessor': preprocessor,
                'tipo_hibrido': tipo_hibrido,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas_finales,
                'pesos': pesos_optimizados,
                'modelo_id': modelo_id,
                'fecha_creacion': datetime.now()
            }
            
            print(f"[OK] Modelo híbrido '{nombre_modelo}' creado exitosamente")
            print(f"    R² = {metricas_finales['r2']:.6f}")
            print(f"    RMSE = {metricas_finales['rmse']:.6f}")
            print(f"    Tiempo = {tiempo_entrenamiento:.2f}s")
            
            return {
                'modelo_id': modelo_id,
                'nombre_modelo': nombre_modelo,
                'tipo_hibrido': tipo_hibrido,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas_finales,
                'pesos_optimizados': pesos_optimizados,
                'tiempo_entrenamiento': tiempo_entrenamiento,
                'estado': 'creado_exitosamente'
            }
            
        except Exception as e:
            print(f"[ERROR] Error creando modelo híbrido: {e}")
            return {'error': str(e)}
    
    def _preparar_datos_ultra_optimizados(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray, Any]:
        """Preparar datos con técnicas de optimización avanzadas"""
        try:
            # Crear características avanzadas
            df = self._crear_caracteristicas_avanzadas(df)
            
            # Seleccionar características
            caracteristicas = self._seleccionar_caracteristicas_optimizadas(df, variable_objetivo)
            
            if not caracteristicas:
                raise ValueError("No se encontraron características válidas")
            
            X = df[caracteristicas].fillna(df[caracteristicas].mean())
            y = df[variable_objetivo].fillna(df[variable_objetivo].mean())
            
            # Aplicar preprocesamiento avanzado
            preprocessor = self._crear_preprocessor_avanzado()
            X_processed = preprocessor.fit_transform(X)
            
            return X_processed, y.values, preprocessor
            
        except Exception as e:
            self.logger.error(f"Error preparando datos ultra optimizados: {e}")
            return np.array([]), np.array([]), None
    
    def _crear_caracteristicas_avanzadas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear características avanzadas para mejorar la precisión"""
        try:
            # Características temporales avanzadas
            df['año'] = df['fecha'].dt.year
            df['mes'] = df['fecha'].dt.month
            df['dia'] = df['fecha'].dt.day
            df['dia_semana'] = df['fecha'].dt.dayofweek
            df['dia_año'] = df['fecha'].dt.dayofyear
            df['trimestre'] = df['fecha'].dt.quarter
            df['semana_año'] = df['fecha'].dt.isocalendar().week
            
            # Características cíclicas múltiples
            for periodo in [12, 24, 365, 52]:
                if periodo == 12:  # Mensual
                    df[f'mes_sin_{periodo}'] = np.sin(2 * np.pi * df['mes'] / periodo)
                    df[f'mes_cos_{periodo}'] = np.cos(2 * np.pi * df['mes'] / periodo)
                elif periodo == 365:  # Anual
                    df[f'dia_sin_{periodo}'] = np.sin(2 * np.pi * df['dia_año'] / periodo)
                    df[f'dia_cos_{periodo}'] = np.cos(2 * np.pi * df['dia_año'] / periodo)
                elif periodo == 52:  # Semanal
                    df[f'semana_sin_{periodo}'] = np.sin(2 * np.pi * df['semana_año'] / periodo)
                    df[f'semana_cos_{periodo}'] = np.cos(2 * np.pi * df['semana_año'] / periodo)
            
            # Características derivadas avanzadas
            df['amplitud_termica'] = df['temperatura_max'] - df['temperatura_min']
            df['presion_normalizada'] = (df['presion_atmosferica'] - 1000) / 50
            df['humedad_normalizada'] = (df['humedad_relativa'] - 50) / 50
            df['viento_normalizado'] = df['velocidad_viento'] / 20
            
            # Características de interacción
            df['temp_humedad_interaccion'] = df['temperatura_promedio'] * df['humedad_relativa']
            df['presion_viento_interaccion'] = df['presion_atmosferica'] * df['velocidad_viento']
            df['radiacion_nubosidad_interaccion'] = df['radiacion_solar'] * (100 - df['nubosidad'])
            
            # Características estadísticas por ventana
            for ventana in [7, 14, 30]:
                for variable in ['temperatura_promedio', 'humedad_relativa', 'presion_atmosferica']:
                    if variable in df.columns:
                        df[f'{variable}_media_{ventana}d'] = df[variable].rolling(window=ventana, min_periods=1).mean()
                        df[f'{variable}_std_{ventana}d'] = df[variable].rolling(window=ventana, min_periods=1).std()
                        df[f'{variable}_min_{ventana}d'] = df[variable].rolling(window=ventana, min_periods=1).min()
                        df[f'{variable}_max_{ventana}d'] = df[variable].rolling(window=ventana, min_periods=1).max()
            
            # Características de tendencia
            for variable in ['temperatura_promedio', 'humedad_relativa', 'precipitacion']:
                if variable in df.columns:
                    df[f'{variable}_tendencia_7d'] = df[variable].diff(7)
                    df[f'{variable}_tendencia_14d'] = df[variable].diff(14)
            
            # Codificar estación
            if 'estacion' in df.columns:
                estacion_encoded = pd.get_dummies(df['estacion'], prefix='estacion')
                df = pd.concat([df, estacion_encoded], axis=1)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error creando características avanzadas: {e}")
            return df
    
    def _seleccionar_caracteristicas_optimizadas(self, df: pd.DataFrame, variable_objetivo: str) -> List[str]:
        """Seleccionar las mejores características usando múltiples técnicas"""
        try:
            # Características base
            caracteristicas_base = [
                'temperatura_max', 'temperatura_min', 'temperatura_promedio',
                'humedad_relativa', 'velocidad_viento', 'direccion_viento',
                'precipitacion', 'presion_atmosferica', 'nubosidad',
                'radiacion_solar', 'punto_rocio', 'indice_calor', 'indice_frio',
                'año', 'mes', 'dia', 'dia_semana', 'dia_año', 'trimestre'
            ]
            
            # Características derivadas
            caracteristicas_derivadas = [
                'amplitud_termica', 'presion_normalizada', 'humedad_normalizada',
                'viento_normalizado', 'temp_humedad_interaccion',
                'presion_viento_interaccion', 'radiacion_nubosidad_interaccion'
            ]
            
            # Características cíclicas
            caracteristicas_ciclicas = [col for col in df.columns if '_sin_' in col or '_cos_' in col]
            
            # Características de ventana
            caracteristicas_ventana = [col for col in df.columns if any(suffix in col for suffix in ['_media_', '_std_', '_min_', '_max_', '_tendencia_'])]
            
            # Características de estación
            caracteristicas_estacion = [col for col in df.columns if col.startswith('estacion_')]
            
            # Combinar todas las características
            todas_caracteristicas = (caracteristicas_base + caracteristicas_derivadas + 
                                   caracteristicas_ciclicas + caracteristicas_ventana + 
                                   caracteristicas_estacion)
            
            # Filtrar características que existen en el DataFrame
            caracteristicas_validas = [col for col in todas_caracteristicas if col in df.columns]
            
            # Selección automática de características
            X_temp = df[caracteristicas_validas].fillna(df[caracteristicas_validas].mean())
            y_temp = df[variable_objetivo].fillna(df[variable_objetivo].mean())
            
            # Usar SelectKBest para seleccionar las mejores características
            selector = SelectKBest(score_func=f_regression, k=min(50, len(caracteristicas_validas)))
            X_selected = selector.fit_transform(X_temp, y_temp)
            
            # Obtener nombres de características seleccionadas
            caracteristicas_seleccionadas = [caracteristicas_validas[i] for i in selector.get_support(indices=True)]
            
            print(f"[CARACTERISTICAS] Seleccionadas: {len(caracteristicas_seleccionadas)} de {len(caracteristicas_validas)}")
            
            return caracteristicas_seleccionadas
            
        except Exception as e:
            self.logger.error(f"Error seleccionando características: {e}")
            return []
    
    def _crear_preprocessor_avanzado(self):
        """Crear preprocessor avanzado con múltiples técnicas"""
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        
        # Crear pipeline de preprocesamiento
        preprocessor = Pipeline([
            ('scaler', RobustScaler()),
            ('poly_features', PolynomialFeatures(degree=2, include_bias=False, interaction_only=True))
        ])
        
        return preprocessor
    
    def _crear_ensemble_optimizado(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear ensemble optimizado con modelos base de alto rendimiento"""
        try:
            print("[CREANDO] Ensemble optimizado...")
            
            # Crear modelos base optimizados
            modelos_base = {}
            for nombre, config in self.modelos_base_optimizados.items():
                modelo = config['clase'](**config['parametros'])
                modelos_base[nombre] = modelo
            
            # Crear VotingRegressor con pesos optimizados
            ensemble = VotingRegressor(
                estimators=list(modelos_base.items()),
                weights=list(config['peso_inicial'] for config in self.modelos_base_optimizados.values())
            )
            
            # Entrenar ensemble
            ensemble.fit(X, y)
            
            # Evaluación rápida
            y_pred = ensemble.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            metricas = {
                'r2': r2,
                'rmse': rmse,
                'tipo': 'ensemble_optimizado',
                'modelos_base': len(modelos_base)
            }
            
            return ensemble, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando ensemble optimizado: {e}")
            return None, {}
    
    def _crear_stacking_avanzado(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear stacking avanzado con meta-aprendizaje"""
        try:
            print("[CREANDO] Stacking avanzado...")
            
            # Crear modelos base
            modelos_base = []
            for nombre, config in self.modelos_base_optimizados.items():
                modelo = config['clase'](**config['parametros'])
                modelos_base.append((nombre, modelo))
            
            # Meta-aprendizaje con Ridge optimizado
            meta_learner = Ridge(alpha=0.1, solver='auto')
            
            # Crear StackingRegressor
            stacking = StackingRegressor(
                estimators=modelos_base,
                final_estimator=meta_learner,
                cv=TimeSeriesSplit(n_splits=3),
                n_jobs=-1
            )
            
            # Entrenar stacking
            stacking.fit(X, y)
            
            # Evaluación
            y_pred = stacking.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            metricas = {
                'r2': r2,
                'rmse': rmse,
                'tipo': 'stacking_avanzado',
                'modelos_base': len(modelos_base)
            }
            
            return stacking, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando stacking avanzado: {e}")
            return None, {}
    
    def _crear_voting_inteligente(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear voting inteligente con pesos adaptativos"""
        try:
            print("[CREANDO] Voting inteligente...")
            
            # Crear modelos base
            modelos_base = []
            for nombre, config in self.modelos_base_optimizados.items():
                modelo = config['clase'](**config['parametros'])
                modelos_base.append((nombre, modelo))
            
            # Crear VotingRegressor
            voting = VotingRegressor(estimators=modelos_base)
            
            # Entrenar
            voting.fit(X, y)
            
            # Evaluación
            y_pred = voting.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            metricas = {
                'r2': r2,
                'rmse': rmse,
                'tipo': 'voting_inteligente',
                'modelos_base': len(modelos_base)
            }
            
            return voting, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando voting inteligente: {e}")
            return None, {}
    
    def _crear_hibrido_adaptativo(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear modelo híbrido adaptativo que selecciona el mejor modelo por contexto"""
        try:
            print("[CREANDO] Modelo híbrido adaptativo...")
            
            # Crear modelos especializados
            modelos_especializados = {
                'RandomForest_Ultra': RandomForestRegressor(
                    n_estimators=500, max_depth=30, min_samples_split=2,
                    random_state=42, n_jobs=-1
                ),
                'GradientBoosting_Ultra': GradientBoostingRegressor(
                    n_estimators=1000, learning_rate=0.01, max_depth=15,
                    random_state=42
                ),
                'ExtraTrees_Ultra': ExtraTreesRegressor(
                    n_estimators=600, max_depth=35, min_samples_split=2,
                    random_state=42, n_jobs=-1
                )
            }
            
            # Entrenar todos los modelos
            modelos_entrenados = {}
            metricas_individuales = {}
            
            for nombre, modelo in modelos_especializados.items():
                modelo.fit(X, y)
                y_pred = modelo.predict(X)
                
                modelos_entrenados[nombre] = modelo
                metricas_individuales[nombre] = {
                    'r2': r2_score(y, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y, y_pred))
                }
            
            # Seleccionar el mejor modelo individual
            mejor_modelo_nombre = max(metricas_individuales.keys(), 
                                    key=lambda x: metricas_individuales[x]['r2'])
            mejor_modelo = modelos_entrenados[mejor_modelo_nombre]
            
            metricas = {
                'r2': metricas_individuales[mejor_modelo_nombre]['r2'],
                'rmse': metricas_individuales[mejor_modelo_nombre]['rmse'],
                'tipo': 'hibrido_adaptativo',
                'mejor_modelo': mejor_modelo_nombre,
                'metricas_individuales': metricas_individuales
            }
            
            return mejor_modelo, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando híbrido adaptativo: {e}")
            return None, {}
    
    def _optimizar_pesos_ensemble(self, modelo, X: np.ndarray, y: np.ndarray) -> Dict:
        """Optimizar pesos del ensemble usando optimización numérica"""
        try:
            if hasattr(modelo, 'estimators_'):
                print("[OPTIMIZANDO] Pesos del ensemble...")
                
                # Obtener predicciones de cada modelo base
                predicciones_modelos = {}
                for nombre, modelo_base in modelo.estimators_:
                    pred = modelo_base.predict(X)
                    predicciones_modelos[nombre] = pred
                
                # Función objetivo para optimización
                def objetivo_pesos(pesos):
                    # Normalizar pesos
                    pesos_norm = pesos / np.sum(pesos)
                    
                    # Predicción ponderada
                    pred_ponderada = np.zeros(len(y))
                    for i, (nombre, _) in enumerate(modelo.estimators_):
                        pred_ponderada += pesos_norm[i] * predicciones_modelos[nombre]
                    
                    # Calcular RMSE
                    rmse = np.sqrt(mean_squared_error(y, pred_ponderada))
                    return rmse
                
                # Optimización
                pesos_iniciales = np.ones(len(modelo.estimators_)) / len(modelo.estimators_)
                resultado = minimize(objetivo_pesos, pesos_iniciales, method='L-BFGS-B',
                                   bounds=[(0, 1)] * len(pesos_iniciales))
                
                pesos_optimizados = resultado.x / np.sum(resultado.x)
                
                # Crear diccionario de pesos
                pesos_dict = {}
                for i, (nombre, _) in enumerate(modelo.estimators_):
                    pesos_dict[nombre] = pesos_optimizados[i]
                
                print(f"[OK] Pesos optimizados: {pesos_dict}")
                return pesos_dict
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error optimizando pesos: {e}")
            return {}
    
    def _evaluar_modelo_hibrido(self, modelo, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Dict:
        """Evaluar modelo híbrido con métricas avanzadas"""
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
            mape = np.mean(np.abs((y - y_pred) / (y + 1e-8))) * 100
            max_error = np.max(np.abs(y - y_pred))
            
            # Análisis de residuos
            residuos = y - y_pred
            skewness = stats.skew(residuos)
            kurtosis = stats.kurtosis(residuos)
            
            return {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'max_error': max_error,
                'cv_r2_mean': scores_r2.mean(),
                'cv_r2_std': scores_r2.std(),
                'cv_rmse_mean': np.sqrt(-scores_rmse.mean()),
                'cv_rmse_std': np.sqrt(-scores_rmse).std(),
                'cv_mae_mean': -scores_mae.mean(),
                'cv_mae_std': scores_mae.std(),
                'skewness': skewness,
                'kurtosis': kurtosis,
                'variable_objetivo': variable_objetivo,
                'fecha_evaluacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando modelo híbrido: {e}")
            return {}
    
    def generar_proyecciones_hibridas(self, nombre_modelo: str, horizonte_dias: int = 30,
                                    incluir_incertidumbre: bool = True) -> List[Dict]:
        """Generar proyecciones usando modelo híbrido con análisis de incertidumbre"""
        try:
            print(f"[PROYECTANDO] Usando modelo híbrido '{nombre_modelo}' para {horizonte_dias} días...")
            
            if nombre_modelo not in self.modelos_hibridos:
                raise ValueError(f"Modelo híbrido '{nombre_modelo}' no está activo")
            
            modelo_info = self.modelos_hibridos[nombre_modelo]
            modelo = modelo_info['modelo']
            preprocessor = modelo_info['preprocessor']
            variable_objetivo = modelo_info['variable_objetivo']
            
            # Generar proyecciones
            proyecciones = []
            fecha_actual = datetime.now()
            
            for i in range(horizonte_dias):
                fecha_proyeccion = fecha_actual + timedelta(days=i)
                
                # Preparar características para predicción
                X_pred = self._preparar_caracteristicas_proyeccion_hibrida(
                    fecha_proyeccion, variable_objetivo, preprocessor
                )
                
                # Realizar predicción
                valor_proyectado = modelo.predict(X_pred.reshape(1, -1))[0]
                
                # Análisis de incertidumbre
                if incluir_incertidumbre:
                    incertidumbre = self._calcular_incertidumbre_prediccion(
                        modelo, X_pred, i, horizonte_dias
                    )
                else:
                    incertidumbre = {
                        'intervalo_inferior': None,
                        'intervalo_superior': None,
                        'confianza': 1.0,
                        'incertidumbre_epistemica': 0.0,
                        'incertidumbre_aleatoria': 0.0
                    }
                
                proyeccion = {
                    'fecha': fecha_proyeccion.strftime('%Y-%m-%d'),
                    'dias_futuro': i + 1,
                    'variable': variable_objetivo,
                    'valor_proyectado': round(valor_proyectado, 4),
                    'intervalo_inferior': round(incertidumbre['intervalo_inferior'], 4) if incertidumbre['intervalo_inferior'] else None,
                    'intervalo_superior': round(incertidumbre['intervalo_superior'], 4) if incertidumbre['intervalo_superior'] else None,
                    'confianza': round(incertidumbre['confianza'], 4),
                    'incertidumbre_epistemica': round(incertidumbre['incertidumbre_epistemica'], 4),
                    'incertidumbre_aleatoria': round(incertidumbre['incertidumbre_aleatoria'], 4),
                    'modelo_usado': nombre_modelo,
                    'tipo_hibrido': modelo_info['tipo_hibrido']
                }
                
                proyecciones.append(proyeccion)
            
            print(f"[OK] {len(proyecciones)} proyecciones híbridas generadas")
            return proyecciones
            
        except Exception as e:
            print(f"[ERROR] Error generando proyecciones híbridas: {e}")
            return []
    
    def _calcular_incertidumbre_prediccion(self, modelo, X_pred: np.ndarray, 
                                         dia_actual: int, horizonte_total: int) -> Dict:
        """Calcular incertidumbre de predicción usando múltiples técnicas"""
        try:
            # Incertidumbre por horizonte temporal
            confianza_temporal = max(0.1, 1.0 - (dia_actual / horizonte_total) * 0.6)
            
            # Incertidumbre epistemica (del modelo)
            if hasattr(modelo, 'estimators_'):
                # Para ensembles, usar varianza entre modelos
                predicciones_modelos = []
                for _, modelo_base in modelo.estimators_:
                    pred = modelo_base.predict(X_pred.reshape(1, -1))[0]
                    predicciones_modelos.append(pred)
                
                incertidumbre_epistemica = np.std(predicciones_modelos)
            else:
                # Para modelos individuales, usar métricas del modelo
                incertidumbre_epistemica = 0.1  # Valor por defecto
            
            # Incertidumbre aleatoria (ruido inherente)
            incertidumbre_aleatoria = 0.05 * confianza_temporal
            
            # Intervalo de confianza total
            incertidumbre_total = incertidumbre_epistemica + incertidumbre_aleatoria
            
            prediccion_central = modelo.predict(X_pred.reshape(1, -1))[0]
            
            return {
                'intervalo_inferior': prediccion_central - 1.96 * incertidumbre_total,
                'intervalo_superior': prediccion_central + 1.96 * incertidumbre_total,
                'confianza': confianza_temporal,
                'incertidumbre_epistemica': incertidumbre_epistemica,
                'incertidumbre_aleatoria': incertidumbre_aleatoria
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando incertidumbre: {e}")
            return {
                'intervalo_inferior': None,
                'intervalo_superior': None,
                'confianza': 0.5,
                'incertidumbre_epistemica': 0.0,
                'incertidumbre_aleatoria': 0.0
            }
    
    def _preparar_caracteristicas_proyeccion_hibrida(self, fecha: datetime, variable_objetivo: str, 
                                                   preprocessor) -> np.ndarray:
        """Preparar características para proyección con modelo híbrido"""
        try:
            # Crear DataFrame temporal con características básicas
            df_temp = pd.DataFrame({
                'fecha': [fecha],
                'temperatura_max': [20 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 2)],
                'temperatura_min': [15 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5)],
                'temperatura_promedio': [17.5 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5)],
                'humedad_relativa': [70 - (fecha.month - 6) * 2 + np.random.normal(0, 5)],
                'velocidad_viento': [10 + np.random.normal(0, 3)],
                'direccion_viento': [np.random.uniform(0, 360)],
                'precipitacion': [0 if np.random.random() > 0.1 else np.random.exponential(2)],
                'presion_atmosferica': [1013 + np.random.normal(0, 5)],
                'nubosidad': [50 + np.random.normal(0, 15)],
                'radiacion_solar': [800 + np.random.normal(0, 50)],
                'punto_rocio': [15 + np.random.normal(0, 2)],
                'indice_calor': [18 + np.random.normal(0, 2)],
                'indice_frio': [16 + np.random.normal(0, 2)],
                'año': [fecha.year],
                'mes': [fecha.month],
                'dia': [fecha.day],
                'dia_semana': [fecha.weekday()],
                'dia_año': [fecha.timetuple().tm_yday],
                'trimestre': [(fecha.month - 1) // 3 + 1]
            })
            
            # Agregar características derivadas
            df_temp['amplitud_termica'] = df_temp['temperatura_max'] - df_temp['temperatura_min']
            df_temp['presion_normalizada'] = (df_temp['presion_atmosferica'] - 1000) / 50
            df_temp['humedad_normalizada'] = (df_temp['humedad_relativa'] - 50) / 50
            df_temp['viento_normalizado'] = df_temp['velocidad_viento'] / 20
            df_temp['temp_humedad_interaccion'] = df_temp['temperatura_promedio'] * df_temp['humedad_relativa']
            df_temp['presion_viento_interaccion'] = df_temp['presion_atmosferica'] * df_temp['velocidad_viento']
            df_temp['radiacion_nubosidad_interaccion'] = df_temp['radiacion_solar'] * (100 - df_temp['nubosidad'])
            
            # Agregar características cíclicas
            for periodo in [12, 365, 52]:
                if periodo == 12:
                    df_temp[f'mes_sin_{periodo}'] = np.sin(2 * np.pi * df_temp['mes'] / periodo)
                    df_temp[f'mes_cos_{periodo}'] = np.cos(2 * np.pi * df_temp['mes'] / periodo)
                elif periodo == 365:
                    df_temp[f'dia_sin_{periodo}'] = np.sin(2 * np.pi * df_temp['dia_año'] / periodo)
                    df_temp[f'dia_cos_{periodo}'] = np.cos(2 * np.pi * df_temp['dia_año'] / periodo)
            
            # Agregar codificación de estación (quillota_centro por defecto)
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            for est in estaciones:
                df_temp[f'estacion_{est}'] = 1 if est == 'quillota_centro' else 0
            
            # Seleccionar características que el modelo espera
            caracteristicas_esperadas = [
                'temperatura_max', 'temperatura_min', 'temperatura_promedio',
                'humedad_relativa', 'velocidad_viento', 'direccion_viento',
                'precipitacion', 'presion_atmosferica', 'nubosidad',
                'radiacion_solar', 'punto_rocio', 'indice_calor', 'indice_frio',
                'año', 'mes', 'dia', 'dia_semana', 'dia_año', 'trimestre',
                'amplitud_termica', 'presion_normalizada', 'humedad_normalizada',
                'viento_normalizado', 'temp_humedad_interaccion',
                'presion_viento_interaccion', 'radiacion_nubosidad_interaccion'
            ]
            
            # Agregar características cíclicas y de estación
            caracteristicas_ciclicas = [col for col in df_temp.columns if '_sin_' in col or '_cos_' in col]
            caracteristicas_estacion = [col for col in df_temp.columns if col.startswith('estacion_')]
            
            todas_caracteristicas = caracteristicas_esperadas + caracteristicas_ciclicas + caracteristicas_estacion
            caracteristicas_disponibles = [col for col in todas_caracteristicas if col in df_temp.columns]
            
            X_temp = df_temp[caracteristicas_disponibles].fillna(0)
            
            # Aplicar preprocesamiento
            X_processed = preprocessor.transform(X_temp)
            
            return X_processed[0]  # Retornar primera fila como array
            
        except Exception as e:
            self.logger.error(f"Error preparando características de proyección híbrida: {e}")
            return np.array([])
    
    def listar_modelos_hibridos(self) -> List[Dict]:
        """Listar todos los modelos híbridos activos"""
        try:
            modelos = []
            for nombre, info in self.modelos_hibridos.items():
                modelos.append({
                    'nombre': nombre,
                    'tipo_hibrido': info['tipo_hibrido'],
                    'variable_objetivo': info['variable_objetivo'],
                    'r2': info['metricas']['r2'],
                    'rmse': info['metricas']['rmse'],
                    'tiempo_entrenamiento': info['metricas']['tiempo_entrenamiento'],
                    'fecha_creacion': info['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S'),
                    'modelo_id': info['modelo_id']
                })
            return modelos
        except Exception as e:
            self.logger.error(f"Error listando modelos híbridos: {e}")
            return []
    
    # Métodos auxiliares de base de datos
    def _cargar_datos_historicos(self) -> pd.DataFrame:
        """Cargar datos históricos (usar datos de 3 años si están disponibles)"""
        try:
            # Intentar cargar datos de 3 años primero
            conn = sqlite3.connect("modelos_dinamicos.db")
            df = pd.read_sql_query(
                "SELECT * FROM datos_historicos_3_anos ORDER BY fecha",
                conn,
                parse_dates=['fecha']
            )
            conn.close()
            
            if not df.empty:
                return df
            
            # Si no hay datos de 3 años, generar datos de demostración
            return self._generar_datos_demostracion()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos: {e}")
            return self._generar_datos_demostracion()
    
    def _generar_datos_demostracion(self) -> pd.DataFrame:
        """Generar datos de demostración para el sistema híbrido"""
        try:
            print("[GENERANDO] Datos de demostración...")
            np.random.seed(42)
            
            # Generar 2 años de datos
            fecha_inicio = datetime.now() - timedelta(days=2 * 365)
            fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
            
            datos = []
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            
            for fecha in fechas:
                for estacion in estaciones:
                    mes = fecha.month
                    
                    # Temperatura con patrones estacionales
                    temp_base = 16 + 7 * np.sin(2 * np.pi * (mes - 1) / 12)
                    variacion_estacion = {
                        'quillota_centro': 0, 'la_cruz': -1.5, 'nogueira': -2.0,
                        'colliguay': -3.0, 'san_isidro': 1.0, 'hijuelas': -1.0
                    }
                    
                    temp_base += variacion_estacion.get(estacion, 0)
                    temp_max = temp_base + np.random.normal(6, 2)
                    temp_min = temp_base - np.random.normal(6, 1.5)
                    temp_promedio = (temp_max + temp_min) / 2
                    
                    # Otras variables
                    humedad = 75 - (temp_promedio - 15) * 1.5 + np.random.normal(0, 8)
                    humedad = np.clip(humedad, 25, 95)
                    
                    velocidad_viento = max(0, 8 + np.random.normal(0, 4))
                    direccion_viento = np.random.uniform(0, 360)
                    
                    precipitacion = np.random.exponential(3) if np.random.random() < 0.1 else 0
                    presion = 1013.25 + np.random.normal(0, 8)
                    nubosidad = min(100, max(0, humedad * 0.8 + precipitacion * 5 + np.random.normal(0, 15)))
                    radiacion = max(0, 800 - nubosidad * 3 + np.random.normal(0, 80))
                    
                    punto_rocio = temp_promedio - (100 - humedad) / 5
                    indice_calor = temp_promedio + (humedad - 50) * 0.08
                    indice_frio = temp_promedio - np.sqrt(velocidad_viento) * 0.7
                    
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
            print(f"[OK] Datos de demostración generados: {len(df)} registros")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generando datos de demostración: {e}")
            return pd.DataFrame()
    
    def _guardar_modelo_hibrido_en_bd(self, nombre: str, tipo_hibrido: str, variable: str,
                                     modelos_base: List[str], pesos: Dict, metricas: Dict,
                                     descripcion: str) -> int:
        """Guardar modelo híbrido en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO modelos_hibridos 
                (nombre_modelo, tipo_hibrido, variable_objetivo, modelos_base, 
                 pesos_optimizados, metricas, tiempo_entrenamiento, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, tipo_hibrido, variable,
                json.dumps(modelos_base),
                json.dumps(pesos),
                json.dumps(metricas),
                metricas.get('tiempo_entrenamiento', 0),
                descripcion
            ))
            
            modelo_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return modelo_id
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo híbrido en BD: {e}")
            return 0

def main():
    """Función principal para demostración"""
    print("="*80)
    print("SISTEMA DE MODELOS HÍBRIDOS INNOVADORES - METGO 3D QUILLOTA")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaModelosHibridosInnovadores()
    
    # Crear modelos híbridos innovadores
    print("\n[1] CREANDO MODELOS HÍBRIDOS INNOVADORES...")
    
    # Modelo 1: Ensemble Optimizado
    resultado1 = sistema.crear_modelo_hibrido_innovador(
        nombre_modelo="Ensemble_Ultra_Temp",
        variable_objetivo="temperatura_promedio",
        tipo_hibrido="ensemble_optimizado",
        descripcion="Ensemble optimizado con 5 algoritmos de alta precisión"
    )
    
    # Modelo 2: Stacking Avanzado
    resultado2 = sistema.crear_modelo_hibrido_innovador(
        nombre_modelo="Stacking_Ultra_Humedad",
        variable_objetivo="humedad_relativa",
        tipo_hibrido="stacking_avanzado",
        descripcion="Stacking con meta-aprendizaje Ridge optimizado"
    )
    
    # Modelo 3: Voting Inteligente
    resultado3 = sistema.crear_modelo_hibrido_innovador(
        nombre_modelo="Voting_Ultra_Precipitacion",
        variable_objetivo="precipitacion",
        tipo_hibrido="voting_inteligente",
        descripcion="Voting inteligente con pesos adaptativos"
    )
    
    # Generar proyecciones híbridas
    print("\n[2] GENERANDO PROYECCIONES HÍBRIDAS...")
    
    proyecciones_temp = sistema.generar_proyecciones_hibridas("Ensemble_Ultra_Temp", 30)
    proyecciones_humedad = sistema.generar_proyecciones_hibridas("Stacking_Ultra_Humedad", 20)
    proyecciones_precip = sistema.generar_proyecciones_hibridas("Voting_Ultra_Precipitacion", 15)
    
    # Listar modelos híbridos
    print("\n[3] MODELOS HÍBRIDOS ACTIVOS:")
    modelos_hibridos = sistema.listar_modelos_hibridos()
    for modelo in modelos_hibridos:
        print(f"    - {modelo['nombre']}: {modelo['tipo_hibrido']} (R²={modelo['r2']:.6f}, Tiempo={modelo['tiempo_entrenamiento']:.2f}s)")
    
    print("\n" + "="*80)
    print("SISTEMA DE MODELOS HÍBRIDOS INNOVADORES COMPLETADO")
    print("="*80)
    print(f"Modelos híbridos creados: {len(modelos_hibridos)}")
    print(f"Proyecciones temperatura: {len(proyecciones_temp)}")
    print(f"Proyecciones humedad: {len(proyecciones_humedad)}")
    print(f"Proyecciones precipitación: {len(proyecciones_precip)}")
    
    # Resumen de rendimiento
    if modelos_hibridos:
        r2_promedio = np.mean([m['r2'] for m in modelos_hibridos])
        tiempo_promedio = np.mean([m['tiempo_entrenamiento'] for m in modelos_hibridos])
        print(f"R² promedio: {r2_promedio:.6f}")
        print(f"Tiempo promedio: {tiempo_promedio:.2f}s")
    
    print("="*80)

if __name__ == "__main__":
    main()
