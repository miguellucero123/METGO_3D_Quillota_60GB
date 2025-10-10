"""
Sistema de validación robusta de datos meteorológicos.
Versión operativa con validación completa.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


class ValidadorDatos:
    """
    Clase para validación robusta de datos meteorológicos.
    
    Características:
    - Validación de rangos meteorológicos
    - Detección de outliers
    - Verificación de consistencia temporal
    - Validación de calidad de datos
    - Corrección automática de errores menores
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar validador de datos.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuración de validación
        self.umbrales = config.get('METEOROLOGIA', {}).get('umbrales', {})
        self.variables = config.get('METEOROLOGIA', {}).get('variables', [])
        
        # Rangos de validación meteorológica
        self.rangos_validos = {
            'temperatura_max': (-50, 60),
            'temperatura_min': (-50, 60),
            'humedad_relativa': (0, 100),
            'precipitacion': (0, 500),
            'velocidad_viento': (0, 200),
            'presion_atmosferica': (800, 1100),
            'radiacion_solar': (0, 50),
            'nubosidad': (0, 100)
        }
        
        self.logger.info("Validador de datos meteorológicos inicializado")
    
    def validar_datos_meteorologicos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Validar datos meteorológicos completos.
        
        Args:
            datos: DataFrame con datos meteorológicos
            
        Returns:
            DataFrame con datos validados y corregidos
            
        Raises:
            DatosInvalidosError: Si los datos no pasan la validación crítica
        """
        self.logger.info(f"Validando {len(datos)} registros meteorológicos")
        
        try:
            # Crear copia para no modificar datos originales
            datos_validados = datos.copy()
            
            # 1. Validación básica de estructura
            datos_validados = self._validar_estructura(datos_validados)
            
            # 2. Validación de tipos de datos
            datos_validados = self._validar_tipos_datos(datos_validados)
            
            # 3. Validación de rangos meteorológicos
            datos_validados = self._validar_rangos_meteorologicos(datos_validados)
            
            # 4. Validación de consistencia temporal
            datos_validados = self._validar_consistencia_temporal(datos_validados)
            
            # 5. Detección y corrección de outliers
            datos_validados = self._detectar_corregir_outliers(datos_validados)
            
            # 6. Validación de lógica meteorológica
            datos_validados = self._validar_logica_meteorologica(datos_validados)
            
            # 7. Validación final de calidad
            calidad = self._evaluar_calidad_datos(datos_validados)
            
            self.logger.info(f"Validación completada. Calidad: {calidad:.1f}%")
            
            if calidad < 70:
                self.logger.warning(f"Calidad de datos baja: {calidad:.1f}%")
            
            return datos_validados
            
        except Exception as e:
            self.logger.error(f"Error en validación de datos: {e}")
            raise DatosInvalidosError(f"Error validando datos: {e}")
    
    def _validar_estructura(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Validar estructura básica del DataFrame."""
        self.logger.debug("Validando estructura de datos")
        
        # Verificar columnas requeridas
        columnas_requeridas = [
            'fecha', 'temperatura_max', 'temperatura_min', 
            'humedad_relativa', 'precipitacion', 'velocidad_viento'
        ]
        
        columnas_faltantes = [col for col in columnas_requeridas if col not in datos.columns]
        if columnas_faltantes:
            raise DatosInvalidosError(f"Columnas faltantes: {columnas_faltantes}")
        
        # Verificar que no esté vacío
        if datos.empty:
            raise DatosInvalidosError("DataFrame vacío")
        
        # Verificar fechas
        if not pd.api.types.is_datetime64_any_dtype(datos['fecha']):
            try:
                datos['fecha'] = pd.to_datetime(datos['fecha'])
            except Exception as e:
                raise DatosInvalidosError(f"Error convirtiendo fechas: {e}")
        
        return datos
    
    def _validar_tipos_datos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Validar tipos de datos numéricos."""
        self.logger.debug("Validando tipos de datos")
        
        columnas_numericas = [
            'temperatura_max', 'temperatura_min', 'humedad_relativa',
            'precipitacion', 'velocidad_viento', 'presion_atmosferica',
            'radiacion_solar', 'nubosidad'
        ]
        
        for col in columnas_numericas:
            if col in datos.columns:
                try:
                    datos[col] = pd.to_numeric(datos[col], errors='coerce')
                except Exception as e:
                    self.logger.warning(f"Error convirtiendo {col} a numérico: {e}")
        
        return datos
    
    def _validar_rangos_meteorologicos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Validar rangos meteorológicos válidos."""
        self.logger.debug("Validando rangos meteorológicos")
        
        errores_rango = []
        
        for variable, (min_val, max_val) in self.rangos_validos.items():
            if variable in datos.columns:
                # Contar valores fuera de rango
                fuera_rango = (datos[variable] < min_val) | (datos[variable] > max_val)
                count_fuera = fuera_rango.sum()
                
                if count_fuera > 0:
                    self.logger.warning(f"{variable}: {count_fuera} valores fuera de rango [{min_val}, {max_val}]")
                    
                    # Corregir valores extremos
                    datos.loc[datos[variable] < min_val, variable] = min_val
                    datos.loc[datos[variable] > max_val, variable] = max_val
                    
                    errores_rango.append(f"{variable}: {count_fuera} valores corregidos")
        
        if errores_rango:
            self.logger.info(f"Correcciones aplicadas: {', '.join(errores_rango)}")
        
        return datos
    
    def _validar_consistencia_temporal(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Validar consistencia temporal de los datos."""
        self.logger.debug("Validando consistencia temporal")
        
        # Ordenar por fecha
        datos = datos.sort_values('fecha').reset_index(drop=True)
        
        # Verificar duplicados de fecha
        duplicados = datos['fecha'].duplicated()
        if duplicados.any():
            count_duplicados = duplicados.sum()
            self.logger.warning(f"Encontrados {count_duplicados} registros duplicados")
            datos = datos.drop_duplicates(subset=['fecha'], keep='first')
        
        # Verificar saltos temporales grandes
        if len(datos) > 1:
            diferencias = datos['fecha'].diff().dt.days
            saltos_grandes = diferencias > 7  # Más de una semana
            
            if saltos_grandes.any():
                count_saltos = saltos_grandes.sum()
                self.logger.warning(f"Encontrados {count_saltos} saltos temporales grandes")
        
        return datos
    
    def _detectar_corregir_outliers(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Detectar y corregir outliers meteorológicos."""
        self.logger.debug("Detectando outliers")
        
        variables_outlier = [
            'temperatura_max', 'temperatura_min', 'humedad_relativa',
            'precipitacion', 'velocidad_viento'
        ]
        
        outliers_corregidos = 0
        
        for variable in variables_outlier:
            if variable in datos.columns:
                outliers = self._detectar_outliers_iqr(datos[variable])
                
                if outliers.any():
                    count_outliers = outliers.sum()
                    self.logger.debug(f"{variable}: {count_outliers} outliers detectados")
                    
                    # Corregir outliers usando interpolación
                    datos.loc[outliers, variable] = np.nan
                    datos[variable] = datos[variable].interpolate(method='linear')
                    
                    outliers_corregidos += count_outliers
        
        if outliers_corregidos > 0:
            self.logger.info(f"Total outliers corregidos: {outliers_corregidos}")
        
        return datos
    
    def _detectar_outliers_iqr(self, serie: pd.Series) -> pd.Series:
        """Detectar outliers usando método IQR."""
        Q1 = serie.quantile(0.25)
        Q3 = serie.quantile(0.75)
        IQR = Q3 - Q1
        
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        return (serie < limite_inferior) | (serie > limite_superior)
    
    def _validar_logica_meteorologica(self, datos: pd.DataFrame) -> pd.DataFrame:
        """Validar lógica meteorológica básica."""
        self.logger.debug("Validando lógica meteorológica")
        
        # Temperatura máxima debe ser mayor que mínima
        temp_inconsistente = datos['temperatura_max'] < datos['temperatura_min']
        if temp_inconsistente.any():
            count_inconsistente = temp_inconsistente.sum()
            self.logger.warning(f"Encontradas {count_inconsistente} inconsistencias de temperatura")
            
            # Intercambiar valores cuando máximo < mínimo
            datos.loc[temp_inconsistente, ['temperatura_max', 'temperatura_min']] = \
                datos.loc[temp_inconsistente, ['temperatura_min', 'temperatura_max']].values
        
        # Amplitud térmica razonable (no más de 30°C)
        amplitud = datos['temperatura_max'] - datos['temperatura_min']
        amplitud_excesiva = amplitud > 30
        
        if amplitud_excesiva.any():
            count_excesiva = amplitud_excesiva.sum()
            self.logger.warning(f"Encontradas {count_excesiva} amplitudes térmicas excesivas")
        
        return datos
    
    def _evaluar_calidad_datos(self, datos: pd.DataFrame) -> float:
        """Evaluar calidad general de los datos."""
        self.logger.debug("Evaluando calidad de datos")
        
        total_registros = len(datos)
        if total_registros == 0:
            return 0.0
        
        # Puntuación por aspectos de calidad
        puntuacion = 100.0
        
        # Penalizar valores nulos
        valores_nulos = datos.isnull().sum().sum()
        penalizacion_nulos = (valores_nulos / (total_registros * len(datos.columns))) * 30
        puntuacion -= penalizacion_nulos
        
        # Penalizar valores fuera de rango (ya corregidos)
        valores_fuera_rango = 0
        for variable, (min_val, max_val) in self.rangos_validos.items():
            if variable in datos.columns:
                fuera_rango = (datos[variable] < min_val) | (datos[variable] > max_val)
                valores_fuera_rango += fuera_rango.sum()
        
        penalizacion_rango = (valores_fuera_rango / total_registros) * 20
        puntuacion -= penalizacion_rango
        
        # Penalizar inconsistencias temporales
        if len(datos) > 1:
            diferencias = datos['fecha'].diff().dt.days
            saltos_grandes = (diferencias > 7).sum()
            penalizacion_temporal = (saltos_grandes / len(datos)) * 10
            puntuacion -= penalizacion_temporal
        
        # Penalizar outliers extremos
        outliers_extremos = 0
        for variable in ['temperatura_max', 'temperatura_min']:
            if variable in datos.columns:
                outliers = self._detectar_outliers_iqr(datos[variable])
                outliers_extremos += outliers.sum()
        
        penalizacion_outliers = (outliers_extremos / total_registros) * 15
        puntuacion -= penalizacion_outliers
        
        return max(0.0, puntuacion)
    
    def generar_reporte_validacion(self, datos_originales: pd.DataFrame, 
                                 datos_validados: pd.DataFrame) -> Dict[str, Any]:
        """
        Generar reporte de validación de datos.
        
        Args:
            datos_originales: DataFrame original
            datos_validados: DataFrame validado
            
        Returns:
            Diccionario con reporte de validación
        """
        self.logger.info("Generando reporte de validación")
        
        reporte = {
            'fecha_validacion': datetime.now().isoformat(),
            'registros_originales': len(datos_originales),
            'registros_validados': len(datos_validados),
            'registros_eliminados': len(datos_originales) - len(datos_validados),
            'calidad_datos': self._evaluar_calidad_datos(datos_validados),
            'correcciones_aplicadas': [],
            'alertas': []
        }
        
        # Detectar correcciones aplicadas
        for variable in self.rangos_validos.keys():
            if variable in datos_originales.columns and variable in datos_validados.columns:
                cambios = (datos_originales[variable] != datos_validados[variable]).sum()
                if cambios > 0:
                    reporte['correcciones_aplicadas'].append({
                        'variable': variable,
                        'cambios': int(cambios)
                    })
        
        # Generar alertas
        calidad = reporte['calidad_datos']
        if calidad < 50:
            reporte['alertas'].append("CRÍTICO: Calidad de datos muy baja")
        elif calidad < 70:
            reporte['alertas'].append("ADVERTENCIA: Calidad de datos baja")
        elif calidad < 90:
            reporte['alertas'].append("INFO: Calidad de datos aceptable")
        else:
            reporte['alertas'].append("EXCELENTE: Calidad de datos alta")
        
        return reporte


class DatosInvalidosError(Exception):
    """Excepción para errores de validación de datos."""
    pass
