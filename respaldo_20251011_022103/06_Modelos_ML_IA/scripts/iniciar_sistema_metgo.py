#!/usr/bin/env python3
"""
Iniciador del Sistema METGO 3D - Versión Simplificada
"""

import subprocess
import sys
import os
import time
import requests

def verificar_puerto(puerto):
    """Verificar si un puerto está disponible"""
    try:
        response = requests.get(f"http://localhost:{puerto}/_stcore/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def ejecutar_dashboard(archivo, puerto, nombre):
    """Ejecutar un dashboard"""
    if verificar_puerto(puerto):
        print(f"[OK] {nombre} ya está ejecutándose en puerto {puerto}")
        return True
    
    try:
        print(f"[INICIANDO] {nombre} en puerto {puerto}...")
        
        comando = [
            sys.executable, "-m", "streamlit", "run", 
            archivo, 
            "--server.port", str(puerto), 
            "--server.headless", "true"
        ]
        
        proceso = subprocess.Popen(
            comando, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        time.sleep(3)
        
        if verificar_puerto(puerto):
            print(f"[OK] {nombre} iniciado en http://localhost:{puerto}")
            return True
        else:
            print(f"[ERROR] {nombre} no se inició correctamente")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando {nombre}: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("INICIANDO SISTEMA METGO 3D QUILLOTA")
    print("=" * 60)
    
    # Lista de dashboards en orden de prioridad
    dashboards = [
        ("sistema_autenticacion_metgo.py", 8500, "Sistema de Autenticación"),
        ("dashboard_meteorologico_final.py", 8502, "Dashboard Meteorológico Mejorado"),
        ("dashboard_integrado_recomendaciones_metgo.py", 8510, "Dashboard de Recomendaciones"),
        ("sistema_alertas_visuales_integrado_metgo.py", 8511, "Sistema de Alertas"),
        ("dashboard_principal_integrado_metgo.py", 8512, "Dashboard Principal Integrado"),
        ("dashboard_agricola_avanzado.py", 8501, "Dashboard Agrícola"),
        ("dashboard_empresarial_unificado_metgo.py", 8503, "Dashboard Empresarial"),
        ("dashboard_central_metgo.py", 8509, "Dashboard Central")
    ]
    
    exitosos = 0
    fallidos = 0
    
    for archivo, puerto, nombre in dashboards:
        if ejecutar_dashboard(archivo, puerto, nombre):
            exitosos += 1
        else:
            fallidos += 1
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("RESUMEN DE INICIO")
    print("=" * 60)
    print(f"Dashboards exitosos: {exitosos}")
    print(f"Dashboards fallidos: {fallidos}")
    
    if exitosos > 0:
        print("\nDASHBOARDS DISPONIBLES:")
        for archivo, puerto, nombre in dashboards:
            if verificar_puerto(puerto):
                print(f"  - {nombre}: http://localhost:{puerto}")
        
        print("\nUSUARIOS DE PRUEBA:")
        print("  - admin / admin123")
        print("  - agricultor / agricultor123")
        print("  - tecnico / tecnico123")
        
        print("\nINSTRUCCIONES:")
        print("  1. Accede al Sistema de Autenticación: http://localhost:8500")
        print("  2. Inicia sesión con cualquier usuario de prueba")
        print("  3. Selecciona el dashboard que deseas usar")
        
        # Abrir automáticamente
        try:
            import webbrowser
            webbrowser.open("http://localhost:8500")
            print("\n[Navegador] Abriendo sistema de autenticación...")
        except:
            print("\n[INFO] Abre manualmente: http://localhost:8500")

if __name__ == "__main__":
    main()


