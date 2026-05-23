# MANUAL DE USUARIO - METGO 3D QUILLOTA

**Version:** 1.0.0  
**Fecha:** 2025-10-07 10:34:44  
**Sistema:** Meteorologico Agricola Integral

---

## INTRODUCCION

METGO 3D Quillota es un sistema integral de gestion agricola que combina datos meteorologicos en tiempo real, predicciones de Machine Learning, alertas automaticas y reportes avanzados para optimizar las operaciones agricolas en el Valle de Quillota.

### Caracteristicas Principales:
- Datos Meteorologicos en Tiempo Real de 6 estaciones
- Predicciones de IA con Machine Learning
- Alertas Automaticas de heladas y eventos criticos
- Reportes Profesionales en multiples formatos
- Notificaciones por WhatsApp, Email y SMS
- Dashboards Interactivos con visualizaciones avanzadas

---

## INSTALACION Y CONFIGURACION

### Requisitos del Sistema:
- **Sistema Operativo:** Windows 10/11, Linux, macOS
- **Python:** 3.11 o superior
- **Memoria RAM:** Minimo 4GB, Recomendado 8GB
- **Espacio en Disco:** 2GB libres
- **Conexion a Internet:** Requerida para APIs meteorologicas

### Instalacion Rapida:
```bash
# 1. Clonar el repositorio
git clone https://github.com/metgo/quillota-3d.git
cd quillota-3d

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar instalacion automatica
python instalar_metgo.py

# 4. Iniciar sistema optimizado
iniciar_metgo_optimizado.bat
```

### Configuracion Inicial:
1. **Configurar APIs Meteorologicas:**
   ```bash
   python configurar_apis_reales.py
   ```

2. **Configurar Notificaciones:**
   ```bash
   python activar_notificaciones_simple.py
   ```

3. **Verificar Sistema:**
   ```bash
   python demo_sistema_simple.py
   ```

---

## ACCESO AL SISTEMA

### URLs de Acceso:
- **Dashboard Principal:** http://localhost:8501
- **Dashboard Agricola Avanzado:** http://localhost:8510
- **Dashboard Global:** http://localhost:8502
- **Dashboard Agricola:** http://localhost:8508

### Credenciales por Defecto:
- **Usuario:** admin
- **Contraseña:** metgo2025

---

## FUNCIONALIDADES PRINCIPALES

### 1. Dashboard Principal
**Acceso:** http://localhost:8501

**Funcionalidades:**
- **Inicio:** Resumen general del sistema
- **Dashboard:** Acceso a todos los dashboards disponibles
- **Visualizaciones:** Graficos interactivos de datos meteorologicos
- **Predicciones:** Predicciones de Machine Learning
- **Alertas:** Sistema de alertas meteorologicas
- **Reportes:** Generacion de reportes automaticos
- **Configuracion:** Ajustes del sistema

### 2. Dashboard Agricola Avanzado
**Acceso:** http://localhost:8510

**Funcionalidades:**
- **Datos en Tiempo Real:** APIs meteorologicas de 6 estaciones
- **Predicciones ML:** 4 algoritmos, 6 variables predichas
- **Alertas de Heladas:** Sistema avanzado de deteccion
- **Reportes Automaticos:** HTML, JSON, CSV, PDF
- **Notificaciones:** WhatsApp, Email, SMS

### 3. Sistema de Predicciones ML
**Algoritmos Disponibles:**
- Random Forest Regressor
- Gradient Boosting Regressor
- Linear Regression
- Ridge Regression

**Variables Predichas:**
- Temperatura maxima
- Temperatura minima
- Humedad relativa
- Velocidad del viento
- Direccion del viento
- Precipitacion

**Precision:** R² > 0.95 en todos los modelos

### 4. Sistema de Alertas
**Tipos de Alertas:**
- **Heladas:** Temperatura < 2°C
- **Viento Fuerte:** Velocidad > 30 km/h
- **Humedad Baja:** < 30%
- **Precipitacion Intensa:** > 20mm/h
- **Temperatura Extrema:** < 0°C o > 35°C
- **Presion Baja:** < 1000 hPa
- **Cambio Brusco:** Variacion > 10°C/h

**Canales de Notificacion:**
- **WhatsApp:** Alertas instantaneas
- **Email:** Reportes detallados
- **SMS:** Alertas criticas

---

## CONFIGURACION AVANZADA

### Configuracion de APIs Meteorologicas

**Archivo:** `api_keys_meteorologicas.json`
```json
{
    "openmeteo": {
        "activa": true,
        "url": "https://api.open-meteo.com/v1/forecast",
        "timeout": 30
    },
    "openweathermap": {
        "activa": false,
        "api_key": "TU_API_KEY",
        "url": "https://api.openweathermap.org/data/2.5/weather"
    },
    "accuweather": {
        "activa": false,
        "api_key": "TU_API_KEY",
        "url": "https://dataservice.accuweather.com/currentconditions/v1/"
    }
}
```

### Configuracion de Notificaciones

**Archivo:** `configuracion_notificaciones_avanzada.json`
```json
{
    "whatsapp": {
        "activo": true,
        "twilio_account_sid": "TU_ACCOUNT_SID",
        "twilio_auth_token": "TU_AUTH_TOKEN",
        "numero_origen": "+1234567890"
    },
    "email": {
        "activo": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "usuario": "tu_email@gmail.com",
        "password": "tu_app_password"
    },
    "sms": {
        "activo": true,
        "twilio_account_sid": "TU_ACCOUNT_SID",
        "twilio_auth_token": "TU_AUTH_TOKEN"
    }
}
```

### Configuracion de Estaciones Meteorologicas

