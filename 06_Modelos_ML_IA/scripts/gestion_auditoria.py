#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE AUDITORÍA DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE AUDITORÍA DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class GestorAuditoria:
    """Clase para gestión de auditoría del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_auditoria': 'auditoria',
            'archivo_auditoria': 'auditoria/auditoria.json',
            'archivo_config': 'config/auditoria.yaml',
            'retencion_dias': 90,
            'nivel_log': 'INFO'
        }
        
        self.eventos = [
            'login',
            'logout',
            'crear_usuario',
            'eliminar_usuario',
            'modificar_configuracion',
            'ejecutar_analisis',
            'generar_reporte',
            'acceso_datos',
            'error_sistema',
            'alerta_seguridad'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de auditoría"""
        try:
            print_info("Cargando configuración de auditoría...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_auditoria(self):
        """Crear estructura de auditoría"""
        try:
            print_info("Creando estructura de auditoría...")
            
            # Crear directorio principal
            auditoria_dir = Path(self.configuracion['directorio_auditoria'])
            auditoria_dir.mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            # Crear archivo de auditoría si no existe
            archivo_auditoria = Path(self.configuracion['archivo_auditoria'])
            if not archivo_auditoria.exists():
                with open(archivo_auditoria, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de auditoría creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # config/auditoria.yaml
            config_content = '''# Configuración de auditoría del sistema METGO 3D

auditoria:
  retencion_dias: 90
  nivel_log: INFO
  
  eventos:
    - login
    - logout
    - crear_usuario
    - eliminar_usuario
    - modificar_configuracion
    - ejecutar_analisis
    - generar_reporte
    - acceso_datos
    - error_sistema
    - alerta_seguridad
  
  campos_obligatorios:
    - timestamp
    - evento
    - usuario
    - ip
    - resultado
  
  alertas:
    intentos_fallidos: 3
    accesos_no_autorizados: 1
    modificaciones_criticas: 1
'''
            
            config_file = Path('config/auditoria.yaml')
            config_file.parent.mkdir(exist_ok=True)
            config_file.write_text(config_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def registrar_evento(self, evento, usuario, ip, resultado, detalles=None):
        """Registrar evento de auditoría"""
        try:
            print_info(f"Registrando evento: {evento}")
            
            # Crear registro de auditoría
            registro = {
                'timestamp': datetime.now().isoformat(),
                'evento': evento,
                'usuario': usuario,
                'ip': ip,
                'resultado': resultado,
                'detalles': detalles or {},
                'id': hashlib.md5(f"{evento}{usuario}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
            }
            
            # Cargar registros existentes
            archivo_auditoria = Path(self.configuracion['archivo_auditoria'])
            if archivo_auditoria.exists():
                with open(archivo_auditoria, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
            else:
                registros = []
            
            # Agregar nuevo registro
            registros.append(registro)
            
            # Guardar registros
            with open(archivo_auditoria, 'w', encoding='utf-8') as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)
            
            print_success(f"Evento {evento} registrado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error registrando evento: {e}")
            return False
    
    def consultar_eventos(self, evento=None, usuario=None, fecha_inicio=None, fecha_fin=None):
        """Consultar eventos de auditoría"""
        try:
            print_info("Consultando eventos de auditoría...")
            
            # Cargar registros
            archivo_auditoria = Path(self.configuracion['archivo_auditoria'])
            if not archivo_auditoria.exists():
                print_warning("No hay registros de auditoría")
                return []
            
            with open(archivo_auditoria, 'r', encoding='utf-8') as f:
                registros = json.load(f)
            
            # Filtrar registros
            registros_filtrados = registros
            
            if evento:
                registros_filtrados = [r for r in registros_filtrados if r['evento'] == evento]
            
            if usuario:
                registros_filtrados = [r for r in registros_filtrados if r['usuario'] == usuario]
            
            if fecha_inicio:
                fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
                registros_filtrados = [r for r in registros_filtrados 
                                    if datetime.fromisoformat(r['timestamp']) >= fecha_inicio_dt]
            
            if fecha_fin:
                fecha_fin_dt = datetime.fromisoformat(fecha_fin)
                registros_filtrados = [r for r in registros_filtrados 
                                    if datetime.fromisoformat(r['timestamp']) <= fecha_fin_dt]
            
            print_success(f"Eventos encontrados: {len(registros_filtrados)}")
            return registros_filtrados
            
        except Exception as e:
            print_error(f"Error consultando eventos: {e}")
            return []
    
    def generar_reporte_auditoria(self, fecha_inicio=None, fecha_fin=None):
        """Generar reporte de auditoría"""
        try:
            print_info("Generando reporte de auditoría...")
            
            # Consultar eventos
            eventos = self.consultar_eventos(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'periodo': {
                    'inicio': fecha_inicio or 'N/A',
                    'fin': fecha_fin or 'N/A'
                },
                'resumen': {
                    'total_eventos': len(eventos),
                    'eventos_por_tipo': {},
                    'eventos_por_usuario': {},
                    'eventos_por_resultado': {}
                },
                'eventos': eventos
            }
            
            # Contar eventos por tipo
            for evento in self.eventos:
                count = len([e for e in eventos if e['evento'] == evento])
                reporte['resumen']['eventos_por_tipo'][evento] = count
            
            # Contar eventos por usuario
            usuarios = set(e['usuario'] for e in eventos)
            for usuario in usuarios:
                count = len([e for e in eventos if e['usuario'] == usuario])
                reporte['resumen']['eventos_por_usuario'][usuario] = count
            
            # Contar eventos por resultado
            resultados = set(e['resultado'] for e in eventos)
            for resultado in resultados:
                count = len([e for e in eventos if e['resultado'] == resultado])
                reporte['resumen']['eventos_por_resultado'][resultado] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de auditoría generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de auditoría:")
            print(f"Total de eventos: {reporte['resumen']['total_eventos']}")
            print(f"Eventos por tipo: {reporte['resumen']['eventos_por_tipo']}")
            print(f"Eventos por usuario: {reporte['resumen']['eventos_por_usuario']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None
    
    def limpiar_auditoria(self, dias=None):
        """Limpiar registros de auditoría antiguos"""
        try:
            print_info("Limpiando registros de auditoría antiguos...")
            
            # Usar días de configuración si no se especifica
            if dias is None:
                dias = self.configuracion['retencion_dias']
            
            # Calcular fecha límite
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Cargar registros
            archivo_auditoria = Path(self.configuracion['archivo_auditoria'])
            if not archivo_auditoria.exists():
                print_warning("No hay registros de auditoría")
                return True
            
            with open(archivo_auditoria, 'r', encoding='utf-8') as f:
                registros = json.load(f)
            
            # Filtrar registros recientes
            registros_recientes = [r for r in registros 
                                if datetime.fromisoformat(r['timestamp']) >= fecha_limite]
            
            # Guardar registros filtrados
            with open(archivo_auditoria, 'w', encoding='utf-8') as f:
                json.dump(registros_recientes, f, indent=2, ensure_ascii=False)
            
            registros_eliminados = len(registros) - len(registros_recientes)
            print_success(f"Registros eliminados: {registros_eliminados}")
            print_success(f"Registros restantes: {len(registros_recientes)}")
            
            return True
            
        except Exception as e:
            print_error(f"Error limpiando auditoría: {e}")
            return False

def mostrar_menu():
    """Mostrar menú de gestión de auditoría"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE AUDITORÍA - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de auditoría")
    print("3. 📝 Registrar evento")
    print("4. 🔍 Consultar eventos")
    print("5. 📊 Generar reporte")
    print("6. 🧹 Limpiar auditoría")
    print("7. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de auditoría"""
    print_header()
    
    # Crear gestor de auditoría
    gestor = GestorAuditoria()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-7): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de auditoría")
                if gestor.crear_estructura_auditoria():
                    print_success("Estructura de auditoría creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Registrando evento")
                try:
                    evento = input(f"Evento ({', '.join(gestor.eventos)}): ").strip()
                    usuario = input("Usuario: ").strip()
                    ip = input("IP: ").strip()
                    resultado = input("Resultado: ").strip()
                    detalles = input("Detalles (JSON opcional): ").strip()
                    
                    if detalles:
                        try:
                            detalles = json.loads(detalles)
                        except json.JSONDecodeError:
                            print_warning("Detalles no válidos, ignorando")
                            detalles = None
                    
                    if gestor.registrar_evento(evento, usuario, ip, resultado, detalles):
                        print_success("Evento registrado correctamente")
                    else:
                        print_error("Error registrando evento")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Consultando eventos")
                try:
                    evento = input("Evento (opcional): ").strip() or None
                    usuario = input("Usuario (opcional): ").strip() or None
                    fecha_inicio = input("Fecha inicio (YYYY-MM-DD, opcional): ").strip() or None
                    fecha_fin = input("Fecha fin (YYYY-MM-DD, opcional): ").strip() or None
                    
                    eventos = gestor.consultar_eventos(evento, usuario, fecha_inicio, fecha_fin)
                    if eventos:
                        print_success(f"Eventos encontrados: {len(eventos)}")
                        for evento in eventos[:5]:  # Mostrar solo los primeros 5
                            print(f"- {evento['timestamp']} | {evento['evento']} | {evento['usuario']} | {evento['resultado']}")
                    else:
                        print_warning("No se encontraron eventos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Generando reporte de auditoría")
                try:
                    fecha_inicio = input("Fecha inicio (YYYY-MM-DD, opcional): ").strip() or None
                    fecha_fin = input("Fecha fin (YYYY-MM-DD, opcional): ").strip() or None
                    
                    reporte = gestor.generar_reporte_auditoria(fecha_inicio, fecha_fin)
                    if reporte:
                        print_success(f"Reporte generado: {reporte}")
                    else:
                        print_error("Error generando reporte")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Limpiando auditoría")
                try:
                    dias = input("Días de retención (opcional): ").strip()
                    dias = int(dias) if dias else None
                    
                    if gestor.limpiar_auditoria(dias):
                        print_success("Auditoría limpiada correctamente")
                    else:
                        print_error("Error limpiando auditoría")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_info("Saliendo del gestor de auditoría...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-7.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de auditoría interrumpida por el usuario")
            print_success("¡Hasta luego! 🌾")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            input("\n⏸️ Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)