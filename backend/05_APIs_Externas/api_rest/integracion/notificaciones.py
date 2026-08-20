#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuración y envío multicanal (módulo 07) — Fase 9."""

from __future__ import annotations

import json
import os
import smtplib
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

EMAIL_CORPORATIVO_DEFAULT = "miguel.lucero@metgo3d.com"


def _config_path() -> Path:
    for p in Path(__file__).resolve().parents:
        runtime = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
        if (p / "metgo_paths.py").exists():
            runtime.mkdir(parents=True, exist_ok=True)
            return runtime / "notificaciones_config.json"
    return Path("notificaciones_config.json")


def _outbox_path() -> Path:
    return _config_path().parent / "notificaciones_outbox.jsonl"


def _email_destino_default() -> str:
    return os.environ.get("METGO_NOTIFY_EMAIL", "").strip() or EMAIL_CORPORATIVO_DEFAULT


def _smtp_configurado() -> bool:
    return bool(
        os.environ.get("METGO_SMTP_HOST")
        and os.environ.get("METGO_SMTP_USER")
        and os.environ.get("METGO_SMTP_PASSWORD")
    )


def _webhook_url(cfg: dict[str, Any] | None = None) -> str:
    cfg = cfg or leer_config()
    return (cfg.get("webhook_url") or os.environ.get("METGO_WEBHOOK_URL", "")).strip()


def leer_config() -> dict[str, Any]:
    destino = _email_destino_default()
    base = {
        "email_habilitado": True,
        "email_destino": destino,
        "email_corporativo": EMAIL_CORPORATIVO_DEFAULT,
        "webhook_url": os.environ.get("METGO_WEBHOOK_URL", ""),
        "webhook_habilitado": True,
        "sms_habilitado": False,
        "canal_defecto": "email",
        "smtp_configurado": _smtp_configurado(),
        "alertas_auto_email": True,
    }
    path = _config_path()
    if path.is_file():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
            base.update(stored)
        except (json.JSONDecodeError, OSError):
            pass
    if not base.get("email_destino"):
        base["email_destino"] = destino
    base["webhook_activo"] = bool(_webhook_url(base))
    return base


def guardar_config(data: dict[str, Any]) -> dict[str, Any]:
    path = _config_path()
    actual = leer_config()
    actual.update(
        {
            k: v
            for k, v in data.items()
            if k
            in (
                "email_habilitado",
                "email_destino",
                "webhook_url",
                "webhook_habilitado",
                "sms_habilitado",
                "canal_defecto",
                "alertas_auto_email",
            )
        }
    )
    path.write_text(json.dumps(actual, ensure_ascii=False, indent=2), encoding="utf-8")
    return leer_config()


def _encolar_outbox(destino: str, asunto: str, cuerpo: str, estado: str = "pendiente_smtp") -> dict[str, Any]:
    entry = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "destino": destino,
        "asunto": asunto,
        "cuerpo": cuerpo,
        "estado": estado,
    }
    try:
        with _outbox_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        return {"ok": False, "error": str(e)}
    return entry


def listar_outbox(limite: int = 30) -> list[dict[str, Any]]:
    path = _outbox_path()
    if not path.is_file():
        return []
    lineas = path.read_text(encoding="utf-8").strip().splitlines()
    items: list[dict[str, Any]] = []
    for line in lineas[-limite:]:
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(items))


def estado_canales() -> dict[str, Any]:
    cfg = leer_config()
    pendientes = sum(1 for x in listar_outbox(200) if x.get("estado") == "pendiente_smtp")
    return {
        "smtp_configurado": _smtp_configurado(),
        "webhook_activo": bool(_webhook_url(cfg)) and cfg.get("webhook_habilitado", True),
        "email_habilitado": cfg.get("email_habilitado", True),
        "email_destino": cfg.get("email_destino"),
        "alertas_auto_email": cfg.get("alertas_auto_email", True),
        "outbox_pendientes": pendientes,
        "outbox_total_recientes": len(listar_outbox(50)),
        "canal_recomendado": "webhook" if _webhook_url(cfg) else ("smtp" if _smtp_configurado() else "outbox"),
    }


