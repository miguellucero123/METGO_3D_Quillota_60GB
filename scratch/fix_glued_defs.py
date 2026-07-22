"""Inserta saltos de línea antes de def/class/from cuando quedaron pegados."""
from __future__ import annotations

import re
from pathlib import Path

FILES = [
    "frontend/dashboards/dashboard_meteorologico_profesional.py",
    "frontend/dashboards/dashboard_monitoreo_tiempo_real.py",
    "frontend/dashboards/dashboard_visualizaciones_avanzadas.py",
    "frontend/dashboards/dashboard_global_metricas.py",
    "frontend/dashboards/dashboard_agricola_inteligente.py",
]

# Cualquier carácter no-espacio (excepto inicio de línea) pegado a def/class/from/import/@
PATTERNS = [
    (re.compile(r"([^\s\n])(def )"), r"\1\n\n\2"),
    (re.compile(r"([^\s\n])(class )"), r"\1\n\n\2"),
    (re.compile(r'([^\s\n])(from __future__)'), r"\1\n\n\2"),
    (re.compile(r'([^\s\n])(@st\.)'), r"\1\n\n\2"),
    (re.compile(r'([^\s\n])(@[a-zA-Z_])'), r"\1\n\n\2"),
    # Docstring de función pegado al cuerpo: """..."""code
    (re.compile(r'("""[^"\n]*""")([A-Za-z_])'), r"\1\n    \2"),
]

root = Path(__file__).resolve().parents[1]
for rel in FILES:
    path = root / rel
    text = path.read_text(encoding="utf-8-sig")
    new = text
    for _ in range(5):  # apply repeatedly until stable
        prev = new
        for pat, repl in PATTERNS:
            new = pat.sub(repl, new)
        if new == prev:
            break
    # Indent bodies that lost indent after """...\n    X became wrong - skip for now
    path.write_text(new, encoding="utf-8")
    print("rewrote", rel, "delta", len(new) - len(text))
