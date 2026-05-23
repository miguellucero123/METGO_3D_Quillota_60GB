#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas con los datos meteorológicos
"""

import sqlite3
import pandas as pd
from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
import os

def diagnosticar_problema():
    print("="*60)
    print("DIAGNÓSTICO DE DATOS METEOROLÓGICOS")
    print("="*60)
    
    # 1. Verificar si existe la base de datos
    db_path = "datos_meteorologicos.db"
    print(f"\n1. Verificando base de datos: {db_path}")
    
    if os.path.exists(db_path):
        print("[OK] Base de datos existe")
        
        # Verificar estructura de la tabla
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(datos_meteorologicos)")
            columns = cursor.fetchall()
            print("\nEstructura de la tabla:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Verificar datos existentes
            cursor.execute("SELECT COUNT(*) FROM datos_meteorologicos")
            count = cursor.fetchone()[0]
            print(f"\nTotal de registros: {count}")
            
            if count > 0:
                # Mostrar últimos registros
                cursor.execute("SELECT * FROM datos_meteorologicos ORDER BY fecha DESC LIMIT 3")
                rows = cursor.fetchall()
                print("\nUltimos 3 registros:")
                column_names = [description[0] for description in cursor.description]
                print("   Columnas:", column_names)
                for i, row in enumerate(rows, 1):
                    print(f"   Registro {i}: {row}")
                    
        except sqlite3.OperationalError as e:
            print(f"[ERROR] Error en la tabla: {e}")
        
        conn.close()
    else:
        print("[ERROR] Base de datos no existe")
    
    # 2. Probar el conector de APIs
    print(f"\n2. Probando conector de APIs meteorológicas...")
    try:
        conector = ConectorAPIsMeteorologicas()
        print("[OK] Conector inicializado correctamente")
        
        # Obtener datos de una estación
        print("\nObteniendo datos de Quillota Centro...")
        datos = conector.obtener_datos_openmeteo('quillota_centro', 1)
        
        if datos and 'datos' in datos:
            df = datos['datos']
            print(f"[OK] Datos obtenidos: {len(df)} registros")
            print(f"Columnas disponibles: {list(df.columns)}")
            
            # Mostrar primera fila
            if len(df) > 0:
                print(f"\nPrimera fila de datos:")
                primera_fila = df.iloc[0]
                for col, valor in primera_fila.items():
                    print(f"   {col}: {valor} ({type(valor).__name__})")
        else:
            print("[ERROR] No se pudieron obtener datos")
            
    except Exception as e:
        print(f"[ERROR] Error en conector: {e}")
    
    # 3. Probar obtención de datos combinados
    print(f"\n3. Probando datos combinados...")
    try:
        datos_combinados = conector.obtener_datos_todas_estaciones(dias=1)
        
        if datos_combinados and 'datos_combinados' in datos_combinados:
            df_combinado = datos_combinados['datos_combinados']
            print(f"[OK] Datos combinados obtenidos: {len(df_combinado)} registros")
            print(f"Columnas: {list(df_combinado.columns)}")
            
            # Verificar si las columnas esperadas existen
            columnas_esperadas = ['humedad_relativa', 'presion_atmosferica', 'precipitacion']
            for col in columnas_esperadas:
                if col in df_combinado.columns:
                    print(f"[OK] Columna '{col}' encontrada")
                    # Mostrar valores no nulos
                    valores_no_nulos = df_combinado[col].dropna()
                    if len(valores_no_nulos) > 0:
                        print(f"   Valores no nulos: {len(valores_no_nulos)}")
                        print(f"   Rango: {valores_no_nulos.min()} - {valores_no_nulos.max()}")
                    else:
                        print(f"   [WARNING] Todos los valores son nulos")
                else:
                    print(f"[ERROR] Columna '{col}' NO encontrada")
        else:
            print("[ERROR] No se pudieron obtener datos combinados")
            
    except Exception as e:
        print(f"[ERROR] Error en datos combinados: {e}")
    
    print("\n" + "="*60)
    print("DIAGNÓSTICO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    diagnosticar_problema()
