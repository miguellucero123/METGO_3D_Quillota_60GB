"""
SISTEMA DE MONITOREO DE PRODUCCIÓN - METGO 3D QUILLOTA
Monitorea el estado del sistema en tiempo real
"""

import psutil
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List

class MonitoreoProduccion:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.config = self._cargar_configuracion()
        self.servicios = [
            {'nombre': 'Dashboard Principal', 'url': 'http://localhost:8501'},
            {'nombre': 'Dashboard Agrícola', 'url': 'http://localhost:8510'},
            {'nombre': 'Sistema de Monitoreo', 'url': 'http://localhost:8502'}
        ]
    
    def _configurar_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/monitoreo_produccion.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('MONITOREO_PRODUCCION')
    
    def _cargar_configuracion(self):
        """Cargar configuración de monitoreo"""
        try:
            with open('config/monitoreo_config.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'intervalo_verificacion': 300,
                'umbral_memoria': 80,
                'umbral_cpu': 80,
                'alertas_email': False
            }
    
    def verificar_servicios(self) -> Dict:
        """Verificar estado de servicios"""
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'servicios': [],
            'sistema': self._verificar_sistema(),
            'alertas': []
        }
        
        for servicio in self.servicios:
            estado = self._verificar_servicio(servicio)
            resultados['servicios'].append(estado)
            
            if not estado['activo']:
                resultados['alertas'].append({
                    'tipo': 'servicio_inactivo',
                    'servicio': servicio['nombre'],
                    'mensaje': f"Servicio {servicio['nombre']} no está respondiendo"
                })
        
        return resultados
    
    def _verificar_servicio(self, servicio: Dict) -> Dict:
        """Verificar un servicio específico"""
        try:
            response = requests.get(servicio['url'], timeout=5)
            return {
                'nombre': servicio['nombre'],
                'url': servicio['url'],
                'activo': response.status_code == 200,
                'status_code': response.status_code,
                'tiempo_respuesta': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'nombre': servicio['nombre'],
                'url': servicio['url'],
                'activo': False,
                'error': str(e)
            }
    
    def _verificar_sistema(self) -> Dict:
        """Verificar estado del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory()
            disco = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memoria_percent': memoria.percent,
                'memoria_disponible_gb': memoria.available / (1024**3),
                'disco_percent': disco.percent,
                'disco_disponible_gb': disco.free / (1024**3)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generar_reporte_estado(self) -> str:
        """Generar reporte de estado"""
        resultados = self.verificar_servicios()
        
        reporte = f"""
REPORTE DE ESTADO - METGO 3D QUILLOTA
Fecha: {resultados['timestamp']}

SERVICIOS:
"""
        
        for servicio in resultados['servicios']:
            estado = "ACTIVO" if servicio['activo'] else "INACTIVO"
            reporte += f"  - {servicio['nombre']}: {estado}\n"
        
        if 'sistema' in resultados and 'error' not in resultados['sistema']:
            reporte += f"""
SISTEMA:
  - CPU: {resultados['sistema']['cpu_percent']:.1f}%
  - Memoria: {resultados['sistema']['memoria_percent']:.1f}%
  - Disco: {resultados['sistema']['disco_percent']:.1f}%
"""
        
        if resultados['alertas']:
            reporte += "\nALERTAS:\n"
            for alerta in resultados['alertas']:
                reporte += f"  - {alerta['mensaje']}\n"
        
        return reporte
    
    def ejecutar_monitoreo_continuo(self):
        """Ejecutar monitoreo continuo"""
        print("Iniciando monitoreo continuo del sistema...")
        
        while True:
            try:
                resultados = self.verificar_servicios()
                
                # Log de estado
                self.logger.info(f"Estado del sistema verificado: {len([s for s in resultados['servicios'] if s['activo']])}/{len(resultados['servicios'])} servicios activos")
                
                # Verificar alertas
                if resultados['alertas']:
                    for alerta in resultados['alertas']:
                        self.logger.warning(f"ALERTA: {alerta['mensaje']}")
                
                # Esperar antes de la siguiente verificación
                time.sleep(self.config['intervalo_verificacion'])
                
            except KeyboardInterrupt:
                print("\nMonitoreo detenido por el usuario")
                break
            except Exception as e:
                self.logger.error(f"Error en monitoreo: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

def main():
    """Función principal"""
    monitoreo = MonitoreoProduccion()
    
    # Generar reporte inicial
    print(monitoreo.generar_reporte_estado())
    
    # Ejecutar monitoreo continuo
    monitoreo.ejecutar_monitoreo_continuo()

if __name__ == "__main__":
    main()
