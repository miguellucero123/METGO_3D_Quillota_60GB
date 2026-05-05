# 🤖 AUTOMATIZACIÓN DEL SISTEMA METGO

## 📋 Scripts Disponibles

### **1. Inicio Automático**
```bash
python iniciar_sistema_automatico.py
```
- Inicia todos los 15 dashboards automáticamente
- Verifica que no haya conflictos de puertos
- Muestra el estado de cada dashboard

### **2. Detención Automática**
```bash
python detener_sistema.py
```
- Detiene todos los dashboards del sistema
- Libera todos los puertos
- Verifica que el sistema esté completamente detenido

### **3. Monitoreo del Sistema**
```bash
python monitorear_sistema.py
```
- Muestra el estado de todos los dashboards
- Información de CPU y memoria de cada proceso
- Tiempo de ejecución de cada dashboard
- Estado general del sistema

### **4. Reinicio del Sistema**
```bash
python reiniciar_sistema.py
```
- Detiene y reinicia todo el sistema automáticamente
- Útil para aplicar cambios o resolver problemas

## 🚀 INICIO AUTOMÁTICO CON WINDOWS

### **Instalación:**
1. Ejecuta `instalar_inicio_automatico.bat` como **Administrador**
2. El sistema se iniciará automáticamente al encender Windows

### **Desinstalación:**
1. Ejecuta `desinstalar_inicio_automatico.bat`
2. El sistema ya no se iniciará automáticamente

## 📱 ACCESO AL SISTEMA

### **URL Principal:**
```
http://192.168.1.7:8501
```

### **Todos los Dashboards:**
- Dashboard Principal: `http://192.168.1.7:8501`
- Meteorológico: `http://192.168.1.7:8502`
- Agrícola: `http://192.168.1.7:8503`
- Monitoreo: `http://192.168.1.7:8504`
- IA/ML: `http://192.168.1.7:8505`
- Visualizaciones: `http://192.168.1.7:8506`
- Global: `http://192.168.1.7:8507`
- Precisión: `http://192.168.1.7:8508`
- Comparativo: `http://192.168.1.7:8509`
- Alertas: `http://192.168.1.7:8510`
- Simple: `http://192.168.1.7:8511`
- Unificado: `http://192.168.1.7:8512`
- Móvil: `http://192.168.1.7:8513`
- Notificaciones: `http://192.168.1.7:8514`
- Caché: `http://192.168.1.7:8515`

## 🔧 COMANDOS ÚTILES

### **Inicio Rápido:**
```bash
python iniciar_sistema_automatico.py
```

### **Verificar Estado:**
```bash
python monitorear_sistema.py
```

### **Reiniciar Sistema:**
```bash
python reiniciar_sistema.py
```

### **Detener Todo:**
```bash
python detener_sistema.py
```

## 📊 MONITOREO CONTINUO

Para monitorear el sistema continuamente, puedes usar:

```bash
# En Windows PowerShell
while ($true) { python monitorear_sistema.py; Start-Sleep 30 }
```

## ⚠️ NOTAS IMPORTANTES

1. **Puertos:** Asegúrate de que los puertos 8501-8515 estén libres
2. **Firewall:** Configura el firewall para permitir conexiones en estos puertos
3. **Red:** Todos los dispositivos deben estar en la misma red WiFi
4. **Python:** Asegúrate de tener Python 3.11+ instalado
5. **Dependencias:** Instala las dependencias con `pip install -r requirements.txt`

## 🆘 SOLUCIÓN DE PROBLEMAS

### **Si un dashboard no inicia:**
1. Ejecuta `python detener_sistema.py`
2. Espera 5 segundos
3. Ejecuta `python iniciar_sistema_automatico.py`

### **Si hay conflictos de puertos:**
1. Ejecuta `python detener_sistema.py`
2. Reinicia el sistema
3. Ejecuta `python iniciar_sistema_automatico.py`

### **Si el sistema no responde:**
1. Ejecuta `python monitorear_sistema.py` para ver el estado
2. Si es necesario, reinicia manualmente con `python reiniciar_sistema.py`

## 📞 SOPORTE

Para más ayuda, revisa los logs en la carpeta `logs/` o ejecuta `python monitorear_sistema.py` para diagnóstico.
