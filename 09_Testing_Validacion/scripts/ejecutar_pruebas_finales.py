#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 EJECUTOR DE PRUEBAS FINALES METGO 3D
Sistema Meteorológico Agrícola Quillota - Ejecutor de Pruebas Finales
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
import logging

def ejecutar_pruebas_finales():
    """Ejecutar todas las pruebas finales del sistema"""
    print("🚀 EJECUTOR DE PRUEBAS FINALES METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota")
    print("=" * 60)
    
    try:
        # Verificar que el archivo de pruebas existe
        archivo_pruebas = "pruebas_finales_metgo.py"
        if not Path(archivo_pruebas).exists():
            print(f"❌ Error: {archivo_pruebas} no encontrado")
            return False
        
        print(f"\n🧪 Ejecutando pruebas finales...")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar pruebas
        inicio = time.time()
        
        try:
            resultado = subprocess.run([
                sys.executable, archivo_pruebas
            ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
            
            duracion = time.time() - inicio
            
            # Mostrar salida
            if resultado.stdout:
                print("\n📋 Salida del proceso:")
                print(resultado.stdout)
            
            if resultado.stderr:
                print("\n⚠️ Errores del proceso:")
                print(resultado.stderr)
            
            # Mostrar resultado
            print(f"\n⏱️ Duración: {duracion:.2f} segundos")
            print(f"🔢 Código de salida: {resultado.returncode}")
            
            if resultado.returncode == 0:
                print("✅ Pruebas finales ejecutadas exitosamente")
                return True
            else:
                print("❌ Pruebas finales fallaron")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout: Las pruebas tardaron más de 5 minutos")
            return False
        except Exception as e:
            print(f"❌ Error ejecutando pruebas: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    try:
        exito = ejecutar_pruebas_finales()
        
        if exito:
            print("\n🎉 ¡Pruebas finales completadas exitosamente!")
            print("📋 Revisa el reporte generado en la carpeta 'reportes/'")
        else:
            print("\n💥 Pruebas finales fallaron")
            print("🔍 Revisa los logs para más detalles")
        
        return exito
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)
