"""
INICIAR SISTEMA SIMPLE - METGO 3D QUILLOTA
Script sin emojis para evitar problemas de codificacion en Windows
"""

import subprocess
import sys
import os
import time
import webbrowser
from datetime import datetime

class IniciadorSistemaSimple:
    def __init__(self):
        self.puerto_autenticacion = 8500
        self.puerto_central = 8509
        self.procesos = {}
        
    def iniciar_autenticacion(self):
        """Iniciar sistema de autenticacion"""
        try:
            print("[SISTEMA] Iniciando Sistema de Autenticacion...")
            
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
            
            print(f"[OK] Sistema de Autenticacion iniciado en puerto {self.puerto_autenticacion}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error iniciando autenticacion: {e}")
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
        
        # Iniciar autenticacion
        if not self.iniciar_autenticacion():
            return False
        
        time.sleep(3)  # Esperar a que inicie
        
        # Iniciar dashboard central
        if not self.iniciar_dashboard_central():
            return False
        
        time.sleep(3)  # Esperar a que inicie
        
        # Mostrar informacion del sistema
        print("\n" + "="*70)
        print("SISTEMA INICIADO EXITOSAMENTE")
        print("="*70)
        
        print("\n[WEB] ACCESO AL SISTEMA:")
        print(f"   [AUTH] Autenticacion: http://localhost:{self.puerto_autenticacion}")
        print(f"   [CENTRAL] Dashboard Central: http://localhost:{self.puerto_central}")
        
        print("\n[USERS] USUARIOS DE PRUEBA:")
        print("   [ADMIN] Administrador: admin / admin123")
        print("   [EXEC] Ejecutivo: ejecutivo / ejecutivo123")
        print("   [AGRI] Agricultor: agricultor / agricultor123")
        print("   [TECH] Tecnico: tecnico / tecnico123")
        print("   [USER] Usuario: usuario / usuario123")
        
        print("\n[INFO] INSTRUCCIONES:")
        print("   1. Abre tu navegador")
        print("   2. Ve a http://localhost:8500 (Autenticacion)")
        print("   3. Inicia sesion con cualquier usuario de prueba")
        print("   4. Desde el dashboard central, inicia los modulos que necesites")
        print("   5. Cada modulo se abrira en su propio puerto")
        
        print("\n[MODULES] MODULOS DISPONIBLES:")
        print("   [EMP] Dashboard Empresarial (Puerto 8503)")
        print("   [AGRI] Dashboard Agricola (Puerto 8501)")
        print("   [MET] Dashboard Meteorologico (Puerto 8502)")
        print("   [DRONE] Dashboard con Drones (Puerto 8504)")
        print("   [ECON] Sistema Economico (Puerto 8506)")
        print("   [INT] Sistema de Integracion (Puerto 8507)")
        print("   [REP] Reportes Avanzados (Puerto 8508)")
        
        print("\n[CTRL] CONTROL DEL SISTEMA:")
        print("   - Presiona Ctrl+C para detener todos los procesos")
        print("   - El sistema se actualiza automaticamente")
        print("   - Los dashboards se pueden iniciar/detener individualmente")
        
        # Intentar abrir navegador automaticamente
        try:
            print(f"\n[BROWSER] Abriendo navegador en http://localhost:{self.puerto_autenticacion}...")
            webbrowser.open(f"http://localhost:{self.puerto_autenticacion}")
        except:
            print("   (No se pudo abrir automaticamente - abre manualmente)")
        
        return True
    
    def monitorear_sistema(self):
        """Monitorear el sistema en ejecucion"""
        try:
            print("\n[INFO] Sistema en ejecucion. Presiona Ctrl+C para detener...")
            
            while True:
                # Verificar que los procesos esten activos
                procesos_activos = 0
                
                for nombre, proceso in list(self.procesos.items()):
                    if proceso.poll() is None:  # Proceso activo
                        procesos_activos += 1
                    else:
                        print(f"[WARNING] Proceso {nombre} termino inesperadamente")
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
    """Funcion principal"""
    iniciador = IniciadorSistemaSimple()
    
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


