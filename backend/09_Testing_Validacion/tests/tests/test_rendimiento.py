#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTS DE RENDIMIENTO METGO 3D
Sistema Meteorológico Agrícola Quillota - Testing de Rendimiento y Carga
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
import time
import threading
import psutil
import gc

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from ia_avanzada_metgo import IAAvanzadaMETGO
    from sistema_iot_metgo import SistemaIoTMETGO
    from analisis_avanzado_metgo import AnalisisAvanzadoMETGO
    from visualizacion_3d_metgo import Visualizacion3DMETGO
    from pipeline_completo_metgo import PipelineCompletoMETGO
    from orquestador_metgo_avanzado import OrquestadorMETGOAvanzado
    RENDIMIENTO_AVAILABLE = True
except ImportError:
    RENDIMIENTO_AVAILABLE = False

class TestRendimientoIA(unittest.TestCase):
    """Tests de rendimiento para el módulo de IA"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.ia = IAAvanzadaMETGO()
        cls.datos_grandes = cls._generar_datos_grandes()
    
    @classmethod
    def _generar_datos_grandes(cls):
        """Generar dataset grande para tests de rendimiento"""
        fechas = pd.date_range(
            start='2020-01-01',
            end='2023-12-31',
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
    
    def test_rendimiento_entrenamiento_lstm(self):
        """Test de rendimiento del entrenamiento LSTM"""
        import time
        
        # Preparar datos
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_grandes, 'temperatura')
        
        if len(X) == 0:
            self.skipTest("No se pudieron preparar datos para LSTM")
        
        # Crear modelo
        modelo = self.ia.crear_modelo_lstm((X.shape[1], X.shape[2]), 'temperatura')
        
        # Medir tiempo de entrenamiento
        inicio = time.time()
        metricas = self.ia.entrenar_modelo_lstm(modelo, X, y, 'temperatura')
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 600)  # Menos de 10 minutos
        
        # Verificar que se generaron métricas
        self.assertIsInstance(metricas, dict)
        self.assertIn('epochs_entrenados', metricas)
        
        print(f"Entrenamiento LSTM completado en {duracion:.2f} segundos")
    
    def test_rendimiento_entrenamiento_transformer(self):
        """Test de rendimiento del entrenamiento Transformer"""
        import time
        
        # Preparar datos
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_grandes, 'temperatura')
        
        if len(X) == 0:
            self.skipTest("No se pudieron preparar datos para Transformer")
        
        # Crear modelo
        modelo = self.ia.crear_modelo_transformer((X.shape[1], X.shape[2]), 'temperatura')
        
        # Medir tiempo de entrenamiento
        inicio = time.time()
        metricas = self.ia.entrenar_modelo_transformer(modelo, X, y, 'temperatura')
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 600)  # Menos de 10 minutos
        
        # Verificar que se generaron métricas
        self.assertIsInstance(metricas, dict)
        self.assertIn('epochs_entrenados', metricas)
        
        print(f"Entrenamiento Transformer completado en {duracion:.2f} segundos")
    
    def test_rendimiento_ensemble(self):
        """Test de rendimiento del modelo ensemble"""
        import time
        
        # Preparar datos
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_grandes, 'temperatura')
        
        if len(X) == 0:
            self.skipTest("No se pudieron preparar datos para ensemble")
        
        # Medir tiempo de entrenamiento
        inicio = time.time()
        resultados = self.ia.crear_ensemble_model(X, y, 'temperatura')
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 300)  # Menos de 5 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertGreater(len(resultados), 0)
        
        print(f"Entrenamiento ensemble completado en {duracion:.2f} segundos")
    
    def test_rendimiento_predicciones(self):
        """Test de rendimiento de predicciones"""
        import time
        
        # Preparar datos
        X, y = self.ia.preparar_datos_entrenamiento(self.datos_grandes, 'temperatura')
        
        if len(X) == 0:
            self.skipTest("No se pudieron preparar datos para predicciones")
        
        # Medir tiempo de predicciones
        inicio = time.time()
        predicciones = self.ia.generar_predicciones(self.datos_grandes, 'temperatura', 'lstm', horizonte=24)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 60)  # Menos de 1 minuto
        
        # Verificar que se generaron predicciones
        self.assertIsInstance(predicciones, np.ndarray)
        self.assertGreater(len(predicciones), 0)
        
        print(f"Predicciones generadas en {duracion:.2f} segundos")
    
    def test_rendimiento_memoria_ia(self):
        """Test de rendimiento de memoria para IA"""
        import psutil
        import os
        
        # Obtener proceso actual
        proceso = psutil.Process(os.getpid())
        
        # Medir memoria antes
        memoria_inicial = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Ejecutar entrenamiento
        resultados = self.ia.entrenar_todos_los_modelos(self.datos_grandes)
        
        # Medir memoria después
        memoria_final = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Calcular incremento de memoria
        incremento_memoria = memoria_final - memoria_inicial
        
        # Verificar que el incremento es razonable
        self.assertLess(incremento_memoria, 1000)  # Menos de 1 GB
        
        print(f"Memoria inicial IA: {memoria_inicial:.2f} MB")
        print(f"Memoria final IA: {memoria_final:.2f} MB")
        print(f"Incremento IA: {incremento_memoria:.2f} MB")
        
        # Limpiar memoria
        gc.collect()

class TestRendimientoIoT(unittest.TestCase):
    """Tests de rendimiento para el módulo IoT"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento IoT"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.sistema_iot = SistemaIoTMETGO()
    
    def test_rendimiento_red_sensores(self):
        """Test de rendimiento de creación de red de sensores"""
        import time
        
        # Medir tiempo de creación
        inicio = time.time()
        resultado = self.sistema_iot.crear_red_sensores({})
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 30)  # Menos de 30 segundos
        
        # Verificar que se creó la red
        self.assertTrue(resultado)
        self.assertGreater(len(self.sistema_iot.gateways), 0)
        self.assertGreater(len(self.sistema_iot.sensores), 0)
        
        print(f"Red de sensores creada en {duracion:.2f} segundos")
    
    def test_rendimiento_monitoreo_iot(self):
        """Test de rendimiento de monitoreo IoT"""
        import time
        
        # Crear red de sensores
        self.sistema_iot.crear_red_sensores({})
        
        # Medir tiempo de monitoreo
        inicio = time.time()
        resultado = self.sistema_iot.iniciar_monitoreo_iot(duracion_minutos=2)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 150)  # Menos de 2.5 minutos
        
        # Verificar que se generaron datos
        self.assertTrue(resultado)
        self.assertGreater(len(self.sistema_iot.datos_iot), 0)
        
        print(f"Monitoreo IoT completado en {duracion:.2f} segundos")
    
    def test_rendimiento_procesamiento_iot(self):
        """Test de rendimiento de procesamiento IoT"""
        import time
        
        # Generar datos de prueba
        self.sistema_iot.datos_iot = []
        for i in range(1000):
            dato = {
                'sensor_id': f'sensor_{i % 10:03d}',
                'tipo': 'temperatura',
                'timestamp': datetime.now().isoformat(),
                'valor': 20 + np.random.normal(0, 5),
                'unidad': '°C',
                'bateria': 100 - i * 0.01,
                'senal': 85 + np.random.normal(0, 5)
            }
            self.sistema_iot.datos_iot.append(dato)
        
        # Medir tiempo de procesamiento
        inicio = time.time()
        resultado = self.sistema_iot.procesar_datos_iot()
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 10)  # Menos de 10 segundos
        
        # Verificar que se procesaron los datos
        self.assertTrue(resultado)
        self.assertIn('total_lecturas', self.sistema_iot.estadisticas)
        
        print(f"Procesamiento IoT completado en {duracion:.2f} segundos")

