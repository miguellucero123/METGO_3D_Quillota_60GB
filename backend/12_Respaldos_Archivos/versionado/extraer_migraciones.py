#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXTRAER MIGRACIONES DE CHATS - METGO 3D
"""

from pathlib import Path
from datetime import datetime

def extraer_migraciones():
    """Extraer conversaciones sobre migración de los chats"""
    print("EXTRAYENDO CONVERSACIONES SOBRE MIGRACIÓN")
    print("="*50)
    
    # Archivos de chat
    archivos_chat = [
        'cursor_revisar_la_carpeta_proyecto_metg.md',
        'cursor_revisar_la_carpeta_proyecto_metg0.md'
    ]
    
    terminos_migracion = [
        'migraci', 'migrar', 'migration', 'disco', 'nube', 
        'exportar', 'transferir', 'mover', 'copiar'
    ]
    
    todas_las_migraciones = []
    
    for archivo_nombre in archivos_chat:
        archivo_path = Path(archivo_nombre)
        
        if not archivo_path.exists():
            print(f"Archivo no encontrado: {archivo_nombre}")
            continue
        
        print(f"\nProcesando: {archivo_nombre}")
        
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            lineas = contenido.split('\n')
            migraciones_archivo = []
            
            for i, linea in enumerate(lineas, 1):
                for termino in terminos_migracion:
                    if termino.lower() in linea.lower():
                        migraciones_archivo.append({
                            'archivo': archivo_nombre,
                            'linea': i,
                            'contenido': linea.strip()
                        })
                        break
            
            print(f"  Encontradas {len(migraciones_archivo)} líneas sobre migración")
            todas_las_migraciones.extend(migraciones_archivo)
            
        except Exception as e:
            print(f"  Error procesando {archivo_nombre}: {e}")
    
    # Mostrar resultados
    print(f"\nTOTAL DE CONVERSACIONES SOBRE MIGRACIÓN: {len(todas_las_migraciones)}")
    print("="*60)
    
    for i, migracion in enumerate(todas_las_migraciones[:30], 1):
        print(f"{i:2d}. [{migracion['archivo']}:{migracion['linea']}] {migracion['contenido']}")
    
    if len(todas_las_migraciones) > 30:
        print(f"\n... y {len(todas_las_migraciones) - 30} conversaciones más")
    
    # Guardar en archivo
    if todas_las_migraciones:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_salida = f"migraciones_extraidas_{timestamp}.txt"
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write("CONVERSACIONES SOBRE MIGRACIÓN - METGO 3D\n")
                f.write("="*50 + "\n")
                f.write(f"Fecha de extracción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de conversaciones: {len(todas_las_migraciones)}\n")
                f.write("="*50 + "\n\n")
                
                for migracion in todas_las_migraciones:
                    f.write(f"[{migracion['archivo']}:{migracion['linea']}] {migracion['contenido']}\n")
            
            print(f"\n✅ Extracción guardada en: {archivo_salida}")
            
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")
    
    return todas_las_migraciones

if __name__ == "__main__":
    extraer_migraciones()
