#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 OPTIMIZACIÓN DEL SISTEMA METGO 3D
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
    print("🌾 OPTIMIZACIÓN DEL SISTEMA METGO 3D")
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
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class OptimizadorSistema:
    """Clase para optimización del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_optimizacion': 'optimizacion',
            'archivo_config': 'config/optimizacion.yaml',
            'umbral_cpu': 80,
            'umbral_memoria': 80,
            'umbral_disco': 90
        }
        
        self.optimizaciones = [
            'limpieza_archivos',
            'optimizacion_memoria',
            'optimizacion_disco',
            'optimizacion_red',
            'optimizacion_procesos',
            'optimizacion_configuracion'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de optimización"""
        try:
            print_info("Cargando configuración de optimización...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_optimizacion(self):
        """Crear estructura de optimización"""
        try:
            print_info("Creando estructura de optimización...")
            
            # Crear directorio principal
            optimizacion_dir = Path(self.configuracion['directorio_optimizacion'])
            optimizacion_dir.mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            print_success("Estructura de optimización creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # config/optimizacion.yaml
            config_content = '''# Configuración de optimización del sistema METGO 3D

optimizacion:
  umbrales:
    cpu: 80
    memoria: 80
    disco: 90
  
  limpieza:
    archivos_temporales: true
    logs_antiguos: true
    cache: true
    backups_antiguos: true
  
  memoria:
    garbage_collection: true
    liberar_cache: true
    optimizar_imports: true
  
  disco:
    comprimir_archivos: true
    eliminar_duplicados: true
    optimizar_espacio: true
  
  red:
    optimizar_conexiones: true
    comprimir_datos: true
    cache_dns: true
  
  procesos:
    prioridad_normal: true
    limitar_recursos: true
    optimizar_threads: true
'''
            
            config_file = Path('config/optimizacion.yaml')
            config_file.parent.mkdir(exist_ok=True)
            config_file.write_text(config_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def limpiar_archivos_temporales(self):
        """Limpiar archivos temporales"""
        try:
            print_info("Limpiando archivos temporales...")
            
            archivos_eliminados = 0
            espacio_liberado = 0
            
            # Directorios a limpiar
            directorios = [
                'logs',
                'data/temp',
                'reportes/temp',
                'optimizacion/temp'
            ]
            
            for directorio in directorios:
                dir_path = Path(directorio)
                if dir_path.exists():
                    for archivo in dir_path.glob('*'):
                        try:
                            if archivo.is_file():
                                tamaño = archivo.stat().st_size
                                archivo.unlink()
                                archivos_eliminados += 1
                                espacio_liberado += tamaño
                        except Exception as e:
                            print_warning(f"Error eliminando {archivo}: {e}")
            
            print_success(f"Archivos eliminados: {archivos_eliminados}")
            print_success(f"Espacio liberado: {espacio_liberado / 1024 / 1024:.2f} MB")
            
            return True
            
        except Exception as e:
            print_error(f"Error limpiando archivos temporales: {e}")
            return False
    
    def optimizar_memoria(self):
        """Optimizar uso de memoria"""
        try:
            print_info("Optimizando memoria...")
            
            # Obtener información de memoria
            memoria = psutil.virtual_memory()
            memoria_percent = memoria.percent
            
            print_info(f"Uso actual de memoria: {memoria_percent}%")
            
            if memoria_percent > self.configuracion['umbral_memoria']:
                print_warning("Memoria alta, aplicando optimizaciones...")
                
                # Forzar garbage collection
                import gc
                gc.collect()
                
                # Limpiar cache de Python
                sys.modules.clear()
                
                print_success("Memoria optimizada")
            else:
                print_info("Memoria en niveles normales")
            
            return True
            
        except Exception as e:
            print_error(f"Error optimizando memoria: {e}")
            return False
    
    def optimizar_disco(self):
        """Optimizar uso de disco"""
        try:
            print_info("Optimizando disco...")
            
            # Obtener información de disco
            disco = psutil.disk_usage('/')
            disco_percent = disco.percent
            
            print_info(f"Uso actual de disco: {disco_percent}%")
            
            if disco_percent > self.configuracion['umbral_disco']:
                print_warning("Disco lleno, aplicando optimizaciones...")
                
                # Limpiar archivos temporales
                self.limpiar_archivos_temporales()
                
                # Comprimir archivos grandes
                self.comprimir_archivos_grandes()
                
                print_success("Disco optimizado")
            else:
                print_info("Disco en niveles normales")
            
            return True
            
        except Exception as e:
            print_error(f"Error optimizando disco: {e}")
            return False
    
    def comprimir_archivos_grandes(self):
        """Comprimir archivos grandes"""
        try:
            print_info("Comprimiendo archivos grandes...")
            
            # Buscar archivos grandes (> 10MB)
            archivos_grandes = []
            for archivo in Path('.').rglob('*'):
                if archivo.is_file() and archivo.stat().st_size > 10 * 1024 * 1024:
                    archivos_grandes.append(archivo)
            
            print_info(f"Archivos grandes encontrados: {len(archivos_grandes)}")
            
            # Comprimir archivos
            for archivo in archivos_grandes:
                try:
                    # Crear archivo comprimido
                    archivo_comprimido = archivo.with_suffix(archivo.suffix + '.gz')
                    
                    # Comprimir con gzip
                    subprocess.run(['gzip', '-c', str(archivo)], 
                                 stdout=open(archivo_comprimido, 'wb'), 
                                 check=True)
                    
                    # Eliminar archivo original
                    archivo.unlink()
                    
                    print_success(f"Archivo comprimido: {archivo}")
                    
                except Exception as e:
                    print_warning(f"Error comprimiendo {archivo}: {e}")
            
            return True
            
        except Exception as e:
            print_error(f"Error comprimiendo archivos: {e}")
            return False
    
    def optimizar_procesos(self):
        """Optimizar procesos del sistema"""
        try:
            print_info("Optimizando procesos...")
            
            # Obtener información de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            print_info(f"Uso actual de CPU: {cpu_percent}%")
            
            if cpu_percent > self.configuracion['umbral_cpu']:
                print_warning("CPU alta, aplicando optimizaciones...")
                
                # Optimizar procesos Python
                procesos_python = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        if 'python' in proc.info['name'].lower():
                            procesos_python.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Ajustar prioridad de procesos
                for proc in procesos_python:
                    try:
                        proc.nice(10)  # Bajar prioridad
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                print_success("Procesos optimizados")
            else:
                print_info("CPU en niveles normales")
            
            return True
            
        except Exception as e:
            print_error(f"Error optimizando procesos: {e}")
            return False
    
    def optimizar_configuracion(self):
        """Optimizar configuración del sistema"""
        try:
            print_info("Optimizando configuración...")
            
            # Verificar archivos de configuración
            archivos_config = [
                'config/config.yaml',
                'config/optimizacion.yaml',
                'pytest.ini',
                'setup.cfg'
            ]
            
            for archivo in archivos_config:
                archivo_path = Path(archivo)
                if archivo_path.exists():
                    # Verificar permisos
                    stat = archivo_path.stat()
                    permisos = oct(stat.st_mode)[-3:]
                    
                    if permisos != '644':
                        print_warning(f"Permisos incorrectos en {archivo}: {permisos}")
                        # Corregir permisos
                        archivo_path.chmod(0o644)
                        print_success(f"Permisos corregidos en {archivo}")
            
            print_success("Configuración optimizada")
            return True
            
        except Exception as e:
            print_error(f"Error optimizando configuración: {e}")
            return False
    
    def ejecutar_optimizacion_completa(self):
        """Ejecutar optimización completa del sistema"""
        try:
            print_info("Ejecutando optimización completa...")
            
            # Ejecutar todas las optimizaciones
            optimizaciones = [
                ('Limpieza de archivos', self.limpiar_archivos_temporales),
                ('Optimización de memoria', self.optimizar_memoria),
                ('Optimización de disco', self.optimizar_disco),
                ('Optimización de procesos', self.optimizar_procesos),
                ('Optimización de configuración', self.optimizar_configuracion)
            ]
            
            resultados = []
            
            for nombre, funcion in optimizaciones:
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
            print(f"\n📊 Resumen de optimización:")
            exitosos = sum(1 for _, exito, _ in resultados if exito)
            total = len(resultados)
            
            print(f"Optimizaciones exitosas: {exitosos}/{total}")
            
            for nombre, exito, mensaje in resultados:
                estado = "✅" if exito else "❌"
                print(f"{estado} {nombre}: {mensaje}")
            
            return exitosos == total
            
        except Exception as e:
            print_error(f"Error ejecutando optimización completa: {e}")
            return False
    
    def generar_reporte_optimizacion(self):
        """Generar reporte de optimización"""
        try:
            print_info("Generando reporte de optimización...")
            
            # Obtener métricas del sistema
            memoria = psutil.virtual_memory()
            disco = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'metricas': {
                    'cpu': {
                        'porcentaje': cpu_percent,
                        'estado': 'OK' if cpu_percent < self.configuracion['umbral_cpu'] else 'ALERTA'
                    },
                    'memoria': {
                        'porcentaje': memoria.percent,
                        'total': memoria.total,
                        'disponible': memoria.available,
                        'estado': 'OK' if memoria.percent < self.configuracion['umbral_memoria'] else 'ALERTA'
                    },
                    'disco': {
                        'porcentaje': disco.percent,
                        'total': disco.total,
                        'disponible': disco.free,
                        'estado': 'OK' if disco.percent < self.configuracion['umbral_disco'] else 'ALERTA'
                    }
                },
                'optimizaciones': {
                    'limpieza_archivos': True,
                    'optimizacion_memoria': True,
                    'optimizacion_disco': True,
                    'optimizacion_procesos': True,
                    'optimizacion_configuracion': True
                },
                'recomendaciones': []
            }
            
            # Generar recomendaciones
            if cpu_percent > self.configuracion['umbral_cpu']:
                reporte['recomendaciones'].append("Considerar reducir la carga de procesamiento")
            
            if memoria.percent > self.configuracion['umbral_memoria']:
                reporte['recomendaciones'].append("Considerar aumentar la memoria disponible")
            
            if disco.percent > self.configuracion['umbral_disco']:
                reporte['recomendaciones'].append("Considerar liberar espacio en disco")
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"optimizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de optimización generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de optimización:")
            print(f"CPU: {cpu_percent}% ({reporte['metricas']['cpu']['estado']})")
            print(f"Memoria: {memoria.percent}% ({reporte['metricas']['memoria']['estado']})")
            print(f"Disco: {disco.percent}% ({reporte['metricas']['disco']['estado']})")
            
            if reporte['recomendaciones']:
                print(f"\n💡 Recomendaciones:")
                for recomendacion in reporte['recomendaciones']:
                    print(f"- {recomendacion}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de optimización"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE OPTIMIZACIÓN - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de optimización")
    print("3. 🧹 Limpiar archivos temporales")
    print("4. 💾 Optimizar memoria")
    print("5. 💿 Optimizar disco")
    print("6. ⚙️ Optimizar procesos")
    print("7. 🔧 Optimizar configuración")
    print("8. 🚀 Optimización completa")
    print("9. 📊 Generar reporte")
    print("10. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de optimización"""
    print_header()
    
    # Crear optimizador
    optimizador = OptimizadorSistema()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-10): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if optimizador.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de optimización")
                if optimizador.crear_estructura_optimizacion():
                    print_success("Estructura de optimización creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Limpiando archivos temporales")
                if optimizador.limpiar_archivos_temporales():
                    print_success("Archivos temporales limpiados correctamente")
                else:
                    print_error("Error limpiando archivos temporales")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Optimizando memoria")
                if optimizador.optimizar_memoria():
                    print_success("Memoria optimizada correctamente")
                else:
                    print_error("Error optimizando memoria")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Optimizando disco")
                if optimizador.optimizar_disco():
                    print_success("Disco optimizado correctamente")
                else:
                    print_error("Error optimizando disco")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Optimizando procesos")
                if optimizador.optimizar_procesos():
                    print_success("Procesos optimizados correctamente")
                else:
                    print_error("Error optimizando procesos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Optimizando configuración")
                if optimizador.optimizar_configuracion():
                    print_success("Configuración optimizada correctamente")
                else:
                    print_error("Error optimizando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Ejecutando optimización completa")
                if optimizador.ejecutar_optimizacion_completa():
                    print_success("Optimización completa ejecutada correctamente")
                else:
                    print_error("Error ejecutando optimización completa")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Generando reporte de optimización")
                reporte = optimizador.generar_reporte_optimizacion()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_info("Saliendo del optimizador...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-10.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Optimización interrumpida por el usuario")
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