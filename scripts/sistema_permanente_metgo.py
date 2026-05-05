#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Permanente METGO_3D
Script para mantener todos los dashboards siempre en línea
"""

import subprocess
import time
import os
import sys
import signal
import psutil
from datetime import datetime
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sistema_permanente.log'),
        logging.StreamHandler()
    ]
)

class SistemaPermanenteMETGO:
    def __init__(self):
        self.dashboards = {
            "Principal": {
                "archivo": "sistema_auth_dashboard_principal_metgo.py",
                "puerto": 8501,
                "proceso": None,
                "activo": False
            },
            "Meteorologico": {
                "archivo": "dashboard_meteorologico_metgo.py",
                "puerto": 8502,
                "proceso": None,
                "activo": False
            },
            "Agricola": {
                "archivo": "dashboard_agricola_metgo.py",
                "puerto": 8503,
                "proceso": None,
                "activo": False
            },
            "Monitoreo": {
                "archivo": "dashboard_monitoreo_tiempo_real.py",
                "puerto": 8504,
                "proceso": None,
                "activo": False
            },
            "IA_ML": {
                "archivo": "dashboard_ia_ml_avanzado.py",
                "puerto": 8505,
                "proceso": None,
                "activo": False
            },
            "Visualizaciones": {
                "archivo": "dashboard_visualizaciones_avanzadas.py",
                "puerto": 8506,
                "proceso": None,
                "activo": False
            },
            "Global": {
                "archivo": "dashboard_global_metricas.py",
                "puerto": 8507,
                "proceso": None,
                "activo": False
            },
            "Agricultura_Precision": {
                "archivo": "dashboard_agricultura_precision.py",
                "puerto": 8508,
                "proceso": None,
                "activo": False
            },
            "Comparativo": {
                "archivo": "dashboard_analisis_comparativo.py",
                "puerto": 8509,
                "proceso": None,
                "activo": False
            },
            "Alertas": {
                "archivo": "dashboard_alertas_automaticas.py",
                "puerto": 8510,
                "proceso": None,
                "activo": False
            },
            "Simple": {
                "archivo": "dashboard_simple_optimizado.py",
                "puerto": 8511,
                "proceso": None,
                "activo": False
            },
            "Unificado": {
                "archivo": "dashboard_unificado_diferenciado.py",
                "puerto": 8512,
                "proceso": None,
                "activo": False
            },
            "Mobile": {
                "archivo": "dashboard_mobile_optimizado.py",
                "puerto": 8513,
                "proceso": None,
                "activo": False
            }
        }
        
        self.monitoreo_activo = True
        self.intervalo_verificacion = 30  # segundos
        
    def crear_directorio_logs(self):
        """Crear directorio de logs si no existe"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            logging.info("Directorio de logs creado")
    
    def verificar_puerto_disponible(self, puerto):
        """Verificar si un puerto está disponible"""
        for conn in psutil.net_connections():
            if conn.laddr.port == puerto:
                return False
        return True
    
    def iniciar_dashboard(self, nombre, config):
        """Iniciar un dashboard específico"""
        try:
            if not os.path.exists(config["archivo"]):
                logging.warning(f"Archivo no encontrado: {config['archivo']}")
                return False
            
            if not self.verificar_puerto_disponible(config["puerto"]):
                logging.warning(f"Puerto {config['puerto']} ya está en uso para {nombre}")
                return False
            
            # Comando para iniciar streamlit
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                config["archivo"],
                "--server.port", str(config["puerto"]),
                "--server.address", "0.0.0.0",  # Permitir acceso externo
                "--server.headless", "true",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false",
                "--browser.gatherUsageStats", "false"
            ]
            
            logging.info(f"Iniciando {nombre} en puerto {config['puerto']}")
            
            # Iniciar proceso en background
            proceso = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            config["proceso"] = proceso
            config["activo"] = True
            
            # Esperar un poco para verificar que se inició correctamente
            time.sleep(5)
            
            if proceso.poll() is None:
                logging.info(f"✅ {nombre} iniciado correctamente en puerto {config['puerto']}")
                return True
            else:
                logging.error(f"❌ Error al iniciar {nombre}")
                config["activo"] = False
                return False
                
        except Exception as e:
            logging.error(f"Error iniciando {nombre}: {e}")
            config["activo"] = False
            return False
    
    def detener_dashboard(self, nombre, config):
        """Detener un dashboard específico"""
        try:
            if config["proceso"] and config["activo"]:
                logging.info(f"Deteniendo {nombre}...")
                
                # Terminar proceso
                if os.name == 'nt':  # Windows
                    config["proceso"].terminate()
                else:  # Linux/Mac
                    config["proceso"].send_signal(signal.SIGTERM)
                
                # Esperar a que termine
                try:
                    config["proceso"].wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Forzar terminación si no responde
                    config["proceso"].kill()
                
                config["proceso"] = None
                config["activo"] = False
                logging.info(f"✅ {nombre} detenido")
                
        except Exception as e:
            logging.error(f"Error deteniendo {nombre}: {e}")
    
    def verificar_dashboard(self, nombre, config):
        """Verificar si un dashboard está funcionando correctamente"""
        try:
            if not config["activo"]:
                return False
            
            if config["proceso"] is None:
                config["activo"] = False
                return False
            
            # Verificar si el proceso sigue ejecutándose
            if config["proceso"].poll() is not None:
                logging.warning(f"⚠️ {nombre} se detuvo inesperadamente")
                config["activo"] = False
                return False
            
            # Verificar si el puerto está respondiendo
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            resultado = sock.connect_ex(('localhost', config["puerto"]))
            sock.close()
            
            if resultado != 0:
                logging.warning(f"⚠️ {nombre} no responde en puerto {config['puerto']}")
                config["activo"] = False
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error verificando {nombre}: {e}")
            config["activo"] = False
            return False
    
    def reiniciar_dashboard(self, nombre, config):
        """Reiniciar un dashboard que no esté funcionando"""
        logging.info(f"🔄 Reiniciando {nombre}...")
        self.detener_dashboard(nombre, config)
        time.sleep(2)
        return self.iniciar_dashboard(nombre, config)
    
    def monitorear_dashboards(self):
        """Hilo de monitoreo continuo de todos los dashboards"""
        logging.info("🔍 Iniciando monitoreo de dashboards...")
        
        while self.monitoreo_activo:
            try:
                for nombre, config in self.dashboards.items():
                    if not self.verificar_dashboard(nombre, config):
                        if config["activo"]:  # Si estaba activo pero falló
                            logging.warning(f"🔄 Dashboard {nombre} falló, intentando reiniciar...")
                            self.reiniciar_dashboard(nombre, config)
                        else:  # Si no estaba activo, intentar iniciarlo
                            logging.info(f"🚀 Intentando iniciar {nombre}...")
                            self.iniciar_dashboard(nombre, config)
                
                time.sleep(self.intervalo_verificacion)
                
            except Exception as e:
                logging.error(f"Error en monitoreo: {e}")
                time.sleep(self.intervalo_verificacion)
    
    def iniciar_todos_dashboards(self):
        """Iniciar todos los dashboards disponibles"""
        logging.info("🚀 Iniciando todos los dashboards del sistema METGO...")
        
        dashboards_iniciados = 0
        for nombre, config in self.dashboards.items():
            if self.iniciar_dashboard(nombre, config):
                dashboards_iniciados += 1
                time.sleep(2)  # Pausa entre inicios
        
        logging.info(f"✅ {dashboards_iniciados}/{len(self.dashboards)} dashboards iniciados")
        return dashboards_iniciados
    
    def detener_todos_dashboards(self):
        """Detener todos los dashboards"""
        logging.info("🛑 Deteniendo todos los dashboards...")
        
        for nombre, config in self.dashboards.items():
            self.detener_dashboard(nombre, config)
        
        logging.info("✅ Todos los dashboards detenidos")
    
    def mostrar_estado(self):
        """Mostrar estado actual de todos los dashboards"""
        print("\n" + "="*80)
        print("🌤️ ESTADO DEL SISTEMA METGO_3D - DASHBOARDS")
        print("="*80)
        print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-"*80)
        
        dashboards_activos = 0
        for nombre, config in self.dashboards.items():
            estado = "🟢 ACTIVO" if config["activo"] else "🔴 INACTIVO"
            puerto = config["puerto"]
            archivo = config["archivo"]
            
            print(f"{nombre:20} | {estado:12} | Puerto: {puerto:4} | {archivo}")
            
            if config["activo"]:
                dashboards_activos += 1
        
        print("-"*80)
        print(f"📊 RESUMEN: {dashboards_activos}/{len(self.dashboards)} dashboards activos")
        
        if dashboards_activos > 0:
            print("\n🌐 ACCESO A DASHBOARDS:")
            print("-"*50)
            for nombre, config in self.dashboards.items():
                if config["activo"]:
                    print(f"🔗 {nombre}: http://localhost:{config['puerto']}")
        
        print("="*80)
    
    def ejecutar_comando_interactivo(self, comando):
        """Ejecutar comandos interactivos"""
        comando = comando.lower().strip()
        
        if comando in ['estado', 'status']:
            self.mostrar_estado()
            
        elif comando in ['iniciar', 'start']:
            dashboards_iniciados = self.iniciar_todos_dashboards()
            print(f"\n✅ {dashboards_iniciados} dashboards iniciados")
            
        elif comando in ['detener', 'stop']:
            self.detener_todos_dashboards()
            print("\n✅ Todos los dashboards detenidos")
            
        elif comando in ['reiniciar', 'restart']:
            self.detener_todos_dashboards()
            time.sleep(3)
            dashboards_iniciados = self.iniciar_todos_dashboards()
            print(f"\n🔄 Sistema reiniciado: {dashboards_iniciados} dashboards activos")
            
        elif comando in ['ayuda', 'help']:
            print("\n📋 COMANDOS DISPONIBLES:")
            print("-"*30)
            print("estado/status    - Mostrar estado de dashboards")
            print("iniciar/start    - Iniciar todos los dashboards")
            print("detener/stop     - Detener todos los dashboards")
            print("reiniciar/restart - Reiniciar sistema completo")
            print("ayuda/help       - Mostrar esta ayuda")
            print("salir/exit       - Salir del sistema")
            
        elif comando in ['salir', 'exit', 'quit']:
            print("\n👋 Cerrando sistema METGO...")
            return False
            
        else:
            print(f"\n❌ Comando desconocido: {comando}")
            print("Escribe 'ayuda' para ver comandos disponibles")
        
        return True
    
    def ejecutar_modo_interactivo(self):
        """Ejecutar en modo interactivo"""
        print("\n🌤️ SISTEMA PERMANENTE METGO_3D")
        print("="*50)
        print("Sistema de monitoreo y gestión de dashboards")
        print("Escribe 'ayuda' para ver comandos disponibles")
        print("-"*50)
        
        # Iniciar monitoreo en hilo separado
        hilo_monitoreo = threading.Thread(target=self.monitorear_dashboards, daemon=True)
        hilo_monitoreo.start()
        
        # Iniciar dashboards automáticamente
        self.iniciar_todos_dashboards()
        
        # Bucle interactivo
        while True:
            try:
                comando = input("\n🔧 METGO> ").strip()
                if not self.ejecutar_comando_interactivo(comando):
                    break
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupción detectada. Cerrando sistema...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        # Limpiar al salir
        self.monitoreo_activo = False
        self.detener_todos_dashboards()
        print("\n✅ Sistema METGO cerrado correctamente")

def main():
    """Función principal"""
    try:
        sistema = SistemaPermanenteMETGO()
        sistema.crear_directorio_logs()
        
        # Verificar argumentos de línea de comandos
        if len(sys.argv) > 1:
            comando = sys.argv[1].lower()
            
            if comando == 'iniciar':
                dashboards_iniciados = sistema.iniciar_todos_dashboards()
                print(f"✅ {dashboards_iniciados} dashboards iniciados")
                
                # Mantener ejecutándose
                sistema.monitoreo_activo = True
                hilo_monitoreo = threading.Thread(target=sistema.monitorear_dashboards, daemon=True)
                hilo_monitoreo.start()
                
                print("🔍 Sistema de monitoreo activo. Presiona Ctrl+C para detener.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    sistema.monitoreo_activo = False
                    sistema.detener_todos_dashboards()
                    
            elif comando == 'estado':
                sistema.mostrar_estado()
            else:
                print("Comandos disponibles: iniciar, estado")
        else:
            # Modo interactivo
            sistema.ejecutar_modo_interactivo()
            
    except Exception as e:
        logging.error(f"Error en sistema principal: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
