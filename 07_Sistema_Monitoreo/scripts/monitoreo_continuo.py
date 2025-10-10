#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 MONITOREO CONTINUO DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 MONITOREO CONTINUO DEL SISTEMA METGO 3D")
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

class MonitoreoContinuo:
    """Clase para monitoreo continuo del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_monitoreo': 'monitoreo',
            'archivo_config': 'config/monitoreo.yaml',
            'intervalo': 60,  # segundos
            'umbral_cpu': 80,
            'umbral_memoria': 80,
            'umbral_disco': 90,
            'modo_continuo': True
        }
        
        self.metricas = {
            'sistema': [],
            'aplicacion': [],
            'meteorologia': []
        }
        
        self.alertas = []
        self.running = False
    
    def cargar_configuracion(self):
        """Cargar configuración de monitoreo"""
        try:
            print_info("Cargando configuración de monitoreo...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_monitoreo(self):
        """Crear estructura de monitoreo"""
        try:
            print_info("Creando estructura de monitoreo...")
            
            # Crear directorio principal
            monitoreo_dir = Path(self.configuracion['directorio_monitoreo'])
            monitoreo_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['metricas', 'alertas', 'reportes']
            for subdir in subdirs:
                (monitoreo_dir / subdir).mkdir(exist_ok=True)
            
            print_success("Estructura de monitoreo creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def obtener_metricas_sistema(self):
        """Obtener métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memoria = psutil.virtual_memory()
            
            # Disco
            disco = psutil.disk_usage('/')
            
            # Red
            red = psutil.net_io_counters()
            
            # Procesos
            procesos = len(psutil.pids())
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'porcentaje': cpu_percent,
                    'estado': 'OK' if cpu_percent < self.configuracion['umbral_cpu'] else 'ALERTA'
                },
                'memoria': {
                    'porcentaje': memoria.percent,
                    'total': memoria.total,
                    'disponible': memoria.available,
                    'estado': 'OK' if memoria.percent < self.configuracion['umbral_memoria'] else 'ALERTA'
                },
                'disco': {
                    'porcentaje': disco.percent,
                    'total': disco.total,
                    'disponible': disco.free,
                    'estado': 'OK' if disco.percent < self.configuracion['umbral_disco'] else 'ALERTA'
                },
                'red': {
                    'bytes_enviados': red.bytes_sent,
                    'bytes_recibidos': red.bytes_recv,
                    'paquetes_enviados': red.packets_sent,
                    'paquetes_recibidos': red.packets_recv
                },
                'procesos': {
                    'total': procesos,
                    'estado': 'OK'
                }
            }
            
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas del sistema: {e}")
            return None
    
    def obtener_metricas_aplicacion(self):
        """Obtener métricas de la aplicación"""
        try:
            # Procesos Python
            procesos_python = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        procesos_python.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Logs del sistema
            logs_dir = Path('logs')
            logs_files = list(logs_dir.glob('*.log')) if logs_dir.exists() else []
            
            # Errores recientes
            errores_recientes = 0
            for log_file in logs_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        errores_recientes += sum(1 for line in lines if 'ERROR' in line)
                except Exception:
                    pass
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'procesos': {
                    'python': len(procesos_python),
                    'detalles': procesos_python
                },
                'logs': {
                    'archivos': len(logs_files),
                    'errores_recientes': errores_recientes
                },
                'rendimiento': {
                    'estado': 'OK' if errores_recientes < 10 else 'ALERTA'
                }
            }
            
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas de la aplicación: {e}")
            return None
    
    def obtener_metricas_meteorologia(self):
        """Obtener métricas meteorológicas"""
        try:
            # Verificar archivos de datos
            data_dir = Path('data')
            data_files = list(data_dir.glob('*.json')) if data_dir.exists() else []
            
            # Verificar reportes
            reportes_dir = Path('reportes')
            reportes_files = list(reportes_dir.glob('*.json')) if reportes_dir.exists() else []
            
            # Verificar alertas
            alertas_recientes = 0
            for reporte_file in reportes_files:
                try:
                    with open(reporte_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'alertas' in data:
                            alertas_recientes += len(data['alertas'])
                except Exception:
                    pass
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'datos': {
                    'archivos': len(data_files),
                    'ultima_actualizacion': max([f.stat().st_mtime for f in data_files]) if data_files else 0
                },
                'reportes': {
                    'archivos': len(reportes_files),
                    'alertas_recientes': alertas_recientes
                },
                'calidad': {
                    'estado': 'OK' if alertas_recientes < 5 else 'ALERTA'
                }
            }
            
            return metricas
            
        except Exception as e:
            print_error(f"Error obteniendo métricas meteorológicas: {e}")
            return None
    
    def verificar_alertas(self, metricas):
        """Verificar alertas basadas en métricas"""
        try:
            alertas = []
            
            # Verificar CPU
            if metricas['sistema']['cpu']['estado'] == 'ALERTA':
                alertas.append({
                    'tipo': 'cpu',
                    'mensaje': f"CPU alta: {metricas['sistema']['cpu']['porcentaje']}%",
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ALERTA'
                })
            
            # Verificar memoria
            if metricas['sistema']['memoria']['estado'] == 'ALERTA':
                alertas.append({
                    'tipo': 'memoria',
                    'mensaje': f"Memoria alta: {metricas['sistema']['memoria']['porcentaje']}%",
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ALERTA'
                })
            
            # Verificar disco
            if metricas['sistema']['disco']['estado'] == 'ALERTA':
                alertas.append({
                    'tipo': 'disco',
                    'mensaje': f"Disco lleno: {metricas['sistema']['disco']['porcentaje']}%",
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ALERTA'
                })
            
            # Verificar errores de aplicación
            if metricas['aplicacion']['rendimiento']['estado'] == 'ALERTA':
                alertas.append({
                    'tipo': 'aplicacion',
                    'mensaje': f"Errores recientes: {metricas['aplicacion']['logs']['errores_recientes']}",
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ALERTA'
                })
            
            # Verificar calidad de datos meteorológicos
            if metricas['meteorologia']['calidad']['estado'] == 'ALERTA':
                alertas.append({
                    'tipo': 'meteorologia',
                    'mensaje': f"Alertas meteorológicas: {metricas['meteorologia']['reportes']['alertas_recientes']}",
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ALERTA'
                })
            
            return alertas
            
        except Exception as e:
            print_error(f"Error verificando alertas: {e}")
            return []
    
    def guardar_metricas(self, metricas):
        """Guardar métricas en archivo"""
        try:
            # Crear archivo de métricas
            metricas_file = Path(f"monitoreo/metricas/metricas_{datetime.now().strftime('%Y%m%d')}.json")
            metricas_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar métricas existentes
            if metricas_file.exists():
                with open(metricas_file, 'r', encoding='utf-8') as f:
                    metricas_existentes = json.load(f)
            else:
                metricas_existentes = []
            
            # Agregar nuevas métricas
            metricas_existentes.append(metricas)
            
            # Guardar métricas
            with open(metricas_file, 'w', encoding='utf-8') as f:
                json.dump(metricas_existentes, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando métricas: {e}")
            return False
    
    def guardar_alertas(self, alertas):
        """Guardar alertas en archivo"""
        try:
            if not alertas:
                return True
            
            # Crear archivo de alertas
            alertas_file = Path(f"monitoreo/alertas/alertas_{datetime.now().strftime('%Y%m%d')}.json")
            alertas_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar alertas existentes
            if alertas_file.exists():
                with open(alertas_file, 'r', encoding='utf-8') as f:
                    alertas_existentes = json.load(f)
            else:
                alertas_existentes = []
            
            # Agregar nuevas alertas
            alertas_existentes.extend(alertas)
            
            # Guardar alertas
            with open(alertas_file, 'w', encoding='utf-8') as f:
                json.dump(alertas_existentes, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando alertas: {e}")
            return False
    
    def ciclo_monitoreo(self):
        """Ciclo principal de monitoreo"""
        try:
            while self.running:
                # Obtener métricas
                metricas_sistema = self.obtener_metricas_sistema()
                metricas_aplicacion = self.obtener_metricas_aplicacion()
                metricas_meteorologia = self.obtener_metricas_meteorologia()
                
                if metricas_sistema and metricas_aplicacion and metricas_meteorologia:
                    # Combinar métricas
                    metricas = {
                        'timestamp': datetime.now().isoformat(),
                        'sistema': metricas_sistema,
                        'aplicacion': metricas_aplicacion,
                        'meteorologia': metricas_meteorologia
                    }
                    
                    # Verificar alertas
                    alertas = self.verificar_alertas(metricas)
                    
                    # Guardar métricas y alertas
                    self.guardar_metricas(metricas)
                    self.guardar_alertas(alertas)
                    
                    # Mostrar resumen
                    print(f"\n📊 Monitoreo - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"CPU: {metricas_sistema['cpu']['porcentaje']}% ({metricas_sistema['cpu']['estado']})")
                    print(f"Memoria: {metricas_sistema['memoria']['porcentaje']}% ({metricas_sistema['memoria']['estado']})")
                    print(f"Disco: {metricas_sistema['disco']['porcentaje']}% ({metricas_sistema['disco']['estado']})")
                    print(f"Alertas: {len(alertas)}")
                
                # Esperar intervalo
                time.sleep(self.configuracion['intervalo'])
            
        except Exception as e:
            print_error(f"Error en ciclo de monitoreo: {e}")
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo"""
        try:
            print_info("Iniciando monitoreo continuo...")
            
            # Crear estructura
            self.crear_estructura_monitoreo()
            
            # Iniciar hilo de monitoreo
            self.running = True
            hilo_monitoreo = threading.Thread(target=self.ciclo_monitoreo)
            hilo_monitoreo.daemon = True
            hilo_monitoreo.start()
            
            print_success("Monitoreo continuo iniciado")
            return True
            
        except Exception as e:
            print_error(f"Error iniciando monitoreo: {e}")
            return False
    
    def detener_monitoreo(self):
        """Detener monitoreo continuo"""
        try:
            print_info("Deteniendo monitoreo continuo...")
            
            self.running = False
            
            print_success("Monitoreo continuo detenido")
            return True
            
        except Exception as e:
            print_error(f"Error deteniendo monitoreo: {e}")
            return False
    
    def generar_reporte_monitoreo(self):
        """Generar reporte de monitoreo"""
        try:
            print_info("Generando reporte de monitoreo...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'estado': 'monitoreando' if self.running else 'detenido',
                'configuracion': self.configuracion,
                'metricas': {
                    'sistema': self.metricas['sistema'],
                    'aplicacion': self.metricas['aplicacion'],
                    'meteorologia': self.metricas['meteorologia']
                },
                'alertas': self.alertas
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"monitoreo_continuo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de monitoreo generado: {reporte_file}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de monitoreo continuo"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE MONITOREO CONTINUO - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de monitoreo")
    print("3. 🚀 Iniciar monitoreo")
    print("4. 🛑 Detener monitoreo")
    print("5. 📊 Generar reporte")
    print("6. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de monitoreo continuo"""
    print_header()
    
    # Crear monitoreo
    monitoreo = MonitoreoContinuo()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if monitoreo.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de monitoreo")
                if monitoreo.crear_estructura_monitoreo():
                    print_success("Estructura de monitoreo creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Iniciando monitoreo continuo")
                if monitoreo.iniciar_monitoreo():
                    print_success("Monitoreo continuo iniciado correctamente")
                    print_info("Presiona Ctrl+C para detener el monitoreo")
                    try:
                        while monitoreo.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        monitoreo.detener_monitoreo()
                else:
                    print_error("Error iniciando monitoreo continuo")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Deteniendo monitoreo continuo")
                if monitoreo.detener_monitoreo():
                    print_success("Monitoreo continuo detenido correctamente")
                else:
                    print_error("Error deteniendo monitoreo continuo")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Generando reporte de monitoreo")
                reporte = monitoreo.generar_reporte_monitoreo()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_info("Saliendo del monitoreo continuo...")
                if monitoreo.running:
                    monitoreo.detener_monitoreo()
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-6.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Monitoreo continuo interrumpido por el usuario")
            if monitoreo.running:
                monitoreo.detener_monitoreo()
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