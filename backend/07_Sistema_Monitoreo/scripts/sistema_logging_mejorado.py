#!/usr/bin/env python3
"""
Sistema de Logging Mejorado para METGO 3D Operativo
Configuración centralizada de logging con rotación automática
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class SistemaLogging:
    """
    Sistema de logging centralizado para METGO 3D Operativo
    """
    
    def __init__(self, nombre_modulo="METGO_3D", nivel=logging.INFO):
        """
        Inicializar sistema de logging
        
        Args:
            nombre_modulo (str): Nombre del módulo
            nivel (int): Nivel de logging
        """
        self.nombre_modulo = nombre_modulo
        self.nivel = nivel
        self.logger = None
        self._configurar_logging()
    
    def _configurar_logging(self):
        """
        Configurar sistema de logging con rotación automática
        """
        # Crear directorio de logs si no existe
        directorio_logs = Path("logs")
        directorio_logs.mkdir(exist_ok=True)
        
        # Configurar logger principal
        self.logger = logging.getLogger(self.nombre_modulo)
        self.logger.setLevel(self.nivel)
        
        # Evitar duplicación de handlers
        if self.logger.handlers:
            return
        
        # Formato de logging
        formato = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo con rotación
        archivo_log = directorio_logs / f"{self.nombre_modulo.lower()}_operativo.log"
        handler_archivo = logging.handlers.RotatingFileHandler(
            archivo_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler_archivo.setLevel(self.nivel)
        handler_archivo.setFormatter(formato)
        
        # Handler para consola
        handler_consola = logging.StreamHandler()
        handler_consola.setLevel(logging.INFO)
        handler_consola.setFormatter(formato)
        
        # Agregar handlers
        self.logger.addHandler(handler_archivo)
        self.logger.addHandler(handler_consola)
        
        # Log inicial
        self.logger.info(f"Sistema de logging inicializado para {self.nombre_modulo}")
    
    def info(self, mensaje):
        """Log de información"""
        self.logger.info(mensaje)
    
    def warning(self, mensaje):
        """Log de advertencia"""
        self.logger.warning(mensaje)
    
    def error(self, mensaje):
        """Log de error"""
        self.logger.error(mensaje)
    
    def critical(self, mensaje):
        """Log crítico"""
        self.logger.critical(mensaje)
    
    def debug(self, mensaje):
        """Log de debug"""
        self.logger.debug(mensaje)
    
    def log_operacion(self, operacion, resultado="exitoso", detalles=""):
        """
        Log específico para operaciones del sistema
        
        Args:
            operacion (str): Nombre de la operación
            resultado (str): Resultado de la operación
            detalles (str): Detalles adicionales
        """
        mensaje = f"Operación: {operacion} - Resultado: {resultado}"
        if detalles:
            mensaje += f" - Detalles: {detalles}"
        
        if resultado == "exitoso":
            self.info(mensaje)
        elif resultado == "error":
            self.error(mensaje)
        else:
            self.warning(mensaje)
    
    def log_api(self, api, endpoint, status_code, tiempo_respuesta=None):
        """
        Log específico para llamadas a APIs
        
        Args:
            api (str): Nombre de la API
            endpoint (str): Endpoint llamado
            status_code (int): Código de respuesta
            tiempo_respuesta (float): Tiempo de respuesta en segundos
        """
        mensaje = f"API {api} - {endpoint} - Status: {status_code}"
        if tiempo_respuesta:
            mensaje += f" - Tiempo: {tiempo_respuesta:.2f}s"
        
        if status_code == 200:
            self.info(mensaje)
        elif status_code >= 400:
            self.error(mensaje)
        else:
            self.warning(mensaje)
    
    def log_ml(self, modelo, metricas, tiempo_entrenamiento=None):
        """
        Log específico para operaciones de Machine Learning
        
        Args:
            modelo (str): Nombre del modelo
            metricas (dict): Métricas del modelo
            tiempo_entrenamiento (float): Tiempo de entrenamiento en segundos
        """
        mensaje = f"ML Modelo: {modelo}"
        
        if metricas:
            mensaje += f" - R²: {metricas.get('r2', 'N/A'):.4f}"
            mensaje += f" - RMSE: {metricas.get('rmse', 'N/A'):.4f}"
        
        if tiempo_entrenamiento:
            mensaje += f" - Tiempo: {tiempo_entrenamiento:.2f}s"
        
        self.info(mensaje)
    
    def log_datos(self, operacion, registros_procesados, errores=0):
        """
        Log específico para operaciones de datos
        
        Args:
            operacion (str): Tipo de operación
            registros_procesados (int): Número de registros procesados
            errores (int): Número de errores encontrados
        """
        mensaje = f"Datos {operacion} - Registros: {registros_procesados}"
        if errores > 0:
            mensaje += f" - Errores: {errores}"
            self.warning(mensaje)
        else:
            self.info(mensaje)

# Instancia global del sistema de logging
logger_global = SistemaLogging("METGO_3D_OPERATIVO")

def obtener_logger(nombre_modulo=None):
    """
    Obtener instancia del logger
    
    Args:
        nombre_modulo (str): Nombre del módulo específico
    
    Returns:
        SistemaLogging: Instancia del logger
    """
    if nombre_modulo:
        return SistemaLogging(nombre_modulo)
    return logger_global

# Funciones de conveniencia
def log_info(mensaje):
    """Log de información"""
    logger_global.info(mensaje)

def log_warning(mensaje):
    """Log de advertencia"""
    logger_global.warning(mensaje)

def log_error(mensaje):
    """Log de error"""
    logger_global.error(mensaje)

def log_critical(mensaje):
    """Log crítico"""
    logger_global.critical(mensaje)

def log_debug(mensaje):
    """Log de debug"""
    logger_global.debug(mensaje)

# Ejemplo de uso
if __name__ == "__main__":
    # Probar sistema de logging
    logger = obtener_logger("TEST")
    
    logger.info("Sistema de logging funcionando correctamente")
    logger.log_operacion("carga_datos", "exitoso", "30 registros cargados")
    logger.log_api("OpenMeteo", "/forecast", 200, 1.5)
    logger.log_ml("RandomForest", {"r2": 0.85, "rmse": 2.3}, 45.2)
    logger.log_datos("procesamiento", 100, 0)
    
    print("✅ Sistema de logging probado exitosamente")
