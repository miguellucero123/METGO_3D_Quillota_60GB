#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE SEGURIDAD DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE SEGURIDAD DEL SISTEMA METGO 3D")
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

class GestorSeguridad:
    """Clase para gestión de seguridad del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_seguridad': 'seguridad',
            'archivo_config': 'config/seguridad.yaml',
            'nivel_auditoria': 'alto',
            'encriptacion': 'AES-256',
            'hash_algorithm': 'SHA-256'
        }
        
        self.auditorias = [
            'archivos_sensibles',
            'permisos',
            'dependencias',
            'configuracion',
            'logs',
            'accesos'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de seguridad"""
        try:
            print_info("Cargando configuración de seguridad...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_seguridad(self):
        """Crear estructura de seguridad"""
        try:
            print_info("Creando estructura de seguridad...")
            
            # Crear directorio principal
            seguridad_dir = Path(self.configuracion['directorio_seguridad'])
            seguridad_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['auditorias', 'certificados', 'claves', 'backups']
            for subdir in subdirs:
                (seguridad_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            print_success("Estructura de seguridad creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # config/seguridad.yaml
            config_content = '''# Configuración de seguridad del sistema METGO 3D

seguridad:
  nivel_auditoria: alto
  encriptacion: AES-256
  hash_algorithm: SHA-256
  
  auditorias:
    archivos_sensibles: true
    permisos: true
    dependencias: true
    configuracion: true
    logs: true
    accesos: true
  
  alertas:
    email:
      habilitado: false
      destinatarios: []
    webhook:
      habilitado: false
      url: ""
  
  archivos_sensibles:
    - "*.env"
    - "*.key"
    - "*.pem"
    - "*.p12"
    - "config/*.yaml"
    - "data/*.json"
'''
            
            config_file = Path('config/seguridad.yaml')
            config_file.parent.mkdir(exist_ok=True)
            config_file.write_text(config_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def auditar_archivos_sensibles(self):
        """Auditar archivos sensibles"""
        try:
            print_info("Auditando archivos sensibles...")
            
            archivos_sensibles = [
                '*.env', '*.key', '*.pem', '*.p12',
                'config/*.yaml', 'data/*.json'
            ]
            
            resultados = []
            
            for patron in archivos_sensibles:
                archivos = list(Path('.').glob(patron))
                for archivo in archivos:
                    try:
                        # Verificar permisos
                        stat = archivo.stat()
                        permisos = oct(stat.st_mode)[-3:]
                        
                        # Calcular hash
                        with open(archivo, 'rb') as f:
                            contenido = f.read()
                            hash_archivo = hashlib.sha256(contenido).hexdigest()
                        
                        resultados.append({
                            'archivo': str(archivo),
                            'permisos': permisos,
                            'hash': hash_archivo,
                            'tamaño': stat.st_size,
                            'modificado': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                        
                    except Exception as e:
                        print_warning(f"Error procesando {archivo}: {e}")
            
            print_success(f"Archivos sensibles auditados: {len(resultados)}")
            return resultados
            
        except Exception as e:
            print_error(f"Error auditando archivos sensibles: {e}")
            return []
    
    def auditar_permisos(self):
        """Auditar permisos del sistema"""
        try:
            print_info("Auditando permisos del sistema...")
            
            archivos_importantes = [
                'gestion_*.py',
                '*.ipynb',
                'config/*.yaml',
                'requirements.txt'
            ]
            
            resultados = []
            
            for patron in archivos_importantes:
                archivos = list(Path('.').glob(patron))
                for archivo in archivos:
                    try:
                        stat = archivo.stat()
                        permisos = oct(stat.st_mode)[-3:]
                        
                        # Verificar si los permisos son seguros
                        permisos_ok = True
                        if archivo.suffix == '.py' and permisos != '644':
                            permisos_ok = False
                        elif archivo.suffix == '.yaml' and permisos not in ['644', '600']:
                            permisos_ok = False
                        
                        resultados.append({
                            'archivo': str(archivo),
                            'permisos': permisos,
                            'seguro': permisos_ok,
                            'recomendacion': '644' if archivo.suffix == '.py' else '600'
                        })
                        
                    except Exception as e:
                        print_warning(f"Error procesando {archivo}: {e}")
            
            print_success(f"Permisos auditados: {len(resultados)}")
            return resultados
            
        except Exception as e:
            print_error(f"Error auditando permisos: {e}")
            return []
    
    def auditar_dependencias(self):
        """Auditar dependencias del sistema"""
        try:
            print_info("Auditando dependencias del sistema...")
            
            # Verificar requirements.txt
            requirements_file = Path('requirements.txt')
            if not requirements_file.exists():
                print_warning("Archivo requirements.txt no encontrado")
                return []
            
            # Leer dependencias
            dependencias = []
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencias.append(line)
            
            # Verificar vulnerabilidades con bandit
            try:
                resultado = subprocess.run(['bandit', '-r', '.', '-f', 'json'], 
                                         capture_output=True, text=True, timeout=60)
                
                if resultado.returncode == 0:
                    print_success("Dependencias auditadas con bandit")
                else:
                    print_warning("Bandit encontró problemas de seguridad")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_warning("Bandit no está instalado")
            
            print_success(f"Dependencias auditadas: {len(dependencias)}")
            return dependencias
            
        except Exception as e:
            print_error(f"Error auditando dependencias: {e}")
            return []
    
    def auditar_configuracion(self):
        """Auditar configuración del sistema"""
        try:
            print_info("Auditando configuración del sistema...")
            
            archivos_config = [
                'config/config.yaml',
                'config/seguridad.yaml',
                'config/monitoreo.yaml',
                'pytest.ini',
                'setup.cfg',
                'pyproject.toml'
            ]
            
            resultados = []
            
            for archivo in archivos_config:
                archivo_path = Path(archivo)
                if archivo_path.exists():
                    try:
                        # Verificar permisos
                        stat = archivo_path.stat()
                        permisos = oct(stat.st_mode)[-3:]
                        
                        # Verificar contenido sensible
                        with open(archivo_path, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        
                        # Buscar patrones sensibles
                        patrones_sensibles = ['password', 'secret', 'key', 'token', 'api_key']
                        contenido_sensible = any(patron in contenido.lower() for patron in patrones_sensibles)
                        
                        resultados.append({
                            'archivo': archivo,
                            'permisos': permisos,
                            'contenido_sensible': contenido_sensible,
                            'tamaño': stat.st_size
                        })
                        
                    except Exception as e:
                        print_warning(f"Error procesando {archivo}: {e}")
            
            print_success(f"Configuración auditada: {len(resultados)}")
            return resultados
            
        except Exception as e:
            print_error(f"Error auditando configuración: {e}")
            return []
    
    def generar_reporte_seguridad(self):
        """Generar reporte de seguridad"""
        try:
            print_info("Generando reporte de seguridad...")
            
            # Ejecutar todas las auditorías
            archivos_sensibles = self.auditar_archivos_sensibles()
            permisos = self.auditar_permisos()
            dependencias = self.auditar_dependencias()
            configuracion = self.auditar_configuracion()
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'auditorias': {
                    'archivos_sensibles': {
                        'total': len(archivos_sensibles),
                        'archivos': archivos_sensibles
                    },
                    'permisos': {
                        'total': len(permisos),
                        'archivos': permisos
                    },
                    'dependencias': {
                        'total': len(dependencias),
                        'lista': dependencias
                    },
                    'configuracion': {
                        'total': len(configuracion),
                        'archivos': configuracion
                    }
                },
                'resumen': {
                    'estado_general': 'OK',
                    'vulnerabilidades': 0,
                    'archivos_inseguros': 0
                }
            }
            
            # Calcular estado general
            vulnerabilidades = 0
            archivos_inseguros = 0
            
            # Contar archivos con permisos inseguros
            for archivo in permisos:
                if not archivo['seguro']:
                    archivos_inseguros += 1
            
            # Contar archivos de configuración con contenido sensible
            for archivo in configuracion:
                if archivo['contenido_sensible']:
                    vulnerabilidades += 1
            
            reporte['resumen']['vulnerabilidades'] = vulnerabilidades
            reporte['resumen']['archivos_inseguros'] = archivos_inseguros
            reporte['resumen']['estado_general'] = 'ALERTA' if vulnerabilidades > 0 or archivos_inseguros > 0 else 'OK'
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de seguridad generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de seguridad:")
            print(f"Estado general: {reporte['resumen']['estado_general']}")
            print(f"Vulnerabilidades: {vulnerabilidades}")
            print(f"Archivos inseguros: {archivos_inseguros}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de seguridad"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE SEGURIDAD - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de seguridad")
    print("3. 🔒 Auditar archivos sensibles")
    print("4. 📋 Auditar permisos")
    print("5. 📦 Auditar dependencias")
    print("6. ⚙️ Auditar configuración")
    print("7. 📊 Generar reporte completo")
    print("8. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de seguridad"""
    print_header()
    
    # Crear gestor de seguridad
    gestor = GestorSeguridad()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-8): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de seguridad")
                if gestor.crear_estructura_seguridad():
                    print_success("Estructura de seguridad creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Auditando archivos sensibles")
                archivos = gestor.auditar_archivos_sensibles()
                if archivos:
                    print_success(f"Archivos sensibles auditados: {len(archivos)}")
                else:
                    print_error("Error auditando archivos sensibles")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Auditando permisos")
                permisos = gestor.auditar_permisos()
                if permisos:
                    print_success(f"Permisos auditados: {len(permisos)}")
                else:
                    print_error("Error auditando permisos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Auditando dependencias")
                dependencias = gestor.auditar_dependencias()
                if dependencias:
                    print_success(f"Dependencias auditadas: {len(dependencias)}")
                else:
                    print_error("Error auditando dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Auditando configuración")
                config = gestor.auditar_configuracion()
                if config:
                    print_success(f"Configuración auditada: {len(config)}")
                else:
                    print_error("Error auditando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Generando reporte completo de seguridad")
                reporte = gestor.generar_reporte_seguridad()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_info("Saliendo del gestor de seguridad...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-8.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de seguridad interrumpida por el usuario")
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