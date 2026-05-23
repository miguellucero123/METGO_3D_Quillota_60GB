#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Dashboards Especializados - METGO 3D
Sistema para ejecutar todos los dashboards disponibles en puertos específicos
"""

import subprocess
import sys
import time
import os
import signal
import threading
from datetime import datetime

class EjecutorDashboards:
    """Ejecutor de dashboards especializados"""
    
    def __init__(self):
        self.procesos_activos = {}
        self.puertos_dashboards = {
            'dashboard_completo_metgo.py': 8502,
            'dashboard_global_metgo.py': 8503,
            'dashboard_unificado_metgo.py': 8505,
            'dashboard_integrado_notebooks.py': 8506,
            'dashboard_monitoreo_metgo.py': 8507,
            'sistema_unificado_autenticado.py': 8504
        }
        
        print("=" * 80)
        print("EJECUTOR DE DASHBOARDS ESPECIALIZADOS - METGO 3D")
        print("Sistema Meteorologico Agricola Quillota - Version 2.0")
        print("=" * 80)
    
    def mostrar_menu(self):
        """Mostrar menú de opciones"""
        print("\nDASHBOARDS DISPONIBLES:")
        print("-" * 50)
        
        dashboards = [
            ("1", "dashboard_completo_metgo.py", "Dashboard Completo", "Puerto 8502"),
            ("2", "dashboard_global_metgo.py", "Dashboard Global", "Puerto 8503"),
            ("3", "dashboard_unificado_metgo.py", "Dashboard Unificado", "Puerto 8505"),
            ("4", "dashboard_integrado_notebooks.py", "Dashboard Integrado", "Puerto 8506"),
            ("5", "dashboard_monitoreo_metgo.py", "Dashboard Monitoreo", "Puerto 8507"),
            ("6", "sistema_unificado_autenticado.py", "Sistema Autenticado", "Puerto 8504"),
            ("7", "todos", "Ejecutar Todos los Dashboards", "Puertos 8502-8507"),
            ("8", "estado", "Ver Estado de Servicios", "Verificar puertos"),
            ("9", "detener", "Detener Todos los Servicios", "Cerrar procesos"),
            ("0", "salir", "Salir", "Terminar ejecutor")
        ]
        
        for opcion, archivo, nombre, puerto in dashboards:
            estado = "[ACTIVO]" if archivo in self.procesos_activos else "[INACTIVO]"
            print(f"{opcion}. {nombre:<25} {puerto:<15} {estado}")
        
        print("-" * 50)
    
    def verificar_archivo(self, archivo):
        """Verificar si el archivo existe"""
        if not os.path.exists(archivo):
            print(f"[ERROR] Error: El archivo {archivo} no existe")
            return False
        return True
    
    def verificar_puerto(self, puerto):
        """Verificar si el puerto está disponible"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', puerto))
            sock.close()
            return result != 0  # True si está disponible
        except:
            return False
    
    def ejecutar_dashboard(self, archivo, puerto):
        """Ejecutar un dashboard específico"""
        if not self.verificar_archivo(archivo):
            return False
        
        if not self.verificar_puerto(puerto):
            print(f"[ADVERTENCIA] Advertencia: Puerto {puerto} esta en uso")
            respuesta = input("¿Continuar de todos modos? (s/n): ").lower()
            if respuesta != 's':
                return False
        
        print(f"\n[EJECUTANDO] Ejecutando {archivo} en puerto {puerto}...")
        
        try:
            # Ejecutar dashboard en segundo plano
            proceso = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', archivo,
                '--server.port', str(puerto),
                '--server.headless', 'true'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.procesos_activos[archivo] = {
                'proceso': proceso,
                'puerto': puerto,
                'inicio': datetime.now()
            }
            
            print(f"✅ {archivo} iniciado exitosamente")
            print(f"   Puerto: {puerto}")
            print(f"   URL: http://localhost:{puerto}")
            print(f"   PID: {proceso.pid}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando {archivo}: {e}")
            return False
    
    def ejecutar_todos(self):
        """Ejecutar todos los dashboards"""
        print("\n🚀 Ejecutando todos los dashboards...")
        
        exito = 0
        total = len(self.puertos_dashboards)
        
        for archivo, puerto in self.puertos_dashboards.items():
            if self.ejecutar_dashboard(archivo, puerto):
                exito += 1
            time.sleep(2)  # Esperar entre ejecuciones
        
        print(f"\n📊 Resumen: {exito}/{total} dashboards iniciados exitosamente")
        
        if exito > 0:
            print("\n🌐 URLs disponibles:")
            for archivo, info in self.procesos_activos.items():
                print(f"   {archivo}: http://localhost:{info['puerto']}")
    
    def verificar_estado(self):
        """Verificar estado de todos los servicios"""
        print("\n📋 ESTADO DE SERVICIOS:")
        print("-" * 50)
        
        for archivo, puerto in self.puertos_dashboards.items():
            if archivo in self.procesos_activos:
                proceso_info = self.procesos_activos[archivo]
                try:
                    # Verificar si el proceso sigue activo
                    proceso_info['proceso'].poll()
                    if proceso_info['proceso'].returncode is None:
                        estado = "🟢 Activo"
                        tiempo = datetime.now() - proceso_info['inicio']
                        print(f"✅ {archivo:<35} Puerto {puerto:<5} {estado} (PID: {proceso_info['proceso'].pid}) - {tiempo}")
                    else:
                        estado = "🔴 Terminado"
                        print(f"❌ {archivo:<35} Puerto {puerto:<5} {estado}")
                        del self.procesos_activos[archivo]
                except:
                    estado = "❓ Desconocido"
                    print(f"❓ {archivo:<35} Puerto {puerto:<5} {estado}")
            else:
                # Verificar si hay algo corriendo en el puerto
                if self.verificar_puerto(puerto):
                    estado = "🔴 Inactivo"
                else:
                    estado = "🟡 Puerto ocupado"
                print(f"⚪ {archivo:<35} Puerto {puerto:<5} {estado}")
    
    def detener_todos(self):
        """Detener todos los servicios activos"""
        print("\n🛑 Deteniendo todos los servicios...")
        
        if not self.procesos_activos:
            print("ℹ️  No hay servicios activos")
            return
        
        for archivo, info in list(self.procesos_activos.items()):
            try:
                print(f"🛑 Deteniendo {archivo}...")
                info['proceso'].terminate()
                
                # Esperar a que termine
                try:
                    info['proceso'].wait(timeout=5)
                    print(f"✅ {archivo} detenido exitosamente")
                except subprocess.TimeoutExpired:
                    print(f"⚠️  {archivo} no respondió, forzando terminación...")
                    info['proceso'].kill()
                    info['proceso'].wait()
                    print(f"✅ {archivo} detenido forzadamente")
                
                del self.procesos_activos[archivo]
                
            except Exception as e:
                print(f"❌ Error deteniendo {archivo}: {e}")
        
        print("✅ Todos los servicios han sido detenidos")
    
    def manejar_salida(self):
        """Manejar salida del programa"""
        def signal_handler(signum, frame):
            print("\n\n🛑 Señal de interrupción recibida...")
            self.detener_todos()
            print("👋 Saliendo del ejecutor de dashboards")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def ejecutar(self):
        """Ejecutar el menú principal"""
        self.manejar_salida()
        
        while True:
            try:
                self.mostrar_menu()
                
                opcion = input("\nSelecciona una opción: ").strip()
                
                if opcion == "0" or opcion.lower() == "salir":
                    print("👋 Saliendo del ejecutor...")
                    self.detener_todos()
                    break
                
                elif opcion == "7" or opcion.lower() == "todos":
                    self.ejecutar_todos()
                
                elif opcion == "8" or opcion.lower() == "estado":
                    self.verificar_estado()
                
                elif opcion == "9" or opcion.lower() == "detener":
                    self.detener_todos()
                
                elif opcion in ["1", "2", "3", "4", "5", "6"]:
                    archivos = list(self.puertos_dashboards.keys())
                    indice = int(opcion) - 1
                    if 0 <= indice < len(archivos):
                        archivo = archivos[indice]
                        puerto = self.puertos_dashboards[archivo]
                        self.ejecutar_dashboard(archivo, puerto)
                    else:
                        print("❌ Opción inválida")
                
                else:
                    print("❌ Opción no reconocida")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupción del usuario")
                self.detener_todos()
                break
            except Exception as e:
                    print(f"[ERROR] Error inesperado: {e}")
                input("Presiona Enter para continuar...")

def main():
    """Función principal"""
    try:
        ejecutor = EjecutorDashboards()
        ejecutor.ejecutar()
    except Exception as e:
        print(f"[ERROR] Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
