import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SMTP_USER
        self.sender_password = settings.SMTP_PASSWORD
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
        attachments: Optional[List[tuple]] = None
    ) -> bool:
        """
        Enviar email
        
        Args:
            to_email: Email destino
            subject: Asunto
            html_content: Contenido HTML
            plain_text: Versión texto plano (fallback)
            attachments: Lista de (filename, content)
        """
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Versión texto
            if plain_text:
                part_text = MIMEText(plain_text, "plain")
                message.attach(part_text)
            
            # Versión HTML
            part_html = MIMEText(html_content, "html")
            message.attach(part_html)
            
            # Adjuntos
            if attachments:
                for filename, content in attachments:
                    part = MIMEText(content)
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    message.attach(part)
            
            # Enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Email error ({to_email}): {e}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Email de bienvenida"""
        
        subject = "¡Bienvenido a METGO 3D!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Hola {user_name}!</h2>
                
                <p>Gracias por registrarte en <strong>METGO 3D</strong>.</p>
                
                <p>Ahora tienes acceso a:</p>
                <ul>
                    <li>✅ 14 días de prueba gratuita</li>
                    <li>✅ Alertas climáticas automáticas</li>
                    <li>✅ Pronósticos hiperlocales para tu zona</li>
                    <li>✅ Soporte técnico 24/7</li>
                </ul>
                
                <p><a href="https://app.metgo3d.com/login" style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Acceder al panel →
                </a></p>
                
                <hr>
                <p><em>METGO 3D - Inteligencia climática operacional</em></p>
                <p><a href="https://metgo3d.com">www.metgo3d.com</a></p>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_alert_email(
        self,
        to_email: str,
        alert_name: str,
        zone: str,
        value: float,
        threshold: float,
        timestamp: str
    ) -> bool:
        """Email de alerta"""
        
        subject = f"⚠️ ALERTA: {alert_name} - {zone.upper()}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: #fee2e2; padding: 20px; border-radius: 5px; border-left: 4px solid #dc2626;">
                    <h2 style="color: #991b1b;">⚠️ ALERTA DE CLIMA</h2>
                    
                    <p><strong>Zona:</strong> {zone.upper()}</p>
                    <p><strong>Alerta:</strong> {alert_name}</p>
                    
                    <p><strong>Valor medido:</strong> <span style="font-size: 24px; color: #dc2626;">{value:.1f}</span></p>
                    <p><strong>Umbral:</strong> {threshold:.1f}</p>
                    
                    <p><strong>Hora:</strong> {timestamp}</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)

email_service = EmailService()
