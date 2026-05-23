"""
INICIADOR DEL ACTUALIZADOR AUTOMÁTICO
METGO 3D Quillota - Sistema de Actualización en Tiempo Real
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def verificar_archivos_necesarios():
    """Verificar que todos los archivos necesarios estén presentes"""
    archivos_requeridos = [
        "actualizador_datos_automatico.py",
        "conector_apis_meteorologicas_reales.py",
        "api_keys_meteorologicas.json"
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("[ERROR] Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"  - {archivo}")
        return False
    
    print("[OK] Todos los archivos necesarios están presentes")
    return True

def crear_directorios():
    """Crear directorios necesarios"""
    directorios = ["logs", "reportes", "alertas"]
    
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"[CREADO] Directorio: {directorio}")

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    try:
        import requests
        import pandas
        import numpy
        import schedule
        print("[OK] Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"[ERROR] Dependencia faltante: {e}")
        print("[SOLUCION] Ejecutar: pip install requests pandas numpy schedule")
        return False

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("=" * 60)
    print("ACTUALIZADOR AUTOMÁTICO DE DATOS METEOROLÓGICOS")
    print("METGO 3D Quillota - Sistema de Actualización en Tiempo Real")
    print("=" * 60)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("OPCIONES DISPONIBLES:")
    print("1. Actualización manual (una vez)")
    print("2. Actualización automática (cada hora)")
    print("3. Verificar estado del sistema")
    print("4. Ver último reporte")
    print("5. Salir")
    print()
    
    while True:
        try:
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            if opcion in ["1", "2", "3", "4", "5"]:
                return opcion
            else:
                print("[ERROR] Opción inválida. Ingresa un número del 1 al 5.")
        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada por el usuario")
            return "5"

def ejecutar_actualizacion_manual():
    """Ejecutar actualización manual"""
    print("[EJECUTANDO] Actualización manual...")
    try:
        result = subprocess.run([
            sys.executable, "actualizador_datos_automatico.py", "manual"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("[OK] Actualización manual completada exitosamente")
            print(result.stdout)
        else:
            print("[ERROR] Error en actualización manual")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("[ERROR] La actualización manual tardó demasiado tiempo")
    except Exception as e:
        print(f"[ERROR] Error ejecutando actualización manual: {e}")

def ejecutar_actualizacion_automatica():
    """Ejecutar actualización automática"""
    print("[EJECUTANDO] Iniciando actualización automática...")
    print("[INFO] El sistema se actualizará cada hora")
    print("[INFO] Presiona Ctrl+C para detener")
    print()
    
    try:
        # Ejecutar en segundo plano
        process = subprocess.Popen([
            sys.executable, "actualizador_datos_automatico.py"
        ])
        
        print(f"[INFO] Proceso iniciado con PID: {process.pid}")
        print("[INFO] El actualizador automático está ejecutándose...")
        
        # Esperar a que el usuario presione Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Deteniendo actualizador automático...")
            process.terminate()
            process.wait()
            print("[INFO] Actualizador automático detenido")
            
    except Exception as e:
        print(f"[ERROR] Error iniciando actualización automática: {e}")

def verificar_estado_sistema():
    """Verificar el estado del sistema"""
    print("[VERIFICANDO] Estado del sistema...")
    
    # Verificar archivos de datos
    archivos_datos = [
        "datos_meteorologicos_actualizados.json",
        "datos_meteorologicos_reales.db"
    ]
    
    for archivo in archivos_datos:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            mtime = datetime.fromtimestamp(os.path.getmtime(archivo))
            print(f"[OK] {archivo}: {size} bytes, modificado: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[FALTANTE] {archivo}")
    
    # Verificar directorios
    directorios = ["logs", "reportes", "alertas"]
    for directorio in directorios:
        if os.path.exists(directorio):
            archivos = os.listdir(directorio)
            print(f"[OK] {directorio}/: {len(archivos)} archivos")
        else:
            print(f"[FALTANTE] {directorio}/")

def ver_ultimo_reporte():
    """Ver el último reporte generado"""
    if not os.path.exists("reportes"):
        print("[ERROR] No hay directorio de reportes")
        return
    
    archivos_reporte = [f for f in os.listdir("reportes") if f.startswith("reporte_actualizacion_")]
    
    if not archivos_reporte:
        print("[INFO] No hay reportes disponibles")
        return
    
    # Ordenar por fecha de modificación
    archivos_reporte.sort(key=lambda x: os.path.getmtime(os.path.join("reportes", x)), reverse=True)
    ultimo_reporte = archivos_reporte[0]
    
    print(f"[REPORTE] Último reporte: {ultimo_reporte}")
    
    try:
        with open(os.path.join("reportes", ultimo_reporte), 'r', encoding='utf-8') as f:
            contenido = f.read()
            print("\n[CONTENIDO]")
            print(contenido[:1000] + "..." if len(contenido) > 1000 else contenido)
    except Exception as e:
        print(f"[ERROR] Error leyendo reporte: {e}")

def main():
    """Función principal"""
    print("Iniciando sistema de actualización automática...")
    print()
    
    # Verificaciones iniciales
    if not verificar_archivos_necesarios():
        return
    
    if not verificar_dependencias():
        return
    
    crear_directorios()
    print()
    
    # Menú principal
    while True:
        opcion = mostrar_menu()
        
        if opcion == "1":
            ejecutar_actualizacion_manual()
        elif opcion == "2":
            ejecutar_actualizacion_automatica()
        elif opcion == "3":
            verificar_estado_sistema()
        elif opcion == "4":
            ver_ultimo_reporte()
        elif opcion == "5":
            print("[INFO] Saliendo del sistema...")
            break
        
        if opcion != "5":
            input("\nPresiona Enter para continuar...")
            print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")



