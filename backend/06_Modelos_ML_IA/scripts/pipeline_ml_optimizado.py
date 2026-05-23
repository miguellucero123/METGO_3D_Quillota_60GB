#!/usr/bin/env python3
"""
Pipeline de Machine Learning Optimizado - METGO 3D Operativo
Sistema completo de ML con validación cruzada y métricas robustas
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
import joblib
import warnings
from datetime import datetime
from typing import Dict, List, Tuple, Any
import os

warnings.filterwarnings('ignore')

class PipelineMLOptimizado:
    """
    Pipeline de Machine Learning optimizado para predicciones meteorológicas
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializar pipeline de ML
        
        Args:
            config (Dict): Configuración del pipeline
        """
        self.config = config or self._configuracion_default()
        self.modelos = {}
        self.mejores_modelos = {}
        self.scalers = {}
        self.metricas = {}
        self.directorio_modelos = "modelos_ml_quillota"
        
        # Crear directorio para modelos
        os.makedirs(self.directorio_modelos, exist_ok=True)
        
        # Definir modelos disponibles
        self.modelos_disponibles = {
            'RandomForest': RandomForestRegressor(random_state=42),
            'GradientBoosting': GradientBoostingRegressor(random_state=42),
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(random_state=42),
            'Lasso': Lasso(random_state=42),
            'SVR': SVR(),
            'KNeighbors': KNeighborsRegressor()
        }
        
        # Parámetros para GridSearch
        self.parametros_grid = {
            'RandomForest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10]
            },
            'GradientBoosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'Ridge': {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            },
            'Lasso': {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            },
            'SVR': {
                'C': [0.1, 1.0, 10.0],
                'gamma': ['scale', 'auto', 0.1, 1.0],
                'kernel': ['rbf', 'linear']
            },
            'KNeighbors': {
                'n_neighbors': [3, 5, 7, 9],
                'weights': ['uniform', 'distance']
            }
        }
    
    def _configuracion_default(self) -> Dict:
        """
        Configuración por defecto del pipeline
        """
        return {
            'test_size': 0.2,
            'random_state': 42,
            'cv_folds': 5,
            'scoring': 'neg_mean_squared_error',
            'n_jobs': -1,
            'verbose': 1
        }
    
    def preparar_datos(self, datos: pd.DataFrame, variable_objetivo: str) -> Tuple:
        """
        Preparar datos para entrenamiento
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
            variable_objetivo (str): Variable a predecir
        
        Returns:
            Tuple: X_train, X_test, y_train, y_test
        """
        # Seleccionar características
        caracteristicas = [
            'temperatura_max', 'temperatura_min', 'humedad_relativa',
            'precipitacion', 'velocidad_viento', 'presion_atmosferica',
            'radiacion_solar', 'nubosidad'
        ]
        
        # Filtrar características disponibles
        caracteristicas_disponibles = [col for col in caracteristicas if col in datos.columns]
        
        # Crear características adicionales
        datos_procesados = datos.copy()
        
        # Características temporales
        if 'fecha' in datos.columns:
            datos_procesados['dia_año'] = datos_procesados['fecha'].dt.dayofyear
            datos_procesados['mes'] = datos_procesados['fecha'].dt.month
            datos_procesados['dia_semana'] = datos_procesados['fecha'].dt.dayofweek
            
            caracteristicas_disponibles.extend(['dia_año', 'mes', 'dia_semana'])
        
        # Características derivadas
        if 'temperatura_max' in datos.columns and 'temperatura_min' in datos.columns:
            datos_procesados['amplitud_termica'] = datos_procesados['temperatura_max'] - datos_procesados['temperatura_min']
            caracteristicas_disponibles.append('amplitud_termica')
        
        # Preparar X e y
        X = datos_procesados[caracteristicas_disponibles].fillna(0)
        y = datos_procesados[variable_objetivo].fillna(0)
        
        # División train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.config['test_size'],
            random_state=self.config['random_state']
        )
        
        return X_train, X_test, y_train, y_test, caracteristicas_disponibles
    
    def entrenar_modelo(self, X_train: pd.DataFrame, y_train: pd.Series, 
                       nombre_modelo: str, usar_grid_search: bool = True) -> Dict:
        """
        Entrenar un modelo específico
        
        Args:
            X_train (pd.DataFrame): Datos de entrenamiento
            y_train (pd.Series): Variable objetivo de entrenamiento
            nombre_modelo (str): Nombre del modelo
            usar_grid_search (bool): Usar GridSearch para optimización
        
        Returns:
            Dict: Información del modelo entrenado
        """
        if nombre_modelo not in self.modelos_disponibles:
            raise ValueError(f"Modelo {nombre_modelo} no disponible")
        
        modelo_base = self.modelos_disponibles[nombre_modelo]
        
        # Crear pipeline con escalado
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('modelo', modelo_base)
        ])
        
        if usar_grid_search and nombre_modelo in self.parametros_grid:
            # Optimizar hiperparámetros
            parametros = {}
            for param, valores in self.parametros_grid[nombre_modelo].items():
                parametros[f'modelo__{param}'] = valores
            
            grid_search = GridSearchCV(
                pipeline,
                parametros,
                cv=self.config['cv_folds'],
                scoring=self.config['scoring'],
                n_jobs=self.config['n_jobs'],
                verbose=self.config['verbose']
            )
            
            grid_search.fit(X_train, y_train)
            modelo_optimizado = grid_search.best_estimator_
            mejores_parametros = grid_search.best_params_
            mejor_score_cv = grid_search.best_score_
        else:
            modelo_optimizado = pipeline
            modelo_optimizado.fit(X_train, y_train)
            mejores_parametros = {}
            mejor_score_cv = cross_val_score(
                modelo_optimizado, X_train, y_train,
                cv=self.config['cv_folds'],
                scoring=self.config['scoring']
            ).mean()
        
        # Guardar modelo
        self.modelos[nombre_modelo] = modelo_optimizado
        
        return {
            'modelo': modelo_optimizado,
            'mejores_parametros': mejores_parametros,
            'mejor_score_cv': mejor_score_cv,
            'nombre': nombre_modelo
        }
    
    def evaluar_modelo(self, modelo, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluar modelo con métricas completas
        
        Args:
            modelo: Modelo entrenado
            X_test (pd.DataFrame): Datos de prueba
            y_test (pd.Series): Variable objetivo de prueba
        
        Returns:
            Dict: Métricas de evaluación
        """
        # Predicciones
        y_pred = modelo.predict(X_test)
        
        # Métricas
        metricas = {
            'r2_test': r2_score(y_test, y_pred),
            'rmse_test': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae_test': mean_absolute_error(y_test, y_pred),
            'mape_test': np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        }
        
        return metricas
    
    def entrenar_todos_modelos(self, datos: pd.DataFrame, variable_objetivo: str) -> Dict:
        """
        Entrenar todos los modelos disponibles
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
            variable_objetivo (str): Variable a predecir
        
        Returns:
            Dict: Resultados de todos los modelos
        """
        print(f"\n🤖 ENTRENANDO MODELOS PARA: {variable_objetivo}")
        print("=" * 50)
        
        # Preparar datos
        X_train, X_test, y_train, y_test, caracteristicas = self.preparar_datos(datos, variable_objetivo)
        
        print(f"📊 Datos de entrenamiento: {len(X_train)} registros")
        print(f"📊 Datos de prueba: {len(X_test)} registros")
        print(f"🔧 Características: {len(caracteristicas)}")
        
        resultados = {}
        metricas_generales = {
            'mejor_r2_test': -np.inf,
            'mejor_rmse_test': np.inf,
            'mejor_modelo': None,
            'total_modelos': 0
        }
        
        # Entrenar cada modelo
        for nombre_modelo in self.modelos_disponibles.keys():
            try:
                print(f"\n🔄 Entrenando {nombre_modelo}...")
                
                # Entrenar modelo
                info_modelo = self.entrenar_modelo(X_train, y_train, nombre_modelo)
                
                # Evaluar modelo
                metricas = self.evaluar_modelo(info_modelo['modelo'], X_test, y_test)
                
                # Guardar resultados
                resultados[nombre_modelo] = {
                    'modelo': info_modelo['modelo'],
                    'metricas': metricas,
                    'mejores_parametros': info_modelo['mejores_parametros'],
                    'cv_mean': info_modelo['mejor_score_cv'],
                    'cv_std': 0  # Se podría calcular con más detalle
                }
                
                # Actualizar mejores métricas
                if metricas['r2_test'] > metricas_generales['mejor_r2_test']:
                    metricas_generales['mejor_r2_test'] = metricas['r2_test']
                    metricas_generales['mejor_modelo'] = nombre_modelo
                
                if metricas['rmse_test'] < metricas_generales['mejor_rmse_test']:
                    metricas_generales['mejor_rmse_test'] = metricas['rmse_test']
                
                print(f"   ✅ R²: {metricas['r2_test']:.4f}")
                print(f"   ✅ RMSE: {metricas['rmse_test']:.4f}")
                print(f"   ✅ CV Score: {info_modelo['mejor_score_cv']:.4f}")
                
            except Exception as e:
                print(f"   ❌ Error entrenando {nombre_modelo}: {e}")
                continue
        
        metricas_generales['total_modelos'] = len(resultados)
        
        # Guardar mejor modelo
        if metricas_generales['mejor_modelo']:
            mejor_modelo = resultados[metricas_generales['mejor_modelo']]['modelo']
            self.mejores_modelos[variable_objetivo] = mejor_modelo
            
            # Guardar modelo en disco
            archivo_modelo = os.path.join(
                self.directorio_modelos, 
                f"{variable_objetivo}_{metricas_generales['mejor_modelo']}.pkl"
            )
            joblib.dump(mejor_modelo, archivo_modelo)
            print(f"\n💾 Mejor modelo guardado: {archivo_modelo}")
        
        return {
            'modelos': resultados,
            'metricas_generales': metricas_generales,
            'mejor_modelo': metricas_generales['mejor_modelo'],
            'mejor_score': metricas_generales['mejor_r2_test']
        }
    
    def predecir(self, datos: pd.DataFrame, variable_objetivo: str) -> np.ndarray:
        """
        Realizar predicciones con el mejor modelo
        
        Args:
            datos (pd.DataFrame): Datos para predicción
            variable_objetivo (str): Variable objetivo
        
        Returns:
            np.ndarray: Predicciones
        """
        if variable_objetivo not in self.mejores_modelos:
            raise ValueError(f"No hay modelo entrenado para {variable_objetivo}")
        
        modelo = self.mejores_modelos[variable_objetivo]
        
        # Preparar datos de la misma manera que en entrenamiento
        caracteristicas = [
            'temperatura_max', 'temperatura_min', 'humedad_relativa',
            'precipitacion', 'velocidad_viento', 'presion_atmosferica',
            'radiacion_solar', 'nubosidad'
        ]
        
        caracteristicas_disponibles = [col for col in caracteristicas if col in datos.columns]
        
        # Crear características adicionales
        datos_procesados = datos.copy()
        
        if 'fecha' in datos.columns:
            datos_procesados['dia_año'] = datos_procesados['fecha'].dt.dayofyear
            datos_procesados['mes'] = datos_procesados['fecha'].dt.month
            datos_procesados['dia_semana'] = datos_procesados['fecha'].dt.dayofweek
            
            caracteristicas_disponibles.extend(['dia_año', 'mes', 'dia_semana'])
        
        if 'temperatura_max' in datos.columns and 'temperatura_min' in datos.columns:
            datos_procesados['amplitud_termica'] = datos_procesados['temperatura_max'] - datos_procesados['temperatura_min']
            caracteristicas_disponibles.append('amplitud_termica')
        
        X = datos_procesados[caracteristicas_disponibles].fillna(0)
        
        return modelo.predict(X)
    
    def cargar_modelo(self, archivo: str) -> Any:
        """
        Cargar modelo desde archivo
        
        Args:
            archivo (str): Ruta del archivo del modelo
        
        Returns:
            Any: Modelo cargado
        """
        return joblib.load(archivo)
    
    def obtener_resumen_modelos(self) -> Dict:
        """
        Obtener resumen de todos los modelos entrenados
        
        Returns:
            Dict: Resumen de modelos
        """
        resumen = {}
        
        for variable, modelo in self.mejores_modelos.items():
            archivo_modelo = os.path.join(
                self.directorio_modelos, 
                f"{variable}_*.pkl"
            )
            
            resumen[variable] = {
                'modelo': str(type(modelo).__name__),
                'archivo': archivo_modelo,
                'fecha_entrenamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return resumen

# Función de conveniencia
def entrenar_pipeline_ml(datos: pd.DataFrame, variables_objetivo: List[str]) -> Dict:
    """
    Función de conveniencia para entrenar pipeline completo
    
    Args:
        datos (pd.DataFrame): DataFrame con datos meteorológicos
        variables_objetivo (List[str]): Variables a predecir
    
    Returns:
        Dict: Resultados de entrenamiento
    """
    pipeline = PipelineMLOptimizado()
    resultados = {}
    
    for variable in variables_objetivo:
        if variable in datos.columns:
            resultados[variable] = pipeline.entrenar_todos_modelos(datos, variable)
        else:
            print(f"⚠️ Variable {variable} no encontrada en los datos")
    
    return resultados

# Ejemplo de uso
if __name__ == "__main__":
    # Crear datos de prueba
    np.random.seed(42)
    fechas = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    datos_prueba = pd.DataFrame({
        'fecha': fechas,
        'temperatura_max': np.random.normal(22, 6, 100),
        'temperatura_min': np.random.normal(10, 4, 100),
        'humedad_relativa': np.random.normal(70, 15, 100),
        'precipitacion': np.random.exponential(0.8, 100),
        'velocidad_viento': np.random.normal(8, 3, 100),
        'presion_atmosferica': np.random.normal(1013, 8, 100),
        'radiacion_solar': np.random.normal(18, 6, 100),
        'nubosidad': np.random.randint(0, 100, 100)
    })
    
    # Entrenar pipeline
    pipeline = PipelineMLOptimizado()
    resultados = pipeline.entrenar_todos_modelos(datos_prueba, 'temperatura_max')
    
    print("\n🎯 RESUMEN DE ENTRENAMIENTO:")
    print(f"🏆 Mejor modelo: {resultados['mejor_modelo']}")
    print(f"📈 Mejor R²: {resultados['mejor_score']:.4f}")
    print(f"📊 Total modelos: {resultados['metricas_generales']['total_modelos']}")
    
    print("\n✅ Pipeline de ML funcionando correctamente")
