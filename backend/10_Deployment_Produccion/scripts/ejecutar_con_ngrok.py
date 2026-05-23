#!/usr/bin/env python3
"""
Script para ejecutar el dashboard con ngrok para acceso público
"""

import subprocess
import sys
import time
import threading
import requests

def verificar_ngrok():
    """Verifica si ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def instalar_ngrok():
    """Instala ngrok si no está disponible"""
    print("📥 ngrok no encontrado. Instalando...")
    try:
        # Descargar ngrok
        subprocess.run([
            'curl', '-s', 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip', 
            '-o', 'ngrok.zip'
        ], check=True)
        
        # Extraer ngrok
        subprocess.run(['powershell', 'Expand-Archive', 'ngrok.zip', '-DestinationPath', '.'], check=True)
        
        print("✅ ngrok instalado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error instalando ngrok: {e}")
        return False

def ejecutar_streamlit():
    """Ejecuta Streamlit en segundo plano"""
    comando = [
        sys.executable, "-m", "streamlit", "run",
        "sistema_auth_dashboard_principal_metgo.py",
        "--server.port=8501",
        "--server.address=127.0.0.1",
        "--server.headless=true"
    ]
    
    try:
        subprocess.run(comando)
    except Exception as e:
        print(f"❌ Error ejecutando Streamlit: {e}")

def ejecutar_ngrok():
    """Ejecuta ngrok para crear túnel público"""
    try:
        subprocess.run(['ngrok', 'http', '8501', '--log=stdout'])
    except Exception as e:
        print(f"❌ Error ejecutando ngrok: {e}")

def obtener_url_ngrok():
    """Obtiene la URL pública de ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        data = response.json()
        
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
        
        # Si no hay HTTPS, usar HTTP
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'http':
                return tunnel['public_url']
                
    except Exception as e:
        print(f"⚠️  No se pudo obtener URL de ngrok: {e}")
    
    return None

def main():
    print("🚀 Dashboard METGO con Acceso Público (ngrok)")
    print("=" * 50)
    
    # Verificar/instalar ngrok
    if not verificar_ngrok():
        if not instalar_ngrok():
            print("❌ No se pudo instalar ngrok. Usando acceso local solamente.")
            print("🌐 URLs disponibles:")
            print("   🏠 Local: http://localhost:8501")
            print("   🏢 Red:   http://192.168.1.7:8501")
            
            # Ejecutar solo Streamlit
            ejecutar_streamlit()
            return
    
    print("✅ ngrok disponible")
    print()
    
    # Iniciar Streamlit en hilo separado
    print("🚀 Iniciando Streamlit...")
    streamlit_thread = threading.Thread(target=ejecutar_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Esperar a que Streamlit inicie
    print("⏳ Esperando a que Streamlit inicie...")
    time.sleep(5)
    
    # Iniciar ngrok
    print("🌐 Iniciando túnel público con ngrok...")
    ngrok_thread = threading.Thread(target=ejecutar_ngrok, daemon=True)
    ngrok_thread.start()
    
    # Esperar a que ngrok inicie
    time.sleep(3)
    
    # Obtener URL pública
    url_publica = obtener_url_ngrok()
    
    print("=" * 50)
    print("🎉 Dashboard METGO Ejecutándose")
    print("=" * 50)
    
    if url_publica:
        print(f"🌍 URL Pública: {url_publica}")
        print("   ✅ Accesible desde cualquier lugar del mundo")
    else:
        print("⚠️  URL pública no disponible")
    
    print()
    print("🌐 URLs Disponibles:")
    print("   🏠 Local:        http://localhost:8501")
    print("   🏢 Red Local:    http://192.168.1.7:8501")
    if url_publica:
        print(f"   🌍 Pública:      {url_publica}")
    
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Presiona Ctrl+C para detener")
    print("   - La URL pública cambiará cada vez que reinicies")
    print("   - Para URL fija, registra una cuenta en ngrok.com")
    
    try:
        # Mantener el programa ejecutándose
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo dashboard...")
        print("✅ Dashboard detenido")

if __name__ == "__main__":
    main()
