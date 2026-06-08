#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Predicción de nieblas y visibilidad."""

from __future__ import annotations

from enum import Enum
from typing import Any

from .meteo_utils import calcular_punto_rocio


class TipoNiebla(str, Enum):
    RADIATIVA = "radiativa"
    ADVECTIVA = "advectiva"
    ROCIO_CERRO = "rocio_cerro"


class SeveridadNiebla(str, Enum):
    NORMAL = "normal"
    MODERADA = "moderada"
    DENSA = "densa"
    MUY_DENSA = "muy_densa"


class PredictorNiebla:
    def __init__(self, estacion_id: str, altitud: float = 145):
        self.estacion_id = estacion_id
        self.altitud = altitud

    @staticmethod
    def calcular_punto_rocio(temperatura: float, humedad_relativa: float) -> float:
        return calcular_punto_rocio(temperatura, humedad_relativa)

    def predecir_niebla(
        self,
        temperatura: float,
        humedad_relativa: float,
        visibilidad_pronosticada: float,
        velocidad_viento: float,
        punto_rocio: float,
        hora_del_dia: int,
        cobertura_nubosa: float,
        fecha_iso: str,
        historia_temperaturas: list[float] | None = None,
    ) -> dict[str, Any]:
        diff = temperatura - punto_rocio
        f_sat = self._evaluar_saturacion(diff)
        f_inv = self._evaluar_inversion(historia_temperaturas, temperatura)
        f_viento = self._evaluar_viento(velocidad_viento)
        f_hr = self._evaluar_humedad(humedad_relativa)
        f_hora = self._evaluar_hora(hora_del_dia)
        f_nubes = 0.7 if cobertura_nubosa > 80 else 0.4 if cobertura_nubosa > 60 else 0.1

        prob = (
            f_sat * 0.35
            + f_inv * 0.25
            + f_viento * 0.15
            + f_hr * 0.10
            + f_hora * 0.10
            + f_nubes * 0.05
        ) * 100

        tipo = (
            TipoNiebla.ADVECTIVA
            if velocidad_viento > 5
            else TipoNiebla.RADIATIVA
        )
        severidad = self._evaluar_severidad(visibilidad_pronosticada)

        return {
            "estacion_id": self.estacion_id,
            "fecha_pronostico": fecha_iso,
            "tipo_niebla": tipo.value,
            "severidad": severidad.value,
            "probabilidad_niebla": round(prob, 1),
            "visibilidad_esperada": round(visibilidad_pronosticada, 2),
            "visibilidad_esperada_unidad": "km",
            "temperatura_punto_rocio_diferencia": round(diff, 1),
            "punto_rocio": punto_rocio,
            "hora_maxima_densidad": "04:30",
            "recomendaciones": self._recomendaciones(severidad, prob),
            "scores_componentes": {
                "saturacion": round(f_sat * 100, 1),
                "inversion_termica": round(f_inv * 100, 1),
                "viento": round(f_viento * 100, 1),
                "humedad": round(f_hr * 100, 1),
                "hora": round(f_hora * 100, 1),
                "nubes": round(f_nubes * 100, 1),
            },
        }

    def _evaluar_saturacion(self, diferencia: float) -> float:
        if diferencia < 0.5:
            return 1.0
        if diferencia < 1.0:
            return 0.9
        if diferencia < 2.0:
            return 0.7
        if diferencia < 3.0:
            return 0.4
        return 0.1 if diferencia < 5.0 else 0.0

    def _evaluar_inversion(
        self, historia: list[float] | None, temp_actual: float
    ) -> float:
        if not historia or len(historia) < 3:
            return 0.3
        pendiente = (historia[-1] - historia[0]) / (len(historia) - 1)
        if pendiente > 0.3:
            return 0.9
        if pendiente > 0:
            return 0.6
        return 0.2

    def _evaluar_viento(self, velocidad: float) -> float:
        if velocidad < 0.5:
            return 1.0
        if velocidad < 1.5:
            return 0.8
        if velocidad < 3:
            return 0.5
        return 0.2 if velocidad < 5 else 0.05

    def _evaluar_humedad(self, hr: float) -> float:
        if hr > 95:
            return 1.0
        if hr > 90:
            return 0.9
        if hr > 85:
            return 0.7
        if hr > 75:
            return 0.3
        return 0.0

    def _evaluar_hora(self, hora: int) -> float:
        if 3 <= hora <= 8:
            return 0.95
        if 2 <= hora <= 9:
            return 0.7
        return 0.05

    def _evaluar_severidad(self, visibilidad: float) -> SeveridadNiebla:
        if visibilidad > 1.0:
            return SeveridadNiebla.NORMAL
        if visibilidad > 0.5:
            return SeveridadNiebla.MODERADA
        if visibilidad > 0.1:
            return SeveridadNiebla.DENSA
        return SeveridadNiebla.MUY_DENSA

    def _recomendaciones(self, severidad: SeveridadNiebla, prob: float) -> list[str]:
        if prob < 20:
            return ["Riesgo bajo de niebla. Operaciones normales."]
        recs = [f"Probabilidad de niebla: {prob:.0f}%"]
        if severidad == SeveridadNiebla.MUY_DENSA:
            recs.append("ALERTA: niebla muy densa — reducir velocidad en carreteras")
        elif severidad == SeveridadNiebla.DENSA:
            recs.append("Niebla densa — activar luces y máxima precaución")
        elif severidad == SeveridadNiebla.MODERADA:
            recs.append("Visibilidad reducida — precaución en tránsito")
        return recs
