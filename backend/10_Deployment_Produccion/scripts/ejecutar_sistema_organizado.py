#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Launcher Streamlit local (DT-1) — rutas vía metgo.paths.

Deprecado frente a ``iniciar_metgo_desarrollo.bat`` + Vue; útil para smoke 8501–8513.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

# Bootstrap raíz del monorepo
_root = Path(__file__).resolve()
for p in _root.parents:
    if (p / "metgo_paths.py").exists() or (p / "metgo" / "paths.py").exists():
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
        break

from _deprecated_notice import warn_if_deprecated  # noqa: E402

warn_if_deprecated(__file__, "iniciar_metgo_desarrollo.bat + Centro de servicios (Vue)")

try:
    from metgo.paths import PROJECT_ROOT, frontend_vue_dir, streamlit_dashboard_path
except ImportError:
    from metgo_paths import PROJECT_ROOT  # type: ignore

    def streamlit_dashboard_path(filename: str) -> Path:  # type: ignore
        return PROJECT_ROOT / "frontend" / "dashboards" / filename

    def frontend_vue_dir() -> Path:  # type: ignore
        return PROJECT_ROOT / "frontend" / "vue"


# Checklist F — puertos 8501–8513 (portal + dashboards)
DASHBOARDS: list[tuple[Path, int, str]] = [
    (PROJECT_ROOT / "streamlit_app.py", 8501, "Portal Streamlit"),
    (streamlit_dashboard_path("dashboard_meteorologico_profesional.py"), 8502, "Meteorológico"),
    (streamlit_dashboard_path("dashboard_agricola_inteligente.py"), 8503, "Agrícola"),
    (streamlit_dashboard_path("dashboard_monitoreo_tiempo_real.py"), 8504, "Monitoreo"),
    (streamlit_dashboard_path("dashboard_ia_ml_avanzado.py"), 8505, "ML/IA"),
    (streamlit_dashboard_path("dashboard_visualizaciones_avanzadas.py"), 8506, "Visualizaciones"),
    (streamlit_dashboard_path("dashboard_global_metricas.py"), 8507, "Métricas globales"),
    (streamlit_dashboard_path("dashboard_agricultura_precision.py"), 8508, "Agricultura precisión"),
    (streamlit_dashboard_path("dashboard_analisis_comparativo.py"), 8509, "Comparativo"),
    (streamlit_dashboard_path("dashboard_alertas_automaticas.py"), 8510, "Alertas"),
    (streamlit_dashboard_path("dashboard_simple_optimizado.py"), 8511, "Simple"),
    (streamlit_dashboard_path("dashboard_unificado_diferenciado.py"), 8512, "Unificado"),
    (streamlit_dashboard_path("dashboard_mobile_optimizado.py"), 8513, "Mobile"),
]


def ejecutar_dashboard(ruta: Path, puerto: int) -> bool:
    if not ruta.is_file():
        print(f"WARNING no encontrado: {ruta}")
        return False
    try:
        print(f"Ejecutando {ruta.name} en puerto {puerto}...")
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(ruta),
                "--server.port",
                str(puerto),
                "--server.headless",
                "true",
            ],
            cwd=str(PROJECT_ROOT),
        )
        time.sleep(1.5)
        print(f"OK http://localhost:{puerto}")
        return True
    except Exception as exc:
        print(f"ERROR {ruta.name}: {exc}")
        return False


def main() -> None:
    print("=" * 72)
    print("METGO — Streamlit local (metgo.paths / checklist F)")
    print(f"Vue SPA: {frontend_vue_dir()}")
    print("=" * 72)
    # Por defecto solo portal + meteo + agrícola (evitar abrir 13 procesos)
    seleccion = DASHBOARDS[:3]
    if "--all" in sys.argv:
        seleccion = DASHBOARDS

    n = 0
    for ruta, puerto, desc in seleccion:
        if ejecutar_dashboard(ruta, puerto):
            n += 1
            print(f"  - {desc}: http://localhost:{puerto}")
    print(f"\nActivos: {n}/{len(seleccion)} (usa --all para 8501–8513)")
    print("Preferido UI: cd frontend/vue && npm run dev → :5173")


if __name__ == "__main__":
    main()
