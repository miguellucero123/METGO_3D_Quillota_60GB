#!/usr/bin/env python3
"""
Sistema de Validación de Datos Meteorológicos - METGO 3D Operativo
Validación robusta de datos meteorológicos con detección de outliers
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

class ValidadorDatosMeteorologicos:
    """
    Validador robusto de datos meteorológicos para Quillota
    """
    
    def __init__(self):
        """
        Inicializar validador con rangos meteorológicos para Quillota
        """
        # Rangos válidos para Quillota (Valparaíso, Chile)
        self.rangos_validos = {
            'temperatura_max': (-5, 45),      # °C
            'temperatura_min': (-10, 35),     # °C
            'humedad_relativa': (0, 100),      # %
            'precipitacion': (0, 200),         # mm/día
            'velocidad_viento': (0, 100),      # km/h
            'presion_atmosferica': (950, 1050), # hPa
            'radiacion_solar': (0, 35),        # MJ/m²
            'nubosidad': (0, 100)              # %
        }
        
        # Rangos críticos para alertas
        self.rangos_criticos = {
            'helada_severa': (-10, -2),
            'helada_moderada': (-2, 0),
            'calor_extremo': (35, 45),
            'calor_moderado': (30, 35),
            'lluvia_intensa': (20, 200),
            'viento_fuerte': (25, 100),
            'humedad_muy_baja': (0, 30),
            'humedad_muy_alta': (85, 100)
        }
        
        # Estadísticas históricas de Quillota
        self.estadisticas_historicas = {
            'temperatura_max': {'media': 22.5, 'std': 6.2},
            'temperatura_min': {'media': 10.8, 'std': 4.1},
            'humedad_relativa': {'media': 68.5, 'std': 15.2},
            'precipitacion': {'media': 0.8, 'std': 2.1},
            'velocidad_viento': {'media': 8.2, 'std': 3.8}
        }
    
    def validar_rangos(self, datos: pd.DataFrame) -> Dict[str, List[int]]:
        """
        Validar que los datos estén dentro de rangos válidos
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
        
        Returns:
            Dict[str, List[int]]: Índices de filas con datos fuera de rango
        """
        errores_rango = {}
        
        for columna, (min_val, max_val) in self.rangos_validos.items():
            if columna in datos.columns:
                # Encontrar valores fuera de rango
                fuera_rango = datos[
                    (datos[columna] < min_val) | (datos[columna] > max_val)
                ].index.tolist()
                
                if fuera_rango:
                    errores_rango[columna] = fuera_rango
        
        return errores_rango
    
    def detectar_outliers(self, datos: pd.DataFrame, metodo='iqr') -> Dict[str, List[int]]:
        """
        Detectar outliers usando diferentes métodos
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
            metodo (str): Método de detección ('iqr', 'zscore', 'modified_zscore')
        
        Returns:
            Dict[str, List[int]]: Índices de outliers por columna
        """
        outliers = {}
        
        for columna in datos.select_dtypes(include=[np.number]).columns:
            if columna in self.rangos_validos:
                valores = datos[columna].dropna()
                
                if metodo == 'iqr':
                    Q1 = valores.quantile(0.25)
                    Q3 = valores.quantile(0.75)
                    IQR = Q3 - Q1
                    limite_inferior = Q1 - 1.5 * IQR
                    limite_superior = Q3 + 1.5 * IQR
                    
                    outliers_columna = datos[
                        (datos[columna] < limite_inferior) | 
                        (datos[columna] > limite_superior)
                    ].index.tolist()
                
                elif metodo == 'zscore':
                    z_scores = np.abs((valores - valores.mean()) / valores.std())
                    outliers_columna = datos[z_scores > 3].index.tolist()
                
                elif metodo == 'modified_zscore':
                    median = valores.median()
                    mad = np.median(np.abs(valores - median))
                    modified_z_scores = 0.6745 * (valores - median) / mad
                    outliers_columna = datos[np.abs(modified_z_scores) > 3.5].index.tolist()
                
                if outliers_columna:
                    outliers[columna] = outliers_columna
        
        return outliers
    
    def validar_consistencia_temporal(self, datos: pd.DataFrame) -> List[int]:
        """
        Validar consistencia temporal de los datos
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
        
        Returns:
            List[int]: Índices de filas con inconsistencias temporales
        """
        inconsistencias = []
        
        if 'fecha' in datos.columns:
            # Verificar duplicados de fecha
            duplicados = datos[datos['fecha'].duplicated()].index.tolist()
            inconsistencias.extend(duplicados)
            
            # Verificar orden cronológico
            datos_ordenados = datos.sort_values('fecha')
            if not datos_ordenados['fecha'].equals(datos['fecha']):
                inconsistencias.extend(datos.index.tolist())
            
            # Verificar fechas futuras
            hoy = datetime.now().date()
            fechas_futuras = datos[datos['fecha'].dt.date > hoy].index.tolist()
            inconsistencias.extend(fechas_futuras)
        
        return list(set(inconsistencias))
    
    def validar_logica_meteorologica(self, datos: pd.DataFrame) -> List[int]:
        """
        Validar lógica meteorológica básica
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
        
        Returns:
            List[int]: Índices de filas con inconsistencias lógicas
        """
        inconsistencias = []
        
        # Temperatura mínima no puede ser mayor que máxima
        if 'temperatura_min' in datos.columns and 'temperatura_max' in datos.columns:
            temp_inconsistente = datos[
                datos['temperatura_min'] > datos['temperatura_max']
            ].index.tolist()
            inconsistencias.extend(temp_inconsistente)
        
        # Precipitación con humedad muy baja (inconsistente)
        if 'precipitacion' in datos.columns and 'humedad_relativa' in datos.columns:
            lluvia_humedad_baja = datos[
                (datos['precipitacion'] > 5) & (datos['humedad_relativa'] < 40)
            ].index.tolist()
            inconsistencias.extend(lluvia_humedad_baja)
        
        # Viento fuerte con presión alta (inconsistente)
        if 'velocidad_viento' in datos.columns and 'presion_atmosferica' in datos.columns:
            viento_presion_alta = datos[
                (datos['velocidad_viento'] > 30) & (datos['presion_atmosferica'] > 1020)
            ].index.tolist()
            inconsistencias.extend(viento_presion_alta)
        
        return list(set(inconsistencias))
    
    def calcular_metricas_calidad(self, datos: pd.DataFrame) -> Dict[str, float]:
        """
        Calcular métricas de calidad de los datos
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
        
        Returns:
            Dict[str, float]: Métricas de calidad
        """
        metricas = {}
        
        # Completitud de datos
        metricas['completitud'] = (1 - datos.isnull().sum().sum() / (len(datos) * len(datos.columns))) * 100
        
        # Consistencia temporal
        inconsistencias_temporales = len(self.validar_consistencia_temporal(datos))
        metricas['consistencia_temporal'] = (1 - inconsistencias_temporales / len(datos)) * 100
        
        # Consistencia lógica
        inconsistencias_logicas = len(self.validar_logica_meteorologica(datos))
        metricas['consistencia_logica'] = (1 - inconsistencias_logicas / len(datos)) * 100
        
        # Calidad general (promedio ponderado)
        metricas['calidad_general'] = (
            metricas['completitud'] * 0.4 +
            metricas['consistencia_temporal'] * 0.3 +
            metricas['consistencia_logica'] * 0.3
        )
        
        return metricas
    
    def validar_datos_completos(self, datos: pd.DataFrame) -> Dict[str, any]:
        """
        Validación completa de datos meteorológicos
        
        Args:
            datos (pd.DataFrame): DataFrame con datos meteorológicos
        
        Returns:
            Dict[str, any]: Resultado completo de la validación
        """
        resultado = {
            'datos_validos': True,
            'errores_rango': {},
            'outliers': {},
            'inconsistencias_temporales': [],
            'inconsistencias_logicas': [],
            'metricas_calidad': {},
            'recomendaciones': []
        }
        
        # Validar rangos
        resultado['errores_rango'] = self.validar_rangos(datos)
        
        # Detectar outliers
        resultado['outliers'] = self.detectar_outliers(datos)
        
        # Validar consistencia temporal
        resultado['inconsistencias_temporales'] = self.validar_consistencia_temporal(datos)
        
        # Validar lógica meteorológica
        resultado['inconsistencias_logicas'] = self.validar_logica_meteorologica(datos)
        
        # Calcular métricas de calidad
        resultado['metricas_calidad'] = self.calcular_metricas_calidad(datos)
        
        # Determinar si los datos son válidos
        total_errores = (
            len(resultado['errores_rango']) +
            len(resultado['outliers']) +
            len(resultado['inconsistencias_temporales']) +
            len(resultado['inconsistencias_logicas'])
        )
        
        resultado['datos_validos'] = total_errores == 0
        
        # Generar recomendaciones
        if resultado['metricas_calidad']['completitud'] < 90:
            resultado['recomendaciones'].append("Completitud baja - revisar fuentes de datos")
        
        if resultado['metricas_calidad']['consistencia_temporal'] < 95:
            resultado['recomendaciones'].append("Inconsistencias temporales detectadas")
        
        if resultado['metricas_calidad']['consistencia_logica'] < 90:
            resultado['recomendaciones'].append("Inconsistencias lógicas detectadas")
        
        if resultado['metricas_calidad']['calidad_general'] < 85:
            resultado['recomendaciones'].append("Calidad general de datos baja")
        
        return resultado
    
    def corregir_datos(self, datos: pd.DataFrame, resultado_validacion: Dict) -> pd.DataFrame:
        """
        Corregir datos basado en resultados de validación
        
        Args:
            datos (pd.DataFrame): DataFrame original
            resultado_validacion (Dict): Resultado de validación
        
        Returns:
            pd.DataFrame: DataFrame corregido
        """
        datos_corregidos = datos.copy()
        
        # Corregir valores fuera de rango
        for columna, indices in resultado_validacion['errores_rango'].items():
            if columna in self.rangos_validos:
                min_val, max_val = self.rangos_validos[columna]
                datos_corregidos.loc[indices, columna] = np.clip(
                    datos_corregidos.loc[indices, columna], min_val, max_val
                )
        
        # Corregir outliers usando interpolación
        for columna, indices in resultado_validacion['outliers'].items():
            if len(indices) < len(datos) * 0.1:  # Solo si son menos del 10%
                datos_corregidos.loc[indices, columna] = datos_corregidos[columna].interpolate()
        
        return datos_corregidos

# Función de conveniencia
def validar_datos_meteorologicos(datos: pd.DataFrame) -> Dict[str, any]:
    """
    Función de conveniencia para validar datos meteorológicos
    
    Args:
        datos (pd.DataFrame): DataFrame con datos meteorológicos
    
    Returns:
        Dict[str, any]: Resultado de la validación
    """
    validador = ValidadorDatosMeteorologicos()
    return validador.validar_datos_completos(datos)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear datos de prueba
    np.random.seed(42)
    fechas = pd.date_range(start='2024-01-01', periods=30, freq='D')
    
    datos_prueba = pd.DataFrame({
        'fecha': fechas,
        'temperatura_max': np.random.normal(22, 6, 30),
        'temperatura_min': np.random.normal(10, 4, 30),
        'humedad_relativa': np.random.normal(70, 15, 30),
        'precipitacion': np.random.exponential(0.8, 30),
        'velocidad_viento': np.random.normal(8, 3, 30)
    })
    
    # Introducir algunos errores intencionalmente
    datos_prueba.loc[5, 'temperatura_max'] = 50  # Fuera de rango
    datos_prueba.loc[10, 'temperatura_min'] = 15  # Mayor que máxima
    datos_prueba.loc[15, 'humedad_relativa'] = 150  # Fuera de rango
    
    # Validar datos
    validador = ValidadorDatosMeteorologicos()
    resultado = validador.validar_datos_completos(datos_prueba)
    
    print("🔍 RESULTADO DE VALIDACIÓN:")
    print(f"✅ Datos válidos: {resultado['datos_validos']}")
    print(f"📊 Calidad general: {resultado['metricas_calidad']['calidad_general']:.1f}%")
    print(f"📈 Completitud: {resultado['metricas_calidad']['completitud']:.1f}%")
    print(f"⏰ Consistencia temporal: {resultado['metricas_calidad']['consistencia_temporal']:.1f}%")
    print(f"🧠 Consistencia lógica: {resultado['metricas_calidad']['consistencia_logica']:.1f}%")
    
    if resultado['recomendaciones']:
        print("\n💡 RECOMENDACIONES:")
        for recomendacion in resultado['recomendaciones']:
            print(f"   • {recomendacion}")
    
    print("\n✅ Sistema de validación funcionando correctamente")
