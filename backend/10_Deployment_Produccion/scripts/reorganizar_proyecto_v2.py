#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganización segura del proyecto METGO v2.
Mueve archivos de la raíz a sus módulos y crea wrappers de compatibilidad.

Uso:
    python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v2.py --dry-run
    python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v2.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Archivos que NUNCA se mueven desde la raíz
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
}

# Mapeo: nombre_en_raíz -> ruta relativa destino
FILE_MAP: dict[str, str] = {
    # Documentación
    "INSTRUCCIONES_ACCESO_EXTERNO.md": "11_Documentacion/manuales/",
    "INSTRUCCIONES_GITHUB.md": "11_Documentacion/manuales/",
    "INSTRUCCIONES_AUTOMATIZACION.md": "11_Documentacion/manuales/",
    "INTEGRACION_DATOS_REALES.md": "11_Documentacion/manuales/",
    "OPCIONES_WEB.md": "11_Documentacion/manuales/",
    "CORRECCION_ERROR_KEYERROR.md": "11_Documentacion/manuales/",
    "RESUMEN_MEJORAS_MOVILES.md": "11_Documentacion/manuales/",
    "RESUMEN_ESTADO_ACTUAL_SISTEMA.md": "11_Documentacion/manuales/",
    # Batch
    "configurar_acceso_externo.bat": "10_Deployment_Produccion/scripts/",
    "configurar_acceso_externo_permanente.bat": "10_Deployment_Produccion/scripts/",
    "configurar_router.bat": "10_Deployment_Produccion/scripts/",
    "configurar_inicio_automatico.bat": "10_Deployment_Produccion/scripts/",
    "automatizar_sistema.bat": "10_Deployment_Produccion/scripts/",
    "instalar_inicio_automatico.bat": "10_Deployment_Produccion/scripts/",
    "desinstalar_inicio_automatico.bat": "10_Deployment_Produccion/scripts/",
    "iniciar_sistema_permanente.bat": "10_Deployment_Produccion/scripts/",
    # Datos meteorológicos
    "datos_reales_openmeteo.py": "01_Sistema_Meteorologico/scripts/",
    # Mobile helpers
    "mobile_config.py": "04_Dashboards_Unificados/dashboards/mobile/",
    "cache_offline_mobile.py": "04_Dashboards_Unificados/dashboards/mobile/",
    "notificaciones_mobile.py": "07_Sistema_Monitoreo/scripts/",
    # Dashboard principal y dashboards
    "sistema_auth_dashboard_principal_metgo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_agricola_inteligente.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_agricola_metgo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_agricultura_precision.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_alertas_automaticas.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_analisis_comparativo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_global_metricas.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_ia_ml_avanzado.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_meteorologico_metgo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_meteorologico_profesional.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_mobile_optimizado.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_monitoreo_tiempo_real.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_simple_metgo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_simple_optimizado.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_unificado_diferenciado.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_unificado_metgo.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_visualizaciones_avanzadas.py": "04_Dashboards_Unificados/dashboards/",
    "dashboard_web_publico.py": "04_Dashboards_Unificados/dashboards/",
    # Deploy / orquestación
    "deploy_streamlit_cloud.py": "10_Deployment_Produccion/scripts/",
    "poner_en_linea.py": "10_Deployment_Produccion/scripts/",
    "ejecutar_con_ngrok.py": "10_Deployment_Produccion/scripts/",
    "ejecutar_dashboard_externo.py": "10_Deployment_Produccion/scripts/",
    "ejecutar_dashboards_correctos.py": "10_Deployment_Produccion/scripts/",
    "ejecutar_todos_dashboards.py": "10_Dashboards_Unificados/dashboards/",
    "iniciar_sistema_automatico.py": "10_Deployment_Produccion/scripts/",
    "detener_sistema.py": "10_Deployment_Produccion/scripts/",
    "reiniciar_sistema.py": "10_Deployment_Produccion/scripts/",
    "monitorear_sistema.py": "10_Deployment_Produccion/scripts/",
    "sistema_permanente_metgo.py": "10_Deployment_Produccion/scripts/",
    # Testing / verificación
    "verificar_datos_reales.py": "09_Testing_Validacion/scripts/",
    "verificar_github.py": "09_Testing_Validacion/scripts/",
    "verificar_acceso_simple.py": "09_Testing_Validacion/scripts/",
    "verificar_acceso_movil.py": "09_Testing_Validacion/scripts/",
    "probar_tipo_analisis.py": "09_Testing_Validacion/scripts/",
}

