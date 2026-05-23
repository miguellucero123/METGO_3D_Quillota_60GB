# DOCUMENTACION DE APIs - METGO 3D QUILLOTA

**Version:** 1.0.0  
**Fecha:** 2025-10-07 10:34:44

---

## APIs METEOROLOGICAS INTEGRADAS

### 1. OpenMeteo API
**URL Base:** https://api.open-meteo.com/v1/forecast

**Caracteristicas:**
- Gratuita y sin limites
- Datos historicos y pronosticos
- Actualizacion cada hora
- Cobertura global

**Parametros:**
```json
{
    "latitude": -32.8833,
    "longitude": -71.2667,
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "wind_direction_10m",
        "pressure_msl",
        "cloud_cover"
    ],
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum"
    ],
    "timezone": "America/Santiago"
}
```

### 2. OpenWeatherMap API
**URL Base:** https://api.openweathermap.org/data/2.5/weather

**Caracteristicas:**
- Requiere API Key
- Datos detallados
- Pronosticos extendidos
- Datos historicos

### 3. AccuWeather API
**URL Base:** https://dataservice.accuweather.com/

**Caracteristicas:**
- Requiere API Key
- Datos precisos
- Pronosticos detallados
- Alertas meteorologicas

---

## APIs DE MACHINE LEARNING

### Sistema de Predicciones ML
**Archivo:** `sistema_predicciones_ml_avanzado.py`

**Algoritmos Disponibles:**
1. **Random Forest Regressor**
   - Parametros: n_estimators=100, max_depth=10
   - Precision: R² > 0.95
   - Variables: 6

2. **Gradient Boosting Regressor**
   - Parametros: n_estimators=100, learning_rate=0.1
   - Precision: R² > 0.95
   - Variables: 6

3. **Linear Regression**
   - Parametros: default
   - Precision: R² > 0.90
   - Variables: 6

4. **Ridge Regression**
   - Parametros: alpha=1.0
   - Precision: R² > 0.90
   - Variables: 6

---

## APIs DE NOTIFICACIONES

### 1. Twilio WhatsApp API
**URL Base:** https://api.twilio.com/2010-04-01/Accounts/

**Configuracion:**
```json
{
    "account_sid": "TU_ACCOUNT_SID",
    "auth_token": "TU_AUTH_TOKEN",
    "from_number": "+1234567890",
    "webhook_url": "https://tu-dominio.com/webhook"
}
```

### 2. Gmail SMTP API
**Servidor:** smtp.gmail.com  
**Puerto:** 587  
**Seguridad:** TLS

### 3. Twilio SMS API
**URL Base:** https://api.twilio.com/2010-04-01/Accounts/

---

## APIs DE BASE DE DATOS

### SQLite Database APIs
**Archivos:**
- `metgo_agricola.db` - Datos meteorologicos
- `metgo_ml.db` - Predicciones ML
- `metgo_notificaciones.db` - Logs de notificaciones

**Operaciones CRUD:**
```python
import sqlite3

# Conectar a base de datos
conn = sqlite3.connect('metgo_agricola.db')
cursor = conn.cursor()

# Insertar datos meteorologicos
cursor.execute('''
    INSERT INTO datos_meteorologicos 
    (fecha, estacion, temperatura, humedad, precipitacion)
    VALUES (?, ?, ?, ?, ?)
''', (fecha, estacion, temp, hum, prec))

# Consultar datos
cursor.execute('''
    SELECT * FROM datos_meteorologicos 
    WHERE estacion = ? AND fecha >= ?
''', (estacion, fecha_inicio))

datos = cursor.fetchall()
conn.commit()
conn.close()
```

---

## APIs DE CONFIGURACION

### Sistema de Configuracion Unificada
**Archivo:** `configuracion_unificada_metgo.py`

**Configuracion Principal:**
```python
from configuracion_unificada_metgo import ConfiguracionUnificadaMetgo

config = ConfiguracionUnificadaMetgo()

# Obtener configuracion
api_config = config.obtener_configuracion('apis_meteorologicas')
alertas_config = config.obtener_configuracion('alertas')

# Actualizar configuracion
config.actualizar_configuracion('alertas', {
    'temperatura_minima': 2.0,
    'humedad_minima': 30.0
})
```

---

## APIs DE REPORTES

### Sistema de Reportes Automaticos
**Archivo:** `sistema_reportes_automaticos_avanzado.py`

**Generacion de Reportes:**
```python
from sistema_reportes_automaticos_avanzado import SistemaReportesAutomaticosAvanzado

sistema_reportes = SistemaReportesAutomaticosAvanzado()

# Generar reporte diario
reporte = sistema_reportes.generar_reporte_diario(
    formato='html',
    incluir_graficos=True
)

# Generar reporte personalizado
reporte_personalizado = sistema_reportes.generar_reporte_personalizado(
    tipo='agricola',
    formato='pdf',
    fecha_inicio='2025-10-01',
    fecha_fin='2025-10-07'
)
```

**Formatos Disponibles:**
- **HTML:** Interactivo para web
- **JSON:** Datos estructurados
- **CSV:** Para analisis en Excel
- **PDF:** Para impresion

---

## CODIGOS DE ERROR

### Codigos de Error Comunes:
- **1001:** Error de conexion API meteorologica
- **1002:** API Key invalida
- **1003:** Limite de requests excedido
- **2001:** Error de base de datos
- **2002:** Tabla no encontrada
- **3001:** Error de notificacion WhatsApp
- **3002:** Error de notificacion Email
- **3003:** Error de notificacion SMS
- **4001:** Error de prediccion ML
- **4002:** Modelo no entrenado
- **5001:** Error de configuracion
- **5002:** Archivo de configuracion no encontrado

### Manejo de Errores:
```python
try:
    resultado = api.obtener_datos()
except APIError as e:
    logger.error(f"Error API {e.code}: {e.message}")
    # Manejar error especifico
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    # Manejar error generico
```

---

## RECURSOS ADICIONALES

### Documentacion Externa:
- **Streamlit:** https://docs.streamlit.io/
- **Plotly:** https://plotly.com/python/
- **Twilio:** https://www.twilio.com/docs
- **OpenMeteo:** https://open-meteo.com/en/docs
- **SQLite:** https://www.sqlite.org/docs.html

### Ejemplos de Codigo:
- **ejemplos/api_meteorologica.py**
- **ejemplos/notificaciones.py**
- **ejemplos/reportes.py**
- **ejemplos/optimizacion.py**

---

*Documentacion de APIs - METGO 3D Quillota v1.0.0*  
*Generado el 2025-10-07 10:34:44*
