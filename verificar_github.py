#!/usr/bin/env python3
"""
Script para verificar que todos los archivos estén listos para GitHub
"""

import os
import sys

def verificar_archivos_requeridos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_requeridos = [
        'sistema_auth_dashboard_principal_metgo.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        '.streamlit/config.toml'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    return archivos_faltantes

def verificar_archivos_opcionales():
    """Verifica archivos opcionales"""
    archivos_opcionales = [
        'LICENSE',
        '.streamlit/secrets.toml.example',
        'dashboard_meteorologico_metgo.py',
        'dashboard_agricola_metgo.py',
        'dashboard_unificado_metgo.py',
        'dashboard_simple_metgo.py'
    ]
    
    archivos_presentes = []
    
    for archivo in archivos_opcionales:
        if os.path.exists(archivo):
            archivos_presentes.append(archivo)
    
    return archivos_presentes

def verificar_requirements():
    """Verifica que requirements.txt tenga las dependencias necesarias"""
    try:
        with open('requirements.txt', 'r') as f:
            contenido = f.read()
        
        dependencias_requeridas = [
            'streamlit',
            'plotly',
            'pandas',
            'numpy'
        ]
        
        dependencias_faltantes = []
        
        for dep in dependencias_requeridas:
            if dep not in contenido:
                dependencias_faltantes.append(dep)
        
        return dependencias_faltantes
    
    except FileNotFoundError:
        return ['requirements.txt no encontrado']

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("VERIFICACION DE ARCHIVOS PARA GITHUB")
    print("=" * 60)
    
    # Verificar archivos requeridos
    print("\n1. Verificando archivos requeridos...")
    archivos_faltantes = verificar_archivos_requeridos()
    
    if archivos_faltantes:
        print("❌ ARCHIVOS FALTANTES:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print("\n⚠️  Debes crear estos archivos antes de subir a GitHub")
        return False
    else:
        print("[OK] Todos los archivos requeridos estan presentes")
    
    # Verificar dependencias
    print("\n2. Verificando dependencias en requirements.txt...")
    deps_faltantes = verificar_requirements()
    
    if deps_faltantes:
        print("❌ DEPENDENCIAS FALTANTES:")
        for dep in deps_faltantes:
            print(f"   - {dep}")
        print("\n⚠️  Agrega estas dependencias a requirements.txt")
        return False
    else:
        print("[OK] Todas las dependencias estan presentes")
    
    # Verificar archivos opcionales
    print("\n3. Archivos opcionales presentes:")
    archivos_opcionales = verificar_archivos_opcionales()
    
    if archivos_opcionales:
        for archivo in archivos_opcionales:
            print(f"   [OK] {archivo}")
    else:
        print("   (Ningún archivo opcional presente)")
    
    # Verificar tamaño del proyecto
    print("\n4. Información del proyecto:")
    
    archivos_python = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"   Archivos Python: {len(archivos_python)}")
    
    # Verificar archivo principal
    if os.path.exists('sistema_auth_dashboard_principal_metgo.py'):
        size = os.path.getsize('sistema_auth_dashboard_principal_metgo.py')
        print(f"   Tamano del dashboard principal: {size:,} bytes")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE VERIFICACION")
    print("=" * 60)
    
    if not archivos_faltantes and not deps_faltantes:
        print("[LISTO] PROYECTO LISTO PARA GITHUB!")
        print("\nPasos siguientes:")
        print("1. Abre GitHub Desktop")
        print("2. Crea un nuevo repositorio o selecciona uno existente")
        print("3. Agrega todos los archivos")
        print("4. Haz commit con el mensaje: 'Dashboard METGO - Sistema integrado'")
        print("5. Push al repositorio")
        print("6. Ve a https://share.streamlit.io para deployar")
        print("\n[EXITO] Tu dashboard estara en linea en minutos!")
        return True
    else:
        print("[ERROR] PROYECTO NO ESTA LISTO")
        print("Corrige los errores antes de subir a GitHub")
        return False

if __name__ == "__main__":
    main()
