#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicios de negocio para la API REST METGO."""

from __future__ import annotations

import io
import contextlib
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any

import pandas as pd

from datos_reales_openmeteo import OpenMeteoData, obtener_datos_meteorologicos_reales

from api_rest.estaciones_catalogo import (
    COORDS,
    ESTACIONES_PRINCIPALES,
    META_EXTRA,
    NOMBRE_A_SLUG,
    SLUG_A_NOMBRE,
    listar_sitios as catalogo_listar_sitios,
    normalizar_sitio,
    slugs_de_sitio,
)

# Caché OpenMeteo (Fase 1.4)
_CACHE_MOD = None
_CACHE_JSON = None
for _p in Path(__file__).resolve().parents:
    _gd = _p / "backend" / "08_Gestion_Datos"
    if (_p / "metgo_paths.py").exists() and _gd.is_dir():
        if str(_gd) not in sys.path:
            sys.path.insert(0, str(_gd))
        try:
            from cache_openmeteo import get_meteo_cached as _get_meteo_cached

            _CACHE_MOD = _get_meteo_cached
        except ImportError:
            pass
        try:
            from cache_openmeteo import get_json_cached as _get_json_cached

            _CACHE_JSON = _get_json_cached
        except ImportError:
            pass
        break

# Slug / catálogo: ver api_rest.estaciones_catalogo (multi-sitio)


def slug_a_nombre(estacion_id: str) -> str:
    key = estacion_id.lower().replace("-", "_")
    if key in SLUG_A_NOMBRE:
        return SLUG_A_NOMBRE[key]
    return estacion_id.replace("_", " ").title()


def nombre_a_slug(nombre: str) -> str:
    return NOMBRE_A_SLUG.get(nombre, nombre.lower().replace(" ", "_"))


def listar_sitios(incluir_plantilla: bool = True) -> list[dict[str, Any]]:
    """Lista sitios METGO (quillota, paine, demo, …)."""
    return catalogo_listar_sitios(incluir_plantilla=incluir_plantilla)


def listar_estaciones(
    tenant_id: str | None = None,
    sitio: str | None = None,
) -> list[dict[str, Any]]:
    """Lista estaciones. ``sitio`` default ``quillota`` (cero impacto SPA actual)."""
    om = OpenMeteoData()
    sitio_n = normalizar_sitio(sitio)
    slugs = slugs_de_sitio(sitio_n)
    if tenant_id and sitio_n == "quillota":
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = [s for s in estaciones_de_tenant(tenant_id) if s in SLUG_A_NOMBRE]
        except ImportError:
            pass
    resultado = []
    for slug in slugs:
        nombre = SLUG_A_NOMBRE.get(slug)
        if not nombre:
            continue
        coords = om.estaciones.get(nombre) or COORDS.get(slug)
        if not coords:
            continue
        item: dict[str, Any] = {
            "id": slug,
            "nombre": nombre,
            "activa": True,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "sitio": sitio_n,
        }
        extra = META_EXTRA.get(slug)
        if extra:
            item.update(extra)
        resultado.append(item)
    return resultado


def _fetch_meteo_raw(estacion: str, tipo: str, dias: int) -> pd.DataFrame | None:
    try:
        return obtener_datos_meteorologicos_reales(
            estacion=estacion, tipo=tipo, dias=dias
        )
    except Exception as e:
        with open("openmeteo_error.log", "a") as f:
            f.write(f"ERROR OpenMeteo {estacion} {tipo}: {e}\n")
        return None


def _df_sin_prints(estacion: str, tipo: str, dias: int) -> pd.DataFrame | None:
    """Obtiene DataFrame suprimiendo prints; usa caché si está disponible."""
    if _CACHE_MOD:
        return _CACHE_MOD(estacion, tipo, dias, _fetch_meteo_raw)
    return _fetch_meteo_raw(estacion, tipo, dias)


def _fila_hoy(df: pd.DataFrame | None) -> pd.Series | None:
    """Fila del día actual en Chile (o la observación más reciente ≤ hoy)."""
    if df is None or df.empty:
        return None
    work = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work["fecha"]):
        work["fecha"] = pd.to_datetime(work["fecha"])
    hoy = _hoy_chile()
    work["_dia"] = work["fecha"].apply(_fecha_dia)
    mask_hoy = work["_dia"] == hoy
    if mask_hoy.any():
        return work.loc[mask_hoy].sort_values("fecha").iloc[0]
    pasados = work[work["_dia"] <= hoy]
    if not pasados.empty:
        return pasados.sort_values("fecha", ascending=False).iloc[0]
    return work.sort_values("fecha", ascending=True).iloc[0]


