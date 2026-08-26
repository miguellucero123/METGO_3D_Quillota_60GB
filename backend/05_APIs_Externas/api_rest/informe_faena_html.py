#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plantilla HTML ejecutiva del informe ambiental (impresión / PDF via xhtml2pdf).

Layout compatible con motores PDF: @page A4, display:table (sin flex/grid en body).
Tema claro (fondo #f4f7f6, hoja blanca) — no dark mode.
"""

from __future__ import annotations

from html import escape
from typing import Any


def _esc(v: Any) -> str:
    if v is None or v == "":
        return "—"
    return escape(str(v))


def _num(v: Any, nd: int = 1) -> str:
    if v is None or v == "":
        return "—"
    try:
        return f"{round(float(v), nd)}"
    except (TypeError, ValueError):
        return escape(str(v))


def _cell_val(v: Any, *, nd: int = 1, unit: str = "", critical: bool = False) -> str:
    txt = _num(v, nd)
    if unit and txt != "—":
        txt = f"{txt} {escape(unit)}"
    cls = "val crit" if critical and txt != "—" else "val"
    return f'<td class="{cls}">{txt}</td>'


def _rango_cells(st: dict[str, Any] | None, unit: str = "") -> str:
    st = st or {}
    if st.get("min") is None and st.get("max") is None and st.get("avg") is None:
        return (
            '<td class="val">—</td><td class="val">—</td><td class="val">—</td>'
        )
    u = f" {escape(unit)}" if unit else ""
    return (
        f'<td class="val">{_num(st.get("min"))}{u}</td>'
        f'<td class="val">{_num(st.get("max"))}{u}</td>'
        f'<td class="val">{_num(st.get("avg"))}{u}</td>'
    )


def _nivel_cls(nivel: str | None) -> str:
    n = (nivel or "").strip().lower()
    if n == "rojo":
        return "nv-rojo"
    if n == "amarillo":
        return "nv-amarillo"
    if n == "verde":
        return "nv-verde"
    return "nv-neutro"


def _es_critico_rafaga(ms: Any) -> bool:
    try:
        return float(ms) >= 10.0
    except (TypeError, ValueError):
        return False


def _aviso_bloque(pkg: dict[str, Any]) -> str:
    partes: list[str] = []
    if pkg.get("aviso"):
        partes.append(str(pkg["aviso"]))
    fuente = pkg.get("fuente") or {}
    if pkg.get("degradado") or fuente.get("meteo") == "synthetic_degraded":
        partes.append(
            "Nota: paquete estimado / degradado (Open-Meteo no disponible o rate limit)."
        )
    if not partes:
        return ""
    body = "<br/>".join(escape(p) for p in partes)
    return f'<div class="banner-aviso"><strong>AVISO</strong> — {body}</div>'


def _cards_ops(ops: dict[str, Any]) -> str:
    acts = (ops or {}).get("actividades") or {}
    orden = ["izaje", "caminos", "botaderos"]
    ids = [a for a in orden if a in acts] + [a for a in acts if a not in orden]
    if not ids:
        return '<p class="muted">Sin evaluación operativa.</p>'
    cells = []
    for aid in ids:
        av = acts.get(aid) or {}
        nivel = (av.get("nivel") or "—").lower()
        raz_raw = ", ".join(str(r).replace("→", "→") for r in (av.get("razones") or []))
        raz = escape(raz_raw) if raz_raw else "Sin restricciones"
        cells.append(
            f'<td class="ops-card {_nivel_cls(nivel)}">'
            f'<div class="ops-label">{escape(aid.upper())}</div>'
            f'<div class="ops-nivel">{escape(nivel)}</div>'
            f'<div class="ops-raz">{raz}</div>'
            f"</td>"
        )
    # Rellenar a 3 columnas si hace falta
    while len(cells) < 3:
        cells.append('<td class="ops-card nv-neutro empty">&nbsp;</td>')
    return (
        '<table class="ops-row" cellspacing="0" cellpadding="0"><tr>'
        + "".join(cells[:3])
        + "</tr></table>"
    )


def _tabla_kv(rows: list[tuple[str, str]], *, critical_keys: set[str] | None = None) -> str:
    critical_keys = critical_keys or set()
    body = []
    for i, (k, v) in enumerate(rows):
        zebra = " zebra" if i % 2 else ""
        crit = " crit" if k in critical_keys else ""
        body.append(
            f'<tr class="{zebra}"><th>{escape(k)}</th>'
            f'<td class="val{crit}">{v}</td></tr>'
        )
    return (
        '<table class="data">'
        '<thead><tr><th class="col-k">Parámetro</th><th class="col-v">Valor</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def render_informe_ejecutivo_html(
    pkg: dict[str, Any],
    *,
    resumen: dict[str, Any],
    tramos: list[dict[str, Any]] | None = None,
    mvo: dict[str, Any] | None = None,
) -> str:
    """HTML A4 ejecutivo (tema claro) para vista previa e impresión/PDF."""
    a = pkg.get("actual") or {}
    nieve = pkg.get("nieve") or {}
    flags = pkg.get("flags") or {}
    ops = pkg.get("operaciones") or {}
    gen = pkg.get("generado_en") or "—"
    alt = pkg.get("altitud_m")
    alt_txt = f"{_esc(alt)} m s.n.m." if alt is not None else "—"
    raf_crit = _es_critico_rafaga(a.get("rafaga_10m_ms"))

    meteo_rows = [
        ("Temperatura", f"{_num(a.get('temperatura_c'), 1)} °C"),
        ("Humedad relativa", f"{_num(a.get('humedad_relativa_pct'), 1)} %"),
        ("Precipitación", f"{_num(a.get('precipitacion_mm'), 2)} mm"),
        ("Snowfall", f"{_num(a.get('snowfall_mm'), 2)} mm"),
        ("Visibilidad", f"{_num(a.get('visibilidad_m'), 0)} m"),
        ("Presión MSL", f"{_num(a.get('presion_msl_hpa'), 1)} hPa"),
        (
            "Viento 10 m",
            f"{_num(a.get('viento_10m_ms'), 2)} m/s · {_num(a.get('viento_10m_dir_deg'), 0)}°",
        ),
        ("Ráfaga 10 m", f"{_num(a.get('rafaga_10m_ms'), 2)} m/s"),
        (
            "Viento 100 m",
            f"{_num(a.get('viento_100m_ms'), 2)} m/s · {_num(a.get('viento_100m_dir_deg'), 0)}°",
        ),
        (
            "Nieve acum. 72 h / 24 h",
            f"{_num(nieve.get('acumulacion_proxy_cm'), 1)} cm / "
            f"{_num(nieve.get('acumulacion_24h_cm'), 1)} cm",
        ),
    ]
    aire_rows = [
        ("PM2.5", f"{_num(a.get('pm2_5'), 1)} µg/m³"),
        ("PM10", f"{_num(a.get('pm10'), 1)} µg/m³"),
        ("SO₂", f"{_num(a.get('so2'), 1)} µg/m³"),
        ("NO₂", f"{_num(a.get('no2'), 1)} µg/m³"),
        ("O₃", f"{_num(a.get('o3'), 1)} µg/m³"),
        ("Dust", f"{_num(a.get('dust'), 1)} µg/m³"),
        ("ICAP", f"{_num(a.get('icap'), 0)} · {_esc(a.get('nivel_icap'))}"),
    ]
    crit_keys = {"Ráfaga 10 m"} if raf_crit else set()

    resumen_rows = "".join(
        [
            "<tr><th>Temperatura</th>"
            + _rango_cells(resumen.get("temperatura_c"), "°C")
            + "</tr>",
            "<tr class='zebra'><th>Viento 10 m</th>"
            + _rango_cells(resumen.get("viento_10m_ms"), "m/s")
            + "</tr>",
            "<tr><th>Ráfaga</th>"
            + _rango_cells(resumen.get("rafaga_10m_ms"), "m/s")
            + "</tr>",
            "<tr class='zebra'><th>Visibilidad</th>"
            + _rango_cells(resumen.get("visibilidad_m"), "m")
            + "</tr>",
            "<tr><th>Snowfall suma</th>"
            f'<td class="val" colspan="3">{_num(resumen.get("snowfall_mm_suma"), 2)} mm</td></tr>',
            "<tr class='zebra'><th>PM2.5</th>"
            + _rango_cells(resumen.get("pm2_5"), "µg/m³")
            + "</tr>",
            "<tr><th>PM10</th>"
            + _rango_cells(resumen.get("pm10"), "µg/m³")
            + "</tr>",
            "<tr class='zebra'><th>SO₂ / NO₂</th>"
            + _rango_cells(resumen.get("so2"), "µg/m³")
            + "</tr>",
        ]
    )

    tramos = tramos or []
    tramos_body = ""
    for i, t in enumerate(tramos):
        zebra = " zebra" if i % 2 else ""
        rc = _es_critico_rafaga(t.get("rafaga_max_ms"))
        tramos_body += (
            f'<tr class="{zebra}">'
            f"<td>{_esc(t.get('inicio'))}</td>"
            f'<td class="val">{_num(t.get("viento_ms"), 2)}</td>'
            f'<td class="val{" crit" if rc else ""}">{_num(t.get("rafaga_max_ms"), 2)}</td>'
            f'<td class="val">{_num(t.get("snowfall_mm"), 2)}</td>'
            f'<td class="val">{_num(t.get("pm2_5"), 1)}</td>'
            "</tr>"
        )
    if not tramos_body:
        tramos_body = '<tr><td colspan="5" class="muted">Sin serie horaria</td></tr>'

    estaciones = pkg.get("estaciones_area") or []
    est_body = ""
    for i, e in enumerate(estaciones):
        zebra = " zebra" if i % 2 else ""
        est_body += (
            f'<tr class="{zebra}">'
            f"<td>{_esc(e.get('nombre'))}</td>"
            f"<td>{_esc(e.get('rol'))}</td>"
            f'<td class="val">{_esc(e.get("lat"))}</td>'
            f'<td class="val">{_esc(e.get("lon"))}</td>'
            f"<td>{_esc(e.get('fuente'))}</td>"
            "</tr>"
        )
    if not est_body:
        est_body = '<tr><td colspan="5" class="muted">Sin puntos de área</td></tr>'

    mvo_html = ""
    if mvo:
        aire = mvo.get("aire") or {}
        meteo = mvo.get("meteo") or {}
        iot = mvo.get("iot") or {}
        mvo_html = f"""
  <h2>Modelo vs observado (M5)</h2>
  <p class="meta-line">Estado: <strong>{_esc(mvo.get('estado'))}</strong>
     · Estación {_esc(mvo.get('estacion_id'))}
     · IoT {_esc(iot.get('n_lecturas'))} lecturas</p>
  <table class="data">
    <thead><tr>
      <th>Dominio</th><th>Pares</th><th>Sesgo PM2.5 / T</th><th>Sesgo PM10</th>
    </tr></thead>
    <tbody>
      <tr>
        <th>Aire</th>
        <td class="val">{_esc(aire.get('n_pares'))}</td>
        <td class="val">{_num((aire.get('pm25') or {}).get('sesgo_medio'), 1)}</td>
        <td class="val">{_num((aire.get('pm10') or {}).get('sesgo_medio'), 1)}</td>
      </tr>
      <tr class="zebra">
        <th>Meteo</th>
        <td class="val">{_esc(meteo.get('n_pares'))}</td>
        <td class="val">{_num((meteo.get('temperatura') or {}).get('sesgo_medio'), 1)}</td>
        <td class="val">—</td>
      </tr>
    </tbody>
  </table>
"""

    nivel_g = flags.get("nivel_global") or "—"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>VENTORA — Informe {_esc(pkg.get('nombre'))}</title>
<style>
  @page {{
    size: A4;
    margin: 15mm;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
    color: #1e293b;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.4;
  }}
  .sheet {{
    background: #ffffff;
    padding: 0;
  }}
  .header-banner {{
    background: #0f172a;
    color: #ffffff;
    padding: 20px;
    border-bottom: 5px solid #0ea5e9;
    margin-bottom: 20px;
  }}
  table.header-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  table.header-table td {{ vertical-align: middle; }}
  .brand {{
    font-size: 26pt;
    font-weight: 900;
    color: #0ea5e9;
    letter-spacing: 1px;
    margin: 0;
  }}
  .subtitle {{
    font-size: 10pt;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 4px 0 0 0;
  }}
  .meta-right {{
    text-align: right;
    font-size: 9pt;
    color: #cbd5e1;
    line-height: 1.5;
  }}
  .meta-right strong {{
    color: #ffffff;
    font-size: 11pt;
  }}
  .badge {{
    display: inline-block;
    background: #0ea5e9;
    color: #ffffff;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8pt;
    font-weight: bold;
    margin-left: 8px;
  }}
  .banner-aviso {{
    background: #fffbeb;
    color: #b45309;
    border-left: 5px solid #f59e0b;
    padding: 10px 14px;
    margin: 0 0 16px 0;
    font-size: 9pt;
  }}
  h2 {{
    font-size: 13pt;
    color: #0f172a;
    margin: 20px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #e2e8f0;
    page-break-after: avoid;
  }}
  .flags-line {{
    font-size: 9pt;
    color: #64748b;
    margin: 0 0 12px 0;
    background: #f8fafc;
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}
  .cols-2 {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 16px 0;
    margin: 0 -16px;
  }}
  .cols-2 > tbody > tr > td {{
    width: 50%;
    vertical-align: top;
  }}
  .col-title {{
    font-size: 9pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #0ea5e9;
    margin: 0 0 8px 0;
    page-break-after: avoid;
  }}
  table.data {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    border: 1px solid #e2e8f0;
  }}
  table.data th,
  table.data td {{
    padding: 8px 10px;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
    font-size: 9pt;
  }}
  table.data thead th {{
    background: #f1f5f9;
    color: #475569;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 800;
  }}
  table.data tbody th {{
    font-weight: 600;
    color: #334155;
    width: 45%;
    background: transparent;
  }}
  table.data tr.zebra td,
  table.data tr.zebra th {{
    background: #f8fafc;
  }}
  td.val {{
    text-align: right;
    font-weight: bold;
    color: #0f172a;
    white-space: nowrap;
  }}
  td.val.crit {{
    color: #ef4444;
  }}
  .ops-row {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 10px 0;
    margin: 0 -10px 16px;
  }}
  .ops-card {{
    width: 33.33%;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top-width: 5px;
    border-radius: 6px;
    padding: 12px 14px;
    vertical-align: top;
  }}
  .ops-card.nv-rojo {{ border-top-color: #ef4444; background: #fef2f2; }}
  .ops-card.nv-amarillo {{ border-top-color: #f59e0b; background: #fffbeb; }}
  .ops-card.nv-verde {{ border-top-color: #10b981; background: #ecfdf5; }}
  .ops-card.nv-neutro {{ border-top-color: #94a3b8; background: #f8fafc; }}
  .ops-label {{
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b;
    margin-bottom: 4px;
    font-weight: 800;
  }}
  .ops-nivel {{
    font-size: 14pt;
    font-weight: 900;
    text-transform: uppercase;
  }}
  .nv-rojo .ops-nivel {{ color: #b91c1c; }}
  .nv-amarillo .ops-nivel {{ color: #b45309; }}
  .nv-verde .ops-nivel {{ color: #047857; }}
  .ops-raz {{
    font-size: 8.5pt;
    color: #64748b;
    margin-top: 6px;
    line-height: 1.4;
  }}
  .footer {{
    margin-top: 30px;
    padding-top: 15px;
    border-top: 2px solid #e2e8f0;
    font-size: 8pt;
    color: #94a3b8;
    text-align: justify;
  }}
  .muted {{ color: #94a3b8; }}
  .pill-nivel {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 8pt;
  }}
  .pill-nivel.nv-rojo {{ background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }}
  .pill-nivel.nv-amarillo {{ background: #fffbeb; color: #f59e0b; border: 1px solid #fde68a; }}
  .pill-nivel.nv-verde {{ background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; }}
</style>
</head>
<body>
<div class="sheet">
  <div class="header-banner">
    <table class="header-table">
      <tr>
        <td>
          <div class="brand">VENTORA</div>
          <div class="subtitle">Informe Operacional de Terminal</div>
        </td>
        <td class="meta-right">
          <strong>{_esc(pkg.get('nombre'))}</strong>
          <span class="badge">{_esc(pkg.get('faena_id'))}</span><br/>
          Lat {_esc(pkg.get('lat'))} · Lon {_esc(pkg.get('lon'))}<br/>
          Altitud {alt_txt}<br/>
          Generado {_esc(gen)}
        </td>
      </tr>
    </table>
  </div>

  {_aviso_bloque(pkg)}

  <h2>Flags operativos (M3)</h2>
  <p class="flags-line">Nivel global
    <span class="pill-nivel {_nivel_cls(str(nivel_g))}">{_esc(nivel_g)}</span>
    · nieve activa: {_esc(flags.get('flag_nieve_activa'))}
    · izaje restringido: {_esc(flags.get('flag_izaje_restringido'))}
    · caminos: {_esc(flags.get('flag_caminos_restringido'))}
    · botaderos: {_esc(flags.get('flag_botaderos_restringido'))}
  </p>
  {_cards_ops(ops)}

  <h2>Condición actual</h2>
  <table class="cols-2"><tr>
    <td>
      <div class="col-title">Meteorología</div>
      {_tabla_kv(meteo_rows, critical_keys=crit_keys)}
    </td>
    <td>
      <div class="col-title">Calidad del aire</div>
      {_tabla_kv(aire_rows)}
    </td>
  </tr></table>

  <h2>Resumen horizonte 72 h</h2>
  <table class="data">
    <thead><tr>
      <th>Variable</th><th>Mín</th><th>Máx</th><th>Media</th>
    </tr></thead>
    <tbody>{resumen_rows}</tbody>
  </table>

  <h2>Tramos 3 h (próximas 24 h)</h2>
  <table class="data">
    <thead><tr>
      <th>Inicio</th><th>Viento (m/s)</th><th>Ráfaga máx</th><th>Snowfall</th><th>PM2.5</th>
    </tr></thead>
    <tbody>{tramos_body}</tbody>
  </table>

  <h2>Estaciones de área</h2>
  <table class="data">
    <thead><tr>
      <th>Nombre</th><th>Rol</th><th>Lat</th><th>Lon</th><th>Fuente</th>
    </tr></thead>
    <tbody>{est_body}</tbody>
  </table>

  {mvo_html}

  <div class="footer">
  <div class="footer">
    Fuente: Pronóstico costero y portuario integrado (VENTORA - METGO3D SPA).<br/>
    <strong>CONFIDENCIAL.</strong> Este documento es un resumen de la condición de viento, visibilidad y oleaje para decisiones de maniobras STS y de fondeo.
    El cierre y validación final de operación es estricta responsabilidad del operador del terminal y/o la autoridad marítima.
  </div>
</div>
</body>
</html>
"""
