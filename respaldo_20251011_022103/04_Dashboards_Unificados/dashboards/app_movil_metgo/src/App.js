/**
 * APLICACIÓN MÓVIL METGO 3D QUILLOTA
 * Sistema integral para agricultores del Valle de Quillota
 * 
 * Funcionalidades:
 * - Alertas meteorológicas en tiempo real
 * - Fotos de cultivos con geolocalización
 * - GPS y mapas interactivos
 * - Dashboard meteorológico
 * - Sistema de riego inteligente
 * - Predicciones ML
 * - Reportes y análisis
 */

import React, {useEffect, useState} from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Alert,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Importar componentes principales
import DashboardScreen from './screens/DashboardScreen';
import WeatherScreen from './screens/WeatherScreen';
import IrrigationScreen from './screens/IrrigationScreen';
import CameraScreen from './screens/CameraScreen';
import MapsScreen from './screens/MapsScreen';
import AlertsScreen from './screens/AlertsScreen';
import ReportsScreen from './screens/ReportsScreen';
import ProfileScreen from './screens/ProfileScreen';

// Importar servicios
import NotificationService from './services/NotificationService';
import LocationService from './services/LocationService';
import ApiService from './services/ApiService';
import StorageService from './services/StorageService';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Configuración de colores del tema METGO
const COLORS = {
  primary: '#2E7D32',      // Verde agrícola
  secondary: '#4CAF50',    // Verde claro
  accent: '#FF9800',       // Naranja
  background: '#F5F5F5',   // Gris claro
  surface: '#FFFFFF',      // Blanco
  text: '#212121',         // Negro
  textSecondary: '#757575', // Gris
  error: '#F44336',        // Rojo
  warning: '#FF9800',      // Naranja
  success: '#4CAF50',      // Verde
  info: '#2196F3',         // Azul
};

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Weather':
              iconName = 'wb-sunny';
              break;
            case 'Irrigation':
              iconName = 'opacity';
              break;
            case 'Camera':
              iconName = 'camera-alt';
              break;
            case 'Maps':
              iconName = 'map';
              break;
            case 'Alerts':
              iconName = 'notifications';
              break;
            case 'Reports':
              iconName = 'assessment';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textSecondary,
        tabBarStyle: {
          backgroundColor: COLORS.surface,
          borderTopColor: COLORS.primary,
          borderTopWidth: 2,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        headerStyle: {
          backgroundColor: COLORS.primary,
        },
        headerTintColor: COLORS.surface,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{title: 'Dashboard'}}
      />
      <Tab.Screen 
        name="Weather" 
        component={WeatherScreen}
        options={{title: 'Meteorología'}}
      />
      <Tab.Screen 
        name="Irrigation" 
        component={IrrigationScreen}
        options={{title: 'Riego'}}
      />
      <Tab.Screen 
        name="Camera" 
        component={CameraScreen}
        options={{title: 'Fotos'}}
      />
      <Tab.Screen 
        name="Maps" 
        component={MapsScreen}
        options={{title: 'Mapas'}}
      />
      <Tab.Screen 
        name="Alerts" 
        component={AlertsScreen}
        options={{title: 'Alertas'}}
      />
      <Tab.Screen 
        name="Reports" 
        component={ReportsScreen}
        options={{title: 'Reportes'}}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{title: 'Perfil'}}
      />
    </Tab.Navigator>
  );
}

function App() {
  const [isReady, setIsReady] = useState(false);
  const [initialRoute, setInitialRoute] = useState('MainTabs');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('[APP] Inicializando aplicación METGO 3D...');
      
      // Solicitar permisos necesarios
      await requestPermissions();
      
      // Inicializar servicios
      await initializeServices();
      
      // Configurar notificaciones
      await NotificationService.configure();
      
      // Verificar conexión inicial
      await checkInitialConnection();
      
      setIsReady(true);
      console.log('[APP] Aplicación inicializada correctamente');
      
    } catch (error) {
      console.error('[APP] Error inicializando aplicación:', error);
      Alert.alert(
        'Error de Inicialización',
        'No se pudo inicializar la aplicación correctamente. Verifique su conexión a internet.',
        [{text: 'Reintentar', onPress: initializeApp}]
      );
    }
  };

  const requestPermissions = async () => {
    try {
      console.log('[APP] Solicitando permisos...');
      
      if (Platform.OS === 'android') {
        const permissions = [
          PermissionsAndroid.PERMISSIONS.CAMERA,
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION,
          PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
        ];

        const granted = await PermissionsAndroid.requestMultiple(permissions);
        
        const allGranted = Object.values(granted).every(
          permission => permission === PermissionsAndroid.RESULTS.GRANTED
        );
        
        if (!allGranted) {
          Alert.alert(
            'Permisos Requeridos',
            'La aplicación necesita ciertos permisos para funcionar correctamente. Por favor, otorgue todos los permisos solicitados.',
            [{text: 'OK'}]
          );
        }
      }
      
      console.log('[APP] Permisos solicitados');
      
    } catch (error) {
      console.error('[APP] Error solicitando permisos:', error);
    }
  };

  const initializeServices = async () => {
    try {
      console.log('[APP] Inicializando servicios...');
      
      // Inicializar servicio de ubicación
      await LocationService.initialize();
      
      // Inicializar servicio de API
      await ApiService.initialize();
      
      // Inicializar servicio de almacenamiento
      await StorageService.initialize();
      
      console.log('[APP] Servicios inicializados');
      
    } catch (error) {
      console.error('[APP] Error inicializando servicios:', error);
      throw error;
    }
  };

  const checkInitialConnection = async () => {
    try {
      console.log('[APP] Verificando conexión inicial...');
      
      // Verificar conexión a internet
      const isConnected = await ApiService.checkConnection();
      
      if (!isConnected) {
        Alert.alert(
          'Sin Conexión',
          'No se pudo conectar con los servidores de METGO 3D. La aplicación funcionará en modo offline.',
          [{text: 'Continuar'}]
        );
      }
      
      console.log('[APP] Conexión verificada');
      
    } catch (error) {
      console.error('[APP] Error verificando conexión:', error);
    }
  };

  if (!isReady) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <StatusBar barStyle="light-content" backgroundColor={COLORS.primary} />
        {/* Aquí iría un componente de loading */}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={COLORS.primary} />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName={initialRoute}
          screenOptions={{
            headerStyle: {
              backgroundColor: COLORS.primary,
            },
            headerTintColor: COLORS.surface,
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="MainTabs" 
            component={MainTabs}
            options={{headerShown: false}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default App;