def _ultima_fila(df: pd.DataFrame | None) -> pd.Series | None:
    """Última fila cronológica (histórico). Para resumen del día use _fila_hoy."""
    if df is None or df.empty:
        return None
    return df.sort_values("fecha", ascending=False).iloc[0]


def _fecha_dia(val: Any) -> str:
    """Normaliza cualquier fecha a YYYY-MM-DD (evita duplicados local vs OpenMeteo)."""
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


def _hoy_chile() -> str:
    return datetime.now(ZoneInfo("America/Santiago")).date().isoformat()


def _dedupe_historico_por_dia(filas: list[dict[str, Any]], dias: int) -> list[dict[str, Any]]:
    """Una fila por día (solo fechas <= hoy Chile); prefiere datos reales sobre sintéticos."""
    hoy = _hoy_chile()
    por_dia: dict[str, dict[str, Any]] = {}
    for r in filas:
        dia = _fecha_dia(r.get("fecha"))
        if dia and dia <= hoy:
            es_sintetico = "sintetico" in str(r.get("fuente", "")).lower()
            if dia in por_dia:
                ya_es_sintetico = "sintetico" in str(por_dia[dia].get("fuente", "")).lower()
                # Si el nuevo es sintético y el existente es real, no sobreescribir
                if es_sintetico and not ya_es_sintetico:
                    continue
            por_dia[dia] = {**r, "fecha": dia}
    return sorted(por_dia.values(), key=lambda x: x["fecha"])[-dias:]


def _dedupe_pronostico_por_dia(filas: list[dict[str, Any]], dias: int) -> list[dict[str, Any]]:
    """Pronóstico: hoy y días siguientes; prefiere datos reales sobre sintéticos."""
    hoy = _hoy_chile()
    por_dia: dict[str, dict[str, Any]] = {}
    for r in filas:
        dia = _fecha_dia(r.get("fecha"))
        if dia and dia >= hoy:
            es_sintetico = "sintetico" in str(r.get("fuente", "")).lower()
            if dia in por_dia:
                ya_es_sintetico = "sintetico" in str(por_dia[dia].get("fuente", "")).lower()
                if es_sintetico and not ya_es_sintetico:
                    continue
            por_dia[dia] = {**r, "fecha": dia}
    if not por_dia and filas:
        # Respaldo: caché/sintético antiguo con fechas pasadas — usar últimos N días disponibles
        for r in sorted(filas, key=lambda x: _fecha_dia(x.get("fecha"))):
            dia = _fecha_dia(r.get("fecha"))
            if dia:
                por_dia[dia] = {**r, "fecha": dia}
    return sorted(por_dia.values(), key=lambda x: x["fecha"])[:dias]


def _fila_a_resumen(row: pd.Series, estacion_id: str) -> dict[str, Any]:
    nombre = row.get("estacion", slug_a_nombre(estacion_id))
    pop = row.get("probabilidad_lluvia")
    if pop is not None and not (isinstance(pop, float) and pd.isna(pop)):
        pop_val = round(float(pop), 0)
    else:
        pop_val = None
    out = {
        "estacion_id": estacion_id,
        "estacion": str(nombre),
        "fecha": _fecha_dia(row["fecha"]),
        "temperatura": round(float(row.get("temperatura_promedio") or 0), 1),
        "temperatura_max": round(float(row.get("temperatura_max") or 0), 1),
        "temperatura_min": round(float(row.get("temperatura_min") or 0), 1),
        "humedad": round(float(row.get("humedad_relativa") or 0), 1),
        "viento": round(float(row.get("velocidad_viento") or 0), 1),
        "precipitacion": round(float(row.get("precipitacion") or 0), 1),
        "presion": round(float(row.get("presion_atmosferica") or 0), 1),
        "fuente": str(row.get("fuente_datos", "desconocida")),
        "actualizado": datetime.now().isoformat(),
    }
    if pop_val is not None:
        out["probabilidad_lluvia"] = pop_val
        out["pop"] = pop_val
    for src, dst in (
        ("cobertura_nubosa", "cobertura_nubosa"),
        ("radiacion_solar_sum", "radiacion_solar_sum"),
        ("direccion_viento", "direccion_viento"),
        ("visibilidad", "visibilidad"),
        ("visibilidad_madrugada", "visibilidad_madrugada"),
    ):
        raw = row.get(src)
        if raw is not None and not (isinstance(raw, float) and pd.isna(raw)):
            out[dst] = round(float(raw), 1)
    if out.get("radiacion_solar_sum") is not None:
        mj = float(out["radiacion_solar_sum"])
        out["radiacion_solar"] = round((mj * 1e6) / (12 * 3600), 0)
    # Identificación observada de helada / niebla (insumo store + UI)
    helada_raw = row.get("helada")
    if helada_raw is not None and not (isinstance(helada_raw, float) and pd.isna(helada_raw)):
        out["helada"] = bool(helada_raw)
    else:
        out["helada"] = out["temperatura_min"] <= 0.0
    niebla_raw = row.get("niebla")
    if niebla_raw is not None and not (isinstance(niebla_raw, float) and pd.isna(niebla_raw)):
        out["niebla"] = bool(niebla_raw)
    else:
        vis_m = out.get("visibilidad_madrugada")
        vis = out.get("visibilidad")
        if vis_m is not None:
            out["niebla"] = float(vis_m) < 1.0
        elif vis is not None:
            out["niebla"] = float(vis) < 1.0
    # Propaga la marca de caché (dato real, servido desde caché por fallo de OpenMeteo).
    dc = row.get("desde_cache")
    if dc is not None and not (isinstance(dc, float) and pd.isna(dc)) and bool(dc):
        out["desde_cache"] = True
        edad = row.get("cache_edad_horas")
        if edad is not None and not (isinstance(edad, float) and pd.isna(edad)):
            out["cache_edad_horas"] = round(float(edad), 1)
    return out


