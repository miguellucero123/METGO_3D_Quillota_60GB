"""
REVISOR SIMPLE DE DASHBOARDS METGO 3D
Script simplificado para identificar los dashboards principales y funcionales
"""

import os
import glob
from pathlib import Path

def encontrar_dashboards_principales():
    """Encontrar y categorizar los dashboards principales"""
    
    print("REVISION DE DASHBOARDS METGO 3D")
    print("=" * 50)
    
    # Buscar todos los archivos dashboard
    dashboards = glob.glob("dashboard_*.py")
    dashboards.sort()
    
    print(f"Se encontraron {len(dashboards)} archivos dashboard:")
    print()
    
    # Categorizar por tipo
    categorias = {
        'meteorologicos': [],
        'agricolas': [],
        'principales': [],
        'especializados': [],
        'otros': []
    }
    
    for dashboard in dashboards:
        nombre = dashboard.lower()
        
        if 'meteorologico' in nombre:
            categorias['meteorologicos'].append(dashboard)
        elif 'agricola' in nombre:
            categorias['agricolas'].append(dashboard)
        elif 'principal' in nombre or 'central' in nombre:
            categorias['principales'].append(dashboard)
        elif any(x in nombre for x in ['ml_', 'modelos', 'drones', 'economico']):
            categorias['especializados'].append(dashboard)
        else:
            categorias['otros'].append(dashboard)
    
    # Mostrar categorías
    for categoria, lista in categorias.items():
        if lista:
            print(f"{categoria.upper()}:")
            for dashboard in lista:
                print(f"  - {dashboard}")
            print()
    
    return categorias

def verificar_errores_conocidos(dashboard):
    """Verificar errores conocidos en un dashboard"""
    errores = []
    
    try:
        with open(dashboard, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Errores conocidos
        if '.dt.strftime' in contenido and 'pd.to_datetime' not in contenido:
            errores.append('Error .dt accessor sin conversion datetime')
        
        if 'use_container_width' in contenido:
            errores.append('use_container_width deprecado')
        
        if 'st.experimental_rerun' in contenido:
            errores.append('st.experimental_rerun deprecado')
        
        # Verificar sintaxis básica
        try:
            compile(contenido, dashboard, 'exec')
            sintaxis_ok = True
        except SyntaxError:
            sintaxis_ok = False
            errores.append('Error de sintaxis')
        
        return errores, sintaxis_ok
        
    except Exception as e:
        return [f'Error leyendo archivo: {e}'], False

def analizar_dashboards_principales(categorias):
    """Analizar los dashboards más importantes"""
    
    print("ANALISIS DE DASHBOARDS PRINCIPALES")
    print("=" * 40)
    
    dashboards_analizar = []
    
    # Dashboard meteorológico (priorizar 'final')
    meteorologicos = categorias['meteorologicos']
    if 'dashboard_meteorologico_final.py' in meteorologicos:
        dashboards_analizar.append(('dashboard_meteorologico_final.py', 'Meteorologico Principal'))
    elif meteorologicos:
        dashboards_analizar.append((meteorologicos[0], 'Meteorologico'))
    
    # Dashboard agrícola
    if categorias['agricolas']:
        dashboards_analizar.append((categorias['agricolas'][0], 'Agricola'))
    
    # Dashboard principal
    if categorias['principales']:
        dashboards_analizar.append((categorias['principales'][0], 'Principal'))
    
    # Analizar cada dashboard
    resultados = {}
    
    for dashboard, tipo in dashboards_analizar:
        print(f"\n{dashboard} ({tipo}):")
        print("-" * (len(dashboard) + len(tipo) + 3))
        
        errores, sintaxis_ok = verificar_errores_conocidos(dashboard)
        
        if sintaxis_ok:
            print("Sintaxis: OK")
        else:
            print("Sintaxis: ERROR")
        
        if errores:
            print("Problemas encontrados:")
            for error in errores:
                print(f"  - {error}")
        else:
            print("Sin problemas conocidos")
        
        resultados[dashboard] = {
            'tipo': tipo,
            'sintaxis_ok': sintaxis_ok,
            'errores': errores
        }
    
    return resultados

def generar_recomendaciones(resultados):
    """Generar recomendaciones basadas en el análisis"""
    
    print("\nRECOMENDACIONES")
    print("=" * 20)
    
    dashboards_recomendados = []
    dashboards_problemas = []
    
    for dashboard, info in resultados.items():
        if info['sintaxis_ok'] and not info['errores']:
            dashboards_recomendados.append(dashboard)
        else:
            dashboards_problemas.append((dashboard, info))
    
    print("DASHBOARDS RECOMENDADOS PARA USO:")
    for dashboard in dashboards_recomendados:
        print(f"  OK: {dashboard}")
    
    if dashboards_problemas:
        print("\nDASHBOARDS CON PROBLEMAS:")
        for dashboard, info in dashboards_problemas:
            print(f"  PROBLEMA: {dashboard}")
            for error in info['errores']:
                print(f"    - {error}")
    
    return dashboards_recomendados, dashboards_problemas

def main():
    # 1. Encontrar dashboards
    categorias = encontrar_dashboards_principales()
    
    # 2. Analizar principales
    resultados = analizar_dashboards_principales(categorias)
    
    # 3. Generar recomendaciones
    recomendados, problemas = generar_recomendaciones(resultados)
    
    print("\n" + "=" * 50)
    print("RESUMEN FINAL")
    print("=" * 50)
    print(f"Dashboards recomendados: {len(recomendados)}")
    print(f"Dashboards con problemas: {len(problemas)}")
    
    if recomendados:
        print("\nPara usar el sistema, ejecuta estos dashboards:")
        for dashboard in recomendados:
            print(f"  python -m streamlit run {dashboard}")

if __name__ == "__main__":
    main()
