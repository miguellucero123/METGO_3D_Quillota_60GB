#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M9 — umbrales SPATI por sitio/faena (defaults + override JSON)."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

# Defaults canónicos (km/h) — alineados a CraneSafetyAlertSystem histórico.
UMBRALES_SPATI_DEFAULT: dict[str, Any] = {
    "verde_max_kmh": 26,
    "amarillo_min_kmh": 26,
    "naranja_min_kmh": 30,
    "rojo_min_kmh": 35,
    "flag_critico_kmh": 36,
    "rayos_pct": 30,
    "precip_mmh": 2.0,
    "fuerza_naranja_pct": 55,
    "fuerza_rojo_pct": 80,
    "nota": (
        "Umbral crítico por ráfaga; control por fuerza F=½ρv²ACd "
        "(ρ corregida por altitud)"
    ),
}

ALERTAS_DESTINO_DEFAULT: dict[str, Any] = {
    "emails": [],
    "webhook_url": None,
    "nivel_minimo": 2,
}


def _runtime_overrides_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d / "spati_umbrales_overrides.json"
    return Path("spati_umbrales_overrides.json")


def _payload_publico(umb: dict[str, Any]) -> dict[str, Any]:
    """Formato API (compat con frontend)."""
    a0 = float(umb["amarillo_min_kmh"])
    n0 = float(umb["naranja_min_kmh"])
    r0 = float(umb["rojo_min_kmh"])
    return {
        "verde_max_kmh": float(umb["verde_max_kmh"]),
        "amarillo": [a0, n0 - 1],
        "naranja": [n0, r0 - 1],
        "rojo_min_kmh": r0,
        "flag_critico_kmh": float(umb["flag_critico_kmh"]),
        "rayos_pct": float(umb.get("rayos_pct", 30)),
        "precip_mmh": float(umb.get("precip_mmh", 2.0)),
        "fuerza_naranja_pct": float(umb.get("fuerza_naranja_pct", 55)),
        "fuerza_rojo_pct": float(umb.get("fuerza_rojo_pct", 80)),
        "nota": umb.get("nota") or UMBRALES_SPATI_DEFAULT["nota"],
        "fuente": umb.get("fuente") or "default",
    }


