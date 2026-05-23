"""
SCRIPT DE PRUEBA - INTEGRACIÓN DE APIs METEOROLÓGICAS REALES
METGO 3D Quillota - Sistema de Pruebas
"""

import sys
import os
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def probar_conector_apis():
    """Probar el conector de APIs meteorológicas"""
    print("=" * 60)
    print("PROBANDO CONECTOR DE APIs METEOROLÓGICAS REALES")
    print("METGO 3D Quillota - Sistema de Pruebas")
    print("=" * 60)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el conector
        from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
        
        print("[OK] Conector importado correctamente")
        
        # Crear instancia
        conector = ConectorAPIsMeteorologicas()
        print("[OK] Instancia del conector creada")
        
        # Coordenadas de prueba (Quillota Centro)
        lat = -32.8833
        lon = -71.2667
        
        print(f"[PRUEBA] Obteniendo datos de OpenMeteo para Quillota Centro")
        print(f"[COORDENADAS] Lat: {lat}, Lon: {lon}")
        print()
        
        # Probar OpenMeteo
        datos = conector.obtener_datos_openmeteo_coordenadas(lat, lon)
        
        if datos:
            print("[OK] Datos obtenidos de OpenMeteo:")
            print(f"  - Temperatura: {datos.get('temperatura_actual', 'N/A')}°C")
            print(f"  - Humedad: {datos.get('humedad_relativa', 'N/A')}%")
            print(f"  - Precipitación: {datos.get('precipitacion', 'N/A')} mm/h")
            print(f"  - Viento: {datos.get('velocidad_viento', 'N/A')} km/h")
            print(f"  - Presión: {datos.get('presion_atmosferica', 'N/A')} hPa")
            print(f"  - Nubosidad: {datos.get('nubosidad', 'N/A')}%")
            print()
            
            # Probar pronóstico
            if 'pronostico_24h' in datos and datos['pronostico_24h']:
                pronostico = datos['pronostico_24h']
                print("[OK] Pronóstico 24h disponible:")
                print(f"  - Temp Mín/Máx: {pronostico.get('temp_min', 'N/A')}°C / {pronostico.get('temp_max', 'N/A')}°C")
                print(f"  - Precipitación Total: {pronostico.get('precipitacion_total', 'N/A')} mm")
                print(f"  - Probabilidad Lluvia: {pronostico.get('probabilidad_lluvia', 'N/A')}%")
                print()
            
            # Probar alertas
            if 'alertas' in datos and datos['alertas']:
                print(f"[OK] {len(datos['alertas'])} alertas meteorológicas encontradas")
                for alerta in datos['alertas']:
                    print(f"  - {alerta['nivel'].upper()}: {alerta['tipo']} - {alerta['descripcion']}")
                print()
            
            return True
            
        else:
            print("[ERROR] No se pudieron obtener datos de OpenMeteo")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error probando conector: {str(e)}")
        return False

def probar_multiple_estaciones():
    """Probar obtención de datos de múltiples estaciones"""
    print("=" * 60)
    print("PROBANDO MÚLTIPLES ESTACIONES METEOROLÓGICAS")
    print("=" * 60)
    
    try:
        from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
        
        conector = ConectorAPIsMeteorologicas()
        
        # Coordenadas de las 6 estaciones del Valle de Quillota
        estaciones = {
            "Quillota_Centro": {"lat": -32.8833, "lon": -71.2667},
            "La_Cruz": {"lat": -32.8167, "lon": -71.2167},
            "Nogales": {"lat": -32.7500, "lon": -71.2167},
            "San_Isidro": {"lat": -32.9167, "lon": -71.2333},
            "Pocochay": {"lat": -32.8500, "lon": -71.3000},
            "Valle_Hermoso": {"lat": -32.9333, "lon": -71.2833}
        }
        
        datos_estaciones = {}
        exitos = 0
        
        for nombre, coordenadas in estaciones.items():
            print(f"[PROBANDO] {nombre}...")
            
            try:
                datos = conector.obtener_datos_openmeteo_coordenadas(coordenadas["lat"], coordenadas["lon"])
                
                if datos:
                    datos_estaciones[nombre] = datos
                    exitos += 1
                    print(f"  [OK] Datos obtenidos - Temp: {datos.get('temperatura_actual', 'N/A')}°C")
                else:
                    print(f"  [ERROR] No se obtuvieron datos")
                    
            except Exception as e:
                print(f"  [ERROR] {str(e)}")
            
            print()
        
        print("=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        print(f"[ESTACIONES PROBADAS] {len(estaciones)}")
        print(f"[EXITOS] {exitos}")
        print(f"[FALLOS] {len(estaciones) - exitos}")
        print(f"[TASA EXITO] {(exitos/len(estaciones)*100):.1f}%")
        
        if datos_estaciones:
            print("\n[DATOS OBTENIDOS]")
            for nombre, datos in datos_estaciones.items():
                temp = datos.get('temperatura_actual', 'N/A')
                humedad = datos.get('humedad_relativa', 'N/A')
                print(f"  - {nombre}: {temp}°C, {humedad}% HR")
        
        return exitos > 0
        
    except Exception as e:
        print(f"[ERROR] Error en prueba de múltiples estaciones: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("INICIANDO PRUEBAS DE INTEGRACIÓN DE APIs METEOROLÓGICAS")
    print()
    
    # Prueba 1: Conector básico
    resultado1 = probar_conector_apis()
    print()
    
    # Prueba 2: Múltiples estaciones
    resultado2 = probar_multiple_estaciones()
    print()
    
    # Resumen final
    print("=" * 60)
    print("RESUMEN FINAL DE PRUEBAS")
    print("=" * 60)
    
    if resultado1 and resultado2:
        print("[RESULTADO] TODAS LAS PRUEBAS EXITOSAS")
        print("[ESTADO] Sistema listo para integración con dashboard")
        print("[RECOMENDACION] Proceder con implementación en dashboard agrícola")
    elif resultado1:
        print("[RESULTADO] PRUEBA BÁSICA EXITOSA")
        print("[ESTADO] Conector funcional, problemas con múltiples estaciones")
        print("[RECOMENDACION] Revisar configuración de APIs")
    else:
        print("[RESULTADO] PRUEBAS FALLIDAS")
        print("[ESTADO] Problemas con conector de APIs")
        print("[RECOMENDACION] Verificar configuración y conectividad")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