def _num(val: Any) -> float:
    try:
        if val is None:
            return 0.0
        return round(float(val), 1)
    except (TypeError, ValueError):
        return 0.0


def _resumen_desde_store(estacion_id: str) -> dict[str, Any] | None:
    """Fallback: último registro REAL persistido en meteo_store (Supabase).

    Se usa solo cuando OpenMeteo (en vivo) y la caché local no devuelven datos.
    No inventa datos: si no hay registros almacenados, devuelve None.
    """
    try:
        from api_rest.integracion.meteo_store import leer_registros, leer_pronostico
    except ImportError:
        return None
    try:
        registros = leer_registros(estacion_id, 14)
    except Exception:
        registros = []
    if not registros:
        try:
            registros = leer_pronostico(estacion_id, 2)
        except Exception:
            registros = []
    if not registros:
        return None
    reciente = sorted(registros, key=lambda r: str(r.get("fecha") or ""))[-1]
    return {
        "estacion_id": estacion_id,
        "estacion": slug_a_nombre(estacion_id),
        "fecha": str(reciente.get("fecha") or "")[:10],
        "temperatura": _num(reciente.get("temperatura_promedio") or reciente.get("temperatura")),
        "temperatura_max": _num(reciente.get("temperatura_max")),
        "temperatura_min": _num(reciente.get("temperatura_min")),
        "humedad": _num(reciente.get("humedad")),
        "viento": _num(reciente.get("viento")),
        "precipitacion": _num(reciente.get("precipitacion")),
        "presion": _num(reciente.get("presion")),
        "fuente": str(reciente.get("fuente") or "supabase_db"),
        "actualizado": datetime.now().isoformat(),
        "tipo_dato": "observado",
        "desde_cache": True,
        "origen_fallback": "meteo_store",
    }


def resumen_meteo(estacion_id: str) -> dict[str, Any] | None:
    """Resumen del día: prioriza histórico observado OpenMeteo; si no hay, pronóstico;
    y si OpenMeteo/caché fallan, el último dato REAL persistido en Supabase."""
    nombre = slug_a_nombre(estacion_id)
    df_hist = _df_sin_prints(nombre, "historicos", 14)
    row = _fila_hoy(df_hist)
    tipo_dato = "observado"
    if row is None:
        df = _df_sin_prints(nombre, "pronostico", 7)
        row = _fila_hoy(df)
        tipo_dato = "pronostico"
    if row is None:
        # Último recurso: base de datos persistida (datos reales, sin inventar).
        return _resumen_desde_store(estacion_id)
    out = _fila_a_resumen(row, estacion_id)
    out["tipo_dato"] = tipo_dato
    return out


