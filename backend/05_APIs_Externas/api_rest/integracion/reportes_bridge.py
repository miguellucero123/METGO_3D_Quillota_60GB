#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expone reportes JSON del módulo 07."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _reportes_dir() -> Path | None:
    for p in Path(__file__).resolve().parents:
        d = p / "backend" / "07_Sistema_Monitoreo" / "reportes" / "reportes"
        if d.is_dir():
            return d
    return None


def listar_ultimos_reportes(limite: int = 10) -> list[dict[str, Any]]:
    d = _reportes_dir()
    if not d:
        return []
    archivos = sorted(d.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    out = []
    for f in archivos[:limite]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            out.append(
                {
                    "archivo": f.name,
                    "ruta": str(f),
                    "modificado": f.stat().st_mtime,
                    "resumen": data if isinstance(data, dict) else {"tipo": "lista", "items": len(data)},
                }
            )
        except (json.JSONDecodeError, OSError):
            out.append({"archivo": f.name, "error": "no legible"})
    return out


def leer_reporte(nombre: str) -> dict[str, Any]:
    d = _reportes_dir()
    if not d:
        return {"error": "Directorio reportes no encontrado"}
    nombre = nombre.replace("..", "").lstrip("/")
    path = d / nombre
    if not path.is_file() or path.suffix != ".json":
        return {"error": "Reporte no encontrado"}
    try:
        return {"archivo": nombre, "contenido": json.loads(path.read_text(encoding="utf-8"))}
    except (json.JSONDecodeError, OSError) as e:
        return {"error": str(e)}
