#!/usr/bin/env python3
"""
Script para forzar la actualización de datos en el dashboard meteorológico
"""

import sqlite3
import pandas as pd
from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
from datetime import datetime

def actualizar_datos_dashboard():
    print("="*60)
    print("ACTUALIZANDO DATOS DEL DASHBOARD METEOROLOGICO")
    print("="*60)
    
    # 1. Limpiar base de datos existente
    db_path = "datos_meteorologicos.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Limpiando datos existentes...")
    cursor.execute("DELETE FROM datos_meteorologicos")
    conn.commit()
    print("[OK] Datos anteriores eliminados")
    
    # 2. Obtener datos frescos de la API
    print("\nObteniendo datos frescos de la API...")
    conector = ConectorAPIsMeteorologicas()
    datos_obtenidos = conector.obtener_datos_todas_estaciones(dias=1)
    
    if datos_obtenidos and 'datos_combinados' in datos_obtenidos:
        df_combinado = datos_obtenidos['datos_combinados']
        print(f"[OK] Datos frescos obtenidos: {len(df_combinado)} registros")
        
        # 3. Insertar datos frescos
        print("\nInsertando datos frescos...")
        registros_insertados = 0
        
        for _, fila in df_combinado.iterrows():
            # Mapear las columnas correctamente
            temperatura = fila.get('temperatura', None)
            humedad = fila.get('humedad_relativa', None)
            presion = fila.get('presion_atmosferica', None)
            precipitacion = fila.get('precipitacion', None)
            velocidad_viento = fila.get('velocidad_viento', None)
            direccion_viento = fila.get('direccion_viento', None)
            nubosidad = fila.get('nubosidad', None)
            indice_uv = fila.get('radiacion_solar', None)
            
            # Obtener nombre de estación y fecha
            estacion = fila.get('estacion', 'Estacion Desconocida')
            fecha = str(fila.get('fecha', datetime.now()))
            
            # Insertar en la base de datos
            cursor.execute('''
                INSERT INTO datos_meteorologicos 
                (estacion, fecha, temperatura, humedad, presion, precipitacion, 
                 velocidad_viento, direccion_viento, nubosidad, indice_uv)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estacion, fecha, temperatura, humedad, presion, precipitacion,
                velocidad_viento, direccion_viento, nubosidad, indice_uv
            ))
            
            registros_insertados += 1
        
        conn.commit()
        print(f"[OK] {registros_insertados} registros frescos insertados")
        
        # 4. Verificar datos por estación
        print("\nVerificando datos por estación...")
        cursor.execute("SELECT estacion, COUNT(*) as count FROM datos_meteorologicos GROUP BY estacion")
        estaciones = cursor.fetchall()
        
        for estacion, count in estaciones:
            cursor.execute("SELECT humedad, presion, precipitacion FROM datos_meteorologicos WHERE estacion = ? LIMIT 1", (estacion,))
            sample = cursor.fetchone()
            print(f"  {estacion}: {count} registros - Humedad: {sample[0]}, Presion: {sample[1]}, Precipitacion: {sample[2]}")
        
    else:
        print("[ERROR] No se pudieron obtener datos frescos")
    
    conn.close()
    
    print("\n" + "="*60)
    print("ACTUALIZACION COMPLETADA")
    print("="*60)
    print("Ahora recarga el dashboard en el navegador para ver los datos actualizados.")

if __name__ == "__main__":
    actualizar_datos_dashboard()


