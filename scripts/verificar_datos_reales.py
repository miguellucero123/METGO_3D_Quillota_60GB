#!/usr/bin/env python3
"""
Sistema METGO - Verificación de Datos Reales
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("VERIFICACION DE DATOS REALES OPENMETEO")
    print("=" * 60)
    print()
    
    try:
        from datos_reales_openmeteo import OpenMeteoData, verificar_datos_reales
        
        print("1. Verificando conectividad con OpenMeteo...")
        openmeteo = OpenMeteoData()
        
        if openmeteo.verificar_conexion():
            print("   OK - Conexion exitosa con OpenMeteo")
        else:
            print("   ERROR - Sin conexion a OpenMeteo")
            return False
        
        print()
        print("2. Probando obtencion de datos para diferentes estaciones...")
        
        estaciones = ['Quillota', 'Santiago', 'Valparaiso', 'Vina del Mar']
        
        for estacion in estaciones:
            print(f"   Probando {estacion}...")
            
            datos = openmeteo.obtener_datos_historicos(estacion, 7)
            
            if datos is not None:
                print(f"   OK - {len(datos)} registros obtenidos")
                print(f"       Temperatura: {datos['temperatura_max'].min():.1f}°C - {datos['temperatura_max'].max():.1f}°C")
                print(f"       Precipitacion: {datos['precipitacion'].sum():.1f}mm")
            else:
                print(f"   ERROR - No se pudieron obtener datos para {estacion}")
        
        print()
        print("3. Probando pronosticos...")
        
        pronostico = openmeteo.obtener_datos_pronostico('Quillota', 7)
        
        if pronostico is not None:
            print(f"   OK - Pronostico obtenido: {len(pronostico)} dias")
            print(f"       Temperatura futura: {pronostico['temperatura_max'].min():.1f}°C - {pronostico['temperatura_max'].max():.1f}°C")
        else:
            print("   ERROR - No se pudo obtener pronostico")
        
        print()
        print("4. Verificacion completa del sistema...")
        
        if verificar_datos_reales():
            print("   OK - Sistema de datos reales funcionando correctamente")
            print()
            print("=" * 60)
            print("RESULTADO: DATOS REALES DISPONIBLES")
            print("=" * 60)
            print()
            print("El sistema METGO puede usar datos reales de OpenMeteo.")
            print("Los dashboards mostraran informacion meteorologica actual.")
            print()
            print("Para usar datos reales en el dashboard principal:")
            print("1. Ejecuta: python sistema_auth_dashboard_principal_metgo.py")
            print("2. Selecciona una estacion meteorologica")
            print("3. Los datos reales se cargaran automaticamente")
            return True
        else:
            print("   ERROR - Sistema de datos reales no funcionando")
            return False
            
    except ImportError as e:
        print(f"ERROR - No se puede importar el modulo de datos reales: {e}")
        return False
    except Exception as e:
        print(f"ERROR - Error inesperado: {e}")
        return False

if __name__ == "__main__":
    main()
