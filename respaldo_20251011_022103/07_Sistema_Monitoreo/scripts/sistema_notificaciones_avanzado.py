"""
SISTEMA DE NOTIFICACIONES AVANZADO - METGO 3D QUILLOTA
Sistema completo de notificaciones: WhatsApp, Email, SMS
"""

import requests
import json
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

class SistemaNotificacionesAvanzado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._cargar_configuracion()
        self.base_datos = "notificaciones_metgo.db"
        self._inicializar_base_datos()
        
    def _cargar_configuracion(self) -> Dict:
        """Cargar configuración de notificaciones"""
        try:
            with open('configuracion_notificaciones_avanzada.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuración por defecto
            config_default = {
                "whatsapp": {
                    "twilio_account_sid": "YOUR_TWILIO_ACCOUNT_SID",
                    "twilio_auth_token": "YOUR_TWILIO_AUTH_TOKEN",
                    "twilio_whatsapp_number": "whatsapp:+14155238886",
                    "activa": False
                },
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email_usuario": "your_email@gmail.com",
                    "email_password": "your_app_password",
                    "activa": False
                },
                "sms": {
                    "twilio_account_sid": "YOUR_TWILIO_ACCOUNT_SID",
                    "twilio_auth_token": "YOUR_TWILIO_AUTH_TOKEN",
                    "twilio_phone_number": "+1234567890",
                    "activa": False
                },
                "alertas": {
                    "helada_temperatura_critica": 2.0,
                    "helada_temperatura_advertencia": 5.0,
                    "viento_fuerte": 50.0,
                    "alta_humedad": 90.0,
                    "precipitacion_intensa": 10.0
                },
                "agricultores": {
                    "default": {
                        "nombre": "Agricultor del Valle de Quillota",
                        "telefono": "+56912345678",
                        "email": "agricultor@example.com",
                        "cultivos": ["paltos", "citricos", "verduras"],
                        "notificaciones": {
                            "whatsapp": True,
                            "email": True,
                            "sms": False
                        }
                    }
                }
            }
            
            # Guardar configuración por defecto
            with open('configuracion_notificaciones_avanzada.json', 'w', encoding='utf-8') as f:
                json.dump(config_default, f, indent=2, ensure_ascii=False)
            
            return config_default
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para notificaciones"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de notificaciones enviadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notificaciones_enviadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_alerta TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    estacion TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    destinatario TEXT NOT NULL,
                    metodo_envio TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    respuesta TEXT
                )
            ''')
            
            # Tabla de agricultores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agricultores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    cultivos TEXT,
                    notificaciones_whatsapp BOOLEAN DEFAULT 1,
                    notificaciones_email BOOLEAN DEFAULT 1,
                    notificaciones_sms BOOLEAN DEFAULT 0,
                    activo BOOLEAN DEFAULT 1,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas críticas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_criticas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_alerta TEXT NOT NULL,
                    estacion TEXT NOT NULL,
                    valor_medido REAL NOT NULL,
                    umbral REAL NOT NULL,
                    mensaje TEXT NOT NULL,
                    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notificaciones_enviadas INTEGER DEFAULT 0,
                    resuelta BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Base de datos de notificaciones inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def enviar_whatsapp(self, telefono: str, mensaje: str) -> bool:
        """Enviar mensaje por WhatsApp usando Twilio"""
        try:
            if not self.config["whatsapp"]["activa"]:
                self.logger.info("WhatsApp no está activado en la configuración")
                return False
            
            account_sid = self.config["whatsapp"]["twilio_account_sid"]
            auth_token = self.config["whatsapp"]["twilio_auth_token"]
            from_number = self.config["whatsapp"]["twilio_whatsapp_number"]
            
            if account_sid == "YOUR_TWILIO_ACCOUNT_SID":
                self.logger.warning("Configuración de Twilio no establecida")
                return False
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            data = {
                'From': from_number,
                'To': f'whatsapp:{telefono}',
                'Body': mensaje
            }
            
            response = requests.post(url, auth=(account_sid, auth_token), data=data)
            
            if response.status_code == 201:
                self.logger.info(f"WhatsApp enviado exitosamente a {telefono}")
                return True
            else:
                self.logger.error(f"Error enviando WhatsApp: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando WhatsApp: {e}")
            return False
    
    def enviar_email(self, destinatario: str, asunto: str, mensaje: str) -> bool:
        """Enviar email usando SMTP"""
        try:
            if not self.config["email"]["activa"]:
                self.logger.info("Email no está activado en la configuración")
                return False
            
            smtp_server = self.config["email"]["smtp_server"]
            smtp_port = self.config["email"]["smtp_port"]
            email_usuario = self.config["email"]["email_usuario"]
            email_password = self.config["email"]["email_password"]
            
            if email_usuario == "your_email@gmail.com":
                self.logger.warning("Configuración de email no establecida")
                return False
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = email_usuario
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'html', 'utf-8'))
            
            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_usuario, email_password)
            text = msg.as_string()
            server.sendmail(email_usuario, destinatario, text)
            server.quit()
            
            self.logger.info(f"Email enviado exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return False
    
    def enviar_sms(self, telefono: str, mensaje: str) -> bool:
        """Enviar SMS usando Twilio"""
        try:
            if not self.config["sms"]["activa"]:
                self.logger.info("SMS no está activado en la configuración")
                return False
            
            account_sid = self.config["sms"]["twilio_account_sid"]
            auth_token = self.config["sms"]["twilio_auth_token"]
            from_number = self.config["sms"]["twilio_phone_number"]
            
            if account_sid == "YOUR_TWILIO_ACCOUNT_SID":
                self.logger.warning("Configuración de Twilio para SMS no establecida")
                return False
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            data = {
                'From': from_number,
                'To': telefono,
                'Body': mensaje
            }
            
            response = requests.post(url, auth=(account_sid, auth_token), data=data)
            
            if response.status_code == 201:
                self.logger.info(f"SMS enviado exitosamente a {telefono}")
                return True
            else:
                self.logger.error(f"Error enviando SMS: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando SMS: {e}")
            return False
    
    def procesar_alertas_meteorologicas(self, datos_meteorologicos: Dict) -> List[Dict]:
        """Procesar datos meteorológicos y generar alertas"""
        alertas_generadas = []
        
        try:
            for estacion, datos in datos_meteorologicos.items():
                temperatura = datos.get('temperatura_actual')
                humedad = datos.get('humedad_relativa')
                viento = datos.get('velocidad_viento')
                precipitacion = datos.get('precipitacion')
                
                # Alerta de helada crítica
                if temperatura and temperatura <= self.config["alertas"]["helada_temperatura_critica"]:
                    alerta = {
                        "tipo": "helada_critica",
                        "nivel": "critico",
                        "estacion": estacion,
                        "valor": temperatura,
                        "umbral": self.config["alertas"]["helada_temperatura_critica"],
                        "mensaje": f"[ALERTA CRITICA] ALERTA CRÍTICA DE HELADA\n\n"
                                 f"Estación: {estacion.replace('_', ' ').title()}\n"
                                 f"Temperatura: {temperatura:.1f}°C\n"
                                 f"⚠️ RIESGO CRÍTICO DE HELADA EN CULTIVOS\n\n"
                                 f"ACCIONES INMEDIATAS:\n"
                                 f"• Activar sistemas de riego por aspersión\n"
                                 f"• Cubrir cultivos sensibles\n"
                                 f"• Monitorear continuamente\n\n"
                                 f"METGO 3D - Sistema de Alertas Agrícolas"
                    }
                    alertas_generadas.append(alerta)
                
                # Alerta de helada advertencia
                elif temperatura and temperatura <= self.config["alertas"]["helada_temperatura_advertencia"]:
                    alerta = {
                        "tipo": "helada_advertencia",
                        "nivel": "advertencia",
                        "estacion": estacion,
                        "valor": temperatura,
                        "umbral": self.config["alertas"]["helada_temperatura_advertencia"],
                        "mensaje": f"[ADVERTENCIA] ADVERTENCIA DE HELADA\n\n"
                                 f"Estación: {estacion.replace('_', ' ').title()}\n"
                                 f"Temperatura: {temperatura:.1f}°C\n"
                                 f"🌡️ Temperatura baja - Monitorear cultivos\n\n"
                                 f"RECOMENDACIONES:\n"
                                 f"• Preparar sistemas de protección\n"
                                 f"• Monitorear cada hora\n"
                                 f"• Considerar riego preventivo\n\n"
                                 f"METGO 3D - Sistema de Alertas Agrícolas"
                    }
                    alertas_generadas.append(alerta)
                
                # Alerta de viento fuerte
                if viento and viento >= self.config["alertas"]["viento_fuerte"]:
                    alerta = {
                        "tipo": "viento_fuerte",
                        "nivel": "advertencia",
                        "estacion": estacion,
                        "valor": viento,
                        "umbral": self.config["alertas"]["viento_fuerte"],
                        "mensaje": f"[VIENTO] ADVERTENCIA DE VIENTO FUERTE\n\n"
                                 f"Estación: {estacion.replace('_', ' ').title()}\n"
                                 f"Velocidad del viento: {viento:.1f} km/h\n"
                                 f"⚠️ Posibles daños en cultivos\n\n"
                                 f"RECOMENDACIONES:\n"
                                 f"• Proteger cultivos sensibles\n"
                                 f"• Revisar estructuras de soporte\n"
                                 f"• Evitar aplicaciones foliares\n\n"
                                 f"METGO 3D - Sistema de Alertas Agrícolas"
                    }
                    alertas_generadas.append(alerta)
                
                # Alerta de alta humedad
                if humedad and humedad >= self.config["alertas"]["alta_humedad"]:
                    alerta = {
                        "tipo": "alta_humedad",
                        "nivel": "advertencia",
                        "estacion": estacion,
                        "valor": humedad,
                        "umbral": self.config["alertas"]["alta_humedad"],
                        "mensaje": f"[HUMEDAD] ADVERTENCIA DE ALTA HUMEDAD\n\n"
                                 f"Estación: {estacion.replace('_', ' ').title()}\n"
                                 f"Humedad relativa: {humedad:.1f}%\n"
                                 f"⚠️ Riesgo de enfermedades fúngicas\n\n"
                                 f"RECOMENDACIONES:\n"
                                 f"• Aplicar fungicidas preventivos\n"
                                 f"• Mejorar ventilación\n"
                                 f"• Monitorear síntomas\n\n"
                                 f"METGO 3D - Sistema de Alertas Agrícolas"
                    }
                    alertas_generadas.append(alerta)
                
                # Alerta de precipitación intensa
                if precipitacion and precipitacion >= self.config["alertas"]["precipitacion_intensa"]:
                    alerta = {
                        "tipo": "precipitacion_intensa",
                        "nivel": "advertencia",
                        "estacion": estacion,
                        "valor": precipitacion,
                        "umbral": self.config["alertas"]["precipitacion_intensa"],
                        "mensaje": f"[LLUVIA] ADVERTENCIA DE PRECIPITACIÓN INTENSA\n\n"
                                 f"Estación: {estacion.replace('_', ' ').title()}\n"
                                 f"Precipitación: {precipitacion:.1f} mm/h\n"
                                 f"⚠️ Riesgo de encharcamiento y erosión\n\n"
                                 f"RECOMENDACIONES:\n"
                                 f"• Verificar drenajes\n"
                                 f"• Proteger cultivos sensibles\n"
                                 f"• Monitorear suelos\n\n"
                                 f"METGO 3D - Sistema de Alertas Agrícolas"
                    }
                    alertas_generadas.append(alerta)
        
        except Exception as e:
            self.logger.error(f"Error procesando alertas meteorológicas: {e}")
        
        return alertas_generadas
    
    def enviar_notificaciones_agricultores(self, alertas: List[Dict]) -> Dict:
        """Enviar notificaciones a todos los agricultores registrados"""
        resultados = {
            "total_alertas": len(alertas),
            "notificaciones_enviadas": 0,
            "errores": 0,
            "detalle": []
        }
        
        try:
            # Obtener lista de agricultores
            agricultores = self._obtener_agricultores()
            
            for alerta in alertas:
                for agricultor in agricultores:
                    try:
                        # Enviar WhatsApp si está habilitado
                        if agricultor.get('notificaciones_whatsapp', False) and agricultor.get('telefono'):
                            exito = self.enviar_whatsapp(agricultor['telefono'], alerta['mensaje'])
                            if exito:
                                resultados["notificaciones_enviadas"] += 1
                                self._registrar_notificacion(alerta, agricultor, "whatsapp", "enviado")
                            else:
                                resultados["errores"] += 1
                                self._registrar_notificacion(alerta, agricultor, "whatsapp", "error")
                        
                        # Enviar Email si está habilitado
                        if agricultor.get('notificaciones_email', False) and agricultor.get('email'):
                            asunto = f"🚨 {alerta['tipo'].replace('_', ' ').title()} - {alerta['estacion'].replace('_', ' ').title()}"
                            exito = self.enviar_email(agricultor['email'], asunto, alerta['mensaje'])
                            if exito:
                                resultados["notificaciones_enviadas"] += 1
                                self._registrar_notificacion(alerta, agricultor, "email", "enviado")
                            else:
                                resultados["errores"] += 1
                                self._registrar_notificacion(alerta, agricultor, "email", "error")
                        
                        # Enviar SMS si está habilitado
                        if agricultor.get('notificaciones_sms', False) and agricultor.get('telefono'):
                            exito = self.enviar_sms(agricultor['telefono'], alerta['mensaje'])
                            if exito:
                                resultados["notificaciones_enviadas"] += 1
                                self._registrar_notificacion(alerta, agricultor, "sms", "enviado")
                            else:
                                resultados["errores"] += 1
                                self._registrar_notificacion(alerta, agricultor, "sms", "error")
                        
                    except Exception as e:
                        self.logger.error(f"Error enviando notificación a {agricultor.get('nombre', 'Unknown')}: {e}")
                        resultados["errores"] += 1
        
        except Exception as e:
            self.logger.error(f"Error enviando notificaciones a agricultores: {e}")
        
        return resultados
    
    def _obtener_agricultores(self) -> List[Dict]:
        """Obtener lista de agricultores activos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT nombre, telefono, email, cultivos, 
                       notificaciones_whatsapp, notificaciones_email, notificaciones_sms
                FROM agricultores 
                WHERE activo = 1
            ''')
            
            agricultores = []
            for row in cursor.fetchall():
                agricultor = {
                    'nombre': row[0],
                    'telefono': row[1],
                    'email': row[2],
                    'cultivos': row[3].split(',') if row[3] else [],
                    'notificaciones_whatsapp': bool(row[4]),
                    'notificaciones_email': bool(row[5]),
                    'notificaciones_sms': bool(row[6])
                }
                agricultores.append(agricultor)
            
            conn.close()
            
            # Si no hay agricultores en BD, usar configuración por defecto
            if not agricultores:
                agricultores = [self.config["agricultores"]["default"]]
            
            return agricultores
            
        except Exception as e:
            self.logger.error(f"Error obteniendo agricultores: {e}")
            return [self.config["agricultores"]["default"]]
    
    def _registrar_notificacion(self, alerta: Dict, agricultor: Dict, metodo: str, estado: str):
        """Registrar notificación en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notificaciones_enviadas 
                (tipo_alerta, nivel, estacion, mensaje, destinatario, metodo_envio, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alerta['tipo'],
                alerta['nivel'],
                alerta['estacion'],
                alerta['mensaje'],
                agricultor['nombre'],
                metodo,
                estado
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando notificación: {e}")
    
    def _registrar_alerta_critica(self, alerta: Dict):
        """Registrar alerta crítica en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alertas_criticas 
                (tipo_alerta, estacion, valor_medido, umbral, mensaje)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alerta['tipo'],
                alerta['estacion'],
                alerta['valor'],
                alerta['umbral'],
                alerta['mensaje']
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Alerta crítica registrada: {alerta['tipo']} en {alerta['estacion']}")
            
        except Exception as e:
            self.logger.error(f"Error registrando alerta crítica: {e}")
    
    def procesar_datos_y_notificar(self, datos_meteorologicos: Dict) -> Dict:
        """Procesar datos meteorológicos y enviar notificaciones"""
        try:
            # Generar alertas
            alertas = self.procesar_alertas_meteorologicas(datos_meteorologicos)
            
            # Enviar notificaciones
            resultados = self.enviar_notificaciones_agricultores(alertas)
            
            # Registrar alertas críticas
            for alerta in alertas:
                if alerta['nivel'] == 'critico':
                    self._registrar_alerta_critica(alerta)
            
            return {
                "alertas_generadas": len(alertas),
                "notificaciones_enviadas": resultados["notificaciones_enviadas"],
                "errores": resultados["errores"],
                "alertas_criticas": len([a for a in alertas if a['nivel'] == 'critico'])
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando datos y notificando: {e}")
            return {"error": str(e)}

def main():
    """Función principal para pruebas"""
    logging.basicConfig(level=logging.INFO)
    
    sistema = SistemaNotificacionesAvanzado()
    
    # Datos de prueba
    datos_prueba = {
        "Quillota_Centro": {
            "temperatura_actual": 1.5,
            "humedad_relativa": 85,
            "velocidad_viento": 25,
            "precipitacion": 0.5
        }
    }
    
    print("Probando sistema de notificaciones...")
    resultados = sistema.procesar_datos_y_notificar(datos_prueba)
    print(f"Resultados: {resultados}")

if __name__ == "__main__":
    main()
