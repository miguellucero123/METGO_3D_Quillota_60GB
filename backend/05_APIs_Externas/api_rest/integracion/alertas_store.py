#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Historial de alertas (módulo 07) + umbrales módulo 01."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# Umbrales alineados con sistema_alertas_automaticas (01)
UMBRALES_01 = {
    "temperatura_maxima": 35.0,
    "temperatura_minima": -2.0,
    "precipitacion_intensa": 20.0,
    "viento_fuerte": 40.0,
    "humedad_alta": 90.0,
    "humedad_baja": 30.0,
}

# Frecuencia operativa: una misma alerta relevante no se re-emite dentro de 6 horas
CADENCIA_ALERTAS = timedelta(hours=6)


def _path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "alertas_historial.json"
    return Path("alertas_historial.json")


_ALERTAS_SUPABASE_WARNED = False


def _load() -> list[dict[str, Any]]:
    global _ALERTAS_SUPABASE_WARNED
    try:
        from api_rest.integracion.supabase_store import get_supabase_client
        client = get_supabase_client()
        if client:
            res = client.table("alertas").select("*").order("registrado_en", desc=True).limit(500).execute()
            return res.data or []
    except Exception as e:
        # Tabla aún no migrada en Supabase (PGRST205): usar historial local, sin spam.
        msg = str(e)
        if not _ALERTAS_SUPABASE_WARNED:
            _ALERTAS_SUPABASE_WARNED = True
            if "PGRST205" in msg or "alertas" in msg.lower():
                print(
                    "Alertas Supabase: tabla 'public.alertas' no existe; "
                    "usando historial local (aviso único)."
                )
            else:
                print(f"Error cargando alertas de Supabase: {e}")
    # Fallback archivo local
    path = _path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _alerta_clave(alerta: dict[str, Any]) -> tuple[str, str]:
    return (
        str(alerta.get("estacion_id") or alerta.get("estacion") or "quillota"),
        str(alerta.get("mensaje") or ""),
    )


def _ya_emitida_en_ventana(alerta: dict[str, Any], ventana: timedelta = CADENCIA_ALERTAS) -> bool:
    """Evita repetir la misma alerta durante la ventana operativa."""
    key_estacion, key_mensaje = _alerta_clave(alerta)
    ahora = datetime.now(timezone.utc)
    for item in _load():
        if _alerta_clave(item) != (key_estacion, key_mensaje):
            continue
        ts = _parse_ts(item.get("registrado_en"))
        if ts and ahora - ts < ventana:
            return True
    return False


def filtrar_por_cadencia(alertas: list[dict[str, Any]], ventana: timedelta = CADENCIA_ALERTAS) -> list[dict[str, Any]]:
    """Retorna solo alertas nuevas respecto a la última emisión de la misma señal."""
    salida: list[dict[str, Any]] = []
    for alerta in alertas:
        if not _ya_emitida_en_ventana(alerta, ventana):
            salida.append(alerta)
    return salida


def evaluar_umbrales_01(resumen: dict[str, Any], estacion_id: str) -> list[dict[str, Any]]:
    alertas = []
    if not resumen:
        return alertas
    t_max = float(resumen.get("temperatura_max", 0))
    t_min = float(resumen.get("temperatura_min", 0))
    precip = float(resumen.get("precipitacion", 0))
    viento = float(resumen.get("viento", 0))
    humedad = float(resumen.get("humedad", 0))

    checks = [
        (t_max >= UMBRALES_01["temperatura_maxima"], "warning", f"Temperatura máxima extrema ({t_max}°C)"),
        (t_min <= UMBRALES_01["temperatura_minima"], "warning", f"Riesgo helada ({t_min}°C)"),
        (precip >= UMBRALES_01["precipitacion_intensa"], "warning", f"Precipitación intensa ({precip} mm)"),
        (viento >= UMBRALES_01["viento_fuerte"], "warning", f"Viento fuerte ({viento} km/h)"),
        (humedad >= UMBRALES_01["humedad_alta"], "info", f"Humedad muy alta ({humedad}%)"),
        (humedad <= UMBRALES_01["humedad_baja"], "info", f"Humedad baja ({humedad}%)"),
    ]
    for ok, nivel, msg in checks:
        if ok:
            alertas.append(
                {
                    "nivel": nivel,
                    "estacion_id": estacion_id,
                    "mensaje": msg,
                    "origen": "modulo_01_umbrales",
                }
            )
    return alertas


def registrar_alertas(alertas: list[dict[str, Any]]) -> None:
    if not alertas:
        return
    items = _load()
    ts = datetime.now(timezone.utc).isoformat()
    try:
        from api_rest.integracion import notificaciones
    except ImportError:
        notificaciones = None
    nuevas_alertas = []
    for a in filtrar_por_cadencia(alertas):
        if a.get("nivel") == "info" and "normales" in (a.get("mensaje") or "").lower():
            continue
        alerta = {**a, "registrado_en": ts}
        nuevas_alertas.append(alerta)
        if notificaciones:
            try:
                notificaciones.enviar_alerta_critica(a)
            except Exception:
                pass
                
    if nuevas_alertas:
        try:
            from api_rest.integracion.supabase_store import get_supabase_client
            client = get_supabase_client()
            if client:
                client.table("alertas").insert(nuevas_alertas).execute()
                
            # ENVIAR EMAILS CON EMAIL_SERVICE (Fase 10 / Producción)
            try:
                from api_rest.domain_services.email_service import email_service
                if email_service.is_configured() and client:
                    # Obtener usuarios con plan activo que pertenezcan a este sitio/faena
                    res = client.table("users").select("email").eq("status", "active").execute()
                    if res.data:
                        emails = [u["email"] for u in res.data if u.get("email")]
                        for a in nuevas_alertas:
                            if a.get("nivel") in ["warning", "critical", "alta"]:
                                for email in emails:
                                    email_service.send_alert_email(
                                        user_email=email,
                                        alert_level=a.get("nivel", "warning"),
                                        alert_message=a.get("mensaje", ""),
                                        station_id=a.get("estacion_id", "METGO")
                                    )
            except Exception as e_email:
                print(f"Error enviando alertas por email_service: {e_email}")

        except Exception as e:
            print(f"Error guardando alertas en Supabase: {e}")


def listar_historial(estacion_id: str | None = None, limite: int = 50) -> list[dict[str, Any]]:
    items = _load()
    if estacion_id:
        items = [x for x in items if x.get("estacion_id") == estacion_id]
    return sorted(items, key=lambda x: x.get("registrado_en", ""), reverse=True)[:limite]
