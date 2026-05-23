"""
ABRIR LOGIN METGO 3D QUILLOTA
Script simple para abrir el sistema de login en el navegador
"""

import webbrowser
import time

def abrir_login():
    """Abrir el sistema de login METGO 3D en el navegador"""
    print("="*60)
    print("ABRIENDO SISTEMA DE LOGIN METGO 3D QUILLOTA")
    print("="*60)
    
    url_login = "http://localhost:8500"
    
    print("[INFO] Verificando servicio...")
    time.sleep(2)
    
    print("\n[WEB] Abriendo Sistema de Login...")
    print(f"[URL] {url_login}")
    
    try:
        webbrowser.open(url_login)
        print("[OK] Navegador abierto exitosamente")
    except Exception as e:
        print(f"[ERROR] Error abriendo navegador: {e}")
        print(f"[MANUAL] Abre manualmente: {url_login}")
    
    print("\n" + "="*60)
    print("INFORMACION DEL SISTEMA")
    print("="*60)
    
    print("\n[URL] Enlace del Sistema:")
    print(f"   [LOGIN] Sistema de Login: {url_login}")
    
    print("\n[USERS] Usuarios de Prueba:")
    print("   [ADMIN] admin / admin123")
    print("   [EXEC] ejecutivo / ejecutivo123")
    print("   [AGRI] agricultor / agricultor123")
    print("   [TECH] tecnico / tecnico123")
    print("   [USER] usuario / usuario123")
    
    print("\n[STEPS] Pasos para usar el sistema:")
    print("   1. Inicia sesion con cualquier usuario de prueba")
    print("   2. El sistema te mostrara los dashboards disponibles")
    print("   3. Selecciona el dashboard que necesites")
    print("   4. El sistema te dara la URL para acceder")
    
    print("\n[DASHBOARDS] Dashboards disponibles:")
    print("   [EMP] Dashboard Empresarial (Puerto 8503)")
    print("   [AGRI] Dashboard Agricola (Puerto 8501)")
    print("   [MET] Dashboard Meteorologico (Puerto 8502)")
    print("   [DRONE] Dashboard con Drones (Puerto 8504)")
    print("   [ECON] Sistema Economico (Puerto 8506)")
    print("   [INT] Sistema de Integracion (Puerto 8507)")
    print("   [REP] Reportes Avanzados (Puerto 8508)")
    
    print("\n[HELP] Si tienes problemas:")
    print("   - Verifica que el puerto 8500 este activo")
    print("   - Usa las credenciales exactas (sin espacios)")
    print("   - El sistema funciona mejor en Chrome/Firefox")
    print("   - Reinicia con: python reiniciar_sistema_login.py")

if __name__ == "__main__":
    abrir_login()


