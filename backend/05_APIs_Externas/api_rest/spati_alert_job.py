#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M9 — cron alertas SPATI: transiciones de nivel → notificaciones (webhook/email/outbox)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api_rest.spati.alert_system import NIVEL_NOMBRE


def _state_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d / "spati_alert_state.json"
    return Path("spati_alert_state.json")


def _leer_estado() -> dict[str, Any]:
    path = _state_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_estado(data: dict[str, Any]) -> None:
    path = _state_path()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _nivel_de_pronostico(data: dict[str, Any]) -> tuple[int, str | None]:
    nivel = int(data.get("nivel_maximo") or 0)
    vt = None
    serie = data.get("serie") or []
    if serie:
        # Primer paso con nivel máximo (horizonte cercano crítico)
        for step in serie[:8]:
            if int(step.get("nivel_alerta") or 0) >= nivel:
                vt = step.get("valid_time")
                break
        if not vt:
            vt = serie[0].get("valid_time")
    return nivel, vt


def evaluar_y_notificar(
    sitio_id: str,
    *,
    forzar: bool = False,
    pronostico: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa run_spati (o pronóstico mock) y notifica si sube el nivel ≥ umbral."""
    from api_rest.spati.umbrales_service import alertas_destino

    sid = (sitio_id or "").strip().lower()
    dest = alertas_destino(sid)
    nivel_min = int(dest.get("nivel_minimo") or 2)

    if pronostico is None:
        from api_rest.spati import run_spati

        pronostico = run_spati(sid)
    if not isinstance(pronostico, dict) or pronostico.get("error"):
        return {
            "sitio_id": sid,
            "ok": False,
            "error": (pronostico or {}).get("error") or "sin_pronostico",
            "notificado": False,
        }

    nivel, valid_time = _nivel_de_pronostico(pronostico)
    estado = _leer_estado()
    prev = estado.get(sid) or {}
    prev_nivel = int(prev.get("ultimo_nivel") or 0)

    subir = nivel > prev_nivel and nivel >= nivel_min
    crit = nivel >= 3 and (forzar or nivel != prev_nivel)
    debe = forzar or subir or crit

    result: dict[str, Any] = {
        "sitio_id": sid,
        "ok": True,
        "nivel": nivel,
        "nivel_nombre": NIVEL_NOMBRE.get(nivel, str(nivel)),
        "nivel_previo": prev_nivel,
        "nivel_minimo": nivel_min,
        "valid_time": valid_time,
        "notificado": False,
        "motivo": "sin_cambio" if not debe else "transicion",
    }

    if not debe:
        estado[sid] = {
            "ultimo_nivel": nivel,
            "ultimo_valid_time": valid_time,
            "ultimo_notificado_en": prev.get("ultimo_notificado_en"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        _guardar_estado(estado)
        _persist_supabase(sid, nivel, valid_time, prev.get("ultimo_notificado_en"))
        return result

    nombre = (pronostico.get("sitio") or {}).get("nombre") or sid
    asunto = f"METGO SPATI — Izaje {NIVEL_NOMBRE.get(nivel, nivel)} · {nombre}"
    mensaje = (
        f"Sitio {nombre} ({sid}): nivel {prev_nivel}→{nivel} "
        f"({NIVEL_NOMBRE.get(nivel)}). valid_time={valid_time}. "
        f"Máximo horizonte: {pronostico.get('nivel_maximo')}."
    )

    notif_ok = False
    try:
        from api_rest.integracion import notificaciones

        emails = dest.get("emails") or []
        destino = emails[0] if emails else None
        r = notificaciones.enviar_notificacion(
            mensaje=mensaje,
            asunto=asunto,
            destino=destino,
        )
        result["envio"] = r
        notif_ok = True
    except Exception as exc:
        result["envio_error"] = str(exc)

    try:
        from api_rest.integracion import alertas_store

        nivel_txt = "critical" if nivel >= 3 else "warning" if nivel >= 2 else "info"
        alertas_store.registrar_alertas(
            [
                {
                    "nivel": nivel_txt,
                    "estacion_id": sid,
                    "mensaje": mensaje,
                    "origen": "spati_m9",
                }
            ]
        )
    except Exception as exc:
        result["alertas_store_error"] = str(exc)

    now = datetime.now(timezone.utc).isoformat()
    estado[sid] = {
        "ultimo_nivel": nivel,
        "ultimo_valid_time": valid_time,
        "ultimo_notificado_en": now,
        "updated_at": now,
    }
    _guardar_estado(estado)
    _persist_supabase(sid, nivel, valid_time, now)

    result["notificado"] = True
    result["motivo"] = "forzado" if forzar else "transicion"
    result["notif_ok"] = notif_ok
    return result


def _persist_supabase(
    sitio_id: str,
    nivel: int,
    valid_time: str | None,
    notificado_en: str | None,
) -> None:
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if not client:
            return
        client.table("spati_alert_state").upsert(
            {
                "sitio_slug": sitio_id,
                "ultimo_nivel": nivel,
                "ultimo_valid_time": valid_time,
                "ultimo_notificado_en": notificado_en,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="sitio_slug",
        ).execute()
    except Exception:
        pass


def evaluar_sitios(
    sitios: list[str] | None = None,
    *,
    forzar: bool = False,
) -> dict[str, Any]:
    from api_rest.spati import listar_sitios

    if sitios:
        ids = [s.strip().lower() for s in sitios if s]
    else:
        ids = [
            str(s.get("sitio_id") or s.get("id") or s.get("slug") or "")
            for s in listar_sitios()
        ]
        ids = [i for i in ids if i]
    detalle = []
    n_ok = 0
    n_notif = 0
    for sid in ids:
        try:
            r = evaluar_y_notificar(sid, forzar=forzar)
            detalle.append(r)
            if r.get("ok"):
                n_ok += 1
            if r.get("notificado"):
                n_notif += 1
        except Exception as exc:
            detalle.append({"sitio_id": sid, "ok": False, "error": str(exc), "notificado": False})
    return {
        "fase": "M9",
        "sitios": len(ids),
        "ok": n_ok,
        "notificados": n_notif,
        "detalle": detalle,
    }
