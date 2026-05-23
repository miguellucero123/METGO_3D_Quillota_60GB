#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la integración del sistema de validación en main.py
"""

import sys
import os

# Agregar directorio de scripts al path
sys.path.append('scripts')
# Agregar directorio padre al path para importar main.py
sys.path.append('..')

def probar_integracion_main():
    """Probar la integración del sistema de validación en main.py"""
    
    print("=" * 70)
    print("PROBANDO INTEGRACION DEL SISTEMA DE VALIDACION EN MAIN.PY")
    print("=" * 70)
    
    try:
        # 1. Probar importación de módulos de validación
        print("\n1. Probando importación de módulos de validación...")
        
        from validador_flexible import ValidadorFlexible
        from limpiador_datos_meteorologicos import LimpiadorDatosMeteorologicos
        from monitor_simple import MonitorSimple
        
        print("OK - Módulos de validación importados correctamente")
        
        # 2. Inicializar sistemas
        print("\n2. Inicializando sistemas de validación...")
        
        validador = ValidadorFlexible()
        limpiador = LimpiadorDatosMeteorologicos()
        monitor = MonitorSimple()
        
        print("OK - Sistemas de validación inicializados")
        
        # 3. Probar importación de main.py
        print("\n3. Probando importación de main.py...")
        
        # Importar la clase GestorDatosMeteorologicos directamente
        import main
        from main import GestorDatosMeteorologicos
        
        print("OK - main.py importado correctamente")
        
        # 4. Probar inicialización del gestor
        print("\n4. Probando inicialización del gestor de datos...")
        
        gestor = GestorDatosMeteorologicos()
        print("OK - Gestor de datos inicializado")
        
        # 5. Probar carga de datos con validación
        print("\n5. Probando carga de datos con validación...")
        
        datos = gestor.cargar_datos()
        print(f"OK - Datos cargados: {len(datos)} registros")
        
        # 6. Probar estado de validación
        print("\n6. Probando estado de validación...")
        
        estado_validacion = gestor.obtener_estado_validacion()
        if estado_validacion:
            print(f"OK - Estado de validación disponible: {estado_validacion['puntuacion']:.1f}/100")
        else:
            print("WARN - Estado de validación no disponible")
        
        # 7. Probar monitoreo de calidad
        print("\n7. Probando monitoreo de calidad...")
        
        monitoreo = gestor.ejecutar_monitoreo_calidad()
        print(f"OK - Monitoreo ejecutado: {monitoreo['calidad']:.1f}% calidad")
        
        # 8. Resumen final
        print("\n" + "=" * 70)
        print("RESUMEN DE INTEGRACION")
        print("=" * 70)
        
        print("OK - Sistema de validación integrado correctamente")
        print("OK - Gestor de datos con validación funcionando")
        print("OK - Monitoreo de calidad operativo")
        print(f"OK - Datos procesados: {len(datos)} registros")
        
        if estado_validacion:
            print(f"OK - Calidad de datos: {estado_validacion['puntuacion']:.1f}/100")
        
        print(f"OK - Calidad general: {monitoreo['calidad']:.1f}%")
        
        return True
        
    except ImportError as e:
        print(f"ERROR - Error de importación: {e}")
        return False
    except Exception as e:
        print(f"ERROR - Error general: {e}")
        return False

if __name__ == "__main__":
    exito = probar_integracion_main()
    
    if exito:
        print(f"\nEXITO - Integración completada exitosamente!")
        print(f"El sistema main.py está listo para usar con validación")
    else:
        print(f"\nFALLO - La integración falló")
        print(f"Revisar errores y corregir problemas")
