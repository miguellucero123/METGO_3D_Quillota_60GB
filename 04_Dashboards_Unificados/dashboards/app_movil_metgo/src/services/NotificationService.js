/**
 * SERVICIO DE NOTIFICACIONES PUSH
 * Maneja notificaciones push para alertas meteorológicas y agrícolas
 */

import PushNotification from 'react-native-push-notification';
import {Platform, Alert} from 'react-native';
import StorageService from './StorageService';

class NotificationService {
  static isConfigured = false;

  static configure() {
    if (this.isConfigured) return;

    try {
      console.log('[NOTIFICATIONS] Configurando servicio de notificaciones...');

      PushNotification.configure({
        // (optional) Called when Token is generated (iOS and Android)
        onRegister: function (token) {
          console.log('[NOTIFICATIONS] Token registrado:', token);
          // Guardar token para enviar notificaciones específicas
          StorageService.saveNotificationToken(token.token);
        },

        // (required) Called when a remote or local notification is opened or received
        onNotification: function (notification) {
          console.log('[NOTIFICATIONS] Notificación recibida:', notification);
          
          // Manejar diferentes tipos de notificaciones
          if (notification.userInteraction) {
            // Usuario tocó la notificación
            handleNotificationPress(notification);
          } else {
            // Notificación recibida en background
            handleBackgroundNotification(notification);
          }
        },

        // (optional) Called when the user fails to register for remote notifications.
        onRegistrationError: function(err) {
          console.error('[NOTIFICATIONS] Error de registro:', err);
        },

        // IOS ONLY (optional): default: all - Permissions to register.
        permissions: {
          alert: true,
          badge: true,
          sound: true,
        },

        // Should the initial notification be popped automatically
        popInitialNotification: true,

        /**
         * (optional) default: true
         * - Specified if permissions (ios) and token (android and ios) will requested or not,
         * - if not, you must call PushNotificationsHandler.requestPermissions() later
         */
        requestPermissions: Platform.OS === 'ios',
      });

      // Crear canal de notificaciones para Android
      if (Platform.OS === 'android') {
        this.createNotificationChannels();
      }

      this.isConfigured = true;
      console.log('[NOTIFICATIONS] Servicio de notificaciones configurado');

    } catch (error) {
      console.error('[NOTIFICATIONS] Error configurando notificaciones:', error);
    }
  }

  static createNotificationChannels() {
    try {
      // Canal para alertas críticas
      PushNotification.createChannel(
        {
          channelId: 'metgo-critical',
          channelName: 'Alertas Críticas',
          channelDescription: 'Alertas meteorológicas críticas',
          playSound: true,
          soundName: 'default',
          importance: 4, // Alta importancia
          vibrate: true,
        },
        (created) => console.log('[NOTIFICATIONS] Canal crítico creado:', created)
      );

      // Canal para alertas normales
      PushNotification.createChannel(
        {
          channelId: 'metgo-alerts',
          channelName: 'Alertas Meteorológicas',
          channelDescription: 'Alertas meteorológicas y agrícolas',
          playSound: true,
          soundName: 'default',
          importance: 3, // Importancia normal
          vibrate: true,
        },
        (created) => console.log('[NOTIFICATIONS] Canal alertas creado:', created)
      );

      // Canal para información general
      PushNotification.createChannel(
        {
          channelId: 'metgo-info',
          channelName: 'Información METGO',
          channelDescription: 'Información general del sistema',
          playSound: false,
          importance: 2, // Baja importancia
          vibrate: false,
        },
        (created) => console.log('[NOTIFICATIONS] Canal información creado:', created)
      );

    } catch (error) {
      console.error('[NOTIFICATIONS] Error creando canales:', error);
    }
  }

