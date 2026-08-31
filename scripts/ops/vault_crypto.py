#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta / restaura vault METGO (secretos + internos ocultos de Git).

Uso:
  python scripts/ops/vault_crypto.py pack
      -> local/METGO_VAULT.local.enc
         (vault env + bootstrap + .env + docs/ + site-web/ + templates/ + …)

  python scripts/ops/vault_crypto.py unpack
      -> restaura en el repo (sin pisar .env si ya existe)

Nunca commitear: *.local.env, *.local.md, *.local.enc
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

# Secretos / bootstrap (carpeta local/)
VAULT_FILES = (
    "METGO_VAULT.local.env",
    "METGO_BOOTSTRAP.local.md",
)

# Carpetas ocultas en GitHub pero necesarias para operar / documentar
INTERNAL_DIRS = (
    "docs",
    "site-web",
    "templates",
    "loadtests",
    ".devcontainer",
)

# Archivos sueltos ocultos
INTERNAL_FILES = (
    "docker-compose.dev.yml",
    "test_supabase.py",
)

SKIP_DIR_NAMES = {
    "__pycache__",
    ".ipynb_checkpoints",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "dist",
    ".wrangler",
    ".lighthouseci",
}

SKIP_SUFFIXES = {".pyc", ".pyo", ".db", ".log"}


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


def _should_skip(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def _add_tree(zf: zipfile.ZipFile, rel_dir: str) -> int:
    """Añade carpeta relativa a ROOT. Retorna nº de archivos."""
    base = ROOT / rel_dir
    if not base.is_dir():
        print(f"  (omitido, no existe) {rel_dir}/")
        return 0
    n = 0
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path.relative_to(ROOT)):
            continue
        arc = path.relative_to(ROOT).as_posix()
        zf.write(path, arcname=arc)
        n += 1
    print(f"  + {rel_dir}/ ({n} archivos)")
    return n


def pack() -> None:
    LOCAL.mkdir(parents=True, exist_ok=True)
    missing = [n for n in VAULT_FILES if not (LOCAL / n).is_file()]
    if missing:
        print("Faltan archivos del vault. Copia primero las plantillas:")
        for n in missing:
            if n.endswith(".env"):
                ex = "METGO_VAULT.local.example.env"
            else:
                ex = "METGO_BOOTSTRAP.local.example.md"
            print(f"  copy local\\{ex} local\\{n}")
        raise SystemExit(1)

    passphrase = getpass.getpass("Passphrase (no la pierdas): ")
    confirm = getpass.getpass("Repetir passphrase: ")
    if passphrase != confirm or len(passphrase) < 12:
        raise SystemExit("Passphrase no coincide o es demasiado corta (mín. 12).")

    print("Empaquetando…")
    buf = BytesIO()
    total = 0
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        meta = {
            "v": 2,
            "vault_files": list(VAULT_FILES),
            "internal_dirs": list(INTERNAL_DIRS),
            "internal_files": list(INTERNAL_FILES),
        }
        zf.writestr("_metgo_bundle_meta.json", json.dumps(meta, indent=2))

        for name in VAULT_FILES:
            zf.write(LOCAL / name, arcname=f"local/{name}")
            total += 1
            print(f"  + local/{name}")

        root_env = ROOT / ".env"
        if root_env.is_file():
            zf.write(root_env, arcname=".env")
            total += 1
            print("  + .env")

        for d in INTERNAL_DIRS:
            total += _add_tree(zf, d)

        for name in INTERNAL_FILES:
            p = ROOT / name
            if p.is_file():
                zf.write(p, arcname=name)
                total += 1
                print(f"  + {name}")
            else:
                print(f"  (omitido, no existe) {name}")

    salt = os.urandom(16)
    token = _fernet(passphrase, salt).encrypt(buf.getvalue())
    payload = {
        "v": 2,
        "salt": base64.b64encode(salt).decode("ascii"),
        "data": base64.b64encode(token).decode("ascii"),
        "files_approx": total,
    }
    ENC_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    size_mb = ENC_PATH.stat().st_size / (1024 * 1024)
    print(f"OK -> {ENC_PATH} (~{size_mb:.1f} MB, ~{total} entradas)")
    print("Copia el .enc por USB/canal privado + passphrase por otro canal.")
    print("NO lo subas a GitHub.")


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
    restored = 0
    skipped = 0
    with zipfile.ZipFile(BytesIO(raw), "r") as zf:
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            if name.endswith("/") or name == "_metgo_bundle_meta.json":
                continue
            # Compat v1: vault files sin prefijo local/
            if name in VAULT_FILES:
                target = LOCAL / name
            elif name.startswith("local/"):
                target = ROOT / name
            else:
                target = ROOT / name

            # No pisar .env existente
            if target.resolve() == (ROOT / ".env").resolve() and target.exists():
                print(f"Omitido (ya existe): {target}")
                skipped += 1
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))
            restored += 1
            if restored <= 30 or name.endswith((".env", ".md", "yml")):
                print(f"Restaurado: {target}")

    if restored > 30:
        print(f"… y {restored - 30} archivos más")

    vault_env = LOCAL / "METGO_VAULT.local.env"
    root_env = ROOT / ".env"
    if vault_env.is_file() and not root_env.exists():
        root_env.write_bytes(vault_env.read_bytes())
        print(f"También copiado a {root_env}")

    print(f"Listo. restaurados={restored} omitidos={skipped}")
    print("Siguiente: copy local\\METGO_VAULT.local.env .env  (si hace falta)")
    print("Docs: docs/ops/BOOTSTRAP_OTRO_PC.md (tras unpack)")


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
