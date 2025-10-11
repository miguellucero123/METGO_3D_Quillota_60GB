#!/usr/bin/env python3
"""
Sistema METGO - Reinicio Automático
Autor: Sistema METGO
Fecha: 2025-10-10
"""

import subprocess
import time
import sys
from datetime import datetime

def main():
    """Función principal de reinicio"""
    print("=" * 60)
    print("🔄 SISTEMA METGO - REINICIO AUTOMÁTICO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1️⃣ Deteniendo sistema actual...")
    try:
        subprocess.run([sys.executable, "detener_sistema.py"], check=True)
    except subprocess.CalledProcessError:
        print("⚠️  Error al detener el sistema")
    
    print("\n2️⃣ Esperando 5 segundos...")
    time.sleep(5)
    
    print("\n3️⃣ Iniciando sistema...")
    try:
        subprocess.run([sys.executable, "iniciar_sistema_automatico.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error al iniciar el sistema")
        sys.exit(1)
    
    print("\n✅ Sistema METGO reiniciado correctamente")

if __name__ == "__main__":
    main()
