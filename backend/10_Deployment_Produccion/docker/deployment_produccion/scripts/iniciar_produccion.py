"""
SCRIPT DE INICIO DE PRODUCCIÓN - METGO 3D QUILLOTA
Inicia todos los servicios del sistema en modo producción
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime

def iniciar_produccion():
    """Iniciar sistema en modo producción"""
    print("="*60)
    print("INICIANDO SISTEMA METGO 3D QUILLOTA EN PRODUCCIÓN")
    print("="*60)
    
    # Verificar dependencias
    print("\n[VERIFICANDO] Dependencias del sistema...")
    try:
        import streamlit
        import pandas
        import plotly
        import sklearn
        print("  [OK] Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"  [ERROR] Dependencia faltante: {e}")
        return False
    
    # Iniciar servicios
    servicios = [
        {
            'nombre': 'Dashboard Principal',
            'comando': ['python', '-m', 'streamlit', 'run', 'sistema_unificado_con_conectores.py', 
                       '--server.port', '8501', '--server.headless', 'true'],
            'puerto': 8501
        },
        {
            'nombre': 'Dashboard Agrícola Avanzado',
            'comando': ['python', '-m', 'streamlit', 'run', 'dashboard_agricola_avanzado.py',
                       '--server.port', '8510', '--server.headless', 'true'],
            'puerto': 8510
        },
        {
            'nombre': 'Sistema de Monitoreo',
            'comando': ['python', 'monitoreo_tiempo_real.py'],
            'puerto': 8502
        }
    ]
    
    procesos = []
    
    for servicio in servicios:
        print(f"\n[INICIANDO] {servicio['nombre']}...")
        try:
            proceso = subprocess.Popen(servicio['comando'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            procesos.append({
                'proceso': proceso,
                'nombre': servicio['nombre'],
                'puerto': servicio['puerto']
            })
            print(f"  [OK] {servicio['nombre']} iniciado (PID: {proceso.pid})")
            time.sleep(2)  # Esperar entre servicios
        except Exception as e:
            print(f"  [ERROR] Error iniciando {servicio['nombre']}: {e}")
    
    # Verificar estado de servicios
    print("\n[VERIFICANDO] Estado de servicios...")
    for proc_info in procesos:
        if proc_info['proceso'].poll() is None:
            print(f"  [OK] {proc_info['nombre']} - Activo")
        else:
            print(f"  [ERROR] {proc_info['nombre']} - Inactivo")
    
    print("\n" + "="*60)
    print("SISTEMA METGO 3D QUILLOTA INICIADO EN PRODUCCIÓN")
    print("="*60)
    print("\nServicios disponibles:")
    print("  - Dashboard Principal: http://localhost:8501")
    print("  - Dashboard Agrícola: http://localhost:8510")
    print("  - Monitoreo: http://localhost:8502")
    print("\nPara detener el sistema, ejecute: python parar_produccion.py")
    
    return True

if __name__ == "__main__":
    iniciar_produccion()