  // Enviar notificación local
  static sendLocalNotification(title, message, data = {}, options = {}) {
    try {
      const notificationOptions = {
        channelId: options.channelId || 'metgo-alerts',
        title: title,
        message: message,
        data: data,
        smallIcon: 'ic_notification',
        largeIcon: 'ic_launcher',
        ...options,
      };

      PushNotification.localNotification(notificationOptions);
      
      console.log('[NOTIFICATIONS] Notificación local enviada:', title);
      
    } catch (error) {
      console.error('[NOTIFICATIONS] Error enviando notificación local:', error);
    }
  }

  // Enviar notificación de alerta crítica
  static sendCriticalAlert(title, message, data = {}) {
    this.sendLocalNotification(title, message, data, {
      channelId: 'metgo-critical',
      soundName: 'default',
      vibrate: true,
      priority: 'high',
      importance: 'high',
      ongoing: false,
      autoCancel: true,
      invokeApp: true,
    });
  }

  // Enviar notificación de alerta meteorológica
  static sendWeatherAlert(type, message, data = {}) {
    const title = `🌡️ Alerta Meteorológica: ${type}`;
    
    this.sendLocalNotification(title, message, data, {
      channelId: 'metgo-alerts',
      soundName: 'default',
      vibrate: true,
      priority: 'high',
      importance: 'high',
    });
  }

  // Enviar notificación de riego
  static sendIrrigationAlert(message, data = {}) {
    const title = '💧 Sistema de Riego';
    
    this.sendLocalNotification(title, message, data, {
      channelId: 'metgo-alerts',
      soundName: 'default',
      vibrate: true,
    });
  }

  // Enviar notificación informativa
  static sendInfoNotification(title, message, data = {}) {
    this.sendLocalNotification(title, message, data, {
      channelId: 'metgo-info',
      soundName: null,
      vibrate: false,
      priority: 'low',
    });
  }

  // Programar notificación
  static scheduleNotification(date, title, message, data = {}) {
    try {
      PushNotification.localNotificationSchedule({
        date: date,
        channelId: 'metgo-alerts',
        title: title,
        message: message,
        data: data,
        smallIcon: 'ic_notification',
        largeIcon: 'ic_launcher',
        soundName: 'default',
        vibrate: true,
      });

      console.log('[NOTIFICATIONS] Notificación programada para:', date);
      
    } catch (error) {
      console.error('[NOTIFICATIONS] Error programando notificación:', error);
    }
  }

  // Cancelar todas las notificaciones
  static cancelAllNotifications() {
    try {
      PushNotification.cancelAllLocalNotifications();
      console.log('[NOTIFICATIONS] Todas las notificaciones canceladas');
    } catch (error) {
      console.error('[NOTIFICATIONS] Error cancelando notificaciones:', error);
    }
  }

  // Obtener notificaciones programadas
  static getScheduledNotifications() {
    return new Promise((resolve, reject) => {
      PushNotification.getScheduledLocalNotifications((notifications) => {
        resolve(notifications || []);
      });
    });
  }

  // Configurar notificaciones periódicas
  static setupPeriodicNotifications() {
    try {
      // Notificación diaria de resumen meteorológico
      const dailyTime = new Date();
      dailyTime.setHours(8, 0, 0, 0); // 8:00 AM
      
      this.scheduleNotification(
        dailyTime,
        '📊 Resumen Diario METGO 3D',
        'Revise las condiciones meteorológicas y recomendaciones para hoy',
        {type: 'daily_summary'}
      );

      // Notificación semanal de reportes
      const weeklyTime = new Date();
      weeklyTime.setDate(weeklyTime.getDate() + (1 - weeklyTime.getDay())); // Lunes
      weeklyTime.setHours(9, 0, 0, 0); // 9:00 AM
      
      this.scheduleNotification(
        weeklyTime,
        '📈 Reporte Semanal Disponible',
        'Su reporte semanal de análisis agrícola está listo',
        {type: 'weekly_report'}
      );

      console.log('[NOTIFICATIONS] Notificaciones periódicas configuradas');
      
    } catch (error) {
      console.error('[NOTIFICATIONS] Error configurando notificaciones periódicas:', error);
    }
  }

