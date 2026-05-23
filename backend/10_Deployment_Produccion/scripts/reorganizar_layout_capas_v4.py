#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout por capas METGO v4: backend / frontend / site-web / docs.

Uso:
    python backend/10_Deployment_Produccion/scripts/reorganizar_layout_capas_v4.py --dry-run
    python backend/10_Deployment_Produccion/scripts/reorganizar_layout_capas_v4.py
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "metgo_paths.py").exists():
            return parent
    return here.parents[2]


PROJECT_ROOT = find_project_root()
BACKEND = PROJECT_ROOT / "backend"
FRONTEND = PROJECT_ROOT / "frontend"
SITE_WEB = PROJECT_ROOT / "site-web"
DOCS = PROJECT_ROOT / "docs"

BACKEND_MODULES = [
    "01_Sistema_Meteorologico",
    "02_Sistema_Agricola",
    "03_Sistema_IoT_Drones",
    "05_APIs_Externas",
    "06_Modelos_ML_IA",
    "07_Sistema_Monitoreo",
    "08_Gestion_Datos",
    "09_Testing_Validacion",
    "10_Deployment_Produccion",
    "12_Respaldos_Archivos",
]

FRONTEND_FROM_04 = {
    "frontend_vue": "vue",
    "dashboards": "dashboards",
    "config": "config",
    "static": "static",
    "templates": "templates",
    "app_movil_metgo": "app_movil",
}

PUBLIC_STREAMLIT = "dashboard_web_publico.py"


def _move_dir(src: Path, dest: Path, dry_run: bool) -> bool:
    if not src.is_dir():
        return False
    if dest.exists():
        # Migración parcial: fusionar restos
        if any(src.iterdir()):
            print(f"  FUSIONAR restos {src.name} -> {dest.relative_to(PROJECT_ROOT)}")
            if not dry_run:
                for item in src.iterdir():
                    target = dest / item.name
                    if target.exists():
                        continue
                    shutil.move(str(item), str(target))
                shutil.rmtree(src, ignore_errors=True)
            return True
        print(f"  LIMPIAR vacío {src.relative_to(PROJECT_ROOT)}")
        if not dry_run:
            shutil.rmtree(src, ignore_errors=True)
        return False
    print(f"  MOVER {src.relative_to(PROJECT_ROOT)} -> {dest.relative_to(PROJECT_ROOT)}")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dest))
        except (PermissionError, OSError) as exc:
            print(f"  AVISO move falló ({exc}); intentando robocopy...")
            dest.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                subprocess.run(
                    [
                        "robocopy",
                        str(src),
                        str(dest),
                        "/E",
                        "/MOVE",
                        "/R:1",
                        "/W:1",
                        "/NFL",
                        "/NDL",
                        "/NJH",
                        "/NJS",
                    ],
                    check=False,
                )
            shutil.rmtree(src, ignore_errors=True)
    return True


def _relocate_public_dashboard(dry_run: bool) -> None:
    src = FRONTEND / "dashboards" / PUBLIC_STREAMLIT
    dest_dir = SITE_WEB / "streamlit"
    dest = dest_dir / PUBLIC_STREAMLIT
    if not src.is_file():
        legacy = PROJECT_ROOT / "04_Dashboards_Unificados/dashboards" / PUBLIC_STREAMLIT
        if legacy.is_file():
            src = legacy
        else:
            return
    print(f"  SITE-WEB {PUBLIC_STREAMLIT}")
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest.unlink()
        shutil.move(str(src), str(dest))


def _recreate_junctions(dry_run: bool) -> None:
    runtime_data = BACKEND / "08_Gestion_Datos/datos_runtime"
    runtime_logs = BACKEND / "08_Gestion_Datos/logs_runtime"
    for name, target in (("data", runtime_data), ("logs", runtime_logs)):
        link = PROJECT_ROOT / name
        if link.exists() or not target.exists():
            if not dry_run and link.is_dir() and not link.is_symlink():
                pass
            elif link.exists():
                continue
        print(f"  JUNCTION {name} -> {target.relative_to(PROJECT_ROOT)}")
        if dry_run:
            continue
        target.mkdir(parents=True, exist_ok=True)
        if link.exists():
            if link.is_symlink() or link.is_junction():
                link.unlink()
            else:
                continue
        if sys.platform == "win32":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                check=False,
                capture_output=True,
            )


def reorganize(dry_run: bool = False) -> None:
    print("=" * 70)
    print(f"LAYOUT CAPAS v4 {'(DRY-RUN)' if dry_run else '(APLICAR)'}")
    print(f"Raíz: {PROJECT_ROOT}")
    print("=" * 70)

    if BACKEND.exists() and (BACKEND / "05_APIs_Externas").exists():
        print("Layout por capas ya aplicado. Solo junctions públicos.")
        _recreate_junctions(dry_run)
        return

    if not dry_run:
        BACKEND.mkdir(exist_ok=True)
        FRONTEND.mkdir(exist_ok=True)
        SITE_WEB.mkdir(exist_ok=True)
        (SITE_WEB / "static").mkdir(exist_ok=True)

    print("\n--- backend ---")
    for name in BACKEND_MODULES:
        _move_dir(PROJECT_ROOT / name, BACKEND / name, dry_run)

    print("\n--- frontend (desde 04) ---")
    src04 = PROJECT_ROOT / "04_Dashboards_Unificados"
    if src04.is_dir():
        for src_name, dest_name in FRONTEND_FROM_04.items():
            _move_dir(src04 / src_name, FRONTEND / dest_name, dry_run)
        readme = src04 / "README.md"
        if readme.is_file():
            print(f"  COPIAR README 04 -> frontend/README.md")
            if not dry_run:
                shutil.copy2(readme, FRONTEND / "README.md")
        if not dry_run and src04.exists() and not any(src04.iterdir()):
            src04.rmdir()
        elif not dry_run and src04.exists():
            print(f"  AVISO: quedan archivos en {src04}")

    print("\n--- docs ---")
    _move_dir(PROJECT_ROOT / "11_Documentacion", DOCS, dry_run)

    print("\n--- site-web público ---")
    _relocate_public_dashboard(dry_run)

    print("\n--- junctions data/logs ---")
    _recreate_junctions(dry_run)

    print("\nHecho. Actualice metgo_paths y ejecute pruebas de arranque.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    reorganize(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
