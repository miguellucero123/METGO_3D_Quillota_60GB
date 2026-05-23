# 💾 GUÍA DE BACKUP - METGO 3D QUILLOTA

## 🎯 Sistema de Backup

El sistema incluye backup automático de:
- Datos meteorológicos
- Configuraciones
- Logs del sistema
- Bases de datos
- Código fuente

## 🚀 Backup Manual

### Crear Backup
```bash
python backup/backup_automatico.py
```

### Listar Backups
```bash
python backup/backup_automatico.py
```

## ⚙️ Configuración de Backup

### Archivo de Configuración
`config/backup_config.json`:
```json
{
  "directorio_backup": "./backups",
  "retencion_dias": 30,
  "frecuencia": "diario",
  "archivos_incluir": [
    "data/",
    "logs/",
    "config/",
    "*.db",
    "*.json",
    "*.py"
  ]
}
```

### Directorios Incluidos
- `data/` - Datos meteorológicos
- `logs/` - Logs del sistema
- `config/` - Configuraciones
- `*.db` - Bases de datos
- `*.json` - Archivos de configuración
- `*.py` - Código fuente

## 📅 Backup Automático

### Programar Backup Diario
#### Windows (Task Scheduler)
1. Abrir Task Scheduler
2. Crear tarea básica
3. Configurar para ejecutar diariamente
4. Acción: `python backup/backup_automatico.py`

#### Linux/Mac (Cron)
```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2:00 AM
0 2 * * * cd /ruta/a/metgo && python backup/backup_automatico.py
```

## 🔄 Restauración

### Restaurar Backup
```python
from backup.backup_automatico import BackupAutomatico

backup = BackupAutomatico()
backup.restaurar_backup('metgo_backup_20251007_143000.zip')
```

### Listar Backups Disponibles
```python
from backup.backup_automatico import BackupAutomatico

backup = BackupAutomatico()
backups = backup.listar_backups()
for b in backups:
    print(f"{b['nombre']} - {b['fecha_creacion']} - {b['tamaño_mb']:.2f} MB")
```

## 📊 Gestión de Backups

### Retención
- Backups se mantienen por 30 días por defecto
- Configurable en `backup_config.json`
- Backups antiguos se eliminan automáticamente

### Compresión
- Backups se comprimen en formato ZIP
- Reducción de tamaño ~70%
- Verificación de integridad automática

### Verificación
```bash
# Verificar integridad de backup
unzip -t backups/metgo_backup_20251007_143000.zip
```

## 🚨 Recuperación de Desastres

### Procedimiento de Recuperación
1. Detener sistema: `python scripts/parar_produccion.py`
2. Restaurar backup más reciente
3. Verificar integridad de datos
4. Reiniciar sistema: `python scripts/iniciar_produccion.py`

### Backup de Emergencia
```bash
# Crear backup de emergencia
python backup/backup_automatico.py

# Copiar a ubicación externa
cp backups/metgo_backup_*.zip /ruta/externa/
```

## 🔧 Mantenimiento

### Limpiar Backups Antiguos
```bash
# Eliminar backups más antiguos que 30 días
find backups/ -name "metgo_backup_*.zip" -mtime +30 -delete
```

### Verificar Espacio en Disco
```bash
# Verificar espacio disponible
df -h backups/
```

### Monitorear Backups
```bash
# Verificar último backup
ls -la backups/ | tail -1
```

## 📈 Monitoreo de Backups

### Verificar Estado
```bash
python scripts/verificar_estado.py
```

### Logs de Backup
```bash
tail -f logs/backup_automatico.log
```

### Alertas de Backup
Configurar alertas si backup falla:
```json
{
  "alertas": {
    "backup_fallido": true,
    "email_notificacion": "admin@metgo.cl"
  }
}
```

## 🛠️ Solución de Problemas

### Error de Permisos
```bash
# Dar permisos de escritura
chmod 755 backups/
chown usuario:grupo backups/
```

### Error de Espacio
```bash
# Verificar espacio disponible
df -h
# Limpiar backups antiguos
find backups/ -name "*.zip" -mtime +30 -delete
```

### Error de Compresión
```bash
# Verificar integridad
unzip -t backups/metgo_backup_*.zip
# Recrear backup si es necesario
python backup/backup_automatico.py
```

---

*Guía de Backup - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
