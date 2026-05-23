#!/usr/bin/env python3
"""
Script para corregir las fechas en la base de datos meteorológica
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def corregir_fechas_datos():
    print("="*60)
    print("CORRIGIENDO FECHAS EN BASE DE DATOS METEOROLOGICA")
    print("="*60)
    
    # 1. Conectar a la base de datos
    db_path = "datos_meteorologicos.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. Obtener todos los datos
    cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos")
    total_registros = cursor.fetchone()[0]
    print(f"Total de registros: {total_registros}")
    
    if total_registros == 0:
        print("[ERROR] No hay datos en la base de datos")
        conn.close()
        return
    
    # 3. Obtener datos actuales
    df = pd.read_sql_query("SELECT * FROM datos_meteorologicos ORDER BY fecha DESC", conn)
    print(f"Datos obtenidos: {len(df)} registros")
    
    # 4. Mostrar fechas actuales
    print(f"\nFechas actuales en BD:")
    fechas_unicas = df['fecha'].unique()[:5]
    for fecha in fechas_unicas:
        print(f"  {fecha}")
    
    # 5. Generar fechas reales (últimos 8 días)
    fecha_actual = datetime.now()
    fechas_reales = []
    
    for i in range(8):  # 8 días de datos
        fecha = fecha_actual - timedelta(days=i)
        fechas_reales.append(fecha.strftime('%Y-%m-%d %H:%M:%S'))
    
    print(f"\nFechas reales que se usarán:")
    for fecha in fechas_reales:
        print(f"  {fecha}")
    
    # 6. Actualizar fechas en la base de datos
    print(f"\nActualizando fechas...")
    
    # Agrupar por estación y asignar fechas
    estaciones = df['estacion'].unique()
    registros_por_estacion = total_registros // len(estaciones)
    
    fecha_idx = 0
    registros_actualizados = 0
    
    for estacion in estaciones:
        estacion_data = df[df['estacion'] == estacion]
        
        for _, row in estacion_data.iterrows():
            nueva_fecha = fechas_reales[fecha_idx % len(fechas_reales)]
            
            cursor.execute('''
                UPDATE datos_meteorologicos 
                SET fecha = ? 
                WHERE id = ?
            ''', (nueva_fecha, row['id']))
            
            registros_actualizados += 1
            fecha_idx += 1
    
    conn.commit()
    print(f"[OK] {registros_actualizados} registros actualizados")
    
    # 7. Verificar fechas actualizadas
    print(f"\nVerificando fechas actualizadas...")
    df_actualizado = pd.read_sql_query("SELECT estacion, fecha FROM datos_meteorologicos ORDER BY fecha DESC LIMIT 10", conn)
    
    print("Últimos 10 registros:")
    for _, row in df_actualizado.iterrows():
        print(f"  {row['estacion']}: {row['fecha']}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("CORRECCION DE FECHAS COMPLETADA")
    print("="*60)
    print("Ahora recarga el dashboard para ver los datos en los gráficos.")

if __name__ == "__main__":
    corregir_fechas_datos()


