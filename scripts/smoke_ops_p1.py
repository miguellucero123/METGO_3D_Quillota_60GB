#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke ops METGO — revisión automática de endpoints (GET/POST/PUT).

Contratos reales (no placeholders):
  GET  /api/health
  GET  /api/public/planes?sitio=
  GET  /api/public/estaciones?sitio=
  GET  /api/public/spati/{faena}/umbrales
  PUT  /api/public/spati/{faena}/umbrales   (Bearer o X-Cron-Token)
  POST /api/auth/login                      body: username, password, sitio, faena?
  GET  /api/auth/me                         Bearer
  GET  /api/auth/cuenta                     Bearer
  GET  /api/auth/access                     Bearer
  POST /api/auth/validate-registro          dry-run registro
  POST /api/auth/register-v2                opcional (crea usuario real)
  POST /api/cron/spati/alertas              CRON_SECRET
  POST /api/cron/notificaciones/outbox-retry  CRON_SECRET

Uso (PowerShell):
  $env:CRON_SECRET = "..."          # opcional: umbrales PUT + cron
  $env:METGO_SMOKE_USER = "admin"   # o email identity
  $env:METGO_SMOKE_PASS = "..."
  $env:METGO_SMOKE_SITIO = "spati"
  $env:METGO_SMOKE_FAENA = "escondida"
  python scripts/smoke_ops_p1.py

  # Solo públicos (sin secretos):
  python scripts/smoke_ops_p1.py --public-only

  # Dry-run validate-registro Paine:
  python scripts/smoke_ops_p1.py --validate-registro --sitio paine

  # Registro real (crea org; requiere mail real + SMOKE_DO_REGISTER=1):
  $env:SMOKE_DO_REGISTER = "1"
  $env:METGO_SMOKE_EMAIL = "tu@correo.com"
  python scripts/smoke_ops_p1.py --register --sitio paine
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


DEFAULT_API = "https://metgo-api.onrender.com/api"


def _req(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 90,
) -> tuple[int, Any]:
    hdrs = {"Accept": "application/json", **(headers or {})}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                payload = json.loads(raw.decode("utf-8") or "null")
            except json.JSONDecodeError:
                payload = raw.decode("utf-8", errors="replace")[:400]
            return resp.status, payload
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw.decode("utf-8") or "null")
        except json.JSONDecodeError:
            payload = raw.decode("utf-8", errors="replace")[:400]
        return e.code, payload
    except Exception as e:
        return 0, {"error": str(e)}


class Runner:
    def __init__(self) -> None:
        self.ok = 0
        self.fail = 0
        self.skip = 0

    def check(self, label: str, cond: bool, detail: str = "") -> bool:
        mark = "OK" if cond else "FAIL"
        if cond:
            self.ok += 1
        else:
            self.fail += 1
        extra = f" — {detail}" if detail else ""
        print(f"  [{mark}] {label}{extra}")
        return cond

    def skipped(self, label: str, reason: str) -> None:
        self.skip += 1
        print(f"  [SKIP] {label} — {reason}")


