"""Trunca modos sintéticos en monitoreo y análisis comparativo (solo API)."""
from __future__ import annotations

from pathlib import Path

# --- Monitoreo: solo API ---
mon = Path("frontend/dashboards/dashboard_monitoreo_tiempo_real.py")
text = mon.read_text(encoding="utf-8")
marker = "    st.stop()\n\n# --- Modo simulación IoT (demo) ---"
idx = text.find(marker)
if idx == -1:
    marker2 = "    st.stop()\n\n# --- Modo simulación"
    idx = text.find(marker2)
if idx != -1:
    keep = text[: idx + len("    st.stop()\n")]
    keep += """
st.caption(
    f"Sistema METGO — Monitoreo · datos reales API · "
)
"""
    mon.write_text(keep, encoding="utf-8")
    # Also force radio to API only
    keep = mon.read_text(encoding="utf-8")
    keep = keep.replace(
        '["Estaciones METGO (API)", "Simulación sensores"]',
        '["Estaciones METGO (API)"]',
    )
    mon.write_text(keep, encoding="utf-8")
    print("monitoreo truncated")
else:
    print("monitoreo marker not found")

# --- Análisis comparativo: solo API ---
cmp = Path("frontend/dashboards/dashboard_analisis_comparativo.py")
text = cmp.read_text(encoding="utf-8")
# Force API-only radio
text = text.replace(
    '["API METGO (valle)", "Series ilustrativas (5 años)"]',
    '["API METGO (valle)"]',
)
idx = text.find("st.stop()\n\nst.info(\n    \"**Modo ilustrativo:**")
if idx == -1:
    idx = text.find('st.stop()\n\nst.info(\n    "**Modo ilustrativo:')
if idx == -1:
    # find second st.stop after hist
    positions = [i for i in range(len(text)) if text.startswith("    st.stop()", i)]
    # use the one before ilustrativo
    ill = text.find("Modo ilustrativo")
    if ill != -1:
        # find st.stop before ill
        idx = text.rfind("st.stop()", 0, ill)
        if idx != -1:
            # include st.stop() line
            end = text.find("\n", idx) + 1
            keep = text[:end] + "\n"
            cmp.write_text(keep, encoding="utf-8")
            print("analisis truncated at", end)
        else:
            print("analisis stop not found")
    else:
        cmp.write_text(text, encoding="utf-8")
        print("analisis radio only, no truncate")
else:
    end = text.find("\n", idx) + 1
    keep = text[:end] + "\n"
    # apply radio replace already in text before truncate - re-read
    keep = text[:end]
    keep = keep.replace(
        '["API METGO (valle)", "Series ilustrativas (5 años)"]',
        '["API METGO (valle)"]',
    )
    cmp.write_text(keep + "\n", encoding="utf-8")
    print("analisis truncated ilustrativo")
