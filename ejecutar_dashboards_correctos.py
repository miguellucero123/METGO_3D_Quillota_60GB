import subprocess
import time
import os
import sys
from datetime import datetime

def ejecutar_dashboard(archivo, puerto):
    """Ejecuta un dashboard en un puerto específico"""
    try:
        print(f"Iniciando {archivo} en puerto {puerto}...")
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            archivo, 
            "--server.port", str(puerto),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        # Ejecutar en background
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        print(f"OK - {archivo} iniciado en puerto {puerto}")
        return process
    except Exception as e:
        print(f"ERROR - {archivo}: {e}")
        return None

def main():
    """Función principal para ejecutar los dashboards correctos"""
    print("=" * 60)
    print("INICIANDO DASHBOARDS CORRECTOS - SISTEMA METGO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Solo los archivos nuevos y correctos
    dashboards_correctos = [
        ("sistema_auth_dashboard_principal_metgo.py", 8501, "Dashboard Principal"),
        ("dashboard_meteorologico_profesional.py", 8502, "Meteorologico Profesional"),
        ("dashboard_agricola_inteligente.py", 8503, "Agricola Inteligente"),
        ("dashboard_monitoreo_tiempo_real.py", 8504, "Monitoreo Tiempo Real"),
        ("dashboard_ia_ml_avanzado.py", 8505, "IA/ML Avanzado"),
        ("dashboard_visualizaciones_avanzadas.py", 8506, "Visualizaciones Avanzadas"),
        ("dashboard_global_metricas.py", 8507, "Global Metricas"),
        ("dashboard_agricultura_precision.py", 8508, "Agricultura Precision"),
        ("dashboard_analisis_comparativo.py", 8509, "Analisis Comparativo"),
        ("dashboard_alertas_automaticas.py", 8510, "Alertas Automaticas"),
        ("dashboard_simple_optimizado.py", 8511, "Dashboard Simple"),
        ("dashboard_unificado_diferenciado.py", 8512, "Dashboard Unificado")
    ]
    
    procesos = []
    
    print("DASHBOARDS CORRECTOS A INICIAR:")
    print("-" * 50)
    for archivo, puerto, nombre in dashboards_correctos:
        print(f"{nombre:<30} -> Puerto {puerto}")
    print("-" * 50)
    print()
    
    # Verificar que los archivos existen
    archivos_faltantes = []
    for archivo, _, _ in dashboards_correctos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("ARCHIVOS FALTANTES:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print()
        print("Solo se ejecutaran los dashboards disponibles.")
        print()
    
    # Ejecutar dashboards disponibles
    dashboards_disponibles = [(archivo, puerto, nombre) for archivo, puerto, nombre in dashboards_correctos 
                             if os.path.exists(archivo)]
    
    print("INICIANDO DASHBOARDS...")
    print()
    
    for archivo, puerto, nombre in dashboards_disponibles:
        proceso = ejecutar_dashboard(archivo, puerto)
        if proceso:
            procesos.append((proceso, archivo, puerto, nombre))
        time.sleep(3)  # Esperar 3 segundos entre cada inicio
    
    print()
    print("=" * 60)
    print("DASHBOARDS INICIADOS EXITOSAMENTE")
    print("=" * 60)
    print()
    
    # Mostrar URLs de acceso
    print("ACCESO DESDE CELULAR (Red Local):")
    print("-" * 40)
    for _, _, puerto, nombre in procesos:
        print(f"{nombre:<30} -> http://192.168.1.7:{puerto}")
    print("-" * 40)
    print()
    
    print("ACCESO DESDE COMPUTADORA:")
    print("-" * 40)
    for _, _, puerto, nombre in procesos:
        print(f"{nombre:<30} -> http://localhost:{puerto}")
    print("-" * 40)
    print()
    
    print("INSTRUCCIONES PARA ACCEDER:")
    print("-" * 40)
    print("1. Desde tu celular, conecta a la misma red WiFi")
    print("2. Abre el navegador y ve a: http://192.168.1.7:8501")
    print("3. Usa las credenciales de acceso")
    print("4. Navega a otros dashboards desde el menu principal")
    print("-" * 40)
    print()
    
    print("IMPORTANTE:")
    print("- Manten esta ventana abierta para que los dashboards funcionen")
    print("- Para detener todos los dashboards, cierra esta ventana")
    print("- Cada dashboard funciona independientemente")
    print()
    
    try:
        print("Dashboards ejecutandose... Presiona Ctrl+C para detener")
        print("=" * 60)
        
        # Mantener el script corriendo
        while True:
            time.sleep(10)
            # Verificar que los procesos sigan corriendo
            procesos_activos = []
            for proceso, archivo, puerto, nombre in procesos:
                if proceso.poll() is None:  # Proceso aún corriendo
                    procesos_activos.append((proceso, archivo, puerto, nombre))
                else:
                    print(f"WARN - {nombre} se detuvo inesperadamente")
            
            procesos = procesos_activos
            
            if not procesos:
                print("ERROR - Todos los dashboards se han detenido")
                break
                
    except KeyboardInterrupt:
        print("\nDeteniendo todos los dashboards...")
        
        # Terminar todos los procesos
        for proceso, archivo, puerto, nombre in procesos:
            try:
                proceso.terminate()
                print(f"OK - {nombre} detenido")
            except:
                pass
        
        print("Todos los dashboards detenidos correctamente")

if __name__ == "__main__":
    main()
