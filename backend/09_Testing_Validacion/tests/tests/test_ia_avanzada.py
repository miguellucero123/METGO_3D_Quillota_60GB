#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTS UNITARIOS - IA AVANZADA METGO 3D
Sistema Meteorológico Agrícola Quillota - Testing de IA Avanzada
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ia_avanzada_metgo import IAAvanzadaMETGO
    IA_AVAILABLE = True
except ImportError:
    IA_AVAILABLE = False

class TestIAAvanzadaMETGO(unittest.TestCase):
    """Tests unitarios para el módulo de IA Avanzada"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not IA_AVAILABLE:
            raise unittest.SkipTest("Módulo de IA Avanzada no disponible")
        
        cls.ia = IAAvanzadaMETGO()
        cls.datos_test = cls._generar_datos_test()
    
    @classmethod
    def _generar_datos_test(cls):
        """Generar datos de prueba"""
        fechas = pd.date_range(
            start='2023-01-01',
            end='2023-01-31',
            freq='H'
        )
        
        np.random.seed(42)
        datos = pd.DataFrame(index=fechas)
        datos['temperatura'] = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
        datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, np.random.exponential(0.5, len(fechas)), 0)
        datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
        datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
        datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
        datos['humedad'] = np.clip(datos['humedad'], 0, 100)
        datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
        datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
        datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
        
        return datos
    
    def test_inicializacion(self):
        """Test de inicialización del módulo"""
        self.assertIsNotNone(self.ia)
        self.assertIsInstance(self.ia.configuracion, dict)
        self.assertIn('version', self.ia.configuracion)
        self.assertEqual(self.ia.configuracion['version'], '2.0')
    
    def test_cargar_datos_meteorologicos(self):
        """Test de carga de datos meteorológicos"""
        datos = self.ia.cargar_datos_meteorologicos()
        self.assertIsInstance(datos, pd.DataFrame)
        self.assertGreater(len(datos), 0)
        
        # Verificar columnas esperadas
        columnas_esperadas = ['temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion', 'humedad', 'presion', 'radiacion_solar', 'punto_rocio']
        for columna in columnas_esperadas:
            self.assertIn(columna, datos.columns)
    
    def test_generar_datos_sinteticos(self):
        """Test de generación de datos sintéticos"""
        datos = self.ia._generar_datos_sinteticos()
        self.assertIsInstance(datos, pd.DataFrame)
        self.assertGreater(len(datos), 0)
        
        # Verificar que no hay valores NaN
        self.assertFalse(datos.isnull().any().any())
        
        # Verificar rangos de valores
        self.assertTrue((datos['temperatura'] >= -10).all())
        self.assertTrue((datos['temperatura'] <= 50).all())
        self.assertTrue((datos['humedad'] >= 0).all())
        self.assertTrue((datos['humedad'] <= 100).all())
        self.assertTrue((datos['precipitacion'] >= 0).all())
    
    def test_preparar_datos_entrenamiento(self):
        """Test de preparación de datos para entrenamiento"""
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_test, 'temperatura')
        
        self.assertIsInstance(X, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertGreater(len(X), 0)
        self.assertGreater(len(y), 0)
        self.assertEqual(len(X), len(y))
        
        # Verificar dimensiones
        self.assertEqual(X.ndim, 3)  # (samples, timesteps, features)
        self.assertEqual(y.ndim, 2)  # (samples, features)
    
    def test_crear_modelo_lstm(self):
        """Test de creación de modelo LSTM"""
        X, _ = self.ia.preparar_datos_entrenamiento(self.datos_test, 'temperatura')
        if len(X) > 0:
            input_shape = (X.shape[1], X.shape[2])
            modelo = self.ia.crear_modelo_lstm(input_shape, 'temperatura')
            
            self.assertIsNotNone(modelo)
            # Verificar que es un modelo de Keras
            self.assertTrue(hasattr(modelo, 'summary'))
            self.assertTrue(hasattr(modelo, 'compile'))
    
    def test_crear_modelo_transformer(self):
        """Test de creación de modelo Transformer"""
        X, _ = self.ia.preparar_datos_entrenamiento(self.datos_test, 'temperatura')
        if len(X) > 0:
            input_shape = (X.shape[1], X.shape[2])
            modelo = self.ia.crear_modelo_transformer(input_shape, 'temperatura')
            
            self.assertIsNotNone(modelo)
            # Verificar que es un modelo de Keras
            self.assertTrue(hasattr(modelo, 'summary'))
            self.assertTrue(hasattr(modelo, 'compile'))
    
    def test_crear_ensemble_model(self):
        """Test de creación de modelo ensemble"""
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_test, 'temperatura')
        if len(X) > 0:
            resultados = self.ia.crear_ensemble_model(X, y, 'temperatura')
            
            self.assertIsInstance(resultados, dict)
            self.assertGreater(len(resultados), 0)
            
            # Verificar que contiene métricas
            for modelo, metricas in resultados.items():
                self.assertIn('mae', metricas)
                self.assertIn('mse', metricas)
                self.assertIn('r2', metricas)
    
    def test_entrenar_todos_los_modelos(self):
        """Test de entrenamiento de todos los modelos"""
        resultados = self.ia.entrenar_todos_los_modelos(self.datos_test)
        
        self.assertIsInstance(resultados, dict)
        self.assertGreater(len(resultados), 0)
        
        # Verificar que se entrenaron modelos para diferentes variables
        variables_entrenadas = set()
        for key in resultados.keys():
            if '_' in key:
                variable = key.split('_', 1)[1]
                variables_entrenadas.add(variable)
        
        self.assertGreater(len(variables_entrenadas), 0)
    
    def test_evaluar_modelos(self):
        """Test de evaluación de modelos"""
        evaluacion = self.ia.evaluar_modelos(self.datos_test)
        
        self.assertIsInstance(evaluacion, dict)
        
        # Verificar estructura de evaluación
        for variable, modelos in evaluacion.items():
            self.assertIsInstance(modelos, dict)
            for modelo, metricas in modelos.items():
                self.assertIn('mae', metricas)
                self.assertIn('mse', metricas)
                self.assertIn('r2', metricas)
                self.assertIn('rmse', metricas)
    
    def test_generar_predicciones(self):
        """Test de generación de predicciones"""
        predicciones = self.ia.generar_predicciones(self.datos_test, 'temperatura', 'lstm', horizonte=12)
        
        self.assertIsInstance(predicciones, np.ndarray)
        self.assertGreater(len(predicciones), 0)
    
    def test_generar_reporte_ia(self):
        """Test de generación de reporte de IA"""
        # Primero entrenar algunos modelos
        resultados = self.ia.entrenar_todos_los_modelos(self.datos_test)
        evaluacion = self.ia.evaluar_modelos(self.datos_test)
        
        reporte = self.ia.generar_reporte_ia(resultados, evaluacion)
        
        self.assertIsInstance(reporte, str)
        self.assertGreater(len(reporte), 0)
        
        # Verificar que el archivo existe
        self.assertTrue(Path(reporte).exists())
    
    def test_configuracion_modelos(self):
        """Test de configuración de modelos"""
        config = self.ia.modelos_config
        
        self.assertIn('lstm', config)
        self.assertIn('transformer', config)
        self.assertIn('ensemble', config)
        
        # Verificar configuración LSTM
        lstm_config = config['lstm']
        self.assertIn('sequence_length', lstm_config)
        self.assertIn('lstm_units', lstm_config)
        self.assertIn('dropout', lstm_config)
        self.assertIn('epochs', lstm_config)
        
        # Verificar configuración Transformer
        transformer_config = config['transformer']
        self.assertIn('d_model', transformer_config)
        self.assertIn('num_heads', transformer_config)
        self.assertIn('num_layers', transformer_config)
    
    def test_variables_meteorologicas(self):
        """Test de variables meteorológicas"""
        variables = self.ia.variables_meteorologicas
        
        self.assertIsInstance(variables, list)
        self.assertGreater(len(variables), 0)
        
        variables_esperadas = ['temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion', 'humedad', 'presion', 'radiacion_solar', 'punto_rocio']
        for variable in variables_esperadas:
            self.assertIn(variable, variables)
    
    def test_manejo_errores(self):
        """Test de manejo de errores"""
        # Test con datos vacíos
        datos_vacios = pd.DataFrame()
        resultados = self.ia.entrenar_todos_los_modelos(datos_vacios)
        self.assertIsInstance(resultados, dict)
        
        # Test con variable inexistente
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_test, 'variable_inexistente')
        self.assertEqual(len(X), 0)
        self.assertEqual(len(y), 0)
    
    def test_rendimiento(self):
        """Test de rendimiento básico"""
        import time
        
        inicio = time.time()
        resultados = self.ia.entrenar_todos_los_modelos(self.datos_test)
        fin = time.time()
        
        duracion = fin - inicio
        self.assertLess(duracion, 300)  # Menos de 5 minutos
        
        print(f"Tiempo de entrenamiento: {duracion:.2f} segundos")

class TestIAAvanzadaIntegracion(unittest.TestCase):
    """Tests de integración para el módulo de IA Avanzada"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de integración"""
        if not IA_AVAILABLE:
            raise unittest.SkipTest("Módulo de IA Avanzada no disponible")
        
        cls.ia = IAAvanzadaMETGO()
    
    def test_pipeline_completo_ia(self):
        """Test del pipeline completo de IA"""
        # Generar datos de prueba
        datos = self.ia._generar_datos_sinteticos()
        self.assertGreater(len(datos), 0)
        
        # Entrenar modelos
        resultados_entrenamiento = self.ia.entrenar_todos_los_modelos(datos)
        self.assertIsInstance(resultados_entrenamiento, dict)
        
        # Evaluar modelos
        evaluacion = self.ia.evaluar_modelos(datos)
        self.assertIsInstance(evaluacion, dict)
        
        # Generar predicciones
        predicciones = self.ia.generar_predicciones(datos, 'temperatura', 'lstm')
        self.assertIsInstance(predicciones, np.ndarray)
        
        # Generar reporte
        reporte = self.ia.generar_reporte_ia(resultados_entrenamiento, evaluacion)
        self.assertIsInstance(reporte, str)
        self.assertTrue(Path(reporte).exists())
    
    def test_integracion_con_datos_reales(self):
        """Test de integración con datos reales simulados"""
        # Simular datos reales con patrones más complejos
        fechas = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
        np.random.seed(42)
        
        datos = pd.DataFrame(index=fechas)
        datos['temperatura'] = 15 + 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
        datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, np.random.exponential(0.5, len(fechas)), 0)
        datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
        datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
        datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
        datos['humedad'] = np.clip(datos['humedad'], 0, 100)
        datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
        datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
        datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
        
        # Ejecutar pipeline completo
        resultados = self.ia.entrenar_todos_los_modelos(datos)
        self.assertIsInstance(resultados, dict)
        self.assertGreater(len(resultados), 0)
        
        # Verificar que se entrenaron modelos para múltiples variables
        variables_entrenadas = set()
        for key in resultados.keys():
            if '_' in key:
                variable = key.split('_', 1)[1]
                variables_entrenadas.add(variable)
        
        self.assertGreaterEqual(len(variables_entrenadas), 3)  # Al menos 3 variables

if __name__ == '__main__':
    # Configurar el runner de tests
    unittest.main(verbosity=2)
