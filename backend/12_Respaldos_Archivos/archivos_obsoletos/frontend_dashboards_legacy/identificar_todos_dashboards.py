"""
IDENTIFICADOR COMPLETO DE DASHBOARDS METGO 3D
Script para identificar todos los dashboards del proyecto (Python y HTML)
"""

import os
import glob
from pathlib import Path

def identificar_todos_los_dashboards():
    """Identificar todos los dashboards del proyecto"""
    
    print("IDENTIFICACIÓN COMPLETA DE DASHBOARDS METGO 3D")
    print("=" * 60)
    
    # Buscar dashboards Python
    dashboards_python = glob.glob("dashboard_*.py")
    dashboards_python.sort()
    
    # Buscar dashboards HTML
    dashboards_html = glob.glob("*.html")
    dashboards_html = [d for d in dashboards_html if 'dashboard' in d.lower()]
    dashboards_html.sort()
    
    # Buscar otros dashboards en subdirectorios
    dashboards_html_subdirs = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') and 'dashboard' in file.lower():
                rel_path = os.path.relpath(os.path.join(root, file))
                dashboards_html_subdirs.append(rel_path)
    
    dashboards_html_subdirs.sort()
    
    print(f"📊 DASHBOARDS PYTHON (.py): {len(dashboards_python)}")
    print("-" * 40)
    for i, dashboard in enumerate(dashboards_python, 1):
        print(f"{i:2d}. {dashboard}")
    
    print(f"\n🌐 DASHBOARDS HTML (.html): {len(dashboards_html)}")
    print("-" * 40)
    for i, dashboard in enumerate(dashboards_html, 1):
        print(f"{i:2d}. {dashboard}")
    
    print(f"\n📁 DASHBOARDS HTML EN SUBDIRECTORIOS: {len(dashboards_html_subdirs)}")
    print("-" * 40)
    for i, dashboard in enumerate(dashboards_html_subdirs, 1):
        print(f"{i:2d}. {dashboard}")
    
    # Categorizar dashboards
    categorias = {
        'meteorologicos': [],
        'agricolas': [],
        'economicos': [],
        'drones': [],
        'reportes': [],
        'integracion': [],
        'otros': []
    }
    
    todos_los_dashboards = dashboards_python + dashboards_html + dashboards_html_subdirs
    
    for dashboard in todos_los_dashboards:
        nombre_lower = dashboard.lower()
        
        if any(x in nombre_lower for x in ['meteorologico', 'weather', 'climate']):
            categorias['meteorologicos'].append(dashboard)
        elif any(x in nombre_lower for x in ['agricola', 'agriculture', 'crop', 'cultivo']):
            categorias['agricolas'].append(dashboard)
        elif any(x in nombre_lower for x in ['economico', 'roi', 'van', 'tir', 'cost']):
            categorias['economicos'].append(dashboard)
        elif any(x in nombre_lower for x in ['drone', 'satelital', 'aereo']):
            categorias['drones'].append(dashboard)
        elif any(x in nombre_lower for x in ['reporte', 'report', 'analisis']):
            categorias['reportes'].append(dashboard)
        elif any(x in nombre_lower for x in ['integracion', 'unificado', 'sistema', 'global']):
            categorias['integracion'].append(dashboard)
        else:
            categorias['otros'].append(dashboard)
    
    print(f"\n📋 CATEGORIZACIÓN DE DASHBOARDS:")
    print("=" * 40)
    
    for categoria, dashboards in categorias.items():
        if dashboards:
            print(f"\n{categoria.upper()}: {len(dashboards)} dashboards")
            for dashboard in dashboards:
                print(f"  - {dashboard}")
    
    # Identificar dashboards que NO están integrados
    dashboards_integrados = [
        'dashboard_meteorologico_final.py',
        'dashboard_agricola_avanzado.py',
        'dashboard_principal_integrado_metgo.py',
        'dashboard_maestro_unificado_metgo.py'
    ]
    
    dashboards_no_integrados = []
    for dashboard in todos_los_dashboards:
        if dashboard not in dashboards_integrados:
            dashboards_no_integrados.append(dashboard)
    
    print(f"\n❌ DASHBOARDS NO INTEGRADOS: {len(dashboards_no_integrados)}")
    print("=" * 50)
    for i, dashboard in enumerate(dashboards_no_integrados, 1):
        print(f"{i:2d}. {dashboard}")
    
    return {
        'python': dashboards_python,
        'html': dashboards_html,
        'html_subdirs': dashboards_html_subdirs,
        'categorias': categorias,
        'no_integrados': dashboards_no_integrados,
        'total': len(todos_los_dashboards)
    }

def generar_recomendaciones_integracion(resultado):
    """Generar recomendaciones para integrar todos los dashboards"""
    
    print(f"\n💡 RECOMENDACIONES DE INTEGRACIÓN:")
    print("=" * 50)
    
    print("1. DASHBOARDS HTML PRINCIPALES A INTEGRAR:")
    dashboards_importantes = [
        'dashboard_global_html.html',
        'dashboard_html_completo.html', 
        'dashboard_sistema_unificado.html',
        'dashboard_metgo_3d.html'
    ]
    
    for dashboard in dashboards_importantes:
        if dashboard in resultado['no_integrados']:
            print(f"   ✅ {dashboard}")
    
    print("\n2. DASHBOARDS DE REPORTES A INTEGRAR:")
    reportes_importantes = [d for d in resultado['categorias']['reportes'] if d in resultado['no_integrados']]
    for reporte in reportes_importantes[:5]:  # Mostrar solo los primeros 5
        print(f"   📊 {reporte}")
    
    print("\n3. DASHBOARDS ECONÓMICOS A INTEGRAR:")
    economicos = [d for d in resultado['categorias']['economicos'] if d in resultado['no_integrados']]
    for economico in economicos[:3]:  # Mostrar solo los primeros 3
        print(f"   💰 {economico}")
    
    print(f"\n📈 RESUMEN:")
    print(f"   Total de dashboards encontrados: {resultado['total']}")
    print(f"   Dashboards Python: {len(resultado['python'])}")
    print(f"   Dashboards HTML: {len(resultado['html']) + len(resultado['html_subdirs'])}")
    print(f"   Dashboards no integrados: {len(resultado['no_integrados'])}")
    print(f"   Porcentaje de integración: {((resultado['total'] - len(resultado['no_integrados'])) / resultado['total'] * 100):.1f}%")

def main():
    resultado = identificar_todos_los_dashboards()
    generar_recomendaciones_integracion(resultado)

if __name__ == "__main__":
    main()
