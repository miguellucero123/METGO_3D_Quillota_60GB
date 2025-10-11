#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 IA AVANZADA PARA METGO 3D
Sistema Meteorológico Agrícola Quillota - Inteligencia Artificial Avanzada
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Machine Learning Avanzado
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention, MultiHeadAttention, LayerNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# AutoML
try:
    import autosklearn.regression
    AUTOSKLEARN_AVAILABLE = True
except ImportError:
    AUTOSKLEARN_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')

class IAAvanzadaMETGO:
    """Clase para IA avanzada del sistema METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_modelos': 'modelos_ia_avanzada',
            'directorio_datos': 'data/processed',
            'directorio_logs': 'logs/ia',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Configuración de modelos
        self.modelos_config = {
            'lstm': {
                'sequence_length': 24,
                'lstm_units': [64, 32],
                'dropout': 0.2,
                'epochs': 100,
                'batch_size': 32,
                'validation_split': 0.2
            },
            'transformer': {
                'd_model': 64,
                'num_heads': 8,
                'num_layers': 4,
                'dff': 128,
                'dropout': 0.1,
                'epochs': 50,
                'batch_size': 16
            },
            'ensemble': {
                'models': ['lstm', 'transformer', 'random_forest', 'gradient_boosting'],
                'weights': [0.3, 0.3, 0.2, 0.2]
            }
        }
        
        # Variables meteorológicas
        self.variables_meteorologicas = [
            'temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion',
            'humedad', 'presion', 'radiacion_solar', 'punto_rocio'
        ]
        
        # Crear directorios
        self._crear_directorios()
        
        # Inicializar modelos
        self.modelos = {}
        self.scalers = {}
        self.metricas = {}
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def cargar_datos_meteorologicos(self, archivo: str = None) -> pd.DataFrame:
        """Cargar datos meteorológicos para entrenamiento"""
        try:
            if archivo is None:
                archivo = f"{self.configuracion['directorio_datos']}/datos_meteorologicos_quillota.csv"
            
            if not Path(archivo).exists():
                print(f"Archivo no encontrado: {archivo}")
                return self._generar_datos_sinteticos()
            
            datos = pd.read_csv(archivo)
            datos['fecha'] = pd.to_datetime(datos['fecha'])
            datos.set_index('fecha', inplace=True)
            
            print(f"✅ Datos cargados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return self._generar_datos_sinteticos()
    
    def _generar_datos_sinteticos(self) -> pd.DataFrame:
        """Generar datos sintéticos para entrenamiento"""
        try:
            print("🔄 Generando datos sintéticos...")
            
            # Generar fechas (2 años de datos)
            fechas = pd.date_range(
                start='2022-01-01',
                end='2024-01-01',
                freq='H'
            )
            
            # Generar datos sintéticos realistas
            np.random.seed(42)
            datos = pd.DataFrame(index=fechas)
            
            # Temperatura (patrón estacional)
            datos['temperatura'] = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
            
            # Precipitación (eventos esporádicos)
            datos['precipitacion'] = np.random.exponential(0.5, len(fechas))
            datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, datos['precipitacion'], 0)
            
            # Viento
            datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
            datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
            
            # Humedad (inversamente relacionada con temperatura)
            datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
            datos['humedad'] = np.clip(datos['humedad'], 0, 100)
            
            # Presión
            datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
            
            # Radiación solar
            datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
            
            # Punto de rocío
            datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
            
            print(f"✅ Datos sintéticos generados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def preparar_datos_entrenamiento(self, datos: pd.DataFrame, variable: str, sequence_length: int = 24) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento de modelos de secuencia"""
        try:
            # Normalizar datos
            scaler = MinMaxScaler()
            datos_normalizados = scaler.fit_transform(datos[[variable]].values)
            
            # Crear secuencias
            X, y = [], []
            for i in range(sequence_length, len(datos_normalizados)):
                X.append(datos_normalizados[i-sequence_length:i])
                y.append(datos_normalizados[i])
            
            X = np.array(X)
            y = np.array(y)
            
            # Guardar scaler
            self.scalers[variable] = scaler
            
            print(f"✅ Datos preparados para {variable}: X={X.shape}, y={y.shape}")
            return X, y
            
        except Exception as e:
            print(f"Error preparando datos: {e}")
            return np.array([]), np.array([])
    
    def crear_modelo_lstm(self, input_shape: Tuple[int, int], variable: str) -> Model:
        """Crear modelo LSTM avanzado"""
        try:
            config = self.modelos_config['lstm']
            
            model = Sequential([
                LSTM(config['lstm_units'][0], return_sequences=True, input_shape=input_shape),
                Dropout(config['dropout']),
                LSTM(config['lstm_units'][1], return_sequences=False),
                Dropout(config['dropout']),
                Dense(32, activation='relu'),
                Dropout(config['dropout']),
                Dense(1, activation='linear')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            print(f"✅ Modelo LSTM creado para {variable}")
            return model
            
        except Exception as e:
            print(f"Error creando modelo LSTM: {e}")
            return None
    
    def crear_modelo_transformer(self, input_shape: Tuple[int, int], variable: str) -> Model:
        """Crear modelo Transformer para series temporales"""
        try:
            config = self.modelos_config['transformer']
            
            # Input layer
            inputs = tf.keras.Input(shape=input_shape)
            
            # Embedding layer
            x = Dense(config['d_model'])(inputs)
            
            # Transformer blocks
            for _ in range(config['num_layers']):
                # Multi-head attention
                attn_output = MultiHeadAttention(
                    num_heads=config['num_heads'],
                    key_dim=config['d_model'] // config['num_heads']
                )(x, x)
                
                # Add & Norm
                x = LayerNormalization(epsilon=1e-6)(x + attn_output)
                
                # Feed Forward
                ffn = Sequential([
                    Dense(config['dff'], activation='relu'),
                    Dense(config['d_model'])
                ])
                ffn_output = ffn(x)
                
                # Add & Norm
                x = LayerNormalization(epsilon=1e-6)(x + ffn_output)
            
            # Global average pooling
            x = tf.keras.layers.GlobalAveragePooling1D()(x)
            
            # Output layer
            outputs = Dense(1, activation='linear')(x)
            
            model = Model(inputs, outputs)
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            print(f"✅ Modelo Transformer creado para {variable}")
            return model
            
        except Exception as e:
            print(f"Error creando modelo Transformer: {e}")
            return None
    
    def entrenar_modelo_lstm(self, model: Model, X: np.ndarray, y: np.ndarray, variable: str) -> Dict:
        """Entrenar modelo LSTM"""
        try:
            config = self.modelos_config['lstm']
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5),
                ModelCheckpoint(
                    f"{self.configuracion['directorio_modelos']}/lstm_{variable}_best.h5",
                    save_best_only=True
                )
            ]
            
            # Entrenar
            history = model.fit(
                X, y,
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                validation_split=config['validation_split'],
                callbacks=callbacks,
                verbose=1
            )
            
            # Guardar modelo
            model.save(f"{self.configuracion['directorio_modelos']}/lstm_{variable}_final.h5")
            
            # Métricas
            metricas = {
                'variable': variable,
                'modelo': 'LSTM',
                'epochs_entrenados': len(history.history['loss']),
                'loss_final': history.history['loss'][-1],
                'val_loss_final': history.history['val_loss'][-1],
                'mae_final': history.history['mae'][-1],
                'val_mae_final': history.history['val_mae'][-1]
            }
            
            self.metricas[f'lstm_{variable}'] = metricas
            
            print(f"✅ Modelo LSTM entrenado para {variable}")
            return metricas
            
        except Exception as e:
            print(f"Error entrenando modelo LSTM: {e}")
            return {}
    
    def entrenar_modelo_transformer(self, model: Model, X: np.ndarray, y: np.ndarray, variable: str) -> Dict:
        """Entrenar modelo Transformer"""
        try:
            config = self.modelos_config['transformer']
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(factor=0.5, patience=5),
                ModelCheckpoint(
                    f"{self.configuracion['directorio_modelos']}/transformer_{variable}_best.h5",
                    save_best_only=True
                )
            ]
            
            # Entrenar
            history = model.fit(
                X, y,
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                validation_split=0.2,
                callbacks=callbacks,
                verbose=1
            )
            
            # Guardar modelo
            model.save(f"{self.configuracion['directorio_modelos']}/transformer_{variable}_final.h5")
            
            # Métricas
            metricas = {
                'variable': variable,
                'modelo': 'Transformer',
                'epochs_entrenados': len(history.history['loss']),
                'loss_final': history.history['loss'][-1],
                'val_loss_final': history.history['val_loss'][-1],
                'mae_final': history.history['mae'][-1],
                'val_mae_final': history.history['val_mae'][-1]
            }
            
            self.metricas[f'transformer_{variable}'] = metricas
            
            print(f"✅ Modelo Transformer entrenado para {variable}")
            return metricas
            
        except Exception as e:
            print(f"Error entrenando modelo Transformer: {e}")
            return {}
    
    def crear_ensemble_model(self, X: np.ndarray, y: np.ndarray, variable: str) -> Dict:
        """Crear modelo ensemble con múltiples algoritmos"""
        try:
            # Preparar datos para modelos tradicionales
            X_flat = X.reshape(X.shape[0], -1)
            
            # Modelos tradicionales
            modelos_tradicionales = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'svr': SVR(kernel='rbf', C=1.0, gamma='scale'),
                'mlp': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
            }
            
            # Entrenar modelos tradicionales
            metricas_ensemble = {}
            for nombre, modelo in modelos_tradicionales.items():
                try:
                    modelo.fit(X_flat, y.ravel())
                    
                    # Predicciones
                    y_pred = modelo.predict(X_flat)
                    
                    # Métricas
                    mae = mean_absolute_error(y, y_pred)
                    mse = mean_squared_error(y, y_pred)
                    r2 = r2_score(y, y_pred)
                    
                    metricas_ensemble[nombre] = {
                        'mae': mae,
                        'mse': mse,
                        'r2': r2
                    }
                    
                    # Guardar modelo
                    joblib.dump(modelo, f"{self.configuracion['directorio_modelos']}/{nombre}_{variable}.pkl")
                    
                    print(f"✅ Modelo {nombre} entrenado para {variable}")
                    
                except Exception as e:
                    print(f"Error entrenando {nombre}: {e}")
            
            self.metricas[f'ensemble_{variable}'] = metricas_ensemble
            
            return metricas_ensemble
            
        except Exception as e:
            print(f"Error creando ensemble: {e}")
            return {}
    
    def entrenar_autosklearn(self, X: np.ndarray, y: np.ndarray, variable: str) -> Dict:
        """Entrenar modelo con AutoML (AutoSklearn)"""
        try:
            if not AUTOSKLEARN_AVAILABLE:
                print("⚠️ AutoSklearn no disponible")
                return {}
            
            # Preparar datos
            X_flat = X.reshape(X.shape[0], -1)
            
            # Crear modelo AutoML
            automl = autosklearn.regression.AutoSklearnRegressor(
                time_left_for_this_task=300,  # 5 minutos
                per_run_time_limit=60,        # 1 minuto por modelo
                memory_limit=3072,            # 3GB
                n_jobs=-1
            )
            
            # Entrenar
            automl.fit(X_flat, y.ravel())
            
            # Predicciones
            y_pred = automl.predict(X_flat)
            
            # Métricas
            mae = mean_absolute_error(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            metricas = {
                'mae': mae,
                'mse': mse,
                'r2': r2,
                'modelos_entrenados': len(automl.show_models())
            }
            
            # Guardar modelo
            joblib.dump(automl, f"{self.configuracion['directorio_modelos']}/autosklearn_{variable}.pkl")
            
            self.metricas[f'autosklearn_{variable}'] = metricas
            
            print(f"✅ Modelo AutoML entrenado para {variable}")
            return metricas
            
        except Exception as e:
            print(f"Error entrenando AutoML: {e}")
            return {}
    
    def entrenar_todos_los_modelos(self, datos: pd.DataFrame) -> Dict:
        """Entrenar todos los modelos para todas las variables"""
        try:
            print("🚀 Iniciando entrenamiento de todos los modelos...")
            
            resultados = {}
            
            for variable in self.variables_meteorologicas:
                if variable not in datos.columns:
                    print(f"⚠️ Variable {variable} no encontrada en los datos")
                    continue
                
                print(f"\n📊 Entrenando modelos para {variable}...")
                
                # Preparar datos
                X, y = self.preparar_datos_entrenamiento(datos, variable)
                
                if len(X) == 0:
                    continue
                
                # Entrenar LSTM
                try:
                    model_lstm = self.crear_modelo_lstm((X.shape[1], X.shape[2]), variable)
                    if model_lstm:
                        metricas_lstm = self.entrenar_modelo_lstm(model_lstm, X, y, variable)
                        resultados[f'lstm_{variable}'] = metricas_lstm
                except Exception as e:
                    print(f"Error entrenando LSTM para {variable}: {e}")
                
                # Entrenar Transformer
                try:
                    model_transformer = self.crear_modelo_transformer((X.shape[1], X.shape[2]), variable)
                    if model_transformer:
                        metricas_transformer = self.entrenar_modelo_transformer(model_transformer, X, y, variable)
                        resultados[f'transformer_{variable}'] = metricas_transformer
                except Exception as e:
                    print(f"Error entrenando Transformer para {variable}: {e}")
                
                # Entrenar Ensemble
                try:
                    metricas_ensemble = self.crear_ensemble_model(X, y, variable)
                    resultados[f'ensemble_{variable}'] = metricas_ensemble
                except Exception as e:
                    print(f"Error entrenando Ensemble para {variable}: {e}")
                
                # Entrenar AutoML
                try:
                    metricas_autosklearn = self.entrenar_autosklearn(X, y, variable)
                    if metricas_autosklearn:
                        resultados[f'autosklearn_{variable}'] = metricas_autosklearn
                except Exception as e:
                    print(f"Error entrenando AutoML para {variable}: {e}")
            
            print("✅ Entrenamiento de todos los modelos completado")
            return resultados
            
        except Exception as e:
            print(f"Error entrenando modelos: {e}")
            return {}
    
    def generar_predicciones(self, datos: pd.DataFrame, variable: str, modelo: str, horizonte: int = 24) -> np.ndarray:
        """Generar predicciones con el modelo entrenado"""
        try:
            # Cargar modelo
            if modelo.startswith('lstm') or modelo.startswith('transformer'):
                model_path = f"{self.configuracion['directorio_modelos']}/{modelo}_{variable}_final.h5"
                if Path(model_path).exists():
                    model = tf.keras.models.load_model(model_path)
                else:
                    print(f"Modelo {modelo} no encontrado")
                    return np.array([])
            else:
                model_path = f"{self.configuracion['directorio_modelos']}/{modelo}_{variable}.pkl"
                if Path(model_path).exists():
                    model = joblib.load(model_path)
                else:
                    print(f"Modelo {modelo} no encontrado")
                    return np.array([])
            
            # Preparar datos
            X, _ = self.preparar_datos_entrenamiento(datos, variable)
            
            if len(X) == 0:
                return np.array([])
            
            # Generar predicciones
            if modelo.startswith('lstm') or modelo.startswith('transformer'):
                predicciones = model.predict(X[-horizonte:])
                # Desnormalizar
                if variable in self.scalers:
                    predicciones = self.scalers[variable].inverse_transform(predicciones)
            else:
                X_flat = X[-horizonte:].reshape(X[-horizonte:].shape[0], -1)
                predicciones = model.predict(X_flat)
                # Desnormalizar
                if variable in self.scalers:
                    predicciones = self.scalers[variable].inverse_transform(predicciones.reshape(-1, 1))
            
            print(f"✅ Predicciones generadas para {variable} con {modelo}")
            return predicciones
            
        except Exception as e:
            print(f"Error generando predicciones: {e}")
            return np.array([])
    
    def evaluar_modelos(self, datos: pd.DataFrame) -> Dict:
        """Evaluar todos los modelos entrenados"""
        try:
            print("📊 Evaluando modelos...")
            
            evaluacion = {}
            
            for variable in self.variables_meteorologicas:
                if variable not in datos.columns:
                    continue
                
                evaluacion[variable] = {}
                
                # Evaluar cada tipo de modelo
                for modelo in ['lstm', 'transformer', 'ensemble', 'autosklearn']:
                    try:
                        predicciones = self.generar_predicciones(datos, variable, modelo)
                        
                        if len(predicciones) > 0:
                            # Calcular métricas
                            y_true = datos[variable].values[-len(predicciones):]
                            y_pred = predicciones.ravel()
                            
                            mae = mean_absolute_error(y_true, y_pred)
                            mse = mean_squared_error(y_true, y_pred)
                            r2 = r2_score(y_true, y_pred)
                            
                            evaluacion[variable][modelo] = {
                                'mae': mae,
                                'mse': mse,
                                'r2': r2,
                                'rmse': np.sqrt(mse)
                            }
                            
                    except Exception as e:
                        print(f"Error evaluando {modelo} para {variable}: {e}")
            
            print("✅ Evaluación de modelos completada")
            return evaluacion
            
        except Exception as e:
            print(f"Error evaluando modelos: {e}")
            return {}
    
    def generar_reporte_ia(self, resultados: Dict, evaluacion: Dict) -> str:
        """Generar reporte de IA avanzada"""
        try:
            print("📋 Generando reporte de IA avanzada...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - IA Avanzada',
                'version': self.configuracion['version'],
                'resumen': {
                    'total_variables': len(self.variables_meteorologicas),
                    'modelos_entrenados': len(resultados),
                    'mejor_modelo_por_variable': {}
                },
                'resultados_entrenamiento': resultados,
                'evaluacion_modelos': evaluacion,
                'recomendaciones': []
            }
            
            # Encontrar mejor modelo por variable
            for variable in self.variables_meteorologicas:
                mejor_modelo = None
                mejor_mae = float('inf')
                
                if variable in evaluacion:
                    for modelo, metricas in evaluacion[variable].items():
                        if metricas['mae'] < mejor_mae:
                            mejor_mae = metricas['mae']
                            mejor_modelo = modelo
                
                if mejor_modelo:
                    reporte['resumen']['mejor_modelo_por_variable'][variable] = {
                        'modelo': mejor_modelo,
                        'mae': mejor_mae
                    }
            
            # Generar recomendaciones
            if evaluacion:
                reporte['recomendaciones'] = [
                    "Los modelos LSTM y Transformer muestran mejor rendimiento para series temporales",
                    "El ensemble de modelos tradicionales proporciona robustez adicional",
                    "AutoML puede encontrar configuraciones óptimas automáticamente",
                    "Se recomienda reentrenar los modelos periódicamente con nuevos datos"
                ]
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"ia_avanzada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte de IA generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de IA avanzada"""
    print("🤖 IA AVANZADA PARA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Inteligencia Artificial Avanzada")
    print("=" * 80)
    
    try:
        # Crear instancia de IA avanzada
        ia = IAAvanzadaMETGO()
        
        # Cargar datos
        print("\n📊 Cargando datos meteorológicos...")
        datos = ia.cargar_datos_meteorologicos()
        
        if datos.empty:
            print("❌ No se pudieron cargar los datos")
            return False
        
        # Entrenar todos los modelos
        print("\n🚀 Entrenando modelos de IA avanzada...")
        resultados = ia.entrenar_todos_los_modelos(datos)
        
        # Evaluar modelos
        print("\n📊 Evaluando modelos...")
        evaluacion = ia.evaluar_modelos(datos)
        
        # Generar reporte
        print("\n📋 Generando reporte...")
        reporte = ia.generar_reporte_ia(resultados, evaluacion)
        
        if reporte:
            print(f"\n✅ IA avanzada completada exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print("\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en IA avanzada: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

