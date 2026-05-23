#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💾 RESPALDOS AUTOMÁTICOS METGO 3D
Sistema Meteorológico Agrícola Quillota - Sistema de Respaldos Automáticos
"""

import os
import sys
import time
import json
import shutil
import zipfile
import tarfile
import hashlib
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
import psutil
import requests

# Configuración
warnings.filterwarnings('ignore')

class TipoRespaldo(Enum):
    """Tipos de respaldo"""
    COMPLETO = "completo"
    INCREMENTAL = "incremental"
    DIFERENCIAL = "diferencial"

class EstadoRespaldo(Enum):
    """Estados de respaldo"""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"

@dataclass
class Respaldo:
    """Estructura de respaldo"""
    id: str
    tipo: TipoRespaldo
    estado: EstadoRespaldo
    timestamp: datetime
    archivo: str
    tamaño: int
    checksum: str
    duracion: float
    metadata: Dict[str, Any] = None

@dataclass
class ConfiguracionRespaldo:
    """Configuración de respaldo"""
    nombre: str
    directorios: List[str]
    exclusiones: List[str]
    tipo: TipoRespaldo
    compresion: bool
    cifrado: bool
    programacion: str
    retencion_dias: int
    destino: str
    metadata: Dict[str, Any] = None

class RespaldosAutomaticosMETGO:
    """Sistema de respaldos automáticos para METGO 3D"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_respaldos': 'backups',
            'directorio_logs': 'logs/backups',
            'directorio_config': 'config/backups',
            'directorio_temp': 'temp/backups',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Configuración de respaldos
        self.configuracion_respaldos = {
            'habilitar_respaldos': True,
            'frecuencia_completo': '0 2 * * 0',  # Domingos a las 2 AM
            'frecuencia_incremental': '0 3 * * 1-6',  # Lunes a Sábado a las 3 AM
            'compresion': True,
            'cifrado': False,
            'retencion_dias': 30,
            'verificacion_integridad': True,
            'notificaciones': True,
            'limpieza_automatica': True
        }
        
        # Estado del sistema
        self.estado_sistema = {
            'activo': False,
            'ultimo_respaldo': None,
            'respaldos_completados': 0,
            'respaldos_fallidos': 0,
            'espacio_utilizado': 0,
            'errores': []
        }
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuraciones de respaldo
        self.respaldos_configurados = self._cargar_configuraciones()
        
        # Hilo de programación
        self.hilo_programacion = None
        self.detener_hilo = threading.Event()
        
        # Configuración de notificaciones
        self.configuracion_notificaciones = {
            'email': {
                'habilitado': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'usuario': 'metgo3d@example.com',
                'password': 'password',
                'destinatarios': ['admin@metgo3d.cl']
            },
            'webhook': {
                'habilitado': False,
                'url': 'https://api.example.com/webhook',
                'headers': {'Authorization': 'Bearer token'}
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/respaldos_automaticos.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_RESPALDOS_AUTOMATICOS')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_respaldos']}/respaldos.db"
            
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
            
            # Crear tablas
            self._crear_tablas_bd()
            
            self.logger.info(f"Base de datos inicializada: {archivo_bd}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _crear_tablas_bd(self):
        """Crear tablas en la base de datos"""
        try:
            # Tabla de respaldos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS respaldos (
                    id TEXT PRIMARY KEY,
                    tipo TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    archivo TEXT NOT NULL,
                    tamaño INTEGER,
                    checksum TEXT,
                    duracion REAL,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de configuraciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS configuraciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    configuracion TEXT NOT NULL,
                    activa BOOLEAN DEFAULT TRUE,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de eventos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_respaldos_timestamp ON respaldos(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_respaldos_tipo ON respaldos(tipo)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_respaldos_estado ON respaldos(estado)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _cargar_configuraciones(self) -> List[ConfiguracionRespaldo]:
        """Cargar configuraciones de respaldo"""
        try:
            configuraciones = []
            
            # Configuración por defecto
            config_default = ConfiguracionRespaldo(
                nombre="metgo3d_completo",
                directorios=[
                    "data",
                    "config",
                    "logs",
                    "reportes",
                    "graficos",
                    "modelos_ml_quillota"
                ],
                exclusiones=[
                    "*.tmp",
                    "*.log",
                    "*.cache",
                    "temp/*",
                    "backups/*"
                ],
                tipo=TipoRespaldo.COMPLETO,
                compresion=True,
                cifrado=False,
                programacion="0 2 * * 0",
                retencion_dias=30,
                destino="backups/completos"
            )
            configuraciones.append(config_default)
            
            # Configuración incremental
            config_incremental = ConfiguracionRespaldo(
                nombre="metgo3d_incremental",
                directorios=[
                    "data",
                    "logs"
                ],
                exclusiones=[
                    "*.tmp",
                    "*.cache"
                ],
                tipo=TipoRespaldo.INCREMENTAL,
                compresion=True,
                cifrado=False,
                programacion="0 3 * * 1-6",
                retencion_dias=7,
                destino="backups/incrementales"
            )
            configuraciones.append(config_incremental)
            
            return configuraciones
            
        except Exception as e:
            self.logger.error(f"Error cargando configuraciones: {e}")
            return []
    
    def crear_respaldo(self, configuracion: ConfiguracionRespaldo) -> Respaldo:
        """Crear respaldo según configuración"""
        try:
            inicio = time.time()
            timestamp = datetime.now()
            respaldo_id = f"respaldo_{configuracion.nombre}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"Iniciando respaldo: {respaldo_id}")
            
            # Crear respaldo
            respaldo = Respaldo(
                id=respaldo_id,
                tipo=configuracion.tipo,
                estado=EstadoRespaldo.EN_PROGRESO,
                timestamp=timestamp,
                archivo="",
                tamaño=0,
                checksum="",
                duracion=0,
                metadata={'configuracion': configuracion.nombre}
            )
            
            # Guardar respaldo en base de datos
            self._guardar_respaldo(respaldo)
            
            # Crear directorio de destino
            destino_dir = Path(configuracion.destino)
            destino_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo de respaldo
            if configuracion.compresion:
                archivo_respaldo = destino_dir / f"{respaldo_id}.tar.gz"
                respaldo.archivo = str(archivo_respaldo)
                
                # Crear respaldo comprimido
                with tarfile.open(archivo_respaldo, "w:gz") as tar:
                    for directorio in configuracion.directorios:
                        if Path(directorio).exists():
                            tar.add(directorio, arcname=directorio)
            else:
                archivo_respaldo = destino_dir / f"{respaldo_id}.zip"
                respaldo.archivo = str(archivo_respaldo)
                
                # Crear respaldo ZIP
                with zipfile.ZipFile(archivo_respaldo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for directorio in configuracion.directorios:
                        if Path(directorio).exists():
                            for root, dirs, files in os.walk(directorio):
                                for file in files:
                                    file_path = Path(root) / file
                                    arcname = file_path.relative_to(Path.cwd())
                                    zipf.write(file_path, arcname)
            
            # Calcular tamaño y checksum
            respaldo.tamaño = archivo_respaldo.stat().st_size
            respaldo.checksum = self._calcular_checksum(archivo_respaldo)
            respaldo.duracion = time.time() - inicio
            respaldo.estado = EstadoRespaldo.COMPLETADO
            
            # Actualizar respaldo en base de datos
            self._guardar_respaldo(respaldo)
            
            # Verificar integridad si está habilitado
            if self.configuracion_respaldos['verificacion_integridad']:
                if not self._verificar_integridad(archivo_respaldo, respaldo.checksum):
                    respaldo.estado = EstadoRespaldo.FALLIDO
                    self._guardar_respaldo(respaldo)
                    raise Exception("Verificación de integridad falló")
            
            self.logger.info(f"Respaldo completado: {respaldo_id} ({respaldo.tamaño} bytes)")
            return respaldo
            
        except Exception as e:
            self.logger.error(f"Error creando respaldo: {e}")
            
            # Marcar respaldo como fallido
            if 'respaldo' in locals():
                respaldo.estado = EstadoRespaldo.FALLIDO
                respaldo.duracion = time.time() - inicio
                self._guardar_respaldo(respaldo)
            
            raise e
    
    def _calcular_checksum(self, archivo: Path) -> str:
        """Calcular checksum SHA256 de un archivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(archivo, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando checksum: {e}")
            return ""
    
    def _verificar_integridad(self, archivo: Path, checksum_esperado: str) -> bool:
        """Verificar integridad de un archivo"""
        try:
            checksum_calculado = self._calcular_checksum(archivo)
            return checksum_calculado == checksum_esperado
        except Exception as e:
            self.logger.error(f"Error verificando integridad: {e}")
            return False
    
    def _guardar_respaldo(self, respaldo: Respaldo):
        """Guardar respaldo en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT OR REPLACE INTO respaldos 
                (id, tipo, estado, timestamp, archivo, tamaño, checksum, duracion, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                respaldo.id,
                respaldo.tipo.value,
                respaldo.estado.value,
                respaldo.timestamp,
                respaldo.archivo,
                respaldo.tamaño,
                respaldo.checksum,
                respaldo.duracion,
                json.dumps(respaldo.metadata) if respaldo.metadata else None
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando respaldo: {e}")
    
    def restaurar_respaldo(self, respaldo_id: str, destino: str = None) -> bool:
        """Restaurar respaldo desde archivo"""
        try:
            self.logger.info(f"Iniciando restauración: {respaldo_id}")
            
            # Obtener información del respaldo
            self.cursor_bd.execute('SELECT * FROM respaldos WHERE id = ?', (respaldo_id,))
            respaldo_data = self.cursor_bd.fetchone()
            
            if not respaldo_data:
                raise Exception(f"Respaldo no encontrado: {respaldo_id}")
            
            archivo_respaldo = Path(respaldo_data[4])  # archivo
            
            if not archivo_respaldo.exists():
                raise Exception(f"Archivo de respaldo no encontrado: {archivo_respaldo}")
            
            # Verificar integridad
            if not self._verificar_integridad(archivo_respaldo, respaldo_data[6]):  # checksum
                raise Exception("Verificación de integridad falló")
            
            # Determinar destino
            if not destino:
                destino = Path.cwd()
            else:
                destino = Path(destino)
            
            # Extraer respaldo
            if archivo_respaldo.suffix == '.gz':
                with tarfile.open(archivo_respaldo, "r:gz") as tar:
                    tar.extractall(destino)
            else:
                with zipfile.ZipFile(archivo_respaldo, 'r') as zipf:
                    zipf.extractall(destino)
            
            self.logger.info(f"Restauración completada: {respaldo_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando respaldo: {e}")
            return False
    
    def limpiar_respaldos_antiguos(self, dias_retencion: int = None) -> int:
        """Limpiar respaldos antiguos"""
        try:
            if not dias_retencion:
                dias_retencion = self.configuracion_respaldos['retencion_dias']
            
            fecha_limite = datetime.now() - timedelta(days=dias_retencion)
            
            # Obtener respaldos antiguos
            self.cursor_bd.execute('''
                SELECT id, archivo FROM respaldos 
                WHERE timestamp < ? AND estado = 'completado'
            ''', (fecha_limite,))
            
            respaldos_antiguos = self.cursor_bd.fetchall()
            respaldos_eliminados = 0
            
            for respaldo_id, archivo in respaldos_antiguos:
                try:
                    # Eliminar archivo
                    if Path(archivo).exists():
                        Path(archivo).unlink()
                    
                    # Eliminar registro de base de datos
                    self.cursor_bd.execute('DELETE FROM respaldos WHERE id = ?', (respaldo_id,))
                    respaldos_eliminados += 1
                    
                except Exception as e:
                    self.logger.error(f"Error eliminando respaldo {respaldo_id}: {e}")
            
            self.conexion_bd.commit()
            
            self.logger.info(f"Respaldos antiguos eliminados: {respaldos_eliminados}")
            return respaldos_eliminados
            
        except Exception as e:
            self.logger.error(f"Error limpiando respaldos antiguos: {e}")
            return 0
    
    def programar_respaldos(self):
        """Programar respaldos automáticos"""
        try:
            self.logger.info("Programando respaldos automáticos...")
            
            # Limpiar programaciones existentes
            schedule.clear()
            
            # Programar respaldos completos
            schedule.every().sunday.at("02:00").do(
                self._ejecutar_respaldos_programados, 
                tipo=TipoRespaldo.COMPLETO
            )
            
            # Programar respaldos incrementales
            for dia in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                getattr(schedule.every(), dia).at("03:00").do(
                    self._ejecutar_respaldos_programados,
                    tipo=TipoRespaldo.INCREMENTAL
                )
            
            self.logger.info("Respaldos programados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error programando respaldos: {e}")
    
    def _ejecutar_respaldos_programados(self, tipo: TipoRespaldo):
        """Ejecutar respaldos programados"""
        try:
            self.logger.info(f"Ejecutando respaldos programados: {tipo.value}")
            
            for config in self.respaldos_configurados:
                if config.tipo == tipo:
                    try:
                        respaldo = self.crear_respaldo(config)
                        
                        # Enviar notificación
                        if self.configuracion_respaldos['notificaciones']:
                            self._enviar_notificacion_respaldo(respaldo)
                        
                        # Actualizar estadísticas
                        if respaldo.estado == EstadoRespaldo.COMPLETADO:
                            self.estado_sistema['respaldos_completados'] += 1
                        else:
                            self.estado_sistema['respaldos_fallidos'] += 1
                        
                        self.estado_sistema['ultimo_respaldo'] = respaldo.timestamp.isoformat()
                        
                    except Exception as e:
                        self.logger.error(f"Error ejecutando respaldo {config.nombre}: {e}")
                        self.estado_sistema['respaldos_fallidos'] += 1
            
            # Limpiar respaldos antiguos
            if self.configuracion_respaldos['limpieza_automatica']:
                self.limpiar_respaldos_antiguos()
            
        except Exception as e:
            self.logger.error(f"Error ejecutando respaldos programados: {e}")
    
    def _enviar_notificacion_respaldo(self, respaldo: Respaldo):
        """Enviar notificación de respaldo"""
        try:
            if not self.configuracion_notificaciones['email']['habilitado']:
                return
            
            config = self.configuracion_notificaciones['email']
            
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = config['usuario']
            msg['To'] = ', '.join(config['destinatarios'])
            msg['Subject'] = f"METGO 3D - Respaldo {respaldo.estado.value.upper()}"
            
            # Contenido del mensaje
            body = f"""
            Respaldo del Sistema METGO 3D
            
            ID: {respaldo.id}
            Tipo: {respaldo.tipo.value}
            Estado: {respaldo.estado.value}
            Tamaño: {respaldo.tamaño / (1024*1024):.2f} MB
            Duración: {respaldo.duracion:.2f} segundos
            Timestamp: {respaldo.timestamp}
            
            Sistema Meteorológico Agrícola Quillota
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['usuario'], config['password'])
            text = msg.as_string()
            server.sendmail(config['usuario'], config['destinatarios'], text)
            server.quit()
            
            self.logger.info(f"Notificación de respaldo enviada: {respaldo.id}")
            
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
    
    def iniciar_respaldos_automaticos(self) -> bool:
        """Iniciar respaldos automáticos"""
        try:
            self.logger.info("Iniciando respaldos automáticos...")
            
            self.estado_sistema['activo'] = True
            self.detener_hilo.clear()
            
            # Programar respaldos
            self.programar_respaldos()
            
            # Iniciar hilo de programación
            self.hilo_programacion = threading.Thread(
                target=self._hilo_programacion,
                name="RespaldosAutomaticos"
            )
            self.hilo_programacion.daemon = True
            self.hilo_programacion.start()
            
            self.logger.info("Respaldos automáticos iniciados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando respaldos automáticos: {e}")
            return False
    
    def _hilo_programacion(self):
        """Hilo para ejecutar programaciones"""
        while not self.detener_hilo.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                self.logger.error(f"Error en hilo de programación: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def detener_respaldos_automaticos(self):
        """Detener respaldos automáticos"""
        try:
            self.logger.info("Deteniendo respaldos automáticos...")
            
            self.estado_sistema['activo'] = False
            self.detener_hilo.set()
            
            # Esperar a que termine el hilo
            if self.hilo_programacion:
                self.hilo_programacion.join(timeout=10)
            
            self.logger.info("Respaldos automáticos detenidos")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo respaldos automáticos: {e}")
    
    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas de respaldos"""
        try:
            # Estadísticas de respaldos
            self.cursor_bd.execute('SELECT COUNT(*) FROM respaldos')
            total_respaldos = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('SELECT COUNT(*) FROM respaldos WHERE estado = "completado"')
            respaldos_completados = self.cursor_bd.fetchone()[0]
            
            self.cursor_bd.execute('SELECT COUNT(*) FROM respaldos WHERE estado = "fallido"')
            respaldos_fallidos = self.cursor_bd.fetchone()[0]
            
            # Tamaño total de respaldos
            self.cursor_bd.execute('SELECT SUM(tamaño) FROM respaldos WHERE estado = "completado"')
            tamaño_total = self.cursor_bd.fetchone()[0] or 0
            
            # Último respaldo
            self.cursor_bd.execute('''
                SELECT timestamp FROM respaldos 
                WHERE estado = "completado" 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            ultimo_respaldo = self.cursor_bd.fetchone()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'estado_sistema': self.estado_sistema,
                'estadisticas': {
                    'total_respaldos': total_respaldos,
                    'respaldos_completados': respaldos_completados,
                    'respaldos_fallidos': respaldos_fallidos,
                    'tamaño_total_mb': tamaño_total / (1024 * 1024),
                    'ultimo_respaldo': ultimo_respaldo[0] if ultimo_respaldo else None
                },
                'configuracion': self.configuracion_respaldos
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def generar_reporte_respaldos(self) -> str:
        """Generar reporte de respaldos"""
        try:
            self.logger.info("Generando reporte de respaldos...")
            
            estadisticas = self.obtener_estadisticas()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Respaldos Automáticos',
                'version': self.configuracion['version'],
                'resumen': {
                    'respaldos_activos': self.estado_sistema['activo'],
                    'ultimo_respaldo': self.estado_sistema.get('ultimo_respaldo'),
                    'respaldos_completados': self.estado_sistema['respaldos_completados'],
                    'respaldos_fallidos': self.estado_sistema['respaldos_fallidos']
                },
                'estadisticas': estadisticas,
                'configuracion': self.configuracion_respaldos,
                'recomendaciones': [
                    "Verificar regularmente el estado de los respaldos",
                    "Monitorear el espacio en disco disponible",
                    "Probar la restauración de respaldos periódicamente",
                    "Mantener configuraciones de respaldo actualizadas",
                    "Implementar respaldos en la nube para mayor seguridad"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"respaldos_automaticos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de respaldos generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del sistema de respaldos automáticos"""
    print("💾 RESPALDOS AUTOMÁTICOS METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Sistema de Respaldos Automáticos")
    print("=" * 80)
    
    try:
        # Crear sistema de respaldos
        respaldos = RespaldosAutomaticosMETGO()
        
        # Ejecutar respaldo completo
        print(f"\n💾 Ejecutando respaldo completo...")
        configuracion = respaldos.respaldos_configurados[0]  # Configuración completa
        respaldo = respaldos.crear_respaldo(configuracion)
        
        print(f"✅ Respaldo completado: {respaldo.id}")
        print(f"📁 Archivo: {respaldo.archivo}")
        print(f"📊 Tamaño: {respaldo.tamaño / (1024*1024):.2f} MB")
        print(f"⏱️ Duración: {respaldo.duracion:.2f} segundos")
        print(f"🔒 Checksum: {respaldo.checksum[:16]}...")
        
        # Obtener estadísticas
        print(f"\n📊 Estadísticas de respaldos:")
        estadisticas = respaldos.obtener_estadisticas()
        if estadisticas:
            stats = estadisticas.get('estadisticas', {})
            print(f"   Total respaldos: {stats.get('total_respaldos', 0)}")
            print(f"   Respaldos completados: {stats.get('respaldos_completados', 0)}")
            print(f"   Respaldos fallidos: {stats.get('respaldos_fallidos', 0)}")
            print(f"   Tamaño total: {stats.get('tamaño_total_mb', 0):.2f} MB")
            print(f"   Último respaldo: {stats.get('ultimo_respaldo', 'N/A')}")
        
        # Generar reporte
        print(f"\n📋 Generando reporte...")
        reporte = respaldos.generar_reporte_respaldos()
        
        if reporte:
            print(f"\n✅ Respaldos automáticos ejecutados exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print(f"\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en respaldos automáticos: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
