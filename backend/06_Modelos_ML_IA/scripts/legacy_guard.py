#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evita que scripts legacy de entrenamiento corrompan artefactos de producción."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def bloquear_entrenamiento_legacy(
    script: str | Path,
    *,
    alternative: str = (
        "PYTHONPATH=backend/05_APIs_Externas python -c "
        "\"from api_rest.integracion.ml_train_runner import entrenar_todos; print(entrenar_todos())\""
    ),
) -> None:
    """Sale con código 2 salvo METGO_ALLOW_LEGACY_ML=1."""
    name = Path(script).name
    msg = (
        f"[LEGACY ML] {name} está obsoleto y puede escribir .joblib en rutas incorrectas "
        f"(CWD relativo). Use el pipeline unificado:\n  {alternative}\n"
        "Para forzar ejecución: METGO_ALLOW_LEGACY_ML=1"
    )
    print("=" * 72)
    print(msg)
    print("=" * 72)
    if os.getenv("METGO_ALLOW_LEGACY_ML") != "1":
        sys.exit(2)
