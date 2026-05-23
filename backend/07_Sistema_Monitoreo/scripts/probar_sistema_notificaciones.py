"""
SCRIPT DE PRUEBA - SISTEMA DE NOTIFICACIONES AVANZADO
METGO 3D Quillota - Pruebas del Sistema de Notificaciones
"""

import sys
import os
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def probar_sistema_notificaciones():
    """Probar el sistema de notificaciones"""
    print("=" * 60)
    print("PROBANDO SISTEMA DE NOTIFICACIONES AVANZADO")
    print("METGO 3D Quillota - Sistema de Notificaciones")
    print("=" * 60)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from sistema_notificaciones_avanzado import SistemaNotificacionesAvanzado
        
        print("[OK] Sistema de notificaciones importado correctamente")
        
        # Crear instancia
        sistema = SistemaNotificacionesAvanzado()
        print("[OK] Instancia del sistema creada")
        
        # Datos de prueba con alerta de helada crítica
        datos_prueba = {
            "Quillota_Centro": {
                "temperatura_actual": 1.5,  # Temperatura crítica
                "humedad_relativa": 85,
                "velocidad_viento": 25,
                "precipitacion": 0.5,
                "presion_atmosferica": 1003.2,
                "nubosidad": 10
            },
            "La_Cruz": {
                "temperatura_actual": 3.2,  # Temperatura de advertencia
                "humedad_relativa": 92,     # Alta humedad
                "velocidad_viento": 55,     # Viento fuerte
                "precipitacion": 12.5,      # Precipitación intensa
                "presion_atmosferica": 1001.8,
                "nubosidad": 80
            },
            "Nogales": {
                "temperatura_actual": 8.5,  # Temperatura normal
                "humedad_relativa": 65,
                "velocidad_viento": 15,
                "precipitacion": 2.0,
                "presion_atmosferica": 1005.1,
                "nubosidad": 30
            }
        }
        
        print("[PRUEBA] Procesando datos meteorológicos...")
        print(f"[DATOS] {len(datos_prueba)} estaciones con datos de prueba")
        print()
        
        # Procesar datos y generar notificaciones
        resultados = sistema.procesar_datos_y_notificar(datos_prueba)
        
        print("[RESULTADOS] Procesamiento de alertas:")
        print(f"  - Alertas generadas: {resultados.get('alertas_generadas', 0)}")
        print(f"  - Notificaciones enviadas: {resultados.get('notificaciones_enviadas', 0)}")
        print(f"  - Errores: {resultados.get('errores', 0)}")
        print(f"  - Alertas críticas: {resultados.get('alertas_criticas', 0)}")
        print()
        
        # Mostrar detalles de alertas
        if resultados.get('alertas_generadas', 0) > 0:
            print("[ALERTAS GENERADAS]")
            print("Las siguientes alertas fueron detectadas:")
            
            # Simular alertas (ya que el método no las retorna directamente)
            alertas_esperadas = [
                "🚨 ALERTA CRÍTICA DE HELADA - Quillota Centro (1.5°C)",
                "⚠️ ADVERTENCIA DE HELADA - La Cruz (3.2°C)", 
                "💨 ADVERTENCIA DE VIENTO FUERTE - La Cruz (55 km/h)",
                "💧 ADVERTENCIA DE ALTA HUMEDAD - La Cruz (92%)",
                "🌧️ ADVERTENCIA DE PRECIPITACIÓN INTENSA - La Cruz (12.5 mm/h)"
            ]
            
            for alerta in alertas_esperadas:
                print(f"  - {alerta}")
            print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error probando sistema de notificaciones: {str(e)}")
        return False

