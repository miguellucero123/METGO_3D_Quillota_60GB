#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Informe de incidentes real para VENTORA Izaje Mar (puertos).

Reemplaza el stub `/reporte-mensual` que solo mostraba metadata del sitio.
Consume el historial real de `alertas_store` (poblado por
`puerto_alert_job.py`): ráfaga/delta real, umbral vigente y hora UTC de
cada evento de suspensión — la evidencia que el material comercial ya
promete pero que hasta ahora no existía.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any

logger = logging.getLogger(__name__)


def _obtener_incidentes(sitio_id: str, *, dias: int = 30) -> list[dict[str, Any]]:
    from api_rest.integracion import alertas_store

    items = alertas_store.listar_historial(estacion_id=sitio_id, limite=500)
    items = [x for x in items if x.get("origen") == "puerto_incidente"]
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max(1, dias))).isoformat()
    items = [x for x in items if str(x.get("registrado_en") or "") >= cutoff]
    return items


def _fmt_dt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M UTC")
    except ValueError:
        return str(iso)


def construir_incidentes_html(sitio_id: str, *, dias: int = 30) -> str | None:
    from api_rest.spati.puerto_pronostico_service import get_puerto

    puerto = get_puerto(sitio_id)
    if not puerto:
        return None
    incidentes = _obtener_incidentes(sitio_id, dias=dias)
    generado = datetime.now(timezone.utc).isoformat(timespec="seconds")

    filas = ""
    for it in incidentes:
        nivel = (it.get("nivel") or "").upper()
        color = "#dc2626" if nivel == "CRITICAL" else "#f59e0b" if nivel == "WARNING" else "#64748b"
        tipo = it.get("tipo_incidente") or "—"
        if tipo == "sustained_wind":
            detalle = f"{it.get('viento_kmh', '—')} km/h (umbral {it.get('umbral_kmh', '—')} km/h)"
        elif tipo == "pendulum_resonance":
            detalle = f"Δ período {it.get('delta_s', '—')} s (riesgo resonancia)"
        else:
            detalle = it.get("mensaje") or "—"
        filas += (
            "<tr>"
            f"<td>{_fmt_dt(it.get('valid_time'))}</td>"
            f"<td><span style='color:{color};font-weight:700'>{nivel or '—'}</span></td>"
            f"<td>{tipo}</td>"
            f"<td>{detalle}</td>"
            f"<td>{it.get('duracion_horas', '—')} h</td>"
            f"<td style='font-size:11px;color:#64748b'>{_fmt_dt(it.get('registrado_en'))}</td>"
            "</tr>"
        )
    if not incidentes:
        filas = (
            "<tr><td colspan='6' style='text-align:center;color:#64748b;padding:24px'>"
            f"Sin incidentes registrados en los últimos {dias} días para este sitio."
            "</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>VENTORA · Informe de incidentes {puerto.get('nombre')}</title>
<style>
body{{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:32px}}
.card{{max-width:900px;margin:0 auto;background:#111827;border:1px solid #1e293b;border-radius:12px;padding:28px}}
h1{{margin:0 0 8px;color:#10b981;font-size:20px}} .muted{{color:#94a3b8;font-size:13px}}
table{{width:100%;border-collapse:collapse;margin-top:20px;font-size:13px}}
th,td{{padding:8px 10px;border-bottom:1px solid #1e293b;text-align:left}}
th{{color:#94a3b8;font-size:11px;text-transform:uppercase}}
.note{{margin-top:24px;font-size:11px;color:#64748b;line-height:1.5}}
</style></head><body><div class="card">
<h1>Informe de incidentes — VENTORA Izaje Mar</h1>
<p class="muted">{puerto.get('nombre')} ({puerto.get('sitio_id')}) · últimos {dias} días · generado {generado}</p>
<table>
<thead><tr><th>Hora del evento (UTC)</th><th>Nivel</th><th>Tipo</th><th>Detalle real</th><th>Duración</th><th>Registrado</th></tr></thead>
<tbody>{filas}</tbody>
</table>
<p class="note">
Cada fila corresponde a un evento real detectado por el pronóstico multi-modelo
(ECMWF+ICON+GFS) y la física de resonancia pendular, no a un valor de ejemplo.
"Hora del evento" es la marca UTC de la ventana pronosticada que cruzó el umbral
vigente en ese momento; "Registrado" es cuándo el sistema lo detectó. Los
umbrales por sitio se configuran en /api/public/spati/{sitio_id}/umbrales.
</p>
<p class="note">METGO 3D SpA · contacto@metgo3d.com</p>
</div></body></html>"""


def _html_a_pdf_bytes(html: str) -> bytes | None:
    try:
        from xhtml2pdf import pisa
    except ImportError:
        logger.warning("xhtml2pdf no instalado; informe de incidentes cae a texto plano")
        return None
    buf = BytesIO()
    try:
        result = pisa.CreatePDF(src=html, dest=buf, encoding="utf-8")
    except Exception as exc:
        logger.warning("xhtml2pdf fallo (incidentes): %s", exc)
        return None
    if result.err:
        logger.warning("xhtml2pdf err=%s (incidentes)", result.err)
        return None
    raw = buf.getvalue()
    return raw if raw.startswith(b"%PDF") else None


def construir_incidentes_pdf_bytes(sitio_id: str, *, dias: int = 30) -> bytes | None:
    html = construir_incidentes_html(sitio_id, dias=dias)
    if not html:
        return None
    pdf = _html_a_pdf_bytes(html)
    if pdf:
        return pdf
    from api_rest.informe_paipote_service import _texto_a_pdf
    from api_rest.spati.puerto_pronostico_service import get_puerto

    puerto = get_puerto(sitio_id) or {}
    incidentes = _obtener_incidentes(sitio_id, dias=dias)
    lines = [
        "METGO - Informe de incidentes VENTORA Izaje Mar",
        f"{puerto.get('nombre')} ({sitio_id}) - ultimos {dias} dias",
        "",
    ]
    if not incidentes:
        lines.append("Sin incidentes registrados en el periodo.")
    for it in incidentes:
        lines.append(
            f"{_fmt_dt(it.get('valid_time'))} | {it.get('nivel')} | "
            f"{it.get('tipo_incidente')} | {it.get('mensaje')}"
        )
    return _texto_a_pdf(lines)


def construir_incidentes_csv(sitio_id: str, *, dias: int = 30) -> str | None:
    from api_rest.spati.puerto_pronostico_service import get_puerto

    puerto = get_puerto(sitio_id)
    if not puerto:
        return None
    incidentes = _obtener_incidentes(sitio_id, dias=dias)

    def esc(v: Any) -> str:
        if v is None:
            return ""
        s = str(v)
        if any(c in s for c in (",", '"', "\n", "\r")):
            return '"' + s.replace('"', '""') + '"'
        return s

    lines = [
        "sitio_id,nombre,hora_evento_utc,nivel,tipo,viento_kmh,umbral_kmh,delta_resonancia_s,duracion_horas,registrado_en"
    ]
    for it in incidentes:
        lines.append(
            ",".join(
                esc(v)
                for v in (
                    sitio_id,
                    puerto.get("nombre"),
                    it.get("valid_time"),
                    it.get("nivel"),
                    it.get("tipo_incidente"),
                    it.get("viento_kmh"),
                    it.get("umbral_kmh"),
                    it.get("delta_s"),
                    it.get("duracion_horas"),
                    it.get("registrado_en"),
                )
            )
        )
    return "﻿" + "\n".join(lines) + "\n"
