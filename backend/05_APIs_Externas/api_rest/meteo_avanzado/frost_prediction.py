#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de riesgo de helada radiativa (6 factores + criterio psicrómetro)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .meteo_utils import (
    calcular_bulbo_humedo,
    calcular_punto_rocio,
    estimar_temp_atardecer,
    evaluar_criterio_psicrometro,
)


class ModeloHeladaRadiativa:
    """Helada radiativa: cielo despejado + viento débil + Td/Th al atardecer."""

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
        temperatura_atardecer: float | None = None,
        bulbo_humedo: float | None = None,
    ) -> dict[str, Any]:
        t_atardecer = (
            temperatura_atardecer
            if temperatura_atardecer is not None
            else estimar_temp_atardecer(
                temperatura_pronosticada, temperatura_minima_pronosticada
            )
        )
        # Td/Th de atardecer: priorizar valores del caller (psicrómetro / core)
        td_atardecer = (
            float(punto_rocio)
            if punto_rocio is not None
            else calcular_punto_rocio(t_atardecer, humedad_relativa)
        )
        th_atardecer = (
            float(bulbo_humedo)
            if bulbo_humedo is not None
            else calcular_bulbo_humedo(t_atardecer, humedad_relativa)
        )
        temp_f = self._evaluar_temperatura(temperatura_minima_pronosticada)
        nub_f = self._evaluar_nubosidad(cobertura_nubosa)
        viento_f = self._evaluar_viento(velocidad_viento)
        hum_f = self._evaluar_humedad(humedad_relativa)
        tend_f = self._evaluar_tendencia(historia_temperatura) if historia_temperatura else 0.5
        rocio_f = self._evaluar_punto_rocio(td_atardecer, temperatura_minima_pronosticada)
        psico_f = self._evaluar_psicrometro(td_atardecer, th_atardecer)

        pesos = {
            "temperatura": 0.25,
            "nubosidad": 0.20,
            "viento": 0.15,
            "humedad": 0.10,
            "tendencia": 0.05,
            "rocio": 0.10,
            "psicrometro": 0.15,
        }
        prob = (
            temp_f * pesos["temperatura"]
            + nub_f * pesos["nubosidad"]
            + viento_f * pesos["viento"]
            + hum_f * pesos["humedad"]
            + tend_f * pesos["tendencia"]
            + rocio_f * pesos["rocio"]
            + psico_f * pesos["psicrometro"]
        ) * 100

        criterio = evaluar_criterio_psicrometro(
            td_atardecer, th_atardecer, cobertura_nubosa, velocidad_viento
        )
        if criterio["riesgo_inminente"]:
            prob = max(prob, 75.0)
        elif criterio["riesgo_alto"]:
            prob = max(prob, 60.0)

        riesgo_severo = prob > 70 and temperatura_minima_pronosticada < -2
        riesgo_moderado = prob > 40 and temperatura_minima_pronosticada < 0
        if criterio["riesgo_inminente"]:
            riesgo_severo = True
            riesgo_moderado = True

        factores = []
        if cobertura_nubosa < 20:
            factores.append(f"Cielo despejado ({cobertura_nubosa:.0f}% nubosidad)")
        if velocidad_viento < 3:
            factores.append(f"Viento débil ({velocidad_viento:.1f} m/s)")
        if humedad_relativa > 70:
            factores.append(f"Humedad alta ({humedad_relativa:.0f}%)")
        if td_atardecer <= 0:
            factores.append(f"Punto de rocío al atardecer ≤ 0 °C (Td={td_atardecer:.1f})")
        elif abs(td_atardecer - temperatura_minima_pronosticada) < 3:
            factores.append("Punto de rocío cercano a T° mínima")
        if th_atardecer <= 2:
            factores.append(
                f"Bulbo húmedo al atardecer ≤ 2 °C (Th={th_atardecer:.1f}) — riesgo inminente"
            )

        nivel_riesgo = "Bajo"
        if criterio["riesgo_inminente"] or riesgo_severo:
            nivel_riesgo = "Inminente" if criterio["riesgo_inminente"] else "Severo"
        elif riesgo_moderado or criterio["riesgo_alto"]:
            nivel_riesgo = "Alto" if criterio["riesgo_alto"] else "Moderado"
        elif prob > 20:
            nivel_riesgo = "Vigilancia"

        return {
            "estacion_id": self.estacion_id,
            "fecha_pronostico": fecha.isoformat(),
            "probabilidad_helada": round(min(100.0, prob), 1),
            "riesgo_helada_radiativa": round(min(100.0, prob), 1),
            "temperatura_minima_esperada": round(temperatura_minima_pronosticada, 1),
            "temperatura_minima_absoluta": round(temperatura_minima_pronosticada, 1),
            "temperatura_maxima": round(temperatura_pronosticada, 1),
            "temperatura_atardecer": round(t_atardecer, 1),
            "punto_rocio": round(td_atardecer, 1),
            "punto_rocio_atardecer": round(td_atardecer, 1),
            "bulbo_humedo": round(th_atardecer, 1),
            "bulbo_humedo_atardecer": round(th_atardecer, 1),
            "riesgo_severo": riesgo_severo,
            "riesgo_moderado": riesgo_moderado,
            "riesgo_inminente": criterio["riesgo_inminente"],
            "nivel_riesgo": nivel_riesgo,
            "hora_critica_esperada": "04:00",
            "factores_contribuyentes": factores,
            "criterio_psicrometro": criterio,
            "recomendaciones": self._generar_recomendaciones(
                prob, temperatura_minima_pronosticada, riesgo_severo, criterio
            ),
            "recomendacion": criterio["mensaje"],
            "scores_componentes": {
                "temperatura": round(temp_f * 100, 1),
                "nubosidad": round(nub_f * 100, 1),
                "viento": round(viento_f * 100, 1),
                "humedad": round(hum_f * 100, 1),
                "tendencia": round(tend_f * 100, 1),
                "punto_rocio": round(rocio_f * 100, 1),
                "psicrometro": round(psico_f * 100, 1),
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
        # Td ≤ 0 °C es señal fuerte de escarcha potencial
        if pr <= -2:
            return 1.0
        if pr <= 0:
            return 0.85
        diferencia = temp_min - pr
        if diferencia < 1:
            return 0.7
        if diferencia < 2:
            return 0.5
        if diferencia < 3:
            return 0.3
        if diferencia < 5:
            return 0.15
        return 0.05

    def _evaluar_psicrometro(self, td: float, th: float) -> float:
        """Score 0–1 del método de campo (Td + Th al atardecer)."""
        score = 0.0
        if th <= 0:
            score += 0.6
        elif th <= 2:
            score += 0.45
        elif th <= 4:
            score += 0.2
        if td <= -2:
            score += 0.4
        elif td <= 0:
            score += 0.35
        elif td <= 2:
            score += 0.15
        return min(1.0, score)

    def _generar_recomendaciones(
        self,
        prob: float,
        temp_min: float,
        severo: bool,
        criterio: dict[str, Any] | None = None,
    ) -> list[str]:
        recs: list[str] = []
        criterio = criterio or {}
        if criterio.get("riesgo_inminente"):
            recs.extend(
                [
                    "RIESGO INMINENTE (psicrómetro): Th ≤ 2 °C + cielo despejado",
                    "Activar protección antihielo antes de medianoche",
                    "Monitorear temperatura entre 3–6 AM",
                ]
            )
        elif severo:
            recs.extend(
                [
                    "ALERTA CRÍTICA: riesgo muy alto de daño por helada",
                    "Activar protección antihielo (riego por aspersión, mallas)",
                    "Monitorear temperatura entre 3–6 AM",
                ]
            )
        elif criterio.get("riesgo_alto") or prob > 40:
            recs.extend(
                [
                    "ALERTA: Td ≤ 0 °C o probabilidad significativa de helada radiativa",
                    "Preparar sistemas de protección",
                    "Revisar psicrómetro / pronóstico cada 6 h",
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
