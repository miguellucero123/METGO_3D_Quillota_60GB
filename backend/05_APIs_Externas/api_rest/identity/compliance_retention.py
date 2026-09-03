#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retención audit_auth y utilidades compliance (Ley 21.719)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any


def retention_days() -> int:
    """Default 548 ≈ 18 meses."""
    try:
        return max(30, int(os.getenv("METGO_AUDIT_AUTH_RETENTION_DAYS", "548")))
    except ValueError:
        return 548


def purge_audit_auth(*, dry_run: bool = False) -> dict[str, Any]:
    """Borra filas de audit_auth más antiguas que la retención."""
    days = retention_days()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    from api_rest.identity import identity_store

    if identity_store.use_memory():
        with identity_store._lock:
            before = len(identity_store._MEM.get("audit_auth") or [])
            kept = [
                a
                for a in identity_store._MEM.get("audit_auth") or []
                if _keep_audit(a, cutoff)
            ]
            deleted = before - len(kept)
            if not dry_run:
                identity_store._MEM["audit_auth"] = kept
        return {
            "ok": True,
            "dry_run": dry_run,
            "retention_days": days,
            "cutoff": cutoff_iso,
            "deleted": deleted,
            "store": "memory",
        }

    from api_rest.integracion import supabase_store as sb

    if dry_run:
        sample = sb.rest_select(
            "audit_auth",
            params={
                "created_at": f"lt.{cutoff_iso}",
                "select": "id",
            },
            limit=1000,
        )
        return {
            "ok": True,
            "dry_run": True,
            "retention_days": days,
            "cutoff": cutoff_iso,
            "deleted_estimate": len(sample),
            "store": "supabase",
        }

    deleted = sb.rest_delete("audit_auth", {"created_at": f"lt.{cutoff_iso}"})
    return {
        "ok": True,
        "dry_run": False,
        "retention_days": days,
        "cutoff": cutoff_iso,
        "deleted": deleted,
        "store": "supabase",
    }


def _keep_audit(row: dict[str, Any], cutoff: datetime) -> bool:
    raw = row.get("created_at")
    if not raw:
        return True
    try:
        if isinstance(raw, datetime):
            ts = raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
        else:
            s = str(raw).replace("Z", "+00:00")
            ts = datetime.fromisoformat(s)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        return ts >= cutoff
    except Exception:
        return True
