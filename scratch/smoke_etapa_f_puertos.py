#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke Etapa F: importa cada dashboard del catálogo y valida contrato UI (sin Streamlit server)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "frontend" / "dashboards"

ACTIVOS = [
    ("8502", "dashboard_meteorologico_profesional.py"),
    ("8503", "dashboard_agricola_inteligente.py"),
    ("8504", "dashboard_monitoreo_tiempo_real.py"),
    ("8505", "dashboard_ia_ml_avanzado.py"),
    ("8506", "dashboard_visualizaciones_avanzadas.py"),
    ("8507", "dashboard_global_metricas.py"),
    ("8508", "dashboard_agricultura_precision.py"),
    ("8509", "dashboard_analisis_comparativo.py"),
    ("8510", "dashboard_alertas_automaticas.py"),
    ("8511", "dashboard_simple_optimizado.py"),
    ("8512", "dashboard_unificado_diferenciado.py"),
    ("8513", "dashboard_mobile_optimizado.py"),
]


def check_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        ast.parse(text)
    except SyntaxError as e:
        errs.append(f"syntax:{e}")
        return errs
    if "st.plotly_chart" in text or "plotly_chart(" in text:
        if "plotly_layout" not in text:
            errs.append("plotly_chart_sin_plotly_layout")
    if "np.random" in text or "generar_datos_simulados" in text:
        errs.append("sintetico_sospechoso")
    return errs


def main() -> int:
    failed = 0
    print("Etapa F — smoke estático catálogo 8502–8513")
    for puerto, name in ACTIVOS:
        path = DASH / name
        if not path.is_file():
            print(f"  FAIL {puerto} {name}: missing")
            failed += 1
            continue
        errs = check_file(path)
        if errs:
            print(f"  FAIL {puerto} {name}: {', '.join(errs)}")
            failed += 1
        else:
            print(f"  OK   {puerto} {name}")
    print(f"\nResultado: {'FAIL' if failed else 'OK'} ({failed} fallos)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
