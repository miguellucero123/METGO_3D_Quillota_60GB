"""
SCRIPT DE DEPLOYMENT CON DOCKER - METGO 3D QUILLOTA
Despliega el sistema usando Docker
"""

import subprocess
import os
import sys

def deploy_docker():
    """Desplegar sistema con Docker"""
    print("="*60)
    print("DEPLOYMENT CON DOCKER - METGO 3D QUILLOTA")
    print("="*60)
    
    # Verificar Docker
    print("\n[VERIFICANDO] Docker...")
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("  [OK] Docker disponible")
    except subprocess.CalledProcessError:
        print("  [ERROR] Docker no está instalado o no está en el PATH")
        return False
    
    # Construir imagen
    print("\n[CONSTRUYENDO] Imagen Docker...")
    try:
        subprocess.run(['docker', 'build', '-t', 'metgo-quillota', '.'], check=True)
        print("  [OK] Imagen construida exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error construyendo imagen: {e}")
        return False
    
    # Iniciar servicios
    print("\n[INICIANDO] Servicios con Docker Compose...")
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("  [OK] Servicios iniciados")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error iniciando servicios: {e}")
        return False
    
    print("\n[COMPLETADO] Sistema desplegado con Docker")
    print("\nServicios disponibles:")
    print("  - Dashboard Principal: http://localhost:8501")
    print("  - Dashboard Agrícola: http://localhost:8510")
    print("  - Monitoreo: http://localhost:8502")
    
    return True

if __name__ == "__main__":
    deploy_docker()
