"""
SCRIPT DE PARADA DE PRODUCCIÓN - METGO 3D QUILLOTA
Detiene todos los servicios del sistema
"""

import os
import subprocess
import signal
import sys

def parar_produccion():
    """Parar sistema de producción"""
    print("="*60)
    print("DETENIENDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    # Buscar procesos de Streamlit
    try:
        # En Windows
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'streamlit' in result.stdout.lower():
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], check=False)
        else:
            # En Linux/Mac
            subprocess.run(['pkill', '-f', 'streamlit'], check=False)
        
        print("  [OK] Procesos de Streamlit detenidos")
    except Exception as e:
        print(f"  [ADVERTENCIA] Error deteniendo procesos: {e}")
    
    # Buscar procesos específicos del sistema
    procesos_metgo = [
        'sistema_unificado_con_conectores.py',
        'dashboard_agricola_avanzado.py',
        'monitoreo_tiempo_real.py'
    ]
    
    for proceso in procesos_metgo:
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/FI', f'WINDOWTITLE eq {proceso}'], check=False)
            else:
                subprocess.run(['pkill', '-f', proceso], check=False)
            print(f"  [OK] {proceso} detenido")
        except:
            pass
    
    print("\n[OK] Sistema METGO 3D QUILLOTA detenido")
    print("="*60)

if __name__ == "__main__":
    parar_produccion()
