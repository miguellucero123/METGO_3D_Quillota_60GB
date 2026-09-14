#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke pasos Izaje Mar (prod o local) — checklist automatizable.

  1) health/live
  2) security-config (Turnstile)
  3) validate-registro (ventora_mar + puerto)
  4) puerto/pronostico
  5) register-v2  — solo si SMOKE_DO_REGISTER=1 y token Turnstile
  6–8) verify/login/access — requieren register + mail (o METGO_EMAIL_DEV)

Uso:
  python scripts/smoke_izaje_mar_flujo.py
  python scripts/smoke_izaje_mar_flujo.py --base https://metgo-api.onrender.com/api

Registro real (crea usuario):
  $env:SMOKE_DO_REGISTER="1"
  $env:METGO_SMOKE_EMAIL="tu@correo.com"
  $env:METGO_SMOKE_TURNSTILE_TOKEN="<token del widget en el navegador>"
  python scripts/smoke_izaje_mar_flujo.py --register
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_API = "https://metgo-api.onrender.com/api"
PRODUCTO = "ventora_mar"
PUERTO = "ventanas_muelle"


def _req(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 90,
) -> tuple[int, Any]:
    hdrs = {
        "Accept": "application/json",
        "X-Metgo-Product": PRODUCTO,
        **(headers or {}),
    }
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
        self.ok += cond
        self.fail += not cond
        print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
        return cond

    def skipped(self, label: str, reason: str) -> None:
        self.skip += 1
        print(f"  [SKIP] {label} — {reason}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Smoke flujo Izaje Mar")
    p.add_argument("--base", default=os.getenv("METGO_API_BASE", DEFAULT_API))
    p.add_argument("--puerto", default=os.getenv("METGO_SMOKE_PUERTO", PUERTO))
    p.add_argument("--register", action="store_true", help="Intentar register-v2 real")
    args = p.parse_args()
    api = args.base.rstrip("/")
    if not api.endswith("/api"):
        api = f"{api}/api"

    r = Runner()
    print(f"Smoke Izaje Mar · {api}")
    print(f"producto={PRODUCTO} puerto={args.puerto}")
    print()

    print("== 1) Liveness ==")
    code, live = _req("GET", f"{api}/health/live", timeout=45)
    r.check(
        "GET /health/live",
        code == 200 and isinstance(live, dict) and live.get("live") is True,
        f"HTTP {code}",
    )

    print("== 2) Turnstile / security-config ==")
    code, cfg = _req("GET", f"{api}/public/security-config")
    ts = (cfg or {}).get("turnstile") if isinstance(cfg, dict) else {}
    r.check(
        "GET /public/security-config",
        code == 200 and isinstance(cfg, dict),
        f"HTTP {code}",
    )
    r.check(
        "Turnstile enabled+required",
        bool(ts.get("enabled")) and bool(ts.get("required")) and bool(ts.get("site_key")),
        f"enabled={ts.get('enabled')} required={ts.get('required')} key={bool(ts.get('site_key'))}",
    )

    print("== 3) validate-registro ==")
    stamp = int(time.time())
    email = (os.getenv("METGO_SMOKE_EMAIL") or f"smoke.izaje.{stamp}@example.com").strip()
    payload = {
        "email": email,
        "password": "SeguraPuerto1",
        "password_confirm": "SeguraPuerto1",
        "nombres": "Camila",
        "apellidos": "Rojas",
        "telefono": "+56987654321",
        "razon_social": "Terminal Smoke SpA",
        "rut": "76.063.552-9",
        "sitio": "spati",
        "producto": PRODUCTO,
        "spa": PRODUCTO,
        "faena": args.puerto,
        "consentimientos": {
            "almacenamiento_datos": True,
            "tos": True,
            "privacy": True,
            "veracidad": True,
        },
    }
    code, val = _req("POST", f"{api}/auth/validate-registro", body=payload)
    r.check(
        "POST /auth/validate-registro",
        code == 200 and isinstance(val, dict) and val.get("ok") is True,
        f"HTTP {code} errors={(val or {}).get('errors') if isinstance(val, dict) else val}",
    )

    print("== 4) puerto/pronostico ==")
    code, puerto = _req(
        "GET",
        f"{api}/public/spati/{args.puerto}/puerto/pronostico",
        timeout=120,
    )
    fuente = (puerto or {}).get("fuente") if isinstance(puerto, dict) else None
    n = len((puerto or {}).get("hourly_states") or []) if isinstance(puerto, dict) else 0
    # API vieja puede no mandar `fuente`; con hours>0 el endpoint está vivo.
    r.check(
        f"GET /public/spati/{args.puerto}/puerto/pronostico",
        code == 200 and n > 0,
        f"HTTP {code} fuente={fuente or 'n/d (API pre-P1)'} hours={n}",
    )

    print("== 5–8) register → verify → login → access ==")
    do_reg = args.register and os.getenv("SMOKE_DO_REGISTER") == "1"
    token_ts = (os.getenv("METGO_SMOKE_TURNSTILE_TOKEN") or "").strip()
    if not do_reg:
        r.skipped(
            "register-v2 + verify + login",
            "usa --register con SMOKE_DO_REGISTER=1 y METGO_SMOKE_TURNSTILE_TOKEN "
            "(token del widget en el navegador; no se puede automatizar sin browser)",
        )
    elif not token_ts:
        r.skipped(
            "register-v2",
            "faltá METGO_SMOKE_TURNSTILE_TOKEN (completa Turnstile en /registro y copia el token)",
        )
    else:
        payload["turnstile_token"] = token_ts
        code, reg = _req("POST", f"{api}/auth/register-v2", body=payload, timeout=120)
        ok_reg = code == 201 and isinstance(reg, dict)
        r.check("POST /auth/register-v2", ok_reg, f"HTTP {code} {reg if not ok_reg else ''}")
        if ok_reg:
            verify_url = reg.get("verify_url") or ""
            r.check(
                "verify_url apunta a Izaje Mar",
                "ventora-izaje-mar" in verify_url or "/p/" in verify_url or "/verificar" in verify_url,
                verify_url[:80] or "(vacío — revisar METGO_VENTORA_MAR_PUBLIC_URL)",
            )
            vtok = reg.get("verify_token")
            if vtok:
                code, _ = _req("GET", f"{api}/auth/verify-email?token={vtok}")
                r.check("GET /auth/verify-email", code == 200, f"HTTP {code}")
            else:
                r.skipped(
                    "verify-email automático",
                    "prod no devuelve verify_token; abre el link del correo manualmente",
                )
                print("       Luego login manual y /auth/access.")
                vtok = None

            if vtok or os.getenv("METGO_SMOKE_ALREADY_VERIFIED") == "1":
                code, login = _req(
                    "POST",
                    f"{api}/auth/login",
                    body={
                        "username": email,
                        "password": payload["password"],
                        "sitio": "spati",
                        "faena": args.puerto,
                    },
                )
                if r.check("POST /auth/login", code == 200, f"HTTP {code}"):
                    jwt = (login or {}).get("access_token")
                    code, acc = _req(
                        "GET",
                        f"{api}/auth/access?sitio=spati&faena={args.puerto}&tab=panel",
                        headers={"Authorization": f"Bearer {jwt}"},
                    )
                    r.check(
                        "GET /auth/access?tab=panel",
                        code == 200 and (acc or {}).get("tab_allowed") is True,
                        f"HTTP {code}",
                    )

    print()
    print("== RESUMEN ==")
    print(f"  OK={r.ok}  FAIL={r.fail}  SKIP={r.skip}")
    if r.fail:
        print("  Hay fallos: revisá Render env / deploy / contratos.")
        return 1
    print("  Pasos API OK. Falta humana si SKIP register: completar Turnstile + mail en el navegador.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
