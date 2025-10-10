/**
 * SERVICIO DE API
 * Maneja la comunicación con los servidores METGO 3D
 */

import axios from 'axios';
import NetInfo from '@react-native-netinfo/netinfo';
import DeviceInfo from 'react-native-device-info';
import StorageService from './StorageService';

class ApiService {
  static baseURL = 'https://api.metgo3d.cl'; // URL del servidor de producción
  static localURL = 'http://192.168.1.100:8501'; // URL local para desarrollo
  static isInitialized = false;
  static apiClient = null;
  static deviceInfo = null;

  static async initialize() {
    if (this.isInitialized) return;

    try {
      console.log('[API] Inicializando servicio de API...');

      // Obtener información del dispositivo
      this.deviceInfo = {
        deviceId: await DeviceInfo.getUniqueId(),
        deviceName: await DeviceInfo.getDeviceName(),
        systemName: await DeviceInfo.getSystemName(),
        systemVersion: await DeviceInfo.getSystemVersion(),
        appVersion: await DeviceInfo.getVersion(),
        buildNumber: await DeviceInfo.getBuildNumber(),
      };

      // Configurar cliente Axios
      this.apiClient = axios.create({
        baseURL: this.baseURL,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': `METGO3D-Mobile/${this.deviceInfo.appVersion}`,
          'X-Device-ID': this.deviceInfo.deviceId,
        },
      });

      // Configurar interceptores
      this.setupInterceptors();

      this.isInitialized = true;
      console.log('[API] Servicio de API inicializado');

    } catch (error) {
      console.error('[API] Error inicializando servicio:', error);
      throw error;
    }
  }

  static setupInterceptors() {
    // Interceptor de solicitudes
    this.apiClient.interceptors.request.use(
      async (config) => {
        try {
          // Verificar conexión a internet
          const netInfo = await NetInfo.fetch();
          if (!netInfo.isConnected) {
            throw new Error('Sin conexión a internet');
          }

          // Agregar token de autenticación si está disponible
          const authToken = await StorageService.getAuthToken();
          if (authToken) {
            config.headers.Authorization = `Bearer ${authToken}`;
          }

          console.log('[API] Enviando solicitud:', config.method?.toUpperCase(), config.url);
          return config;
        } catch (error) {
          console.error('[API] Error en interceptor de solicitud:', error);
          throw error;
        }
      },
      (error) => {
        console.error('[API] Error en interceptor de solicitud:', error);
        return Promise.reject(error);
      }
    );

    // Interceptor de respuestas
    this.apiClient.interceptors.response.use(
      (response) => {
        console.log('[API] Respuesta recibida:', response.status, response.config.url);
        return response;
      },
      async (error) => {
        console.error('[API] Error en respuesta:', error.response?.status, error.message);

        if (error.response?.status === 401) {
          // Token expirado, limpiar autenticación
          await StorageService.clearAuthToken();
        }

        return Promise.reject(error);
      }
    );
  }

  // Verificar conexión a internet
  static async checkConnection() {
    try {
      const netInfo = await NetInfo.fetch();
      return netInfo.isConnected;
    } catch (error) {
      console.error('[API] Error verificando conexión:', error);
      return false;
    }
  }

  // Autenticación
  static async authenticate(email, password) {
    try {
      const response = await this.apiClient.post('/auth/login', {
        email,
        password,
        deviceInfo: this.deviceInfo,
      });

      const {token, user} = response.data;
      
      // Guardar token y datos de usuario
      await StorageService.saveAuthToken(token);
      await StorageService.saveUserData(user);

      return {success: true, user, token};
    } catch (error) {
      console.error('[API] Error en autenticación:', error);
      return {success: false, error: error.message};
    }
  }

  // Obtener datos del dashboard
  static async getDashboardData() {
    try {
      const response = await this.apiClient.get('/dashboard/data');
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo datos del dashboard:', error);
      
      // Devolver datos simulados en caso de error
      return this.getMockDashboardData();
    }
  }

  // Obtener datos meteorológicos
  static async getWeatherData(stationId = null) {
    try {
      const url = stationId ? `/weather/${stationId}` : '/weather/current';
      const response = await this.apiClient.get(url);
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo datos meteorológicos:', error);
      return this.getMockWeatherData();
    }
  }

  // Obtener datos de riego
  static async getIrrigationData() {
    try {
      const response = await this.apiClient.get('/irrigation/data');
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo datos de riego:', error);
      return this.getMockIrrigationData();
    }
  }

  // Subir foto de cultivo
  static async uploadPhoto(photoData) {
    try {
      const formData = new FormData();
      
      formData.append('photo', {
        uri: photoData.uri,
        type: 'image/jpeg',
        name: `crop_photo_${photoData.id}.jpg`,
      });
      
      formData.append('metadata', JSON.stringify({
        id: photoData.id,
        timestamp: photoData.timestamp,
        location: photoData.location,
        cropType: photoData.cropType,
        notes: photoData.notes,
        deviceInfo: this.deviceInfo,
      }));

      const response = await this.apiClient.post('/photos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('[API] Error subiendo foto:', error);
      throw error;
    }
  }

  // Obtener reportes
  static async getReports(type = 'all', dateRange = null) {
    try {
      const params = {type};
      if (dateRange) {
        params.startDate = dateRange.start;
        params.endDate = dateRange.end;
      }

      const response = await this.apiClient.get('/reports', {params});
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo reportes:', error);
      return [];
    }
  }

  // Obtener alertas
  static async getAlerts() {
    try {
      const response = await this.apiClient.get('/alerts');
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo alertas:', error);
      return [];
    }
  }

  // Enviar datos de ubicación
  static async sendLocationData(locationData) {
    try {
      const response = await this.apiClient.post('/location/update', {
        ...locationData,
        deviceInfo: this.deviceInfo,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('[API] Error enviando datos de ubicación:', error);
      throw error;
    }
  }

  // Obtener predicciones ML
  static async getMLPredictions(stationId, horizon = 7) {
    try {
      const response = await this.apiClient.get('/ml/predictions', {
        params: {stationId, horizon},
      });
      return response.data;
    } catch (error) {
      console.error('[API] Error obteniendo predicciones ML:', error);
      return null;
    }
  }

  // Sincronizar datos offline
  static async syncOfflineData() {
    try {
      const offlineData = await StorageService.getOfflineData();
      
      if (offlineData.length === 0) {
        console.log('[API] No hay datos offline para sincronizar');
        return;
      }

      console.log(`[API] Sincronizando ${offlineData.length} elementos offline...`);

      for (const data of offlineData) {
        try {
          await this.apiClient.post('/sync/offline-data', data);
          await StorageService.removeOfflineData(data.id);
        } catch (error) {
          console.error('[API] Error sincronizando elemento offline:', error);
        }
      }

      console.log('[API] Sincronización offline completada');
    } catch (error) {
      console.error('[API] Error en sincronización offline:', error);
    }
  }

  // Datos simulados para desarrollo/testing
  static getMockDashboardData() {
    return {
      weather: {
        temperature: 22.5,
        humidity: 68,
        precipitation: 0,
        windSpeed: 12.3,
        pressure: 1013.2,
        cloudiness: 25,
        uvIndex: 7,
      },
      irrigation: {
        activeSectors: 3,
        nextIrrigation: '2 horas',
        waterLevel: 85,
        totalWaterUsed: 1250,
        efficiency: 92,
      },
      alerts: [
        {
          id: 1,
          type: 'warning',
          message: 'Temperatura alta prevista para mañana',
          timestamp: new Date(),
        },
        {
          id: 2,
          type: 'info',
          message: 'Riego programado para las 6:00 AM',
          timestamp: new Date(),
        },
      ],
      charts: {
        temperature: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            data: [15, 12, 18, 25, 28, 22],
            color: (opacity = 1) => `rgba(46, 125, 50, ${opacity})`,
          }],
        },
        precipitation: {
          labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
          datasets: [{
            data: [0, 0, 5.2, 0, 0, 0, 0],
          }],
        },
        crops: [
          {
            name: 'Palto',
            population: 45,
            color: '#2E7D32',
          },
          {
            name: 'Uva',
            population: 30,
            color: '#4CAF50',
          },
          {
            name: 'Cítricos',
            population: 25,
            color: '#8BC34A',
          },
        ],
      },
    };
  }

  static getMockWeatherData() {
    return {
      station: 'quillota_centro',
      timestamp: new Date(),
      temperature: {
        current: 22.5,
        max: 28.3,
        min: 16.2,
      },
      humidity: 68,
      precipitation: 0,
      wind: {
        speed: 12.3,
        direction: 180,
      },
      pressure: 1013.2,
      cloudiness: 25,
      uvIndex: 7,
      forecast: [
        {
          date: new Date(Date.now() + 24 * 60 * 60 * 1000),
          temperature: {max: 26, min: 15},
          precipitation: 0,
          humidity: 65,
        },
        {
          date: new Date(Date.now() + 48 * 60 * 60 * 1000),
          temperature: {max: 24, min: 13},
          precipitation: 2.5,
          humidity: 72,
        },
      ],
    };
  }

  static getMockIrrigationData() {
    return {
      sectors: [
        {
          id: 1,
          name: 'Sector Norte - Paltos',
          active: true,
          waterFlow: 45.2,
          duration: 30,
          nextSchedule: new Date(Date.now() + 2 * 60 * 60 * 1000),
        },
        {
          id: 2,
          name: 'Sector Sur - Uvas',
          active: false,
          waterFlow: 0,
          duration: 0,
          nextSchedule: new Date(Date.now() + 6 * 60 * 60 * 1000),
        },
        {
          id: 3,
          name: 'Sector Este - Cítricos',
          active: true,
          waterFlow: 38.7,
          duration: 45,
          nextSchedule: new Date(Date.now() + 4 * 60 * 60 * 1000),
        },
      ],
      waterLevel: 85,
      totalWaterUsed: 1250,
      efficiency: 92,
      nextIrrigation: new Date(Date.now() + 2 * 60 * 60 * 1000),
    };
  }
}

export default ApiService;