class TestRendimientoAnalisis(unittest.TestCase):
    """Tests de rendimiento para el módulo de análisis"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento análisis"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.analisis = AnalisisAvanzadoMETGO()
        cls.datos_grandes = cls._generar_datos_grandes()
    
    @classmethod
    def _generar_datos_grandes(cls):
        """Generar dataset grande para tests de rendimiento"""
        fechas = pd.date_range(
            start='2020-01-01',
            end='2023-12-31',
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
    
    def test_rendimiento_estacionalidad(self):
        """Test de rendimiento de análisis de estacionalidad"""
        import time
        
        # Medir tiempo de análisis
        inicio = time.time()
        resultado = self.analisis.analisis_estacionalidad(self.datos_grandes, 'temperatura')
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 30)  # Menos de 30 segundos
        
        # Verificar que se generó resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('estacionalidad', resultado)
        
        print(f"Análisis de estacionalidad completado en {duracion:.2f} segundos")
    
    def test_rendimiento_correlaciones(self):
        """Test de rendimiento de análisis de correlaciones"""
        import time
        
        # Medir tiempo de análisis
        inicio = time.time()
        resultado = self.analisis.analisis_correlaciones(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 60)  # Menos de 1 minuto
        
        # Verificar que se generó resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('matriz_correlacion', resultado)
        
        print(f"Análisis de correlaciones completado en {duracion:.2f} segundos")
    
    def test_rendimiento_clustering(self):
        """Test de rendimiento de análisis de clustering"""
        import time
        
        # Medir tiempo de análisis
        inicio = time.time()
        resultado = self.analisis.analisis_clustering(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 120)  # Menos de 2 minutos
        
        # Verificar que se generó resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('kmeans', resultado)
        self.assertIn('dbscan', resultado)
        
        print(f"Análisis de clustering completado en {duracion:.2f} segundos")
    
    def test_rendimiento_anomalias(self):
        """Test de rendimiento de análisis de anomalías"""
        import time
        
        # Medir tiempo de análisis
        inicio = time.time()
        resultado = self.analisis.analisis_anomalias(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 60)  # Menos de 1 minuto
        
        # Verificar que se generó resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('anomalias_por_variable', resultado)
        
        print(f"Análisis de anomalías completado en {duracion:.2f} segundos")
    
    def test_rendimiento_pca(self):
        """Test de rendimiento de análisis PCA"""
        import time
        
        # Medir tiempo de análisis
        inicio = time.time()
        resultado = self.analisis.analisis_pca(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 60)  # Menos de 1 minuto
        
        # Verificar que se generó resultado
        self.assertIsInstance(resultado, dict)
        self.assertIn('varianza_explicada', resultado)
        self.assertIn('componentes_principales', resultado)
        
        print(f"Análisis PCA completado en {duracion:.2f} segundos")

class TestRendimientoVisualizacion(unittest.TestCase):
    """Tests de rendimiento para el módulo de visualización"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento visualización"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.visualizacion = Visualizacion3DMETGO()
        cls.datos_grandes = cls._generar_datos_grandes()
    
    @classmethod
    def _generar_datos_grandes(cls):
        """Generar dataset grande para tests de rendimiento"""
        fechas = pd.date_range(
            start='2020-01-01',
            end='2023-12-31',
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
    
    def test_rendimiento_visualizacion_3d(self):
        """Test de rendimiento de visualización 3D"""
        import time
        
        # Medir tiempo de creación
        inicio = time.time()
        archivo = self.visualizacion.crear_visualizacion_3d_temperatura(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 120)  # Menos de 2 minutos
        
        # Verificar que se generó archivo
        self.assertIsInstance(archivo, str)
        if archivo:
            self.assertTrue(Path(archivo).exists())
        
        print(f"Visualización 3D completada en {duracion:.2f} segundos")
    
    def test_rendimiento_dashboard_interactivo(self):
        """Test de rendimiento de dashboard interactivo"""
        import time
        
        # Medir tiempo de creación
        inicio = time.time()
        archivo = self.visualizacion.crear_dashboard_interactivo_3d(self.datos_grandes)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 180)  # Menos de 3 minutos
        
        # Verificar que se generó archivo
        self.assertIsInstance(archivo, str)
        if archivo:
            self.assertTrue(Path(archivo).exists())
        
        print(f"Dashboard interactivo completado en {duracion:.2f} segundos")
    
    def test_rendimiento_visualizaciones_multiples(self):
        """Test de rendimiento de múltiples visualizaciones"""
        import time
        
        # Lista de funciones de visualización
        funciones = [
            self.visualizacion.crear_visualizacion_3d_temperatura,
            self.visualizacion.crear_visualizacion_3d_viento,
            self.visualizacion.crear_visualizacion_3d_multivariable,
            self.visualizacion.crear_visualizacion_estacional_3d,
            self.visualizacion.crear_visualizacion_correlaciones_3d
        ]
        
        # Medir tiempo total
        inicio = time.time()
        
        for funcion in funciones:
            try:
                archivo = funcion(self.datos_grandes)
                self.assertIsInstance(archivo, str)
            except Exception as e:
                print(f"Error en {funcion.__name__}: {e}")
        
        fin = time.time()
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 600)  # Menos de 10 minutos
        
        print(f"Múltiples visualizaciones completadas en {duracion:.2f} segundos")

