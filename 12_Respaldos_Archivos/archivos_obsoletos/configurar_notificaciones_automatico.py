"""
CONFIGURADOR AUTOMÁTICO DE NOTIFICACIONES - METGO 3D QUILLOTA
Configura automáticamente las notificaciones sin interacción del usuario
"""

import json
import os
from datetime import datetime

def configurar_notificaciones_automatico():
    """Configurar notificaciones automáticamente"""
    print("CONFIGURANDO NOTIFICACIONES AUTOMÁTICAMENTE...")
    
    # Configuración básica de notificaciones
    configuracion = {
        "whatsapp": {
            "activo": True,
            "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "from_number": "whatsapp:+14155238886",
            "to_numbers": ["whatsapp:+56912345678"]
        },
        "email": {
            "activo": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "metgo.quillota@gmail.com",
            "password": "app_password_aqui",
            "from_email": "metgo.quillota@gmail.com",
            "to_emails": ["agricultor@quillota.cl", "admin@metgo.cl"]
        },
        "sms": {
            "activo": True,
            "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "auth_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "from_number": "+1234567890",
            "to_numbers": ["+56912345678"]
        },
        "alertas": {
            "helada_critica": {
                "temperatura_max": 2.0,
                "activo": True
            },
            "helada_advertencia": {
                "temperatura_max": 5.0,
                "activo": True
            },
            "viento_fuerte": {
                "velocidad": 50.0,
                "activo": True
            },
            "precipitacion_intensa": {
                "precipitacion": 10.0,
                "activo": True
            }
        },
        "agricultores": [
            {
                "nombre": "Juan Pérez",
                "telefono": "+56912345678",
                "email": "juan.perez@quillota.cl",
                "cultivos": ["paltos", "cítricos"],
                "activo": True
            },
            {
                "nombre": "María González",
                "telefono": "+56987654321",
                "email": "maria.gonzalez@quillota.cl",
                "cultivos": ["uvas", "paltos"],
                "activo": True
            }
        ],
        "configuracion_general": {
            "frecuencia_alertas": "inmediata",
            "hora_envio_diario": "08:00",
            "idioma": "es",
            "zona_horaria": "America/Santiago"
        }
    }
    
    # Guardar configuración
    try:
        with open('configuracion_notificaciones_avanzada.json', 'w', encoding='utf-8') as f:
            json.dump(configuracion, f, indent=2, ensure_ascii=False)
        
        print("[OK] Configuracion de notificaciones guardada exitosamente")
        print("[EMAIL] Email: Configurado (requiere app password)")
        print("[WHATSAPP] WhatsApp: Configurado (requiere credenciales Twilio)")
        print("[SMS] SMS: Configurado (requiere credenciales Twilio)")
        print("[ALERTAS] Alertas: Todas activadas")
        print("[AGRICULTORES] Agricultores: 2 configurados")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error guardando configuracion: {e}")
        return False

def verificar_configuracion():
    """Verificar que la configuración se guardó correctamente"""
    try:
        if os.path.exists('configuracion_notificaciones_avanzada.json'):
            with open('configuracion_notificaciones_avanzada.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            canales_activos = 0
            for canal in ['whatsapp', 'email', 'sms']:
                if config.get(canal, {}).get('activo', False):
                    canales_activos += 1
            
            print(f"\n[VERIFICACION] VERIFICACION:")
            print(f"   - Canales activos: {canales_activos}/3")
            print(f"   - Alertas configuradas: {len(config.get('alertas', {}))}")
            print(f"   - Agricultores: {len(config.get('agricultores', []))}")
            
            return canales_activos > 0
            
    except Exception as e:
        print(f"[ERROR] Error verificando configuracion: {e}")
        return False

def main():
    """Función principal"""
    print("="*60)
    print("CONFIGURADOR AUTOMÁTICO DE NOTIFICACIONES")
    print("METGO 3D QUILLOTA")
    print("="*60)
    
    # Configurar notificaciones
    if configurar_notificaciones_automatico():
        print("\n" + "="*60)
        print("CONFIGURACIÓN COMPLETADA")
        print("="*60)
        
        # Verificar configuración
        if verificar_configuracion():
            print("\n[OK] Sistema de notificaciones configurado correctamente")
            print("[NOTA] NOTA: Para activar notificaciones reales, actualiza las credenciales en:")
            print("   - configuracion_notificaciones_avanzada.json")
            print("   - Email: Usa App Password de Gmail")
            print("   - WhatsApp/SMS: Usa credenciales de Twilio")
        else:
            print("\n[ERROR] Error en la configuracion")
    else:
        print("\n[ERROR] No se pudo configurar el sistema")

if __name__ == "__main__":
    main()
