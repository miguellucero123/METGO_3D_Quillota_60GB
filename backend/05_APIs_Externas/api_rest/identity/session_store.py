#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sesión única por usuario + idle timeout opcional (METGO_SESSION_IDLE_S).

Redis queda diferido (multi-instancia); en Render free el store in-memory basta
mientras haya un solo worker.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any

_lock = threading.Lock()
# email/username lower → { "jti": str, "at": float }
_CURRENT: dict[str, dict[str, Any]] = {}


def session_idle_seconds() -> int:
    try:
        return max(0, int(os.getenv("METGO_SESSION_IDLE_S") or "0"))
    except ValueError:
        return 0


def register_session(user_key: str, jti: str) -> None:
    key = (user_key or "").strip().lower()
    if not key or not jti:
        return
    with _lock:
        _CURRENT[key] = {"jti": str(jti), "at": time.time()}


def touch_session(user_key: str, jti: str | None = None) -> None:
    """Renueva actividad (idle). Si jti no coincide, no toca."""
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


def is_session_active(user_key: str, jti: str | None) -> bool:
    """True si no hay registro (tokens legacy) o jti coincide y no expiró idle."""
    key = (user_key or "").strip().lower()
    if not key:
        return False
    with _lock:
        cur = _CURRENT.get(key)
        if not cur:
            # Sin registro: permitir (JWT emitidos antes del feature o refresh)
            return True
        if not jti:
            return False
        if str(cur.get("jti") or "") != str(jti):
            return False
        idle = session_idle_seconds()
        if idle > 0:
            at = float(cur.get("at") or 0)
            if at and (time.time() - at) > idle:
                _CURRENT.pop(key, None)
                return False
        return True


def clear_session(user_key: str) -> None:
    key = (user_key or "").strip().lower()
    with _lock:
        _CURRENT.pop(key, None)


def reset_for_tests() -> None:
    with _lock:
        _CURRENT.clear()
