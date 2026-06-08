#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alertas configurables por usuario (persistencia JSON — Fase 2.2)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api_rest.services import ESTACIONES_PRINCIPALES, resumen_meteo, slug_a_nombre

_VARIABLES = ("temperatura_max", "temperatura_min", "precipitacion", "viento", "humedad")
_OPERADORES = (">", "<", ">=", "<=")


def _store_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            if not (p / "backend").is_dir():
                gd = p / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "alertas_config.json"
    return Path("alertas_config.json")


def _load() -> list[dict[str, Any]]:
    path = _store_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    path = _store_path()
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def listar_por_usuario(usuario: str) -> list[dict[str, Any]]:
    return [a for a in _load() if a.get("usuario_id") == usuario]


def crear(usuario: str, payload: dict[str, Any]) -> dict[str, Any]:
    estacion = (payload.get("estacion") or "quillota").lower().replace(" ", "_")
    variable = payload.get("variable", "temperatura_max")
    if variable not in _VARIABLES:
        raise ValueError(f"variable invalida: {variable}")
    operador = payload.get("operador", ">")
    if operador not in _OPERADORES:
        raise ValueError(f"operador invalido: {operador}")
    item = {
        "id": str(uuid.uuid4()),
        "usuario_id": usuario,
        "estacion": estacion,
        "variable": variable,
        "umbral": float(payload.get("umbral", 0)),
        "operador": operador,
        "activa": bool(payload.get("activa", True)),
        "creado_en": datetime.now(timezone.utc).isoformat(),
    }
    items = _load()
    items.append(item)
    _save(items)
    return item


def actualizar(usuario: str, alerta_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    items = _load()
    for i, a in enumerate(items):
        if a.get("id") == alerta_id and a.get("usuario_id") == usuario:
            if "estacion" in payload:
                a["estacion"] = str(payload["estacion"]).lower()
            if "variable" in payload:
                if payload["variable"] not in _VARIABLES:
                    raise ValueError("variable invalida")
                a["variable"] = payload["variable"]
            if "umbral" in payload:
                a["umbral"] = float(payload["umbral"])
            if "operador" in payload:
                if payload["operador"] not in _OPERADORES:
                    raise ValueError("operador invalido")
                a["operador"] = payload["operador"]
            if "activa" in payload:
                a["activa"] = bool(payload["activa"])
            items[i] = a
            _save(items)
            return a
    return None


def eliminar(usuario: str, alerta_id: str) -> bool:
    items = _load()
    nuevo = [a for a in items if not (a.get("id") == alerta_id and a.get("usuario_id") == usuario)]
    if len(nuevo) == len(items):
        return False
    _save(nuevo)
    return True


def _evaluar(valor: float, umbral: float, operador: str) -> bool:
    if operador == ">":
        return valor > umbral
    if operador == "<":
        return valor < umbral
    if operador == ">=":
        return valor >= umbral
    if operador == "<=":
        return valor <= umbral
    return False


def evaluar_configuradas(estacion_id: str | None = None) -> list[dict[str, Any]]:
    """Dispara alertas según reglas guardadas y pronóstico actual."""
    disparadas: list[dict[str, Any]] = []
    configs = [c for c in _load() if c.get("activa")]
    if estacion_id:
        configs = [c for c in configs if c.get("estacion") == estacion_id]

    for cfg in configs:
        eid = cfg.get("estacion", "quillota")
        resumen = resumen_meteo(eid)
        if not resumen:
            continue
        var = cfg["variable"]
        valor = float(resumen.get(var, 0))
        if _evaluar(valor, float(cfg["umbral"]), cfg["operador"]):
            nombre = resumen.get("estacion", slug_a_nombre(eid))
            disparadas.append(
                {
                    "id": cfg["id"],
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": (
                        f"{nombre}: {var} {cfg['operador']} {cfg['umbral']} "
                        f"(valor actual {valor})"
                    ),
                    "configurada": True,
                    "usuario_id": cfg.get("usuario_id"),
                }
            )
    return disparadas


def generar_alertas_combinadas(estacion_id: str | None = None) -> list[dict[str, Any]]:
    """Alertas automáticas + reglas configuradas, con cadencia mínima de 6 horas."""
    from api_rest import services
    from api_rest.integracion.alertas_store import filtrar_por_cadencia

    base = services.generar_alertas(estacion_id)
    custom = evaluar_configuradas(estacion_id)
    seen = {a.get("mensaje") for a in base}
    for a in custom:
        if a["mensaje"] not in seen:
            base.append(a)
    return filtrar_por_cadencia(base)


def notificar_alertas_criticas(alertas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Opcional: envía email si METGO_ALERTAS_EMAIL_AUTO=1 y hay alertas warning+."""
    if os.environ.get("METGO_ALERTAS_EMAIL_AUTO", "").lower() not in ("1", "true", "yes"):
        return []
    from api_rest.integracion import notificaciones

    enviados = []
    for a in alertas:
        r = notificaciones.enviar_alerta_critica(a)
        if r:
            enviados.append(r)
    return enviados
