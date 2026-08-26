// ============================================
// VENTORA IZAJE - CONFIGURACIÓN PORTUARIA
// ============================================

export const appConfig = {
  // BRANDING
  appName: 'VENTORA Izaje Portuario',
  tagline: 'Pronóstico y Alerta para Operaciones Costeras',
  version: '1.0.0',

  // API BASE
  apiBaseURL: 'https://api.metgo3d.cl/spati/v2',

  // ============================================
  // PUERTOS CHILENOS
  // ============================================
  ports: {
    // ========== PUERTO DE IQUIQUE ==========
    IQQ: {
      name: 'Puerto de Iquique',
      region: 'Tarapacá',
      coordinates: [-20.2058, -70.1608],
      type: 'general-cargo',
      operatingHours: '24/7',
      cranes: [
        {
          id: 'STS-01',
          type: 'STS',
          model: 'Liebherr CBG700',
          maxOutreach: 58,
          maxHeight: 72,
          maxWind: 72, // km/h (sin restricción)
        },
        {
          id: 'RTG-02',
          type: 'RTG',
          maxHeight: 18,
          maxWind: 56,
        },
      ],
      anchorage: {
        depth: 14,
        holdingGood: 'mud',
        numBuoys: 4,
      },
    },

    // ========== PUERTO VENTANAS ==========
    ventanas_muelle: {
      name: 'Puerto Ventanas (Muelle)',
      region: 'Valparaíso',
      coordinates: [-32.748, -71.482],
      type: 'bulk-carrier',
      operatingHours: '24/7',
      cranes: [
        {
          id: 'STS-VTM',
          type: 'STS',
          maxHeight: 65,
          maxWind: 70,
        },
      ],
      anchorage: {
        depth: 16,
        holdingGood: 'sand',
        numBuoys: 2,
      },
    },

    // ========== PUERTO DE ANTOFAGASTA ==========
    ANF: {
      name: 'Puerto de Antofagasta',
      region: 'Antofacasta',
      coordinates: [-23.6500, -70.4000],
      type: 'mining-export',
      cranes: [
        {
          id: 'STS-03',
          type: 'STS',
          maxHeight: 65,
          maxWind: 70,
        },
      ],
      anchorage: {
        depth: 18,
        holdingGood: 'sand',
        numBuoys: 6,
      },
    },

    // ========== PUERTO DE VALPARAÍSO ==========
    VLP: {
      name: 'Puerto de Valparaíso',
      region: 'Valparaíso',
      coordinates: [-33.0473, -71.6127],
      type: 'container-general',
      cranes: [
        {
          id: 'STS-04',
          type: 'STS',
          maxHeight: 75,
          maxWind: 72,
        },
        {
          id: 'MHC-05',
          type: 'MHC',
          maxHeight: 42,
          maxWind: 65,
        },
      ],
      anchorage: {
        depth: 12,
        holdingGood: 'mud-sand',
        numBuoys: 8,
      },
    },

    // ========== PUERTO DE SAN ANTONIO ==========
    SAN: {
      name: 'Puerto de San Antonio',
      region: 'O\'Higgins',
      coordinates: [-33.5936, -71.6127],
      type: 'container-breakbulk',
      cranes: [
        {
          id: 'STS-06',
          type: 'STS',
          maxHeight: 70,
          maxWind: 72,
        },
      ],
      anchorage: {
        depth: 10,
        holdingGood: 'mud',
        numBuoys: 5,
      },
    },

    // ========== PUERTO MONTT ==========
    PMC: {
      name: 'Puerto Montt',
      region: 'Los Lagos',
      coordinates: [-41.3196, -72.1533],
      type: 'general-breakbulk',
      cranes: [
        {
          id: 'RTG-07',
          type: 'RTG',
          maxHeight: 16,
          maxWind: 55,
        },
      ],
      anchorage: {
        depth: 20,
        holdingGood: 'mud',
        numBuoys: 3,
      },
    },
  },

  // ============================================
  // RESTRICCIONES POR ALTURA DE CARGA
  // ============================================
  // Umbrales de viento (km/h) según altura de carga sobre cubierta
  liftRestrictions: {
    // ALTURA 10m (Container, carga pequeña)
    '10m': {
      label: 'Carga 10m (Container 20\', carga pequeña)',
      thresholds: {
        GREEN: { wind: 35, gust: 50, waves: 1.5, visibility: 500 },
        YELLOW: { wind: 35, gust: 50, waves: 2.5, visibility: 300 },
        RED: { wind: 50, gust: 70, waves: 3.0, visibility: 200 },
      },
      color: '#10b981', // Green
      icon: 'CheckCircle',
    },

    // ALTURA 40m (Container 40\', carga mediana)
    '40m': {
      label: 'Carga 40m (Container FEU, carga mediana)',
      thresholds: {
        GREEN: { wind: 30, gust: 45, waves: 1.2, visibility: 500 },
        YELLOW: { wind: 30, gust: 45, waves: 2.0, visibility: 300 },
        RED: { wind: 45, gust: 65, waves: 2.5, visibility: 200 },
      },
      color: '#f59e0b', // Amber
      icon: 'AlertCircle',
    },

    // ALTURA 100m (Carga pesada, grúa STS plena)
    '100m': {
      label: 'Carga 100m (Pesada, STS plena extensión)',
      thresholds: {
        GREEN: { wind: 25, gust: 40, waves: 0.8, visibility: 500 },
        YELLOW: { wind: 25, gust: 40, waves: 1.5, visibility: 300 },
        RED: { wind: 40, gust: 60, waves: 2.0, visibility: 200 },
      },
      color: '#f97316', // Orange
      icon: 'AlertTriangle',
    },

    // ALTURA 200m (Carga crítica, máxima altura)
    '200m': {
      label: 'Carga 200m (Crítica, máxima altura de operación)',
      thresholds: {
        GREEN: { wind: 20, gust: 35, waves: 0.5, visibility: 500 },
        YELLOW: { wind: 20, gust: 35, waves: 1.0, visibility: 300 },
        RED: { wind: 35, gust: 55, waves: 1.5, visibility: 200 },
      },
      color: '#dc2626', // Red
      icon: 'AlertOctagon',
    },
  },

  // ============================================
  // CONDICIONES DE FONDAJE (BUQUES ANCLADOS)
  // ============================================
  anchorageConditions: {
    GREEN: {
      maxWind: 25, // km/h
      maxWaves: 1.5, // m
      maxCurrents: 1.5, // nudos
      minVisibility: 500, // m
      maxShipHeal: 5, // grados
    },
    YELLOW: {
      maxWind: 35,
      maxWaves: 2.5,
      maxCurrents: 2.0,
      minVisibility: 300,
      maxShipHeal: 10,
    },
    RED: {
      maxWind: 50,
      maxWaves: 4.0,
      maxCurrents: 2.5,
      minVisibility: 100,
      maxShipHeal: 15,
    },
  },

  // ============================================
  // PARÁMETROS OCEANOGRÁFICOS
  // ============================================
  oceanParameters: {
    // VIENTO - Alturas estándar de medición
    wind: {
      referenceHeight: 10, // metros (WMO standard)
      measurementHeights: [10, 40, 100, 200], // metros (para extrapolación)
      roughnessLength: 0.0002, // mar abierto
    },

    // OLEAJE
    waves: {
      minHs: 0.0,
      maxHs: 12.0,
      typicalTp: 10, // segundos, período de pico
      swellSeason: 'Abr-Sep', // mayor período largo en austral invierno
    },

    // MAREAS
    tides: {
      reference: 'MLWS', // Mean Low Water Springs
      meanRange: 1.1, // metros (Iquique típico)
      springRange: 1.3,
    },

    // CORRIENTES LITORALES
    currents: {
      maxDriftSpeed: 2.5, // nudos
      typicalDirection: 'NNE', // norte por humboldt
    },

    // VISIBILIDAD
    visibility: {
      excellent: 5000, // m
      good: 2000,
      poor: 500,
      critical: 200,
      fogSeasonMonths: [6, 7, 8, 9], // Jun-Sep
    },
  },

  // ============================================
  // UMBRALES DE ALERTA GLOBAL
  // ============================================
  alertThresholds: {
    // Viento sostenido (3+ horas)
    sustainedWindRED: 50, // km/h
    sustainedWindYELLOW: 35,

    // Ráfagas instantáneas
    gustRED: 70, // km/h
    gustYELLOW: 50,

    // Oleaje de período largo (CRÍTICO para buques)
    swellTpCritical: 16, // segundos
    swellTpWarning: 14,

    // Resonancia de oscilación (cable + carga)
    pendulumRessonanceRange: 2, // segundos (|Tpendulum - Tswell| < 2s = ROJO)

    // Índice de Tensión en Espigas (ITE)
    ITE_RED: 85, // porcentaje
    ITE_YELLOW: 70,
    ITE_GREEN: 50,
  },

  // ============================================
  // TEMA Y COLORES
  // ============================================
  theme: {
    colors: {
      GREEN: '#10b981', // Operación segura
      YELLOW: '#f59e0b', // Alerta, restricción
      RED: '#dc2626', // Suspensión
      CRITICAL: '#7c3aed', // Crítica (resonancia, heave extremo)
      neutral: '#6b7280',
    },
    typography: {
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont',
      sizeBase: 14,
    },
  },

  // ============================================
  // INTEGRACIÓN API
  // ============================================
  api: {
    spatiEndpoint: '/forecast/72h',
    sensorsEndpoint: '/sensors/current',
    tidesEndpoint: '/tides/iquique',
    alertsEndpoint: '/alerts/active',
    pollInterval: 300000, // 5 minutos
  },
};

export default appConfig;
