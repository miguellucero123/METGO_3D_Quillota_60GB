"""
Sistema de logging y configuración para METGO 3D Operativo.
Versión robusta con logging estructurado.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from datetime import datetime


def configurar_logger(nombre: str, nivel: str = "INFO", 
                     archivo_log: Optional[str] = None) -> logging.Logger:
    """
    Configurar logger estructurado para el sistema.
    
    Args:
        nombre: Nombre del logger
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        archivo_log: Ruta al archivo de log (opcional)
        
    Returns:
        Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(nombre)
    logger.setLevel(getattr(logging, nivel.upper()))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Crear directorio de logs si no existe
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    if archivo_log is None:
        archivo_log = logs_dir / f"metgo_operativo_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        archivo_log,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formato)
    logger.addHandler(file_handler)
    
    return logger


def cargar_configuracion(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Cargar configuración del sistema.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con configuración
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config_template.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        logging.warning(f"Archivo de configuración no encontrado: {config_path}")
        return {}
    except Exception as e:
        logging.error(f"Error cargando configuración: {e}")
        return {}


def crear_directorios_proyecto():
    """Crear directorios necesarios del proyecto."""
    directorios = [
        "data/raw",
        "data/processed", 
        "data/external",
        "logs",
        "tests",
        "docs",
        "notebooks",
        "scripts"
    ]
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
    
    logging.info("Directorios del proyecto creados/verificados")
