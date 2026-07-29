# Plan integración METGO Quillota ↔ METGO Paine

> **Objetivo:** armonizar ambos productos (design system, gráficos, datos y API) manteniendo la identidad y el objetivo de cada uno: Quillota = AgriTech operacional (verde `#00ffaa`), Paine = clima outdoor/criósfera (cian `#22d3ee`).
>
> **Repos:** Quillota `D:\METGO_3D_Quillota_60GB` · Paine `D:\metgo-paine` (GitHub `miguellucero123/metgo-paine`).
>
> **Hosting Paine (2026-07-28):** canónico **Cloudflare Pages** (`metgo-paine` / `https://metgo-paine.pages.dev`). Netlify solo compatibilidad (stop builds tras cutover). Auth JWT E9 (`METGO_PASSWORD_PAINE` en Render). Módulo Carretera Austral en `/carretera` (**Leaflet + OpenStreetMap**, sin Google Maps).
>
> **Estado base (2026-07-23):** Paine ya usa el shell Quillota (header + sidebar + tokens dark) con acento cian y rutas `/`, `/estado`, `/meteo`, `/meteo/precipitacion`.
>
> **Visión extendida:** este plan es la base (E0–E5) del **`PLAN_MAESTRO_METGO_MULTISITIO.md`** (E6–E12: template multi-sitio, Copiapó calidad del aire, Mantos Blancos minería, clase mundial).

---

## Etapa 0 — Pre-trabajo en Quillota (cerrar pendientes de fases)

> **Estado (2026-07-23):** Etapa 0.1 docs — fase-2/01 y fichas DT hechas.  
> **2026-07-24:** §6.3 ML Δ cerrado; sync maestro §4; DT-1 docs paths actualizados.

### 0.1 Sincronizar docs desalineados (rápido, solo documentación)

La auditoría detectó checklists que contradicen el código ya desplegado:

| Doc | Problema | Acción |
|-----|----------|--------|
| `docs/PROMPT_MEJORAS_ORDEN_METEO_AGRICOLA_GRAFICOS.md` §6.3 | 11 `[ ]` pero ECharts/WindRose/Combo/selector histórico YA existen | Marcar hechos; dejar solo gaps reales (ver 0.2) |
| `docs/roadmap/fase-2/01-migrar-dashboards-vue.md` | Estado `pendiente` pero las 3 vistas existen | Actualizar a `hecho` |
| `docs/PROMPT_REVISION_COMPLETA_SISTEMA.md` | `[ ]` tablas meteo que CHECKLIST_E marca hechas | Cruzar y marcar |
| `docs/roadmap/deuda-tecnica/` | README apunta a fichas DT-2 / DT-3 inexistentes | Crear fichas mínimas |

### 0.2 Gaps reales de gráficos §6.3 (los que tocaremos al compartir charts)

- [x] Leyenda toggle interactiva en `TimeSeriesChart`
- [x] Click en barra (`HorizontalBarChart`) → set `estacionActiva` + navegar `/meteo` (consistente en todas las vistas)
- [x] Export PNG universal (ya existe en algunos; unificar helper)
- [x] Skeleton loaders unificados para cargas OpenMeteo largas
- [x] ML: barras agrupadas con Δ coloreado (tooltip Δ ML−obs + color por |error|)

**Por qué antes:** el trío `TimeSeriesChart` / `ComboMeteoChart` / `HorizontalBarChart` se copiará a Paine; mejor portarlos ya mejorados y no mantener dos versiones.

### 0.3 Pendientes de fases que NO bloquean (registrar, no ejecutar ahora)

- Códigos Agromet/DMC reales (`fase-3/estaciones_oficiales_mapeo.md`) — sigue diferido
- Multi-tenant real / aislamiento por organización (escalamiento §10.2)
- Fase 3.5 Streamlit dedicado — decisión de negocio
- SMTP Zoho/ZeptoMail (fases 6–7)
- DT-1 rutas hardcodeadas

---

