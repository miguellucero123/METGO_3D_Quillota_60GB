"""
SISTEMA DE REPORTES AUTOMÁTICOS AVANZADO - METGO 3D QUILLOTA
Sistema completo de generación automática de reportes meteorológicos y agrícolas
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import base64
from io import BytesIO

class SistemaReportesAutomaticosAvanzado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reportes_dir = "reportes_automaticos"
        self.templates_dir = "templates_reportes"
        self._crear_directorios()
        self._inicializar_templates()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        for directorio in [self.reportes_dir, self.templates_dir]:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_templates(self):
        """Inicializar templates de reportes"""
        # Template HTML básico
        template_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2E8B57; color: white; padding: 20px; text-align: center; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f0f0f0; }
        .alert-critical { background-color: #ffebee; border-left: 5px solid #f44336; }
        .alert-warning { background-color: #fff3e0; border-left: 5px solid #ff9800; }
        .alert-normal { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ titulo }}</h1>
        <p>Generado el {{ fecha_generacion }}</p>
    </div>
    
    <div class="section">
        <h2>📊 Resumen Ejecutivo</h2>
        {{ resumen_ejecutivo }}
    </div>
    
    <div class="section">
        <h2>🌡️ Datos Meteorológicos</h2>
        {{ datos_meteorologicos }}
    </div>
    
    <div class="section">
        <h2>🚨 Alertas y Recomendaciones</h2>
        {{ alertas_recomendaciones }}
    </div>
    
    <div class="section">
        <h2>📈 Análisis Estadístico</h2>
        {{ analisis_estadistico }}
    </div>
    
    <div class="section">
        <h2>🤖 Predicciones ML</h2>
        {{ predicciones_ml }}
    </div>
    
    <footer style="margin-top: 50px; text-align: center; color: #666;">
        <p>Sistema METGO 3D Quillota - Reporte Automático</p>
    </footer>
</body>
</html>
        """
        
        with open(os.path.join(self.templates_dir, "reporte_completo.html"), 'w', encoding='utf-8') as f:
            f.write(template_html)
    
    def generar_reporte_diario(self, datos_estaciones: Dict, 
                             predicciones_ml: Dict = None,
                             alertas: Dict = None) -> Dict:
        """Generar reporte diario completo"""
        try:
            fecha = datetime.now()
            nombre_archivo = f"reporte_diario_{fecha.strftime('%Y%m%d')}"
            
            # Recopilar datos
            datos_reporte = {
                'fecha_generacion': fecha.isoformat(),
                'titulo': f'Reporte Diario METGO 3D - {fecha.strftime("%d/%m/%Y")}',
                'datos_estaciones': datos_estaciones,
                'predicciones_ml': predicciones_ml or {},
                'alertas': alertas or {},
                'estadisticas': self._calcular_estadisticas_generales(datos_estaciones),
                'resumen_ejecutivo': self._generar_resumen_ejecutivo(datos_estaciones, alertas)
            }
            
            # Generar reportes en diferentes formatos
            reportes_generados = {}
            
            # Reporte HTML
            html_path = self._generar_reporte_html(datos_reporte, nombre_archivo)
            reportes_generados['html'] = html_path
            
            # Reporte JSON
            json_path = self._generar_reporte_json(datos_reporte, nombre_archivo)
            reportes_generados['json'] = json_path
            
            # Reporte CSV
            csv_path = self._generar_reporte_csv(datos_estaciones, nombre_archivo)
            reportes_generados['csv'] = csv_path
            
            # Reporte PDF (simulado)
            pdf_path = self._generar_reporte_pdf_simulado(datos_reporte, nombre_archivo)
            reportes_generados['pdf'] = pdf_path
            
            # Guardar metadatos
            self._guardar_metadatos_reporte(nombre_archivo, reportes_generados, datos_reporte)
            
            self.logger.info(f"Reporte diario generado: {nombre_archivo}")
            return {
                'exito': True,
                'archivos': reportes_generados,
                'metadatos': datos_reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte diario: {e}")
            return {'exito': False, 'error': str(e)}
    
    def _calcular_estadisticas_generales(self, datos_estaciones: Dict) -> Dict:
        """Calcular estadísticas generales"""
        try:
            estadisticas = {
                'total_estaciones': len(datos_estaciones),
                'temperaturas': [],
                'humedades': [],
                'vientos': [],
                'precipitaciones': []
            }
            
            for estacion, datos in datos_estaciones.items():
                # Temperatura
                temp = datos.get('temperatura_actual', datos.get('temperatura', None))
                if temp is not None:
                    estadisticas['temperaturas'].append(temp)
                
                # Humedad
                humedad = datos.get('humedad_relativa', datos.get('humedad', None))
                if humedad is not None:
                    estadisticas['humedades'].append(humedad)
                
                # Viento
                viento = datos.get('velocidad_viento', datos.get('viento', None))
                if viento is not None:
                    estadisticas['vientos'].append(viento)
                
                # Precipitación
                precip = datos.get('precipitacion', datos.get('lluvia', None))
                if precip is not None:
                    estadisticas['precipitaciones'].append(precip)
            
            # Calcular estadísticas descriptivas
            for variable in ['temperaturas', 'humedades', 'vientos', 'precipitaciones']:
                if estadisticas[variable]:
                    valores = estadisticas[variable]
                    estadisticas[f'{variable}_stats'] = {
                        'min': min(valores),
                        'max': max(valores),
                        'promedio': np.mean(valores),
                        'mediana': np.median(valores),
                        'desviacion': np.std(valores)
                    }
            
            return estadisticas
            
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas: {e}")
            return {}
    
    def _generar_resumen_ejecutivo(self, datos_estaciones: Dict, alertas: Dict) -> str:
        """Generar resumen ejecutivo"""
        try:
            total_estaciones = len(datos_estaciones)
            alertas_criticas = 0
            alertas_advertencia = 0
            
            if alertas:
                alertas_criticas = alertas.get('resumen_alertas', {}).get('criticas', 0)
                alertas_advertencia = alertas.get('resumen_alertas', {}).get('advertencia', 0)
            
            # Calcular temperatura promedio
            temperaturas = []
            for datos in datos_estaciones.values():
                temp = datos.get('temperatura_actual', datos.get('temperatura', None))
                if temp is not None:
                    temperaturas.append(temp)
            
            temp_promedio = np.mean(temperaturas) if temperaturas else 0
            
            resumen = f"""
            <p><strong>Monitoreo de {total_estaciones} estaciones meteorológicas</strong> en el Valle de Quillota.</p>
            <p><strong>Temperatura promedio:</strong> {temp_promedio:.1f}°C</p>
            <p><strong>Alertas críticas:</strong> {alertas_criticas}</p>
            <p><strong>Alertas de advertencia:</strong> {alertas_advertencia}</p>
            <p><strong>Estado general:</strong> {'🚨 CRÍTICO' if alertas_criticas > 0 else '⚠️ ADVERTENCIA' if alertas_advertencia > 0 else '✅ NORMAL'}</p>
            """
            
            return resumen
            
        except Exception as e:
            self.logger.error(f"Error generando resumen ejecutivo: {e}")
            return "<p>Error generando resumen ejecutivo</p>"
    
    def _generar_reporte_html(self, datos_reporte: Dict, nombre_archivo: str) -> str:
        """Generar reporte en formato HTML"""
        try:
            # Cargar template
            with open(os.path.join(self.templates_dir, "reporte_completo.html"), 'r', encoding='utf-8') as f:
                template_str = f.read()
            
            template = Template(template_str)
            
            # Preparar datos para el template
            datos_template = {
                'titulo': datos_reporte['titulo'],
                'fecha_generacion': datetime.fromisoformat(datos_reporte['fecha_generacion']).strftime("%d/%m/%Y %H:%M:%S"),
                'resumen_ejecutivo': datos_reporte['resumen_ejecutivo'],
                'datos_meteorologicos': self._generar_tabla_datos_meteorologicos(datos_reporte['datos_estaciones']),
                'alertas_recomendaciones': self._generar_seccion_alertas(datos_reporte['alertas']),
                'analisis_estadistico': self._generar_analisis_estadistico(datos_reporte['estadisticas']),
                'predicciones_ml': self._generar_seccion_predicciones(datos_reporte['predicciones_ml'])
            }
            
            # Renderizar template
            html_content = template.render(**datos_template)
            
            # Guardar archivo
            archivo_path = os.path.join(self.reportes_dir, f"{nombre_archivo}.html")
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return archivo_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte HTML: {e}")
            return ""
    
    def _generar_tabla_datos_meteorologicos(self, datos_estaciones: Dict) -> str:
        """Generar tabla HTML de datos meteorológicos"""
        try:
            html = "<table><tr><th>Estación</th><th>Temperatura (°C)</th><th>Humedad (%)</th><th>Viento (km/h)</th><th>Precipitación (mm)</th></tr>"
            
            for estacion, datos in datos_estaciones.items():
                temp = datos.get('temperatura_actual', datos.get('temperatura', 'N/A'))
                humedad = datos.get('humedad_relativa', datos.get('humedad', 'N/A'))
                viento = datos.get('velocidad_viento', datos.get('viento', 'N/A'))
                precip = datos.get('precipitacion', datos.get('lluvia', 'N/A'))
                
                html += f"<tr><td>{estacion.replace('_', ' ')}</td><td>{temp}</td><td>{humedad}</td><td>{viento}</td><td>{precip}</td></tr>"
            
            html += "</table>"
            return html
            
        except Exception as e:
            self.logger.error(f"Error generando tabla datos meteorológicos: {e}")
            return "<p>Error generando tabla de datos meteorológicos</p>"
    
    def _generar_seccion_alertas(self, alertas: Dict) -> str:
        """Generar sección de alertas"""
        try:
            if not alertas:
                return "<p>No hay alertas activas</p>"
            
            html = ""
            resumen = alertas.get('resumen_alertas', {})
            
            html += f"<div class='metric'>Alertas Críticas: {resumen.get('criticas', 0)}</div>"
            html += f"<div class='metric'>Alertas Advertencia: {resumen.get('advertencia', 0)}</div>"
            html += f"<div class='metric'>Estaciones Normales: {resumen.get('normales', 0)}</div>"
            
            # Mostrar estaciones críticas
            estaciones_criticas = alertas.get('estaciones_criticas', [])
            if estaciones_criticas:
                html += "<h3>🚨 Estaciones Críticas</h3><ul>"
                for estacion in estaciones_criticas:
                    html += f"<li>{estacion.get('nombre', 'Unknown')}</li>"
                html += "</ul>"
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error generando sección alertas: {e}")
            return "<p>Error generando sección de alertas</p>"
    
    def _generar_analisis_estadistico(self, estadisticas: Dict) -> str:
        """Generar análisis estadístico"""
        try:
            html = "<h3>📊 Estadísticas Generales</h3>"
            
            # Estadísticas de temperatura
            if 'temperaturas_stats' in estadisticas:
                stats = estadisticas['temperaturas_stats']
                html += f"""
                <div class='section'>
                    <h4>🌡️ Temperatura</h4>
                    <p>Mínima: {stats['min']:.1f}°C | Máxima: {stats['max']:.1f}°C | Promedio: {stats['promedio']:.1f}°C</p>
                </div>
                """
            
            # Estadísticas de humedad
            if 'humedades_stats' in estadisticas:
                stats = estadisticas['humedades_stats']
                html += f"""
                <div class='section'>
                    <h4>💧 Humedad Relativa</h4>
                    <p>Mínima: {stats['min']:.1f}% | Máxima: {stats['max']:.1f}% | Promedio: {stats['promedio']:.1f}%</p>
                </div>
                """
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error generando análisis estadístico: {e}")
            return "<p>Error generando análisis estadístico</p>"
    
    def _generar_seccion_predicciones(self, predicciones_ml: Dict) -> str:
        """Generar sección de predicciones ML"""
        try:
            if not predicciones_ml:
                return "<p>No hay predicciones ML disponibles</p>"
            
            html = "<h3>🤖 Predicciones de Machine Learning</h3>"
            
            for variable, pred in predicciones_ml.items():
                html += f"""
                <div class='metric'>
                    <strong>{variable.replace('_', ' ').title()}:</strong> 
                    {pred.get('valor_predicho', 'N/A')} 
                    (Confianza: {pred.get('confianza', 0):.1%})
                </div>
                """
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error generando sección predicciones: {e}")
            return "<p>Error generando sección de predicciones</p>"
    
    def _generar_reporte_json(self, datos_reporte: Dict, nombre_archivo: str) -> str:
        """Generar reporte en formato JSON"""
        try:
            archivo_path = os.path.join(self.reportes_dir, f"{nombre_archivo}.json")
            with open(archivo_path, 'w', encoding='utf-8') as f:
                json.dump(datos_reporte, f, indent=2, ensure_ascii=False)
            
            return archivo_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte JSON: {e}")
            return ""
    
    def _generar_reporte_csv(self, datos_estaciones: Dict, nombre_archivo: str) -> str:
        """Generar reporte en formato CSV"""
        try:
            # Preparar datos para CSV
            datos_csv = []
            for estacion, datos in datos_estaciones.items():
                fila = {
                    'estacion': estacion,
                    'temperatura': datos.get('temperatura_actual', datos.get('temperatura', '')),
                    'humedad': datos.get('humedad_relativa', datos.get('humedad', '')),
                    'viento': datos.get('velocidad_viento', datos.get('viento', '')),
                    'precipitacion': datos.get('precipitacion', datos.get('lluvia', '')),
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                datos_csv.append(fila)
            
            # Crear DataFrame y guardar
            df = pd.DataFrame(datos_csv)
            archivo_path = os.path.join(self.reportes_dir, f"{nombre_archivo}.csv")
            df.to_csv(archivo_path, index=False, encoding='utf-8')
            
            return archivo_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte CSV: {e}")
            return ""
    
    def _generar_reporte_pdf_simulado(self, datos_reporte: Dict, nombre_archivo: str) -> str:
        """Generar reporte PDF simulado (en realidad HTML con extensión PDF)"""
        try:
            # Para simplicidad, generamos un HTML que simula un PDF
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{datos_reporte['titulo']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .section {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{datos_reporte['titulo']}</h1>
                    <p>Generado: {datetime.fromisoformat(datos_reporte['fecha_generacion']).strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                <div class="section">
                    <h2>Resumen</h2>
                    {datos_reporte['resumen_ejecutivo']}
                </div>
                <div class="section">
                    <h2>Datos Meteorológicos</h2>
                    {self._generar_tabla_datos_meteorologicos(datos_reporte['datos_estaciones'])}
                </div>
            </body>
            </html>
            """
            
            archivo_path = os.path.join(self.reportes_dir, f"{nombre_archivo}.pdf")
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return archivo_path
            
        except Exception as e:
            self.logger.error(f"Error generando reporte PDF simulado: {e}")
            return ""
    
    def _guardar_metadatos_reporte(self, nombre_archivo: str, archivos: Dict, metadatos: Dict):
        """Guardar metadatos del reporte"""
        try:
            metadatos_completos = {
                'nombre_archivo': nombre_archivo,
                'fecha_generacion': datetime.now().isoformat(),
                'archivos_generados': archivos,
                'metadatos': metadatos,
                'estado': 'completado'
            }
            
            archivo_metadatos = os.path.join(self.reportes_dir, f"{nombre_archivo}_metadatos.json")
            with open(archivo_metadatos, 'w', encoding='utf-8') as f:
                json.dump(metadatos_completos, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error guardando metadatos: {e}")
    
    def generar_reporte_semanal(self, datos_historicos: List[Dict]) -> Dict:
        """Generar reporte semanal"""
        try:
            fecha = datetime.now()
            nombre_archivo = f"reporte_semanal_{fecha.strftime('%Y%m%d')}"
            
            # Procesar datos históricos
            df = pd.DataFrame(datos_historicos)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Calcular estadísticas semanales
            estadisticas_semanales = {
                'temperatura_promedio': df['temperatura'].mean() if 'temperatura' in df.columns else 0,
                'temperatura_minima': df['temperatura'].min() if 'temperatura' in df.columns else 0,
                'temperatura_maxima': df['temperatura'].max() if 'temperatura' in df.columns else 0,
                'precipitacion_total': df['precipitacion'].sum() if 'precipitacion' in df.columns else 0,
                'dias_con_lluvia': (df['precipitacion'] > 0).sum() if 'precipitacion' in df.columns else 0
            }
            
            # Generar reporte
            datos_reporte = {
                'fecha_generacion': fecha.isoformat(),
                'titulo': f'Reporte Semanal METGO 3D - Semana del {fecha.strftime("%d/%m/%Y")}',
                'tipo': 'semanal',
                'estadisticas_semanales': estadisticas_semanales,
                'datos_historicos': datos_historicos
            }
            
            # Generar archivos
            archivos = {}
            archivos['json'] = self._generar_reporte_json(datos_reporte, nombre_archivo)
            
            self.logger.info(f"Reporte semanal generado: {nombre_archivo}")
            return {
                'exito': True,
                'archivos': archivos,
                'metadatos': datos_reporte
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte semanal: {e}")
            return {'exito': False, 'error': str(e)}
    
    def listar_reportes_generados(self) -> List[Dict]:
        """Listar reportes generados"""
        try:
            reportes = []
            
            if not os.path.exists(self.reportes_dir):
                return reportes
            
            for archivo in os.listdir(self.reportes_dir):
                if archivo.endswith('_metadatos.json'):
                    try:
                        with open(os.path.join(self.reportes_dir, archivo), 'r', encoding='utf-8') as f:
                            metadatos = json.load(f)
                            reportes.append(metadatos)
                    except Exception as e:
                        self.logger.error(f"Error leyendo metadatos {archivo}: {e}")
            
            # Ordenar por fecha de generación
            reportes.sort(key=lambda x: x.get('fecha_generacion', ''), reverse=True)
            
            return reportes
            
        except Exception as e:
            self.logger.error(f"Error listando reportes: {e}")
            return []

def main():
    """Función principal para pruebas"""
    logging.basicConfig(level=logging.INFO)
    
    sistema = SistemaReportesAutomaticosAvanzado()
    
    # Datos de prueba
    datos_prueba = {
        "Quillota_Centro": {
            "temperatura_actual": 15.5,
            "humedad_relativa": 65.0,
            "velocidad_viento": 8.2,
            "precipitacion": 0.0
        },
        "La_Cruz": {
            "temperatura_actual": 14.2,
            "humedad_relativa": 70.0,
            "velocidad_viento": 12.5,
            "precipitacion": 1.2
        }
    }
    
    alertas_prueba = {
        'resumen_alertas': {'criticas': 0, 'advertencia': 1, 'normales': 1},
        'estaciones_criticas': [],
        'estaciones_advertencia': ['La_Cruz'],
        'estaciones_normales': ['Quillota_Centro']
    }
    
    print("Probando sistema de reportes automáticos...")
    
    # Generar reporte diario
    resultado = sistema.generar_reporte_diario(datos_prueba, alertas=alertas_prueba)
    
    if resultado['exito']:
        print(f"Reporte generado exitosamente: {resultado['archivos']}")
    else:
        print(f"Error generando reporte: {resultado['error']}")

if __name__ == "__main__":
    main()
