#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutar Sistema METGO_3D Organizado
Script final para ejecutar el sistema desde estructura organizada
"""

import subprocess
import sys
import time
import os

def ejecutar_dashboard(ruta_dashboard, puerto):
    """Ejecutar un dashboard desde su ruta organizada"""
    try:
        print(f"Ejecutando {ruta_dashboard} en puerto {puerto}...")
        subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', ruta_dashboard,
            '--server.port', str(puerto), '--server.headless', 'true'
        ])
        time.sleep(2)
        print(f"OK {ruta_dashboard} ejecutandose en http://localhost:{puerto}")
        return True
    except Exception as e:
        print(f"ERROR ejecutando {ruta_dashboard}: {e}")
        return False

def main():
    print("=" * 80)
    print("METGO_3D - SISTEMA COMPLETAMENTE ORGANIZADO")
    print("=" * 80)
    
    # Dashboards organizados
    dashboards = [
        ('04_Dashboards_Unificados/dashboards/sistema_auth_dashboard_principal_metgo.py', 8500, "Sistema Principal"),
        ('01_Sistema_Meteorologico/main.py', 8501, "Sistema Meteorológico"),
        ('02_Sistema_Agricola/main.py', 8503, "Sistema Agrícola"),
        ('04_Dashboards_Unificados/main_dashboard.py', 8504, "Dashboard Unificado"),
        ('06_Modelos_ML_IA/main.py', 8505, "Modelos ML/IA")
    ]
    
    dashboards_ejecutados = 0
    
    for ruta, puerto, descripcion in dashboards:
        if os.path.exists(ruta):
            if ejecutar_dashboard(ruta, puerto):
                dashboards_ejecutados += 1
        else:
            print(f"WARNING {ruta} no encontrado")
    
    print(f"\nSistema ejecutado: {dashboards_ejecutados}/{len(dashboards)} dashboards activos")
    
    if dashboards_ejecutados > 0:
        print("\n" + "=" * 80)
        print("DASHBOARDS DISPONIBLES:")
        print("=" * 80)
        
        for ruta, puerto, descripcion in dashboards:
            if os.path.exists(ruta):
                print(f"  - {descripcion}: http://localhost:{puerto}")
        
        print("\nCredenciales: admin / admin123")
        print("\n¡Sistema METGO_3D completamente organizado y funcionando!")

if __name__ == "__main__":
    main()
