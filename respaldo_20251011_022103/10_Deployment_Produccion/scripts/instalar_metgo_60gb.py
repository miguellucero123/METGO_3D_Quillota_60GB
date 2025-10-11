#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

print("INSTALADOR METGO 3D - VERSION 60GB")
print("="*40)

# Instalar dependencias
try:
    print("Instalando dependencias...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    print("OK: Dependencias instaladas")
except Exception as e:
    print(f"ERROR: {e}")

# Crear directorios
directorios = ['data', 'logs', 'config', 'modelos_ml_quillota', 'backups']
for directorio in directorios:
    Path(directorio).mkdir(exist_ok=True)

# Crear .env
env_file = Path('.env')
if not env_file.exists():
    with open(env_file, 'w') as f:
        f.write("# Configuracion METGO 3D\n")
        f.write("OPENWEATHER_API_KEY=tu_clave_aqui\n")
        f.write("NASA_API_KEY=tu_clave_aqui\n")
        f.write("GOOGLE_MAPS_API_KEY=tu_clave_aqui\n")
        f.write("DEBUG=False\n")
        f.write("LOG_LEVEL=INFO\n")
    print("OK: Archivo .env creado")

print("\nOK: INSTALACION COMPLETADA")
print("\nPara iniciar:")
print("python -m streamlit run sistema_unificado_con_conectores.py")
print("\nURL: http://localhost:8501")
print("Usuario: admin")
print("Contrasena: admin123")
