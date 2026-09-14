# Plan — Red LoRa DIY Aconcagua

## Objetivo

Desplegar una red de nodos meteorológicos de bajo costo (~70–80 % funcionalidad tipo Davis Vantage Pro2 a ~1/7 del costo) y alimentar METGO 3D con observaciones locales (QC + calibración).

## Fases

### Fase 0 — Repositorio y BOM (actual)

- [x] Carpeta `hardware/red-estaciones-diy-aconcagua/`
- [x] Firmware PlatformIO base
- [x] Docker Compose gateway
- [x] Decoder + QC
- [x] BOM CSV
- [x] Pinout / netlist PCB
- [x] Bridge ingesta METGO
- [x] Checklist compra MVP (`bom/CHECKLIST_COMPRA_MVP.md`)
- [x] Firmware BME280 (prototipo)
- [x] Panel Vue `/iot/estaciones-diy` + API
- [ ] Pedido de componentes (AliExpress / local)

### Fase 1 — Prototipo mínimo (1 nodo)

- [ ] Flash ESP32 + **BME280** + SD + RTC (ver checklist)
- [ ] CSV local validado 48 h
- [ ] TX LoRa → ChirpStack → Influx → Grafana (o WiFi MQTT en lab)
- [ ] Stevenson screen 3D o comercial
- [ ] Ver lecturas reales en Vue (dejar de simular)

### Fase 2 — Calibración

- [ ] Comparar T/HR/P vs estación WMO/Agromet cercana (≥14 días)
- [ ] Ajustar `CALIBRATION` en `decoder.py` y `stations/*.yaml`
- [ ] Validar anemómetro / tipping bucket (cubeta 0.2 mm)

### Fase 3 — Red piloto (5–8 nodos)

- [ ] Config por unidad (`STATION_ID`, `LORA_SF`, flags sensores)
- [ ] Mapa de cobertura LoRa (SF vs distancia)
- [ ] Solar + LiPo + TP4056 en cada nodo
- [ ] Ingest continuo a API METGO (`fuente=lora_diy`)

### Fase 4 — Variables ampliadas

- [ ] PMS5003 (PM2.5/PM10) en nodos urbanos / faena
- [ ] AS3935 (rayos) opcional
- [ ] DS18B20 suelo en nodos agro
- [ ] Ultrasonido viento solo alta montaña

### Fase 5 — Operación

- [ ] Dashboard Grafana + paneles Vue METGO
- [ ] Alertas (helada, viento umbral, lluvia intensa)
- [ ] Runbook mantención (filtros HR, hielo anemómetro, SD)

## Próximos pasos inmediatos (esta iteración)

1. Completar pedido con `bom/CHECKLIST_COMPRA_MVP.md` (~USD 75 nodo / ~230 con gateway).
2. `python integration/generate_config_h.py ACQ-01` → `pio run -t upload`.
3. Gateway lab: `docker compose up -d` en `gateway/`.
4. Panel: https://metgo-quillota.pages.dev → `/iot/estaciones-diy` (o local Vue).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Sobrecalentamiento carcasa | Stevenson screen |
| Degradación HR | SHT31 + filtro Gore-Tex |
| Corte de energía | RTC + buffer SD/EEPROM |
| Deriva presión | Calibración lineal vs WMO |
| Sin internet en fundo | LoRa → gateway central |
