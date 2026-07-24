#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo gobernanza de fuentes (E12) — lectura Supabase + seed en memoria."""

from __future__ import annotations

from typing import Any

# Seed alineado con migración 20260724170000_e12_fuentes_gobernanza.sql
_SEED: list[dict[str, Any]] = [
    {
        "id": "openmeteo_forecast_quillota",
        "sitio": "quillota",
        "proveedor": "openmeteo",
        "nombre": "Open-Meteo Forecast",
        "tipo_dato": "pronostico",
        "licencia": "CC-BY 4.0 (Open-Meteo)",
        "url": "https://open-meteo.com/",
        "frescura_sla_h": 6,
        "cobertura": "Valle de Aconcagua (5 estaciones)",
        "estado": "activo",
    },
    {
        "id": "openmeteo_archive_quillota",
        "sitio": "quillota",
        "proveedor": "openmeteo",
        "nombre": "Open-Meteo Archive (ERA5)",
        "tipo_dato": "reanalisis",
        "licencia": "CC-BY 4.0 (Open-Meteo / ECMWF)",
        "url": "https://open-meteo.com/en/docs/historical-weather-api",
        "frescura_sla_h": 24,
        "cobertura": "Reanálisis ~9 km",
        "estado": "activo",
    },
    {
        "id": "agromet_quillota",
        "sitio": "quillota",
        "proveedor": "agromet_inia",
        "nombre": "Agromet INIA",
        "tipo_dato": "observado",
        "licencia": "Uso sujeto a registro INIA",
        "url": "https://agromet.inia.cl/",
        "frescura_sla_h": 3,
        "cobertura": "Estaciones físicas valle (códigos pendientes)",
        "estado": "pendiente",
    },
    {
        "id": "dmc_quillota",
        "sitio": "quillota",
        "proveedor": "dmc",
        "nombre": "DMC Chile",
        "tipo_dato": "observado",
        "licencia": "Datos oficiales DMC",
        "url": "https://www.meteochile.gob.cl/",
        "frescura_sla_h": 3,
        "cobertura": "Red sinóptica (códigos pendientes)",
        "estado": "pendiente",
    },
    {
        "id": "openmeteo_cams_copiapo",
        "sitio": "copiapo",
        "proveedor": "openmeteo_cams",
        "nombre": "Open-Meteo Air Quality (CAMS)",
        "tipo_dato": "modelo",
        "licencia": "CC-BY 4.0 (Open-Meteo / CAMS)",
        "url": "https://open-meteo.com/en/docs/air-quality-api",
        "frescura_sla_h": 3,
        "cobertura": "Airshed Copiapó / Tierra Amarilla",
        "estado": "activo",
    },
    {
        "id": "sinca_mma_copiapo",
        "sitio": "copiapo",
        "proveedor": "sinca_mma",
        "nombre": "SINCA MMA Chile",
        "tipo_dato": "observado",
        "licencia": "Datos públicos MMA (portal SINCA)",
        "url": "https://sinca.mma.gob.cl",
        "frescura_sla_h": 24,
        "cobertura": "Copiapó, Paipote, Tierra Amarilla",
        "estado": "pendiente",
    },
    {
        "id": "openmeteo_cams_mantos",
        "sitio": "mantos_blancos",
        "proveedor": "openmeteo_cams",
        "nombre": "Open-Meteo Air Quality (CAMS)",
        "tipo_dato": "modelo",
        "licencia": "CC-BY 4.0 (Open-Meteo / CAMS)",
        "url": "https://open-meteo.com/en/docs/air-quality-api",
        "frescura_sla_h": 3,
        "cobertura": "Puntos de faena Mantos Blancos",
        "estado": "activo",
    },
    {
        "id": "openmeteo_forecast_paine",
        "sitio": "paine",
        "proveedor": "openmeteo",
        "nombre": "Open-Meteo Forecast",
        "tipo_dato": "pronostico",
        "licencia": "CC-BY 4.0 (Open-Meteo)",
        "url": "https://open-meteo.com/",
        "frescura_sla_h": 6,
        "cobertura": "Torres del Paine",
        "estado": "activo",
    },
]


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client() or None
    except Exception:
        return None


def listar_fuentes(sitio: str | None = None) -> list[dict[str, Any]]:
    """Lista fuentes desde Supabase; si no hay filas/cliente, usa seed en memoria."""
    client = _client()
    if client:
        try:
            q = client.table("fuentes").select("*").order("id")
            if sitio:
                q = q.eq("sitio", sitio.strip().lower())
            res = q.execute()
            if res.data:
                return list(res.data)
        except Exception as exc:
            print(f"fuentes_store.listar_fuentes: {exc}")
    rows = list(_SEED)
    if sitio:
        s = sitio.strip().lower()
        rows = [r for r in rows if r.get("sitio") == s]
    return rows


def resumen_gobernanza(sitio: str | None = None) -> dict[str, Any]:
    rows = listar_fuentes(sitio)
    por_estado: dict[str, int] = {}
    for r in rows:
        est = str(r.get("estado") or "desconocido")
        por_estado[est] = por_estado.get(est, 0) + 1
    origen = "seed_memoria"
    client = _client()
    if client:
        try:
            probe = client.table("fuentes").select("id").limit(1).execute()
            if probe.data:
                origen = "supabase"
        except Exception:
            pass
    return {
        "total": len(rows),
        "por_estado": por_estado,
        "fuentes": rows,
        "origen": origen,
    }
