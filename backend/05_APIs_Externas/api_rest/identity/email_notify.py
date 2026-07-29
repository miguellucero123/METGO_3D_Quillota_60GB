#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envío de email de verificación (SMTP opcional; si no, solo log)."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Any


def smtp_configurado() -> bool:
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
) -> dict[str, Any]:
    """Intenta SMTP. Sin host → mode=log (dev)."""
    subject = f"METGO · verificar email ({sitio}" + (f"/{faena}" if faena else "") + ")"
    body = (
        f"Confirme su cuenta METGO:\n\n{verify_url}\n\n"
        "Si no solicitó este registro, ignore este mensaje.\n"
    )
    if not smtp_configurado():
        print(f"[identity-email] (log) to={to_email} url={verify_url}")
        return {"mode": "log", "sent": False, "to": to_email}

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
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            if use_tls:
                smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
        return {"mode": "smtp", "sent": True, "to": to_email}
    except Exception as exc:
        print(f"[identity-email] SMTP error: {exc}")
        return {"mode": "smtp", "sent": False, "error": str(exc), "to": to_email}
