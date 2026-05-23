#!/usr/bin/env python3
"""
Script para probar la inserción de datos meteorológicos
"""

import sqlite3
import pandas as pd
from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
from datetime import datetime

def probar_insercion():
    print("="*60)
    print("PROBANDO INSERCION DE DATOS METEOROLOGICOS")
    print("="*60)
    
    # 1. Crear/limpiar la base de datos
    db_path = "datos_meteorologicos.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Eliminar tabla existente si existe
    cursor.execute("DROP TABLE IF EXISTS datos_meteorologicos")
    
    # Crear tabla nueva
    cursor.execute('''
        CREATE TABLE datos_meteorologicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estacion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            temperatura REAL,
            humedad REAL,
            presion REAL,
            precipitacion REAL,
            velocidad_viento REAL,
            direccion_viento REAL,
            nubosidad REAL,
            indice_uv REAL
        )
    ''')
    
    conn.commit()
    print("[OK] Tabla creada correctamente")
    
    # 2. Obtener datos de la API
    print("\nObteniendo datos de la API...")
    conector = ConectorAPIsMeteorologicas()
    datos_obtenidos = conector.obtener_datos_todas_estaciones(dias=1)
    
    if datos_obtenidos and 'datos_combinados' in datos_obtenidos:
        df_combinado = datos_obtenidos['datos_combinados']
        print(f"[OK] Datos obtenidos: {len(df_combinado)} registros")
        print(f"Columnas: {list(df_combinado.columns)}")
        
        # 3. Insertar datos en la base de datos
        print("\nInsertando datos en la base de datos...")
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
            indice_uv = fila.get('radiacion_solar', None)  # Usar radiación solar como proxy
            
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
        print(f"[OK] {registros_insertados} registros insertados")
        
        # 4. Verificar los datos insertados
        print("\nVerificando datos insertados...")
        cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos")
        count = cursor.fetchone()[0]
        print(f"Total de registros en BD: {count}")
        
        cursor.execute("SELECT * FROM datos_meteorologicos LIMIT 3")
        rows = cursor.fetchall()
        print("\nPrimeros 3 registros:")
        for i, row in enumerate(rows, 1):
            print(f"Registro {i}: {row}")
        
        # 5. Verificar que no hay valores NULL en humedad, presión, etc.
        cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos WHERE humedad IS NOT NULL")
        humedad_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos WHERE presion IS NOT NULL")
        presion_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos WHERE precipitacion IS NOT NULL")
        precipitacion_count = cursor.fetchone()[0]
        
        print(f"\nValores no nulos:")
        print(f"  - Humedad: {humedad_count}/{count}")
        print(f"  - Presion: {presion_count}/{count}")
        print(f"  - Precipitacion: {precipitacion_count}/{count}")
        
    else:
        print("[ERROR] No se pudieron obtener datos de la API")
    
    conn.close()
    print("\n" + "="*60)
    print("PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    probar_insercion()
