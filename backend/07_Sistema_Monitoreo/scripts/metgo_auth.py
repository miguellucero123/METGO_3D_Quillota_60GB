#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autenticacion compartida METGO (Streamlit + API REST JWT).
Credenciales: METGO_PASSWORD_{USUARIO} en mayúsculas.
Roles: admin | agronomo | operador | lectura
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
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

# Usuario de login -> rol JWT
USER_TO_ROLE: dict[str, str] = {
    "admin": "admin",
    "user": "operador",
    "metgo": "agronomo",
    "agronomo": "agronomo",
    "operador": "operador",
    "lector": "lectura",
}

USUARIOS_VALIDOS = tuple(USER_TO_ROLE.keys())

ROLE_HIERARCHY = ("admin", "agronomo", "operador", "lectura")

_DEV_FALLBACK = {
    "admin": "admin123",
    "user": "user123",
    "metgo": "metgo2025",
    "agronomo": "agro123",
    "operador": "op123",
    "lector": "lec123",
}

_warned_dev = False

_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")


def _registry_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "usuarios_registrados.json"
    return Path("usuarios_registrados.json")


def cargar_usuarios_registrados() -> dict[str, dict[str, Any]]:
    path = _registry_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def usuario_existe(usuario: str) -> bool:
    u = usuario.lower().strip()
    return u in USER_TO_ROLE or u in cargar_usuarios_registrados()


def registrar_usuario(
    usuario: str, contraseña: str, email: str | None = None
) -> tuple[bool, str]:
    """Auto-registro demo (rol lectura). Requiere METGO_ALLOW_SELF_REGISTER=1."""
    if os.getenv("METGO_ALLOW_SELF_REGISTER", "1") != "1":
        return False, "Registro deshabilitado en este entorno"

    u = usuario.lower().strip()
    if not _USERNAME_RE.match(u):
        return (
            False,
            "Usuario inválido (3-32 caracteres: letras minúsculas, números, _)",
        )
    if u in USER_TO_ROLE:
        return False, "Nombre de usuario reservado del sistema"
    if u in cargar_usuarios_registrados():
        return False, "El usuario ya existe"
    if len(contraseña or "") < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"

    reg = cargar_usuarios_registrados()
    reg[u] = {
        "password_hash": _hash_password(contraseña),
        "email": (email or "").strip() or None,
        "role": "lectura",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = _registry_path()
    path.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
    return True, "Usuario registrado correctamente"


def rol_de_usuario(usuario: str) -> str:
    u = usuario.lower().strip()
    if u in USER_TO_ROLE:
        return USER_TO_ROLE[u]
    if u in cargar_usuarios_registrados():
        return str(cargar_usuarios_registrados()[u].get("role") or "lectura")
    return "lectura"


def tenant_de_usuario(usuario: str) -> str | None:
    """None = admin ve todos los tenants."""
    try:
        from api_rest.tenants import tenant_de_usuario as _t

        return _t(usuario)
    except ImportError:
        return "quillota" if usuario != "admin" else None


def rol_permitido(user_role: str, roles_requeridos: tuple[str, ...]) -> bool:
    if user_role == "admin":
        return True
    return user_role in roles_requeridos


def _warn_dev_fallback() -> None:
    global _warned_dev
    if not _warned_dev:
        warnings.warn(
            "METGO: usando contraseñas de desarrollo. "
            "Defina METGO_PASSWORD_* en el entorno.",
            stacklevel=3,
        )
        _warned_dev = True


def obtener_password(usuario: str) -> str | None:
    usuario = usuario.lower().strip()
    if usuario in cargar_usuarios_registrados():
        return None
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
    if not usuario or not contraseña:
        return False
    u = usuario.lower().strip()
    reg = cargar_usuarios_registrados()
    if u in reg:
        return reg[u].get("password_hash") == _hash_password(contraseña)
    esperada = obtener_password(u)
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
    if jwt is None:
        raise RuntimeError("Instale PyJWT: pip install PyJWT")

    usuario = usuario.lower().strip()
    if not usuario_existe(usuario):
        raise ValueError("Usuario no permitido")

    role = rol_de_usuario(usuario)
    tenant = tenant_de_usuario(usuario)
    exp_secs = jwt_expiration_seconds()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": usuario,
        "role": role,
        "tenant": tenant,
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
        "user": {"username": usuario, "role": role, "tenant": tenant},
    }


def decodificar_token(token: str) -> dict[str, Any] | None:
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
