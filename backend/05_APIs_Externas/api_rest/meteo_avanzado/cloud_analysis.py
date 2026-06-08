#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análisis de nubosidad y radiación solar."""

from __future__ import annotations

from enum import Enum
from typing import Any


class TipoNube(str, Enum):
    DESPEJADO = "despejado"
    PARCIALMENTE_NUBLADO = "parcialmente_nublado"
    NUBLADO = "nublado"
    MUY_NUBLADO = "muy_nublado"


class AnalizadorNubosidad:
    @staticmethod
    def clasificar_cobertura(porcentaje: float) -> TipoNube:
        if porcentaje < 10:
            return TipoNube.DESPEJADO
        if porcentaje < 50:
            return TipoNube.PARCIALMENTE_NUBLADO
        if porcentaje < 80:
            return TipoNube.NUBLADO
        return TipoNube.MUY_NUBLADO

    @staticmethod
    def estimar_radiacion_solar(
        radiacion_bruta: float,
        cobertura_nubosa: float,
        altitud_m: float = 145,
    ) -> dict[str, Any]:
        factores = {
            TipoNube.DESPEJADO: 0.95,
            TipoNube.PARCIALMENTE_NUBLADO: 0.70,
            TipoNube.NUBLADO: 0.40,
            TipoNube.MUY_NUBLADO: 0.10,
        }
        tipo = AnalizadorNubosidad.clasificar_cobertura(cobertura_nubosa)
        factor = factores[tipo]
        alt_factor = 1.0 + (altitud_m / 1000.0) * 0.10
        superficie = radiacion_bruta * factor * alt_factor
        difusa = radiacion_bruta * (1 - factor) * 0.3
        directa = max(0.0, superficie - difusa)
        return {
            "radiacion_global_superficie": round(superficie, 2),
            "radiacion_directa": round(directa, 2),
            "radiacion_difusa": round(difusa, 2),
            "tipo_nube": tipo.value,
            "factor_atenacion": round(factor, 2),
        }

    @staticmethod
    def impacto_en_temperatura(
        cobertura_nubosa: float,
        temperatura_dia: float,
        temperatura_noche: float,
    ) -> dict[str, Any]:
        tipo = AnalizadorNubosidad.clasificar_cobertura(cobertura_nubosa)
        reduccion = {
            TipoNube.DESPEJADO: 0.0,
            TipoNube.PARCIALMENTE_NUBLADO: -2.0,
            TipoNube.NUBLADO: -4.0,
            TipoNube.MUY_NUBLADO: -6.0,
        }
        aumento = {
            TipoNube.DESPEJADO: 0.0,
            TipoNube.PARCIALMENTE_NUBLADO: 2.0,
            TipoNube.NUBLADO: 4.0,
            TipoNube.MUY_NUBLADO: 5.0,
        }
        return {
            "tipo_nube": tipo.value,
            "cobertura_porcentaje": cobertura_nubosa,
            "temperatura_dia_estimada": round(
                temperatura_dia + reduccion[tipo], 1
            ),
            "efecto_dia": reduccion[tipo],
            "temperatura_noche_estimada": round(
                temperatura_noche + aumento[tipo], 1
            ),
            "efecto_noche": aumento[tipo],
        }
