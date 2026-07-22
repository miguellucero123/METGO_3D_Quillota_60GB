"""Repara docstrings pegados al cuerpo tras el strip de emojis."""
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

# """text"""NEXT -> """text"""\n\nNEXT  (when NEXT starts a statement)
FIX = re.compile(
    r'("""[^"]*?""")(?=(from |import |def |class |[A-Za-z_][A-Za-z0-9_]*\s*=|st\.|if |for |while |return |try:|with |@))',
    re.DOTALL,
)

root = Path(__file__).resolve().parents[1]
for rel in FILES:
    path = root / rel
    text = path.read_text(encoding="utf-8-sig")
    new = FIX.sub(r"\1\n", text)
    # Also fix ):"""Doc"""body
    new = re.sub(
        r'(\):)("""[^"]*?""")(?=[A-Za-z_])',
        r"\1\n    \2\n    ",
        new,
    )
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("fixed", rel)
    else:
        print("no change", rel)
