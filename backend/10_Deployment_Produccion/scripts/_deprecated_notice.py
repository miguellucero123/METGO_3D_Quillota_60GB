#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aviso unificado para scripts de arranque legacy METGO."""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path


def warn_if_deprecated(
    script: str | Path,
    alternative: str,
    *,
    exit_unless_allowed: bool = True,
) -> None:
    name = Path(script).name
    msg = (
        f"[DEPRECATED] {name} — use: {alternative}. "
        "Set METGO_ALLOW_DEPRECATED=1 to run this script anyway."
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    print("=" * 70)
    print(msg)
    print("=" * 70)
    if exit_unless_allowed and os.getenv("METGO_ALLOW_DEPRECATED") != "1":
        sys.exit(2)
