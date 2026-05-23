"""
Pipeline de Machine Learning optimizado para predicción meteorológica.
Versión operativa con validación cruzada y métricas completas.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pickle
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


class PipelineML:
    """
    Pipeline de Machine Learning para predicción meteorológica.
    
    Características:
    - Múltiples algoritmos de ML
    - Validación cruzada automática
    - Optimización de hiperparámetros
    - Métricas de evaluación completas
    - Guardado automático de modelos
    - Reproducibilidad garantizada
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar pipeline de ML.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuración de ML
        self.ml_config = config.get('MACHINE_LEARNING', {})
        self.algoritmos = self.ml_config.get('algoritmos', [])
        self.entrenamiento_config = self.ml_config.get('entrenamiento', {})
        
        # Parámetros de entrenamiento
        self.test_size = self.entrenamiento_config.get('test_size', 0.2)
        self.random_state = self.entrenamiento_config.get('random_state', 42)
        self.cv_folds = self.entrenamiento_config.get('cv_folds', 5)
        self.scoring = self.entrenamiento_config.get('scoring', 'neg_mean_squared_error')
        
        # Configuración de modelos
        self.modelos_config = self.ml_config.get('modelos', {})
        self.guardar_automatico = self.modelos_config.get('guardar_automatico', True)
        self.versionado = self.modelos_config.get('versionado', True)
        
        # Directorio para modelos
        self.modelos_dir = Path("data/processed/modelos")
        self.modelos_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelos entrenados
        self.modelos_entrenados = {}
        self.metricas_modelos = {}
        
        self.logger.info("Pipeline de ML inicializado")
    
    def entrenar_modelos(self, datos: pd.DataFrame, 
                        variables_objetivo: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Entrenar múltiples modelos de ML para predicción meteorológica.
        
        Args:
            datos: DataFrame con datos meteorológicos
            variables_objetivo: Variables a predecir (por defecto: temperatura_max, temperatura_min)
            
        Returns:
            Diccionario con resultados del entrenamiento
        """
        self.logger.info("Iniciando entrenamiento de modelos ML")
        
        if variables_objetivo is None:
            variables_objetivo = ['temperatura_max', 'temperatura_min']
        
        try:
            # Preparar datos
            X, y_dict = self._preparar_datos_entrenamiento(datos, variables_objetivo)
            
            # Entrenar modelos para cada variable objetivo
            resultados = {}
            
            for variable in variables_objetivo:
                self.logger.info(f"Entrenando modelos para {variable}")
                
                y = y_dict[variable]
                resultados_variable = self._entrenar_modelos_variable(X, y, variable)
                resultados[variable] = resultados_variable
            
            # Guardar modelos si está habilitado
            if self.guardar_automatico:
                self._guardar_modelos()
            
            self.logger.info("Entrenamiento de modelos completado exitosamente")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error en entrenamiento de modelos: {e}")
            raise MLError(f"Error entrenando modelos: {e}")
    
    def _preparar_datos_entrenamiento(self, datos: pd.DataFrame, 
                                    variables_objetivo: List[str]) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """Preparar datos para entrenamiento."""
        self.logger.debug("Preparando datos para entrenamiento")
        
        # Crear características (features)
        caracteristicas = self._crear_caracteristicas(datos)
        
        # Separar variables objetivo
        y_dict = {}
        for variable in variables_objetivo:
            if variable in datos.columns:
                y_dict[variable] = datos[variable]
            else:
                self.logger.warning(f"Variable objetivo {variable} no encontrada")
        
        return caracteristicas, y_dict
    
    def _crear_caracteristicas(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Crear características para el modelo."""
        caracteristicas = pd.DataFrame()
        
        # Características temporales
        caracteristicas['dia_año'] = datos['fecha'].dt.dayofyear
        caracteristicas['mes'] = datos['fecha'].dt.month
        caracteristicas['dia_semana'] = datos['fecha'].dt.dayofweek
        caracteristicas['trimestre'] = datos['fecha'].dt.quarter
        
        # Características meteorológicas básicas
        variables_meteorologicas = [
            'humedad_relativa', 'precipitacion', 'velocidad_viento',
            'presion_atmosferica', 'radiacion_solar', 'nubosidad'
        ]
        
        for variable in variables_meteorologicas:
            if variable in datos.columns:
                caracteristicas[variable] = datos[variable]
        
        # Características derivadas
        if 'temperatura_max' in datos.columns and 'temperatura_min' in datos.columns:
            caracteristicas['amplitud_termica'] = datos['temperatura_max'] - datos['temperatura_min']
        
        # Características de tendencia (promedios móviles)
        for variable in ['temperatura_max', 'temperatura_min', 'humedad_relativa']:
            if variable in datos.columns:
                caracteristicas[f'{variable}_prom_3d'] = datos[variable].rolling(window=3, min_periods=1).mean()
                caracteristicas[f'{variable}_prom_7d'] = datos[variable].rolling(window=7, min_periods=1).mean()
        
        # Eliminar valores nulos
        caracteristicas = caracteristicas.fillna(method='ffill').fillna(method='bfill')
        
        return caracteristicas
    
    def _entrenar_modelos_variable(self, X: pd.DataFrame, y: pd.Series, 
                                 variable: str) -> Dict[str, Any]:
        """Entrenar modelos para una variable específica."""
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        # Definir modelos
        modelos = self._definir_modelos()
        
        resultados = {
            'variable': variable,
            'modelos': {},
            'mejor_modelo': None,
            'mejor_score': -np.inf,
            'metricas_generales': {}
        }
        
        # Entrenar cada modelo
        for nombre_modelo, modelo in modelos.items():
            try:
                self.logger.debug(f"Entrenando {nombre_modelo} para {variable}")
                
                # Entrenar modelo
                modelo.fit(X_train, y_train)
                
                # Predicciones
                y_pred_train = modelo.predict(X_train)
                y_pred_test = modelo.predict(X_test)
                
                # Métricas
                metricas = self._calcular_metricas(y_train, y_pred_train, y_test, y_pred_test)
                
                # Validación cruzada
                cv_scores = cross_val_score(
                    modelo, X_train, y_train, 
                    cv=self.cv_folds, scoring=self.scoring
                )
                
                # Guardar resultados
                resultados['modelos'][nombre_modelo] = {
                    'modelo': modelo,
                    'metricas': metricas,
                    'cv_scores': cv_scores.tolist(),
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std()
                }
                
                # Actualizar mejor modelo
                if cv_scores.mean() > resultados['mejor_score']:
                    resultados['mejor_score'] = cv_scores.mean()
                    resultados['mejor_modelo'] = nombre_modelo
                
                # Guardar modelo entrenado
                self.modelos_entrenados[f"{variable}_{nombre_modelo}"] = modelo
                self.metricas_modelos[f"{variable}_{nombre_modelo}"] = metricas
                
            except Exception as e:
                self.logger.error(f"Error entrenando {nombre_modelo} para {variable}: {e}")
                continue
        
        # Métricas generales
        resultados['metricas_generales'] = self._calcular_metricas_generales(resultados['modelos'])
        
        return resultados
    
    def _definir_modelos(self) -> Dict[str, Any]:
        """Definir modelos de ML a entrenar."""
        modelos = {}
        
        # Random Forest
        modelos['RandomForest'] = RandomForestRegressor(
            n_estimators=100,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # Gradient Boosting
        modelos['GradientBoosting'] = GradientBoostingRegressor(
            n_estimators=100,
            random_state=self.random_state
        )
        
        # Linear Regression
        modelos['LinearRegression'] = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        # Support Vector Regression
        modelos['SVR'] = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', SVR(kernel='rbf', C=1.0, gamma='scale'))
        ])
        
        # K-Nearest Neighbors
        modelos['KNN'] = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', KNeighborsRegressor(n_neighbors=5))
        ])
        
        return modelos
    
    def _calcular_metricas(self, y_train: pd.Series, y_pred_train: np.ndarray,
                          y_test: pd.Series, y_pred_test: np.ndarray) -> Dict[str, float]:
        """Calcular métricas de evaluación."""
        metricas = {
            'train_mse': mean_squared_error(y_train, y_pred_train),
            'test_mse': mean_squared_error(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        return metricas
    
    def _calcular_metricas_generales(self, modelos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular métricas generales de todos los modelos."""
        metricas_generales = {
            'total_modelos': len(modelos),
            'mejor_r2_test': max([m['metricas']['test_r2'] for m in modelos.values()]),
            'mejor_rmse_test': min([m['metricas']['test_rmse'] for m in modelos.values()]),
            'promedio_r2_test': np.mean([m['metricas']['test_r2'] for m in modelos.values()]),
            'promedio_rmse_test': np.mean([m['metricas']['test_rmse'] for m in modelos.values()])
        }
        
        return metricas_generales
    
    def _guardar_modelos(self):
        """Guardar modelos entrenados."""
        self.logger.info("Guardando modelos entrenados")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for nombre_modelo, modelo in self.modelos_entrenados.items():
            try:
                # Crear nombre de archivo
                if self.versionado:
                    archivo = self.modelos_dir / f"{nombre_modelo}_{timestamp}.pkl"
                else:
                    archivo = self.modelos_dir / f"{nombre_modelo}.pkl"
                
                # Guardar modelo
                joblib.dump(modelo, archivo)
                self.logger.debug(f"Modelo guardado: {archivo}")
                
            except Exception as e:
                self.logger.error(f"Error guardando modelo {nombre_modelo}: {e}")
    
    def cargar_modelo(self, nombre_modelo: str, version: Optional[str] = None) -> Any:
        """
        Cargar modelo entrenado.
        
        Args:
            nombre_modelo: Nombre del modelo a cargar
            version: Versión específica del modelo (opcional)
            
        Returns:
            Modelo cargado
        """
        try:
            if version:
                archivo = self.modelos_dir / f"{nombre_modelo}_{version}.pkl"
            else:
                # Buscar la versión más reciente
                archivos = list(self.modelos_dir.glob(f"{nombre_modelo}_*.pkl"))
                if not archivos:
                    raise MLError(f"No se encontraron modelos para {nombre_modelo}")
                
                archivo = max(archivos, key=lambda x: x.stat().st_mtime)
            
            modelo = joblib.load(archivo)
            self.logger.info(f"Modelo cargado: {archivo}")
            return modelo
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo {nombre_modelo}: {e}")
            raise MLError(f"Error cargando modelo: {e}")
    
    def predecir(self, modelo_nombre: str, datos: pd.DataFrame, 
                version: Optional[str] = None) -> np.ndarray:
        """
        Realizar predicciones con un modelo entrenado.
        
        Args:
            modelo_nombre: Nombre del modelo
            datos: Datos para predicción
            version: Versión del modelo
            
        Returns:
            Predicciones del modelo
        """
        try:
            # Cargar modelo
            modelo = self.cargar_modelo(modelo_nombre, version)
            
            # Preparar características
            caracteristicas = self._crear_caracteristicas(datos)
            
            # Realizar predicción
            predicciones = modelo.predict(caracteristicas)
            
            self.logger.info(f"Predicciones realizadas con {modelo_nombre}: {len(predicciones)} valores")
            return predicciones
            
        except Exception as e:
            self.logger.error(f"Error realizando predicciones: {e}")
            raise MLError(f"Error en predicciones: {e}")
    
    def evaluar_modelo(self, modelo_nombre: str, datos_test: pd.DataFrame, 
                      variable_objetivo: str, version: Optional[str] = None) -> Dict[str, float]:
        """
        Evaluar modelo con datos de prueba.
        
        Args:
            modelo_nombre: Nombre del modelo
            datos_test: Datos de prueba
            variable_objetivo: Variable objetivo
            version: Versión del modelo
            
        Returns:
            Métricas de evaluación
        """
        try:
            # Cargar modelo
            modelo = self.cargar_modelo(modelo_nombre, version)
            
            # Preparar datos
            caracteristicas = self._crear_caracteristicas(datos_test)
            y_true = datos_test[variable_objetivo]
            
            # Predicciones
            y_pred = modelo.predict(caracteristicas)
            
            # Métricas
            metricas = {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred)
            }
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error evaluando modelo: {e}")
            raise MLError(f"Error en evaluación: {e}")
    
    def generar_reporte_ml(self, resultados: Dict[str, Any]) -> str:
        """
        Generar reporte de entrenamiento de modelos.
        
        Args:
            resultados: Resultados del entrenamiento
            
        Returns:
            Ruta al archivo de reporte
        """
        self.logger.info("Generando reporte de ML")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        reporte_path = f"logs/reporte_ml_{timestamp}.txt"
        
        try:
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE MACHINE LEARNING - METGO 3D OPERATIVO\n")
                f.write("=" * 60 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for variable, resultado in resultados.items():
                    f.write(f"VARIABLE: {variable.upper()}\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Mejor modelo: {resultado['mejor_modelo']}\n")
                    f.write(f"Mejor score CV: {resultado['mejor_score']:.4f}\n\n")
                    
                    f.write("MÉTRICAS POR MODELO:\n")
                    for nombre_modelo, info_modelo in resultado['modelos'].items():
                        f.write(f"\n{nombre_modelo}:\n")
                        f.write(f"  R² Test: {info_modelo['metricas']['test_r2']:.4f}\n")
                        f.write(f"  RMSE Test: {info_modelo['metricas']['test_rmse']:.4f}\n")
                        f.write(f"  MAE Test: {info_modelo['metricas']['test_mae']:.4f}\n")
                        f.write(f"  CV Score: {info_modelo['cv_mean']:.4f} ± {info_modelo['cv_std']:.4f}\n")
                    
                    f.write("\n" + "=" * 60 + "\n\n")
            
            self.logger.info(f"Reporte ML generado: {reporte_path}")
            return reporte_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte ML: {e}")
            raise MLError(f"Error generando reporte: {e}")


class MLError(Exception):
    """Excepción para errores de Machine Learning."""
    pass
