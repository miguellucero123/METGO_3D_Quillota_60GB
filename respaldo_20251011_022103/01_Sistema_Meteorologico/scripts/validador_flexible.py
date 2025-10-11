#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador Flexible de Datos Meteorológicos METGO 3D
Validador adaptado a los datos existentes del sistema
"""

import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidadorFlexible:
    """Validador flexible adaptado a datos existentes"""
    
    def __init__(self):
        self.estadisticas = {
            'registros_procesados': 0,
            'registros_validos': 0,
            'registros_con_errores': 0,
            'errores_por_tipo': {},
            'advertencias_por_tipo': {}
        }
    
    def validar_registro_flexible(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Validar registro con criterios flexibles"""
        errores = []
        advertencias = []
        puntuacion = 100.0
        
        # Campos requeridos flexibles (al menos uno debe estar presente)
        campos_temperatura = ['temperatura_promedio', 'temperatura_maxima', 'temperatura_minima', 'temp']
        campos_precipitacion = ['precipitacion_diaria', 'precipitacion', 'rain', 'precip']
        campos_humedad = ['humedad_relativa', 'humedad', 'humidity']
        
        tiene_temperatura = any(campo in datos and datos[campo] is not None for campo in campos_temperatura)
        tiene_precipitacion = any(campo in datos and datos[campo] is not None for campo in campos_precipitacion)
        tiene_humedad = any(campo in datos and datos[campo] is not None for campo in campos_humedad)
        
        # Verificar que tenga al menos algunos datos meteorológicos
        if not (tiene_temperatura or tiene_precipitacion or tiene_humedad):
            errores.append("No hay datos meteorológicos básicos")
            puntuacion -= 50
        
        # Validar campos numéricos presentes
        campos_numericos = {
            'temperatura_maxima': (-50, 50),
            'temperatura_minima': (-50, 50),
            'temperatura_promedio': (-50, 50),
            'temp': (-50, 50),
            'precipitacion_diaria': (0, 500),
            'precipitacion': (0, 500),
            'rain': (0, 500),
            'precip': (0, 500),
            'humedad_relativa': (0, 100),
            'humedad': (0, 100),
            'humidity': (0, 100),
            'presion_atmosferica': (850, 1100),
            'presion': (850, 1100),
            'pressure': (850, 1100),
            'viento_velocidad': (0, 200),
            'viento': (0, 200),
            'wind_speed': (0, 200),
            'cobertura_nubosa': (0, 100),
            'clouds': (0, 100),
            'indice_uv': (0, 15),
            'uv': (0, 15)
        }
        
        for campo, (min_val, max_val) in campos_numericos.items():
            if campo in datos and datos[campo] is not None:
                try:
                    valor = float(datos[campo])
                    if valor < min_val or valor > max_val:
                        if campo in ['temperatura_maxima', 'temperatura_minima', 'temperatura_promedio', 'temp']:
                            if abs(valor) > 60:  # Solo alertar temperaturas muy extremas
                                errores.append(f"Temperatura extrema en {campo}: {valor}°C")
                                puntuacion -= 20
                            else:
                                advertencias.append(f"Temperatura fuera de rango en {campo}: {valor}°C")
                                puntuacion -= 5
                        elif campo in ['precipitacion_diaria', 'precipitacion', 'rain', 'precip']:
                            if valor < 0:
                                errores.append(f"Precipitación negativa en {campo}: {valor}")
                                puntuacion -= 15
                            elif valor > 200:  # Precipitación muy alta
                                advertencias.append(f"Precipitación muy alta en {campo}: {valor}mm")
                                puntuacion -= 5
                        elif campo in ['humedad_relativa', 'humedad', 'humidity']:
                            if valor < 0 or valor > 100:
                                errores.append(f"Humedad fuera de rango en {campo}: {valor}%")
                                puntuacion -= 15
                        else:
                            advertencias.append(f"Valor fuera de rango en {campo}: {valor}")
                            puntuacion -= 5
                except (ValueError, TypeError):
                    errores.append(f"Valor no numérico en {campo}: {datos[campo]}")
                    puntuacion -= 10
        
        # Validar consistencia si hay múltiples temperaturas
        temp_campos = [campo for campo in campos_temperatura if campo in datos and datos[campo] is not None]
        if len(temp_campos) >= 2:
            valores_temp = {campo: float(datos[campo]) for campo in temp_campos}
            
            if 'temperatura_maxima' in valores_temp and 'temperatura_minima' in valores_temp:
                if valores_temp['temperatura_maxima'] < valores_temp['temperatura_minima']:
                    errores.append("Temperatura máxima menor que mínima")
                    puntuacion -= 20
            elif 'temperatura_promedio' in valores_temp:
                temp_prom = valores_temp['temperatura_promedio']
                for campo, valor in valores_temp.items():
                    if campo != 'temperatura_promedio':
                        if abs(valor - temp_prom) > 20:  # Diferencia muy grande
                            advertencias.append(f"Gran diferencia entre {campo} y temperatura promedio")
                            puntuacion -= 5
        
        # Validar timestamp
        campos_timestamp = ['fecha', 'timestamp', 'date', 'time']
        tiene_timestamp = False
        
        for campo in campos_timestamp:
            if campo in datos and datos[campo] is not None:
                try:
                    pd.to_datetime(datos[campo])
                    tiene_timestamp = True
                    break
                except:
                    pass
        
        if not tiene_timestamp:
            advertencias.append("No hay timestamp válido")
            puntuacion -= 10
        
        # Determinar si es válido (más flexible)
        es_valido = puntuacion >= 60 and len(errores) <= 2
        
        return {
            'es_valido': es_valido,
            'puntuacion': max(0, puntuacion),
            'errores': errores,
            'advertencias': advertencias,
            'tiene_temperatura': tiene_temperatura,
            'tiene_precipitacion': tiene_precipitacion,
            'tiene_humedad': tiene_humedad,
            'tiene_timestamp': tiene_timestamp
        }
    
    def validar_dataset_completo(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validar dataset completo con criterios flexibles"""
        resultados = []
        errores_totales = []
        advertencias_totales = []
        puntuaciones = []
        
        for index, row in df.iterrows():
            datos_dict = row.to_dict()
            
            # Limpiar valores NaN
            for key, value in datos_dict.items():
                if pd.isna(value):
                    datos_dict[key] = None
            
            resultado = self.validar_registro_flexible(datos_dict)
            resultados.append(resultado)
            
            errores_totales.extend(resultado['errores'])
            advertencias_totales.extend(resultado['advertencias'])
            puntuaciones.append(resultado['puntuacion'])
        
        # Calcular estadísticas
        puntuacion_promedio = np.mean(puntuaciones) if puntuaciones else 0
        registros_validos = sum(1 for r in resultados if r['es_valido'])
        porcentaje_validos = (registros_validos / len(resultados)) * 100 if resultados else 0
        
        # Contar errores y advertencias por tipo
        errores_comunes = {}
        for error in errores_totales:
            tipo = error.split(':')[0] if ':' in error else error
            errores_comunes[tipo] = errores_comunes.get(tipo, 0) + 1
        
        advertencias_comunes = {}
        for advertencia in advertencias_totales:
            tipo = advertencia.split(':')[0] if ':' in advertencia else advertencia
            advertencias_comunes[tipo] = advertencias_comunes.get(tipo, 0) + 1
        
        return {
            'total_registros': len(resultados),
            'registros_validos': registros_validos,
            'registros_con_errores': len(resultados) - registros_validos,
            'porcentaje_validos': round(porcentaje_validos, 2),
            'puntuacion_promedio': round(puntuacion_promedio, 2),
            'puntuacion_minima': round(min(puntuaciones), 2) if puntuaciones else 0,
            'puntuacion_maxima': round(max(puntuaciones), 2) if puntuaciones else 0,
            'errores_mas_comunes': dict(sorted(errores_comunes.items(), key=lambda x: x[1], reverse=True)[:5]),
            'advertencias_mas_comunes': dict(sorted(advertencias_comunes.items(), key=lambda x: x[1], reverse=True)[:5]),
            'total_errores': len(errores_totales),
            'total_advertencias': len(advertencias_totales),
            'resultados_individuales': resultados
        }

def probar_validador_flexible():
    """Probar validador flexible con datos reales"""
    print("=" * 70)
    print("VALIDADOR FLEXIBLE DE DATOS METEOROLOGICOS")
    print("=" * 70)
    
    validador = ValidadorFlexible()
    
    # Bases de datos a probar
    bases_datos = [
        "scripts/datos_meteorologicos.db",
        "scripts/datos_meteorologicos_reales.db"
    ]
    
    resultados_totales = {
        'bases_probadadas': 0,
        'registros_totales': 0,
        'registros_validos': 0,
        'registros_con_errores': 0,
        'puntuaciones': []
    }
    
    for db_path in bases_datos:
        print(f"\nAnalizando: {db_path}")
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(db_path)
            
            # Obtener datos recientes
            query = """
                SELECT * FROM datos_meteorologicos 
                ORDER BY fecha DESC 
                LIMIT 50
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                print(f"   No hay datos en {db_path}")
                continue
            
            print(f"   Registros encontrados: {len(df)}")
            resultados_totales['bases_probadadas'] += 1
            resultados_totales['registros_totales'] += len(df)
            
            # Validar con validador flexible
            resultado = validador.validar_dataset_completo(df)
            
            print(f"   Registros validos: {resultado['registros_validos']}")
            print(f"   Registros con errores: {resultado['registros_con_errores']}")
            print(f"   Porcentaje validos: {resultado['porcentaje_validos']}%")
            print(f"   Puntuacion promedio: {resultado['puntuacion_promedio']}/100")
            
            resultados_totales['registros_validos'] += resultado['registros_validos']
            resultados_totales['registros_con_errores'] += resultado['registros_con_errores']
            resultados_totales['puntuaciones'].extend([r['puntuacion'] for r in resultado['resultados_individuales']])
            
            # Mostrar errores más comunes
            if resultado['errores_mas_comunes']:
                print(f"   Errores mas comunes:")
                for tipo, cantidad in list(resultado['errores_mas_comunes'].items())[:3]:
                    print(f"      {tipo}: {cantidad}")
            
            # Mostrar advertencias más comunes
            if resultado['advertencias_mas_comunes']:
                print(f"   Advertencias mas comunes:")
                for tipo, cantidad in list(resultado['advertencias_mas_comunes'].items())[:3]:
                    print(f"      {tipo}: {cantidad}")
            
        except Exception as e:
            print(f"   Error: {e}")
    
    # Reporte final
    print(f"\n" + "=" * 70)
    print("REPORTE FINAL - VALIDADOR FLEXIBLE")
    print("=" * 70)
    
    print(f"Bases de datos probadas: {resultados_totales['bases_probadadas']}")
    print(f"Registros totales: {resultados_totales['registros_totales']}")
    print(f"Registros validos: {resultados_totales['registros_validos']}")
    print(f"Registros con errores: {resultados_totales['registros_con_errores']}")
    
    if resultados_totales['registros_totales'] > 0:
        porcentaje_total = (resultados_totales['registros_validos'] / resultados_totales['registros_totales']) * 100
        print(f"Porcentaje total validos: {porcentaje_total:.1f}%")
    
    if resultados_totales['puntuaciones']:
        puntuacion_promedio = np.mean(resultados_totales['puntuaciones'])
        print(f"Puntuacion promedio: {puntuacion_promedio:.1f}/100")
    
    # Recomendaciones
    print(f"\nRECOMENDACIONES:")
    if porcentaje_total >= 80:
        print("   - Calidad de datos BUENA")
        print("   - Mantener validaciones actuales")
    elif porcentaje_total >= 60:
        print("   - Calidad de datos ACEPTABLE")
        print("   - Mejorar fuentes de datos")
    else:
        print("   - Calidad de datos BAJA")
        print("   - Implementar limpieza adicional")
    
    return resultados_totales

def main():
    """Función principal"""
    probar_validador_flexible()

if __name__ == "__main__":
    main()

