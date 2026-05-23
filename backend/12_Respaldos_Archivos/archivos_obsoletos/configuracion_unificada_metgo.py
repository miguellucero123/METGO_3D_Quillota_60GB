#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚙️ CONFIGURACIÓN UNIFICADA METGO 3D
Sistema Meteorológico Agrícola Quillota - Configuración Centralizada
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class ConfiguracionUnificadaMETGO:
    """Clase para gestión de configuración unificada del sistema METGO 3D"""
    
    def __init__(self):
        self.directorio_config = Path("config/unificado")
        self.directorio_config.mkdir(parents=True, exist_ok=True)
        
        # Configuración base del sistema
        self.configuracion_base = {
            'sistema': {
                'nombre': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'descripcion': 'Sistema integrado avanzado para análisis meteorológico agrícola',
                'autor': 'Sistema METGO 3D',
                'fecha_creacion': '2024-01-01T00:00:00',
                'ultima_actualizacion': datetime.now().isoformat(),
                'entorno': 'produccion',  # desarrollo, testing, produccion
                'debug': False,
                'log_level': 'INFO'
            },
            
            'quillota': {
                'coordenadas': {
                    'latitud': -32.8833,
                    'longitud': -71.2333,
                    'altitud': 127
                },
                'zona_horaria': 'America/Santiago',
                'region': 'Valparaíso',
                'pais': 'Chile',
                'clima': 'Mediterráneo',
                'estaciones_meteorologicas': [
                    {'nombre': 'Centro', 'latitud': -32.8833, 'longitud': -71.2333, 'altitud': 127},
                    {'nombre': 'Norte', 'latitud': -32.8500, 'longitud': -71.2000, 'altitud': 150},
                    {'nombre': 'Sur', 'latitud': -32.9200, 'longitud': -71.2500, 'altitud': 100},
                    {'nombre': 'Este', 'latitud': -32.8800, 'longitud': -71.1800, 'altitud': 200},
                    {'nombre': 'Oeste', 'latitud': -32.8900, 'longitud': -71.2800, 'altitud': 80}
                ]
            },
            
            'meteorologia': {
                'variables': [
                    'temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion',
                    'humedad', 'presion', 'radiacion_solar', 'punto_rocio'
                ],
                'unidades': {
                    'temperatura': '°C',
                    'precipitacion': 'mm',
                    'viento_velocidad': 'm/s',
                    'viento_direccion': '°',
                    'humedad': '%',
                    'presion': 'hPa',
                    'radiacion_solar': 'W/m²',
                    'punto_rocio': '°C'
                },
                'umbrales': {
                    'temperatura': {'min': -5, 'max': 40},
                    'precipitacion': {'min': 0, 'max': 100},
                    'viento_velocidad': {'min': 0, 'max': 50},
                    'humedad': {'min': 0, 'max': 100},
                    'presion': {'min': 950, 'max': 1050},
                    'radiacion_solar': {'min': 0, 'max': 1200},
                    'punto_rocio': {'min': -20, 'max': 30}
                },
                'frecuencia_muestreo': 3600,  # segundos
                'retencion_datos': 365  # días
            },
            
            'agricultura': {
                'cultivos_principales': [
                    'paltos', 'citricos', 'vides', 'hortalizas', 'cereales'
                ],
                'indices': [
                    'grados_dia', 'confort_termico', 'necesidad_riego', 
                    'riesgo_heladas', 'riesgo_hongos'
                ],
                'umbrales_criticos': {
                    'heladas': {'temperatura_minima': 0},
                    'calor_extremo': {'temperatura_maxima': 35},
                    'sequia': {'dias_sin_lluvia': 30},
                    'humedad_excesiva': {'humedad_minima': 90}
                },
                'estaciones_fenologicas': {
                    'invierno': [6, 7, 8],
                    'primavera': [9, 10, 11],
                    'verano': [12, 1, 2],
                    'otono': [3, 4, 5]
                }
            },
            
            'alertas': {
                'niveles': ['critica', 'alta', 'media', 'baja'],
                'canales': ['email', 'sms', 'push', 'webhook'],
                'configuracion': {
                    'critica': {
                        'tiempo_respuesta': 5,  # minutos
                        'canales': ['email', 'sms', 'push']
                    },
                    'alta': {
                        'tiempo_respuesta': 15,
                        'canales': ['email', 'push']
                    },
                    'media': {
                        'tiempo_respuesta': 60,
                        'canales': ['email']
                    },
                    'baja': {
                        'tiempo_respuesta': 240,
                        'canales': ['webhook']
                    }
                }
            },
            
            'apis': {
                'openmeteo': {
                    'url_base': 'https://api.open-meteo.com/v1/forecast',
                    'parametros': {
                        'latitude': -32.8833,
                        'longitude': -71.2333,
                        'hourly': 'temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,shortwave_radiation,dewpoint_2m',
                        'timezone': 'America/Santiago'
                    },
                    'timeout': 30,
                    'max_reintentos': 3,
                    'intervalo_reintentos': 5
                },
                'servicios_internos': {
                    'puerto_principal': 5000,
                    'puerto_meteorologia': 5001,
                    'puerto_agricola': 5002,
                    'puerto_alertas': 5003,
                    'puerto_iot': 5004,
                    'puerto_ml': 5005,
                    'puerto_visualizacion': 5006,
                    'puerto_reportes': 5007,
                    'puerto_configuracion': 5008,
                    'puerto_monitoreo': 5009
                }
            },
            
            'iot': {
                'protocolos': ['mqtt', 'http', 'udp'],
                'configuracion_mqtt': {
                    'broker': 'localhost',
                    'puerto': 1883,
                    'topic_base': 'metgo3d',
                    'qos': 1,
                    'retain': True
                },
                'sensores': {
                    'tipos': [
                        'temperatura', 'humedad', 'precipitacion', 'viento_velocidad',
                        'viento_direccion', 'presion', 'radiacion_solar', 'punto_rocio'
                    ],
                    'frecuencia_lectura': 60,  # segundos
                    'bateria_minima': 20,  # porcentaje
                    'senal_minima': 30  # porcentaje
                },
                'gateways': {
                    'frecuencia_comunicacion': 300,  # segundos
                    'timeout': 30,
                    'max_reintentos': 3
                }
            },
            
            'machine_learning': {
                'modelos': {
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
                        'modelos': ['lstm', 'transformer', 'random_forest', 'gradient_boosting'],
                        'weights': [0.3, 0.3, 0.2, 0.2]
                    }
                },
                'entrenamiento': {
                    'frecuencia': 'diaria',
                    'hora': '02:00',
                    'validacion_cruzada': True,
                    'optimizacion_hiperparametros': True
                },
                'predicciones': {
                    'horizonte': 24,  # horas
                    'frecuencia': 'horaria',
                    'confianza_minima': 0.7
                }
            },
            
            'visualizacion': {
                'tipos': ['2d', '3d', 'interactiva', 'estatica'],
                'formatos': ['png', 'pdf', 'html', 'svg'],
                'colores_quillota': {
                    'primario': '#2E8B57',
                    'secundario': '#FFD700',
                    'acento': '#FF6347',
                    'neutro': '#708090',
                    'fondo': '#F5F5DC'
                },
                'dashboards': {
                    'temperatura_3d': True,
                    'viento_3d': True,
                    'multivariable_3d': True,
                    'dashboard_interactivo': True,
                    'estacional_3d': True,
                    'correlaciones_3d': True
                }
            },
            
            'analisis': {
                'estacionalidad': {
                    'ventana_movil': 30,  # días
                    'componentes_fourier': 10
                },
                'correlaciones': {
                    'metodo': 'pearson',
                    'umbral_significancia': 0.05
                },
                'clustering': {
                    'algoritmos': ['kmeans', 'dbscan'],
                    'max_clusters': 8,
                    'min_samples': 5
                },
                'anomalias': {
                    'metodos': ['zscore', 'iqr', 'percentiles'],
                    'umbral_zscore': 3,
                    'percentil_inferior': 1,
                    'percentil_superior': 99
                },
                'pca': {
                    'varianza_explicada': 0.95,
                    'componentes_maximos': 10
                }
            },
            
            'base_datos': {
                'tipo': 'sqlite',  # sqlite, postgresql, mysql
                'archivo': 'data/metgo3d.db',
                'configuracion': {
                    'timeout': 30,
                    'check_same_thread': False
                },
                'tablas': {
                    'datos_meteorologicos': {
                        'columnas': [
                            'id INTEGER PRIMARY KEY AUTOINCREMENT',
                            'timestamp DATETIME NOT NULL',
                            'temperatura REAL',
                            'precipitacion REAL',
                            'viento_velocidad REAL',
                            'viento_direccion REAL',
                            'humedad REAL',
                            'presion REAL',
                            'radiacion_solar REAL',
                            'punto_rocio REAL'
                        ],
                        'indices': ['timestamp', 'temperatura', 'precipitacion']
                    },
                    'alertas': {
                        'columnas': [
                            'id INTEGER PRIMARY KEY AUTOINCREMENT',
                            'timestamp DATETIME NOT NULL',
                            'tipo VARCHAR(50) NOT NULL',
                            'nivel VARCHAR(20) NOT NULL',
                            'mensaje TEXT NOT NULL',
                            'activa BOOLEAN DEFAULT TRUE'
                        ],
                        'indices': ['timestamp', 'tipo', 'nivel', 'activa']
                    },
                    'predicciones_ml': {
                        'columnas': [
                            'id INTEGER PRIMARY KEY AUTOINCREMENT',
                            'timestamp DATETIME NOT NULL',
                            'modelo VARCHAR(50) NOT NULL',
                            'variable VARCHAR(50) NOT NULL',
                            'prediccion REAL NOT NULL',
                            'confianza REAL',
                            'horizonte INTEGER'
                        ],
                        'indices': ['timestamp', 'modelo', 'variable']
                    }
                }
            },
            
            'logging': {
                'nivel': 'INFO',
                'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'archivos': {
                    'principal': 'logs/metgo3d.log',
                    'errores': 'logs/errores.log',
                    'debug': 'logs/debug.log',
                    'apis': 'logs/apis.log',
                    'iot': 'logs/iot.log',
                    'ml': 'logs/ml.log'
                },
                'rotacion': {
                    'max_bytes': 10485760,  # 10MB
                    'backup_count': 5
                }
            },
            
            'seguridad': {
                'autenticacion': {
                    'habilitada': True,
                    'metodo': 'jwt',  # jwt, oauth2, basic
                    'tiempo_expiracion': 3600  # segundos
                },
                'autorizacion': {
                    'roles': ['admin', 'usuario', 'lector'],
                    'permisos': {
                        'admin': ['read', 'write', 'delete', 'configure'],
                        'usuario': ['read', 'write'],
                        'lector': ['read']
                    }
                },
                'encriptacion': {
                    'algoritmo': 'AES-256',
                    'clave_maestra': 'metgo3d_2024_secure_key'
                }
            },
            
            'monitoreo': {
                'metricas': {
                    'sistema': ['cpu', 'memoria', 'disco', 'red'],
                    'aplicacion': ['requests', 'errores', 'tiempo_respuesta'],
                    'negocio': ['alertas', 'predicciones', 'usuarios_activos']
                },
                'alertas_sistema': {
                    'cpu_alto': 80,  # porcentaje
                    'memoria_alta': 85,
                    'disco_lleno': 90,
                    'tiempo_respuesta_alto': 5  # segundos
                },
                'reportes': {
                    'frecuencia': 'diaria',
                    'hora': '08:00',
                    'formato': 'pdf',
                    'destinatarios': ['admin@metgo3d.cl']
                }
            },
            
            'backup': {
                'frecuencia': 'diaria',
                'hora': '03:00',
                'retencion': 30,  # días
                'destinos': [
                    'local',
                    'nube'
                ],
                'archivos': [
                    'data/',
                    'config/',
                    'logs/',
                    'modelos_ml/'
                ]
            },
            
            'performance': {
                'cache': {
                    'habilitada': True,
                    'tiempo_vida': 3600,  # segundos
                    'max_elementos': 1000
                },
                'paralelismo': {
                    'habilitado': True,
                    'max_workers': 4,
                    'timeout': 300  # segundos
                },
                'optimizacion': {
                    'compresion_datos': True,
                    'indices_bd': True,
                    'lazy_loading': True
                }
            }
        }
        
        # Cargar configuración existente o crear nueva
        self.configuracion = self.cargar_configuracion()
    
    def cargar_configuracion(self) -> Dict:
        """Cargar configuración desde archivo"""
        try:
            archivo_config = self.directorio_config / "configuracion_unificada.yaml"
            
            if archivo_config.exists():
                with open(archivo_config, 'r', encoding='utf-8') as f:
                    configuracion = yaml.safe_load(f)
                print(f"✅ Configuración cargada desde {archivo_config}")
                return configuracion
            else:
                print("⚠️ Archivo de configuración no encontrado, creando configuración por defecto")
                return self.crear_configuracion_default()
                
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return self.crear_configuracion_default()
    
    def crear_configuracion_default(self) -> Dict:
        """Crear configuración por defecto"""
        try:
            # Actualizar timestamp
            self.configuracion_base['sistema']['ultima_actualizacion'] = datetime.now().isoformat()
            
            # Guardar configuración
            self.guardar_configuracion(self.configuracion_base)
            
            print("✅ Configuración por defecto creada")
            return self.configuracion_base
            
        except Exception as e:
            print(f"❌ Error creando configuración por defecto: {e}")
            return {}
    
    def guardar_configuracion(self, configuracion: Dict = None) -> bool:
        """Guardar configuración a archivo"""
        try:
            if configuracion is None:
                configuracion = self.configuracion
            
            # Actualizar timestamp
            configuracion['sistema']['ultima_actualizacion'] = datetime.now().isoformat()
            
            # Guardar como YAML
            archivo_yaml = self.directorio_config / "configuracion_unificada.yaml"
            with open(archivo_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(configuracion, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            # Guardar como JSON
            archivo_json = self.directorio_config / "configuracion_unificada.json"
            with open(archivo_json, 'w', encoding='utf-8') as f:
                json.dump(configuracion, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración guardada en {archivo_yaml} y {archivo_json}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def obtener_configuracion(self, seccion: str = None) -> Dict:
        """Obtener configuración completa o de una sección específica"""
        try:
            if seccion is None:
                return self.configuracion
            else:
                return self.configuracion.get(seccion, {})
                
        except Exception as e:
            print(f"❌ Error obteniendo configuración: {e}")
            return {}
    
    def actualizar_configuracion(self, seccion: str, datos: Dict) -> bool:
        """Actualizar configuración de una sección específica"""
        try:
            if seccion in self.configuracion:
                self.configuracion[seccion].update(datos)
                self.guardar_configuracion()
                print(f"✅ Configuración de {seccion} actualizada")
                return True
            else:
                print(f"❌ Sección {seccion} no encontrada")
                return False
                
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")
            return False
    
    def validar_configuracion(self) -> Dict:
        """Validar configuración del sistema"""
        try:
            errores = []
            advertencias = []
            
            # Validar secciones requeridas
            secciones_requeridas = [
                'sistema', 'quillota', 'meteorologia', 'agricultura', 
                'alertas', 'apis', 'iot', 'machine_learning'
            ]
            
            for seccion in secciones_requeridas:
                if seccion not in self.configuracion:
                    errores.append(f"Sección requerida faltante: {seccion}")
            
            # Validar configuración de Quillota
            if 'quillota' in self.configuracion:
                quillota = self.configuracion['quillota']
                if 'coordenadas' not in quillota:
                    errores.append("Coordenadas de Quillota no configuradas")
                else:
                    coords = quillota['coordenadas']
                    if not (-90 <= coords.get('latitud', 0) <= 90):
                        errores.append("Latitud de Quillota inválida")
                    if not (-180 <= coords.get('longitud', 0) <= 180):
                        errores.append("Longitud de Quillota inválida")
            
            # Validar umbrales meteorológicos
            if 'meteorologia' in self.configuracion:
                meteorologia = self.configuracion['meteorologia']
                if 'umbrales' in meteorologia:
                    for variable, umbrales in meteorologia['umbrales'].items():
                        if 'min' in umbrales and 'max' in umbrales:
                            if umbrales['min'] >= umbrales['max']:
                                errores.append(f"Umbrales inválidos para {variable}")
            
            # Validar configuración de APIs
            if 'apis' in self.configuracion:
                apis = self.configuracion['apis']
                if 'servicios_internos' in apis:
                    puertos = apis['servicios_internos']
                    puertos_unicos = set(puertos.values())
                    if len(puertos_unicos) != len(puertos):
                        errores.append("Puertos duplicados en servicios internos")
            
            # Validar configuración de ML
            if 'machine_learning' in self.configuracion:
                ml = self.configuracion['machine_learning']
                if 'modelos' in ml:
                    for modelo, config in ml['modelos'].items():
                        if 'epochs' in config and config['epochs'] <= 0:
                            errores.append(f"Épocas inválidas para modelo {modelo}")
            
            # Advertencias
            if self.configuracion.get('sistema', {}).get('debug', False):
                advertencias.append("Modo debug habilitado en producción")
            
            if self.configuracion.get('seguridad', {}).get('autenticacion', {}).get('habilitada', False) == False:
                advertencias.append("Autenticación deshabilitada")
            
            return {
                'valida': len(errores) == 0,
                'errores': errores,
                'advertencias': advertencias,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return {'valida': False, 'errores': [str(e)], 'advertencias': []}
    
    def generar_configuracion_entorno(self, entorno: str) -> Dict:
        """Generar configuración específica para un entorno"""
        try:
            configuracion_entorno = self.configuracion.copy()
            
            if entorno == 'desarrollo':
                configuracion_entorno['sistema']['debug'] = True
                configuracion_entorno['sistema']['log_level'] = 'DEBUG'
                configuracion_entorno['machine_learning']['entrenamiento']['frecuencia'] = 'manual'
                configuracion_entorno['apis']['openmeteo']['timeout'] = 10
                
            elif entorno == 'testing':
                configuracion_entorno['sistema']['debug'] = True
                configuracion_entorno['sistema']['log_level'] = 'WARNING'
                configuracion_entorno['base_datos']['archivo'] = 'data/metgo3d_test.db'
                configuracion_entorno['logging']['archivos']['principal'] = 'logs/metgo3d_test.log'
                
            elif entorno == 'produccion':
                configuracion_entorno['sistema']['debug'] = False
                configuracion_entorno['sistema']['log_level'] = 'INFO'
                configuracion_entorno['seguridad']['autenticacion']['habilitada'] = True
                configuracion_entorno['performance']['cache']['habilitada'] = True
                configuracion_entorno['performance']['paralelismo']['habilitado'] = True
            
            # Actualizar timestamp
            configuracion_entorno['sistema']['ultima_actualizacion'] = datetime.now().isoformat()
            configuracion_entorno['sistema']['entorno'] = entorno
            
            return configuracion_entorno
            
        except Exception as e:
            print(f"❌ Error generando configuración de entorno: {e}")
            return {}
    
    def exportar_configuracion(self, formato: str = 'yaml') -> str:
        """Exportar configuración en formato específico"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if formato.lower() == 'yaml':
                archivo = self.directorio_config / f"configuracion_exportada_{timestamp}.yaml"
                with open(archivo, 'w', encoding='utf-8') as f:
                    yaml.dump(self.configuracion, f, default_flow_style=False, allow_unicode=True, indent=2)
                    
            elif formato.lower() == 'json':
                archivo = self.directorio_config / f"configuracion_exportada_{timestamp}.json"
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.configuracion, f, indent=2, ensure_ascii=False)
                    
            else:
                raise ValueError(f"Formato no soportado: {formato}")
            
            print(f"✅ Configuración exportada a {archivo}")
            return str(archivo)
            
        except Exception as e:
            print(f"❌ Error exportando configuración: {e}")
            return ""
    
    def importar_configuracion(self, archivo: str) -> bool:
        """Importar configuración desde archivo"""
        try:
            archivo_path = Path(archivo)
            
            if not archivo_path.exists():
                print(f"❌ Archivo no encontrado: {archivo}")
                return False
            
            if archivo_path.suffix.lower() == '.yaml' or archivo_path.suffix.lower() == '.yml':
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    configuracion_importada = yaml.safe_load(f)
                    
            elif archivo_path.suffix.lower() == '.json':
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    configuracion_importada = json.load(f)
                    
            else:
                print(f"❌ Formato de archivo no soportado: {archivo_path.suffix}")
                return False
            
            # Validar configuración importada
            config_temp = ConfiguracionUnificadaMETGO()
            config_temp.configuracion = configuracion_importada
            validacion = config_temp.validar_configuracion()
            
            if validacion['valida']:
                self.configuracion = configuracion_importada
                self.guardar_configuracion()
                print(f"✅ Configuración importada desde {archivo}")
                return True
            else:
                print(f"❌ Configuración inválida: {validacion['errores']}")
                return False
                
        except Exception as e:
            print(f"❌ Error importando configuración: {e}")
            return False
    
    def generar_reporte_configuracion(self) -> str:
        """Generar reporte de configuración"""
        try:
            print("📋 Generando reporte de configuración...")
            
            # Validar configuración
            validacion = self.validar_configuracion()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Configuración Unificada',
                'version': self.configuracion.get('sistema', {}).get('version', 'N/A'),
                'resumen': {
                    'total_secciones': len(self.configuracion),
                    'configuracion_valida': validacion['valida'],
                    'total_errores': len(validacion['errores']),
                    'total_advertencias': len(validacion['advertencias'])
                },
                'validacion': validacion,
                'secciones': list(self.configuracion.keys()),
                'configuracion': self.configuracion,
                'recomendaciones': [
                    "Revisar regularmente la configuración del sistema",
                    "Validar configuración antes de cambios en producción",
                    "Mantener respaldos de configuraciones estables",
                    "Documentar cambios en la configuración",
                    "Monitorear el rendimiento según la configuración"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"configuracion_unificada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte de configuración generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"❌ Error generando reporte de configuración: {e}")
            return ""

def main():
    """Función principal de configuración unificada"""
    print("⚙️ CONFIGURACIÓN UNIFICADA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Configuración Centralizada")
    print("=" * 80)
    
    try:
        # Crear instancia de configuración
        config = ConfiguracionUnificadaMETGO()
        
        # Mostrar resumen
        print(f"\n📊 Resumen de configuración:")
        print(f"   Total de secciones: {len(config.configuracion)}")
        print(f"   Versión del sistema: {config.configuracion.get('sistema', {}).get('version', 'N/A')}")
        print(f"   Entorno: {config.configuracion.get('sistema', {}).get('entorno', 'N/A')}")
        
        # Validar configuración
        print(f"\n🔍 Validando configuración...")
        validacion = config.validar_configuracion()
        
        if validacion['valida']:
            print(f"✅ Configuración válida")
        else:
            print(f"❌ Configuración inválida:")
            for error in validacion['errores']:
                print(f"   - {error}")
        
        if validacion['advertencias']:
            print(f"⚠️ Advertencias:")
            for advertencia in validacion['advertencias']:
                print(f"   - {advertencia}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = config.generar_reporte_configuracion()
        
        if reporte:
            print(f"\n✅ Configuración unificada completada exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print(f"\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en configuración unificada: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

