#!/usr/bin/env python3
"""
Script para verificar que los datos se están leyendo correctamente para los gráficos
"""

import sqlite3
import pandas as pd
from datetime import datetime

def verificar_datos_graficos():
    print("="*60)
    print("VERIFICANDO DATOS PARA GRAFICOS")
    print("="*60)
    
    # 1. Verificar datos en la base de datos
    db_path = "datos_meteorologicos.db"
    conn = sqlite3.connect(db_path)
    
    # Obtener todos los datos
    query = '''
        SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
               velocidad_viento, direccion_viento, nubosidad, indice_uv
        FROM datos_meteorologicos
        ORDER BY fecha DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"Total de registros: {len(df)}")
    
    if df.empty:
        print("[ERROR] No hay datos en la base de datos")
        return
    
    # 2. Verificar estructura de datos
    print(f"\nColumnas disponibles: {list(df.columns)}")
    print(f"Tipos de datos:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")
    
    # 3. Verificar datos por estación
    print(f"\nDatos por estación:")
    for estacion in df['estacion'].unique():
        estacion_data = df[df['estacion'] == estacion]
        print(f"  {estacion}: {len(estacion_data)} registros")
        
        # Mostrar muestra de datos
        if len(estacion_data) > 0:
            sample = estacion_data.iloc[0]
            print(f"    Muestra: Temp={sample['temperatura']}, Humedad={sample['humedad']}, Presion={sample['presion']}")
    
    # 4. Verificar fechas
    print(f"\nVerificando fechas:")
    print(f"Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
    
    # Convertir fechas a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    fechas_validas = df.dropna(subset=['fecha'])
    
    print(f"Fechas válidas: {len(fechas_validas)}/{len(df)}")
    
    if len(fechas_validas) > 0:
        print(f"Rango de fechas válidas: {fechas_validas['fecha'].min()} a {fechas_validas['fecha'].max()}")
        
        # 5. Verificar datos para gráficos
        print(f"\nDatos para gráficos:")
        
        # Temperatura
        temp_data = fechas_validas[fechas_validas['temperatura'].notna()]
        print(f"  Temperatura: {len(temp_data)} registros válidos")
        
        # Humedad
        humedad_data = fechas_validas[fechas_validas['humedad'].notna()]
        print(f"  Humedad: {len(humedad_data)} registros válidos")
        
        # Presión
        presion_data = fechas_validas[fechas_validas['presion'].notna()]
        print(f"  Presión: {len(presion_data)} registros válidos")
        
        # Viento
        viento_data = fechas_validas[fechas_validas['velocidad_viento'].notna()]
        print(f"  Viento: {len(viento_data)} registros válidos")
        
        # 6. Mostrar muestra de datos para gráficos
        if len(temp_data) > 0:
            print(f"\nMuestra de datos para gráfico de temperatura:")
            sample_temp = temp_data[['estacion', 'fecha', 'temperatura']].head(3)
            print(sample_temp.to_string(index=False))
        
        if len(humedad_data) > 0:
            print(f"\nMuestra de datos para gráfico de humedad:")
            sample_humedad = humedad_data[['estacion', 'fecha', 'humedad']].head(3)
            print(sample_humedad.to_string(index=False))
        
        if len(presion_data) > 0:
            print(f"\nMuestra de datos para gráfico de presión:")
            sample_presion = presion_data[['estacion', 'fecha', 'presion']].head(3)
            print(sample_presion.to_string(index=False))
    
    print("\n" + "="*60)
    print("VERIFICACION COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    verificar_datos_graficos()


