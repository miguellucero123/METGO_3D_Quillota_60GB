"""
SISTEMA DE NOTIFICACIONES AGRÍCOLAS - METGO 3D QUILLOTA
Sistema para enviar alertas automáticas por WhatsApp, Email y SMS
"""

import smtplib
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import sqlite3
import os
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

class SistemaNotificacionesAgricolas:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configuracion = self._cargar_configuracion()
        self.base_datos = "notificaciones_agricolas.db"
        self._inicializar_base_datos()
        
    def _cargar_configuracion(self) -> Dict:
        """Cargar configuración de notificaciones"""
        config_file = "configuracion_notificaciones.json"
        
        # Configuración por defecto
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email_origen": "metgo.quillota@gmail.com",
                "password": "YOUR_APP_PASSWORD",
                "activo": False
            },
            "whatsapp": {
                "api_key": "YOUR_WHATSAPP_API_KEY",
                "phone_number_id": "YOUR_PHONE_NUMBER_ID",
                "access_token": "YOUR_ACCESS_TOKEN",
                "activo": False
            },
            "sms": {
                "api_key": "YOUR_SMS_API_KEY",
                "service": "twilio",
                "activo": False
            },
            "alertas": {
                "heladas": {
                    "temperatura_critica": 0,
                    "anticipacion_horas": 24,
                    "enviar_whatsapp": True,
                    "enviar_email": True,
                    "enviar_sms": False
                },
                "plagas": {
                    "condiciones_favorables": True,
                    "anticipacion_horas": 48,
                    "enviar_whatsapp": True,
                    "enviar_email": True,
                    "enviar_sms": False
                },
                "cosecha": {
                    "madurez_critica": 90,
                    "anticipacion_dias": 7,
                    "enviar_whatsapp": True,
                    "enviar_email": True,
                    "enviar_sms": False
                }
            },
            "contactos": {
                "agricultores": [
                    {
                        "nombre": "Juan Pérez",
                        "telefono": "+56912345678",
                        "email": "juan.perez@email.com",
                        "estaciones": ["quillota_centro", "la_cruz"],
                        "cultivos": ["paltos", "citricos"]
                    },
                    {
                        "nombre": "María González",
                        "telefono": "+56987654321",
                        "email": "maria.gonzalez@email.com",
                        "estaciones": ["nogueira", "colliguay"],
                        "cultivos": ["vides", "frutales_templados"]
                    }
                ]
            },
            "configuracion_general": {
                "hora_inicio_notificaciones": "06:00",
                "hora_fin_notificaciones": "22:00",
                "dias_semana": [1, 2, 3, 4, 5, 6, 7],
                "max_notificaciones_dia": 10,
                "cooldown_minutos": 30
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración: {e}")
        
        # Crear archivo de configuración por defecto
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Archivo de configuración creado: {config_file}")
        except Exception as e:
            self.logger.error(f"Error creando archivo de configuración: {e}")
        
        return default_config
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos para registro de notificaciones"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de notificaciones enviadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_alerta TEXT NOT NULL,
                    estacion TEXT NOT NULL,
                    destinatario TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    canal TEXT NOT NULL,
                    estado TEXT DEFAULT 'enviada',
                    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_programada TIMESTAMP,
                    intentos INTEGER DEFAULT 1,
                    error_mensaje TEXT
                )
            ''')
            
            # Tabla de alertas activas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas_activas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_alerta TEXT NOT NULL,
                    estacion TEXT NOT NULL,
                    nivel_riesgo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion TIMESTAMP,
                    notificaciones_enviadas INTEGER DEFAULT 0,
                    activa BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de configuración de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios_notificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    estaciones TEXT,
                    cultivos TEXT,
                    preferencias TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Base de datos de notificaciones inicializada")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def enviar_email(self, destinatario: str, asunto: str, mensaje: str, adjuntos: List = None) -> bool:
        """Enviar notificación por email"""
        try:
            if not EMAIL_AVAILABLE:
                self.logger.warning("Módulos de email no disponibles")
                return False
                
            config_email = self.configuracion["email"]
            
            if not config_email["activo"]:
                self.logger.info("Email desactivado en configuración")
                return False
            
            # Crear mensaje
            msg = MimeMultipart()
            msg['From'] = config_email["email_origen"]
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            # Agregar cuerpo del mensaje
            msg.attach(MimeText(mensaje, 'html', 'utf-8'))
            
            # Agregar adjuntos si los hay
            if adjuntos:
                for archivo in adjuntos:
                    if os.path.exists(archivo):
                        with open(archivo, "rb") as attachment:
                            part = MimeBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(archivo)}'
                        )
                        msg.attach(part)
            
            # Conectar y enviar
            server = smtplib.SMTP(config_email["smtp_server"], config_email["smtp_port"])
            server.starttls()
            server.login(config_email["email_origen"], config_email["password"])
            
            text = msg.as_string()
            server.sendmail(config_email["email_origen"], destinatario, text)
            server.quit()
            
            self.logger.info(f"Email enviado exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando email a {destinatario}: {e}")
            return False
    
    def enviar_whatsapp(self, telefono: str, mensaje: str) -> bool:
        """Enviar notificación por WhatsApp"""
        try:
            config_whatsapp = self.configuracion["whatsapp"]
            
            if not config_whatsapp["activo"]:
                self.logger.info("WhatsApp desactivado en configuración")
                return False
            
            # Preparar datos para la API de WhatsApp
            url = f"https://graph.facebook.com/v17.0/{config_whatsapp['phone_number_id']}/messages"
            
            headers = {
                "Authorization": f"Bearer {config_whatsapp['access_token']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": telefono,
                "type": "text",
                "text": {"body": mensaje}
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"WhatsApp enviado exitosamente a {telefono}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando WhatsApp a {telefono}: {e}")
            return False
    
    def enviar_sms(self, telefono: str, mensaje: str) -> bool:
        """Enviar notificación por SMS"""
        try:
            config_sms = self.configuracion["sms"]
            
            if not config_sms["activo"]:
                self.logger.info("SMS desactivado en configuración")
                return False
            
            # Implementación para Twilio (ejemplo)
            if config_sms["service"] == "twilio":
                from twilio.rest import Client
                
                account_sid = config_sms["account_sid"]
                auth_token = config_sms["auth_token"]
                client = Client(account_sid, auth_token)
                
                message = client.messages.create(
                    body=mensaje,
                    from_=config_sms["from_number"],
                    to=telefono
                )
                
                self.logger.info(f"SMS enviado exitosamente a {telefono}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error enviando SMS a {telefono}: {e}")
            return False
    
    def generar_mensaje_alerta_helada(self, estacion: str, datos: Dict) -> str:
        """Generar mensaje de alerta de helada"""
        mensaje = f"""
🌡️ *ALERTA DE HELADA - VALLE DE QUILLOTA*

📍 *Estación:* {estacion}
🌡️ *Temperatura mínima:* {datos.get('temperatura_minima', 'N/A')}°C
⏰ *Hora prevista:* {datos.get('hora_critica', 'N/A')}
📊 *Probabilidad:* {datos.get('probabilidad', 'N/A')}%

⚠️ *RECOMENDACIONES URGENTES:*
• Implementar riego por aspersión
• Activar calefactores si están disponibles
• Cubrir cultivos sensibles
• Monitorear cada 2 horas

🌱 *Cultivos en riesgo:*
{datos.get('cultivos_afectados', 'N/A')}

📞 *Para más información:* METGO 3D Quillota
🕐 *Enviado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        return mensaje.strip()
    
    def generar_mensaje_alerta_plaga(self, estacion: str, datos: Dict) -> str:
        """Generar mensaje de alerta de plaga"""
        mensaje = f"""
🐛 *ALERTA DE PLAGA - VALLE DE QUILLOTA*

📍 *Estación:* {estacion}
🐛 *Plaga detectada:* {datos.get('plaga', 'N/A')}
🌡️ *Temperatura:* {datos.get('temperatura', 'N/A')}°C
💧 *Humedad:* {datos.get('humedad', 'N/A')}%

⚠️ *RECOMENDACIONES:*
• Revisar cultivos inmediatamente
• Aplicar tratamiento preventivo
• Monitorear cada 24 horas
• {datos.get('tratamiento_recomendado', 'Consultar con técnico')}

🌱 *Cultivos afectados:*
{datos.get('cultivos_afectados', 'N/A')}

📞 *Para más información:* METGO 3D Quillota
🕐 *Enviado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        return mensaje.strip()
    
    def generar_mensaje_cosecha(self, estacion: str, datos: Dict) -> str:
        """Generar mensaje de recomendación de cosecha"""
        mensaje = f"""
🌾 *RECOMENDACIÓN DE COSECHA - VALLE DE QUILLOTA*

📍 *Estación:* {estacion}
🌱 *Cultivo:* {datos.get('cultivo', 'N/A')}
📊 *Madurez:* {datos.get('madurez', 'N/A')}%
📅 *Días restantes:* {datos.get('dias_restantes', 'N/A')}

✅ *RECOMENDACIONES:*
• {datos.get('recomendacion_principal', 'Evaluar estado del cultivo')}
• Preparar equipos de cosecha
• Coordinar con personal
• Verificar condiciones de mercado

💰 *Información de mercado:*
• Precio actual: {datos.get('precio_mercado', 'N/A')}
• Rendimiento esperado: {datos.get('rendimiento_esperado', 'N/A')}

📞 *Para más información:* METGO 3D Quillota
🕐 *Enviado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        return mensaje.strip()
    
    def enviar_alerta_helada(self, estacion: str, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Enviar alerta de helada a agricultores afectados"""
        try:
            # Analizar datos para detectar riesgo de helada
            temp_minima = datos_meteorologicos["temperatura_min"].min()
            
            if temp_minima > 2:  # No hay riesgo de helada
                return {"enviado": False, "razon": "No hay riesgo de helada"}
            
            # Determinar nivel de riesgo
            if temp_minima <= 0:
                nivel_riesgo = "CRÍTICO"
            elif temp_minima <= 1:
                nivel_riesgo = "ALTO"
            else:
                nivel_riesgo = "MEDIO"
            
            # Preparar datos para el mensaje
            datos_alerta = {
                "temperatura_minima": temp_minima,
                "probabilidad": min(100, max(0, (2 - temp_minima) * 50)),
                "hora_critica": "Madrugada (03:00-06:00)",
                "cultivos_afectados": "Paltos, Cítricos (alta sensibilidad)"
            }
            
            # Generar mensaje
            mensaje = self.generar_mensaje_alerta_helada(estacion, datos_alerta)
            
            # Encontrar agricultores afectados
            agricultores_afectados = self._obtener_agricultores_por_estacion(estacion)
            
            resultados = []
            for agricultor in agricultores_afectados:
                resultado = {
                    "agricultor": agricultor["nombre"],
                    "canales": []
                }
                
                # Enviar por WhatsApp
                if self.configuracion["alertas"]["heladas"]["enviar_whatsapp"] and agricultor["telefono"]:
                    if self.enviar_whatsapp(agricultor["telefono"], mensaje):
                        resultado["canales"].append("whatsapp")
                        self._registrar_notificacion("helada", estacion, agricultor["nombre"], mensaje, "whatsapp")
                
                # Enviar por Email
                if self.configuracion["alertas"]["heladas"]["enviar_email"] and agricultor["email"]:
                    asunto = f"🌡️ ALERTA DE HELADA - {nivel_riesgo} - {estacion}"
                    if self.enviar_email(agricultor["email"], asunto, mensaje.replace('*', '').replace('_', '')):
                        resultado["canales"].append("email")
                        self._registrar_notificacion("helada", estacion, agricultor["nombre"], mensaje, "email")
                
                # Enviar por SMS
                if self.configuracion["alertas"]["heladas"]["enviar_sms"] and agricultor["telefono"]:
                    if self.enviar_sms(agricultor["telefono"], mensaje):
                        resultado["canales"].append("sms")
                        self._registrar_notificacion("helada", estacion, agricultor["nombre"], mensaje, "sms")
                
                resultados.append(resultado)
            
            # Registrar alerta activa
            self._registrar_alerta_activa("helada", estacion, nivel_riesgo, mensaje)
            
            return {
                "enviado": True,
                "estacion": estacion,
                "nivel_riesgo": nivel_riesgo,
                "agricultores_notificados": len(agricultores_afectados),
                "resultados": resultados
            }
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta de helada: {e}")
            return {"enviado": False, "error": str(e)}
    
    def enviar_alerta_plaga(self, estacion: str, datos_meteorologicos: pd.DataFrame) -> Dict:
        """Enviar alerta de plaga a agricultores afectados"""
        try:
            # Analizar condiciones para plagas
            temp_promedio = datos_meteorologicos["temperatura"].mean()
            humedad_promedio = datos_meteorologicos["humedad_relativa"].mean()
            
            plagas_detectadas = []
            
            # Detectar condiciones favorables para araña roja
            if temp_promedio >= 25 and humedad_promedio <= 60:
                plagas_detectadas.append({
                    "plaga": "Araña Roja",
                    "nivel": "ALTO",
                    "tratamiento": "Aplicar acaricidas específicos o control biológico"
                })
            
            # Detectar condiciones favorables para pulgón
            if 15 <= temp_promedio <= 25 and humedad_promedio >= 60:
                plagas_detectadas.append({
                    "plaga": "Pulgón",
                    "nivel": "MEDIO",
                    "tratamiento": "Control biológico con mariquitas o jabón potásico"
                })
            
            if not plagas_detectadas:
                return {"enviado": False, "razon": "No se detectaron condiciones favorables para plagas"}
            
            resultados = []
            
            for plaga_info in plagas_detectadas:
                # Preparar datos para el mensaje
                datos_alerta = {
                    "plaga": plaga_info["plaga"],
                    "temperatura": temp_promedio,
                    "humedad": humedad_promedio,
                    "tratamiento_recomendado": plaga_info["tratamiento"],
                    "cultivos_afectados": "Paltos, Cítricos, Vides"
                }
                
                # Generar mensaje
                mensaje = self.generar_mensaje_alerta_plaga(estacion, datos_alerta)
                
                # Encontrar agricultores afectados
                agricultores_afectados = self._obtener_agricultores_por_estacion(estacion)
                
                for agricultor in agricultores_afectados:
                    resultado = {
                        "agricultor": agricultor["nombre"],
                        "plaga": plaga_info["plaga"],
                        "canales": []
                    }
                    
                    # Enviar notificaciones según configuración
                    if self.configuracion["alertas"]["plagas"]["enviar_whatsapp"] and agricultor["telefono"]:
                        if self.enviar_whatsapp(agricultor["telefono"], mensaje):
                            resultado["canales"].append("whatsapp")
                    
                    if self.configuracion["alertas"]["plagas"]["enviar_email"] and agricultor["email"]:
                        asunto = f"🐛 ALERTA DE PLAGA - {plaga_info['nivel']} - {estacion}"
                        if self.enviar_email(agricultor["email"], asunto, mensaje.replace('*', '').replace('_', '')):
                            resultado["canales"].append("email")
                    
                    resultados.append(resultado)
            
            return {
                "enviado": True,
                "estacion": estacion,
                "plagas_detectadas": len(plagas_detectadas),
                "resultados": resultados
            }
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta de plaga: {e}")
            return {"enviado": False, "error": str(e)}
    
    def enviar_recomendacion_cosecha(self, estacion: str, datos_cultivo: Dict) -> Dict:
        """Enviar recomendación de cosecha a agricultores"""
        try:
            # Generar mensaje
            mensaje = self.generar_mensaje_cosecha(estacion, datos_cultivo)
            
            # Encontrar agricultores afectados
            agricultores_afectados = self._obtener_agricultores_por_cultivo(datos_cultivo.get("cultivo", ""))
            
            resultados = []
            for agricultor in agricultores_afectados:
                resultado = {
                    "agricultor": agricultor["nombre"],
                    "cultivo": datos_cultivo.get("cultivo", ""),
                    "canales": []
                }
                
                # Enviar notificaciones según configuración
                if self.configuracion["alertas"]["cosecha"]["enviar_whatsapp"] and agricultor["telefono"]:
                    if self.enviar_whatsapp(agricultor["telefono"], mensaje):
                        resultado["canales"].append("whatsapp")
                
                if self.configuracion["alertas"]["cosecha"]["enviar_email"] and agricultor["email"]:
                    asunto = f"🌾 RECOMENDACIÓN DE COSECHA - {datos_cultivo.get('cultivo', '')} - {estacion}"
                    if self.enviar_email(agricultor["email"], asunto, mensaje.replace('*', '').replace('_', '')):
                        resultado["canales"].append("email")
                
                resultados.append(resultado)
            
            return {
                "enviado": True,
                "estacion": estacion,
                "cultivo": datos_cultivo.get("cultivo", ""),
                "agricultores_notificados": len(agricultores_afectados),
                "resultados": resultados
            }
            
        except Exception as e:
            self.logger.error(f"Error enviando recomendación de cosecha: {e}")
            return {"enviado": False, "error": str(e)}
    
    def _obtener_agricultores_por_estacion(self, estacion: str) -> List[Dict]:
        """Obtener agricultores que tienen cultivos en una estación específica"""
        agricultores = self.configuracion["contactos"]["agricultores"]
        return [ag for ag in agricultores if estacion in ag.get("estaciones", [])]
    
    def _obtener_agricultores_por_cultivo(self, cultivo: str) -> List[Dict]:
        """Obtener agricultores que tienen un cultivo específico"""
        agricultores = self.configuracion["contactos"]["agricultores"]
        return [ag for ag in agricultores if cultivo in ag.get("cultivos", [])]
    
    def _registrar_notificacion(self, tipo_alerta: str, estacion: str, destinatario: str, mensaje: str, canal: str):
        """Registrar notificación enviada en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notificaciones (tipo_alerta, estacion, destinatario, mensaje, canal)
                VALUES (?, ?, ?, ?, ?)
            ''', (tipo_alerta, estacion, destinatario, mensaje, canal))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando notificación: {e}")
    
    def _registrar_alerta_activa(self, tipo_alerta: str, estacion: str, nivel_riesgo: str, mensaje: str):
        """Registrar alerta activa en la base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Verificar si ya existe una alerta activa similar
            cursor.execute('''
                SELECT id FROM alertas_activas 
                WHERE tipo_alerta = ? AND estacion = ? AND activa = TRUE
            ''', (tipo_alerta, estacion))
            
            if cursor.fetchone():
                # Actualizar alerta existente
                cursor.execute('''
                    UPDATE alertas_activas 
                    SET notificaciones_enviadas = notificaciones_enviadas + 1,
                        fecha_deteccion = CURRENT_TIMESTAMP
                    WHERE tipo_alerta = ? AND estacion = ? AND activa = TRUE
                ''', (tipo_alerta, estacion))
            else:
                # Crear nueva alerta
                cursor.execute('''
                    INSERT INTO alertas_activas (tipo_alerta, estacion, nivel_riesgo, mensaje, fecha_expiracion)
                    VALUES (?, ?, ?, ?, datetime('now', '+24 hours'))
                ''', (tipo_alerta, estacion, nivel_riesgo, mensaje))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando alerta activa: {e}")
    
    def obtener_estadisticas_notificaciones(self, dias: int = 7) -> Dict:
        """Obtener estadísticas de notificaciones enviadas"""
        try:
            conn = sqlite3.connect(self.base_datos)
            
            # Consultar notificaciones de los últimos días
            query = '''
                SELECT 
                    tipo_alerta,
                    canal,
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'enviada' THEN 1 END) as exitosas,
                    COUNT(CASE WHEN estado = 'error' THEN 1 END) as fallidas
                FROM notificaciones 
                WHERE fecha_envio >= datetime('now', '-{} days')
                GROUP BY tipo_alerta, canal
            '''.format(dias)
            
            df = pd.read_sql_query(query, conn)
            
            # Consultar alertas activas
            query_alertas = '''
                SELECT tipo_alerta, COUNT(*) as alertas_activas
                FROM alertas_activas 
                WHERE activa = TRUE
                GROUP BY tipo_alerta
            '''
            
            df_alertas = pd.read_sql_query(query_alertas, conn)
            
            conn.close()
            
            return {
                "notificaciones": df.to_dict('records') if not df.empty else [],
                "alertas_activas": df_alertas.to_dict('records') if not df_alertas.empty else [],
                "periodo_dias": dias,
                "fecha_consulta": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}

def main():
    """Función principal para probar el sistema de notificaciones"""
    logging.basicConfig(level=logging.INFO)
    
    sistema = SistemaNotificacionesAgricolas()
    
    print("=== SISTEMA DE NOTIFICACIONES AGRÍCOLAS ===")
    print(f"Contactos configurados: {len(sistema.configuracion['contactos']['agricultores'])}")
    print(f"Email activo: {sistema.configuracion['email']['activo']}")
    print(f"WhatsApp activo: {sistema.configuracion['whatsapp']['activo']}")
    print(f"SMS activo: {sistema.configuracion['sms']['activo']}")
    
    # Simular datos meteorológicos para prueba
    datos_test = pd.DataFrame({
        "fecha": [datetime.now()],
        "temperatura": [25.5],
        "temperatura_min": [0.5],  # Riesgo de helada
        "humedad_relativa": [45],
        "precipitacion": [0]
    })
    
    print("\nProbando alerta de helada...")
    resultado = sistema.enviar_alerta_helada("quillota_centro", datos_test)
    print(f"Resultado: {resultado}")
    
    # Obtener estadísticas
    print("\nEstadísticas de notificaciones:")
    stats = sistema.obtener_estadisticas_notificaciones(7)
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
