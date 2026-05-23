"""
Script para verificar y configurar correctamente todos los dashboards desde el disco D:
"""

import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path

class VerificadorDashboards:
    def __init__(self):
        self.directorio_actual = os.getcwd()
        self.dashboards_config = {
            "autenticacion": {
                "archivo": "sistema_autenticacion_metgo.py",
                "puerto": 8500,
                "nombre": "Sistema de Autenticacion"
            },
            "principal": {
                "archivo": "dashboard_principal_integrado_metgo.py", 
                "puerto": 8512,
                "nombre": "Dashboard Principal Integrado"
            },
            "meteorologico": {
                "archivo": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "nombre": "Dashboard Meteorologico"
            },
            "agricola": {
                "archivo": "dashboard_agricola_avanzado.py",
                "puerto": 8501,
                "nombre": "Dashboard Agricola"
            }
        }
    
    def verificar_directorio(self):
        """Verificar que estamos en el directorio correcto"""
        print(f"Directorio actual: {self.directorio_actual}")
        
        if not self.directorio_actual.startswith("D:"):
            print("ADVERTENCIA: No estamos en el disco D:")
            return False
        
        # Verificar que los archivos de dashboard existen
        archivos_faltantes = []
        for dashboard_id, config in self.dashboards_config.items():
            archivo = config["archivo"]
            if not os.path.exists(archivo):
                archivos_faltantes.append(archivo)
        
        if archivos_faltantes:
            print("ERROR: Archivos faltantes:")
            for archivo in archivos_faltantes:
                print(f"  - {archivo}")
            return False
        
        print("OK: Todos los archivos de dashboard existen")
        return True
    
    def verificar_puerto(self, puerto):
        """Verificar si un puerto está en uso"""
        try:
            response = requests.get(f"http://localhost:{puerto}/_stcore/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def iniciar_dashboard(self, dashboard_id, config):
        """Iniciar un dashboard específico"""
        archivo = config["archivo"]
        puerto = config["puerto"]
        nombre = config["nombre"]
        
        print(f"Iniciando {nombre} en puerto {puerto}...")
        
        try:
            command = [
                sys.executable, "-m", "streamlit", "run",
                archivo,
                "--server.port", str(puerto),
                "--server.headless", "true"
            ]
            
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Esperar a que se inicie
            
            if self.verificar_puerto(puerto):
                print(f"OK: {nombre} iniciado correctamente en puerto {puerto}")
                return True
            else:
                print(f"ERROR: {nombre} no se pudo iniciar en puerto {puerto}")
                return False
                
        except Exception as e:
            print(f"ERROR iniciando {nombre}: {e}")
            return False
    
    def verificar_todos_los_dashboards(self):
        """Verificar el estado de todos los dashboards"""
        print("VERIFICANDO ESTADO DE DASHBOARDS")
        print("=" * 50)
        
        dashboards_activos = 0
        dashboards_faltantes = []
        
        for dashboard_id, config in self.dashboards_config.items():
            puerto = config["puerto"]
            nombre = config["nombre"]
            
            if self.verificar_puerto(puerto):
                print(f"OK: {nombre} - Puerto {puerto} (ACTIVO)")
                dashboards_activos += 1
            else:
                print(f"ERROR: {nombre} - Puerto {puerto} (INACTIVO)")
                dashboards_faltantes.append((dashboard_id, config))
        
        print(f"\nResumen: {dashboards_activos}/{len(self.dashboards_config)} dashboards activos")
        
        return dashboards_faltantes
    
    def iniciar_dashboards_faltantes(self, dashboards_faltantes):
        """Iniciar los dashboards que no están ejecutándose"""
        if not dashboards_faltantes:
            print("Todos los dashboards ya están ejecutándose")
            return
        
        print("\nINICIANDO DASHBOARDS FALTANTES")
        print("=" * 40)
        
        for dashboard_id, config in dashboards_faltantes:
            self.iniciar_dashboard(dashboard_id, config)
    
    def mostrar_enlaces(self):
        """Mostrar enlaces a todos los dashboards"""
        print("\nENLACES A DASHBOARDS")
        print("=" * 30)
        
        for dashboard_id, config in self.dashboards_config.items():
            puerto = config["puerto"]
            nombre = config["nombre"]
            url = f"http://localhost:{puerto}"
            print(f"{nombre}: {url}")
    
    def abrir_dashboard_principal(self):
        """Abrir el Dashboard Principal en el navegador"""
        puerto_principal = self.dashboards_config["principal"]["puerto"]
        url = f"http://localhost:{puerto_principal}"
        
        print(f"\nAbriendo Dashboard Principal: {url}")
        webbrowser.open_new_tab(url)
    
    def ejecutar_verificacion_completa(self):
        """Ejecutar verificación completa del sistema"""
        print("VERIFICACION COMPLETA DE DASHBOARDS METGO 3D")
        print("=" * 60)
        
        # 1. Verificar directorio
        if not self.verificar_directorio():
            print("ERROR: Verificación de directorio falló")
            return False
        
        print()
        
        # 2. Verificar estado de dashboards
        dashboards_faltantes = self.verificar_todos_los_dashboards()
        
        # 3. Iniciar dashboards faltantes
        if dashboards_faltantes:
            self.iniciar_dashboards_faltantes(dashboards_faltantes)
            print("\nVerificando estado después de iniciar dashboards...")
            time.sleep(2)
            self.verificar_todos_los_dashboards()
        
        # 4. Mostrar enlaces
        self.mostrar_enlaces()
        
        # 5. Abrir Dashboard Principal
        self.abrir_dashboard_principal()
        
        print("\nVERIFICACION COMPLETA FINALIZADA")
        print("Sistema listo para usar!")
        
        return True

def main():
    verificador = VerificadorDashboards()
    verificador.ejecutar_verificacion_completa()

if __name__ == "__main__":
    main()


