"""
SCRIPT DE REINICIO DE PRODUCCIÓN - METGO 3D QUILLOTA
Reinicia todos los servicios del sistema
"""

import subprocess
import sys
import os

def reiniciar_produccion():
    """Reiniciar sistema de producción"""
    print("="*60)
    print("REINICIANDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    # Parar sistema
    print("\n[PARANDO] Sistema actual...")
    try:
        subprocess.run([sys.executable, 'parar_produccion.py'], check=True)
    except:
        pass
    
    # Esperar un momento
    import time
    time.sleep(3)
    
    # Iniciar sistema
    print("\n[INICIANDO] Sistema reiniciado...")
    try:
        subprocess.run([sys.executable, 'iniciar_produccion.py'], check=True)
    except Exception as e:
        print(f"  [ERROR] Error reiniciando sistema: {e}")
        return False
    
    print("\n[OK] Sistema reiniciado exitosamente")
    return True

if __name__ == "__main__":
    reiniciar_produccion()
