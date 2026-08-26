// ============================================
// OCEANOGRAFÍA PORTUARIA - CÁLCULOS CRÍTICOS
// ============================================

import appConfig from '@/site.config.js';

/**
 * PERFIL LOGARÍTMICO DE VIENTO
 * Extrapola viento desde 10m a alturas de interés (40, 100, 200m)
 * Basado en: v(z) = (u_star/kappa) * ln(z / z0)
 * donde u_star = friction velocity, kappa = von Kármán (0.4), z0 = roughness length
 */
export function windProfile(wind10m, heightM = 10, z0 = 0.0002) {
  const kappa = 0.4;
  const z_ref = 10;

  // Estima friction velocity desde viento a 10m
  const u_star = wind10m * kappa / Math.log(z_ref / z0);

  // Extrapola a altura target
  const windAtHeight = (u_star / kappa) * Math.log(heightM / z0);

  return Math.max(0, windAtHeight);
}

/**
 * CALCULA VIENTO EN MÚLTIPLES ALTURAS (para grúas)
 */
export function windProfileMulti(wind10m, z0 = 0.0002) {
  const heights = [10, 40, 100, 200];
  return heights.reduce((acc, h) => {
    acc[h] = windProfile(wind10m, h, z0);
    return acc;
  }, {});
}

/**
 * ÍNDICE DE TENSIÓN EN ESPIGAS (ITE)
 * Combina:
 * - Fuerza de viento (función cuadrática de velocidad)
 * - Oscilación de carga (función de período del swell)
 * - Movimiento del buque (heave, roll)
 *
 * ITE = 100 * [ (Fwind/Fmax)² + (Fosc/Fmax)² + (Fship/Fmax)² ] ^ 0.5
 */
export function calculateITE(
  windSpeedMs,
  waveHeightM,
  wavePeriodS,
  shipHeaveM = 0.1,
  shipRollDeg = 0,
  loadMassKg = 20000
) {
  // Parámetros de carga
  const Cd = 1.2; // coeficiente aerodinámico
  const rho = 1.225; // densidad aire
  const A = 6.3 * 1.5; // área frontal aprox (10m x 1.5m de banda típica)

  // FUERZA DE VIENTO
  const F_wind = 0.5 * rho * windSpeedMs ** 2 * A * Cd;

  // FUERZA DE OSCILACIÓN (oleaje)
  const T_pendulum = 2 * Math.PI * Math.sqrt(30 / 9.81); // cable ~30m
  const frequency_swell = 1 / wavePeriodS;
  const frequency_pendulum = 1 / T_pendulum;

  // Resonancia: si frecuencias cercanas, amplificación
  const resonanceFactor = Math.abs(frequency_swell - frequency_pendulum) < 0.05 ? 2.5 : 1.0;

  const F_oscillation =
    (loadMassKg * 9.81 * (waveHeightM / 2) * resonanceFactor) / T_pendulum;

  // FUERZA POR MOVIMIENTO DE BUQUE
  const F_ship = loadMassKg * 9.81 * (shipHeaveM / 10) * (1 + shipRollDeg / 90);

  // FUERZA MÁXIMA TOLERABLE (a 10m altura, condición estática)
  const F_max = loadMassKg * 9.81; // peso estático

  // ÍNDICE COMBINADO
  const combined = Math.sqrt(
    (F_wind / F_max) ** 2 +
    (F_oscillation / F_max) ** 2 +
    (F_ship / F_max) ** 2
  );

  const ITE = Math.min(100, combined * 100);

  return {
    ITE: Math.round(ITE),
    components: {
      wind: Math.round((F_wind / F_max) * 100),
      oscillation: Math.round((F_oscillation / F_max) * 100),
      ship: Math.round((F_ship / F_max) * 100),
    },
    resonanceFactor,
    riskLevel: ITE > 85 ? 'RED' : ITE > 70 ? 'YELLOW' : 'GREEN',
  };
}

/**
 * MAREA ASTRONÓMICA SINTÉTICA
 * Predicción armónica simplificada para 72h
 * Basada en componentes M2, S2, K1, O1 de SHOA
 */
export function predictTides(startDate = new Date(), hoursAhead = 72) {
  const predictions = [];
  const M2_amplitude = 0.42;
  const M2_phase = 25;
  const S2_amplitude = 0.15;
  const K1_amplitude = 0.18;

  for (let h = 0; h < hoursAhead; h++) {
    const t = startDate.getTime() + h * 3600 * 1000;
    const date = new Date(t);

    // Horas desde época
    const hours = date.getTime() / 3600000;

    // Componentes armónicos
    const M2 = M2_amplitude * Math.cos((hours * 2 * Math.PI) / 12.42 + (M2_phase * Math.PI) / 180);
    const S2 = S2_amplitude * Math.cos((hours * 2 * Math.PI) / 12);
    const K1 = K1_amplitude * Math.cos((hours * 2 * Math.PI) / 24);

    const level = 0.75 + M2 + S2 + K1; // ref MLWS + offset

    predictions.push({
      timestamp: date.toISOString(),
      hour: h,
      levelM: Math.round(level * 100) / 100,
      label: date.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }),
    });
  }

  return predictions;
}

/**
 * DETERMINACIÓN DE ESTADO (GREEN/YELLOW/RED)
 * según altura de carga y condiciones meteorológicas
 */
export function determineStatus(
  windKmh,
  gustKmh,
  waveHeightM,
  visibilityM,
  selectedHeight = '40m'
) {
  const config = appConfig.liftRestrictions[selectedHeight];

  if (!config) return { status: 'UNKNOWN', reason: 'Altura no configurada' };

  const thresholds = config.thresholds;

  // ROJO: Si excede RED
  if (
    windKmh > thresholds.RED.wind ||
    gustKmh > thresholds.RED.gust ||
    waveHeightM > thresholds.RED.waves ||
    visibilityM < thresholds.RED.visibility
  ) {
    return {
      status: 'RED',
      reason: `Excede límites: viento ${windKmh}km/h, olas ${waveHeightM}m, visib ${visibilityM}m`,
      color: appConfig.theme.colors.RED,
    };
  }

  // AMARILLO: Si está entre YELLOW y RED
  if (
    windKmh > thresholds.YELLOW.wind ||
    gustKmh > thresholds.YELLOW.gust ||
    waveHeightM > thresholds.YELLOW.waves ||
    visibilityM < thresholds.YELLOW.visibility
  ) {
    return {
      status: 'YELLOW',
      reason: 'Alerta: Restricción operativa',
      color: appConfig.theme.colors.YELLOW,
    };
  }

  // VERDE: Dentro de límites operativos
  return {
    status: 'GREEN',
    reason: 'Operación segura autorizada',
    color: appConfig.theme.colors.GREEN,
  };
}

export default {
  windProfile,
  windProfileMulti,
  calculateITE,
  predictTides,
  determineStatus,
};
