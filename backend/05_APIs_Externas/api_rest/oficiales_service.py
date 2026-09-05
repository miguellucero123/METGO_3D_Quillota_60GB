#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fuentes oficiales Chile (E12) — Agromet INIA + DMC.

Sin inventar series: solo lee CSV locales o HTTP si hay URL/credenciales.
Códigos se activan con:

- ``METGO_AGROMET_IDS='{"quillota":"CODIGO"}'``
- ``METGO_DMC_IDS='{"quillota":"320124"}'``  (Quillota Liceo Agrícola, inventario 2026-09)
- ``METGO_AGROMET_CSV_DIR`` / ``METGO_DMC_CSV_DIR`` con ``{slug}.csv``

Columnas CSV esperadas: fecha, temperatura_max, temperatura_min, temperatura,
humedad, precipitacion, viento, presion.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

# Inventario 2026-09-04: códigos confirmados en ficha DMC / listados públicos.
# Activar candidatos con METGO_DMC_USAR_CANDIDATOS=1 o pisar con METGO_DMC_IDS.
AGROMET_ESTACIONES: dict[str, dict[str, Any]] = {
    "quillota": {
        "codigo": None,
        "codigo_candidato": None,
        "nombre": "Quillota",
        "nombre_red": "Usar DMC 320124; Agromet La Cruz cercano (código INIA pendiente)",
        "estado": "usar_dmc_320124",
        "url_portal": "https://agrometeorologia.cl/",
    },
    "la_cruz": {
        "codigo": None,
        "nombre": "La Cruz",
        "estado": "pendiente_codigo_inia",
        "url_portal": "https://agrometeorologia.cl/",
        "nota": "Confirmada activa en listado INIA; ID interno no publicado",
    },
    "los_nogales": {
        "codigo": None,
        "nombre": "Los Nogales",
        "estado": "sin_estacion_confirmada",
        "url_portal": "https://agrometeorologia.cl/",
    },
    "hijuelas": {
        "codigo": None,
        "nombre": "Hijuelas",
        "estado": "sin_estacion_confirmada",
        "url_portal": "https://agrometeorologia.cl/",
    },
    "limache": {
        "codigo": None,
        "nombre": "Limache",
        "estado": "gap_historico",
        "url_portal": "https://agrometeorologia.cl/",
        "nota": "Boletín DMC histórico; no en listado vivo 2026-09",
    },
    "olmue": {
        "codigo": None,
        "nombre": "Olmue",
        "estado": "gap_historico",
        "url_portal": "https://agrometeorologia.cl/",
    },
}

DMC_ESTACIONES: dict[str, dict[str, Any]] = {
    "quillota": {
        "codigo": None,
        "codigo_candidato": "320124",
        "nombre": "Quillota, Liceo Agrícola",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/320124",
        "lat": -32.90722,
        "lon": -71.27139,
        "nota": "Inventario 2026-09 — reemplaza candidato antiguo 330007",
    },
    "quillota_fdf": {
        "codigo": None,
        "codigo_candidato": "320100",
        "nombre": "Quillota (FDF)",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/320096",
        "nota": "Dato de terceros vía DMC; ficha también 320096",
    },
    "limache": {
        "codigo": None,
        "nombre": "Limache",
        "estado": "gap_historico",
        "url_portal": "https://www.meteochile.gob.cl/",
    },
    "copiapo_centro": {
        "codigo": None,
        "codigo_candidato": "270009",
        "nombre": "Copiapó, Universidad de Atacama",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/270009",
        "lat": -27.35889,
        "lon": -70.35333,
    },
    "chamonate": {
        "codigo": None,
        "codigo_candidato": "270002",
        "nombre": "Copiapó, Chamonate Ad.",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/270002",
    },
    "chuquicamata": {
        "codigo": None,
        "codigo_candidato": "220901",
        "nombre": "El Loa - Chuquicamata CODELCO",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/220901",
        "nota": "~1 km faena",
    },
    "rio_serrano": {
        "codigo": None,
        "codigo_candidato": "510020",
        "nombre": "Río Serrano, Torres del Paine",
        "estado": "confirmado_ficha",
        "url_portal": "https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion/510020",
    },
}


