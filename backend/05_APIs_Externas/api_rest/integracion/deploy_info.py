#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scripts oficiales de despliegue (módulo 10)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def scripts_despliegue() -> list[dict[str, Any]]:
    for p in Path(__file__).resolve().parents:
        deploy = p / "backend" / "10_Deployment_Produccion" / "scripts"
        if deploy.is_dir():
            out = []
            for f in sorted(deploy.iterdir()):
                if f.suffix in (".bat", ".py", ".sh"):
                    out.append({"nombre": f.name, "ruta": str(f.relative_to(p)), "tipo": f.suffix[1:]})
            return out
    return []


def resumen_deploy() -> dict[str, Any]:
    scripts = scripts_despliegue()
    for p in Path(__file__).resolve().parents:
        root = p
        return {
            "scripts": scripts,
            "docker_compose_dev": (root / "docker-compose.dev.yml").is_file(),
            "render": (root / "render.yaml").is_file() or (root / "backend" / "10_Deployment_Produccion").is_dir(),
            "iniciar_desarrollo": any(s["nombre"] == "iniciar_metgo_desarrollo.bat" for s in scripts),
            "integrado": len(scripts) >= 3,
        }
    return {"scripts": [], "integrado": False}
