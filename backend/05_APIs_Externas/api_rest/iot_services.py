#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingesta IoT simulada + persistencia JSON (Fase 3.1)."""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _store_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "iot_lecturas.json"
    return Path("iot_lecturas.json")


def _load() -> list[dict[str, Any]]:
    try:
        from api_rest.integracion.supabase_store import get_supabase_client
        client = get_supabase_client()
        if client:
            res = client.table("datos_iot").select("*").order("timestamp", desc=True).limit(500).execute()
            if res.data:
                return res.data
    except Exception as e:
        print(f"Error cargando iot de Supabase: {e}")
    # Fallback JSON local (M7 demo / offline)
    path = _store_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
        except Exception as e:
            print(f"Error leyendo iot local: {e}")
    return _seed()


def _save(items: list[dict[str, Any]]) -> None:
    # Persistencia local siempre (demo M7 / degradación)
    path = _store_path()
    try:
        prev: list[dict[str, Any]] = []
        if path.is_file():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                prev = raw
        merged = items + prev
        path.write_text(
            json.dumps(merged[:500], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"Error guardando iot local: {e}")
    try:
        from api_rest.integracion.supabase_store import get_supabase_client
        client = get_supabase_client()
        if client and items:
            nuevos = []
            for item in items:
                data = {
                    "sensor_id": item.get("sensor_id"),
                    "tipo": item.get("tipo"),
                    "estacion_id": item.get("estacion_id"),
                    "valor": item.get("valor"),
                    "unidad": item.get("unidad"),
                    "fuente": item.get("fuente"),
                    "timestamp": item.get("timestamp")
                }
                nuevos.append(data)
            client.table("datos_iot").insert(nuevos).execute()
    except Exception as e:
        print(f"Error guardando iot en Supabase: {e}")


def _seed() -> list[dict[str, Any]]:
    sensores = listar_sensores()
    items = []
    for s in sensores[:3]:
        items.append(_generar_lectura(s["id"], s["tipo"], s["estacion_id"]))
    _save(items)
    return items


def listar_sensores() -> list[dict[str, Any]]:
    base = [
        {
            "id": "iot-q-temp",
            "tipo": "temperatura",
            "estacion_id": "quillota",
            "ubicacion": "Fundo demo Quillota",
            "activo": True,
            "red": "simulado",
        },
        {
            "id": "iot-q-hum",
            "tipo": "humedad",
            "estacion_id": "quillota",
            "ubicacion": "Invernadero Quillota",
            "activo": True,
            "red": "simulado",
        },
        {
            "id": "iot-hij-viento",
            "tipo": "viento_velocidad",
            "estacion_id": "hijuelas",
            "ubicacion": "Parcela Hijuelas",
            "activo": True,
            "red": "simulado",
        },
        {
            "id": "iot-cas-temp",
            "tipo": "temperatura",
            "estacion_id": "casablanca",
            "ubicacion": "Casablanca costa",
            "activo": True,
            "red": "simulado",
        },
    ]
    return base + _sensores_lora_diy()


def _estaciones_diy_catalogo() -> list[dict[str, Any]]:
    """Catálogo red LoRa DIY Aconcagua (hardware/red-estaciones-diy-aconcagua)."""
    return [
        {
            "id": "acq-01",
            "station_id": "ACQ-01",
            "nombre": "Quillota Fundo Demo",
            "lat": -32.883,
            "lon": -71.249,
            "profile": "mvp_bme280",
            "lora_sf": 9,
            "activo": True,
            "estado": "prototipo",
        },
        {
            "id": "acq-02",
            "station_id": "ACQ-02",
            "nombre": "Hijuelas Sector Norte",
            "lat": -32.800,
            "lon": -71.150,
            "profile": "agro",
            "lora_sf": 10,
            "activo": True,
            "estado": "planificado",
        },
        {
            "id": "acq-03",
            "station_id": "ACQ-03",
            "nombre": "La Cruz",
            "lat": -32.825,
            "lon": -71.227,
            "profile": "cobertura",
            "lora_sf": 9,
            "activo": True,
            "estado": "planificado",
        },
    ]


def _sensores_lora_diy() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for est in _estaciones_diy_catalogo():
        sid = est["station_id"]
        eid = est["id"]
        for tipo, suf in (
            ("temperatura", "temp_c"),
            ("humedad", "rh"),
            ("presion", "pressure_hpa"),
        ):
            out.append(
                {
                    "id": f"lora-{sid}-{suf}",
                    "tipo": tipo,
                    "estacion_id": eid,
                    "ubicacion": est["nombre"],
                    "activo": est["activo"],
                    "red": "lora_diy",
                    "station_id": sid,
                }
            )
    return out


def listar_estaciones_diy() -> dict[str, Any]:
    estaciones = _estaciones_diy_catalogo()
    lecturas = [x for x in _load() if x.get("fuente") == "lora_diy"]
    por_est: dict[str, int] = {}
    for L in lecturas:
        eid = L.get("estacion_id") or ""
        por_est[eid] = por_est.get(eid, 0) + 1
    for e in estaciones:
        e["lecturas_recientes"] = por_est.get(e["id"], 0)
    return {
        "red": "lora_diy_aconcagua",
        "nodos": len(estaciones),
        "estaciones": estaciones,
        "docs": "hardware/red-estaciones-diy-aconcagua/README.md",
    }


def simular_lora_diy(station_id: str | None = None) -> int:
    """Genera una ronda de lecturas fuente=lora_diy para el panel Vue."""
    catalogo = _estaciones_diy_catalogo()
    if station_id:
        catalogo = [e for e in catalogo if e["station_id"] == station_id or e["id"] == station_id]
    items: list[dict[str, Any]] = []
    for est in catalogo:
        eid = est["id"]
        sid = est["station_id"]
        specs = [
            ("temperatura", "temp_c", 14 + random.uniform(-2, 6)),
            ("humedad", "rh", 60 + random.uniform(-15, 20)),
            ("presion", "pressure_hpa", 1012 + random.uniform(-4, 4)),
        ]
        ts = datetime.now(timezone.utc).isoformat()
        for tipo, suf, valor in specs:
            if tipo == "humedad":
                valor = max(0.0, min(100.0, valor))
            items.append(
                {
                    "id": str(uuid.uuid4()),
                    "sensor_id": f"lora-{sid}-{suf}",
                    "tipo": tipo,
                    "estacion_id": eid,
                    "valor": round(float(valor), 2),
                    "unidad": _unidad(tipo),
                    "fuente": "lora_diy",
                    "timestamp": ts,
                    "station_id": sid,
                }
            )
    if items:
        _save(items)
    return len(items)


def _generar_lectura(sensor_id: str, tipo: str, estacion_id: str) -> dict[str, Any]:
    base = {
        "temperatura": 18 + random.uniform(-3, 8),
        "humedad": 55 + random.uniform(-15, 25),
        "viento_velocidad": random.uniform(0, 35),
        "precipitacion": random.choice([0, 0, 0, 0.2, 1.5]),
        "presion": 1013 + random.uniform(-5, 5),
    }
    valor = round(float(base.get(tipo.replace("viento_velocidad", "viento_velocidad"), 20)), 2)
    if tipo == "humedad":
        valor = max(0, min(100, valor))
    return {
        "id": str(uuid.uuid4()),
        "sensor_id": sensor_id,
        "tipo": tipo,
        "estacion_id": estacion_id,
        "valor": valor,
        "unidad": _unidad(tipo),
        "fuente": "iot_simulado",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _unidad(tipo: str) -> str:
    return {
        "temperatura": "°C",
        "humedad": "%",
        "viento_velocidad": "km/h",
        "precipitacion": "mm",
        "presion": "hPa",
    }.get(tipo, "")


def listar_lecturas(
    estacion_id: str | None = None,
    limite: int = 50,
) -> list[dict[str, Any]]:
    items = _load()
    if estacion_id:
        items = [x for x in items if x.get("estacion_id") == estacion_id]
    return sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)[:limite]


def registrar_lectura(payload: dict[str, Any]) -> dict[str, Any]:
    sensor_id = payload.get("sensor_id") or "iot-manual"
    tipo = payload.get("tipo", "temperatura")
    estacion_id = payload.get("estacion_id", "quillota")
    valor = float(payload.get("valor", 0))
    item = {
        "id": str(uuid.uuid4()),
        "sensor_id": sensor_id,
        "tipo": tipo,
        "estacion_id": estacion_id,
        "valor": valor,
        "unidad": payload.get("unidad") or _unidad(tipo),
        "fuente": payload.get("fuente", "iot_api"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _save([item])
    return item


def refrescar_simulacion() -> int:
    items = _load()
    try:
        from api_rest.integracion.iot_bridge import generar_lecturas_modulo03

        lecturas = generar_lecturas_modulo03(6)
        if lecturas:
            _save(lecturas)
            return len(lecturas)
    except ImportError:
        pass
    nuevas = []
    for s in listar_sensores():
        if s.get("activo"):
            nuevas.append(_generar_lectura(s["id"], s["tipo"], s["estacion_id"]))
    if nuevas:
        _save(nuevas)
    return len(listar_sensores())
