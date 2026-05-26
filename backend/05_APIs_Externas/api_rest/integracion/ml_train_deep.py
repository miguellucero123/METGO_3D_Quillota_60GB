#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrenamiento profundo opcional (módulo 06) — Fase 10.

Invoca script legacy con subprocess y timeout; si falla, devuelve estado sin tumbar la API.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise FileNotFoundError("metgo_paths.py no encontrado")


def _script_pipeline() -> Path | None:
    root = _repo_root()
    candidatos = [
        root / "backend/06_Modelos_ML_IA/scripts/pipeline_ml_optimizado.py",
        root / "backend/06_Modelos_ML_IA/scripts/fix_ml_models.py",
    ]
    for c in candidatos:
        if c.is_file():
            return c
    return None


def _log_path() -> Path:
    d = _repo_root() / "backend" / "08_Gestion_Datos" / "datos_runtime"
    d.mkdir(parents=True, exist_ok=True)
    return d / "ml_train_deep_last.json"


def estado_ultimo() -> dict[str, Any]:
    p = _log_path()
    if not p.is_file():
        return {"ejecutado": False}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"ejecutado": False, "error": "log corrupto"}


def ejecutar_entrenamiento_profundo(timeout_s: int | None = None) -> dict[str, Any]:
    script = _script_pipeline()
    timeout_s = timeout_s or int(os.environ.get("METGO_ML_DEEP_TIMEOUT", "300"))
    inicio = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if not script:
        res = {
            "ok": False,
            "error": "No se encontró pipeline_ml_optimizado.py ni fix_ml_models.py",
            "inicio": inicio,
        }
        _log_path().write_text(json.dumps(res, indent=2), encoding="utf-8")
        return res

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [sys.executable, str(script)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(script.parent),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
        )
        res = {
            "ok": proc.returncode == 0,
            "script": str(script.relative_to(_repo_root())).replace("\\", "/"),
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2000:],
            "stderr_tail": (proc.stderr or "")[-1000:],
            "inicio": inicio,
            "fin": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    except subprocess.TimeoutExpired:
        res = {
            "ok": False,
            "error": f"Timeout tras {timeout_s}s",
            "script": str(script),
            "inicio": inicio,
        }
    except Exception as e:
        res = {"ok": False, "error": str(e), "script": str(script), "inicio": inicio}

    if res.get("ok"):
        try:
            from api_rest.integracion import ml_registry

            reg = ml_registry.sincronizar_registro()
            res["registry_servibles"] = reg.get("servibles")
            res["registry_total"] = reg.get("total")
        except Exception as e:
            res["registry_sync_error"] = str(e)

    _log_path().write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return res
