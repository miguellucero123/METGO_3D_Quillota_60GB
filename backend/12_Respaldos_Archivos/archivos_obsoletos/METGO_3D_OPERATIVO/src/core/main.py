"""
Sistema Meteorológico Agrícola Quillota - Módulo Principal
Versión Operativa 2.0

Este módulo contiene la clase principal del sistema METGO 3D Operativo.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from .api.meteorological_api import APIMeteorologica
from .ml.pipeline_ml import PipelineML
from .utils.data_validator import ValidadorDatos
from .utils.logger_config import configurar_logger
from .visualization.dashboard import DashboardMeteorologico


class SistemaMeteorologicoQuillota:
    """
    Clase principal del Sistema Meteorológico Agrícola Quillota.
    
    Esta clase coordina todas las funcionalidades del sistema:
    - Carga de datos meteorológicos
    - Validación de datos
    - Análisis meteorológico
    - Machine Learning
    - Generación de alertas
    - Visualizaciones
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar el sistema meteorológico.
        
        Args:
            config_path: Ruta al archivo de configuración. Si es None, usa configuración por defecto.
        """
        self.logger = configurar_logger(__name__)
        self.config = self._cargar_configuracion(config_path)
        
        # Inicializar componentes del sistema
        self.api = APIMeteorologica(self.config)
        self.validador = ValidadorDatos(self.config)
        self.pipeline_ml = PipelineML(self.config)
        self.dashboard = DashboardMeteorologico(self.config)
        
        self.logger.info("Sistema Meteorológico Quillota inicializado correctamente")
    
    def _cargar_configuracion(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Cargar configuración del sistema.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Returns:
            Diccionario con la configuración cargada
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config_template.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            self.logger.info(f"Configuración cargada desde: {config_path}")
            return config
        except FileNotFoundError:
            self.logger.warning("Archivo de configuración no encontrado, usando configuración por defecto")
            return self._configuracion_por_defecto()
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            return self._configuracion_por_defecto()
    
    def _configuracion_por_defecto(self) -> Dict[str, Any]:
        """Configuración por defecto del sistema."""
        return {
            'QUILLOTA': {
                'nombre': 'Quillota',
                'region': 'Valparaíso',
                'coordenadas': {'latitud': -32.8833, 'longitud': -71.25}
            },
            'METEOROLOGIA': {
                'umbrales': {
                    'temperatura': {'helada_severa': -2, 'calor_extremo': 35},
                    'precipitacion': {'lluvia_intensa': 20},
                    'viento': {'fuerte': 25},
                    'humedad': {'muy_baja': 30, 'muy_alta': 85}
                }
            }
        }
    
    def cargar_datos_meteorologicos(self, dias: int = 30, fuente: str = "auto") -> pd.DataFrame:
        """
        Cargar datos meteorológicos desde la fuente especificada.
        
        Args:
            dias: Número de días de datos a cargar
            fuente: Fuente de datos ("openmeteo", "local", "auto")
            
        Returns:
            DataFrame con datos meteorológicos
        """
        self.logger.info(f"Cargando datos meteorológicos para {dias} días desde {fuente}")
        
        try:
            if fuente == "auto":
                # Intentar API primero, luego datos locales
                try:
                    datos = self.api.obtener_datos_openmeteo(dias)
                    self.logger.info("Datos obtenidos desde OpenMeteo API")
                except Exception as e:
                    self.logger.warning(f"Error con API OpenMeteo: {e}, usando datos locales")
                    datos = self._cargar_datos_locales(dias)
            elif fuente == "openmeteo":
                datos = self.api.obtener_datos_openmeteo(dias)
            elif fuente == "local":
                datos = self._cargar_datos_locales(dias)
            else:
                raise ValueError(f"Fuente no válida: {fuente}")
            
            # Validar datos cargados
            datos_validados = self.validador.validar_datos_meteorologicos(datos)
            
            self.logger.info(f"Datos cargados exitosamente: {len(datos_validados)} registros")
            return datos_validados
            
        except Exception as e:
            self.logger.error(f"Error cargando datos meteorológicos: {e}")
            raise
    
    def _cargar_datos_locales(self, dias: int) -> pd.DataFrame:
        """Cargar datos desde archivos locales."""
        # Implementar carga desde archivos CSV locales
        # Por ahora, generar datos de ejemplo
        return self._generar_datos_ejemplo(dias)
    
    def _generar_datos_ejemplo(self, dias: int) -> pd.DataFrame:
        """Generar datos meteorológicos de ejemplo para testing."""
        np.random.seed(42)
        fechas = pd.date_range(start='2024-01-01', periods=dias, freq='D')
        
        datos = pd.DataFrame({
            'fecha': fechas,
            'temperatura_max': np.random.normal(22, 6, dias),
            'temperatura_min': np.random.normal(10, 4, dias),
            'humedad_relativa': np.clip(np.random.normal(65, 15, dias), 20, 95),
            'precipitacion': np.random.exponential(0.8, dias),
            'velocidad_viento': np.clip(np.random.normal(8, 3, dias), 0, 40),
            'direccion_viento': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], dias),
            'presion_atmosferica': np.random.normal(1013, 8, dias),
            'radiacion_solar': np.clip(np.random.normal(18, 6, dias), 0, 30)
        })
        
        return datos
    
    def analizar_datos(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """
        Realizar análisis meteorológico completo de los datos.
        
        Args:
            datos: DataFrame con datos meteorológicos
            
        Returns:
            Diccionario con resultados del análisis
        """
        self.logger.info("Iniciando análisis meteorológico")
        
        try:
            analisis = {
                'resumen_general': self._analizar_resumen_general(datos),
                'estadisticas_temperatura': self._analizar_temperaturas(datos),
                'analisis_precipitacion': self._analizar_precipitacion(datos),
                'indices_agricolas': self._calcular_indices_agricolas(datos),
                'tendencias_temporales': self._analizar_tendencias(datos),
                'fecha_analisis': datetime.now().isoformat()
            }
            
            self.logger.info("Análisis meteorológico completado exitosamente")
            return analisis
            
        except Exception as e:
            self.logger.error(f"Error en análisis meteorológico: {e}")
            raise
    
    def _analizar_resumen_general(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """Analizar resumen general de los datos."""
        return {
            'total_dias': len(datos),
            'fecha_inicio': datos['fecha'].min().strftime('%Y-%m-%d'),
            'fecha_fin': datos['fecha'].max().strftime('%Y-%m-%d'),
            'temperatura_promedio': datos['temperatura_max'].mean(),
            'precipitacion_total': datos['precipitacion'].sum(),
            'dias_con_lluvia': (datos['precipitacion'] > 1).sum()
        }
    
    def _analizar_temperaturas(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """Analizar patrones de temperatura."""
        return {
            'temperatura_maxima': datos['temperatura_max'].max(),
            'temperatura_minima': datos['temperatura_min'].min(),
            'temperatura_promedio_max': datos['temperatura_max'].mean(),
            'temperatura_promedio_min': datos['temperatura_min'].mean(),
            'amplitud_termica_promedio': (datos['temperatura_max'] - datos['temperatura_min']).mean(),
            'dias_helada': (datos['temperatura_min'] <= 0).sum(),
            'dias_calor_extremo': (datos['temperatura_max'] >= 35).sum()
        }
    
    def _analizar_precipitacion(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """Analizar patrones de precipitación."""
        return {
            'precipitacion_total': datos['precipitacion'].sum(),
            'precipitacion_promedio': datos['precipitacion'].mean(),
            'dias_con_lluvia': (datos['precipitacion'] > 1).sum(),
            'dias_sin_lluvia': (datos['precipitacion'] <= 0.1).sum(),
            'lluvia_maxima_diaria': datos['precipitacion'].max(),
            'periodos_sequia': self._calcular_periodos_sequia(datos)
        }
    
    def _calcular_indices_agricolas(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """Calcular índices agrícolas importantes."""
        # Calcular grados-día
        temperatura_base = 10  # °C
        grados_dia = np.maximum(0, datos['temperatura_max'] - temperatura_base)
        
        return {
            'grados_dia_total': grados_dia.sum(),
            'grados_dia_promedio': grados_dia.mean(),
            'confort_termico': self._calcular_confort_termico(datos),
            'necesidad_riego': self._calcular_necesidad_riego(datos),
            'riesgo_hongos': self._calcular_riesgo_hongos(datos)
        }
    
    def _analizar_tendencias(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """Analizar tendencias temporales."""
        # Implementar análisis de tendencias
        return {
            'tendencia_temperatura': 'estable',
            'tendencia_precipitacion': 'variable',
            'tendencia_humedad': 'estable'
        }
    
    def _calcular_periodos_sequia(self, datos: pd.DataFrame) -> int:
        """Calcular períodos de sequía."""
        sequia = datos['precipitacion'] <= 0.1
        periodos = 0
        en_sequia = False
        
        for dia in sequia:
            if dia and not en_sequia:
                periodos += 1
                en_sequia = True
            elif not dia:
                en_sequia = False
        
        return periodos
    
    def _calcular_confort_termico(self, datos: pd.DataFrame) -> str:
        """Calcular índice de confort térmico."""
        temp_promedio = datos['temperatura_max'].mean()
        if 18 <= temp_promedio <= 25:
            return "Óptimo"
        elif 15 <= temp_promedio < 18 or 25 < temp_promedio <= 30:
            return "Bueno"
        else:
            return "Desfavorable"
    
    def _calcular_necesidad_riego(self, datos: pd.DataFrame) -> str:
        """Calcular necesidad de riego."""
        precipitacion_total = datos['precipitacion'].sum()
        dias_periodo = len(datos)
        
        if precipitacion_total < dias_periodo * 0.5:
            return "Alta"
        elif precipitacion_total < dias_periodo * 1.0:
            return "Media"
        else:
            return "Baja"
    
    def _calcular_riesgo_hongos(self, datos: pd.DataFrame) -> str:
        """Calcular riesgo de enfermedades fúngicas."""
        humedad_alta = (datos['humedad_relativa'] > 80).sum()
        dias_periodo = len(datos)
        
        if humedad_alta > dias_periodo * 0.3:
            return "Alto"
        elif humedad_alta > dias_periodo * 0.1:
            return "Medio"
        else:
            return "Bajo"
    
    def evaluar_alertas(self, datos: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Evaluar alertas meteorológicas basadas en los datos.
        
        Args:
            datos: DataFrame con datos meteorológicos
            
        Returns:
            Lista de alertas generadas
        """
        self.logger.info("Evaluando alertas meteorológicas")
        
        alertas = []
        umbrales = self.config['METEOROLOGIA']['umbrales']
        
        # Verificar cada día para alertas
        for _, fila in datos.iterrows():
            fecha = fila['fecha']
            
            # Alertas de temperatura
            if fila['temperatura_min'] <= umbrales['temperatura']['helada_severa']:
                alertas.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'tipo': 'helada_severa',
                    'severidad': 'alta',
                    'mensaje': f'🧊 HELADA SEVERA ({fila["temperatura_min"]:.1f}°C) - Proteger cultivos urgentemente',
                    'valor': fila['temperatura_min']
                })
            
            if fila['temperatura_max'] >= umbrales['temperatura']['calor_extremo']:
                alertas.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'tipo': 'calor_extremo',
                    'severidad': 'alta',
                    'mensaje': f'🔥 CALOR EXTREMO ({fila["temperatura_max"]:.1f}°C) - Aumentar riego',
                    'valor': fila['temperatura_max']
                })
            
            # Alertas de viento
            if fila['velocidad_viento'] >= umbrales['viento']['fuerte']:
                alertas.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'tipo': 'viento_fuerte',
                    'severidad': 'media',
                    'mensaje': f'💨 VIENTO FUERTE ({fila["velocidad_viento"]:.1f} km/h) - Revisar estructuras',
                    'valor': fila['velocidad_viento']
                })
            
            # Alertas de precipitación
            if fila['precipitacion'] >= umbrales['precipitacion']['lluvia_intensa']:
                alertas.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'tipo': 'lluvia_intensa',
                    'severidad': 'media',
                    'mensaje': f'🌧️ LLUVIA INTENSA ({fila["precipitacion"]:.1f} mm) - Evitar labores',
                    'valor': fila['precipitacion']
                })
        
        self.logger.info(f"Generadas {len(alertas)} alertas meteorológicas")
        return alertas
    
    def entrenar_modelos_ml(self, datos: pd.DataFrame) -> Dict[str, Any]:
        """
        Entrenar modelos de Machine Learning para predicción meteorológica.
        
        Args:
            datos: DataFrame con datos meteorológicos históricos
            
        Returns:
            Diccionario con resultados del entrenamiento
        """
        self.logger.info("Iniciando entrenamiento de modelos ML")
        
        try:
            resultados = self.pipeline_ml.entrenar_modelos(datos)
            self.logger.info("Entrenamiento de modelos ML completado exitosamente")
            return resultados
        except Exception as e:
            self.logger.error(f"Error en entrenamiento ML: {e}")
            raise
    
    def crear_dashboard(self, analisis: Dict[str, Any], datos: pd.DataFrame) -> None:
        """
        Crear dashboard meteorológico interactivo.
        
        Args:
            analisis: Resultados del análisis meteorológico
            datos: DataFrame con datos meteorológicos
        """
        self.logger.info("Creando dashboard meteorológico")
        
        try:
            self.dashboard.crear_dashboard_completo(analisis, datos)
            self.logger.info("Dashboard meteorológico creado exitosamente")
        except Exception as e:
            self.logger.error(f"Error creando dashboard: {e}")
            raise
    
    def generar_reporte(self, analisis: Dict[str, Any], alertas: List[Dict[str, Any]]) -> str:
        """
        Generar reporte ejecutivo del análisis meteorológico.
        
        Args:
            analisis: Resultados del análisis meteorológico
            alertas: Lista de alertas generadas
            
        Returns:
            Ruta al archivo de reporte generado
        """
        self.logger.info("Generando reporte ejecutivo")
        
        try:
            # Implementar generación de reporte
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            reporte_path = f"logs/reporte_meteorologico_{timestamp}.txt"
            
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write("REPORTE METEOROLÓGICO QUILLOTA\n")
                f.write("=" * 50 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("RESUMEN GENERAL:\n")
                f.write(f"- Período analizado: {analisis['resumen_general']['total_dias']} días\n")
                f.write(f"- Temperatura promedio: {analisis['resumen_general']['temperatura_promedio']:.1f}°C\n")
                f.write(f"- Precipitación total: {analisis['resumen_general']['precipitacion_total']:.1f} mm\n")
                f.write(f"- Días con lluvia: {analisis['resumen_general']['dias_con_lluvia']}\n\n")
                
                f.write("ALERTAS GENERADAS:\n")
                for alerta in alertas:
                    f.write(f"- {alerta['mensaje']}\n")
            
            self.logger.info(f"Reporte generado: {reporte_path}")
            return reporte_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            raise


def main():
    """Función principal para ejecutar el sistema."""
    try:
        # Inicializar sistema
        sistema = SistemaMeteorologicoQuillota()
        
        # Cargar datos meteorológicos
        datos = sistema.cargar_datos_meteorologicos(dias=30)
        
        # Realizar análisis
        analisis = sistema.analizar_datos(datos)
        
        # Evaluar alertas
        alertas = sistema.evaluar_alertas(datos)
        
        # Crear dashboard
        sistema.crear_dashboard(analisis, datos)
        
        # Generar reporte
        reporte_path = sistema.generar_reporte(analisis, alertas)
        
        print(f"✅ Sistema ejecutado exitosamente")
        print(f"📊 Datos procesados: {len(datos)} registros")
        print(f"🚨 Alertas generadas: {len(alertas)}")
        print(f"📋 Reporte: {reporte_path}")
        
    except Exception as e:
        print(f"❌ Error ejecutando sistema: {e}")


if __name__ == "__main__":
    main()
