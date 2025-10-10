"""
SISTEMA DE BACKUP AUTOMÁTICO - METGO 3D QUILLOTA
Realiza respaldos automáticos del sistema
"""

import os
import shutil
import zipfile
import json
import sqlite3
from datetime import datetime, timedelta
import logging

class BackupAutomatico:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.config = self._cargar_configuracion()
        self.directorio_backup = self.config['directorio_backup']
        self.retencion_dias = self.config['retencion_dias']
    
    def _configurar_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup_automatico.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('BACKUP_AUTOMATICO')
    
    def _cargar_configuracion(self):
        """Cargar configuración de backup"""
        try:
            with open('config/backup_config.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'directorio_backup': './backups',
                'retencion_dias': 30,
                'archivos_incluir': [
                    'data/',
                    'logs/',
                    'config/',
                    '*.db',
                    '*.json',
                    '*.py'
                ]
            }
    
    def crear_backup_completo(self):
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_backup = f"metgo_backup_{timestamp}.zip"
            ruta_backup = os.path.join(self.directorio_backup, nombre_backup)
            
            # Crear directorio de backup si no existe
            os.makedirs(self.directorio_backup, exist_ok=True)
            
            # Crear archivo ZIP
            with zipfile.ZipFile(ruta_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Incluir archivos y directorios especificados
                for patron in self.config['archivos_incluir']:
                    if patron.endswith('/'):
                        # Directorio
                        directorio = patron[:-1]
                        if os.path.exists(directorio):
                            for root, dirs, files in os.walk(directorio):
                                for file in files:
                                    ruta_completa = os.path.join(root, file)
                                    ruta_relativa = os.path.relpath(ruta_completa)
                                    zipf.write(ruta_completa, ruta_relativa)
                    else:
                        # Archivo con patrón
                        import glob
                        for archivo in glob.glob(patron):
                            if os.path.isfile(archivo):
                                zipf.write(archivo, os.path.basename(archivo))
            
            # Verificar tamaño del backup
            tamaño_mb = os.path.getsize(ruta_backup) / (1024 * 1024)
            
            self.logger.info(f"Backup creado: {nombre_backup} ({tamaño_mb:.2f} MB)")
            
            # Limpiar backups antiguos
            self._limpiar_backups_antiguos()
            
            return ruta_backup
            
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None
    
    def _limpiar_backups_antiguos(self):
        """Limpiar backups antiguos según retención"""
        try:
            fecha_limite = datetime.now() - timedelta(days=self.retencion_dias)
            
            for archivo in os.listdir(self.directorio_backup):
                if archivo.startswith('metgo_backup_') and archivo.endswith('.zip'):
                    ruta_archivo = os.path.join(self.directorio_backup, archivo)
                    fecha_archivo = datetime.fromtimestamp(os.path.getctime(ruta_archivo))
                    
                    if fecha_archivo < fecha_limite:
                        os.remove(ruta_archivo)
                        self.logger.info(f"Backup antiguo eliminado: {archivo}")
                        
        except Exception as e:
            self.logger.error(f"Error limpiando backups antiguos: {e}")
    
    def restaurar_backup(self, nombre_backup: str, directorio_destino: str = '.'):
        """Restaurar backup"""
        try:
            ruta_backup = os.path.join(self.directorio_backup, nombre_backup)
            
            if not os.path.exists(ruta_backup):
                self.logger.error(f"Backup no encontrado: {nombre_backup}")
                return False
            
            with zipfile.ZipFile(ruta_backup, 'r') as zipf:
                zipf.extractall(directorio_destino)
            
            self.logger.info(f"Backup restaurado: {nombre_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando backup: {e}")
            return False
    
    def listar_backups(self):
        """Listar backups disponibles"""
        try:
            backups = []
            for archivo in os.listdir(self.directorio_backup):
                if archivo.startswith('metgo_backup_') and archivo.endswith('.zip'):
                    ruta_archivo = os.path.join(self.directorio_backup, archivo)
                    tamaño_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)
                    fecha_creacion = datetime.fromtimestamp(os.path.getctime(ruta_archivo))
                    
                    backups.append({
                        'nombre': archivo,
                        'tamaño_mb': tamaño_mb,
                        'fecha_creacion': fecha_creacion.isoformat()
                    })
            
            return sorted(backups, key=lambda x: x['fecha_creacion'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
            return []

def main():
    """Función principal"""
    backup = BackupAutomatico()
    
    # Crear backup
    print("Creando backup del sistema...")
    ruta_backup = backup.crear_backup_completo()
    
    if ruta_backup:
        print(f"Backup creado exitosamente: {ruta_backup}")
    else:
        print("Error creando backup")
    
    # Listar backups
    print("\nBackups disponibles:")
    backups = backup.listar_backups()
    for backup_info in backups:
        print(f"  - {backup_info['nombre']} ({backup_info['tamaño_mb']:.2f} MB) - {backup_info['fecha_creacion']}")

if __name__ == "__main__":
    main()
