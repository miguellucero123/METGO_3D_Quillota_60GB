"""Trunca código sintético tras st.stop() en dashboards del catálogo restantes."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "frontend" / "dashboards"

TARGETS = {
    "dashboard_agricultura_precision.py": "st.sidebar.markdown(\"---\")\nst.sidebar.caption(\"Modo ilustrativo:",
    "dashboard_alertas_automaticas.py": None,  # special
    "dashboard_unificado_diferenciado.py": "st.sidebar.caption(\"Modo demo: datos simulados",
    "dashboard_simple_optimizado.py": "st.sidebar.caption(\"Modo demo activo\")",
}


def truncate_before(path: Path, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    idx = text.find(marker)
    if idx < 0:
        print("MARKER NOT FOUND", path.name)
        return False
    # Keep everything before marker; ensure we end after previous st.stop()
    keep = text[:idx].rstrip() + "\n"
    path.write_text(keep, encoding="utf-8")
    print("truncated", path.name, "at", idx)
    return True


for name, marker in TARGETS.items():
    if marker is None:
        continue
    truncate_before(DASH / name, marker)

# Alertas: find st.stop after API block then cut before simulado generator
alertas = DASH / "dashboard_alertas_automaticas.py"
at = alertas.read_text(encoding="utf-8")
# Force radio to API only
at2 = at.replace(
    '["Alertas METGO (API)", "Historial simulado (demo)"]',
    '["Alertas METGO (API)"]',
)
ill = at2.find("Historial simulado")
# Find generar after API stop - look for "Función para generar alertas" or random.randint section
markers = [
    "\n# Función para generar alertas",
    "\ndef generar_alertas_automaticas",
    "\n@st.cache_data\ndef generar_alertas",
    "\n# Generar alertas simuladas",
    "for i in range(random.randint",
]
cut = -1
for m in markers:
    i = at2.find(m)
    if i >= 0 and (cut < 0 or i < cut):
        # Prefer cutting at function definitions; for random find previous blank+comment
        if m.startswith("\nfor i"):
            # find last st.stop before this
            stop = at2.rfind("st.stop()", 0, i)
            if stop >= 0:
                cut = at2.find("\n", stop) + 1
                break
        else:
            cut = i
            break
if cut > 0:
    alertas.write_text(at2[:cut].rstrip() + "\n", encoding="utf-8")
    print("truncated alertas at", cut)
else:
    alertas.write_text(at2, encoding="utf-8")
    print("alertas: radio only, no truncate point")

# Mobile: stop if no real data instead of synthetic fallback
mob = DASH / "dashboard_mobile_optimizado.py"
mt = mob.read_text(encoding="utf-8")
old = '''if datos is None:
    datos = generar_datos_mobile(estacion, vista)
    datos["hist"] = []
'''
new = '''if datos is None:
    st.warning("Sin datos — requiere API METGO (:8080).")
    st.stop()
'''
if old in mt:
    mt = mt.replace(old, new)
    # Remove the generar_datos_mobile function and anything that only serves demo charts with random
    # Truncate after function definition start if still present and unused - leave function but unused is ok for tests
    # Better: remove function entirely
    start = mt.find("\n# Función para generar datos móviles")
    if start < 0:
        start = mt.find("\n@st.cache_data\ndef generar_datos_mobile")
    end = mt.find("\nif datos is None:")
    if start > 0 and end > start:
        mt = mt[:start] + "\n" + mt[end:]
    mob.write_text(mt, encoding="utf-8")
    print("mobile: removed synth fallback")
else:
    print("mobile: pattern not found")
    # still try remove generator if fallback already changed
    if "generar_datos_mobile" in mt and "random.uniform" in mt:
        print("mobile still has generator - manual check needed")
