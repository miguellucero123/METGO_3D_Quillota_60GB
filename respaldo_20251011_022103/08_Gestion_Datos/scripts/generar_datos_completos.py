#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR DE DATOS METEOROLÓGICOS COMPLETOS - METGO 3D
Genera datos sintéticos con todas las variables meteorológicas para Quillota
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def generar_datos_meteorologicos_completos(dias=30):
    """Generar datos meteorológicos completos con todas las variables"""
    
    print("Generando datos meteorologicos completos para Quillota...")
    
    # Generar fechas
    fechas = pd.date_range(
        start=datetime.now() - timedelta(days=dias),
        end=datetime.now(),
        freq='H'
    )
    
    # Configurar semilla para reproducibilidad
    np.random.seed(42)
    
    # Crear DataFrame
    datos = pd.DataFrame(index=fechas)
    
    # 1. TEMPERATURA
    print("   Generando temperaturas...")
    # Patrón estacional para Quillota (clima mediterráneo)
    estacional = 8 * np.sin(2 * np.pi * fechas.dayofyear / 365)
    # Variación diaria
    diaria = 6 * np.sin(2 * np.pi * fechas.hour / 24)
    # Ruido
    ruido = np.random.normal(0, 2, len(fechas))
    
    datos['temperatura'] = 18 + estacional + diaria + ruido
    datos['temperatura_max'] = datos['temperatura'] + np.random.uniform(3, 8, len(fechas))
    datos['temperatura_min'] = datos['temperatura'] - np.random.uniform(3, 8, len(fechas))
    
    # 2. PRECIPITACION
    print("   Generando precipitacion...")
    # Eventos de lluvia esporádicos (más frecuentes en invierno)
    prob_lluvia = 0.05 + 0.03 * np.sin(2 * np.pi * fechas.dayofyear / 365)
    lluvia = np.where(np.random.random(len(fechas)) < prob_lluvia,
                     np.random.exponential(2.0, len(fechas)), 0)
    datos['precipitacion'] = lluvia
    
    # 3. HUMEDAD RELATIVA
    print("   Generando humedad relativa...")
    # Relación inversa con temperatura
    humedad_base = 75 - (datos['temperatura'] - 18) * 1.5
    # Aumentar humedad cuando llueve
    humedad_lluvia = np.where(datos['precipitacion'] > 0, 
                             humedad_base + 15, humedad_base)
    datos['humedad_relativa'] = np.clip(humedad_lluvia + np.random.normal(0, 5, len(fechas)), 0, 100)
    
    # 4. PRESION ATMOSFERICA
    print("   Generando presion atmosferica...")
    # Presión base para Quillota (120m altitud)
    presion_base = 1013.25 - (120 * 0.12)  # Reducción por altitud
    # Variaciones estacionales y de alta/baja presión
    variacion = 10 * np.sin(2 * np.pi * fechas.dayofyear / 365) + np.random.normal(0, 3, len(fechas))
    datos['presion_atmosferica'] = presion_base + variacion
    
    # 5. VIENTO
    print("   Generando datos de viento...")
    # Velocidad del viento (más fuerte en primavera)
    viento_base = 5 + 3 * np.sin(2 * np.pi * fechas.dayofyear / 365)
    datos['velocidad_viento'] = np.maximum(0, viento_base + np.random.gamma(2, 1.5, len(fechas)))
    
    # Dirección del viento (predominante SW en Quillota)
    direcciones = [225, 270, 315]  # SW, W, NW
    pesos = [0.4, 0.3, 0.3]
    datos['direccion_viento'] = np.random.choice(direcciones, len(fechas), p=pesos) + np.random.normal(0, 30, len(fechas))
    datos['direccion_viento'] = datos['direccion_viento'] % 360
    
    # 6. NUBOSIDAD
    print("   Generando nubosidad...")
    # Relacionada con precipitación y humedad
    nubosidad_base = 30 + (datos['humedad_relativa'] - 70) * 0.5
    nubosidad_lluvia = np.where(datos['precipitacion'] > 0, nubosidad_base + 40, nubosidad_base)
    datos['nubosidad'] = np.clip(nubosidad_lluvia + np.random.normal(0, 10, len(fechas)), 0, 100)
    
    # 7. RADIACION SOLAR
    print("   Generando radiacion solar...")
    # Patrón diario (máximo al mediodía)
    radiacion_diaria = 800 * np.sin(np.pi * fechas.hour / 24)
    # Reducir por nubosidad
    factor_nubosidad = (100 - datos['nubosidad']) / 100
    datos['radiacion_solar'] = np.maximum(0, radiacion_diaria * factor_nubosidad + np.random.normal(0, 50, len(fechas)))
    
    # 8. PUNTO DE ROCIO
    print("   Calculando punto de rocio...")
    # Fórmula aproximada
    datos['punto_rocio'] = datos['temperatura'] - ((100 - datos['humedad_relativa']) / 5)
    
    # 9. INDICES AGRICOLAS
    print("   Calculando indices agricolas...")
    # Grados día (base 10°C)
    datos['grados_dia'] = np.maximum(0, datos['temperatura'] - 10)
    
    # Confort térmico
    datos['confort_termico'] = np.where(
        (datos['temperatura'] >= 18) & (datos['temperatura'] <= 25) &
        (datos['humedad_relativa'] >= 40) & (datos['humedad_relativa'] <= 70),
        1, 0
    )
    
    # 10. ALERTAS
    print("   Generando alertas...")
    alertas = []
    
    # Alerta de helada
    helada = (datos['temperatura_min'] < 0)
    if helada.any():
        alertas.append({
            'tipo': 'helada',
            'severidad': 'alta' if (datos['temperatura_min'] < -2).any() else 'media',
            'descripcion': 'Riesgo de heladas detectado'
        })
    
    # Alerta de calor extremo
    calor = (datos['temperatura_max'] > 35)
    if calor.any():
        alertas.append({
            'tipo': 'calor_extremo',
            'severidad': 'alta',
            'descripcion': 'Temperaturas extremas detectadas'
        })
    
    # Alerta de viento fuerte
    viento_fuerte = (datos['velocidad_viento'] > 25)
    if viento_fuerte.any():
        alertas.append({
            'tipo': 'viento_fuerte',
            'severidad': 'media',
            'descripcion': 'Vientos fuertes detectados'
        })
    
    # Redondear valores
    columnas_numericas = ['temperatura', 'temperatura_max', 'temperatura_min', 
                         'precipitacion', 'humedad_relativa', 'presion_atmosferica',
                         'velocidad_viento', 'direccion_viento', 'nubosidad',
                         'radiacion_solar', 'punto_rocio', 'grados_dia']
    
    for col in columnas_numericas:
        if col in datos.columns:
            datos[col] = datos[col].round(2)
    
    # Guardar datos
    archivo_csv = f"datos_meteorologicos_completos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    datos.to_csv(archivo_csv)
    
    # Crear resumen
    resumen = {
        'fecha_generacion': datetime.now().isoformat(),
        'periodo': {
            'inicio': fechas[0].isoformat(),
            'fin': fechas[-1].isoformat(),
            'total_registros': len(datos)
        },
        'variables_generadas': list(datos.columns),
        'estadisticas': {
            'temperatura_promedio': float(datos['temperatura'].mean()),
            'precipitacion_total': float(datos['precipitacion'].sum()),
            'humedad_promedio': float(datos['humedad_relativa'].mean()),
            'presion_promedio': float(datos['presion_atmosferica'].mean()),
            'viento_promedio': float(datos['velocidad_viento'].mean()),
            'nubosidad_promedio': float(datos['nubosidad'].mean())
        },
        'alertas': alertas,
        'archivo_generado': archivo_csv
    }
    
    # Guardar resumen
    with open(f"resumen_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    
    print(f"Datos generados exitosamente:")
    print(f"   Total registros: {len(datos)}")
    print(f"   Periodo: {fechas[0].strftime('%Y-%m-%d')} a {fechas[-1].strftime('%Y-%m-%d')}")
    print(f"   Archivo: {archivo_csv}")
    print(f"   Temperatura promedio: {datos['temperatura'].mean():.1f}C")
    print(f"   Humedad promedio: {datos['humedad_relativa'].mean():.1f}%")
    print(f"   Presion promedio: {datos['presion_atmosferica'].mean():.1f} hPa")
    print(f"   Viento promedio: {datos['velocidad_viento'].mean():.1f} km/h")
    print(f"   Nubosidad promedio: {datos['nubosidad'].mean():.1f}%")
    
    if alertas:
        print(f"   Alertas generadas: {len(alertas)}")
        for alerta in alertas:
            print(f"      - {alerta['tipo']}: {alerta['descripcion']}")
    
    return datos, resumen

if __name__ == "__main__":
    # Generar datos para los últimos 30 días
    datos, resumen = generar_datos_meteorologicos_completos(dias=30)
    
    print("\nGeneracion de datos meteorologicos completos finalizada!")
    print("   El sistema ahora tiene todas las variables meteorologicas disponibles.")
