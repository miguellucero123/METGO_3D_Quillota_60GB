#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 RUNNER DE TESTS METGO 3D
Sistema Meteorológico Agrícola Quillota - Ejecutor de Tests
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
import argparse

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

class TestRunnerMETGO:
    """Runner para ejecutar todos los tests del sistema METGO 3D"""
    
    def __init__(self):
        self.directorio_tests = Path(__file__).parent
        self.directorio_reportes = Path("reportes/tests")
        self.directorio_reportes.mkdir(parents=True, exist_ok=True)
        
        self.resultados = {
            'timestamp': datetime.now().isoformat(),
            'sistema': 'METGO 3D - Tests',
            'version': '2.0',
            'tests_ejecutados': 0,
            'tests_exitosos': 0,
            'tests_fallidos': 0,
            'tests_omitidos': 0,
            'tiempo_total': 0,
            'detalles': []
        }
    
    def descubrir_tests(self):
        """Descubrir todos los archivos de test"""
        archivos_test = []
        
        # Buscar archivos de test
        for archivo in self.directorio_tests.glob("test_*.py"):
            if archivo.name != "runner_tests.py":
                archivos_test.append(archivo)
        
        return archivos_test
    
    def ejecutar_tests_individuales(self, archivos_test, verbosity=2):
        """Ejecutar tests individuales"""
        print(f"\n🧪 Ejecutando {len(archivos_test)} archivos de test...")
        
        for archivo_test in archivos_test:
            print(f"\n📋 Ejecutando: {archivo_test.name}")
            
            # Crear suite de tests
            loader = unittest.TestLoader()
            suite = loader.discover(
                start_dir=str(self.directorio_tests),
                pattern=archivo_test.name,
                top_level_dir=str(self.directorio_tests.parent)
            )
            
            # Ejecutar tests
            runner = unittest.TextTestRunner(verbosity=verbosity)
            resultado = runner.run(suite)
            
            # Registrar resultados
            self.resultados['tests_ejecutados'] += resultado.testsRun
            self.resultados['tests_exitosos'] += resultado.testsRun - len(resultado.failures) - len(resultado.errors)
            self.resultados['tests_fallidos'] += len(resultado.failures) + len(resultado.errors)
            self.resultados['tests_omitidos'] += len(resultado.skipped)
            
            # Detalles del archivo
            detalle = {
                'archivo': archivo_test.name,
                'tests_ejecutados': resultado.testsRun,
                'tests_exitosos': resultado.testsRun - len(resultado.failures) - len(resultado.errors),
                'tests_fallidos': len(resultado.failures) + len(resultado.errors),
                'tests_omitidos': len(resultado.skipped),
                'fallos': [str(f[1]) for f in resultado.failures],
                'errores': [str(e[1]) for e in resultado.errors],
                'omitidos': [str(s[1]) for s in resultado.skipped]
            }
            
            self.resultados['detalles'].append(detalle)
            
            # Mostrar resumen del archivo
            if resultado.wasSuccessful():
                print(f"✅ {archivo_test.name}: {resultado.testsRun} tests exitosos")
            else:
                print(f"❌ {archivo_test.name}: {len(resultado.failures)} fallos, {len(resultado.errors)} errores")
    
    def ejecutar_tests_completos(self, verbosity=2):
        """Ejecutar todos los tests del sistema"""
        print(f"\n🧪 Ejecutando todos los tests del sistema...")
        
        # Crear suite de tests
        loader = unittest.TestLoader()
        suite = loader.discover(
            start_dir=str(self.directorio_tests),
            pattern="test_*.py",
            top_level_dir=str(self.directorio_tests.parent)
        )
        
        # Ejecutar tests
        runner = unittest.TextTestRunner(verbosity=verbosity)
        resultado = runner.run(suite)
        
        # Registrar resultados
        self.resultados['tests_ejecutados'] = resultado.testsRun
        self.resultados['tests_exitosos'] = resultado.testsRun - len(resultado.failures) - len(resultado.errors)
        self.resultados['tests_fallidos'] = len(resultado.failures) + len(resultado.errors)
        self.resultados['tests_omitidos'] = len(resultado.skipped)
        
        # Detalles generales
        self.resultados['detalles'] = {
            'fallos': [str(f[1]) for f in resultado.failures],
            'errores': [str(e[1]) for e in resultado.errors],
            'omitidos': [str(s[1]) for s in resultado.skipped]
        }
        
        return resultado
    
    def ejecutar_tests_por_categoria(self, categoria, verbosity=2):
        """Ejecutar tests por categoría"""
        categorias = {
            'unitarios': ['test_ia_avanzada.py', 'test_sistema_iot.py'],
            'integracion': ['test_integracion_completa.py'],
            'rendimiento': ['test_rendimiento.py'],
            'todos': ['test_*.py']
        }
        
        if categoria not in categorias:
            print(f"❌ Categoría no válida: {categoria}")
            print(f"Categorías disponibles: {list(categorias.keys())}")
            return None
        
        print(f"\n🧪 Ejecutando tests de categoría: {categoria}")
        
        if categoria == 'todos':
            return self.ejecutar_tests_completos(verbosity)
        
        archivos_test = categorias[categoria]
        archivos_encontrados = []
        
        for patron in archivos_test:
            if '*' in patron:
                # Buscar archivos que coincidan con el patrón
                for archivo in self.directorio_tests.glob(patron):
                    if archivo.name != "runner_tests.py":
                        archivos_encontrados.append(archivo)
            else:
                # Archivo específico
                archivo = self.directorio_tests / patron
                if archivo.exists():
                    archivos_encontrados.append(archivo)
        
        if not archivos_encontrados:
            print(f"❌ No se encontraron archivos de test para la categoría: {categoria}")
            return None
        
        return self.ejecutar_tests_individuales(archivos_encontrados, verbosity)
    
    def generar_reporte_tests(self):
        """Generar reporte de tests"""
        try:
            print(f"\n📋 Generando reporte de tests...")
            
            # Calcular métricas
            total_tests = self.resultados['tests_ejecutados']
            exitosos = self.resultados['tests_exitosos']
            fallidos = self.resultados['tests_fallidos']
            omitidos = self.resultados['tests_omitidos']
            
            if total_tests > 0:
                tasa_exito = (exitosos / total_tests) * 100
                tasa_fallo = (fallidos / total_tests) * 100
                tasa_omision = (omitidos / total_tests) * 100
            else:
                tasa_exito = tasa_fallo = tasa_omision = 0
            
            # Agregar métricas al reporte
            self.resultados['metricas'] = {
                'tasa_exito': tasa_exito,
                'tasa_fallo': tasa_fallo,
                'tasa_omision': tasa_omision,
                'estado_general': 'EXITOSO' if fallidos == 0 else 'FALLIDO'
            }
            
            # Agregar recomendaciones
            recomendaciones = []
            
            if fallidos > 0:
                recomendaciones.append("Revisar y corregir los tests fallidos")
                recomendaciones.append("Verificar la configuración del entorno de testing")
            
            if omitidos > 0:
                recomendaciones.append("Investigar por qué algunos tests fueron omitidos")
                recomendaciones.append("Verificar dependencias y configuraciones")
            
            if tasa_exito < 80:
                recomendaciones.append("La tasa de éxito es baja, revisar la calidad del código")
            elif tasa_exito >= 95:
                recomendaciones.append("Excelente tasa de éxito, mantener la calidad del código")
            
            recomendaciones.extend([
                "Ejecutar tests regularmente durante el desarrollo",
                "Mantener cobertura de tests alta",
                "Documentar casos de test complejos",
                "Automatizar la ejecución de tests en CI/CD"
            ])
            
            self.resultados['recomendaciones'] = recomendaciones
            
            # Guardar reporte
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_reporte = self.directorio_reportes / f"reporte_tests_{timestamp}.json"
            
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte de tests generado: {archivo_reporte}")
            return str(archivo_reporte)
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return ""
    
    def mostrar_resumen(self):
        """Mostrar resumen de resultados"""
        print(f"\n📊 RESUMEN DE TESTS")
        print(f"=" * 50)
        
        total = self.resultados['tests_ejecutados']
        exitosos = self.resultados['tests_exitosos']
        fallidos = self.resultados['tests_fallidos']
        omitidos = self.resultados['tests_omitidos']
        
        print(f"Tests ejecutados: {total}")
        print(f"Tests exitosos: {exitosos}")
        print(f"Tests fallidos: {fallidos}")
        print(f"Tests omitidos: {omitidos}")
        
        if total > 0:
            tasa_exito = (exitosos / total) * 100
            print(f"Tasa de éxito: {tasa_exito:.1f}%")
            
            if fallidos == 0:
                print(f"🎉 ¡Todos los tests pasaron exitosamente!")
            else:
                print(f"⚠️ {fallidos} tests fallaron")
        
        print(f"Tiempo total: {self.resultados['tiempo_total']:.2f} segundos")
    
    def ejecutar(self, categoria='todos', verbosity=2):
        """Ejecutar tests según la categoría especificada"""
        try:
            inicio = time.time()
            
            print(f"🧪 RUNNER DE TESTS METGO 3D")
            print(f"Sistema Meteorológico Agrícola Quillota")
            print(f"=" * 50)
            
            # Ejecutar tests
            if categoria == 'todos':
                resultado = self.ejecutar_tests_completos(verbosity)
            else:
                resultado = self.ejecutar_tests_por_categoria(categoria, verbosity)
            
            if resultado is None:
                return False
            
            # Calcular tiempo total
            fin = time.time()
            self.resultados['tiempo_total'] = fin - inicio
            
            # Mostrar resumen
            self.mostrar_resumen()
            
            # Generar reporte
            reporte = self.generar_reporte_tests()
            
            if reporte:
                print(f"\n📄 Reporte detallado: {reporte}")
            
            return resultado.wasSuccessful()
            
        except Exception as e:
            print(f"\n❌ Error ejecutando tests: {e}")
            return False

