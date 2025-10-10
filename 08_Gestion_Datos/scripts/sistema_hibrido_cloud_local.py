"""
SISTEMA HÍBRIDO CLOUD-LOCAL - METGO 3D QUILLOTA
Sistema que puede ejecutarse tanto localmente como en la nube
"""

import os
import psutil
import platform
import time
from typing import Dict, Any, Optional
import json
import logging

class SistemaHibridoCloudLocal:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configuracion = self._detectar_entorno()
        self.recursos_disponibles = self._evaluar_recursos()
        
    def _detectar_entorno(self) -> Dict[str, Any]:
        """Detectar si estamos en entorno local o nube"""
        try:
            config = {
                'sistema_operativo': platform.system(),
                'arquitectura': platform.machine(),
                'procesador': platform.processor(),
                'python_version': platform.python_version(),
                'entorno_nube': False,
                'servicio_nube': None
            }
            
            # Detectar servicios de nube
            if 'GOOGLE_CLOUD_PROJECT' in os.environ:
                config['entorno_nube'] = True
                config['servicio_nube'] = 'Google Cloud'
            elif 'AWS_REGION' in os.environ:
                config['entorno_nube'] = True
                config['servicio_nube'] = 'AWS'
            elif 'AZURE_CLOUD' in os.environ:
                config['entorno_nube'] = True
                config['servicio_nube'] = 'Azure'
            elif 'COLAB' in os.environ:
                config['entorno_nube'] = True
                config['servicio_nube'] = 'Google Colab'
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error detectando entorno: {e}")
            return {'entorno_nube': False}
    
    def _evaluar_recursos(self) -> Dict[str, Any]:
        """Evaluar recursos disponibles del sistema"""
        try:
            recursos = {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'memory_percent': psutil.virtual_memory().percent,
                'disk_total': psutil.disk_usage('/').total,
                'disk_free': psutil.disk_usage('/').free,
                'disk_percent': psutil.disk_usage('/').percent
            }
            
            # Convertir bytes a GB
            recursos['memory_total_gb'] = recursos['memory_total'] / (1024**3)
            recursos['memory_available_gb'] = recursos['memory_available'] / (1024**3)
            recursos['disk_total_gb'] = recursos['disk_total'] / (1024**3)
            recursos['disk_free_gb'] = recursos['disk_free'] / (1024**3)
            
            return recursos
            
        except Exception as e:
            self.logger.error(f"Error evaluando recursos: {e}")
            return {}
    
    def recomendar_configuracion(self) -> Dict[str, Any]:
        """Recomendar configuración óptima basada en recursos disponibles"""
        try:
            recomendaciones = {
                'entorno_actual': self.configuracion,
                'recursos_disponibles': self.recursos_disponibles,
                'recomendacion_principal': None,
                'configuracion_optimizada': {},
                'mejoras_sugeridas': [],
                'costo_estimado': {}
            }
            
            # Evaluar si es suficiente para modelos híbridos
            cpu_count = self.recursos_disponibles.get('cpu_count', 0)
            memory_gb = self.recursos_disponibles.get('memory_available_gb', 0)
            
            if cpu_count >= 8 and memory_gb >= 16:
                recomendaciones['recomendacion_principal'] = 'LOCAL_OPTIMO'
                recomendaciones['configuracion_optimizada'] = {
                    'n_jobs': -1,
                    'n_estimators': 200,
                    'max_features': 'sqrt',
                    'parallel_processing': True,
                    'cache_size': '1GB'
                }
            elif cpu_count >= 4 and memory_gb >= 8:
                recomendaciones['recomendacion_principal'] = 'LOCAL_ACEPTABLE'
                recomendaciones['configuracion_optimizada'] = {
                    'n_jobs': 4,
                    'n_estimators': 100,
                    'max_features': 'sqrt',
                    'parallel_processing': True,
                    'cache_size': '512MB'
                }
            else:
                recomendaciones['recomendacion_principal'] = 'NUBE_RECOMENDADA'
                recomendaciones['configuracion_optimizada'] = {
                    'n_jobs': 2,
                    'n_estimators': 50,
                    'max_features': 'sqrt',
                    'parallel_processing': False,
                    'cache_size': '256MB'
                }
            
            # Sugerir mejoras
            if cpu_count < 8:
                recomendaciones['mejoras_sugeridas'].append(
                    f"Considerar CPU con al menos 8 núcleos (actual: {cpu_count})"
                )
            
            if memory_gb < 16:
                recomendaciones['mejoras_sugeridas'].append(
                    f"Considerar al menos 16GB RAM (actual: {memory_gb:.1f}GB)"
                )
            
            if not self.configuracion['entorno_nube']:
                recomendaciones['mejoras_sugeridas'].append(
                    "Considerar migración a nube para mejor escalabilidad"
                )
            
            # Estimar costos
            if self.configuracion['entorno_nube']:
                if self.configuracion['servicio_nube'] == 'Google Cloud':
                    recomendaciones['costo_estimado'] = {
                        'desarrollo': '$50-100/mes',
                        'produccion': '$200-500/mes',
                        'inferencia': '$0.02/1M requests'
                    }
                elif self.configuracion['servicio_nube'] == 'AWS':
                    recomendaciones['costo_estimado'] = {
                        'desarrollo': '$100-200/mes',
                        'produccion': '$300-800/mes',
                        'inferencia': '$0.20/1M requests'
                    }
            else:
                recomendaciones['costo_estimado'] = {
                    'hardware_recomendado': '$1000-3000',
                    'mejora_cpu': '$200-500',
                    'mejora_ram': '$100-300'
                }
            
            return recomendaciones
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {e}")
            return {}
    
    def generar_reporte_recursos(self) -> str:
        """Generar reporte detallado de recursos y recomendaciones"""
        try:
            recomendaciones = self.recomendar_configuracion()
            
            reporte = f"""
=== REPORTE DE RECURSOS Y RECOMENDACIONES - METGO 3D QUILLOTA ===

ENTORNO ACTUAL:
- Sistema Operativo: {self.configuracion.get('sistema_operativo', 'N/A')}
- Arquitectura: {self.configuracion.get('arquitectura', 'N/A')}
- Entorno Nube: {'Sí' if self.configuracion.get('entorno_nube') else 'No'}
- Servicio Nube: {self.configuracion.get('servicio_nube', 'N/A')}

RECURSOS DISPONIBLES:
- CPU: {self.recursos_disponibles.get('cpu_count', 0)} núcleos
- RAM: {self.recursos_disponibles.get('memory_available_gb', 0):.1f}GB disponibles
- Disco: {self.recursos_disponibles.get('disk_free_gb', 0):.1f}GB libres
- Uso CPU: {self.recursos_disponibles.get('cpu_percent', 0):.1f}%
- Uso RAM: {self.recursos_disponibles.get('memory_percent', 0):.1f}%

RECOMENDACIÓN PRINCIPAL: {recomendaciones.get('recomendacion_principal', 'N/A')}

CONFIGURACIÓN OPTIMIZADA:
{json.dumps(recomendaciones.get('configuracion_optimizada', {}), indent=2)}

MEJORAS SUGERIDAS:
"""
            
            for mejora in recomendaciones.get('mejoras_sugeridas', []):
                reporte += f"- {mejora}\n"
            
            costo = recomendaciones.get('costo_estimado', {})
            if costo:
                reporte += "\nCOSTOS ESTIMADOS:\n"
                for item, precio in costo.items():
                    reporte += f"- {item}: {precio}\n"
            
            return reporte
            
        except Exception as e:
            return f"Error generando reporte: {e}"
    
    def configurar_optimizacion_automatica(self) -> Dict[str, Any]:
        """Configurar optimización automática basada en recursos"""
        try:
            recomendaciones = self.recomendar_configuracion()
            config_optima = recomendaciones.get('configuracion_optimizada', {})
            
            # Aplicar configuración óptima
            configuracion_final = {
                'modelos_hibridos': {
                    'RandomForest': {
                        'n_estimators': config_optima.get('n_estimators', 100),
                        'n_jobs': config_optima.get('n_jobs', -1),
                        'max_features': config_optima.get('max_features', 'sqrt')
                    },
                    'GradientBoosting': {
                        'n_estimators': config_optima.get('n_estimators', 100),
                        'max_depth': 8 if config_optima.get('n_estimators', 100) >= 100 else 6
                    },
                    'ExtraTrees': {
                        'n_estimators': config_optima.get('n_estimators', 100),
                        'n_jobs': config_optima.get('n_jobs', -1)
                    }
                },
                'preprocesamiento': {
                    'max_features': 50 if config_optima.get('n_estimators', 100) >= 200 else 30,
                    'cache_size': config_optima.get('cache_size', '512MB')
                },
                'validacion': {
                    'cv_splits': 5 if config_optima.get('n_estimators', 100) >= 100 else 3,
                    'parallel_processing': config_optima.get('parallel_processing', True)
                }
            }
            
            return configuracion_final
            
        except Exception as e:
            self.logger.error(f"Error configurando optimización: {e}")
            return {}

def main():
    """Función principal para análisis de recursos"""
    print("="*80)
    print("ANÁLISIS DE RECURSOS Y RECOMENDACIONES - METGO 3D QUILLOTA")
    print("="*80)
    
    sistema = SistemaHibridoCloudLocal()
    
    # Generar reporte
    reporte = sistema.generar_reporte_recursos()
    print(reporte)
    
    # Configuración óptima
    config_optima = sistema.configurar_optimizacion_automatica()
    print("\nCONFIGURACIÓN ÓPTIMA PARA TU SISTEMA:")
    print(json.dumps(config_optima, indent=2))
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()