def _registros_desde_df(df: pd.DataFrame, estacion_id: str) -> list[dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    for _, row in df.sort_values("fecha").iterrows():
        registros.append(_fila_a_resumen(row, estacion_id))
    return registros


def _persistir_pronostico(estacion_id: str, registros: list[dict[str, Any]]) -> None:
    """Guarda en Supabase solo filas con datos reales de OpenMeteo (nunca sintéticos)."""
    reales = [
        r for r in registros
        if "sintetico" not in str(r.get("fuente", "")).lower()
    ]
    if not reales:
        return
    try:
        from api_rest.integracion.meteo_store import guardar_pronostico

        guardar_pronostico(estacion_id, reales)
    except ImportError:
        pass
    except Exception:
        pass


def _pronostico_desde_store(estacion_id: str, dias: int) -> list[dict[str, Any]] | None:
    """Fallback: pronóstico REAL persistido en Supabase (última sincronización)."""
    try:
        from api_rest.integracion.meteo_store import leer_pronostico
    except ImportError:
        return None
    try:
        filas = leer_pronostico(estacion_id, dias)
    except Exception:
        return None
    if not filas:
        return None
    out = []
    for r in filas:
        out.append({
            **r,
            "estacion": slug_a_nombre(estacion_id),
            "desde_cache": True,
            "origen_fallback": "meteo_store",
        })
    return out


def pronostico_meteo(estacion_id: str, dias: int = 7) -> list[dict[str, Any]] | None:
    """Pronóstico diario: OpenMeteo (validado) → persiste en Supabase → sirve.

    Si OpenMeteo/caché fallan, sirve el último pronóstico REAL guardado en Supabase.
    """
    nombre = slug_a_nombre(estacion_id)
    ventana = min(dias, 16)
    df = _df_sin_prints(nombre, "pronostico", ventana)
    registros: list[dict[str, Any]] = []
    if df is not None and not df.empty:
        registros = _registros_desde_df(df, estacion_id)
    out = _dedupe_pronostico_por_dia(registros, dias)
    if out:
        # Dato fresco de OpenMeteo: persistir en Supabase para servir desde BD.
        if not any(r.get("desde_cache") for r in out):
            _persistir_pronostico(estacion_id, out)
        return out
    return _pronostico_desde_store(estacion_id, dias)


def _guardar_serie_supabase(estacion_id: str, tipo: str, payload: dict[str, Any]) -> None:
    try:
        from api_rest.integracion.meteo_store import guardar_serie

        guardar_serie(estacion_id, tipo, payload)
    except ImportError:
        pass
    except Exception:
        pass


def _leer_serie_supabase(estacion_id: str, tipo: str) -> dict[str, Any] | None:
    try:
        from api_rest.integracion.meteo_store import leer_serie

        return leer_serie(estacion_id, tipo)
    except ImportError:
        return None
    except Exception:
        return None


def viento_horario_meteo(estacion_id: str, dias: int = 7) -> dict[str, Any] | None:
    """Rosa de vientos: serie horaria (dirección+velocidad) desde OpenMeteo forecast."""
    try:
        nombre = slug_a_nombre(estacion_id)
        om = OpenMeteoData()

        def _fetch_viento():
            return om.obtener_viento_horario_pronostico(nombre, dias)

        if _CACHE_JSON:
            data = _CACHE_JSON(
                f"viento_horario|{nombre}|{dias}",
                _fetch_viento,
                es_valido=lambda d: bool(d and d.get("direcciones")),
            )
        else:
            data = _fetch_viento()
        # Persistir dato fresco en Supabase; si no hubo dato, intentar desde Supabase.
        if data and data.get("direcciones") and not data.get("desde_cache"):
            _guardar_serie_supabase(estacion_id, f"viento_horario_{dias}", data)
        if not data or not data.get("direcciones"):
            desde_db = _leer_serie_supabase(estacion_id, f"viento_horario_{dias}")
            if desde_db and desde_db.get("direcciones"):
                data = desde_db
        if not data:
            return {"direcciones": [], "velocidades": [], "unidad": "m/s", "fuente": "openmeteo_hourly"}
        # Normaliza claves al formato esperado por el frontend.
        out = {
            "direcciones": data.get("direcciones") or [],
            "velocidades": data.get("velocidades") or [],
            "unidad": data.get("unidad") or "m/s",
            "fuente": data.get("fuente_datos") or "openmeteo_hourly",
        }
        if data.get("desde_cache"):
            out["desde_cache"] = True
            if data.get("cache_edad_horas") is not None:
                out["cache_edad_horas"] = data["cache_edad_horas"]
        return out
    except Exception:
        return {"direcciones": [], "velocidades": [], "unidad": "m/s", "fuente": "openmeteo_hourly_error"}


def serie_helada_madrugada_meteo(estacion_id: str, dias: int = 7) -> dict[str, Any] | None:
    """Serie horaria de madrugada (T°, HR, viento, nubosidad, Td) para identificación de helada."""
    tipo = f"helada_madrugada_{dias}"
    try:
        nombre = slug_a_nombre(estacion_id)
        om = OpenMeteoData()

        def _fetch():
            return om.obtener_serie_helada_madrugada(nombre, dias)

        if _CACHE_JSON:
            data = _CACHE_JSON(
                f"helada_madrugada|{nombre}|{dias}",
                _fetch,
                es_valido=lambda d: bool(d and (d.get("puntos") or d.get("madrugada"))),
            )
        else:
            data = _fetch()
        if data and (data.get("puntos") or data.get("madrugada")) and not data.get("desde_cache"):
            _guardar_serie_supabase(estacion_id, tipo, data)
        if not data or not (data.get("puntos") or data.get("madrugada")):
            desde_db = _leer_serie_supabase(estacion_id, tipo)
            if desde_db:
                data = desde_db
        if not data:
            return {
                "estacion_id": estacion_id,
                "horas": [],
                "puntos": [],
                "madrugada": [],
                "fuente": "openmeteo_helada_hourly",
            }
        out = dict(data)
        out["estacion_id"] = estacion_id
        out["fuente"] = data.get("fuente_datos") or data.get("fuente") or "openmeteo_helada_hourly"
        return out
    except Exception:
        return {
            "estacion_id": estacion_id,
            "horas": [],
            "puntos": [],
            "madrugada": [],
            "fuente": "openmeteo_helada_hourly_error",
        }


def historico_meteo(estacion_id: str, dias: int = 30) -> list[dict[str, Any]] | None:
    """Histórico diario real.

    - dias <= 92: OpenMeteo forecast/past_days + merge con store.
    - dias > 92: solo lectura del store (ETL Archive / CSV); no llama OpenMeteo
      en caliente para evitar timeouts en Render free.
    """
    dias = max(1, int(dias))
    nombre = slug_a_nombre(estacion_id)
    registros: list[dict[str, Any]] = []

    if dias <= 92:
        df = _df_sin_prints(nombre, "historicos", dias)
        if df is not None and not df.empty:
            df = df.sort_values("fecha")
            registros = [_fila_a_resumen(row, estacion_id) for _, row in df.iterrows()]

    try:
        from api_rest.integracion.meteo_store import guardar_registros, leer_registros

        if registros:
            guardar_registros(estacion_id, registros)
        local = leer_registros(estacion_id, dias)
        merged: list[dict[str, Any]] = []
        if local:
            merged.extend(local)
        if registros:
            merged.extend(registros)
        if merged:
            return _dedupe_historico_por_dia(merged, dias)
        if dias > 92:
            # Sin store poblado: no inventar; el cliente debe disparar ETL Archive
            return []
    except ImportError:
        if dias > 92:
            return []
    return _dedupe_historico_por_dia(registros, dias) if registros else None


def generar_alertas(estacion_id: str | None = None) -> list[dict[str, Any]]:
    """Alertas derivadas de umbrales sobre el pronóstico actual."""
    alertas: list[dict[str, Any]] = []
    estaciones = [estacion_id] if estacion_id else ESTACIONES_PRINCIPALES
    aid = 1

    for eid in estaciones:
        resumen = resumen_meteo(eid)
        if not resumen:
            continue
        nombre = resumen["estacion"]

        if resumen["temperatura_max"] >= 32:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: temperatura máxima alta ({resumen['temperatura_max']}°C)",
                }
            )
            aid += 1
        if resumen["temperatura_min"] <= 4:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: riesgo de heladas (mín {resumen['temperatura_min']}°C)",
                }
            )
            aid += 1
        if resumen["precipitacion"] >= 10:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "info",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: precipitación significativa ({resumen['precipitacion']} mm)",
                }
            )
            aid += 1
        if resumen["viento"] >= 40:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: viento fuerte ({resumen['viento']} km/h)",
                }
            )
            aid += 1
        if resumen["humedad"] >= 90:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "info",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: humedad muy alta ({resumen['humedad']}%)",
                }
            )
            aid += 1

    if not alertas:
        alertas.append(
            {
                "id": 1,
                "nivel": "info",
                "estacion_id": estacion_id or "quillota",
                "mensaje": "Condiciones dentro de rangos normales",
            }
        )

    try:
        from api_rest.integracion.alertas_store import evaluar_umbrales_01, registrar_alertas

        for eid in estaciones:
            res = resumen_meteo(eid)
            if res:
                extra = evaluar_umbrales_01(res, eid)
                seen = {a["mensaje"] for a in alertas}
                for ex in extra:
                    if ex["mensaje"] not in seen:
                        ex["id"] = aid
                        aid += 1
                        alertas.append(ex)
        registrar_alertas(alertas)
    except ImportError:
        pass

    return alertas


