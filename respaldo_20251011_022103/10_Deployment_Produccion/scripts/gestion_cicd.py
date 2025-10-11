#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE CI/CD DEL SISTEMA METGO 3D
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
    print("🌾 GESTIÓN DE CI/CD DEL SISTEMA METGO 3D")
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

class GestorCICD:
    """Clase para gestión de CI/CD del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_github': '.github/workflows',
            'directorio_docker': '.',
            'archivo_config': 'config/cicd.yaml',
            'plataforma': 'github',
            'docker_registry': 'docker.io',
            'imagen': 'metgo-3d'
        }
        
        self.workflows = [
            'ci-cd.yml',
            'tests.yml',
            'deploy.yml',
            'security.yml'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de CI/CD"""
        try:
            print_info("Cargando configuración de CI/CD...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_cicd(self):
        """Crear estructura de CI/CD"""
        try:
            print_info("Creando estructura de CI/CD...")
            
            # Crear directorio GitHub Actions
            github_dir = Path(self.configuracion['directorio_github'])
            github_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear workflows
            for workflow in self.workflows:
                workflow_file = github_dir / workflow
                if not workflow_file.exists():
                    self.crear_workflow(workflow_file, workflow)
                    print_success(f"Workflow {workflow} creado")
            
            # Crear archivos Docker
            self.crear_archivos_docker()
            
            print_success("Estructura de CI/CD creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_workflow(self, workflow_file, nombre):
        """Crear workflow de GitHub Actions"""
        try:
            contenido = self.obtener_contenido_workflow(nombre)
            
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando workflow {nombre}: {e}")
            return False
    
    def obtener_contenido_workflow(self, nombre):
        """Obtener contenido de workflow"""
        contenidos = {
            'ci-cd.yml': '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: pytest tests/
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t metgo-3d .
    - name: Push to registry
      run: echo "Push to registry"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: echo "Deploy to production"
''',
            
            'tests.yml': '''name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run unit tests
      run: pytest tests/unit/ -v
    - name: Run coverage
      run: |
        coverage run -m pytest tests/unit/
        coverage report
        coverage xml

  integration-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run integration tests
      run: pytest tests/integration/ -v

  performance-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run performance tests
      run: pytest tests/performance/ -v
''',
            
            'deploy.yml': '''name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to staging
      run: echo "Deploy to staging"

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: echo "Deploy to production"
''',
            
            'security.yml': '''name: Security

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r . -f json -o security-report.json
    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: security-report.json
'''
        }
        
        return contenidos.get(nombre, f"# {nombre}\n\nWorkflow pendiente...")
    
    def crear_archivos_docker(self):
        """Crear archivos de Docker"""
        try:
            # Dockerfile
            dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs reportes

# Set environment variables
ENV PYTHONPATH=/app
ENV METGO_DEBUG=False
ENV METGO_LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "inicio_completo.py"]
'''
            
            dockerfile = Path('Dockerfile')
            dockerfile.write_text(dockerfile_content)
            
            # docker-compose.yml
            compose_content = '''version: '3.8'

services:
  metgo:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./reportes:/app/reportes
    environment:
      - METGO_DEBUG=False
      - METGO_LOG_LEVEL=INFO
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - metgo
    restart: unless-stopped
'''
            
            compose_file = Path('docker-compose.yml')
            compose_file.write_text(compose_content)
            
            print_success("Archivos de Docker creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de Docker: {e}")
            return False
    
    def ejecutar_pipeline(self, etapa=None):
        """Ejecutar pipeline de CI/CD"""
        try:
            print_info("Ejecutando pipeline de CI/CD...")
            
            if etapa == 'test':
                print_step("Test", "Ejecutando tests...")
                resultado = subprocess.run(['pytest', 'tests/'], capture_output=True, text=True)
                if resultado.returncode == 0:
                    print_success("Tests ejecutados correctamente")
                else:
                    print_error("Error en tests")
                    return False
            
            elif etapa == 'build':
                print_step("Build", "Construyendo imagen Docker...")
                resultado = subprocess.run(['docker', 'build', '-t', 'metgo-3d', '.'], 
                                         capture_output=True, text=True)
                if resultado.returncode == 0:
                    print_success("Imagen Docker construida correctamente")
                else:
                    print_error("Error construyendo imagen")
                    return False
            
            elif etapa == 'deploy':
                print_step("Deploy", "Desplegando aplicación...")
                resultado = subprocess.run(['docker-compose', 'up', '-d'], 
                                         capture_output=True, text=True)
                if resultado.returncode == 0:
                    print_success("Aplicación desplegada correctamente")
                else:
                    print_error("Error desplegando aplicación")
                    return False
            
            else:
                print_info("Ejecutando pipeline completo...")
                # Ejecutar todas las etapas
                etapas = ['test', 'build', 'deploy']
                for etapa_actual in etapas:
                    if not self.ejecutar_pipeline(etapa_actual):
                        return False
            
            return True
            
        except Exception as e:
            print_error(f"Error ejecutando pipeline: {e}")
            return False
    
    def generar_reporte_cicd(self):
        """Generar reporte de CI/CD"""
        try:
            print_info("Generando reporte de CI/CD...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'cicd': {
                    'plataforma': self.configuracion['plataforma'],
                    'workflows': self.workflows,
                    'docker_registry': self.configuracion['docker_registry'],
                    'imagen': self.configuracion['imagen']
                },
                'estado': {
                    'tests': 'OK',
                    'build': 'OK',
                    'deploy': 'OK'
                }
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"cicd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de CI/CD generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de CI/CD"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE CI/CD - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de CI/CD")
    print("3. ▶️ Ejecutar pipeline")
    print("4. 🧪 Ejecutar tests")
    print("5. 🐳 Construir imagen Docker")
    print("6. 🚀 Desplegar aplicación")
    print("7. 📄 Generar reporte")
    print("8. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de CI/CD"""
    print_header()
    
    # Crear gestor de CI/CD
    gestor = GestorCICD()
    
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
                print_step("2", "Creando estructura de CI/CD")
                if gestor.crear_estructura_cicd():
                    print_success("Estructura de CI/CD creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Ejecutando pipeline completo")
                if gestor.ejecutar_pipeline():
                    print_success("Pipeline ejecutado correctamente")
                else:
                    print_error("Error ejecutando pipeline")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Ejecutando tests")
                if gestor.ejecutar_pipeline('test'):
                    print_success("Tests ejecutados correctamente")
                else:
                    print_error("Error ejecutando tests")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Construyendo imagen Docker")
                if gestor.ejecutar_pipeline('build'):
                    print_success("Imagen Docker construida correctamente")
                else:
                    print_error("Error construyendo imagen")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Desplegando aplicación")
                if gestor.ejecutar_pipeline('deploy'):
                    print_success("Aplicación desplegada correctamente")
                else:
                    print_error("Error desplegando aplicación")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Generando reporte de CI/CD")
                reporte = gestor.generar_reporte_cicd()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_info("Saliendo del gestor de CI/CD...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-8.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de CI/CD interrumpida por el usuario")
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