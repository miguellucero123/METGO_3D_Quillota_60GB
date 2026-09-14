/**
 * METGO DIY — loop wake / mide / log SD / LoRa / deep sleep
 * Compilar: pio run -t upload
 */
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <LoRa.h>
#include <esp_task_wdt.h>
#include <esp_sleep.h>
#include <RTClib.h>

#include "config.h"

#if HAS_BME280
#include <Adafruit_BME280.h>
Adafruit_BME280 bme;
#endif

#if HAS_SHT31
#include <Adafruit_SHT31.h>
Adafruit_SHT31 sht31 = Adafruit_SHT31();
#endif

#if HAS_BMP388
#include <Adafruit_BMP3XX.h>
Adafruit_BMP3XX bmp;
#endif

#if HAS_VEML6075
#include <Adafruit_VEML6075.h>
Adafruit_VEML6075 veml = Adafruit_VEML6075();
#endif

#if HAS_DS18B20
#include <OneWire.h>
#include <DallasTemperature.h>
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature soil(&oneWire);
#endif

RTC_DS3231 rtc;

volatile uint32_t tipCount = 0;
volatile uint32_t windPulses = 0;
uint32_t lastSampleMs = 0;
float rainAccumMm = 0.0f;

struct Sample {
  float temp_c;
  float rh;
  float pressure_hpa;
  float wind_ms;
  int wind_dir_deg;
  float rain_mm;
  float uv_index;
  float pm25;
  float pm10;
  float soil_c;
  uint32_t epoch;
};

void IRAM_ATTR onRainTip() { tipCount++; }
void IRAM_ATTR onWindPulse() { windPulses++; }

void setupWatchdog() {
  esp_task_wdt_init(WATCHDOG_TIMEOUT_S, true);
  esp_task_wdt_add(NULL);
}

void setupPins() {
#if HAS_RAIN
  pinMode(PIN_RAIN_TIP, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_RAIN_TIP), onRainTip, FALLING);
#endif
#if HAS_WIND
  pinMode(PIN_ANEMOMETER, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ANEMOMETER), onWindPulse, FALLING);
#endif
}

bool setupSensors() {
  Wire.begin(I2C_SDA, I2C_SCL);
  bool ok = true;

  if (!rtc.begin()) {
    Serial.println(F("[RTC] DS3231 no encontrado — timestamps locales millis"));
    ok = false;
  }

#if HAS_BME280
  if (!bme.begin(0x76) && !bme.begin(0x77)) {
    Serial.println(F("[BME280] fail"));
    ok = false;
  }
#endif

#if HAS_SHT31
  if (!sht31.begin(0x44)) {
    Serial.println(F("[SHT31] fail"));
    ok = false;
  }
#endif

#if HAS_BMP388
  if (!bmp.begin_I2C()) {
    Serial.println(F("[BMP388] fail"));
    ok = false;
  } else {
    bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
    bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
    bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
  }
#endif

#if HAS_VEML6075
  if (!veml.begin()) {
    Serial.println(F("[VEML6075] fail"));
    ok = false;
  }
#endif

#if HAS_DS18B20
  soil.begin();
#endif

  if (!SD.begin(PIN_SD_CS)) {
    Serial.println(F("[SD] no montada — solo TX en vivo"));
  }

  return ok;
}

bool setupLoRa() {
  SPI.begin(LORA_PIN_SCK, LORA_PIN_MISO, LORA_PIN_MOSI, LORA_PIN_SS);
  LoRa.setPins(LORA_PIN_SS, LORA_PIN_RST, LORA_PIN_DIO0);
  if (!LoRa.begin(LORA_FREQ_HZ)) {
    Serial.println(F("[LoRa] begin fail"));
    return false;
  }
  LoRa.setSpreadingFactor(LORA_SF);
  LoRa.setSignalBandwidth(LORA_BW);
  LoRa.setCodingRate4(LORA_CR);
  LoRa.setTxPower(LORA_TX_POWER_DBM);
  LoRa.setSyncWord(LORA_SYNC_WORD);
  return true;
}

float calcWindSpeed(uint32_t pulses, uint32_t dtMs) {
  if (dtMs == 0) return 0.0f;
  float hz = (pulses * 1000.0f) / (float)dtMs;
  return hz / ANEMO_PULSES_PER_M;
}

int readWindDir() {
  // Veleta resistiva: mapear ADC → 0..360 (calibrar Fase 2)
  int raw = analogRead(PIN_WIND_DIR_ADC);
  return (int)((raw / 4095.0f) * 360.0f) % 360;
}

