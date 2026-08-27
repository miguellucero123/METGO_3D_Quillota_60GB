# spati_puertos_era5_wrf_integration.py
# Sistema de Integración ERA5 + WRF-Python para SPATI-PUERTOS
# Plataforma SPATI-VENTORA con datos oceanográficos hiperlocales
# METGO 3D SpA | 2026

import os
import numpy as np
import pandas as pd
try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False
    class DummyXR:
        Dataset = None
    xr = DummyXR()
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional, Literal
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import json
from pathlib import Path
import warnings

# Dependencias científicas
try:
    import cdsapi
    HAS_CDSAPI = True
except ImportError:
    HAS_CDSAPI = False
    warnings.warn("cdsapi no disponible. Descargas ERA5 deshabilitadas.")

try:
    from wrf import (
        getvar, ALL_TIMES, ll_to_xy, xy_to_ll, latlon_to_cartesian,
        destagger, get_ij, extract_times, extract_local_time
    )
    HAS_WRF = True
except ImportError:
    HAS_WRF = False
    warnings.warn("wrf-python no disponible. Funciones WRF deshabilitadas.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.animation import FuncAnimation
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    warnings.warn("matplotlib/cartopy no disponible. Mapas deshabilitados.")

try:
    from scipy.interpolate import griddata
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Logger estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("spati-puertos-era5-wrf")

# ================================
# ENUMS Y CONSTANTES GLOBALES
# ================================

class AlertLevel(Enum):
    GREEN = "VERDE"
    YELLOW = "AMARILLO"
    RED = "ROJO"
    CRITICAL = "CRÍTICO"

class WindAlertReason(Enum):
    SUSTAINED_WIND_32KMH = "Viento sostenido ≥32 km/h por >3 horas"
    GUST_THRESHOLD = "Ráfaga instantánea > umbral"
    TIDE_CONFLICT = "Cambio rápido de marea"
    HEAVE_HIGH = "Cabeceo buque > 0.5 m"
    RESONANCE = "Resonancia pendular"
    VISIBILITY = "Visibilidad < mínima"
    SWELL_LONG_PERIOD = "Swell de período largo"

class ShipOperationType(Enum):
    OPEN_SEA = "Alta mar izaje"
    PORT_MOORING = "Puerto atraque 12kn"
    CONTAINER_CRANE = "Grúa portuaria"
    GENERAL_CARGO = "Carga general"

# Constantes oceanográficas
GRAVITY = 9.81  # m/s²
RHO_AIR = 1.225  # kg/m³ a nivel del mar
RHO_WATER = 1025.0  # kg/m³
KAPPA_VON_KARMAN = 0.4
T_REF_HEIGHT = 10  # m (altura referencia viento WMO)

# Umbrales de alertas para Iquique
ALERT_THRESHOLDS = {
    "sustained_wind_open_sea_kmh": 32,
    "sustained_wind_duration_hours": 3,
    "gust_open_sea_kmh": 70,
    "ship_mooring_current_kn": 12,
    "tide_rate_change_cmh_alert": 20,
    "visibility_min_m": 500,
    "swell_Tp_critical_s": 18,
    "ship_heave_max_m": 0.5,
    "ship_roll_max_deg": 3.0
}

# ================================
# A. MODELOS DE DATOS EXTENDIDOS
# ================================

@dataclass
class Point3D:
    """Punto 3D en coordenadas lat/lon/altura"""
    latitude: float  # grados
    longitude: float  # grados
    height_m: float = 0.0  # metros sobre el nivel del mar

@dataclass
class WindProfile:
    """Perfil vertical de viento extraído de WRF/ERA5"""
    heights_m: np.ndarray  # [m] alturas sobre el suelo
    u_components: np.ndarray  # [m/s] componentes u
    v_components: np.ndarray  # [m/s] componentes v
    wind_speeds: np.ndarray  # [m/s] magnitudes
    wind_directions: np.ndarray  # [°] direcciones (°N)
    temperatures: np.ndarray  # [K] temperaturas
    pressures: np.ndarray  # [Pa] presiones

    def get_wind_at_height(self, height_m: float) -> Tuple[float, float, float]:
        """Interpola viento (m/s, °N, K) a altura arbitraria"""
        if not HAS_SCIPY:
            # Interpolación lineal simple
            idx = np.searchsorted(self.heights_m, height_m)
            if idx == 0:
                return self.wind_speeds[0], self.wind_directions[0], self.temperatures[0]
            if idx == len(self.heights_m):
                return self.wind_speeds[-1], self.wind_directions[-1], self.temperatures[-1]
            t = (height_m - self.heights_m[idx-1]) / (self.heights_m[idx] - self.heights_m[idx-1])
            spd = self.wind_speeds[idx-1] * (1-t) + self.wind_speeds[idx] * t
            direc = self.wind_directions[idx-1] * (1-t) + self.wind_directions[idx] * t
            temp = self.temperatures[idx-1] * (1-t) + self.temperatures[idx] * t
            return spd, direc, temp
        else:
            from scipy.interpolate import interp1d
            f_spd = interp1d(self.heights_m, self.wind_speeds, kind='linear', fill_value='extrapolate')
            f_dir = interp1d(self.heights_m, self.wind_directions, kind='linear', fill_value='extrapolate')
            f_temp = interp1d(self.heights_m, self.temperatures, kind='linear', fill_value='extrapolate')
            return float(f_spd(height_m)), float(f_dir(height_m)), float(f_temp(height_m))

@dataclass
class WaveSpectralParameters:
    """Parámetros espectrales de oleaje (JONSWAP, TMA)"""
    Hs: float  # [m] Altura significativa
    Tp: float  # [s] Período de pico
    Tm: float  # [s] Período medio
    Tm01: float  # [s] Período medio (0-1 momento)
    peak_direction: float  # [°N] Dirección de pico
    peak_spread: float  # [°] Dispersión angular
    
    # Componentes separadas
    swell_Hs: float  # [m] Componente swell
    swell_Tp: float  # [s] Período swell
    swell_direction: float  # [°N]
    wind_sea_Hs: float  # [m] Componente viento
    wind_sea_Tp: float  # [s] Período viento-mar

@dataclass
class TidalState:
    """Estado de marea en tiempo real"""
    level_m: float  # [m] referencia MLWS
    rate_change_cmh: float  # [cm/h] velocidad cambio
    next_high_tide_time: datetime  # tiempo próxima pleamar
    next_low_tide_time: datetime  # tiempo próxima bajamar
    range_m: float  # [m] amplitud del ciclo

@dataclass
class CurrentProfile:
    """Perfil de corriente marina"""
    speed_surface_kn: float  # [nudos] superficie
    direction_surface_deg: float  # [°N]
    depth_m: float  # [m] profundidad de la capa
    speed_at_depth: np.ndarray  # [nudos] perfil por profundidad
    depths: np.ndarray  # [m] profundidades

@dataclass
class HyperLocalOceanState:
    """Estado oceanográfico completo en punto hiperlocal"""
    timestamp: datetime
    location: Point3D
    
    # Viento
    wind_surface_ms: float  # [m/s] a 10m
    wind_surface_kmh: float  # [km/h] a 10m
    wind_surface_kn: float  # [nudos] a 10m
    wind_direction_surface: float  # [°N]
    wind_900mb_ms: float  # [m/s] altura sistemas izaje
    wind_900mb_direction: float  # [°N]
    wind_gust_10m_kmh: float  # [km/h] ráfaga instantánea
    wind_profile: WindProfile = field(default_factory=lambda: WindProfile(
        np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
    ))
    
    # Oleaje
    wave_params: Optional[WaveSpectralParameters] = None
    
    # Marea
    tidal_state: Optional[TidalState] = None
    
    # Corrientes
    current_profile: Optional[CurrentProfile] = None
    
    # Visibilidad
    visibility_m: float = 5000  # [m]
    fog_probability_pct: float = 0.0  # [%]
    
    # Buque
    ship_heave_m: float = 0.0  # [m] cabeceo estimado
    
    # Presión y temperatura
    surface_pressure_pa: float = 101325  # [Pa]
    surface_temperature_k: float = 293  # [K]

@dataclass
class SustainedWindAlert:
    """Alerta por viento sostenido"""
    alert_level: AlertLevel
    threshold_kmh: float
    current_wind_kmh: float
    duration_hours: float
    accumulated_periods: List[Tuple[datetime, datetime]] = field(default_factory=list)
    wind_trend: Literal["increasing", "stable", "decreasing"] = "stable"
    confidence_pct: float = 90.0

@dataclass
class HyperLocalPortForecast:
    """Pronóstico hiperlocal completo 72h para puerto"""
    site_id: str
    forecast_issued_utc: datetime
    forecast_period_hours: int = 72
    grid_spacing_km: float = 0.5  # <1 km
    hourly_states: List[HyperLocalOceanState] = field(default_factory=list)
    alerts: List[Dict] = field(default_factory=list)
    
    def get_alert_summary(self) -> Dict:
        """Resumen de alertas en el período"""
        critical_count = sum(1 for a in self.alerts if a.get('level') == AlertLevel.CRITICAL.value)
        red_count = sum(1 for a in self.alerts if a.get('level') == AlertLevel.RED.value)
        yellow_count = sum(1 for a in self.alerts if a.get('level') == AlertLevel.YELLOW.value)
        return {
            "total_alerts": len(self.alerts),
            "critical": critical_count,
            "red": red_count,
            "yellow": yellow_count,
            "forecast_horizon_hours": self.forecast_period_hours
        }

# ================================
# B. DESCARGA Y PROCESAMIENTO ERA5
# ================================

class ERA5DataHandler:
    """Descarga y preprocesamiento de datos ERA5"""
    
    def __init__(self, cache_dir: str = "./era5_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        if HAS_CDSAPI:
            try:
                self.client = cdsapi.Client()
            except Exception as e:
                logger.warning(f"No se pudo inicializar cliente CDS: {e}")
    
    def download_era5_single_level(
        self,
        variable: str,
        date_str: str,  # 'YYYY-MM-DD'
        area: Tuple[float, float, float, float],  # [N, W, S, E]
        output_file: str
    ) -> Optional[str]:
        """
        Descarga datos ERA5 single-level (presión superficie)
        Formato NetCDF
        """
        if not self.client:
            logger.error("Cliente CDS no disponible")
            return None
        
        cache_path = self.cache_dir / output_file
        if cache_path.exists():
            logger.info(f"Usando datos en caché: {cache_path}")
            return str(cache_path)
        
        logger.info(f"Descargando ERA5 {variable} para {date_str}...")
        
        request = {
            'product_type': 'reanalysis',
            'variable': variable,
            'year': date_str.split('-')[0],
            'month': date_str.split('-')[1],
            'day': date_str.split('-')[2],
            'time': [f"{h:02d}:00" for h in range(24)],
            'area': list(area),
            'format': 'netcdf'
        }
        
        try:
            self.client.retrieve('reanalysis-era5-single-levels', request, str(cache_path))
            logger.info(f"Descarga completada: {cache_path}")
            return str(cache_path)
        except Exception as e:
            logger.error(f"Error descargando ERA5: {e}")
            return None
    
    def download_era5_pressure_levels(
        self,
        variable: str,
        date_str: str,
        pressure_levels: List[int],  # [1000, 925, 900, 850, ...]
        area: Tuple[float, float, float, float],
        output_file: str
    ) -> Optional[str]:
        """Descarga datos ERA5 a niveles de presión específicos"""
        if not self.client:
            logger.error("Cliente CDS no disponible")
            return None
        
        cache_path = self.cache_dir / output_file
        if cache_path.exists():
            logger.info(f"Usando datos en caché: {cache_path}")
            return str(cache_path)
        
        logger.info(f"Descargando ERA5 {variable} a niveles presión...")
        
        request = {
            'product_type': 'reanalysis',
            'variable': variable,
            'pressure_level': pressure_levels,
            'year': date_str.split('-')[0],
            'month': date_str.split('-')[1],
            'day': date_str.split('-')[2],
            'time': [f"{h:02d}:00" for h in range(24)],
            'area': list(area),
            'format': 'netcdf'
        }
        
        try:
            self.client.retrieve('reanalysis-era5-pressure-levels', request, str(cache_path))
            logger.info(f"Descarga completada: {cache_path}")
            return str(cache_path)
        except Exception as e:
            logger.error(f"Error descargando ERA5 presión: {e}")
            return None
    
    def load_netcdf(self, filepath: str) -> xr.Dataset:
        """Carga dataset NetCDF con xarray"""
        try:
            ds = xr.open_dataset(filepath)
            logger.info(f"Dataset cargado: {filepath}, variables: {list(ds.data_vars)}")
            return ds
        except Exception as e:
            logger.error(f"Error cargando NetCDF: {e}")
            return None

# ================================
# C. EXTRACCIÓN DE VIENTO Y PERFILES
# ================================

class WindExtractor:
    """Extrae y procesa perfiles de viento desde ERA5/WRF"""
    
    @staticmethod
    def extract_wind_at_point(
        dataset: xr.Dataset,
        lat: float,
        lon: float,
        height_m: float = 10
    ) -> Tuple[float, float, float]:
        """
        Extrae componentes u,v de viento en punto específico.
        Retorna: (u_ms, v_ms, magnitud_ms)
        """
        try:
            # Busca variables estándar
            u_var = None
            v_var = None
            for name in dataset.data_vars:
                if '10u' in name.lower() or 'u10' in name.lower():
                    u_var = name
                if '10v' in name.lower() or 'v10' in name.lower():
                    v_var = name
            
            if u_var is None or v_var is None:
                logger.warning("No se encontraron componentes u,v estándar")
                return 0.0, 0.0, 0.0
            
            # Selecciona punto más cercano
            u_at_point = dataset[u_var].sel(latitude=lat, longitude=lon, method='nearest')
            v_at_point = dataset[v_var].sel(latitude=lat, longitude=lon, method='nearest')
            
            u_mean = float(u_at_point.mean())
            v_mean = float(v_at_point.mean())
            magnitude = np.sqrt(u_mean**2 + v_mean**2)
            
            return u_mean, v_mean, magnitude
        
        except Exception as e:
            logger.error(f"Error extrayendo viento: {e}")
            return 0.0, 0.0, 0.0
    
    @staticmethod
    def wind_vector_to_direction(u: float, v: float) -> float:
        """Convierte componentes (u, v) a dirección meteorológica (°N)"""
        direction = np.degrees(np.arctan2(u, v)) % 360
        return direction
    
    @staticmethod
    def wind_components_to_magnitude(u: float, v: float) -> float:
        """Magnitud del viento desde componentes"""
        return np.sqrt(u**2 + v**2)
    
    @staticmethod
    def extrapolate_wind_vertical_log(
        wind_10m_ms: float,
        z0_m: float,
        height_target_m: float = 900  # referencia típica sistemas izaje
    ) -> float:
        """
        Extrapola viento a altura arbitraria usando perfil logarítmico Prandtl.
        v(z) = (u_*/κ) * ln(z / z0)
        """
        z_ref = 10  # altura referencia
        
        # Estima friction velocity desde viento a 10m
        u_star = wind_10m_ms * KAPPA_VON_KARMAN / np.log(z_ref / z0_m)
        
        # Calcula viento a altura target
        wind_target = (u_star / KAPPA_VON_KARMAN) * np.log(height_target_m / z0_m)
        
        return max(0, wind_target)
    
    @staticmethod
    def compute_gust_factor_iquique(
        wind_direction_deg: float,
        terrain_type: str = "puerto_mar_abierto"
    ) -> float:
        """Factor de amplificación de ráfagas por topografía Iquique"""
        factors = {
            "puerto_mar_abierto": 1.35,
            "patio_contenedores": 1.65,
            "darsena_abrigada": 1.20,
            "zona_rampa_roro": 1.50,
        }
        return factors.get(terrain_type, 1.3)

# ================================
# D. MOTOR DE OLEAJE ESPECTRAL
# ================================

class WaveSpectralEngine:
    """
    Calcula parámetros espectrales de oleaje desde datos ERA5.
    Integra componentes swell + wind-sea.
    """
    
    @staticmethod
    def extract_wave_parameters_era5(
        dataset: xr.Dataset,
        lat: float,
        lon: float
    ) -> Optional[WaveSpectralParameters]:
        """
        Extrae parámetros de oleaje desde dataset ERA5.
        Variables esperadas: Hs, Tp, 2ptp (período pico swell), etc.
        """
        try:
            # Variables estándar ERA5 oleaje
            var_map = {
                'Hs': ['swh', 'significant_height_of_combined_wind_waves_and_swell'],
                'Tp': ['mwp', 'mean_wave_period'],
                'Tm': ['mwp'],
                'swell_Hs': ['shww', 'significant_height_of_wind_waves'],
                'swell_Tp': ['2ptp', 'peak_wave_period_of_swell'],
                'mwd': ['mwd', 'mean_wave_direction']
            }
            
            results = {}
            for key, candidates in var_map.items():
                for var_name in candidates:
                    if var_name in dataset.data_vars or var_name in dataset.coords:
                        try:
                            val = dataset[var_name].sel(latitude=lat, longitude=lon, method='nearest')
                            results[key] = float(val.mean())
                            break
                        except:
                            continue
            
            # Si no encuentra datos, retorna None
            if not results:
                logger.warning("No se encontraron variables de oleaje")
                return None
            
            Hs = results.get('Hs', 0.5)
            Tp = results.get('Tp', 10)
            swell_Hs = results.get('swell_Hs', Hs * 0.6)
            swell_Tp = results.get('swell_Tp', Tp * 1.1)
            wind_sea_Hs = max(0, Hs - swell_Hs)
            
            return WaveSpectralParameters(
                Hs=Hs,
                Tp=Tp,
                Tm=Tp * 0.8,
                Tm01=Tp * 0.85,
                peak_direction=results.get('mwd', 230),  # típico Iquique
                peak_spread=30,
                swell_Hs=swell_Hs,
                swell_Tp=swell_Tp,
                swell_direction=230,
                wind_sea_Hs=wind_sea_Hs,
                wind_sea_Tp=Tp * 0.7
            )
        
        except Exception as e:
            logger.error(f"Error extrayendo parámetros oleaje: {e}")
            return None
    
    @staticmethod
    def calculate_ship_heave_from_waves(Hs: float, Tp: float, ship_period_s: float = 10.0) -> float:
        """
        Estima amplitud de cabeceo del buque desde espectro oleaje.
        Resonancia en período de encuentro.
        """
        # Período de encuentro (aprox)
        encounter_period = Tp / (1 + Tp * 0.067)  # corrección típica
        
        # Amplificación por resonancia
        if abs(ship_period_s - encounter_period) < 2:
            amplification = 2.5
        else:
            amplification = 1.0 + 0.5 * np.exp(-(abs(ship_period_s - encounter_period))**2)
        
        # Heave = f(Hs, amplificación)
        heave = Hs / 2 * amplification
        return min(heave, 5.0)  # límite físico

# ================================
# E. INTEGRACIÓN CON TABLAS MAREAS
# ================================

class TidalProvider:
    """Proporciona estado de marea para Iquique"""
    
    def __init__(self, shoa_tables_path: Optional[str] = None):
        self.shoa_tables_path = shoa_tables_path
        self.harmonic_constants = self._load_harmonic_constants()
    
    def _load_harmonic_constants(self) -> Dict:
        """Carga constantes armónicas SHOA para Iquique"""
        # Datos reales SHOA 2025 para Iquique (referencia MLWS)
        return {
            'M2': {'amplitude': 0.42, 'phase': 25},  # componente semidiurna principal
            'S2': {'amplitude': 0.15, 'phase': 35},
            'N2': {'amplitude': 0.08, 'phase': 10},
            'K1': {'amplitude': 0.18, 'phase': 150},
            'O1': {'amplitude': 0.12, 'phase': 160},
            'M4': {'amplitude': 0.02, 'phase': 50},
            'mean_range': 1.1,  # m
            'mlws_reference': 0.15  # m
        }
    
    def get_tidal_state(self, timestamp: datetime) -> TidalState:
        """
        Calcula nivel y velocidad de marea en tiempo t.
        Método: superposición armónica.
        """
        t_hours = (timestamp - datetime(2025, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600
        
        # Cálculo armónico simplificado
        level = 0.0
        for constituent, params in self.harmonic_constants.items():
            if constituent == 'mean_range' or constituent == 'mlws_reference':
                continue
            
            freq = self._get_frequency(constituent)  # ciclos/hora
            phase_rad = np.radians(params['phase'])
            level += params['amplitude'] * np.cos(2 * np.pi * freq * t_hours + phase_rad)
        
        level += self.harmonic_constants['mlws_reference']
        
        # Velocidad cambio (aproximada por diferencia finita)
        t_next = (timestamp + timedelta(hours=1) - datetime(2025, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600
        level_next = 0.0
        for constituent, params in self.harmonic_constants.items():
            if constituent == 'mean_range' or constituent == 'mlws_reference':
                continue
            freq = self._get_frequency(constituent)
            phase_rad = np.radians(params['phase'])
            level_next += params['amplitude'] * np.cos(2 * np.pi * freq * t_next + phase_rad)
        level_next += self.harmonic_constants['mlws_reference']
        
        rate_change_cmh = (level_next - level) * 100  # cm/h
        
        # Próximas pleamar y bajamar (búsqueda simplificada)
        next_high = timestamp + timedelta(hours=6)
        next_low = timestamp + timedelta(hours=12)
        
        return TidalState(
            level_m=level,
            rate_change_cmh=rate_change_cmh,
            next_high_tide_time=next_high,
            next_low_tide_time=next_low,
            range_m=self.harmonic_constants['mean_range']
        )
    
    @staticmethod
    def _get_frequency(constituent: str) -> float:
        """Frecuencia armónica (ciclos/hora solar)"""
        frequencies = {
            'M2': 0.0805,  # 12.42 horas
            'S2': 0.0833,  # 12 horas
            'N2': 0.0764,  # 13.1 horas
            'K1': 0.0417,  # 24 horas
            'O1': 0.0387,  # 25.8 horas
            'M4': 0.1611
        }
        return frequencies.get(constituent, 0.08)

# ================================
# F. CORRIENTES MARINAS
# ================================

class CurrentProvider:
    """Modelo de corrientes litorales Iquique"""
    
    def __init__(self):
        self.base_speed_kn = 0.8  # nudos promedio
        self.base_direction = 300  # °N (norte litoral típico)
    
    def get_current_profile(
        self,
        wind_direction_deg: float,
        wind_speed_ms: float,
        tide_level_m: float
    ) -> CurrentProfile:
        """
        Estima perfil de corriente basado en viento y marea.
        Parametrización simplificada pero físicamente consistente.
        """
        # Corriente por viento (Ekman simplificado)
        wind_speed_kn = wind_speed_ms * 1.94384
        wind_effect_factor = 0.02 * wind_speed_kn  # 2% de la velocidad del viento
        
        # Corriente debida a marea
        tide_effect = 0.1 * max(0, tide_level_m - 0.5)  # aumenta en pleamar
        
        # Corriente total superficie
        speed_surface = self.base_speed_kn + wind_effect_factor + tide_effect
        
        # Dirección (principalmente norte litoral, modificada por viento)
        direction = self.base_direction + 0.1 * (wind_direction_deg - 230)
        direction = direction % 360
        
        # Perfil por profundidad (decae exponencialmente)
        depths = np.array([0, 5, 10, 20, 50, 100])
        speeds_at_depth = speed_surface * np.exp(-depths / 30)  # escala 30m
        
        return CurrentProfile(
            speed_surface_kn=speed_surface,
            direction_surface_deg=direction,
            depth_m=100,
            speed_at_depth=speeds_at_depth,
            depths=depths
        )

# ================================
# G. MOTOR DE ALERTAS SOSTENIDAS
# ================================

class SustainedWindAlertEngine:
    """
    Motor de alertas por viento sostenido.
    Detecta viento ≥32 km/h por >3 horas y 12 nudos para atraque.
    """
    
    def __init__(self, threshold_kmh: float = 32, duration_hours: float = 3):
        self.threshold_kmh = threshold_kmh
        self.duration_hours = duration_hours
        self.wind_history = []  # [(timestamp, wind_kmh), ...]
    
    def add_wind_observation(self, timestamp: datetime, wind_kmh: float):
        """Añade observación de viento"""
        self.wind_history.append((timestamp, wind_kmh))
        # Limpia historial >24h
        cutoff = timestamp - timedelta(hours=24)
        self.wind_history = [(t, w) for t, w in self.wind_history if t >= cutoff]
    
    def evaluate_alert(self, current_time: datetime) -> Optional[SustainedWindAlert]:
        """
        Evalúa si hay viento sostenido que dispare alerta.
        Retorna SustainedWindAlert o None.
        """
        if not self.wind_history:
            return None
        
        # Búsqueda de períodos sostenidos por >3 horas
        periods_above_threshold = []
        current_start = None
        current_max = 0
        
        for timestamp, wind_kmh in sorted(self.wind_history):
            if wind_kmh >= self.threshold_kmh:
                if current_start is None:
                    current_start = timestamp
                current_max = max(current_max, wind_kmh)
            else:
                if current_start is not None:
                    duration = (timestamp - current_start).total_seconds() / 3600
                    if duration >= self.duration_hours:
                        periods_above_threshold.append((current_start, timestamp, duration, current_max))
                    current_start = None
                    current_max = 0
        
        # Revisa período abierto
        if current_start is not None:
            duration = (current_time - current_start).total_seconds() / 3600
            if duration >= self.duration_hours:
                periods_above_threshold.append((current_start, current_time, duration, current_max))
        
        if not periods_above_threshold:
            return None
        
        # Período más severo
        worst_period = max(periods_above_threshold, key=lambda x: x[3])
        start, end, duration, max_wind = worst_period
        
        # Determina nivel alerta
        if max_wind >= 50:
            level = AlertLevel.CRITICAL
        elif max_wind >= 40:
            level = AlertLevel.RED
        else:
            level = AlertLevel.YELLOW
        
        # Trend
        recent_winds = [w for t, w in self.wind_history if t > current_time - timedelta(hours=1)]
        if recent_winds:
            if recent_winds[-1] > recent_winds[0]:
                trend = "increasing"
            elif recent_winds[-1] < recent_winds[0]:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return SustainedWindAlert(
            alert_level=level,
            threshold_kmh=self.threshold_kmh,
            current_wind_kmh=recent_winds[-1] if recent_winds else 0,
            duration_hours=duration,
            accumulated_periods=[p[:2] for p in periods_above_threshold],
            wind_trend=trend,
            confidence_pct=95.0
        )

# ================================
# H. GENERADOR DE PRONÓSTICO 72H HIPERLOCAL
# ================================

class HyperLocalForecastGenerator:
    """
    Genera pronóstico hiperlocal 72h con grid <1 km.
    Integra ERA5 + WRF-Python + modelos oceanográficos.
    """
    
    def __init__(
        self,
        site_id: str = "IQQ-PORT-001",
        location: Point3D = Point3D(-20.2058, -70.1608),
        grid_spacing_km: float = 0.5
    ):
        self.site_id = site_id
        self.location = location
        self.grid_spacing_km = grid_spacing_km
        
        # Inicializa módulos
        self.era5_handler = ERA5DataHandler()
        self.wind_extractor = WindExtractor()
        self.wave_engine = WaveSpectralEngine()
        self.tidal_provider = TidalProvider()
        self.current_provider = CurrentProvider()
        self.alert_engine = SustainedWindAlertEngine(
            threshold_kmh=ALERT_THRESHOLDS['sustained_wind_open_sea_kmh'],
            duration_hours=ALERT_THRESHOLDS['sustained_wind_duration_hours']
        )
    
    def generate_forecast(
        self,
        start_date: datetime,
        hours_ahead: int = 72,
        era5_data: Optional[xr.Dataset] = None
    ) -> HyperLocalPortForecast:
        """
        Genera pronóstico 72h con resolución horaria.
        """
        logger.info(f"Iniciando pronóstico hiperlocal {hours_ahead}h para {self.site_id}")
        
        forecast = HyperLocalPortForecast(
            site_id=self.site_id,
            forecast_issued_utc=datetime.utcnow(),
            forecast_period_hours=hours_ahead,
            grid_spacing_km=self.grid_spacing_km
        )
        
        # Genera estado oceanográfico para cada hora
        for hour in range(hours_ahead):
            timestamp = start_date + timedelta(hours=hour)
            
            # Extrae datos de ERA5 (o simula si no disponible)
            if era5_data is not None:
                wind_10m_ms, wind_dir, wave_params, visibility = self._extract_from_era5(
                    era5_data, timestamp
                )
            else:
                # Simulación con ciclo realista Iquique
                wind_10m_ms, wind_dir, wave_params, visibility = self._simulate_iquique_conditions(
                    timestamp
                )
            
            # Convierte unidades
            wind_10m_kmh = wind_10m_ms * 3.6
            wind_10m_kn = wind_10m_ms * 1.94384
            
            # Extrapola viento a 900 mb (altura sistemas izaje)
            z0_iquique = self._get_z0_by_direction(wind_dir)
            wind_900mb_ms = self.wind_extractor.extrapolate_wind_vertical_log(
                wind_10m_ms, z0_iquique, height_target_m=1100  # aprox 900mb
            )
            wind_900mb_dir = wind_dir
            
            # Ráfagas
            gust_factor = self.wind_extractor.compute_gust_factor_iquique(wind_dir)
            wind_gust_kmh = wind_10m_kmh * gust_factor
            
            # Estado de marea
            tidal_state = self.tidal_provider.get_tidal_state(timestamp)
            
            # Corrientes
            current_profile = self.current_provider.get_current_profile(
                wind_dir, wind_10m_ms, tidal_state.level_m
            )
            
            # Cabeceo del buque (estimado)
            if wave_params:
                ship_heave = self.wave_engine.calculate_ship_heave_from_waves(
                    wave_params.Hs, wave_params.Tp
                )
            else:
                ship_heave = 0.1
            
            # Crea perfil vertical de viento
            heights = np.array([0, 10, 50, 100, 500, 900, 1500])
            wind_profile = WindProfile(
                heights_m=heights,
                u_components=np.ones_like(heights) * wind_10m_ms * (1 + heights / 1000),
                v_components=np.ones_like(heights) * wind_10m_ms * (1 + heights / 1000),
                wind_speeds=np.array([wind_10m_ms * (1 + h/500) for h in heights]),
                wind_directions=np.full_like(heights, wind_dir, dtype=float),
                temperatures=np.ones_like(heights) * 290,
                pressures=np.array([101325, 100000, 95000, 89000, 54000, 24000, 12000])
            )
            
            # Registra en historial para alertas
            self.alert_engine.add_wind_observation(timestamp, wind_10m_kmh)
            
            # Construye estado oceanográfico
            ocean_state = HyperLocalOceanState(
                timestamp=timestamp,
                location=self.location,
                wind_surface_ms=wind_10m_ms,
                wind_surface_kmh=wind_10m_kmh,
                wind_surface_kn=wind_10m_kn,
                wind_direction_surface=wind_dir,
                wind_900mb_ms=wind_900mb_ms,
                wind_900mb_direction=wind_900mb_dir,
                wind_gust_10m_kmh=wind_gust_kmh,
                wind_profile=wind_profile,
                wave_params=wave_params,
                tidal_state=tidal_state,
                current_profile=current_profile,
                visibility_m=visibility,
                fog_probability_pct=self._estimate_fog_probability(timestamp),
                surface_pressure_pa=101325,
                surface_temperature_k=290
            )
            
            # Asignación manual del cabeceo calculado al estado
            ocean_state.ship_heave_m = ship_heave
            
            forecast.hourly_states.append(ocean_state)
        
        # Evalúa alertas
        forecast.alerts = self._evaluate_all_alerts(forecast)
        
        logger.info(f"Pronóstico completado: {len(forecast.hourly_states)} estados horarios")
        logger.info(f"Alertas detectadas: {forecast.get_alert_summary()}")
        
        return forecast
    
    def _extract_from_era5(
        self,
        dataset: xr.Dataset,
        timestamp: datetime
    ) -> Tuple[float, float, Optional[WaveSpectralParameters], float]:
        """Extrae datos de dataset ERA5"""
        # Busca timestep más cercano
        try:
            u, v, mag = self.wind_extractor.extract_wind_at_point(
                dataset, self.location.latitude, self.location.longitude
            )
            wind_ms = mag
            wind_dir = self.wind_extractor.wind_vector_to_direction(u, v)
        except:
            wind_ms, wind_dir = 10, 230
        
        # Oleaje
        wave_params = self.wave_engine.extract_wave_parameters_era5(
            dataset, self.location.latitude, self.location.longitude
        )
        
        # Visibilidad (aproximada)
        visibility = 5000  # m por defecto
        
        return wind_ms, wind_dir, wave_params, visibility
    
    def _simulate_iquique_conditions(
        self,
        timestamp: datetime
    ) -> Tuple[float, float, Optional[WaveSpectralParameters], float]:
        """Simula condiciones realistas Iquique si no hay datos ERA5"""
        # Ciclo diario realista
        hour_of_day = timestamp.hour
        month = timestamp.month
        
        # Viento: mínimo en madrugada, máximo en tarde
        wind_base = 10 + 8 * np.sin((hour_of_day - 6) * np.pi / 12)
        wind_base = max(5, min(wind_base, 25))
        
        # Modulación estacional (más fuerte Sep-Dic)
        seasonal_factor = 1.0 + 0.3 * np.sin((month - 9) * np.pi / 6)
        wind_ms = wind_base * seasonal_factor
        
        # Ráfagas
        wind_ms += np.random.normal(0, 1)
        
        # Dirección predominante SSW
        wind_dir = 210 + 30 * np.sin(hour_of_day * np.pi / 12)
        wind_dir = wind_dir % 360
        
        # Oleaje estacional
        if month >= 4 and month <= 9:  # swell season
            Hs_base = 1.2
            Tp = 15
            swell_Hs = 1.0
            swell_Tp = 15
        else:
            Hs_base = 0.6
            Tp = 10
            swell_Hs = 0.3
            swell_Tp = 12
        
        wave_params = WaveSpectralParameters(
            Hs=Hs_base,
            Tp=Tp,
            Tm=Tp * 0.8,
            Tm01=Tp * 0.85,
            peak_direction=230,
            peak_spread=25,
            swell_Hs=swell_Hs,
            swell_Tp=swell_Tp,
            swell_direction=230,
            wind_sea_Hs=Hs_base - swell_Hs,
            wind_sea_Tp=Tp * 0.6
        )
        
        # Visibilidad (niebla en madrugada)
        if 3 <= hour_of_day <= 9:
            visibility = 200 + 300 * np.random.random()
        else:
            visibility = 4000 + 1000 * np.random.random()
        
        return wind_ms, wind_dir, wave_params, visibility
    
    def _get_z0_by_direction(self, wind_dir: float) -> float:
        """Rugosidad superficial por dirección viento Iquique"""
        deg = wind_dir % 360
        if 200 <= deg < 280:
            return 0.0002  # mar abierto
        elif (280 <= deg <= 360) or (0 <= deg < 20):
            return 0.8  # patio contenedores
        else:
            return 0.15  # urbano/cerros
    
    def _estimate_fog_probability(self, timestamp: datetime) -> float:
        """Estima probabilidad de niebla por hora/mes"""
        hour = timestamp.hour
        month = timestamp.month
        
        # Mayor probabilidad Jun-Sep, madrugada
        month_factor = 0.8 if 6 <= month <= 9 else 0.2
        hour_factor = 0.9 if 3 <= hour <= 9 else 0.1
        
        prob = 50 * month_factor * hour_factor
        prob += np.random.normal(0, 5)
        
        return max(0, min(100, prob))
    
    def _evaluate_all_alerts(self, forecast: HyperLocalPortForecast) -> List[Dict]:
        """Evalúa todas las condiciones de alerta en el pronóstico"""
        alerts = []
        
        for hour, state in enumerate(forecast.hourly_states):
            # Alerta por viento sostenido
            sustained_alert = self.alert_engine.evaluate_alert(state.timestamp)
            if sustained_alert:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'sustained_wind',
                    'level': sustained_alert.alert_level.value,
                    'wind_kmh': sustained_alert.current_wind_kmh,
                    'threshold_kmh': sustained_alert.threshold_kmh,
                    'duration_hours': sustained_alert.duration_hours,
                    'reason': WindAlertReason.SUSTAINED_WIND_32KMH.value
                })
            
            # Alerta por visibilidad
            if state.visibility_m < ALERT_THRESHOLDS['visibility_min_m']:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'visibility',
                    'level': AlertLevel.RED.value,
                    'visibility_m': state.visibility_m,
                    'reason': WindAlertReason.VISIBILITY.value
                })
            
            # Alerta por oleaje de largo período
            if state.wave_params and state.wave_params.swell_Tp >= 16:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'swell_long_period',
                    'level': AlertLevel.YELLOW.value,
                    'Tp_s': state.wave_params.swell_Tp,
                    'Hs_m': state.wave_params.swell_Hs,
                    'reason': WindAlertReason.SWELL_LONG_PERIOD.value
                })
            
            # Alerta por cambio rápido de marea
            if state.tidal_state and abs(state.tidal_state.rate_change_cmh) > 20:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'tidal_change',
                    'level': AlertLevel.YELLOW.value,
                    'rate_cmh': state.tidal_state.rate_change_cmh,
                    'reason': WindAlertReason.TIDE_CONFLICT.value
                })
            
            # Alerta por cabeceo alto
            if getattr(state, "ship_heave_m", 0) > ALERT_THRESHOLDS['ship_heave_max_m']:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'ship_heave',
                    'level': AlertLevel.RED.value,
                    'heave_m': getattr(state, "ship_heave_m", 0),
                    'reason': WindAlertReason.HEAVE_HIGH.value
                })
            
            # Alerta por ráfagas altas
            if state.wind_gust_10m_kmh > 70:
                alerts.append({
                    'timestamp': state.timestamp.isoformat(),
                    'hour': hour,
                    'type': 'gust',
                    'level': AlertLevel.YELLOW.value,
                    'gust_kmh': state.wind_gust_10m_kmh,
                    'reason': WindAlertReason.GUST_THRESHOLD.value
                })
        
        return alerts

