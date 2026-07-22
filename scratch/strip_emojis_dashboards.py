"""Quita emojis de dashboards Streamlit prioritarios (Etapa C)."""
from __future__ import annotations

import re
from pathlib import Path

FILES = [
    "frontend/dashboards/dashboard_meteorologico_profesional.py",
    "frontend/dashboards/dashboard_monitoreo_tiempo_real.py",
    "frontend/dashboards/dashboard_ia_ml_avanzado.py",
    "frontend/dashboards/dashboard_visualizaciones_avanzadas.py",
    "frontend/dashboards/dashboard_global_metricas.py",
    "frontend/dashboards/dashboard_agricola_inteligente.py",
]

EMOJI = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0000FE0F"
    "\U0000200D"
    "]+",
    flags=re.UNICODE,
)

root = Path(__file__).resolve().parents[1]
for rel in FILES:
    path = root / rel
    if not path.is_file():
        print("skip missing", rel)
        continue
    text = path.read_text(encoding="utf-8")
    new = EMOJI.sub("", text)
    new = re.sub(r'(["\'])\s{2,}', r"\1", new)
    new = re.sub(r"\s{2,}([\"'])", r"\1", new)
    new = re.sub(r"(#{1,4})\s{2,}", r"\1 ", new)
    new = re.sub(r"page_icon=\"\"", 'page_icon="METGO"', new)
    new = re.sub(r"page_icon=''", "page_icon='METGO'", new)
    if new != text:
        path.write_text(new, encoding="utf-8")
        print(f"cleaned {rel}: {len(text) - len(new)} chars")
    else:
        print(f"no change {rel}")
