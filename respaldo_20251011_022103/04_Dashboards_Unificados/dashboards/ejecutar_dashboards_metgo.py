"""
EJECUTAR DASHBOARDS METGO 3D QUILLOTA
Script para ejecutar todos los dashboards disponibles
"""

import subprocess
import sys
import os
import time
import threading
from datetime import datetime

class EjecutorDashboardsMetgo:
    def __init__(self):
        self.dashboards = {
            'autenticacion': {
                'nombre': 'Sistema de Autenticación',
                'archivo': 'sistema_autenticacion_metgo.py',
                'puerto': 8500,
                'descripcion': 'Login y acceso seguro a dashboards'
            },
            'dashboard_empresarial': {
                'nombre': 'Dashboard Empresarial',
                'archivo': 'dashboard_empresarial_unificado_metgo.py',
                'puerto': 8503,
                'descripcion': 'Vista ejecutiva con métricas empresariales'
            },
            'dashboard_agricola': {
                'nombre': 'Dashboard Agrícola Avanzado',
                'archivo': 'dashboard_agricola_avanzado_metgo.py',
                'puerto': 8501,
                'descripcion': 'Gestión completa de cultivos y producción'
            },
            'dashboard_meteorologico': {
                'nombre': 'Dashboard Meteorológico',
                'archivo': 'dashboard_meteorologico_metgo.py',
                'puerto': 8502,
                'descripcion': 'Monitoreo climático en tiempo real'
            },
            'dashboard_drones': {
                'nombre': 'Dashboard con Drones',
                'archivo': 'dashboard_unificado_metgo_con_drones.py',
                'puerto': 8504,
                'descripcion': 'Monitoreo aéreo y análisis de cultivos'
            },
            'dashboard_unificado': {
                'nombre': 'Dashboard Unificado',
                'archivo': 'dashboard_unificado_metgo_integrado.py',
                'puerto': 8505,
                'descripcion': 'Punto de acceso central a todos los módulos'
            }
        }
        
        self.procesos_activos = {}
    
    def verificar_archivo(self, archivo):
        """Verificar que el archivo existe"""
        return os.path.exists(archivo)
    
    def ejecutar_dashboard(self, dashboard_id):
        """Ejecutar un dashboard específico"""
        try:
            dashboard = self.dashboards[dashboard_id]
            
            if not self.verificar_archivo(dashboard['archivo']):
                print(f"[ERROR] Archivo {dashboard['archivo']} no encontrado")
                return False
            
            print(f"[EJECUTANDO] {dashboard['nombre']} en puerto {dashboard['puerto']}")
            
            # Comando para ejecutar Streamlit
            comando = [
                sys.executable, "-m", "streamlit", "run", 
                dashboard['archivo'], 
                "--server.port", str(dashboard['puerto']),
                "--server.headless", "true"
            ]
            
            # Ejecutar en proceso separado
            proceso = subprocess.Popen(comando, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            self.procesos_activos[dashboard_id] = proceso
            
            print(f"[OK] {dashboard['nombre']} iniciado en puerto {dashboard['puerto']}")
            print(f"[URL] http://localhost:{dashboard['puerto']}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error ejecutando {dashboard_id}: {e}")
            return False
    
    def ejecutar_todos_dashboards(self):
        """Ejecutar todos los dashboards disponibles"""
        print("="*70)
        print("INICIANDO TODOS LOS DASHBOARDS METGO 3D QUILLOTA")
        print("="*70)
        
        dashboards_exitosos = 0
        dashboards_fallidos = 0
        
        for dashboard_id, dashboard in self.dashboards.items():
            print(f"\n[PROCESANDO] {dashboard['nombre']}...")
            
            if self.ejecutar_dashboard(dashboard_id):
                dashboards_exitosos += 1
                time.sleep(2)  # Esperar entre ejecuciones
            else:
                dashboards_fallidos += 1
        
        print("\n" + "="*70)
        print("RESUMEN DE EJECUCIÓN")
        print("="*70)
        print(f"✅ Dashboards exitosos: {dashboards_exitosos}")
        print(f"❌ Dashboards fallidos: {dashboards_fallidos}")
        print(f"📊 Total procesados: {len(self.dashboards)}")
        
        if dashboards_exitosos > 0:
            print("\n🌐 DASHBOARDS DISPONIBLES:")
            for dashboard_id, dashboard in self.dashboards.items():
                if dashboard_id in self.procesos_activos:
                    print(f"  - {dashboard['nombre']}: http://localhost:{dashboard['puerto']}")
        
        print("\n🔐 USUARIOS DE PRUEBA:")
        print("  - Administrador: admin / admin123")
        print("  - Ejecutivo: ejecutivo / ejecutivo123")
        print("  - Agricultor: agricultor / agricultor123")
        print("  - Técnico: tecnico / tecnico123")
        print("  - Usuario: usuario / usuario123")
        
        print("\n💡 INSTRUCCIONES:")
        print("  1. Accede primero al Sistema de Autenticación (Puerto 8500)")
        print("  2. Inicia sesión con cualquier usuario de prueba")
        print("  3. Selecciona el dashboard que deseas usar")
        print("  4. Usa el mismo usuario y contraseña en cada dashboard")
        
        return dashboards_exitosos > 0
    
    def monitorear_procesos(self):
        """Monitorear procesos activos"""
        try:
            while True:
                procesos_activos = 0
                for dashboard_id, proceso in list(self.procesos_activos.items()):
                    if proceso.poll() is None:  # Proceso aún activo
                        procesos_activos += 1
                    else:
                        # Proceso terminado
                        print(f"[INFO] {dashboard_id} terminado")
                        del self.procesos_activos[dashboard_id]
                
                if procesos_activos == 0:
                    print("\n[INFO] Todos los dashboards han terminado")
                    break
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n[INFO] Deteniendo monitoreo...")
            self.detener_todos_dashboards()
    
    def detener_todos_dashboards(self):
        """Detener todos los dashboards activos"""
        print("\n[INFO] Deteniendo todos los dashboards...")
        
        for dashboard_id, proceso in self.procesos_activos.items():
            try:
                proceso.terminate()
                print(f"[OK] {dashboard_id} detenido")
            except:
                print(f"[ERROR] Error deteniendo {dashboard_id}")
        
        self.procesos_activos.clear()
    
    def mostrar_menu(self):
        """Mostrar menú interactivo"""
        while True:
            print("\n" + "="*50)
            print("MENÚ DASHBOARDS METGO 3D QUILLOTA")
            print("="*50)
            print("1. [AUTH] Ejecutar Sistema de Autenticacion")
            print("2. [EMP] Ejecutar Dashboard Empresarial")
            print("3. [AGR] Ejecutar Dashboard Agricola")
            print("4. [MET] Ejecutar Dashboard Meteorologico")
            print("5. [DRONE] Ejecutar Dashboard con Drones")
            print("6. [UNI] Ejecutar Dashboard Unificado")
            print("7. [ALL] Ejecutar Todos los Dashboards")
            print("8. [STATUS] Mostrar Estado de Dashboards")
            print("9. [STOP] Detener Todos los Dashboards")
            print("0. [EXIT] Salir")
            print("="*50)
            
            try:
                opcion = input("Selecciona una opción: ").strip()
                
                if opcion == "1":
                    self.ejecutar_dashboard('autenticacion')
                elif opcion == "2":
                    self.ejecutar_dashboard('dashboard_empresarial')
                elif opcion == "3":
                    self.ejecutar_dashboard('dashboard_agricola')
                elif opcion == "4":
                    self.ejecutar_dashboard('dashboard_meteorologico')
                elif opcion == "5":
                    self.ejecutar_dashboard('dashboard_drones')
                elif opcion == "6":
                    self.ejecutar_dashboard('dashboard_unificado')
                elif opcion == "7":
                    self.ejecutar_todos_dashboards()
                elif opcion == "8":
                    self.mostrar_estado()
                elif opcion == "9":
                    self.detener_todos_dashboards()
                elif opcion == "0":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def mostrar_estado(self):
        """Mostrar estado actual de los dashboards"""
        print("\n" + "="*60)
        print("ESTADO DE DASHBOARDS METGO 3D")
        print("="*60)
        
        for dashboard_id, dashboard in self.dashboards.items():
            estado = "🟢 ACTIVO" if dashboard_id in self.procesos_activos else "🔴 INACTIVO"
            print(f"{estado} | {dashboard['nombre']} | Puerto {dashboard['puerto']}")
        
        if self.procesos_activos:
            print(f"\n📊 Procesos activos: {len(self.procesos_activos)}")
        else:
            print("\n📊 No hay procesos activos")

def main():
    """Función principal"""
    ejecutor = EjecutorDashboardsMetgo()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "auth" or comando == "autenticacion":
            ejecutor.ejecutar_dashboard('autenticacion')
        elif comando == "empresarial":
            ejecutor.ejecutar_dashboard('dashboard_empresarial')
        elif comando == "agricola":
            ejecutor.ejecutar_dashboard('dashboard_agricola')
        elif comando == "meteorologico":
            ejecutor.ejecutar_dashboard('dashboard_meteorologico')
        elif comando == "drones":
            ejecutor.ejecutar_dashboard('dashboard_drones')
        elif comando == "unificado":
            ejecutor.ejecutar_dashboard('dashboard_unificado')
        elif comando == "todos" or comando == "all":
            ejecutor.ejecutar_todos_dashboards()
            # Monitorear procesos
            try:
                ejecutor.monitorear_procesos()
            except KeyboardInterrupt:
                ejecutor.detener_todos_dashboards()
        else:
            print("❌ Comando no reconocido")
            print("💡 Comandos disponibles: auth, empresarial, agricola, meteorologico, drones, unificado, todos")
    else:
        # Mostrar menú interactivo
        ejecutor.mostrar_menu()

if __name__ == "__main__":
    main()
