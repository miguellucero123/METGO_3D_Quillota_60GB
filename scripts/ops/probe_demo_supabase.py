#!/usr/bin/env python3
"""Probe / seed demo via PostgREST (requires grants already applied)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def rest(method: str, path: str, body: dict | None = None, prefer: str = "") -> tuple[int, str]:
    url = (os.environ.get("SUPABASE_URL") or "").rstrip("/") + path
    key = os.environ.get("SUPABASE_KEY") or ""
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main() -> int:
    load_dotenv()
    host = (os.environ.get("SUPABASE_URL") or "").split("//")[-1][:48]
    print(f"host={host or 'missing'}")
    code, body = rest("GET", "/rest/v1/usuarios_app?select=id,email_norm&limit=3")
    print(f"SELECT usuarios_app -> {code}")
    print(body[:400])
    if code == 200:
        code2, body2 = rest(
            "GET",
            "/rest/v1/usuarios_app?email_norm=eq.demo@ventora.demo&select=email_norm,faena,status",
        )
        print(f"demo row -> {code2} {body2[:300]}")
        return 0
    print(
        "\nFalta aplicar grants en SQL Editor:\n"
        "  supabase/migrations/20260731020000_preview_grants_demo_fijo.sql\n"
        "Ver docs/roadmap/FIX_LOGIN_DEMO_SUPABASE.md"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
