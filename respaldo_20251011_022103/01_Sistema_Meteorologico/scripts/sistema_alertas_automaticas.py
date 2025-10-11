#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Automáticas METGO 3D
Sistema completo de notificaciones por email y SMS
"""

import smtplib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from pathlib import Path
import requests
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sistema_alertas.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SistemaAlertas:
    """Sistema completo de alertas automáticas"""
    
    def __init__(self, config_path: str = "scripts/config_alertas.json"):
        self.config_path = config_path
        self.config = self._cargar_configuracion()
        self.historial_alertas = []
        self.alertas_enviadas = []
        
        # Crear directorios necesarios
        Path('logs').mkdir(exist_ok=True)
        Path('alertas').mkdir(exist_ok=True)
        Path('templates').mkdir(exist_ok=True)
    
    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Cargar configuración del sistema de alertas"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}")
            return self._configuracion_por_defecto()
    
    def _configuracion_por_defecto(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'email': {
                'habilitado': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'usuario': '',
                'password': '',
                'destinatarios': []
            },
            'sms': {
                'habilitado': False,
                'api_key': '',
                'servicio': 'twilio',
                'destinatarios': []
            },
            'alertas': {
                'calidad_datos_baja': True,
                'errores_criticos': True,
                'temperatura_extrema': True,
                'precipitacion_intensa': True,
                'viento_fuerte': True,
                'humedad_critica': True
            },
            'umbrales': {
                'calidad_minima': 70.0,
                'temperatura_maxima': 35.0,
                'temperatura_minima': -2.0,
                'precipitacion_intensa': 20.0,
                'viento_fuerte': 25.0,
                'humedad_baja': 30.0,
                'humedad_alta': 85.0
            },
            'frecuencia': {
                'max_alertas_por_hora': 5,
                'cooldown_minutos': 30
            }
        }
    
    def procesar_alertas_validacion(self, estado_validacion: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Procesar alertas basadas en estado de validación"""
        alertas_generadas = []
        
        if not estado_validacion:
            return alertas_generadas
        
        # Alerta de calidad de datos baja
        if estado_validacion['puntuacion'] < self.config['umbrales']['calidad_minima']:
            alerta = {
                'tipo': 'calidad_datos_baja',
                'severidad': 'critica',
                'titulo': 'Calidad de Datos Crítica',
                'mensaje': f"La calidad de datos meteorológicos ha bajado a {estado_validacion['puntuacion']:.1f}/100",
                'detalles': {
                    'puntuacion': estado_validacion['puntuacion'],
                    'registros_totales': estado_validacion.get('total_registros', 0),
                    'errores': estado_validacion.get('errores', {}),
                    'timestamp': datetime.now().isoformat()
                }
            }
            alertas_generadas.append(alerta)
        
        # Alerta de muchos errores
        if estado_validacion.get('errores'):
            total_errores = sum(estado_validacion['errores'].values())
            if total_errores > 10:
                alerta = {
                    'tipo': 'errores_criticos',
                    'severidad': 'alta',
                    'titulo': 'Múltiples Errores Detectados',
                    'mensaje': f"Se han detectado {total_errores} errores en los datos meteorológicos",
                    'detalles': {
                        'total_errores': total_errores,
                        'errores_detalle': estado_validacion['errores'],
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        return alertas_generadas
    
    def procesar_alertas_meteorologicas(self, datos_actuales: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Procesar alertas basadas en datos meteorológicos actuales"""
        alertas_generadas = []
        
        # Alerta de temperatura extrema
        if 'temperatura_max' in datos_actuales:
            temp_max = datos_actuales['temperatura_max']
            if temp_max >= self.config['umbrales']['temperatura_maxima']:
                alerta = {
                    'tipo': 'temperatura_extrema',
                    'severidad': 'alta',
                    'titulo': 'Temperatura Extrema Detectada',
                    'mensaje': f"Temperatura máxima de {temp_max:.1f}°C detectada en Quillota",
                    'detalles': {
                        'temperatura_maxima': temp_max,
                        'temperatura_minima': datos_actuales.get('temperatura_min', 'N/A'),
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        if 'temperatura_min' in datos_actuales:
            temp_min = datos_actuales['temperatura_min']
            if temp_min <= self.config['umbrales']['temperatura_minima']:
                alerta = {
                    'tipo': 'helada_detectada',
                    'severidad': 'critica',
                    'titulo': 'Helada Detectada',
                    'mensaje': f"Temperatura mínima de {temp_min:.1f}°C - Riesgo de helada",
                    'detalles': {
                        'temperatura_minima': temp_min,
                        'temperatura_maxima': datos_actuales.get('temperatura_max', 'N/A'),
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        # Alerta de precipitación intensa
        if 'precipitacion' in datos_actuales:
            precipitacion = datos_actuales['precipitacion']
            if precipitacion >= self.config['umbrales']['precipitacion_intensa']:
                alerta = {
                    'tipo': 'precipitacion_intensa',
                    'severidad': 'alta',
                    'titulo': 'Precipitación Intensa',
                    'mensaje': f"Precipitación de {precipitacion:.1f} mm detectada",
                    'detalles': {
                        'precipitacion': precipitacion,
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        # Alerta de viento fuerte
        if 'velocidad_viento' in datos_actuales:
            viento = datos_actuales['velocidad_viento']
            if viento >= self.config['umbrales']['viento_fuerte']:
                alerta = {
                    'tipo': 'viento_fuerte',
                    'severidad': 'media',
                    'titulo': 'Viento Fuerte Detectado',
                    'mensaje': f"Velocidad de viento de {viento:.1f} km/h",
                    'detalles': {
                        'velocidad_viento': viento,
                        'direccion_viento': datos_actuales.get('direccion_viento', 'N/A'),
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        # Alerta de humedad crítica
        if 'humedad_relativa' in datos_actuales:
            humedad = datos_actuales['humedad_relativa']
            if humedad <= self.config['umbrales']['humedad_baja']:
                alerta = {
                    'tipo': 'humedad_baja',
                    'severidad': 'media',
                    'titulo': 'Humedad Muy Baja',
                    'mensaje': f"Humedad relativa de {humedad:.1f}% - Riesgo de sequía",
                    'detalles': {
                        'humedad_relativa': humedad,
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
            elif humedad >= self.config['umbrales']['humedad_alta']:
                alerta = {
                    'tipo': 'humedad_alta',
                    'severidad': 'media',
                    'titulo': 'Humedad Muy Alta',
                    'mensaje': f"Humedad relativa de {humedad:.1f}% - Condiciones húmedas",
                    'detalles': {
                        'humedad_relativa': humedad,
                        'ubicacion': 'Quillota, Valparaíso',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                alertas_generadas.append(alerta)
        
        return alertas_generadas
    
    def enviar_alerta_email(self, alerta: Dict[str, Any]) -> bool:
        """Enviar alerta por email"""
        if not self.config['email']['habilitado']:
            logger.info("Email no habilitado, saltando envío")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['usuario']
            msg['To'] = ', '.join(self.config['email']['destinatarios'])
            msg['Subject'] = f"[METGO 3D] {alerta['titulo']}"
            
            # Crear contenido del email
            contenido = self._generar_contenido_email(alerta)
            msg.attach(MIMEText(contenido, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['usuario'], self.config['email']['password'])
            
            text = msg.as_string()
            server.sendmail(self.config['email']['usuario'], self.config['email']['destinatarios'], text)
            server.quit()
            
            logger.info(f"Email enviado exitosamente: {alerta['titulo']}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def enviar_alerta_sms(self, alerta: Dict[str, Any]) -> bool:
        """Enviar alerta por SMS"""
        if not self.config['sms']['habilitado']:
            logger.info("SMS no habilitado, saltando envío")
            return False
        
        try:
            # Crear mensaje SMS
            mensaje = self._generar_contenido_sms(alerta)
            
            # Enviar SMS (ejemplo con Twilio)
            if self.config['sms']['servicio'] == 'twilio':
                from twilio.rest import Client
                
                client = Client(self.config['sms']['api_key'], self.config['sms']['auth_token'])
                
                for destinatario in self.config['sms']['destinatarios']:
                    message = client.messages.create(
                        body=mensaje,
                        from_=self.config['sms']['numero_origen'],
                        to=destinatario
                    )
                    logger.info(f"SMS enviado a {destinatario}: {message.sid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return False
    
    def _generar_contenido_email(self, alerta: Dict[str, Any]) -> str:
        """Generar contenido HTML para email"""
        severidad_colores = {
            'critica': '#dc3545',
            'alta': '#fd7e14',
            'media': '#ffc107',
            'baja': '#28a745'
        }
        
        color = severidad_colores.get(alerta['severidad'], '#6c757d')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🌤️ METGO 3D - Sistema Meteorológico</h2>
                <h3>{alerta['titulo']}</h3>
            </div>
            
            <div class="content">
                <p><strong>Mensaje:</strong> {alerta['mensaje']}</p>
                <p><strong>Severidad:</strong> {alerta['severidad'].upper()}</p>
                <p><strong>Ubicación:</strong> Quillota, Valparaíso, Chile</p>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
            
            <div class="details">
                <h4>Detalles Técnicos:</h4>
                <ul>
        """
        
        for key, value in alerta['detalles'].items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        
        html += """
                </ul>
            </div>
            
            <div class="footer">
                <p>Este es un mensaje automático del Sistema Meteorológico METGO 3D</p>
                <p>Para más información, visite el dashboard del sistema</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generar_contenido_sms(self, alerta: Dict[str, Any]) -> str:
        """Generar contenido para SMS"""
        emoji_severidad = {
            'critica': '🚨',
            'alta': '⚠️',
            'media': '📢',
            'baja': 'ℹ️'
        }
        
        emoji = emoji_severidad.get(alerta['severidad'], '📱')
        
        mensaje = f"{emoji} METGO 3D - {alerta['titulo']}\n"
        mensaje += f"{alerta['mensaje']}\n"
        mensaje += f"Quillota, Valparaíso\n"
        mensaje += f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return mensaje
    
    def procesar_y_enviar_alertas(self, estado_validacion: Dict[str, Any], datos_actuales: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar y enviar todas las alertas"""
        resultado = {
            'alertas_generadas': 0,
            'emails_enviados': 0,
            'sms_enviados': 0,
            'errores': []
        }
        
        try:
            # Generar alertas
            alertas_validacion = self.procesar_alertas_validacion(estado_validacion)
            alertas_meteorologicas = self.procesar_alertas_meteorologicas(datos_actuales)
            
            todas_alertas = alertas_validacion + alertas_meteorologicas
            resultado['alertas_generadas'] = len(todas_alertas)
            
            # Verificar límites de frecuencia
            alertas_a_enviar = self._filtrar_alertas_por_frecuencia(todas_alertas)
            
            # Enviar alertas
            for alerta in alertas_a_enviar:
                # Enviar por email
                if self.enviar_alerta_email(alerta):
                    resultado['emails_enviados'] += 1
                
                # Enviar por SMS
                if self.enviar_alerta_sms(alerta):
                    resultado['sms_enviados'] += 1
                
                # Guardar en historial
                self._guardar_alerta_en_historial(alerta)
            
            logger.info(f"Procesadas {resultado['alertas_generadas']} alertas, enviados {resultado['emails_enviados']} emails, {resultado['sms_enviados']} SMS")
            
        except Exception as e:
            logger.error(f"Error procesando alertas: {e}")
            resultado['errores'].append(str(e))
        
        return resultado
    
    def _filtrar_alertas_por_frecuencia(self, alertas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtrar alertas según límites de frecuencia"""
        ahora = datetime.now()
        limite_hora = ahora - timedelta(hours=1)
        limite_cooldown = ahora - timedelta(minutes=self.config['frecuencia']['cooldown_minutos'])
        
        # Contar alertas enviadas en la última hora
        alertas_recientes = [
            a for a in self.alertas_enviadas 
            if datetime.fromisoformat(a['timestamp']) > limite_hora
        ]
        
        if len(alertas_recientes) >= self.config['frecuencia']['max_alertas_por_hora']:
            logger.warning(f"Límite de alertas por hora alcanzado ({len(alertas_recientes)})")
            return []
        
        # Filtrar por cooldown
        alertas_filtradas = []
        for alerta in alertas:
            tipo_alerta = alerta['tipo']
            ultima_alerta_tipo = None
            
            for a in reversed(self.alertas_enviadas):
                if a['tipo'] == tipo_alerta:
                    ultima_alerta_tipo = datetime.fromisoformat(a['timestamp'])
                    break
            
            if not ultima_alerta_tipo or ultima_alerta_tipo < limite_cooldown:
                alertas_filtradas.append(alerta)
            else:
                logger.info(f"Alerta {tipo_alerta} en cooldown")
        
        return alertas_filtradas
    
    def _guardar_alerta_en_historial(self, alerta: Dict[str, Any]):
        """Guardar alerta en historial"""
        alerta_completa = {
            'timestamp': datetime.now().isoformat(),
            'tipo': alerta['tipo'],
            'severidad': alerta['severidad'],
            'titulo': alerta['titulo'],
            'mensaje': alerta['mensaje'],
            'detalles': alerta['detalles']
        }
        
        self.alertas_enviadas.append(alerta_completa)
        
        # Guardar en archivo
        archivo_historial = f"alertas/historial_alertas_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            historial_existente = []
            if os.path.exists(archivo_historial):
                with open(archivo_historial, 'r', encoding='utf-8') as f:
                    historial_existente = json.load(f)
            
            historial_existente.append(alerta_completa)
            
            with open(archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(historial_existente, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
    
    def obtener_estadisticas_alertas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de alertas"""
        ahora = datetime.now()
        ultimas_24h = ahora - timedelta(hours=24)
        ultima_semana = ahora - timedelta(days=7)
        
        alertas_24h = [
            a for a in self.alertas_enviadas 
            if datetime.fromisoformat(a['timestamp']) > ultimas_24h
        ]
        
        alertas_semana = [
            a for a in self.alertas_enviadas 
            if datetime.fromisoformat(a['timestamp']) > ultima_semana
        ]
        
        # Contar por tipo
        tipos_24h = {}
        for alerta in alertas_24h:
            tipo = alerta['tipo']
            tipos_24h[tipo] = tipos_24h.get(tipo, 0) + 1
        
        return {
            'total_alertas_24h': len(alertas_24h),
            'total_alertas_semana': len(alertas_semana),
            'tipos_alertas_24h': tipos_24h,
            'configuracion': {
                'email_habilitado': self.config['email']['habilitado'],
                'sms_habilitado': self.config['sms']['habilitado'],
                'destinatarios_email': len(self.config['email']['destinatarios']),
                'destinatarios_sms': len(self.config['sms']['destinatarios'])
            }
        }

def main():
    """Función principal para probar el sistema de alertas"""
    print("=" * 70)
    print("SISTEMA DE ALERTAS AUTOMATICAS METGO 3D")
    print("=" * 70)
    
    sistema = SistemaAlertas()
    
    # Datos de prueba
    estado_validacion_prueba = {
        'puntuacion': 45.0,
        'total_registros': 100,
        'errores': {'temperatura_fuera_rango': 15, 'humedad_invalida': 8}
    }
    
    datos_actuales_prueba = {
        'temperatura_max': 38.5,
        'temperatura_min': 15.2,
        'precipitacion': 25.0,
        'velocidad_viento': 30.0,
        'humedad_relativa': 25.0
    }
    
    print("Procesando alertas de prueba...")
    resultado = sistema.procesar_y_enviar_alertas(estado_validacion_prueba, datos_actuales_prueba)
    
    print(f"Alertas generadas: {resultado['alertas_generadas']}")
    print(f"Emails enviados: {resultado['emails_enviados']}")
    print(f"SMS enviados: {resultado['sms_enviados']}")
    
    if resultado['errores']:
        print(f"Errores: {resultado['errores']}")
    
    # Mostrar estadísticas
    stats = sistema.obtener_estadisticas_alertas()
    print(f"\nEstadísticas:")
    print(f"Alertas últimas 24h: {stats['total_alertas_24h']}")
    print(f"Email habilitado: {stats['configuracion']['email_habilitado']}")
    print(f"SMS habilitado: {stats['configuracion']['sms_habilitado']}")

if __name__ == "__main__":
    main()

