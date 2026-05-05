# 🌐 Instrucciones para Acceso Externo al Dashboard METGO

## 🚀 Solución Rápida - Opción 1: ngrok (Recomendado)

### 1. Ejecutar con ngrok:
```bash
python ejecutar_con_ngrok.py
```

### 2. Beneficios de ngrok:
- ✅ **Acceso público inmediato** sin configuración del router
- ✅ **URL pública temporal** que funciona desde cualquier lugar
- ✅ **Túnel seguro** con HTTPS automático
- ✅ **No requiere configuración** del router o firewall

---

## 🔧 Solución Completa - Opción 2: Configuración del Router

### 1. Configurar Firewall de Windows:
```bash
configurar_acceso_externo.bat
```

### 2. Configurar Router (Port Forwarding):

#### Acceso al Router:
- **URL:** http://192.168.1.1
- **Usuario:** admin
- **Password:** admin (o los de tu router)

#### Configuración de Port Forwarding:
1. Buscar **"Port Forwarding"** o **"Redirección de Puertos"**
2. Agregar nueva regla:
   - **Puerto Externo:** 8501
   - **Puerto Interno:** 8501
   - **IP Interna:** 192.168.1.7
   - **Protocolo:** TCP
   - **Estado:** Habilitado

### 3. URLs Disponibles:
- **🏠 Local:** http://localhost:8501
- **🏢 Red Local:** http://192.168.1.7:8501
- **🌍 Externa:** http://200.104.179.146:8501

---

## 📱 Acceso desde Dispositivos Móviles

### Desde la misma red WiFi:
```
http://192.168.1.7:8501
```

### Desde internet (si configuraste el router):
```
http://200.104.179.146:8501
```

### Con ngrok (URL pública):
```
https://xxxxx.ngrok.io (se genera automáticamente)
```

---

## 🛠️ Solución de Problemas

### ❌ "Conexión rechazada" desde internet:
1. **Verificar Port Forwarding** en el router
2. **Comprobar IP externa** real (puede cambiar)
3. **Usar ngrok** como alternativa rápida

### ❌ "Puerto ya en uso":
```bash
taskkill /F /IM python.exe
```

### ❌ Firewall bloqueando:
```bash
netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
```

---

## 🌟 Dashboards Disponibles

| Dashboard | Puerto | URL Local | URL Externa |
|-----------|--------|-----------|-------------|
| 🏠 Principal | 8501 | http://localhost:8501 | http://200.104.179.146:8501 |
| 🌤️ Meteorológico | 8503 | http://localhost:8503 | http://200.104.179.146:8503 |
| 🌾 Agrícola | 8504 | http://localhost:8504 | http://200.104.179.146:8504 |
| 🏠 Unificado | 8502 | http://localhost:8502 | http://200.104.179.146:8502 |
| 📊 Simple | 8505 | http://localhost:8505 | http://200.104.179.146:8505 |

---

## 🎯 Recomendaciones

### Para Uso Personal/Pruebas:
- ✅ **Usar ngrok** - Configuración automática
- ✅ **Acceso local** - http://192.168.1.7:8501

### Para Uso Profesional/Producción:
- ✅ **Configurar router** con Port Forwarding
- ✅ **Obtener IP fija** del ISP
- ✅ **Configurar dominio** personalizado
- ✅ **Usar HTTPS** con certificado SSL

---

## 📞 Soporte

Si tienes problemas:
1. **Verifica la IP externa:** http://whatismyipaddress.com
2. **Prueba ngrok** como alternativa
3. **Comprueba el firewall** de Windows
4. **Revisa la configuración** del router

---

## 🚀 Ejecución Rápida

```bash
# Opción 1: Con ngrok (Recomendado)
python ejecutar_con_ngrok.py

# Opción 2: Configuración completa
configurar_acceso_externo.bat

# Opción 3: Solo dashboard
python -m streamlit run sistema_auth_dashboard_principal_metgo.py --server.port 8501 --server.address 0.0.0.0
```

---

*Dashboard METGO - Sistema Integrado de Monitoreo Meteorológico y Agrícola para Quillota* 🌾
