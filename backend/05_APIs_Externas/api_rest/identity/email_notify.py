#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envío de email de verificación (SMTP opcional; si no, solo log)."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Any


def smtp_configurado() -> bool:
    """HOST + FROM mínimos para identidad (USER/PASSWORD opcionales según proveedor)."""
    return bool(
        (os.getenv("METGO_SMTP_HOST") or "").strip()
        and (os.getenv("METGO_SMTP_FROM") or "").strip()
    )


def enviar_verificacion(
    *,
    to_email: str,
    verify_url: str,
    sitio: str,
    faena: str | None = None,
    trial_days: int = 15,
) -> dict[str, Any]:
    """Intenta SMTP. Sin host/from → mode=log (dev). Incluye copy de piloto."""
    sitio_l = (sitio or "metgo").strip().lower()
    faena_l = (faena or "").strip().lower()
    where = f"{sitio_l}" + (f"/{faena_l}" if faena_l else "")
    days = max(1, int(trial_days or 15))

    subject = f"METGO · active su piloto {days} días ({where})"
    body = (
        f"Bienvenido a METGO ({where}).\n\n"
        f"Su cuenta fue creada con el plan Piloto: {days} días gratis.\n"
        "Al vencer el piloto sin un plan pago, el acceso queda bloqueado automáticamente.\n\n"
        "Paso obligatorio — verifique su correo abriendo este enlace "
        "(válido ~48 h; sin esto no podrá iniciar sesión):\n\n"
        f"{verify_url}\n\n"
        "Luego entre a la app con el mismo email y contraseña.\n\n"
        "Nota: el RUT de empresa se valida por formato y dígito verificador chileno; "
        "no es una verificación automática ante el SII.\n\n"
        "Si no solicitó este registro, ignore este mensaje.\n"
    )
    if not smtp_configurado():
        print(f"[identity-email] (log) to={to_email} url={verify_url}")
        return {
            "mode": "log",
            "sent": False,
            "to": to_email,
            "reason": "smtp_not_configured",
        }

    host = os.getenv("METGO_SMTP_HOST", "").strip()
    port = int(os.getenv("METGO_SMTP_PORT", "587"))
    user = (os.getenv("METGO_SMTP_USER") or "").strip()
    password = os.getenv("METGO_SMTP_PASSWORD") or ""
    from_addr = os.getenv("METGO_SMTP_FROM", "").strip()
    use_tls = (os.getenv("METGO_SMTP_TLS") or "1") == "1"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(body)

    try:
        smtp_timeout = int(os.getenv("METGO_SMTP_TIMEOUT", "20"))
        with smtplib.SMTP(host, port, timeout=smtp_timeout) as smtp:
            if use_tls:
                smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
        return {"mode": "smtp", "sent": True, "to": to_email}
    except Exception as exc:
        print(f"[identity-email] SMTP error: {exc}")
        return {"mode": "smtp", "sent": False, "error": str(exc), "to": to_email}
