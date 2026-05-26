#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reintenta outbox SMTP (Fase 9) — usar en cron cuando METGO_SMTP_* esté configurado."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("No se encontró metgo_paths.py")


def main() -> int:
    root = _repo_root()
    sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("05_api_rest")
    apis = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if apis:
        sys.path.insert(0, str(apis))

    from api_rest.integracion import notificaciones

    res = notificaciones.reintentar_outbox(max_items=20)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
