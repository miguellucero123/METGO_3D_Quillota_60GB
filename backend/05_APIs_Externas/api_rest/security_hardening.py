#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Endurecimiento seguridad: rate limit in-memory + Cloudflare Turnstile."""

from __future__ import annotations

import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from typing import Any

_lock = threading.Lock()
# key -> deque de timestamps
_buckets: dict[str, deque[float]] = defaultdict(deque)


def rate_limit_enabled() -> bool:
    return (os.getenv("METGO_RATE_LIMIT_ENABLED") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def client_ip() -> str:
    from flask import request

    fwd = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    return fwd or (request.remote_addr or "unknown")


def check_rate_limit(
    bucket: str,
    *,
    limit: int,
    window_s: int,
    key: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    """True si permitido. Respuesta incluye retry_after_s si bloqueado."""
    if not rate_limit_enabled():
        return True, {"limited": False}
    k = f"{bucket}:{(key or client_ip()).strip().lower()}"
    now = time.time()
    with _lock:
        q = _buckets[k]
        while q and q[0] <= now - window_s:
            q.popleft()
        if len(q) >= limit:
            retry = max(1, int(window_s - (now - q[0])) + 1)
            return False, {
                "limited": True,
                "retry_after_s": retry,
                "limit": limit,
                "window_s": window_s,
            }
        q.append(now)
    return True, {"limited": False, "limit": limit, "window_s": window_s}


def reset_rate_limits() -> None:
    """Solo tests."""
    with _lock:
        _buckets.clear()


def turnstile_configured() -> bool:
    return bool((os.getenv("METGO_TURNSTILE_SECRET") or "").strip())


def turnstile_site_key() -> str:
    return (os.getenv("METGO_TURNSTILE_SITE_KEY") or "").strip()


def turnstile_required() -> bool:
    """Obligatorio si hay secret y (REQUIRED=1 o producción)."""
    if not turnstile_configured():
        return False
    forced = (os.getenv("METGO_TURNSTILE_REQUIRED") or "").strip().lower()
    if forced in ("1", "true", "yes", "on"):
        return True
    if forced in ("0", "false", "no", "off"):
        return False
    env = (os.getenv("METGO_ENV") or "").strip().lower()
    return env == "production" or bool(os.getenv("RENDER"))


def verify_turnstile(token: str | None, *, remoteip: str | None = None) -> tuple[bool, str]:
    """Valida token Turnstile. Sin secret configurado → OK (dev)."""
    if not turnstile_configured():
        return True, "skipped"
    tok = (token or "").strip()
    if not tok:
        if turnstile_required():
            return False, "Captcha requerido"
        return True, "skipped_empty"
    secret = (os.getenv("METGO_TURNSTILE_SECRET") or "").strip()
    data = urllib.parse.urlencode(
        {
            "secret": secret,
            "response": tok,
            **({"remoteip": remoteip} if remoteip else {}),
        }
    ).encode()
    req = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            import json

            body = json.loads(resp.read().decode("utf-8", errors="replace"))
        if body.get("success"):
            return True, "ok"
        return False, "Captcha inválido"
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        # Fail-closed solo si required; si no, no bloquear registro por outage CF
        if turnstile_required():
            return False, f"No se pudo validar captcha: {exc}"
        return True, "skipped_error"


def security_public_config() -> dict[str, Any]:
    return {
        "turnstile": {
            "enabled": turnstile_configured() and bool(turnstile_site_key()),
            "required": turnstile_required(),
            "site_key": turnstile_site_key() or None,
        },
        "rate_limit_enabled": rate_limit_enabled(),
        "email_verification_required": (
            os.getenv("METGO_REQUIRE_EMAIL_VERIFY", "1").strip().lower()
            not in ("0", "false", "no", "off")
        ),
    }


def rate_limit_response(meta: dict[str, Any]):
    from flask import jsonify

    retry = int(meta.get("retry_after_s") or 60)
    resp = jsonify(
        {
            "error": "Demasiados intentos. Espere e intente de nuevo.",
            "code": "rate_limited",
            "retry_after_s": retry,
        }
    )
    resp.status_code = 429
    resp.headers["Retry-After"] = str(retry)
    return resp