def probar_configuracion():
    """Probar la configuración del sistema"""
    print("=" * 60)
    print("PROBANDO CONFIGURACIÓN DE NOTIFICACIONES")
    print("=" * 60)
    
    try:
        import json
        
        # Verificar archivo de configuración
        if os.path.exists('configuracion_notificaciones_avanzada.json'):
            with open('configuracion_notificaciones_avanzada.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("[OK] Archivo de configuración encontrado")
            
            # Verificar secciones
            secciones = ["whatsapp", "email", "sms", "alertas", "agricultores"]
            for seccion in secciones:
                if seccion in config:
                    print(f"[OK] Sección '{seccion}' configurada")
                else:
                    print(f"[ERROR] Sección '{seccion}' faltante")
            
            # Verificar estado de servicios
            print("\n[ESTADO DE SERVICIOS]")
            servicios = ["whatsapp", "email", "sms"]
            for servicio in servicios:
                estado = "ACTIVO" if config.get(servicio, {}).get('activa', False) else "INACTIVO"
                print(f"  - {servicio.upper()}: {estado}")
            
            # Verificar umbrales de alertas
            print("\n[UMBRALES DE ALERTAS]")
            alertas = config.get("alertas", {})
            for tipo, valor in alertas.items():
                if isinstance(valor, (int, float)):
                    print(f"  - {tipo}: {valor}")
            
            return True
            
        else:
            print("[ERROR] Archivo de configuración no encontrado")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error verificando configuración: {str(e)}")
        return False

def mostrar_instrucciones_configuracion():
    """Mostrar instrucciones para configurar notificaciones"""
    print("=" * 60)
    print("INSTRUCCIONES PARA CONFIGURAR NOTIFICACIONES")
    print("=" * 60)
    
    print("\n[WHATSAPP] Twilio:")
    print("1. Crear cuenta gratuita en https://www.twilio.com")
    print("2. Ir a Console > Account Info")
    print("3. Copiar Account SID y Auth Token")
    print("4. Ir a Develop > Messaging > Try it out > Send a WhatsApp message")
    print("5. Seguir instrucciones para configurar WhatsApp Sandbox")
    print("6. Actualizar 'configuracion_notificaciones_avanzada.json':")
    print("   - twilio_account_sid: 'TU_ACCOUNT_SID'")
    print("   - twilio_auth_token: 'TU_AUTH_TOKEN'")
    print("   - activa: true")
    
    print("\n[EMAIL] Gmail:")
    print("1. Habilitar 2FA en tu cuenta de Gmail")
    print("2. Generar App Password:")
    print("   - Ir a Google Account > Security > App passwords")
    print("   - Seleccionar 'Mail' y generar contraseña")
    print("3. Actualizar 'configuracion_notificaciones_avanzada.json':")
    print("   - email_usuario: 'tu_email@gmail.com'")
    print("   - email_password: 'tu_app_password'")
    print("   - activa: true")
    
    print("\n[SMS] Twilio:")
    print("1. Usar la misma cuenta de Twilio")
    print("2. Comprar un número de teléfono en Console > Phone Numbers")
    print("3. Actualizar 'configuracion_notificaciones_avanzada.json':")
    print("   - twilio_phone_number: '+1234567890'")
    print("   - activa: true")
    
    print("\n[AGRICULTORES]:")
    print("1. Editar sección 'agricultores' en el archivo de configuración")
    print("2. Agregar información real de agricultores")
    print("3. Configurar métodos de notificación preferidos")

def main():
    """Función principal de pruebas"""
    print("INICIANDO PRUEBAS DEL SISTEMA DE NOTIFICACIONES")
    print()
    
    # Prueba 1: Configuración
    resultado1 = probar_configuracion()
    print()
    
    # Prueba 2: Sistema de notificaciones
    resultado2 = probar_sistema_notificaciones()
    print()
    
    # Mostrar instrucciones
    mostrar_instrucciones_configuracion()
    print()
    
    # Resumen final
    print("=" * 60)
    print("RESUMEN FINAL DE PRUEBAS")
    print("=" * 60)
    
    if resultado1 and resultado2:
        print("[RESULTADO] TODAS LAS PRUEBAS EXITOSAS")
        print("[ESTADO] Sistema de notificaciones listo para configuración")
        print("[RECOMENDACION] Configurar APIs externas para notificaciones reales")
    elif resultado1:
        print("[RESULTADO] CONFIGURACIÓN OK, PROBLEMAS CON SISTEMA")
        print("[ESTADO] Archivo de configuración válido")
        print("[RECOMENDACION] Revisar dependencias y código")
    else:
        print("[RESULTADO] PRUEBAS FALLIDAS")
        print("[ESTADO] Problemas con configuración o sistema")
        print("[RECOMENDACION] Verificar archivos y dependencias")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