def main():
    """Función principal del runner de tests"""
    parser = argparse.ArgumentParser(description='Runner de Tests METGO 3D')
    parser.add_argument('--categoria', '-c', 
                       choices=['unitarios', 'integracion', 'rendimiento', 'todos'],
                       default='todos',
                       help='Categoría de tests a ejecutar')
    parser.add_argument('--verbosity', '-v',
                       type=int,
                       choices=[0, 1, 2],
                       default=2,
                       help='Nivel de verbosidad (0=minimal, 1=normal, 2=verbose)')
    parser.add_argument('--archivo', '-f',
                       help='Archivo específico de test a ejecutar')
    
    args = parser.parse_args()
    
    try:
        runner = TestRunnerMETGO()
        
        if args.archivo:
            # Ejecutar archivo específico
            archivo_test = Path("tests") / args.archivo
            if archivo_test.exists():
                print(f"🧪 Ejecutando archivo específico: {args.archivo}")
                resultado = runner.ejecutar_tests_individuales([archivo_test], args.verbosity)
                runner.mostrar_resumen()
                return resultado
            else:
                print(f"❌ Archivo no encontrado: {args.archivo}")
                return False
        else:
            # Ejecutar por categoría
            return runner.ejecutar(args.categoria, args.verbosity)
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
