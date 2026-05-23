#!/usr/bin/env python3
"""
Sistema METGO - Inicio Automático
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import subprocess
import time
import sys
import os
from datetime import datetime
import psutil

def verificar_proceso_puerto(puerto):
    """Verifica si hay un proceso ejecutándose en un puerto específico"""
    for conn in psutil.net_connections():
        if conn.laddr.port == puerto and conn.status == 'LISTEN':
            return True
    return False

def iniciar_dashboard(archivo, puerto, nombre):
    """Inicia un dashboard en un puerto específico"""
    try:
        if verificar_proceso_puerto(puerto):
            print(f"OK - {nombre} ya esta ejecutandose en puerto {puerto}")
            return True
            
        print(f"Iniciando {nombre} en puerto {puerto}...")
        
        cmd = [
            sys.executable, "-m", "streamlit", "run", archivo,
            "--server.port", str(puerto),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        
        # Esperar a que el proceso se inicie
        time.sleep(3)
        
        if verificar_proceso_puerto(puerto):
            print(f"OK - {nombre} iniciado correctamente en puerto {puerto}")
            return True
        else:
            print(f"ERROR - Error al iniciar {nombre}")
            return False
            
    except Exception as e:
        print(f"ERROR - Error al iniciar {nombre}: {e}")
        return False

def main():
    """Función principal de inicio automático"""
    print("=" * 60)
    print("SISTEMA METGO - INICIO AUTOMATICO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de dashboards a iniciar
    dashboards = [
        ("sistema_auth_dashboard_principal_metgo.py", 8501, "Dashboard Principal"),
        ("dashboard_meteorologico_profesional.py", 8502, "Meteorológico Profesional"),
        ("dashboard_agricola_inteligente.py", 8503, "Agrícola Inteligente"),
        ("dashboard_monitoreo_tiempo_real.py", 8504, "Monitoreo Tiempo Real"),
        ("dashboard_ia_ml_avanzado.py", 8505, "IA/ML Avanzado"),
        ("dashboard_visualizaciones_avanzadas.py", 8506, "Visualizaciones Avanzadas"),
        ("dashboard_global_metricas.py", 8507, "Global Métricas"),
        ("dashboard_agricultura_precision.py", 8508, "Agricultura Precisión"),
        ("dashboard_analisis_comparativo.py", 8509, "Análisis Comparativo"),
        ("dashboard_alertas_automaticas.py", 8510, "Alertas Automáticas"),
        ("dashboard_simple_optimizado.py", 8511, "Dashboard Simple"),
        ("dashboard_unificado_diferenciado.py", 8512, "Dashboard Unificado"),
        ("dashboard_mobile_optimizado.py", 8513, "Dashboard Móvil"),
        ("notificaciones_mobile.py", 8514, "Notificaciones Móviles"),
        ("cache_offline_mobile.py", 8515, "Caché Offline")
    ]
    
    print("INICIANDO DASHBOARDS...")
    print("-" * 50)
    
    exitosos = 0
    fallidos = 0
    
    for archivo, puerto, nombre in dashboards:
        if os.path.exists(archivo):
            if iniciar_dashboard(archivo, puerto, nombre):
                exitosos += 1
            else:
                fallidos += 1
        else:
            print(f"WARN - Archivo no encontrado: {archivo}")
            fallidos += 1
        
        time.sleep(1)  # Pausa entre inicios
    
    print("-" * 50)
    print(f"RESULTADO: {exitosos} exitosos, {fallidos} fallidos")
    print()
    
    if exitosos > 0:
        print("DASHBOARDS ACCESIBLES:")
        print("-" * 30)
        for archivo, puerto, nombre in dashboards:
            if verificar_proceso_puerto(puerto):
                print(f"OK - {nombre}: http://192.168.1.7:{puerto}")
        
        print()
        print("URL PRINCIPAL: http://192.168.1.7:8501")
        print()
        print("Para detener el sistema, ejecuta: detener_sistema.py")
        print("Para monitorear el sistema, ejecuta: monitorear_sistema.py")
    else:
        print("ERROR - No se pudo iniciar ningun dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
