-- SPATI: sitios de izaje — mineras de alta montaña Chile (+ demos METGO)

CREATE TABLE IF NOT EXISTS public.spati_sitios_grua (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug            TEXT NOT NULL UNIQUE,
  nombre          TEXT NOT NULL,
  region          TEXT,
  operador        TEXT,
  lat             NUMERIC(9,6) NOT NULL CHECK (lat BETWEEN -56 AND -17),
  lon             NUMERIC(9,6) NOT NULL CHECK (lon BETWEEN -76 AND -66),
  altitud_msnm    NUMERIC(7,1) NOT NULL DEFAULT 0,
  altura_pluma_m  NUMERIC(5,1) NOT NULL CHECK (altura_pluma_m > 0),
  z0_terreno      NUMERIC(6,4) NOT NULL CHECK (z0_terreno > 0),
  tipo_terreno    TEXT,
  area_carga_m2   NUMERIC(7,2) NOT NULL DEFAULT 10.0,
  coef_forma_cd   NUMERIC(4,2) NOT NULL DEFAULT 1.2,
  fuerza_limite_n NUMERIC(12,1) NOT NULL DEFAULT 25000,
  faena_id        TEXT,
  estacion_metgo  TEXT,
  activo          BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.spati_pronosticos (
  id              BIGSERIAL PRIMARY KEY,
  sitio_slug      TEXT NOT NULL REFERENCES public.spati_sitios_grua(slug),
  run_timestamp   TIMESTAMPTZ NOT NULL,
  valid_time      TIMESTAMPTZ NOT NULL,
  v_modelo_10m    NUMERIC(5,1),
  v_fisica_grua   NUMERIC(5,1),
  v_mos_kmh       NUMERIC(5,1),
  v_final_kmh     NUMERIC(5,1) NOT NULL,
  dir_viento_deg  NUMERIC(5,1),
  rho_kg_m3       NUMERIC(6,4),
  fuerza_n        NUMERIC(9,1),
  pct_fuerza      NUMERIC(5,1),
  nivel_alerta    SMALLINT NOT NULL CHECK (nivel_alerta BETWEEN 0 AND 3),
  flag_critico    BOOLEAN NOT NULL DEFAULT FALSE,
  flag_meteo      BOOLEAN NOT NULL DEFAULT FALSE,
  razon_alerta    TEXT,
  modo_sin_mos    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (sitio_slug, run_timestamp, valid_time)
);

CREATE TABLE IF NOT EXISTS public.spati_mediciones_dron (
  id              BIGSERIAL PRIMARY KEY,
  sitio_slug      TEXT NOT NULL REFERENCES public.spati_sitios_grua(slug),
  timestamp_vuelo TIMESTAMPTZ NOT NULL,
  altura_m        NUMERIC(6,1) NOT NULL,
  velocidad_kmh   NUMERIC(5,1) NOT NULL,
  direccion_deg   NUMERIC(5,1),
  sesgo_calculado NUMERIC(5,2),
  operador        TEXT,
  modelo_dron     TEXT,
  payload_json    JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spati_pron_sitio_valid
  ON public.spati_pronosticos (sitio_slug, valid_time DESC);
CREATE INDEX IF NOT EXISTS idx_spati_dron_sitio_ts
  ON public.spati_mediciones_dron (sitio_slug, timestamp_vuelo DESC);

INSERT INTO public.spati_sitios_grua (
  slug, nombre, region, operador, lat, lon, altitud_msnm, altura_pluma_m, z0_terreno, tipo_terreno
) VALUES
  ('quebrada_blanca', 'Quebrada Blanca', 'Tarapacá', 'Teck Resources', -21.000000, -68.816667, 4400, 55, 0.25, 'rajo_minero'),
  ('collahuasi', 'Collahuasi', 'Tarapacá', 'Compañía Minera Doña Inés de Collahuasi', -20.964167, -68.661111, 4200, 55, 0.20, 'rajo_minero'),
  ('cerro_colorado', 'Cerro Colorado', 'Tarapacá', 'BHP', -20.059444, -69.270000, 2600, 55, 0.10, 'rajo_minero'),
  ('el_abra', 'El Abra', 'Antofagasta', 'Freeport-McMoRan', -21.920556, -68.832222, 4005, 55, 0.22, 'rajo_minero'),
  ('chuquicamata', 'Chuquicamata', 'Antofagasta', 'Codelco', -22.290556, -68.901944, 2860, 55, 0.35, 'rajo_minero'),
  ('radomiro_tomic', 'Radomiro Tomic', 'Antofagasta', 'Codelco', -22.216667, -68.900000, 2950, 55, 0.15, 'rajo_minero'),
  ('ministro_hales', 'Ministro Hales', 'Antofagasta', 'Codelco', -22.381667, -68.912222, 2600, 55, 0.20, 'rajo_minero'),
  ('spence', 'Spence', 'Antofagasta', 'BHP', -22.795556, -69.253333, 1725, 55, 0.05, 'llano_semiarido'),
  ('escondida', 'Escondida', 'Antofagasta', 'BHP', -24.251667, -69.054167, 3075, 55, 0.25, 'rajo_minero'),
  ('el_penon', 'El Peñón', 'Antofagasta', 'Yamana Gold', -24.410833, -69.496111, 2200, 45, 0.15, 'rajo_minero'),
  ('la_coipa', 'La Coipa', 'Atacama', 'Kinross Gold', -26.699722, -69.500000, 4000, 55, 0.18, 'valle_cordillera'),
  ('maricunga', 'Maricunga', 'Atacama', 'Kinross Gold', -27.533333, -69.300000, 4300, 55, 0.05, 'llano_semiarido'),
  ('candelaria', 'Candelaria', 'Atacama', 'Lundin Mining', -27.509722, -70.287500, 729, 55, 0.05, 'costero_abierto'),
  ('los_pelambres', 'Los Pelambres', 'Coquimbo', 'Antofagasta Minerals', -31.716667, -70.490556, 3600, 55, 0.30, 'valle_cordillera'),
  ('los_bronces', 'Los Bronces', 'Metropolitana', 'Anglo American', -33.150278, -70.287222, 3500, 55, 0.35, 'valle_cordillera'),
  ('andina', 'Andina', 'Valparaíso', 'Codelco', -33.061389, -70.250278, 3950, 55, 0.40, 'valle_cordillera'),
  ('el_teniente', 'El Teniente', 'O''Higgins', 'Codelco', -34.094167, -70.350833, 2300, 55, 0.30, 'valle_cordillera'),
  ('mantos_blancos_rajo', 'Mantos Blancos · Rajo', 'Antofagasta', 'METGO demo', -23.430000, -70.060000, 1100, 55, 0.15, 'rajo_minero'),
  ('paipote_izaje', 'Paipote · Izaje', 'Atacama', 'METGO demo', -27.406400, -70.285300, 810, 55, 0.12, 'rajo_minero')
ON CONFLICT (slug) DO UPDATE SET
  nombre = EXCLUDED.nombre,
  region = EXCLUDED.region,
  operador = EXCLUDED.operador,
  lat = EXCLUDED.lat,
  lon = EXCLUDED.lon,
  altitud_msnm = EXCLUDED.altitud_msnm,
  z0_terreno = EXCLUDED.z0_terreno,
  tipo_terreno = EXCLUDED.tipo_terreno;

ALTER TABLE public.spati_sitios_grua ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spati_pronosticos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spati_mediciones_dron ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS spati_sitios_select ON public.spati_sitios_grua;
CREATE POLICY spati_sitios_select ON public.spati_sitios_grua FOR SELECT USING (true);
DROP POLICY IF EXISTS spati_pron_select ON public.spati_pronosticos;
CREATE POLICY spati_pron_select ON public.spati_pronosticos FOR SELECT USING (true);
DROP POLICY IF EXISTS spati_dron_select ON public.spati_mediciones_dron;
CREATE POLICY spati_dron_select ON public.spati_mediciones_dron FOR SELECT USING (true);
