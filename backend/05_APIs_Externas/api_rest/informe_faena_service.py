#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Informe ambiental genérico por faena (M1–M3).

HTML ejecutivo imprimible + PDF (xhtml2pdf). Fallback texto si falta el motor.
"""

from __future__ import annotations

import logging
from datetime import datetime
from io import BytesIO
from typing import Any
from zoneinfo import ZoneInfo

TZ_CHILE = ZoneInfo("America/Santiago")
logger = logging.getLogger(__name__)


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


def _cargar_paquete_y_mvo(faena_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    from api_rest.paquete_ambiental_service import construir_paquete_ambiental

    pkg = construir_paquete_ambiental(faena_id, horas=72)
    if not pkg or pkg.get("error"):
        return None, None
    if not pkg.get("generado_en"):
        pkg = {**pkg, "generado_en": datetime.now(TZ_CHILE).isoformat(timespec="seconds")}
    mvo = None
    try:
        from api_rest.modelo_vs_observado_service import reporte_modelo_vs_observado

        mvo = reporte_modelo_vs_observado(faena_id, dias=14) or None
    except Exception as exc:
        logger.debug("informe mvo omitido: %s", exc)
    return pkg, mvo


def construir_informe_html(faena_id: str) -> str | None:
    """Vista previa HTML ejecutiva (mismo diseño que el PDF)."""
    from api_rest.informe_faena_html import render_informe_ejecutivo_html

    pkg, mvo = _cargar_paquete_y_mvo(faena_id)
    if not pkg:
        return None
    return render_informe_ejecutivo_html(
        pkg,
        resumen=resumen_horizonte(pkg),
        tramos=_tramos_3h(pkg.get("serie_meteo") or [], pkg.get("serie_aire") or []),
        mvo=mvo,
    )


def _html_a_pdf_bytes(html: str) -> bytes | None:
    """HTML → PDF con xhtml2pdf (pip puro; apto Render)."""
    try:
        from xhtml2pdf import pisa
    except ImportError:
        logger.warning("xhtml2pdf no instalado; PDF cae a texto plano")
        return None
    buf = BytesIO()
    try:
        result = pisa.CreatePDF(
            src=html,
            dest=buf,
            encoding="utf-8",
        )
    except Exception as exc:
        logger.warning("xhtml2pdf fallo: %s", exc)
        return None
    if result.err:
        logger.warning("xhtml2pdf err=%s", result.err)
        return None
    raw = buf.getvalue()
    return raw if raw.startswith(b"%PDF") else None


def _pdf_fallback_texto(pkg: dict[str, Any], mvo: dict[str, Any] | None) -> bytes:
    """Fallback mínimo si xhtml2pdf no está disponible."""
    from api_rest.informe_paipote_service import _texto_a_pdf

    a = pkg.get("actual") or {}
    flags = pkg.get("flags") or {}
    lines = [
        "METGO - Informe ambiental de faena (M3)",
        f"{pkg.get('nombre')} ({pkg.get('faena_id')})",
        f"Generado: {pkg.get('generado_en')}",
        f"Nivel global: {flags.get('nivel_global')}",
        f"T: {a.get('temperatura_c')} C  Rafaga: {a.get('rafaga_10m_ms')} m/s",
        "",
        "Instale xhtml2pdf para el informe ejecutivo con diseno.",
    ]
    if mvo:
        lines.append(f"MVO estado: {mvo.get('estado')}")
    return _texto_a_pdf(lines)


def construir_informe_pdf_bytes(faena_id: str) -> bytes | None:
    """PDF ejecutivo A4 (HTML→xhtml2pdf). Fallback texto si falta motor."""
    html = construir_informe_html(faena_id)
    if not html:
        return None
    pdf = _html_a_pdf_bytes(html)
    if pdf:
        return pdf
    pkg, mvo = _cargar_paquete_y_mvo(faena_id)
    if not pkg:
        return None
    return _pdf_fallback_texto(pkg, mvo)


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
