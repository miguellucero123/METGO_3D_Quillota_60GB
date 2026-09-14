#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera firmware/include/config.h desde stations/<ID>.yaml"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Instala PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = """/**
 * AUTO-GENERADO desde stations/{station_id}.yaml — no editar a mano.
 * Regenerar: python integration/generate_config_h.py {station_id}
 */
#ifndef METGO_STATION_CONFIG_H
#define METGO_STATION_CONFIG_H

#define STATION_ID          "{station_id}"
#define STATION_NAME        "{name}"
#define FIRMWARE_VERSION    "0.1.0"

#define INTERVAL_MS         ({interval_ms}UL)
#define WATCHDOG_TIMEOUT_S  30
#define ENABLE_DEEP_SLEEP   1

#define LORA_SF             {lora_sf}
#define LORA_BW             125E3
#define LORA_CR             5
#define LORA_FREQ_HZ        915E6
#define LORA_TX_POWER_DBM   14
#define LORA_SYNC_WORD      0x12

#define LORA_PIN_SCK        18
#define LORA_PIN_MISO       19
#define LORA_PIN_MOSI       23
#define LORA_PIN_SS         5
#define LORA_PIN_RST        14
#define LORA_PIN_DIO0       26

#define I2C_SDA             21
#define I2C_SCL             22

#define PIN_RAIN_TIP        33
#define PIN_ANEMOMETER      32
#define PIN_WIND_DIR_ADC    34
#define PIN_SD_CS           15

#define HAS_BME280          {bme280}
#define HAS_SHT31           {sht31}
#define HAS_BMP388          {bmp388}
#define HAS_VEML6075        {veml6075}
#define HAS_RAIN            {rain}
#define HAS_WIND            {wind}
#define HAS_PMS5003         {pms5003}
#define HAS_AS3935          {as3935}
#define HAS_DS18B20         {ds18b20}
#define HAS_ULTRASONIC_WIND 0

#if HAS_BME280 && (HAS_SHT31 || HAS_BMP388)
#error "Usar BME280 O SHT31+BMP388, no ambos"
#endif

#if HAS_PMS5003
#define PMS_RX              16
#define PMS_TX              17
#endif

#if HAS_DS18B20
#define PIN_ONEWIRE         4
#endif

#define RAIN_MM_PER_TIP     0.2f
#define ANEMO_PULSES_PER_M  2.5f

#define SD_LOG_PATH         "/metgo_log.csv"
#define OFFLINE_BUF_MAX     64

#endif
"""


def b(v: bool) -> str:
    return "1" if v else "0"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("station_id", help="ej. ACQ-01")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "firmware" / "include" / "config.h",
    )
    args = ap.parse_args()

    path = ROOT / "stations" / f"{args.station_id}.yaml"
    if not path.is_file():
        print(f"No existe {path}", file=sys.stderr)
        sys.exit(1)

    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    sens = cfg.get("sensors", {})
    use_bme = bool(sens.get("bme280", False))
    # Defaults: si no hay BME, asumir kit pro SHT31+BMP388
    out = TEMPLATE.format(
        station_id=cfg["station_id"],
        name=cfg.get("name", cfg["station_id"]),
        interval_ms=int(cfg.get("interval_s", 300)) * 1000,
        lora_sf=int(cfg.get("lora_sf", 9)),
        bme280=b(use_bme),
        sht31=b(sens.get("sht31", not use_bme)),
        bmp388=b(sens.get("bmp388", not use_bme)),
        veml6075=b(sens.get("veml6075", False)),
        rain=b(sens.get("rain", False)),
        wind=b(sens.get("wind", False)),
        pms5003=b(sens.get("pms5003", False)),
        as3935=b(sens.get("as3935", False)),
        ds18b20=b(sens.get("ds18b20", False)),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(out, encoding="utf-8")
    print(f"Escrito {args.output}")


if __name__ == "__main__":
    main()