class TestRendimientoPipeline(unittest.TestCase):
    """Tests de rendimiento para el pipeline completo"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento pipeline"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.pipeline = PipelineCompletoMETGO()
    
    def test_rendimiento_pipeline_completo(self):
        """Test de rendimiento del pipeline completo"""
        import time
        
        # Medir tiempo de ejecución
        inicio = time.time()
        resultados = self.pipeline.ejecutar_pipeline_completo()
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 300)  # Menos de 5 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertIn('etapas', resultados)
        self.assertIn('duracion_total_segundos', resultados)
        
        print(f"Pipeline completo ejecutado en {duracion:.2f} segundos")
    
    def test_rendimiento_generacion_datos(self):
        """Test de rendimiento de generación de datos"""
        import time
        
        # Medir tiempo de generación
        inicio = time.time()
        datos = self.pipeline.generar_datos_sinteticos(10000)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 30)  # Menos de 30 segundos
        
        # Verificar que se generaron datos
        self.assertIsInstance(datos, list)
        self.assertEqual(len(datos), 10000)
        
        print(f"10,000 registros generados en {duracion:.2f} segundos")
    
    def test_rendimiento_validacion_datos(self):
        """Test de rendimiento de validación de datos"""
        import time
        
        # Generar datos de prueba
        datos = self.pipeline.generar_datos_sinteticos(5000)
        
        # Medir tiempo de validación
        inicio = time.time()
        datos_validos = self.pipeline.validar_datos_meteorologicos(datos)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 10)  # Menos de 10 segundos
        
        # Verificar que se validaron datos
        self.assertIsInstance(datos_validos, list)
        self.assertGreater(len(datos_validos), 0)
        
        print(f"5,000 registros validados en {duracion:.2f} segundos")
    
    def test_rendimiento_procesamiento_datos(self):
        """Test de rendimiento de procesamiento de datos"""
        import time
        
        # Generar y validar datos
        datos = self.pipeline.generar_datos_sinteticos(5000)
        datos_validos = self.pipeline.validar_datos_meteorologicos(datos)
        
        # Medir tiempo de procesamiento
        inicio = time.time()
        datos_procesados = self.pipeline.procesar_datos_meteorologicos(datos_validos)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 5)  # Menos de 5 segundos
        
        # Verificar que se procesaron datos
        self.assertIsInstance(datos_procesados, list)
        self.assertEqual(len(datos_procesados), len(datos_validos))
        
        print(f"Datos procesados en {duracion:.2f} segundos")
    
    def test_rendimiento_predicciones_ml(self):
        """Test de rendimiento de predicciones ML"""
        import time
        
        # Generar datos
        datos = self.pipeline.generar_datos_sinteticos(1000)
        datos_validos = self.pipeline.validar_datos_meteorologicos(datos)
        datos_procesados = self.pipeline.procesar_datos_meteorologicos(datos_validos)
        
        # Medir tiempo de predicciones
        inicio = time.time()
        predicciones = self.pipeline.generar_predicciones_ml(datos_procesados)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 60)  # Menos de 1 minuto
        
        # Verificar que se generaron predicciones
        self.assertIsInstance(predicciones, list)
        self.assertGreater(len(predicciones), 0)
        
        print(f"Predicciones ML generadas en {duracion:.2f} segundos")
    
    def test_rendimiento_evaluacion_alertas(self):
        """Test de rendimiento de evaluación de alertas"""
        import time
        
        # Generar datos
        datos = self.pipeline.generar_datos_sinteticos(1000)
        datos_validos = self.pipeline.validar_datos_meteorologicos(datos)
        datos_procesados = self.pipeline.procesar_datos_meteorologicos(datos_validos)
        
        # Medir tiempo de evaluación
        inicio = time.time()
        alertas = self.pipeline.evaluar_alertas(datos_procesados)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 5)  # Menos de 5 segundos
        
        # Verificar que se generaron alertas
        self.assertIsInstance(alertas, list)
        
        print(f"Alertas evaluadas en {duracion:.2f} segundos")

class TestRendimientoOrquestador(unittest.TestCase):
    """Tests de rendimiento para el orquestador"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento orquestador"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.orquestador = OrquestadorMETGOAvanzado()
    
    def test_rendimiento_orquestador_completo(self):
        """Test de rendimiento del orquestador completo"""
        import time
        
        # Medir tiempo de ejecución
        inicio = time.time()
        resultados = self.orquestador.ejecutar_pipeline_completo()
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 600)  # Menos de 10 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertIn('etapas', resultados)
        self.assertIn('integracion', resultados)
        
        print(f"Orquestador completo ejecutado en {duracion:.2f} segundos")
    
    def test_rendimiento_carga_datos(self):
        """Test de rendimiento de carga de datos"""
        import time
        
        # Medir tiempo de carga
        inicio = time.time()
        datos = self.orquestador.cargar_datos_integrados()
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 30)  # Menos de 30 segundos
        
        # Verificar que se cargaron datos
        self.assertIsInstance(datos, pd.DataFrame)
        self.assertGreater(len(datos), 0)
        
        print(f"Datos integrados cargados en {duracion:.2f} segundos")
    
    def test_rendimiento_modulos_paralelo(self):
        """Test de rendimiento de módulos en paralelo"""
        import time
        
        # Cargar datos
        datos = self.orquestador.cargar_datos_integrados()
        
        # Medir tiempo de ejecución paralela
        inicio = time.time()
        resultados = self.orquestador._ejecutar_modulos_paralelo(datos)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 300)  # Menos de 5 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertGreater(len(resultados), 0)
        
        print(f"Módulos en paralelo ejecutados en {duracion:.2f} segundos")
    
    def test_rendimiento_modulos_secuencial(self):
        """Test de rendimiento de módulos secuenciales"""
        import time
        
        # Cargar datos
        datos = self.orquestador.cargar_datos_integrados()
        
        # Medir tiempo de ejecución secuencial
        inicio = time.time()
        resultados = self.orquestador._ejecutar_modulos_secuencial(datos)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 600)  # Menos de 10 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertGreater(len(resultados), 0)
        
        print(f"Módulos secuenciales ejecutados en {duracion:.2f} segundos")

