"""
ACTIVADOR SIMPLE DE NOTIFICACIONES - METGO 3D QUILLOTA
Script simple para activar notificaciones básicas
"""

import json
import os
from datetime import datetime

def activar_notificaciones_basicas():
    """Activar notificaciones básicas sin APIs externas"""
    print("=" * 60)
    print("ACTIVADOR SIMPLE DE NOTIFICACIONES")
    print("METGO 3D Quillota - Configuración Básica")
    print("=" * 60)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar archivo de configuración
    archivo_config = 'configuracion_notificaciones_avanzada.json'
    
    if not os.path.exists(archivo_config):
        print(f"[ERROR] No se encontró: {archivo_config}")
        print("[SOLUCION] Ejecutar primero: python probar_sistema_notificaciones.py")
        return False
    
    try:
        # Cargar configuración actual
        with open(archivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("[OK] Configuración cargada")
        
        # Crear respaldo
        backup_file = f"configuracion_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"[RESPALDO] Guardado en: {backup_file}")
        
        # Configurar agricultores de prueba
        agricultores_prueba = {
            "agricultor_prueba": {
                "nombre": "Agricultor de Prueba - Valle de Quillota",
                "telefono": "+56912345678",
                "email": "prueba@example.com",
                "cultivos": ["paltos", "citricos", "verduras"],
                "notificaciones": {
                    "whatsapp": False,  # Inactivo hasta configurar Twilio
                    "email": False,     # Inactivo hasta configurar Gmail
                    "sms": False        # Inactivo hasta configurar Twilio
                }
            }
        }
        
        # Actualizar configuración
        config["agricultores"].update(agricultores_prueba)
        
        # Mantener servicios inactivos pero con configuración de ejemplo
        config["whatsapp"]["activa"] = False
        config["email"]["activa"] = False
        config["sms"]["activa"] = False
        
        # Guardar configuración actualizada
        with open(archivo_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("[OK] Configuración actualizada")
        
        # Mostrar estado
        print("\n[ESTADO ACTUAL]")
        print("WhatsApp: INACTIVO (requiere configuración Twilio)")
        print("Email: INACTIVO (requiere configuración Gmail)")
        print("SMS: INACTIVO (requiere configuración Twilio)")
        print("Agricultores: CONFIGURADOS (modo prueba)")
        
        # Mostrar instrucciones
        print("\n[INSTRUCCIONES PARA ACTIVAR]")
        print("1. WhatsApp: Configurar Twilio (gratuito)")
        print("2. Email: Configurar Gmail con App Password")
        print("3. SMS: Comprar número en Twilio ($1 USD/mes)")
        print("4. Ver guía: GUIA_CONFIGURACION_APIS.md")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error configurando: {e}")
        return False

def probar_sistema_actual():
    """Probar el sistema actual"""
    print("\n" + "="*50)
    print("PROBANDO SISTEMA ACTUAL")
    print("="*50)
    
    try:
        from sistema_notificaciones_avanzado import SistemaNotificacionesAvanzado
        
        sistema = SistemaNotificacionesAvanzado()
        
        # Datos de prueba con alerta crítica
        datos_prueba = {
            "Quillota_Centro": {
                "temperatura_actual": 1.5,  # Alerta crítica
                "humedad_relativa": 85,
                "velocidad_viento": 25,
                "precipitacion": 0.5
            },
            "La_Cruz": {
                "temperatura_actual": 3.2,  # Alerta advertencia
                "humedad_relativa": 92,     # Alta humedad
                "velocidad_viento": 55,     # Viento fuerte
                "precipitacion": 12.5,      # Precipitación intensa
                "presion_atmosferica": 1001.8,
                "nubosidad": 80
            }
        }
        
        print("[PRUEBA] Procesando alertas meteorológicas...")
        resultados = sistema.procesar_datos_y_notificar(datos_prueba)
        
        print(f"[RESULTADO] Alertas generadas: {resultados.get('alertas_generadas', 0)}")
        print(f"[RESULTADO] Notificaciones enviadas: {resultados.get('notificaciones_enviadas', 0)}")
        print(f"[RESULTADO] Errores: {resultados.get('errores', 0)}")
        print(f"[RESULTADO] Alertas críticas: {resultados.get('alertas_criticas', 0)}")
        
        if resultados.get('alertas_generadas', 0) > 0:
            print("[OK] Sistema detectando alertas correctamente")
            print("[INFO] Las notificaciones no se envían porque las APIs están inactivas")
            print("[SOLUCION] Configurar APIs para envío real de notificaciones")
        else:
            print("[ADVERTENCIA] No se generaron alertas")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error probando sistema: {e}")
        return False

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "="*60)
    print("OPCIONES DISPONIBLES")
    print("="*60)
    print("1. Configurar notificaciones básicas")
    print("2. Probar sistema actual")
    print("3. Ver guía de configuración")
    print("4. Salir")
    print()
    
    while True:
        try:
            opcion = input("Selecciona una opción (1-4): ").strip()
            if opcion in ["1", "2", "3", "4"]:
                return opcion
            else:
                print("[ERROR] Opción inválida. Ingresa 1, 2, 3 o 4.")
        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada")
            return "4"

def main():
    """Función principal"""
    print("INICIANDO ACTIVADOR SIMPLE DE NOTIFICACIONES")
    print()
    
    while True:
        opcion = mostrar_menu()
        
        if opcion == "1":
            activar_notificaciones_basicas()
        elif opcion == "2":
            probar_sistema_actual()
        elif opcion == "3":
            print("\n[GUÍA] Ver archivo: GUIA_CONFIGURACION_APIS.md")
            print("[GUÍA] O ejecutar: python configurar_apis_reales.py")
        elif opcion == "4":
            print("\n[INFO] Saliendo...")
            break
        
        if opcion != "4":
            input("\nPresiona Enter para continuar...")
            print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")



