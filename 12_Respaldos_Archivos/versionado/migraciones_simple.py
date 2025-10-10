#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRACIONES SIMPLE - METGO 3D
"""

import os
from pathlib import Path

def buscar_migraciones():
    """Buscar migraciones en los archivos de chat"""
    
    # Archivos de chat
    archivos = [
        'cursor_revisar_la_carpeta_proyecto_metg.md',
        'cursor_revisar_la_carpeta_proyecto_metg0.md'
    ]
    
    terminos = ['migraci', 'migrar', 'disco', 'nube', 'exportar']
    
    print("BUSCANDO MIGRACIONES...")
    print("="*40)
    
    total_encontradas = 0
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"\nArchivo: {archivo}")
            
            try:
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    lineas = f.readlines()
                
                encontradas = 0
                
                for i, linea in enumerate(lineas, 1):
                    for termino in terminos:
                        if termino.lower() in linea.lower():
                            encontradas += 1
                            total_encontradas += 1
                            
                            # Mostrar solo las primeras 10 por archivo
                            if encontradas <= 10:
                                print(f"  Linea {i}: {linea.strip()[:100]}...")
                            break
                
                print(f"  Total encontradas: {encontradas}")
                
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"Archivo no encontrado: {archivo}")
    
    print(f"\nTOTAL DE MIGRACIONES ENCONTRADAS: {total_encontradas}")
    
    # Crear archivo de resumen
    crear_resumen_migraciones(archivos, terminos)

def crear_resumen_migraciones(archivos, terminos):
    """Crear archivo de resumen de migraciones"""
    
    print("\nCreando archivo de resumen...")
    
    with open('resumen_migraciones.txt', 'w', encoding='utf-8') as f:
        f.write("RESUMEN DE MIGRACIONES - METGO 3D\n")
        f.write("="*50 + "\n\n")
        
        for archivo in archivos:
            if os.path.exists(archivo):
                f.write(f"ARCHIVO: {archivo}\n")
                f.write("-" * 30 + "\n")
                
                try:
                    with open(archivo, 'r', encoding='utf-8', errors='ignore') as file:
                        lineas = file.readlines()
                    
                    for i, linea in enumerate(lineas, 1):
                        for termino in terminos:
                            if termino.lower() in linea.lower():
                                f.write(f"Linea {i}: {linea.strip()}\n")
                                break
                    
                    f.write("\n")
                    
                except Exception as e:
                    f.write(f"Error leyendo archivo: {e}\n\n")
    
    print("Archivo creado: resumen_migraciones.txt")

if __name__ == "__main__":
    buscar_migraciones()
