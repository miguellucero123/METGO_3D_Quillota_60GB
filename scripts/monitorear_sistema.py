#!/usr/bin/env python3
"""
Sistema METGO - Monitor del Sistema
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import time
import psutil
import requests
from datetime import datetime
import sys

def verificar_dashboard(puerto, nombre):
    """Verifica si un dashboard está funcionando correctamente"""
    try:
        url = f"http://192.168.1.7:{puerto}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, "OK"
        else:
            return False, f"Error {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, "No accesible"

def obtener_info_proceso(puerto):
    """Obtiene información del proceso que usa un puerto"""
    for conn in psutil.net_connections():
        if conn.laddr.port == puerto and conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                return {
                    'pid': proc.pid,
                    'cpu': proc.cpu_percent(),
                    'memoria': proc.memory_info().rss / 1024 / 1024,  # MB
                    'tiempo': time.time() - proc.create_time()
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
    return None

def formatear_tiempo(segundos):
    """Formatea segundos en formato legible"""
    if segundos < 60:
        return f"{int(segundos)}s"
    elif segundos < 3600:
        return f"{int(segundos/60)}m {int(segundos%60)}s"
    else:
        horas = int(segundos/3600)
        minutos = int((segundos%3600)/60)
        return f"{horas}h {minutos}m"

def main():
    """Función principal de monitoreo"""
    print("=" * 80)
    print("SISTEMA METGO - MONITOR DEL SISTEMA")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de dashboards a monitorear
    dashboards = [
        (8501, "Dashboard Principal"),
        (8502, "Meteorológico Profesional"),
        (8503, "Agrícola Inteligente"),
        (8504, "Monitoreo Tiempo Real"),
        (8505, "IA/ML Avanzado"),
        (8506, "Visualizaciones Avanzadas"),
        (8507, "Global Métricas"),
        (8508, "Agricultura Precisión"),
        (8509, "Análisis Comparativo"),
        (8510, "Alertas Automáticas"),
        (8511, "Dashboard Simple"),
        (8512, "Dashboard Unificado"),
        (8513, "Dashboard Móvil"),
        (8514, "Notificaciones Móviles"),
        (8515, "Caché Offline")
    ]
    
    print(f"{'Dashboard':<25} {'Puerto':<8} {'Estado':<12} {'PID':<8} {'CPU%':<8} {'Mem(MB)':<10} {'Tiempo':<12}")
    print("-" * 80)
    
    total_activos = 0
    total_cpu = 0
    total_memoria = 0
    
    for puerto, nombre in dashboards:
        # Verificar estado del dashboard
        estado_ok, estado_texto = verificar_dashboard(puerto, nombre)
        
        # Obtener información del proceso
        info_proceso = obtener_info_proceso(puerto)
        
        if info_proceso:
            total_activos += 1
            total_cpu += info_proceso['cpu']
            total_memoria += info_proceso['memoria']
            
            print(f"{nombre:<25} {puerto:<8} {estado_texto:<12} {info_proceso['pid']:<8} "
                  f"{info_proceso['cpu']:<8.1f} {info_proceso['memoria']:<10.1f} "
                  f"{formatear_tiempo(info_proceso['tiempo']):<12}")
        else:
            print(f"{nombre:<25} {puerto:<8} {estado_texto:<12} {'N/A':<8} {'N/A':<8} {'N/A':<10} {'N/A':<12}")
    
    print("-" * 80)
    print(f"RESUMEN:")
    print(f"   Dashboards activos: {total_activos}/{len(dashboards)}")
    print(f"   CPU total: {total_cpu:.1f}%")
    print(f"   Memoria total: {total_memoria:.1f} MB")
    print()
    
    # Información del sistema
    print("INFORMACION DEL SISTEMA:")
    print(f"   CPU del sistema: {psutil.cpu_percent(interval=1):.1f}%")
    print(f"   Memoria disponible: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.1f} GB")
    print(f"   Memoria usada: {psutil.virtual_memory().percent:.1f}%")
    print()
    
    if total_activos == len(dashboards):
        print("Sistema METGO funcionando al 100%")
    elif total_activos > 0:
        print(f"Sistema METGO funcionando parcialmente ({total_activos}/{len(dashboards)})")
    else:
        print("Sistema METGO no esta ejecutandose")

if __name__ == "__main__":
    main()
