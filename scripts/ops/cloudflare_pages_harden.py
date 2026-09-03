#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica política de seguridad Pages desde Git → Cloudflare API.

Fuente: config/cloudflare/pages_security.json
Secrets: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID

Uso:
  python scripts/ops/cloudflare_pages_harden.py            # aplicar
  python scripts/ops/cloudflare_pages_harden.py --check    # solo verificar (exit 1 si drift)
  python scripts/ops/cloudflare_pages_harden.py --dry-run  # mostrar PATCH sin llamar
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "cloudflare" / "pages_security.json"
API = "https://api.cloudflare.com/client/v4"


def _load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _creds() -> tuple[str, str]:
    token = (os.getenv("CLOUDFLARE_API_TOKEN") or "").strip()
    account = (os.getenv("CLOUDFLARE_ACCOUNT_ID") or "").strip()
    if not token or not account:
        print(
            "Faltan CLOUDFLARE_API_TOKEN y/o CLOUDFLARE_ACCOUNT_ID "
            "(GitHub Secrets o .env local).",
            file=sys.stderr,
        )
        sys.exit(2)
    return token, account


def _request(
    method: str,
    url: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"success": False, "errors": [{"message": raw or str(e)}]}
        payload["_http_status"] = e.code
        return payload
    return payload


def _desired(policy: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    defaults = policy.get("defaults") or {}
    out: dict[str, Any] = {
        "preview_deployment_setting": project.get(
            "preview_deployment_setting",
            defaults.get("preview_deployment_setting", "none"),
        ),
    }
    branch = project.get("production_branch", defaults.get("production_branch"))
    if branch:
        out["production_branch"] = branch
    if out["preview_deployment_setting"] == "custom":
        includes = project.get("preview_branch_includes") or defaults.get(
            "preview_branch_includes"
        )
        excludes = project.get("preview_branch_excludes") or defaults.get(
            "preview_branch_excludes"
        )
        if includes is not None:
            out["preview_branch_includes"] = includes
        if excludes is not None:
            out["preview_branch_excludes"] = excludes
    return out


def _get_project(token: str, account: str, name: str) -> dict[str, Any]:
    url = f"{API}/accounts/{account}/pages/projects/{name}"
    return _request("GET", url, token)


def _patch_project(
    token: str, account: str, name: str, body: dict[str, Any]
) -> dict[str, Any]:
    url = f"{API}/accounts/{account}/pages/projects/{name}"
    return _request("PATCH", url, token, body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Solo verifica drift; exit 1 si no cumple la política",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No llama a PATCH; imprime el cuerpo previsto",
    )
    args = parser.parse_args()

    policy = _load_policy()
    token, account = _creds()
    projects = policy.get("projects") or []
    if not projects:
        print("Sin proyectos en pages_security.json", file=sys.stderr)
        return 2

    drift = 0
    applied = 0
    skipped = 0
    errors = 0

    for proj in projects:
        name = proj.get("name")
        if not name:
            continue
        optional = bool(proj.get("optional"))
        desired = _desired(policy, proj)

        got = _get_project(token, account, name)
        if not got.get("success"):
            status = got.get("_http_status")
            msgs = got.get("errors") or []
            msg = msgs[0].get("message") if msgs else "error"
            if optional and status == 404:
                print(f"[skip] {name}: no existe (optional)")
                skipped += 1
                continue
            print(f"[error] {name}: GET falló ({status}): {msg}", file=sys.stderr)
            errors += 1
            continue

        result = got.get("result") or {}
        current = {
            "preview_deployment_setting": result.get("preview_deployment_setting"),
            "production_branch": result.get("production_branch"),
        }
        mismatch = {
            k: {"have": current.get(k), "want": v}
            for k, v in desired.items()
            if current.get(k) != v
        }

        if not mismatch:
            print(f"[ok] {name}: cumple política {desired}")
            continue

        drift += 1
        print(f"[drift] {name}: {json.dumps(mismatch, ensure_ascii=False)}")

        if args.check:
            continue

        if args.dry_run:
            print(f"[dry-run] PATCH {name} ← {json.dumps(desired)}")
            continue

        patched = _patch_project(token, account, name, desired)
        if not patched.get("success"):
            msgs = patched.get("errors") or []
            msg = msgs[0].get("message") if msgs else "error"
            print(f"[error] {name}: PATCH falló: {msg}", file=sys.stderr)
            errors += 1
            continue

        after = patched.get("result") or {}
        print(
            f"[applied] {name}: "
            f"preview={after.get('preview_deployment_setting')} "
            f"branch={after.get('production_branch')}"
        )
        applied += 1

    print(
        f"Resumen: drift={drift} applied={applied} skipped={skipped} errors={errors}"
    )
    if errors:
        return 1
    if args.check and drift:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
