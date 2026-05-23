"""
CONFIGURADOR DE APIs REALES - METGO 3D QUILLOTA
Script interactivo para configurar APIs de notificaciones
"""

import json
import os
import sys
from datetime import datetime

def mostrar_banner():
    """Mostrar banner del configurador"""
    print("=" * 70)
    print("CONFIGURADOR DE APIs REALES - METGO 3D QUILLOTA")
    print("Sistema de Configuración de Notificaciones")
    print("=" * 70)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def verificar_archivo_configuracion():
    """Verificar si existe el archivo de configuración"""
    archivo = 'configuracion_notificaciones_avanzada.json'
    
    if not os.path.exists(archivo):
        print(f"[ERROR] No se encontró el archivo: {archivo}")
        print("[SOLUCION] Ejecutar primero: python probar_sistema_notificaciones.py")
        return False
    
    print(f"[OK] Archivo de configuración encontrado: {archivo}")
    return True

def cargar_configuracion():
    """Cargar configuración actual"""
    try:
        with open('configuracion_notificaciones_avanzada.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Error cargando configuración: {e}")
        return None

def guardar_configuracion(config):
    """Guardar configuración actualizada"""
    try:
        # Crear respaldo
        backup_file = f"configuracion_notificaciones_avanzada_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if os.path.exists('configuracion_notificaciones_avanzada.json'):
            with open('configuracion_notificaciones_avanzada.json', 'r', encoding='utf-8') as f:
                backup_config = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_config)
            print(f"[RESPALDO] Configuración respaldada en: {backup_file}")
        
        # Guardar nueva configuración
        with open('configuracion_notificaciones_avanzada.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("[OK] Configuración guardada exitosamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error guardando configuración: {e}")
        return False

def configurar_whatsapp():
    """Configurar WhatsApp con Twilio"""
    print("\n" + "="*50)
    print("CONFIGURACIÓN DE WHATSAPP (TWILIO)")
    print("="*50)
    
    print("\n[PASO 1] Crear cuenta en Twilio:")
    print("1. Ir a: https://www.twilio.com")
    print("2. Hacer clic en 'Sign up' (gratuito)")
    print("3. Completar registro con email y teléfono")
    print("4. Verificar email y teléfono")
    
    input("\nPresiona Enter cuando hayas creado la cuenta...")
    
    print("\n[PASO 2] Obtener credenciales:")
    print("1. Ir a Console > Account Info")
    print("2. Copiar 'Account SID' y 'Auth Token'")
    print("3. NO compartir estas credenciales")
    
    account_sid = input("\nIngresa tu Account SID: ").strip()
    auth_token = input("Ingresa tu Auth Token: ").strip()
    
    print("\n[PASO 3] Configurar WhatsApp Sandbox:")
    print("1. Ir a Develop > Messaging > Try it out > Send a WhatsApp message")
    print("2. Seguir las instrucciones para configurar WhatsApp Sandbox")
    print("3. El número de WhatsApp será: whatsapp:+14155238886")
    
    activar = input("\n¿Deseas activar WhatsApp? (s/n): ").strip().lower()
    
    return {
        "twilio_account_sid": account_sid,
        "twilio_auth_token": auth_token,
        "twilio_whatsapp_number": "whatsapp:+14155238886",
        "activa": activar == 's'
    }

def configurar_email():
    """Configurar Email con Gmail"""
    print("\n" + "="*50)
    print("CONFIGURACIÓN DE EMAIL (GMAIL)")
    print("="*50)
    
    print("\n[PASO 1] Habilitar 2FA en Gmail:")
    print("1. Ir a: https://myaccount.google.com/security")
    print("2. Activar 'Verificación en 2 pasos'")
    print("3. Completar configuración")
    
    input("\nPresiona Enter cuando hayas habilitado 2FA...")
    
    print("\n[PASO 2] Generar App Password:")
    print("1. Ir a: https://myaccount.google.com/apppasswords")
    print("2. Seleccionar 'Mail' como aplicación")
    print("3. Generar contraseña (16 caracteres)")
    print("4. Copiar la contraseña generada")
    
    email_usuario = input("\nIngresa tu email de Gmail: ").strip()
    app_password = input("Ingresa tu App Password (16 caracteres): ").strip()
    
    activar = input("\n¿Deseas activar Email? (s/n): ").strip().lower()
    
    return {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email_usuario": email_usuario,
        "email_password": app_password,
        "activa": activar == 's'
    }

def configurar_sms():
    """Configurar SMS con Twilio"""
    print("\n" + "="*50)
    print("CONFIGURACIÓN DE SMS (TWILIO)")
    print("="*50)
    
    print("\n[NOTA] Para SMS necesitas:")
    print("1. Usar la misma cuenta de Twilio del WhatsApp")
    print("2. Comprar un número de teléfono")
    print("3. Costo aproximado: $1 USD/mes")
    
    continuar = input("\n¿Deseas continuar con SMS? (s/n): ").strip().lower()
    
    if continuar != 's':
        return {
            "twilio_account_sid": "YOUR_TWILIO_ACCOUNT_SID",
            "twilio_auth_token": "YOUR_TWILIO_AUTH_TOKEN",
            "twilio_phone_number": "+1234567890",
            "activa": False
        }
    
    print("\n[PASO 1] Comprar número de teléfono:")
    print("1. Ir a Console > Phone Numbers > Manage > Buy a number")
    print("2. Seleccionar país (Chile: +56)")
    print("3. Comprar número (aproximadamente $1 USD/mes)")
    print("4. Copiar el número comprado")
    
    account_sid = input("\nIngresa tu Account SID (mismo del WhatsApp): ").strip()
    auth_token = input("Ingresa tu Auth Token (mismo del WhatsApp): ").strip()
    phone_number = input("Ingresa tu número de teléfono comprado (ej: +56912345678): ").strip()
    
    activar = input("\n¿Deseas activar SMS? (s/n): ").strip().lower()
    
    return {
        "twilio_account_sid": account_sid,
        "twilio_auth_token": auth_token,
        "twilio_phone_number": phone_number,
        "activa": activar == 's'
    }

def configurar_agricultores():
    """Configurar agricultores reales"""
    print("\n" + "="*50)
    print("CONFIGURACIÓN DE AGRICULTORES")
    print("="*50)
    
    agricultores = {}
    
    print("\n[AGRICULTOR 1 - PREDETERMINADO]")
    nombre1 = input("Nombre del agricultor 1 (ej: Juan Pérez): ").strip() or "Juan Pérez - Finca Los Olivos"
    telefono1 = input("Teléfono (ej: +56987654321): ").strip() or "+56987654321"
    email1 = input("Email: ").strip() or "juan.perez@example.com"
    cultivos1 = input("Cultivos (separados por coma): ").strip() or "paltos, citricos"
    
    print("\n¿Qué notificaciones desea recibir?")
    whatsapp1 = input("WhatsApp? (s/n): ").strip().lower() == 's'
    email_notif1 = input("Email? (s/n): ").strip().lower() == 's'
    sms1 = input("SMS? (s/n): ").strip().lower() == 's'
    
    agricultores["agricultor_1"] = {
        "nombre": nombre1,
        "telefono": telefono1,
        "email": email1,
        "cultivos": cultivos1.split(','),
        "notificaciones": {
            "whatsapp": whatsapp1,
            "email": email_notif1,
            "sms": sms1
        }
    }
    
    # Preguntar por más agricultores
    mas_agricultores = input("\n¿Deseas agregar más agricultores? (s/n): ").strip().lower()
    
    if mas_agricultores == 's':
        contador = 2
        while True:
            print(f"\n[AGRICULTOR {contador}]")
            nombre = input(f"Nombre del agricultor {contador}: ").strip()
            if not nombre:
                break
                
            telefono = input("Teléfono: ").strip()
            email = input("Email: ").strip()
            cultivos = input("Cultivos (separados por coma): ").strip()
            
            print("¿Qué notificaciones desea recibir?")
            whatsapp = input("WhatsApp? (s/n): ").strip().lower() == 's'
            email_notif = input("Email? (s/n): ").strip().lower() == 's'
            sms = input("SMS? (s/n): ").strip().lower() == 's'
            
            agricultores[f"agricultor_{contador}"] = {
                "nombre": nombre,
                "telefono": telefono,
                "email": email,
                "cultivos": cultivos.split(',') if cultivos else [],
                "notificaciones": {
                    "whatsapp": whatsapp,
                    "email": email_notif,
                    "sms": sms
                }
            }
            
            contador += 1
            continuar = input("\n¿Agregar otro agricultor? (s/n): ").strip().lower()
            if continuar != 's':
                break
    
    return agricultores

def mostrar_resumen_configuracion(config):
    """Mostrar resumen de la configuración"""
    print("\n" + "="*70)
    print("RESUMEN DE CONFIGURACIÓN")
    print("="*70)
    
    print("\n[SERVICIOS CONFIGURADOS]")
    servicios = ["whatsapp", "email", "sms"]
    for servicio in servicios:
        estado = "ACTIVO" if config.get(servicio, {}).get('activa', False) else "INACTIVO"
        print(f"  - {servicio.upper()}: {estado}")
    
    print("\n[AGRICULTORES CONFIGURADOS]")
    agricultores = config.get("agricultores", {})
    for key, agricultor in agricultores.items():
        if key != "default":
            print(f"  - {agricultor['nombre']}")
            print(f"    Teléfono: {agricultor.get('telefono', 'N/A')}")
            print(f"    Email: {agricultor.get('email', 'N/A')}")
            print(f"    Cultivos: {', '.join(agricultor.get('cultivos', []))}")
            notif = agricultor.get('notificaciones', {})
            metodos = []
            if notif.get('whatsapp'): metodos.append('WhatsApp')
            if notif.get('email'): metodos.append('Email')
            if notif.get('sms'): metodos.append('SMS')
            print(f"    Notificaciones: {', '.join(metodos) if metodos else 'Ninguna'}")

def probar_configuracion():
    """Probar la configuración"""
    print("\n" + "="*50)
    print("PROBANDO CONFIGURACIÓN")
    print("="*50)
    
    try:
        # Importar y probar sistema de notificaciones
        from sistema_notificaciones_avanzado import SistemaNotificacionesAvanzado
        
        sistema = SistemaNotificacionesAvanzado()
        
        # Datos de prueba
        datos_prueba = {
            "Quillota_Centro": {
                "temperatura_actual": 1.5,  # Alerta crítica
                "humedad_relativa": 85,
                "velocidad_viento": 25,
                "precipitacion": 0.5
            }
        }
        
        print("[PRUEBA] Procesando alertas de prueba...")
        resultados = sistema.procesar_datos_y_notificar(datos_prueba)
        
        print(f"[RESULTADO] Alertas generadas: {resultados.get('alertas_generadas', 0)}")
        print(f"[RESULTADO] Notificaciones enviadas: {resultados.get('notificaciones_enviadas', 0)}")
        print(f"[RESULTADO] Errores: {resultados.get('errores', 0)}")
        
        if resultados.get('notificaciones_enviadas', 0) > 0:
            print("[OK] Sistema de notificaciones funcionando correctamente")
            return True
        else:
            print("[ADVERTENCIA] No se enviaron notificaciones (puede ser normal si las APIs están inactivas)")
            return True
            
    except Exception as e:
        print(f"[ERROR] Error probando configuración: {e}")
        return False

def main():
    """Función principal"""
    mostrar_banner()
    
    # Verificar archivo de configuración
    if not verificar_archivo_configuracion():
        return
    
    # Cargar configuración actual
    config = cargar_configuracion()
    if not config:
        return
    
    print("[INICIO] Configuración interactiva de APIs")
    print("\nEste proceso te guiará paso a paso para configurar:")
    print("1. WhatsApp (Twilio) - Gratuito")
    print("2. Email (Gmail) - Gratuito")
    print("3. SMS (Twilio) - $1 USD/mes")
    print("4. Agricultores reales")
    
    continuar = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    if continuar != 's':
        print("[INFO] Configuración cancelada")
        return
    
    # Configurar servicios
    print("\n[CONFIGURANDO] WhatsApp...")
    config["whatsapp"] = configurar_whatsapp()
    
    print("\n[CONFIGURANDO] Email...")
    config["email"] = configurar_email()
    
    print("\n[CONFIGURANDO] SMS...")
    config["sms"] = configurar_sms()
    
    print("\n[CONFIGURANDO] Agricultores...")
    agricultores_nuevos = configurar_agricultores()
    config["agricultores"].update(agricultores_nuevos)
    
    # Mostrar resumen
    mostrar_resumen_configuracion(config)
    
    # Confirmar guardado
    guardar = input("\n¿Deseas guardar esta configuración? (s/n): ").strip().lower()
    if guardar == 's':
        if guardar_configuracion(config):
            print("\n[CONFIGURACIÓN COMPLETADA]")
            
            # Probar configuración
            probar = input("\n¿Deseas probar la configuración? (s/n): ").strip().lower()
            if probar == 's':
                probar_configuracion()
            
            print("\n[PRÓXIMOS PASOS]")
            print("1. El sistema de notificaciones está configurado")
            print("2. Las notificaciones se enviarán automáticamente")
            print("3. Puedes ejecutar el actualizador automático")
            print("4. Continuar con el Día 3 del plan")
        else:
            print("[ERROR] No se pudo guardar la configuración")
    else:
        print("[INFO] Configuración no guardada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Configuración interrumpida por el usuario")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