## Etapa 1 — Design system compartido (tokens + tema ECharts site-aware)

> **Estado (2026-07-23):** hecho — `echartsTheme.js` lee `--color-primary` / accent en runtime.

### 1.1 Un solo archivo de tokens

- Fuente de verdad: `frontend/vue/src/assets/main.css` (Quillota)
- La identidad queda reducida a un bloque de ~8 variables por sitio:
  - Quillota: `--color-primary: #00ffaa` (+hover/muted/subtle/glow)
  - Paine: `--color-primary: #22d3ee`
- Script de sync (`scripts/compat/sync_tokens_paine.py` o copia manual documentada) para propagar cambios estructurales a `D:\metgo-paine\src\styles\main.css` sin pisar el bloque de identidad

### 1.2 Tema ECharts leyendo tokens CSS (clave)

- Modificar `frontend/vue/src/utils/echartsTheme.js`: los colores `verde`, `celeste`, etc. se resuelven en runtime con `getComputedStyle(document.documentElement).getPropertyValue('--color-primary')` (con fallback al hex actual)
- Resultado: el MISMO archivo pinta verde en Quillota y cian en Paine
- Riesgo nulo en Quillota: el token vale exactamente `#00ffaa`

**Verificación:** `npm run dev` en Quillota → gráficos idénticos a hoy; snapshot visual de DashboardView.

---

## Etapa 2 — Gráficos ECharts en Paine

> **Estado (2026-07-23):** hecho — TimeSeries / Combo / HorizontalBar en Dashboard, LugarDetalle, Precipitación.

### 2.1 Dependencias

```bash
cd D:\metgo-paine
npm i echarts vue-echarts
```

### 2.2 Portar componentes (con las mejoras 0.2 incluidas)

| Componente | Destino en Paine | Reemplaza |
|------------|------------------|-----------|
| `TimeSeriesChart.vue` | `LugarDetalle.vue` — tendencia máx/mín con banda | SVG polyline manual |
| `ComboMeteoChart.vue` | `DashboardView.vue` — T° + precipitación 7 días del lugar destacado | (nuevo) |
| `HorizontalBarChart.vue` | `PrecipitacionView.vue` — ranking lugares por precipitación | Barras CSS |
| `utils/echartsTheme.js` | `src/utils/` | (nuevo, site-aware) |

- Adaptar imports (Paine usa Vuex y alias `@utils`, no Pinia)
- `HorizontalBarChart` con click → navegar a `/lugar/:id` (equivalente Paine del click→estación)

**Verificación:** `npm run build` + smoke en `http://localhost:5174` (detalle de lugar, panel, precipitación).

---

## Etapa 3 — Datos compartidos: campo `sitio` + endpoint + contrato

> **Estado (2026-07-23):** hecho en código — catálogo `estaciones_catalogo.py`, `?sitio=paine|quillota`, OpenAPI, CORS example, migración SQL `estaciones`. Aplicar SQL en Supabase Dashboard cuando se despliegue. ETL Paine aún no incluido (cuota OpenMeteo).

### 3.1 Migración Supabase

- `supabase/migrations/<ts>_sitio_estaciones.sql`:
  - `ALTER TABLE estaciones ADD COLUMN sitio text NOT NULL DEFAULT 'quillota';`
  - Índice `(sitio)`
  - Seed 5–6 puntos TDP (`sitio='paine'`): Base Torres, Glaciar Grey, Valle Francés, Paine Grande, Laguna Amarga (coords de `metgo-paine/src/data/lugares.js`)

### 3.2 API Flask (contract-first)

- `openapi.yaml`: parámetro `sitio` (enum `quillota|paine`, default `quillota`) en `/api/meteo/estaciones` y donde aplique
- Repositorio/endpoint: filtro `sitio` con default `quillota` → **cero impacto** en la SPA actual
- CORS: agregar dominio Netlify de Paine a la allowlist
- Tests: casos `sitio=paine`, default, y `MockTable` de `tests/conftest.py` si hace falta

