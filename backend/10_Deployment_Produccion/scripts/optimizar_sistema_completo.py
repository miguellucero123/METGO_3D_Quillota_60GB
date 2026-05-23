#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR SISTEMA COMPLETO - METGO 3D
Script principal para optimizacion y estabilizacion del sistema
"""

import os
import sys
import time
import logging
from datetime import datetime

# Importar modulos de optimizacion
from fix_ml_models import MLModelsFixer
from optimizar_disco import OptimizadorDisco
from fix_streamlit_errors import StreamlitErrorFixer

class OptimizadorSistemaCompleto:
    """Optimizador completo del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('SISTEMA_OPTIMIZER')
        self.inicio = datetime.now()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('optimizacion.log'),
                logging.StreamHandler()
            ]
        )
    
    def ejecutar_optimizacion_completa(self):
        """Ejecutar optimizacion completa del sistema"""
        try:
            self.logger.info("=" * 70)
            self.logger.info("INICIANDO OPTIMIZACION COMPLETA DEL SISTEMA METGO 3D")
            self.logger.info("=" * 70)
            
            resultados = {
                'inicio': self.inicio.isoformat(),
                'pasos_completados': [],
                'errores': [],
                'estadisticas': {}
            }
            
            # PASO 1: Corregir modelos de ML
            self.logger.info("\nPASO 1: Corrigiendo modelos de Machine Learning...")
            try:
                ml_fixer = MLModelsFixer()
                resultado_ml = ml_fixer.entrenar_todos_los_modelos()
                
                if 'error' not in resultado_ml:
                    resultados['pasos_completados'].append('ML_Models_Fixed')
                    resultados['estadisticas']['modelos_entrenados'] = len(resultado_ml)
                    self.logger.info(f"Modelos ML corregidos: {len(resultado_ml)}")
                else:
                    resultados['errores'].append(f"ML_Error: {resultado_ml['error']}")
                    
            except Exception as e:
                resultados['errores'].append(f"ML_Exception: {str(e)}")
                self.logger.error(f"Error en paso 1: {e}")
            
            # PASO 2: Optimizar uso de disco
            self.logger.info("\nPASO 2: Optimizando uso de disco...")
            try:
                disk_optimizer = OptimizadorDisco()
                resultado_disco = disk_optimizer.optimizar_completo()
                
                if 'error' not in resultado_disco:
                    resultados['pasos_completados'].append('Disk_Optimized')
                    resultados['estadisticas']['espacio_liberado_mb'] = resultado_disco['espacio_liberado_mb']
                    resultados['estadisticas']['archivos_eliminados'] = resultado_disco['archivos_eliminados']
                    self.logger.info(f"Disco optimizado: {resultado_disco['espacio_liberado_mb']:.2f} MB liberados")
                else:
                    resultados['errores'].append(f"Disk_Error: {resultado_disco['error']}")
                    
            except Exception as e:
                resultados['errores'].append(f"Disk_Exception: {str(e)}")
                self.logger.error(f"Error en paso 2: {e}")
            
            # PASO 3: Corregir errores de Streamlit
            self.logger.info("\nPASO 3: Corrigiendo errores de Streamlit...")
            try:
                streamlit_fixer = StreamlitErrorFixer()
                if streamlit_fixer.corregir_todos_los_errores():
                    resultados['pasos_completados'].append('Streamlit_Fixed')
                    self.logger.info("Errores de Streamlit corregidos")
                else:
                    resultados['errores'].append("Streamlit_Error: No se pudieron corregir todos los errores")
                    
            except Exception as e:
                resultados['errores'].append(f"Streamlit_Exception: {str(e)}")
                self.logger.error(f"Error en paso 3: {e}")
            
            # PASO 4: Verificar sistema
            self.logger.info("\nPASO 4: Verificando estado del sistema...")
            try:
                estado_sistema = self.verificar_estado_sistema()
                resultados['estadisticas']['estado_sistema'] = estado_sistema
                resultados['pasos_completados'].append('System_Verified')
                self.logger.info("Estado del sistema verificado")
                
            except Exception as e:
                resultados['errores'].append(f"Verification_Exception: {str(e)}")
                self.logger.error(f"Error en paso 4: {e}")
            
            # Finalizar
            fin = datetime.now()
            duracion = (fin - self.inicio).total_seconds()
            
            resultados['fin'] = fin.isoformat()
            resultados['duracion_segundos'] = duracion
            resultados['pasos_totales'] = len(resultados['pasos_completados'])
            resultados['errores_totales'] = len(resultados['errores'])
            
            # Generar reporte
            self.generar_reporte_optimizacion(resultados)
            
            self.logger.info("=" * 70)
            self.logger.info("OPTIMIZACION COMPLETA FINALIZADA")
            self.logger.info(f"Duracion: {duracion:.2f} segundos")
            self.logger.info(f"Pasos completados: {resultados['pasos_totales']}")
            self.logger.info(f"Errores: {resultados['errores_totales']}")
            self.logger.info("=" * 70)
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error en optimizacion completa: {e}")
            return {'error': str(e)}
    
    def verificar_estado_sistema(self):
        """Verificar estado actual del sistema"""
        try:
            estado = {
                'archivos_python': len([f for f in os.listdir('.') if f.endswith('.py')]),
                'notebooks': len([f for f in os.listdir('.') if f.endswith('.ipynb')]),
                'modelos_ml': len([f for f in os.listdir('modelos_ml_quillota') if f.endswith('.joblib')]) if os.path.exists('modelos_ml_quillota') else 0,
                'directorio_data': os.path.exists('data'),
                'directorio_config': os.path.exists('config'),
                'archivo_principal': os.path.exists('sistema_unificado_con_conectores.py')
            }
            
            return estado
            
        except Exception as e:
            self.logger.error(f"Error verificando estado: {e}")
            return {'error': str(e)}
    
    def generar_reporte_optimizacion(self, resultados):
        """Generar reporte de optimizacion"""
        try:
            reporte_path = f"reporte_optimizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE OPTIMIZACION - METGO 3D\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Fecha: {resultados['inicio']}\n")
                f.write(f"Duracion: {resultados['duracion_segundos']:.2f} segundos\n\n")
                
                f.write("PASOS COMPLETADOS:\n")
                f.write("-" * 20 + "\n")
                for paso in resultados['pasos_completados']:
                    f.write(f"✓ {paso}\n")
                
                f.write("\nERRORES ENCONTRADOS:\n")
                f.write("-" * 20 + "\n")
                if resultados['errores']:
                    for error in resultados['errores']:
                        f.write(f"✗ {error}\n")
                else:
                    f.write("Ningun error encontrado\n")
                
                f.write("\nESTADISTICAS:\n")
                f.write("-" * 15 + "\n")
                for key, value in resultados['estadisticas'].items():
                    f.write(f"{key}: {value}\n")
            
            self.logger.info(f"Reporte generado: {reporte_path}")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")

def main():
    """Funcion principal"""
    print("OPTIMIZADOR SISTEMA COMPLETO - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear optimizador
        optimizer = OptimizadorSistemaCompleto()
        
        # Ejecutar optimizacion completa
        print("\nIniciando optimizacion completa del sistema...")
        resultado = optimizer.ejecutar_optimizacion_completa()
        
        if 'error' in resultado:
            print(f"\nError en optimizacion: {resultado['error']}")
            return False
        
        print(f"\nOptimizacion completada en {resultado['duracion_segundos']:.2f} segundos")
        print(f"Pasos completados: {resultado['pasos_totales']}")
        print(f"Errores: {resultado['errores_totales']}")
        
        if resultado['errores_totales'] == 0:
            print("\nSistema optimizado exitosamente - Sin errores")
        else:
            print(f"\nSistema optimizado con {resultado['errores_totales']} errores")
        
        return True
        
    except Exception as e:
        print(f"\nError en optimizacion: {e}")
        return False

if __name__ == "__main__":
    main()
