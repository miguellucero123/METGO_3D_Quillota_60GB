#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE TAREAS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE TAREAS DEL SISTEMA METGO 3D")
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

class GestorTareas:
    """Clase para gestión de tareas del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_tareas': 'tareas',
            'archivo_config': 'config/tareas.yaml',
            'archivo_tareas': 'tareas/tareas.json',
            'max_tareas': 100,
            'timeout': 300  # segundos
        }
        
        self.tareas = []
        self.tareas_ejecutandose = []
        self.tareas_completadas = []
        self.tareas_fallidas = []
        
        self.tipos_tareas = [
            'analisis_meteorologico',
            'generacion_reporte',
            'respaldo_datos',
            'limpieza_sistema',
            'optimizacion',
            'monitoreo',
            'notificacion',
            'actualizacion'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de tareas"""
        try:
            print_info("Cargando configuración de tareas...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_tareas(self):
        """Crear estructura de tareas"""
        try:
            print_info("Creando estructura de tareas...")
            
            # Crear directorio principal
            tareas_dir = Path(self.configuracion['directorio_tareas'])
            tareas_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['pendientes', 'ejecutandose', 'completadas', 'fallidas']
            for subdir in subdirs:
                (tareas_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de tareas si no existe
            archivo_tareas = Path(self.configuracion['archivo_tareas'])
            if not archivo_tareas.exists():
                with open(archivo_tareas, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de tareas creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_tarea(self, tipo, descripcion, parametros=None, prioridad=1):
        """Crear nueva tarea"""
        try:
            print_info(f"Creando tarea: {tipo}")
            
            # Verificar que el tipo sea válido
            if tipo not in self.tipos_tareas:
                print_error(f"Tipo de tarea no válido: {tipo}")
                return False
            
            # Crear tarea
            tarea = {
                'id': f"tarea_{int(time.time())}",
                'tipo': tipo,
                'descripcion': descripcion,
                'parametros': parametros or {},
                'prioridad': prioridad,
                'estado': 'pendiente',
                'creada': datetime.now().isoformat(),
                'iniciada': None,
                'completada': None,
                'resultado': None,
                'error': None
            }
            
            # Agregar tarea
            self.tareas.append(tarea)
            
            # Guardar tareas
            self.guardar_tareas()
            
            print_success(f"Tarea {tarea['id']} creada correctamente")
            return tarea['id']
            
        except Exception as e:
            print_error(f"Error creando tarea: {e}")
            return None
    
    def ejecutar_tarea(self, tarea_id):
        """Ejecutar tarea"""
        try:
            print_info(f"Ejecutando tarea: {tarea_id}")
            
            # Buscar tarea
            tarea = next((t for t in self.tareas if t['id'] == tarea_id), None)
            if not tarea:
                print_error(f"Tarea {tarea_id} no encontrada")
                return False
            
            # Verificar estado
            if tarea['estado'] != 'pendiente':
                print_error(f"Tarea {tarea_id} no está pendiente")
                return False
            
            # Cambiar estado
            tarea['estado'] = 'ejecutandose'
            tarea['iniciada'] = datetime.now().isoformat()
            
            # Agregar a tareas ejecutándose
            self.tareas_ejecutandose.append(tarea)
            
            # Ejecutar tarea en hilo separado
            hilo = threading.Thread(target=self._ejecutar_tarea_hilo, args=(tarea,))
            hilo.daemon = True
            hilo.start()
            
            print_success(f"Tarea {tarea_id} iniciada")
            return True
            
        except Exception as e:
            print_error(f"Error ejecutando tarea: {e}")
            return False
    
    def _ejecutar_tarea_hilo(self, tarea):
        """Ejecutar tarea en hilo separado"""
        try:
            # Ejecutar tarea según tipo
            if tarea['tipo'] == 'analisis_meteorologico':
                resultado = self._ejecutar_analisis_meteorologico(tarea)
            elif tarea['tipo'] == 'generacion_reporte':
                resultado = self._ejecutar_generacion_reporte(tarea)
            elif tarea['tipo'] == 'respaldo_datos':
                resultado = self._ejecutar_respaldo_datos(tarea)
            elif tarea['tipo'] == 'limpieza_sistema':
                resultado = self._ejecutar_limpieza_sistema(tarea)
            elif tarea['tipo'] == 'optimizacion':
                resultado = self._ejecutar_optimizacion(tarea)
            elif tarea['tipo'] == 'monitoreo':
                resultado = self._ejecutar_monitoreo(tarea)
            elif tarea['tipo'] == 'notificacion':
                resultado = self._ejecutar_notificacion(tarea)
            elif tarea['tipo'] == 'actualizacion':
                resultado = self._ejecutar_actualizacion(tarea)
            else:
                resultado = {'exito': False, 'mensaje': 'Tipo de tarea no implementado'}
            
            # Actualizar tarea
            tarea['completada'] = datetime.now().isoformat()
            tarea['resultado'] = resultado
            
            if resultado.get('exito', False):
                tarea['estado'] = 'completada'
                self.tareas_completadas.append(tarea)
                print_success(f"Tarea {tarea['id']} completada")
            else:
                tarea['estado'] = 'fallida'
                tarea['error'] = resultado.get('mensaje', 'Error desconocido')
                self.tareas_fallidas.append(tarea)
                print_error(f"Tarea {tarea['id']} falló: {tarea['error']}")
            
            # Remover de tareas ejecutándose
            self.tareas_ejecutandose = [t for t in self.tareas_ejecutandose if t['id'] != tarea['id']]
            
            # Guardar tareas
            self.guardar_tareas()
            
        except Exception as e:
            print_error(f"Error ejecutando tarea {tarea['id']}: {e}")
            tarea['estado'] = 'fallida'
            tarea['error'] = str(e)
            tarea['completada'] = datetime.now().isoformat()
            self.tareas_fallidas.append(tarea)
            self.guardar_tareas()
    
    def _ejecutar_analisis_meteorologico(self, tarea):
        """Ejecutar análisis meteorológico"""
        try:
            print_info("Ejecutando análisis meteorológico...")
            
            # Simular análisis meteorológico
            time.sleep(2)
            
            return {
                'exito': True,
                'mensaje': 'Análisis meteorológico completado',
                'datos': {
                    'temperatura_promedio': 20.5,
                    'humedad_promedio': 65.2,
                    'precipitacion_total': 15.3
                }
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_generacion_reporte(self, tarea):
        """Ejecutar generación de reporte"""
        try:
            print_info("Generando reporte...")
            
            # Simular generación de reporte
            time.sleep(1)
            
            return {
                'exito': True,
                'mensaje': 'Reporte generado correctamente',
                'archivo': f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_respaldo_datos(self, tarea):
        """Ejecutar respaldo de datos"""
        try:
            print_info("Ejecutando respaldo de datos...")
            
            # Simular respaldo
            time.sleep(3)
            
            return {
                'exito': True,
                'mensaje': 'Respaldo de datos completado',
                'archivo': f"respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_limpieza_sistema(self, tarea):
        """Ejecutar limpieza del sistema"""
        try:
            print_info("Ejecutando limpieza del sistema...")
            
            # Simular limpieza
            time.sleep(1)
            
            return {
                'exito': True,
                'mensaje': 'Limpieza del sistema completada',
                'archivos_eliminados': 15,
                'espacio_liberado': '2.5 MB'
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_optimizacion(self, tarea):
        """Ejecutar optimización"""
        try:
            print_info("Ejecutando optimización...")
            
            # Simular optimización
            time.sleep(2)
            
            return {
                'exito': True,
                'mensaje': 'Optimización completada',
                'mejoras': ['memoria', 'disco', 'procesos']
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_monitoreo(self, tarea):
        """Ejecutar monitoreo"""
        try:
            print_info("Ejecutando monitoreo...")
            
            # Simular monitoreo
            time.sleep(1)
            
            return {
                'exito': True,
                'mensaje': 'Monitoreo completado',
                'metricas': {
                    'cpu': 45.2,
                    'memoria': 67.8,
                    'disco': 23.1
                }
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_notificacion(self, tarea):
        """Ejecutar notificación"""
        try:
            print_info("Ejecutando notificación...")
            
            # Simular notificación
            time.sleep(0.5)
            
            return {
                'exito': True,
                'mensaje': 'Notificación enviada',
                'destinatarios': 3
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def _ejecutar_actualizacion(self, tarea):
        """Ejecutar actualización"""
        try:
            print_info("Ejecutando actualización...")
            
            # Simular actualización
            time.sleep(2)
            
            return {
                'exito': True,
                'mensaje': 'Actualización completada',
                'version': '2.0.1'
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': str(e)}
    
    def listar_tareas(self, estado=None):
        """Listar tareas"""
        try:
            print_info("Listando tareas...")
            
            tareas_filtradas = self.tareas
            if estado:
                tareas_filtradas = [t for t in self.tareas if t['estado'] == estado]
            
            if not tareas_filtradas:
                print_warning("No hay tareas para mostrar")
                return []
            
            print(f"\n📋 Tareas ({len(tareas_filtradas)}):")
            print("-" * 100)
            print(f"{'ID':<15} {'Tipo':<20} {'Estado':<12} {'Prioridad':<8} {'Creada':<20} {'Resultado':<20}")
            print("-" * 100)
            
            for tarea in tareas_filtradas:
                resultado = "OK" if tarea['estado'] == 'completada' else "Pendiente"
                if tarea['estado'] == 'fallida':
                    resultado = "Error"
                
                print(f"{tarea['id']:<15} {tarea['tipo']:<20} {tarea['estado']:<12} {tarea['prioridad']:<8} {tarea['creada'][:19]:<20} {resultado:<20}")
            
            return tareas_filtradas
            
        except Exception as e:
            print_error(f"Error listando tareas: {e}")
            return []
    
    def cancelar_tarea(self, tarea_id):
        """Cancelar tarea"""
        try:
            print_info(f"Cancelando tarea: {tarea_id}")
            
            # Buscar tarea
            tarea = next((t for t in self.tareas if t['id'] == tarea_id), None)
            if not tarea:
                print_error(f"Tarea {tarea_id} no encontrada")
                return False
            
            # Verificar estado
            if tarea['estado'] not in ['pendiente', 'ejecutandose']:
                print_error(f"Tarea {tarea_id} no se puede cancelar")
                return False
            
            # Cambiar estado
            tarea['estado'] = 'cancelada'
            tarea['completada'] = datetime.now().isoformat()
            tarea['resultado'] = {'exito': False, 'mensaje': 'Tarea cancelada por el usuario'}
            
            # Remover de tareas ejecutándose
            self.tareas_ejecutandose = [t for t in self.tareas_ejecutandose if t['id'] != tarea_id]
            
            # Guardar tareas
            self.guardar_tareas()
            
            print_success(f"Tarea {tarea_id} cancelada")
            return True
            
        except Exception as e:
            print_error(f"Error cancelando tarea: {e}")
            return False
    
    def guardar_tareas(self):
        """Guardar tareas en archivo"""
        try:
            archivo_tareas = Path(self.configuracion['archivo_tareas'])
            with open(archivo_tareas, 'w', encoding='utf-8') as f:
                json.dump(self.tareas, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando tareas: {e}")
            return False
    
    def cargar_tareas(self):
        """Cargar tareas desde archivo"""
        try:
            archivo_tareas = Path(self.configuracion['archivo_tareas'])
            if archivo_tareas.exists():
                with open(archivo_tareas, 'r', encoding='utf-8') as f:
                    self.tareas = json.load(f)
                
                # Clasificar tareas
                self.tareas_ejecutandose = [t for t in self.tareas if t['estado'] == 'ejecutandose']
                self.tareas_completadas = [t for t in self.tareas if t['estado'] == 'completada']
                self.tareas_fallidas = [t for t in self.tareas if t['estado'] == 'fallida']
                
                print_success(f"Tareas cargadas: {len(self.tareas)}")
                return True
            else:
                print_warning("Archivo de tareas no encontrado")
                return False
            
        except Exception as e:
            print_error(f"Error cargando tareas: {e}")
            return False
    
    def generar_reporte_tareas(self):
        """Generar reporte de tareas"""
        try:
            print_info("Generando reporte de tareas...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'tareas': {
                    'total': len(self.tareas),
                    'pendientes': len([t for t in self.tareas if t['estado'] == 'pendiente']),
                    'ejecutandose': len(self.tareas_ejecutandose),
                    'completadas': len(self.tareas_completadas),
                    'fallidas': len(self.tareas_fallidas),
                    'canceladas': len([t for t in self.tareas if t['estado'] == 'cancelada'])
                },
                'tipos': {},
                'detalles': self.tareas
            }
            
            # Contar por tipo
            for tipo in self.tipos_tareas:
                count = len([t for t in self.tareas if t['tipo'] == tipo])
                reporte['tareas']['tipos'][tipo] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"tareas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de tareas generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de tareas:")
            print(f"Total: {reporte['tareas']['total']}")
            print(f"Pendientes: {reporte['tareas']['pendientes']}")
            print(f"Ejecutándose: {reporte['tareas']['ejecutandose']}")
            print(f"Completadas: {reporte['tareas']['completadas']}")
            print(f"Fallidas: {reporte['tareas']['fallidas']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de tareas"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE TAREAS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de tareas")
    print("3. 📝 Crear tarea")
    print("4. ▶️ Ejecutar tarea")
    print("5. 📋 Listar tareas")
    print("6. ❌ Cancelar tarea")
    print("7. 💾 Cargar tareas")
    print("8. 📊 Generar reporte")
    print("9. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de tareas"""
    print_header()
    
    # Crear gestor de tareas
    gestor = GestorTareas()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-9): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de tareas")
                if gestor.crear_estructura_tareas():
                    print_success("Estructura de tareas creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Creando tarea")
                try:
                    tipo = input(f"Tipo de tarea ({', '.join(gestor.tipos_tareas)}): ").strip()
                    descripcion = input("Descripción: ").strip()
                    prioridad = int(input("Prioridad (1-5): ").strip() or "1")
                    
                    tarea_id = gestor.crear_tarea(tipo, descripcion, prioridad=prioridad)
                    if tarea_id:
                        print_success(f"Tarea creada: {tarea_id}")
                    else:
                        print_error("Error creando tarea")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Ejecutando tarea")
                try:
                    tarea_id = input("ID de la tarea: ").strip()
                    
                    if gestor.ejecutar_tarea(tarea_id):
                        print_success("Tarea ejecutada correctamente")
                    else:
                        print_error("Error ejecutando tarea")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Listando tareas")
                try:
                    estado = input("Estado (opcional): ").strip() or None
                    tareas = gestor.listar_tareas(estado)
                    if tareas:
                        print_success(f"Tareas listadas: {len(tareas)}")
                    else:
                        print_warning("No hay tareas para mostrar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Cancelando tarea")
                try:
                    tarea_id = input("ID de la tarea: ").strip()
                    
                    if gestor.cancelar_tarea(tarea_id):
                        print_success("Tarea cancelada correctamente")
                    else:
                        print_error("Error cancelando tarea")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Cargando tareas")
                if gestor.cargar_tareas():
                    print_success("Tareas cargadas correctamente")
                else:
                    print_error("Error cargando tareas")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Generando reporte de tareas")
                reporte = gestor.generar_reporte_tareas()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_info("Saliendo del gestor de tareas...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-9.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de tareas interrumpida por el usuario")
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