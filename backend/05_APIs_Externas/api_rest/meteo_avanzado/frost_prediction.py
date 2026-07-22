#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelo de riesgo de helada radiativa (cultivo + psicrómetro + factores Quillota)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .cultivo_helada import (
    POP_BAJA_MAX,
    clasificar_dano_cultivo,
    clasificar_probabilidad_boletin,
    evaluar_condiciones_atmosfericas_noche,
    factor_humedad_suelo,
    factor_oquedad_relieve,
    obtener_umbrales_cultivo,
)
from .meteo_utils import (
    calcular_bulbo_humedo,
    calcular_punto_rocio,
    estimar_temp_atardecer,
    evaluar_criterio_psicrometro,
)


class ModeloHeladaRadiativa:
    """Helada radiativa: atmósfera + Td/Th atardecer + umbrales por cultivo + relieve/suelo."""

    def __init__(self, estacion_id: str, altitud_m: float | None = None):
        self.estacion_id = estacion_id
        self.altitud_m = altitud_m

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
        cultivo: str = "palto",
        humedad_suelo_pct: float | None = None,
        precip_reciente_mm: float | None = None,
        suelo_descubierto: bool | None = None,
        altitud_m: float | None = None,
    ) -> dict[str, Any]:
        alt = altitud_m if altitud_m is not None else self.altitud_m
        t_atardecer = (
            temperatura_atardecer
            if temperatura_atardecer is not None
            else estimar_temp_atardecer(
                temperatura_pronosticada, temperatura_minima_pronosticada
            )
        )
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

        dano = clasificar_dano_cultivo(temperatura_minima_pronosticada, cultivo)
        umb = obtener_umbrales_cultivo(cultivo)
        atmos = evaluar_condiciones_atmosfericas_noche(
            cobertura_nubosa, velocidad_viento, humedad_relativa
        )
        oquedad = factor_oquedad_relieve(alt)
        suelo = factor_humedad_suelo(
            humedad_suelo_pct, precip_reciente_mm, suelo_descubierto
        )
        criterio = evaluar_criterio_psicrometro(
            td_atardecer, th_atardecer, cobertura_nubosa, velocidad_viento
        )

        temp_f = self._evaluar_temperatura_cultivo(
            temperatura_minima_pronosticada, umb
        )
        nub_f = self._evaluar_nubosidad(cobertura_nubosa)
        viento_f = self._evaluar_viento(velocidad_viento)
        # Baja HR nocturna favorece irradiación (no alta HR)
        hum_f = self._evaluar_humedad_baja_noche(humedad_relativa)
        tend_f = (
            self._evaluar_tendencia(historia_temperatura)
            if historia_temperatura
            else 0.5
        )
        rocio_f = self._evaluar_punto_rocio(td_atardecer, temperatura_minima_pronosticada)
        psico_f = self._evaluar_psicrometro(td_atardecer, th_atardecer)
        oquedad_f = float(oquedad["score"])
        suelo_f = float(suelo["score"])

        pesos = {
            "temperatura": 0.22,
            "nubosidad": 0.14,
            "viento": 0.12,
            "humedad": 0.08,
            "tendencia": 0.04,
            "rocio": 0.08,
            "psicrometro": 0.12,
            "oquedad": 0.10,
            "suelo": 0.10,
        }
        prob = (
            temp_f * pesos["temperatura"]
            + nub_f * pesos["nubosidad"]
            + viento_f * pesos["viento"]
            + hum_f * pesos["humedad"]
            + tend_f * pesos["tendencia"]
            + rocio_f * pesos["rocio"]
            + psico_f * pesos["psicrometro"]
            + oquedad_f * pesos["oquedad"]
            + suelo_f * pesos["suelo"]
        ) * 100

        if criterio["riesgo_inminente"]:
            prob = max(prob, 75.0)
        elif criterio["riesgo_alto"]:
            prob = max(prob, 60.0)
        if dano["severidad_cultivo"] == "critico" and atmos["favorables_irradiacion"]:
            prob = max(prob, 70.0)

        prob = min(100.0, prob)
        pop_boletin = clasificar_probabilidad_boletin(prob)

        riesgo_severo = (
            dano["severidad_cultivo"] == "critico" and prob > POP_BAJA_MAX
        ) or (criterio["riesgo_inminente"] and dano["alerta_cultivo"])
        riesgo_moderado = dano["severidad_cultivo"] in ("critico", "alto", "moderado") and (
            prob > 40 or criterio["riesgo_alto"]
        )
        if criterio["riesgo_inminente"]:
            riesgo_severo = True
            riesgo_moderado = True

        factores: list[str] = []
        if atmos["cielo_despejado"]:
            factores.append(f"Cielo despejado ({cobertura_nubosa:.0f}% nubosidad)")
        if atmos["viento_calma"]:
            factores.append(f"Viento en calma ({velocidad_viento:.1f} m/s)")
        if atmos["baja_humedad_nocturna"]:
            factores.append(
                f"Baja humedad nocturna ({humedad_relativa:.0f}% HR) — favorece irradiación"
            )
        if td_atardecer <= 0:
            factores.append(f"Punto de rocío al atardecer ≤ 0 °C (Td={td_atardecer:.1f})")
        elif abs(td_atardecer - temperatura_minima_pronosticada) < 3:
            factores.append("Punto de rocío cercano a T° mínima")
        if th_atardecer <= 2:
            factores.append(
                f"Bulbo húmedo al atardecer ≤ 2 °C (Th={th_atardecer:.1f}) — riesgo inminente"
            )
        if oquedad["nivel"] in ("alto", "medio"):
            factores.append(oquedad["mensaje"])
        if suelo["score"] >= 0.6:
            factores.append(suelo["mensaje"])
        if dano["tipo_helada"] != "sin_helada":
            factores.append(
                f"Helada {dano['tipo_helada']} para {dano['cultivo_nombre']} "
                f"(Tmín={temperatura_minima_pronosticada:.1f} °C, umbral crítico "
                f"{umb['critico']} °C)"
            )

        nivel_riesgo = self._nivel_riesgo(
            pop_boletin, dano, criterio, riesgo_severo, riesgo_moderado
        )

        return {
            "estacion_id": self.estacion_id,
            "fecha_pronostico": fecha.isoformat(),
            "cultivo": dano["cultivo"],
            "cultivo_nombre": dano["cultivo_nombre"],
            "probabilidad_helada": round(prob, 1),
            "probabilidad_boletin": pop_boletin,
            "riesgo_helada_radiativa": round(prob, 1),
            "temperatura_minima_esperada": round(temperatura_minima_pronosticada, 1),
            "temperatura_minima_absoluta": round(temperatura_minima_pronosticada, 1),
            "temperatura_maxima": round(temperatura_pronosticada, 1),
            "temperatura_atardecer": round(t_atardecer, 1),
            "punto_rocio": round(td_atardecer, 1),
            "punto_rocio_atardecer": round(td_atardecer, 1),
            "bulbo_humedo": round(th_atardecer, 1),
            "bulbo_humedo_atardecer": round(th_atardecer, 1),
            "dano_cultivo": dano,
            "umbral_cultivo": umb["critico"],
            "umbrales_cultivo": dano["umbrales"],
            "alerta_cultivo": dano["alerta_cultivo"],
            "tipo_helada": dano["tipo_helada"],
            "riesgo_severo": riesgo_severo,
            "riesgo_moderado": riesgo_moderado,
            "riesgo_inminente": criterio["riesgo_inminente"],
            "nivel_riesgo": nivel_riesgo,
            "hora_critica_esperada": "04:00",
            "factores_contribuyentes": factores,
            "criterio_psicrometro": criterio,
            "condiciones_atmosfericas": atmos,
            "factor_oquedad": oquedad,
            "factor_humedad_suelo": suelo,
            "recomendaciones": self._generar_recomendaciones(
                prob, temperatura_minima_pronosticada, riesgo_severo, criterio, dano
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
                "oquedad": round(oquedad_f * 100, 1),
                "suelo": round(suelo_f * 100, 1),
            },
        }

    def _evaluar_temperatura_cultivo(
        self, temp_min: float, umb: dict[str, Any]
    ) -> float:
        """Score según umbrales del cultivo (no un único 0 °C genérico)."""
        if temp_min <= umb["critico"] - 3:
            return 1.0
        if temp_min <= umb["critico"]:
            return 0.9
        if temp_min <= umb["alto"]:
            return 0.65
        if temp_min <= umb["moderado"]:
            return 0.35
        if temp_min <= umb["moderado"] + 2:
            return 0.15
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

    def _evaluar_humedad_baja_noche(self, hr: float) -> float:
        """Baja HR nocturna favorece pérdida de calor por irradiación."""
        if hr < 40:
            return 1.0
        if hr < 50:
            return 0.85
        if hr < 60:
            return 0.7
        if hr < 75:
            return 0.35
        return 0.1

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

    def _nivel_riesgo(
        self,
        pop_boletin: str,
        dano: dict[str, Any],
        criterio: dict[str, Any],
        riesgo_severo: bool,
        riesgo_moderado: bool,
    ) -> str:
        if criterio.get("riesgo_inminente"):
            return "Inminente"
        if pop_boletin == "alta" or riesgo_severo:
            return "Alto"
        if pop_boletin == "media" or dano["severidad_cultivo"] in ("critico", "alto"):
            return "Medio"
        if riesgo_moderado or dano["severidad_cultivo"] == "moderado":
            return "Moderado"
        if pop_boletin == "baja" and dano["severidad_cultivo"] == "bajo":
            return "Bajo"
        return "Vigilancia"

    def _generar_recomendaciones(
        self,
        prob: float,
        temp_min: float,
        severo: bool,
        criterio: dict[str, Any] | None = None,
        dano: dict[str, Any] | None = None,
    ) -> list[str]:
        recs: list[str] = []
        criterio = criterio or {}
        dano = dano or {}
        cultivo_n = dano.get("cultivo_nombre", "cultivo")
        pop = clasificar_probabilidad_boletin(prob)

        if criterio.get("riesgo_inminente"):
            recs.extend(
                [
                    f"RIESGO INMINENTE ({cultivo_n}): Th ≤ 2 °C + cielo despejado",
                    "Activar protección antihielo antes de medianoche",
                    "Monitorear temperatura entre 3–6 AM",
                ]
            )
        elif pop == "alta" or severo:
            recs.extend(
                [
                    f"ALERTA ALTA (boletin ≥90 %) para {cultivo_n}",
                    "Activar protección antihielo (riego por aspersión, mallas)",
                    "Monitorear temperatura entre 3–6 AM",
                ]
            )
        elif pop == "media" or criterio.get("riesgo_alto") or dano.get("alerta_cultivo"):
            recs.extend(
                [
                    f"ALERTA MEDIA (66–90 %) / umbral de {cultivo_n}",
                    "Preparar sistemas de protección",
                    "Revisar psicrómetro y pronóstico cada 6 h",
                ]
            )
        elif prob > 20:
            recs.append(f"Vigilancia baja (≤66 %) para {cultivo_n}")
        else:
            recs.append(f"Riesgo bajo para {cultivo_n}. Operaciones normales.")

        if dano.get("tipo_helada") == "agrometeorologica":
            recs.append(
                "Helada agrometeorológica: T° sobre 0 °C pero dentro del rango de daño del cultivo"
            )
        if temp_min <= 0:
            recs.append("Helada meteorológica (T° ≤ 0 °C): evitar labores que expongan tejidos")
        if dano.get("alerta_cultivo"):
            recs.append("Preferir riego previo (humedecer suelo) para aumentar inercia térmica")
        return recs
