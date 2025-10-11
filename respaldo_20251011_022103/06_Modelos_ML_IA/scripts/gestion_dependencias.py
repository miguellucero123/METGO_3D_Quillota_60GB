#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE DEPENDENCIAS DEL SISTEMA METGO 3D
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
    print("🌾 GESTIÓN DE DEPENDENCIAS DEL SISTEMA METGO 3D")
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

class GestorDependencias:
    """Clase para gestión de dependencias del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'archivo_requirements': 'requirements.txt',
            'archivo_config': 'config/dependencias.yaml',
            'archivo_dependencias': 'dependencias/dependencias.json',
            'directorio_dependencias': 'dependencias',
            'timeout': 300  # segundos
        }
        
        self.dependencias = {
            'principales': [
                'numpy',
                'pandas',
                'matplotlib',
                'seaborn',
                'plotly',
                'scikit-learn',
                'requests',
                'yaml',
                'psutil',
                'jupyter'
            ],
            'opcionales': [
                'tensorflow',
                'torch',
                'xgboost',
                'lightgbm',
                'catboost',
                'optuna',
                'hyperopt',
                'mlflow',
                'wandb',
                'streamlit'
            ],
            'desarrollo': [
                'pytest',
                'flake8',
                'black',
                'isort',
                'mypy',
                'bandit',
                'tox',
                'pre-commit',
                'sphinx',
                'coverage'
            ],
            'sistema': [
                'python',
                'pip',
                'conda',
                'git',
                'docker',
                'docker-compose'
            ]
        }
        
        self.estados = {
            'instaladas': [],
            'no_instaladas': [],
            'desactualizadas': [],
            'conflictos': []
        }
    
    def cargar_configuracion(self):
        """Cargar configuración de dependencias"""
        try:
            print_info("Cargando configuración de dependencias...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_dependencias(self):
        """Crear estructura de dependencias"""
        try:
            print_info("Creando estructura de dependencias...")
            
            # Crear directorio principal
            deps_dir = Path(self.configuracion['directorio_dependencias'])
            deps_dir.mkdir(exist_ok=True)
            
            # Crear archivo de dependencias si no existe
            archivo_deps = Path(self.configuracion['archivo_dependencias'])
            if not archivo_deps.exists():
                with open(archivo_deps, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de dependencias creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def verificar_dependencias(self):
        """Verificar dependencias del sistema"""
        try:
            print_info("Verificando dependencias del sistema...")
            
            # Verificar Python
            version_python = sys.version_info
            if version_python.major < 3 or (version_python.major == 3 and version_python.minor < 8):
                print_error("Python 3.8 o superior requerido")
                return False
            
            print_success(f"Python {version_python.major}.{version_python.minor}.{version_python.micro}")
            
            # Verificar pip
            try:
                resultado = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                         capture_output=True, text=True, check=True)
                print_success(f"pip {resultado.stdout.strip()}")
            except subprocess.CalledProcessError:
                print_error("pip no está disponible")
                return False
            
            # Verificar archivo requirements.txt
            requirements_file = Path(self.configuracion['archivo_requirements'])
            if not requirements_file.exists():
                print_warning("Archivo requirements.txt no encontrado")
                return False
            
            print_success("Archivo requirements.txt encontrado")
            return True
            
        except Exception as e:
            print_error(f"Error verificando dependencias: {e}")
            return False
    
    def instalar_dependencias(self, archivo_requirements=None):
        """Instalar dependencias"""
        try:
            print_info("Instalando dependencias...")
            
            # Usar archivo por defecto si no se especifica
            if archivo_requirements is None:
                archivo_requirements = self.configuracion['archivo_requirements']
            
            archivo_path = Path(archivo_requirements)
            if not archivo_path.exists():
                print_error(f"Archivo {archivo_requirements} no encontrado")
                return False
            
            # Instalar dependencias
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', str(archivo_path)
                ], capture_output=True, text=True, check=True, timeout=self.configuracion['timeout'])
                
                print_success("Dependencias instaladas correctamente")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error instalando dependencias: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print_error("Timeout instalando dependencias")
                return False
            
        except Exception as e:
            print_error(f"Error instalando dependencias: {e}")
            return False
    
    def actualizar_dependencias(self):
        """Actualizar dependencias"""
        try:
            print_info("Actualizando dependencias...")
            
            # Actualizar pip
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                             capture_output=True, text=True, check=True)
                print_success("pip actualizado")
            except subprocess.CalledProcessError:
                print_warning("Error actualizando pip")
            
            # Actualizar dependencias
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 
                    self.configuracion['archivo_requirements']
                ], capture_output=True, text=True, check=True, timeout=self.configuracion['timeout'])
                
                print_success("Dependencias actualizadas correctamente")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error actualizando dependencias: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print_error("Timeout actualizando dependencias")
                return False
            
        except Exception as e:
            print_error(f"Error actualizando dependencias: {e}")
            return False
    
    def verificar_conflictos(self):
        """Verificar conflictos de dependencias"""
        try:
            print_info("Verificando conflictos de dependencias...")
            
            # Verificar con pip check
            try:
                resultado = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                         capture_output=True, text=True, check=True)
                
                print_success("No hay conflictos de dependencias")
                return True
                
            except subprocess.CalledProcessError as e:
                print_warning(f"Conflictos encontrados: {e.stderr}")
                return False
            
        except Exception as e:
            print_error(f"Error verificando conflictos: {e}")
            return False
    
    def listar_dependencias(self):
        """Listar dependencias instaladas"""
        try:
            print_info("Listando dependencias instaladas...")
            
            # Obtener lista de paquetes instalados
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'list', '--format=json'
                ], capture_output=True, text=True, check=True)
                
                paquetes = json.loads(resultado.stdout)
                
                print(f"\n📋 Dependencias instaladas ({len(paquetes)}):")
                print("-" * 80)
                print(f"{'Paquete':<25} {'Versión':<15} {'Ubicación':<30}")
                print("-" * 80)
                
                for paquete in paquetes:
                    nombre = paquete['name']
                    version = paquete['version']
                    ubicacion = paquete.get('location', 'N/A')
                    
                    print(f"{nombre:<25} {version:<15} {ubicacion:<30}")
                
                return paquetes
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error listando dependencias: {e.stderr}")
                return []
            except json.JSONDecodeError:
                print_error("Error decodificando lista de dependencias")
                return []
            
        except Exception as e:
            print_error(f"Error listando dependencias: {e}")
            return []
    
    def verificar_dependencia(self, nombre):
        """Verificar dependencia específica"""
        try:
            print_info(f"Verificando dependencia: {nombre}")
            
            # Verificar si está instalada
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'show', nombre
                ], capture_output=True, text=True, check=True)
                
                print_success(f"Dependencia {nombre} instalada")
                return True
                
            except subprocess.CalledProcessError:
                print_warning(f"Dependencia {nombre} no instalada")
                return False
            
        except Exception as e:
            print_error(f"Error verificando dependencia {nombre}: {e}")
            return False
    
    def instalar_dependencia(self, nombre, version=None):
        """Instalar dependencia específica"""
        try:
            print_info(f"Instalando dependencia: {nombre}")
            
            # Construir comando de instalación
            comando = [sys.executable, '-m', 'pip', 'install']
            
            if version:
                comando.append(f"{nombre}=={version}")
            else:
                comando.append(nombre)
            
            # Instalar dependencia
            try:
                resultado = subprocess.run(comando, capture_output=True, text=True, 
                                         check=True, timeout=self.configuracion['timeout'])
                
                print_success(f"Dependencia {nombre} instalada correctamente")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error instalando {nombre}: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print_error(f"Timeout instalando {nombre}")
                return False
            
        except Exception as e:
            print_error(f"Error instalando dependencia {nombre}: {e}")
            return False
    
    def desinstalar_dependencia(self, nombre):
        """Desinstalar dependencia específica"""
        try:
            print_info(f"Desinstalando dependencia: {nombre}")
            
            # Desinstalar dependencia
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'uninstall', '-y', nombre
                ], capture_output=True, text=True, check=True, timeout=self.configuracion['timeout'])
                
                print_success(f"Dependencia {nombre} desinstalada correctamente")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error desinstalando {nombre}: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print_error(f"Timeout desinstalando {nombre}")
                return False
            
        except Exception as e:
            print_error(f"Error desinstalando dependencia {nombre}: {e}")
            return False
    
    def generar_requirements(self, archivo_salida=None):
        """Generar archivo requirements.txt"""
        try:
            print_info("Generando archivo requirements.txt...")
            
            # Obtener lista de paquetes instalados
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip', 'freeze'
                ], capture_output=True, text=True, check=True)
                
                # Determinar archivo de salida
                if archivo_salida is None:
                    archivo_salida = self.configuracion['archivo_requirements']
                
                archivo_path = Path(archivo_salida)
                archivo_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Escribir archivo
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(resultado.stdout)
                
                print_success(f"Archivo requirements.txt generado: {archivo_path}")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error generando requirements: {e.stderr}")
                return False
            
        except Exception as e:
            print_error(f"Error generando requirements: {e}")
            return False
    
    def limpiar_dependencias(self):
        """Limpiar dependencias no utilizadas"""
        try:
            print_info("Limpiando dependencias no utilizadas...")
            
            # Instalar pip-autoremove si no está instalado
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pip-autoremove'], 
                             capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                print_warning("Error instalando pip-autoremove")
                return False
            
            # Limpiar dependencias
            try:
                resultado = subprocess.run([
                    sys.executable, '-m', 'pip_autoremove', '-y'
                ], capture_output=True, text=True, check=True, timeout=self.configuracion['timeout'])
                
                print_success("Dependencias no utilizadas limpiadas")
                return True
                
            except subprocess.CalledProcessError as e:
                print_error(f"Error limpiando dependencias: {e.stderr}")
                return False
            except subprocess.TimeoutExpired:
                print_error("Timeout limpiando dependencias")
                return False
            
        except Exception as e:
            print_error(f"Error limpiando dependencias: {e}")
            return False
    
    def generar_reporte_dependencias(self):
        """Generar reporte de dependencias"""
        try:
            print_info("Generando reporte de dependencias...")
            
            # Obtener información de dependencias
            dependencias_instaladas = self.listar_dependencias()
            conflictos = self.verificar_conflictos()
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'python': {
                    'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    'ejecutable': sys.executable
                },
                'dependencias': {
                    'total': len(dependencias_instaladas),
                    'principales': len([d for d in dependencias_instaladas if d['name'] in self.dependencias['principales']]),
                    'opcionales': len([d for d in dependencias_instaladas if d['name'] in self.dependencias['opcionales']]),
                    'desarrollo': len([d for d in dependencias_instaladas if d['name'] in self.dependencias['desarrollo']])
                },
                'conflictos': not conflictos,
                'detalles': dependencias_instaladas
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"dependencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de dependencias generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de dependencias:")
            print(f"Total: {reporte['dependencias']['total']}")
            print(f"Principales: {reporte['dependencias']['principales']}")
            print(f"Opcionales: {reporte['dependencias']['opcionales']}")
            print(f"Desarrollo: {reporte['dependencias']['desarrollo']}")
            print(f"Conflictos: {'Sí' if reporte['conflictos'] else 'No'}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de dependencias"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE DEPENDENCIAS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de dependencias")
    print("3. ✅ Verificar dependencias")
    print("4. 📦 Instalar dependencias")
    print("5. 🔄 Actualizar dependencias")
    print("6. ⚠️ Verificar conflictos")
    print("7. 📋 Listar dependencias")
    print("8. 🔍 Verificar dependencia específica")
    print("9. 📦 Instalar dependencia específica")
    print("10. ❌ Desinstalar dependencia específica")
    print("11. 📄 Generar requirements.txt")
    print("12. 🧹 Limpiar dependencias")
    print("13. 📊 Generar reporte")
    print("14. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de dependencias"""
    print_header()
    
    # Crear gestor de dependencias
    gestor = GestorDependencias()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-14): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de dependencias")
                if gestor.crear_estructura_dependencias():
                    print_success("Estructura de dependencias creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Verificando dependencias")
                if gestor.verificar_dependencias():
                    print_success("Dependencias verificadas correctamente")
                else:
                    print_error("Error verificando dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Instalando dependencias")
                try:
                    archivo = input("Archivo requirements (opcional): ").strip() or None
                    
                    if gestor.instalar_dependencias(archivo):
                        print_success("Dependencias instaladas correctamente")
                    else:
                        print_error("Error instalando dependencias")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Actualizando dependencias")
                if gestor.actualizar_dependencias():
                    print_success("Dependencias actualizadas correctamente")
                else:
                    print_error("Error actualizando dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Verificando conflictos")
                if gestor.verificar_conflictos():
                    print_success("No hay conflictos de dependencias")
                else:
                    print_warning("Se encontraron conflictos de dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Listando dependencias")
                dependencias = gestor.listar_dependencias()
                if dependencias:
                    print_success(f"Dependencias listadas: {len(dependencias)}")
                else:
                    print_warning("No hay dependencias para mostrar")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Verificando dependencia específica")
                try:
                    nombre = input("Nombre de la dependencia: ").strip()
                    
                    if gestor.verificar_dependencia(nombre):
                        print_success(f"Dependencia {nombre} instalada")
                    else:
                        print_warning(f"Dependencia {nombre} no instalada")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Instalando dependencia específica")
                try:
                    nombre = input("Nombre de la dependencia: ").strip()
                    version = input("Versión (opcional): ").strip() or None
                    
                    if gestor.instalar_dependencia(nombre, version):
                        print_success(f"Dependencia {nombre} instalada correctamente")
                    else:
                        print_error(f"Error instalando dependencia {nombre}")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_step("10", "Desinstalando dependencia específica")
                try:
                    nombre = input("Nombre de la dependencia: ").strip()
                    
                    if gestor.desinstalar_dependencia(nombre):
                        print_success(f"Dependencia {nombre} desinstalada correctamente")
                    else:
                        print_error(f"Error desinstalando dependencia {nombre}")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "11":
                print_step("11", "Generando requirements.txt")
                try:
                    archivo = input("Archivo de salida (opcional): ").strip() or None
                    
                    if gestor.generar_requirements(archivo):
                        print_success("Archivo requirements.txt generado correctamente")
                    else:
                        print_error("Error generando requirements.txt")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "12":
                print_step("12", "Limpiando dependencias")
                if gestor.limpiar_dependencias():
                    print_success("Dependencias limpiadas correctamente")
                else:
                    print_error("Error limpiando dependencias")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "13":
                print_step("13", "Generando reporte de dependencias")
                reporte = gestor.generar_reporte_dependencias()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "14":
                print_info("Saliendo del gestor de dependencias...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-14.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de dependencias interrumpida por el usuario")
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