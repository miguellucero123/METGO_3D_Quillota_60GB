#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE CONFIGURACIÓN DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import yaml
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE CONFIGURACIÓN DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito")
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia")
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class GestorConfiguracion:
    """Clase para gestión de configuración del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_config': 'config',
            'archivo_config_principal': 'config/config.yaml',
            'archivo_config_sistema': 'config/sistema.yaml',
            'archivo_config_datos': 'config/datos.yaml',
            'archivo_config_logs': 'config/logs.yaml',
            'archivo_config_monitoreo': 'config/monitoreo.yaml',
            'archivo_config_alertas': 'config/alertas.yaml',
            'archivo_config_respaldos': 'config/respaldos.yaml',
            'archivo_config_seguridad': 'config/seguridad.yaml',
            'archivo_config_usuarios': 'config/usuarios.yaml',
            'archivo_config_auditoria': 'config/auditoria.yaml',
            'archivo_config_optimizacion': 'config/optimizacion.yaml',
            'archivo_config_tareas': 'config/tareas.yaml',
            'archivo_config_cicd': 'config/cicd.yaml',
            'archivo_config_documentacion': 'config/documentacion.yaml'
        }
        
        self.configuraciones = {}
        self.archivos_config = [
            'config.yaml',
            'sistema.yaml',
            'datos.yaml',
            'logs.yaml',
            'monitoreo.yaml',
            'alertas.yaml',
            'respaldos.yaml',
            'seguridad.yaml',
            'usuarios.yaml',
            'auditoria.yaml',
            'optimizacion.yaml',
            'tareas.yaml',
            'cicd.yaml',
            'documentacion.yaml'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración del sistema"""
        try:
            print_info("Cargando configuración del sistema...")
            
            # Cargar configuración principal
            config_principal = self.cargar_archivo_config('config.yaml')
            if config_principal:
                self.configuraciones['principal'] = config_principal
                print_success("Configuración principal cargada")
            else:
                print_warning("Configuración principal no encontrada")
            
            # Cargar todas las configuraciones
            for archivo in self.archivos_config:
                config = self.cargar_archivo_config(archivo)
                if config:
                    nombre = archivo.replace('.yaml', '')
                    self.configuraciones[nombre] = config
                    print_success(f"Configuración {nombre} cargada")
                else:
                    print_warning(f"Configuración {archivo} no encontrada")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def cargar_archivo_config(self, archivo):
        """Cargar archivo de configuración"""
        try:
            archivo_path = Path(f"config/{archivo}")
            if not archivo_path.exists():
                return None
            
            with open(archivo_path, 'r', encoding='utf-8') as f:
                if archivo.endswith('.yaml') or archivo.endswith('.yml'):
                    return yaml.safe_load(f)
                elif archivo.endswith('.json'):
                    return json.load(f)
                else:
                    return None
            
        except Exception as e:
            print_error(f"Error cargando {archivo}: {e}")
            return None
    
    def crear_estructura_configuracion(self):
        """Crear estructura de configuración"""
        try:
            print_info("Creando estructura de configuración...")
            
            # Crear directorio principal
            config_dir = Path(self.configuracion['directorio_config'])
            config_dir.mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_configuracion()
            
            print_success("Estructura de configuración creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_configuracion(self):
        """Crear archivos de configuración"""
        try:
            print_info("Creando archivos de configuración...")
            
            # config/config.yaml
            config_principal = {
                'sistema': {
                    'nombre': 'METGO 3D',
                    'version': '2.0',
                    'descripcion': 'Sistema Meteorológico Agrícola Quillota',
                    'autor': 'Sistema METGO 3D',
                    'fecha_creacion': datetime.now().isoformat()
                },
                'quillota': {
                    'coordenadas': {
                        'latitud': -32.8833,
                        'longitud': -71.2333
                    },
                    'altitud': 127,
                    'zona_horaria': 'America/Santiago'
                },
                'meteorologia': {
                    'umbrales': {
                        'temperatura': {
                            'min': -5,
                            'max': 40
                        },
                        'precipitacion': {
                            'min': 0,
                            'max': 100
                        },
                        'viento': {
                            'min': 0,
                            'max': 50
                        },
                        'humedad': {
                            'min': 0,
                            'max': 100
                        }
                    }
                },
                'sistema': {
                    'version': '2.0',
                    'debug': False,
                    'log_level': 'INFO',
                    'timeout': 300
                }
            }
            
            self.guardar_archivo_config('config.yaml', config_principal)
            
            # config/sistema.yaml
            config_sistema = {
                'sistema': {
                    'nombre': 'METGO 3D',
                    'version': '2.0',
                    'descripcion': 'Sistema Meteorológico Agrícola Quillota',
                    'autor': 'Sistema METGO 3D',
                    'fecha_creacion': datetime.now().isoformat()
                },
                'modulos': [
                    'configuracion',
                    'datos',
                    'notebooks',
                    'servicios',
                    'monitoreo',
                    'respaldos',
                    'alertas',
                    'logs',
                    'reportes',
                    'seguridad',
                    'usuarios',
                    'auditoria',
                    'optimizacion'
                ],
                'estados': {
                    'iniciado': False,
                    'configurado': False,
                    'datos_cargados': False,
                    'notebooks_ejecutados': False,
                    'servicios_activos': False,
                    'monitoreo_activo': False,
                    'respaldos_activos': False,
                    'alertas_configuradas': False,
                    'logs_configurados': False,
                    'reportes_configurados': False,
                    'seguridad_configurada': False,
                    'usuarios_configurados': False,
                    'auditoria_configurada': False,
                    'optimizacion_activa': False
                },
                'configuracion': {
                    'timeout': 300,
                    'debug': False,
                    'log_level': 'INFO'
                }
            }
            
            self.guardar_archivo_config('sistema.yaml', config_sistema)
            
            # config/datos.yaml
            config_datos = {
                'datos': {
                    'directorio': 'data',
                    'formatos_soportados': ['json', 'csv', 'xlsx', 'parquet', 'hdf5'],
                    'compresion': True,
                    'encriptacion': False,
                    'validacion': True,
                    'limpieza': True,
                    'transformacion': True
                },
                'tipos_datos': [
                    'meteorologicos',
                    'agricolas',
                    'sensores',
                    'satelitales',
                    'modelos',
                    'calibracion',
                    'validacion'
                ],
                'operaciones': [
                    'cargar',
                    'guardar',
                    'validar',
                    'limpiar',
                    'transformar',
                    'filtrar',
                    'agregar',
                    'exportar'
                ]
            }
            
            self.guardar_archivo_config('datos.yaml', config_datos)
            
            # config/logs.yaml
            config_logs = {
                'logs': {
                    'directorio': 'logs',
                    'nivel': 'INFO',
                    'formato': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'rotacion': True,
                    'max_tamaño_mb': 10,
                    'max_archivos': 5,
                    'compresion': True,
                    'retencion_dias': 30
                },
                'tipos_logs': [
                    'sistema',
                    'aplicacion',
                    'meteorologico',
                    'seguridad',
                    'auditoria',
                    'errores',
                    'debug'
                ],
                'niveles_logs': [
                    'DEBUG',
                    'INFO',
                    'WARNING',
                    'ERROR',
                    'CRITICAL'
                ]
            }
            
            self.guardar_archivo_config('logs.yaml', config_logs)
            
            # config/monitoreo.yaml
            config_monitoreo = {
                'monitoreo': {
                    'directorio': 'monitoreo',
                    'intervalo': 60,
                    'umbrales': {
                        'cpu': 80,
                        'memoria': 80,
                        'disco': 90,
                        'temperatura': 70
                    },
                    'alertas': {
                        'email': {
                            'habilitado': False,
                            'destinatarios': []
                        },
                        'webhook': {
                            'habilitado': False,
                            'url': ""
                        }
                    }
                },
                'metricas': {
                    'sistema': ['cpu', 'memoria', 'disco', 'red'],
                    'aplicacion': ['procesos', 'logs', 'errores', 'rendimiento'],
                    'meteorologia': ['datos', 'alertas', 'calidad', 'actualizaciones']
                }
            }
            
            self.guardar_archivo_config('monitoreo.yaml', config_monitoreo)
            
            # config/alertas.yaml
            config_alertas = {
                'alertas': {
                    'directorio': 'alertas',
                    'max_alertas': 1000,
                    'timeout': 30,
                    'tipos_alertas': [
                        'sistema',
                        'meteorologico',
                        'seguridad',
                        'rendimiento',
                        'datos',
                        'conexion',
                        'disco',
                        'memoria'
                    ],
                    'niveles_alertas': [
                        'info',
                        'warning',
                        'error',
                        'critical'
                    ]
                },
                'notificaciones': {
                    'email': {
                        'habilitado': False,
                        'servidor': 'smtp.gmail.com',
                        'puerto': 587,
                        'usuario': '',
                        'password': '',
                        'destinatarios': []
                    },
                    'webhook': {
                        'habilitado': False,
                        'url': ''
                    }
                }
            }
            
            self.guardar_archivo_config('alertas.yaml', config_alertas)
            
            # config/respaldos.yaml
            config_respaldos = {
                'respaldos': {
                    'directorio': 'respaldos',
                    'max_respaldos': 10,
                    'compresion': True,
                    'encriptacion': False,
                    'tipos_respaldos': [
                        'completo',
                        'datos',
                        'configuracion',
                        'logs',
                        'reportes',
                        'usuarios',
                        'auditoria'
                    ]
                },
                'programacion': {
                    'automatico': True,
                    'frecuencia': 'diaria',
                    'hora': '02:00',
                    'dias_semana': [1, 2, 3, 4, 5, 6, 7]
                }
            }
            
            self.guardar_archivo_config('respaldos.yaml', config_respaldos)
            
            # config/seguridad.yaml
            config_seguridad = {
                'seguridad': {
                    'directorio': 'seguridad',
                    'nivel_auditoria': 'alto',
                    'encriptacion': 'AES-256',
                    'hash_algorithm': 'SHA-256',
                    'auditorias': {
                        'archivos_sensibles': True,
                        'permisos': True,
                        'dependencias': True,
                        'configuracion': True,
                        'logs': True,
                        'accesos': True
                    }
                },
                'archivos_sensibles': [
                    '*.env',
                    '*.key',
                    '*.pem',
                    '*.p12',
                    'config/*.yaml',
                    'data/*.json'
                ]
            }
            
            self.guardar_archivo_config('seguridad.yaml', config_seguridad)
            
            # config/usuarios.yaml
            config_usuarios = {
                'usuarios': {
                    'directorio': 'usuarios',
                    'hash_algorithm': 'SHA-256',
                    'salt_length': 32,
                    'session_timeout': 3600,
                    'roles': [
                        'admin',
                        'operador',
                        'consultor',
                        'auditor'
                    ],
                    'permisos': {
                        'admin': ['crear', 'leer', 'actualizar', 'eliminar', 'configurar', 'auditar'],
                        'operador': ['crear', 'leer', 'actualizar'],
                        'consultor': ['leer'],
                        'auditor': ['leer', 'auditar']
                    }
                },
                'politicas': {
                    'longitud_minima_password': 8,
                    'complejidad_password': True,
                    'intentos_maximos': 3,
                    'bloqueo_temporal': 300
                }
            }
            
            self.guardar_archivo_config('usuarios.yaml', config_usuarios)
            
            # config/auditoria.yaml
            config_auditoria = {
                'auditoria': {
                    'directorio': 'auditoria',
                    'retencion_dias': 90,
                    'nivel_log': 'INFO',
                    'eventos': [
                        'login',
                        'logout',
                        'crear_usuario',
                        'eliminar_usuario',
                        'modificar_configuracion',
                        'ejecutar_analisis',
                        'generar_reporte',
                        'acceso_datos',
                        'error_sistema',
                        'alerta_seguridad'
                    ]
                },
                'campos_obligatorios': [
                    'timestamp',
                    'evento',
                    'usuario',
                    'ip',
                    'resultado'
                ]
            }
            
            self.guardar_archivo_config('auditoria.yaml', config_auditoria)
            
            # config/optimizacion.yaml
            config_optimizacion = {
                'optimizacion': {
                    'directorio': 'optimizacion',
                    'umbrales': {
                        'cpu': 80,
                        'memoria': 80,
                        'disco': 90
                    },
                    'limpieza': {
                        'archivos_temporales': True,
                        'logs_antiguos': True,
                        'cache': True,
                        'backups_antiguos': True
                    }
                }
            }
            
            self.guardar_archivo_config('optimizacion.yaml', config_optimizacion)
            
            # config/tareas.yaml
            config_tareas = {
                'tareas': {
                    'directorio': 'tareas',
                    'max_tareas': 100,
                    'timeout': 300,
                    'tipos_tareas': [
                        'analisis_meteorologico',
                        'generacion_reporte',
                        'respaldo_datos',
                        'limpieza_sistema',
                        'optimizacion',
                        'monitoreo',
                        'notificacion',
                        'actualizacion'
                    ]
                }
            }
            
            self.guardar_archivo_config('tareas.yaml', config_tareas)
            
            # config/cicd.yaml
            config_cicd = {
                'cicd': {
                    'plataforma': 'github',
                    'docker_registry': 'docker.io',
                    'imagen': 'metgo-3d',
                    'workflows': [
                        'ci-cd.yml',
                        'tests.yml',
                        'deploy.yml',
                        'security.yml'
                    ]
                }
            }
            
            self.guardar_archivo_config('cicd.yaml', config_cicd)
            
            # config/documentacion.yaml
            config_documentacion = {
                'documentacion': {
                    'directorio': 'docs',
                    'formato': 'rst',
                    'tema': 'sphinx_rtd_theme',
                    'idioma': 'es',
                    'version': '2.0',
                    'autor': 'Sistema METGO 3D',
                    'copyright': '2024'
                }
            }
            
            self.guardar_archivo_config('documentacion.yaml', config_documentacion)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def guardar_archivo_config(self, archivo, config):
        """Guardar archivo de configuración"""
        try:
            archivo_path = Path(f"config/{archivo}")
            archivo_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(archivo_path, 'w', encoding='utf-8') as f:
                if archivo.endswith('.yaml') or archivo.endswith('.yml'):
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                elif archivo.endswith('.json'):
                    json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando {archivo}: {e}")
            return False
    
    def validar_configuracion(self, archivo=None):
        """Validar configuración"""
        try:
            print_info("Validando configuración...")
            
            if archivo:
                # Validar archivo específico
                config = self.cargar_archivo_config(archivo)
                if config:
                    print_success(f"Configuración {archivo} válida")
                    return True
                else:
                    print_error(f"Configuración {archivo} no válida")
                    return False
            else:
                # Validar todas las configuraciones
                archivos_validos = 0
                archivos_invalidos = 0
                
                for archivo_config in self.archivos_config:
                    config = self.cargar_archivo_config(archivo_config)
                    if config:
                        archivos_validos += 1
                        print_success(f"Configuración {archivo_config} válida")
                    else:
                        archivos_invalidos += 1
                        print_error(f"Configuración {archivo_config} no válida")
                
                print(f"\n📊 Resumen de validación:")
                print(f"Archivos válidos: {archivos_validos}")
                print(f"Archivos inválidos: {archivos_invalidos}")
                
                return archivos_invalidos == 0
            
        except Exception as e:
            print_error(f"Error validando configuración: {e}")
            return False
    
    def listar_configuraciones(self):
        """Listar configuraciones"""
        try:
            print_info("Listando configuraciones...")
            
            if not self.configuraciones:
                print_warning("No hay configuraciones cargadas")
                return []
            
            print(f"\n📋 Configuraciones ({len(self.configuraciones)}):")
            print("-" * 80)
            print(f"{'Nombre':<20} {'Archivo':<25} {'Estado':<15} {'Tamaño':<10}")
            print("-" * 80)
            
            for nombre, config in self.configuraciones.items():
                archivo = f"{nombre}.yaml"
                estado = "Cargada" if config else "No cargada"
                tamaño = len(str(config)) if config else 0
                
                print(f"{nombre:<20} {archivo:<25} {estado:<15} {tamaño:<10}")
            
            return list(self.configuraciones.keys())
            
        except Exception as e:
            print_error(f"Error listando configuraciones: {e}")
            return []
    
    def actualizar_configuracion(self, archivo, config):
        """Actualizar configuración"""
        try:
            print_info(f"Actualizando configuración: {archivo}")
            
            # Validar configuración
            if not self.validar_configuracion(archivo):
                print_error(f"Configuración {archivo} no válida")
                return False
            
            # Guardar configuración
            if self.guardar_archivo_config(archivo, config):
                print_success(f"Configuración {archivo} actualizada")
                return True
            else:
                print_error(f"Error actualizando configuración {archivo}")
                return False
            
        except Exception as e:
            print_error(f"Error actualizando configuración: {e}")
            return False
    
    def generar_reporte_configuracion(self):
        """Generar reporte de configuración"""
        try:
            print_info("Generando reporte de configuración...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'configuraciones': {
                    'total': len(self.configuraciones),
                    'cargadas': len([c for c in self.configuraciones.values() if c]),
                    'no_cargadas': len([c for c in self.configuraciones.values() if not c])
                },
                'archivos_config': self.archivos_config,
                'detalles': self.configuraciones
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"configuracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de configuración generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de configuración:")
            print(f"Total: {reporte['configuraciones']['total']}")
            print(f"Cargadas: {reporte['configuraciones']['cargadas']}")
            print(f"No cargadas: {reporte['configuraciones']['no_cargadas']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de configuración"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE CONFIGURACIÓN - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de configuración")
    print("3. ✅ Validar configuración")
    print("4. 📋 Listar configuraciones")
    print("5. 🔄 Actualizar configuración")
    print("6. 📊 Generar reporte")
    print("7. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de configuración"""
    print_header()
    
    # Crear gestor de configuración
    gestor = GestorConfiguracion()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-7): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de configuración")
                if gestor.crear_estructura_configuracion():
                    print_success("Estructura de configuración creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Validando configuración")
                try:
                    archivo = input("Archivo (opcional): ").strip() or None
                    
                    if gestor.validar_configuracion(archivo):
                        print_success("Configuración válida")
                    else:
                        print_warning("Configuración con problemas")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Listando configuraciones")
                configuraciones = gestor.listar_configuraciones()
                if configuraciones:
                    print_success(f"Configuraciones listadas: {len(configuraciones)}")
                else:
                    print_warning("No hay configuraciones para mostrar")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Actualizando configuración")
                try:
                    archivo = input("Archivo: ").strip()
                    config = input("Configuración (JSON): ").strip()
                    
                    try:
                        config = json.loads(config)
                        if gestor.actualizar_configuracion(archivo, config):
                            print_success("Configuración actualizada correctamente")
                        else:
                            print_error("Error actualizando configuración")
                    except json.JSONDecodeError:
                        print_error("Configuración no válida")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Generando reporte de configuración")
                reporte = gestor.generar_reporte_configuracion()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_info("Saliendo del gestor de configuración...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-7.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de configuración interrumpida por el usuario")
            print_success("¡Hasta luego! 🌾")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            input("\n⏸️ Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)