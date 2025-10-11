"""
EJECUTOR DEL DASHBOARD AGRÍCOLA AVANZADO - METGO 3D QUILLOTA
Script para ejecutar el sistema sofisticado de recomendaciones agrícolas
"""

import subprocess
import sys
import os
import time
import webbrowser
from datetime import datetime

class EjecutorDashboardAgricolaAvanzado:
    def __init__(self):
        self.archivo_dashboard = "dashboard_agricola_avanzado.py"
        self.puerto = 8508
        self.url = f"http://localhost:{self.puerto}"
        
    def verificar_dependencias(self):
        """Verificar que las dependencias estén instaladas"""
        try:
            import streamlit
            import pandas
            import numpy
            import plotly
            print("[OK] Todas las dependencias estan instaladas")
            return True
        except ImportError as e:
            print(f"[ERROR] Dependencia faltante: {e}")
            print("[INSTALANDO] Instalando dependencias...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pandas", "numpy", "plotly"])
                print("[OK] Dependencias instaladas exitosamente")
                return True
            except subprocess.CalledProcessError:
                print("[ERROR] Error instalando dependencias")
                return False
    
    def verificar_archivos(self):
        """Verificar que los archivos necesarios existan"""
        archivos_requeridos = [
            "dashboard_agricola_avanzado.py",
            "sistema_recomendaciones_agricolas_avanzado.py"
        ]
        
        for archivo in archivos_requeridos:
            if not os.path.exists(archivo):
                print(f"[ERROR] Archivo faltante: {archivo}")
                return False
        
        print("[OK] Todos los archivos necesarios estan presentes")
        return True
    
    def verificar_puerto(self):
        """Verificar si el puerto está disponible"""
        import socket
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", self.puerto))
            s.close()
            print(f"[OK] Puerto {self.puerto} esta disponible")
            return True
        except socket.error:
            print(f"[ADVERTENCIA] Puerto {self.puerto} esta en uso")
            return False
    
    def ejecutar_dashboard(self):
        """Ejecutar el dashboard agrícola avanzado"""
        print("[INICIANDO] Iniciando Dashboard Agricola Avanzado...")
        print(f"[PUERTO] Puerto: {self.puerto}")
        print(f"[URL] URL: {self.url}")
        print("-" * 50)
        
        try:
            # Comando para ejecutar Streamlit
            comando = [
                sys.executable, "-m", "streamlit", "run",
                self.archivo_dashboard,
                "--server.port", str(self.puerto),
                "--server.headless", "true",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false"
            ]
            
            print("[EJECUTANDO] Ejecutando comando:")
            print(" ".join(comando))
            print("-" * 50)
            
            # Ejecutar el proceso
            proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Esperar un poco para que Streamlit se inicie
            print("[ESPERANDO] Esperando que el servidor se inicie...")
            time.sleep(8)
            
            # Verificar si el proceso está ejecutándose
            if proceso.poll() is None:
                print("[OK] Dashboard ejecutandose exitosamente")
                print(f"[URL] Accede a: {self.url}")
                
                # Intentar abrir el navegador
                try:
                    webbrowser.open(self.url)
                    print("[OK] Navegador abierto automaticamente")
                except Exception as e:
                    print(f"[ADVERTENCIA] No se pudo abrir el navegador automaticamente: {e}")
                    print(f"[URL] Abre manualmente: {self.url}")
                
                print("-" * 50)
                print("[INSTRUCCIONES] INSTRUCCIONES DE USO:")
                print("1. [PLANTA] El dashboard esta disenado para el Valle de Quillota")
                print("2. [REFRESH] Haz clic en 'Generar Datos Meteorologicos' en la sidebar")
                print("3. [TEMPERATURA] Explora las alertas de heladas por estacion")
                print("4. [CULTIVO] Revisa las recomendaciones de cosecha por cultivo")
                print("5. [PLAGA] Analiza el control de plagas")
                print("6. [GRAFICO] Genera reportes integrales")
                print("-" * 50)
                print("[DETENER] Para detener el servidor, presiona Ctrl+C")
                
                # Mantener el proceso ejecutándose
                try:
                    proceso.wait()
                except KeyboardInterrupt:
                    print("\n[DETENIENDO] Deteniendo servidor...")
                    proceso.terminate()
                    proceso.wait()
                    print("[OK] Servidor detenido")
            else:
                print("[ERROR] Error al ejecutar el dashboard")
                stdout, stderr = proceso.communicate()
                if stderr:
                    print("Error:", stderr)
                return False
                
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            return False
        
        return True
    
    def mostrar_informacion_sistema(self):
        """Mostrar información del sistema"""
        print("=" * 60)
        print("[PLANTA] METGO 3D - DASHBOARD AGRICOLA AVANZADO")
        print("Sistema Integral de Gestion Agricola para el Valle de Quillota")
        print("=" * 60)
        print(f"[FECHA] Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[PYTHON] Python: {sys.version.split()[0]}")
        print(f"[DIRECTORIO] Directorio: {os.getcwd()}")
        print("=" * 60)
    
    def ejecutar(self):
        """Ejecutar el proceso completo"""
        self.mostrar_informacion_sistema()
        
        # Verificaciones previas
        if not self.verificar_dependencias():
            return False
        
        if not self.verificar_archivos():
            return False
        
        if not self.verificar_puerto():
            respuesta = input("¿Continuar de todos modos? (s/n): ").lower()
            if respuesta != 's':
                print("[ERROR] Operacion cancelada")
                return False
        
        # Ejecutar dashboard
        return self.ejecutar_dashboard()

def main():
    """Función principal"""
    ejecutor = EjecutorDashboardAgricolaAvanzado()
    
    try:
        exito = ejecutor.ejecutar()
        if exito:
            print("\n[OK] Dashboard ejecutado exitosamente")
        else:
            print("\n[ERROR] Error ejecutando el dashboard")
    except KeyboardInterrupt:
        print("\n[DETENIDO] Operacion cancelada por el usuario")
    except Exception as e:
        print(f"\n[ERROR] Error critico: {e}")

if __name__ == "__main__":
    main()