def recomendaciones_agricolas(estacion_id: str, *, avanzado: bool = True) -> list[dict[str, Any]]:
    """Recomendaciones módulo 02 (avanzado si está disponible)."""
    pron = pronostico_meteo(estacion_id, 14) or []
    hist = historico_meteo(estacion_id, 14) or []
    filas = (hist or []) + (pron or [])

    if avanzado and filas:
        try:
            from api_rest.integracion.agricola_avanzado import recomendaciones_lista

            return recomendaciones_lista(filas, estacion_id)
        except Exception:
            pass

    resumen = resumen_meteo(estacion_id)
    if not resumen:
        return [
            {
                "cultivo": "General",
                "accion": "Sin datos",
                "motivo": "No se pudo obtener pronóstico",
            }
        ]

    recs = []
    t_min = resumen["temperatura_min"]
    precip = resumen["precipitacion"]
    humedad = resumen["humedad"]

    if t_min <= 5:
        recs.append(
            {
                "cultivo": "Cítricos / Vid",
                "accion": "Activar protección antihielo",
                "motivo": f"Temperatura mínima prevista {t_min}°C",
            }
        )
    if precip >= 5:
        recs.append(
            {
                "cultivo": "General",
                "accion": "Suspender riego",
                "motivo": f"Precipitación esperada {precip} mm",
            }
        )
    elif precip < 1 and humedad < 50:
        recs.append(
            {
                "cultivo": "Palta / Hortalizas",
                "accion": "Programar riego moderado",
                "motivo": f"Baja humedad ({humedad}%) y sin lluvia",
            }
        )
    else:
        recs.append(
            {
                "cultivo": "General",
                "accion": "Monitoreo rutinario",
                "motivo": "Condiciones estables según pronóstico",
            }
        )

    return recs


