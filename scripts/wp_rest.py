"""METGO WordPress.com REST helpers. Creds: env WP_USER + WP_APP_PASSWORD."""
from __future__ import annotations

import base64
import json
import os
import socket
import sys
import urllib.error
import urllib.request

# Intentar cargar .env automáticamente
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
try:
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
except Exception:
    pass

socket.setdefaulttimeout(45)
BASE = (os.environ.get("WP_URL") or "https://metgo3d.com").rstrip("/") + "/wp-json"


def _auth_header() -> dict[str, str]:
    u = os.environ.get("WP_USER") or ""
    p = os.environ.get("WP_APP_PASSWORD") or ""
    if not u or not p:
        raise SystemExit("Define WP_USER y WP_APP_PASSWORD en el entorno o .env")
    token = base64.b64encode(f"{u}:{p}".encode()).decode()
    return {
        "Authorization": "Basic " + token,
        "User-Agent": "METGO-WP-Script/1.0",
        "Content-Type": "application/json",
    }


def request(method: str, path: str, body: dict | None = None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=_auth_header(), method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        raise SystemExit(f"{method} {path} -> {e.code}: {err[:500]}") from e


def main() -> None:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "list").lower()
    if cmd == "list":
        pages = request("GET", "/wp/v2/pages?per_page=50&context=edit&status=any")
        posts = request("GET", "/wp/v2/posts?per_page=50&context=edit&status=any")
        print("PAGES")
        for x in pages or []:
            print(f"  {x['id']}\t{x['status']}\t{x['title'].get('raw')}")
        print("POSTS")
        for x in posts or []:
            print(f"  {x['id']}\t{x['status']}\t{x['title'].get('raw')}\t{x.get('link')}")
        return
    if cmd == "trash-post":
        pid = sys.argv[2]
        out = request("DELETE", f"/wp/v2/posts/{pid}")
        print("trashed post", pid, "status=", (out or {}).get("status"))
        return
    if cmd == "trash-page":
        pid = sys.argv[2]
        out = request("DELETE", f"/wp/v2/pages/{pid}")
        print("trashed page", pid, "status=", (out or {}).get("status"))
        return
    if cmd == "draft-page":
        pid = sys.argv[2]
        out = request("POST", f"/wp/v2/pages/{pid}", {"status": "draft"})
        print("draft page", pid, "status=", (out or {}).get("status"))
        return
    raise SystemExit(f"Comando desconocido: {cmd}")


if __name__ == "__main__":
    main()
