#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Ejecución Simple - METGO_3D
Ejecuta los dashboards principales del sistema
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
        time.sleep(3)
        webbrowser.open(f'http://localhost:{puerto}')
        print(f"OK {dashboard} ejecutandose en http://localhost:{puerto}")
        return True
    except Exception as e:
        print(f"ERROR ejecutando {dashboard}: {e}")
        return False

def main():
    print("=" * 60)
    print("METGO_3D - SISTEMA DE DASHBOARDS LIMPIADO")
    print("=" * 60)
    
    # Verificar qué dashboards están disponibles
    dashboards_disponibles = []
    
    if os.path.exists('sistema_auth_dashboard_principal_metgo.py'):
        dashboards_disponibles.append(('sistema_auth_dashboard_principal_metgo.py', 8501))
    
    if os.path.exists('dashboard_agricola_sin_plotly_metgo.py'):
        dashboards_disponibles.append(('dashboard_agricola_sin_plotly_metgo.py', 8502))
    
    if os.path.exists('dashboard_completo_metgo.py'):
        dashboards_disponibles.append(('dashboard_completo_metgo.py', 8503))
    
    if os.path.exists('dashboard_global_metgo.py'):
        dashboards_disponibles.append(('dashboard_global_metgo.py', 8504))
    
    print("Dashboards disponibles encontrados:")
    for dashboard, puerto in dashboards_disponibles:
        print(f"  - {dashboard}")
    
    print("\nEjecutando dashboards principales...")
    
    for dashboard, puerto in dashboards_disponibles:
        ejecutar_dashboard(dashboard, puerto)
        time.sleep(2)  # Pausa entre ejecuciones
    
    print("\n" + "=" * 60)
    print("Sistema METGO_3D ejecutandose correctamente!")
    print("=" * 60)
    print("Dashboards disponibles:")
    
    for dashboard, puerto in dashboards_disponibles:
        print(f"  - {dashboard}: http://localhost:{puerto}")
    
    print("\nCredenciales por defecto:")
    print("  Usuario: admin")
    print("  Contrasena: admin123")

if __name__ == "__main__":
    main()

