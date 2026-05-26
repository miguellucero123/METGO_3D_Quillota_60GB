#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Índice documentación (módulo 11)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


DOCS_CLAVE = [
    "docs/roadmap/BACKEND_MODULOS_01-12_AUDITORIA.md",
    "docs/roadmap/fase-4/README.md",
    "docs/DESARROLLO_LOCAL.md",
    "docs/PROMPT_MVP_METGO.md",
    "AGENTS.md",
    "README.md",
]


def indice_documentacion() -> dict[str, Any]:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            root = p
            docs = []
            for rel in DOCS_CLAVE:
                f = root / rel
                docs.append({"ruta": rel, "existe": f.is_file(), "bytes": f.stat().st_size if f.is_file() else 0})
            roadmap = root / "docs" / "roadmap"
            return {
                "documentos": docs,
                "roadmap_items": len(list(roadmap.rglob("*.md"))) if roadmap.is_dir() else 0,
                "integrado": all(d["existe"] for d in docs[:4]),
            }
    return {"documentos": [], "integrado": False}
