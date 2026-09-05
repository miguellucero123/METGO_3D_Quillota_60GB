# Política de fuentes meteorológicas METGO

**Alcance:** Quillota primero · 2026-09-04  
**Relacionado:** `ESTACIONES_OFICIALES_QUILLOTA.md`, `oficiales_service.py`, `openmeteo_ciclo.py`

## Principio

| Capa | Qué es | Fuente primaria | Fallback |
|------|--------|-----------------|----------|
| Observado (ahora / histórico medido) | Estación real | **DMC** o **Agromet** (si hay código + CSV/API) | `meteo_store` last rows → Open-Meteo archive |
| Pronóstico (7d, mapas, NWP) | Modelo | **Open-Meteo** ciclo 00/12 UTC | last-good del ciclo · **no inventar** |
| Aire | Calidad aire | **SINCA** | CSV ejemplo solo demo |

DMC/Agromet **no sustituyen** el pronóstico NWP. Complementan con medición.

## Open-Meteo (operación)

- `METGO_OPENMETEO_FETCH_MODE=ciclo` (default): descargas en cron 00/12 UTC.  
- No martillar OM en cada request ni en cada `/health`.  
- Timeouts: `METGO_OPENMETEO_TIMEOUT`, reintentos `METGO_OPENMETEO_RETRIES`, cooldown `METGO_OPENMETEO_COOLDOWN`.  
- Health: `openmeteo=true` si hay **live** o **dato usable** (last-good / store).  
  Campos: `openmeteo_live`, `lastgood_age_s`, `ciclo_utc`, `fuente_activa`, `openmeteo_cooldown_s`.

## Etiquetas en API / SPA

| `fuente` | Significado |
|----------|-------------|
| `openmeteo` / `openmeteo_*` | Modelo / archive OM |
| `dmc` | Observado DMC |
| `agromet` | Observado INIA Agromet |
| `lastgood` / `supabase_db` | Caché o store (puede ser cualquiera previo) |

UI Quillota: badge de fuente + `TipoDatoBadge` (observado / pronóstico).

## Alternativas NWP (evaluación — no swap ciego)

| Candidato | Rol | Decisión |
|-----------|-----|----------|
| Open-Meteo | NWP multi-modelo | **Primario** corto plazo |
| DMC / Agromet | Observado | Activar E12 (piloto Quillota) |
| NOAA GFS / ECMWF open | NWP-2 | Spike si OM degradado &gt; ~20 % del tiempo en 14 días **y** last-good insuficiente |
| Meteoblue / comercial | NWP pago | Solo si cliente exige SLA contractual |

## Métrica

Seguir `/api/health`: ratio `openmeteo_live=false` con `openmeteo_usable=true` (OK) vs ambos false (incidente).
