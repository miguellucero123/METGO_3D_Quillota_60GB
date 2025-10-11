#!/usr/bin/env python3
"""
Script para poner el dashboard METGO en linea y accesible por web
"""

import subprocess
import sys
import time
import threading
import requests
import socket

def obtener_ip_publica():
    """Obtiene la IP publica del sistema"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return "No disponible"

def verificar_puerto_abierto(ip, puerto):
    """Verifica si un puerto esta abierto"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, puerto))
        sock.close()
        return result == 0
    except:
        return False

def configurar_firewall_windows():
    """Configura el firewall de Windows"""
    try:
        print("Configurando firewall de Windows...")
        
        comandos = [
            'netsh advfirewall firewall add rule name="METGO Dashboard 8501" dir=in action=allow protocol=TCP localport=8501',
            'netsh advfirewall firewall add rule name="METGO Dashboard 8502" dir=in action=allow protocol=TCP localport=8502',
            'netsh advfirewall firewall add rule name="METGO Dashboard 8503" dir=in action=allow protocol=TCP localport=8503',
            'netsh advfirewall firewall add rule name="METGO Dashboard 8504" dir=in action=allow protocol=TCP localport=8504',
            'netsh advfirewall firewall add rule name="METGO Dashboard 8505" dir=in action=allow protocol=TCP localport=8505'
        ]
        
        for comando in comandos:
            try:
                subprocess.run(comando, shell=True, check=True, capture_output=True)
                puerto = comando.split('localport=')[1]
                print(f"Puerto {puerto} configurado correctamente")
            except:
                puerto = comando.split('localport=')[1]
                print(f"Puerto {puerto} ya estaba configurado")
        
        print("Firewall configurado exitosamente")
        return True
        
    except Exception as e:
        print(f"Error configurando firewall: {e}")
        return False

def ejecutar_dashboard_publico():
    """Ejecuta el dashboard con acceso publico"""
    
    print("=" * 60)
    print("DASHBOARD METGO - ACCESO PUBLICO")
    print("=" * 60)
    
    # Configurar firewall
    configurar_firewall_windows()
    
    # Obtener IPs
    ip_local = "192.168.1.7"
    ip_publica = obtener_ip_publica()
    
    print(f"IP Local: {ip_local}")
    print(f"IP Publica: {ip_publica}")
    print()
    
    # Mostrar URLs disponibles
    print("URLS DISPONIBLES:")
    print(f"Local:        http://localhost:8501")
    print(f"Red Local:    http://{ip_local}:8501")
    print(f"Publica:      http://{ip_publica}:8501")
    print()
    
    # Verificar si el puerto esta abierto
    if ip_publica != "No disponible":
        if verificar_puerto_abierto(ip_publica, 8501):
            print("ESTADO: Puerto 8501 ABIERTO - Acceso publico disponible")
        else:
            print("ESTADO: Puerto 8501 CERRADO - Configurar router")
    
    print()
    print("IMPORTANTE PARA ACCESO PUBLICO:")
    print("1. El router debe tener PORT FORWARDING configurado")
    print("2. Puerto 8501 debe estar abierto en el router")
    print("3. Si no funciona, usar ngrok como alternativa")
    print()
    
    # Configuracion de Streamlit para acceso publico
    config_streamlit = [
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false",
        "--browser.gatherUsageStats=false"
    ]
    
    print("Ejecutando dashboard...")
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        # Ejecutar Streamlit
        comando = [
            sys.executable, "-m", "streamlit", "run", 
            "sistema_auth_dashboard_principal_metgo.py"
        ] + config_streamlit
        
        subprocess.run(comando)
        
    except KeyboardInterrupt:
        print("\nDashboard detenido por el usuario")
    except Exception as e:
        print(f"\nError ejecutando dashboard: {e}")

def main():
    """Funcion principal"""
    try:
        ejecutar_dashboard_publico()
    except Exception as e:
        print(f"Error: {e}")
        print("Usando configuracion basica...")
        
        # Configuracion basica sin verificaciones
        comando = [
            sys.executable, "-m", "streamlit", "run",
            "sistema_auth_dashboard_principal_metgo.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ]
        
        subprocess.run(comando)

if __name__ == "__main__":
    main()
