/**
 * PANTALLA PRINCIPAL DEL DASHBOARD
 * Dashboard principal con resumen de información meteorológica y agrícola
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
  Alert,
} from 'react-native';
import {LineChart, BarChart, PieChart} from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

import ApiService from '../services/ApiService';
import StorageService from '../services/StorageService';

const {width: screenWidth} = Dimensions.get('window');

const COLORS = {
  primary: '#2E7D32',
  secondary: '#4CAF50',
  accent: '#FF9800',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  text: '#212121',
  textSecondary: '#757575',
  error: '#F44336',
  warning: '#FF9800',
  success: '#4CAF50',
  info: '#2196F3',
};

const DashboardScreen = ({navigation}) => {
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      console.log('[DASHBOARD] Cargando datos del dashboard...');
      
      // Obtener datos del dashboard desde la API
      const data = await ApiService.getDashboardData();
      
      if (data) {
        setDashboardData(data);
        setLastUpdate(new Date());
        await StorageService.saveDashboardData(data);
      } else {
        // Cargar datos desde almacenamiento local si no hay conexión
        const localData = await StorageService.getDashboardData();
        setDashboardData(localData);
        console.log('[DASHBOARD] Datos cargados desde almacenamiento local');
      }
      
      setLoading(false);
      
    } catch (error) {
      console.error('[DASHBOARD] Error cargando datos:', error);
      setLoading(false);
      Alert.alert('Error', 'No se pudieron cargar los datos del dashboard');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const renderWeatherCard = () => {
    if (!dashboardData?.weather) return null;

    const {weather} = dashboardData;
    
    return (
      <View style={styles.card}>
        <LinearGradient
          colors={[COLORS.primary, COLORS.secondary]}
          style={styles.cardGradient}
        >
          <View style={styles.cardHeader}>
            <Icon name="wb-sunny" size={24} color={COLORS.surface} />
            <Text style={styles.cardTitle}>Condiciones Actuales</Text>
          </View>
          
          <View style={styles.weatherGrid}>
            <View style={styles.weatherItem}>
              <Text style={styles.weatherValue}>{weather.temperature}°C</Text>
              <Text style={styles.weatherLabel}>Temperatura</Text>
            </View>
            
            <View style={styles.weatherItem}>
              <Text style={styles.weatherValue}>{weather.humidity}%</Text>
              <Text style={styles.weatherLabel}>Humedad</Text>
            </View>
            
            <View style={styles.weatherItem}>
              <Text style={styles.weatherValue}>{weather.precipitation}mm</Text>
              <Text style={styles.weatherLabel}>Precipitación</Text>
            </View>
            
            <View style={styles.weatherItem}>
              <Text style={styles.weatherValue}>{weather.windSpeed} km/h</Text>
              <Text style={styles.weatherLabel}>Viento</Text>
            </View>
          </View>
        </LinearGradient>
      </View>
    );
  };

  const renderIrrigationCard = () => {
    if (!dashboardData?.irrigation) return null;

    const {irrigation} = dashboardData;
    
    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="opacity" size={24} color={COLORS.info} />
          <Text style={styles.cardTitle}>Sistema de Riego</Text>
        </View>
        
        <View style={styles.irrigationGrid}>
          <View style={styles.irrigationItem}>
            <Text style={styles.irrigationValue}>{irrigation.activeSectors}</Text>
            <Text style={styles.irrigationLabel}>Sectores Activos</Text>
          </View>
          
          <View style={styles.irrigationItem}>
            <Text style={styles.irrigationValue}>{irrigation.nextIrrigation}</Text>
            <Text style={styles.irrigationLabel}>Próximo Riego</Text>
          </View>
          
          <View style={styles.irrigationItem}>
            <Text style={styles.irrigationValue}>{irrigation.waterLevel}%</Text>
            <Text style={styles.irrigationLabel}>Nivel de Agua</Text>
          </View>
        </View>
      </View>
    );
  };

  const renderAlertsCard = () => {
    if (!dashboardData?.alerts) return null;

    const {alerts} = dashboardData;
    
    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="notifications" size={24} color={COLORS.warning} />
          <Text style={styles.cardTitle}>Alertas Activas</Text>
        </View>
        
        {alerts.length > 0 ? (
          alerts.slice(0, 3).map((alert, index) => (
            <View key={index} style={styles.alertItem}>
              <Icon 
                name={alert.type === 'critical' ? 'error' : 'warning'} 
                size={16} 
                color={alert.type === 'critical' ? COLORS.error : COLORS.warning} 
              />
              <Text style={styles.alertText}>{alert.message}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.noAlertsText}>No hay alertas activas</Text>
        )}
      </View>
    );
  };

  const renderTemperatureChart = () => {
    if (!dashboardData?.charts?.temperature) return null;

    const data = dashboardData.charts.temperature;
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Temperatura (Últimas 24h)</Text>
        <LineChart
          data={data}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            backgroundColor: COLORS.surface,
            backgroundGradientFrom: COLORS.surface,
            backgroundGradientTo: COLORS.surface,
            decimalPlaces: 1,
            color: (opacity = 1) => `rgba(46, 125, 50, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(33, 33, 33, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForDots: {
              r: '6',
              strokeWidth: '2',
              stroke: COLORS.primary,
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>
    );
  };

  const renderPrecipitationChart = () => {
    if (!dashboardData?.charts?.precipitation) return null;

    const data = dashboardData.charts.precipitation;
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Precipitación (Últimos 7 días)</Text>
        <BarChart
          data={data}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            backgroundColor: COLORS.surface,
            backgroundGradientFrom: COLORS.surface,
            backgroundGradientTo: COLORS.surface,
            decimalPlaces: 1,
            color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(33, 33, 33, ${opacity})`,
          }}
          style={styles.chart}
        />
      </View>
    );
  };

  const renderCropDistributionChart = () => {
    if (!dashboardData?.charts?.crops) return null;

    const data = dashboardData.charts.crops;
    
    return (
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Distribución de Cultivos</Text>
        <PieChart
          data={data}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            backgroundColor: COLORS.surface,
            backgroundGradientFrom: COLORS.surface,
            backgroundGradientTo: COLORS.surface,
            decimalPlaces: 1,
            color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
          }}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
          style={styles.chart}
        />
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard METGO 3D</Text>
        <Text style={styles.headerSubtitle}>Valle de Quillota</Text>
        {lastUpdate && (
          <Text style={styles.lastUpdate}>
            Última actualización: {lastUpdate.toLocaleTimeString()}
          </Text>
        )}
      </View>

      {renderWeatherCard()}
      {renderIrrigationCard()}
      {renderAlertsCard()}
      {renderTemperatureChart()}
      {renderPrecipitationChart()}
      {renderCropDistributionChart()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: COLORS.textSecondary,
  },
  header: {
    padding: 20,
    backgroundColor: COLORS.surface,
    marginBottom: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: 5,
  },
  lastUpdate: {
    fontSize: 12,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: 10,
  },
  card: {
    backgroundColor: COLORS.surface,
    margin: 10,
    padding: 15,
    borderRadius: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardGradient: {
    borderRadius: 10,
    padding: 15,
    margin: -15,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginLeft: 10,
  },
  weatherGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  weatherItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 15,
  },
  weatherValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.surface,
  },
  weatherLabel: {
    fontSize: 12,
    color: COLORS.surface,
    marginTop: 5,
    textAlign: 'center',
  },
  irrigationGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  irrigationItem: {
    alignItems: 'center',
  },
  irrigationValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.info,
  },
  irrigationLabel: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 5,
    textAlign: 'center',
  },
  alertItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  alertText: {
    fontSize: 14,
    color: COLORS.text,
    marginLeft: 10,
    flex: 1,
  },
  noAlertsText: {
    fontSize: 14,
    color: COLORS.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});

export default DashboardScreen;