### 3.3 ETL

- El ETL nocturno itera estaciones desde BD → al existir filas `paine`, TDP acumula histórico automáticamente (validar que no exceda cuota OpenMeteo; si es necesario, flag `etl_sitios=quillota,paine`)

**Verificación:** `GET /api/meteo/estaciones?sitio=paine` en Render devuelve puntos TDP; la SPA Quillota no cambia.

---

## Etapa 4 — Paine consume metgo-api

> **Estado (2026-07-23):** hecho — `metgoApiService.js` + `weatherService` (API → Open-Meteo → caché); endpoint público `/api/public/meteo/{id}/pronostico`. Configurar `VITE_METGO_API` en Netlify.

- `D:\metgo-paine\.env` / Netlify: `VITE_API_BASE=https://metgo-api.onrender.com/api`
- Nuevo `src/services/metgoApiService.js`: estaciones + pronóstico por `sitio=paine`
- `weatherService.js` queda como **fallback** (Render free duerme): si la API falla → Open-Meteo directo → caché localStorage (cadena ya existente)
- Mapear respuesta API → forma `pronosticoSemanal` actual (sin tocar vistas)

**Verificación:** Panel Paine muestra fuente "metgo-api" y con la API caída sigue funcionando (fallback).

---

## Etapa 5 — Backports Paine → Quillota (sin perder identidad)

> **Estado (2026-07-23):** hecho — toggle Tarjetas|Tabla en `MeteoView`; selector °C/°F en `MetgoHeader`; `EstacionCard` en Comparativo (clic → `/meteo`).

| Qué | Dónde en Quillota | Nota |
|-----|-------------------|------|
| Toggle **Tarjetas \| Tabla** del pronóstico | `MeteoView.vue` | Hecho (`vistaPronostico`) |
| Selector **°C/°F** en header | `MetgoHeader.vue` + `useFormatTemp` | Hecho (`preferences.tempUnit`) |
| Cards tipo `PlaceCard` para sectores/estaciones | `ComparativoEstacionesView` + `EstacionCard.vue` | Badge riesgo helada/riego; tabla favoritos debajo |

**Verificación:** smoke visual + `npm run build` en `frontend/vue`.

---

## Etapa 6 — Posterior (fuera de este plan E0–E5; ver plan maestro)

> **E6 plantilla:** ver `PLAN_MAESTRO_METGO_MULTISITIO.md` y `templates/metgo-site-template/` (hecho 2026-07-23).

- Auth unificada: login Paine contra JWT metgo-api con `tenant: paine`; favoritos/preferencias server-side (fase 3.x multi-tenant real)
- Agromet/DMC códigos reales (Etapa E / fase 3)
- MINAGRI/DMC APIs (largo plazo escalamiento)

---

## Orden de ejecución y riesgo

| # | Etapa | Repo(s) | Riesgo | Depende de |
|---|-------|---------|--------|------------|
| 1 | 0.1 docs sync + fichas DT | Quillota | Nulo | — |
| 2 | 0.2 gaps gráficos §6.3 | Quillota | Bajo | — |
| 3 | 1 tokens + tema site-aware | Ambos | Nulo | — |
| 4 | 2 charts en Paine | Paine | Nulo | 3 |
| 5 | 3 migración sitio + API + OpenAPI | Quillota/Supabase | Bajo | — |
| 6 | 4 Paine → metgo-api | Paine + Render | Bajo | 5 |
| 7 | 5 backports UX | Quillota | Bajo | 2 |

Commits/push/deploy: solo con instrucción explícita del usuario (regla 5 AGENTS.md). Cloudflare Pages Paine redeploya al push a `main` de `metgo-paine` (o `npm run pages:deploy`).

## Fase roadmap

- Etapa 0: DT-x + cierre documental fases 2–3
- Etapas 1–2, 5: fase 2.x (producto ampliado / UI)
- Etapas 3–4: fase 2.x–3.x (multi-valle / multi-sitio, escalamiento §10.2)
