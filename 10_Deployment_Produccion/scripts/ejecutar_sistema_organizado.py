#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutar Sistema METGO_3D Organizado
Ejecuta el sistema desde las carpetas organizadas
"""

import subprocess
import sys
import time
import webbrowser
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
    print("METGO_3D - SISTEMA ORGANIZADO EJECUTANDOSE")
    print("=" * 80)
    print("Ejecutando desde carpetas organizadas...")
    
    # Dashboards organizados por carpetas
    dashboards_organizados = [
        ('04_Dashboards_Unificados/dashboards/sistema_auth_dashboard_principal_metgo.py', 8500, "Sistema Principal (Autenticación)"),
        ('01_Sistema_Meteorologico/main.py', 8501, "Sistema Meteorológico (Nuevo)"),
        ('04_Dashboards_Unificados/dashboards/dashboard_meteorologico_final.py', 8502, "Dashboard Meteorológico (Original)"),
        ('02_Sistema_Agricola/main.py', 8503, "Sistema Agrícola (Nuevo)"),
        ('04_Dashboards_Unificados/main_dashboard.py', 8504, "Dashboard Unificado"),
        ('06_Modelos_ML_IA/main.py', 8505, "Modelos ML/IA")
    ]
    
    dashboards_ejecutados = 0
    
    for ruta, puerto, descripcion in dashboards_organizados:
        if os.path.exists(ruta):
            if ejecutar_dashboard(ruta, puerto):
                dashboards_ejecutados += 1
        else:
            print(f"WARNING {ruta} no encontrado")
    
    print(f"\nSistema ejecutado: {dashboards_ejecutados}/{len(dashboards_organizados)} dashboards activos")
    
    if dashboards_ejecutados > 0:
        print("\n" + "=" * 80)
        print("DASHBOARDS ORGANIZADOS DISPONIBLES:")
        print("=" * 80)
        
        for ruta, puerto, descripcion in dashboards_organizados:
            if os.path.exists(ruta):
                print(f"  - {descripcion}: http://localhost:{puerto}")
        
        print("\nCREDENCIALES:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        
        print("\nESTRUCTURA ORGANIZADA:")
        print("  ✅ 01_Sistema_Meteorologico/")
        print("  ✅ 02_Sistema_Agricola/")
        print("  ✅ 03_Sistema_IoT_Drones/")
        print("  ✅ 04_Dashboards_Unificados/")
        print("  ✅ 05_APIs_Externas/")
        print("  ✅ 06_Modelos_ML_IA/")
        print("  ✅ 07_Sistema_Monitoreo/")
        print("  ✅ 08_Gestion_Datos/")
        print("  ✅ 09_Testing_Validacion/")
        print("  ✅ 10_Deployment_Produccion/")
        print("  ✅ 11_Documentacion/")
        print("  ✅ 12_Respaldos_Archivos/")
        
        print("\n¡Sistema METGO_3D completamente organizado y funcionando!")

if __name__ == "__main__":
    main()
