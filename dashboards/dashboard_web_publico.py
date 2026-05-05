#!/usr/bin/env python3
"""
Script para poner el dashboard METGO en linea publica usando ngrok
"""

import subprocess
import sys
import time
import threading
import os
import urllib.request

def instalar_ngrok():
    """Descarga e instala ngrok"""
    print("Descargando ngrok...")
    try:
        # URL de descarga de ngrok
        ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        ngrok_zip = "ngrok.zip"
        
        print("Descargando desde:", ngrok_url)
        urllib.request.urlretrieve(ngrok_url, ngrok_zip)
        
        # Extraer ngrok
        import zipfile
        with zipfile.ZipFile(ngrok_zip, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Limpiar archivo zip
        os.remove(ngrok_zip)
        
        print("ngrok instalado correctamente")
        return True
        
    except Exception as e:
        print(f"Error instalando ngrok: {e}")
        return False

def verificar_ngrok():
    """Verifica si ngrok esta instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True, shell=True)
        return True
    except:
        return False

def ejecutar_streamlit():
    """Ejecuta Streamlit en segundo plano"""
    try:
        comando = [
            sys.executable, "-m", "streamlit", "run",
            "sistema_auth_dashboard_principal_metgo.py",
            "--server.port=8501",
            "--server.address=127.0.0.1",
            "--server.headless=true"
        ]
        
        print("Iniciando Streamlit...")
        subprocess.run(comando)
        
    except Exception as e:
        print(f"Error ejecutando Streamlit: {e}")

def ejecutar_ngrok():
    """Ejecuta ngrok para crear tunel publico"""
    try:
        print("Iniciando tunel publico con ngrok...")
        subprocess.run(['ngrok', 'http', '8501', '--log=stdout'], shell=True)
    except Exception as e:
        print(f"Error ejecutando ngrok: {e}")

def obtener_url_ngrok():
    """Obtiene la URL publica de ngrok"""
    try:
        import requests
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        data = response.json()
        
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
        
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'http':
                return tunnel['public_url']
                
    except Exception as e:
        print(f"No se pudo obtener URL de ngrok: {e}")
    
    return None

def main():
    """Funcion principal"""
    print("=" * 60)
    print("DASHBOARD METGO - ACCESO PUBLICO WEB")
    print("=" * 60)
    
    # Verificar si ngrok esta instalado
    if not verificar_ngrok():
        print("ngrok no encontrado. Instalando...")
        if not instalar_ngrok():
            print("No se pudo instalar ngrok. Usando acceso local solamente.")
            print("URLs disponibles:")
            print("Local: http://localhost:8501")
            print("Red:   http://192.168.1.7:8501")
            
            # Ejecutar solo Streamlit
            ejecutar_streamlit()
            return
    
    print("ngrok disponible")
    print()
    
    # Iniciar Streamlit en hilo separado
    streamlit_thread = threading.Thread(target=ejecutar_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Esperar a que Streamlit inicie
    print("Esperando a que Streamlit inicie...")
    time.sleep(5)
    
    # Iniciar ngrok
    ngrok_thread = threading.Thread(target=ejecutar_ngrok, daemon=True)
    ngrok_thread.start()
    
    # Esperar a que ngrok inicie
    time.sleep(3)
    
    # Obtener URL publica
    url_publica = obtener_url_ngrok()
    
    print("=" * 60)
    print("DASHBOARD METGO EJECUTANDOSE")
    print("=" * 60)
    
    if url_publica:
        print(f"URL PUBLICA: {url_publica}")
        print("Accesible desde cualquier lugar del mundo")
        print()
        print("Comparte esta URL con otros usuarios:")
        print(f"{url_publica}")
    else:
        print("URL publica no disponible")
    
    print()
    print("URLS DISPONIBLES:")
    print(f"Local:        http://localhost:8501")
    print(f"Red Local:    http://192.168.1.7:8501")
    if url_publica:
        print(f"Publica:      {url_publica}")
    
    print()
    print("IMPORTANTE:")
    print("- Presiona Ctrl+C para detener")
    print("- La URL publica cambiara cada vez que reinicies")
    print("- Para URL fija, registra cuenta en ngrok.com")
    print()
    
    try:
        # Mantener el programa ejecutandose
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo dashboard...")
        print("Dashboard detenido")

if __name__ == "__main__":
    main()
