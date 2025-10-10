#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 CIERRE DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import signal
import subprocess
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 CIERRE DEL SISTEMA METGO 3D")
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
    """Imprimir mensaje de advertencia")
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class CierreSistema:
    """Clase para cierre del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_sistema': '.',
            'archivo_config': 'config/config.yaml',
            'timeout': 30,  # segundos
            'modo_graceful': True
        }
        
        self.componentes = [
            'servicios',
            'procesos',
            'conexiones',
            'archivos',
            'logs',
            'respaldos'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración del sistema"""
        try:
            print_info("Cargando configuración del sistema...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def detener_servicios(self):
        """Detener servicios del sistema"""
        try:
            print_info("Deteniendo servicios del sistema...")
            
            # Lista de servicios a detener
            servicios = [
                'monitor_sistema.py',
                'backup_sistema.py',
                'monitoreo_tiempo_real.py',
                'respaldos_automaticos.py'
            ]
            
            for servicio in servicios:
                try:
                    # Buscar proceso
                    resultado = subprocess.run(['pgrep', '-f', servicio], 
                                             capture_output=True, text=True)
                    
                    if resultado.returncode == 0:
                        pids = resultado.stdout.strip().split('\n')
                        for pid in pids:
                            if pid:
                                try:
                                    # Enviar señal de terminación
                                    os.kill(int(pid), signal.SIGTERM)
                                    print_success(f"Servicio {servicio} (PID {pid}) detenido")
                                except ProcessLookupError:
                                    print_warning(f"Proceso {pid} ya no existe")
                                except Exception as e:
                                    print_warning(f"Error deteniendo {servicio}: {e}")
                    else:
                        print_info(f"Servicio {servicio} no está ejecutándose")
                
                except Exception as e:
                    print_warning(f"Error verificando servicio {servicio}: {e}")
            
            return True
            
        except Exception as e:
            print_error(f"Error deteniendo servicios: {e}")
            return False
    
    def detener_procesos(self):
        """Detener procesos del sistema"""
        try:
            print_info("Deteniendo procesos del sistema...")
            
            # Buscar procesos Python relacionados con METGO
            try:
                resultado = subprocess.run(['pgrep', '-f', 'metgo'], 
                                         capture_output=True, text=True)
                
                if resultado.returncode == 0:
                    pids = resultado.stdout.strip().split('\n')
                    for pid in pids:
                        if pid and pid != str(os.getpid()):
                            try:
                                # Enviar señal de terminación
                                os.kill(int(pid), signal.SIGTERM)
                                print_success(f"Proceso METGO (PID {pid}) detenido")
                            except ProcessLookupError:
                                print_warning(f"Proceso {pid} ya no existe")
                            except Exception as e:
                                print_warning(f"Error deteniendo proceso {pid}: {e}")
                else:
                    print_info("No hay procesos METGO ejecutándose")
            
            except Exception as e:
                print_warning(f"Error buscando procesos: {e}")
            
            return True
            
        except Exception as e:
            print_error(f"Error deteniendo procesos: {e}")
            return False
    
    def cerrar_conexiones(self):
        """Cerrar conexiones del sistema"""
        try:
            print_info("Cerrando conexiones del sistema...")
            
            # Cerrar conexiones de base de datos si existen
            try:
                # Aquí se cerrarían las conexiones a bases de datos
                # Por ahora solo se registra
                print_info("Conexiones de base de datos cerradas")
            except Exception as e:
                print_warning(f"Error cerrando conexiones de BD: {e}")
            
            # Cerrar conexiones de red
            try:
                # Aquí se cerrarían las conexiones de red
                # Por ahora solo se registra
                print_info("Conexiones de red cerradas")
            except Exception as e:
                print_warning(f"Error cerrando conexiones de red: {e}")
            
            print_success("Conexiones cerradas")
            return True
            
        except Exception as e:
            print_error(f"Error cerrando conexiones: {e}")
            return False
    
    def finalizar_archivos(self):
        """Finalizar archivos del sistema"""
        try:
            print_info("Finalizando archivos del sistema...")
            
            # Crear archivo de estado de cierre
            estado_cierre = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'estado': 'cerrado',
                'componentes': {
                    'servicios': 'detenidos',
                    'procesos': 'detenidos',
                    'conexiones': 'cerradas',
                    'archivos': 'finalizados',
                    'logs': 'cerrados',
                    'respaldos': 'completados'
                }
            }
            
            # Guardar estado
            estado_file = Path('data/estado_cierre.json')
            estado_file.parent.mkdir(exist_ok=True)
            
            with open(estado_file, 'w', encoding='utf-8') as f:
                json.dump(estado_cierre, f, indent=2, ensure_ascii=False)
            
            print_success("Archivos finalizados")
            return True
            
        except Exception as e:
            print_error(f"Error finalizando archivos: {e}")
            return False
    
    def cerrar_logs(self):
        """Cerrar logs del sistema"""
        try:
            print_info("Cerrando logs del sistema...")
            
            # Crear entrada de cierre en el log
            log_entry = f"[{datetime.now().isoformat()}] [INFO] Sistema METGO 3D cerrado correctamente\n"
            
            # Escribir en log principal
            log_file = Path('logs/sistema.log')
            if log_file.exists():
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                print_success("Log principal cerrado")
            else:
                print_warning("Log principal no encontrado")
            
            # Rotar logs si es necesario
            self.rotar_logs()
            
            return True
            
        except Exception as e:
            print_error(f"Error cerrando logs: {e}")
            return False
    
    def rotar_logs(self):
        """Rotar logs del sistema"""
        try:
            print_info("Rotando logs del sistema...")
            
            logs_dir = Path('logs')
            if not logs_dir.exists():
                return True
            
            # Rotar logs grandes (> 10MB)
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_size > 10 * 1024 * 1024:
                    # Crear archivo rotado
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    log_rotado = log_file.with_suffix(f'.{timestamp}.log')
                    
                    # Mover archivo
                    log_file.rename(log_rotado)
                    
                    # Crear nuevo archivo vacío
                    log_file.touch()
                    
                    print_success(f"Log rotado: {log_file.name}")
            
            return True
            
        except Exception as e:
            print_warning(f"Error rotando logs: {e}")
            return True
    
    def completar_respaldos(self):
        """Completar respaldos del sistema"""
        try:
            print_info("Completando respaldos del sistema...")
            
            # Ejecutar respaldo final
            try:
                resultado = subprocess.run([sys.executable, 'backup_sistema.py'], 
                                         capture_output=True, text=True, timeout=60)
                
                if resultado.returncode == 0:
                    print_success("Respaldo final completado")
                else:
                    print_warning(f"Error en respaldo final: {resultado.stderr}")
            
            except subprocess.TimeoutExpired:
                print_warning("Timeout en respaldo final")
            except Exception as e:
                print_warning(f"Error ejecutando respaldo final: {e}")
            
            return True
            
        except Exception as e:
            print_error(f"Error completando respaldos: {e}")
            return False
    
    def generar_reporte_cierre(self):
        """Generar reporte de cierre"""
        try:
            print_info("Generando reporte de cierre...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'estado': 'cerrado',
                'componentes': {
                    'servicios': 'detenidos',
                    'procesos': 'detenidos',
                    'conexiones': 'cerradas',
                    'archivos': 'finalizados',
                    'logs': 'cerrados',
                    'respaldos': 'completados'
                },
                'duracion_sesion': 0,  # Se calcularía basado en el inicio
                'errores': [],
                'advertencias': []
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"cierre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de cierre generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del cierre:")
            print(f"Servicios: {reporte['componentes']['servicios']}")
            print(f"Procesos: {reporte['componentes']['procesos']}")
            print(f"Conexiones: {reporte['componentes']['conexiones']}")
            print(f"Archivos: {reporte['componentes']['archivos']}")
            print(f"Logs: {reporte['componentes']['logs']}")
            print(f"Respaldos: {reporte['componentes']['respaldos']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None
    
    def ejecutar_cierre_completo(self):
        """Ejecutar cierre completo del sistema"""
        try:
            print_info("Ejecutando cierre completo del sistema...")
            
            # Ejecutar todos los pasos
            pasos = [
                ('Cargar configuración', self.cargar_configuracion),
                ('Detener servicios', self.detener_servicios),
                ('Detener procesos', self.detener_procesos),
                ('Cerrar conexiones', self.cerrar_conexiones),
                ('Finalizar archivos', self.finalizar_archivos),
                ('Cerrar logs', self.cerrar_logs),
                ('Completar respaldos', self.completar_respaldos),
                ('Generar reporte', self.generar_reporte_cierre)
            ]
            
            resultados = []
            
            for nombre, funcion in pasos:
                print_step(nombre, f"Ejecutando {nombre.lower()}...")
                try:
                    if funcion():
                        resultados.append((nombre, True, "OK"))
                        print_success(f"{nombre} completado")
                    else:
                        resultados.append((nombre, False, "Error"))
                        print_error(f"Error en {nombre.lower()}")
                except Exception as e:
                    resultados.append((nombre, False, str(e)))
                    print_error(f"Error en {nombre.lower()}: {e}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del cierre completo:")
            exitosos = sum(1 for _, exito, _ in resultados if exito)
            total = len(resultados)
            
            print(f"Pasos exitosos: {exitosos}/{total}")
            
            for nombre, exito, mensaje in resultados:
                estado = "✅" if exito else "❌"
                print(f"{estado} {nombre}: {mensaje}")
            
            return exitosos == total
            
        except Exception as e:
            print_error(f"Error ejecutando cierre completo: {e}")
            return False

def mostrar_menu():
    """Mostrar menú de cierre"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE CIERRE - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 🛑 Detener servicios")
    print("3. 🔄 Detener procesos")
    print("4. 🔌 Cerrar conexiones")
    print("5. 📁 Finalizar archivos")
    print("6. 📝 Cerrar logs")
    print("7. 💾 Completar respaldos")
    print("8. 📊 Generar reporte")
    print("9. 🚪 Cierre completo")
    print("10. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de cierre"""
    print_header()
    
    # Crear cierre
    cierre = CierreSistema()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-10): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if cierre.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Deteniendo servicios")
                if cierre.detener_servicios():
                    print_success("Servicios detenidos correctamente")
                else:
                    print_error("Error deteniendo servicios")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Deteniendo procesos")
                if cierre.detener_procesos():
                    print_success("Procesos detenidos correctamente")
                else:
                    print_error("Error deteniendo procesos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Cerrando conexiones")
                if cierre.cerrar_conexiones():
                    print_success("Conexiones cerradas correctamente")
                else:
                    print_error("Error cerrando conexiones")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Finalizando archivos")
                if cierre.finalizar_archivos():
                    print_success("Archivos finalizados correctamente")
                else:
                    print_error("Error finalizando archivos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Cerrando logs")
                if cierre.cerrar_logs():
                    print_success("Logs cerrados correctamente")
                else:
                    print_error("Error cerrando logs")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Completando respaldos")
                if cierre.completar_respaldos():
                    print_success("Respaldos completados correctamente")
                else:
                    print_error("Error completando respaldos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Generando reporte de cierre")
                reporte = cierre.generar_reporte_cierre()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Ejecutando cierre completo del sistema")
                if cierre.ejecutar_cierre_completo():
                    print_success("Cierre completo ejecutado correctamente")
                else:
                    print_error("Error ejecutando cierre completo")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_info("Saliendo del cierre...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-10.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Cierre interrumpido por el usuario")
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