def _ids_env(var: str) -> dict[str, str]:
    raw = (os.getenv(var) or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return {str(k): str(v) for k, v in data.items() if v}
    except json.JSONDecodeError:
        return {}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_csv_dir(kind: str) -> tuple[Path | None, str]:
    """kind: agromet | dmc. Env, docs/ejemplos, o tests/fixtures."""
    env_key = "METGO_AGROMET_CSV_DIR" if kind == "agromet" else "METGO_DMC_CSV_DIR"
    env = (os.getenv(env_key) or "").strip()
    if env:
        p = Path(env)
        return p, "env" if p.is_dir() else "env_missing"
    allow_key = (
        "METGO_AGROMET_USE_EJEMPLOS" if kind == "agromet" else "METGO_DMC_USE_EJEMPLOS"
    )
    if (os.getenv(allow_key) or "1").strip().lower() in ("0", "false", "no"):
        return None, "disabled"
    root = _repo_root()
    for rel, origen in (
        (Path("docs") / "ejemplos" / f"{kind}_csv", "ejemplos"),
        (Path("tests") / "fixtures" / kind, "fixtures"),
    ):
        candid = root / rel
        if candid.is_dir():
            return candid, origen
    return None, "none"


def catalogo_agromet() -> dict[str, dict[str, Any]]:
    overrides = _ids_env("METGO_AGROMET_IDS")
    out: dict[str, dict[str, Any]] = {}
    for slug, meta in AGROMET_ESTACIONES.items():
        m = dict(meta)
        if overrides.get(slug):
            m["codigo"] = overrides[slug]
            m["estado"] = "activo_env"
        out[slug] = m
    return out


def catalogo_dmc() -> dict[str, dict[str, Any]]:
    overrides = _ids_env("METGO_DMC_IDS")
    activar_candidatos = (os.getenv("METGO_DMC_USAR_CANDIDATOS") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    out: dict[str, dict[str, Any]] = {}
    for slug, meta in DMC_ESTACIONES.items():
        m = dict(meta)
        if overrides.get(slug):
            m["codigo"] = overrides[slug]
            m["estado"] = "activo_env"
        elif activar_candidatos and m.get("codigo_candidato") and not m.get("codigo"):
            m["codigo"] = m["codigo_candidato"]
            m["estado"] = "candidato_activado"
        out[slug] = m
    return out


def estado_fuentes() -> dict[str, Any]:
    agro = catalogo_agromet()
    dmc = catalogo_dmc()
    agro_ok = sum(1 for e in agro.values() if e.get("codigo"))
    dmc_ok = sum(1 for e in dmc.values() if e.get("codigo"))
    agro_path, agro_origen = resolve_csv_dir("agromet")
    dmc_path, dmc_origen = resolve_csv_dir("dmc")
    csv_agro = agro_origen in ("env", "ejemplos", "fixtures")
    csv_dmc = dmc_origen in ("env", "ejemplos", "fixtures")
    if dmc_ok or csv_dmc:
        fuente_activa = "dmc"
    elif agro_ok or csv_agro:
        fuente_activa = "agromet"
    else:
        fuente_activa = "openmeteo_archive"
    return {
        "agromet": {
            "disponible": agro_ok > 0 or csv_agro,
            "estaciones_con_codigo": agro_ok,
            "csv_dir_configurado": csv_agro,
            "csv_dir_origen": agro_origen,
            "csv_dir": str(agro_path) if agro_path else None,
            "motivo": (
                None
                if agro_ok or csv_agro
                else "Sin códigos METGO_AGROMET_IDS ni METGO_AGROMET_CSV_DIR"
            ),
            "estaciones": agro,
        },
        "dmc": {
            "disponible": dmc_ok > 0 or csv_dmc,
            "estaciones_con_codigo": dmc_ok,
            "csv_dir_configurado": csv_dmc,
            "csv_dir_origen": dmc_origen,
            "csv_dir": str(dmc_path) if dmc_path else None,
            "motivo": (
                None
                if dmc_ok or csv_dmc
                else "Sin códigos METGO_DMC_IDS ni METGO_DMC_CSV_DIR"
            ),
            "estaciones": dmc,
        },
        "fuente_activa": fuente_activa,
        "nota_e12": (
            "Observado: DMC/Agromet vía METGO_*_IDS + CSV. "
            "Pronóstico: Open-Meteo ciclo 00/12 (ver POLITICA_FUENTES.md). "
            "Quillota DMC confirmado 320124 (ficha); activar METGO_DMC_USAR_CANDIDATOS=1 "
            "o METGO_DMC_IDS. Ver config/meteo/INVENTARIO_ESTACIONES_PARTE1.md."
        ),
    }


def _leer_csv_meteo(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    filas: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fecha = (row.get("fecha") or row.get("date") or "").strip()[:10]
            if not fecha:
                continue
            fila: dict[str, Any] = {"fecha": fecha}
            for col in (
                "temperatura_max",
                "temperatura_min",
                "temperatura",
                "temperatura_promedio",
                "humedad",
                "precipitacion",
                "viento",
                "presion",
                "radiacion",
                "evapotranspiracion",
            ):
                raw = row.get(col)
                if raw is None or str(raw).strip() == "":
                    continue
                try:
                    fila[col] = float(raw)
                except ValueError:
                    continue
            filas.append(fila)
    return filas


def fetch_agromet_historico(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    """Lee CSV Agromet si hay dir; no inventa datos HTTP sin contrato estable."""
    slug = estacion_id.lower().replace("-", "_")
    meta = catalogo_agromet().get(slug)
    if not meta:
        return []
    csv_path, _ = resolve_csv_dir("agromet")
    if csv_path and csv_path.is_dir():
        filas = _leer_csv_meteo(csv_path / f"{slug}.csv")
        if dias > 0 and filas:
            return filas[-dias:]
        return filas
    if not meta.get("codigo"):
        return []
    # Sin API pública estable documentada: vacío hasta conectar endpoint oficial.
    return []


def fetch_dmc_historico(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    slug = estacion_id.lower().replace("-", "_")
    meta = catalogo_dmc().get(slug)
    if not meta:
        return []
    csv_path, _ = resolve_csv_dir("dmc")
    if csv_path and csv_path.is_dir():
        filas = _leer_csv_meteo(csv_path / f"{slug}.csv")
        if dias > 0 and filas:
            return filas[-dias:]
        return filas
    if not meta.get("codigo"):
        return []
    return []


def sincronizar_oficiales(estaciones: list[str] | None = None) -> dict[str, Any]:
    """ETL Agromet/DMC CSV → meteo_registros (tipo observado vía fuente)."""
    try:
        from api_rest.integracion import meteo_store
    except Exception as exc:
        return {"omitido": True, "motivo": f"meteo_store: {exc}"}

    slugs = estaciones or sorted(set(catalogo_agromet()) | set(catalogo_dmc()))
    detalle: dict[str, Any] = {"agromet": {}, "dmc": {}}
    for slug in slugs:
        agro = fetch_agromet_historico(slug, dias=92)
        if agro:
            detalle["agromet"][slug] = meteo_store.guardar_registros(
                slug, agro, fuente="agromet"
            )
        dmc = fetch_dmc_historico(slug, dias=92)
        if dmc:
            detalle["dmc"][slug] = meteo_store.guardar_registros(slug, dmc, fuente="dmc")

    escritos = sum(detalle["agromet"].values()) + sum(detalle["dmc"].values())
    return {
        "oficiales_sync": detalle,
        "omitido": escritos == 0,
        "motivo": None if escritos else "sin_csv_ni_filas",
        "estado": estado_fuentes(),
    }
