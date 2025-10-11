#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE MONITOREO DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE MONITOREO DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️ {message}")

class GestorMonitoreo:
    """Clase para gestión de monitoreo del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_logs': 'logs',
            'directorio_metricas': 'metricas',
            'archivo_config': 'config/monitoreo.yaml',
            'intervalo': 60,  # segundos
            'umbral_cpu': 80,
            'umbral_memoria': 80,
            'umbral_disco': 90
        }
        
        self.metricas = {
            'sistema': ['cpu', 'memoria', 'disco', 'red'],
            'aplicacion': ['procesos', 'logs', 'errores', 'rendimiento'],
            'meteorologia': ['datos', 'alertas', 'calidad', 'actualizaciones']
        }
    
    def cargar_configuracion(self):
        """Cargar configuración de monitoreo"""
        try:
            print_info("Cargando configuración de monitoreo...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_monitoreo(self):
        """Crear estructura de monitoreo"""
        try:
            print_info("Creando estructura de monitoreo...")
            
            # Crear directorios
            logs_dir = Path(self.configuracion['directorio_logs'])
            logs_dir.mkdir(exist_ok=True)
            
            metricas_dir = Path(self.configuracion['directorio_metricas'])
            metricas_dir.mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            print_success("Estructura de monitoreo creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # config/monitoreo.yaml
            config_content = '''# Configuración de monitoreo del sistema METGO 3D

monitoreo:
  intervalo: 60  # segundos
  umbrales:
    cpu: 80
    memoria: 80
    disco: 90
    temperatura: 70
  
  alertas:
    email:
      habilitado: false
      destinatarios: []
    webhook:
      habilitado: false
      url: ""
  
  metricas:
    sistema:
      - cpu
      - memoria
      - disco
      - red
    aplicacion:
      - procesos
      - logs
      - errores
      - rendimiento
    meteorologia:
      - datos
      - alertas
      - calidad
      - actualizaciones
'''
            
            config_file = Path('config/monitoreo.yaml')
            config_file.parent.mkdir(exist_ok=True)
            config_file.write_text(config_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def obtener_metricas_sistema(self):
        """Obtener métricas del sistema"""
        try:
            print_info("Obteniendo métricas del sistema...")
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memoria = psutil.virtual_memory()
            memoria_percent = memoria.percent
            
            # Disco
            disco = psutil.disk_usage('/')
            disco_percent = disco.percent
            
            # Red
            red = psutil.net_io_counters()
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'porcentaje': cpu_percent,
                    'estado': 'OK' if cpu_percent < self.configuracion['umbral_cpu'] else 'ALERTA'
                },
                'memoria': {
                    'porcentaje': memoria_percent,
                    'total': memoria.total,
                    'disponible': memoria.available,
                    'estado': 'OK' if memoria_percent < self.configuracion['umbral_memoria'] else 'ALERTA'
                },
                'disco': {
                    'porcentaje': disco_percent,
                    'total': disco.total,
                    'disponible': disco.free,
                    'estado': 'OK' if disco_percent < self.configuracion['umbral_disco'] else 'ALERTA'
                },
                'red': {
                    'bytes_enviados': red.bytes_sent,
                    'bytes_recibidos': red.bytes_recv,
                    'paquetes_enviados': red.packets_sent,
                    'paquetes_recibidos': red.packets_recv
                }
            }
            
            print_success("Métricas del sistema obtenidas")
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas del sistema: {e}")
            return None
    
    def obtener_metricas_aplicacion(self):
        """Obtener métricas de la aplicación"""
        try:
            print_info("Obteniendo métricas de la aplicación...")
            
            # Procesos Python
            procesos_python = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        procesos_python.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Logs del sistema
            logs_dir = Path(self.configuracion['directorio_logs'])
            logs_files = list(logs_dir.glob('*.log'))
            
            # Errores recientes
            errores_recientes = 0
            for log_file in logs_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        errores_recientes += sum(1 for line in lines if 'ERROR' in line)
                except Exception:
                    pass
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'procesos': {
                    'python': len(procesos_python),
                    'detalles': procesos_python
                },
                'logs': {
                    'archivos': len(logs_files),
                    'errores_recientes': errores_recientes
                },
                'rendimiento': {
                    'estado': 'OK' if errores_recientes < 10 else 'ALERTA'
                }
            }
            
            print_success("Métricas de la aplicación obtenidas")
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas de la aplicación: {e}")
            return None
    
    def obtener_metricas_meteorologia(self):
        """Obtener métricas meteorológicas"""
        try:
            print_info("Obteniendo métricas meteorológicas...")
            
            # Verificar archivos de datos
            data_dir = Path('data')
            data_files = list(data_dir.glob('*.json')) if data_dir.exists() else []
            
            # Verificar reportes
            reportes_dir = Path('reportes')
            reportes_files = list(reportes_dir.glob('*.json')) if reportes_dir.exists() else []
            
            # Verificar alertas
            alertas_recientes = 0
            for reporte_file in reportes_files:
                try:
                    with open(reporte_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'alertas' in data:
                            alertas_recientes += len(data['alertas'])
                except Exception:
                    pass
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'datos': {
                    'archivos': len(data_files),
                    'ultima_actualizacion': max([f.stat().st_mtime for f in data_files]) if data_files else 0
                },
                'reportes': {
                    'archivos': len(reportes_files),
                    'alertas_recientes': alertas_recientes
                },
                'calidad': {
                    'estado': 'OK' if alertas_recientes < 5 else 'ALERTA'
                }
            }
            
            print_success("Métricas meteorológicas obtenidas")
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas meteorológicas: {e}")
            return None
    
    def generar_reporte_monitoreo(self):
        """Generar reporte de monitoreo"""
        try:
            print_info("Generando reporte de monitoreo...")
            
            # Obtener todas las métricas
            metricas_sistema = self.obtener_metricas_sistema()
            metricas_aplicacion = self.obtener_metricas_aplicacion()
            metricas_meteorologia = self.obtener_metricas_meteorologia()
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'metricas': {
                    'sistema': metricas_sistema,
                    'aplicacion': metricas_aplicacion,
                    'meteorologia': metricas_meteorologia
                },
                'resumen': {
                    'estado_general': 'OK',
                    'alertas': 0,
                    'errores': 0
                }
            }
            
            # Calcular estado general
            alertas = 0
            errores = 0
            
            if metricas_sistema:
                for key, value in metricas_sistema.items():
                    if isinstance(value, dict) and 'estado' in value:
                        if value['estado'] == 'ALERTA':
                            alertas += 1
            
            if metricas_aplicacion:
                if metricas_aplicacion['logs']['errores_recientes'] > 0:
                    errores += metricas_aplicacion['logs']['errores_recientes']
            
            reporte['resumen']['alertas'] = alertas
            reporte['resumen']['errores'] = errores
            reporte['resumen']['estado_general'] = 'ALERTA' if alertas > 0 or errores > 0 else 'OK'
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de monitoreo generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del monitoreo:")
            print(f"Estado general: {reporte['resumen']['estado_general']}")
            print(f"Alertas: {alertas}")
            print(f"Errores: {errores}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de monitoreo"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE MONITOREO - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de monitoreo")
    print("3. 💻 Monitorear sistema")
    print("4. 📱 Monitorear aplicación")
    print("5. 🌤️ Monitorear meteorología")
    print("6. 📊 Generar reporte completo")
    print("7. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de monitoreo"""
    print_header()
    
    # Crear gestor de monitoreo
    gestor = GestorMonitoreo()
    
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
                print_step("2", "Creando estructura de monitoreo")
                if gestor.crear_estructura_monitoreo():
                    print_success("Estructura de monitoreo creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Monitoreando sistema")
                metricas = gestor.obtener_metricas_sistema()
                if metricas:
                    print_success("Métricas del sistema obtenidas")
                    print(f"CPU: {metricas['cpu']['porcentaje']}%")
                    print(f"Memoria: {metricas['memoria']['porcentaje']}%")
                    print(f"Disco: {metricas['disco']['porcentaje']}%")
                else:
                    print_error("Error obteniendo métricas del sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Monitoreando aplicación")
                metricas = gestor.obtener_metricas_aplicacion()
                if metricas:
                    print_success("Métricas de la aplicación obtenidas")
                    print(f"Procesos Python: {metricas['procesos']['python']}")
                    print(f"Errores recientes: {metricas['logs']['errores_recientes']}")
                else:
                    print_error("Error obteniendo métricas de la aplicación")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Monitoreando meteorología")
                metricas = gestor.obtener_metricas_meteorologia()
                if metricas:
                    print_success("Métricas meteorológicas obtenidas")
                    print(f"Archivos de datos: {metricas['datos']['archivos']}")
                    print(f"Alertas recientes: {metricas['reportes']['alertas_recientes']}")
                else:
                    print_error("Error obteniendo métricas meteorológicas")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Generando reporte completo de monitoreo")
                reporte = gestor.generar_reporte_monitoreo()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_info("Saliendo del gestor de monitoreo...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-7.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de monitoreo interrumpida por el usuario")
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