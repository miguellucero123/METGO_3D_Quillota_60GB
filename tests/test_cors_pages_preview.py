#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CORS: previews Cloudflare Pages / Netlify."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "backend" / "05_APIs_Externas"
if str(API) not in sys.path:
    sys.path.insert(0, str(API))


def test_expand_cors_preview_pages_dev():
    from api_rest.app import expand_cors_origins

    origins = expand_cors_origins(
        ["https://metgo-copiapo.pages.dev", "https://metgo3d.netlify.app"]
    )
    preview = "https://8705dcc4.metgo-copiapo.pages.dev"
    prod = "https://metgo-copiapo.pages.dev"
    bad = "https://evil.example.com"

    def allowed(origin: str) -> bool:
        for o in origins:
            if hasattr(o, "match"):
                if o.match(origin):
                    return True
            elif o == origin:
                return True
        return False

    assert allowed(preview)
    assert allowed(prod)
    assert allowed("https://metgo3d.netlify.app")
    assert not allowed(bad)


def test_cors_preflight_preview_origin():
    from api_rest.app import create_app

    c = create_app().test_client()
    origin = "https://8705dcc4.metgo-copiapo.pages.dev"
    r = c.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("Access-Control-Allow-Origin") == origin