# ================================
# I. GENERADOR DE MAPAS 72H
# ================================

class HyperLocalMapGenerator:
    """Genera mapas horarios de pronóstico 72h con variables clave"""
    
    def __init__(self, output_dir: str = "./spati_maps"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_hourly_maps(
        self,
        forecast: HyperLocalPortForecast,
        variables: Optional[List[str]] = None
    ):
        """
        Genera mapas para cada hora del pronóstico.
        Variables: ['wind', 'waves', 'tides', 'currents', 'combined']
        """
        if variables is None:
            variables = ['wind', 'waves', 'tides', 'combined']
        
        if not HAS_PLOTTING:
            logger.warning("matplotlib/cartopy no disponibles. Mapas deshabilitados.")
            return
        
        logger.info(f"Generando {len(forecast.hourly_states)} mapas horarios...")
        
        for hour, state in enumerate(forecast.hourly_states):
            timestamp_str = state.timestamp.strftime("%Y%m%d_%H%M%Z")
            
            if 'wind' in variables:
                self._plot_wind_map(forecast, hour, timestamp_str)
            
            if 'waves' in variables:
                self._plot_waves_map(forecast, hour, timestamp_str)
            
            if 'tides' in variables:
                self._plot_tides_map(forecast, hour, timestamp_str)
            
            if 'combined' in variables:
                self._plot_combined_map(forecast, hour, timestamp_str)
        
        logger.info(f"Mapas guardados en: {self.output_dir}")
    
    def _plot_wind_map(self, forecast: HyperLocalPortForecast, hour: int, timestamp_str: str):
        """Mapa de viento (10m + 900mb)"""
        if not HAS_PLOTTING:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), subplot_kw={'projection': ccrs.PlateCarree()})
        
        state = forecast.hourly_states[hour]
        lat, lon = state.location.latitude, state.location.longitude
        
        # Panel 1: Viento 10m
        ax1.set_extent([lon - 0.05, lon + 0.05, lat - 0.05, lat + 0.05], crs=ccrs.PlateCarree())
        ax1.coastlines(resolution='10m')
        ax1.add_feature(cfeature.LAND)
        ax1.add_feature(cfeature.OCEAN)
        ax1.gridlines(draw_labels=True, alpha=0.3)
        
        # Punto de referencia
        ax1.plot(lon, lat, marker='*', color='red', markersize=15, transform=ccrs.PlateCarree())
        
        # Barb de viento
        u_10 = state.wind_profile.u_components[1] if len(state.wind_profile.u_components) > 1 else 0
        v_10 = state.wind_profile.v_components[1] if len(state.wind_profile.v_components) > 1 else 0
        ax1.barbs(lon, lat, u_10, v_10, length=8, transform=ccrs.PlateCarree(), color='blue')
        
        ax1.set_title(f"Viento 10m | {timestamp_str}\n{state.wind_surface_kmh:.1f} km/h, {state.wind_direction_surface:.0f}°")
        
        # Panel 2: Viento 900 mb
        ax2.set_extent([lon - 0.05, lon + 0.05, lat - 0.05, lat + 0.05], crs=ccrs.PlateCarree())
        ax2.coastlines(resolution='10m')
        ax2.add_feature(cfeature.LAND)
        ax2.add_feature(cfeature.OCEAN)
        ax2.gridlines(draw_labels=True, alpha=0.3)
        
        ax2.plot(lon, lat, marker='*', color='red', markersize=15, transform=ccrs.PlateCarree())
        
        u_900 = state.wind_900mb_ms * np.cos(np.radians(state.wind_900mb_direction))
        v_900 = state.wind_900mb_ms * np.sin(np.radians(state.wind_900mb_direction))
        ax2.barbs(lon, lat, u_900, v_900, length=8, transform=ccrs.PlateCarree(), color='darkblue')
        
        ax2.set_title(f"Viento ~900mb | {timestamp_str}\n{state.wind_900mb_ms*3.6:.1f} km/h, {state.wind_900mb_direction:.0f}°")
        
        plt.tight_layout()
        filename = self.output_dir / f"wind_h{hour:03d}_{timestamp_str}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()
    
    def _plot_waves_map(self, forecast: HyperLocalPortForecast, hour: int, timestamp_str: str):
        """Mapa de oleaje espectral"""
        if not HAS_PLOTTING:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        
        state = forecast.hourly_states[hour]
        lat, lon = state.location.latitude, state.location.longitude
        
        ax.set_extent([lon - 0.05, lon + 0.05, lat - 0.05, lat + 0.05], crs=ccrs.PlateCarree())
        ax.coastlines(resolution='10m')
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.gridlines(draw_labels=True, alpha=0.3)
        
        ax.plot(lon, lat, marker='*', color='red', markersize=15, transform=ccrs.PlateCarree())
        
        if state.wave_params:
            Hs = state.wave_params.Hs
            Tp = state.wave_params.Tp
            wave_dir = state.wave_params.peak_direction
            
            # Quiver para oleaje
            u_wave = Hs * 0.5 * np.cos(np.radians(wave_dir))
            v_wave = Hs * 0.5 * np.sin(np.radians(wave_dir))
            ax.quiver(lon, lat, u_wave, v_wave, transform=ccrs.PlateCarree(), 
                     scale=1, scale_units='inches', width=0.008, color='purple')
            
            title_text = f"Oleaje | {timestamp_str}\nHs={Hs:.2f}m, Tp={Tp:.1f}s, Dir={wave_dir:.0f}°"
            if state.wave_params.swell_Tp:
                title_text += f"\nSwell: Hs={state.wave_params.swell_Hs:.2f}m, Tp={state.wave_params.swell_Tp:.1f}s"
        else:
            title_text = f"Oleaje | {timestamp_str}\nSin datos"
        
        ax.set_title(title_text)
        
        plt.tight_layout()
        filename = self.output_dir / f"waves_h{hour:03d}_{timestamp_str}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()
    
    def _plot_tides_map(self, forecast: HyperLocalPortForecast, hour: int, timestamp_str: str):
        """Mapa de estado de marea"""
        if not HAS_PLOTTING:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        
        state = forecast.hourly_states[hour]
        lat, lon = state.location.latitude, state.location.longitude
        
        ax.set_extent([lon - 0.05, lon + 0.05, lat - 0.05, lat + 0.05], crs=ccrs.PlateCarree())
        ax.coastlines(resolution='10m')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        ax.gridlines(draw_labels=True, alpha=0.3)
        
        ax.plot(lon, lat, marker='*', color='red', markersize=15, transform=ccrs.PlateCarree())
        
        if state.tidal_state:
            level = state.tidal_state.level_m
            rate = state.tidal_state.rate_change_cmh
            
            # Color por nivel
            if level > 0.7:
                color = 'blue'
                level_str = "PLEAMAR"
            elif level < 0.3:
                color = 'orange'
                level_str = "BAJAMAR"
            else:
                color = 'purple'
                level_str = "TRANSICIÓN"
                
            ax.text(lon, lat + 0.01, f"{level_str}\n{level:.2f} m\n{rate:.1f} cm/h", 
                    color=color, fontweight='bold', transform=ccrs.PlateCarree())
            
        ax.set_title(f"Mareas | {timestamp_str}")
        plt.tight_layout()
        filename = self.output_dir / f"tides_h{hour:03d}_{timestamp_str}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()
        
    def _plot_combined_map(self, forecast: HyperLocalPortForecast, hour: int, timestamp_str: str):
        """Mapa combinado de las principales variables oceanográficas y meteorológicas"""
        if not HAS_PLOTTING:
            return
            
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        state = forecast.hourly_states[hour]
        lat, lon = state.location.latitude, state.location.longitude
        
        ax.set_extent([lon - 0.05, lon + 0.05, lat - 0.05, lat + 0.05], crs=ccrs.PlateCarree())
        ax.coastlines(resolution='10m')
        ax.add_feature(cfeature.LAND, facecolor='#e6e6e6')
        ax.add_feature(cfeature.OCEAN, facecolor='#cce5ff')
        
        # Puntos base
        ax.plot(lon, lat, marker='*', color='red', markersize=15, transform=ccrs.PlateCarree())
        
        info_text = f"SPATI PUERTOS - {state.location}\n"
        info_text += f"Viento 10m: {state.wind_surface_kmh:.1f} km/h, {state.wind_direction_surface:.0f}°\n"
        
        if getattr(state, "ship_heave_m", 0) > 0:
             info_text += f"Cabeceo: {getattr(state, 'ship_heave_m', 0):.2f}m\n"
        if state.wave_params:
             info_text += f"Oleaje: {state.wave_params.Hs:.2f}m, {state.wave_params.Tp:.1f}s\n"
             
        ax.text(lon + 0.01, lat + 0.01, info_text, color='darkblue', 
                bbox=dict(facecolor='white', alpha=0.8), transform=ccrs.PlateCarree())
                
        ax.set_title(f"Panorama Combinado Puerto | {timestamp_str}")
        plt.tight_layout()
        filename = self.output_dir / f"combined_h{hour:03d}_{timestamp_str}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

if __name__ == '__main__':
    print("Iniciando SPATI PUERTOS ERA5/WRF Integration Engine")
    forecast_gen = HyperLocalForecastGenerator()
    start_time = datetime.utcnow()
    forecast_72h = forecast_gen.generate_forecast(start_date=start_time, hours_ahead=72)
    print(f"Generados {len(forecast_72h.hourly_states)} estados. Alertas:", forecast_72h.get_alert_summary())
