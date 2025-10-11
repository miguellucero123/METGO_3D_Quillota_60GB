#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 DEEP LEARNING AVANZADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Modelos de Deep Learning Avanzados
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import sqlite3
from dataclasses import dataclass
import yaml

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Conv1D, MaxPooling1D, Flatten, Embedding, MultiHeadAttention, LayerNormalization, GlobalAveragePooling1D
    from tensorflow.keras.optimizers import Adam, RMSprop
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.neural_network import MLPRegressor, MLPClassifier
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class ModeloDeepLearning:
    """Configuración de modelo de deep learning"""
    nombre: str
    tipo: str
    arquitectura: Dict[str, Any]
    hiperparametros: Dict[str, Any]
    metricas: Dict[str, float]
    entrenado: bool = False
    metadata: Dict[str, Any] = None

class DeepLearningAvanzadoMETGO:
    """Sistema de deep learning avanzado para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/deep_learning',
            'directorio_modelos': 'modelos/deep_learning',
            'directorio_logs': 'logs/deep_learning',
            'directorio_reportes': 'reportes/deep_learning',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Verificar disponibilidad de librerías
        self._verificar_dependencias()
        
        # Modelos disponibles
        self.modelos = {}
        self.datos_entrenamiento = None
        self.datos_validacion = None
        
        # Configuración de modelos
        self.configuracion_modelos = {
            'habilitar_tensorflow': TENSORFLOW_AVAILABLE,
            'habilitar_pytorch': PYTORCH_AVAILABLE,
            'habilitar_sklearn': SKLEARN_AVAILABLE,
            'epochs_default': 100,
            'batch_size_default': 32,
            'learning_rate_default': 0.001,
            'validation_split': 0.2
        }
        
        # Base de datos
        self._inicializar_base_datos()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/deep_learning.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_DEEP_LEARNING')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _verificar_dependencias(self):
        """Verificar dependencias de deep learning"""
        try:
            self.logger.info("Verificando dependencias de deep learning...")
            
            dependencias = {
                'TensorFlow': TENSORFLOW_AVAILABLE,
                'PyTorch': PYTORCH_AVAILABLE,
                'Scikit-learn': SKLEARN_AVAILABLE
            }
            
            for lib, disponible in dependencias.items():
                if disponible:
                    self.logger.info(f"{lib} disponible")
                else:
                    self.logger.warning(f"{lib} no disponible")
            
            if not any(dependencias.values()):
                self.logger.error("Ninguna librería de deep learning disponible")
            
        except Exception as e:
            self.logger.error(f"Error verificando dependencias: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/deep_learning.db"
            
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
            
            # Crear tablas
            self._crear_tablas_bd()
            
            self.logger.info(f"Base de datos inicializada: {archivo_bd}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _crear_tablas_bd(self):
        """Crear tablas en la base de datos"""
        try:
            # Tabla de modelos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS modelos_deep_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    arquitectura TEXT NOT NULL,
                    hiperparametros TEXT NOT NULL,
                    metricas TEXT NOT NULL,
                    entrenado BOOLEAN DEFAULT FALSE,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de entrenamientos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS entrenamientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo_id INTEGER NOT NULL,
                    epoch INTEGER NOT NULL,
                    loss REAL NOT NULL,
                    val_loss REAL NOT NULL,
                    accuracy REAL,
                    val_accuracy REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_modelos_nombre ON modelos_deep_learning(nombre)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_entrenamientos_modelo ON entrenamientos(modelo_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def generar_datos_sinteticos(self, n_muestras: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """Generar datos sintéticos para entrenamiento"""
        try:
            self.logger.info(f"Generando {n_muestras} muestras sintéticas...")
            
            # Generar características meteorológicas
            np.random.seed(42)
            
            # Características de entrada (temperatura, humedad, presión, viento, etc.)
            X = np.random.randn(n_muestras, 10)
            
            # Normalizar características
            X[:, 0] = 15 + 10 * X[:, 0]  # Temperatura (5-25°C)
            X[:, 1] = 60 + 30 * X[:, 1]  # Humedad (30-90%)
            X[:, 2] = 1013 + 20 * X[:, 2]  # Presión (993-1033 hPa)
            X[:, 3] = 5 + 15 * X[:, 3]  # Velocidad viento (0-20 m/s)
            X[:, 4] = 0 + 100 * X[:, 4]  # Precipitación (0-100 mm)
            
            # Variables adicionales
            X[:, 5] = np.random.randint(0, 24, n_muestras)  # Hora del día
            X[:, 6] = np.random.randint(1, 13, n_muestras)  # Mes
            X[:, 7] = np.random.randint(0, 7, n_muestras)  # Día de la semana
            X[:, 8] = np.random.randint(0, 365, n_muestras)  # Día del año
            X[:, 9] = np.random.randn(n_muestras)  # Variable adicional
            
            # Generar objetivo (predicción de temperatura futura)
            y = 0.7 * X[:, 0] + 0.1 * X[:, 1] + 0.05 * X[:, 2] + 0.05 * X[:, 3] + 0.1 * np.random.randn(n_muestras)
            
            # Agregar ruido
            y += np.random.randn(n_muestras) * 0.5
            
            self.logger.info(f"Datos sintéticos generados: X={X.shape}, y={y.shape}")
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return np.array([]), np.array([])
    
    def preparar_datos(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento"""
        try:
            self.logger.info("Preparando datos para entrenamiento...")
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar características
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
            
            X_train_scaled = scaler_X.fit_transform(X_train)
            X_test_scaled = scaler_X.transform(X_test)
            y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
            y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).ravel()
            
            self.datos_entrenamiento = (X_train_scaled, y_train_scaled)
            self.datos_validacion = (X_test_scaled, y_test_scaled)
            self.scalers = {'X': scaler_X, 'y': scaler_y}
            
            self.logger.info(f"Datos preparados: Train={X_train_scaled.shape}, Test={X_test_scaled.shape}")
            return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled
            
        except Exception as e:
            self.logger.error(f"Error preparando datos: {e}")
            return np.array([]), np.array([]), np.array([]), np.array([])
    
    def crear_modelo_lstm_avanzado(self) -> Optional[Any]:
        """Crear modelo LSTM avanzado con TensorFlow"""
        try:
            if not TENSORFLOW_AVAILABLE:
                self.logger.warning("TensorFlow no disponible")
                return None
            
            self.logger.info("Creando modelo LSTM avanzado...")
            
            # Preparar datos para LSTM (secuencias temporales)
            X_train, y_train = self.datos_entrenamiento
            X_test, y_test = self.datos_validacion
            
            # Reshape para LSTM (muestras, timesteps, características)
            timesteps = 24  # 24 horas
            features = X_train.shape[1]
            
            # Crear secuencias
            X_train_seq = self._crear_secuencias(X_train, timesteps)
            y_train_seq = y_train[timesteps:]
            X_test_seq = self._crear_secuencias(X_test, timesteps)
            y_test_seq = y_test[timesteps:]
            
            # Crear modelo LSTM
            model = Sequential([
                LSTM(128, return_sequences=True, input_shape=(timesteps, features)),
                Dropout(0.2),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dropout(0.2),
                Dense(1, activation='linear')
            ])
            
            # Compilar modelo
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Callbacks
            callbacks_list = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5),
                ModelCheckpoint(
                    f"{self.configuracion['directorio_modelos']}/lstm_avanzado_best.h5",
                    monitor='val_loss',
                    save_best_only=True
                )
            ]
            
            # Entrenar modelo
            history = model.fit(
                X_train_seq, y_train_seq,
                validation_data=(X_test_seq, y_test_seq),
                epochs=self.configuracion_modelos['epochs_default'],
                batch_size=self.configuracion_modelos['batch_size_default'],
                callbacks=callbacks_list,
                verbose=1
            )
            
            # Evaluar modelo
            train_loss = model.evaluate(X_train_seq, y_train_seq, verbose=0)
            test_loss = model.evaluate(X_test_seq, y_test_seq, verbose=0)
            
            # Guardar modelo
            model.save(f"{self.configuracion['directorio_modelos']}/lstm_avanzado_final.h5")
            
            # Crear objeto de modelo
            modelo = ModeloDeepLearning(
                nombre="LSTM_Avanzado",
                tipo="LSTM",
                arquitectura={
                    'capas': ['LSTM(128)', 'Dropout(0.2)', 'LSTM(64)', 'Dropout(0.2)', 'LSTM(32)', 'Dropout(0.2)', 'Dense(16)', 'Dropout(0.2)', 'Dense(1)'],
                    'timesteps': timesteps,
                    'features': features
                },
                hiperparametros={
                    'epochs': len(history.history['loss']),
                    'batch_size': self.configuracion_modelos['batch_size_default'],
                    'learning_rate': 0.001,
                    'optimizer': 'Adam'
                },
                metricas={
                    'train_loss': train_loss[0],
                    'test_loss': test_loss[0],
                    'train_mae': train_loss[1],
                    'test_mae': test_loss[1]
                },
                entrenado=True,
                metadata={'history': history.history}
            )
            
            self.modelos['LSTM_Avanzado'] = modelo
            self._guardar_modelo(modelo)
            
            self.logger.info("Modelo LSTM avanzado creado y entrenado exitosamente")
            return model
            
        except Exception as e:
            self.logger.error(f"Error creando modelo LSTM avanzado: {e}")
            return None
    
    def crear_modelo_transformer(self) -> Optional[Any]:
        """Crear modelo Transformer avanzado"""
        try:
            if not TENSORFLOW_AVAILABLE:
                self.logger.warning("TensorFlow no disponible")
                return None
            
            self.logger.info("Creando modelo Transformer avanzado...")
            
            # Preparar datos
            X_train, y_train = self.datos_entrenamiento
            X_test, y_test = self.datos_validacion
            
            # Reshape para Transformer
            timesteps = 24
            features = X_train.shape[1]
            
            X_train_seq = self._crear_secuencias(X_train, timesteps)
            y_train_seq = y_train[timesteps:]
            X_test_seq = self._crear_secuencias(X_test, timesteps)
            y_test_seq = y_test[timesteps:]
            
            # Crear modelo Transformer
            inputs = keras.Input(shape=(timesteps, features))
            
            # Embedding
            x = Dense(64)(inputs)
            
            # Multi-head attention
            attention_output = MultiHeadAttention(num_heads=8, key_dim=64)(x, x)
            x = LayerNormalization(epsilon=1e-6)(x + attention_output)
            
            # Feed forward
            ffn = Sequential([
                Dense(128, activation='relu'),
                Dense(64)
            ])
            ffn_output = ffn(x)
            x = LayerNormalization(epsilon=1e-6)(x + ffn_output)
            
            # Global average pooling
            x = GlobalAveragePooling1D()(x)
            
            # Output layers
            x = Dense(32, activation='relu')(x)
            x = Dropout(0.2)(x)
            outputs = Dense(1, activation='linear')(x)
            
            model = Model(inputs, outputs)
            
            # Compilar modelo
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Callbacks
            callbacks_list = [
                EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
            ]
            
            # Entrenar modelo
            history = model.fit(
                X_train_seq, y_train_seq,
                validation_data=(X_test_seq, y_test_seq),
                epochs=self.configuracion_modelos['epochs_default'],
                batch_size=self.configuracion_modelos['batch_size_default'],
                callbacks=callbacks_list,
                verbose=1
            )
            
            # Evaluar modelo
            train_loss = model.evaluate(X_train_seq, y_train_seq, verbose=0)
            test_loss = model.evaluate(X_test_seq, y_test_seq, verbose=0)
            
            # Guardar modelo
            model.save(f"{self.configuracion['directorio_modelos']}/transformer_avanzado.h5")
            
            # Crear objeto de modelo
            modelo = ModeloDeepLearning(
                nombre="Transformer_Avanzado",
                tipo="Transformer",
                arquitectura={
                    'capas': ['Dense(64)', 'MultiHeadAttention(8)', 'LayerNormalization', 'Dense(128)', 'Dense(64)', 'GlobalAveragePooling1D', 'Dense(32)', 'Dense(1)'],
                    'timesteps': timesteps,
                    'features': features,
                    'num_heads': 8
                },
                hiperparametros={
                    'epochs': len(history.history['loss']),
                    'batch_size': self.configuracion_modelos['batch_size_default'],
                    'learning_rate': 0.001,
                    'optimizer': 'Adam'
                },
                metricas={
                    'train_loss': train_loss[0],
                    'test_loss': test_loss[0],
                    'train_mae': train_loss[1],
                    'test_mae': test_loss[1]
                },
                entrenado=True,
                metadata={'history': history.history}
            )
            
            self.modelos['Transformer_Avanzado'] = modelo
            self._guardar_modelo(modelo)
            
            self.logger.info("Modelo Transformer avanzado creado y entrenado exitosamente")
            return model
            
        except Exception as e:
            self.logger.error(f"Error creando modelo Transformer: {e}")
            return None
    
    def crear_modelo_cnn_1d(self) -> Optional[Any]:
        """Crear modelo CNN 1D para series temporales"""
        try:
            if not TENSORFLOW_AVAILABLE:
                self.logger.warning("TensorFlow no disponible")
                return None
            
            self.logger.info("Creando modelo CNN 1D...")
            
            # Preparar datos
            X_train, y_train = self.datos_entrenamiento
            X_test, y_test = self.datos_validacion
            
            # Reshape para CNN 1D
            timesteps = 24
            features = X_train.shape[1]
            
            X_train_seq = self._crear_secuencias(X_train, timesteps)
            y_train_seq = y_train[timesteps:]
            X_test_seq = self._crear_secuencias(X_test, timesteps)
            y_test_seq = y_test[timesteps:]
            
            # Crear modelo CNN 1D
            model = Sequential([
                Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(timesteps, features)),
                MaxPooling1D(pool_size=2),
                Conv1D(filters=32, kernel_size=3, activation='relu'),
                MaxPooling1D(pool_size=2),
                Flatten(),
                Dense(50, activation='relu'),
                Dropout(0.2),
                Dense(1, activation='linear')
            ])
            
            # Compilar modelo
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Callbacks
            callbacks_list = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
            ]
            
            # Entrenar modelo
            history = model.fit(
                X_train_seq, y_train_seq,
                validation_data=(X_test_seq, y_test_seq),
                epochs=self.configuracion_modelos['epochs_default'],
                batch_size=self.configuracion_modelos['batch_size_default'],
                callbacks=callbacks_list,
                verbose=1
            )
            
            # Evaluar modelo
            train_loss = model.evaluate(X_train_seq, y_train_seq, verbose=0)
            test_loss = model.evaluate(X_test_seq, y_test_seq, verbose=0)
            
            # Guardar modelo
            model.save(f"{self.configuracion['directorio_modelos']}/cnn_1d_avanzado.h5")
            
            # Crear objeto de modelo
            modelo = ModeloDeepLearning(
                nombre="CNN_1D_Avanzado",
                tipo="CNN_1D",
                arquitectura={
                    'capas': ['Conv1D(64)', 'MaxPooling1D(2)', 'Conv1D(32)', 'MaxPooling1D(2)', 'Flatten', 'Dense(50)', 'Dropout(0.2)', 'Dense(1)'],
                    'timesteps': timesteps,
                    'features': features
                },
                hiperparametros={
                    'epochs': len(history.history['loss']),
                    'batch_size': self.configuracion_modelos['batch_size_default'],
                    'learning_rate': 0.001,
                    'optimizer': 'Adam'
                },
                metricas={
                    'train_loss': train_loss[0],
                    'test_loss': test_loss[0],
                    'train_mae': train_loss[1],
                    'test_mae': test_loss[1]
                },
                entrenado=True,
                metadata={'history': history.history}
            )
            
            self.modelos['CNN_1D_Avanzado'] = modelo
            self._guardar_modelo(modelo)
            
            self.logger.info("Modelo CNN 1D avanzado creado y entrenado exitosamente")
            return model
            
        except Exception as e:
            self.logger.error(f"Error creando modelo CNN 1D: {e}")
            return None
    
    def crear_modelo_ensemble(self) -> Optional[Dict[str, Any]]:
        """Crear modelo ensemble combinando múltiples modelos"""
        try:
            self.logger.info("Creando modelo ensemble...")
            
            if not SKLEARN_AVAILABLE:
                self.logger.warning("Scikit-learn no disponible")
                return None
            
            # Preparar datos
            X_train, y_train = self.datos_entrenamiento
            X_test, y_test = self.datos_validacion
            
            # Crear múltiples modelos
            modelos_ensemble = {}
            
            # MLP Regressor 1
            mlp1 = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=1000,
                random_state=42
            )
            mlp1.fit(X_train, y_train)
            modelos_ensemble['MLP_1'] = mlp1
            
            # MLP Regressor 2
            mlp2 = MLPRegressor(
                hidden_layer_sizes=(200, 100, 50),
                activation='tanh',
                solver='adam',
                alpha=0.0001,
                learning_rate='adaptive',
                max_iter=1000,
                random_state=123
            )
            mlp2.fit(X_train, y_train)
            modelos_ensemble['MLP_2'] = mlp2
            
            # MLP Regressor 3
            mlp3 = MLPRegressor(
                hidden_layer_sizes=(150, 75),
                activation='relu',
                solver='lbfgs',
                alpha=0.01,
                max_iter=1000,
                random_state=456
            )
            mlp3.fit(X_train, y_train)
            modelos_ensemble['MLP_3'] = mlp3
            
            # Hacer predicciones
            pred_train = {}
            pred_test = {}
            
            for nombre, modelo in modelos_ensemble.items():
                pred_train[nombre] = modelo.predict(X_train)
                pred_test[nombre] = modelo.predict(X_test)
            
            # Ensemble simple (promedio)
            ensemble_train = np.mean(list(pred_train.values()), axis=0)
            ensemble_test = np.mean(list(pred_test.values()), axis=0)
            
            # Calcular métricas
            train_mse = mean_squared_error(y_train, ensemble_train)
            test_mse = mean_squared_error(y_test, ensemble_test)
            train_r2 = r2_score(y_train, ensemble_train)
            test_r2 = r2_score(y_test, ensemble_test)
            
            # Crear objeto de modelo
            modelo = ModeloDeepLearning(
                nombre="Ensemble_Avanzado",
                tipo="Ensemble",
                arquitectura={
                    'modelos': list(modelos_ensemble.keys()),
                    'metodo': 'promedio',
                    'n_modelos': len(modelos_ensemble)
                },
                hiperparametros={
                    'MLP_1': {'hidden_layers': (100, 50), 'activation': 'relu', 'solver': 'adam'},
                    'MLP_2': {'hidden_layers': (200, 100, 50), 'activation': 'tanh', 'solver': 'adam'},
                    'MLP_3': {'hidden_layers': (150, 75), 'activation': 'relu', 'solver': 'lbfgs'}
                },
                metricas={
                    'train_mse': train_mse,
                    'test_mse': test_mse,
                    'train_r2': train_r2,
                    'test_r2': test_r2
                },
                entrenado=True,
                metadata={'modelos': list(modelos_ensemble.keys())}
            )
            
            self.modelos['Ensemble_Avanzado'] = modelo
            self._guardar_modelo(modelo)
            
            self.logger.info("Modelo ensemble avanzado creado y entrenado exitosamente")
            return {
                'modelos': modelos_ensemble,
                'predicciones_train': pred_train,
                'predicciones_test': pred_test,
                'ensemble_train': ensemble_train,
                'ensemble_test': ensemble_test,
                'metricas': {
                    'train_mse': train_mse,
                    'test_mse': test_mse,
                    'train_r2': train_r2,
                    'test_r2': test_r2
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creando modelo ensemble: {e}")
            return None
    
    def _crear_secuencias(self, datos: np.ndarray, timesteps: int) -> np.ndarray:
        """Crear secuencias para modelos de series temporales"""
        try:
            secuencias = []
            for i in range(timesteps, len(datos)):
                secuencias.append(datos[i-timesteps:i])
            return np.array(secuencias)
        except Exception as e:
            self.logger.error(f"Error creando secuencias: {e}")
            return np.array([])
    
    def _guardar_modelo(self, modelo: ModeloDeepLearning):
        """Guardar modelo en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO modelos_deep_learning 
                (nombre, tipo, arquitectura, hiperparametros, metricas, entrenado, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                modelo.nombre,
                modelo.tipo,
                json.dumps(modelo.arquitectura),
                json.dumps(modelo.hiperparametros),
                json.dumps(modelo.metricas),
                modelo.entrenado,
                json.dumps(modelo.metadata) if modelo.metadata else None
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo: {e}")
    
    def entrenar_todos_los_modelos(self) -> Dict[str, Any]:
        """Entrenar todos los modelos de deep learning"""
        try:
            self.logger.info("Iniciando entrenamiento de todos los modelos...")
            
            inicio = time.time()
            resultados = {}
            
            # Generar datos sintéticos
            X, y = self.generar_datos_sinteticos(10000)
            if X.size == 0:
                return {'exitoso': False, 'error': 'Error generando datos'}
            
            # Preparar datos
            X_train, X_test, y_train, y_test = self.preparar_datos(X, y)
            if X_train.size == 0:
                return {'exitoso': False, 'error': 'Error preparando datos'}
            
            # Entrenar modelos
            modelos_entrenados = {}
            
            # LSTM Avanzado
            if TENSORFLOW_AVAILABLE:
                try:
                    modelo_lstm = self.crear_modelo_lstm_avanzado()
                    if modelo_lstm:
                        modelos_entrenados['LSTM'] = modelo_lstm
                        resultados['LSTM'] = 'exitoso'
                    else:
                        resultados['LSTM'] = 'fallido'
                except Exception as e:
                    self.logger.error(f"Error entrenando LSTM: {e}")
                    resultados['LSTM'] = f'error: {e}'
            
            # Transformer
            if TENSORFLOW_AVAILABLE:
                try:
                    modelo_transformer = self.crear_modelo_transformer()
                    if modelo_transformer:
                        modelos_entrenados['Transformer'] = modelo_transformer
                        resultados['Transformer'] = 'exitoso'
                    else:
                        resultados['Transformer'] = 'fallido'
                except Exception as e:
                    self.logger.error(f"Error entrenando Transformer: {e}")
                    resultados['Transformer'] = f'error: {e}'
            
            # CNN 1D
            if TENSORFLOW_AVAILABLE:
                try:
                    modelo_cnn = self.crear_modelo_cnn_1d()
                    if modelo_cnn:
                        modelos_entrenados['CNN_1D'] = modelo_cnn
                        resultados['CNN_1D'] = 'exitoso'
                    else:
                        resultados['CNN_1D'] = 'fallido'
                except Exception as e:
                    self.logger.error(f"Error entrenando CNN 1D: {e}")
                    resultados['CNN_1D'] = f'error: {e}'
            
            # Ensemble
            if SKLEARN_AVAILABLE:
                try:
                    modelo_ensemble = self.crear_modelo_ensemble()
                    if modelo_ensemble:
                        modelos_entrenados['Ensemble'] = modelo_ensemble
                        resultados['Ensemble'] = 'exitoso'
                    else:
                        resultados['Ensemble'] = 'fallido'
                except Exception as e:
                    self.logger.error(f"Error entrenando Ensemble: {e}")
                    resultados['Ensemble'] = f'error: {e}'
            
            duracion = time.time() - inicio
            
            # Calcular estadísticas
            modelos_exitosos = sum(1 for r in resultados.values() if r == 'exitoso')
            modelos_fallidos = sum(1 for r in resultados.values() if r == 'fallido')
            modelos_con_error = sum(1 for r in resultados.values() if isinstance(r, str) and r.startswith('error'))
            
            resultados_finales = {
                'exitoso': True,
                'duracion': duracion,
                'modelos_entrenados': modelos_exitosos,
                'modelos_fallidos': modelos_fallidos,
                'modelos_con_error': modelos_con_error,
                'resultados': resultados,
                'modelos_disponibles': list(modelos_entrenados.keys()),
                'configuracion': self.configuracion_modelos
            }
            
            self.logger.info(f"Entrenamiento completado en {duracion:.2f} segundos")
            self.logger.info(f"Modelos exitosos: {modelos_exitosos}, Fallidos: {modelos_fallidos}, Con error: {modelos_con_error}")
            
            return resultados_finales
            
        except Exception as e:
            self.logger.error(f"Error entrenando todos los modelos: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_deep_learning(self) -> str:
        """Generar reporte de deep learning"""
        try:
            self.logger.info("Generando reporte de deep learning...")
            
            # Entrenar todos los modelos
            resultados = self.entrenar_todos_los_modelos()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Deep Learning Avanzado',
                'version': self.configuracion['version'],
                'resultados': resultados,
                'modelos': {
                    nombre: {
                        'tipo': modelo.tipo,
                        'entrenado': modelo.entrenado,
                        'metricas': modelo.metricas,
                        'hiperparametros': modelo.hiperparametros
                    } for nombre, modelo in self.modelos.items()
                },
                'configuracion': self.configuracion_modelos,
                'recomendaciones': [
                    "Implementar transfer learning con modelos pre-entrenados",
                    "Agregar más datos de entrenamiento reales",
                    "Implementar early stopping y regularization",
                    "Optimizar hiperparámetros con GridSearch o RandomSearch",
                    "Implementar cross-validation para mejor evaluación",
                    "Agregar modelos de ensemble más sofisticados",
                    "Implementar modelos de attention mechanism",
                    "Agregar soporte para PyTorch",
                    "Implementar modelos de GAN para generación de datos",
                    "Agregar visualización de arquitecturas de modelos"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"deep_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de deep learning generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de deep learning avanzado"""
    print("DEEP LEARNING AVANZADO METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Modelos de Deep Learning Avanzados")
    print("=" * 80)
    
    try:
        # Crear sistema de deep learning
        dl_sistema = DeepLearningAvanzadoMETGO()
        
        # Entrenar todos los modelos
        print(f"\nEntrenando modelos de deep learning...")
        resultados = dl_sistema.entrenar_todos_los_modelos()
        
        if resultados.get('exitoso'):
            print(f"Entrenamiento completado exitosamente")
            print(f"Duracion: {resultados.get('duracion', 0):.2f} segundos")
            
            # Mostrar resultados
            print(f"\nModelos entrenados: {resultados.get('modelos_entrenados', 0)}")
            print(f"Modelos fallidos: {resultados.get('modelos_fallidos', 0)}")
            print(f"Modelos con error: {resultados.get('modelos_con_error', 0)}")
            
            # Mostrar modelos disponibles
            modelos_disponibles = resultados.get('modelos_disponibles', [])
            if modelos_disponibles:
                print(f"\nModelos disponibles:")
                for modelo in modelos_disponibles:
                    print(f"   - {modelo}")
            
            # Mostrar configuración
            config = resultados.get('configuracion', {})
            print(f"\nConfiguracion:")
            print(f"   TensorFlow: {'Disponible' if config.get('habilitar_tensorflow') else 'No disponible'}")
            print(f"   PyTorch: {'Disponible' if config.get('habilitar_pytorch') else 'No disponible'}")
            print(f"   Scikit-learn: {'Disponible' if config.get('habilitar_sklearn') else 'No disponible'}")
        else:
            print(f"Error en entrenamiento: {resultados.get('error', 'Error desconocido')}")
        
        # Generar reporte
        print(f"\nGenerando reporte...")
        reporte = dl_sistema.generar_reporte_deep_learning()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        return resultados.get('exitoso', False)
        
    except Exception as e:
        print(f"\nError en deep learning avanzado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
