"""
INICIAR SISTEMA COMPLETO - METGO 3D QUILLOTA
Script para iniciar automáticamente el sistema completo con autenticación y dashboard central
"""

import subprocess
import sys
import os
import time
import webbrowser
from datetime import datetime

class IniciadorSistemaCompleto:
    def __init__(self):
        self.puerto_autenticacion = 8500
        self.puerto_central = 8509
        self.procesos = {}
        
    def iniciar_autenticacion(self):
        """Iniciar sistema de autenticación"""
        try:
            print("[SISTEMA] Iniciando Sistema de Autenticación...")
            
            comando = [
                sys.executable, "-m", "streamlit", "run", 
                "sistema_autenticacion_metgo.py", 
                "--server.port", str(self.puerto_autenticacion),
                "--server.headless", "true"
            ]
            
            proceso = subprocess.Popen(comando, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            self.procesos['autenticacion'] = proceso
            
            print(f"[OK] Sistema de Autenticación iniciado en puerto {self.puerto_autenticacion}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error iniciando autenticación: {e}")
            return False
    
    def iniciar_dashboard_central(self):
        """Iniciar dashboard central"""
        try:
            print("[SISTEMA] Iniciando Dashboard Central...")
            
            comando = [
                sys.executable, "-m", "streamlit", "run", 
                "dashboard_central_metgo.py", 
                "--server.port", str(self.puerto_central),
                "--server.headless", "true"
            ]
            
            proceso = subprocess.Popen(comando, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            self.procesos['central'] = proceso
            
            print(f"[OK] Dashboard Central iniciado en puerto {self.puerto_central}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error iniciando dashboard central: {e}")
            return False
    
    def iniciar_sistema_completo(self):
        """Iniciar sistema completo"""
        print("="*70)
        print("INICIANDO SISTEMA COMPLETO METGO 3D QUILLOTA")
        print("="*70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Verificar archivos necesarios
        archivos_necesarios = [
            "sistema_autenticacion_metgo.py",
            "dashboard_central_metgo.py"
        ]
        
        for archivo in archivos_necesarios:
            if not os.path.exists(archivo):
                print(f"[ERROR] Archivo {archivo} no encontrado")
                return False
        
        print("[OK] Todos los archivos necesarios encontrados")
        
        # Iniciar autenticación
        if not self.iniciar_autenticacion():
            return False
        
        time.sleep(3)  # Esperar a que inicie
        
        # Iniciar dashboard central
        if not self.iniciar_dashboard_central():
            return False
        
        time.sleep(3)  # Esperar a que inicie
        
        # Mostrar información del sistema
        print("\n" + "="*70)
        print("SISTEMA INICIADO EXITOSAMENTE")
        print("="*70)
        
        print("\n🌐 ACCESO AL SISTEMA:")
        print(f"   🔐 Autenticación: http://localhost:{self.puerto_autenticacion}")
        print(f"   🎯 Dashboard Central: http://localhost:{self.puerto_central}")
        
        print("\n👥 USUARIOS DE PRUEBA:")
        print("   👑 Administrador: admin / admin123")
        print("   💼 Ejecutivo: ejecutivo / ejecutivo123")
        print("   🌾 Agricultor: agricultor / agricultor123")
        print("   🔧 Técnico: tecnico / tecnico123")
        print("   👤 Usuario: usuario / usuario123")
        
        print("\n💡 INSTRUCCIONES:")
        print("   1. Abre tu navegador")
        print("   2. Ve a http://localhost:8500 (Autenticación)")
        print("   3. Inicia sesión con cualquier usuario de prueba")
        print("   4. Desde el dashboard central, inicia los módulos que necesites")
        print("   5. Cada módulo se abrirá en su propio puerto")
        
        print("\n🚀 MÓDULOS DISPONIBLES:")
        print("   📊 Dashboard Empresarial (Puerto 8503)")
        print("   🌱 Dashboard Agrícola (Puerto 8501)")
        print("   🌤️ Dashboard Meteorológico (Puerto 8502)")
        print("   🚁 Dashboard con Drones (Puerto 8504)")
        print("   💰 Sistema Económico (Puerto 8506)")
        print("   🔗 Sistema de Integración (Puerto 8507)")
        print("   📈 Reportes Avanzados (Puerto 8508)")
        
        print("\n⚙️ CONTROL DEL SISTEMA:")
        print("   - Presiona Ctrl+C para detener todos los procesos")
        print("   - El sistema se actualiza automáticamente")
        print("   - Los dashboards se pueden iniciar/detener individualmente")
        
        # Intentar abrir navegador automáticamente
        try:
            print(f"\n🌐 Abriendo navegador en http://localhost:{self.puerto_autenticacion}...")
            webbrowser.open(f"http://localhost:{self.puerto_autenticacion}")
        except:
            print("   (No se pudo abrir automáticamente - abre manualmente)")
        
        return True
    
    def monitorear_sistema(self):
        """Monitorear el sistema en ejecución"""
        try:
            print("\n[INFO] Sistema en ejecución. Presiona Ctrl+C para detener...")
            
            while True:
                # Verificar que los procesos estén activos
                procesos_activos = 0
                
                for nombre, proceso in list(self.procesos.items()):
                    if proceso.poll() is None:  # Proceso activo
                        procesos_activos += 1
                    else:
                        print(f"[WARNING] Proceso {nombre} terminó inesperadamente")
                        del self.procesos[nombre]
                
                if procesos_activos == 0:
                    print("[ERROR] Todos los procesos han terminado")
                    break
                
                time.sleep(5)  # Verificar cada 5 segundos
                
        except KeyboardInterrupt:
            print("\n[INFO] Deteniendo sistema...")
            self.detener_sistema()
    
    def detener_sistema(self):
        """Detener todos los procesos"""
        print("\n[INFO] Deteniendo todos los procesos...")
        
        for nombre, proceso in self.procesos.items():
            try:
                proceso.terminate()
                print(f"[OK] Proceso {nombre} detenido")
            except:
                print(f"[ERROR] Error deteniendo proceso {nombre}")
        
        self.procesos.clear()
        print("[OK] Sistema detenido completamente")

def main():
    """Función principal"""
    iniciador = IniciadorSistemaCompleto()
    
    try:
        # Iniciar sistema completo
        if iniciador.iniciar_sistema_completo():
            # Monitorear sistema
            iniciador.monitorear_sistema()
        else:
            print("[ERROR] No se pudo iniciar el sistema")
            return False
            
    except KeyboardInterrupt:
        print("\n[INFO] Sistema detenido por el usuario")
        iniciador.detener_sistema()
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        iniciador.detener_sistema()
    
    return True

if __name__ == "__main__":
    main()


