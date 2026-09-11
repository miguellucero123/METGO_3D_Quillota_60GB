#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sesión única por usuario + idle timeout opcional (METGO_SESSION_IDLE_S).

Persistencia: memoria + Supabase `auth_sessions` (sobrevive cold start Render).
Desactivar: METGO_SINGLE_SESSION=0
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any

_lock = threading.Lock()
# email/username lower → { "jti": str, "at": float }
_CURRENT: dict[str, dict[str, Any]] = {}


def single_session_enabled() -> bool:
    raw = (os.getenv("METGO_SINGLE_SESSION") or "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def session_idle_seconds() -> int:
    try:
        return max(0, int(os.getenv("METGO_SESSION_IDLE_S") or "0"))
    except ValueError:
        return 0


def _persist_enabled() -> bool:
    if (os.getenv("METGO_IDENTITY_STORE") or "").strip().lower() == "memory":
        return False
    raw = (os.getenv("METGO_SESSION_PERSIST") or "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _sb_upsert(user_key: str, jti: str, at: float) -> None:
    if not _persist_enabled():
        return
    try:
        from api_rest.integracion import supabase_store
        from datetime import datetime, timezone

        ts = datetime.fromtimestamp(at, tz=timezone.utc).isoformat()
        supabase_store.rest_upsert(
            "auth_sessions",
            [{"user_key": user_key, "jti": jti, "updated_at": ts}],
            on_conflict="user_key",
        )
    except Exception as exc:
        print(f"session_store.upsert: {exc}")


def _sb_load(user_key: str) -> dict[str, Any] | None:
    if not _persist_enabled():
        return None
    try:
        from api_rest.integracion import supabase_store
        from datetime import datetime

        rows = supabase_store.rest_select(
            "auth_sessions",
            params={
                "user_key": f"eq.{user_key}",
                "select": "user_key,jti,updated_at",
            },
            limit=1,
        )
        if not rows:
            return None
        row = rows[0]
        jti = str(row.get("jti") or "")
        if not jti:
            return None
        at = time.time()
        raw_at = row.get("updated_at")
        if raw_at:
            try:
                dt = datetime.fromisoformat(str(raw_at).replace("Z", "+00:00"))
                at = dt.timestamp()
            except ValueError:
                pass
        return {"jti": jti, "at": at}
    except Exception as exc:
        print(f"session_store.load: {exc}")
        return None


def _sb_delete(user_key: str) -> None:
    if not _persist_enabled():
        return
    try:
        from api_rest.integracion import supabase_store

        supabase_store.rest_delete("auth_sessions", {"user_key": f"eq.{user_key}"})
    except Exception as exc:
        print(f"session_store.delete: {exc}")


def register_session(user_key: str, jti: str) -> None:
    if not single_session_enabled():
        return
    key = (user_key or "").strip().lower()
    if not key or not jti:
        return
    now = time.time()
    with _lock:
        _CURRENT[key] = {"jti": str(jti), "at": now}
    _sb_upsert(key, str(jti), now)


def touch_session(user_key: str, jti: str | None = None) -> None:
    """Renueva actividad (idle). Si jti no coincide, no toca."""
    if not single_session_enabled():
        return
    key = (user_key or "").strip().lower()
    if not key:
        return
    with _lock:
        cur = _CURRENT.get(key)
        if not cur:
            return
        if jti and str(cur.get("jti") or "") != str(jti):
            return
        cur["at"] = time.time()
        jti_s = str(cur.get("jti") or "")
        at = float(cur["at"])
    if jti_s:
        _sb_upsert(key, jti_s, at)


def _resolve_current(key: str) -> dict[str, Any] | None:
    with _lock:
        cur = _CURRENT.get(key)
        if cur:
            return dict(cur)
    loaded = _sb_load(key)
    if loaded:
        with _lock:
            _CURRENT[key] = loaded
        return dict(loaded)
    return None


def is_session_active(user_key: str, jti: str | None) -> bool:
    """True si jti coincide y no expiró idle. Sin feature → True."""
    if not single_session_enabled():
        return True
    key = (user_key or "").strip().lower()
    if not key:
        return False
    cur = _resolve_current(key)
    if not cur:
        # Sin registro: permitir JWT emitidos antes del feature (un solo uso)
        return True
    if not jti:
        return False
    if str(cur.get("jti") or "") != str(jti):
        return False
    idle = session_idle_seconds()
    if idle > 0:
        at = float(cur.get("at") or 0)
        if at and (time.time() - at) > idle:
            clear_session(key)
            return False
    return True


def clear_session(user_key: str) -> None:
    key = (user_key or "").strip().lower()
    with _lock:
        _CURRENT.pop(key, None)
    _sb_delete(key)


def reset_for_tests() -> None:
    with _lock:
        _CURRENT.clear()
