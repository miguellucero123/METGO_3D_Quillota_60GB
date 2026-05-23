#!/usr/bin/env python3
"""
Sistema METGO - Detención Automática
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import subprocess
import time
import sys
from datetime import datetime
import psutil

def detener_procesos_streamlit():
    """Detiene todos los procesos de Streamlit"""
    print(" Deteniendo procesos de Streamlit...")
    
    try:
        # Detener procesos python3.11.exe
        result = subprocess.run(['taskkill', '/f', '/im', 'python3.11.exe'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK - Procesos Python detenidos")
        else:
            print("WARN -  Algunos procesos no se pudieron detener")
        
        time.sleep(2)
        
        # Verificar si quedan procesos
        procesos_activos = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python3.11.exe':
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'streamlit' in cmdline:
                        procesos_activos += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if procesos_activos == 0:
            print("OK - Todos los dashboards detenidos correctamente")
        else:
            print(f"WARN -  Quedan {procesos_activos} procesos activos")
            
    except Exception as e:
        print(f"❌ Error al detener procesos: {e}")

def verificar_puertos_libres():
    """Verifica que los puertos estén libres"""
    print("\n Verificando puertos...")
    
    puertos_streamlit = list(range(8501, 8516))  # Puertos 8501-8515
    puertos_ocupados = []
    
    for conn in psutil.net_connections():
        if conn.laddr.port in puertos_streamlit and conn.status == 'LISTEN':
            puertos_ocupados.append(conn.laddr.port)
    
    if puertos_ocupados:
        print(f"WARN -  Puertos aún ocupados: {puertos_ocupados}")
        return False
    else:
        print("OK - Todos los puertos están libres")
        return True

def main():
    """Función principal de detención"""
    print("=" * 60)
    print(" SISTEMA METGO - DETENCIÓN AUTOMÁTICA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    detener_procesos_streamlit()
    
    time.sleep(3)
    
    if verificar_puertos_libres():
        print("\n Sistema METGO detenido completamente")
    else:
        print("\nWARN -  Algunos procesos pueden seguir ejecutándose")
        print(" Si es necesario, reinicia el sistema")

if __name__ == "__main__":
    main()
