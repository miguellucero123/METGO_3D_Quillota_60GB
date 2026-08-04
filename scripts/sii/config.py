#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuración SII desde entorno (sin secretos en código)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env.sii"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        # Parseo mínimo KEY=VALUE sin dependencia
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


@dataclass(frozen=True)
class SiiConfig:
    ambiente: str
    rut_emisor: str
    razon_emisor: str
    giro_emisor: str
    direccion_emisor: str
    comuna_emisor: str
    cert_path: str
    cert_password: str
    caf_path: str
    resolucion_num: str
    resolucion_fecha: str

    @property
    def puede_firmar(self) -> bool:
        return bool(self.cert_path and Path(self.cert_path).is_file() and self.cert_password)

    @property
    def listo_emision(self) -> bool:
        return bool(self.rut_emisor and self.razon_emisor and self.puede_firmar)


def load_config() -> SiiConfig:
    return SiiConfig(
        ambiente=(os.getenv("SII_AMBIENTE") or "cert").strip().lower(),
        rut_emisor=(os.getenv("SII_RUT_EMISOR") or "").strip(),
        razon_emisor=(os.getenv("SII_RAZON_EMISOR") or "").strip(),
        giro_emisor=(os.getenv("SII_GIRO_EMISOR") or "").strip(),
        direccion_emisor=(os.getenv("SII_DIRECCION_EMISOR") or "").strip(),
        comuna_emisor=(os.getenv("SII_COMUNA_EMISOR") or "").strip(),
        cert_path=(os.getenv("SII_CERT_PATH") or "").strip(),
        cert_password=(os.getenv("SII_CERT_PASSWORD") or "").strip(),
        caf_path=(os.getenv("SII_CAF_PATH") or "").strip(),
        resolucion_num=(os.getenv("SII_RESOLUCION_NUM") or "").strip(),
        resolucion_fecha=(os.getenv("SII_RESOLUCION_FECHA") or "").strip(),
    )
