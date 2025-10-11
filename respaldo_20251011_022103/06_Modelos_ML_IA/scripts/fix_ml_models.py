#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX ML MODELS - METGO 3D
Correccion de modelos de Machine Learning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import logging

class MLModelsFixer:
    """Corrector de modelos de ML para METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('ML_FIXER')
        self.models_dir = 'modelos_ml_quillota'
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Configuracion de modelos
        self.models_config = {
            'temperatura_max': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['dia_año', 'hora', 'humedad', 'presion', 'viento_velocidad']
            },
            'temperatura_min': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['dia_año', 'hora', 'humedad', 'presion', 'viento_velocidad']
            },
            'precipitacion': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['dia_año', 'hora', 'humedad', 'presion', 'temperatura_max']
            },
            'humedad': {
                'model': LinearRegression(),
                'features': ['dia_año', 'hora', 'temperatura_max', 'temperatura_min', 'presion']
            },
            'presion': {
                'model': SVR(kernel='rbf', C=1.0, gamma='scale'),
                'features': ['dia_año', 'hora', 'temperatura_max', 'temperatura_min', 'humedad']
            }
        }
    
    def generar_datos_entrenamiento(self, n_dias=365):
        """Generar datos sinteticos para entrenar modelos"""
        try:
            # Generar fechas
            fecha_inicio = datetime.now() - timedelta(days=n_dias)
            fechas = [fecha_inicio + timedelta(days=i) for i in range(n_dias)]
            
            datos = []
            for fecha in fechas:
                for hora in range(24):
                    # Variables base
                    dia_año = fecha.timetuple().tm_yday
                    
                    # Patrones estacionales
                    temp_base = 15 + 10 * np.sin(2 * np.pi * dia_año / 365)
                    humedad_base = 60 + 20 * np.cos(2 * np.pi * dia_año / 365)
                    presion_base = 1013 + 10 * np.sin(2 * np.pi * dia_año / 365)
                    
                    # Variacion horaria
                    temp_hora = temp_base + 5 * np.sin(2 * np.pi * hora / 24)
                    humedad_hora = humedad_base + 10 * np.cos(2 * np.pi * hora / 24)
                    
                    # Ruido aleatorio
                    ruido = np.random.normal(0, 1, 5)
                    
                    # Calcular variables dependientes
                    temp_max = temp_hora + 5 + ruido[0]
                    temp_min = temp_hora - 5 + ruido[1]
                    humedad = max(0, min(100, humedad_hora + ruido[2]))
                    presion = presion_base + ruido[3]
                    viento_velocidad = max(0, 5 + ruido[4])
                    
                    # Precipitacion (probabilistica)
                    prob_lluvia = 0.1 + 0.2 * np.sin(2 * np.pi * dia_año / 365)
                    precipitacion = np.random.exponential(2) if np.random.random() < prob_lluvia else 0
                    
                    datos.append({
                        'fecha': fecha,
                        'hora': hora,
                        'dia_año': dia_año,
                        'temperatura_max': round(temp_max, 1),
                        'temperatura_min': round(temp_min, 1),
                        'humedad': round(humedad, 1),
                        'presion': round(presion, 1),
                        'viento_velocidad': round(viento_velocidad, 1),
                        'precipitacion': round(precipitacion, 1)
                    })
            
            return pd.DataFrame(datos)
            
        except Exception as e:
            self.logger.error(f"Error generando datos de entrenamiento: {e}")
            return pd.DataFrame()
    
    def entrenar_modelo(self, variable, datos):
        """Entrenar modelo para una variable especifica"""
        try:
            config = self.models_config[variable]
            features = config['features']
            
            # Preparar datos
            X = datos[features].values
            y = datos[variable].values
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Entrenar modelo
            modelo = config['model']
            modelo.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = modelo.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Guardar modelo
            modelo_path = os.path.join(self.models_dir, f'modelo_{variable}.joblib')
            joblib.dump(modelo, modelo_path)
            
            self.logger.info(f"Modelo {variable} entrenado - MSE: {mse:.3f}, R2: {r2:.3f}")
            
            return {
                'variable': variable,
                'mse': mse,
                'r2': r2,
                'modelo_path': modelo_path,
                'features': features
            }
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelo {variable}: {e}")
            return None
    
    def entrenar_todos_los_modelos(self):
        """Entrenar todos los modelos de ML"""
        try:
            self.logger.info("Generando datos de entrenamiento...")
            datos = self.generar_datos_entrenamiento(365)
            
            if datos.empty:
                return {'error': 'No se pudieron generar datos de entrenamiento'}
            
            self.logger.info(f"Datos generados: {len(datos)} registros")
            
            resultados = {}
            
            for variable in self.models_config.keys():
                self.logger.info(f"Entrenando modelo para {variable}...")
                resultado = self.entrenar_modelo(variable, datos)
                if resultado:
                    resultados[variable] = resultado
            
            # Guardar configuracion de modelos
            config_path = os.path.join(self.models_dir, 'configuracion_modelos.json')
            import json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Modelos entrenados: {len(resultados)}")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelos: {e}")
            return {'error': str(e)}
    
    def cargar_modelo(self, variable):
        """Cargar modelo entrenado"""
        try:
            modelo_path = os.path.join(self.models_dir, f'modelo_{variable}.joblib')
            if os.path.exists(modelo_path):
                modelo = joblib.load(modelo_path)
                return modelo
            else:
                self.logger.warning(f"Modelo {variable} no encontrado")
                return None
        except Exception as e:
            self.logger.error(f"Error cargando modelo {variable}: {e}")
            return None
    
    def predecir(self, variable, features_dict):
        """Hacer prediccion con modelo entrenado"""
        try:
            modelo = self.cargar_modelo(variable)
            if modelo is None:
                return {'error': f'Modelo {variable} no disponible'}
            
            config = self.models_config[variable]
            features = config['features']
            
            # Preparar features
            X = np.array([features_dict.get(f, 0) for f in features]).reshape(1, -1)
            
            # Predecir
            prediccion = modelo.predict(X)[0]
            
            return {
                'variable': variable,
                'prediccion': round(prediccion, 2),
                'features_usadas': features,
                'features_valores': features_dict
            }
            
        except Exception as e:
            self.logger.error(f"Error prediciendo {variable}: {e}")
            return {'error': str(e)}

def main():
    """Funcion principal para corregir modelos ML"""
    print("CORRECCION DE MODELOS ML - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear corrector
        fixer = MLModelsFixer()
        
        # Entrenar todos los modelos
        print("\n1. Entrenando modelos de ML...")
        resultados = fixer.entrenar_todos_los_modelos()
        
        if 'error' in resultados:
            print(f"   Error: {resultados['error']}")
            return False
        
        print(f"   Modelos entrenados: {len(resultados)}")
        
        # Mostrar resultados
        for variable, info in resultados.items():
            print(f"   - {variable}: MSE={info['mse']:.3f}, R2={info['r2']:.3f}")
        
        # Probar predicciones
        print("\n2. Probando predicciones...")
        features_test = {
            'dia_año': 150,
            'hora': 12,
            'humedad': 65,
            'presion': 1013,
            'viento_velocidad': 10,
            'temperatura_max': 25,
            'temperatura_min': 15
        }
        
        for variable in ['temperatura_max', 'temperatura_min', 'precipitacion']:
            prediccion = fixer.predecir(variable, features_test)
            if 'error' not in prediccion:
                print(f"   {variable}: {prediccion['prediccion']}")
            else:
                print(f"   {variable}: Error - {prediccion['error']}")
        
        print("\nModelos ML corregidos exitosamente")
        return True
        
    except Exception as e:
        print(f"\nError corrigiendo modelos ML: {e}")
        return False

if __name__ == "__main__":
    main()
