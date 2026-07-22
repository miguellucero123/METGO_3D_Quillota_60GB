"""
Sistema para iniciar automáticamente el Dashboard Principal después del login
"""

import subprocess
import sys
import time
import webbrowser

def iniciar_dashboard_principal():
    """Iniciar el Dashboard Principal automáticamente"""
    
    print("🚀 INICIANDO DASHBOARD PRINCIPAL METGO 3D")
    print("=" * 50)
    
    # Verificar si el Dashboard Principal ya está ejecutándose
    try:
        import requests
        response = requests.get("http://localhost:8512/_stcore/health", timeout=2)
        if response.status_code == 200:
            print("✅ Dashboard Principal ya está ejecutándose")
            print("🌐 Abriendo en el navegador...")
            webbrowser.open_new_tab("http://localhost:8512")
            return True
    except:
        pass
    
    # Iniciar el Dashboard Principal
    print("🔄 Iniciando Dashboard Principal...")
    
    try:
        command = [
            sys.executable, "-m", "streamlit", "run", 
            "dashboard_principal_integrado_metgo.py", 
            "--server.port", "8512", 
            "--server.headless", "true"
        ]
        
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Esperar un poco para que se inicie
        time.sleep(3)
        
        print("✅ Dashboard Principal iniciado")
        print("🌐 Abriendo en el navegador...")
        
        # Abrir en el navegador
        webbrowser.open_new_tab("http://localhost:8512")
        
        print("🎉 Dashboard Principal disponible en: http://localhost:8512")
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando Dashboard Principal: {e}")
        return False

if __name__ == "__main__":
    iniciar_dashboard_principal()
