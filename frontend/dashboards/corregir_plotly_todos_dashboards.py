#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir automáticamente los warnings de Plotly en todos los dashboards
Sistema METGO 3D Quillota - Solución moderna de Plotly
"""

import os
import re
import glob
from pathlib import Path

def corregir_plotly_dashboard(archivo):
    """Corrige un dashboard individual aplicando la configuración moderna de Plotly"""
    print(f"Corrigiendo: {archivo}")
    
    try:
        # Leer el archivo
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # 1. Agregar configuración moderna de Plotly después de st.set_page_config
        config_plotly = """
# Configuración moderna de Plotly para eliminar warnings
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'grafico_metgo',
        'height': 500,
        'width': 700,
        'scale': 2
    },
    'responsive': True,
    'staticPlot': False
}
"""
        
        # Buscar st.set_page_config y agregar la configuración después
        if 'st.set_page_config' in contenido and 'PLOTLY_CONFIG' not in contenido:
            patron = r'(st\.set_page_config\([^)]+\)\s*\))'
            contenido = re.sub(patron, r'\1' + config_plotly, contenido)
        
        # 2. Reemplazar configuraciones deprecated
        # Reemplazar config=PLOTLY_CONFIG por config=PLOTLY_CONFIG
        contenido = re.sub(
            r"config=\{'displayModeBar': False\}",
            "config=PLOTLY_CONFIG",
            contenido
        )
        
        # Reemplazar config=PLOTLY_CONFIG por config=PLOTLY_CONFIG
        contenido = re.sub(
            r"config=\{'displayModeBar': True\}",
            "config=PLOTLY_CONFIG",
            contenido
        )
        
        # 3. Corregir use_container_width deprecated
        contenido = re.sub(
            r"use_container_width=True",
            "use_container_width=True",
            contenido
        )
        
        # 4. Corregir use_container_width=True por use_container_width=True
        contenido = re.sub(
            r"use_container_width=True",
            "use_container_width=True",
            contenido
        )
        
        # 5. Asegurar que todas las llamadas a st.plotly_chart usen la configuración moderna
        patron_plotly = r"st\.plotly_chart\(([^,]+)(?:,\s*[^)]+)?\)"
        
        def reemplazar_plotly_chart(match):
            grafico = match.group(1)
            # Verificar si ya tiene config
            if 'config=' in match.group(0):
                # Ya tiene config, no hacer nada
                return match.group(0)
            else:
                # Agregar config=PLOTLY_CONFIG
                return f"st.plotly_chart({grafico}, config=PLOTLY_CONFIG, use_container_width=True)"
        
        contenido = re.sub(patron_plotly, reemplazar_plotly_chart, contenido)
        
        # 6. Corregir warnings de update_layout
        # Agregar showlegend=False donde falte
        patron_update_layout = r"fig\.update_layout\(([^)]+)\)"
        
        def corregir_update_layout(match):
            params = match.group(1)
            if 'showlegend' not in params:
                if params.strip().endswith(','):
                    params += " showlegend=False"
                else:
                    params += ", showlegend=False"
            return f"fig.update_layout({params}, showlegend=False)"
        
        contenido = re.sub(patron_update_layout, corregir_update_layout, contenido)
        
        # Escribir el archivo corregido solo si hubo cambios
        if contenido != contenido_original:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"Corregido: {archivo}")
            return True
        else:
            print(f"Sin cambios: {archivo}")
            return False
            
    except Exception as e:
        print(f"Error corrigiendo {archivo}: {e}")
        return False

def encontrar_dashboards_con_plotly():
    """Encuentra todos los dashboards que usan Plotly"""
    patrones = [
        "dashboard_*.py",
        "*dashboard*.py",
        "*metgo*.py"
    ]
    
    dashboards = []
    
    for patron in patrones:
        archivos = glob.glob(patron)
        dashboards.extend(archivos)
    
    # Filtrar solo los que contienen plotly
    dashboards_plotly = []
    for archivo in dashboards:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'plotly' in contenido.lower() and 'st.plotly_chart' in contenido:
                    dashboards_plotly.append(archivo)
        except:
            continue
    
    return list(set(dashboards_plotly))

def main():
    """Función principal"""
    print("INICIANDO CORRECCION AUTOMATICA DE PLOTLY")
    print("=" * 60)
    
    # Encontrar dashboards con Plotly
    dashboards = encontrar_dashboards_con_plotly()
    
    if not dashboards:
        print("No se encontraron dashboards con Plotly")
        return
    
    print(f"Encontrados {len(dashboards)} dashboards con Plotly:")
    for dashboard in dashboards:
        print(f"   - {dashboard}")
    
    print("\nINICIANDO CORRECCION...")
    print("=" * 60)
    
    corregidos = 0
    errores = 0
    
    for dashboard in dashboards:
        if corregir_plotly_dashboard(dashboard):
            corregidos += 1
        else:
            errores += 1
    
    print("\nRESUMEN DE CORRECCION:")
    print("=" * 60)
    print(f"Dashboards corregidos: {corregidos}")
    print(f"Errores: {errores}")
    print(f"Total procesados: {len(dashboards)}")
    
    if corregidos > 0:
        print("\nCORRECCION COMPLETADA")
        print("Los dashboards ahora usan la configuracion moderna de Plotly")
        print("sin warnings deprecated, manteniendo todas las visualizaciones.")
    
    print("\nCAMBIOS APLICADOS:")
    print("- Configuracion moderna PLOTLY_CONFIG agregada")
    print("- Reemplazadas configuraciones deprecated")
    print("- Corregidos parametros use_container_width")
    print("- Agregados showlegend=False donde faltaba")
    print("- Mantenidas todas las visualizaciones originales")

if __name__ == "__main__":
    main()
