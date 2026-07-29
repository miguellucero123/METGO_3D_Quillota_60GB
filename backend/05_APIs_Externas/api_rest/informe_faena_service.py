#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Informe ambiental genérico por faena (M1–M2). HTML imprimible + PDF texto."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any
from zoneinfo import ZoneInfo

TZ_CHILE = ZoneInfo("America/Santiago")


def _esc(v: Any) -> str:
    if v is None:
        return "—"
    return escape(str(v))


def _nums(serie: list[dict[str, Any]], key: str) -> list[float]:
    out: list[float] = []
    for f in serie:
        v = f.get(key)
        if v is None:
            continue
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            continue
    return out


def _stats(vals: list[float]) -> dict[str, float | None]:
    if not vals:
        return {"min": None, "max": None, "avg": None}
    return {
        "min": round(min(vals), 2),
        "max": round(max(vals), 2),
        "avg": round(sum(vals) / len(vals), 2),
    }


def resumen_horizonte(pkg: dict[str, Any]) -> dict[str, Any]:
    """Agregados 72 h para informe enriquecido (M2)."""
    meteo = pkg.get("serie_meteo") or []
    aire = pkg.get("serie_aire") or []
    v10 = _stats(_nums(meteo, "wind_speed_10m"))
    raf = _stats(_nums(meteo, "wind_gusts_10m"))
    t = _stats(_nums(meteo, "temperature_2m"))
    vis = _stats(_nums(meteo, "visibility"))
    snow = _nums(meteo, "snowfall")
    pm25 = _stats(_nums(aire, "pm2_5"))
    pm10 = _stats(_nums(aire, "pm10"))
    so2 = _stats(_nums(aire, "sulphur_dioxide"))
    no2 = _stats(_nums(aire, "nitrogen_dioxide"))
    return {
        "n_horas_meteo": len(meteo),
        "n_horas_aire": len(aire),
        "temperatura_c": t,
        "viento_10m_ms": v10,
        "rafaga_10m_ms": raf,
        "visibilidad_m": vis,
        "snowfall_mm_suma": round(sum(snow), 2) if snow else 0.0,
        "pm2_5": pm25,
        "pm10": pm10,
        "so2": so2,
        "no2": no2,
    }


def _tramos_3h(meteo: list[dict[str, Any]], aire: list[dict[str, Any]], n: int = 8) -> list[dict[str, Any]]:
    """Primeras n ventanas de 3 h (promedio)."""
    if not meteo:
        return []
    aire_by_ts = {str(r.get("fecha_hora")): r for r in aire}
    out: list[dict[str, Any]] = []
    for i in range(0, min(len(meteo), n * 3), 3):
        chunk = meteo[i : i + 3]
        if not chunk:
            break
        vels = _nums(chunk, "wind_speed_10m")
        rafs = _nums(chunk, "wind_gusts_10m")
        snows = _nums(chunk, "snowfall")
        pm_vals: list[float] = []
        for c in chunk:
            a = aire_by_ts.get(str(c.get("fecha_hora"))) or {}
            if a.get("pm2_5") is not None:
                try:
                    pm_vals.append(float(a["pm2_5"]))
                except (TypeError, ValueError):
                    pass
        out.append(
            {
                "inicio": chunk[0].get("fecha_hora"),
                "fin": chunk[-1].get("fecha_hora"),
                "viento_ms": round(sum(vels) / len(vels), 2) if vels else None,
                "rafaga_max_ms": round(max(rafs), 2) if rafs else None,
                "snowfall_mm": round(sum(snows), 2) if snows else 0.0,
                "pm2_5": round(sum(pm_vals) / len(pm_vals), 1) if pm_vals else None,
            }
        )
    return out


