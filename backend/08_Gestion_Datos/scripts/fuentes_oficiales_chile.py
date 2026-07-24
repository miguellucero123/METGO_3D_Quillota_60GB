"""Conectores oficiales Chile — Agromet (INIA) y DMC.

La implementación vive en ``api_rest.oficiales_service`` (E12).
Este script reexporta el contrato para CLI / etl_sync.
"""

from __future__ import annotations

import sys
from pathlib import Path

_API = Path(__file__).resolve().parents[2] / "05_APIs_Externas"
if str(_API) not in sys.path:
    sys.path.insert(0, str(_API))

from api_rest.oficiales_service import (  # noqa: E402
    AGROMET_ESTACIONES,
    DMC_ESTACIONES,
    catalogo_agromet,
    catalogo_dmc,
    estado_fuentes,
    fetch_agromet_historico,
    fetch_dmc_historico,
    sincronizar_oficiales,
)

__all__ = [
    "AGROMET_ESTACIONES",
    "DMC_ESTACIONES",
    "catalogo_agromet",
    "catalogo_dmc",
    "estado_fuentes",
    "fetch_agromet_historico",
    "fetch_dmc_historico",
    "sincronizar_oficiales",
]
