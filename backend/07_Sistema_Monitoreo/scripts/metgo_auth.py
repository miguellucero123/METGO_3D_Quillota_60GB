#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autenticacion compartida METGO (Streamlit + API REST JWT).
Credenciales: METGO_PASSWORD_ADMIN, METGO_PASSWORD_USER, METGO_PASSWORD_METGO
"""

from __future__ import annotations

import os
import warnings
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    import jwt
except ImportError:
    jwt = None  # type: ignore

USUARIOS_VALIDOS = ("admin", "user", "metgo")

# Solo desarrollo local si no hay variables de entorno
_DEV_FALLBACK = {
    "admin": "admin123",
    "user": "user123",
    "metgo": "metgo2025",
}

_warned_dev = False


def _warn_dev_fallback() -> None:
    global _warned_dev
    if not _warned_dev:
        warnings.warn(
            "METGO: usando contraseñas de desarrollo. "
            "Defina METGO_PASSWORD_ADMIN, METGO_PASSWORD_USER, METGO_PASSWORD_METGO.",
            stacklevel=3,
        )
        _warned_dev = True


def obtener_password(usuario: str) -> str | None:
    """Lee contraseña desde variable de entorno METGO_PASSWORD_{USUARIO}."""
    usuario = usuario.lower().strip()
    if usuario not in USUARIOS_VALIDOS:
        return None
    env_key = f"METGO_PASSWORD_{usuario.upper()}"
    value = os.getenv(env_key)
    if value:
        return value
    if usuario in _DEV_FALLBACK:
        _warn_dev_fallback()
        return _DEV_FALLBACK[usuario]
    return None


def verificar_credenciales(usuario: str, contraseña: str) -> bool:
    """Valida usuario y contraseña (Streamlit y API login)."""
    if not usuario or not contraseña:
        return False
    esperada = obtener_password(usuario)
    return esperada is not None and esperada == contraseña


def jwt_secret() -> str:
    secret = os.getenv("METGO_JWT_SECRET")
    if secret:
        return secret
    _warn_dev_fallback()
    return os.getenv("METGO_JWT_SECRET_DEV", "metgo-dev-jwt-change-in-production")


def jwt_expiration_seconds() -> int:
    return int(os.getenv("METGO_JWT_EXPIRATION_SECONDS", "3600"))


def jwt_algorithm() -> str:
    return os.getenv("METGO_JWT_ALGORITHM", "HS256")


def crear_token_acceso(usuario: str) -> dict[str, Any]:
    """Genera JWT y metadatos para el cliente."""
    if jwt is None:
        raise RuntimeError("Instale PyJWT: pip install PyJWT")

    usuario = usuario.lower().strip()
    if usuario not in USUARIOS_VALIDOS:
        raise ValueError("Usuario no permitido")

    exp_secs = jwt_expiration_seconds()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": usuario,
        "role": usuario,
        "iat": now,
        "exp": now + timedelta(seconds=exp_secs),
    }
    token = jwt.encode(payload, jwt_secret(), algorithm=jwt_algorithm())
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": exp_secs,
        "user": {"username": usuario, "role": usuario},
    }


def decodificar_token(token: str) -> dict[str, Any] | None:
    """Devuelve payload JWT o None si es invalido/expirado."""
    if jwt is None or not token:
        return None
    try:
        return jwt.decode(
            token,
            jwt_secret(),
            algorithms=[jwt_algorithm()],
        )
    except jwt.PyJWTError:
        return None
