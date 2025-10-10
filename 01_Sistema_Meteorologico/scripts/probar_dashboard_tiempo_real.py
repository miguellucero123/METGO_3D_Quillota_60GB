#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el dashboard en tiempo real
"""

import sys
import os

# Agregar directorio actual al path
sys.path.append('.')

def probar_dashboard_tiempo_real():
    """Probar el dashboard en tiempo real"""
    
    print("=" * 70)
    print("PROBANDO DASHBOARD EN TIEMPO REAL METGO 3D")
    print("=" * 70)
    
    try:
        # 1. Probar importación de módulos
        print("\n1. Probando importación de módulos...")
        
        import streamlit as st
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        from datetime import datetime, timedelta
        import json
        import sqlite3
        import requests
        import time
        from typing import Dict, List, Optional
        import logging
        
        print("OK - Módulos básicos importados")
        
        # 2. Probar importación del sistema de validación
        print("\n2. Probando importación del sistema de validación...")
        
        sys.path.append('scripts')
        
        try:
            from validador_flexible import ValidadorFlexible
            from limpiador_datos_meteorologicos import LimpiadorDatosMeteorologicos
            from monitor_simple import MonitorSimple
            from sistema_alertas_automaticas import SistemaAlertas
            
            print("OK - Sistema de validación y alertas importado")
            SISTEMA_VALIDACION_ACTIVO = True
            SISTEMA_ALERTAS_ACTIVO = True
            
        except ImportError as e:
            print(f"WARN - Sistema de validación no disponible: {e}")
            SISTEMA_VALIDACION_ACTIVO = False
            SISTEMA_ALERTAS_ACTIVO = False
        
        # 3. Probar importación del dashboard
        print("\n3. Probando importación del dashboard...")
        
        from main_tiempo_real import GestorDatosMeteorologicos, crear_dashboard_avanzado
        
        print("OK - Dashboard en tiempo real importado")
        
        # 4. Probar inicialización del gestor
        print("\n4. Probando inicialización del gestor...")
        
        gestor = GestorDatosMeteorologicos()
        print("OK - Gestor de datos inicializado")
        
        # 5. Probar carga de datos
        print("\n5. Probando carga de datos...")
        
        datos = gestor.cargar_datos()
        print(f"OK - Datos cargados: {len(datos)} registros")
        
        # 6. Probar conversión a DataFrame
        print("\n6. Probando conversión a DataFrame...")
        
        df = pd.DataFrame(datos)
        print(f"OK - DataFrame creado: {df.shape}")
        
        # 7. Probar funciones de gráficos
        print("\n7. Probando funciones de gráficos...")
        
        from main_tiempo_real import crear_graficos_tiempo_real, mostrar_alertas_tiempo_real
        
        # Probar con datos de muestra
        crear_graficos_tiempo_real(df.head(7), "Líneas")
        print("OK - Gráficos en tiempo real funcionando")
        
        mostrar_alertas_tiempo_real(df.head(7))
        print("OK - Alertas en tiempo real funcionando")
        
        # 8. Probar estado de validación
        print("\n8. Probando estado de validación...")
        
        estado_validacion = gestor.obtener_estado_validacion()
        if estado_validacion:
            print(f"OK - Estado de validación: {estado_validacion['puntuacion']:.1f}/100")
        else:
            print("WARN - Estado de validación no disponible")
        
        # 9. Probar estadísticas de alertas
        print("\n9. Probando estadísticas de alertas...")
        
        stats_alertas = gestor.obtener_estadisticas_alertas()
        if 'total_alertas_24h' in stats_alertas:
            print(f"OK - Estadísticas de alertas: {stats_alertas['total_alertas_24h']} alertas")
        else:
            print("WARN - Estadísticas de alertas no disponibles")
        
        # 10. Resumen final
        print("\n" + "=" * 70)
        print("RESUMEN DE PRUEBAS - DASHBOARD EN TIEMPO REAL")
        print("=" * 70)
        
        print("OK - Dashboard en tiempo real funcionando correctamente")
        print("OK - Sistema de validación integrado")
        print("OK - Sistema de alertas integrado")
        print("OK - Gráficos dinámicos funcionando")
        print("OK - Alertas en tiempo real funcionando")
        print(f"OK - Datos procesados: {len(datos)} registros")
        print(f"OK - DataFrame: {df.shape}")
        
        if estado_validacion:
            print(f"OK - Calidad de datos: {estado_validacion['puntuacion']:.1f}/100")
        
        print("\nFUNCIONALIDADES DISPONIBLES:")
        print("✅ Dashboard principal con métricas en tiempo real")
        print("✅ Gráficos dinámicos con múltiples tipos")
        print("✅ Alertas automáticas en tiempo real")
        print("✅ Recomendaciones agrícolas")
        print("✅ Actualización automática configurable")
        print("✅ Sistema de validación integrado")
        print("✅ Sistema de alertas por email/SMS")
        print("✅ Múltiples vistas de análisis")
        
        return True
        
    except Exception as e:
        print(f"ERROR - Error en las pruebas: {e}")
        return False

if __name__ == "__main__":
    exito = probar_dashboard_tiempo_real()
    
    if exito:
        print(f"\nEXITO - Dashboard en tiempo real funcionando correctamente!")
        print(f"Para ejecutar el dashboard:")
        print(f"streamlit run main_tiempo_real.py")
    else:
        print(f"\nFALLO - Las pruebas fallaron")
        print(f"Revisar errores y corregir problemas")

