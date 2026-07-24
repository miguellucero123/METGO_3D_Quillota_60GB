# SLOs METGO — etapa E10

> Definición operativa de objetivos de servicio. Medición vía `/api/health/sitios`
> y `/api/metrics` (Prometheus text). Alertas: Grafana Cloud (free) o cron que
> consulte health y notifique si `estado=critico`.

## Objetivos

| SLO | Objetivo | Cómo se mide | Alerta |
|-----|----------|--------------|--------|
| **API latencia** | p95 &lt; **800 ms** en endpoints cacheados (`/api/health`, `/api/public/*` calientes) | Histograma `metgo_http_request_duration_ms` / buckets en `/api/metrics` | p95 &gt; 800 ms 15 min |
| **Frescura aire** | Edad del último `aire_registros` &lt; **2 h** (Copiapó / Mantos) | `GET /api/health/sitios` → `frescura.aire.edad_horas` | `estado=critico` (&gt; 4 h) |
| **Frescura meteo** | Último registro meteo &lt; **24 h** | `frescura.meteo.edad_horas` | crítico &gt; 48 h |
| **Frescura operaciones** | Última ventana faena &lt; **3 h** (Mantos) | `frescura.operaciones.edad_horas` | crítico &gt; 6 h |
| **Disponibilidad API** | Uptime Render health &gt; **99 %** mes | `metgo_uptime_seconds` + checks externos | 2 fallos /api/health seguidos |

## Estados por sitio

| Estado | Criterio |
|--------|----------|
| `ok` | Todas las frescuras aplicables ≤ SLO |
| `degradado` | Alguna frescura &gt; SLO y ≤ 2× SLO, o `sin_datos` |
| `critico` | Alguna frescura &gt; 2× SLO |

## Endpoints

```http
GET /api/health                 # global (fase 10)
GET /api/health/sitios          # multi-sitio + frescura
GET /api/health/sitios?sitio=copiapo
GET /api/metrics                # Prometheus (público si METGO_METRICS_PUBLIC=1)
GET /api/metrics?format=json
```

## Grafana Cloud (checklist)

1. Crear cuenta free en Grafana Cloud.
2. Añadir scrape Prometheus → URL `https://metgo-api.onrender.com/api/metrics`.
3. Panel: `metgo_http_request_duration_ms` (heatmap / quantiles).
4. Panel: gauges `metgo_frescura_*_horas{sitio=…}`.
5. Alerta: `metgo_sitio_estado{sitio="copiapo"} == 2` (2=crítico).

## Sentry

- API: `METGO_SENTRY_DSN` → init en `observability.py`.
- SPAs: `VITE_SENTRY_DSN` (opcional; sin DSN no carga SDK).

## Carga (k6)

Script: `loadtests/k6_smoke.js` — 20 VUs × 30 s sobre `/api/health` y públicos cacheados.

## Fase

**E10** — `docs/roadmap/PLAN_MAESTRO_METGO_MULTISITIO.md`
