"""
SCRIPT DE VERIFICACIÓN DE ESTADO - METGO 3D QUILLOTA
Verifica el estado de todos los servicios del sistema
"""

import requests
import subprocess
import os
import sys
from datetime import datetime

def verificar_estado():
    """Verificar estado del sistema"""
    print("="*60)
    print("VERIFICANDO ESTADO DEL SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Servicios a verificar
    servicios = [
        {'nombre': 'Dashboard Principal', 'url': 'http://localhost:8501', 'puerto': 8501},
        {'nombre': 'Dashboard Agrícola', 'url': 'http://localhost:8510', 'puerto': 8510},
        {'nombre': 'Sistema de Monitoreo', 'url': 'http://localhost:8502', 'puerto': 8502}
    ]
    
    servicios_activos = 0
    servicios_totales = len(servicios)
    
    for servicio in servicios:
        print(f"\n[VERIFICANDO] {servicio['nombre']}...")
        try:
            response = requests.get(servicio['url'], timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {servicio['nombre']} - Activo (Status: {response.status_code})")
                servicios_activos += 1
            else:
                print(f"  [ERROR] {servicio['nombre']} - Error (Status: {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"  [ERROR] {servicio['nombre']} - No disponible")
        except Exception as e:
            print(f"  [ERROR] {servicio['nombre']} - Error: {e}")
    
    # Verificar procesos
    print("\n[VERIFICANDO] Procesos del sistema...")
    try:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            procesos_python = result.stdout.count('python.exe')
            print(f"  [INFO] Procesos Python activos: {procesos_python}")
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            procesos_streamlit = result.stdout.count('streamlit')
            print(f"  [INFO] Procesos Streamlit activos: {procesos_streamlit}")
    except Exception as e:
        print(f"  [ADVERTENCIA] Error verificando procesos: {e}")
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE ESTADO")
    print("="*60)
    print(f"Servicios activos: {servicios_activos}/{servicios_totales}")
    
    if servicios_activos == servicios_totales:
        print("Estado: [OK] Todos los servicios funcionando correctamente")
        return True
    elif servicios_activos > 0:
        print("Estado: [ADVERTENCIA] Algunos servicios no están funcionando")
        return False
    else:
        print("Estado: [ERROR] Ningún servicio está funcionando")
        return False

if __name__ == "__main__":
    verificar_estado()
