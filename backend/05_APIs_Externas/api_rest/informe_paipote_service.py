#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Informe operativo Paipote (HTML imprimible + PDF texto mínimo)."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from api_rest import ventilacion_service

TZ_CHILE = ZoneInfo("America/Santiago")


def _esc(x: Any) -> str:
    return html.escape("" if x is None else str(x))


def construir_informe_html(estacion_id: str = "paipote") -> str | None:
    pkg = ventilacion_service.construir_paquete(estacion_id)
    if not pkg:
        return None

    tramos = pkg.get("tramos_3h_24h") or []
    diaria = pkg.get("diaria") or []
    proy = pkg.get("proyeccion") or {}
    sinop = ", ".join(pkg.get("sinoptica_predominante") or [])

    rows_3h = "".join(
        f"<tr><td>{_esc(t.get('inicio'))}</td>"
        f"<td><b>{_esc(t.get('ventilacion'))}</b> ({_esc(t.get('ventilacion_label'))})</td>"
        f"<td>{_esc(t.get('viento_velocidad'))} m/s · {_esc(t.get('viento_direccion'))}°</td>"
        f"<td>{_esc(t.get('nubosidad_baja'))}%</td>"
        f"<td>{_esc(t.get('icono'))}</td></tr>"
        for t in tramos
    )
    rows_d = "".join(
        f"<tr><td>{_esc(d.get('fecha'))}</td>"
        f"<td>{_esc(d.get('icono'))}</td>"
        f"<td><b>{_esc(d.get('ventilacion'))}</b></td>"
        f"<td>{_esc(d.get('caracteristica'))}</td></tr>"
        for d in diaria
    )
    bloques = proy.get("bloques") or []
    rows_p = "".join(
        f"<tr><td>{_esc(b.get('periodo'))} d</td>"
        f"<td><b>{_esc(b.get('ventilacion'))}</b></td>"
        f"<td>{_esc(b.get('viento_superficie_ms'))} m/s</td>"
        f"<td>{_esc(b.get('confianza'))}</td></tr>"
        for b in bloques
    )
    vn = proy.get("vientos_predominantes") or {}
    media = vn.get("atmosfera_media") or {}
    altos = vn.get("niveles_altos") or {}

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"/>
<title>Informe ventilación Paipote</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#111;font-size:13px}}
h1{{font-size:1.4rem;margin:0 0 .4rem}} h2{{font-size:1.05rem;margin:1.4rem 0 .5rem;border-bottom:1px solid #ccc;padding-bottom:.25rem}}
.meta{{color:#444;margin-bottom:1rem}} table{{border-collapse:collapse;width:100%;margin:.5rem 0 1rem}}
th,td{{border:1px solid #bbb;padding:6px 8px;text-align:left}} th{{background:#f3f4f6}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-weight:700}}
.N{{background:#bbf7d0}} .R{{background:#fde68a}} .M{{background:#fecaca}}
.note{{font-size:11px;color:#666;margin-top:1.5rem}}
@media print{{body{{margin:12px}}}}
</style></head><body>
<h1>Informe operativo — Faena Paipote</h1>
<p class="meta">
  Estación {_esc(pkg.get('estacion_nombre'))} · Corrida <b>{_esc(pkg.get('corrida_utc'))} UTC</b>
  ({_esc(pkg.get('corrida_en'))}) · Generado {_esc(pkg.get('generado_en'))}<br/>
  Códigos: <span class="badge N">N</span> normal ·
  <span class="badge R">R</span> regular ·
  <span class="badge M">M</span> mala
</p>

<h2>1. Pronóstico 24 h (tramos de 3 horas)</h2>
<p>Configuraciones sinópticas predominantes: <b>{_esc(sinop)}</b></p>
<table>
<thead><tr><th>Inicio</th><th>Ventilación</th><th>Viento</th><th>Nubosidad baja</th><th>Cielo</th></tr></thead>
<tbody>{rows_3h or '<tr><td colspan="5">Sin datos</td></tr>'}</tbody>
</table>

<h2>2. Pronóstico 7–14 días</h2>
<table>
<thead><tr><th>Fecha</th><th>Icono</th><th>Vent.</th><th>Característica</th></tr></thead>
<tbody>{rows_d or '<tr><td colspan="4">Sin datos</td></tr>'}</tbody>
</table>

<h2>3. Proyección 30–90 días (STM / climatología)</h2>
<p>{_esc(proy.get('stm_nota'))}</p>
<table>
<thead><tr><th>Periodo</th><th>Vent.</th><th>Viento superficie</th><th>Confianza</th></tr></thead>
<tbody>{rows_p or '<tr><td colspan="4">Sin datos</td></tr>'}</tbody>
</table>
<p><b>Atmósfera media</b> (~{_esc(media.get('nivel_hpa'))} hPa): dir {_esc(media.get('dir_predominante_deg'))}° ·
{_esc(media.get('velocidad_media_ms'))} m/s<br/>
<b>Niveles altos</b> (~{_esc(altos.get('nivel_hpa'))} hPa): dir {_esc(altos.get('dir_predominante_deg'))}° ·
{_esc(altos.get('velocidad_media_ms'))} m/s</p>

<p class="note">Producto METGO proxy operativo para faena Paipote. No sustituye dictamen DMC ni modelación regulatoria AERMOD/CALPUFF.
Próxima corrida: {_esc(pkg.get('proxima_corrida_utc'))} UTC ({_esc(pkg.get('proxima_corrida_en'))}).</p>
</body></html>"""


def construir_informe_pdf_bytes(estacion_id: str = "paipote") -> bytes | None:
    """PDF mínimo (texto) sin dependencias externas."""
    pkg = ventilacion_service.construir_paquete(estacion_id)
    if not pkg:
        return None
    lines = [
        "INFORME OPERATIVO — FAENA PAIPOTE",
        f"Corrida {pkg.get('corrida_utc')} UTC | {pkg.get('generado_en')}",
        f"Codigos: N=normal R=regular M=mala",
        "",
        "=== 24 h (tramos 3 h) ===",
    ]
    for t in pkg.get("tramos_3h_24h") or []:
        lines.append(
            f"{t.get('inicio')}  V={t.get('ventilacion')}  "
            f"viento={t.get('viento_velocidad')}m/s {t.get('viento_direccion')}deg  "
            f"nub={t.get('nubosidad_baja')}%"
        )
    lines += ["", f"Sinoptica: {', '.join(pkg.get('sinoptica_predominante') or [])}", "", "=== 7-14 dias ==="]
    for d in pkg.get("diaria") or []:
        lines.append(f"{d.get('fecha')}  {d.get('icono')}  V={d.get('ventilacion')}  {d.get('caracteristica')}")
    lines += ["", "=== 30-90 dias ==="]
    proy = pkg.get("proyeccion") or {}
    for b in proy.get("bloques") or []:
        lines.append(
            f"{b.get('periodo')}  V={b.get('ventilacion')}  viento_sup={b.get('viento_superficie_ms')}"
        )
    lines.append(proy.get("stm_nota") or "")
    return _texto_a_pdf(lines)


# Caracteres fuera de WinAnsi → equivalentes ASCII (flechas, superíndices, etc.)
_PDF_UNICODE_MAP = str.maketrans(
    {
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "—": "-",
        "–": "-",
        "…": "...",
        "“": '"',
        "”": '"',
        "„": '"',
        "‘": "'",
        "’": "'",
        "´": "'",
        "²": "2",
        "³": "3",
        "¹": "1",
        "µ": "u",
        "×": "x",
        "•": "*",
        "\u00a0": " ",
    }
)


def _pdf_safe_text(s: str, *, max_len: int = 95) -> str:
    """Texto seguro para Helvetica + WinAnsiEncoding (latin-1 occidental)."""
    t = (s or "").translate(_PDF_UNICODE_MAP)
    # WinAnsi ≈ latin-1 para español (áéíóúñ¿¡°·)
    t = t.encode("latin-1", errors="replace").decode("latin-1")
    t = t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return t[:max_len]


def _texto_a_pdf(lines: list[str]) -> bytes:
    """Genera PDF 1.4 simple con Helvetica + WinAnsi (acentos ES legibles)."""
    content_lines = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    first = True
    y_lines = 0
    max_lines = 58
    page_contents: list[str] = []
    for raw in lines:
        text = _pdf_safe_text(raw)
        if y_lines >= max_lines:
            content_lines.append("ET")
            page_contents.append("\n".join(content_lines))
            content_lines = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
            first = True
            y_lines = 0
        if first:
            content_lines.append(f"({text}) Tj")
            first = False
        else:
            content_lines.append("T*")
            content_lines.append(f"({text}) Tj")
        y_lines += 1
    content_lines.append("ET")
    page_contents.append("\n".join(content_lines))

    objs: dict[int, bytes] = {}
    objs[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    font_id = 3
    # WinAnsi: á, ñ, °, etc. (sin esto Helvetica StandardEncoding corrompe acentos)
    objs[font_id] = (
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>"
    )
    next_id = 4
    page_ids = []
    for stream in page_contents:
        stream_b = stream.encode("latin-1", errors="replace")
        cont_id = next_id
        page_id = next_id + 1
        next_id += 2
        objs[cont_id] = (
            f"<< /Length {len(stream_b)} >>\nstream\n".encode() + stream_b + b"\nendstream"
        )
        objs[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {cont_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        ).encode()
        page_ids.append(page_id)

    kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
    objs[2] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>".encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets = {0: 0}
    max_obj = max(objs)
    for i in range(1, max_obj + 1):
        offsets[i] = len(out)
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(objs[i])
        out.extend(b"\nendobj\n")
    xref_pos = len(out)
    out.extend(f"xref\n0 {max_obj + 1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for i in range(1, max_obj + 1):
        out.extend(f"{offsets[i]:010d} 00000 n \n".encode())
    out.extend(
        f"trailer\n<< /Size {max_obj + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(out)
