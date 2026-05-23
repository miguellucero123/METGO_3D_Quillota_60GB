import streamlit as st
import json
import time
from datetime import datetime, timedelta
import random

class MobileNotifications:
    """Sistema de notificaciones para dispositivos móviles"""
    
    def __init__(self):
        self.notifications = []
        self.last_check = datetime.now()
    
    def add_notification(self, title, message, type_notification="info", priority="normal"):
        """Agrega una nueva notificación"""
        notification = {
            'id': len(self.notifications) + 1,
            'title': title,
            'message': message,
            'type': type_notification,  # info, warning, error, success
            'priority': priority,  # low, normal, high, critical
            'timestamp': datetime.now(),
            'read': False
        }
        self.notifications.insert(0, notification)
        return notification
    
    def get_unread_count(self):
        """Obtiene el número de notificaciones no leídas"""
        return len([n for n in self.notifications if not n['read']])
    
    def mark_as_read(self, notification_id):
        """Marca una notificación como leída"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                break
    
    def generate_weather_alerts(self, datos_meteorologicos):
        """Genera alertas basadas en datos meteorológicos"""
        alertas = []
        
        if datos_meteorologicos.get('temperatura', 0) > 30:
            alertas.append({
                'title': '🌡️ Temperatura Alta',
                'message': f"Temperatura crítica: {datos_meteorologicos['temperatura']}°C. Considerar medidas de protección.",
                'type': 'warning',
                'priority': 'high'
            })
        
        if datos_meteorologicos.get('humedad', 0) < 50:
            alertas.append({
                'title': '💧 Humedad Baja',
                'message': f"Humedad baja: {datos_meteorologicos['humedad']}%. Incrementar riego.",
                'type': 'info',
                'priority': 'normal'
            })
        
        if datos_meteorologicos.get('viento', 0) > 15:
            alertas.append({
                'title': '💨 Vientos Fuertes',
                'message': f"Vientos fuertes: {datos_meteorologicos['viento']} km/h. Proteger estructuras.",
                'type': 'warning',
                'priority': 'high'
            })
        
        if datos_meteorologicos.get('precipitacion', 0) > 1:
            alertas.append({
                'title': '🌧️ Lluvia Intensa',
                'message': f"Lluvia intensa: {datos_meteorologicos['precipitacion']} mm. Verificar drenaje.",
                'type': 'warning',
                'priority': 'normal'
            })
        
        return alertas
    
    def generate_agricultural_alerts(self, datos_agricolas):
        """Genera alertas agrícolas"""
        alertas = []
        
        if datos_agricolas.get('rendimiento', 0) < 18:
            alertas.append({
                'title': '🌾 Rendimiento Bajo',
                'message': f"Rendimiento por debajo del objetivo: {datos_agricolas['rendimiento']} t/ha.",
                'type': 'error',
                'priority': 'high'
            })
        
        if datos_agricolas.get('calidad', 0) < 70:
            alertas.append({
                'title': '⭐ Calidad Baja',
                'message': f"Calidad del producto comprometida: {datos_agricolas['calidad']}%.",
                'type': 'warning',
                'priority': 'normal'
            })
        
        if datos_agricolas.get('eficiencia', 0) < 75:
            alertas.append({
                'title': '⚡ Eficiencia Baja',
                'message': f"Eficiencia de riego baja: {datos_agricolas['eficiencia']}%. Optimizar sistema.",
                'type': 'info',
                'priority': 'normal'
            })
        
        return alertas
    
    def generate_system_alerts(self):
        """Genera alertas del sistema"""
        alertas = []
        
        # Simular alertas del sistema
        if random.random() < 0.1:  # 10% de probabilidad
            alertas.append({
                'title': '📡 Sensor Desconectado',
                'message': 'Sensor de humedad en Zona A desconectado. Verificar conectividad.',
                'type': 'error',
                'priority': 'high'
            })
        
        if random.random() < 0.05:  # 5% de probabilidad
            alertas.append({
                'title': '🔋 Batería Baja',
                'message': 'Batería del sensor de temperatura al 15%. Reemplazar pronto.',
                'type': 'warning',
                'priority': 'normal'
            })
        
        if random.random() < 0.03:  # 3% de probabilidad
            alertas.append({
                'title': '🔄 Actualización Disponible',
                'message': 'Nueva versión del sistema disponible. Actualizar cuando sea conveniente.',
                'type': 'info',
                'priority': 'low'
            })
        
        return alertas
    
    def update_notifications(self, datos_meteorologicos, datos_agricolas):
        """Actualiza las notificaciones con nuevos datos"""
        # Limpiar notificaciones antiguas (más de 24 horas)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.notifications = [n for n in self.notifications if n['timestamp'] > cutoff_time]
        
        # Generar nuevas alertas
        weather_alerts = self.generate_weather_alerts(datos_meteorologicos)
        agricultural_alerts = self.generate_agricultural_alerts(datos_agricolas)
        system_alerts = self.generate_system_alerts()
        
        # Agregar nuevas notificaciones
        for alerta in weather_alerts + agricultural_alerts + system_alerts:
            self.add_notification(
                alerta['title'],
                alerta['message'],
                alerta['type'],
                alerta['priority']
            )
    
    def get_notifications_html(self, max_notifications=5):
        """Genera HTML para mostrar notificaciones"""
        html = """
        <style>
            .notification-container {
                max-height: 400px;
                overflow-y: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            .notification-item {
                background: white;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid;
                position: relative;
                animation: slideIn 0.3s ease;
            }
            
            .notification-item.info {
                border-left-color: #3498db;
            }
            
            .notification-item.warning {
                border-left-color: #f39c12;
            }
            
            .notification-item.error {
                border-left-color: #e74c3c;
            }
            
            .notification-item.success {
                border-left-color: #27ae60;
            }
            
            .notification-item.unread {
                background: #f8f9fa;
                border: 2px solid #667eea;
            }
            
            .notification-title {
                font-weight: bold;
                margin-bottom: 0.5rem;
                color: #2c3e50;
            }
            
            .notification-message {
                color: #7f8c8d;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .notification-time {
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                font-size: 0.8rem;
                color: #95a5a6;
            }
            
            .notification-priority {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: bold;
                text-transform: uppercase;
                margin-top: 0.5rem;
            }
            
            .priority-low {
                background: #e9ecef;
                color: #6c757d;
            }
            
            .priority-normal {
                background: #d1ecf1;
                color: #0c5460;
            }
            
            .priority-high {
                background: #fff3cd;
                color: #856404;
            }
            
            .priority-critical {
                background: #f8d7da;
                color: #721c24;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .notification-badge {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #e74c3c;
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.8rem;
                font-weight: bold;
                z-index: 1000;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.1);
                }
                100% {
                    transform: scale(1);
                }
            }
        </style>
        """
        
        if not self.notifications:
            html += """
            <div class="notification-item success">
                <div class="notification-title">✅ Sin Notificaciones</div>
                <div class="notification-message">No hay alertas activas en este momento.</div>
            </div>
            """
        else:
            html += '<div class="notification-container">'
            
            for notification in self.notifications[:max_notifications]:
                read_class = "" if notification['read'] else "unread"
                time_str = notification['timestamp'].strftime("%H:%M")
                
                html += f"""
                <div class="notification-item {notification['type']} {read_class}" onclick="markAsRead({notification['id']})">
                    <div class="notification-time">{time_str}</div>
                    <div class="notification-title">{notification['title']}</div>
                    <div class="notification-message">{notification['message']}</div>
                    <div class="notification-priority priority-{notification['priority']}">
                        {notification['priority']}
                    </div>
                </div>
                """
            
            html += '</div>'
        
        # JavaScript para marcar como leído
        html += """
        <script>
            function markAsRead(notificationId) {
                // Aquí se implementaría la lógica para marcar como leído
                console.log('Marcando notificación', notificationId, 'como leída');
                
                // Simular vibración en dispositivos móviles
                if ('vibrate' in navigator) {
                    navigator.vibrate([50]);
                }
                
                // Remover clase unread
                event.target.closest('.notification-item').classList.remove('unread');
            }
            
            // Auto-refresh cada 30 segundos
            setTimeout(function() {
                location.reload();
            }, 30000);
        </script>
        """
        
        return html

def mostrar_notificaciones_mobile():
    """Función principal para mostrar notificaciones móviles"""
    
    # Inicializar sistema de notificaciones
    if 'notifications' not in st.session_state:
        st.session_state.notifications = MobileNotifications()
    
    notifications = st.session_state.notifications
    
    # Datos simulados para generar alertas
    datos_meteorologicos = {
        'temperatura': 28 + random.uniform(-3, 3),
        'humedad': 60 + random.uniform(-10, 10),
        'viento': 8 + random.uniform(-2, 2),
        'precipitacion': random.uniform(0, 0.5)
    }
    
    datos_agricolas = {
        'rendimiento': 20 + random.uniform(-2, 2),
        'calidad': 75 + random.uniform(-5, 5),
        'eficiencia': 80 + random.uniform(-5, 5)
    }
    
    # Actualizar notificaciones
    notifications.update_notifications(datos_meteorologicos, datos_agricolas)
    
    # Mostrar contador de notificaciones
    unread_count = notifications.get_unread_count()
    if unread_count > 0:
        st.markdown(f"""
        <div class="notification-badge">
            {unread_count}
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar notificaciones
    st.markdown("### 🔔 Notificaciones")
    st.markdown(notifications.get_notifications_html(), unsafe_allow_html=True)
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualizar", key="refresh_notifications"):
            st.success("Notificaciones actualizadas")
            st.rerun()
    
    with col2:
        if st.button("✅ Marcar Todas", key="mark_all_read"):
            for notification in notifications.notifications:
                notification['read'] = True
            st.success("Todas marcadas como leídas")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Limpiar", key="clear_notifications"):
            notifications.notifications = []
            st.success("Notificaciones limpiadas")
            st.rerun()

# Si se ejecuta directamente
if __name__ == "__main__":
    st.set_page_config(
        page_title="🔔 Notificaciones - METGO Mobile",
        page_icon="🔔",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🔔 Sistema de Notificaciones Móviles")
    mostrar_notificaciones_mobile()
