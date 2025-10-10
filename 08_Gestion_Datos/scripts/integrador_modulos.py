#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrador de Modulos - METGO 3D
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import logging

class IntegradorModulos:
    """Integrador de todos los notebooks y archivos Python"""
    
    def __init__(self):
        self.directorio_base = Path.cwd()
        self.logger = logging.getLogger('INTEGRADOR')
        
        # Escanear modulos
        self.notebooks = self._escanear_notebooks()
        self.archivos_py = self._escanear_archivos_py()
        
    def _escanear_notebooks(self) -> List[Dict]:
        """Escanear todos los notebooks del proyecto"""
        notebooks = []
        
        for notebook_file in self.directorio_base.glob('*.ipynb'):
            if 'checkpoint' not in str(notebook_file):
                notebooks.append({
                    'nombre': notebook_file.name,
                    'ruta': str(notebook_file),
                    'tipo': 'notebook',
                    'categoria': self._categorizar_notebook(notebook_file.name)
                })
        
        self.logger.info(f"Encontrados {len(notebooks)} notebooks")
        return notebooks
    
    def _escanear_archivos_py(self) -> List[Dict]:
        """Escanear todos los archivos Python del proyecto"""
        archivos = []
        
        for py_file in self.directorio_base.glob('*.py'):
            archivos.append({
                'nombre': py_file.name,
                'ruta': str(py_file),
                'tipo': 'python',
                'categoria': self._categorizar_python(py_file.name)
            })
        
        self.logger.info(f"Encontrados {len(archivos)} archivos Python")
        return archivos
    
    def _categorizar_notebook(self, nombre: str) -> str:
        """Categorizar notebook por nombre"""
        if '00' in nombre or 'Principal' in nombre:
            return 'core'
        elif '01' in nombre or 'Configuracion' in nombre:
            return 'config'
        elif '02' in nombre or 'Carga' in nombre or 'Procesamiento' in nombre:
            return 'data'
        elif '03' in nombre or 'Analisis' in nombre:
            return 'analysis'
        elif '04' in nombre or 'Visualizacion' in nombre:
            return 'visualization'
        elif '05' in nombre or 'ML' in nombre or 'Modelos' in nombre:
            return 'ml'
        elif '06' in nombre or 'Dashboard' in nombre:
            return 'dashboard'
        elif '07' in nombre or 'Reportes' in nombre:
            return 'reports'
        elif '08' in nombre or 'APIs' in nombre:
            return 'api'
        elif '09' in nombre or 'Testing' in nombre:
            return 'testing'
        elif '10' in nombre or 'Deployment' in nombre:
            return 'deployment'
        elif '11' in nombre or 'Monitoreo' in nombre:
            return 'monitoring'
        elif '12' in nombre or 'Respaldos' in nombre:
            return 'backup'
        elif '13' in nombre or 'Optimizacion' in nombre:
            return 'optimization'
        elif '14' in nombre or 'Reportes_Avanzados' in nombre:
            return 'advanced_reports'
        elif '15' in nombre or 'Integracion' in nombre:
            return 'integration'
        else:
            return 'otros'
    
    def _categorizar_python(self, nombre: str) -> str:
        """Categorizar archivo Python por nombre"""
        if 'auth' in nombre.lower():
            return 'autenticacion'
        elif 'dashboard' in nombre.lower():
            return 'dashboard'
        elif 'sistema' in nombre.lower():
            return 'sistema'
        elif 'integ' in nombre.lower():
            return 'integracion'
        elif 'orquest' in nombre.lower():
            return 'orquestacion'
        elif 'pipeline' in nombre.lower():
            return 'pipeline'
        elif 'config' in nombre.lower():
            return 'configuracion'
        elif 'monitor' in nombre.lower():
            return 'monitoreo'
        elif 'backup' in nombre.lower() or 'respaldo' in nombre.lower():
            return 'respaldo'
        elif 'test' in nombre.lower():
            return 'testing'
        elif 'ia' in nombre.lower() or 'ml' in nombre.lower():
            return 'ia_ml'
        elif 'iot' in nombre.lower():
            return 'iot'
        elif 'analisis' in nombre.lower():
            return 'analisis'
        elif 'visual' in nombre.lower():
            return 'visualizacion'
        elif 'api' in nombre.lower():
            return 'api'
        elif 'deploy' in nombre.lower():
            return 'deployment'
        elif 'gestion' in nombre.lower():
            return 'gestion'
        else:
            return 'otros'
    
    def obtener_modulos_por_categoria(self) -> Dict:
        """Obtener modulos agrupados por categoria"""
        modulos_por_categoria = {}
        
        # Agrupar notebooks
        for notebook in self.notebooks:
            categoria = notebook['categoria']
            if categoria not in modulos_por_categoria:
                modulos_por_categoria[categoria] = {'notebooks': [], 'archivos_py': []}
            modulos_por_categoria[categoria]['notebooks'].append(notebook)
        
        # Agrupar archivos Python
        for archivo in self.archivos_py:
            categoria = archivo['categoria']
            if categoria not in modulos_por_categoria:
                modulos_por_categoria[categoria] = {'notebooks': [], 'archivos_py': []}
            modulos_por_categoria[categoria]['archivos_py'].append(archivo)
        
        return modulos_por_categoria
    
    def obtener_resumen(self) -> Dict:
        """Obtener resumen de modulos"""
        modulos_por_categoria = self.obtener_modulos_por_categoria()
        
        return {
            'total_notebooks': len(self.notebooks),
            'total_archivos_py': len(self.archivos_py),
            'total_modulos': len(self.notebooks) + len(self.archivos_py),
            'categorias': len(modulos_por_categoria),
            'modulos_por_categoria': {
                categoria: {
                    'notebooks': len(modulos['notebooks']),
                    'archivos_py': len(modulos['archivos_py']),
                    'total': len(modulos['notebooks']) + len(modulos['archivos_py'])
                }
                for categoria, modulos in modulos_por_categoria.items()
            }
        }



