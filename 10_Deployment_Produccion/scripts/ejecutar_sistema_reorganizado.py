#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema METGO_3D - Ejecución Principal Reorganizado
Ejecuta el sistema completo desde la estructura organizada
"""

import os
import sys
import subprocess
import webbrowser
import time

def ejecutar_modulo(modulo, puerto):
    """Ejecutar un módulo específico"""
    try:
        print(f"Ejecutando {modulo} en puerto {puerto}...")
        
        # Buscar script principal del módulo
        script_path = None
        posibles_scripts = [
            f"{modulo}/main.py",
            f"{modulo}/scripts/main.py",
            f"{modulo}/dashboards/main_dashboard.py",
            f"{modulo}/main_dashboard.py"
        ]
        
        for script in posibles_scripts:
            if os.path.exists(script):
                script_path = script
                break
        
        if script_path:
            subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', script_path,
                '--server.port', str(puerto), '--server.headless', 'true'
            ])
            time.sleep(2)
            webbrowser.open(f'http://localhost:{puerto}')
            print(f"OK {modulo} ejecutandose en http://localhost:{puerto}")
            return True
        else:
            print(f"WARNING No se encontro script principal para {modulo}")
            return False
            
    except Exception as e:
        print(f"ERROR ejecutando {modulo}: {e}")
        return False

def main():
    print("=" * 80)
    print("METGO_3D - SISTEMA REORGANIZADO")
    print("=" * 80)
    
    modulos = [
        ('01_Sistema_Meteorologico', 8501),
        ('02_Sistema_Agricola', 8502),
        ('04_Dashboards_Unificados', 8503),
        ('06_Modelos_ML_IA', 8504)
    ]
    
    print("Ejecutando módulos principales...")
    
    modulos_ejecutados = 0
    for modulo, puerto in modulos:
        if os.path.exists(modulo):
            if ejecutar_modulo(modulo, puerto):
                modulos_ejecutados += 1
        else:
            print(f"WARNING Modulo {modulo} no encontrado")
    
    print(f"\nSistema ejecutado: {modulos_ejecutados}/{len(modulos)} módulos activos")
    
    if modulos_ejecutados > 0:
        print("\nURLs del Sistema:")
        for modulo, puerto in modulos:
            print(f"  - {modulo}: http://localhost:{puerto}")

if __name__ == "__main__":
    main()
