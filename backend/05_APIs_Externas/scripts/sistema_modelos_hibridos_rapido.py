"""
SISTEMA DE MODELOS HÍBRIDOS RÁPIDOS - METGO 3D QUILLOTA
Versión optimizada para máxima velocidad manteniendo alta precisión
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
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

warnings.filterwarnings('ignore')

class SistemaModelosHibridosRapidos:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "modelos_hibridos_rapidos.db"
        self.modelos_dir = "modelos_hibridos_rapidos"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos_hibridos = {}
        self.metricas_modelos = {}
        
        # Configuración de modelos base optimizados para velocidad
        self.modelos_base_rapidos = {
            'RandomForest_Rapido': {
                'clase': RandomForestRegressor,
                'parametros': {
                    'n_estimators': 100,  # Reducido para velocidad
                    'max_depth': 15,
                    'min_samples_split': 5,
                    'random_state': 42,
                    'n_jobs': -1
                },
                'peso_inicial': 0.3
            },
            'GradientBoosting_Rapido': {
                'clase': GradientBoostingRegressor,
                'parametros': {
                    'n_estimators': 100,  # Reducido para velocidad
                    'learning_rate': 0.1,
                    'max_depth': 8,
                    'random_state': 42
                },
                'peso_inicial': 0.3
            },
            'ExtraTrees_Rapido': {
                'clase': ExtraTreesRegressor,
                'parametros': {
                    'n_estimators': 100,  # Reducido para velocidad
                    'max_depth': 15,
                    'min_samples_split': 5,
                    'random_state': 42,
                    'n_jobs': -1
                },
                'peso_inicial': 0.2
            },
            'Ridge_Rapido': {
                'clase': Ridge,
                'parametros': {
                    'alpha': 1.0,
                    'solver': 'auto'
                },
                'peso_inicial': 0.1
            },
            'SVR_Rapido': {
                'clase': SVR,
                'parametros': {
                    'kernel': 'rbf',
                    'C': 10,  # Reducido para velocidad
                    'gamma': 'scale'
                },
                'peso_inicial': 0.1
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.modelos_dir, 'logs']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para modelos híbridos rápidos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de modelos híbridos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS modelos_hibridos_rapidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_modelo TEXT UNIQUE NOT NULL,
                    tipo_hibrido TEXT NOT NULL,
                    variable_objetivo TEXT NOT NULL,
                    modelos_base TEXT NOT NULL,
                    metricas TEXT NOT NULL,
                    tiempo_entrenamiento REAL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo',
                    descripcion TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Base de datos modelos híbridos rápidos inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def crear_modelo_hibrido_rapido(self, nombre_modelo: str, variable_objetivo: str,
                                   tipo_hibrido: str = 'ensemble_rapido',
                                   descripcion: str = "") -> Dict:
        """Crear modelo híbrido rápido con máxima velocidad"""
        try:
            print(f"[CREANDO] Modelo híbrido rápido: {nombre_modelo}")
            inicio_tiempo = datetime.now()
            
            # Cargar datos
            df = self._cargar_datos_historicos()
            if df.empty:
                raise ValueError("No hay datos históricos disponibles")
            
            # Preparar datos optimizados para velocidad
            X, y = self._preparar_datos_rapidos(df, variable_objetivo)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No hay datos válidos para entrenar")
            
            print(f"[DATOS] {len(X)} muestras, {X.shape[1]} características")
            
            # Crear modelo híbrido según tipo
            if tipo_hibrido == 'ensemble_rapido':
                modelo_hibrido, metricas = self._crear_ensemble_rapido(X, y, variable_objetivo)
            elif tipo_hibrido == 'voting_rapido':
                modelo_hibrido, metricas = self._crear_voting_rapido(X, y, variable_objetivo)
            else:
                raise ValueError(f"Tipo de híbrido '{tipo_hibrido}' no soportado")
            
            # Evaluación rápida
            metricas_finales = self._evaluar_modelo_rapido(modelo_hibrido, X, y, variable_objetivo)
            
            tiempo_entrenamiento = (datetime.now() - inicio_tiempo).total_seconds()
            metricas_finales['tiempo_entrenamiento'] = tiempo_entrenamiento
            
            # Guardar modelo
            modelo_id = self._guardar_modelo_hibrido_en_bd(
                nombre_modelo, tipo_hibrido, variable_objetivo,
                list(self.modelos_base_rapidos.keys()),
                metricas_finales, descripcion
            )
            
            # Guardar modelo en disco
            ruta_modelo = os.path.join(self.modelos_dir, f"{nombre_modelo}.joblib")
            joblib.dump({
                'modelo': modelo_hibrido,
                'metricas': metricas_finales,
                'tipo_hibrido': tipo_hibrido
            }, ruta_modelo)
            
            # Actualizar modelos híbridos activos
            self.modelos_hibridos[nombre_modelo] = {
                'modelo': modelo_hibrido,
                'tipo_hibrido': tipo_hibrido,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas_finales,
                'modelo_id': modelo_id,
                'fecha_creacion': datetime.now()
            }
            
            print(f"[OK] Modelo híbrido rápido '{nombre_modelo}' creado exitosamente")
            print(f"    R² = {metricas_finales['r2']:.6f}")
            print(f"    RMSE = {metricas_finales['rmse']:.6f}")
            print(f"    Tiempo = {tiempo_entrenamiento:.2f}s")
            
            return {
                'modelo_id': modelo_id,
                'nombre_modelo': nombre_modelo,
                'tipo_hibrido': tipo_hibrido,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas_finales,
                'tiempo_entrenamiento': tiempo_entrenamiento,
                'estado': 'creado_exitosamente'
            }
            
        except Exception as e:
            print(f"[ERROR] Error creando modelo híbrido rápido: {e}")
            return {'error': str(e)}
    
    def _preparar_datos_rapidos(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos optimizados para velocidad"""
        try:
            # Crear características básicas (sin tantas características avanzadas)
            df['año'] = df['fecha'].dt.year
            df['mes'] = df['fecha'].dt.month
            df['dia'] = df['fecha'].dt.day
            df['dia_semana'] = df['fecha'].dt.dayofweek
            df['dia_año'] = df['fecha'].dt.dayofyear
            
            # Características cíclicas básicas
            df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
            df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
            df['dia_sin'] = np.sin(2 * np.pi * df['dia_año'] / 365)
            df['dia_cos'] = np.cos(2 * np.pi * df['dia_año'] / 365)
            
            # Características derivadas básicas
            df['amplitud_termica'] = df['temperatura_max'] - df['temperatura_min']
            df['presion_normalizada'] = (df['presion_atmosferica'] - 1000) / 50
            
            # Codificar estación
            if 'estacion' in df.columns:
                estacion_encoded = pd.get_dummies(df['estacion'], prefix='estacion')
                df = pd.concat([df, estacion_encoded], axis=1)
            
            # Seleccionar características básicas
            caracteristicas_base = [
                'temperatura_max', 'temperatura_min', 'temperatura_promedio',
                'humedad_relativa', 'velocidad_viento', 'precipitacion',
                'presion_atmosferica', 'nubosidad', 'radiacion_solar',
                'año', 'mes', 'dia', 'dia_semana', 'dia_año',
                'mes_sin', 'mes_cos', 'dia_sin', 'dia_cos',
                'amplitud_termica', 'presion_normalizada'
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
            
            # Selección rápida de características (máximo 30)
            if X_scaled.shape[1] > 30:
                selector = SelectKBest(score_func=f_regression, k=30)
                X_scaled = selector.fit_transform(X_scaled, y)
            
            return X_scaled, y.values
            
        except Exception as e:
            self.logger.error(f"Error preparando datos rápidos: {e}")
            return np.array([]), np.array([])
    
    def _crear_ensemble_rapido(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear ensemble rápido con modelos optimizados"""
        try:
            print("[CREANDO] Ensemble rápido...")
            
            # Crear modelos base rápidos
            modelos_base = {}
            for nombre, config in self.modelos_base_rapidos.items():
                modelo = config['clase'](**config['parametros'])
                modelos_base[nombre] = modelo
            
            # Crear VotingRegressor con pesos optimizados
            ensemble = VotingRegressor(
                estimators=list(modelos_base.items()),
                weights=list(config['peso_inicial'] for config in self.modelos_base_rapidos.values())
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
                'tipo': 'ensemble_rapido',
                'modelos_base': len(modelos_base)
            }
            
            return ensemble, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando ensemble rápido: {e}")
            return None, {}
    
    def _crear_voting_rapido(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Tuple[Any, Dict]:
        """Crear voting rápido"""
        try:
            print("[CREANDO] Voting rápido...")
            
            # Crear modelos base
            modelos_base = []
            for nombre, config in self.modelos_base_rapidos.items():
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
                'tipo': 'voting_rapido',
                'modelos_base': len(modelos_base)
            }
            
            return voting, metricas
            
        except Exception as e:
            self.logger.error(f"Error creando voting rápido: {e}")
            return None, {}
    
    def _evaluar_modelo_rapido(self, modelo, X: np.ndarray, y: np.ndarray, variable_objetivo: str) -> Dict:
        """Evaluar modelo con métricas rápidas"""
        try:
            # Validación cruzada temporal (menos splits para velocidad)
            tscv = TimeSeriesSplit(n_splits=3)  # Reducido para velocidad
            
            # Métricas de validación cruzada
            scores_r2 = cross_val_score(modelo, X, y, cv=tscv, scoring='r2')
            scores_rmse = cross_val_score(modelo, X, y, cv=tscv, scoring='neg_mean_squared_error')
            
            # Métricas en conjunto completo
            y_pred = modelo.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mae = mean_absolute_error(y, y_pred)
            
            # Métricas adicionales básicas
            mape = np.mean(np.abs((y - y_pred) / (y + 1e-8))) * 100
            
            return {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'cv_r2_mean': scores_r2.mean(),
                'cv_r2_std': scores_r2.std(),
                'cv_rmse_mean': np.sqrt(-scores_rmse.mean()),
                'cv_rmse_std': np.sqrt(-scores_rmse).std(),
                'variable_objetivo': variable_objetivo,
                'fecha_evaluacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando modelo rápido: {e}")
            return {}
    
    def generar_proyecciones_rapidas(self, nombre_modelo: str, horizonte_dias: int = 30) -> List[Dict]:
        """Generar proyecciones rápidas"""
        try:
            print(f"[PROYECTANDO] Usando modelo híbrido rápido '{nombre_modelo}' para {horizonte_dias} días...")
            
            if nombre_modelo not in self.modelos_hibridos:
                raise ValueError(f"Modelo híbrido '{nombre_modelo}' no está activo")
            
            modelo_info = self.modelos_hibridos[nombre_modelo]
            modelo = modelo_info['modelo']
            variable_objetivo = modelo_info['variable_objetivo']
            
            # Generar proyecciones
            proyecciones = []
            fecha_actual = datetime.now()
            
            for i in range(horizonte_dias):
                fecha_proyeccion = fecha_actual + timedelta(days=i)
                
                # Preparar características para predicción (simplificado)
                X_pred = self._preparar_caracteristicas_proyeccion_rapida(
                    fecha_proyeccion, variable_objetivo
                )
                
                # Realizar predicción
                valor_proyectado = modelo.predict(X_pred.reshape(1, -1))[0]
                
                # Intervalo de confianza simplificado
                rmse = modelo_info['metricas']['rmse']
                intervalo = rmse * 1.96
                confianza = max(0.1, 1.0 - (i / horizonte_dias) * 0.5)
                
                proyeccion = {
                    'fecha': fecha_proyeccion.strftime('%Y-%m-%d'),
                    'dias_futuro': i + 1,
                    'variable': variable_objetivo,
                    'valor_proyectado': round(valor_proyectado, 4),
                    'intervalo_inferior': round(valor_proyectado - intervalo * confianza, 4),
                    'intervalo_superior': round(valor_proyectado + intervalo * confianza, 4),
                    'confianza': round(confianza, 3),
                    'modelo_usado': nombre_modelo,
                    'tipo_hibrido': modelo_info['tipo_hibrido']
                }
                
                proyecciones.append(proyeccion)
            
            print(f"[OK] {len(proyecciones)} proyecciones rápidas generadas")
            return proyecciones
            
        except Exception as e:
            print(f"[ERROR] Error generando proyecciones rápidas: {e}")
            return []
    
    def _preparar_caracteristicas_proyeccion_rapida(self, fecha: datetime, variable_objetivo: str) -> np.ndarray:
        """Preparar características para proyección rápida"""
        try:
            # Características básicas
            caracteristicas = [
                20 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 2),  # temp_max
                15 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5),  # temp_min
                17.5 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5),  # temp_promedio
                70 + np.random.normal(0, 5),  # humedad_relativa
                10 + np.random.normal(0, 3),  # velocidad_viento
                0 if np.random.random() > 0.1 else np.random.exponential(2),  # precipitacion
                1013 + np.random.normal(0, 5),  # presion_atmosferica
                50 + np.random.normal(0, 15),  # nubosidad
                800 + np.random.normal(0, 50),  # radiacion_solar
                fecha.year,  # año
                fecha.month,  # mes
                fecha.day,  # dia
                fecha.weekday(),  # dia_semana
                fecha.timetuple().tm_yday,  # dia_año
                np.sin(2 * np.pi * fecha.month / 12),  # mes_sin
                np.cos(2 * np.pi * fecha.month / 12),  # mes_cos
                np.sin(2 * np.pi * fecha.timetuple().tm_yday / 365),  # dia_sin
                np.cos(2 * np.pi * fecha.timetuple().tm_yday / 365),  # dia_cos
                5 + np.random.normal(0, 2),  # amplitud_termica
                0.26 + np.random.normal(0, 0.1)  # presion_normalizada
            ]
            
            # Agregar codificación de estación (quillota_centro = 1, otros = 0)
            estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
            for est in estaciones:
                caracteristicas.append(1 if est == 'quillota_centro' else 0)
            
            return np.array(caracteristicas)
            
        except Exception as e:
            self.logger.error(f"Error preparando características de proyección rápida: {e}")
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
    
    # Métodos auxiliares
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
            
            # Si no hay datos de 3 años, generar datos de demostración rápidos
            return self._generar_datos_demostracion_rapidos()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos: {e}")
            return self._generar_datos_demostracion_rapidos()
    
    def _generar_datos_demostracion_rapidos(self) -> pd.DataFrame:
        """Generar datos de demostración rápidos"""
        try:
            print("[GENERANDO] Datos de demostración rápidos...")
            np.random.seed(42)
            
            # Generar 1 año de datos (menos datos para velocidad)
            fecha_inicio = datetime.now() - timedelta(days=365)
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
                    precipitacion = np.random.exponential(3) if np.random.random() < 0.1 else 0
                    presion = 1013.25 + np.random.normal(0, 8)
                    nubosidad = min(100, max(0, humedad * 0.8 + precipitacion * 5 + np.random.normal(0, 15)))
                    radiacion = max(0, 800 - nubosidad * 3 + np.random.normal(0, 80))
                    
                    datos.append({
                        'fecha': fecha,
                        'estacion': estacion,
                        'temperatura_max': round(temp_max, 1),
                        'temperatura_min': round(temp_min, 1),
                        'temperatura_promedio': round(temp_promedio, 1),
                        'humedad_relativa': round(humedad, 1),
                        'velocidad_viento': round(velocidad_viento, 1),
                        'precipitacion': round(precipitacion, 1),
                        'presion_atmosferica': round(presion, 1),
                        'nubosidad': round(nubosidad, 1),
                        'radiacion_solar': round(radiacion, 1)
                    })
            
            df = pd.DataFrame(datos)
            print(f"[OK] Datos de demostración rápidos generados: {len(df)} registros")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generando datos de demostración rápidos: {e}")
            return pd.DataFrame()
    
    def _guardar_modelo_hibrido_en_bd(self, nombre: str, tipo_hibrido: str, variable: str,
                                     modelos_base: List[str], metricas: Dict, descripcion: str) -> int:
        """Guardar modelo híbrido en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO modelos_hibridos_rapidos 
                (nombre_modelo, tipo_hibrido, variable_objetivo, modelos_base, 
                 metricas, tiempo_entrenamiento, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, tipo_hibrido, variable,
                json.dumps(modelos_base),
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
    """Función principal para demostración rápida"""
    print("="*80)
    print("SISTEMA DE MODELOS HÍBRIDOS RÁPIDOS - METGO 3D QUILLOTA")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaModelosHibridosRapidos()
    
    # Crear modelos híbridos rápidos
    print("\n[1] CREANDO MODELOS HÍBRIDOS RÁPIDOS...")
    
    # Modelo 1: Ensemble Rápido
    resultado1 = sistema.crear_modelo_hibrido_rapido(
        nombre_modelo="Ensemble_Rapido_Temp",
        variable_objetivo="temperatura_promedio",
        tipo_hibrido="ensemble_rapido",
        descripcion="Ensemble rápido con 5 algoritmos optimizados para velocidad"
    )
    
    # Modelo 2: Voting Rápido
    resultado2 = sistema.crear_modelo_hibrido_rapido(
        nombre_modelo="Voting_Rapido_Humedad",
        variable_objetivo="humedad_relativa",
        tipo_hibrido="voting_rapido",
        descripcion="Voting rápido para humedad relativa"
    )
    
    # Generar proyecciones rápidas
    print("\n[2] GENERANDO PROYECCIONES RÁPIDAS...")
    
    proyecciones_temp = sistema.generar_proyecciones_rapidas("Ensemble_Rapido_Temp", 30)
    proyecciones_humedad = sistema.generar_proyecciones_rapidas("Voting_Rapido_Humedad", 20)
    
    # Listar modelos híbridos
    print("\n[3] MODELOS HÍBRIDOS RÁPIDOS ACTIVOS:")
    modelos_hibridos = sistema.listar_modelos_hibridos()
    for modelo in modelos_hibridos:
        print(f"    - {modelo['nombre']}: {modelo['tipo_hibrido']} (R²={modelo['r2']:.6f}, Tiempo={modelo['tiempo_entrenamiento']:.2f}s)")
    
    print("\n" + "="*80)
    print("SISTEMA DE MODELOS HÍBRIDOS RÁPIDOS COMPLETADO")
    print("="*80)
    print(f"Modelos híbridos creados: {len(modelos_hibridos)}")
    print(f"Proyecciones temperatura: {len(proyecciones_temp)}")
    print(f"Proyecciones humedad: {len(proyecciones_humedad)}")
    
    # Resumen de rendimiento
    if modelos_hibridos:
        r2_promedio = np.mean([m['r2'] for m in modelos_hibridos])
        tiempo_promedio = np.mean([m['tiempo_entrenamiento'] for m in modelos_hibridos])
        print(f"R² promedio: {r2_promedio:.6f}")
        print(f"Tiempo promedio: {tiempo_promedio:.2f}s")
        print(f"Velocidad: {tiempo_promedio:.2f}s por modelo (MUY RÁPIDO)")
    
    print("="*80)

if __name__ == "__main__":
    main()
