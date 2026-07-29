#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke M7 minería multi-faena — CSV/PDF/status/demo.

Uso:
  python scripts/smoke_mineria_m7.py
  python scripts/smoke_mineria_m7.py --base http://127.0.0.1:8080
  python scripts/smoke_mineria_m7.py --base https://metgo-api.onrender.com --faena paipote --demo
  python scripts/smoke_mineria_m7.py --base https://metgo-api.onrender.com --token $env:CRON_SECRET --demo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _get(url: str, timeout: int = 90) -> tuple[int, bytes, str]:
    req = Request(url, headers={"Accept": "*/*"})
    with urlopen(req, timeout=timeout) as resp:
        ctype = resp.headers.get("Content-Type") or ""
        return resp.status, resp.read(), ctype


def _post(url: str, timeout: int = 120) -> tuple[int, bytes, str]:
    req = Request(url, method="POST", headers={"Accept": "application/json"}, data=b"")
    with urlopen(req, timeout=timeout) as resp:
        ctype = resp.headers.get("Content-Type") or ""
        return resp.status, resp.read(), ctype


def _ok(label: str, cond: bool, detail: str = "") -> bool:
    mark = "OK" if cond else "FAIL"
    extra = f" — {detail}" if detail else ""
    print(f"  [{mark}] {label}{extra}")
    return cond


def run(base: str, faena: str, demo: bool, token: str | None) -> int:
    base = base.rstrip("/")
    api = f"{base}/api" if not base.endswith("/api") else base
    print(f"Smoke M7 · {api} · faena={faena}")
    fails = 0

    try:
        st, body, ctype = _get(f"{api}/public/operaciones/faenas")
        fails += not _ok("GET faenas", st == 200 and b"faenas" in body, f"HTTP {st}")
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"  [FAIL] GET faenas — {exc}")
        return 1

    checks: list[tuple[str, str, Callable[[int, bytes, str], bool]]] = [
        (
            f"informe CSV",
            f"{api}/public/operaciones/faena/{faena}/informe?formato=csv",
            lambda st, b, c: st == 200 and ("csv" in c or b.startswith(b"\xef\xbb\xbf") or b"fecha_hora" in b),
        ),
        (
            f"informe PDF",
            f"{api}/public/operaciones/faena/{faena}/informe?formato=pdf",
            lambda st, b, c: st == 200 and (b.startswith(b"%PDF") or "pdf" in c),
        ),
        (
            f"observado-status",
            f"{api}/public/operaciones/faena/{faena}/observado-status",
            lambda st, b, c: st == 200 and b"estado_mvo" in b,
        ),
        (
            f"estaciones-area",
            f"{api}/public/operaciones/faena/{faena}/estaciones-area",
            lambda st, b, c: st == 200 and b"estaciones_area" in b,
        ),
        (
            f"umbrales-operativos",
            f"{api}/public/operaciones/umbrales-operativos",
            lambda st, b, c: st == 200 and b"izaje" in b,
        ),
    ]

    for label, url, pred in checks:
        try:
            st, body, ctype = _get(url)
            if not _ok(label, pred(st, body, ctype.lower()), f"HTTP {st} · {ctype[:40]}"):
                fails += 1
        except Exception as exc:
            print(f"  [FAIL] {label} — {exc}")
            fails += 1

    if demo:
        q = f"faena={faena}&dias=5"
        if token:
            q += f"&token={token}"
        url = f"{api}/cron/faena/demo-observado?{q}"
        try:
            st, body, ctype = _post(url)
            ok = st == 200 and b'"ok"' in body
            if not _ok("POST demo-observado", ok, f"HTTP {st}"):
                fails += 1
            else:
                st2, body2, _ = _get(
                    f"{api}/public/operaciones/faena/{faena}/modelo-vs-observado?dias=7"
                )
                fails += not _ok(
                    "MVO tras demo",
                    st2 == 200 and (b"ok" in body2 or b"parcial" in body2 or b"sin_observado" in body2),
                    body2[:120].decode("utf-8", errors="replace"),
                )
        except HTTPError as exc:
            detail = exc.read()[:200] if exc.fp else b""
            print(f"  [FAIL] POST demo-observado — HTTP {exc.code} {detail!r}")
            fails += 1
        except Exception as exc:
            print(f"  [FAIL] POST demo-observado — {exc}")
            fails += 1

    print("RESULTADO:", "PASS" if fails == 0 else f"{fails} fallos")
    return 0 if fails == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Smoke minería multi-faena M7")
    p.add_argument(
        "--base",
        default="http://127.0.0.1:8080",
        help="Base API (con o sin /api)",
    )
    p.add_argument("--faena", default="paipote")
    p.add_argument("--demo", action="store_true", help="Ejecutar demo-observado")
    p.add_argument("--token", default=None, help="CRON_SECRET si aplica")
    args = p.parse_args(argv)
    return run(args.base, args.faena, args.demo, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
