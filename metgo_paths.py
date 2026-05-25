#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compatibilidad: marcador de raíz del repo + reexportación de rutas.

Implementación en metgo/paths.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from metgo.paths import *  # noqa: F401,F403
