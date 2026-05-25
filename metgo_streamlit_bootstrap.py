#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inicialización común para Streamlit local y Streamlit Cloud."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def bootstrap(*modules: str) -> Path:
    """Registra rutas del proyecto y devuelve la raíz del repo."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import metgo_paths

    if modules:
        metgo_paths.setup_paths(*modules)
    else:
        metgo_paths.setup_all_paths()
    metgo_paths.ensure_runtime_dirs()
    return ROOT
