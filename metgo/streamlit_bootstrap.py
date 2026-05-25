#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inicialización común para Streamlit local y Streamlit Cloud."""

from __future__ import annotations

import sys
from pathlib import Path

from metgo.paths import PROJECT_ROOT

ROOT = PROJECT_ROOT


def bootstrap(*modules: str) -> Path:
    """Registra rutas del proyecto y devuelve la raíz del repo."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import metgo.paths as mp

    compat = mp.compat_scripts_dir()
    if compat.is_dir():
        c = str(compat)
        if c not in sys.path:
            sys.path.insert(0, c)

    if modules:
        mp.setup_paths(*modules)
    else:
        mp.setup_all_paths()
    mp.ensure_runtime_dirs()
    return ROOT
