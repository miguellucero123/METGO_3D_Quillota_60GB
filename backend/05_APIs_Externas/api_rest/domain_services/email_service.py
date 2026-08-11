import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.mailgun.org")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SMTP_USER", "")
        self.sender_password = os.getenv("SMTP_PASSWORD", "")
    
    def is_configured(self) -> bool:
        return bool(self.sender_email and self.sender_password)
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None
    ) -> bool:
        if not self.is_configured():
            logger.warning("SMTP creds not configured. Skipping email.")
            return False
            
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            if plain_text:
                message.attach(MIMEText(plain_text, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
            
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
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
                <p><a href="https://metgo-quillota.pages.dev/login" style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Ir al Dashboard
                </a></p>
                <hr>
                <p><em>METGO 3D - Inteligencia climática operacional</em></p>
            </body>
        </html>
        """
        return self.send_email(user_email, subject, html_content)

    def send_alert_email(self, user_email: str, alert_level: str, alert_message: str, station_id: str) -> bool:
        color = "#eab308" if alert_level.lower() == "warning" else "#ef4444"
        subject = f"METGO 3D ⚠️ Alerta: {station_id.upper()}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="border-left: 4px solid {color}; padding-left: 15px;">
                    <h2 style="color: {color};">Alerta Automática Detectada</h2>
                    <p><strong>Estación/Faena:</strong> {station_id.upper()}</p>
                    <p><strong>Nivel de Alerta:</strong> {alert_level.upper()}</p>
                    <p><strong>Mensaje:</strong> {alert_message}</p>
                    <hr style="border:0; border-top: 1px solid #ccc; margin: 20px 0;">
                    <p>Revisa el portal de METGO para más detalles operativos.</p>
                    <p><a href="https://metgo-quillota.pages.dev/dashboard" style="background: #1e293b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ir al Dashboard →
                    </a></p>
                </div>
            </body>
        </html>
        """
        return self.send_email(user_email, subject, html_content)

email_service = EmailService()
