/**
 * Configuración por unidad — editar ANTES de flashear cada nodo.
 * Generación masiva: ver stations/*.yaml + scripts en integration/.
 */
#ifndef METGO_STATION_CONFIG_H
#define METGO_STATION_CONFIG_H

// ---- Identidad ----
#define STATION_ID          "ACQ-01"   // Quillota piloto
#define STATION_NAME        "Quillota Fundo Demo"
#define FIRMWARE_VERSION    "0.1.0"

// ---- Muestreo / energía ----
#define INTERVAL_MS         (5UL * 60UL * 1000UL)  // 5 min
#define WATCHDOG_TIMEOUT_S  30
#define ENABLE_DEEP_SLEEP   1

// ---- LoRa (SX1276 / RFM95) ----
#define LORA_SF             9          // 7..12 según cobertura
#define LORA_BW             125E3
#define LORA_CR             5
#define LORA_FREQ_HZ        915E6      // Chile: confirmar banda ISM local
#define LORA_TX_POWER_DBM   14
#define LORA_SYNC_WORD      0x12

// Pines LoRa (ajustar a PCB)
#define LORA_PIN_SCK        18
#define LORA_PIN_MISO       19
#define LORA_PIN_MOSI       23
#define LORA_PIN_SS         5
#define LORA_PIN_RST        14
#define LORA_PIN_DIO0       26

// ---- I2C sensores ----
#define I2C_SDA             21
#define I2C_SCL             22

// ---- GPIO mecánicos ----
#define PIN_RAIN_TIP        33         // EXT0 wake (RTC GPIO)
#define PIN_ANEMOMETER      32
#define PIN_WIND_DIR_ADC    34         // solo ADC1 en deep sleep
#define PIN_SD_CS           15

// ---- Flags de sensores (1 = incluido en este nodo) ----
// Prototipo MVP: BME280 solo (T+HR+P). Producción: SHT31+BMP388.
#define HAS_BME280          1
#define HAS_SHT31           0
#define HAS_BMP388          0
#define HAS_VEML6075        0
#define HAS_RAIN            0
#define HAS_WIND            0
#define HAS_PMS5003         0
#define HAS_AS3935          0
#define HAS_DS18B20         0
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

#if HAS_ULTRASONIC_WIND
#define PIN_US_TRIG         25
#define PIN_US_ECHO         27
#endif

// ---- Constantes físicas ----
#define RAIN_MM_PER_TIP     0.2f
#define ANEMO_PULSES_PER_M  2.5f       // calibrar en Fase 2

// ---- SD / buffer offline ----
#define SD_LOG_PATH         "/metgo_log.csv"
#define OFFLINE_BUF_MAX     64

#endif // METGO_STATION_CONFIG_H
