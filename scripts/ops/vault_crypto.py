#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta / restaura el vault local METGO (cifrado con passphrase).

Uso:
  python scripts/ops/vault_crypto.py pack     # local/*.local.* -> local/METGO_VAULT.local.enc
  python scripts/ops/vault_crypto.py unpack   # .enc -> restaura archivos .local

Nunca commitear: METGO_VAULT.local.env, .local.md, .local.enc
"""
from __future__ import annotations

import base64
import getpass
import hashlib
import json
import os
import sys
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "local"
ENC_NAME = "METGO_VAULT.local.enc"
ENC_PATH = LOCAL / ENC_NAME

VAULT_FILES = (
    "METGO_VAULT.local.env",
    "METGO_BOOTSTRAP.local.md",
)


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 400_000, dklen=32)


def _fernet(passphrase: str, salt: bytes):
    try:
        from cryptography.fernet import Fernet
    except ImportError as e:
        raise SystemExit(
            "Falta el paquete cryptography. Instala: pip install cryptography"
        ) from e
    key = base64.urlsafe_b64encode(_derive_key(passphrase, salt))
    return Fernet(key)


def pack() -> None:
    LOCAL.mkdir(parents=True, exist_ok=True)
    missing = [n for n in VAULT_FILES if not (LOCAL / n).is_file()]
    if missing:
        print("Faltan archivos. Copia primero las plantillas:")
        for n in missing:
            ex = n.replace(".local.", ".local.example.").replace(
                "METGO_VAULT.local.env", "METGO_VAULT.local.example.env"
            )
            # normalize example names
            if n.endswith(".env"):
                ex = "METGO_VAULT.local.example.env"
            elif n.endswith(".md"):
                ex = "METGO_BOOTSTRAP.local.example.md"
            print(f"  copy local\\{ex} local\\{n}")
        raise SystemExit(1)

    passphrase = getpass.getpass("Passphrase (no la pierdas): ")
    confirm = getpass.getpass("Repetir passphrase: ")
    if passphrase != confirm or len(passphrase) < 12:
        raise SystemExit("Passphrase no coincide o es demasiado corta (mín. 12).")

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in VAULT_FILES:
            zf.write(LOCAL / name, arcname=name)
        # incluir .env raíz si existe (mismo PC)
        root_env = ROOT / ".env"
        if root_env.is_file():
            zf.write(root_env, arcname=".env")

    salt = os.urandom(16)
    token = _fernet(passphrase, salt).encrypt(buf.getvalue())
    payload = {
        "v": 1,
        "salt": base64.b64encode(salt).decode("ascii"),
        "data": base64.b64encode(token).decode("ascii"),
    }
    ENC_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"OK -> {ENC_PATH}")
    print("Copia ese .enc por USB/canal privado. NO lo subas a GitHub.")


def unpack() -> None:
    if not ENC_PATH.is_file():
        raise SystemExit(f"No existe {ENC_PATH}. Coloca el .enc en local/")

    passphrase = getpass.getpass("Passphrase: ")
    payload = json.loads(ENC_PATH.read_text(encoding="utf-8"))
    salt = base64.b64decode(payload["salt"])
    token = base64.b64decode(payload["data"])
    try:
        raw = _fernet(passphrase, salt).decrypt(token)
    except Exception as e:
        raise SystemExit(f"No se pudo descifrar (passphrase incorrecta?): {e}") from e

    LOCAL.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BytesIO(raw), "r") as zf:
        for info in zf.infolist():
            target = ROOT / info.filename if info.filename == ".env" else LOCAL / info.filename
            if info.filename == ".env":
                if target.exists():
                    print(f"Omitido (ya existe): {target}")
                    continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))
            print(f"Restaurado: {target}")

    vault_env = LOCAL / "METGO_VAULT.local.env"
    root_env = ROOT / ".env"
    if vault_env.is_file() and not root_env.exists():
        root_env.write_bytes(vault_env.read_bytes())
        print(f"También copiado a {root_env}")
    print("Listo. Sigue docs/ops/BOOTSTRAP_OTRO_PC.md")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("pack", "unpack"):
        print(__doc__)
        raise SystemExit(2)
    if sys.argv[1] == "pack":
        pack()
    else:
        unpack()


if __name__ == "__main__":
    main()
