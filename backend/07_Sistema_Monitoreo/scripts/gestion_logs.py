#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE LOGS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE LOGS DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito")
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

class GestorLogs:
    """Clase para gestión de logs del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_logs': 'logs',
            'archivo_config': 'config/logs.yaml',
            'archivo_logs': 'logs/logs.json',
            'max_tamaño_mb': 10,
            'max_archivos': 5,
            'compresion': True,
            'retencion_dias': 30
        }
        
        self.tipos_logs = [
            'sistema',
            'aplicacion',
            'meteorologico',
            'seguridad',
            'auditoria',
            'errores',
            'debug'
        ]
        
        self.niveles_logs = [
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de logs"""
        try:
            print_info("Cargando configuración de logs...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_logs(self):
        """Crear estructura de logs"""
        try:
            print_info("Creando estructura de logs...")
            
            # Crear directorio principal
            logs_dir = Path(self.configuracion['directorio_logs'])
            logs_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['sistema', 'aplicacion', 'meteorologico', 'seguridad', 'auditoria', 'errores', 'debug']
            for subdir in subdirs:
                (logs_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de logs si no existe
            archivo_logs = Path(self.configuracion['archivo_logs'])
            if not archivo_logs.exists():
                with open(archivo_logs, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de logs creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def escribir_log(self, tipo, nivel, mensaje, detalles=None, usuario=None):
        """Escribir entrada de log"""
        try:
            # Verificar que el tipo y nivel sean válidos
            if tipo not in self.tipos_logs:
                print_error(f"Tipo de log no válido: {tipo}")
                return False
            
            if nivel not in self.niveles_logs:
                print_error(f"Nivel de log no válido: {nivel}")
                return False
            
            # Crear entrada de log
            entrada = {
                'timestamp': datetime.now().isoformat(),
                'tipo': tipo,
                'nivel': nivel,
                'mensaje': mensaje,
                'detalles': detalles or {},
                'usuario': usuario or 'sistema',
                'proceso': os.getpid(),
                'thread': threading.get_ident() if 'threading' in sys.modules else None
            }
            
            # Escribir en archivo de log específico
            archivo_log = Path(f"logs/{tipo}/{tipo}_{datetime.now().strftime('%Y%m%d')}.log")
            archivo_log.parent.mkdir(parents=True, exist_ok=True)
            
            with open(archivo_log, 'a', encoding='utf-8') as f:
                f.write(f"[{entrada['timestamp']}] [{entrada['nivel']}] {entrada['mensaje']}\n")
                if detalles:
                    f.write(f"Detalles: {json.dumps(detalles, indent=2)}\n")
                f.write("-" * 80 + "\n")
            
            # Verificar si necesita rotación
            if archivo_log.stat().st_size > self.configuracion['max_tamaño_mb'] * 1024 * 1024:
                self.rotar_log(archivo_log)
            
            print_success(f"Log {tipo} escrito: {mensaje}")
            return True
            
        except Exception as e:
            print_error(f"Error escribiendo log: {e}")
            return False
    
    def rotar_log(self, archivo_log):
        """Rotar archivo de log"""
        try:
            print_info(f"Rotando log: {archivo_log}")
            
            # Crear archivo rotado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_rotado = archivo_log.with_suffix(f'.{timestamp}.log')
            
            # Mover archivo
            shutil.move(str(archivo_log), str(archivo_rotado))
            
            # Comprimir si está habilitado
            if self.configuracion['compresion']:
                archivo_comprimido = archivo_rotado.with_suffix('.log.gz')
                with open(archivo_rotado, 'rb') as f_in:
                    with gzip.open(archivo_comprimido, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Eliminar archivo sin comprimir
                archivo_rotado.unlink()
                archivo_rotado = archivo_comprimido
            
            # Crear nuevo archivo vacío
            archivo_log.touch()
            
            # Limpiar logs antiguos
            self.limpiar_logs_antiguos(archivo_log.parent)
            
            print_success(f"Log rotado: {archivo_rotado}")
            return True
            
        except Exception as e:
            print_error(f"Error rotando log: {e}")
            return False
    
    def limpiar_logs_antiguos(self, directorio_logs):
        """Limpiar logs antiguos"""
        try:
            print_info("Limpiando logs antiguos...")
            
            # Obtener archivos de log
            archivos_log = list(directorio_logs.glob('*.log*'))
            
            # Ordenar por fecha de modificación
            archivos_log.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Mantener solo los archivos más recientes
            archivos_a_eliminar = archivos_log[self.configuracion['max_archivos']:]
            
            for archivo in archivos_a_eliminar:
                archivo.unlink()
                print_success(f"Log antiguo eliminado: {archivo.name}")
            
            return True
            
        except Exception as e:
            print_error(f"Error limpiando logs antiguos: {e}")
            return False
    
    def buscar_logs(self, tipo=None, nivel=None, usuario=None, fecha_inicio=None, fecha_fin=None, patron=None):
        """Buscar logs"""
        try:
            print_info("Buscando logs...")
            
            # Determinar directorio de búsqueda
            if tipo:
                directorio_busqueda = Path(f"logs/{tipo}")
            else:
                directorio_busqueda = Path("logs")
            
            if not directorio_busqueda.exists():
                print_warning("Directorio de logs no encontrado")
                return []
            
            # Obtener archivos de log
            archivos_log = list(directorio_busqueda.rglob('*.log'))
            
            # Filtrar por fecha si se especifica
            if fecha_inicio or fecha_fin:
                archivos_filtrados = []
                for archivo in archivos_log:
                    fecha_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime)
                    
                    if fecha_inicio and fecha_modificacion < datetime.fromisoformat(fecha_inicio):
                        continue
                    
                    if fecha_fin and fecha_modificacion > datetime.fromisoformat(fecha_fin):
                        continue
                    
                    archivos_filtrados.append(archivo)
                
                archivos_log = archivos_filtrados
            
            # Buscar en archivos
            resultados = []
            for archivo in archivos_log:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        lineas = f.readlines()
                    
                    for i, linea in enumerate(lineas):
                        # Verificar nivel
                        if nivel and f"[{nivel}]" not in linea:
                            continue
                        
                        # Verificar usuario
                        if usuario and usuario not in linea:
                            continue
                        
                        # Verificar patrón
                        if patron and patron.lower() not in linea.lower():
                            continue
                        
                        # Agregar resultado
                        resultados.append({
                            'archivo': str(archivo),
                            'linea': i + 1,
                            'contenido': linea.strip(),
                            'timestamp': self._extraer_timestamp(linea)
                        })
                
                except Exception as e:
                    print_warning(f"Error leyendo {archivo}: {e}")
            
            print_success(f"Logs encontrados: {len(resultados)}")
            return resultados
            
        except Exception as e:
            print_error(f"Error buscando logs: {e}")
            return []
    
    def _extraer_timestamp(self, linea):
        """Extraer timestamp de línea de log"""
        try:
            # Buscar patrón [YYYY-MM-DDTHH:MM:SS]
            import re
            patron = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\]'
            match = re.search(patron, linea)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
    
    def analizar_logs(self, tipo=None, fecha_inicio=None, fecha_fin=None):
        """Analizar logs"""
        try:
            print_info("Analizando logs...")
            
            # Buscar logs
            logs = self.buscar_logs(tipo=tipo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
            
            if not logs:
                print_warning("No hay logs para analizar")
                return {}
            
            # Análisis básico
            analisis = {
                'total_entradas': len(logs),
                'por_nivel': {},
                'por_tipo': {},
                'por_usuario': {},
                'errores': [],
                'advertencias': [],
                'patrones': {}
            }
            
            # Contar por nivel
            for log in logs:
                nivel = self._extraer_nivel(log['contenido'])
                if nivel:
                    analisis['por_nivel'][nivel] = analisis['por_nivel'].get(nivel, 0) + 1
                
                # Contar por tipo
                tipo = Path(log['archivo']).parent.name
                analisis['por_tipo'][tipo] = analisis['por_tipo'].get(tipo, 0) + 1
                
                # Extraer errores y advertencias
                if nivel in ['ERROR', 'CRITICAL']:
                    analisis['errores'].append(log)
                elif nivel == 'WARNING':
                    analisis['advertencias'].append(log)
            
            print_success(f"Análisis completado: {analisis['total_entradas']} entradas")
            return analisis
            
        except Exception as e:
            print_error(f"Error analizando logs: {e}")
            return {}
    
    def _extraer_nivel(self, linea):
        """Extraer nivel de log de línea"""
        try:
            import re
            patron = r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]'
            match = re.search(patron, linea)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
    
    def exportar_logs(self, tipo=None, formato='json', archivo_salida=None):
        """Exportar logs"""
        try:
            print_info("Exportando logs...")
            
            # Buscar logs
            logs = self.buscar_logs(tipo=tipo)
            
            if not logs:
                print_warning("No hay logs para exportar")
                return None
            
            # Determinar archivo de salida
            if archivo_salida is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archivo_salida = f"logs_exportados_{timestamp}.{formato}"
            
            archivo_salida = Path(archivo_salida)
            
            # Exportar según formato
            if formato == 'json':
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            
            elif formato == 'csv':
                import csv
                with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['archivo', 'linea', 'timestamp', 'contenido'])
                    for log in logs:
                        writer.writerow([log['archivo'], log['linea'], log['timestamp'], log['contenido']])
            
            elif formato == 'txt':
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    for log in logs:
                        f.write(f"{log['archivo']}:{log['linea']} - {log['contenido']}\n")
            
            else:
                print_error(f"Formato no soportado: {formato}")
                return None
            
            print_success(f"Logs exportados: {archivo_salida}")
            return str(archivo_salida)
            
        except Exception as e:
            print_error(f"Error exportando logs: {e}")
            return None
    
    def generar_reporte_logs(self):
        """Generar reporte de logs"""
        try:
            print_info("Generando reporte de logs...")
            
            # Analizar logs
            analisis = self.analizar_logs()
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'analisis': analisis,
                'configuracion': self.configuracion,
                'estadisticas': {
                    'archivos_log': len(list(Path('logs').rglob('*.log'))),
                    'tamaño_total': sum(f.stat().st_size for f in Path('logs').rglob('*.log')),
                    'logs_antiguos': len(list(Path('logs').rglob('*.log.gz')))
                }
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de logs generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de logs:")
            print(f"Total de entradas: {analisis['total_entradas']}")
            print(f"Archivos de log: {reporte['estadisticas']['archivos_log']}")
            print(f"Tamaño total: {reporte['estadisticas']['tamaño_total'] / 1024 / 1024:.2f} MB")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de logs"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE LOGS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de logs")
    print("3. 📝 Escribir log")
    print("4. 🔍 Buscar logs")
    print("5. 📊 Analizar logs")
    print("6. 📤 Exportar logs")
    print("7. 🔄 Rotar logs")
    print("8. 🧹 Limpiar logs antiguos")
    print("9. 📊 Generar reporte")
    print("10. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de logs"""
    print_header()
    
    # Crear gestor de logs
    gestor = GestorLogs()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-10): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de logs")
                if gestor.crear_estructura_logs():
                    print_success("Estructura de logs creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Escribiendo log")
                try:
                    tipo = input(f"Tipo de log ({', '.join(gestor.tipos_logs)}): ").strip()
                    nivel = input(f"Nivel de log ({', '.join(gestor.niveles_logs)}): ").strip()
                    mensaje = input("Mensaje: ").strip()
                    detalles = input("Detalles (JSON opcional): ").strip()
                    usuario = input("Usuario (opcional): ").strip()
                    
                    if detalles:
                        try:
                            detalles = json.loads(detalles)
                        except json.JSONDecodeError:
                            print_warning("Detalles no válidos, ignorando")
                            detalles = None
                    
                    if gestor.escribir_log(tipo, nivel, mensaje, detalles, usuario):
                        print_success("Log escrito correctamente")
                    else:
                        print_error("Error escribiendo log")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Buscando logs")
                try:
                    tipo = input("Tipo (opcional): ").strip() or None
                    nivel = input("Nivel (opcional): ").strip() or None
                    usuario = input("Usuario (opcional): ").strip() or None
                    fecha_inicio = input("Fecha inicio (YYYY-MM-DD, opcional): ").strip() or None
                    fecha_fin = input("Fecha fin (YYYY-MM-DD, opcional): ").strip() or None
                    patron = input("Patrón de búsqueda (opcional): ").strip() or None
                    
                    logs = gestor.buscar_logs(tipo, nivel, usuario, fecha_inicio, fecha_fin, patron)
                    if logs:
                        print_success(f"Logs encontrados: {len(logs)}")
                        for log in logs[:5]:  # Mostrar solo los primeros 5
                            print(f"- {log['archivo']}:{log['linea']} - {log['contenido']}")
                    else:
                        print_warning("No se encontraron logs")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Analizando logs")
                try:
                    tipo = input("Tipo (opcional): ").strip() or None
                    fecha_inicio = input("Fecha inicio (YYYY-MM-DD, opcional): ").strip() or None
                    fecha_fin = input("Fecha fin (YYYY-MM-DD, opcional): ").strip() or None
                    
                    analisis = gestor.analizar_logs(tipo, fecha_inicio, fecha_fin)
                    if analisis:
                        print_success("Análisis de logs completado")
                        print(f"Total de entradas: {analisis['total_entradas']}")
                        print(f"Por nivel: {analisis['por_nivel']}")
                        print(f"Por tipo: {analisis['por_tipo']}")
                    else:
                        print_warning("No se pudo analizar los logs")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Exportando logs")
                try:
                    tipo = input("Tipo (opcional): ").strip() or None
                    formato = input("Formato (json/csv/txt, default json): ").strip() or "json"
                    archivo_salida = input("Archivo de salida (opcional): ").strip() or None
                    
                    archivo = gestor.exportar_logs(tipo, formato, archivo_salida)
                    if archivo:
                        print_success(f"Logs exportados: {archivo}")
                    else:
                        print_error("Error exportando logs")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Rotando logs")
                try:
                    archivo_log = input("Archivo de log: ").strip()
                    
                    if gestor.rotar_log(Path(archivo_log)):
                        print_success("Log rotado correctamente")
                    else:
                        print_error("Error rotando log")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Limpiando logs antiguos")
                try:
                    directorio = input("Directorio (opcional): ").strip() or "logs"
                    
                    if gestor.limpiar_logs_antiguos(Path(directorio)):
                        print_success("Logs antiguos limpiados correctamente")
                    else:
                        print_error("Error limpiando logs antiguos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Generando reporte de logs")
                reporte = gestor.generar_reporte_logs()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_info("Saliendo del gestor de logs...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-10.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de logs interrumpida por el usuario")
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