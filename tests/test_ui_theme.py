"""Guardarraíles UI/datos: tema oscuro Plotly y cero sintéticos en dashboards activos."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "frontend" / "dashboards"

# Catálogo puertos con Etapa D aplicada (prioridad plan calidad Vue)
ACTIVOS = {
    "dashboard_meteorologico_profesional.py",
    "dashboard_agricola_inteligente.py",
    "dashboard_monitoreo_tiempo_real.py",
    "dashboard_ia_ml_avanzado.py",
    "dashboard_visualizaciones_avanzadas.py",
    "dashboard_global_metricas.py",
    "dashboard_analisis_comparativo.py",
}

FORBIDDEN_SYNTH = re.compile(
    r"np\.random|generar_datos_simulados|generar_datos_globales_5_anos|"
    r"generar_datos_comparativos|generar_datos_tiempo_real|"
    r"\bilustrativo\b|\bdatos simulados\b",
    re.IGNORECASE,
)
FORBIDDEN_WHITE = re.compile(
    r"plotly_white|paper_bgcolor\s*=\s*['\"]#?fff|paper_bgcolor\s*=\s*['\"]white",
    re.IGNORECASE,
)


def _activos() -> list[Path]:
    return sorted(p for p in DASH.glob("*.py") if p.name in ACTIVOS)


def test_dashboards_activos_sin_sinteticos():
    violaciones = []
    for path in _activos():
        text = path.read_text(encoding="utf-8")
        for m in FORBIDDEN_SYNTH.finditer(text):
            line = text[: m.start()].count("\n") + 1
            snippet = text.splitlines()[line - 1].strip()
            if snippet.startswith("#"):
                continue
            if "requiere" in snippet.lower() or "sin datos" in snippet.lower():
                continue
            if "DEPRECATED" in snippet.upper():
                continue
            violaciones.append(f"{path.name}:{line}: {snippet[:120]}")
    assert not violaciones, "Datos sintéticos en dashboards activos:\n" + "\n".join(violaciones)


def test_dashboards_activos_sin_plotly_white():
    violaciones = []
    for path in _activos():
        text = path.read_text(encoding="utf-8")
        for m in FORBIDDEN_WHITE.finditer(text):
            line = text[: m.start()].count("\n") + 1
            violaciones.append(f"{path.name}:{line}")
    assert not violaciones, "Fondos claros Plotly en dashboards activos:\n" + "\n".join(violaciones)
