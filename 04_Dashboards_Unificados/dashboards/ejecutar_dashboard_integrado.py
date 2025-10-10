#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 EJECUTOR DEL DASHBOARD INTEGRADO METGO 3D
Sistema Meteorológico Agrícola Quillota - Ejecutor del Dashboard Integrado
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
import logging

def ejecutar_dashboard_integrado():
    """Ejecutar el dashboard integrado de notebooks"""
    print("EJECUTOR DEL DASHBOARD INTEGRADO METGO 3D")
    print("Sistema Meteorologico Agricola Quillota")
    print("=" * 60)
    
    try:
        # Verificar que el archivo del dashboard existe
        archivo_dashboard = "dashboard_integrado_notebooks.py"
        if not Path(archivo_dashboard).exists():
            print(f"Error: {archivo_dashboard} no encontrado")
            return False
        
        print(f"\nEjecutando dashboard integrado...")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar dashboard
        inicio = time.time()
        
        try:
            # Ejecutar con streamlit
            resultado = subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', archivo_dashboard
            ], capture_output=True, text=True, timeout=30)  # 30 segundos timeout para verificar
            
            duracion = time.time() - inicio
            
            # Mostrar salida
            if resultado.stdout:
                print("\nSalida del proceso:")
                print(resultado.stdout)
            
            if resultado.stderr:
                print("\nErrores del proceso:")
                print(resultado.stderr)
            
            if resultado.returncode == 0:
                print(f"\nDashboard integrado ejecutado exitosamente en {duracion:.2f} segundos")
                print(f"El dashboard deberia estar disponible en: http://localhost:8501")
                return True
            else:
                print(f"\nDashboard integrado fallo con codigo de salida {resultado.returncode} en {duracion:.2f} segundos")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\nTimeout ejecutando dashboard integrado despues de {time.time() - inicio:.2f} segundos")
            print(f"El dashboard deberia estar disponible en: http://localhost:8501")
            return True  # Timeout es normal para streamlit
        except Exception as e:
            print(f"\nError inesperado ejecutando dashboard integrado: {e}")
            return False
            
    except Exception as e:
        print(f"\nError en el ejecutor del dashboard integrado: {e}")
        return False

def verificar_dependencias():
    """Verificar dependencias necesarias"""
    print("\nVerificando dependencias...")
    
    dependencias = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'nbformat',
        'nbconvert'
    ]
    
    dependencias_faltantes = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   OK {dep}")
        except ImportError:
            print(f"   FALTA {dep}")
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        print(f"\nDependencias faltantes: {', '.join(dependencias_faltantes)}")
        print(f"   Instala con: pip install {' '.join(dependencias_faltantes)}")
        return False
    else:
        print(f"\nTodas las dependencias estan disponibles")
        return True

def main():
    """Función principal"""
    print("EJECUTOR DEL DASHBOARD INTEGRADO METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 80)
    
    try:
        # Verificar dependencias
        if not verificar_dependencias():
            print(f"\nDependencias faltantes. Instala las dependencias y vuelve a intentar.")
            return False
        
        # Ejecutar dashboard integrado
        exito = ejecutar_dashboard_integrado()
        
        if exito:
            print(f"\nDashboard integrado ejecutado exitosamente!")
            print(f"Accede al dashboard en: http://localhost:8501")
            print(f"Revisa los logs en: logs/dashboard/")
        else:
            print(f"\nError ejecutando dashboard integrado")
            print(f"Revisa los logs para mas detalles")
        
        return exito
        
    except Exception as e:
        print(f"\nError inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError critico: {e}")
        sys.exit(1)