def _enviar_webhook(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "METGO3D-API/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return {"ok": True, "canal": "webhook", "status": resp.status, "url": url.split("?")[0]}


def _enviar_smtp(destino: str, asunto: str, cuerpo: str, cuerpo_html: str | None = None) -> dict[str, Any]:
    host = os.environ.get("METGO_SMTP_HOST", "smtp.zoho.com")
    port = int(os.environ.get("METGO_SMTP_PORT", "587"))
    user = os.environ.get("METGO_SMTP_USER", "")
    password = os.environ.get("METGO_SMTP_PASSWORD", "")
    remitente = os.environ.get("METGO_SMTP_FROM", user or "noreply@metgo3d.com")
    use_tls = os.environ.get("METGO_SMTP_TLS", "1") != "0"

    msg = MIMEMultipart("alternative")
    msg["From"] = remitente
    msg["To"] = destino
    msg["Subject"] = asunto
    
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))
    if cuerpo_html:
        msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    smtp_timeout = int(os.environ.get("METGO_SMTP_TIMEOUT", "20"))
    with smtplib.SMTP(host, port, timeout=smtp_timeout) as server:
        if use_tls:
            server.starttls()
        if user and password:
            server.login(user, password)
        server.sendmail(remitente, [destino], msg.as_string())

    return {"ok": True, "canal": "email_smtp", "destino": destino, "remitente": remitente}


def _enviar_email_canal(to_addr: str, asunto: str, cuerpo: str, mensaje: str, cuerpo_html: str | None = None) -> dict[str, Any]:
    if _smtp_configurado():
        try:
            return {**_enviar_smtp(to_addr, asunto, cuerpo, cuerpo_html), "mensaje": mensaje}
        except Exception as e:
            entry = _encolar_outbox(to_addr, asunto, cuerpo)
            return {
                "ok": False,
                "canal": "email_error",
                "destino": to_addr,
                "error": str(e),
                "outbox_id": entry.get("id"),
                "nota": "Guardado en outbox para reintento",
            }

    entry = _encolar_outbox(to_addr, asunto, cuerpo)
    return {
        "ok": True,
        "canal": "email_outbox",
        "destino": to_addr,
        "mensaje": mensaje,
        "outbox_id": entry.get("id"),
        "nota": "SMTP no configurado; ver METGO_SMTP_* en .env",
    }


