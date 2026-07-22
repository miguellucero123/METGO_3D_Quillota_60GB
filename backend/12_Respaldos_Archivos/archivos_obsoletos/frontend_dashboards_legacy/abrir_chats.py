#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABRIR CHATS EXPORTADOS - METGO 3D
Version simplificada para abrir chats exportados
"""

import os
from pathlib import Path
from datetime import datetime

def listar_archivos_chat():
    """Listar archivos de chat disponibles"""
    print("ARCHIVOS DE CHAT DISPONIBLES")
    print("="*50)
    
    # Buscar archivos de chat
    patrones = ["cursor_*.md", "*chat*.md", "*conversacion*.md"]
    archivos = []
    
    for patron in patrones:
        for archivo in Path.cwd().glob(patron):
            if archivo.is_file():
                tamaño = archivo.stat().st_size / (1024**2)
                fecha = datetime.fromtimestamp(archivo.stat().st_mtime)
                archivos.append({
                    'nombre': archivo.name,
                    'ruta': str(archivo),
                    'tamaño_mb': tamaño,
                    'fecha': fecha
                })
    
    # Ordenar por fecha
    archivos.sort(key=lambda x: x['fecha'], reverse=True)
    
    for i, archivo in enumerate(archivos, 1):
        print(f"{i}. {archivo['nombre']}")
        print(f"   Tamaño: {archivo['tamaño_mb']:.2f} MB")
        print(f"   Fecha: {archivo['fecha'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Ruta: {archivo['ruta']}")
        print()
    
    return archivos

def abrir_archivo_chat(archivo):
    """Abrir archivo de chat específico"""
    print(f"\nABRIENDO: {archivo['nombre']}")
    print("="*60)
    
    try:
        with open(archivo['ruta'], 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        lineas = contenido.split('\n')
        print(f"Total de líneas: {len(lineas)}")
        print(f"Tamaño: {archivo['tamaño_mb']:.2f} MB")
        print("\nPRIMERAS 30 LÍNEAS:")
        print("-"*40)
        
        for i, linea in enumerate(lineas[:30], 1):
            print(f"{i:3d}: {linea}")
        
        if len(lineas) > 30:
            print(f"\n... y {len(lineas) - 30} líneas más")
        
        return contenido
        
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None

def buscar_en_chat(contenido, termino):
    """Buscar término en el contenido del chat"""
    if not contenido:
        return
    
    lineas = contenido.split('\n')
    coincidencias = []
    
    for i, linea in enumerate(lineas, 1):
        if termino.lower() in linea.lower():
            coincidencias.append((i, linea))
    
    if coincidencias:
        print(f"\nENCONTRADAS {len(coincidencias)} COINCIDENCIAS:")
        print("-"*50)
        
        for i, (num_linea, linea) in enumerate(coincidencias[:20], 1):
            print(f"{i:2d}. Línea {num_linea}: {linea}")
        
        if len(coincidencias) > 20:
            print(f"\n... y {len(coincidencias) - 20} coincidencias más")
    else:
        print(f"No se encontraron coincidencias para '{termino}'")

def extraer_migraciones(contenido):
    """Extraer conversaciones sobre migraciones"""
    if not contenido:
        return
    
    terminos_migracion = ['migraci', 'migrar', 'migration', 'disco', 'nube', 'exportar']
    lineas = contenido.split('\n')
    lineas_migracion = []
    
    for i, linea in enumerate(lineas, 1):
        for termino in terminos_migracion:
            if termino.lower() in linea.lower():
                lineas_migracion.append((i, linea))
                break
    
    if lineas_migracion:
        print(f"\nCONVERSACIONES SOBRE MIGRACIÓN ({len(lineas_migracion)} líneas):")
        print("="*60)
        
        for num_linea, linea in lineas_migracion[:30]:
            print(f"{num_linea:4d}: {linea}")
        
        if len(lineas_migracion) > 30:
            print(f"\n... y {len(lineas_migracion) - 30} líneas más")
        
        # Guardar extracción
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_salida = f"migraciones_extraidas_{timestamp}.txt"
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write("CONVERSACIONES SOBRE MIGRACIÓN\n")
            f.write("="*50 + "\n\n")
            for num_linea, linea in lineas_migracion:
                f.write(f"{num_linea:4d}: {linea}\n")
        
        print(f"\nExtracción guardada en: {archivo_salida}")
    else:
        print("No se encontraron conversaciones sobre migración")

def main():
    """Función principal"""
    print("ABRIR CHATS EXPORTADOS - METGO 3D")
    print("="*50)
    
    # Listar archivos
    archivos = listar_archivos_chat()
    
    if not archivos:
        print("No se encontraron archivos de chat")
        return
    
    print("OPCIONES:")
    print("1. Abrir archivo completo")
    print("2. Buscar en archivos")
    print("3. Extraer conversaciones sobre migración")
    print("4. Salir")
    
    try:
        opcion = input("\nSeleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            # Abrir archivo completo
            try:
                num_archivo = int(input(f"Seleccione archivo (1-{len(archivos)}): ")) - 1
                if 0 <= num_archivo < len(archivos):
                    abrir_archivo_chat(archivos[num_archivo])
                else:
                    print("Número inválido")
            except ValueError:
                print("Por favor ingrese un número válido")
        
        elif opcion == "2":
            # Buscar en archivos
            termino = input("Ingrese término a buscar: ").strip()
            if termino:
                for archivo in archivos:
                    print(f"\n--- BUSCANDO EN: {archivo['nombre']} ---")
                    with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    buscar_en_chat(contenido, termino)
        
        elif opcion == "3":
            # Extraer migraciones
            for archivo in archivos:
                print(f"\n--- EXTRAYENDO MIGRACIONES DE: {archivo['nombre']} ---")
                with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                extraer_migraciones(contenido)
        
        elif opcion == "4":
            print("Saliendo...")
        
        else:
            print("Opción inválida")
    
    except KeyboardInterrupt:
        print("\nSaliendo...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
