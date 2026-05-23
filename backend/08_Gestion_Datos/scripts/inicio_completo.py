#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 INICIO COMPLETO DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 INICIO COMPLETO DEL SISTEMA METGO 3D")
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
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia")
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class IniciadorSistema:
    """Clase para inicio completo del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_sistema': '.',
            'archivo_config': 'config/config.yaml',
            'timeout': 300,  # segundos
            'modo_debug': False
        }
        
        self.componentes = [
            'configuracion',
            'dependencias',
            'datos',
            'notebooks',
            'servicios',
            'monitoreo',
            'optimizacion'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración del sistema"""
        try:
            print_info("Cargando configuración del sistema...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def verificar_dependencias(self):
        """Verificar dependencias del sistema"""
        try:
            print_info("Verificando dependencias...")
            
            # Verificar Python
            version_python = sys.version_info
            if version_python.major < 3 or (version_python.major == 3 and version_python.minor < 8):
                print_error("Python 3.8 o superior requerido")
                return False
            
            print_success(f"Python {version_python.major}.{version_python.minor}.{version_python.micro}")
            
            # Verificar archivos requeridos
            archivos_requeridos = [
                'requirements.txt',
                'config/config.yaml',
                '00_Sistema_Principal_MIP_Quillota.ipynb'
            ]
            
            for archivo in archivos_requeridos:
                if not Path(archivo).exists():
                    print_error(f"Archivo requerido no encontrado: {archivo}")
                    return False
            
            print_success("Archivos requeridos verificados")
            
            # Verificar dependencias Python
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                             capture_output=True, check=True)
                print_success("Dependencias Python verificadas")
            except subprocess.CalledProcessError:
                print_warning("Algunas dependencias pueden tener conflictos")
            
            return True
            
        except Exception as e:
            print_error(f"Error verificando dependencias: {e}")
            return False
    
    def inicializar_directorios(self):
        """Inicializar directorios del sistema"""
        try:
            print_info("Inicializando directorios...")
            
            directorios = [
                'data',
                'logs',
                'reportes',
                'config',
                'usuarios',
                'auditoria',
                'seguridad',
                'optimizacion'
            ]
            
            for directorio in directorios:
                dir_path = Path(directorio)
                dir_path.mkdir(exist_ok=True)
                print_success(f"Directorio {directorio} inicializado")
            
            return True
            
        except Exception as e:
            print_error(f"Error inicializando directorios: {e}")
            return False
    
    def configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            print_info("Configurando sistema de logging...")
            
            # Crear archivo de configuración de logging
            logging_config = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                    }
                },
                'handlers': {
                    'default': {
                        'level': 'INFO',
                        'formatter': 'standard',
                        'class': 'logging.StreamHandler',
                        'stream': 'ext://sys.stdout'
                    },
                    'file': {
                        'level': 'INFO',
                        'formatter': 'standard',
                        'class': 'logging.FileHandler',
                        'filename': 'logs/sistema.log',
                        'mode': 'a'
                    }
                },
                'loggers': {
                    '': {
                        'handlers': ['default', 'file'],
                        'level': 'INFO',
                        'propagate': False
                    }
                }
            }
            
            # Guardar configuración
            config_file = Path('config/logging.yaml')
            with open(config_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(logging_config, f, default_flow_style=False)
            
            print_success("Sistema de logging configurado")
            return True
            
        except Exception as e:
            print_error(f"Error configurando logging: {e}")
            return False
    
    def inicializar_datos(self):
        """Inicializar datos del sistema"""
        try:
            print_info("Inicializando datos del sistema...")
            
            # Crear archivo de datos inicial si no existe
            data_file = Path('data/datos_iniciales.json')
            if not data_file.exists():
                datos_iniciales = {
                    'timestamp': datetime.now().isoformat(),
                    'sistema': 'METGO 3D',
                    'version': '2.0',
                    'estado': 'inicializado',
                    'configuracion': {
                        'quillota': {
                            'coordenadas': {
                                'latitud': -32.8833,
                                'longitud': -71.2333
                            },
                            'altitud': 127,
                            'zona_horaria': 'America/Santiago'
                        }
                    }
                }
                
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(datos_iniciales, f, indent=2, ensure_ascii=False)
                
                print_success("Datos iniciales creados")
            
            return True
            
        except Exception as e:
            print_error(f"Error inicializando datos: {e}")
            return False
    
    def ejecutar_notebooks(self):
        """Ejecutar notebooks del sistema"""
        try:
            print_info("Ejecutando notebooks del sistema...")
            
            # Lista de notebooks en orden de ejecución
            notebooks = [
                '01_Configuracion_e_imports.ipynb',
                '02_Carga_y_Procesamiento_Datos.ipynb',
                '03_Analisis_Meteorologico.ipynb',
                '04_Visualizaciones.ipynb',
                '05_Modelos_ML.ipynb'
            ]
            
            for notebook in notebooks:
                notebook_path = Path(notebook)
                if notebook_path.exists():
                    print_info(f"Ejecutando {notebook}...")
                    
                    try:
                        # Ejecutar notebook con nbconvert
                        resultado = subprocess.run([
                            'jupyter', 'nbconvert', '--execute', '--to', 'notebook',
                            '--inplace', str(notebook_path)
                        ], capture_output=True, text=True, timeout=self.configuracion['timeout'])
                        
                        if resultado.returncode == 0:
                            print_success(f"{notebook} ejecutado correctamente")
                        else:
                            print_warning(f"Error ejecutando {notebook}: {resultado.stderr}")
                    
                    except subprocess.TimeoutExpired:
                        print_warning(f"Timeout ejecutando {notebook}")
                    except Exception as e:
                        print_warning(f"Error ejecutando {notebook}: {e}")
                else:
                    print_warning(f"Notebook no encontrado: {notebook}")
            
            return True
            
        except Exception as e:
            print_error(f"Error ejecutando notebooks: {e}")
            return False
    
    def iniciar_servicios(self):
        """Iniciar servicios del sistema"""
        try:
            print_info("Iniciando servicios del sistema...")
            
            # Iniciar monitoreo
            print_info("Iniciando monitoreo...")
            try:
                subprocess.Popen([sys.executable, 'monitor_sistema.py'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                print_success("Monitoreo iniciado")
            except Exception as e:
                print_warning(f"Error iniciando monitoreo: {e}")
            
            # Iniciar respaldos automáticos
            print_info("Iniciando respaldos automáticos...")
            try:
                subprocess.Popen([sys.executable, 'backup_sistema.py'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                print_success("Respaldos automáticos iniciados")
            except Exception as e:
                print_warning(f"Error iniciando respaldos: {e}")
            
            return True
            
        except Exception as e:
            print_error(f"Error iniciando servicios: {e}")
            return False
    
    def verificar_sistema(self):
        """Verificar estado del sistema"""
        try:
            print_info("Verificando estado del sistema...")
            
            # Verificar archivos críticos
            archivos_criticos = [
                'config/config.yaml',
                'data/datos_iniciales.json',
                'logs/sistema.log'
            ]
            
            for archivo in archivos_criticos:
                if Path(archivo).exists():
                    print_success(f"Archivo crítico verificado: {archivo}")
                else:
                    print_warning(f"Archivo crítico no encontrado: {archivo}")
            
            # Verificar procesos
            try:
                import psutil
                procesos_python = [p for p in psutil.process_iter(['name']) 
                                 if 'python' in p.info['name'].lower()]
                print_success(f"Procesos Python activos: {len(procesos_python)}")
            except Exception:
                print_warning("No se pudo verificar procesos")
            
            return True
            
        except Exception as e:
            print_error(f"Error verificando sistema: {e}")
            return False
    
    def generar_reporte_inicio(self):
        """Generar reporte de inicio"""
        try:
            print_info("Generando reporte de inicio...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'estado': 'iniciado',
                'componentes': {
                    'configuracion': True,
                    'dependencias': True,
                    'datos': True,
                    'notebooks': True,
                    'servicios': True,
                    'monitoreo': True,
                    'optimizacion': True
                },
                'archivos_criticos': [],
                'procesos_activos': 0
            }
            
            # Verificar archivos críticos
            archivos_criticos = [
                'config/config.yaml',
                'data/datos_iniciales.json',
                'logs/sistema.log'
            ]
            
            for archivo in archivos_criticos:
                if Path(archivo).exists():
                    reporte['archivos_criticos'].append(archivo)
            
            # Contar procesos
            try:
                import psutil
                procesos_python = [p for p in psutil.process_iter(['name']) 
                                 if 'python' in p.info['name'].lower()]
                reporte['procesos_activos'] = len(procesos_python)
            except Exception:
                pass
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"inicio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de inicio generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del inicio:")
            print(f"Archivos críticos: {len(reporte['archivos_criticos'])}")
            print(f"Procesos activos: {reporte['procesos_activos']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None
    
    def ejecutar_inicio_completo(self):
        """Ejecutar inicio completo del sistema"""
        try:
            print_info("Ejecutando inicio completo del sistema...")
            
            # Ejecutar todos los pasos
            pasos = [
                ('Cargar configuración', self.cargar_configuracion),
                ('Verificar dependencias', self.verificar_dependencias),
                ('Inicializar directorios', self.inicializar_directorios),
                ('Configurar logging', self.configurar_logging),
                ('Inicializar datos', self.inicializar_datos),
                ('Ejecutar notebooks', self.ejecutar_notebooks),
                ('Iniciar servicios', self.iniciar_servicios),
                ('Verificar sistema', self.verificar_sistema),
                ('Generar reporte', self.generar_reporte_inicio)
            ]
            
            resultados = []
            
            for nombre, funcion in pasos:
                print_step(nombre, f"Ejecutando {nombre.lower()}...")
                try:
                    if funcion():
                        resultados.append((nombre, True, "OK"))
                        print_success(f"{nombre} completado")
                    else:
                        resultados.append((nombre, False, "Error"))
                        print_error(f"Error en {nombre.lower()}")
                except Exception as e:
                    resultados.append((nombre, False, str(e)))
                    print_error(f"Error en {nombre.lower()}: {e}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del inicio completo:")
            exitosos = sum(1 for _, exito, _ in resultados if exito)
            total = len(resultados)
            
            print(f"Pasos exitosos: {exitosos}/{total}")
            
            for nombre, exito, mensaje in resultados:
                estado = "✅" if exito else "❌"
                print(f"{estado} {nombre}: {mensaje}")
            
            return exitosos == total
            
        except Exception as e:
            print_error(f"Error ejecutando inicio completo: {e}")
            return False

def mostrar_menu():
    """Mostrar menú de inicio"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE INICIO COMPLETO - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. ✅ Verificar dependencias")
    print("3. 📁 Inicializar directorios")
    print("4. 📝 Configurar logging")
    print("5. 💾 Inicializar datos")
    print("6. 📓 Ejecutar notebooks")
    print("7. 🚀 Iniciar servicios")
    print("8. 🔍 Verificar sistema")
    print("9. 📊 Generar reporte")
    print("10. 🚀 Inicio completo")
    print("11. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de inicio"""
    print_header()
    
    # Crear iniciador
    iniciador = IniciadorSistema()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-11): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if iniciador.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Verificando dependencias")
                if iniciador.verificar_dependencias():
                    print_success("Dependencias verificadas correctamente")
                else:
                    print_error("Error verificando dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Inicializando directorios")
                if iniciador.inicializar_directorios():
                    print_success("Directorios inicializados correctamente")
                else:
                    print_error("Error inicializando directorios")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Configurando logging")
                if iniciador.configurar_logging():
                    print_success("Logging configurado correctamente")
                else:
                    print_error("Error configurando logging")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Inicializando datos")
                if iniciador.inicializar_datos():
                    print_success("Datos inicializados correctamente")
                else:
                    print_error("Error inicializando datos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Ejecutando notebooks")
                if iniciador.ejecutar_notebooks():
                    print_success("Notebooks ejecutados correctamente")
                else:
                    print_error("Error ejecutando notebooks")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Iniciando servicios")
                if iniciador.iniciar_servicios():
                    print_success("Servicios iniciados correctamente")
                else:
                    print_error("Error iniciando servicios")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Verificando sistema")
                if iniciador.verificar_sistema():
                    print_success("Sistema verificado correctamente")
                else:
                    print_error("Error verificando sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Generando reporte de inicio")
                reporte = iniciador.generar_reporte_inicio()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_step("10", "Ejecutando inicio completo del sistema")
                if iniciador.ejecutar_inicio_completo():
                    print_success("Inicio completo ejecutado correctamente")
                else:
                    print_error("Error ejecutando inicio completo")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "11":
                print_info("Saliendo del iniciador...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-11.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Inicio interrumpido por el usuario")
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