def construir_informe_html(faena_id: str) -> str | None:
    from api_rest.paquete_ambiental_service import construir_paquete_ambiental

    pkg = construir_paquete_ambiental(faena_id, horas=72)
    if not pkg or pkg.get("error"):
        return None
    a = pkg.get("actual") or {}
    nieve = pkg.get("nieve") or {}
    flags = pkg.get("flags") or {}
    ops = pkg.get("operaciones") or {}
    res = resumen_horizonte(pkg)
    tramos = _tramos_3h(pkg.get("serie_meteo") or [], pkg.get("serie_aire") or [])
    gen = pkg.get("generado_en") or datetime.now(TZ_CHILE).isoformat(timespec="seconds")
    caps = ", ".join(pkg.get("capacidades") or []) or "—"

    filas = [
        ("Temperatura", f"{_esc(a.get('temperatura_c'))} °C"),
        ("Humedad relativa", f"{_esc(a.get('humedad_relativa_pct'))} %"),
        ("Precipitación", f"{_esc(a.get('precipitacion_mm'))} mm"),
        ("Nieve (snowfall)", f"{_esc(a.get('snowfall_mm'))} mm"),
        ("Acum. nieve 72 h (proxy)", f"{_esc(nieve.get('acumulacion_proxy_cm'))} cm"),
        ("Acum. nieve 24 h", f"{_esc(nieve.get('acumulacion_24h_cm'))} cm"),
        ("Presión MSL", f"{_esc(a.get('presion_msl_hpa'))} hPa"),
        ("Visibilidad", f"{_esc(a.get('visibilidad_m'))} m"),
        ("Nubosidad", f"{_esc(a.get('nubosidad_pct'))} %"),
        ("Viento 10 m", f"{_esc(a.get('viento_10m_ms'))} m/s · {_esc(a.get('viento_10m_dir_deg'))}°"),
        ("Ráfaga 10 m", f"{_esc(a.get('rafaga_10m_ms'))} m/s"),
        ("Viento 100 m", f"{_esc(a.get('viento_100m_ms'))} m/s · {_esc(a.get('viento_100m_dir_deg'))}°"),
        ("PM2.5", f"{_esc(a.get('pm2_5'))} µg/m³"),
        ("PM10", f"{_esc(a.get('pm10'))} µg/m³"),
        ("SO₂", f"{_esc(a.get('so2'))} µg/m³"),
        ("NO₂ / NOx proxy", f"{_esc(a.get('no2'))} µg/m³"),
        ("O₃", f"{_esc(a.get('o3'))} µg/m³"),
        ("Dust", f"{_esc(a.get('dust'))} µg/m³"),
        ("ICAP", f"{_esc(a.get('icap'))} · {_esc(a.get('nivel_icap'))}"),
    ]
    rows = "".join(f"<tr><th>{escape(k)}</th><td>{v}</td></tr>" for k, v in filas)

    def _rango(st: dict[str, Any], unidad: str) -> str:
        if st.get("max") is None:
            return "—"
        return f"min {_esc(st['min'])} · max {_esc(st['max'])} · media {_esc(st['avg'])} {unidad}"

    resumen_rows = "".join(
        [
            f"<tr><th>Temperatura 72 h</th><td>{_rango(res['temperatura_c'], '°C')}</td></tr>",
            f"<tr><th>Viento 10 m 72 h</th><td>{_rango(res['viento_10m_ms'], 'm/s')}</td></tr>",
            f"<tr><th>Ráfaga 10 m 72 h</th><td>{_rango(res['rafaga_10m_ms'], 'm/s')}</td></tr>",
            f"<tr><th>Visibilidad 72 h</th><td>{_rango(res['visibilidad_m'], 'm')}</td></tr>",
            f"<tr><th>Snowfall suma 72 h</th><td>{_esc(res['snowfall_mm_suma'])} mm</td></tr>",
            f"<tr><th>PM2.5 72 h</th><td>{_rango(res['pm2_5'], 'µg/m³')}</td></tr>",
            f"<tr><th>PM10 72 h</th><td>{_rango(res['pm10'], 'µg/m³')}</td></tr>",
            f"<tr><th>SO₂ 72 h</th><td>{_rango(res['so2'], 'µg/m³')}</td></tr>",
            f"<tr><th>NO₂ 72 h</th><td>{_rango(res['no2'], 'µg/m³')}</td></tr>",
        ]
    )

    tramos_rows = "".join(
        f"<tr><td>{_esc(t.get('inicio'))}</td>"
        f"<td>{_esc(t.get('viento_ms'))}</td>"
        f"<td>{_esc(t.get('rafaga_max_ms'))}</td>"
        f"<td>{_esc(t.get('snowfall_mm'))}</td>"
        f"<td>{_esc(t.get('pm2_5'))}</td></tr>"
        for t in tramos
    ) or "<tr><td colspan='5'>Sin serie horaria</td></tr>"

    estaciones = pkg.get("estaciones_area") or []
    est_rows = "".join(
        f"<tr><td>{_esc(e.get('nombre'))}</td><td>{_esc(e.get('rol'))}</td>"
        f"<td>{_esc(e.get('lat'))}</td><td>{_esc(e.get('lon'))}</td>"
        f"<td>{_esc(e.get('fuente'))}</td></tr>"
        for e in estaciones
    ) or "<tr><td colspan='5'>Sin puntos de área</td></tr>"

    alt = pkg.get("altitud_m")
    alt_txt = f"{_esc(alt)} m s.n.m." if alt is not None else "—"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>Informe ambiental — {_esc(pkg.get('nombre'))}</title>