# Wrappers de compatibilidad en raíz (nombre -> destino relativo del archivo real)
def _wrapper_target(rel: str) -> str:
    """Ruta relativa al repo según layout capas o legacy."""
    root = Path(__file__).resolve().parents[2]
    if (root / "backend" / "05_APIs_Externas").is_dir():
        rel = rel.replace("04_Dashboards_Unificados/", "frontend/")
        rel = rel.replace("01_Sistema_Meteorologico/", "backend/01_Sistema_Meteorologico/")
        rel = rel.replace("11_Documentacion/", "docs/")
        rel = rel.replace("10_Deployment_Produccion/", "backend/10_Deployment_Produccion/")
    return rel


WRAPPER_TARGETS: dict[str, str] = {
    "sistema_auth_dashboard_principal_metgo.py": _wrapper_target(
        "04_Dashboards_Unificados/dashboards/sistema_auth_dashboard_principal_metgo.py"
    ),
    "datos_reales_openmeteo.py": _wrapper_target(
        "01_Sistema_Meteorologico/scripts/datos_reales_openmeteo.py"
    ),
    "mobile_config.py": _wrapper_target(
        "04_Dashboards_Unificados/dashboards/mobile/mobile_config.py"
    ),
    "cache_offline_mobile.py": _wrapper_target(
        "04_Dashboards_Unificados/dashboards/mobile/cache_offline_mobile.py"
    ),
    "dashboard_mobile_optimizado.py": _wrapper_target(
        "04_Dashboards_Unificados/dashboards/dashboard_mobile_optimizado.py"
    ),
    "dashboard_visualizaciones_avanzadas.py": _wrapper_target(
        "04_Dashboards_Unificados/dashboards/dashboard_visualizaciones_avanzadas.py"
    ),
}

WRAPPER_STREAMLIT = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper de compatibilidad METGO — redirige al módulo reorganizado."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import metgo_paths
metgo_paths.setup_all_paths()
runpy.run_path(str(ROOT / "{target}"), run_name="__main__")
'''

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


def _move_file(src: Path, dest_dir: Path, dry_run: bool) -> bool:
    dest = dest_dir / src.name
    if dest.exists() and src.resolve() != dest.resolve():
        if src.stat().st_size >= dest.stat().st_size:
            print(f"  REEMPLAZA {dest} (versión en raíz más reciente)")
            if not dry_run:
                dest.unlink()
        else:
            print(f"  OMITE {src.name} (destino más completo)")
            if not dry_run:
                src.unlink()
            return False
    print(f"  MOVER {src.name} -> {dest_dir}/")
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    return True


def _create_wrapper(name: str, target_rel: str, dry_run: bool) -> None:
    wrapper_path = PROJECT_ROOT / name
    is_streamlit = name == "sistema_auth_dashboard_principal_metgo.py"
    content = (WRAPPER_STREAMLIT if is_streamlit else WRAPPER_IMPORT).format(target=target_rel)
    print(f"  WRAPPER {name}")
    if not dry_run:
        wrapper_path.write_text(content, encoding="utf-8")


def _patch_bat_files(dry_run: bool) -> None:
    bat_dir = PROJECT_ROOT / "10_Deployment_Produccion" / "scripts"
    cd_line = 'cd /d "%~dp0..\\.."\r\n'
    for bat in bat_dir.glob("*.bat"):
        text = bat.read_text(encoding="utf-8", errors="replace")
        if "%~dp0" in text or "METGO_3D_Quillota_60GB" in text[:200]:
            continue
        print(f"  PATCH BAT {bat.name}")
        if not dry_run:
            bat.write_text(cd_line + text, encoding="utf-8")


def reorganize(dry_run: bool = False) -> None:
    print("=" * 70)
    print(f"REORGANIZACIÓN METGO v2 {'(DRY-RUN)' if dry_run else '(APLICAR)'}")
    print(f"Raíz: {PROJECT_ROOT}")
    print("=" * 70)

    moved = 0
    for filename, dest_rel in FILE_MAP.items():
        src = PROJECT_ROOT / filename
        if not src.is_file():
            continue
        dest_dir = PROJECT_ROOT / dest_rel
        if _move_file(src, dest_dir, dry_run):
            moved += 1

    print(f"\n--- Wrappers de compatibilidad ---")
    for name, target_rel in WRAPPER_TARGETS.items():
        target = PROJECT_ROOT / target_rel
        if target.exists() or dry_run:
            _create_wrapper(name, target_rel.replace("\\", "/"), dry_run)

    print(f"\n--- Parche .bat ---")
    _patch_bat_files(dry_run)

    print(f"\nTotal movidos: {moved}")
    if dry_run:
        print("\nEjecute sin --dry-run para aplicar cambios.")
    else:
        print("\nSiguiente paso recomendado: reorganizar_proyecto_v3.py (runtime y respaldos)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorganizar proyecto METGO")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin mover archivos")
    args = parser.parse_args()
    reorganize(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
