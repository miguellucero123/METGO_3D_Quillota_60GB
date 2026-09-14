# Checklist de compra — prototipo mínimo (Fase 1)

Pedido para **1 nodo + gateway de laboratorio**. No comprar la red de 20 hasta validar 48 h de datos.

Marcar al pedir / recibir.

## A. Nodo prototipo (obligatorio)

| # | Item | Qty | ~USD | Link / proveedor | Pedido | Recibido |
|---|------|-----|------|------------------|--------|----------|
| 1 | ESP32 DevKit V1 / WROOM-32 | 1 | 4.50 | AliExpress / MercadoLibre | ☐ | ☐ |
| 2 | BME280 (I2C) **o** SHT31+BMP388 | 1 | 3–9 | Preferir BME280 para MVP | ☐ | ☐ |
| 3 | Módulo LoRa SX1276 / RFM95 **915 MHz** | 1 | 7.50 | Confirmar banda Chile | ☐ | ☐ |
| 4 | Antena LoRa 915 MHz (SMA/IPEX) | 1 | 2.00 | | ☐ | ☐ |
| 5 | DS3231 RTC | 1 | 2.00 | | ☐ | ☐ |
| 6 | Módulo microSD SPI + tarjeta 8–16 GB FAT32 | 1 | 4.00 | | ☐ | ☐ |
| 7 | Panel solar 6W 6V | 1 | 8.00 | | ☐ | ☐ |
| 8 | LiPo 3.7V ≥3000 mAh + JST | 1 | 6.00 | | ☐ | ☐ |
| 9 | TP4056 con protección | 1 | 1.50 | | ☐ | ☐ |
| 10 | Regulador 3.3 V (AP2112 / AMS1117-3.3) | 1 | 1.00 | Si TP4056 solo da 5V USB | ☐ | ☐ |
| 11 | Caja IP65 + prensaestopas | 1 | 10.00 | Local | ☐ | ☐ |
| 12 | Protoboard / PCB perf + jumpers + estaño | 1 | 8.00 | | ☐ | ☐ |
| 13 | Stevenson screen (3D o kit) | 1 | 12.00 | Crítico vs sol | ☐ | ☐ |

**Subtotal nodo MVP:** ~USD 70–80 (sin viento/lluvia)

## B. Opcional primer mes (recomendado tras CSV OK)

| # | Item | Qty | ~USD | Pedido | Recibido |
|---|------|-----|------|--------|----------|
| 14 | Tipping bucket 0.2 mm | 1 | 12 | ☐ | ☐ |
| 15 | Anemómetro + reed | 1 | 15 | ☐ | ☐ |
| 16 | Veleta resistiva | 1 | 10 | ☐ | ☐ |
| 17 | VEML6075 UV | 1 | 3 | ☐ | ☐ |

## C. Gateway laboratorio

| # | Item | Qty | ~USD | Notas | Pedido | Recibido |
|---|------|-----|------|-------|--------|----------|
| 18 | Raspberry Pi 4 4GB (o PC con Docker) | 1 | 55 / 0 | PC vale para lab | ☐ | ☐ |
| 19 | Concentrador LoRa SX1302 USB/HAT 915 MHz | 1 | 75 | Ojo: sin esto solo WiFi MQTT | ☐ | ☐ |
| 20 | microSD 64 GB + PSU RPi | 1 | 25 | | ☐ | ☐ |

**Alternativa lab sin concentrador:** flashear env `esp32dev_wifi` y publicar MQTT directo a Mosquitto (validar decoder/Grafana antes de LoRa).

## D. Herramientas (si no tienes)

| # | Item | Pedido |
|---|------|--------|
| 21 | Multímetro | ☐ |
| 22 | Soldador + estaño | ☐ |
| 23 | Cable USB-C / micro-USB según ESP32 | ☐ |

## Totales orientativos

| Escenario | USD |
|-----------|-----|
| Nodo MVP (A) | ~75 |
| A + viento/lluvia (B) | ~115 |
| A + gateway RPi+concentrador (C) | ~230 |
| Red completa 20 nodos | ~3,021 (ver `bom_red_aconcagua.csv`) |

## Tras recibir

1. Flash: `pio run -e esp32dev -t upload` (BME280: `HAS_BME280=1` en config).
2. Gateway: `cp gateway/.env.example gateway/.env` → `docker compose up -d`.
3. Validar CSV 48 h en SD.
4. Panel Vue: `/iot/estaciones-diy`.

## Firmware flags prototipo BME280

En `stations/ACQ-01.yaml` (MVP):

```yaml
sensors:
  bme280: true
  sht31: false
  bmp388: false
```

Generar: `python integration/generate_config_h.py ACQ-01`