<style>
  body {{ font-family: Georgia, "Times New Roman", serif; margin: 1.5rem 2rem; color: #1a1a1a;
         background: #f7f4ef; }}
  h1 {{ font-size: 1.55rem; margin: 0 0 0.25rem; }}
  h2 {{ font-size: 1.1rem; margin: 1.4rem 0 0.5rem; border-bottom: 1px solid #ccc; padding-bottom: 0.25rem; }}
  .meta {{ color: #555; margin-bottom: 1rem; font-size: 0.95rem; }}
  table {{ border-collapse: collapse; width: 100%; max-width: 52rem; background: #fff; margin-bottom: 0.5rem; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; font-size: 0.92rem; }}
  th {{ background: #f0ebe3; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; background: #e8e2d6; border-radius: 3px; font-size: 0.85rem; }}
  @media print {{ body {{ background: #fff; margin: 0.8rem; }} h2 {{ page-break-after: avoid; }} }}
</style>
</head>
<body>
  <h1>METGO — Informe ambiental de faena</h1>
  <p class="meta">
    <strong>{_esc(pkg.get('nombre'))}</strong>
    <span class="badge">{_esc(pkg.get('faena_id'))}</span>
    · altitud {alt_txt}
    · lat {_esc(pkg.get('lat'))}, lon {_esc(pkg.get('lon'))}<br/>
    Capacidades: {_esc(caps)} · Generado {escape(str(gen))} · tipo_dato modelo
  </p>

  <h2>1. Condición actual</h2>
  <table>{rows}</table>

  <h2>2. Flags operativos (M3)</h2>
  <p class="meta">Nivel global: <strong>{_esc((flags or {}).get('nivel_global'))}</strong>
     · nieve activa: {_esc((flags or {}).get('flag_nieve_activa'))}
     · izaje restringido: {_esc((flags or {}).get('flag_izaje_restringido'))}
     · caminos: {_esc((flags or {}).get('flag_caminos_restringido'))}
     · botaderos: {_esc((flags or {}).get('flag_botaderos_restringido'))}</p>
  <table>
    <thead><tr><th>Actividad</th><th>Nivel</th><th>Razones</th></tr></thead>
    <tbody>
      {"".join(
          f"<tr><td>{_esc(aid)}</td><td><b>{_esc((av or {}).get('nivel'))}</b></td>"
          f"<td>{_esc(', '.join((av or {}).get('razones') or []) or '—')}</td></tr>"
          for aid, av in ((ops or {}).get('actividades') or {}).items()
      ) or "<tr><td colspan='3'>Sin evaluación</td></tr>"}
    </tbody>
  </table>

  <h2>3. Resumen horizonte 72 h</h2>
  <table>{resumen_rows}</table>

  <h2>4. Tramos 3 h (próximas 24 h)</h2>
  <table>
    <thead><tr><th>Inicio</th><th>Viento medio (m/s)</th><th>Ráfaga máx</th><th>Snowfall (mm)</th><th>PM2.5</th></tr></thead>
    <tbody>{tramos_rows}</tbody>
  </table>

  <h2>5. Estaciones por área (modelo)</h2>
  <table>
    <thead><tr><th>Nombre</th><th>Rol</th><th>Lat</th><th>Lon</th><th>Fuente</th></tr></thead>
    <tbody>{est_rows}</tbody>
  </table>

  <p class="meta">Fuente: Open-Meteo Forecast + CAMS (M3). Imprimir (Ctrl+P) o ?formato=pdf.
     Nieve: proxy SWE→cm; umbrales izaje/caminos/botaderos en paquete.</p>
</body>
</html>
"""


def _fmt_num(v: Any, *, unit: str = "", nd: int | None = None) -> str:
    """Valor legible para PDF (None → —)."""
    if v is None or v == "":
        return "—" if not unit else f"— {unit}".strip()
    try:
        if nd is not None and isinstance(v, (int, float)):
            v = round(float(v), nd)
    except (TypeError, ValueError):
        pass
    return f"{v} {unit}".strip() if unit else str(v)


def _fmt_rango(st: dict[str, Any] | None, unit: str = "") -> str:
    """min / max / media sin volcar el dict Python."""
    st = st or {}
    if st.get("min") is None and st.get("max") is None and st.get("avg") is None:
        return "sin dato"
    u = f" {unit}" if unit else ""
    return (
        f"min {_fmt_num(st.get('min'))} / max {_fmt_num(st.get('max'))} / "
        f"media {_fmt_num(st.get('avg'))}{u}"
    )


def _fmt_bool(v: Any) -> str:
    if v is True:
        return "si"
    if v is False:
        return "no"
    return "—"


def construir_informe_pdf_bytes(faena_id: str) -> bytes | None:
    """PDF texto enriquecido (M2/M3) — legible, sin dicts ni None crudos."""
    from api_rest.informe_paipote_service import _texto_a_pdf
    from api_rest.paquete_ambiental_service import construir_paquete_ambiental

    pkg = construir_paquete_ambiental(faena_id, horas=72)
    if not pkg or pkg.get("error"):
        return None
    a = pkg.get("actual") or {}
    nieve = pkg.get("nieve") or {}
    flags = pkg.get("flags") or {}
    ops = pkg.get("operaciones") or {}
    res = resumen_horizonte(pkg)
    fuente = pkg.get("fuente") or {}
    aviso = pkg.get("aviso")
    lines = [
        "METGO - Informe ambiental de faena (M3)",
        f"{pkg.get('nombre')} ({pkg.get('faena_id')})",
        f"Lat/Lon: {pkg.get('lat')}, {pkg.get('lon')}  alt: {_fmt_num(pkg.get('altitud_m'), unit='m')}",
        f"Generado: {pkg.get('generado_en')}",
    ]
    if aviso:
        lines += ["", f"AVISO: {aviso}"]
    if fuente.get("meteo") == "synthetic_degraded" or pkg.get("degradado"):
        lines.append("Nota: paquete estimado / degradado (Open-Meteo no disponible).")
    lines += [
        "",
        "=== 1. Condicion actual ===",
        f"Temperatura: {_fmt_num(a.get('temperatura_c'), unit='C', nd=1)}",
        f"Humedad relativa: {_fmt_num(a.get('humedad_relativa_pct'), unit='%', nd=1)}",
        f"Precipitacion: {_fmt_num(a.get('precipitacion_mm'), unit='mm', nd=2)}",
        f"Snowfall: {_fmt_num(a.get('snowfall_mm'), unit='mm', nd=2)}",
        f"Visibilidad: {_fmt_num(a.get('visibilidad_m'), unit='m', nd=0)}",
        f"Presion MSL: {_fmt_num(a.get('presion_msl_hpa'), unit='hPa', nd=1)}",
        f"Viento 10 m: {_fmt_num(a.get('viento_10m_ms'), unit='m/s', nd=2)}  "
        f"dir {_fmt_num(a.get('viento_10m_dir_deg'), unit='deg', nd=0)}",
        f"Rafaga 10 m: {_fmt_num(a.get('rafaga_10m_ms'), unit='m/s', nd=2)}",
        f"Viento 100 m: {_fmt_num(a.get('viento_100m_ms'), unit='m/s', nd=2)}  "
        f"dir {_fmt_num(a.get('viento_100m_dir_deg'), unit='deg', nd=0)}",
        f"PM2.5: {_fmt_num(a.get('pm2_5'), unit='ug/m3', nd=1)}  "
        f"PM10: {_fmt_num(a.get('pm10'), unit='ug/m3', nd=1)}",
        f"SO2: {_fmt_num(a.get('so2'), unit='ug/m3', nd=1)}  "
        f"NO2: {_fmt_num(a.get('no2'), unit='ug/m3', nd=1)}",
        f"O3: {_fmt_num(a.get('o3'), unit='ug/m3', nd=1)}  "
        f"Dust: {_fmt_num(a.get('dust'), unit='ug/m3', nd=1)}",
        f"ICAP: {_fmt_num(a.get('icap'))} ({_fmt_num(a.get('nivel_icap'))})",
        f"Acum. nieve 72 h: {_fmt_num(nieve.get('acumulacion_proxy_cm'), unit='cm', nd=1)}  "
        f"24 h: {_fmt_num(nieve.get('acumulacion_24h_cm'), unit='cm', nd=1)}",
        "",
        f"=== 2. Flags operativos M3 (global: {_fmt_num(flags.get('nivel_global'))}) ===",
        f"Nieve activa: {_fmt_bool(flags.get('flag_nieve_activa'))}  "
        f"Acum. relevante: {_fmt_bool(flags.get('flag_acum_relevante'))}",
        f"Izaje restringido: {_fmt_bool(flags.get('flag_izaje_restringido'))}  "
        f"Caminos: {_fmt_bool(flags.get('flag_caminos_restringido'))}  "
        f"Botaderos: {_fmt_bool(flags.get('flag_botaderos_restringido'))}",
    ]
    for aid, av in (ops.get("actividades") or {}).items():
        razones = (av or {}).get("razones") or []
        # flecha Unicode → ASCII en capa PDF
        raz = ", ".join(str(r).replace("→", "->") for r in razones) or "ok"
        lines.append(f"  {aid}: {_fmt_num((av or {}).get('nivel'))} ({raz})")
    lines += [
        "",
        "=== 3. Resumen horizonte 72 h ===",
        f"Temperatura: {_fmt_rango(res['temperatura_c'], 'C')}",
        f"Viento 10 m: {_fmt_rango(res['viento_10m_ms'], 'm/s')}",
        f"Rafaga: {_fmt_rango(res['rafaga_10m_ms'], 'm/s')}",
        f"Visibilidad: {_fmt_rango(res['visibilidad_m'], 'm')}",
        f"Snowfall suma: {_fmt_num(res['snowfall_mm_suma'], unit='mm', nd=2)}",
        f"PM2.5: {_fmt_rango(res['pm2_5'], 'ug/m3')}",
        f"PM10: {_fmt_rango(res['pm10'], 'ug/m3')}",
        f"SO2: {_fmt_rango(res['so2'], 'ug/m3')}",
        f"NO2: {_fmt_rango(res['no2'], 'ug/m3')}",
        "",
        "=== 4. Estaciones de area (modelo) ===",
    ]
    estaciones = pkg.get("estaciones_area") or []
    if not estaciones:
        lines.append("  (sin puntos de area)")
    for e in estaciones:
        lines.append(
            f"  - {e.get('nombre')} ({e.get('rol')}): {e.get('lat')}, {e.get('lon')}"
        )
    lines += ["", "Fuente: Open-Meteo Forecast + CAMS (modelo M3)"]
    try:
        from api_rest.modelo_vs_observado_service import reporte_modelo_vs_observado

        mvo = reporte_modelo_vs_observado(faena_id, dias=14) or {}
        aire = mvo.get("aire") or {}
        meteo = mvo.get("meteo") or {}
        iot = mvo.get("iot") or {}
        lines += [
            "",
            f"=== 5. Modelo vs observado (M5 · estado={_fmt_num(mvo.get('estado'))}) ===",
            f"Estacion: {_fmt_num(mvo.get('estacion_id'))}",
            f"Aire pares: {_fmt_num(aire.get('n_pares'))}  "
            f"PM2.5 sesgo: {_fmt_num((aire.get('pm25') or {}).get('sesgo_medio'), nd=1)}  "
            f"PM10 sesgo: {_fmt_num((aire.get('pm10') or {}).get('sesgo_medio'), nd=1)}",
            f"Meteo pares: {_fmt_num(meteo.get('n_pares'))}  "
            f"T sesgo: {_fmt_num((meteo.get('temperatura') or {}).get('sesgo_medio'), nd=1)}",
            f"IoT lecturas: {_fmt_num(iot.get('n_lecturas'))}",
        ]
    except Exception:
        pass
    lines += [
        "",
        "Documentos: ?formato=pdf | ?formato=csv | HTML (sin query).",
        "Producto METGO proxy operativo. No sustituye dictamen DMC ni modelacion regulatoria.",
    ]
    return _texto_a_pdf(lines)


def _csv_escape(v: Any) -> str:
    if v is None:
        return ""
    s = str(v)
    if any(c in s for c in (",", '"', "\n", "\r")):
        return '"' + s.replace('"', '""') + '"'
    return s


def construir_informe_csv(faena_id: str) -> str | None:
    """Informe tabular UTF-8 (CSV) — documento exportable M6.

    Secciones:
    - meta / actual / flags / operaciones (filas clave,valor)
    - serie_horaria (meteo + nieve + aire alineada)
    - modelo_vs_observado pares (si hay)
    """
    from api_rest.paquete_ambiental_service import construir_paquete_ambiental

    pkg = construir_paquete_ambiental(faena_id, horas=72)
    if not pkg or pkg.get("error"):
        return None

    lines: list[str] = []
    lines.append("seccion,clave,valor")
    meta_pairs = [
        ("meta", "faena_id", pkg.get("faena_id")),
        ("meta", "nombre", pkg.get("nombre")),
        ("meta", "lat", pkg.get("lat")),
        ("meta", "lon", pkg.get("lon")),
        ("meta", "altitud_m", pkg.get("altitud_m")),
        ("meta", "generado_en", pkg.get("generado_en")),
        ("meta", "horizonte_horas", pkg.get("horizonte_horas")),
        ("meta", "tipo_dato", (pkg.get("fuente") or {}).get("tipo_dato") or "modelo"),
        ("meta", "formato", "csv"),
    ]
    a = pkg.get("actual") or {}
    for k, v in a.items():
        meta_pairs.append(("actual", k, v))
    nieve = pkg.get("nieve") or {}
    for k, v in nieve.items():
        if k == "nota":
            continue
        meta_pairs.append(("nieve", k, v))
    flags = pkg.get("flags") or {}
    for k, v in flags.items():
        meta_pairs.append(("flags", k, v))
    for aid, av in ((pkg.get("operaciones") or {}).get("actividades") or {}).items():
        meta_pairs.append(("operaciones", f"{aid}_nivel", (av or {}).get("nivel")))
        meta_pairs.append(
            ("operaciones", f"{aid}_razones", ";".join((av or {}).get("razones") or []))
        )
    for e in pkg.get("estaciones_area") or []:
        meta_pairs.append(
            (
                "estaciones_area",
                e.get("id"),
                f"{e.get('rol')}|{e.get('lat')}|{e.get('lon')}|{e.get('fuente')}",
            )
        )
    for sec, k, v in meta_pairs:
        lines.append(",".join(_csv_escape(x) for x in (sec, k, v)))

    # Serie horaria unificada
    meteo = {str(r.get("fecha_hora")): r for r in (pkg.get("serie_meteo") or [])}
    aire = {str(r.get("fecha_hora")): r for r in (pkg.get("serie_aire") or [])}
    nival = {str(r.get("fecha_hora")): r for r in (pkg.get("serie_nival") or [])}
    tiempos = sorted(set(meteo) | set(aire) | set(nival))
    lines.append("")
    lines.append(
        "fecha_hora,temperature_2m,relative_humidity_2m,precipitation,snowfall_mm,"
        "snowfall_cm,acum_rolling_24h_cm,wind_speed_10m,wind_gusts_10m,wind_direction_10m,"
        "visibility,pm2_5,pm10,sulphur_dioxide,nitrogen_dioxide,tipo_dato"
    )
    for ts in tiempos:
        m = meteo.get(ts) or {}
        air = aire.get(ts) or {}
        nv = nival.get(ts) or {}
        row = [
            ts,
            m.get("temperature_2m"),
            m.get("relative_humidity_2m"),
            m.get("precipitation"),
            nv.get("snowfall_mm", m.get("snowfall")),
            nv.get("snowfall_cm"),
            nv.get("acum_rolling_24h_cm"),
            m.get("wind_speed_10m"),
            m.get("wind_gusts_10m"),
            m.get("wind_direction_10m"),
            m.get("visibility"),
            air.get("pm2_5"),
            air.get("pm10"),
            air.get("sulphur_dioxide"),
            air.get("nitrogen_dioxide"),
            "modelo",
        ]
        lines.append(",".join(_csv_escape(x) for x in row))

    # Modelo vs observado
    try:
        from api_rest.modelo_vs_observado_service import reporte_modelo_vs_observado

        mvo = reporte_modelo_vs_observado(faena_id, dias=14) or {}
        lines.append("")
        lines.append("seccion,clave,valor")
        lines.append(
            ",".join(
                _csv_escape(x)
                for x in ("mvo_meta", "estado", mvo.get("estado"))
            )
        )
        lines.append(
            ",".join(
                _csv_escape(x)
                for x in ("mvo_meta", "estacion_id", mvo.get("estacion_id"))
            )
        )
        pares = (mvo.get("aire") or {}).get("pares") or []
        if pares:
            lines.append("")
            lines.append(
                "fecha,cams_pm25,sinca_pm25,cams_pm10,sinca_pm10,tipo_dato_modelo,tipo_dato_observado"
            )
            for p in pares:
                lines.append(
                    ",".join(
                        _csv_escape(x)
                        for x in (
                            p.get("fecha"),
                            p.get("cams_pm25"),
                            p.get("sinca_pm25"),
                            p.get("cams_pm10"),
                            p.get("sinca_pm10"),
                            "modelo",
                            "observado",
                        )
                    )
                )
    except Exception:
        pass

    # BOM UTF-8 para Excel
    return "\ufeff" + "\n".join(lines) + "\n"


def construir_mvo_csv(faena_id: str, *, dias: int = 14) -> str | None:
    """CSV dedicado modelo vs observado (pares aire + meteo)."""
    from api_rest.modelo_vs_observado_service import reporte_modelo_vs_observado

    mvo = reporte_modelo_vs_observado(faena_id, dias=dias)
    if not mvo:
        return None
    lines = [
        "seccion,clave,valor",
        f"meta,faena_id,{_csv_escape(mvo.get('faena_id'))}",
        f"meta,nombre,{_csv_escape(mvo.get('nombre'))}",
        f"meta,estacion_id,{_csv_escape(mvo.get('estacion_id'))}",
        f"meta,estado,{_csv_escape(mvo.get('estado'))}",
        f"meta,tipo_dato_modelo,modelo",
        f"meta,tipo_dato_observado,observado",
        f"meta,dias,{_csv_escape(mvo.get('dias'))}",
        "",
        "fecha,variable,modelo,observado,sesgo,tipo_dato_modelo,tipo_dato_observado",
    ]
    for p in (mvo.get("aire") or {}).get("pares") or []:
        for var, mk, ok in (
            ("pm25", "cams_pm25", "sinca_pm25"),
            ("pm10", "cams_pm10", "sinca_pm10"),
        ):
            mv, ov = p.get(mk), p.get(ok)
            if mv is None and ov is None:
                continue
            sesgo = ""
            if mv is not None and ov is not None:
                sesgo = round(float(mv) - float(ov), 2)
            lines.append(
                ",".join(
                    _csv_escape(x)
                    for x in (p.get("fecha"), var, mv, ov, sesgo, "modelo", "observado")
                )
            )
    for p in (mvo.get("meteo") or {}).get("pares") or []:
        mv, ov = p.get("modelo_temp"), p.get("obs_temp")
        sesgo = ""
        if mv is not None and ov is not None:
            sesgo = round(float(mv) - float(ov), 2)
        lines.append(
            ",".join(
                _csv_escape(x)
                for x in (p.get("fecha"), "temperatura", mv, ov, sesgo, "pronostico", "observado")
            )
        )
    return "\ufeff" + "\n".join(lines) + "\n"
