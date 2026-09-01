#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SINCA (MMA Chile) — E12: catálogo, CSV opcional, sesgo vs CAMS.

SINCA no publica API REST estable. Integración prevista:

1. Completar `sinca_id` (env `METGO_SINCA_IDS` JSON o catálogo).
2. Colocar CSV diarios en `METGO_SINCA_CSV_DIR/{slug}.csv`
   (columnas: fecha,pm25,pm10,so2,no2,o3).
3. Cron llama `sincronizar_sinca()` → `aire_registros` con
   fuente=`sinca`, tipo_dato=`observado`.
4. `sesgo_cams_vs_sinca()` compara medias diarias CAMS vs SINCA.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

# Catálogo airshed Copiapó + rajo Mantos. sinca_id: completar con código portal MMA o vía env.
# nombres_sinca alineados al portal https://sinca.mma.gob.cl (Atacama).
ESTACIONES_SINCA_COPIAPO: dict[str, dict[str, Any]] = {
    "copiapo_centro": {
        "sinca_id": None,
        "nombre_sinca": "Copiapó",
        "region": "Atacama",
        "contaminantes": ["PM25", "PM10", "SO2", "NO2", "O3"],
        "portal": "https://sinca.mma.gob.cl",
        "nota": "Buscar estación 'Copiapó' en red SINCA Atacama; pegar key/ID en METGO_SINCA_IDS",
    },
    "paipote": {
        "sinca_id": None,
        "nombre_sinca": "Paipote",
        "region": "Atacama",
        "contaminantes": ["PM10", "SO2"],
        "portal": "https://sinca.mma.gob.cl",
        "nota": "Estación industrial Paipote (SO2/PM10)",
    },
    "tierra_amarilla": {
        "sinca_id": None,
        "nombre_sinca": "Tierra Amarilla",
        "region": "Atacama",
        "contaminantes": ["PM10"],
        "portal": "https://sinca.mma.gob.cl",
        "nota": "Estación Tierra Amarilla",
    },
    # M5 Mantos — placeholder hasta código SINCA / AWS faena
    "mb_rajo": {
        "sinca_id": None,
        "nombre_sinca": "Mantos Blancos (rajo)",
        "region": "Antofagasta",
        "contaminantes": ["PM10", "PM25"],
        "portal": "https://sinca.mma.gob.cl",
        "nota": "M5: pegar código SINCA o CSV AWS faena en METGO_SINCA_IDS / CSV_DIR",
    },
}


