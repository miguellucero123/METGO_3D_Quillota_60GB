/**
 * SERVICIO DE ALMACENAMIENTO LOCAL
 * Maneja el almacenamiento local de datos, configuraciones y caché
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import EncryptedStorage from 'react-native-encrypted-storage';

class StorageService {
  static isInitialized = false;

  // Claves para almacenamiento
  static KEYS = {
    // Autenticación
    AUTH_TOKEN: 'auth_token',
    USER_DATA: 'user_data',
    
    // Datos de la aplicación
    DASHBOARD_DATA: 'dashboard_data',
    WEATHER_DATA: 'weather_data',
    IRRIGATION_DATA: 'irrigation_data',
    PHOTOS: 'photos',
    REPORTS: 'reports',
    ALERTS: 'alerts',
    
    // Ubicación
    CURRENT_LOCATION: 'current_location',
    NOTIFICATION_TOKEN: 'notification_token',
    
    // Configuraciones
    APP_SETTINGS: 'app_settings',
    NOTIFICATION_SETTINGS: 'notification_settings',
    LOCATION_SETTINGS: 'location_settings',
    
    // Datos offline
    OFFLINE_DATA: 'offline_data',
    
    // Notificaciones
    NOTIFICATIONS: 'notifications',
    
    // Caché
    CACHE_WEATHER: 'cache_weather',
    CACHE_DASHBOARD: 'cache_dashboard',
  };

  static async initialize() {
    if (this.isInitialized) return;

    try {
      console.log('[STORAGE] Inicializando servicio de almacenamiento...');

      // Verificar que AsyncStorage esté disponible
      await AsyncStorage.getItem('test');
      
      this.isInitialized = true;
      console.log('[STORAGE] Servicio de almacenamiento inicializado');

    } catch (error) {
      console.error('[STORAGE] Error inicializando servicio:', error);
      throw error;
    }
  }

  // Métodos de almacenamiento seguro (encriptado)
  static async setSecureItem(key, value) {
    try {
      await EncryptedStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('[STORAGE] Error guardando item seguro:', error);
      throw error;
    }
  }

  static async getSecureItem(key) {
    try {
      const item = await EncryptedStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('[STORAGE] Error obteniendo item seguro:', error);
      return null;
    }
  }

  static async removeSecureItem(key) {
    try {
      await EncryptedStorage.removeItem(key);
    } catch (error) {
      console.error('[STORAGE] Error eliminando item seguro:', error);
    }
  }

  // Métodos de almacenamiento regular
  static async setItem(key, value) {
    try {
      await AsyncStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('[STORAGE] Error guardando item:', error);
      throw error;
    }
  }

  static async getItem(key) {
    try {
      const item = await AsyncStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('[STORAGE] Error obteniendo item:', error);
      return null;
    }
  }

  static async removeItem(key) {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('[STORAGE] Error eliminando item:', error);
    }
  }

  // Autenticación
  static async saveAuthToken(token) {
    await this.setSecureItem(this.KEYS.AUTH_TOKEN, token);
  }

  static async getAuthToken() {
    return await this.getSecureItem(this.KEYS.AUTH_TOKEN);
  }

  static async clearAuthToken() {
    await this.removeSecureItem(this.KEYS.AUTH_TOKEN);
  }

  static async saveUserData(userData) {
    await this.setSecureItem(this.KEYS.USER_DATA, userData);
  }

  static async getUserData() {
    return await this.getSecureItem(this.KEYS.USER_DATA);
  }

  // Datos del dashboard
  static async saveDashboardData(data) {
    await this.setItem(this.KEYS.DASHBOARD_DATA, {
      data,
      timestamp: new Date().toISOString(),
    });
  }

  static async getDashboardData() {
    const item = await this.getItem(this.KEYS.DASHBOARD_DATA);
    return item ? item.data : null;
  }

  // Datos meteorológicos
  static async saveWeatherData(data) {
    await this.setItem(this.KEYS.WEATHER_DATA, {
      data,
      timestamp: new Date().toISOString(),
    });
  }

  static async getWeatherData() {
    const item = await this.getItem(this.KEYS.WEATHER_DATA);
    return item ? item.data : null;
  }

  // Datos de riego
  static async saveIrrigationData(data) {
    await this.setItem(this.KEYS.IRRIGATION_DATA, {
      data,
      timestamp: new Date().toISOString(),
    });
  }

  static async getIrrigationData() {
    const item = await this.getItem(this.KEYS.IRRIGATION_DATA);
    return item ? item.data : null;
  }

  // Fotos
  static async savePhoto(photoData) {
    try {
      const photos = await this.getPhotos();
      const updatedPhotos = [photoData, ...(photos || [])];
      await this.setItem(this.KEYS.PHOTOS, updatedPhotos);
    } catch (error) {
      console.error('[STORAGE] Error guardando foto:', error);
      throw error;
    }
  }

  static async getPhotos() {
    return await this.getItem(this.KEYS.PHOTOS) || [];
  }

  static async updatePhoto(photoData) {
    try {
      const photos = await this.getPhotos();
      const updatedPhotos = photos.map(photo => 
        photo.id === photoData.id ? photoData : photo
      );
      await this.setItem(this.KEYS.PHOTOS, updatedPhotos);
    } catch (error) {
      console.error('[STORAGE] Error actualizando foto:', error);
      throw error;
    }
  }

  static async deletePhoto(photoId) {
    try {
      const photos = await this.getPhotos();
      const updatedPhotos = photos.filter(photo => photo.id !== photoId);
      await this.setItem(this.KEYS.PHOTOS, updatedPhotos);
    } catch (error) {
      console.error('[STORAGE] Error eliminando foto:', error);
      throw error;
    }
  }

  // Ubicación
  static async saveCurrentLocation(location) {
    await this.setItem(this.KEYS.CURRENT_LOCATION, {
      ...location,
      timestamp: new Date().toISOString(),
    });
  }

  static async getCurrentLocation() {
    const item = await this.getItem(this.KEYS.CURRENT_LOCATION);
    return item ? {
      latitude: item.latitude,
      longitude: item.longitude,
      accuracy: item.accuracy,
      altitude: item.altitude,
      speed: item.speed,
      timestamp: new Date(item.timestamp),
    } : null;
  }

  // Token de notificaciones
  static async saveNotificationToken(token) {
    await this.setItem(this.KEYS.NOTIFICATION_TOKEN, token);
  }

  static async getNotificationToken() {
    return await this.getItem(this.KEYS.NOTIFICATION_TOKEN);
  }

  // Reportes
  static async saveReports(reports) {
    await this.setItem(this.KEYS.REPORTS, reports);
  }

  static async getReports() {
    return await this.getItem(this.KEYS.REPORTS) || [];
  }

  // Alertas
  static async saveAlerts(alerts) {
    await this.setItem(this.KEYS.ALERTS, alerts);
  }

  static async getAlerts() {
    return await this.getItem(this.KEYS.ALERTS) || [];
  }

  // Notificaciones
  static async saveNotification(notification) {
    try {
      const notifications = await this.getNotifications();
      const updatedNotifications = [notification, ...(notifications || [])];
      
      // Mantener solo las últimas 100 notificaciones
      if (updatedNotifications.length > 100) {
        updatedNotifications.splice(100);
      }
      
      await this.setItem(this.KEYS.NOTIFICATIONS, updatedNotifications);
    } catch (error) {
      console.error('[STORAGE] Error guardando notificación:', error);
    }
  }

  static async getNotifications() {
    return await this.getItem(this.KEYS.NOTIFICATIONS) || [];
  }

  static async clearNotifications() {
    await this.removeItem(this.KEYS.NOTIFICATIONS);
  }

  // Configuraciones de la aplicación
  static async saveAppSettings(settings) {
    await this.setItem(this.KEYS.APP_SETTINGS, settings);
  }

  static async getAppSettings() {
    const settings = await this.getItem(this.KEYS.APP_SETTINGS);
    return settings || {
      theme: 'light',
      language: 'es',
      units: 'metric',
      autoSync: true,
      offlineMode: false,
    };
  }

  static async saveNotificationSettings(settings) {
    await this.setItem(this.KEYS.NOTIFICATION_SETTINGS, settings);
  }

  static async getNotificationSettings() {
    const settings = await this.getItem(this.KEYS.NOTIFICATION_SETTINGS);
    return settings || {
      enabled: true,
      criticalAlerts: true,
      weatherAlerts: true,
      irrigationAlerts: true,
      reportAlerts: false,
      soundEnabled: true,
      vibrateEnabled: true,
    };
  }

  static async saveLocationSettings(settings) {
    await this.setItem(this.KEYS.LOCATION_SETTINGS, settings);
  }

  static async getLocationSettings() {
    const settings = await this.getItem(this.KEYS.LOCATION_SETTINGS);
    return settings || {
      trackingEnabled: true,
      highAccuracy: true,
      updateInterval: 30000,
      distanceFilter: 10,
    };
  }

  // Datos offline
  static async saveOfflineData(data) {
    try {
      const offlineData = await this.getOfflineData();
      const updatedData = [...offlineData, {
        ...data,
        id: data.id || Date.now().toString(),
        timestamp: new Date().toISOString(),
      }];
      await this.setItem(this.KEYS.OFFLINE_DATA, updatedData);
    } catch (error) {
      console.error('[STORAGE] Error guardando datos offline:', error);
    }
  }

  static async getOfflineData() {
    return await this.getItem(this.KEYS.OFFLINE_DATA) || [];
  }

  static async removeOfflineData(dataId) {
    try {
      const offlineData = await this.getOfflineData();
      const updatedData = offlineData.filter(item => item.id !== dataId);
      await this.setItem(this.KEYS.OFFLINE_DATA, updatedData);
    } catch (error) {
      console.error('[STORAGE] Error eliminando datos offline:', error);
    }
  }

  static async clearOfflineData() {
    await this.removeItem(this.KEYS.OFFLINE_DATA);
  }

  // Caché con expiración
  static async saveCache(key, data, expirationMinutes = 30) {
    const cacheData = {
      data,
      timestamp: new Date().toISOString(),
      expiration: new Date(Date.now() + expirationMinutes * 60 * 1000).toISOString(),
    };
    await this.setItem(key, cacheData);
  }

  static async getCache(key) {
    try {
      const cacheData = await this.getItem(key);
      
      if (!cacheData) return null;
      
      const now = new Date();
      const expiration = new Date(cacheData.expiration);
      
      if (now > expiration) {
        // Cache expirado, eliminar
        await this.removeItem(key);
        return null;
      }
      
      return cacheData.data;
    } catch (error) {
      console.error('[STORAGE] Error obteniendo caché:', error);
      return null;
    }
  }

  static async clearExpiredCache() {
    try {
      const keys = [
        this.KEYS.CACHE_WEATHER,
        this.KEYS.CACHE_DASHBOARD,
      ];
      
      for (const key of keys) {
        const cacheData = await this.getItem(key);
        if (cacheData) {
          const now = new Date();
          const expiration = new Date(cacheData.expiration);
          
          if (now > expiration) {
            await this.removeItem(key);
          }
        }
      }
    } catch (error) {
      console.error('[STORAGE] Error limpiando caché expirado:', error);
    }
  }

  // Limpiar todos los datos
  static async clearAllData() {
    try {
      await AsyncStorage.clear();
      await EncryptedStorage.clear();
      console.log('[STORAGE] Todos los datos eliminados');
    } catch (error) {
      console.error('[STORAGE] Error limpiando datos:', error);
    }
  }

  // Obtener tamaño de almacenamiento usado
  static async getStorageSize() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      let totalSize = 0;
      
      for (const key of keys) {
        const value = await AsyncStorage.getItem(key);
        if (value) {
          totalSize += value.length;
        }
      }
      
      return {
        keys: keys.length,
        size: totalSize,
        sizeFormatted: this.formatBytes(totalSize),
      };
    } catch (error) {
      console.error('[STORAGE] Error calculando tamaño:', error);
      return {keys: 0, size: 0, sizeFormatted: '0 B'};
    }
  }

  static formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Exportar datos para respaldo
  static async exportData() {
    try {
      const data = {
        appSettings: await this.getAppSettings(),
        notificationSettings: await this.getNotificationSettings(),
        locationSettings: await this.getLocationSettings(),
        photos: await this.getPhotos(),
        reports: await this.getReports(),
        notifications: await this.getNotifications(),
        exportDate: new Date().toISOString(),
      };
      
      return JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('[STORAGE] Error exportando datos:', error);
      return null;
    }
  }

  // Importar datos desde respaldo
  static async importData(jsonData) {
    try {
      const data = JSON.parse(jsonData);
      
      if (data.appSettings) await this.saveAppSettings(data.appSettings);
      if (data.notificationSettings) await this.saveNotificationSettings(data.notificationSettings);
      if (data.locationSettings) await this.saveLocationSettings(data.locationSettings);
      if (data.photos) await this.setItem(this.KEYS.PHOTOS, data.photos);
      if (data.reports) await this.saveReports(data.reports);
      if (data.notifications) await this.setItem(this.KEYS.NOTIFICATIONS, data.notifications);
      
      console.log('[STORAGE] Datos importados correctamente');
      return true;
    } catch (error) {
      console.error('[STORAGE] Error importando datos:', error);
      return false;
    }
  }
}

export default StorageService;



