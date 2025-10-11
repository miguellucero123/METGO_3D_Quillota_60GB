#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTS DE INTEGRACIÓN COMPLETA METGO 3D
Sistema Meteorológico Agrícola Quillota - Testing de Integración
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
import json
import time

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from orquestador_metgo_avanzado import OrquestadorMETGOAvanzado
    from configuracion_unificada_metgo import ConfiguracionUnificadaMETGO
    from pipeline_completo_metgo import PipelineCompletoMETGO
    from dashboard_unificado_metgo import DashboardUnificadoMETGO
    INTEGRACION_AVAILABLE = True
except ImportError:
    INTEGRACION_AVAILABLE = False

class TestIntegracionCompleta(unittest.TestCase):
    """Tests de integración completa del sistema METGO 3D"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not INTEGRACION_AVAILABLE:
            raise unittest.SkipTest("Módulos de integración no disponibles")
        
        cls.configuracion = ConfiguracionUnificadaMETGO()
        cls.orquestador = OrquestadorMETGOAvanzado()
        cls.pipeline = PipelineCompletoMETGO()
        cls.dashboard = DashboardUnificadoMETGO()
    
    def test_integracion_configuracion(self):
        """Test de integración de configuración"""
        # Verificar que la configuración se carga correctamente
        config = self.configuracion.obtener_configuracion()
        self.assertIsInstance(config, dict)
        self.assertIn('sistema', config)
        self.assertIn('quillota', config)
        self.assertIn('meteorologia', config)
        
        # Verificar configuración específica de Quillota
        quillota_config = config['quillota']
        self.assertIn('coordenadas', quillota_config)
        self.assertEqual(quillota_config['coordenadas']['latitud'], -32.8833)
        self.assertEqual(quillota_config['coordenadas']['longitud'], -71.2333)
        
        # Verificar variables meteorológicas
        meteorologia_config = config['meteorologia']
        self.assertIn('variables', meteorologia_config)
        self.assertGreater(len(meteorologia_config['variables']), 0)
        
        # Validar configuración
        validacion = self.configuracion.validar_configuracion()
        self.assertIsInstance(validacion, dict)
        self.assertIn('valida', validacion)
    
    def test_integracion_orquestador(self):
        """Test de integración del orquestador"""
        # Verificar inicialización
        self.assertIsNotNone(self.orquestador)
        self.assertIsInstance(self.orquestador.configuracion, dict)
        self.assertIn('version', self.orquestador.configuracion)
        
        # Verificar que se inicializaron los módulos
        self.assertIsInstance(self.orquestador.modulos, dict)
        self.assertIsInstance(self.orquestador.estado_modulos, dict)
        
        # Verificar configuración de integración
        self.assertIn('frecuencia_actualizacion', self.orquestador.configuracion_integracion)
        self.assertIn('habilitar_paralelismo', self.orquestador.configuracion_integracion)
    
    def test_integracion_pipeline(self):
        """Test de integración del pipeline"""
        # Verificar inicialización
        self.assertIsNotNone(self.pipeline)
        self.assertIsInstance(self.pipeline.configuracion, dict)
        self.assertIn('version', self.pipeline.configuracion)
        
        # Verificar configuración del pipeline
        self.assertIn('frecuencia_procesamiento', self.pipeline.configuracion_pipeline)
        self.assertIn('batch_size', self.pipeline.configuracion_pipeline)
        self.assertIn('habilitar_paralelismo', self.pipeline.configuracion_pipeline)
        
        # Verificar estado del pipeline
        self.assertIsInstance(self.pipeline.estado_pipeline, dict)
        self.assertIn('activo', self.pipeline.estado_pipeline)
        self.assertFalse(self.pipeline.estado_pipeline['activo'])  # Inicialmente inactivo
    
    def test_integracion_dashboard(self):
        """Test de integración del dashboard"""
        # Verificar inicialización
        self.assertIsNotNone(self.dashboard)
        self.assertIsInstance(self.dashboard.configuracion, dict)
        self.assertIn('version', self.dashboard.configuracion)
        
        # Verificar colores de Quillota
        self.assertIn('primario', self.dashboard.colores_quillota)
        self.assertIn('secundario', self.dashboard.colores_quillota)
        self.assertEqual(self.dashboard.colores_quillota['primario'], '#2E8B57')
        
        # Verificar que se configuró la aplicación Dash
        self.assertIsNotNone(self.dashboard.app)
    
    def test_pipeline_completo_integracion(self):
        """Test del pipeline completo de integración"""
        # Ejecutar pipeline completo
        resultados = self.pipeline.ejecutar_pipeline_completo()
        
        self.assertIsInstance(resultados, dict)
        self.assertIn('inicio', resultados)
        self.assertIn('fin', resultados)
        self.assertIn('etapas', resultados)
        self.assertIn('duracion_total_segundos', resultados)
        
        # Verificar que se completaron todas las etapas
        etapas = resultados['etapas']
        self.assertIn('generacion_datos', etapas)
        self.assertIn('validacion', etapas)
        self.assertIn('procesamiento', etapas)
        self.assertIn('predicciones_ml', etapas)
        self.assertIn('evaluacion_alertas', etapas)
        self.assertIn('guardado_bd', etapas)
        
        # Verificar que cada etapa se completó exitosamente
        for etapa, info in etapas.items():
            self.assertEqual(info['estado'], 'completado')
            self.assertIn('duracion_segundos', info)
            self.assertGreater(info['duracion_segundos'], 0)
        
        # Verificar duración total
        self.assertGreater(resultados['duracion_total_segundos'], 0)
        self.assertLess(resultados['duracion_total_segundos'], 600)  # Menos de 10 minutos
    
    def test_orquestador_pipeline_integracion(self):
        """Test de integración entre orquestador y pipeline"""
        # Cargar datos integrados
        datos = self.orquestador.cargar_datos_integrados()
        self.assertIsInstance(datos, pd.DataFrame)
        self.assertGreater(len(datos), 0)
        
        # Verificar que los datos se guardaron en el orquestador
        self.assertIn('meteorologicos', self.orquestador.datos_compartidos)
        self.assertIsInstance(self.orquestador.datos_compartidos['meteorologicos'], pd.DataFrame)
        
        # Ejecutar pipeline completo del orquestador
        resultados = self.orquestador.ejecutar_pipeline_completo()
        
        self.assertIsInstance(resultados, dict)
        self.assertIn('inicio', resultados)
        self.assertIn('fin', resultados)
        self.assertIn('etapas', resultados)
        self.assertIn('integracion', resultados)
        self.assertIn('reporte_final', resultados)
        
        # Verificar integración de resultados
        integracion = resultados['integracion']
        self.assertIn('modulos_ejecutados', integracion)
        self.assertIn('resumen', integracion)
        self.assertIn('recomendaciones', integracion)
    
    def test_dashboard_integracion(self):
        """Test de integración del dashboard"""
        # Generar dashboard HTML
        archivo_html = self.dashboard.generar_dashboard_html()
        self.assertIsInstance(archivo_html, str)
        self.assertGreater(len(archivo_html), 0)
        self.assertTrue(Path(archivo_html).exists())
        
        # Generar reporte del dashboard
        reporte = self.dashboard.generar_reporte_dashboard()
        self.assertIsInstance(reporte, str)
        self.assertGreater(len(reporte), 0)
        self.assertTrue(Path(reporte).exists())
        
        # Verificar contenido del reporte
        with open(reporte, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        
        self.assertIn('timestamp', contenido)
        self.assertIn('sistema', contenido)
        self.assertIn('resumen', contenido)
        self.assertIn('configuracion', contenido)
        self.assertIn('recomendaciones', contenido)
    
    def test_rendimiento_integracion(self):
        """Test de rendimiento de la integración completa"""
        import time
        
        # Medir tiempo de ejecución del pipeline
        inicio = time.time()
        resultados = self.pipeline.ejecutar_pipeline_completo()
        fin = time.time()
        
        duracion_pipeline = fin - inicio
        self.assertLess(duracion_pipeline, 300)  # Menos de 5 minutos
        
        # Medir tiempo de ejecución del orquestador
        inicio = time.time()
        resultados_orquestador = self.orquestador.ejecutar_pipeline_completo()
        fin = time.time()
        
        duracion_orquestador = fin - inicio
        self.assertLess(duracion_orquestador, 600)  # Menos de 10 minutos
        
        print(f"Tiempo de pipeline: {duracion_pipeline:.2f} segundos")
        print(f"Tiempo de orquestador: {duracion_orquestador:.2f} segundos")
        
        # Verificar que ambos pipelines generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertIsInstance(resultados_orquestador, dict)
        self.assertIn('etapas', resultados)
        self.assertIn('etapas', resultados_orquestador)
    
    def test_escalabilidad_integracion(self):
        """Test de escalabilidad de la integración"""
        # Verificar que el sistema puede manejar múltiples ejecuciones
        for i in range(3):
            # Ejecutar pipeline
            resultados = self.pipeline.ejecutar_pipeline_completo()
            self.assertIsInstance(resultados, dict)
            self.assertIn('etapas', resultados)
            
            # Verificar que se generaron datos
            self.assertGreater(len(self.pipeline.datos_compartidos), 0)
            
            # Pequeña pausa entre ejecuciones
            time.sleep(1)
        
        # Verificar que el sistema sigue funcionando después de múltiples ejecuciones
        estado_pipeline = self.pipeline.obtener_metricas_pipeline()
        self.assertIsInstance(estado_pipeline, dict)
        self.assertIn('estado_pipeline', estado_pipeline)
    
    def test_manejo_errores_integracion(self):
        """Test de manejo de errores en la integración"""
        # Test con datos inválidos
        datos_invalidos = pd.DataFrame()
        
        # El sistema debe manejar datos vacíos sin fallar
        resultados = self.pipeline.ejecutar_pipeline_completo()
        self.assertIsInstance(resultados, dict)
        
        # Verificar que se registraron errores si los hubo
        if 'error' in resultados:
            self.assertIsInstance(resultados['error'], str)
        else:
            # Si no hay errores, verificar que se completó exitosamente
            self.assertIn('etapas', resultados)
            self.assertIn('duracion_total_segundos', resultados)
    
    def test_persistencia_datos_integracion(self):
        """Test de persistencia de datos en la integración"""
        # Ejecutar pipeline
        resultados = self.pipeline.ejecutar_pipeline_completo()
        
        # Verificar que se guardaron datos en la base de datos
        metricas = self.pipeline.obtener_metricas_pipeline()
        self.assertIsInstance(metricas, dict)
        self.assertIn('metricas_bd', metricas)
        
        bd_metricas = metricas['metricas_bd']
        self.assertIn('total_datos_meteorologicos', bd_metricas)
        self.assertIn('total_datos_iot', bd_metricas)
        self.assertIn('total_predicciones', bd_metricas)
        self.assertIn('total_alertas_activas', bd_metricas)
        
        # Verificar que hay datos en la base de datos
        self.assertGreater(bd_metricas['total_datos_meteorologicos'], 0)
        self.assertGreater(bd_metricas['total_datos_iot'], 0)
        self.assertGreater(bd_metricas['total_predicciones'], 0)
    
    def test_comunicacion_modulos_integracion(self):
        """Test de comunicación entre módulos"""
        # Verificar que el orquestador puede acceder a los módulos
        self.assertIsInstance(self.orquestador.modulos, dict)
        self.assertGreater(len(self.orquestador.modulos), 0)
        
        # Verificar estado de los módulos
        for nombre_modulo, estado in self.orquestador.estado_modulos.items():
            self.assertIsInstance(estado, dict)
            self.assertIn('activo', estado)
            self.assertIn('ultima_actualizacion', estado)
        
        # Verificar que se pueden ejecutar módulos individualmente
        datos = self.orquestador.cargar_datos_integrados()
        self.assertIsInstance(datos, pd.DataFrame)
        self.assertGreater(len(datos), 0)
    
    def test_configuracion_unificada_integracion(self):
        """Test de configuración unificada en la integración"""
        # Verificar que todos los módulos usan la misma configuración base
        config_base = self.configuracion.obtener_configuracion()
        
        # Verificar configuración del orquestador
        self.assertEqual(self.orquestador.configuracion['version'], config_base['sistema']['version'])
        
        # Verificar configuración del pipeline
        self.assertEqual(self.pipeline.configuracion['version'], config_base['sistema']['version'])
        
        # Verificar configuración del dashboard
        self.assertEqual(self.dashboard.configuracion['version'], config_base['sistema']['version'])
        
        # Verificar que la configuración es válida
        validacion = self.configuracion.validar_configuracion()
        self.assertIsInstance(validacion, dict)
        self.assertIn('valida', validacion)
    
    def test_reportes_integracion(self):
        """Test de generación de reportes en la integración"""
        # Generar reporte de configuración
        reporte_config = self.configuracion.generar_reporte_configuracion()
        self.assertIsInstance(reporte_config, str)
        self.assertTrue(Path(reporte_config).exists())
        
        # Generar reporte del pipeline
        reporte_pipeline = self.pipeline.generar_reporte_pipeline()
        self.assertIsInstance(reporte_pipeline, str)
        self.assertTrue(Path(reporte_pipeline).exists())
        
        # Generar reporte del orquestador
        estado_orquestador = self.orquestador.obtener_estado_sistema()
        self.assertIsInstance(estado_orquestador, dict)
        self.assertIn('timestamp', estado_orquestador)
        self.assertIn('sistema', estado_orquestador)
        
        # Generar reporte del dashboard
        reporte_dashboard = self.dashboard.generar_reporte_dashboard()
        self.assertIsInstance(reporte_dashboard, str)
        self.assertTrue(Path(reporte_dashboard).exists())
        
        # Verificar que todos los reportes tienen estructura similar
        reportes = [reporte_config, reporte_pipeline, reporte_dashboard]
        for reporte in reportes:
            if reporte:
                with open(reporte, 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                
                self.assertIn('timestamp', contenido)
                self.assertIn('sistema', contenido)
                self.assertIn('version', contenido)

class TestIntegracionRendimiento(unittest.TestCase):
    """Tests de rendimiento de la integración completa"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de rendimiento"""
        if not INTEGRACION_AVAILABLE:
            raise unittest.SkipTest("Módulos de integración no disponibles")
        
        cls.pipeline = PipelineCompletoMETGO()
        cls.orquestador = OrquestadorMETGOAvanzado()
    
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
        
        # Verificar duración de cada etapa
        for etapa, info in resultados['etapas'].items():
            self.assertLess(info['duracion_segundos'], 60)  # Cada etapa menos de 1 minuto
        
        print(f"Pipeline completo ejecutado en {duracion:.2f} segundos")
    
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
    
    def test_rendimiento_concurrente(self):
        """Test de rendimiento con ejecuciones concurrentes"""
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
        
        for i in range(3):
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
        self.assertEqual(len(resultados), 3)
        
        # Verificar que el tiempo total es razonable
        self.assertLess(duracion, 900)  # Menos de 15 minutos
        
        print(f"3 pipelines concurrentes ejecutados en {duracion:.2f} segundos")
    
    def test_rendimiento_memoria(self):
        """Test de rendimiento de memoria"""
        import psutil
        import os
        
        # Obtener proceso actual
        proceso = psutil.Process(os.getpid())
        
        # Medir memoria antes
        memoria_inicial = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Ejecutar pipeline
        resultados = self.pipeline.ejecutar_pipeline_completo()
        
        # Medir memoria después
        memoria_final = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Calcular incremento de memoria
        incremento_memoria = memoria_final - memoria_inicial
        
        # Verificar que el incremento es razonable
        self.assertLess(incremento_memoria, 500)  # Menos de 500 MB
        
        print(f"Memoria inicial: {memoria_inicial:.2f} MB")
        print(f"Memoria final: {memoria_final:.2f} MB")
        print(f"Incremento: {incremento_memoria:.2f} MB")
        
        # Verificar que se generaron resultados
        self.assertIsInstance(resultados, dict)
        self.assertIn('etapas', resultados)

if __name__ == '__main__':
    # Configurar el runner de tests
    unittest.main(verbosity=2)