def _ids_desde_env() -> dict[str, str]:
    raw = (os.getenv("METGO_SINCA_IDS") or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return {str(k): str(v) for k, v in data.items() if v}
    except json.JSONDecodeError:
        return {}


def _slugs_rajo_faenas() -> dict[str, dict[str, Any]]:
    """M8: anclas rajo de cada faena (SPATI + ventilación) aceptan CSV en METGO_SINCA_CSV_DIR."""
    try:
        from api_rest.faena_catalogo import listar_faenas
        from api_rest.modelo_vs_observado_service import _estacion_aire_faena
    except Exception:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for f in listar_faenas(incluir_izaje=True):
        if not f:
            continue
        slug = _estacion_aire_faena(f)
        if not slug or slug in ESTACIONES_SINCA_COPIAPO:
            continue
        out[slug] = {
            "sinca_id": None,
            "nombre_sinca": f"{f.get('nombre') or f['id']} (rajo)",
            "region": f.get("region") or "",
            "contaminantes": ["PM25", "PM10", "SO2", "NO2", "O3"],
            "portal": "https://sinca.mma.gob.cl",
            "nota": "M8: CSV AWS/SINCA en METGO_SINCA_CSV_DIR/{slug}.csv",
            "faena_id": f["id"],
        }
    return out


def _repo_root() -> Path:
    # api_rest → 05_APIs_Externas → backend → ROOT
    return Path(__file__).resolve().parents[3]


def resolve_csv_dir() -> tuple[Path | None, str]:
    """Dir CSV SINCA: env, o fallback a docs/ejemplos/sinca_csv (E12.1)."""
    env = (os.getenv("METGO_SINCA_CSV_DIR") or "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p, "env"
        return p, "env_missing"
    allow = (os.getenv("METGO_SINCA_USE_EJEMPLOS") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )
    if not allow:
        return None, "disabled"
    root = _repo_root()
    for ejemplos in (
        root / "docs" / "ejemplos" / "sinca_csv",
        root / "tests" / "fixtures" / "sinca",
    ):
        if ejemplos.is_dir() and any(ejemplos.glob("*.csv")):
            return ejemplos, "ejemplos"
    return None, "none"


def catalogo_efectivo() -> dict[str, dict[str, Any]]:
    """Catálogo con sinca_id resuelto (env pisa placeholders) + rajos M8."""
    overrides = _ids_desde_env()
    out: dict[str, dict[str, Any]] = {}
    base = dict(ESTACIONES_SINCA_COPIAPO)
    base.update(_slugs_rajo_faenas())
    for slug, meta in base.items():
        m = dict(meta)
        if overrides.get(slug):
            m["sinca_id"] = overrides[slug]
        out[slug] = m
    return out


def estado_sinca() -> dict[str, Any]:
    """Estado de la integración SINCA (para /api/datos/etl/status y docs)."""
    cat = catalogo_efectivo()
    configuradas = sum(1 for e in cat.values() if e.get("sinca_id"))
    csv_path, csv_origen = resolve_csv_dir()
    csv_files = 0
    if csv_path and csv_path.is_dir():
        csv_files = sum(1 for _ in csv_path.glob("*.csv"))
    return {
        "fuente": "sinca_mma",
        "portal": "https://sinca.mma.gob.cl",
        "estado": (
            "listo_csv"
            if csv_files > 0
            else ("pendiente_fuente" if configuradas == 0 else "parcial")
        ),
        "estaciones_catalogo": len(cat),
        "estaciones_con_codigo": configuradas,
        "csv_dir_configurado": csv_origen in ("env", "ejemplos"),
        "csv_dir_origen": csv_origen,
        "csv_dir": str(csv_path) if csv_path else None,
        "csv_archivos": csv_files,
        "csv_url_configurado": bool((os.getenv("METGO_SINCA_CSV_URL") or "").strip()),
        "circuit_breaker_abierto": _cb_abierto(),
        "circuit_breaker_fallas": _CB_FALLA,
        "estaciones": {
            slug: {
                "sinca_id": m.get("sinca_id"),
                "nombre": m.get("nombre_sinca"),
                "contaminantes": m.get("contaminantes"),
                "nota": m.get("nota"),
            }
            for slug, m in cat.items()
        },
        "nota": (
            "SINCA sin API oficial. Definir METGO_SINCA_IDS y "
            "METGO_SINCA_CSV_DIR o METGO_SINCA_CSV_URL='…/{slug}.csv' (E12). "
            "Sin env, docs/ejemplos/sinca_csv o tests/fixtures/sinca (METGO_SINCA_USE_EJEMPLOS=0 para desactivar). "
            "Ver docs/roadmap/fase-3/sinca_activacion.md"
        ),
    }


def calcular_sesgo(pares: list[dict[str, Any]]) -> dict[str, Any]:
    """Sesgo modelo−observado (CAMS − SINCA) sobre pares diarios alineados.

    Cada ítem: {fecha, cams_pm25?, sinca_pm25?, cams_pm10?, sinca_pm10?}.
    """
    out: dict[str, Any] = {
        "n_pares": len(pares),
        "pm25": None,
        "pm10": None,
    }
    for var in ("pm25", "pm10"):
        diffs: list[float] = []
        for p in pares:
            c = p.get(f"cams_{var}")
            s = p.get(f"sinca_{var}")
            if c is None or s is None:
                continue
            diffs.append(float(c) - float(s))
        if not diffs:
            continue
        mae = sum(abs(d) for d in diffs) / len(diffs)
        bias = sum(diffs) / len(diffs)
        out[var] = {
            "n": len(diffs),
            "sesgo_medio": round(bias, 2),
            "mae": round(mae, 2),
            "unidad": "ug/m3",
            "definicion": "CAMS(modelo) - SINCA(observado)",
        }
    return out


def _leer_csv_estacion(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    filas: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fecha = (row.get("fecha") or row.get("date") or "").strip()
            if not fecha:
                continue
            fila: dict[str, Any] = {
                "fecha": fecha[:10],
                "tipo_dato": "observado",
                "fuente": "sinca",
            }
            for src, dst in (
                ("pm25", "pm2_5"),
                ("pm2_5", "pm2_5"),
                ("pm10", "pm10"),
                ("so2", "sulphur_dioxide"),
                ("no2", "nitrogen_dioxide"),
                ("o3", "ozone"),
            ):
                raw = row.get(src)
                if raw is None or str(raw).strip() == "":
                    continue
                try:
                    fila[dst] = float(raw)
                except ValueError:
                    continue
            # ICAP best-effort
            try:
                from api_rest.aire_service import evaluar_icap

                fila.update(evaluar_icap(fila.get("pm2_5"), fila.get("pm10")))
            except Exception:
                pass
            filas.append(fila)
    return filas


def sincronizar_sinca(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL SINCA → aire_registros (observado) vía CSV local o URL template."""
    estado = estado_sinca()
    cat = catalogo_efectivo()
    slugs = estaciones or list(cat.keys())
    csv_path, csv_origen = resolve_csv_dir()
    url_tpl = (os.getenv("METGO_SINCA_CSV_URL") or "").strip()
    # Ej.: https://ejemplo/sinca/{slug}.csv  o  .../{id}.csv

    if csv_path is None and not url_tpl:
        motivo = "sin_codigos_sinca" if estado["estaciones_con_codigo"] == 0 else "sin_csv_dir"
        return {
            "sinca_sync": {},
            "omitido": True,
            "motivo": motivo,
            "estado": estado,
        }

    try:
        from api_rest.integracion import aire_store
    except Exception as exc:
        return {"sinca_sync": {}, "omitido": True, "motivo": f"aire_store: {exc}", "estado": estado}

    base = csv_path if csv_path and csv_path.is_dir() else None
    detalle: dict[str, int] = {}
    for slug in slugs:
        if slug not in cat:
            continue
        filas: list[dict[str, Any]] = []
        if base is not None:
            filas = _leer_csv_estacion(base / f"{slug}.csv")
        if not filas and url_tpl:
            filas = _fetch_csv_url(url_tpl, slug, cat[slug].get("sinca_id"))
        if not filas:
            detalle[slug] = 0
            continue
        detalle[slug] = aire_store.guardar_aire(
            slug, filas, fuente="sinca", tipo_dato="observado"
        )

    escritos = sum(detalle.values())
    # M8: marcar área con fuente observado cuando hubo escritura
    ids_ok = [s for s, n in detalle.items() if n and n > 0]
    marcados = 0
    if ids_ok:
        try:
            from api_rest.integracion import estaciones_catalog_store

            marcados = estaciones_catalog_store.marcar_fuente_observado(ids_ok)
        except Exception as exc:
            print(f"sinca marcar_observado: {exc}")

    return {
        "sinca_sync": detalle,
        "omitido": escritos == 0,
        "motivo": None if escritos else "csv_sin_filas",
        "csv_dir_origen": csv_origen,
        "estado": estado_sinca(),
        "fuente_observado_marcados": marcados,
    }


# Circuit breaker ligero (E10): tras N fallos de fetch URL, cooldown.
_CB_FALLA = 0
_CB_HASTA = 0.0  # epoch seconds
_CB_UMBRAL = int(os.getenv("METGO_SINCA_CB_FALLAS", "3"))
_CB_COOLDOWN_S = int(os.getenv("METGO_SINCA_CB_COOLDOWN_S", "900"))


def _cb_abierto() -> bool:
    import time

    return time.time() < _CB_HASTA


def _cb_registrar_exito() -> None:
    global _CB_FALLA, _CB_HASTA
    _CB_FALLA = 0
    _CB_HASTA = 0.0


def _cb_registrar_fallo() -> None:
    global _CB_FALLA, _CB_HASTA
    import time

    _CB_FALLA += 1
    if _CB_FALLA >= _CB_UMBRAL:
        _CB_HASTA = time.time() + _CB_COOLDOWN_S


def _fetch_csv_url(template: str, slug: str, sinca_id: Any) -> list[dict[str, Any]]:
    """Descarga CSV remoto. Template puede incluir {slug} y {id}."""
    import tempfile

    if _cb_abierto():
        print(f"sinca_service: circuit breaker abierto; skip fetch {slug}")
        return []

    url = template.replace("{slug}", slug).replace("{id}", str(sinca_id or slug))
    try:
        import requests

        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".csv", delete=False
        ) as tmp:
            tmp.write(r.text)
            path = Path(tmp.name)
        try:
            filas = _leer_csv_estacion(path)
            _cb_registrar_exito()
            return filas
        finally:
            path.unlink(missing_ok=True)
    except Exception as exc:
        _cb_registrar_fallo()
        print(f"sinca_service._fetch_csv_url {slug}: {exc}")
        return []


def sesgo_cams_vs_sinca(estacion_id: str, dias: int = 14) -> dict[str, Any]:
    """Compara últimos días CAMS (modelo) vs SINCA (observado) en aire_registros."""
    slug = estacion_id.lower().replace("-", "_")
    cat = catalogo_efectivo()
    if slug not in cat:
        return {"error": "estacion_no_en_catalogo_sinca", "estacion_id": slug}

    try:
        from api_rest.integracion import aire_store
    except Exception as exc:
        return {"error": str(exc), "estacion_id": slug}

    cams = aire_store.leer_aire_por_fuente(slug, fuente="openmeteo_cams", dias=dias)
    sinca = aire_store.leer_aire_por_fuente(slug, fuente="sinca", dias=dias)

    def _por_dia(filas: list[dict[str, Any]], prefix: str) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        for f in filas:
            dia = str(f.get("fecha") or f.get("fecha_hora") or "")[:10]
            if not dia:
                continue
            bucket = out.setdefault(dia, {})
            if f.get("pm2_5") is not None:
                bucket[f"{prefix}_pm25"] = float(f["pm2_5"])
            if f.get("pm10") is not None:
                bucket[f"{prefix}_pm10"] = float(f["pm10"])
        return out

    por_cams = _por_dia(cams, "cams")
    por_sinca = _por_dia(sinca, "sinca")
    pares: list[dict[str, Any]] = []
    for dia in sorted(set(por_cams) & set(por_sinca)):
        pares.append({"fecha": dia, **por_cams[dia], **por_sinca[dia]})

    metricas = calcular_sesgo(pares)
    return {
        "estacion_id": slug,
        "dias": dias,
        "n_cams": len(cams),
        "n_sinca": len(sinca),
        "pares": pares[-dias:],
        **metricas,
        "estado_sinca": estado_sinca()["estado"],
    }