  // Manejar alertas meteorológicas específicas
  static handleWeatherAlerts(weatherData) {
    try {
      const {temperature, humidity, precipitation, windSpeed} = weatherData;

      // Alerta de helada
      if (temperature <= 2) {
        this.sendCriticalAlert(
          '❄️ ALERTA DE HELADA',
          `Temperatura crítica: ${temperature}°C. Activar sistemas de protección inmediatamente.`,
          {type: 'frost_alert', temperature}
        );
      }

      // Alerta de temperatura alta
      if (temperature >= 35) {
        this.sendWeatherAlert(
          'Temperatura Alta',
          `Temperatura elevada: ${temperature}°C. Monitorear estrés hídrico en cultivos.`,
          {type: 'high_temperature', temperature}
        );
      }

      // Alerta de humedad baja
      if (humidity <= 30) {
        this.sendWeatherAlert(
          'Humedad Baja',
          `Humedad relativa baja: ${humidity}%. Considerar riego adicional.`,
          {type: 'low_humidity', humidity}
        );
      }

      // Alerta de viento fuerte
      if (windSpeed >= 50) {
        this.sendWeatherAlert(
          'Viento Fuerte',
          `Viento fuerte detectado: ${windSpeed} km/h. Verificar estructuras y cultivos.`,
          {type: 'strong_wind', windSpeed}
        );
      }

      // Alerta de precipitación intensa
      if (precipitation >= 20) {
        this.sendWeatherAlert(
          'Lluvia Intensa',
          `Precipitación intensa: ${precipitation}mm. Verificar drenaje y evitar riego.`,
          {type: 'heavy_rain', precipitation}
        );
      }

    } catch (error) {
      console.error('[NOTIFICATIONS] Error manejando alertas meteorológicas:', error);
    }
  }

  // Manejar alertas de riego
  static handleIrrigationAlerts(irrigationData) {
    try {
      const {waterLevel, activeSectors, nextIrrigation} = irrigationData;

      // Alerta de nivel de agua bajo
      if (waterLevel <= 20) {
        this.sendCriticalAlert(
          '💧 Nivel de Agua Bajo',
          `Nivel de agua crítico: ${waterLevel}%. Verificar suministro de agua inmediatamente.`,
          {type: 'low_water_level', waterLevel}
        );
      }

      // Notificación de riego programado
      if (nextIrrigation) {
        this.sendIrrigationAlert(
          `Riego programado en ${nextIrrigation}. ${activeSectors} sectores activos.`,
          {type: 'scheduled_irrigation', nextIrrigation, activeSectors}
        );
      }

    } catch (error) {
      console.error('[NOTIFICATIONS] Error manejando alertas de riego:', error);
    }
  }
}

// Funciones auxiliares para manejar notificaciones
const handleNotificationPress = (notification) => {
  try {
    console.log('[NOTIFICATIONS] Usuario tocó notificación:', notification);
    
    const {data} = notification;
    
    if (data) {
      switch (data.type) {
        case 'frost_alert':
          // Navegar a pantalla de alertas
          break;
        case 'irrigation_alert':
          // Navegar a pantalla de riego
          break;
        case 'daily_summary':
          // Navegar a dashboard
          break;
        case 'weekly_report':
          // Navegar a reportes
          break;
        default:
          // Navegar a dashboard por defecto
          break;
      }
    }
  } catch (error) {
    console.error('[NOTIFICATIONS] Error manejando presión de notificación:', error);
  }
};

const handleBackgroundNotification = (notification) => {
  try {
    console.log('[NOTIFICATIONS] Notificación recibida en background:', notification);
    
    // Guardar notificación en almacenamiento local
    StorageService.saveNotification(notification);
    
  } catch (error) {
    console.error('[NOTIFICATIONS] Error manejando notificación en background:', error);
  }
};

export default NotificationService;



