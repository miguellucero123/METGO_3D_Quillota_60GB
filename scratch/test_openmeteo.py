import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude': -32.8833,
    'longitude': -71.25,
    'daily': [
        'temperature_2m_max',
        'temperature_2m_min',
        'temperature_2m_mean',
        'relative_humidity_2m_max',
        'precipitation_sum',
        'wind_speed_10m_max',
        'pressure_msl_mean',
        'cloud_cover_mean',
        'shortwave_radiation_sum',
        'wind_direction_10m_dominant',
        'et0_fao_evapotranspiration',
    ],
    'hourly': ['visibility', 'cloud_cover'],
    'timezone': 'America/Santiago',
    'past_days': 10,
    'forecast_days': 0,
}

response = requests.get(url, params=params)
print("HISTORICAL STATUS:", response.status_code)
print("HISTORICAL RESPONSE:", response.text)

params_forecast = {
    'latitude': -32.8833,
    'longitude': -71.25,
    'daily': [
        'temperature_2m_max',
        'temperature_2m_min',
        'temperature_2m_mean',
        'relative_humidity_2m_max',
        'precipitation_sum',
        'wind_speed_10m_max',
        'pressure_msl_mean',
        'precipitation_probability_max',
        'cloud_cover_mean',
        'shortwave_radiation_sum',
        'wind_direction_10m_dominant',
        'et0_fao_evapotranspiration',
    ],
    'hourly': ['visibility', 'cloud_cover'],
    'timezone': 'America/Santiago',
    'forecast_days': 7
}

response_forecast = requests.get(url, params=params_forecast)
print("FORECAST STATUS:", response_forecast.status_code)
print("FORECAST RESPONSE:", response_forecast.text)
