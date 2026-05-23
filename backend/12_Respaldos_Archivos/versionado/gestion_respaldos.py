#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE RESPALDOS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE RESPALDOS DEL SISTEMA METGO 3D")
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

class GestorRespaldos:
    """Clase para gestión de respaldos del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_respaldos': 'respaldos',
            'archivo_config': 'config/respaldos.yaml',
            'archivo_respaldos': 'respaldos/respaldos.json',
            'max_respaldos': 10,
            'compresion': True,
            'encriptacion': False
        }
        
        self.respaldos = []
        self.tipos_respaldos = [
            'completo',
            'datos',
            'configuracion',
            'logs',
            'reportes',
            'usuarios',
            'auditoria'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de respaldos"""
        try:
            print_info("Cargando configuración de respaldos...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_respaldos(self):
        """Crear estructura de respaldos"""
        try:
            print_info("Creando estructura de respaldos...")
            
            # Crear directorio principal
            respaldos_dir = Path(self.configuracion['directorio_respaldos'])
            respaldos_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['completos', 'datos', 'configuracion', 'logs', 'reportes', 'usuarios', 'auditoria']
            for subdir in subdirs:
                (respaldos_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de respaldos si no existe
            archivo_respaldos = Path(self.configuracion['archivo_respaldos'])
            if not archivo_respaldos.exists():
                with open(archivo_respaldos, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de respaldos creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_respaldo(self, tipo, descripcion=None, incluir_archivos=None):
        """Crear respaldo"""
        try:
            print_info(f"Creando respaldo: {tipo}")
            
            # Verificar que el tipo sea válido
            if tipo not in self.tipos_respaldos:
                print_error(f"Tipo de respaldo no válido: {tipo}")
                return False
            
            # Crear ID de respaldo
            respaldo_id = f"respaldo_{tipo}_{int(time.time())}"
            
            # Crear directorio de respaldo
            respaldo_dir = Path(f"respaldos/{tipo}/{respaldo_id}")
            respaldo_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear respaldo según tipo
            if tipo == 'completo':
                exito = self._crear_respaldo_completo(respaldo_dir)
            elif tipo == 'datos':
                exito = self._crear_respaldo_datos(respaldo_dir)
            elif tipo == 'configuracion':
                exito = self._crear_respaldo_configuracion(respaldo_dir)
            elif tipo == 'logs':
                exito = self._crear_respaldo_logs(respaldo_dir)
            elif tipo == 'reportes':
                exito = self._crear_respaldo_reportes(respaldo_dir)
            elif tipo == 'usuarios':
                exito = self._crear_respaldo_usuarios(respaldo_dir)
            elif tipo == 'auditoria':
                exito = self._crear_respaldo_auditoria(respaldo_dir)
            
            if not exito:
                print_error(f"Error creando respaldo {tipo}")
                return False
            
            # Comprimir respaldo si está habilitado
            if self.configuracion['compresion']:
                archivo_comprimido = self._comprimir_respaldo(respaldo_dir)
                if archivo_comprimido:
                    # Eliminar directorio original
                    shutil.rmtree(respaldo_dir)
                    respaldo_dir = archivo_comprimido
            
            # Crear registro de respaldo
            respaldo = {
                'id': respaldo_id,
                'tipo': tipo,
                'descripcion': descripcion or f"Respaldo {tipo} automático",
                'archivo': str(respaldo_dir),
                'tamaño': self._obtener_tamaño(respaldo_dir),
                'creado': datetime.now().isoformat(),
                'estado': 'completado',
                'incluir_archivos': incluir_archivos or []
            }
            
            # Agregar respaldo
            self.respaldos.append(respaldo)
            
            # Guardar respaldos
            self.guardar_respaldos()
            
            print_success(f"Respaldo {respaldo_id} creado correctamente")
            return respaldo_id
            
        except Exception as e:
            print_error(f"Error creando respaldo: {e}")
            return None
    
    def _crear_respaldo_completo(self, respaldo_dir):
        """Crear respaldo completo del sistema"""
        try:
            print_info("Creando respaldo completo...")
            
            # Directorios a respaldar
            directorios = [
                'data',
                'config',
                'logs',
                'reportes',
                'usuarios',
                'auditoria',
                'seguridad',
                'optimizacion'
            ]
            
            # Archivos a respaldar
            archivos = [
                'requirements.txt',
                'README.md',
                'LICENSE',
                '*.py',
                '*.ipynb'
            ]
            
            # Copiar directorios
            for directorio in directorios:
                if Path(directorio).exists():
                    shutil.copytree(directorio, respaldo_dir / directorio)
                    print_success(f"Directorio {directorio} respaldado")
            
            # Copiar archivos
            for patron in archivos:
                for archivo in Path('.').glob(patron):
                    if archivo.is_file():
                        shutil.copy2(archivo, respaldo_dir)
                        print_success(f"Archivo {archivo.name} respaldado")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo completo: {e}")
            return False
    
    def _crear_respaldo_datos(self, respaldo_dir):
        """Crear respaldo de datos"""
        try:
            print_info("Creando respaldo de datos...")
            
            # Copiar directorio de datos
            if Path('data').exists():
                shutil.copytree('data', respaldo_dir / 'data')
                print_success("Datos respaldados")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de datos: {e}")
            return False
    
    def _crear_respaldo_configuracion(self, respaldo_dir):
        """Crear respaldo de configuración"""
        try:
            print_info("Creando respaldo de configuración...")
            
            # Copiar directorio de configuración
            if Path('config').exists():
                shutil.copytree('config', respaldo_dir / 'config')
                print_success("Configuración respaldada")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de configuración: {e}")
            return False
    
    def _crear_respaldo_logs(self, respaldo_dir):
        """Crear respaldo de logs"""
        try:
            print_info("Creando respaldo de logs...")
            
            # Copiar directorio de logs
            if Path('logs').exists():
                shutil.copytree('logs', respaldo_dir / 'logs')
                print_success("Logs respaldados")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de logs: {e}")
            return False
    
    def _crear_respaldo_reportes(self, respaldo_dir):
        """Crear respaldo de reportes"""
        try:
            print_info("Creando respaldo de reportes...")
            
            # Copiar directorio de reportes
            if Path('reportes').exists():
                shutil.copytree('reportes', respaldo_dir / 'reportes')
                print_success("Reportes respaldados")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de reportes: {e}")
            return False
    
    def _crear_respaldo_usuarios(self, respaldo_dir):
        """Crear respaldo de usuarios"""
        try:
            print_info("Creando respaldo de usuarios...")
            
            # Copiar directorio de usuarios
            if Path('usuarios').exists():
                shutil.copytree('usuarios', respaldo_dir / 'usuarios')
                print_success("Usuarios respaldados")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de usuarios: {e}")
            return False
    
    def _crear_respaldo_auditoria(self, respaldo_dir):
        """Crear respaldo de auditoría"""
        try:
            print_info("Creando respaldo de auditoría...")
            
            # Copiar directorio de auditoría
            if Path('auditoria').exists():
                shutil.copytree('auditoria', respaldo_dir / 'auditoria')
                print_success("Auditoría respaldada")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando respaldo de auditoría: {e}")
            return False
    
    def _comprimir_respaldo(self, respaldo_dir):
        """Comprimir respaldo"""
        try:
            print_info("Comprimiendo respaldo...")
            
            # Crear archivo ZIP
            archivo_zip = respaldo_dir.with_suffix('.zip')
            
            with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for archivo in respaldo_dir.rglob('*'):
                    if archivo.is_file():
                        # Calcular ruta relativa
                        ruta_relativa = archivo.relative_to(respaldo_dir.parent)
                        zipf.write(archivo, ruta_relativa)
            
            print_success(f"Respaldo comprimido: {archivo_zip}")
            return archivo_zip
            
        except Exception as e:
            print_error(f"Error comprimiendo respaldo: {e}")
            return None
    
    def _obtener_tamaño(self, archivo_o_directorio):
        """Obtener tamaño de archivo o directorio"""
        try:
            if Path(archivo_o_directorio).is_file():
                return Path(archivo_o_directorio).stat().st_size
            else:
                total = 0
                for archivo in Path(archivo_o_directorio).rglob('*'):
                    if archivo.is_file():
                        total += archivo.stat().st_size
                return total
        except Exception:
            return 0
    
    def listar_respaldos(self, tipo=None):
        """Listar respaldos"""
        try:
            print_info("Listando respaldos...")
            
            # Filtrar respaldos
            respaldos_filtrados = self.respaldos
            if tipo:
                respaldos_filtrados = [r for r in self.respaldos if r['tipo'] == tipo]
            
            if not respaldos_filtrados:
                print_warning("No hay respaldos para mostrar")
                return []
            
            print(f"\n📋 Respaldos ({len(respaldos_filtrados)}):")
            print("-" * 120)
            print(f"{'ID':<25} {'Tipo':<15} {'Tamaño':<15} {'Creado':<20} {'Estado':<12} {'Archivo':<30}")
            print("-" * 120)
            
            for respaldo in respaldos_filtrados:
                tamaño_mb = respaldo['tamaño'] / 1024 / 1024
                print(f"{respaldo['id']:<25} {respaldo['tipo']:<15} {tamaño_mb:.2f} MB{'':<8} {respaldo['creado'][:19]:<20} {respaldo['estado']:<12} {Path(respaldo['archivo']).name:<30}")
            
            return respaldos_filtrados
            
        except Exception as e:
            print_error(f"Error listando respaldos: {e}")
            return []
    
    def restaurar_respaldo(self, respaldo_id, destino=None):
        """Restaurar respaldo"""
        try:
            print_info(f"Restaurando respaldo: {respaldo_id}")
            
            # Buscar respaldo
            respaldo = next((r for r in self.respaldos if r['id'] == respaldo_id), None)
            if not respaldo:
                print_error(f"Respaldo {respaldo_id} no encontrado")
                return False
            
            # Verificar que el archivo existe
            archivo_respaldo = Path(respaldo['archivo'])
            if not archivo_respaldo.exists():
                print_error(f"Archivo de respaldo no encontrado: {archivo_respaldo}")
                return False
            
            # Determinar destino
            if destino is None:
                destino = Path('.')
            else:
                destino = Path(destino)
            
            # Crear directorio de destino si no existe
            destino.mkdir(parents=True, exist_ok=True)
            
            # Restaurar según tipo de archivo
            if archivo_respaldo.suffix == '.zip':
                # Descomprimir archivo ZIP
                with zipfile.ZipFile(archivo_respaldo, 'r') as zipf:
                    zipf.extractall(destino)
                print_success("Respaldo restaurado desde archivo ZIP")
            else:
                # Copiar directorio
                shutil.copytree(archivo_respaldo, destino / archivo_respaldo.name)
                print_success("Respaldo restaurado desde directorio")
            
            print_success(f"Respaldo {respaldo_id} restaurado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error restaurando respaldo: {e}")
            return False
    
    def eliminar_respaldo(self, respaldo_id):
        """Eliminar respaldo"""
        try:
            print_info(f"Eliminando respaldo: {respaldo_id}")
            
            # Buscar respaldo
            respaldo = next((r for r in self.respaldos if r['id'] == respaldo_id), None)
            if not respaldo:
                print_error(f"Respaldo {respaldo_id} no encontrado")
                return False
            
            # Eliminar archivo o directorio
            archivo_respaldo = Path(respaldo['archivo'])
            if archivo_respaldo.exists():
                if archivo_respaldo.is_file():
                    archivo_respaldo.unlink()
                else:
                    shutil.rmtree(archivo_respaldo)
                print_success(f"Archivo {archivo_respaldo} eliminado")
            
            # Remover de lista
            self.respaldos = [r for r in self.respaldos if r['id'] != respaldo_id]
            
            # Guardar respaldos
            self.guardar_respaldos()
            
            print_success(f"Respaldo {respaldo_id} eliminado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error eliminando respaldo: {e}")
            return False
    
    def limpiar_respaldos_antiguos(self, dias=30):
        """Limpiar respaldos antiguos"""
        try:
            print_info(f"Limpiando respaldos antiguos (más de {dias} días)...")
            
            # Calcular fecha límite
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Filtrar respaldos antiguos
            respaldos_antiguos = [r for r in self.respaldos 
                                if datetime.fromisoformat(r['creado']) < fecha_limite]
            
            if not respaldos_antiguos:
                print_info("No hay respaldos antiguos para eliminar")
                return True
            
            # Eliminar respaldos antiguos
            for respaldo in respaldos_antiguos:
                self.eliminar_respaldo(respaldo['id'])
            
            print_success(f"Respaldos antiguos eliminados: {len(respaldos_antiguos)}")
            return True
            
        except Exception as e:
            print_error(f"Error limpiando respaldos antiguos: {e}")
            return False
    
    def guardar_respaldos(self):
        """Guardar respaldos en archivo"""
        try:
            archivo_respaldos = Path(self.configuracion['archivo_respaldos'])
            with open(archivo_respaldos, 'w', encoding='utf-8') as f:
                json.dump(self.respaldos, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando respaldos: {e}")
            return False
    
    def cargar_respaldos(self):
        """Cargar respaldos desde archivo"""
        try:
            archivo_respaldos = Path(self.configuracion['archivo_respaldos'])
            if archivo_respaldos.exists():
                with open(archivo_respaldos, 'r', encoding='utf-8') as f:
                    self.respaldos = json.load(f)
                
                print_success(f"Respaldos cargados: {len(self.respaldos)}")
                return True
            else:
                print_warning("Archivo de respaldos no encontrado")
                return False
            
        except Exception as e:
            print_error(f"Error cargando respaldos: {e}")
            return False
    
    def generar_reporte_respaldos(self):
        """Generar reporte de respaldos"""
        try:
            print_info("Generando reporte de respaldos...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'respaldos': {
                    'total': len(self.respaldos),
                    'por_tipo': {},
                    'tamaño_total': sum(r['tamaño'] for r in self.respaldos),
                    'mas_reciente': max([r['creado'] for r in self.respaldos]) if self.respaldos else None
                },
                'detalles': self.respaldos
            }
            
            # Contar por tipo
            for tipo in self.tipos_respaldos:
                count = len([r for r in self.respaldos if r['tipo'] == tipo])
                reporte['respaldos']['por_tipo'][tipo] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"respaldos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de respaldos generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de respaldos:")
            print(f"Total: {reporte['respaldos']['total']}")
            print(f"Tamaño total: {reporte['respaldos']['tamaño_total'] / 1024 / 1024:.2f} MB")
            print(f"Más reciente: {reporte['respaldos']['mas_reciente']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de respaldos"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE RESPALDOS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de respaldos")
    print("3. 💾 Crear respaldo")
    print("4. 📋 Listar respaldos")
    print("5. 🔄 Restaurar respaldo")
    print("6. ❌ Eliminar respaldo")
    print("7. 🧹 Limpiar respaldos antiguos")
    print("8. 💾 Cargar respaldos")
    print("9. 📊 Generar reporte")
    print("10. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de respaldos"""
    print_header()
    
    # Crear gestor de respaldos
    gestor = GestorRespaldos()
    
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
                print_step("2", "Creando estructura de respaldos")
                if gestor.crear_estructura_respaldos():
                    print_success("Estructura de respaldos creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Creando respaldo")
                try:
                    tipo = input(f"Tipo de respaldo ({', '.join(gestor.tipos_respaldos)}): ").strip()
                    descripcion = input("Descripción (opcional): ").strip()
                    
                    respaldo_id = gestor.crear_respaldo(tipo, descripcion)
                    if respaldo_id:
                        print_success(f"Respaldo creado: {respaldo_id}")
                    else:
                        print_error("Error creando respaldo")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Listando respaldos")
                try:
                    tipo = input("Tipo (opcional): ").strip() or None
                    respaldos = gestor.listar_respaldos(tipo)
                    if respaldos:
                        print_success(f"Respaldos listados: {len(respaldos)}")
                    else:
                        print_warning("No hay respaldos para mostrar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Restaurando respaldo")
                try:
                    respaldo_id = input("ID del respaldo: ").strip()
                    destino = input("Destino (opcional): ").strip() or None
                    
                    if gestor.restaurar_respaldo(respaldo_id, destino):
                        print_success("Respaldo restaurado correctamente")
                    else:
                        print_error("Error restaurando respaldo")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Eliminando respaldo")
                try:
                    respaldo_id = input("ID del respaldo: ").strip()
                    
                    if gestor.eliminar_respaldo(respaldo_id):
                        print_success("Respaldo eliminado correctamente")
                    else:
                        print_error("Error eliminando respaldo")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Limpiando respaldos antiguos")
                try:
                    dias = int(input("Días (opcional, default 30): ").strip() or "30")
                    
                    if gestor.limpiar_respaldos_antiguos(dias):
                        print_success("Respaldos antiguos limpiados correctamente")
                    else:
                        print_error("Error limpiando respaldos antiguos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Cargando respaldos")
                if gestor.cargar_respaldos():
                    print_success("Respaldos cargados correctamente")
                else:
                    print_error("Error cargando respaldos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Generando reporte de respaldos")
                reporte = gestor.generar_reporte_respaldos()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_info("Saliendo del gestor de respaldos...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-10.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de respaldos interrumpida por el usuario")
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