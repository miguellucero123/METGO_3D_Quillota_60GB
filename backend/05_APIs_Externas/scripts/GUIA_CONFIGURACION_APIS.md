# 📱 GUÍA RÁPIDA: CONFIGURACIÓN DE APIs REALES

**METGO 3D Quillota - Sistema de Notificaciones**

---

## 🚀 **CONFIGURACIÓN RÁPIDA (5 MINUTOS)**

### **Opción 1: Configuración Automática**
```bash
python configurar_apis_reales.py
```
*Sigue las instrucciones paso a paso*

### **Opción 2: Configuración Manual**
Edita directamente el archivo `configuracion_notificaciones_avanzada.json`

---

## 📱 **WHATSAPP (TWILIO) - GRATUITO**

### **Paso 1: Crear Cuenta Twilio**
1. Ir a: https://www.twilio.com
2. Hacer clic en "Sign up" (gratuito)
3. Completar registro con email y teléfono
4. Verificar email y teléfono

### **Paso 2: Obtener Credenciales**
1. Ir a Console > Account Info
2. Copiar:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### **Paso 3: Configurar WhatsApp Sandbox**
1. Ir a Develop > Messaging > Try it out > Send a WhatsApp message
2. Seguir instrucciones para WhatsApp Sandbox
3. El número será: `whatsapp:+14155238886`

### **Paso 4: Configurar en METGO**
```json
"whatsapp": {
    "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_whatsapp_number": "whatsapp:+14155238886",
    "activa": true
}
```

---

## 📧 **EMAIL (GMAIL) - GRATUITO**

### **Paso 1: Habilitar 2FA en Gmail**
1. Ir a: https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos"
3. Completar configuración

### **Paso 2: Generar App Password**
1. Ir a: https://myaccount.google.com/apppasswords
2. Seleccionar "Mail" como aplicación
3. Generar contraseña (16 caracteres)
4. Copiar la contraseña generada

### **Paso 3: Configurar en METGO**
```json
"email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_usuario": "tu_email@gmail.com",
    "email_password": "abcd efgh ijkl mnop",
    "activa": true
}
```

---

## 📱 **SMS (TWILIO) - $1 USD/MES**

### **Paso 1: Comprar Número de Teléfono**
1. Usar la misma cuenta de Twilio del WhatsApp
2. Ir a Console > Phone Numbers > Manage > Buy a number
3. Seleccionar país (Chile: +56)
4. Comprar número (aproximadamente $1 USD/mes)

### **Paso 2: Configurar en METGO**
```json
"sms": {
    "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_phone_number": "+56912345678",
    "activa": true
}
```

---

## 👥 **AGRICULTORES**

### **Configuración de Agricultores**
```json
"agricultores": {
    "agricultor_1": {
        "nombre": "Juan Pérez - Finca Los Olivos",
        "telefono": "+56987654321",
        "email": "juan.perez@example.com",
        "cultivos": ["paltos", "citricos"],
        "notificaciones": {
            "whatsapp": true,
            "email": true,
            "sms": false
        }
    }
}
```

---

## 🧪 **PROBAR CONFIGURACIÓN**

### **Prueba Manual**
```bash
python probar_sistema_notificaciones.py
```

### **Prueba con Datos Reales**
```bash
python actualizador_datos_automatico.py manual
```

---

## 🔧 **CONFIGURACIÓN COMPLETA DE EJEMPLO**

```json
{
  "whatsapp": {
    "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_whatsapp_number": "whatsapp:+14155238886",
    "activa": true
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_usuario": "tu_email@gmail.com",
    "email_password": "abcd efgh ijkl mnop",
    "activa": true
  },
  "sms": {
    "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_phone_number": "+56912345678",
    "activa": true
  },
  "agricultores": {
    "agricultor_1": {
      "nombre": "Juan Pérez - Finca Los Olivos",
      "telefono": "+56987654321",
      "email": "juan.perez@example.com",
      "cultivos": ["paltos", "citricos"],
      "notificaciones": {
        "whatsapp": true,
        "email": true,
        "sms": false
      }
    }
  }
}
```

---

## ✅ **VERIFICACIÓN**

### **Sistema Funcionando Correctamente**
- ✅ APIs configuradas y activas
- ✅ Agricultores registrados
- ✅ Notificaciones enviándose
- ✅ Alertas automáticas funcionando

### **Comandos de Verificación**
```bash
# Verificar configuración
python probar_sistema_notificaciones.py

# Probar actualizador con notificaciones
python actualizador_datos_automatico.py manual

# Ejecutar actualizador automático
python iniciar_actualizador_automatico.py
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **WhatsApp no funciona**
- Verificar Account SID y Auth Token
- Confirmar que WhatsApp Sandbox está configurado
- Verificar que `"activa": true`

### **Email no funciona**
- Verificar que 2FA está habilitado en Gmail
- Confirmar App Password (16 caracteres)
- Verificar que `"activa": true`

### **SMS no funciona**
- Verificar que se compró un número de teléfono
- Confirmar Account SID y Auth Token
- Verificar que `"activa": true`

---

## 📞 **CONTACTO Y SOPORTE**

- **Twilio Support**: https://support.twilio.com
- **Gmail Help**: https://support.google.com/mail
- **METGO 3D**: Sistema de documentación integrado

---

*Guía de configuración METGO 3D Quillota - Sistema de Notificaciones*
