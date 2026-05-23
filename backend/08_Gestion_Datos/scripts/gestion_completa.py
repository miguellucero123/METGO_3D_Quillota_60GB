#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN COMPLETA DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN COMPLETA DEL SISTEMA METGO 3D")
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

class GestorCompleto:
    """Clase para gestión completa del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_sistema': '.',
            'archivo_config': 'config/sistema.yaml',
            'archivo_estado': 'data/estado_sistema.json',
            'timeout': 300  # segundos
        }
        
        self.modulos = [
            'configuracion',
            'datos',
            'notebooks',
            'servicios',
            'monitoreo',
            'respaldos',
            'alertas',
            'logs',
            'reportes',
            'seguridad',
            'usuarios',
            'auditoria',
            'optimizacion'
        ]
        
        self.estados = {
            'iniciado': False,
            'configurado': False,
            'datos_cargados': False,
            'notebooks_ejecutados': False,
            'servicios_activos': False,
            'monitoreo_activo': False,
            'respaldos_activos': False,
            'alertas_configuradas': False,
            'logs_configurados': False,
            'reportes_configurados': False,
            'seguridad_configurada': False,
            'usuarios_configurados': False,
            'auditoria_configurada': False,
            'optimizacion_activa': False
        }
    
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
    
    def inicializar_sistema(self):
        """Inicializar sistema completo"""
        try:
            print_info("Inicializando sistema completo...")
            
            # Crear directorios necesarios
            directorios = [
                'data', 'logs', 'reportes', 'config', 'usuarios',
                'auditoria', 'seguridad', 'optimizacion', 'respaldos',
                'alertas', 'monitoreo', 'servicios'
            ]
            
            for directorio in directorios:
                Path(directorio).mkdir(exist_ok=True)
                print_success(f"Directorio {directorio} creado")
            
            # Crear archivos de configuración
            self.crear_archivos_configuracion()
            
            # Crear archivo de estado
            self.crear_archivo_estado()
            
            print_success("Sistema inicializado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error inicializando sistema: {e}")
            return False
    
    def crear_archivos_configuracion(self):
        """Crear archivos de configuración"""
        try:
            print_info("Creando archivos de configuración...")
            
            # config/sistema.yaml
            config_sistema = {
                'sistema': {
                    'nombre': 'METGO 3D',
                    'version': '2.0',
                    'descripcion': 'Sistema Meteorológico Agrícola Quillota',
                    'autor': 'Sistema METGO 3D',
                    'fecha_creacion': datetime.now().isoformat()
                },
                'modulos': self.modulos,
                'estados': self.estados,
                'configuracion': {
                    'timeout': 300,
                    'debug': False,
                    'log_level': 'INFO'
                }
            }
            
            config_file = Path('config/sistema.yaml')
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(config_sistema, f, default_flow_style=False)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def crear_archivo_estado(self):
        """Crear archivo de estado del sistema"""
        try:
            print_info("Creando archivo de estado...")
            
            estado = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'estado': 'inicializado',
                'modulos': self.modulos,
                'estados': self.estados,
                'configuracion': self.configuracion
            }
            
            estado_file = Path(self.configuracion['archivo_estado'])
            estado_file.parent.mkdir(exist_ok=True)
            
            with open(estado_file, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)
            
            print_success("Archivo de estado creado")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivo de estado: {e}")
            return False
    
    def ejecutar_modulo(self, modulo, accion='iniciar'):
        """Ejecutar módulo del sistema"""
        try:
            print_info(f"Ejecutando módulo {modulo}: {accion}")
            
            # Mapeo de módulos a scripts
            scripts_modulos = {
                'configuracion': 'gestion_configuracion.py',
                'datos': 'gestion_datos.py',
                'notebooks': 'ejecutar_notebooks_maestro.py',
                'servicios': 'inicio_completo.py',
                'monitoreo': 'gestion_monitoreo.py',
                'respaldos': 'gestion_respaldos.py',
                'alertas': 'gestion_alertas.py',
                'logs': 'gestion_logs.py',
                'reportes': 'gestion_reportes.py',
                'seguridad': 'gestion_seguridad.py',
                'usuarios': 'gestion_usuarios.py',
                'auditoria': 'gestion_auditoria.py',
                'optimizacion': 'optimizar_sistema.py'
            }
            
            script = scripts_modulos.get(modulo)
            if not script:
                print_error(f"Módulo {modulo} no encontrado")
                return False
            
            # Verificar que el script existe
            if not Path(script).exists():
                print_error(f"Script {script} no encontrado")
                return False
            
            # Ejecutar script
            try:
                resultado = subprocess.run([sys.executable, script], 
                                         capture_output=True, text=True, 
                                         timeout=self.configuracion['timeout'])
                
                if resultado.returncode == 0:
                    print_success(f"Módulo {modulo} ejecutado correctamente")
                    return True
                else:
                    print_error(f"Error ejecutando módulo {modulo}: {resultado.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print_error(f"Timeout ejecutando módulo {modulo}")
                return False
            except Exception as e:
                print_error(f"Error ejecutando módulo {modulo}: {e}")
                return False
            
        except Exception as e:
            print_error(f"Error ejecutando módulo: {e}")
            return False
    
    def ejecutar_todos_modulos(self, accion='iniciar'):
        """Ejecutar todos los módulos del sistema"""
        try:
            print_info(f"Ejecutando todos los módulos: {accion}")
            
            resultados = []
            
            for modulo in self.modulos:
                print_step(modulo, f"Ejecutando {modulo}...")
                try:
                    exito = self.ejecutar_modulo(modulo, accion)
                    resultados.append((modulo, exito, "OK" if exito else "Error"))
                    
                    if exito:
                        print_success(f"{modulo} ejecutado correctamente")
                    else:
                        print_error(f"Error ejecutando {modulo}")
                
                except Exception as e:
                    resultados.append((modulo, False, str(e)))
                    print_error(f"Error ejecutando {modulo}: {e}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de ejecución:")
            exitosos = sum(1 for _, exito, _ in resultados if exito)
            total = len(resultados)
            
            print(f"Módulos exitosos: {exitosos}/{total}")
            
            for modulo, exito, mensaje in resultados:
                estado = "✅" if exito else "❌"
                print(f"{estado} {modulo}: {mensaje}")
            
            return exitosos == total
            
        except Exception as e:
            print_error(f"Error ejecutando todos los módulos: {e}")
            return False
    
    def verificar_estado_sistema(self):
        """Verificar estado del sistema"""
        try:
            print_info("Verificando estado del sistema...")
            
            # Verificar archivos críticos
            archivos_criticos = [
                'config/sistema.yaml',
                'data/estado_sistema.json',
                'requirements.txt',
                'README.md'
            ]
            
            archivos_ok = 0
            for archivo in archivos_criticos:
                if Path(archivo).exists():
                    archivos_ok += 1
                    print_success(f"Archivo crítico verificado: {archivo}")
                else:
                    print_warning(f"Archivo crítico no encontrado: {archivo}")
            
            # Verificar directorios
            directorios_criticos = [
                'data', 'logs', 'reportes', 'config'
            ]
            
            directorios_ok = 0
            for directorio in directorios_criticos:
                if Path(directorio).exists():
                    directorios_ok += 1
                    print_success(f"Directorio crítico verificado: {directorio}")
                else:
                    print_warning(f"Directorio crítico no encontrado: {directorio}")
            
            # Verificar scripts
            scripts_criticos = [
                'gestion_configuracion.py',
                'gestion_datos.py',
                'gestion_monitoreo.py',
                'gestion_respaldos.py',
                'gestion_alertas.py',
                'gestion_logs.py',
                'gestion_reportes.py',
                'gestion_seguridad.py',
                'gestion_usuarios.py',
                'gestion_auditoria.py',
                'optimizar_sistema.py',
                'inicio_completo.py',
                'cierre_sistema.py'
            ]
            
            scripts_ok = 0
            for script in scripts_criticos:
                if Path(script).exists():
                    scripts_ok += 1
                    print_success(f"Script crítico verificado: {script}")
                else:
                    print_warning(f"Script crítico no encontrado: {script}")
            
            # Calcular estado general
            total_criticos = len(archivos_criticos) + len(directorios_criticos) + len(scripts_criticos)
            total_ok = archivos_ok + directorios_ok + scripts_ok
            
            estado_general = 'OK' if total_ok == total_criticos else 'ALERTA'
            
            print(f"\n📊 Estado del sistema:")
            print(f"Archivos críticos: {archivos_ok}/{len(archivos_criticos)}")
            print(f"Directorios críticos: {directorios_ok}/{len(directorios_criticos)}")
            print(f"Scripts críticos: {scripts_ok}/{len(scripts_criticos)}")
            print(f"Estado general: {estado_general}")
            
            return estado_general == 'OK'
            
        except Exception as e:
            print_error(f"Error verificando estado del sistema: {e}")
            return False
    
    def generar_reporte_sistema(self):
        """Generar reporte del sistema"""
        try:
            print_info("Generando reporte del sistema...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'configuracion': self.configuracion,
                'modulos': self.modulos,
                'estados': self.estados,
                'archivos_criticos': {
                    'total': 0,
                    'existentes': 0,
                    'faltantes': 0
                },
                'directorios_criticos': {
                    'total': 0,
                    'existentes': 0,
                    'faltantes': 0
                },
                'scripts_criticos': {
                    'total': 0,
                    'existentes': 0,
                    'faltantes': 0
                }
            }
            
            # Verificar archivos críticos
            archivos_criticos = [
                'config/sistema.yaml',
                'data/estado_sistema.json',
                'requirements.txt',
                'README.md'
            ]
            
            reporte['archivos_criticos']['total'] = len(archivos_criticos)
            for archivo in archivos_criticos:
                if Path(archivo).exists():
                    reporte['archivos_criticos']['existentes'] += 1
                else:
                    reporte['archivos_criticos']['faltantes'] += 1
            
            # Verificar directorios críticos
            directorios_criticos = [
                'data', 'logs', 'reportes', 'config'
            ]
            
            reporte['directorios_criticos']['total'] = len(directorios_criticos)
            for directorio in directorios_criticos:
                if Path(directorio).exists():
                    reporte['directorios_criticos']['existentes'] += 1
                else:
                    reporte['directorios_criticos']['faltantes'] += 1
            
            # Verificar scripts críticos
            scripts_criticos = [
                'gestion_configuracion.py',
                'gestion_datos.py',
                'gestion_monitoreo.py',
                'gestion_respaldos.py',
                'gestion_alertas.py',
                'gestion_logs.py',
                'gestion_reportes.py',
                'gestion_seguridad.py',
                'gestion_usuarios.py',
                'gestion_auditoria.py',
                'optimizar_sistema.py',
                'inicio_completo.py',
                'cierre_sistema.py'
            ]
            
            reporte['scripts_criticos']['total'] = len(scripts_criticos)
            for script in scripts_criticos:
                if Path(script).exists():
                    reporte['scripts_criticos']['existentes'] += 1
                else:
                    reporte['scripts_criticos']['faltantes'] += 1
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte del sistema generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen del sistema:")
            print(f"Archivos críticos: {reporte['archivos_criticos']['existentes']}/{reporte['archivos_criticos']['total']}")
            print(f"Directorios críticos: {reporte['directorios_criticos']['existentes']}/{reporte['directorios_criticos']['total']}")
            print(f"Scripts críticos: {reporte['scripts_criticos']['existentes']}/{reporte['scripts_criticos']['total']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None
    
    def limpiar_sistema(self):
        """Limpiar sistema"""
        try:
            print_info("Limpiando sistema...")
            
            # Limpiar archivos temporales
            archivos_temporales = [
                '*.tmp', '*.temp', '*.log', '*.cache'
            ]
            
            archivos_eliminados = 0
            for patron in archivos_temporales:
                for archivo in Path('.').glob(patron):
                    try:
                        archivo.unlink()
                        archivos_eliminados += 1
                        print_success(f"Archivo temporal eliminado: {archivo}")
                    except Exception as e:
                        print_warning(f"Error eliminando {archivo}: {e}")
            
            # Limpiar directorios temporales
            directorios_temporales = [
                'temp', 'tmp', 'cache'
            ]
            
            directorios_eliminados = 0
            for directorio in directorios_temporales:
                dir_path = Path(directorio)
                if dir_path.exists():
                    try:
                        shutil.rmtree(dir_path)
                        directorios_eliminados += 1
                        print_success(f"Directorio temporal eliminado: {directorio}")
                    except Exception as e:
                        print_warning(f"Error eliminando {directorio}: {e}")
            
            print_success(f"Sistema limpiado: {archivos_eliminados} archivos, {directorios_eliminados} directorios")
            return True
            
        except Exception as e:
            print_error(f"Error limpiando sistema: {e}")
            return False
    
    def reiniciar_sistema(self):
        """Reiniciar sistema"""
        try:
            print_info("Reiniciando sistema...")
            
            # Cerrar sistema
            print_info("Cerrando sistema...")
            self.ejecutar_modulo('servicios', 'cerrar')
            
            # Limpiar sistema
            print_info("Limpiando sistema...")
            self.limpiar_sistema()
            
            # Inicializar sistema
            print_info("Inicializando sistema...")
            self.inicializar_sistema()
            
            # Ejecutar todos los módulos
            print_info("Ejecutando todos los módulos...")
            self.ejecutar_todos_modulos('iniciar')
            
            print_success("Sistema reiniciado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error reiniciando sistema: {e}")
            return False

def mostrar_menu():
    """Mostrar menú de gestión completa"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN COMPLETA - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 🚀 Inicializar sistema")
    print("3. ⚙️ Ejecutar módulo")
    print("4. 🔄 Ejecutar todos los módulos")
    print("5. 🔍 Verificar estado del sistema")
    print("6. 📊 Generar reporte del sistema")
    print("7. 🧹 Limpiar sistema")
    print("8. 🔄 Reiniciar sistema")
    print("9. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión completa"""
    print_header()
    
    # Crear gestor completo
    gestor = GestorCompleto()
    
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
                print_step("2", "Inicializando sistema")
                if gestor.inicializar_sistema():
                    print_success("Sistema inicializado correctamente")
                else:
                    print_error("Error inicializando sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Ejecutando módulo")
                try:
                    modulo = input(f"Módulo ({', '.join(gestor.modulos)}): ").strip()
                    accion = input("Acción (iniciar/cerrar, default iniciar): ").strip() or "iniciar"
                    
                    if gestor.ejecutar_modulo(modulo, accion):
                        print_success(f"Módulo {modulo} ejecutado correctamente")
                    else:
                        print_error(f"Error ejecutando módulo {modulo}")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Ejecutando todos los módulos")
                try:
                    accion = input("Acción (iniciar/cerrar, default iniciar): ").strip() or "iniciar"
                    
                    if gestor.ejecutar_todos_modulos(accion):
                        print_success("Todos los módulos ejecutados correctamente")
                    else:
                        print_error("Error ejecutando todos los módulos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Verificando estado del sistema")
                if gestor.verificar_estado_sistema():
                    print_success("Estado del sistema verificado correctamente")
                else:
                    print_warning("Estado del sistema con problemas")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Generando reporte del sistema")
                reporte = gestor.generar_reporte_sistema()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Limpiando sistema")
                if gestor.limpiar_sistema():
                    print_success("Sistema limpiado correctamente")
                else:
                    print_error("Error limpiando sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Reiniciando sistema")
                if gestor.reiniciar_sistema():
                    print_success("Sistema reiniciado correctamente")
                else:
                    print_error("Error reiniciando sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_info("Saliendo del gestor completo...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-9.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión completa interrumpida por el usuario")
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