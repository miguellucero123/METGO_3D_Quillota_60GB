import requests
import time
from datetime import datetime

def verificar_dashboard(puerto, nombre):
    """Verifica si un dashboard está accesible"""
    try:
        url = f"http://192.168.1.7:{puerto}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {nombre} (Puerto {puerto}): ACCESIBLE")
            return True
        else:
            print(f"⚠️  {nombre} (Puerto {puerto}): Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {nombre} (Puerto {puerto}): NO ACCESIBLE - {e}")
        return False

def main():
    """Verifica el acceso a todos los dashboards"""
    print("=" * 60)
    print("📱 VERIFICACIÓN DE ACCESO DESDE CELULAR")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de dashboards y puertos
    dashboards = [
        (8501, "🏠 Dashboard Principal"),
        (8502, "🌤️ Meteorológico Profesional"),
        (8503, "🌾 Agrícola Inteligente"),
        (8504, "🔍 Monitoreo Tiempo Real"),
        (8505, "🤖 IA/ML Avanzado"),
        (8506, "📊 Visualizaciones Avanzadas"),
        (8507, "📈 Global Métricas"),
        (8508, "🌾 Agricultura Precisión"),
        (8509, "📊 Análisis Comparativo"),
        (8510, "🔬 Alertas Automáticas"),
        (8511, "📊 Dashboard Simple"),
        (8512, "🏠 Dashboard Unificado")
    ]
    
    print("🔍 VERIFICANDO ACCESO A DASHBOARDS...")
    print("-" * 50)
    
    accesibles = 0
    total = len(dashboards)
    
    for puerto, nombre in dashboards:
        if verificar_dashboard(puerto, nombre):
            accesibles += 1
        time.sleep(1)  # Esperar 1 segundo entre verificaciones
    
    print("-" * 50)
    print(f"📊 RESULTADO: {accesibles}/{total} dashboards accesibles")
    print()
    
    if accesibles > 0:
        print("✅ DASHBOARDS ACCESIBLES DESDE TU CELULAR:")
        print("-" * 40)
        for puerto, nombre in dashboards:
            print(f"📱 {nombre}")
            print(f"   URL: http://192.168.1.7:{puerto}")
            print()
        
        print("📋 INSTRUCCIONES PARA ACCEDER:")
        print("-" * 40)
        print("1. 📱 Asegúrate de estar en la misma red WiFi")
        print("2. 🌐 Abre el navegador en tu celular")
        print("3. 🔗 Copia y pega una de las URLs de arriba")
        print("4. 🔐 Usa las credenciales de acceso")
        print("5. 🎯 Navega entre dashboards desde el menú")
        print("-" * 40)
    else:
        print("❌ NINGÚN DASHBOARD ACCESIBLE")
        print("Verifica que:")
        print("- Los dashboards estén ejecutándose")
        print("- Estés en la misma red WiFi")
        print("- El firewall no bloquee las conexiones")
        print()
    
    print("🌐 URL PRINCIPAL RECOMENDADA:")
    print("   http://192.168.1.7:8501")
    print()

if __name__ == "__main__":
    main()
