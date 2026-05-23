/**
 * SERVICIO DE GEOLOCALIZACIÓN
 * Maneja la obtención y gestión de ubicación GPS para la aplicación
 */

import Geolocation from 'react-native-geolocation-service';
import {Platform, Alert, PermissionsAndroid} from 'react-native';
import StorageService from './StorageService';

class LocationService {
  static isInitialized = false;
  static watchId = null;
  static currentLocation = null;

  static async initialize() {
    if (this.isInitialized) return;

    try {
      console.log('[LOCATION] Inicializando servicio de geolocalización...');

      // Solicitar permisos de ubicación
      const hasPermission = await this.requestLocationPermission();
      
      if (!hasPermission) {
        throw new Error('Permisos de ubicación denegados');
      }

      // Obtener ubicación inicial
      await this.getCurrentLocation();

      // Iniciar monitoreo continuo de ubicación
      this.startLocationTracking();

      this.isInitialized = true;
      console.log('[LOCATION] Servicio de geolocalización inicializado');

    } catch (error) {
      console.error('[LOCATION] Error inicializando servicio:', error);
      throw error;
    }
  }

  static async requestLocationPermission() {
    try {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Permisos de Ubicación',
            message: 'METGO 3D necesita acceso a su ubicación para proporcionar información meteorológica precisa y geolocalizar fotos de cultivos.',
            buttonNeutral: 'Preguntar más tarde',
            buttonNegative: 'Cancelar',
            buttonPositive: 'Permitir',
          }
        );

        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          console.log('[LOCATION] Permisos de ubicación concedidos');
          return true;
        } else {
          console.log('[LOCATION] Permisos de ubicación denegados');
          return false;
        }
      } else {
        // iOS maneja permisos automáticamente
        return true;
      }
    } catch (error) {
      console.error('[LOCATION] Error solicitando permisos:', error);
      return false;
    }
  }

  static getCurrentLocation() {
    return new Promise((resolve, reject) => {
      const options = {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 10000,
        showLocationDialog: true,
      };

      Geolocation.getCurrentPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            speed: position.coords.speed,
            timestamp: new Date(position.timestamp),
          };

          this.currentLocation = location;
          
          // Guardar ubicación en almacenamiento local
          StorageService.saveCurrentLocation(location);
          
          console.log('[LOCATION] Ubicación actual obtenida:', location);
          resolve(location);
        },
        (error) => {
          console.error('[LOCATION] Error obteniendo ubicación:', error);
          
          // Intentar obtener ubicación desde caché
          this.getCachedLocation()
            .then(cachedLocation => {
              if (cachedLocation) {
                this.currentLocation = cachedLocation;
                resolve(cachedLocation);
              } else {
                reject(error);
              }
            })
            .catch(() => reject(error));
        },
        options
      );
    });
  }

  static startLocationTracking() {
    try {
      if (this.watchId) {
        this.stopLocationTracking();
      }

      const options = {
        enableHighAccuracy: true,
        distanceFilter: 10, // Actualizar cada 10 metros
        interval: 30000, // Actualizar cada 30 segundos
        fastestInterval: 10000, // Actualizar cada 10 segundos como mínimo
      };

      this.watchId = Geolocation.watchPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            speed: position.coords.speed,
            timestamp: new Date(position.timestamp),
          };

          this.currentLocation = location;
          
          // Guardar ubicación en almacenamiento local
          StorageService.saveCurrentLocation(location);
          
          console.log('[LOCATION] Ubicación actualizada:', location);
        },
        (error) => {
          console.error('[LOCATION] Error en seguimiento de ubicación:', error);
        },
        options
      );

      console.log('[LOCATION] Seguimiento de ubicación iniciado');
      
    } catch (error) {
      console.error('[LOCATION] Error iniciando seguimiento:', error);
    }
  }

  static stopLocationTracking() {
    if (this.watchId) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
      console.log('[LOCATION] Seguimiento de ubicación detenido');
    }
  }

  static async getCachedLocation() {
    try {
      const cachedLocation = await StorageService.getCurrentLocation();
      return cachedLocation;
    } catch (error) {
      console.error('[LOCATION] Error obteniendo ubicación en caché:', error);
      return null;
    }
  }

  static getCurrentLocationSync() {
    return this.currentLocation;
  }

  // Calcular distancia entre dos puntos
  static calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radio de la Tierra en kilómetros
    const dLat = this.deg2rad(lat2 - lat1);
    const dLon = this.deg2rad(lon2 - lon1);
    
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) * 
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distancia en kilómetros
    
    return distance;
  }

  static deg2rad(deg) {
    return deg * (Math.PI / 180);
  }

  // Determinar la estación meteorológica más cercana
  static findNearestWeatherStation(userLocation) {
    const stations = [
      {
        id: 'quillota_centro',
        name: 'Quillota Centro',
        latitude: -32.8833,
        longitude: -71.2500,
        altitude: 150,
        crop: 'Palto',
        soil: 'Arcilloso limoso',
      },
      {
        id: 'la_cruz',
        name: 'La Cruz',
        latitude: -32.9167,
        longitude: -71.2333,
        altitude: 200,
        crop: 'Uva',
        soil: 'Franco arcilloso',
      },
      {
        id: 'nogueira',
        name: 'Nogueira',
        latitude: -32.8500,
        longitude: -71.2167,
        altitude: 180,
        crop: 'Cítricos',
        soil: 'Franco',
      },
      {
        id: 'colliguay',
        name: 'Colliguay',
        latitude: -32.9333,
        longitude: -71.1833,
        altitude: 250,
        crop: 'Hortalizas',
        soil: 'Franco arenoso',
      },
      {
        id: 'san_isidro',
        name: 'San Isidro',
        latitude: -32.8667,
        longitude: -71.2667,
        altitude: 120,
        crop: 'Cereales',
        soil: 'Arcilloso',
      },
      {
        id: 'hijuelas',
        name: 'Hijuelas',
        latitude: -32.8000,
        longitude: -71.2000,
        altitude: 220,
        crop: 'Palto',
        soil: 'Franco limoso',
      },
    ];

    if (!userLocation) {
      return stations[0]; // Devolver Quillota Centro por defecto
    }

    let nearestStation = stations[0];
    let minDistance = this.calculateDistance(
      userLocation.latitude,
      userLocation.longitude,
      stations[0].latitude,
      stations[0].longitude
    );

    for (let i = 1; i < stations.length; i++) {
      const distance = this.calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        stations[i].latitude,
        stations[i].longitude
      );

      if (distance < minDistance) {
        minDistance = distance;
        nearestStation = stations[i];
      }
    }

    nearestStation.distance = minDistance;
    return nearestStation;
  }

  // Verificar si la ubicación está en el Valle de Quillota
  static isInQuillotaValley(location) {
    if (!location) return false;

    // Coordenadas aproximadas del Valle de Quillota
    const valleyBounds = {
      north: -32.7,
      south: -33.0,
      east: -71.1,
      west: -71.3,
    };

    return (
      location.latitude >= valleyBounds.south &&
      location.latitude <= valleyBounds.north &&
      location.longitude >= valleyBounds.west &&
      location.longitude <= valleyBounds.east
    );
  }

  // Obtener información de zona agrícola
  static getAgriculturalZoneInfo(location) {
    if (!location) return null;

    const isInValley = this.isInQuillotaValley(location);
    const nearestStation = this.findNearestWeatherStation(location);

    return {
      isInQuillotaValley: isInValley,
      nearestStation: nearestStation,
      zoneType: isInValley ? 'Valle de Quillota' : 'Fuera del Valle',
      recommendations: isInValley ? 
        'Ubicación óptima para agricultura mediterránea' : 
        'Consulte datos meteorológicos de la estación más cercana',
    };
  }

  // Formatear coordenadas para mostrar
  static formatCoordinates(location) {
    if (!location) return 'Ubicación no disponible';

    return `${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}`;
  }

  // Formatear distancia para mostrar
  static formatDistance(distance) {
    if (distance < 1) {
      return `${(distance * 1000).toFixed(0)} m`;
    } else {
      return `${distance.toFixed(2)} km`;
    }
  }

  // Obtener dirección aproximada (requiere servicio de geocodificación inversa)
  static async getAddressFromCoordinates(location) {
    try {
      // En una implementación real, se usaría un servicio como Google Geocoding API
      // Por ahora, devolvemos información basada en las estaciones conocidas
      const nearestStation = this.findNearestWeatherStation(location);
      
      return {
        address: `Cerca de ${nearestStation.name}`,
        district: 'Valle de Quillota',
        region: 'Región de Valparaíso',
        country: 'Chile',
      };
    } catch (error) {
      console.error('[LOCATION] Error obteniendo dirección:', error);
      return null;
    }
  }

  // Limpiar recursos
  static cleanup() {
    this.stopLocationTracking();
    this.isInitialized = false;
    this.currentLocation = null;
    console.log('[LOCATION] Servicio de geolocalización limpiado');
  }
}

export default LocationService;



