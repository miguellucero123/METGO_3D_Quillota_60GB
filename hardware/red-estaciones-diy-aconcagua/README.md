# Red de estaciones meteorológicas DIY — Valle de Aconcagua

Nodos **ESP32 + LoRa** de bajo costo (~USD 100–120/unidad) para agricultura y minería, integrados al stack METGO 3D vía MQTT → InfluxDB → API IoT.

| Capa | Ubicación |
|------|-----------|
| Firmware PlatformIO | `firmware/` |
| Gateway RPi (ChirpStack, Mosquitto, Influx, Grafana) | `gateway/` |
| BOM y presupuesto red | `bom/` |
| Pinout / esquema PCB | `pcb/` |
| Config por estación | `stations/` |
| Puente → API METGO | `integration/` |
| Plan de fases | `PLAN.md` |

## Arquitectura (resumen)

```text
[Sensores] → ESP32 (wake/mide/log SD/LoRa/duerme)
                │ LoRaWAN SF7–SF10
                ▼
         Gateway RPi + ChirpStack
                │ MQTT
                ▼
         decoder.py (calibración + QC)
                │
         InfluxDB 2.x ← Grafana
                │
         metgo_ingest.py → POST /api/iot (METGO)
```

## Arranque rápido

1. **Firmware:** editar `STATION_ID` y `LORA_SF` en `firmware/include/config.h` → `pio run -t upload`
2. **Gateway:** `cp gateway/.env.example gateway/.env` → `docker compose -f gateway/docker-compose.yml up -d`
3. **Token:** tras el primer arranque, regenerar `INFLUX_TOKEN` y actualizar `.env`
4. **Calibración:** ajustar coeficientes en `gateway/decoder/decoder.py` (Fase 2)
5. **METGO:** configurar `METGO_API_URL` + JWT en `integration/.env` y correr el ingest

## Estado

| Entregable | Estado |
|------------|--------|
| Firmware wake/mide/TX/sleep + SD + EXT0 lluvia | Listo (esqueleto compilable) |
| Stack Docker gateway | Listo |
| Decoder + QC 4 tests | Listo |
| BOM red Aconcagua | Listo |
| Pinout PCB | Listo (ver `pcb/`) |
| Bridge API METGO | Listo |
| Checklist compra MVP | Listo (`bom/CHECKLIST_COMPRA_MVP.md`) |
| Firmware BME280 MVP | Listo (`HAS_BME280`) |
| Panel Vue LoRa DIY | Listo (`/iot/estaciones-diy`) |
| Calibración campo Fase 2 | Pendiente (después de montaje) |

**Fase roadmap METGO:** 3.x (IoT de campo) / extensión red LoRa. Ver `PLAN.md`.
