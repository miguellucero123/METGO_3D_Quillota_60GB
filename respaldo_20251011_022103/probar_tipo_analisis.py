#!/usr/bin/env python3
"""
Sistema METGO - Prueba de Tipos de Análisis
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def probar_tipos_analisis():
    """Prueba los diferentes tipos de análisis"""
    print("=" * 60)
    print("PRUEBA DE TIPOS DE ANALISIS - SISTEMA METGO")
    print("=" * 60)
    print()
    
    try:
        from datos_reales_openmeteo import obtener_datos_meteorologicos_reales
        
        estacion = "Quillota"
        
        print(f"Probando tipos de analisis para {estacion}...")
        print()
        
        # 1. Probar análisis histórico
        print("1. Probando analisis HISTORICO...")
        datos_historicos = obtener_datos_meteorologicos_reales(estacion, 'historicos', 7)
        
        if datos_historicos is not None:
            print(f"   OK - Datos historicos: {len(datos_historicos)} registros")
            print(f"       Columnas: {list(datos_historicos.columns)}")
            print(f"       Temperatura promedio: {datos_historicos['temperatura_promedio'].mean():.1f}°C")
        else:
            print("   ERROR - No se obtuvieron datos historicos")
        
        print()
        
        # 2. Probar análisis de pronóstico
        print("2. Probando analisis PRONOSTICO...")
        datos_pronostico = obtener_datos_meteorologicos_reales(estacion, 'pronostico', 7)
        
        if datos_pronostico is not None:
            print(f"   OK - Datos pronostico: {len(datos_pronostico)} registros")
            print(f"       Columnas: {list(datos_pronostico.columns)}")
            print(f"       Temperatura promedio: {datos_pronostico['temperatura_promedio'].mean():.1f}°C")
        else:
            print("   ERROR - No se obtuvieron datos de pronostico")
        
        print()
        
        # 3. Probar normalización de columnas
        print("3. Probando normalizacion de columnas...")
        
        if datos_historicos is not None:
            # Simular la normalización que hace el dashboard
            datos_normalizados = datos_historicos.rename(columns={
                'temperatura_max': 'temp_max',
                'temperatura_min': 'temp_min', 
                'temperatura_promedio': 'temp_promedio',
                'velocidad_viento': 'viento_velocidad'
            })
            
            print(f"   OK - Columnas normalizadas: {list(datos_normalizados.columns)}")
            print(f"       temp_promedio disponible: {'temp_promedio' in datos_normalizados.columns}")
            print(f"       temp_max disponible: {'temp_max' in datos_normalizados.columns}")
            print(f"       viento_velocidad disponible: {'viento_velocidad' in datos_normalizados.columns}")
        
        print()
        print("=" * 60)
        print("RESULTADO: PRUEBAS COMPLETADAS")
        print("=" * 60)
        
        if datos_historicos is not None and datos_pronostico is not None:
            print("OK - Todos los tipos de analisis funcionan correctamente")
            print("El error KeyError deberia estar corregido")
            return True
        else:
            print("ERROR - Algunos tipos de analisis no funcionan")
            return False
            
    except ImportError as e:
        print(f"ERROR - No se puede importar el modulo: {e}")
        return False
    except Exception as e:
        print(f"ERROR - Error inesperado: {e}")
        return False

if __name__ == "__main__":
    probar_tipos_analisis()
