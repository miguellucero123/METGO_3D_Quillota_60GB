#!/usr/bin/env python3
"""
Script para ejecutar el dashboard principal con configuración de acceso externo
"""

import subprocess
import sys
import os
import time

def configurar_firewall():
    """Configura el firewall de Windows para permitir acceso externo"""
    try:
        print("🔧 Configurando firewall para acceso externo...")
        
        # Comandos para abrir puertos en el firewall de Windows
        comandos_firewall = [
            'netsh advfirewall firewall add rule name="Streamlit Dashboard 8501" dir=in action=allow protocol=TCP localport=8501',
            'netsh advfirewall firewall add rule name="Streamlit Dashboard 8502" dir=in action=allow protocol=TCP localport=8502',
            'netsh advfirewall firewall add rule name="Streamlit Dashboard 8503" dir=in action=allow protocol=TCP localport=8503',
            'netsh advfirewall firewall add rule name="Streamlit Dashboard 8504" dir=in action=allow protocol=TCP localport=8504',
            'netsh advfirewall firewall add rule name="Streamlit Dashboard 8505" dir=in action=allow protocol=TCP localport=8505'
        ]
        
        for comando in comandos_firewall:
            try:
                subprocess.run(comando, shell=True, check=True, capture_output=True)
                print(f"✅ Puerto configurado: {comando.split('localport=')[1]}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Puerto ya configurado o error: {comando.split('localport=')[1]}")
                
        print("✅ Configuración de firewall completada")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando firewall: {e}")
        return False

def obtener_ip_externa():
    """Obtiene la IP externa del sistema"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "No disponible"

def ejecutar_dashboard():
    """Ejecuta el dashboard principal con configuración externa"""
    
    print("🚀 Iniciando Dashboard Principal METGO con Acceso Externo")
    print("=" * 60)
    
    # Configurar firewall
    configurar_firewall()
    
    # Obtener IPs
    ip_local = "192.168.1.7"  # IP que obtuvimos anteriormente
    ip_externa = obtener_ip_externa()
    
    print(f"📍 IP Local: {ip_local}")
    print(f"📍 IP Externa: {ip_externa}")
    print()
    
    # URLs disponibles
    print("🌐 URLs Disponibles:")
    print(f"   🏠 Local:        http://localhost:8501")
    print(f"   🏢 Red Local:    http://{ip_local}:8501")
    print(f"   🌍 Externa:      http://{ip_externa}:8501")
    print()
    
    print("⚠️  IMPORTANTE:")
    print("   - Para acceso externo, asegúrate de que el router tenga")
    print("     el puerto 8501 abierto (Port Forwarding)")
    print("   - Si no tienes IP fija, usa servicios como ngrok")
    print()
    
    # Configuración de Streamlit para acceso externo
    config_streamlit = [
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false",
        "--browser.gatherUsageStats=false"
    ]
    
    print("🚀 Ejecutando dashboard...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        # Ejecutar Streamlit
        comando = [
            sys.executable, "-m", "streamlit", "run", 
            "sistema_auth_dashboard_principal_metgo.py"
        ] + config_streamlit
        
        subprocess.run(comando)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando dashboard: {e}")

if __name__ == "__main__":
    ejecutar_dashboard()