Sample takeSample(uint32_t dtMs) {
  Sample s = {};
  s.temp_c = NAN;
  s.rh = NAN;
  s.pressure_hpa = NAN;
  s.uv_index = NAN;
  s.epoch = rtc.lostPower() ? (millis() / 1000UL) : rtc.now().unixtime();

#if HAS_BME280
  s.temp_c = bme.readTemperature();
  s.rh = bme.readHumidity();
  s.pressure_hpa = bme.readPressure() / 100.0f;
#endif

#if HAS_SHT31
  s.temp_c = sht31.readTemperature();
  s.rh = sht31.readHumidity();
#endif

#if HAS_BMP388
  if (bmp.performReading()) {
    s.pressure_hpa = bmp.pressure / 100.0f;
    if (isnan(s.temp_c)) s.temp_c = bmp.temperature;
  }
#endif

#if HAS_VEML6075
  s.uv_index = veml.readUVI();
#endif

#if HAS_WIND
  noInterrupts();
  uint32_t wp = windPulses;
  windPulses = 0;
  interrupts();
  s.wind_ms = calcWindSpeed(wp, dtMs);
  s.wind_dir_deg = readWindDir();
#else
  s.wind_ms = 0.0f;
  s.wind_dir_deg = 0;
#endif

#if HAS_RAIN
  noInterrupts();
  uint32_t tips = tipCount;
  tipCount = 0;
  interrupts();
  rainAccumMm += tips * RAIN_MM_PER_TIP;
  s.rain_mm = rainAccumMm;
#else
  s.rain_mm = 0.0f;
#endif

#if HAS_DS18B20
  soil.requestTemperatures();
  s.soil_c = soil.getTempCByIndex(0);
#endif

  s.pm25 = NAN;
  s.pm10 = NAN;
  return s;
}

void logToSD(const Sample &s) {
  File f = SD.open(SD_LOG_PATH, FILE_APPEND);
  if (!f) return;
  // CSV: id,epoch,t,rh,p,ws,wd,rain,uv,pm25,pm10,soil
  f.printf("%s,%lu,%.2f,%.1f,%.2f,%.2f,%d,%.2f,%.2f,%.1f,%.1f,%.2f\n",
           STATION_ID, (unsigned long)s.epoch, s.temp_c, s.rh, s.pressure_hpa,
           s.wind_ms, s.wind_dir_deg, s.rain_mm, s.uv_index, s.pm25, s.pm10, s.soil_c);
  f.close();
}

void sendLoRa(const Sample &s) {
  // Payload CSV compacto (mismo schema que decoder.py)
  char buf[160];
  snprintf(buf, sizeof(buf),
           "%s,%lu,%.2f,%.1f,%.2f,%.2f,%d,%.2f,%.2f",
           STATION_ID, (unsigned long)s.epoch, s.temp_c, s.rh, s.pressure_hpa,
           s.wind_ms, s.wind_dir_deg, s.rain_mm, s.uv_index);

  LoRa.beginPacket();
  LoRa.print(buf);
  LoRa.endPacket();
  Serial.printf("[TX] %s\n", buf);
}

void goDeepSleep() {
#if ENABLE_DEEP_SLEEP
#if HAS_RAIN
  esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_RAIN_TIP, 0);
#endif
  esp_sleep_enable_timer_wakeup((uint64_t)INTERVAL_MS * 1000ULL);
  Serial.println(F("[SLEEP] deep sleep"));
  Serial.flush();
  esp_deep_sleep_start();
#endif
}

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.printf("\nMETGO DIY %s fw=%s SF=%d\n", STATION_ID, FIRMWARE_VERSION, LORA_SF);

  setupWatchdog();
  setupPins();
  setupSensors();
  setupLoRa();

  lastSampleMs = millis();
  // Primera muestra inmediata tras boot / wake
  Sample s = takeSample(INTERVAL_MS);
  logToSD(s);
  sendLoRa(s);
  esp_task_wdt_reset();
  goDeepSleep();
}

void loop() {
  // Solo se usa si ENABLE_DEEP_SLEEP=0
  esp_task_wdt_reset();
  uint32_t now = millis();
  if (now - lastSampleMs >= INTERVAL_MS) {
    uint32_t dt = now - lastSampleMs;
    Sample s = takeSample(dt);
    logToSD(s);
    sendLoRa(s);
    lastSampleMs = now;
  }
  delay(50);
}
