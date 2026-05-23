#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganización METGO v3 — raíz mínima y carpetas de runtime en 08/12.

Uso:
    python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v3.py --dry-run
    python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v3.py
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

KEEP_IN_ROOT = {
    "README.md",
    "LICENSE",
    "requirements.txt",
    ".gitignore",
    ".dockerignore",
    "metgo_paths.py",
    "streamlit_app.py",
    ".env",
    ".env.example",
    "metgo_auth.py",
    "sistema_auth_dashboard_principal_metgo.py",
    "datos_reales_openmeteo.py",
    "mobile_config.py",
    "cache_offline_mobile.py",
    "dashboard_mobile_optimizado.py",
    "dashboard_visualizaciones_avanzadas.py",
}

# Archivos sueltos en módulos → destino relativo
MODULE_FILE_MAP: dict[str, str] = {
    "01_Sistema_Meteorologico/main.py": "01_Sistema_Meteorologico/scripts/main.py",
    "01_Sistema_Meteorologico/main_tiempo_real.py": "01_Sistema_Meteorologico/scripts/main_tiempo_real.py",
    "01_Sistema_Meteorologico/probar_integracion_simple.py": "01_Sistema_Meteorologico/scripts/probar_integracion_simple.py",
    "04_Dashboards_Unificados/main_dashboard.py": "04_Dashboards_Unificados/dashboards/main_dashboard.py",
    "metgo_auth.py": "07_Sistema_Monitoreo/scripts/metgo_auth.py",
    "10_Deployment_Produccion/scripts/RESUMEN_DEPLOYMENT_PRODUCCION_COMPLETADO.md": "11_Documentacion/manuales/RESUMEN_DEPLOYMENT_PRODUCCION_COMPLETADO.md",
}

DIR_MOVES: dict[str, str] = {
    "data": "08_Gestion_Datos/datos_runtime",
    "logs": "08_Gestion_Datos/logs_runtime",
    "respaldo_20251011_022103": "12_Respaldos_Archivos/backups/respaldo_20251011_022103",
}

JUNCTION_LINKS: dict[str, str] = {
    "data": "08_Gestion_Datos/datos_runtime",
    "logs": "08_Gestion_Datos/logs_runtime",
}

WRAPPER_IMPORT = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper de compatibilidad METGO — reexporta módulo reorganizado."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import metgo_paths
metgo_paths.setup_all_paths()

import importlib.util
_spec = importlib.util.spec_from_file_location("_metgo_shim", ROOT / "{target}")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
globals().update({{k: v for k, v in _mod.__dict__.items() if not k.startswith("_")}})
'''


def _move_file(src: Path, dest: Path, dry_run: bool) -> bool:
    if not src.is_file():
        return False
    if dest.exists() and src.resolve() != dest.resolve():
        print(f"  OMITE {src.name} (ya existe en destino)")
        return False
    print(f"  MOVER {src.relative_to(PROJECT_ROOT)} -> {dest.relative_to(PROJECT_ROOT)}")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    return True


def _move_dir(src: Path, dest: Path, dry_run: bool) -> bool:
    if not src.is_dir():
        return False
    if dest.exists():
        print(f"  FUSIONAR {src.name} -> {dest.relative_to(PROJECT_ROOT)}")
        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                target = dest / item.name
                if target.exists():
                    continue
                shutil.move(str(item), str(target))
            shutil.rmtree(src, ignore_errors=True)
        return True
    print(f"  MOVER DIR {src.name} -> {dest.relative_to(PROJECT_ROOT)}")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    return True


def _remove_duplicate_dashboards_dir(dry_run: bool) -> None:
    dup = PROJECT_ROOT / "10_Dashboards_Unificados"
    if not dup.is_dir():
        return
    canonical = PROJECT_ROOT / "04_Dashboards_Unificados/dashboards/ejecutar_todos_dashboards.py"
    stray = dup / "dashboards/ejecutar_todos_dashboards.py"
    if stray.is_file() and canonical.is_file():
        print("  ELIMINAR carpeta duplicada 10_Dashboards_Unificados (contenido ya en 04)")
        if not dry_run:
            shutil.rmtree(dup, ignore_errors=True)
    elif dup.is_dir():
        print("  AVISO: revisar manualmente 10_Dashboards_Unificados")


def _create_wrapper(name: str, target_rel: str, dry_run: bool) -> None:
    content = WRAPPER_IMPORT.format(target=target_rel.replace("\\", "/"))
    print(f"  WRAPPER {name}")
    if not dry_run:
        (PROJECT_ROOT / name).write_text(content, encoding="utf-8")


def _ensure_junction(link_name: str, target_rel: str, dry_run: bool) -> None:
    link = PROJECT_ROOT / link_name
    target = PROJECT_ROOT / target_rel
    if link.exists() or not target.is_dir():
        return
    print(f"  JUNCTION {link_name} -> {target_rel}")
    if dry_run:
        return
    target.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
        )
    else:
        link.symlink_to(target, target_is_directory=True)


def reorganize(dry_run: bool = False) -> None:
    print("=" * 70)
    print(f"REORGANIZACIÓN METGO v3 {'(DRY-RUN)' if dry_run else '(APLICAR)'}")
    print("=" * 70)

    moved = 0
    for rel_src, rel_dest in MODULE_FILE_MAP.items():
        src = PROJECT_ROOT / rel_src
        dest = PROJECT_ROOT / rel_dest
        if _move_file(src, dest, dry_run):
            moved += 1

    for rel_src, rel_dest in DIR_MOVES.items():
        src = PROJECT_ROOT / rel_src
        dest = PROJECT_ROOT / rel_dest
        if _move_dir(src, dest, dry_run):
            moved += 1

    print("\n--- Carpeta duplicada 10_Dashboards ---")
    _remove_duplicate_dashboards_dir(dry_run)

    print("\n--- Wrapper metgo_auth ---")
    target = "07_Sistema_Monitoreo/scripts/metgo_auth.py"
    if (PROJECT_ROOT / target).exists() or dry_run:
        _create_wrapper("metgo_auth.py", target, dry_run)

    print("\n--- Junctions compatibilidad data/logs ---")
    for link, target_rel in JUNCTION_LINKS.items():
        _ensure_junction(link, target_rel, dry_run)

    print(f"\nTotal operaciones de archivo/carpeta: {moved}")
    if dry_run:
        print("\nEjecute sin --dry-run para aplicar.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorganizar proyecto METGO v3")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    reorganize(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
