#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cifrado PII (AES-256-GCM) + hash de contraseñas (scrypt)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from typing import Final

_PREFIX: Final = "v1"


def _kek() -> bytes:
    raw = (os.getenv("METGO_PII_KEK") or "").strip()
    if not raw:
        # Solo para tests/local: derivar de JWT secret (NO prod)
        raw = (os.getenv("METGO_JWT_SECRET") or "metgo-dev-pii-kek-not-for-prod").strip()
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return digest


def encrypt_pii(plaintext: str) -> str:
    """AES-256-GCM via cryptography if available; else XOR+HMAC sealed blob (dev)."""
    text = (plaintext or "").encode("utf-8")
    nonce = secrets.token_bytes(12)
    key = _kek()
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        ct = AESGCM(key).encrypt(nonce, text, None)
        blob = nonce + ct
    except ImportError:
        # Fallback sin dependencia: stream XOR + HMAC-SHA256 (aceptable solo lab)
        stream = hashlib.sha256(key + nonce).digest()
        out = bytearray()
        for i, b in enumerate(text):
            out.append(b ^ stream[i % len(stream)])
        tag = hmac.new(key, nonce + bytes(out), hashlib.sha256).digest()[:16]
        blob = nonce + tag + bytes(out)
    return f"{_PREFIX}." + base64.urlsafe_b64encode(blob).decode("ascii")


def decrypt_pii(token: str) -> str:
    if not token or not token.startswith(f"{_PREFIX}."):
        raise ValueError("ciphertext invalido")
    blob = base64.urlsafe_b64decode(token.split(".", 1)[1].encode("ascii"))
    key = _kek()
    nonce, rest = blob[:12], blob[12:]
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        pt = AESGCM(key).decrypt(nonce, rest, None)
    except ImportError:
        tag, body = rest[:16], rest[16:]
        expect = hmac.new(key, nonce + body, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(tag, expect):
            raise ValueError("tag invalido")
        stream = hashlib.sha256(key + nonce).digest()
        pt = bytes(b ^ stream[i % len(stream)] for i, b in enumerate(body))
    return pt.decode("utf-8")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
    )
    return "scrypt$" + base64.urlsafe_b64encode(salt + dk).decode("ascii")


def verify_password(password: str, stored: str) -> bool:
    if not stored.startswith("scrypt$"):
        return False
    raw = base64.urlsafe_b64decode(stored.split("$", 1)[1].encode("ascii"))
    salt, expect = raw[:16], raw[16:]
    dk = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
    )
    return hmac.compare_digest(dk, expect)


def hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    pepper = _kek()
    return hashlib.sha256(pepper + ip.encode("utf-8")).hexdigest()[:32]
