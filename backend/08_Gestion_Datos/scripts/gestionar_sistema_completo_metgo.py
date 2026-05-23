#!/usr/bin/env python3
"""
Gestor del Sistema Completo METGO 3D
Script para gestionar todos los dashboards y servicios del sistema
"""

import subprocess
import sys
import os
import time
import requests
import json
from datetime import datetime

class GestorSistemaCompletoMETGO:
    def __init__(self):
        self.dashboards = {
            "autenticacion": {
                "nombre": "Sistema de Autenticación",
                "archivo": "sistema_autenticacion_metgo.py",
                "puerto": 8500,
                "descripcion": "Login y gestión de usuarios",
                "prioridad": 1  # Debe iniciarse primero
            },
            "meteorologico_mejorado": {
                "nombre": "Dashboard Meteorológico Mejorado",
                "archivo": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "descripcion": "Datos meteorológicos con métricas y pronósticos de 14 días",
                "prioridad": 2
            },
            "recomendaciones": {
                "nombre": "Dashboard de Recomendaciones",
                "archivo": "dashboard_integrado_recomendaciones_metgo.py",
                "puerto": 8510,
                "descripcion": "Recomendaciones de riego, plagas y heladas",
                "prioridad": 3
            },
            "alertas": {
                "nombre": "Sistema de Alertas Visuales",
                "archivo": "sistema_alertas_visuales_integrado_metgo.py",
                "puerto": 8511,
                "descripcion": "Alertas meteorológicas y recomendaciones de emergencia",
                "prioridad": 4
            },
            "principal": {
                "nombre": "Dashboard Principal Integrado",
                "archivo": "dashboard_principal_integrado_metgo.py",
                "puerto": 8512,
                "descripcion": "Sistema unificado de gestión",
                "prioridad": 5
            },
            "agricola": {
                "nombre": "Dashboard Agrícola",
                "archivo": "dashboard_agricola_avanzado.py",
                "puerto": 8501,
                "descripcion": "Gestión de cultivos y producción",
                "prioridad": 6
            },
            "empresarial": {
                "nombre": "Dashboard Empresarial",
                "archivo": "dashboard_empresarial_unificado_metgo.py",
                "puerto": 8503,
                "descripcion": "Vista ejecutiva con métricas empresariales",
                "prioridad": 7
            },
            "central": {
                "nombre": "Dashboard Central",
                "archivo": "dashboard_central_metgo.py",
                "puerto": 8509,
                "descripcion": "Hub unificado para todos los dashboards",
                "prioridad": 8
            }
        }
        
        self.procesos_activos = {}
        self.log_file = f"gestion_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def verificar_puerto_disponible(self, puerto):
        """Verificar si un puerto está disponible"""
        try:
            response = requests.get(f"http://localhost:{puerto}/_stcore/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def ejecutar_dashboard(self, dashboard_id):
        """Ejecutar un dashboard específico"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            print(f"[ERROR] Dashboard '{dashboard_id}' no encontrado")
            return False
        
        # Verificar si ya está ejecutándose
        if self.verificar_puerto_disponible(dashboard['puerto']):
            print(f"✅ {dashboard['nombre']} ya está ejecutándose en puerto {dashboard['puerto']}")
            return True
        
        try:
            print(f"🚀 Iniciando {dashboard['nombre']} en puerto {dashboard['puerto']}...")
            
            # Comando para ejecutar Streamlit
            comando = [
                sys.executable, "-m", "streamlit", "run", 
                dashboard['archivo'], 
                "--server.port", str(dashboard['puerto']), 
                "--server.headless", "true"
            ]
            
            # Ejecutar en segundo plano
            proceso = subprocess.Popen(
                comando, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            self.procesos_activos[dashboard_id] = proceso
            
            # Esperar un momento para que se inicie
            time.sleep(3)
            
            # Verificar que se inició correctamente
            if self.verificar_puerto_disponible(dashboard['puerto']):
                print(f"✅ {dashboard['nombre']} iniciado exitosamente en http://localhost:{dashboard['puerto']}")
                self._log(f"Dashboard {dashboard['nombre']} iniciado en puerto {dashboard['puerto']}")
                return True
            else:
                print(f"❌ Error: {dashboard['nombre']} no se inició correctamente")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando {dashboard['nombre']}: {e}")
            self._log(f"Error ejecutando {dashboard['nombre']}: {e}")
            return False
    
    def ejecutar_sistema_completo(self):
        """Ejecutar todo el sistema METGO 3D"""
        print("INICIANDO SISTEMA COMPLETO METGO 3D QUILLOTA")
        print("=" * 60)
        
        # Ordenar dashboards por prioridad
        dashboards_ordenados = sorted(
            self.dashboards.items(), 
            key=lambda x: x[1]['prioridad']
        )
        
        dashboards_exitosos = 0
        dashboards_fallidos = 0
        
        for dashboard_id, dashboard_info in dashboards_ordenados:
            print(f"\n📊 Procesando: {dashboard_info['nombre']}")
            
            if self.ejecutar_dashboard(dashboard_id):
                dashboards_exitosos += 1
                # Esperar entre ejecuciones para evitar conflictos
                time.sleep(2)
            else:
                dashboards_fallidos += 1
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE INICIO DEL SISTEMA")
        print("=" * 60)
        print(f"✅ Dashboards exitosos: {dashboards_exitosos}")
        print(f"❌ Dashboards fallidos: {dashboards_fallidos}")
        print(f"📊 Total procesados: {len(self.dashboards)}")
        
        if dashboards_exitosos > 0:
            print("\n🌐 DASHBOARDS DISPONIBLES:")
            for dashboard_id, dashboard_info in self.dashboards.items():
                if self.verificar_puerto_disponible(dashboard_info['puerto']):
                    print(f"  • {dashboard_info['nombre']}: http://localhost:{dashboard_info['puerto']}")
        
        print("\n👥 USUARIOS DE PRUEBA:")
        print("  • Administrador: admin / admin123")
        print("  • Ejecutivo: ejecutivo / ejecutivo123")
        print("  • Agricultor: agricultor / agricultor123")
        print("  • Técnico: tecnico / tecnico123")
        print("  • Usuario: usuario / usuario123")
        
        print("\n🚀 INSTRUCCIONES:")
        print("  1. Accede al Sistema de Autenticación: http://localhost:8500")
        print("  2. Inicia sesión con cualquier usuario de prueba")
        print("  3. Selecciona el dashboard que deseas usar")
        print("  4. Todos los dashboards están integrados y funcionando")
        
        # Abrir automáticamente el sistema de autenticación
        if self.verificar_puerto_disponible(8500):
            print("\n🌐 Abriendo sistema de autenticación...")
            try:
                import webbrowser
                webbrowser.open("http://localhost:8500")
            except:
                print("⚠️ No se pudo abrir el navegador automáticamente")
        
        return dashboards_exitosos > 0
    
    def verificar_estado_sistema(self):
        """Verificar el estado actual del sistema"""
        print("🔍 VERIFICANDO ESTADO DEL SISTEMA METGO 3D")
        print("=" * 50)
        
        dashboards_activos = 0
        dashboards_inactivos = 0
        
        for dashboard_id, dashboard_info in self.dashboards.items():
            estado = "🟢 ACTIVO" if self.verificar_puerto_disponible(dashboard_info['puerto']) else "🔴 INACTIVO"
            print(f"{estado} {dashboard_info['nombre']} (Puerto: {dashboard_info['puerto']})")
            
            if self.verificar_puerto_disponible(dashboard_info['puerto']):
                dashboards_activos += 1
            else:
                dashboards_inactivos += 1
        
        print("\n" + "=" * 50)
        print(f"📊 RESUMEN: {dashboards_activos} activos, {dashboards_inactivos} inactivos")
        
        return dashboards_activos, dashboards_inactivos
    
    def detener_sistema(self):
        """Detener todo el sistema"""
        print("🛑 DETENIENDO SISTEMA METGO 3D...")
        
        for dashboard_id, proceso in self.procesos_activos.items():
            try:
                if proceso.poll() is None:  # Si el proceso aún está corriendo
                    print(f"🛑 Deteniendo {self.dashboards[dashboard_id]['nombre']}...")
                    proceso.terminate()
                    try:
                        proceso.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proceso.kill()
                        print(f"🔨 Proceso {dashboard_id} terminado forzosamente")
            except Exception as e:
                print(f"❌ Error deteniendo {dashboard_id}: {e}")
        
        self.procesos_activos.clear()
        print("✅ Sistema detenido completamente")
    
    def _log(self, mensaje):
        """Registrar mensaje en el archivo de log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {mensaje}\n")

def main():
    """Función principal"""
    gestor = GestorSistemaCompletoMETGO()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "iniciar":
            gestor.ejecutar_sistema_completo()
        elif comando == "estado":
            gestor.verificar_estado_sistema()
        elif comando == "detener":
            gestor.detener_sistema()
        elif comando == "reiniciar":
            print("🔄 Reiniciando sistema...")
            gestor.detener_sistema()
            time.sleep(3)
            gestor.ejecutar_sistema_completo()
        else:
            print(f"❌ Comando '{comando}' no reconocido")
            print("Comandos disponibles: iniciar, estado, detener, reiniciar")
    else:
        # Modo interactivo
        while True:
            print("\n🌾 GESTOR DEL SISTEMA METGO 3D QUILLOTA")
            print("=" * 40)
            print("1. 🚀 Iniciar Sistema Completo")
            print("2. 🔍 Verificar Estado")
            print("3. 🛑 Detener Sistema")
            print("4. 🔄 Reiniciar Sistema")
            print("5. ❌ Salir")
            print("=" * 40)
            
            try:
                opcion = input("Selecciona una opción (1-5): ").strip()
                
                if opcion == "1":
                    gestor.ejecutar_sistema_completo()
                elif opcion == "2":
                    gestor.verificar_estado_sistema()
                elif opcion == "3":
                    gestor.detener_sistema()
                elif opcion == "4":
                    print("🔄 Reiniciando sistema...")
                    gestor.detener_sistema()
                    time.sleep(3)
                    gestor.ejecutar_sistema_completo()
                elif opcion == "5":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción no válida. Intenta de nuevo.")
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