class TestRendimientoCarga(unittest.TestCase):
    """Tests de rendimiento bajo carga"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de carga"""
        if not RENDIMIENTO_AVAILABLE:
            raise unittest.SkipTest("Módulos de rendimiento no disponibles")
        
        cls.pipeline = PipelineCompletoMETGO()
        cls.orquestador = OrquestadorMETGOAvanzado()
    
    def test_carga_multiple_pipelines(self):
        """Test de carga con múltiples pipelines concurrentes"""
        import threading
        import time
        
        resultados = []
        errores = []
        
        def ejecutar_pipeline():
            try:
                resultado = self.pipeline.ejecutar_pipeline_completo()
                resultados.append(resultado)
            except Exception as e:
                errores.append(e)
        
        # Ejecutar múltiples pipelines concurrentemente
        hilos = []
        inicio = time.time()
        
        for i in range(5):
            hilo = threading.Thread(target=ejecutar_pipeline)
            hilos.append(hilo)
            hilo.start()
        
        # Esperar a que terminen todos los hilos
        for hilo in hilos:
            hilo.join()
        
        fin = time.time()
        duracion = fin - inicio
        
        # Verificar que no hubo errores
        self.assertEqual(len(errores), 0)
        
        # Verificar que se completaron todas las ejecuciones
        self.assertEqual(len(resultados), 5)
        
        # Verificar que el tiempo total es razonable
        self.assertLess(duracion, 1800)  # Menos de 30 minutos
        
        print(f"5 pipelines concurrentes ejecutados en {duracion:.2f} segundos")
    
    def test_carga_datos_grandes(self):
        """Test de carga con datos grandes"""
        import time
        
        # Generar dataset grande
        inicio = time.time()
        datos = self.pipeline.generar_datos_sinteticos(50000)
        fin = time.time()
        
        duracion_generacion = fin - inicio
        
        # Procesar datos grandes
        inicio = time.time()
        datos_validos = self.pipeline.validar_datos_meteorologicos(datos)
        fin = time.time()
        
        duracion_validacion = fin - inicio
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion_generacion, 60)  # Menos de 1 minuto
        self.assertLess(duracion_validacion, 30)  # Menos de 30 segundos
        
        # Verificar que se generaron datos
        self.assertEqual(len(datos), 50000)
        self.assertGreater(len(datos_validos), 0)
        
        print(f"50,000 registros generados en {duracion_generacion:.2f} segundos")
        print(f"50,000 registros validados en {duracion_validacion:.2f} segundos")
    
    def test_carga_memoria_intensiva(self):
        """Test de carga intensiva de memoria"""
        import psutil
        import os
        import gc
        
        # Obtener proceso actual
        proceso = psutil.Process(os.getpid())
        
        # Medir memoria inicial
        memoria_inicial = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Ejecutar múltiples pipelines para aumentar uso de memoria
        for i in range(3):
            resultados = self.pipeline.ejecutar_pipeline_completo()
            self.assertIsInstance(resultados, dict)
            
            # Forzar garbage collection
            gc.collect()
        
        # Medir memoria final
        memoria_final = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Calcular incremento de memoria
        incremento_memoria = memoria_final - memoria_inicial
        
        # Verificar que el incremento es razonable
        self.assertLess(incremento_memoria, 2000)  # Menos de 2 GB
        
        print(f"Memoria inicial: {memoria_inicial:.2f} MB")
        print(f"Memoria final: {memoria_final:.2f} MB")
        print(f"Incremento: {incremento_memoria:.2f} MB")
    
    def test_carga_cpu_intensiva(self):
        """Test de carga intensiva de CPU"""
        import psutil
        import os
        import time
        
        # Obtener proceso actual
        proceso = psutil.Process(os.getpid())
        
        # Medir CPU inicial
        cpu_inicial = proceso.cpu_percent()
        
        # Ejecutar pipeline que consume CPU
        inicio = time.time()
        resultados = self.pipeline.ejecutar_pipeline_completo()
        fin = time.time()
        
        duracion = fin - inicio
        
        # Medir CPU durante la ejecución
        cpu_durante = proceso.cpu_percent()
        
        # Verificar que se completó en tiempo razonable
        self.assertLess(duracion, 300)  # Menos de 5 minutos
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        
        print(f"Pipeline ejecutado en {duracion:.2f} segundos")
        print(f"CPU inicial: {cpu_inicial:.2f}%")
        print(f"CPU durante: {cpu_durante:.2f}%")

if __name__ == '__main__':
    # Configurar el runner de tests
    unittest.main(verbosity=2)
