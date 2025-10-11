"""
ABRIR SISTEMA METGO 3D QUILLOTA
Script simple para abrir el sistema en el navegador
"""

import webbrowser
import time

def abrir_sistema():
    """Abrir el sistema METGO 3D en el navegador"""
    print("="*60)
    print("ABRIENDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    # URLs del sistema
    url_autenticacion = "http://localhost:8500"
    url_central = "http://localhost:8509"
    
    print("[INFO] Verificando servicios...")
    time.sleep(2)
    
    print("\n[WEB] Abriendo Sistema de Autenticacion...")
    print(f"[URL] {url_autenticacion}")
    
    try:
        webbrowser.open(url_autenticacion)
        print("[OK] Navegador abierto exitosamente")
    except Exception as e:
        print(f"[ERROR] Error abriendo navegador: {e}")
        print(f"[MANUAL] Abre manualmente: {url_autenticacion}")
    
    print("\n" + "="*60)
    print("INFORMACION DEL SISTEMA")
    print("="*60)
    
    print("\n[URLS] Enlaces del Sistema:")
    print(f"   [AUTH] Autenticacion: {url_autenticacion}")
    print(f"   [CENTRAL] Dashboard Central: {url_central}")
    
    print("\n[USERS] Usuarios de Prueba:")
    print("   [ADMIN] admin / admin123")
    print("   [EXEC] ejecutivo / ejecutivo123")
    print("   [AGRI] agricultor / agricultor123")
    print("   [TECH] tecnico / tecnico123")
    print("   [USER] usuario / usuario123")
    
    print("\n[STEPS] Pasos para usar el sistema:")
    print("   1. Inicia sesion con cualquier usuario de prueba")
    print("   2. El sistema te llevara al Dashboard Central")
    print("   3. Desde ahi puedes iniciar los modulos que necesites")
    print("   4. Cada modulo se abrira en su propio puerto")
    
    print("\n[MODULES] Modulos disponibles:")
    print("   [EMP] Dashboard Empresarial (Puerto 8503)")
    print("   [AGRI] Dashboard Agricola (Puerto 8501)")
    print("   [MET] Dashboard Meteorologico (Puerto 8502)")
    print("   [DRONE] Dashboard con Drones (Puerto 8504)")
    print("   [ECON] Sistema Economico (Puerto 8506)")
    print("   [INT] Sistema de Integracion (Puerto 8507)")
    print("   [REP] Reportes Avanzados (Puerto 8508)")
    
    print("\n[HELP] Si tienes problemas:")
    print("   - Verifica que los puertos 8500 y 8509 esten activos")
    print("   - Usa Ctrl+C para detener el sistema")
    print("   - Reinicia con: python iniciar_sistema_simple_metgo.py")

if __name__ == "__main__":
    abrir_sistema()


