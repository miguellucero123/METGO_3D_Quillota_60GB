#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Worker entrenamiento ML profundo (Fase 10) — subprocess con timeout."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("metgo_paths no encontrado")


def main() -> int:
    root = _repo_root()
    sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("05_api_rest")
    apis = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if apis:
        sys.path.insert(0, str(apis))

    from api_rest.integracion import ml_train_deep, workers_status

    res = ml_train_deep.ejecutar_entrenamiento_profundo()
    workers_status.registrar_heartbeat(
        "ml_training",
        {"estado": "deep_train", "ok": res.get("ok"), "script": res.get("script")},
    )
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
