"""
VERIFICAR SISTEMA FUNCIONANDO - METGO 3D QUILLOTA
Script para verificar que el sistema esté funcionando correctamente
"""

import requests
import webbrowser
import time

def verificar_sistema():
    """Verificar que el sistema esté funcionando"""
    print("="*60)
    print("VERIFICANDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    url = "http://localhost:8500"
    
    print(f"[INFO] Verificando servicio en {url}...")
    
    try:
        # Intentar hacer una petición HTTP
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("[OK] Sistema funcionando correctamente")
            print(f"[STATUS] Código de respuesta: {response.status_code}")
            print(f"[URL] {url}")
            
            print("\n[WEB] Abriendo navegador...")
            try:
                webbrowser.open(url)
                print("[OK] Navegador abierto exitosamente")
            except Exception as e:
                print(f"[WARNING] No se pudo abrir navegador: {e}")
                print(f"[MANUAL] Abre manualmente: {url}")
            
            print("\n" + "="*60)
            print("INFORMACION DEL SISTEMA")
            print("="*60)
            
            print("\n[USERS] Usuarios de Prueba:")
            print("   [ADMIN] admin / admin123")
            print("   [EXEC] ejecutivo / ejecutivo123")
            print("   [AGRI] agricultor / agricultor123")
            print("   [TECH] tecnico / tecnico123")
            print("   [USER] usuario / usuario123")
            
            print("\n[STEPS] Pasos para usar:")
            print("   1. Ve a http://localhost:8500")
            print("   2. Inicia sesion con admin / admin123")
            print("   3. Selecciona el dashboard que necesites")
            print("   4. El sistema te dara la URL para acceder")
            
            print("\n[DASHBOARDS] Dashboards disponibles:")
            print("   [EMP] Dashboard Empresarial (Puerto 8503)")
            print("   [AGRI] Dashboard Agricola (Puerto 8501)")
            print("   [MET] Dashboard Meteorologico (Puerto 8502)")
            print("   [DRONE] Dashboard con Drones (Puerto 8504)")
            print("   [ECON] Sistema Economico (Puerto 8506)")
            
            return True
            
        else:
            print(f"[ERROR] Sistema respondió con código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al sistema")
        print("[INFO] Verifica que el puerto 8500 esté activo")
        return False
        
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout al conectar con el sistema")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_sistema()