def _merge(base: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    out = deepcopy(base)
    if not override:
        return out
    for k, v in override.items():
        if v is None or k in ("nota",):
            if k == "nota" and v:
                out[k] = v
            continue
        if k in out or k.endswith("_kmh") or k.endswith("_pct") or k.endswith("_mmh"):
            try:
                out[k] = float(v) if isinstance(v, (int, float, str)) and k != "nota" else v
            except (TypeError, ValueError):
                out[k] = v
    # Alias desde payload público
    if "amarillo" in override and isinstance(override["amarillo"], (list, tuple)):
        out["amarillo_min_kmh"] = float(override["amarillo"][0])
        out["verde_max_kmh"] = float(override["amarillo"][0])
    if "naranja" in override and isinstance(override["naranja"], (list, tuple)):
        out["naranja_min_kmh"] = float(override["naranja"][0])
    if "rojo_min_kmh" in override:
        out["rojo_min_kmh"] = float(override["rojo_min_kmh"])
    if "flag_critico_kmh" in override:
        out["flag_critico_kmh"] = float(override["flag_critico_kmh"])
    if "verde_max_kmh" in override:
        out["verde_max_kmh"] = float(override["verde_max_kmh"])
        out["amarillo_min_kmh"] = float(override["verde_max_kmh"])
    return out


def _overrides_env(sitio_id: str) -> dict[str, Any]:
    raw = (os.getenv("METGO_SPATI_UMBRALES_JSON") or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and sitio_id in data and isinstance(data[sitio_id], dict):
            return data[sitio_id]
        if isinstance(data, dict) and "rojo_min_kmh" in data:
            return data
    except json.JSONDecodeError:
        pass
    return {}


def _overrides_archivo(sitio_id: str) -> dict[str, Any]:
    path = _runtime_overrides_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        row = (data.get("umbrales") or {}).get(sitio_id) or {}
        return row if isinstance(row, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _overrides_supabase(sitio_id: str) -> dict[str, Any]:
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if not client:
            return {}
        res = (
            client.table("spati_sitios_grua")
            .select("umbrales_json,alertas_destino")
            .eq("slug", sitio_id)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        if not rows:
            return {}
        umb = rows[0].get("umbrales_json") or {}
        return umb if isinstance(umb, dict) else {}
    except Exception:
        return {}


def umbrales_efectivos(sitio_id: str) -> dict[str, Any]:
    """Merge: default ← archivo local ← env ← Supabase."""
    sid = (sitio_id or "").strip().lower()
    merged = deepcopy(UMBRALES_SPATI_DEFAULT)
    merged = _merge(merged, _overrides_archivo(sid))
    merged = _merge(merged, _overrides_env(sid))
    sb = _overrides_supabase(sid)
    if sb:
        merged = _merge(merged, sb)
        merged["fuente"] = "supabase"
    elif _overrides_env(sid) or _overrides_archivo(sid):
        merged["fuente"] = "override"
    else:
        merged["fuente"] = "default"
    return _payload_publico(merged)


def umbrales_internos(sitio_id: str) -> dict[str, Any]:
    """Dict con claves *_kmh para CraneSafetyAlertSystem."""
    pub = umbrales_efectivos(sitio_id)
    return {
        "amarillo_min_kmh": float(pub["amarillo"][0]),
        "naranja_min_kmh": float(pub["naranja"][0]),
        "rojo_min_kmh": float(pub["rojo_min_kmh"]),
        "flag_critico_kmh": float(pub["flag_critico_kmh"]),
        "verde_max_kmh": float(pub["verde_max_kmh"]),
        "rayos_pct": float(pub.get("rayos_pct", 30)),
        "precip_mmh": float(pub.get("precip_mmh", 2.0)),
        "fuerza_naranja_pct": float(pub.get("fuerza_naranja_pct", 55)),
        "fuerza_rojo_pct": float(pub.get("fuerza_rojo_pct", 80)),
    }


def guardar_umbrales_local(sitio_id: str, override: dict[str, Any]) -> dict[str, Any]:
    """Persiste override en JSON local (dev / sin Supabase)."""
    sid = (sitio_id or "").strip().lower()
    path = _runtime_overrides_path()
    data: dict[str, Any] = {"umbrales": {}, "alertas": {}}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    data.setdefault("umbrales", {})[sid] = override
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # Intentar Supabase
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if client:
            client.table("spati_sitios_grua").update({"umbrales_json": override}).eq(
                "slug", sid
            ).execute()
    except Exception as exc:
        print(f"umbrales_service supabase: {exc}")
    return umbrales_efectivos(sid)


def guardar_alertas_destino(sitio_id: str, dest: dict[str, Any]) -> dict[str, Any]:
    """Persiste destinos de alerta por faena (archivo + Supabase)."""
    sid = (sitio_id or "").strip().lower()
    emails_raw = dest.get("emails") or []
    if isinstance(emails_raw, str):
        emails = [e.strip() for e in emails_raw.replace(";", ",").split(",") if e.strip()]
    else:
        emails = [str(e).strip() for e in emails_raw if str(e).strip()]
    webhook = dest.get("webhook_url")
    if webhook is not None:
        webhook = str(webhook).strip() or None
    try:
        nivel = int(dest.get("nivel_minimo", ALERTAS_DESTINO_DEFAULT["nivel_minimo"]))
    except (TypeError, ValueError):
        nivel = int(ALERTAS_DESTINO_DEFAULT["nivel_minimo"])
    nivel = max(0, min(nivel, 3))
    payload = {"emails": emails, "webhook_url": webhook, "nivel_minimo": nivel}

    path = _runtime_overrides_path()
    data: dict[str, Any] = {"umbrales": {}, "alertas": {}}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    data.setdefault("alertas", {})[sid] = payload
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if client:
            client.table("spati_sitios_grua").update({"alertas_destino": payload}).eq(
                "slug", sid
            ).execute()
    except Exception as exc:
        print(f"umbrales_service alertas supabase: {exc}")
    return alertas_destino(sid)


def alertas_destino_publico(sitio_id: str, *, detallado: bool = False) -> dict[str, Any]:
    """Metadatos públicos; con detallado=True incluye emails/webhook (edición)."""
    dest = alertas_destino(sitio_id)
    out = {
        "nivel_minimo": dest.get("nivel_minimo"),
        "tiene_email": bool(dest.get("emails")),
        "tiene_webhook": bool(dest.get("webhook_url")),
        "n_emails": len(dest.get("emails") or []),
    }
    if detallado:
        out["emails"] = list(dest.get("emails") or [])
        out["webhook_url"] = dest.get("webhook_url")
    return out


def alertas_destino(sitio_id: str) -> dict[str, Any]:
    out = deepcopy(ALERTAS_DESTINO_DEFAULT)
    # Env global
    email = (os.getenv("METGO_SPATI_ALERT_EMAIL") or os.getenv("METGO_NOTIFY_EMAIL") or "").strip()
    if email:
        out["emails"] = [email]
    wh = (os.getenv("METGO_SPATI_ALERT_WEBHOOK") or "").strip()
    if wh:
        out["webhook_url"] = wh
    # Archivo
    path = _runtime_overrides_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            row = (data.get("alertas") or {}).get(sitio_id) or {}
            if isinstance(row, dict):
                if row.get("emails") is not None:
                    out["emails"] = list(row["emails"])
                if "webhook_url" in row:
                    out["webhook_url"] = row["webhook_url"]
                if row.get("nivel_minimo") is not None:
                    out["nivel_minimo"] = int(row["nivel_minimo"])
        except (json.JSONDecodeError, OSError, ValueError):
            pass
    # Supabase
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if client:
            res = (
                client.table("spati_sitios_grua")
                .select("alertas_destino")
                .eq("slug", sitio_id)
                .limit(1)
                .execute()
            )
            rows = res.data or []
            if rows and isinstance(rows[0].get("alertas_destino"), dict):
                dest = rows[0]["alertas_destino"]
                if dest.get("emails") is not None:
                    out["emails"] = list(dest["emails"])
                if "webhook_url" in dest:
                    out["webhook_url"] = dest["webhook_url"]
                if dest.get("nivel_minimo") is not None:
                    out["nivel_minimo"] = int(dest["nivel_minimo"])
    except Exception:
        pass
    return out