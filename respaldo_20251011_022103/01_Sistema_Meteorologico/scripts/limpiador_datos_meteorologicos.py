#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpiador de Datos Meteorológicos METGO 3D
Sistema para limpiar y corregir datos existentes
"""

import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import logging
from pathlib import Path
import shutil

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/limpiador_datos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LimpiadorDatosMeteorologicos:
    """Limpiador avanzado de datos meteorológicos"""
    
    def __init__(self):
        self.estadisticas_limpieza = {
            'registros_procesados': 0,
            'registros_limpiados': 0,
            'errores_corregidos': 0,
            'registros_eliminados': 0,
            'backups_creados': 0
        }
        
        # Configuración de limpieza
        self.configuracion = {
            'rangos_validos': {
                'temperatura_maxima': (-50, 50),
                'temperatura_minima': (-50, 50),
                'temperatura_promedio': (-50, 50),
                'precipitacion_diaria': (0, 500),
                'humedad_relativa': (0, 100),
                'presion_atmosferica': (850, 1100),
                'viento_velocidad': (0, 200),
                'cobertura_nubosa': (0, 100),
                'indice_uv': (0, 15)
            },
            'valores_por_defecto': {
                'temperatura_promedio': 20.0,
                'humedad_relativa': 60.0,
                'presion_atmosferica': 1013.0,
                'viento_velocidad': 10.0,
                'cobertura_nubosa': 50.0,
                'indice_uv': 5.0
            },
            'crear_backup': True,
            'eliminar_registros_corruptos': False,
            'corregir_outliers': True,
            'llenar_valores_faltantes': True
        }
    
    def limpiar_base_datos(self, db_path: str) -> Dict[str, Any]:
        """Limpiar una base de datos específica"""
        logger.info(f"Iniciando limpieza de: {db_path}")
        
        # Crear backup si está habilitado
        if self.configuracion['crear_backup']:
            backup_path = self._crear_backup(db_path)
            logger.info(f"Backup creado: {backup_path}")
            self.estadisticas_limpieza['backups_creados'] += 1
        
        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(db_path)
            
            # Obtener estructura de la tabla
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%meteorologico%';")
            tablas = [row[0] for row in cursor.fetchall()]
            
            if not tablas:
                logger.warning(f"No se encontraron tablas meteorológicas en {db_path}")
                return {'error': 'No hay tablas meteorológicas'}
            
            # Limpiar cada tabla
            resultados_tablas = {}
            for tabla in tablas:
                logger.info(f"Limpiando tabla: {tabla}")
                resultado_tabla = self._limpiar_tabla(conn, tabla)
                resultados_tablas[tabla] = resultado_tabla
            
            conn.commit()
            conn.close()
            
            logger.info(f"Limpieza completada para {db_path}")
            return {
                'exito': True,
                'tablas_procesadas': len(tablas),
                'resultados_tablas': resultados_tablas,
                'estadisticas': self.estadisticas_limpieza.copy()
            }
            
        except Exception as e:
            logger.error(f"Error limpiando {db_path}: {e}")
            return {'error': str(e)}
    
    def _crear_backup(self, db_path: str) -> str:
        """Crear backup de la base de datos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path('scripts/backups')
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"{Path(db_path).stem}_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        
        return str(backup_path)
    
    def _limpiar_tabla(self, conn: sqlite3.Connection, tabla: str) -> Dict[str, Any]:
        """Limpiar una tabla específica"""
        try:
            # Cargar todos los datos
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            
            if df.empty:
                return {'registros_procesados': 0, 'sin_datos': True}
            
            registros_originales = len(df)
            logger.info(f"Procesando {registros_originales} registros en {tabla}")
            
            # Aplicar limpieza
            df_limpiado = self._aplicar_limpieza(df)
            
            # Eliminar registros corruptos si está habilitado
            if self.configuracion['eliminar_registros_corruptos']:
                df_limpiado = self._eliminar_registros_corruptos(df_limpiado)
            
            # Actualizar base de datos
            df_limpiado.to_sql(f"{tabla}_temp", conn, if_exists='replace', index=False)
            
            # Reemplazar tabla original
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE {tabla}")
            cursor.execute(f"ALTER TABLE {tabla}_temp RENAME TO {tabla}")
            
            registros_finales = len(df_limpiado)
            registros_eliminados = registros_originales - registros_finales
            
            self.estadisticas_limpieza['registros_procesados'] += registros_originales
            self.estadisticas_limpieza['registros_limpiados'] += registros_finales
            self.estadisticas_limpieza['registros_eliminados'] += registros_eliminados
            
            return {
                'registros_originales': registros_originales,
                'registros_finales': registros_finales,
                'registros_eliminados': registros_eliminados,
                'porcentaje_mejora': ((registros_finales - registros_originales) / registros_originales) * 100
            }
            
        except Exception as e:
            logger.error(f"Error limpiando tabla {tabla}: {e}")
            return {'error': str(e)}
    
    def _aplicar_limpieza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar todas las técnicas de limpieza"""
        df_limpiado = df.copy()
        
        # 1. Corregir tipos de datos
        df_limpiado = self._corregir_tipos_datos(df_limpiado)
        
        # 2. Corregir valores fuera de rango
        df_limpiado = self._corregir_valores_fuera_rango(df_limpiado)
        
        # 3. Corregir inconsistencias
        df_limpiado = self._corregir_inconsistencias(df_limpiado)
        
        # 4. Llenar valores faltantes
        if self.configuracion['llenar_valores_faltantes']:
            df_limpiado = self._llenar_valores_faltantes(df_limpiado)
        
        # 5. Corregir outliers
        if self.configuracion['corregir_outliers']:
            df_limpiado = self._corregir_outliers(df_limpiado)
        
        # 6. Normalizar formatos
        df_limpiado = self._normalizar_formatos(df_limpiado)
        
        return df_limpiado
    
    def _corregir_tipos_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corregir tipos de datos"""
        df_corregido = df.copy()
        
        # Convertir columnas numéricas
        columnas_numericas = [
            'temperatura_maxima', 'temperatura_minima', 'temperatura_promedio',
            'precipitacion_diaria', 'humedad_relativa', 'presion_atmosferica',
            'viento_velocidad', 'cobertura_nubosa', 'indice_uv'
        ]
        
        for col in columnas_numericas:
            if col in df_corregido.columns:
                df_corregido[col] = pd.to_numeric(df_corregido[col], errors='coerce')
        
        # Convertir timestamp
        if 'fecha' in df_corregido.columns:
            df_corregido['fecha'] = pd.to_datetime(df_corregido['fecha'], errors='coerce')
        elif 'timestamp' in df_corregido.columns:
            df_corregido['timestamp'] = pd.to_datetime(df_corregido['timestamp'], errors='coerce')
        
        return df_corregido
    
    def _corregir_valores_fuera_rango(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corregir valores fuera de rangos válidos"""
        df_corregido = df.copy()
        
        for campo, (min_val, max_val) in self.configuracion['rangos_validos'].items():
            if campo in df_corregido.columns:
                # Identificar valores fuera de rango
                mask_fuera_rango = (df_corregido[campo] < min_val) | (df_corregido[campo] > max_val)
                valores_corregidos = mask_fuera_rango.sum()
                
                if valores_corregidos > 0:
                    logger.info(f"Corrigiendo {valores_corregidos} valores fuera de rango en {campo}")
                    
                    # Corregir con valores por defecto o límites
                    df_corregido.loc[df_corregido[campo] < min_val, campo] = min_val
                    df_corregido.loc[df_corregido[campo] > max_val, campo] = max_val
                    
                    self.estadisticas_limpieza['errores_corregidos'] += valores_corregidos
        
        return df_corregido
    
    def _corregir_inconsistencias(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corregir inconsistencias lógicas"""
        df_corregido = df.copy()
        
        # Corregir temperatura máxima < mínima
        if 'temperatura_maxima' in df_corregido.columns and 'temperatura_minima' in df_corregido.columns:
            mask_inconsistente = df_corregido['temperatura_maxima'] < df_corregido['temperatura_minima']
            inconsistencias = mask_inconsistente.sum()
            
            if inconsistencias > 0:
                logger.info(f"Corrigiendo {inconsistencias} inconsistencias de temperatura")
                
                # Intercambiar valores
                temp_max = df_corregido.loc[mask_inconsistente, 'temperatura_maxima']
                temp_min = df_corregido.loc[mask_inconsistente, 'temperatura_minima']
                
                df_corregido.loc[mask_inconsistente, 'temperatura_maxima'] = temp_min
                df_corregido.loc[mask_inconsistente, 'temperatura_minima'] = temp_max
                
                self.estadisticas_limpieza['errores_corregidos'] += inconsistencias
        
        # Corregir precipitación negativa
        if 'precipitacion_diaria' in df_corregido.columns:
            mask_negativa = df_corregido['precipitacion_diaria'] < 0
            negativas = mask_negativa.sum()
            
            if negativas > 0:
                logger.info(f"Corrigiendo {negativas} valores negativos de precipitación")
                df_corregido.loc[mask_negativa, 'precipitacion_diaria'] = 0.0
                self.estadisticas_limpieza['errores_corregidos'] += negativas
        
        return df_corregido
    
    def _llenar_valores_faltantes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Llenar valores faltantes con valores por defecto o interpolación"""
        df_corregido = df.copy()
        
        for campo, valor_defecto in self.configuracion['valores_por_defecto'].items():
            if campo in df_corregido.columns:
                valores_faltantes = df_corregido[campo].isnull().sum()
                
                if valores_faltantes > 0:
                    logger.info(f"Llenando {valores_faltantes} valores faltantes en {campo}")
                    
                    # Llenar con valor por defecto
                    df_corregido[campo].fillna(valor_defecto, inplace=True)
        
        return df_corregido
    
    def _corregir_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corregir outliers usando método IQR"""
        df_corregido = df.copy()
        
        columnas_numericas = [
            'temperatura_promedio', 'humedad_relativa', 'presion_atmosferica',
            'viento_velocidad'
        ]
        
        for col in columnas_numericas:
            if col in df_corregido.columns and not df_corregido[col].isnull().all():
                # Calcular IQR
                Q1 = df_corregido[col].quantile(0.25)
                Q3 = df_corregido[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # Definir límites
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                
                # Identificar outliers
                mask_outliers = (df_corregido[col] < limite_inferior) | (df_corregido[col] > limite_superior)
                outliers = mask_outliers.sum()
                
                if outliers > 0:
                    logger.info(f"Corrigiendo {outliers} outliers en {col}")
                    
                    # Corregir outliers con valores límite
                    df_corregido.loc[df_corregido[col] < limite_inferior, col] = limite_inferior
                    df_corregido.loc[df_corregido[col] > limite_superior, col] = limite_superior
                    
                    self.estadisticas_limpieza['errores_corregidos'] += outliers
        
        return df_corregido
    
    def _normalizar_formatos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizar formatos de datos"""
        df_corregido = df.copy()
        
        # Normalizar direcciones de viento
        if 'viento_direccion' in df_corregido.columns:
            df_corregido['viento_direccion'] = df_corregido['viento_direccion'].apply(
                self._normalizar_direccion_viento
            )
        
        # Redondear valores numéricos
        columnas_redondear = [
            'temperatura_maxima', 'temperatura_minima', 'temperatura_promedio',
            'precipitacion_diaria', 'humedad_relativa', 'viento_velocidad',
            'cobertura_nubosa', 'indice_uv'
        ]
        
        for col in columnas_redondear:
            if col in df_corregido.columns:
                df_corregido[col] = df_corregido[col].round(1)
        
        # Redondear presión atmosférica
        if 'presion_atmosferica' in df_corregido.columns:
            df_corregido['presion_atmosferica'] = df_corregido['presion_atmosferica'].round(0)
        
        return df_corregido
    
    def _normalizar_direccion_viento(self, direccion) -> str:
        """Normalizar dirección de viento"""
        if pd.isna(direccion):
            return 'N'
        
        direccion = str(direccion).strip().upper()
        
        # Si es un número, convertir a dirección cardinal
        try:
            grados = float(direccion)
            return self._grados_a_cardinales(grados)
        except ValueError:
            pass
        
        # Direcciones válidas
        direcciones_validas = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        ]
        
        if direccion in direcciones_validas:
            return direccion
        
        # Mapeo de direcciones comunes
        mapeo = {
            'NORTH': 'N', 'SOUTH': 'S', 'EAST': 'E', 'WEST': 'W',
            'NORTE': 'N', 'SUR': 'S', 'ESTE': 'E', 'OESTE': 'W'
        }
        
        return mapeo.get(direccion, 'N')
    
    def _grados_a_cardinales(self, grados: float) -> str:
        """Convertir grados a dirección cardinal"""
        direcciones = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        ]
        index = int((grados + 11.25) / 22.5) % 16
        return direcciones[index]
    
    def _eliminar_registros_corruptos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Eliminar registros completamente corruptos"""
        df_limpiado = df.copy()
        
        # Identificar registros con más del 50% de campos faltantes
        umbral_faltantes = len(df_limpiado.columns) * 0.5
        mask_corruptos = df_limpiado.isnull().sum(axis=1) > umbral_faltantes
        
        registros_eliminados = mask_corruptos.sum()
        if registros_eliminados > 0:
            logger.info(f"Eliminando {registros_eliminados} registros completamente corruptos")
            df_limpiado = df_limpiado[~mask_corruptos]
        
        return df_limpiado
    
    def generar_reporte_limpieza(self) -> Dict[str, Any]:
        """Generar reporte de limpieza"""
        # Convertir numpy types a Python types para JSON
        estadisticas_serializable = {}
        for key, value in self.estadisticas_limpieza.items():
            if hasattr(value, 'item'):  # numpy types
                estadisticas_serializable[key] = value.item()
            else:
                estadisticas_serializable[key] = value
        
        return {
            'fecha_limpieza': datetime.now().isoformat(),
            'estadisticas': estadisticas_serializable,
            'configuracion_utilizada': self.configuracion.copy()
        }

def main():
    """Función principal"""
    print("=" * 70)
    print("LIMPIADOR DE DATOS METEOROLOGICOS - METGO 3D")
    print("=" * 70)
    
    limpiador = LimpiadorDatosMeteorologicos()
    
    # Bases de datos a limpiar
    bases_datos = [
        "scripts/datos_meteorologicos.db",
        "scripts/datos_meteorologicos_reales.db"
    ]
    
    resultados_totales = []
    
    for db_path in bases_datos:
        print(f"\nLimpiando: {db_path}")
        print("-" * 50)
        
        resultado = limpiador.limpiar_base_datos(db_path)
        resultados_totales.append(resultado)
        
        if 'error' in resultado:
            print(f"Error: {resultado['error']}")
        else:
            print(f"Tablas procesadas: {resultado['tablas_procesadas']}")
            for tabla, stats in resultado['resultados_tablas'].items():
                print(f"  {tabla}:")
                print(f"    Registros originales: {stats.get('registros_originales', 0)}")
                print(f"    Registros finales: {stats.get('registros_finales', 0)}")
                print(f"    Registros eliminados: {stats.get('registros_eliminados', 0)}")
    
    # Generar reporte final
    reporte = limpiador.generar_reporte_limpieza()
    
    print(f"\n" + "=" * 70)
    print("REPORTE FINAL DE LIMPIEZA")
    print("=" * 70)
    
    print(f"Registros procesados: {limpiador.estadisticas_limpieza['registros_procesados']}")
    print(f"Registros limpiados: {limpiador.estadisticas_limpieza['registros_limpiados']}")
    print(f"Errores corregidos: {limpiador.estadisticas_limpieza['errores_corregidos']}")
    print(f"Registros eliminados: {limpiador.estadisticas_limpieza['registros_eliminados']}")
    print(f"Backups creados: {limpiador.estadisticas_limpieza['backups_creados']}")
    
    # Guardar reporte
    import os
    os.makedirs('reportes', exist_ok=True)
    archivo_reporte = f"reportes/limpieza_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\nReporte guardado en: {archivo_reporte}")
    print("\nLIMPIEZA COMPLETADA")

if __name__ == "__main__":
    main()
