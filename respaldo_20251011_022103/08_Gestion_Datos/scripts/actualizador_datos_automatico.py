"""
ACTUALIZADOR AUTOMÁTICO DE DATOS METEOROLÓGICOS
METGO 3D Quillota - Sistema de Actualización en Tiempo Real
"""

import time
import schedule
import logging
import json
import os
from datetime import datetime, timedelta
import sqlite3
import sys

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conector_apis_meteorologicas_reales import ConectorAPIsMeteorologicas
from sistema_notificaciones_avanzado import SistemaNotificacionesAvanzado

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/actualizador_automatico.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ActualizadorDatosAutomatico:
    def __init__(self):
        self.conector = ConectorAPIsMeteorologicas()
        self.sistema_notificaciones = SistemaNotificacionesAvanzado()
        self.base_datos = "datos_meteorologicos_reales.db"
        self.estaciones = {
            "Quillota_Centro": {"lat": -32.8833, "lon": -71.2667},
            "La_Cruz": {"lat": -32.8167, "lon": -71.2167},
            "Nogales": {"lat": -32.7500, "lon": -71.2167},
            "San_Isidro": {"lat": -32.9167, "lon": -71.2333},
            "Pocochay": {"lat": -32.8500, "lon": -71.3000},
            "Valle_Hermoso": {"lat": -32.9333, "lon": -71.2833}
        }
        self._crear_directorio_logs()
    
    def _crear_directorio_logs(self):
        """Crear directorio de logs si no existe"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
    
    def actualizar_datos_estaciones(self):
        """Actualizar datos de todas las estaciones meteorológicas"""
        logger.info("Iniciando actualización automática de datos meteorológicos")
        
        datos_actualizados = {}
        exitos = 0
        errores = 0
        
        for nombre_estacion, coordenadas in self.estaciones.items():
            try:
                logger.info(f"Actualizando datos de {nombre_estacion}")
                
                # Obtener datos de la API
                datos = self.conector.obtener_datos_openmeteo_coordenadas(
                    coordenadas["lat"], 
                    coordenadas["lon"]
                )
                
                if datos and "error" not in datos:
                    # Guardar en base de datos
                    self._guardar_datos_estacion(nombre_estacion, datos)
                    
                    # Guardar en archivo JSON para acceso rápido
                    datos_actualizados[nombre_estacion] = datos
                    
                    exitos += 1
                    logger.info(f"[OK] Datos actualizados para {nombre_estacion}: {datos.get('temperatura_actual', 'N/A')}°C")
                    
                else:
                    errores += 1
                    logger.error(f"[ERROR] Error obteniendo datos de {nombre_estacion}")
                
                # Pausa entre peticiones para no sobrecargar la API
                time.sleep(2)
                
            except Exception as e:
                errores += 1
                logger.error(f"[ERROR] Error actualizando {nombre_estacion}: {str(e)}")
        
        # Guardar datos actualizados en archivo JSON
        self._guardar_datos_json(datos_actualizados)
        
        # Generar reporte de actualización
        self._generar_reporte_actualizacion(exitos, errores, datos_actualizados)
        
        # Procesar alertas y enviar notificaciones
        if datos_actualizados:
            logger.info("Procesando alertas meteorológicas y enviando notificaciones...")
            resultados_notificaciones = self.sistema_notificaciones.procesar_datos_y_notificar(datos_actualizados)
            logger.info(f"Notificaciones: {resultados_notificaciones}")
        
        logger.info(f"Actualización completada: {exitos} exitos, {errores} errores")
        
        return exitos > 0
    
    def _guardar_datos_estacion(self, nombre_estacion: str, datos: dict):
        """Guardar datos de una estación en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Insertar datos meteorológicos
            cursor.execute('''
                INSERT INTO datos_meteorologicos (
                    estacion, fecha, temperatura, temperatura_max, temperatura_min,
                    precipitacion, humedad_relativa, presion_atmosferica,
                    velocidad_viento, direccion_viento, nubosidad, punto_rocio,
                    fuente_api, calidad_datos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre_estacion,
                datetime.now().isoformat(),
                datos.get('temperatura_actual'),
                datos.get('pronostico_24h', {}).get('temp_max') if datos.get('pronostico_24h') else None,
                datos.get('pronostico_24h', {}).get('temp_min') if datos.get('pronostico_24h') else None,
                datos.get('precipitacion'),
                datos.get('humedad_relativa'),
                datos.get('presion_atmosferica'),
                datos.get('velocidad_viento'),
                datos.get('direccion_viento'),
                datos.get('nubosidad'),
                datos.get('punto_rocio'),
                'openmeteo',
                'buena'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando datos de {nombre_estacion} en BD: {str(e)}")
    
    def _guardar_datos_json(self, datos: dict):
        """Guardar datos actualizados en archivo JSON para acceso rápido"""
        try:
            datos_completos = {
                "fecha_actualizacion": datetime.now().isoformat(),
                "total_estaciones": len(datos),
                "datos_estaciones": datos
            }
            
            with open('datos_meteorologicos_actualizados.json', 'w', encoding='utf-8') as f:
                json.dump(datos_completos, f, indent=2, ensure_ascii=False)
            
            logger.info("Datos guardados en archivo JSON")
            
        except Exception as e:
            logger.error(f"Error guardando datos JSON: {str(e)}")
    
    def _generar_reporte_actualizacion(self, exitos: int, errores: int, datos: dict):
        """Generar reporte de actualización"""
        try:
            reporte = {
                "fecha": datetime.now().isoformat(),
                "resumen": {
                    "total_estaciones": len(self.estaciones),
                    "exitos": exitos,
                    "errores": errores,
                    "tasa_exito": (exitos / len(self.estaciones)) * 100
                },
                "estaciones": {}
            }
            
            for nombre, datos_estacion in datos.items():
                reporte["estaciones"][nombre] = {
                    "temperatura": datos_estacion.get('temperatura_actual'),
                    "humedad": datos_estacion.get('humedad_relativa'),
                    "precipitacion": datos_estacion.get('precipitacion'),
                    "viento": datos_estacion.get('velocidad_viento'),
                    "alertas": len(datos_estacion.get('alertas', []))
                }
            
            # Guardar reporte
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_reporte = f'reportes/reporte_actualizacion_{timestamp}.json'
            
            # Crear directorio de reportes si no existe
            if not os.path.exists('reportes'):
                os.makedirs('reportes')
            
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte guardado: {archivo_reporte}")
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
    
    def verificar_alertas_criticas(self, datos: dict):
        """Verificar y procesar alertas críticas"""
        alertas_criticas = []
        
        for nombre_estacion, datos_estacion in datos.items():
            if 'alertas' in datos_estacion:
                for alerta in datos_estacion['alertas']:
                    if alerta['nivel'] == 'critico':
                        alertas_criticas.append({
                            'estacion': nombre_estacion,
                            'tipo': alerta['tipo'],
                            'descripcion': alerta['descripcion'],
                            'fecha': datetime.now().isoformat()
                        })
        
        if alertas_criticas:
            logger.warning(f"🚨 {len(alertas_criticas)} alertas críticas detectadas")
            
            # Guardar alertas críticas
            self._guardar_alertas_criticas(alertas_criticas)
            
            # Aquí se podría integrar el sistema de notificaciones
            # self._enviar_notificaciones_emergencia(alertas_criticas)
        
        return alertas_criticas
    
    def _guardar_alertas_criticas(self, alertas: list):
        """Guardar alertas críticas en archivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_alertas = f'alertas/alertas_criticas_{timestamp}.json'
            
            # Crear directorio de alertas si no existe
            if not os.path.exists('alertas'):
                os.makedirs('alertas')
            
            with open(archivo_alertas, 'w', encoding='utf-8') as f:
                json.dump(alertas, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Alertas críticas guardadas: {archivo_alertas}")
            
        except Exception as e:
            logger.error(f"Error guardando alertas críticas: {str(e)}")
    
    def iniciar_actualizacion_automatica(self):
        """Iniciar el sistema de actualización automática"""
        logger.info("Iniciando sistema de actualización automática")
        
        # Programar actualizaciones cada hora
        schedule.every().hour.do(self.actualizar_datos_estaciones)
        
        # Actualización inicial
        logger.info("Realizando actualización inicial...")
        self.actualizar_datos_estaciones()
        
        logger.info("Sistema de actualización automática iniciado")
        logger.info("Próxima actualización programada para cada hora")
        
        # Mantener el proceso ejecutándose
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    
    def ejecutar_actualizacion_manual(self):
        """Ejecutar una actualización manual"""
        logger.info("Ejecutando actualización manual...")
        return self.actualizar_datos_estaciones()

def main():
    """Función principal"""
    print("=" * 60)
    print("ACTUALIZADOR AUTOMÁTICO DE DATOS METEOROLÓGICOS")
    print("METGO 3D Quillota - Sistema de Actualización en Tiempo Real")
    print("=" * 60)
    print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    actualizador = ActualizadorDatosAutomatico()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        # Ejecutar actualización manual
        print("[MODO] Actualización manual")
        exito = actualizador.ejecutar_actualizacion_manual()
        
        if exito:
            print("[RESULTADO] Actualización manual exitosa")
        else:
            print("[RESULTADO] Error en actualización manual")
    else:
        # Ejecutar actualización automática
        print("[MODO] Actualización automática (cada hora)")
        print("[INFO] Presiona Ctrl+C para detener")
        print()
        
        try:
            actualizador.iniciar_actualizacion_automatica()
        except KeyboardInterrupt:
            print("\n[INFO] Sistema de actualización detenido por el usuario")
        except Exception as e:
            print(f"\n[ERROR] Error en sistema de actualización: {str(e)}")

if __name__ == "__main__":
    main()
