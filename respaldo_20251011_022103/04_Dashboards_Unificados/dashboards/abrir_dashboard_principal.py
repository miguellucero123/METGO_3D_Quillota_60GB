"""
Script para abrir automáticamente el Dashboard Principal después del login
"""

import webbrowser
import time
import sys

def abrir_dashboard_principal():
    """Abrir el Dashboard Principal en el navegador"""
    url = "http://localhost:8512"
    
    print("🚀 Abriendo Dashboard Principal...")
    print(f"📍 URL: {url}")
    
    # Abrir en el navegador por defecto
    webbrowser.open_new_tab(url)
    
    print("✅ Dashboard Principal abierto")
    print("📋 Otros dashboards disponibles:")
    print("   🌤️ Dashboard Meteorológico: http://localhost:8502")
    print("   🌱 Dashboard Agrícola: http://localhost:8501")
    print("   🏢 Dashboard Empresarial: http://localhost:8503")
    print("   🚁 Dashboard con Drones: http://localhost:8504")
    print("   💰 Sistema Económico: http://localhost:8506")

if __name__ == "__main__":
    abrir_dashboard_principal()