**Estaciones Disponibles:**
1. **Quillota Centro** (Lat: -32.8833, Lon: -71.2667)
2. **La Cruz** (Lat: -32.8167, Lon: -71.2333)
3. **Nogales** (Lat: -32.7500, Lon: -71.2000)
4. **Hijuelas** (Lat: -32.8000, Lon: -71.1500)
5. **La Calera** (Lat: -32.7833, Lon: -71.2167)
6. **San Pedro** (Lat: -32.8500, Lon: -71.1833)

---

## SISTEMA DE NOTIFICACIONES

### Configuracion de WhatsApp
1. **Crear cuenta Twilio:**
   - Ir a https://www.twilio.com
   - Crear cuenta gratuita
   - Obtener Account SID y Auth Token

2. **Configurar numero:**
   - Obtener numero de WhatsApp Business
   - Configurar webhook

3. **Actualizar configuracion:**
   ```bash
   python configurar_apis_reales.py
   ```

### Configuracion de Email
1. **Gmail con App Password:**
   - Habilitar verificacion en 2 pasos
   - Generar App Password
   - Usar App Password en lugar de contraseña normal

2. **Otros proveedores:**
   - Configurar SMTP server y puerto
   - Usar credenciales apropiadas

### Configuracion de SMS
1. **Twilio SMS:**
   - Usar misma cuenta de WhatsApp
   - Configurar numero de origen
   - Establecer limites de uso

---

## GENERACION DE REPORTES

### Tipos de Reportes Disponibles:
- **HTML:** Reportes interactivos para web
- **JSON:** Datos estructurados para APIs
- **CSV:** Datos para analisis en Excel
- **PDF:** Reportes profesionales para impresion

### Generacion Manual:
```bash
# Generar reporte diario
python sistema_reportes_automaticos_avanzado.py

# Generar reporte especifico
python generar_reporte_personalizado.py --tipo agricola --formato pdf
```

### Generacion Automatica:
- **Diaria:** 6:00 AM
- **Semanal:** Lunes 8:00 AM
- **Mensual:** Primer dia del mes 9:00 AM

---

## ACTUALIZACION AUTOMATICA

### Actualizador Automatico:
```bash
# Actualizacion manual
python actualizador_datos_automatico.py manual

# Iniciar actualizador automatico
python iniciar_actualizador_automatico.py
```

### Frecuencia de Actualizacion:
- **Datos Meteorologicos:** Cada hora
- **Predicciones ML:** Cada 6 horas
- **Alertas:** Tiempo real
- **Reportes:** Segun programacion

---

## MANTENIMIENTO DEL SISTEMA

### Tareas de Mantenimiento Diario:
- Verificar logs de errores
- Monitorear uso de memoria
- Revisar estado de APIs
- Validar datos meteorologicos

### Tareas de Mantenimiento Semanal:
- Limpiar cache antiguo
- Optimizar bases de datos
- Actualizar modelos ML
- Generar reportes de rendimiento

### Tareas de Mantenimiento Mensual:
- Backup completo del sistema
- Actualizacion de dependencias
- Revision de configuracion
- Analisis de rendimiento

### Comandos de Mantenimiento:
```bash
# Limpiar sistema
python limpiar_sistema.py

# Optimizar rendimiento
python optimizador_rendimiento_avanzado.py

# Backup del sistema
python backup_sistema.py

# Verificar integridad
python verificar_sistema.py
```

---

## SOLUCION DE PROBLEMAS

### Problemas Comunes:

#### 1. Error de Puerto en Uso
```bash
# Solucion: Cambiar puerto
python -m streamlit run dashboard.py --server.port 8502
```

#### 2. Error de APIs Meteorologicas
```bash
# Verificar conexion
python probar_apis_reales.py

# Reconfigurar APIs
python configurar_apis_reales.py
```

#### 3. Error de Notificaciones
```bash
# Probar sistema de notificaciones
python probar_sistema_notificaciones.py

# Reconfigurar notificaciones
python activar_notificaciones_simple.py
```

#### 4. Error de Base de Datos
```bash
# Verificar bases de datos
python verificar_sistema.py

# Reparar bases de datos
python reparar_bases_datos.py
```

### Logs del Sistema:
- **Logs Generales:** `logs/sistema.log`
- **Logs de Optimizacion:** `logs/optimizacion_rendimiento.log`
- **Logs de Dashboards:** `logs/optimizacion_dashboards.log`
- **Logs de Notificaciones:** `logs/notificaciones.log`

---

## SOPORTE TECNICO

### Informacion de Contacto:
- **Email:** soporte@metgo.cl
- **Telefono:** +56 9 1234 5678
- **Horario:** Lunes a Viernes, 9:00 - 18:00

### Recursos Adicionales:
- **Documentacion Tecnica:** `docs/`
- **Ejemplos de Codigo:** `ejemplos/`
- **FAQ:** `docs/faq.md`
- **Changelog:** `docs/changelog.md`

---

## APENDICES

### A. Glosario de Terminos
- **API:** Application Programming Interface
- **ML:** Machine Learning
- **R²:** Coeficiente de determinacion
- **RMSE:** Root Mean Square Error
- **TTL:** Time To Live
- **WAL:** Write-Ahead Logging

### B. Referencias Tecnicas
- **Streamlit:** https://docs.streamlit.io/
- **Plotly:** https://plotly.com/python/
- **Twilio:** https://www.twilio.com/docs
- **OpenMeteo:** https://open-meteo.com/en/docs

### C. Historial de Versiones
- **v1.0.0:** Version inicial completa
- **v1.1.0:** Optimizaciones de rendimiento
- **v1.2.0:** Sistema de notificaciones avanzado

---

*Manual de Usuario - METGO 3D Quillota v1.0.0*  
*Generado el 2025-10-07 10:34:44*
