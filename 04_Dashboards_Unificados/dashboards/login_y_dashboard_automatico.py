"""
Sistema de Login Automático con Apertura del Dashboard Principal
"""

import subprocess
import sys
import time
import webbrowser
import requests

def verificar_dashboard_activo(puerto):
    """Verificar si un dashboard está activo en un puerto"""
    try:
        response = requests.get(f"http://localhost:{puerto}/_stcore/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def iniciar_dashboard_si_no_activo(script, puerto):
    """Iniciar un dashboard si no está activo"""
    if not verificar_dashboard_activo(puerto):
        print(f"Iniciando dashboard en puerto {puerto}...")
        try:
            command = [
                sys.executable, "-m", "streamlit", "run", 
                script, 
                "--server.port", str(puerto), 
                "--server.headless", "true"
            ]
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"ERROR iniciando dashboard en puerto {puerto}: {e}")
            return False
    else:
        print(f"OK: Dashboard ya activo en puerto {puerto}")
        return True

def main():
    """Función principal"""
    print("SISTEMA DE LOGIN Y DASHBOARD AUTOMATICO METGO 3D")
    print("=" * 60)
    
    # Verificar e iniciar dashboards necesarios
    dashboards = [
        ("sistema_autenticacion_metgo.py", 8500, "Sistema de Autenticacion"),
        ("dashboard_principal_integrado_metgo.py", 8512, "Dashboard Principal"),
        ("dashboard_meteorologico_final.py", 8502, "Dashboard Meteorologico"),
    ]
    
    print("Verificando estado de dashboards...")
    for script, puerto, nombre in dashboards:
        if iniciar_dashboard_si_no_activo(script, puerto):
            print(f"   OK: {nombre} - Puerto {puerto}")
        else:
            print(f"   ERROR: {nombre} - Puerto {puerto}")
    
    print("\n" + "=" * 60)
    print("ACCESO A DASHBOARDS")
    print("=" * 60)
    print("Sistema de Autenticacion: http://localhost:8500")
    print("Dashboard Principal: http://localhost:8512")
    print("Dashboard Meteorologico: http://localhost:8502")
    print("Dashboard Agricola: http://localhost:8501")
    print("Dashboard Empresarial: http://localhost:8503")
    
    print("\nAbriendo Sistema de Autenticacion...")
    webbrowser.open_new_tab("http://localhost:8500")
    
    print("\nINSTRUCCIONES:")
    print("1. Completa el login en el navegador")
    print("2. Despues del login exitoso, usa los enlaces directos")
    print("3. O ejecuta: python abrir_dashboard_principal.py")
    
    print("\nSistema listo para usar!")

if __name__ == "__main__":
    main()