def main() -> int:
    # Force UTF-8 on Windows consoles
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Smoke ops METGO (endpoints reales)")
    p.add_argument("--base", default=os.getenv("METGO_API_BASE", DEFAULT_API))
    p.add_argument("--public-only", action="store_true")
    p.add_argument("--faena", default=os.getenv("METGO_SMOKE_FAENA", "escondida"))
    p.add_argument("--sitio", default=os.getenv("METGO_SMOKE_SITIO", "spati"))
    p.add_argument("--validate-registro", action="store_true")
    p.add_argument("--register", action="store_true", help="POST register-v2 (crea usuario)")
    p.add_argument(
        "--alerta-email",
        default=os.getenv("METGO_SMOKE_ALERT_EMAIL", "miguel.lucero@metgo3d.com"),
    )
    args = p.parse_args()

    api = args.base.rstrip("/")
    if api.endswith("/api"):
        pass
    elif "/api" in api:
        pass
    else:
        api = f"{api}/api"

    r = Runner()
    print(f"Smoke ops METGO · {api}")
    print(f"sitio={args.sitio} faena={args.faena}")
    print()

    # ---- Públicos ----
    print("== GET públicos ==")
    code, health = _req("GET", f"{api}/health", timeout=60)
    r.check("GET /health", code == 200 and isinstance(health, dict) and health.get("status") == "ok", f"HTTP {code}")
    if isinstance(health, dict):
        s5 = health.get("s5_ops") or {}
        print(f"       smtp={s5.get('smtp_configurado')} pendiente={s5.get('pendiente')} version={health.get('version')}")

    for sitio in ("spati", "quillota", "paine", "copiapo", "mantos_blancos"):
        code, data = _req("GET", f"{api}/public/planes?sitio={sitio}")
        n = len((data or {}).get("planes") or []) if isinstance(data, dict) else 0
        r.check(f"GET /public/planes?sitio={sitio}", code == 200 and n > 0, f"HTTP {code} planes={n}")

    code, umb = _req("GET", f"{api}/public/spati/{args.faena}/umbrales")
    r.check(
        f"GET /public/spati/{args.faena}/umbrales",
        code == 200 and isinstance(umb, dict) and "umbrales" in (umb or {}),
        f"HTTP {code}",
    )

    code, est = _req("GET", f"{api}/public/estaciones?sitio=paine")
    n_est = 0
    if isinstance(est, dict):
        n_est = len(est.get("estaciones") or est.get("items") or est.get("data") or [])
        if not n_est and isinstance(est.get("estaciones"), list):
            n_est = len(est["estaciones"])
    # algunas APIs devuelven lista directa
    if isinstance(est, list):
        n_est = len(est)
    r.check("GET /public/estaciones?sitio=paine", code == 200, f"HTTP {code} n={n_est}")

    # ---- Auth / umbrales (credenciales o CRON) ----
    print()
    print("== Auth + umbrales (si hay secretos en env) ==")
    user = (os.getenv("METGO_SMOKE_USER") or "").strip()
    password = (os.getenv("METGO_SMOKE_PASS") or os.getenv("METGO_PASSWORD_ADMIN") or "").strip()
    cron = (os.getenv("CRON_SECRET") or "").strip()
    token = ""

    if args.public_only:
        r.skipped("login/umbrales PUT", "--public-only")
    elif user and password:
        code, login = _req(
            "POST",
            f"{api}/auth/login",
            body={
                "username": user,
                "password": password,
                "sitio": args.sitio,
                **({"faena": args.faena} if args.sitio == "spati" else {}),
            },
            timeout=90,
        )
        if r.check("POST /auth/login", code == 200 and isinstance(login, dict), f"HTTP {code}"):
            token = str(login.get("access_token") or login.get("token") or "")
            r.check("JWT access_token presente", bool(token), f"keys={list(login)[:8]}")
        else:
            print(f"       body={login}")
    elif cron:
        r.skipped("POST /auth/login", "sin METGO_SMOKE_USER/PASS; se usará CRON_SECRET para PUT")
    else:
        r.skipped(
            "login + umbrales autenticados",
            "definí METGO_SMOKE_USER+METGO_SMOKE_PASS o CRON_SECRET",
        )

    if token:
        hdr = {"Authorization": f"Bearer {token}"}
        code, me = _req("GET", f"{api}/auth/me", headers=hdr)
        r.check("GET /auth/me", code == 200, f"HTTP {code}")
        code, cuenta = _req(
            "GET",
            f"{api}/auth/cuenta" + (f"?faena={args.faena}" if args.sitio == "spati" else ""),
            headers=hdr,
        )
        r.check("GET /auth/cuenta", code == 200, f"HTTP {code}")
        code, access = _req(
            "GET",
            f"{api}/auth/access?sitio={args.sitio}"
            + (f"&faena={args.faena}" if args.faena else ""),
            headers=hdr,
        )
        r.check("GET /auth/access", code in (200, 403), f"HTTP {code}")

        code, put = _req(
            "PUT",
            f"{api}/public/spati/{args.faena}/umbrales",
            headers=hdr,
            body={
                "alertas": {
                    "emails": args.alerta_email,
                    "webhook_url": None,
                    "nivel_minimo": 2,
                }
            },
        )
        r.check("PUT umbrales alertas (Bearer)", code == 200, f"HTTP {code} {put if code != 200 else ''}")
        if code == 200:
            code, umb2 = _req(
                "GET",
                f"{api}/public/spati/{args.faena}/umbrales",
                headers=hdr,
            )
            emails = []
            if isinstance(umb2, dict):
                emails = (umb2.get("alertas") or {}).get("emails") or []
            r.check(
                "GET umbrales (detalle Bearer) emails",
                code == 200 and args.alerta_email.split(",")[0].strip() in str(emails),
                f"emails={emails}",
            )
    elif cron and not args.public_only:
        hdr = {"X-Cron-Token": cron}
        code, put = _req(
            "PUT",
            f"{api}/public/spati/{args.faena}/umbrales",
            headers=hdr,
            body={
                "alertas": {
                    "emails": args.alerta_email,
                    "nivel_minimo": 2,
                }
            },
        )
        # PUT puede exigir Bearer si CRON_SECRET está set en Render — token= query también
        if code == 401:
            code, put = _req(
                "PUT",
                f"{api}/public/spati/{args.faena}/umbrales?token={cron}",
                body={"alertas": {"emails": args.alerta_email, "nivel_minimo": 2}},
            )
        r.check("PUT umbrales alertas (CRON)", code == 200, f"HTTP {code}")

        code, alertas = _req(
            "POST",
            f"{api}/cron/spati/alertas?sitio={args.faena}",
            headers={"X-Cron-Token": cron},
            timeout=120,
        )
        r.check("POST /cron/spati/alertas", code == 200, f"HTTP {code}")

        code, outbox = _req(
            "POST",
            f"{api}/cron/notificaciones/outbox-retry?max=5",
            headers={"X-Cron-Token": cron},
            timeout=90,
        )
        r.check(
            "POST /cron/notificaciones/outbox-retry",
            code in (200, 404),
            f"HTTP {code} (404=API sin redeploy aún)",
        )

    # ---- Registro dry-run ----
    print()
    print("== Registro (validate / opcional register-v2) ==")
    if args.validate_registro or args.register or not args.public_only:
        # RUT 76.111.111-6 es DV válido (usado en smoke previo)
        payload = {
            "sitio": "paine" if args.sitio == "spati" and args.validate_registro else args.sitio,
            "email": os.getenv("METGO_SMOKE_EMAIL", "ops-smoke-validate@metgo3d.com"),
            "password": "TestPass12Ab",
            "rut": "76.111.111-6",
            "razon_social": "Smoke Validate Limitada",
            "nombres": "Ops",
            "apellidos": "Validate",
            "consentimientos": {
                "almacenamiento_datos": True,
                "tos": True,
                "privacy": True,
                "veracidad": True,
            },
        }
        if payload["sitio"] == "spati":
            payload["faena"] = args.faena
        if args.sitio != "spati" and not args.validate_registro:
            payload["sitio"] = args.sitio

        # Por defecto validate contra el sitio pedido
        if not args.validate_registro and not args.register:
            payload["sitio"] = args.sitio if args.sitio != "spati" else "quillota"
            if args.sitio == "spati":
                payload["sitio"] = "spati"
                payload["faena"] = args.faena

        code, val = _req("POST", f"{api}/auth/validate-registro", body=payload)
        r.check(
            "POST /auth/validate-registro",
            code == 200 and isinstance(val, dict) and val.get("ok") is True,
            f"HTTP {code} errors={ (val or {}).get('errors') if isinstance(val, dict) else val }",
        )

        if args.register:
            if os.getenv("SMOKE_DO_REGISTER") != "1":
                r.skipped(
                    "POST /auth/register-v2",
                    "seteá SMOKE_DO_REGISTER=1 para crear usuario real",
                )
            else:
                email = (os.getenv("METGO_SMOKE_EMAIL") or "").strip()
                if not email or email.endswith("@metgo3d.com") and "validate" in email:
                    r.skipped("register-v2", "METGO_SMOKE_EMAIL debe ser un correo real tuyo")
                else:
                    payload["email"] = email
                    payload["password"] = os.getenv("METGO_SMOKE_PASS", "TestPass12Ab")
                    code, reg = _req("POST", f"{api}/auth/register-v2", body=payload, timeout=120)
                    mail = (reg or {}).get("email") if isinstance(reg, dict) else None
                    r.check(
                        "POST /auth/register-v2",
                        code in (201, 200),
                        f"HTTP {code} email={mail}",
                    )
                    print(
                        "       [INFO] Revisá el inbox y abrí /verificar?token=… "
                        "Luego: METGO_SMOKE_USER=<email> python scripts/smoke_ops_p1.py"
                    )
    else:
        r.skipped("validate-registro", "--public-only")

    print()
    print("== RESUMEN ==")
    print(f"  OK={r.ok}  FAIL={r.fail}  SKIP={r.skip}")
    if r.fail:
        print("  Hay fallos: revisá contratos o secretos en env.")
        return 1
    print("  Smoke sin fallos. Pasos que siguen siendo humanos: abrir link del mail (si registraste).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
