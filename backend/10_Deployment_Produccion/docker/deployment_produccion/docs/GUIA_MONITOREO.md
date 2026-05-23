# 📊 GUÍA DE MONITOREO - METGO 3D QUILLOTA

## 🎯 Sistema de Monitoreo

El sistema incluye monitoreo automático de:
- Estado de servicios web
- Uso de recursos del sistema (CPU, memoria, disco)
- Alertas automáticas
- Logs de sistema

## 🚀 Iniciar Monitoreo

### Monitoreo Continuo
```bash
python monitoring/monitoreo_produccion.py
```

### Verificación Rápida
```bash
python scripts/verificar_estado.py
```

## 📊 Métricas Monitoreadas

### Servicios Web
- Dashboard Principal (puerto 8501)
- Dashboard Agrícola (puerto 8510)
- Sistema de Monitoreo (puerto 8502)

### Recursos del Sistema
- Uso de CPU (%)
- Uso de memoria (%)
- Espacio en disco (%)
- Tiempo de respuesta de servicios

## 🚨 Alertas

### Tipos de Alertas
- Servicio inactivo
- Alto uso de memoria (>80%)
- Alto uso de CPU (>80%)
- Error en base de datos

### Configuración de Alertas
Editar `config/monitoreo_config.json`:
```json
{
  "intervalo_verificacion": 300,
  "umbral_memoria": 80,
  "umbral_cpu": 80,
  "alertas_email": false
}
```

## 📈 Logs

### Ubicación de Logs
- `logs/monitoreo_produccion.log` - Logs de monitoreo
- `logs/deployment_produccion.log` - Logs de deployment
- `logs/backup_automatico.log` - Logs de backup

### Niveles de Log
- INFO: Información general
- WARNING: Advertencias
- ERROR: Errores
- CRITICAL: Errores críticos

## 🔧 Configuración Avanzada

### Monitoreo Personalizado
```python
from monitoring.monitoreo_produccion import MonitoreoProduccion

monitoreo = MonitoreoProduccion()
resultados = monitoreo.verificar_servicios()
```

### Alertas por Email
Configurar en `config/monitoreo_config.json`:
```json
{
  "notificaciones": {
    "email": {
      "activo": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "metgo.quillota@gmail.com",
      "password": "app_password_aqui",
      "to_emails": ["admin@metgo.cl"]
    }
  }
}
```

## 📊 Reportes

### Reporte de Estado
```bash
python monitoring/monitoreo_produccion.py
```

### Reporte Detallado
El sistema genera reportes automáticos cada 5 minutos con:
- Estado de servicios
- Métricas de sistema
- Alertas activas
- Recomendaciones

## 🛠️ Mantenimiento

### Limpiar Logs Antiguos
```bash
find logs/ -name "*.log" -mtime +30 -delete
```

### Rotar Logs
```bash
logrotate -f /etc/logrotate.d/metgo
```

## 🚨 Solución de Problemas

### Servicio No Responde
1. Verificar estado: `python scripts/verificar_estado.py`
2. Revisar logs: `tail -f logs/monitoreo_produccion.log`
3. Reiniciar servicio: `python scripts/reiniciar_produccion.py`

### Alto Uso de Recursos
1. Verificar métricas: `python scripts/verificar_estado.py`
2. Reiniciar sistema: `python scripts/reiniciar_produccion.py`
3. Verificar procesos: `ps aux | grep python`

### Alertas Falsas
1. Ajustar umbrales en `config/monitoreo_config.json`
2. Verificar configuración de servicios
3. Revisar logs de monitoreo

---

*Guía de Monitoreo - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
