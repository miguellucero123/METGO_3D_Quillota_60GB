#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de riesgo de helada radiativa."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class ModeloHeladaRadiativa:
    """Helada radiativa: cielo despejado + viento débil + HR alta + T° baja."""

    def __init__(self, estacion_id: str):
        self.estacion_id = estacion_id

    def calcular_riesgo_helada(
        self,
        temperatura_pronosticada: float,
        temperatura_minima_pronosticada: float,
        cobertura_nubosa: float,
        velocidad_viento: float,
        humedad_relativa: float,
        punto_rocio: float,
        fecha: datetime,
        historia_temperatura: list[float] | None = None,
    ) -> dict[str, Any]:
        temp_f = self._evaluar_temperatura(temperatura_minima_pronosticada)
        nub_f = self._evaluar_nubosidad(cobertura_nubosa)
        viento_f = self._evaluar_viento(velocidad_viento)
        hum_f = self._evaluar_humedad(humedad_relativa)
        tend_f = self._evaluar_tendencia(historia_temperatura) if historia_temperatura else 0.5
        rocio_f = self._evaluar_punto_rocio(punto_rocio, temperatura_minima_pronosticada)

        pesos = {
            "temperatura": 0.30,
            "nubosidad": 0.25,
            "viento": 0.20,
            "humedad": 0.15,
            "tendencia": 0.05,
            "rocio": 0.05,
        }
        prob = (
            temp_f * pesos["temperatura"]
            + nub_f * pesos["nubosidad"]
            + viento_f * pesos["viento"]
            + hum_f * pesos["humedad"]
            + tend_f * pesos["tendencia"]
            + rocio_f * pesos["rocio"]
        ) * 100

        riesgo_severo = prob > 70 and temperatura_minima_pronosticada < -2
        riesgo_moderado = prob > 40 and temperatura_minima_pronosticada < 0

        factores = []
        if cobertura_nubosa < 20:
            factores.append(f"Cielo despejado ({cobertura_nubosa:.0f}% nubosidad)")
        if velocidad_viento < 3:
            factores.append(f"Viento débil ({velocidad_viento:.1f} m/s)")
        if humedad_relativa > 70:
            factores.append(f"Humedad alta ({humedad_relativa:.0f}%)")
        if abs(punto_rocio - temperatura_minima_pronosticada) < 3:
            factores.append("Punto de rocío cercano a T° mínima")

        return {
            "estacion_id": self.estacion_id,
            "fecha_pronostico": fecha.isoformat(),
            "probabilidad_helada": round(prob, 1),
            "riesgo_helada_radiativa": round(prob, 1),
            "temperatura_minima_esperada": round(temperatura_minima_pronosticada, 1),
            "temperatura_minima_absoluta": round(temperatura_minima_pronosticada, 1),
            "temperatura_maxima": round(temperatura_pronosticada, 1),
            "riesgo_severo": riesgo_severo,
            "riesgo_moderado": riesgo_moderado,
            "hora_critica_esperada": "04:00",
            "factores_contribuyentes": factores,
            "recomendaciones": self._generar_recomendaciones(
                prob, temperatura_minima_pronosticada, riesgo_severo
            ),
            "scores_componentes": {
                "temperatura": round(temp_f * 100, 1),
                "nubosidad": round(nub_f * 100, 1),
                "viento": round(viento_f * 100, 1),
                "humedad": round(hum_f * 100, 1),
                "tendencia": round(tend_f * 100, 1),
                "punto_rocio": round(rocio_f * 100, 1),
            },
        }

    def _evaluar_temperatura(self, temp_min: float) -> float:
        if temp_min < -10:
            return 1.0
        if temp_min < -5:
            return 0.9
        if temp_min < 0:
            return 0.7
        if temp_min < 2:
            return 0.4
        if temp_min < 5:
            return 0.2
        return 0.0

    def _evaluar_nubosidad(self, cobertura: float) -> float:
        if cobertura < 10:
            return 1.0
        if cobertura < 20:
            return 0.9
        if cobertura < 40:
            return 0.6
        if cobertura < 70:
            return 0.2
        return 0.05

    def _evaluar_viento(self, velocidad: float) -> float:
        if velocidad < 1:
            return 1.0
        if velocidad < 2:
            return 0.85
        if velocidad < 3:
            return 0.7
        if velocidad < 5:
            return 0.4
        if velocidad < 8:
            return 0.15
        return 0.05

    def _evaluar_humedad(self, hr: float) -> float:
        if hr > 85:
            return 1.0
        if hr > 75:
            return 0.8
        if hr > 65:
            return 0.5
        if hr > 50:
            return 0.2
        return 0.05

    def _evaluar_tendencia(self, historia: list[float]) -> float:
        if not historia or len(historia) < 2:
            return 0.5
        tendencia = (historia[-1] - historia[0]) / (len(historia) - 1)
        if tendencia < -1:
            return 0.9
        if tendencia < -0.5:
            return 0.7
        if tendencia < 0:
            return 0.5
        return 0.2

    def _evaluar_punto_rocio(self, pr: float, temp_min: float) -> float:
        diferencia = temp_min - pr
        if diferencia < 1:
            return 0.9
        if diferencia < 2:
            return 0.7
        if diferencia < 3:
            return 0.4
        if diferencia < 5:
            return 0.15
        return 0.05

    def _generar_recomendaciones(
        self, prob: float, temp_min: float, severo: bool
    ) -> list[str]:
        recs: list[str] = []
        if severo:
            recs.extend(
                [
                    "ALERTA CRÍTICA: riesgo muy alto de daño por helada",
                    "Activar protección antihielo (riego por aspersión, mallas)",
                    "Monitorear temperatura entre 3–6 AM",
                ]
            )
        elif prob > 40:
            recs.extend(
                [
                    "ALERTA MODERADA: riesgo significativo de helada",
                    "Preparar sistemas de protección",
                    "Revisar pronóstico cada 6 h",
                ]
            )
        elif prob > 20:
            recs.append("Vigilancia: riesgo de helada débil")
        else:
            recs.append("Riesgo bajo de helada. Operaciones normales.")
        if temp_min < 0:
            recs.append("Evitar labores que expongan raíces")
            recs.append("NO regar por aspersión antes de la helada")
        return recs
