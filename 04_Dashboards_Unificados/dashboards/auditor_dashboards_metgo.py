"""
AUDITOR DE DASHBOARDS METGO 3D
Script para revisar todos los dashboards del proyecto y identificar cuáles funcionan correctamente
"""

import os
import sys
import subprocess
import time
import requests
import ast
import re
from pathlib import Path
from datetime import datetime

class AuditorDashboards:
    def __init__(self):
        self.directorio_actual = os.getcwd()
        self.dashboards_encontrados = []
        self.dashboards_funcionando = []
        self.dashboards_con_errores = []
        self.dashboards_obsoletos = []
        
    def encontrar_todos_los_dashboards(self):
        """Encontrar todos los archivos de dashboard en el proyecto"""
        print("BUSCANDO TODOS LOS DASHBOARDS EN EL PROYECTO")
        print("=" * 60)
        
        patrones = ["dashboard_*.py", "*_dashboard*.py"]
        
        for patron in patrones:
            archivos = list(Path(self.directorio_actual).glob(patron))
            for archivo in archivos:
                if archivo.is_file():
                    self.dashboards_encontrados.append(str(archivo.name))
        
        # Eliminar duplicados
        self.dashboards_encontrados = list(set(self.dashboards_encontrados))
        self.dashboards_encontrados.sort()
        
        print(f"Se encontraron {len(self.dashboards_encontrados)} dashboards:")
        for i, dashboard in enumerate(self.dashboards_encontrados, 1):
            print(f"{i:2d}. {dashboard}")
        
        return self.dashboards_encontrados
    
    def analizar_estructura_dashboard(self, archivo):
        """Analizar la estructura básica de un dashboard"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar elementos básicos
            elementos = {
                'streamlit_import': 'import streamlit' in contenido,
                'st_set_page_config': 'st.set_page_config' in contenido,
                'main_function': 'def main(' in contenido or '__main__' in contenido,
                'plotly': 'import plotly' in contenido,
                'pandas': 'import pandas' in contenido,
                'sqlite': 'sqlite3' in contenido,
                'errores_conocidos': []
            }
            
            # Buscar errores conocidos
            if '.dt.strftime' in contenido and 'pd.to_datetime' not in contenido:
                elementos['errores_conocidos'].append('Posible error .dt accessor sin conversión datetime')
            
            if 'use_container_width' in contenido:
                elementos['errores_conocidos'].append('use_container_width deprecado')
            
            if 'st.experimental_rerun' in contenido:
                elementos['errores_conocidos'].append('st.experimental_rerun deprecado')
            
            return elementos
            
        except Exception as e:
            return {'error': f'Error leyendo archivo: {e}'}
    
    def verificar_dashboard_funcional(self, archivo):
        """Verificar si un dashboard puede ejecutarse sin errores de sintaxis"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar sintaxis básica
            ast.parse(contenido)
            
            # Verificar imports críticos
            imports_criticos = ['streamlit', 'pandas']
            for imp in imports_criticos:
                if f'import {imp}' not in contenido and f'from {imp}' not in contenido:
                    return False, f'Falta import de {imp}'
            
            return True, 'Sintaxis OK'
            
        except SyntaxError as e:
            return False, f'Error de sintaxis: {e}'
        except Exception as e:
            return False, f'Error: {e}'
    
    def probar_ejecucion_dashboard(self, archivo, puerto):
        """Probar la ejecución de un dashboard en un puerto específico"""
        try:
            print(f"Probando {archivo} en puerto {puerto}...")
            
            # Comando para ejecutar el dashboard
            command = [
                sys.executable, "-m", "streamlit", "run",
                archivo,
                "--server.port", str(puerto),
                "--server.headless", "true"
            ]
            
            # Ejecutar en background
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)  # Esperar a que se inicie
            
            # Verificar si está funcionando
            try:
                response = requests.get(f"http://localhost:{puerto}/_stcore/health", timeout=3)
                if response.status_code == 200:
                    process.terminate()
                    return True, 'Dashboard ejecutándose correctamente'
                else:
                    process.terminate()
                    return False, 'Dashboard no responde correctamente'
            except:
                process.terminate()
                return False, 'Dashboard no se pudo iniciar'
                
        except Exception as e:
            return False, f'Error ejecutando: {e}'
    
    def categorizar_dashboards(self):
        """Categorizar los dashboards por funcionalidad y estado"""
        categorias = {
            'meteorologicos': [],
            'agricolas': [],
            'principales': [],
            'especializados': [],
            'obsoletos': []
        }
        
        for dashboard in self.dashboards_encontrados:
            nombre_lower = dashboard.lower()
            
            if 'meteorologico' in nombre_lower:
                categorias['meteorologicos'].append(dashboard)
            elif 'agricola' in nombre_lower:
                categorias['agricolas'].append(dashboard)
            elif 'principal' in nombre_lower or 'central' in nombre_lower:
                categorias['principales'].append(dashboard)
            elif any(x in nombre_lower for x in ['drones', 'ml_', 'modelos', 'economico']):
                categorias['especializados'].append(dashboard)
            else:
                categorias['obsoletos'].append(dashboard)
        
        return categorias
    
    def generar_reporte_completo(self):
        """Generar reporte completo de todos los dashboards"""
        print("\n" + "="*80)
        print("REPORTE COMPLETO DE DASHBOARDS METGO 3D")
        print("="*80)
        
        # 1. Encontrar todos los dashboards
        self.encontrar_todos_los_dashboards()
        
        # 2. Categorizar dashboards
        categorias = self.categorizar_dashboards()
        
        print(f"\nCATEGORIZACIÓN DE DASHBOARDS:")
        print("-" * 40)
        for categoria, dashboards in categorias.items():
            print(f"{categoria.upper()}: {len(dashboards)} dashboards")
            for dashboard in dashboards:
                print(f"  - {dashboard}")
        
        # 3. Analizar cada dashboard
        print(f"\nANÁLISIS DETALLADO DE DASHBOARDS:")
        print("-" * 50)
        
        for dashboard in self.dashboards_encontrados:
            print(f"\n📊 {dashboard}")
            print("-" * (len(dashboard) + 4))
            
            # Análisis de estructura
            estructura = self.analizar_estructura_dashboard(dashboard)
            if 'error' in estructura:
                print(f"❌ {estructura['error']}")
                continue
            
            # Verificar funcionalidad
            funcional, mensaje = self.verificar_dashboard_funcional(dashboard)
            if funcional:
                print(f"✅ Sintaxis: OK")
            else:
                print(f"❌ Sintaxis: {mensaje}")
            
            # Mostrar elementos encontrados
            elementos_ok = [k for k, v in estructura.items() if v is True]
            elementos_error = estructura.get('errores_conocidos', [])
            
            print(f"📋 Elementos: {', '.join(elementos_ok)}")
            if elementos_error:
                print(f"⚠️  Problemas: {', '.join(elementos_error)}")
        
        # 4. Recomendaciones
        print(f"\nRECOMENDACIONES:")
        print("-" * 20)
        
        # Identificar dashboards principales recomendados
        dashboards_recomendados = []
        
        # Dashboard meteorológico
        meteorologicos = [d for d in categorias['meteorologicos'] if 'final' in d.lower()]
        if meteorologicos:
            dashboards_recomendados.extend(meteorologicos)
        else:
            dashboards_recomendados.extend(categorias['meteorologicos'][:1])
        
        # Dashboard agrícola
        if categorias['agricolas']:
            dashboards_recomendados.extend(categorias['agricolas'][:1])
        
        # Dashboard principal
        if categorias['principales']:
            dashboards_recomendados.extend(categorias['principales'][:1])
        
        print("🎯 DASHBOARDS RECOMENDADOS PARA USO:")
        for dashboard in dashboards_recomendados:
            print(f"  ✅ {dashboard}")
        
        print("\n🗑️  DASHBOARDS QUE PODRÍAN SER OBSOLETOS:")
        for categoria, dashboards in categorias.items():
            if categoria == 'obsoletos' or len(dashboards) > 2:
                for dashboard in dashboards[2:]:  # Mantener solo los primeros 2
                    print(f"  ❓ {dashboard}")
        
        return {
            'total_dashboards': len(self.dashboards_encontrados),
            'categorias': categorias,
            'recomendados': dashboards_recomendados,
            'estructura_analisis': estructura
        }

def main():
    auditor = AuditorDashboards()
    resultado = auditor.generar_reporte_completo()
    
    print(f"\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"Total de dashboards encontrados: {resultado['total_dashboards']}")
    print(f"Dashboards recomendados: {len(resultado['recomendados'])}")
    
    print(f"\nPara usar el sistema, recomiendo estos dashboards:")
    for dashboard in resultado['recomendados']:
        print(f"  🎯 {dashboard}")

if __name__ == "__main__":
    main()


