#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTS UNITARIOS - SISTEMA IoT METGO 3D
Sistema Meteorológico Agrícola Quillota - Testing del Sistema IoT
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
import json

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sistema_iot_metgo import SistemaIoTMETGO, SensorIoT, GatewayIoT
    IOT_AVAILABLE = True
except ImportError:
    IOT_AVAILABLE = False

class TestSensorIoT(unittest.TestCase):
    """Tests unitarios para la clase SensorIoT"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        if not IOT_AVAILABLE:
            self.skipTest("Módulo IoT no disponible")
        
        self.sensor = SensorIoT(
            sensor_id="test_sensor_001",
            tipo="temperatura",
            ubicacion={'latitud': -32.8833, 'longitud': -71.2333, 'altitud': 127},
            configuracion={'unidad': '°C', 'frecuencia': 60}
        )
    
    def test_inicializacion_sensor(self):
        """Test de inicialización del sensor"""
        self.assertEqual(self.sensor.sensor_id, "test_sensor_001")
        self.assertEqual(self.sensor.tipo, "temperatura")
        self.assertEqual(self.sensor.estado, 'activo')
        self.assertEqual(self.sensor.bateria, 100.0)
        self.assertEqual(self.sensor.senal, 85.0)
        self.assertIsNone(self.sensor.ultima_lectura)
        self.assertEqual(len(self.sensor.lecturas), 0)
    
    def test_leer_sensor(self):
        """Test de lectura del sensor"""
        lectura = self.sensor.leer_sensor()
        
        self.assertIsInstance(lectura, dict)
        self.assertIn('sensor_id', lectura)
        self.assertIn('tipo', lectura)
        self.assertIn('timestamp', lectura)
        self.assertIn('valor', lectura)
        self.assertIn('unidad', lectura)
        self.assertIn('ubicacion', lectura)
        self.assertIn('bateria', lectura)
        self.assertIn('senal', lectura)
        self.assertIn('estado', lectura)
        
        self.assertEqual(lectura['sensor_id'], "test_sensor_001")
        self.assertEqual(lectura['tipo'], "temperatura")
        self.assertEqual(lectura['unidad'], '°C')
        self.assertIsInstance(lectura['valor'], (int, float))
        self.assertIsInstance(lectura['timestamp'], str)
        
        # Verificar que se actualizó el estado del sensor
        self.assertIsNotNone(self.sensor.ultima_lectura)
        self.assertEqual(len(self.sensor.lecturas), 1)
        self.assertLess(self.sensor.bateria, 100.0)
    
    def test_obtener_estado_sensor(self):
        """Test de obtención del estado del sensor"""
        estado = self.sensor.obtener_estado()
        
        self.assertIsInstance(estado, dict)
        self.assertIn('sensor_id', estado)
        self.assertIn('tipo', estado)
        self.assertIn('estado', estado)
        self.assertIn('bateria', estado)
        self.assertIn('senal', estado)
        self.assertIn('ultima_lectura', estado)
        self.assertIn('total_lecturas', estado)
        
        self.assertEqual(estado['sensor_id'], "test_sensor_001")
        self.assertEqual(estado['tipo'], "temperatura")
        self.assertEqual(estado['estado'], 'activo')
        self.assertEqual(estado['total_lecturas'], 0)
    
    def test_consumo_bateria(self):
        """Test de consumo de batería"""
        bateria_inicial = self.sensor.bateria
        
        # Realizar múltiples lecturas
        for _ in range(10):
            self.sensor.leer_sensor()
        
        # Verificar que la batería disminuyó
        self.assertLess(self.sensor.bateria, bateria_inicial)
        
        # Verificar que hay 10 lecturas
        self.assertEqual(len(self.sensor.lecturas), 10)
    
    def test_estado_bateria_baja(self):
        """Test de estado de batería baja"""
        # Simular batería baja
        self.sensor.bateria = 5.0
        self.sensor.leer_sensor()
        
        # Verificar que el estado cambió
        self.assertEqual(self.sensor.estado, 'bateria_baja')
    
    def test_variacion_senal(self):
        """Test de variación de señal"""
        senal_inicial = self.sensor.senal
        
        # Realizar múltiples lecturas
        for _ in range(5):
            self.sensor.leer_sensor()
        
        # Verificar que la señal varió (puede aumentar o disminuir)
        self.assertNotEqual(self.sensor.senal, senal_inicial)
        
        # Verificar que la señal está en rango válido
        self.assertGreaterEqual(self.sensor.senal, 0)
        self.assertLessEqual(self.sensor.senal, 100)

class TestGatewayIoT(unittest.TestCase):
    """Tests unitarios para la clase GatewayIoT"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        if not IOT_AVAILABLE:
            self.skipTest("Módulo IoT no disponible")
        
        self.gateway = GatewayIoT(
            gateway_id="test_gateway_001",
            configuracion={'ubicacion': {'latitud': -32.8833, 'longitud': -71.2333}, 'frecuencia_comunicacion': 60}
        )
        
        # Crear sensores de prueba
        self.sensor1 = SensorIoT("sensor_001", "temperatura", {'latitud': -32.8833, 'longitud': -71.2333}, {'unidad': '°C'})
        self.sensor2 = SensorIoT("sensor_002", "humedad", {'latitud': -32.8833, 'longitud': -71.2333}, {'unidad': '%'})
    
    def test_inicializacion_gateway(self):
        """Test de inicialización del gateway"""
        self.assertEqual(self.gateway.gateway_id, "test_gateway_001")
        self.assertEqual(self.gateway.estado, 'activo')
        self.assertEqual(len(self.gateway.sensores), 0)
        self.assertIsNone(self.gateway.ultima_comunicacion)
    
    def test_agregar_sensor(self):
        """Test de agregar sensor al gateway"""
        self.gateway.agregar_sensor(self.sensor1)
        
        self.assertEqual(len(self.gateway.sensores), 1)
        self.assertIn("sensor_001", self.gateway.sensores)
        self.assertEqual(self.gateway.sensores["sensor_001"], self.sensor1)
    
    def test_leer_todos_los_sensores(self):
        """Test de lectura de todos los sensores"""
        # Agregar sensores
        self.gateway.agregar_sensor(self.sensor1)
        self.gateway.agregar_sensor(self.sensor2)
        
        # Leer todos los sensores
        lecturas = self.gateway.leer_todos_los_sensores()
        
        self.assertIsInstance(lecturas, list)
        self.assertEqual(len(lecturas), 2)
        
        # Verificar que se actualizó la última comunicación
        self.assertIsNotNone(self.gateway.ultima_comunicacion)
        
        # Verificar estructura de las lecturas
        for lectura in lecturas:
            self.assertIsInstance(lectura, dict)
            self.assertIn('sensor_id', lectura)
            self.assertIn('tipo', lectura)
            self.assertIn('valor', lectura)
    
    def test_obtener_estado_gateway(self):
        """Test de obtención del estado del gateway"""
        # Agregar sensores
        self.gateway.agregar_sensor(self.sensor1)
        self.gateway.agregar_sensor(self.sensor2)
        
        estado = self.gateway.obtener_estado_gateway()
        
        self.assertIsInstance(estado, dict)
        self.assertIn('gateway_id', estado)
        self.assertIn('estado', estado)
        self.assertIn('total_sensores', estado)
        self.assertIn('ultima_comunicacion', estado)
        self.assertIn('sensores', estado)
        
        self.assertEqual(estado['gateway_id'], "test_gateway_001")
        self.assertEqual(estado['total_sensores'], 2)
        self.assertEqual(len(estado['sensores']), 2)

