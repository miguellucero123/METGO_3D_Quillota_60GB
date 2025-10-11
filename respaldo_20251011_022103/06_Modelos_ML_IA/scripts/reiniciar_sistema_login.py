"""
REINICIAR SISTEMA CON LOGIN SIMPLE - METGO 3D QUILLOTA
Script para reiniciar el sistema con el nuevo login simplificado
"""

import subprocess
import sys
import os
import time
import webbrowser

def detener_procesos_anteriores():
    """Detener procesos anteriores"""
    try:
        print("[INFO] Deteniendo procesos anteriores...")
        
        # Buscar y detener procesos de Streamlit en puertos específicos
        puertos = [8500, 8509]
        
        for puerto in puertos:
            try:
                # En Windows, usar taskkill para detener procesos
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                             capture_output=True, text=True)
                print(f"[OK] Procesos en puerto {puerto} detenidos")
            except:
                print(f"[INFO] No hay procesos en puerto {puerto}")
        
        time.sleep(2)
        
    except Exception as e:
        print(f"[INFO] Error deteniendo procesos: {e}")

def iniciar_nuevo_sistema():
    """Iniciar nuevo sistema con login simple"""
    try:
        print("[INFO] Iniciando nuevo sistema con login simple...")
        
        # Verificar que el archivo existe
        archivo_login = "sistema_login_simple_metgo.py"
        if not os.path.exists(archivo_login):
            print(f"[ERROR] Archivo {archivo_login} no encontrado")
            return False
        
        print(f"[OK] Archivo {archivo_login} encontrado")
        
        # Ejecutar con Streamlit
        comando = [sys.executable, "-m", "streamlit", "run", archivo_login, "--server.port", "8500"]
        
        print(f"[EJECUTANDO] {' '.join(comando)}")
        print("[INFO] El sistema se abrira en: http://localhost:8500")
        
        # Ejecutar el comando
        proceso = subprocess.Popen(comando, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        time.sleep(5)  # Esperar a que inicie
        
        print("[OK] Sistema iniciado exitosamente")
        
        # Intentar abrir navegador
        try:
            print("[BROWSER] Abriendo navegador...")
            webbrowser.open("http://localhost:8500")
        except:
            print("[INFO] No se pudo abrir navegador automaticamente")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error iniciando sistema: {e}")
        return False

def main():
    """Funcion principal"""
    print("="*70)
    print("REINICIANDO SISTEMA METGO 3D CON LOGIN SIMPLE")
    print("="*70)
    
    try:
        # Detener procesos anteriores
        detener_procesos_anteriores()
        
        # Iniciar nuevo sistema
        if iniciar_nuevo_sistema():
            print("\n" + "="*70)
            print("SISTEMA REINICIADO EXITOSAMENTE")
            print("="*70)
            
            print("\n[WEB] ACCESO AL SISTEMA:")
            print("   [LOGIN] Sistema de Login: http://localhost:8500")
            
            print("\n[USERS] USUARIOS DE PRUEBA:")
            print("   [ADMIN] admin / admin123")
            print("   [EXEC] ejecutivo / ejecutivo123")
            print("   [AGRI] agricultor / agricultor123")
            print("   [TECH] tecnico / tecnico123")
            print("   [USER] usuario / usuario123")
            
            print("\n[INFO] INSTRUCCIONES:")
            print("   1. Ve a http://localhost:8500")
            print("   2. Inicia sesion con cualquier usuario de prueba")
            print("   3. Selecciona el dashboard que deseas usar")
            print("   4. El sistema te mostrara las URLs de acceso")
            
            print("\n[CTRL] CONTROL DEL SISTEMA:")
            print("   - Presiona Ctrl+C para detener el sistema")
            print("   - El navegador se abrio automaticamente")
            print("   - Usa las credenciales de prueba para acceder")
            
            # Mantener el proceso activo
            try:
                print("\n[INFO] Sistema ejecutandose. Presiona Ctrl+C para detener...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[INFO] Sistema detenido por el usuario")
        
        else:
            print("[ERROR] No se pudo reiniciar el sistema")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()


