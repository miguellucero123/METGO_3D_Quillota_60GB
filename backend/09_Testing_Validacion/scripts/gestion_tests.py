#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE TESTS DEL SISTEMA METGO 3D
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
    print("🌾 GESTIÓN DE TESTS DEL SISTEMA METGO 3D")
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

class GestorTests:
    """Clase para gestión de tests del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_tests': 'tests',
            'directorio_coverage': 'coverage',
            'archivo_config': 'pytest.ini',
            'framework': 'pytest',
            'coverage_min': 80,
            'timeout': 300
        }
        
        self.tipos_tests = [
            'unitarios',
            'integración',
            'funcionales',
            'rendimiento',
            'seguridad'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de tests"""
        try:
            print_info("Cargando configuración de tests...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_tests(self):
        """Crear estructura de tests"""
        try:
            print_info("Creando estructura de tests...")
            
            # Crear directorio principal
            tests_dir = Path(self.configuracion['directorio_tests'])
            tests_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            for tipo in self.tipos_tests:
                tipo_dir = tests_dir / tipo
                tipo_dir.mkdir(exist_ok=True)
                
                # Crear __init__.py
                init_file = tipo_dir / '__init__.py'
                if not init_file.exists():
                    init_file.write_text('')
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            print_success("Estructura de tests creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # pytest.ini
            pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    functional: Functional tests
    performance: Performance tests
    security: Security tests
"""
            
            pytest_file = Path('pytest.ini')
            pytest_file.write_text(pytest_config)
            
            # conftest.py
            conftest_content = '''import pytest
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def config_test():
    """Configuración para tests"""
    return {
        'debug': True,
        'test_mode': True
    }
'''
            
            conftest_file = Path('tests/conftest.py')
            conftest_file.write_text(conftest_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def ejecutar_tests(self, tipo=None, archivo=None):
        """Ejecutar tests"""
        try:
            print_info("Ejecutando tests...")
            
            # Verificar pytest
            try:
                subprocess.run(['pytest', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_error("pytest no está instalado")
                return False
            
            # Construir comando
            comando = ['pytest']
            
            if tipo:
                comando.extend(['-m', tipo])
            
            if archivo:
                comando.append(archivo)
            else:
                comando.append('tests/')
            
            # Ejecutar tests
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=self.configuracion['timeout'])
            
            if resultado.returncode == 0:
                print_success("Tests ejecutados correctamente")
                print(resultado.stdout)
                return True
            else:
                print_error("Error ejecutando tests")
                if resultado.stderr:
                    print(resultado.stderr)
                return False
            
        except subprocess.TimeoutExpired:
            print_error("Timeout ejecutando tests")
            return False
        except Exception as e:
            print_error(f"Error ejecutando tests: {e}")
            return False
    
    def ejecutar_coverage(self):
        """Ejecutar tests con cobertura"""
        try:
            print_info("Ejecutando tests con cobertura...")
            
            # Verificar coverage
            try:
                subprocess.run(['coverage', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print_info("Instalando coverage...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], check=True)
            
            # Ejecutar con coverage
            comando = ['coverage', 'run', '-m', 'pytest', 'tests/']
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=self.configuracion['timeout'])
            
            if resultado.returncode == 0:
                # Generar reporte
                subprocess.run(['coverage', 'report'], check=True)
                subprocess.run(['coverage', 'html'], check=True)
                print_success("Tests con cobertura ejecutados")
                return True
            else:
                print_error("Error ejecutando tests con cobertura")
                return False
            
        except Exception as e:
            print_error(f"Error ejecutando coverage: {e}")
            return False
    
    def generar_reporte_tests(self):
        """Generar reporte de tests"""
        try:
            print_info("Generando reporte de tests...")
            
            # Ejecutar tests y capturar resultado
            resultado = subprocess.run(['pytest', 'tests/', '--json-report', '--json-report-file=test_report.json'], 
                                     capture_output=True, text=True, timeout=self.configuracion['timeout'])
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'tests': {
                    'ejecutados': 0,
                    'exitosos': 0,
                    'fallidos': 0,
                    'omitidos': 0,
                    'errores': 0
                },
                'cobertura': {
                    'porcentaje': 0,
                    'lineas_cubiertas': 0,
                    'lineas_totales': 0
                }
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de tests generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de tests"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE TESTS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de tests")
    print("3. ▶️ Ejecutar tests")
    print("4. 📊 Ejecutar tests con cobertura")
    print("5. 📄 Generar reporte")
    print("6. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de tests"""
    print_header()
    
    # Crear gestor de tests
    gestor = GestorTests()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de tests")
                if gestor.crear_estructura_tests():
                    print_success("Estructura de tests creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Ejecutando tests")
                tipo = input("Tipo de test (opcional): ").strip() or None
                archivo = input("Archivo específico (opcional): ").strip() or None
                
                if gestor.ejecutar_tests(tipo, archivo):
                    print_success("Tests ejecutados correctamente")
                else:
                    print_error("Error ejecutando tests")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Ejecutando tests con cobertura")
                if gestor.ejecutar_coverage():
                    print_success("Tests con cobertura ejecutados correctamente")
                else:
                    print_error("Error ejecutando tests con cobertura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Generando reporte de tests")
                reporte = gestor.generar_reporte_tests()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_info("Saliendo del gestor de tests...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-6.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de tests interrumpida por el usuario")
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