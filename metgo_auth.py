#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper de compatibilidad METGO — reexporta módulo reorganizado."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import metgo_paths
metgo_paths.setup_all_paths()

import importlib.util
_spec = importlib.util.spec_from_file_location("_metgo_shim", ROOT / "07_Sistema_Monitoreo/scripts/metgo_auth.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
globals().update({k: v for k, v in _mod.__dict__.items() if not k.startswith("_")})
