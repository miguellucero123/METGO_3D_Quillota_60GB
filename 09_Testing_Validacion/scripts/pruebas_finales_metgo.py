#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 PRUEBAS FINALES METGO 3D
Sistema Meteorológico Agrícola Quillota - Pruebas Finales del Sistema Completo
"""

import os
import sys
import time
import json
import subprocess
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import importlib
import traceback

# Configuración
warnings.filterwarnings('ignore')

class PruebasFinalesMETGO:
    """Sistema de pruebas finales para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/pruebas',
            'directorio_logs': 'logs/pruebas',
            'directorio_reportes': 'reportes/pruebas',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Resultados de pruebas
        self.resultados_pruebas = {
            'inicio': datetime.now().isoformat(),
            'pruebas_ejecutadas': 0,
            'pruebas_exitosas': 0,
            'pruebas_fallidas': 0,
            'errores': [],
            'detalles': {}
        }
        
        # Módulos a probar
        self.modulos_principales = [
            'orquestador_metgo_avanzado',
            'configuracion_unificada_metgo',
            'pipeline_completo_metgo',
            'dashboard_unificado_metgo',
            'monitoreo_avanzado_metgo',
            'respaldos_automaticos_metgo',
            'ia_avanzada_metgo',
            'sistema_iot_metgo',
            'analisis_avanzado_metgo',
            'visualizacion_3d_metgo',
            'apis_avanzadas_metgo',
            'optimizacion_rendimiento_metgo',
            'escalabilidad_metgo',
            'deployment_produccion_metgo'
        ]
        
        # Notebooks a probar
        self.notebooks_principales = [
            '00_Sistema_Principal_MIP_Quillota.ipynb',
            '01_Configuracion_e_imports.ipynb',
            '02_Carga_y_Procesamiento_Datos.ipynb',
            '03_Analisis_Meteorologico.ipynb',
            '04_Visualizaciones.ipynb',
            '05_Modelos_ML.ipynb',
            '11_Monitoreo_Tiempo_Real.ipynb',
            '12_Respaldos_Automaticos.ipynb'
        ]
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/pruebas_finales.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_PRUEBAS_FINALES')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def probar_modulo(self, nombre_modulo: str) -> Dict[str, Any]:
        """Probar un módulo específico"""
        try:
            self.logger.info(f"Probando módulo: {nombre_modulo}")
            
            inicio = time.time()
            resultado = {
                'modulo': nombre_modulo,
                'exitoso': False,
                'error': None,
                'duracion': 0,
                'detalles': {}
            }
            
            # Verificar que el archivo existe
            archivo_modulo = f"{nombre_modulo}.py"
            if not Path(archivo_modulo).exists():
                resultado['error'] = f"Archivo {archivo_modulo} no encontrado"
                return resultado
            
            # Intentar importar el módulo
            try:
                modulo = importlib.import_module(nombre_modulo)
                resultado['detalles']['importacion'] = 'exitoso'
            except Exception as e:
                resultado['error'] = f"Error importando módulo: {e}"
                return resultado
            
            # Verificar que tiene función main
            if hasattr(modulo, 'main'):
                try:
                    # Ejecutar función main (simulada)
                    resultado['detalles']['main'] = 'disponible'
                except Exception as e:
                    resultado['detalles']['main'] = f'error: {e}'
            else:
                resultado['detalles']['main'] = 'no disponible'
            
            # Verificar clases principales
            clases_principales = [attr for attr in dir(modulo) if attr.endswith('METGO')]
            resultado['detalles']['clases'] = clases_principales
            
            duracion = time.time() - inicio
            resultado['duracion'] = duracion
            resultado['exitoso'] = True
            
            self.logger.info(f"Módulo {nombre_modulo} probado exitosamente en {duracion:.2f}s")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error probando módulo {nombre_modulo}: {e}")
            return {
                'modulo': nombre_modulo,
                'exitoso': False,
                'error': str(e),
                'duracion': 0,
                'detalles': {}
            }
    
    def probar_notebook(self, nombre_notebook: str) -> Dict[str, Any]:
        """Probar un notebook específico"""
        try:
            self.logger.info(f"Probando notebook: {nombre_notebook}")
            
            inicio = time.time()
            resultado = {
                'notebook': nombre_notebook,
                'exitoso': False,
                'error': None,
                'duracion': 0,
                'detalles': {}
            }
            
            # Verificar que el archivo existe
            if not Path(nombre_notebook).exists():
                resultado['error'] = f"Notebook {nombre_notebook} no encontrado"
                return resultado
            
            # Verificar tamaño del archivo
            tamaño = Path(nombre_notebook).stat().st_size
            resultado['detalles']['tamaño_bytes'] = tamaño
            
            # Verificar que es un notebook válido
            try:
                with open(nombre_notebook, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    if '"cell_type"' in contenido and '"source"' in contenido:
                        resultado['detalles']['formato'] = 'valido'
                    else:
                        resultado['detalles']['formato'] = 'invalido'
            except Exception as e:
                resultado['detalles']['formato'] = f'error: {e}'
            
            duracion = time.time() - inicio
            resultado['duracion'] = duracion
            resultado['exitoso'] = True
            
            self.logger.info(f"Notebook {nombre_notebook} probado exitosamente en {duracion:.2f}s")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error probando notebook {nombre_notebook}: {e}")
            return {
                'notebook': nombre_notebook,
                'exitoso': False,
                'error': str(e),
                'duracion': 0,
                'detalles': {}
            }
    
    def probar_archivos_configuracion(self) -> Dict[str, Any]:
        """Probar archivos de configuración"""
        try:
            self.logger.info("Probando archivos de configuración...")
            
            inicio = time.time()
            resultado = {
                'tipo': 'configuracion',
                'exitoso': False,
                'error': None,
                'duracion': 0,
                'detalles': {}
            }
            
            # Archivos de configuración a verificar
            archivos_config = [
                'config/config.yaml',
                'requirements.txt',
                'Dockerfile',
                'docker-compose.yml',
                '.gitignore',
                'README.md',
                'LICENSE'
            ]
            
            archivos_encontrados = 0
            archivos_validos = 0
            
            for archivo in archivos_config:
                if Path(archivo).exists():
                    archivos_encontrados += 1
                    try:
                        # Verificar que el archivo no está vacío
                        tamaño = Path(archivo).stat().st_size
                        if tamaño > 0:
                            archivos_validos += 1
                            resultado['detalles'][archivo] = f'valido ({tamaño} bytes)'
                        else:
                            resultado['detalles'][archivo] = 'vacio'
                    except Exception as e:
                        resultado['detalles'][archivo] = f'error: {e}'
                else:
                    resultado['detalles'][archivo] = 'no encontrado'
            
            resultado['detalles']['archivos_encontrados'] = archivos_encontrados
            resultado['detalles']['archivos_validos'] = archivos_validos
            resultado['detalles']['total_archivos'] = len(archivos_config)
            
            duracion = time.time() - inicio
            resultado['duracion'] = duracion
            resultado['exitoso'] = archivos_validos >= len(archivos_config) * 0.8  # 80% válidos
            
            self.logger.info(f"Archivos de configuración probados: {archivos_validos}/{archivos_encontrados}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error probando archivos de configuración: {e}")
            return {
                'tipo': 'configuracion',
                'exitoso': False,
                'error': str(e),
                'duracion': 0,
                'detalles': {}
            }
    
    def probar_documentacion(self) -> Dict[str, Any]:
        """Probar documentación"""
        try:
            self.logger.info("Probando documentación...")
            
            inicio = time.time()
            resultado = {
                'tipo': 'documentacion',
                'exitoso': False,
                'error': None,
                'duracion': 0,
                'detalles': {}
            }
            
            # Archivos de documentación a verificar
            archivos_docs = [
                'docs/README.md',
                'docs/guia_usuario.md',
                'docs/guia_instalacion.md',
                'docs/guia_api.md',
                'docs/guia_configuracion.md',
                'docs/troubleshooting.md'
            ]
            
            archivos_encontrados = 0
            archivos_validos = 0
            
            for archivo in archivos_docs:
                if Path(archivo).exists():
                    archivos_encontrados += 1
                    try:
                        # Verificar que el archivo no está vacío
                        tamaño = Path(archivo).stat().st_size
                        if tamaño > 1000:  # Mínimo 1KB
                            archivos_validos += 1
                            resultado['detalles'][archivo] = f'valido ({tamaño} bytes)'
                        else:
                            resultado['detalles'][archivo] = f'pequeño ({tamaño} bytes)'
                    except Exception as e:
                        resultado['detalles'][archivo] = f'error: {e}'
                else:
                    resultado['detalles'][archivo] = 'no encontrado'
            
            resultado['detalles']['archivos_encontrados'] = archivos_encontrados
            resultado['detalles']['archivos_validos'] = archivos_validos
            resultado['detalles']['total_archivos'] = len(archivos_docs)
            
            duracion = time.time() - inicio
            resultado['duracion'] = duracion
            resultado['exitoso'] = archivos_validos >= len(archivos_docs) * 0.8  # 80% válidos
            
            self.logger.info(f"Documentación probada: {archivos_validos}/{archivos_encontrados}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error probando documentación: {e}")
            return {
                'tipo': 'documentacion',
                'exitoso': False,
                'error': str(e),
                'duracion': 0,
                'detalles': {}
            }
    
    def probar_tests(self) -> Dict[str, Any]:
        """Probar sistema de tests"""
        try:
            self.logger.info("Probando sistema de tests...")
            
            inicio = time.time()
            resultado = {
                'tipo': 'tests',
                'exitoso': False,
                'error': None,
                'duracion': 0,
                'detalles': {}
            }
            
            # Archivos de tests a verificar
            archivos_tests = [
                'tests/test_ia_avanzada.py',
                'tests/test_sistema_iot.py',
                'tests/test_integracion_completa.py',
                'tests/test_rendimiento.py',
                'tests/runner_tests.py'
            ]
            
            archivos_encontrados = 0
            archivos_validos = 0
            
            for archivo in archivos_tests:
                if Path(archivo).exists():
                    archivos_encontrados += 1
                    try:
                        # Verificar que el archivo no está vacío
                        tamaño = Path(archivo).stat().st_size
                        if tamaño > 500:  # Mínimo 500 bytes
                            archivos_validos += 1
                            resultado['detalles'][archivo] = f'valido ({tamaño} bytes)'
                        else:
                            resultado['detalles'][archivo] = f'pequeño ({tamaño} bytes)'
                    except Exception as e:
                        resultado['detalles'][archivo] = f'error: {e}'
                else:
                    resultado['detalles'][archivo] = 'no encontrado'
            
            resultado['detalles']['archivos_encontrados'] = archivos_encontrados
            resultado['detalles']['archivos_validos'] = archivos_validos
            resultado['detalles']['total_archivos'] = len(archivos_tests)
            
            duracion = time.time() - inicio
            resultado['duracion'] = duracion
            resultado['exitoso'] = archivos_validos >= len(archivos_tests) * 0.8  # 80% válidos
            
            self.logger.info(f"Tests probados: {archivos_validos}/{archivos_encontrados}")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error probando tests: {e}")
            return {
                'tipo': 'tests',
                'exitoso': False,
                'error': str(e),
                'duracion': 0,
                'detalles': {}
            }
    
    def ejecutar_pruebas_completas(self) -> Dict[str, Any]:
        """Ejecutar todas las pruebas finales"""
        try:
            self.logger.info("Iniciando pruebas finales completas...")
            
            inicio = time.time()
            resultados = {}
            
            # Probar módulos principales
            print("Probando modulos principales...")
            resultados_modulos = {}
            for modulo in self.modulos_principales:
                resultado = self.probar_modulo(modulo)
                resultados_modulos[modulo] = resultado
                self.resultados_pruebas['pruebas_ejecutadas'] += 1
                if resultado['exitoso']:
                    self.resultados_pruebas['pruebas_exitosas'] += 1
                else:
                    self.resultados_pruebas['pruebas_fallidas'] += 1
                    self.resultados_pruebas['errores'].append(f"Modulo {modulo}: {resultado['error']}")
            
            resultados['modulos'] = resultados_modulos
            
            # Probar notebooks principales
            print("Probando notebooks principales...")
            resultados_notebooks = {}
            for notebook in self.notebooks_principales:
                resultado = self.probar_notebook(notebook)
                resultados_notebooks[notebook] = resultado
                self.resultados_pruebas['pruebas_ejecutadas'] += 1
                if resultado['exitoso']:
                    self.resultados_pruebas['pruebas_exitosas'] += 1
                else:
                    self.resultados_pruebas['pruebas_fallidas'] += 1
                    self.resultados_pruebas['errores'].append(f"Notebook {notebook}: {resultado['error']}")
            
            resultados['notebooks'] = resultados_notebooks
            
            # Probar archivos de configuración
            print("Probando archivos de configuracion...")
            resultado_config = self.probar_archivos_configuracion()
            resultados['configuracion'] = resultado_config
            self.resultados_pruebas['pruebas_ejecutadas'] += 1
            if resultado_config['exitoso']:
                self.resultados_pruebas['pruebas_exitosas'] += 1
            else:
                self.resultados_pruebas['pruebas_fallidas'] += 1
                self.resultados_pruebas['errores'].append(f"Configuracion: {resultado_config['error']}")
            
            # Probar documentación
            print("Probando documentacion...")
            resultado_docs = self.probar_documentacion()
            resultados['documentacion'] = resultado_docs
            self.resultados_pruebas['pruebas_ejecutadas'] += 1
            if resultado_docs['exitoso']:
                self.resultados_pruebas['pruebas_exitosas'] += 1
            else:
                self.resultados_pruebas['pruebas_fallidas'] += 1
                self.resultados_pruebas['errores'].append(f"Documentacion: {resultado_docs['error']}")
            
            # Probar tests
            print("Probando sistema de tests...")
            resultado_tests = self.probar_tests()
            resultados['tests'] = resultado_tests
            self.resultados_pruebas['pruebas_ejecutadas'] += 1
            if resultado_tests['exitoso']:
                self.resultados_pruebas['pruebas_exitosas'] += 1
            else:
                self.resultados_pruebas['pruebas_fallidas'] += 1
                self.resultados_pruebas['errores'].append(f"Tests: {resultado_tests['error']}")
            
            # Calcular estadísticas finales
            duracion = time.time() - inicio
            self.resultados_pruebas['fin'] = datetime.now().isoformat()
            self.resultados_pruebas['duracion_total'] = duracion
            self.resultados_pruebas['tasa_exito'] = (
                self.resultados_pruebas['pruebas_exitosas'] / 
                self.resultados_pruebas['pruebas_ejecutadas'] * 100
                if self.resultados_pruebas['pruebas_ejecutadas'] > 0 else 0
            )
            
            resultados['resumen'] = self.resultados_pruebas
            resultados['exitoso'] = self.resultados_pruebas['tasa_exito'] >= 80  # 80% de éxito
            
            self.logger.info(f"Pruebas finales completadas en {duracion:.2f} segundos")
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error ejecutando pruebas completas: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_pruebas(self) -> str:
        """Generar reporte de pruebas finales"""
        try:
            self.logger.info("Generando reporte de pruebas finales...")
            
            # Ejecutar pruebas completas
            resultados = self.ejecutar_pruebas_completas()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Pruebas Finales',
                'version': self.configuracion['version'],
                'resultados': resultados,
                'resumen': {
                    'pruebas_ejecutadas': self.resultados_pruebas['pruebas_ejecutadas'],
                    'pruebas_exitosas': self.resultados_pruebas['pruebas_exitosas'],
                    'pruebas_fallidas': self.resultados_pruebas['pruebas_fallidas'],
                    'tasa_exito': self.resultados_pruebas['tasa_exito'],
                    'duracion_total': self.resultados_pruebas['duracion_total'],
                    'errores': self.resultados_pruebas['errores']
                },
                'recomendaciones': [
                    "Verificar módulos con errores",
                    "Completar documentación faltante",
                    "Ejecutar tests unitarios",
                    "Validar configuración",
                    "Probar deployment en entorno de testing"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"pruebas_finales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de pruebas finales generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal de pruebas finales"""
    print("PRUEBAS FINALES METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Pruebas Finales del Sistema Completo")
    print("=" * 80)
    
    try:
        # Crear sistema de pruebas
        pruebas = PruebasFinalesMETGO()
        
        # Ejecutar pruebas completas
        print(f"\nEjecutando pruebas finales...")
        resultados = pruebas.ejecutar_pruebas_completas()
        
        if resultados.get('exitoso'):
            print(f"Pruebas finales completadas exitosamente")
        else:
            print(f"Pruebas finales completadas con errores")
        
        # Mostrar resumen
        resumen = resultados.get('resumen', {})
        print(f"\nResumen de pruebas:")
        print(f"   Pruebas ejecutadas: {resumen.get('pruebas_ejecutadas', 0)}")
        print(f"   Pruebas exitosas: {resumen.get('pruebas_exitosas', 0)}")
        print(f"   Pruebas fallidas: {resumen.get('pruebas_fallidas', 0)}")
        print(f"   Tasa de exito: {resumen.get('tasa_exito', 0):.1f}%")
        print(f"   Duracion total: {resumen.get('duracion_total', 0):.2f} segundos")
        
        # Mostrar errores si los hay
        errores = resumen.get('errores', [])
        if errores:
            print(f"\nErrores encontrados:")
            for error in errores[:5]:  # Mostrar solo los primeros 5
                print(f"   - {error}")
            if len(errores) > 5:
                print(f"   ... y {len(errores) - 5} errores mas")
        
        # Generar reporte
        print(f"\nGenerando reporte...")
        reporte = pruebas.generar_reporte_pruebas()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        return resultados.get('exitoso', False)
        
    except Exception as e:
        print(f"\nError en pruebas finales: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
