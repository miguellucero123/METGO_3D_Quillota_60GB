#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutar Todos los Dashboards METGO_3D
Script simple para ejecutar todos los dashboards del sistema
"""

import subprocess
import sys
import time
import webbrowser
import os

def ejecutar_dashboard(dashboard, puerto):
    """Ejecutar un dashboard en un puerto específico"""
    try:
        print(f"Ejecutando {dashboard} en puerto {puerto}...")
        subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', dashboard,
            '--server.port', str(puerto), '--server.headless', 'true'
        ])
        time.sleep(2)
        print(f"OK {dashboard} ejecutandose en http://localhost:{puerto}")
        return True
    except Exception as e:
        print(f"ERROR ejecutando {dashboard}: {e}")
        return False

def main():
    print("=" * 80)
    print("METGO_3D - EJECUTANDO TODOS LOS DASHBOARDS")
    print("=" * 80)
    
    # Lista de dashboards disponibles en la raíz
    dashboards = [
        ('sistema_auth_dashboard_principal_metgo.py', 8500),
        ('dashboard_meteorologico_final.py', 8502),
        ('01_Sistema_Meteorologico/main.py', 8501),
        ('02_Sistema_Agricola/main.py', 8503),
        ('04_Dashboards_Unificados/main_dashboard.py', 8504),
        ('06_Modelos_ML_IA/main.py', 8505)
    ]
    
    print("Ejecutando dashboards disponibles...")
    
    dashboards_ejecutados = 0
    for dashboard, puerto in dashboards:
        if os.path.exists(dashboard):
            if ejecutar_dashboard(dashboard, puerto):
                dashboards_ejecutados += 1
        else:
            print(f"WARNING {dashboard} no encontrado")
    
    print(f"\nSistema ejecutado: {dashboards_ejecutados}/{len(dashboards)} dashboards activos")
    
    if dashboards_ejecutados > 0:
        print("\n" + "=" * 80)
        print("DASHBOARDS DISPONIBLES:")
        print("=" * 80)
        
        urls = [
            (8500, "Sistema Principal (Autenticación)"),
            (8501, "Sistema Meteorológico (Nuevo)"),
            (8502, "Dashboard Meteorológico (Original)"),
            (8503, "Sistema Agrícola (Nuevo)"),
            (8504, "Dashboard Unificado"),
            (8505, "Modelos ML/IA")
        ]
        
        for puerto, descripcion in urls:
            print(f"  - {descripcion}: http://localhost:{puerto}")
        
        print("\nCREDENCIALES:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        
        print("\n¡Sistema METGO_3D ejecutandose correctamente!")

if __name__ == "__main__":
    main()
