#!/usr/bin/env python3
"""
Script para regenerar datos meteorológicos con resolución horaria
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta

def regenerar_datos_horarios():
    """Regenerar datos meteorológicos con datos cada hora"""
    
    db_path = "datos_meteorologicos.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpiar tabla existente
        print("[INFO] Limpiando datos existentes...")
        cursor.execute("DELETE FROM datos_meteorologicos")
        
        # Generar datos para los últimos 7 días con datos cada hora
        estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
        fecha_base = datetime.now() - timedelta(days=7)
        
        print("[INFO] Generando datos cada hora para 7 dias...")
        total_registros = 0
        
        # Generar datos cada hora para los últimos 7 días
        for i in range(7 * 24):  # 7 días * 24 horas = 168 horas
            fecha = fecha_base + timedelta(hours=i)
            fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
            
            for estacion in estaciones:
                # Simular variación diurna de temperatura
                hora = fecha.hour
                temp_base = 15 + 5 * np.sin(2 * np.pi * (hora - 6) / 24)  # Temperatura que varía según la hora
                
                # Datos realistas para Chile central con variación horaria
                temperatura = temp_base + np.random.normal(0, 1.5)  # Variación alrededor de la temperatura base
                humedad = np.random.normal(70, 10)     # 70% promedio
                presion = np.random.normal(1015, 2)    # 1015 hPa promedio
                precipitacion = np.random.exponential(0.5) if np.random.random() < 0.1 else 0  # Menos probabilidad de lluvia
                velocidad_viento = np.random.exponential(8)  # 8 km/h promedio
                direccion_viento = np.random.uniform(0, 360)
                nubosidad = np.random.uniform(0, 100)
                indice_uv = max(0, min(10, np.random.uniform(0, 8)))  # UV entre 0 y 10
                
                cursor.execute('''
                    INSERT INTO datos_meteorologicos 
                    (estacion, fecha, temperatura, humedad, presion, precipitacion,
                     velocidad_viento, direccion_viento, nubosidad, indice_uv)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (estacion, fecha_str, temperatura, humedad, presion, precipitacion,
                      velocidad_viento, direccion_viento, nubosidad, indice_uv))
                
                total_registros += 1
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Datos regenerados exitosamente!")
        print(f"[INFO] Total de registros: {total_registros}")
        print(f"[INFO] Estaciones: {len(estaciones)}")
        print(f"[INFO] Periodo: 7 dias con datos cada hora")
        print(f"[INFO] Rango de fechas: {fecha_base.strftime('%Y-%m-%d %H:%M')} a {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error regenerando datos: {e}")
        return False

if __name__ == "__main__":
    print("REGENERANDO DATOS METEOROLOGICOS CON RESOLUCION HORARIA")
    print("=" * 60)
    
    if regenerar_datos_horarios():
        print("\n[OK] Regeneracion completada exitosamente!")
        print("[INFO] Ahora puedes usar el dashboard con periodos de 6 horas, 12 horas, etc.")
    else:
        print("\n[ERROR] Error en la regeneracion de datos")
