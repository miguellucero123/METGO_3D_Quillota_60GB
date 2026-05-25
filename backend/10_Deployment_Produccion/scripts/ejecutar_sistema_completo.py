#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[SISTEMA] EJECUTOR MAESTRO DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa

Este script ejecuta todos los notebooks del sistema METGO 3D de forma secuencial
y automatizada, proporcionando un punto de entrada único para todo el sistema.

Autor: Sistema METGO 3D
Versión: 2.0
Fecha: 2025-01-02
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ejecutor_maestro.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from _deprecated_notice import warn_if_deprecated

warn_if_deprecated(__file__, "iniciar_metgo_desarrollo.bat o notebooks por módulo")


class EjecutorMETGO3D:
    """
    Clase principal para ejecutar todo el sistema METGO 3D
    """
    
    def __init__(self):
        self.directorio_base = Path.cwd()
        self.notebooks = [
            "01_Configuracion_e_imports.ipynb",
            "02_Carga_y_Procesamiento_Datos.ipynb", 
            "03_Analisis_Meteorologico.ipynb",
            "04_Visualizaciones.ipynb",
            "05_Modelos_ML.ipynb",
            "06_Dashboard_Interactivo.ipynb",
            "07_Reportes_Automaticos.ipynb",
            "08_APIs_Externas.ipynb",
            "09_Testing_Validacion.ipynb",
            "10_Deployment_Produccion.ipynb"
        ]
        self.resultados = {}
        self.tiempo_inicio = None
        self.tiempo_fin = None
        
    def crear_directorios_necesarios(self):
        """Crear directorios necesarios para el sistema"""
        directorios = [
            'logs',
            'data', 
            'reportes_revision',
            'test_results',
            'tests',
            'app',
            'static',
            'templates',
            'backups'
        ]
        
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
            logger.info(f"[OK] Directorio creado/verificado: {directorio}")
    
    def verificar_dependencias(self):
        """Verificar que las dependencias necesarias estén instaladas"""
        dependencias_criticas = [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 
            'plotly', 'sklearn', 'streamlit', 'requests',
            'yaml', 'jupyter', 'nbconvert'
        ]
        
        dependencias_faltantes = []
        
        for dep in dependencias_criticas:
            try:
                __import__(dep)
                logger.info(f"[OK] Dependencia disponible: {dep}")
            except ImportError:
                dependencias_faltantes.append(dep)
                logger.warning(f"[WARNING] Dependencia faltante: {dep}")
        
        if dependencias_faltantes:
            logger.error(f"[ERROR] Dependencias faltantes: {dependencias_faltantes}")
            logger.info("💡 Instalar con: pip install " + " ".join(dependencias_faltantes))
            return False
        
        return True
    
    def ejecutar_notebook(self, notebook_path, timeout=300):
        """
        Ejecutar un notebook individual usando nbconvert
        """
        logger.info(f"🔄 Ejecutando notebook: {notebook_path}")
        
        try:
            # Comando para ejecutar notebook
            comando = [
                'jupyter', 'nbconvert', 
                '--to', 'notebook',
                '--execute',
                '--inplace',
                '--ExecutePreprocessor.timeout=' + str(timeout),
                str(notebook_path)
            ]
            
            # Ejecutar comando
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=timeout + 60
            )
            
            if resultado.returncode == 0:
                logger.info(f"[OK] Notebook ejecutado exitosamente: {notebook_path}")
                return {
                    'estado': 'exitoso',
                    'tiempo_ejecucion': 0,  # Se calculará después
                    'error': None
                }
            else:
                logger.error(f"[ERROR] Error ejecutando notebook: {notebook_path}")
                logger.error(f"Error: {resultado.stderr}")
                return {
                    'estado': 'error',
                    'tiempo_ejecucion': 0,
                    'error': resultado.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout ejecutando notebook: {notebook_path}")
            return {
                'estado': 'timeout',
                'tiempo_ejecucion': timeout,
                'error': 'Timeout en ejecución'
            }
        except Exception as e:
            logger.error(f"[ERROR] Error inesperado ejecutando notebook: {notebook_path}")
            logger.error(f"Error: {str(e)}")
            return {
                'estado': 'error',
                'tiempo_ejecucion': 0,
                'error': str(e)
            }
    
    def ejecutar_sistema_completo(self, modo='completo'):
        """
        Ejecutar todo el sistema METGO 3D
        
        Args:
            modo (str): 'completo', 'rapido', 'testing', 'deployment'
        """
        logger.info("🚀 INICIANDO EJECUCIÓN DEL SISTEMA METGO 3D")
        logger.info(f"[FECHA] Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🎯 Modo: {modo}")
        logger.info("=" * 60)
        
        self.tiempo_inicio = time.time()
        
        # Crear directorios necesarios
        self.crear_directorios_necesarios()
        
        # Verificar dependencias
        if not self.verificar_dependencias():
            logger.error("[ERROR] No se pueden ejecutar los notebooks sin las dependencias necesarias")
            return False
        
        # Determinar qué notebooks ejecutar según el modo
        notebooks_a_ejecutar = self._determinar_notebooks_modo(modo)
        
        # Ejecutar notebooks
        notebooks_exitosos = 0
        notebooks_con_error = 0
        
        for i, notebook in enumerate(notebooks_a_ejecutar, 1):
            logger.info(f"\n📓 EJECUTANDO NOTEBOOK {i}/{len(notebooks_a_ejecutar)}: {notebook}")
            logger.info("-" * 50)
            
            inicio_notebook = time.time()
            resultado = self.ejecutar_notebook(notebook)
            fin_notebook = time.time()
            
            resultado['tiempo_ejecucion'] = fin_notebook - inicio_notebook
            self.resultados[notebook] = resultado
            
            if resultado['estado'] == 'exitoso':
                notebooks_exitosos += 1
                logger.info(f"[OK] Notebook completado en {resultado['tiempo_ejecucion']:.2f} segundos")
            else:
                notebooks_con_error += 1
                logger.error(f"[ERROR] Notebook falló: {resultado['error']}")
                
                # En modo completo, continuar con el siguiente
                if modo == 'completo':
                    logger.info("🔄 Continuando con el siguiente notebook...")
                else:
                    logger.error("🛑 Deteniendo ejecución por error")
                    break
        
        self.tiempo_fin = time.time()
        tiempo_total = self.tiempo_fin - self.tiempo_inicio
        
        # Generar reporte final
        self._generar_reporte_final(notebooks_exitosos, notebooks_con_error, tiempo_total)
        
        return notebooks_con_error == 0
    
    def _determinar_notebooks_modo(self, modo):
        """Determinar qué notebooks ejecutar según el modo"""
        if modo == 'completo':
            return self.notebooks
        elif modo == 'rapido':
            # Solo notebooks esenciales
            return self.notebooks[:5]
        elif modo == 'testing':
            # Solo notebooks de testing
            return ["09_Testing_Validacion.ipynb"]
        elif modo == 'deployment':
            # Solo notebooks de deployment
            return ["10_Deployment_Produccion.ipynb"]
        elif modo == 'analisis':
            # Solo notebooks de análisis
            return self.notebooks[:4]
        else:
            return self.notebooks
    
    def _generar_reporte_final(self, exitosos, errores, tiempo_total):
        """Generar reporte final de ejecución"""
        logger.info("\n" + "=" * 60)
        logger.info("[ESTADISTICAS] REPORTE FINAL DE EJECUCIÓN")
        logger.info("=" * 60)
        
        logger.info(f"[FECHA] Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[TEMPO] Tiempo total: {tiempo_total:.2f} segundos")
        logger.info(f"[ESTADISTICAS] Notebooks ejecutados: {exitosos + errores}")
        logger.info(f"[OK] Exitosos: {exitosos}")
        logger.info(f"[ERROR] Con errores: {errores}")
        logger.info(f"[ESTADISTICAS] Tasa de exito: {(exitosos/(exitosos+errores)*100):.1f}%")
        
        # Detalles por notebook
        logger.info("\n[DETALLES] DETALLES POR NOTEBOOK:")
        for notebook, resultado in self.resultados.items():
            estado_emoji = "[OK]" if resultado['estado'] == 'exitoso' else "[ERROR]"
            logger.info(f"   {estado_emoji} {notebook}: {resultado['estado']} ({resultado['tiempo_ejecucion']:.2f}s)")
            if resultado['error']:
                logger.info(f"      Error: {resultado['error']}")
        
        # Guardar reporte en archivo
        self._guardar_reporte_json()
        
        if errores == 0:
            logger.info("\n🎉 ¡SISTEMA METGO 3D EJECUTADO EXITOSAMENTE!")
            logger.info("🌾 El sistema está listo para uso agrícola en Quillota")
        else:
            logger.warning(f"\n[WARNING] Sistema ejecutado con {errores} errores")
            logger.info("[REVISION] Revisar logs para detalles de errores")
    
    def _guardar_reporte_json(self):
        """Guardar reporte en formato JSON"""
        try:
            reporte = {
                'fecha_ejecucion': datetime.now().isoformat(),
                'tiempo_total': self.tiempo_fin - self.tiempo_inicio,
                'notebooks_ejecutados': len(self.resultados),
                'notebooks_exitosos': sum(1 for r in self.resultados.values() if r['estado'] == 'exitoso'),
                'notebooks_con_error': sum(1 for r in self.resultados.values() if r['estado'] != 'exitoso'),
                'resultados_detallados': self.resultados
            }
            
            archivo_reporte = Path('logs/reporte_ejecucion.json')
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[REPORTE] Reporte guardado: {archivo_reporte}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando reporte: {e}")

def mostrar_ayuda():
    """Mostrar ayuda del ejecutor"""
    print("""
[SISTEMA] EJECUTOR MAESTRO DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa

USO:
    python ejecutar_sistema_completo.py [MODO]

MODOS DISPONIBLES:
    completo     - Ejecutar todos los notebooks (por defecto)
    rapido      - Ejecutar solo notebooks esenciales
    analisis    - Ejecutar solo notebooks de análisis
    testing     - Ejecutar solo notebooks de testing
    deployment  - Ejecutar solo notebooks de deployment

EJEMPLOS:
    python ejecutar_sistema_completo.py
    python ejecutar_sistema_completo.py completo
    python ejecutar_sistema_completo.py rapido
    python ejecutar_sistema_completo.py testing

CARACTERÍSTICAS:
    [OK] Ejecución automática de todos los notebooks
    [OK] Manejo robusto de errores
    [OK] Logging detallado
    [OK] Reportes de ejecución
    [OK] Verificación de dependencias
    [OK] Múltiples modos de ejecución

REQUISITOS:
    - Python 3.8+
    - Jupyter Notebook
    - Todas las dependencias instaladas (ver requirements.txt)

Para más información, ver DEPLOYMENT.md
""")

def main():
    """Función principal"""
    # Verificar argumentos
    modo = 'completo'
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            mostrar_ayuda()
            return
        modo = sys.argv[1]
    
    # Crear ejecutor
    ejecutor = EjecutorMETGO3D()
    
    # Ejecutar sistema
    try:
        exito = ejecutor.ejecutar_sistema_completo(modo)
        
        if exito:
            print("\n🎉 ¡EJECUCIÓN COMPLETADA EXITOSAMENTE!")
            print("🌾 Sistema METGO 3D listo para uso agrícola")
            sys.exit(0)
        else:
            print("\n[WARNING] Ejecución completada con errores")
            print("[REVISION] Revisar logs para detalles")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Ejecución interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
