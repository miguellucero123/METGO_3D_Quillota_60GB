"""Limpieza final radios API-only y mobile demo."""
from __future__ import annotations

from pathlib import Path

DASH = Path(__file__).resolve().parents[1] / "frontend" / "dashboards"

replacements = [
    (
        "dashboard_simple_optimizado.py",
        '["API METGO (OpenMeteo)", "Vista demo (valores fijos)"]',
        '["API METGO (OpenMeteo)"]',
    ),
    (
        "dashboard_unificado_diferenciado.py",
        '["API METGO (valle)", "Vista integrada demo"]',
        '["API METGO (valle)"]',
    ),
    (
        "dashboard_agricultura_precision.py",
        '["API METGO (valle)", "Series ilustrativas (5 años)"]',
        '["API METGO (valle)"]',
    ),
]

for name, old, new in replacements:
    p = DASH / name
    t = p.read_text(encoding="utf-8")
    if old in t:
        p.write_text(t.replace(old, new), encoding="utf-8")
        print("radio", name)
    else:
        print("radio miss", name)

p = DASH / "dashboard_alertas_automaticas.py"
t = p.read_text(encoding="utf-8")
idx = t.find('st.sidebar.caption("Modo demo: alertas aleatorias')
if idx > 0:
    p.write_text(t[:idx].rstrip() + "\n", encoding="utf-8")
    print("alertas cut leftover")
else:
    print("alertas ok")

p = DASH / "dashboard_mobile_optimizado.py"
t = p.read_text(encoding="utf-8")
r = t.find("random.uniform")
if r > 0:
    cut = None
    for hdr in ('st.markdown("###', "# Gráfico", "fig = make_subplots", "horas = list(range"):
        h = t.rfind(hdr, 0, r)
        if h > 200:
            cut = h
            break
    if cut:
        keep = (
            t[:cut].rstrip()
            + '\n\nst.caption("Vista móvil · datos API METGO · Vue http://127.0.0.1:5173")\n'
        )
        p.write_text(keep, encoding="utf-8")
        print("mobile truncated at", cut)
    else:
        print("mobile: could not find cut")
else:
    print("mobile: no random left")
