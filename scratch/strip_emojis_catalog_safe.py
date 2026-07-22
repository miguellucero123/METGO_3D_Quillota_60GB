"""Inventario y strip seguro de emojis en dashboards del catálogo.
No colapsa whitespace; solo elimina caracteres emoji (y ZWJ/VS16 adjuntos).
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

# Rangos típicos de emoji + selectores
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F000-\U0001F02F"
    "\U0001F0A0-\U0001F0FF"
    "\U0000231A-\U0000231B"
    "\U00002328"
    "\U000023E9-\U000023F3"
    "\U000023F8-\U000023FA"
    "\U000025AA-\U000025FE"
    "\U00002B05-\U00002B55"
    "\U00003030\U0000303D"
    "\U00003297\U00003299"
    "\U0000203C\U00002049"
    "\U00002122-\U00002139"
    "\U00002194-\U00002199"
    "\U000024C2"
    "\U0000200D"  # ZWJ
    "\U0000FE0F"  # variation selector
    "\U0000FE0E"
    "]"
)

# Limpiar espacios dobles que quedan al quitar emoji en medio de texto UI
SPACE_FIX = re.compile(r"[ \t]{2,}")

CATALOG = [
    "dashboard_meteorologico_profesional.py",
    "dashboard_agricola_inteligente.py",
    "dashboard_monitoreo_tiempo_real.py",
    "dashboard_ia_ml_avanzado.py",
    "dashboard_visualizaciones_avanzadas.py",
    "dashboard_global_metricas.py",
    "dashboard_agricultura_precision.py",
    "dashboard_analisis_comparativo.py",
    "dashboard_alertas_automaticas.py",
    "dashboard_simple_optimizado.py",
    "dashboard_unificado_diferenciado.py",
    "dashboard_mobile_optimizado.py",
]


def post_fix_empty_ui(text: str) -> str:
    """Evita page_icon/botones vacíos tras quitar emojis-only.

    No tocar literales con \\s entre comillas y el siguiente token del archivo
    (p. ej. cierre de docstring + from __future__).
    """
    text = re.sub(r'page_icon\s*=\s*""', 'page_icon="M"', text)
    text = re.sub(r'st\.button\(\s*""\s*,', 'st.button("Config",', text)
    text = re.sub(r'st\.button\(\s*""\s*\)', 'st.button("OK")', text)
    return text


def strip_line(line: str) -> str:
    """Elimina emojis de una sola línea; no altera el resto del archivo."""
    if not EMOJI_RE.search(line):
        return line
    # Preserve leading indentation exactly
    lead = len(line) - len(line.lstrip(" \t"))
    indent = line[:lead]
    ending = ""
    body = line[lead:]
    if body.endswith("\r\n"):
        ending = "\r\n"
        body = body[:-2]
    elif body.endswith("\n"):
        ending = "\n"
        body = body[:-1]
    elif body.endswith("\r"):
        ending = "\r"
        body = body[:-1]
    body = EMOJI_RE.sub("", body)
    # Colapsar solo espacios/tabs internos duplicados (no saltos de línea)
    body = SPACE_FIX.sub(" ", body)
    # " Temperatura" → "Temperatura" (emoji iba al inicio del literal)
    body = re.sub(
        r'(["\']) +([A-Za-zÁÉÍÓÚáéíóúñÑ0-9*#¿¡])',
        r"\1\2",
        body,
    )
    body = body.rstrip(" \t")
    return indent + body + ending


def process(path: pathlib.Path, apply: bool) -> int:
    raw = path.read_bytes()
    # Detectar newline del archivo
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    hits = 0
    out: list[str] = []
    for i, line in enumerate(lines, 1):
        if EMOJI_RE.search(line):
            hits += 1
            cleaned = strip_line(line)
            if not apply:
                em = "".join(sorted(set(EMOJI_RE.findall(line))))
                safe = (line.rstrip()[:110]).encode("ascii", "backslashreplace").decode("ascii")
                print(f"  L{i} [{em.encode('ascii','backslashreplace').decode()}] {safe}")
            out.append(cleaned)
        else:
            out.append(line)
    if apply and hits:
        new_text = post_fix_empty_ui("".join(out))
        # Preservar si el original terminaba en newline
        if text.endswith("\n") and not new_text.endswith("\n"):
            new_text += "\n"
        path.write_text(new_text, encoding="utf-8", newline="")  # ya trae endings
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--base", default="frontend/dashboards")
    args = ap.parse_args()
    base = pathlib.Path(args.base)
    total = 0
    for name in CATALOG:
        p = base / name
        if not p.exists():
            print(f"MISSING {name}")
            continue
        print(f"\n=== {name} ===")
        hits = process(p, args.apply)
        total += hits
        print(f"  -> {hits} líneas con emoji" + (" (aplicado)" if args.apply and hits else ""))
    print(f"\nTOTAL líneas: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
