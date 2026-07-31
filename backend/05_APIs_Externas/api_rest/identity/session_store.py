#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sesión única por usuario: solo el jti más reciente es válido."""

from __future__ import annotations

import threading
from typing import Any

_lock = threading.Lock()
# email/username lower → { "jti": str, "at": float }
_CURRENT: dict[str, dict[str, Any]] = {}


def register_session(user_key: str, jti: str) -> None:
    key = (user_key or "").strip().lower()
    if not key or not jti:
        return
    import time

    with _lock:
        _CURRENT[key] = {"jti": str(jti), "at": time.time()}


def is_session_active(user_key: str, jti: str | None) -> bool:
    """True si no hay registro (tokens legacy) o jti coincide."""
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
    return str(cur.get("jti") or "") == str(jti)


def clear_session(user_key: str) -> None:
    key = (user_key or "").strip().lower()
    with _lock:
        _CURRENT.pop(key, None)


def reset_for_tests() -> None:
    with _lock:
        _CURRENT.clear()