class TestSistemaIoTMETGO(unittest.TestCase):
    """Tests unitarios para la clase SistemaIoTMETGO"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not IOT_AVAILABLE:
            raise unittest.SkipTest("Módulo IoT no disponible")
        
        cls.sistema_iot = SistemaIoTMETGO()
    
    def test_inicializacion_sistema(self):
        """Test de inicialización del sistema IoT"""
        self.assertIsNotNone(self.sistema_iot)
        self.assertIsInstance(self.sistema_iot.configuracion, dict)
        self.assertIn('version', self.sistema_iot.configuracion)
        self.assertEqual(self.sistema_iot.configuracion['version'], '2.0')
        
        # Verificar configuración de red
        self.assertIn('mqtt_broker', self.sistema_iot.configuracion_red)
        self.assertIn('mqtt_port', self.sistema_iot.configuracion_red)
        self.assertIn('mqtt_topic', self.sistema_iot.configuracion_red)
    
    def test_crear_red_sensores(self):
        """Test de creación de red de sensores"""
        resultado = self.sistema_iot.crear_red_sensores({})
        
        self.assertTrue(resultado)
        self.assertGreater(len(self.sistema_iot.gateways), 0)
        self.assertGreater(len(self.sistema_iot.sensores), 0)
        
        # Verificar que se crearon gateways para diferentes ubicaciones
        ubicaciones = set()
        for gateway in self.sistema_iot.gateways.values():
            ubicacion = gateway.configuracion['ubicacion']['nombre']
            ubicaciones.add(ubicacion)
        
        self.assertGreaterEqual(len(ubicaciones), 3)  # Al menos 3 ubicaciones
    
    def test_iniciar_monitoreo_iot(self):
        """Test de inicio de monitoreo IoT"""
        # Crear red de sensores primero
        self.sistema_iot.crear_red_sensores({})
        
        # Iniciar monitoreo por 1 minuto
        resultado = self.sistema_iot.iniciar_monitoreo_iot(duracion_minutos=1)
        
        self.assertTrue(resultado)
        self.assertGreater(len(self.sistema_iot.datos_iot), 0)
    
    def test_procesar_datos_iot(self):
        """Test de procesamiento de datos IoT"""
        # Generar algunos datos de prueba
        self.sistema_iot.datos_iot = [
            {
                'sensor_id': 'sensor_001',
                'tipo': 'temperatura',
                'timestamp': datetime.now().isoformat(),
                'valor': 22.5,
                'unidad': '°C',
                'bateria': 85.0,
                'senal': 90.0
            },
            {
                'sensor_id': 'sensor_002',
                'tipo': 'humedad',
                'timestamp': datetime.now().isoformat(),
                'valor': 65.2,
                'unidad': '%',
                'bateria': 92.0,
                'senal': 88.0
            }
        ]
        
        resultado = self.sistema_iot.procesar_datos_iot()
        
        self.assertTrue(resultado)
        self.assertIn('total_lecturas', self.sistema_iot.estadisticas)
        self.assertIn('sensores_activos', self.sistema_iot.estadisticas)
        self.assertIn('tipos_sensores', self.sistema_iot.estadisticas)
        self.assertIn('estadisticas_por_tipo', self.sistema_iot.estadisticas)
    
    def test_procesar_mensaje_iot(self):
        """Test de procesamiento de mensaje IoT"""
        mensaje_valido = {
            'sensor_id': 'sensor_001',
            'tipo': 'temperatura',
            'timestamp': datetime.now().isoformat(),
            'valor': 22.5
        }
        
        resultado = self.sistema_iot.procesar_mensaje_iot(mensaje_valido)
        
        self.assertTrue(resultado)
        self.assertGreater(len(self.sistema_iot.datos_iot), 0)
    
    def test_validar_mensaje_iot(self):
        """Test de validación de mensaje IoT"""
        # Mensaje válido
        mensaje_valido = {
            'sensor_id': 'sensor_001',
            'tipo': 'temperatura',
            'timestamp': datetime.now().isoformat(),
            'valor': 22.5
        }
        
        self.assertTrue(self.sistema_iot.validar_mensaje_iot(mensaje_valido))
        
        # Mensaje inválido (falta campo requerido)
        mensaje_invalido = {
            'sensor_id': 'sensor_001',
            'tipo': 'temperatura',
            'timestamp': datetime.now().isoformat()
            # Falta 'valor'
        }
        
        self.assertFalse(self.sistema_iot.validar_mensaje_iot(mensaje_invalido))
        
        # Mensaje inválido (valor no numérico)
        mensaje_invalido2 = {
            'sensor_id': 'sensor_001',
            'tipo': 'temperatura',
            'timestamp': datetime.now().isoformat(),
            'valor': 'no_numerico'
        }
        
        self.assertFalse(self.sistema_iot.validar_mensaje_iot(mensaje_invalido2))
    
    def test_obtener_estado_sistema_iot(self):
        """Test de obtención del estado del sistema IoT"""
        # Crear red de sensores
        self.sistema_iot.crear_red_sensores({})
        
        estado = self.sistema_iot.obtener_estado_sistema_iot()
        
        self.assertIsInstance(estado, dict)
        self.assertIn('timestamp', estado)
        self.assertIn('sistema', estado)
        self.assertIn('version', estado)
        self.assertIn('gateways', estado)
        self.assertIn('sensores', estado)
        self.assertIn('total_lecturas', estado)
        self.assertIn('estadisticas', estado)
        self.assertIn('estado_gateways', estado)
        
        self.assertEqual(estado['sistema'], 'METGO 3D IoT')
        self.assertGreater(estado['gateways'], 0)
        self.assertGreater(estado['sensores'], 0)
    
    def test_generar_reporte_iot(self):
        """Test de generación de reporte IoT"""
        # Crear red de sensores y generar algunos datos
        self.sistema_iot.crear_red_sensores({})
        self.sistema_iot.iniciar_monitoreo_iot(duracion_minutos=1)
        
        reporte = self.sistema_iot.generar_reporte_iot()
        
        self.assertIsInstance(reporte, str)
        self.assertGreater(len(reporte), 0)
        
        # Verificar que el archivo existe
        self.assertTrue(Path(reporte).exists())
        
        # Verificar contenido del reporte
        with open(reporte, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        
        self.assertIn('timestamp', contenido)
        self.assertIn('sistema', contenido)
        self.assertIn('resumen', contenido)
        self.assertIn('estado_sistema', contenido)
        self.assertIn('recomendaciones', contenido)

class TestSistemaIoTIntegracion(unittest.TestCase):
    """Tests de integración para el sistema IoT"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para tests de integración"""
        if not IOT_AVAILABLE:
            raise unittest.SkipTest("Módulo IoT no disponible")
        
        cls.sistema_iot = SistemaIoTMETGO()
    
    def test_pipeline_completo_iot(self):
        """Test del pipeline completo del sistema IoT"""
        # 1. Crear red de sensores
        resultado_red = self.sistema_iot.crear_red_sensores({})
        self.assertTrue(resultado_red)
        
        # 2. Iniciar monitoreo
        resultado_monitoreo = self.sistema_iot.iniciar_monitoreo_iot(duracion_minutos=1)
        self.assertTrue(resultado_monitoreo)
        
        # 3. Procesar datos
        resultado_procesamiento = self.sistema_iot.procesar_datos_iot()
        self.assertTrue(resultado_procesamiento)
        
        # 4. Obtener estado del sistema
        estado = self.sistema_iot.obtener_estado_sistema_iot()
        self.assertIsInstance(estado, dict)
        self.assertGreater(estado['total_lecturas'], 0)
        
        # 5. Generar reporte
        reporte = self.sistema_iot.generar_reporte_iot()
        self.assertIsInstance(reporte, str)
        self.assertTrue(Path(reporte).exists())
    
    def test_rendimiento_sistema_iot(self):
        """Test de rendimiento del sistema IoT"""
        import time
        
        # Crear red de sensores
        self.sistema_iot.crear_red_sensores({})
        
        # Medir tiempo de monitoreo
        inicio = time.time()
        self.sistema_iot.iniciar_monitoreo_iot(duracion_minutos=1)
        fin = time.time()
        
        duracion = fin - inicio
        self.assertLess(duracion, 120)  # Menos de 2 minutos
        
        print(f"Tiempo de monitoreo IoT: {duracion:.2f} segundos")
        
        # Verificar que se generaron datos
        self.assertGreater(len(self.sistema_iot.datos_iot), 0)
        
        # Verificar estadísticas
        self.assertIn('total_lecturas', self.sistema_iot.estadisticas)
        self.assertGreater(self.sistema_iot.estadisticas['total_lecturas'], 0)
    
    def test_escalabilidad_sistema_iot(self):
        """Test de escalabilidad del sistema IoT"""
        # Crear red de sensores
        self.sistema_iot.crear_red_sensores({})
        
        # Verificar que se crearon múltiples gateways y sensores
        self.assertGreater(len(self.sistema_iot.gateways), 1)
        self.assertGreater(len(self.sistema_iot.sensores), 5)
        
        # Verificar que cada gateway tiene múltiples sensores
        for gateway in self.sistema_iot.gateways.values():
            self.assertGreater(len(gateway.sensores), 1)
        
        # Verificar tipos de sensores
        tipos_sensores = set()
        for sensor in self.sistema_iot.sensores.values():
            tipos_sensores.add(sensor.tipo)
        
        self.assertGreaterEqual(len(tipos_sensores), 5)  # Al menos 5 tipos diferentes

if __name__ == '__main__':
    # Configurar el runner de tests
    unittest.main(verbosity=2)
