"""
DIAGNÓSTICO DASHBOARD AGRÍCOLA AVANZADO
Script para diagnosticar problemas con la descarga de datos reales
"""

import sys
import traceback
import requests
from datetime import datetime

def diagnosticar_conector_apis():
    """Diagnosticar el conector de APIs meteorológicas"""
    
    print("DIAGNOSTICO DASHBOARD AGRICOLA AVANZADO")
    print("=" * 50)
    
    try:
        # 1. Verificar importación del conector
        print("\n1. Verificando importacion del conector...")
        try:
            from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
            print("   OK: Conector importado correctamente")
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
        
        # 2. Crear instancia del conector
        print("\n2. Creando instancia del conector...")
        try:
            conector = ConectorAPIsMeteorologicas()
            print("   OK: Instancia creada correctamente")
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        # 3. Verificar configuración de APIs
        print("\n3. Verificando configuracion de APIs...")
        try:
            api_keys = conector.api_keys
            openmeteo_config = api_keys.get('openmeteo', {})
            print(f"   OpenMeteo activa: {openmeteo_config.get('activa', False)}")
            print(f"   Base URL: {openmeteo_config.get('base_url', 'N/A')}")
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
        
        # 4. Probar conexión directa a OpenMeteo
        print("\n4. Probando conexion directa a OpenMeteo...")
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": -32.8833,
                "longitude": -71.2667,
                "current": "temperature_2m",
                "timezone": "America/Santiago"
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("   OK: Conexion exitosa a OpenMeteo")
                print(f"   Datos recibidos: {len(str(data))} caracteres")
            else:
                print(f"   ERROR: Status code {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        # 5. Probar método específico del conector
        print("\n5. Probando metodo obtener_datos_openmeteo_coordenadas...")
        try:
            datos = conector.obtener_datos_openmeteo_coordenadas(-32.8833, -71.2667, 7)
            
            if datos:
                print("   OK: Metodo ejecutado correctamente")
                print(f"   Datos obtenidos: {len(datos)} claves")
                for clave in datos.keys():
                    print(f"     - {clave}")
            else:
                print("   WARNING: Metodo devolvio None")
                
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        # 6. Verificar estaciones configuradas
        print("\n6. Verificando estaciones configuradas...")
        try:
            estaciones = conector.estaciones_quillota
            print(f"   Estaciones configuradas: {len(estaciones)}")
            for nombre, info in estaciones.items():
                print(f"     - {info['nombre']}: ({info['lat']}, {info['lon']})")
        except Exception as e:
            print(f"   ERROR: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("DIAGNOSTICO COMPLETADO")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\nERROR GENERAL: {e}")
        traceback.print_exc()
        return False

def diagnosticar_dashboard_agricola():
    """Diagnosticar el dashboard agrícola específicamente"""
    
    print("\nDIAGNOSTICO DASHBOARD AGRICOLA")
    print("=" * 40)
    
    try:
        # 1. Verificar importación del dashboard
        print("\n1. Verificando importacion del dashboard...")
        try:
            from dashboard_agricola_avanzado import DashboardAgricolaAvanzado
            print("   OK: Dashboard importado correctamente")
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        # 2. Crear instancia del dashboard
        print("\n2. Creando instancia del dashboard...")
        try:
            dashboard = DashboardAgricolaAvanzado()
            print("   OK: Instancia creada correctamente")
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        # 3. Probar método de obtención de datos
        print("\n3. Probando metodo _obtener_datos_reales_apis...")
        try:
            # Simular session state
            import streamlit as st
            if not hasattr(st, 'session_state'):
                class MockSessionState:
                    def __init__(self):
                        self.data = {}
                    def __getattr__(self, key):
                        return self.data.get(key)
                    def __setattr__(self, key, value):
                        if key == 'data':
                            super().__setattr__(key, value)
                        else:
                            self.data[key] = value
                st.session_state = MockSessionState()
            
            datos = dashboard._obtener_datos_reales_apis()
            
            if datos:
                print("   OK: Metodo ejecutado correctamente")
                print(f"   Estaciones con datos: {len(datos)}")
                for estacion in datos.keys():
                    print(f"     - {estacion}")
            else:
                print("   WARNING: Metodo devolvio None")
                
        except Exception as e:
            print(f"   ERROR: {e}")
            traceback.print_exc()
            return False
        
        print("\nDIAGNOSTICO DASHBOARD COMPLETADO")
        return True
        
    except Exception as e:
        print(f"\nERROR GENERAL: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar diagnóstico completo"""
    
    print("INICIANDO DIAGNOSTICO COMPLETO")
    print("=" * 60)
    
    # Diagnóstico del conector
    conector_ok = diagnosticar_conector_apis()
    
    # Diagnóstico del dashboard
    dashboard_ok = diagnosticar_dashboard_agricola()
    
    print("\n" + "=" * 60)
    print("RESUMEN DEL DIAGNOSTICO")
    print("=" * 60)
    
    print(f"Conector APIs: {'OK' if conector_ok else 'ERROR'}")
    print(f"Dashboard Agricola: {'OK' if dashboard_ok else 'ERROR'}")
    
    if conector_ok and dashboard_ok:
        print("\nSISTEMA FUNCIONANDO CORRECTAMENTE")
    else:
        print("\nSE DETECTARON PROBLEMAS - REVISAR LOGS ARRIBA")

if __name__ == "__main__":
    main()


