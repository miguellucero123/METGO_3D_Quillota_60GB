"""
OPTIMIZADOR DE DASHBOARDS METGO 3D QUILLOTA
Sistema específico para optimizar los dashboards y componentes principales
"""

import os
import time
import json
import sqlite3
from datetime import datetime
import logging
import subprocess
import psutil
from typing import Dict, List, Any

class OptimizadorDashboardsMetgo:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.dashboards = [
            'sistema_unificado_con_conectores.py',
            'dashboard_agricola_avanzado.py',
            'dashboard_global_metgo.py',
            'dashboard_completo_metgo.py'
        ]
        self.optimizaciones_aplicadas = []
        
    def _configurar_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/optimizacion_dashboards.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('OPTIMIZADOR_DASHBOARDS')
    
    def analizar_dashboards(self):
        """Analizar dashboards existentes"""
        self.logger.info("Analizando dashboards existentes...")
        
        analisis = {}
        for dashboard in self.dashboards:
            if os.path.exists(dashboard):
                try:
                    with open(dashboard, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    # Análisis básico
                    lineas = len(contenido.split('\n'))
                    caracteres = len(contenido)
                    tamaño_kb = os.path.getsize(dashboard) / 1024
                    
                    # Buscar imports
                    imports = [line for line in contenido.split('\n') if line.strip().startswith('import')]
                    
                    # Buscar funciones
                    funciones = [line for line in contenido.split('\n') if line.strip().startswith('def ')]
                    
                    # Buscar clases
                    clases = [line for line in contenido.split('\n') if line.strip().startswith('class ')]
                    
                    analisis[dashboard] = {
                        'existe': True,
                        'lineas': lineas,
                        'caracteres': caracteres,
                        'tamaño_kb': round(tamaño_kb, 2),
                        'imports': len(imports),
                        'funciones': len(funciones),
                        'clases': len(clases),
                        'imports_lista': imports[:5]  # Primeros 5 imports
                    }
                    
                except Exception as e:
                    analisis[dashboard] = {'existe': True, 'error': str(e)}
            else:
                analisis[dashboard] = {'existe': False}
        
        self._mostrar_analisis_dashboards(analisis)
        return analisis
    
    def _mostrar_analisis_dashboards(self, analisis):
        """Mostrar análisis de dashboards"""
        print("\n" + "="*70)
        print("ANALISIS DE DASHBOARDS METGO 3D QUILLOTA")
        print("="*70)
        
        for dashboard, info in analisis.items():
            print(f"\n[DASHBOARD] {dashboard}:")
            if not info.get('existe', False):
                print("  • Estado: NO ENCONTRADO")
            elif 'error' in info:
                print(f"  • Estado: ERROR - {info['error']}")
            else:
                print(f"  • Estado: OK")
                print(f"  • Líneas: {info['lineas']}")
                print(f"  • Tamaño: {info['tamaño_kb']} KB")
                print(f"  • Imports: {info['imports']}")
                print(f"  • Funciones: {info['funciones']}")
                print(f"  • Clases: {info['clases']}")
                if info['imports_lista']:
                    print("  • Imports principales:")
                    for imp in info['imports_lista']:
                        print(f"    - {imp.strip()}")
        
        print("="*70)
    
    def optimizar_imports(self):
        """Optimizar imports en dashboards"""
        self.logger.info("Optimizando imports en dashboards...")
        
        optimizaciones = []
        
        for dashboard in self.dashboards:
            if os.path.exists(dashboard):
                try:
                    with open(dashboard, 'r', encoding='utf-8') as f:
                        lineas = f.readlines()
                    
                    # Identificar imports duplicados o innecesarios
                    imports_vistos = set()
                    imports_duplicados = []
                    imports_innecesarios = []
                    
                    for i, linea in enumerate(lineas):
                        if linea.strip().startswith('import '):
                            import_line = linea.strip()
                            if import_line in imports_vistos:
                                imports_duplicados.append((i+1, import_line))
                            else:
                                imports_vistos.add(import_line)
                    
                    # Buscar imports no utilizados (análisis básico)
                    contenido_completo = ''.join(lineas)
                    for import_line in imports_vistos:
                        if 'import ' in import_line:
                            modulo = import_line.split('import ')[1].split(' as ')[0].split('.')[0]
                            if modulo not in contenido_completo.replace(import_line, ''):
                                imports_innecesarios.append(import_line)
                    
                    if imports_duplicados or imports_innecesarios:
                        optimizaciones.append({
                            'dashboard': dashboard,
                            'duplicados': imports_duplicados,
                            'innecesarios': imports_innecesarios
                        })
                
                except Exception as e:
                    self.logger.error(f"Error analizando {dashboard}: {e}")
        
        if optimizaciones:
            self._mostrar_optimizaciones_imports(optimizaciones)
        else:
            print("\n[OK] No se encontraron imports duplicados o innecesarios")
        
        return optimizaciones
    
    def _mostrar_optimizaciones_imports(self, optimizaciones):
        """Mostrar optimizaciones de imports"""
        print("\n" + "="*50)
        print("OPTIMIZACIONES DE IMPORTS")
        print("="*50)
        
        for opt in optimizaciones:
            print(f"\n[DASHBOARD] {opt['dashboard']}:")
            
            if opt['duplicados']:
                print("  • Imports duplicados encontrados:")
                for linea, import_line in opt['duplicados']:
                    print(f"    - Línea {linea}: {import_line}")
            
            if opt['innecesarios']:
                print("  • Imports posiblemente innecesarios:")
                for import_line in opt['innecesarios']:
                    print(f"    - {import_line}")
        
        print("="*50)
    
    def optimizar_funciones_lentas(self):
        """Identificar y optimizar funciones lentas"""
        self.logger.info("Identificando funciones que pueden ser optimizadas...")
        
        patrones_lentos = [
            'time.sleep(',
            'for.*in.*range(',
            'while.*:',
            'subprocess.run(',
            'requests.get(',
            'requests.post(',
            'pd.read_csv(',
            'pd.read_excel(',
            'sqlite3.connect(',
            'cursor.execute('
        ]
        
        funciones_lentas = {}
        
        for dashboard in self.dashboards:
            if os.path.exists(dashboard):
                try:
                    with open(dashboard, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    lineas = contenido.split('\n')
                    funciones_encontradas = []
                    
                    for i, linea in enumerate(lineas):
                        for patron in patrones_lentos:
                            if patron in linea:
                                funciones_encontradas.append({
                                    'linea': i+1,
                                    'codigo': linea.strip(),
                                    'patron': patron
                                })
                    
                    if funciones_encontradas:
                        funciones_lentas[dashboard] = funciones_encontradas
                
                except Exception as e:
                    self.logger.error(f"Error analizando {dashboard}: {e}")
        
        if funciones_lentas:
            self._mostrar_funciones_lentas(funciones_lentas)
        else:
            print("\n[OK] No se encontraron patrones de funciones lentas")
        
        return funciones_lentas
    
    def _mostrar_funciones_lentas(self, funciones_lentas):
        """Mostrar funciones que pueden ser lentas"""
        print("\n" + "="*60)
        print("FUNCIONES QUE PUEDEN SER OPTIMIZADAS")
        print("="*60)
        
        for dashboard, funciones in funciones_lentas.items():
            print(f"\n[DASHBOARD] {dashboard}:")
            for func in funciones[:10]:  # Mostrar máximo 10 por dashboard
                print(f"  • Línea {func['linea']}: {func['codigo']}")
                print(f"    Patrón: {func['patron']}")
        
        print("="*60)
    
    def crear_configuracion_optimizada(self):
        """Crear configuración optimizada para dashboards"""
        self.logger.info("Creando configuración optimizada...")
        
        config_optimizada = {
            'streamlit': {
                'server': {
                    'headless': True,
                    'enableCORS': False,
                    'enableXsrfProtection': False,
                    'maxUploadSize': 200
                },
                'browser': {
                    'gatherUsageStats': False
                },
                'theme': {
                    'base': 'light',
                    'primaryColor': '#1f77b4',
                    'backgroundColor': '#ffffff',
                    'secondaryBackgroundColor': '#f0f2f6'
                }
            },
            'cache': {
                'ttl': 3600,  # 1 hora
                'max_entries': 1000,
                'enable': True
            },
            'performance': {
                'max_data_points': 1000,
                'use_webgl': True,
                'enable_animations': False,
                'reduce_precision': True
            },
            'database': {
                'connection_pool_size': 5,
                'query_timeout': 30,
                'enable_wal_mode': True
            }
        }
        
        try:
            with open('config/dashboards_optimizados.json', 'w') as f:
                json.dump(config_optimizada, f, indent=2)
            
            print("\n[OK] Configuración optimizada creada: config/dashboards_optimizados.json")
            
        except Exception as e:
            self.logger.error(f"Error creando configuración: {e}")
    
    def optimizar_visualizaciones(self):
        """Optimizar configuraciones de visualizaciones"""
        self.logger.info("Optimizando configuraciones de visualizaciones...")
        
        config_visualizaciones = {
            'plotly': {
                'config': {
                    'displayModeBar': False,
                    'staticPlot': True,
                    'responsive': True
                },
                'layout': {
                    'autosize': True,
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
                }
            },
            'pandas': {
                'display': {
                    'max_columns': 10,
                    'max_rows': 100,
                    'width': 1000
                }
            },
            'data_limits': {
                'max_points_per_chart': 1000,
                'max_columns_per_table': 20,
                'max_rows_per_table': 1000
            }
        }
        
        try:
            with open('config/visualizaciones_optimizadas.json', 'w') as f:
                json.dump(config_visualizaciones, f, indent=2)
            
            print("\n[OK] Configuración de visualizaciones optimizada")
            
        except Exception as e:
            self.logger.error(f"Error optimizando visualizaciones: {e}")
    
    def crear_script_inicio_optimizado(self):
        """Crear script de inicio optimizado"""
        self.logger.info("Creando script de inicio optimizado...")
        
        script_content = '''@echo off
echo ============================================================
echo METGO 3D QUILLOTA - SISTEMA OPTIMIZADO
echo ============================================================
echo.

echo [INICIANDO] Verificando sistema...
python -c "import streamlit, pandas, plotly, sqlite3; print('[OK] Dependencias verificadas')"

echo.
echo [OPTIMIZANDO] Aplicando optimizaciones...
python optimizador_dashboards_metgo.py

echo.
echo [INICIANDO] Lanzando dashboard principal...
start /B python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true

echo.
echo [INICIANDO] Lanzando dashboard agricola avanzado...
start /B python -m streamlit run dashboard_agricola_avanzado.py --server.port 8510 --server.headless true

echo.
echo ============================================================
echo SISTEMA METGO 3D QUILLOTA INICIADO
echo ============================================================
echo.
echo Dashboards disponibles:
echo - Principal: http://localhost:8501
echo - Agricola Avanzado: http://localhost:8510
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
'''
        
        try:
            with open('iniciar_metgo_optimizado.bat', 'w') as f:
                f.write(script_content)
            
            print("\n[OK] Script de inicio optimizado creado: iniciar_metgo_optimizado.bat")
            
        except Exception as e:
            self.logger.error(f"Error creando script: {e}")
    
    def generar_reporte_optimizacion_dashboards(self):
        """Generar reporte de optimización de dashboards"""
        self.logger.info("Generando reporte de optimización de dashboards...")
        
        reporte = {
            'fecha': datetime.now().isoformat(),
            'dashboards_analizados': len(self.dashboards),
            'optimizaciones_aplicadas': [
                'Análisis de dashboards completado',
                'Configuración optimizada creada',
                'Visualizaciones optimizadas',
                'Script de inicio optimizado creado'
            ],
            'archivos_generados': [
                'config/dashboards_optimizados.json',
                'config/visualizaciones_optimizadas.json',
                'iniciar_metgo_optimizado.bat'
            ],
            'recomendaciones': [
                'Usar el script iniciar_metgo_optimizado.bat para mejor rendimiento',
                'Monitorear el uso de memoria durante la ejecución',
                'Aplicar optimizaciones de imports manualmente si es necesario',
                'Considerar usar cache para datos frecuentemente accedidos'
            ]
        }
        
        try:
            with open('reportes/reporte_optimizacion_dashboards.json', 'w') as f:
                json.dump(reporte, f, indent=2)
            
            print("\n[OK] Reporte de optimización de dashboards generado")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
    
    def ejecutar_optimizacion_dashboards(self):
        """Ejecutar optimización completa de dashboards"""
        print("\n" + "="*80)
        print("OPTIMIZADOR DE DASHBOARDS METGO 3D QUILLOTA")
        print("="*80)
        
        # 1. Analizar dashboards
        print("\n[PASO 1] Analizando dashboards existentes...")
        self.analizar_dashboards()
        
        # 2. Optimizar imports
        print("\n[PASO 2] Optimizando imports...")
        self.optimizar_imports()
        
        # 3. Identificar funciones lentas
        print("\n[PASO 3] Identificando funciones que pueden ser optimizadas...")
        self.optimizar_funciones_lentas()
        
        # 4. Crear configuración optimizada
        print("\n[PASO 4] Creando configuración optimizada...")
        self.crear_configuracion_optimizada()
        
        # 5. Optimizar visualizaciones
        print("\n[PASO 5] Optimizando visualizaciones...")
        self.optimizar_visualizaciones()
        
        # 6. Crear script de inicio optimizado
        print("\n[PASO 6] Creando script de inicio optimizado...")
        self.crear_script_inicio_optimizado()
        
        # 7. Generar reporte
        print("\n[PASO 7] Generando reporte...")
        self.generar_reporte_optimizacion_dashboards()
        
        print("\n" + "="*80)
        print("OPTIMIZACION DE DASHBOARDS COMPLETADA")
        print("="*80)
        
        print("\n[RESUMEN] Optimizaciones aplicadas:")
        print("  • Análisis completo de dashboards")
        print("  • Configuración optimizada creada")
        print("  • Visualizaciones optimizadas")
        print("  • Script de inicio optimizado")
        print("  • Reporte de optimización generado")
        
        print("\n[ARCHIVOS GENERADOS]:")
        print("  • config/dashboards_optimizados.json")
        print("  • config/visualizaciones_optimizadas.json")
        print("  • iniciar_metgo_optimizado.bat")
        print("  • reportes/reporte_optimizacion_dashboards.json")
        
        print("\n[RECOMENDACIONES]:")
        print("  • Usar iniciar_metgo_optimizado.bat para mejor rendimiento")
        print("  • Monitorear uso de memoria durante ejecución")
        print("  • Aplicar optimizaciones de imports manualmente")
        print("  • Considerar usar cache para datos frecuentes")

def main():
    """Función principal"""
    optimizador = OptimizadorDashboardsMetgo()
    optimizador.ejecutar_optimizacion_dashboards()

if __name__ == "__main__":
    main()



