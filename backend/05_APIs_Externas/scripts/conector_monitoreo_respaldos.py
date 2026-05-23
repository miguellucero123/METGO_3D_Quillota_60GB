#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONECTOR MONITOREO Y RESPALDOS - METGO 3D
Sistema de monitoreo avanzado y respaldos automaticos
"""

import os
import json
import time
import sqlite3
import threading
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
import psutil
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
import zipfile
import hashlib

class ConectorMonitoreo:
    """Conector para monitoreo del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('MONITOR_CONNECTOR')
        self.db_path = 'data/monitoreo.db'
        self.monitoreo_activo = False
        self.umbrales = {
            'cpu_max': 80.0,
            'memoria_max': 85.0,
            'disco_max': 90.0,
            'temperatura_max': 70.0,
            'latencia_max': 1000.0
        }
        
        # Inicializar base de datos
        self._inicializar_db()
    
    def _inicializar_db(self):
        """Inicializar base de datos de monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de metricas del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metricas_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memoria_percent REAL,
                    disco_percent REAL,
                    temperatura REAL,
                    latencia_ms REAL,
                    procesos_activos INTEGER,
                    memoria_disponible_mb REAL
                )
            ''')
            
            # Tabla de alertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo TEXT,
                    severidad TEXT,
                    mensaje TEXT,
                    valor_actual REAL,
                    umbral REAL,
                    resuelta BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla de servicios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    estado TEXT,
                    ultima_verificacion DATETIME,
                    puerto INTEGER,
                    url TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error inicializando DB de monitoreo: {e}")
    
    def obtener_metricas_sistema(self) -> Dict[str, Any]:
        """Obtener metricas actuales del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memoria
            memoria = psutil.virtual_memory()
            memoria_percent = memoria.percent
            memoria_disponible = memoria.available / (1024**3)  # GB
            
            # Disco
            disco = psutil.disk_usage('/')
            disco_percent = disco.percent
            
            # Temperatura (si esta disponible)
            try:
                temperatura = psutil.sensors_temperatures()
                temp_cpu = 0
                if 'coretemp' in temperatura:
                    temp_cpu = temperatura['coretemp'][0].current
                elif 'cpu_thermal' in temperatura:
                    temp_cpu = temperatura['cpu_thermal'][0].current
            except:
                temp_cpu = 0
            
            # Procesos
            procesos = len(psutil.pids())
            
            # Latencia (simulada)
            latencia = time.time() * 1000 % 1000  # Simulacion
            
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memoria_percent': memoria_percent,
                'disco_percent': disco_percent,
                'temperatura': temp_cpu,
                'latencia_ms': latencia,
                'procesos_activos': procesos,
                'memoria_disponible_gb': round(memoria_disponible, 2)
            }
            
            # Guardar en base de datos
            self._guardar_metricas(metricas)
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo metricas: {e}")
            return {}
    
    def _guardar_metricas(self, metricas: Dict[str, Any]):
        """Guardar metricas en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO metricas_sistema 
                (cpu_percent, memoria_percent, disco_percent, temperatura, 
                 latencia_ms, procesos_activos, memoria_disponible_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metricas['cpu_percent'],
                metricas['memoria_percent'],
                metricas['disco_percent'],
                metricas['temperatura'],
                metricas['latencia_ms'],
                metricas['procesos_activos'],
                metricas['memoria_disponible_gb'] * 1024
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando metricas: {e}")
    
    def verificar_alertas(self, metricas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verificar si hay alertas basadas en las metricas"""
        alertas = []
        
        try:
            # CPU
            if metricas['cpu_percent'] > self.umbrales['cpu_max']:
                alertas.append({
                    'tipo': 'CPU',
                    'severidad': 'ALTA' if metricas['cpu_percent'] > 95 else 'MEDIA',
                    'mensaje': f"Uso de CPU alto: {metricas['cpu_percent']:.1f}%",
                    'valor_actual': metricas['cpu_percent'],
                    'umbral': self.umbrales['cpu_max']
                })
            
            # Memoria
            if metricas['memoria_percent'] > self.umbrales['memoria_max']:
                alertas.append({
                    'tipo': 'MEMORIA',
                    'severidad': 'ALTA' if metricas['memoria_percent'] > 95 else 'MEDIA',
                    'mensaje': f"Uso de memoria alto: {metricas['memoria_percent']:.1f}%",
                    'valor_actual': metricas['memoria_percent'],
                    'umbral': self.umbrales['memoria_max']
                })
            
            # Disco
            if metricas['disco_percent'] > self.umbrales['disco_max']:
                alertas.append({
                    'tipo': 'DISCO',
                    'severidad': 'ALTA' if metricas['disco_percent'] > 95 else 'MEDIA',
                    'mensaje': f"Uso de disco alto: {metricas['disco_percent']:.1f}%",
                    'valor_actual': metricas['disco_percent'],
                    'umbral': self.umbrales['disco_max']
                })
            
            # Temperatura
            if metricas['temperatura'] > self.umbrales['temperatura_max']:
                alertas.append({
                    'tipo': 'TEMPERATURA',
                    'severidad': 'CRITICA',
                    'mensaje': f"Temperatura alta: {metricas['temperatura']:.1f}°C",
                    'valor_actual': metricas['temperatura'],
                    'umbral': self.umbrales['temperatura_max']
                })
            
            # Guardar alertas en base de datos
            for alerta in alertas:
                self._guardar_alerta(alerta)
            
            return alertas
            
        except Exception as e:
            self.logger.error(f"Error verificando alertas: {e}")
            return []
    
    def _guardar_alerta(self, alerta: Dict[str, Any]):
        """Guardar alerta en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alertas (tipo, severidad, mensaje, valor_actual, umbral)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alerta['tipo'],
                alerta['severidad'],
                alerta['mensaje'],
                alerta['valor_actual'],
                alerta['umbral']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error guardando alerta: {e}")
    
    def iniciar_monitoreo_continuo(self, intervalo=60):
        """Iniciar monitoreo continuo del sistema"""
        try:
            self.monitoreo_activo = True
            self.logger.info(f"Iniciando monitoreo continuo cada {intervalo} segundos")
            
            def monitorear():
                while self.monitoreo_activo:
                    metricas = self.obtener_metricas_sistema()
                    alertas = self.verificar_alertas(metricas)
                    
                    if alertas:
                        self.logger.warning(f"Alertas detectadas: {len(alertas)}")
                        for alerta in alertas:
                            self.logger.warning(f"ALERTA {alerta['severidad']}: {alerta['mensaje']}")
                    
                    time.sleep(intervalo)
            
            thread = threading.Thread(target=monitorear)
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
            return False
    
    def detener_monitoreo(self):
        """Detener monitoreo continuo"""
        self.monitoreo_activo = False
        self.logger.info("Monitoreo detenido")
    
    def obtener_estadisticas_monitoreo(self) -> Dict[str, Any]:
        """Obtener estadisticas de monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estadisticas de metricas
            cursor.execute('''
                SELECT 
                    AVG(cpu_percent) as cpu_promedio,
                    MAX(cpu_percent) as cpu_maximo,
                    AVG(memoria_percent) as memoria_promedio,
                    MAX(memoria_percent) as memoria_maximo,
                    COUNT(*) as total_registros
                FROM metricas_sistema 
                WHERE timestamp >= datetime('now', '-24 hours')
            ''')
            
            stats_metricas = cursor.fetchone()
            
            # Estadisticas de alertas
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_alertas,
                    COUNT(CASE WHEN severidad = 'CRITICA' THEN 1 END) as alertas_criticas,
                    COUNT(CASE WHEN severidad = 'ALTA' THEN 1 END) as alertas_altas,
                    COUNT(CASE WHEN resuelta = 0 THEN 1 END) as alertas_activas
                FROM alertas 
                WHERE timestamp >= datetime('now', '-24 hours')
            ''')
            
            stats_alertas = cursor.fetchone()
            
            conn.close()
            
            return {
                'metricas': {
                    'cpu_promedio': round(stats_metricas[0] or 0, 2),
                    'cpu_maximo': round(stats_metricas[1] or 0, 2),
                    'memoria_promedio': round(stats_metricas[2] or 0, 2),
                    'memoria_maximo': round(stats_metricas[3] or 0, 2),
                    'total_registros': stats_metricas[4] or 0
                },
                'alertas': {
                    'total': stats_alertas[0] or 0,
                    'criticas': stats_alertas[1] or 0,
                    'altas': stats_alertas[2] or 0,
                    'activas': stats_alertas[3] or 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadisticas: {e}")
            return {}

class ConectorRespaldos:
    """Conector para respaldos automaticos del sistema METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('BACKUP_CONNECTOR')
        self.directorio_respaldos = Path('data/respaldos')
        self.directorio_respaldos.mkdir(parents=True, exist_ok=True)
        
        # Configuracion de respaldos
        self.config_respaldos = {
            'tipos': ['completo', 'incremental', 'diferencial'],
            'compresion': True,
            'encriptacion': False,
            'retencion_dias': 30,
            'horarios': ['02:00', '14:00']  # 2 AM y 2 PM
        }
    
    def crear_respaldo_completo(self) -> Dict[str, Any]:
        """Crear respaldo completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_respaldo = f"respaldo_completo_{timestamp}"
            ruta_respaldo = self.directorio_respaldos / f"{nombre_respaldo}.zip"
            
            # Directorios a respaldar
            directorios_respaldo = [
                'data',
                'config',
                'docs',
                'tests',
                'notebooks',
                'src'
            ]
            
            # Archivos a respaldar
            archivos_respaldo = [
                '*.py',
                '*.ipynb',
                '*.yaml',
                '*.yml',
                '*.json',
                '*.md',
                '*.txt',
                '*.html'
            ]
            
            with zipfile.ZipFile(ruta_respaldo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Respaldo de directorios
                for directorio in directorios_respaldo:
                    if Path(directorio).exists():
                        for root, dirs, files in os.walk(directorio):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to('.')
                                zipf.write(file_path, arcname)
                
                # Respaldo de archivos
                for patron in archivos_respaldo:
                    for archivo in Path('.').glob(patron):
                        if archivo.is_file() and not archivo.name.startswith('.'):
                            zipf.write(archivo, archivo.name)
            
            # Calcular hash del respaldo
            hash_respaldo = self._calcular_hash_archivo(ruta_respaldo)
            
            # Crear metadatos
            metadatos = {
                'nombre': nombre_respaldo,
                'tipo': 'completo',
                'timestamp': datetime.now().isoformat(),
                'tamaño_bytes': ruta_respaldo.stat().st_size,
                'hash': hash_respaldo,
                'archivos_incluidos': len(zipf.namelist()),
                'compresion': True
            }
            
            # Guardar metadatos
            ruta_metadatos = self.directorio_respaldos / f"{nombre_respaldo}_metadata.json"
            with open(ruta_metadatos, 'w', encoding='utf-8') as f:
                json.dump(metadatos, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Respaldo completo creado: {nombre_respaldo}")
            return metadatos
            
        except Exception as e:
            self.logger.error(f"Error creando respaldo completo: {e}")
            return {'error': str(e)}
    
    def crear_respaldo_incremental(self, respaldo_base: str = None) -> Dict[str, Any]:
        """Crear respaldo incremental"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_respaldo = f"respaldo_incremental_{timestamp}"
            ruta_respaldo = self.directorio_respaldos / f"{nombre_respaldo}.zip"
            
            # Buscar ultimo respaldo completo
            if not respaldo_base:
                respaldos_completos = list(self.directorio_respaldos.glob("respaldo_completo_*.zip"))
                if respaldos_completos:
                    respaldo_base = max(respaldos_completos, key=os.path.getctime)
                else:
                    return {'error': 'No hay respaldo base para incremental'}
            
            # Obtener fecha del respaldo base
            fecha_base = datetime.fromtimestamp(os.path.getctime(respaldo_base))
            
            with zipfile.ZipFile(ruta_respaldo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                archivos_incluidos = 0
                
                # Buscar archivos modificados desde el respaldo base
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.stat().st_mtime > fecha_base.timestamp():
                            arcname = file_path.relative_to('.')
                            zipf.write(file_path, arcname)
                            archivos_incluidos += 1
            
            # Metadatos
            metadatos = {
                'nombre': nombre_respaldo,
                'tipo': 'incremental',
                'timestamp': datetime.now().isoformat(),
                'respaldo_base': str(respaldo_base),
                'tamaño_bytes': ruta_respaldo.stat().st_size,
                'archivos_incluidos': archivos_incluidos,
                'compresion': True
            }
            
            # Guardar metadatos
            ruta_metadatos = self.directorio_respaldos / f"{nombre_respaldo}_metadata.json"
            with open(ruta_metadatos, 'w', encoding='utf-8') as f:
                json.dump(metadatos, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Respaldo incremental creado: {nombre_respaldo}")
            return metadatos
            
        except Exception as e:
            self.logger.error(f"Error creando respaldo incremental: {e}")
            return {'error': str(e)}
    
    def _calcular_hash_archivo(self, ruta_archivo: Path) -> str:
        """Calcular hash SHA-256 de un archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando hash: {e}")
            return ""
    
    def listar_respaldos(self) -> List[Dict[str, Any]]:
        """Listar todos los respaldos disponibles"""
        try:
            respaldos = []
            
            for archivo_zip in self.directorio_respaldos.glob("*.zip"):
                # Buscar metadatos correspondientes
                nombre_base = archivo_zip.stem
                archivo_metadatos = self.directorio_respaldos / f"{nombre_base}_metadata.json"
                
                if archivo_metadatos.exists():
                    with open(archivo_metadatos, 'r', encoding='utf-8') as f:
                        metadatos = json.load(f)
                    respaldos.append(metadatos)
                else:
                    # Metadatos basicos si no existe archivo de metadatos
                    respaldos.append({
                        'nombre': nombre_base,
                        'tipo': 'desconocido',
                        'timestamp': datetime.fromtimestamp(archivo_zip.stat().st_mtime).isoformat(),
                        'tamaño_bytes': archivo_zip.stat().st_size,
                        'archivos_incluidos': 0
                    })
            
            return sorted(respaldos, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listando respaldos: {e}")
            return []
    
    def restaurar_respaldo(self, nombre_respaldo: str) -> Dict[str, Any]:
        """Restaurar sistema desde un respaldo"""
        try:
            ruta_respaldo = self.directorio_respaldos / f"{nombre_respaldo}.zip"
            
            if not ruta_respaldo.exists():
                return {'error': 'Respaldo no encontrado'}
            
            # Crear directorio de restauracion
            directorio_restauracion = Path(f"restauracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            directorio_restauracion.mkdir(exist_ok=True)
            
            # Extraer respaldo
            with zipfile.ZipFile(ruta_respaldo, 'r') as zipf:
                zipf.extractall(directorio_restauracion)
            
            self.logger.info(f"Respaldo restaurado en: {directorio_restauracion}")
            return {
                'exito': True,
                'directorio_restauracion': str(directorio_restauracion),
                'archivos_extraidos': len(zipf.namelist())
            }
            
        except Exception as e:
            self.logger.error(f"Error restaurando respaldo: {e}")
            return {'error': str(e)}
    
    def limpiar_respaldos_antiguos(self, dias_retener: int = None) -> Dict[str, Any]:
        """Limpiar respaldos antiguos"""
        try:
            if dias_retener is None:
                dias_retener = self.config_respaldos['retencion_dias']
            
            fecha_limite = datetime.now() - timedelta(days=dias_retener)
            archivos_eliminados = 0
            espacio_liberado = 0
            
            for archivo in self.directorio_respaldos.glob("*.zip"):
                fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime)
                if fecha_archivo < fecha_limite:
                    tamaño_archivo = archivo.stat().st_size
                    archivo.unlink()
                    archivos_eliminados += 1
                    espacio_liberado += tamaño_archivo
                    
                    # Eliminar metadatos si existen
                    metadatos_archivo = archivo.with_suffix('_metadata.json')
                    if metadatos_archivo.exists():
                        metadatos_archivo.unlink()
            
            self.logger.info(f"Respaldos antiguos eliminados: {archivos_eliminados}")
            return {
                'archivos_eliminados': archivos_eliminados,
                'espacio_liberado_mb': round(espacio_liberado / (1024**2), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error limpiando respaldos: {e}")
            return {'error': str(e)}

def main():
    """Funcion principal para probar conectores de monitoreo y respaldos"""
    print("CONECTORES MONITOREO Y RESPALDOS - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Probar conector de monitoreo
        print("\n1. Probando Conector de Monitoreo...")
        conector_monitoreo = ConectorMonitoreo()
        
        # Obtener metricas
        metricas = conector_monitoreo.obtener_metricas_sistema()
        print(f"   CPU: {metricas.get('cpu_percent', 0):.1f}%")
        print(f"   Memoria: {metricas.get('memoria_percent', 0):.1f}%")
        print(f"   Disco: {metricas.get('disco_percent', 0):.1f}%")
        
        # Verificar alertas
        alertas = conector_monitoreo.verificar_alertas(metricas)
        print(f"   Alertas detectadas: {len(alertas)}")
        
        # Obtener estadisticas
        stats = conector_monitoreo.obtener_estadisticas_monitoreo()
        print(f"   Registros en DB: {stats.get('metricas', {}).get('total_registros', 0)}")
        
        # Probar conector de respaldos
        print("\n2. Probando Conector de Respaldos...")
        conector_respaldos = ConectorRespaldos()
        
        # Crear respaldo completo
        respaldo = conector_respaldos.crear_respaldo_completo()
        if 'error' not in respaldo:
            print(f"   Respaldo creado: {respaldo['nombre']}")
            print(f"   Tamaño: {respaldo['tamaño_bytes'] / (1024**2):.2f} MB")
            print(f"   Archivos: {respaldo['archivos_incluidos']}")
        
        # Listar respaldos
        respaldos = conector_respaldos.listar_respaldos()
        print(f"   Respaldos disponibles: {len(respaldos)}")
        
        print("\nConectores de Monitoreo y Respaldos probados exitosamente")
        return True
        
    except Exception as e:
        print(f"\nError probando conectores: {e}")
        return False

if __name__ == "__main__":
    main()