def reporte_agricola_avanzado(estacion_id: str) -> dict[str, Any]:
    pron = pronostico_meteo(estacion_id, 14) or []
    hist = historico_meteo(estacion_id, 14) or []
    filas = (hist or []) + (pron or [])
    try:
        from api_rest.integracion.agricola_avanzado import reporte_integral

        return reporte_integral(filas)
    except ImportError as e:
        return {"error": str(e)}


def comparativo_estaciones(tenant_id: str | None = None) -> list[dict[str, Any]]:
    """Resumen actual de todas las estaciones principales (Fase 2.1)."""
    filas = []
    slugs = ESTACIONES_PRINCIPALES
    if tenant_id:
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = estaciones_de_tenant(tenant_id)
        except ImportError:
            pass
    for slug in slugs:
        res = resumen_meteo(slug)
        if res:
            filas.append(res)
    return filas


def comparativo_historico(dias: int = 14, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """Histórico reciente de todas las estaciones principales (visualizaciones / comparativo)."""
    slugs = list(ESTACIONES_PRINCIPALES)
    if tenant_id:
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = [s for s in estaciones_de_tenant(tenant_id) if s in SLUG_A_NOMBRE]
        except ImportError:
            pass
    filas: list[dict[str, Any]] = []
    limite = min(max(dias, 1), 92)
    for slug in slugs:
        hist = historico_meteo(slug, limite) or []
        nombre = slug_a_nombre(slug)
        hoy = _hoy_chile()
        for row in hist[-limite:]:
            dia = _fecha_dia(row.get("fecha"))
            if dia and dia > hoy:
                continue
            filas.append(
                {
                    **row,
                    "estacion_id": slug,
                    "estacion": nombre,
                    "fecha": dia,
                }
            )
    return filas


def metricas_globales(tenant_id: str | None = None) -> dict[str, Any]:
    """KPIs consolidados del valle (Fase 2.1)."""
    filas = comparativo_estaciones(tenant_id)
    ref = _hoy_chile()
    if not filas:
        return {
            "estaciones_activas": 0,
            "temperatura_media_max": None,
            "temperatura_media_min": None,
            "precipitacion_total": 0,
            "alertas_activas": 0,
            "referencia_fecha": ref,
            "detalle_estaciones": [],
            "actualizado": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        }
    alertas = generar_alertas()
    alertas_warn = sum(1 for a in alertas if a.get("nivel") == "warning")
    return {
        "estaciones_activas": len(filas),
        "temperatura_media_max": round(
            sum(f["temperatura_max"] for f in filas) / len(filas), 1
        ),
        "temperatura_media_min": round(
            sum(f["temperatura_min"] for f in filas) / len(filas), 1
        ),
        "precipitacion_total": round(sum(f["precipitacion"] for f in filas), 1),
        "viento_max": max(f["viento"] for f in filas),
        "humedad_media": round(sum(f["humedad"] for f in filas) / len(filas), 1),
        "alertas_activas": len(alertas),
        "alertas_warning": alertas_warn,
        "estaciones": [f["estacion_id"] for f in filas],
        "referencia_fecha": ref,
        "detalle_estaciones": filas,
        "actualizado": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
    }


def pronostico_precipitacion_calibrado(estacion_id: str, dias: int = 7) -> dict[str, Any] | None:
    from api_rest.precipitacion_core import pronostico_precipitacion_calibrado as _cal

    return _cal(
        estacion_id,
        min(dias, 10),
        pronostico_meteo,
        historico_meteo,
        slug_a_nombre,
    )


def precipitacion_horaria_3h_meteo(estacion_id: str, dias: int = 7) -> dict[str, Any]:
    nombre = slug_a_nombre(estacion_id)
    om = OpenMeteoData()
    ventana = min(dias, 16)

    def _fetch_3h():
        return om.obtener_precipitacion_horaria_3h(nombre, ventana)

    if _CACHE_JSON:
        data = _CACHE_JSON(
            f"precip_3h|{nombre}|{ventana}",
            _fetch_3h,
            es_valido=lambda d: bool(d and d.get("fechas")),
        )
    else:
        data = _fetch_3h()
    # Persistir dato fresco en Supabase; si no hubo dato, intentar desde Supabase.
    if data and data.get("fechas") and not data.get("desde_cache"):
        _guardar_serie_supabase(estacion_id, f"precip_3h_{ventana}", data)
    if not data or not data.get("fechas"):
        desde_db = _leer_serie_supabase(estacion_id, f"precip_3h_{ventana}")
        if desde_db and desde_db.get("fechas"):
            return desde_db
    return data


def pronostico_precipitacion_3h_calibrado(
    estacion_id: str, dias: int = 7
) -> dict[str, Any] | None:
    from api_rest.precipitacion_core import pronostico_precipitacion_3h_calibrado as _cal3

    def _fetch(eid: str, d: int) -> dict[str, Any]:
        return precipitacion_horaria_3h_meteo(eid, d)

    return _cal3(
        estacion_id,
        min(dias, 10),
        _fetch,
        pronostico_meteo,
        historico_meteo,
        slug_a_nombre,
    )


def pronostico_precipitacion_bruto(estacion_id: str, dias: int = 7) -> dict[str, Any] | None:
    from api_rest.precipitacion_core import pronostico_precipitacion_bruto as _bruto

    return _bruto(estacion_id, min(dias, 10), pronostico_meteo, slug_a_nombre)


def generar_alertas_precipitacion(
    estacion_id: str, cultivo: str | None = None
) -> list[dict[str, Any]]:
    from api_rest.precipitacion_core import generar_alertas_precipitacion as _gen

    return _gen(
        estacion_id,
        lambda eid, d=7: pronostico_precipitacion_calibrado(eid, d),
        cultivo,
    )


def pronostico_heladas(estacion_id: str, dias: int = 7) -> dict[str, Any]:
    from api_rest.precipitacion_core import pronostico_heladas as _hel

    return _hel(estacion_id, min(dias, 14), pronostico_meteo, slug_a_nombre)


def generar_alertas_helada(estacion_id: str) -> list[dict[str, Any]]:
    from api_rest.precipitacion_core import generar_alertas_helada as _gen

    return _gen(estacion_id, pronostico_heladas)


def obtener_acumulado_precipitacion(
    estacion_id: str, dias_rango: int = 7
) -> dict[str, Any]:
    from api_rest.precipitacion_core import obtener_acumulado_precipitacion as _ac

    return _ac(
        estacion_id,
        dias_rango,
        pronostico_precipitacion_calibrado,
        historico_meteo,
        _hoy_chile,
    )


def obtener_historico_precipitacion(
    estacion_id: str, desde: str, hasta: str
) -> dict[str, Any]:
    from api_rest.precipitacion_core import obtener_historico_precipitacion as _hist

    return _hist(estacion_id, desde, hasta, historico_meteo, _hoy_chile)


def cronograma_riego_inteligente(
    estacion_id: str, cultivo_id: str = "palto"
) -> dict[str, Any]:
    from api_rest.precipitacion_core import cronograma_riego_inteligente as _cron

    return _cron(
        estacion_id,
        cultivo_id,
        pronostico_precipitacion_calibrado,
        resumen_meteo,
    )


CULTIVOS_CRONOGRAMA = frozenset(
    {"palto", "citricos", "vid", "tomate", "lechuga", "hortalizas", "cereales"}
)

MM_RIEGO_REF: dict[str, int] = {
    "palto": 8,
    "citricos": 7,
    "vid": 5,
    "tomate": 10,
    "lechuga": 6,
    "hortalizas": 6,
    "cereales": 4,
}


def cronograma_riego(estacion_id: str, cultivo_slug: str) -> dict[str, Any]:
    """Cronograma de riego dinámico 7 días desde pronóstico OpenMeteo."""
    cultivo_slug = cultivo_slug.lower().replace("-", "_")
    if cultivo_slug not in CULTIVOS_CRONOGRAMA:
        raise ValueError(f"Cultivo no válido: {cultivo_slug}")
    mm_base = MM_RIEGO_REF.get(cultivo_slug, 6)
    dias_pronostico = pronostico_meteo(estacion_id, 7) or []
    hoy = datetime.now(ZoneInfo("America/Santiago")).date()
    cronograma: list[dict[str, Any]] = []
    for dia in dias_pronostico:
        fecha_str = str(dia.get("fecha", ""))[:10]
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        t_min = float(dia.get("temperatura_min") or 20)
        lluvia = float(dia.get("precipitacion") or 0)
        if t_min <= 3:
            regar = False
            mm = 0
            razon = f"Riesgo helada (mín {t_min:.1f}°C) — evitar riego por aspersión"
            categoria = "suspender_riego_helada"
        elif lluvia >= 5:
            regar = False
            mm = 0
            razon = f"Lluvia suficiente ({lluvia:.1f} mm) — suspender riego"
            categoria = "lluvia_cubre"
        elif lluvia > 0:
            mm_reducido = max(0, round(mm_base - lluvia))
            regar = mm_reducido > 0
            mm = mm_reducido
            razon = f"Lluvia parcial ({lluvia:.1f} mm) — riego reducido"
            categoria = "riego_reducido"
        else:
            regar = True
            mm = mm_base
            razon = "Sin lluvia prevista — riego normal"
            categoria = "riego_normal"
        cronograma.append(
            {
                "fecha": fecha_str,
                "es_hoy": fecha == hoy,
                "regar": regar,
                "mm_sugeridos": mm,
                "t_min": round(t_min, 1),
                "lluvia": round(lluvia, 1),
                "razon": razon,
                "categoria": categoria,
            }
        )
    return {
        "estacion": estacion_id,
        "cultivo": cultivo_slug,
        "mm_base": mm_base,
        "generado": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "cronograma": cronograma,
    }


_ULTIMA_VERIFICACION = 0.0
_ULTIMO_ESTADO_OM = True
_ULTIMA_LATENCIA = 0

def health_check() -> dict[str, Any]:
    global _ULTIMA_VERIFICACION, _ULTIMO_ESTADO_OM, _ULTIMA_LATENCIA
    t0 = time.perf_counter()
    ahora = time.time()
    
    if ahora - _ULTIMA_VERIFICACION > 60:
        om = OpenMeteoData()
        with contextlib.redirect_stdout(io.StringIO()):
            _ULTIMO_ESTADO_OM = om.verificar_conexion(timeout_sec=5)
        _ULTIMA_LATENCIA = int((time.perf_counter() - t0) * 1000)
        _ULTIMA_VERIFICACION = ahora

    stats = {"cache_hits": 0, "cache_misses": 0}
    try:
        from cache_openmeteo import cache_stats
        stats = cache_stats()
    except ImportError:
        pass
    return {
        "status": "ok" if _ULTIMO_ESTADO_OM else "degraded",
        "openmeteo": _ULTIMO_ESTADO_OM,
        "latencia_openmeteo_ms": _ULTIMA_LATENCIA,
        "timestamp": datetime.now().isoformat(),
        **stats,
    }
