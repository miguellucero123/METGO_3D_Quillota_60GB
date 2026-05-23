"""
SISTEMA DE PREDICCIONES ML AVANZADO - METGO 3D QUILLOTA
Sistema de Machine Learning para predicciones meteorológicas y agrícolas
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json
import logging
from datetime import datetime, timedelta
import sqlite3
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SistemaPrediccionesMLAvanzado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "predicciones_ml_metgo.db"
        self.modelos_dir = "modelos_ml"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos = {}
        self.scalers = {}
        self.label_encoders = {}
        
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        if not os.path.exists(self.modelos_dir):
            os.makedirs(self.modelos_dir)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para predicciones"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de predicciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacion TEXT NOT NULL,
                    variable TEXT NOT NULL,
                    valor_predicho REAL NOT NULL,
                    confianza REAL NOT NULL,
                    horizonte_horas INTEGER NOT NULL,
                    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_predicha TIMESTAMP NOT NULL,
                    modelo_usado TEXT NOT NULL,
                    metrica_r2 REAL,
                    metrica_rmse REAL
                )
            ''')
            
            # Tabla de historial de entrenamiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_entrenamiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modelo TEXT NOT NULL,
                    variable TEXT NOT NULL,
                    fecha_entrenamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    datos_entrenamiento INTEGER,
                    r2_score REAL,
                    rmse REAL,
                    mae REAL,
                    tiempo_entrenamiento REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Base de datos de predicciones ML inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def cargar_datos_historicos(self) -> pd.DataFrame:
        """Cargar datos históricos para entrenamiento"""
        try:
            # Intentar cargar desde base de datos meteorológica
            conn = sqlite3.connect("datos_meteorologicos_reales.db")
            
            query = '''
                SELECT fecha, estacion, temperatura_actual, humedad_relativa, 
                       velocidad_viento, precipitacion, presion_atmosferica, nubosidad
                FROM datos_meteorologicos
                ORDER BY fecha DESC
                LIMIT 1000
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) == 0:
                # Si no hay datos históricos, generar datos sintéticos
                self.logger.info("Generando datos sintéticos para entrenamiento")
                df = self._generar_datos_sinteticos()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos: {e}")
            return self._generar_datos_sinteticos()
    
    def _generar_datos_sinteticos(self, n_dias: int = 30) -> pd.DataFrame:
        """Generar datos sintéticos para entrenamiento"""
        try:
            fecha_inicio = datetime.now() - timedelta(days=n_dias)
            fechas = pd.date_range(fecha_inicio, periods=n_dias*24, freq='H')
            
            estaciones = [
                "Quillota_Centro", "La_Cruz", "Nogales", 
                "San_Isidro", "Pocochay", "Valle_Hermoso"
            ]
            
            datos = []
            
            for fecha in fechas:
                for estacion in estaciones:
                    # Generar datos realistas para Quillota
                    temp_base = 15 + 10 * np.sin(2 * np.pi * fecha.hour / 24)
                    temp_variacion = np.random.normal(0, 3)
                    temperatura = temp_base + temp_variacion
                    
                    humedad = max(30, min(95, 70 + np.random.normal(0, 15)))
                    viento = max(0, np.random.exponential(8))
                    precipitacion = np.random.exponential(0.5) if np.random.random() < 0.1 else 0
                    presion = 1013 + np.random.normal(0, 10)
                    nubosidad = max(0, min(100, np.random.normal(50, 20)))
                    
                    datos.append({
                        'fecha': fecha,
                        'estacion': estacion,
                        'temperatura_actual': round(temperatura, 1),
                        'humedad_relativa': round(humedad, 1),
                        'velocidad_viento': round(viento, 1),
                        'precipitacion': round(precipitacion, 2),
                        'presion_atmosferica': round(presion, 1),
                        'nubosidad': round(nubosidad, 1)
                    })
            
            return pd.DataFrame(datos)
            
        except Exception as e:
            self.logger.error(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def preparar_datos_entrenamiento(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos para entrenamiento"""
        try:
            # Crear características temporales
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['hora'] = df['fecha'].dt.hour
            df['dia_semana'] = df['fecha'].dt.dayofweek
            df['dia_año'] = df['fecha'].dt.dayofyear
            
            # Codificar estación
            if 'estacion' in df.columns:
                le_estacion = LabelEncoder()
                df['estacion_encoded'] = le_estacion.fit_transform(df['estacion'])
                self.label_encoders[f'estacion_{variable_objetivo}'] = le_estacion
            
            # Seleccionar características
            caracteristicas = [
                'hora', 'dia_semana', 'dia_año', 'estacion_encoded',
                'temperatura_actual', 'humedad_relativa', 'velocidad_viento',
                'precipitacion', 'presion_atmosferica', 'nubosidad'
            ]
            
            # Verificar que todas las características existan
            caracteristicas_disponibles = [col for col in caracteristicas if col in df.columns]
            
            X = df[caracteristicas_disponibles].fillna(0).values
            y = df[variable_objetivo].fillna(0).values
            
            # Normalizar características
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers[variable_objetivo] = scaler
            
            return X_scaled, y
            
        except Exception as e:
            self.logger.error(f"Error preparando datos de entrenamiento: {e}")
            return np.array([]), np.array([])
    
    def entrenar_modelos(self, variable_objetivo: str) -> Dict:
        """Entrenar múltiples modelos para una variable"""
        try:
            # Cargar datos
            df = self.cargar_datos_historicos()
            if len(df) == 0:
                raise ValueError("No hay datos para entrenamiento")
            
            # Preparar datos
            X, y = self.preparar_datos_entrenamiento(df, variable_objetivo)
            if len(X) == 0:
                raise ValueError("Error preparando datos")
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Definir modelos
            modelos = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'LinearRegression': LinearRegression(),
                'Ridge': Ridge(alpha=1.0)
            }
            
            resultados = {}
            
            for nombre, modelo in modelos.items():
                try:
                    # Entrenar modelo
                    inicio = datetime.now()
                    modelo.fit(X_train, y_train)
                    tiempo_entrenamiento = (datetime.now() - inicio).total_seconds()
                    
                    # Evaluar modelo
                    y_pred = modelo.predict(X_test)
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    # Guardar modelo
                    modelo_path = os.path.join(self.modelos_dir, f"{nombre}_{variable_objetivo}.joblib")
                    joblib.dump(modelo, modelo_path)
                    
                    resultados[nombre] = {
                        'modelo': modelo,
                        'r2_score': r2,
                        'rmse': rmse,
                        'mae': mae,
                        'tiempo_entrenamiento': tiempo_entrenamiento,
                        'ruta_modelo': modelo_path
                    }
                    
                    # Guardar en base de datos
                    self._guardar_historial_entrenamiento(
                        nombre, variable_objetivo, len(X_train), r2, rmse, mae, tiempo_entrenamiento
                    )
                    
                    self.logger.info(f"Modelo {nombre} entrenado para {variable_objetivo}: R2={r2:.3f}, RMSE={rmse:.3f}")
                    
                except Exception as e:
                    self.logger.error(f"Error entrenando modelo {nombre}: {e}")
            
            # Seleccionar mejor modelo
            mejor_modelo = max(resultados.keys(), key=lambda x: resultados[x]['r2_score'])
            self.modelos[variable_objetivo] = resultados[mejor_modelo]
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelos para {variable_objetivo}: {e}")
            return {}
    
    def _guardar_historial_entrenamiento(self, modelo: str, variable: str, datos: int, 
                                       r2: float, rmse: float, mae: float, tiempo: float):
        """Guardar historial de entrenamiento en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO historial_entrenamiento 
                (modelo, variable, datos_entrenamiento, r2_score, rmse, mae, tiempo_entrenamiento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (modelo, variable, datos, r2, rmse, mae, tiempo))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando historial: {e}")
    
    def predecir_variable(self, variable: str, datos_actuales: Dict, 
                         horizonte_horas: int = 24) -> Dict:
        """Predecir una variable meteorológica"""
        try:
            # Verificar si el modelo está entrenado
            if variable not in self.modelos:
                self.logger.info(f"Entrenando modelos para {variable}")
                self.entrenar_modelos(variable)
            
            if variable not in self.modelos:
                raise ValueError(f"No se pudo entrenar modelo para {variable}")
            
            modelo_info = self.modelos[variable]
            modelo = modelo_info['modelo']
            scaler = self.scalers[variable]
            
            # Preparar datos para predicción
            datos_prediccion = self._preparar_datos_prediccion(datos_actuales, variable)
            datos_scaled = scaler.transform([datos_prediccion])
            
            # Realizar predicción
            prediccion = modelo.predict(datos_scaled)[0]
            
            # Calcular confianza basada en R2 score
            confianza = max(0, min(1, modelo_info['r2_score']))
            
            # Calcular fecha predicha
            fecha_predicha = datetime.now() + timedelta(hours=horizonte_horas)
            
            # Guardar predicción
            self._guardar_prediccion(
                datos_actuales.get('estacion', 'Unknown'),
                variable, prediccion, confianza, horizonte_horas, 
                fecha_predicha, modelo_info['ruta_modelo'], 
                modelo_info['r2_score'], modelo_info['rmse']
            )
            
            return {
                'variable': variable,
                'valor_predicho': round(prediccion, 2),
                'confianza': round(confianza, 3),
                'horizonte_horas': horizonte_horas,
                'fecha_predicha': fecha_predicha,
                'modelo_usado': modelo_info['ruta_modelo'],
                'r2_score': modelo_info['r2_score'],
                'rmse': modelo_info['rmse']
            }
            
        except Exception as e:
            self.logger.error(f"Error prediciendo {variable}: {e}")
            return {}
    
    def _preparar_datos_prediccion(self, datos_actuales: Dict, variable: str) -> List[float]:
        """Preparar datos actuales para predicción"""
        try:
            ahora = datetime.now()
            
            # Codificar estación si existe
            estacion_encoded = 0
            if 'estacion' in datos_actuales and f'estacion_{variable}' in self.label_encoders:
                le = self.label_encoders[f'estacion_{variable}']
                estacion_encoded = le.transform([datos_actuales['estacion']])[0]
            
            # Crear vector de características
            caracteristicas = [
                ahora.hour,
                ahora.weekday(),
                ahora.timetuple().tm_yday,
                estacion_encoded,
                datos_actuales.get('temperatura_actual', 15.0),
                datos_actuales.get('humedad_relativa', 60.0),
                datos_actuales.get('velocidad_viento', 5.0),
                datos_actuales.get('precipitacion', 0.0),
                datos_actuales.get('presion_atmosferica', 1013.0),
                datos_actuales.get('nubosidad', 50.0)
            ]
            
            return caracteristicas
            
        except Exception as e:
            self.logger.error(f"Error preparando datos de predicción: {e}")
            return [0] * 10  # Vector por defecto
    
    def _guardar_prediccion(self, estacion: str, variable: str, valor: float, 
                          confianza: float, horizonte: int, fecha_predicha: datetime,
                          modelo: str, r2: float, rmse: float):
        """Guardar predicción en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predicciones 
                (estacion, variable, valor_predicho, confianza, horizonte_horas, 
                 fecha_predicha, modelo_usado, metrica_r2, metrica_rmse)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (estacion, variable, valor, confianza, horizonte, 
                  fecha_predicha, modelo, r2, rmse))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando predicción: {e}")
    
    def obtener_predicciones_estacion(self, estacion: str, horas: int = 24) -> List[Dict]:
        """Obtener predicciones para una estación específica"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predicciones 
                WHERE estacion = ? AND fecha_predicha >= datetime('now')
                ORDER BY fecha_predicha
                LIMIT ?
            ''', (estacion, horas))
            
            columnas = [desc[0] for desc in cursor.description]
            predicciones = []
            
            for row in cursor.fetchall():
                prediccion = dict(zip(columnas, row))
                predicciones.append(prediccion)
            
            conn.close()
            return predicciones
            
        except Exception as e:
            self.logger.error(f"Error obteniendo predicciones: {e}")
            return []
    
    def generar_predicciones_completas(self, datos_actuales: Dict) -> Dict:
        """Generar predicciones para todas las variables"""
        try:
            variables = [
                'temperatura_actual',
                'humedad_relativa', 
                'velocidad_viento',
                'precipitacion',
                'presion_atmosferica',
                'nubosidad'
            ]
            
            predicciones = {}
            
            for variable in variables:
                try:
                    pred = self.predecir_variable(variable, datos_actuales, 24)
                    if pred:
                        predicciones[variable] = pred
                except Exception as e:
                    self.logger.error(f"Error prediciendo {variable}: {e}")
            
            return predicciones
            
        except Exception as e:
            self.logger.error(f"Error generando predicciones completas: {e}")
            return {}
    
    def obtener_metricas_modelos(self) -> Dict:
        """Obtener métricas de todos los modelos entrenados"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT modelo, variable, r2_score, rmse, mae, fecha_entrenamiento
                FROM historial_entrenamiento
                ORDER BY fecha_entrenamiento DESC
            ''')
            
            metricas = {}
            for row in cursor.fetchall():
                modelo, variable, r2, rmse, mae, fecha = row
                
                if variable not in metricas:
                    metricas[variable] = {}
                
                metricas[variable][modelo] = {
                    'r2_score': r2,
                    'rmse': rmse,
                    'mae': mae,
                    'fecha_entrenamiento': fecha
                }
            
            conn.close()
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            return {}

def main():
    """Función principal para pruebas"""
    logging.basicConfig(level=logging.INFO)
    
    sistema = SistemaPrediccionesMLAvanzado()
    
    # Datos de prueba
    datos_prueba = {
        'estacion': 'Quillota_Centro',
        'temperatura_actual': 15.5,
        'humedad_relativa': 65.0,
        'velocidad_viento': 8.2,
        'precipitacion': 0.0,
        'presion_atmosferica': 1013.2,
        'nubosidad': 30.0
    }
    
    print("Probando sistema de predicciones ML...")
    
    # Generar predicciones
    predicciones = sistema.generar_predicciones_completas(datos_prueba)
    
    print(f"Predicciones generadas: {len(predicciones)}")
    for variable, pred in predicciones.items():
        print(f"{variable}: {pred['valor_predicho']} (confianza: {pred['confianza']:.3f})")

if __name__ == "__main__":
    main()
