"""
EJECUTAR SISTEMA DE AUTENTICACIÓN - METGO 3D QUILLOTA
Script para ejecutar el sistema de autenticación con Streamlit
"""

import subprocess
import sys
import os
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from _deprecated_notice import warn_if_deprecated


def ejecutar_sistema_autenticacion():
    warn_if_deprecated(__file__, "streamlit run streamlit_app.py (raíz del repo)")
    """Ejecutar sistema de autenticación"""
    try:
        print("="*60)
        print("INICIANDO SISTEMA DE AUTENTICACIÓN METGO 3D")
        print("="*60)
        
        # Verificar que el archivo existe
        archivo_auth = "sistema_autenticacion_metgo.py"
        if not os.path.exists(archivo_auth):
            print(f"[ERROR] Archivo {archivo_auth} no encontrado")
            return False
        
        print(f"[OK] Archivo {archivo_auth} encontrado")
        
        # Ejecutar con Streamlit
        comando = [sys.executable, "-m", "streamlit", "run", archivo_auth, "--server.port", "8500"]
        
        print(f"[EJECUTANDO] {' '.join(comando)}")
        print("[INFO] El sistema se abrirá en: http://localhost:8500")
        print("[INFO] Usuarios de prueba disponibles:")
        print("  - Admin: admin / admin123")
        print("  - Ejecutivo: ejecutivo / ejecutivo123") 
        print("  - Agricultor: agricultor / CHANGE_ME_DEMO_AGRICULTOR")
        print("  - Técnico: tecnico / tecnico123")
        print("  - Usuario: usuario / usuario123")
        print("="*60)
        
        # Ejecutar el comando
        subprocess.run(comando)
        
    except KeyboardInterrupt:
        print("\n[INFO] Sistema detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error ejecutando sistema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    ejecutar_sistema_autenticacion()