def enviar_notificacion(
    mensaje: str,
    asunto: str = "METGO 3D — Notificación",
    destino: str | None = None,
    *,
    destinos: list[str] | None = None,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    """Webhook (si URL) + email (SMTP u outbox). No requiere SMTP para operar.

    - destino / destinos: emails (si hay varios, se envía a cada uno).
    - webhook_url: override del webhook global (p. ej. por faena SPATI M9).
    """
    cfg = leer_config()
    emails: list[str] = []
    if destinos:
        emails = [str(e).strip() for e in destinos if str(e).strip()]
    elif destino and str(destino).strip():
        emails = [str(destino).strip()]
    elif cfg.get("email_destino"):
        emails = [str(cfg.get("email_destino")).strip()]
    else:
        default = _email_destino_default()
        if default:
            emails = [default]

    cuerpo = (
        f"{mensaje}\n\n"
        f"— METGO 3D · Valle de Aconcagua\n"
        f"{datetime.now(timezone.utc).isoformat()}\n"
    )
    
    color = "#10b981" # Verde Normal
    asunto_upper = asunto.upper()
    if "ROJO" in asunto_upper or "CRITICAL" in asunto_upper or "CRÍTICO" in asunto_upper or "ALTA" in asunto_upper:
        color = "#ef4444" # Rojo Peligro
    elif "AMARILLO" in asunto_upper or "WARNING" in asunto_upper:
        color = "#f59e0b" # Amarillo Precaución
    elif "AZUL" in asunto_upper or "INFO" in asunto_upper:
        color = "#3b82f6" # Azul Información
        
    cuerpo_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
          <div style="background-color: {color}; padding: 20px; color: white; text-align: center;">
            <h2 style="margin: 0; font-size: 20px;">{asunto}</h2>
          </div>
          <div style="padding: 30px; font-size: 16px; line-height: 1.6; color: #374151;">
            {mensaje.replace(chr(10), '<br>')}
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="font-size: 13px; color: #6b7280; text-align: center; margin: 0;">
              <strong>METGO 3D</strong> · Plataforma de Inteligencia Climática<br>
              Valle de Aconcagua, Chile
            </p>
          </div>
        </div>
      </body>
    </html>
    """

    canales: list[dict[str, Any]] = []
    errores: list[dict[str, Any]] = []

    url = (webhook_url or "").strip() or _webhook_url(cfg)
    if url and (webhook_url or cfg.get("webhook_habilitado", True)):
        try:
            canales.append(
                _enviar_webhook(
                    url,
                    {
                        "asunto": asunto,
                        "mensaje": mensaje,
                        "destino": emails[0] if emails else None,
                        "destinos": emails,
                        "app": "METGO3D",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
            )
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            errores.append({"canal": "webhook", "error": str(e)})

    if cfg.get("email_habilitado", True):
        for to_addr in emails:
            canales.append(_enviar_email_canal(to_addr, asunto, cuerpo, mensaje, cuerpo_html))

    ok = any(c.get("ok") for c in canales)
    return {
        "ok": ok,
        "canales": canales,
        "errores": errores,
        "mensaje": mensaje,
        "canal": canales[0].get("canal") if len(canales) == 1 else "multicanal",
    }


def enviar_email(
    mensaje: str,
    asunto: str = "METGO 3D — Notificación",
    destino: str | None = None,
) -> dict[str, Any]:
    return enviar_notificacion(mensaje, asunto=asunto, destino=destino)


def enviar_prueba(mensaje: str = "Prueba METGO integración") -> dict[str, Any]:
    return enviar_notificacion(mensaje, asunto="METGO 3D — Prueba de notificación")


def reintentar_outbox(max_items: int = 10) -> dict[str, Any]:
    """Reintenta envío SMTP de entradas pendiente_smtp (admin / cron)."""
    if not _smtp_configurado():
        return {"ok": False, "error": "SMTP no configurado", "enviados": 0}

    path = _outbox_path()
    if not path.is_file():
        return {"ok": True, "enviados": 0, "fallidos": 0}

    lineas = path.read_text(encoding="utf-8").strip().splitlines()
    nuevas: list[str] = []
    enviados = 0
    fallidos = 0
    procesados = 0

    for line in lineas:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            nuevas.append(line)
            continue

        if entry.get("estado") == "pendiente_smtp" and procesados < max_items:
            procesados += 1
            try:
                _enviar_smtp(
                    entry.get("destino", _email_destino_default()),
                    entry.get("asunto", "METGO"),
                    entry.get("cuerpo", ""),
                )
                entry["estado"] = "enviado_smtp"
                entry["enviado_en"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                enviados += 1
            except Exception as e:
                entry["estado"] = "error_smtp"
                entry["error"] = str(e)
                fallidos += 1

        nuevas.append(json.dumps(entry, ensure_ascii=False))

    path.write_text("\n".join(nuevas) + ("\n" if nuevas else ""), encoding="utf-8")
    return {"ok": True, "enviados": enviados, "fallidos": fallidos, "procesados": procesados}


def enviar_alerta_critica(alerta: dict[str, Any]) -> dict[str, Any] | None:
    cfg = leer_config()
    if not cfg.get("alertas_auto_email", True):
        return None
    nivel = (alerta.get("nivel") or "").lower()
    if nivel not in ("warning", "critical", "critico", "alta"):
        return None
    texto = alerta.get("mensaje") or str(alerta)
    estacion = alerta.get("estacion_id", "")
    asunto = f"METGO 3D — Alerta {nivel.upper()}"
    if estacion:
        asunto += f" · {estacion}"
    return enviar_notificacion(texto, asunto=asunto)
