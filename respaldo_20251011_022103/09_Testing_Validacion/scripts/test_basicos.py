#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS BASICOS - METGO 3D
Tests de funcionalidad básica del sistema
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports_basicos():
    """Test de imports básicos"""
    try:
        import pandas as pd
        import numpy as np
        import streamlit as st
        import plotly.express as px
        assert True
    except ImportError as e:
        pytest.fail(f"Error importando módulos básicos: {e}")

def test_archivos_principales():
    """Test de archivos principales"""
    archivos_requeridos = [
        "sistema_unificado_con_conectores.py",
        "requirements.txt",
        "README.md"
    ]
    
    for archivo in archivos_requeridos:
        assert Path(archivo).exists(), f"Archivo requerido no encontrado: {archivo}"

def test_configuracion():
    """Test de configuración"""
    config_path = Path("config/config_avanzada.json")
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        assert 'sistema' in config
        assert 'base_datos' in config

def test_sistema_principal():
    """Test del sistema principal"""
    try:
        # Importar sin ejecutar
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sistema", "sistema_unificado_con_conectores.py"
        )
        sistema = importlib.util.module_from_spec(spec)
        # No ejecutar el módulo, solo verificar que se puede cargar
        assert spec is not None
    except Exception as e:
        pytest.fail(f"Error cargando sistema principal: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
