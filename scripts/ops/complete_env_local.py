#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Completa .env local: genera secretos fuertes; no imprime valores."""
from __future__ import annotations

import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"

BAD_PREFIXES = (
    "cambiar_",
    "generar-",
    "tu_",
    "xxxx",
    "secreto_",
    "password",
    "PLACEHOLDER",
)


def is_bad(v: str | None) -> bool:
    if v is None or v == "":
        return True
    return v.startswith(BAD_PREFIXES) or v == "*"


def parse(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def set_key(text: str, key: str, value: str) -> str:
    if re.search(rf"(?m)^{re.escape(key)}=", text):
        return re.sub(rf"(?m)^{re.escape(key)}=.*$", f"{key}={value}", text)
    return text.rstrip() + f"\n{key}={value}\n"


def main() -> None:
    text = ENV_PATH.read_text(encoding="utf-8", errors="replace") if ENV_PATH.is_file() else ""
    cur = parse(text)

    gen = {
        "METGO_JWT_SECRET": secrets.token_urlsafe(48),
        "METGO_PII_KEK": secrets.token_hex(32),
        "CRON_SECRET": secrets.token_urlsafe(32),
        "METGO_PASSWORD_ADMIN": secrets.token_urlsafe(18),
        "METGO_PASSWORD_USER": secrets.token_urlsafe(18),
        "METGO_PASSWORD_METGO": secrets.token_urlsafe(18),
        "METGO_PASSWORD_AGRONOMO": secrets.token_urlsafe(18),
        "METGO_PASSWORD_OPERADOR": secrets.token_urlsafe(18),
        "METGO_PASSWORD_LECTOR": secrets.token_urlsafe(18),
        "METGO_PASSWORD_COPIAPO": secrets.token_urlsafe(18),
        "METGO_PASSWORD_MANTOS": secrets.token_urlsafe(18),
        "METGO_PASSWORD_PAINE": secrets.token_urlsafe(18),
    }

    cors = ",".join(
        [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:5178",
            "http://localhost:5178",
            "https://metgo-quillota.pages.dev",
            "https://metgo-spati.pages.dev",
            "https://ventora-izaje-mar.pages.dev",
            "https://metgo-copiapo.pages.dev",
            "https://metgo-mantos.pages.dev",
            "https://metgo-paine.pages.dev",
            "https://metgo3d.com",
            "https://www.metgo3d.com",
        ]
    )

    defaults = {
        "METGO_JWT_EXPIRATION_SECONDS": "3600",
        "METGO_API_AUTH_REQUIRED": "1",
        "METGO_API_PORT": "8080",
        "METGO_ALLOW_SELF_REGISTER": "0",
        "METGO_ENV": "development",
        "METGO_IDENTITY_STORE": "supabase",
        "METGO_EMAIL_DEV": "0",
        "METGO_SPATI_PUBLIC_URL": "https://metgo-spati.pages.dev",
        "METGO_QUILLOTA_PUBLIC_URL": "https://metgo-quillota.pages.dev",
        "METGO_COPIAPO_PUBLIC_URL": "https://metgo-copiapo.pages.dev",
        "METGO_MANTOS_PUBLIC_URL": "https://metgo-mantos.pages.dev",
        "METGO_PAINE_PUBLIC_URL": "https://metgo-paine.pages.dev",
        "METGO_SMTP_HOST": "smtp.zoho.com",
        "METGO_SMTP_PORT": "587",
        "METGO_SMTP_TLS": "1",
        "METGO_SMTP_USER": "miguel.lucero@metgo3d.com",
        "METGO_SMTP_FROM": "miguel.lucero@metgo3d.com",
        "METGO_NOTIFY_EMAIL": "miguel.lucero@metgo3d.com",
        "METGO_OPENMETEO_FETCH_MODE": "ciclo",
        "METGO_OPENMETEO_CACHE_TTL": "3600",
        "METGO_CORS_ORIGINS": cors,
        "CLOUDFLARE_API_TOKEN": "",
        "CLOUDFLARE_ACCOUNT_ID": "",
        "GITHUB_PAT": "",
        "STRIPE_SECRET_KEY": "",
        "METGO_TURNSTILE_SECRET": "",
        "METGO_TURNSTILE_SITE_KEY": "",
        "METGO_SMTP_PASSWORD": "",
        "METGO_OPENMETEO_API_KEY": "",
    }

    changed: list[str] = []

    for key, val in gen.items():
        if is_bad(cur.get(key)):
            text = set_key(text, key, val)
            changed.append(key)

    if is_bad(cur.get("METGO_CORS_ORIGINS")) or cur.get("METGO_CORS_ORIGINS") == "*":
        text = set_key(text, "METGO_CORS_ORIGINS", cors)
        changed.append("METGO_CORS_ORIGINS")

    for key, default in defaults.items():
        if key in gen or key == "METGO_CORS_ORIGINS":
            continue
        existing = cur.get(key)
        if existing is None:
            text = set_key(text, key, default)
            changed.append(f"+{key}")
        elif key.endswith(("_TOKEN", "_KEY", "_SECRET", "_PASSWORD", "_PAT", "_ID", "API_KEY")):
            # externos: solo agregar línea vacía si falta; no tocar si ya hay valor
            if existing is None:
                text = set_key(text, key, default)
                changed.append(f"+{key}")
        elif is_bad(existing) and default:
            text = set_key(text, key, default)
            changed.append(key)

    # Re-ensure external keys exist as empty lines
    cur2 = parse(text)
    for key in (
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
        "GITHUB_PAT",
        "STRIPE_SECRET_KEY",
        "METGO_TURNSTILE_SECRET",
        "METGO_TURNSTILE_SITE_KEY",
        "METGO_SMTP_PASSWORD",
        "METGO_OPENMETEO_API_KEY",
        "CRON_SECRET",
        "METGO_PII_KEK",
    ):
        if key not in cur2:
            text = set_key(text, key, gen.get(key, defaults.get(key, "")))
            changed.append(f"+{key}")

    ENV_PATH.write_text(text, encoding="utf-8")

    final = parse(text)
    empty = sorted(k for k, v in final.items() if not v)
    placeholders = sorted(k for k, v in final.items() if v and is_bad(v))
    print(f"OK wrote {ENV_PATH}")
    print(f"changed={len(changed)}")
    print("empty_need_manual:", ",".join(empty) if empty else "(none)")
    print("still_placeholder:", ",".join(placeholders) if placeholders else "(none)")


if __name__ == "__main__":
    main()
