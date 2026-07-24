# SINCA (MMA) — activación E12

Portal: https://sinca.mma.gob.cl

## Estaciones airshed Copiapó (nombres portal)

| Slug METGO | Nombre SINCA | Contaminantes típicos |
|------------|--------------|------------------------|
| `copiapo_centro` | Copiapó | PM2.5, PM10, SO2, NO2, O3 |
| `paipote` | Paipote | PM10, SO2 |
| `tierra_amarilla` | Tierra Amarilla | PM10 |

Los **IDs/keys** del portal cambian de formato (no hay API pública estable).
Procedimiento:

1. Abrir SINCA → región Atacama → estación.
2. Copiar el identificador de la URL o ficha.
3. Configurar en Render / `.env`:

```bash
METGO_SINCA_IDS='{"copiapo_centro":"KEY","paipote":"KEY2","tierra_amarilla":"KEY3"}'
METGO_SINCA_CSV_DIR=/data/sinca
# opcional, plantilla HTTP:
METGO_SINCA_CSV_URL='https://tu-bucket/sinca/{slug}.csv'
```

4. CSV diario por estación: `fecha,pm25,pm10,so2,no2,o3`
5. Cron (`/api/cron/sync`) llama `sincronizar_sinca()` → `aire_registros` (`fuente=sinca`, `tipo_dato=observado`).
6. Validar sesgo: `GET /api/public/aire/sinca/sesgo?estacion_id=copiapo_centro`

## Estado API

`GET /api/public/aire/sinca/estado`
