# 🌾 METGO 3D - API Reference
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

API Reference
=============

This section provides detailed API documentation for METGO 3D.

Core Functions
--------------

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: cargar_configuracion()

   Load centralized configuration from YAML file.

   :returns: Configuration dictionary
   :rtype: dict

.. py:function:: crear_configuracion_default()

   Create default configuration if YAML file doesn't exist.

   :returns: Default configuration dictionary
   :rtype: dict

Data Processing Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: cargar_datos_historicos(dias=365, incluir_indices=True, validar=True)

   Load historical meteorological data with validation.

   :param dias: Number of days of historical data
   :type dias: int
   :param incluir_indices: Include agricultural indices calculation
   :type incluir_indices: bool
   :param validar: Validate data with robust system
   :type validar: bool
   :returns: Processed and validated meteorological data
   :rtype: pandas.DataFrame

.. py:function:: crear_datos_meteorologicos_mejorados(dias=365)

   Create improved synthetic meteorological data with realistic seasonality.

   :param dias: Number of days to generate
   :type dias: int
   :returns: Synthetic meteorological data
   :rtype: pandas.DataFrame

.. py:function:: procesar_datos_meteorologicos_mejorados(datos)

   Process meteorological data with improved functions.

   :param datos: Raw meteorological data
   :type datos: pandas.DataFrame
   :returns: Processed meteorological data
   :rtype: pandas.DataFrame

Analysis Functions
~~~~~~~~~~~~~~~~~~~

.. py:function:: analizar_temperaturas_avanzado(datos)

   Advanced temperature analysis for Quillota with robust statistics.

   :param datos: Meteorological data
   :type datos: pandas.DataFrame
   :returns: Temperature analysis results
   :rtype: dict

.. py:function:: analizar_precipitacion_avanzado(datos)

   Advanced precipitation analysis with hydrological statistics.

   :param datos: Meteorological data
   :type datos: pandas.DataFrame
   :returns: Precipitation analysis results
   :rtype: dict

.. py:function:: analizar_viento_humedad_avanzado(datos)

   Advanced wind and humidity analysis.

   :param datos: Meteorological data
   :type datos: pandas.DataFrame
   :returns: Wind and humidity analysis results
   :rtype: dict

Visualization Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: crear_dashboard_temperaturas(datos, titulo="Dashboard de Temperaturas - Quillota")

   Create complete temperature dashboard with multiple visualizations.

   :param datos: Meteorological data
   :type datos: pandas.DataFrame
   :param titulo: Dashboard title
   :type titulo: str
   :returns: Temperature dashboard
   :rtype: matplotlib.figure.Figure

.. py:function:: crear_dashboard_precipitacion(datos, titulo="Dashboard de Precipitación - Quillota")

   Create complete precipitation dashboard with multiple visualizations.

   :param datos: Meteorological data
   :type datos: pandas.DataFrame
   :param titulo: Dashboard title
   :type titulo: str
   :returns: Precipitation dashboard
   :rtype: matplotlib.figure.Figure

Machine Learning Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: entrenar_modelo_temperatura(datos, variable_objetivo='temperatura_max')

   Train temperature prediction model.

   :param datos: Training data
   :type datos: pandas.DataFrame
   :param variable_objetivo: Target variable
   :type variable_objetivo: str
   :returns: Trained model and metrics
   :rtype: tuple

.. py:function:: entrenar_modelo_precipitacion(datos, variable_objetivo='precipitacion')

   Train precipitation prediction model.

   :param datos: Training data
   :type datos: pandas.DataFrame
   :param variable_objetivo: Target variable
   :type variable_objetivo: str
   :returns: Trained model and metrics
   :rtype: tuple

API Integration Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: obtener_datos_openmeteo(latitud, longitud, dias=30, fuente="auto")

   Get meteorological data from OpenMeteo API with robust error handling.

   :param latitud: Latitude coordinate
   :type latitud: float
   :param longitud: Longitude coordinate
   :type longitud: float
   :param dias: Number of days
   :type dias: int
   :param fuente: Data source
   :type fuente: str
   :returns: Meteorological data
   :rtype: pandas.DataFrame

.. py:function:: crear_datos_sinteticos_respaldo(dias=30)

   Create realistic synthetic data as backup.

   :param dias: Number of days to generate
   :type dias: int
   :returns: Synthetic meteorological data
   :rtype: pandas.DataFrame

Testing Functions
~~~~~~~~~~~~~~~~~~

.. py:function:: test_imports()

   Test critical imports.

   :returns: Test results
   :rtype: bool

.. py:function:: test_configuration()

   Test system configuration.

   :returns: Test results
   :rtype: bool

.. py:function:: test_data_generation()

   Test synthetic data generation.

   :returns: Test results
   :rtype: bool

Utility Functions
~~~~~~~~~~~~~~~~~~

.. py:function:: verificar_dependencias()

   Verify that all critical dependencies are available.

   :returns: Dependency verification results
   :rtype: bool

.. py:function:: mostrar_info_sistema()

   Display system information.

   :returns: None

.. py:function:: configurar_logging()

   Configure structured logging system.

   :returns: Logger instance
   :rtype: logging.Logger

Configuration Classes
---------------------

.. py:class:: QUILLOTA_CONFIG

   Configuration class for Quillota location settings.

   .. py:attribute:: nombre
      :type: str
      :value: 'Quillota'

   .. py:attribute:: region
      :type: str
      :value: 'Valparaíso'

   .. py:attribute:: coordenadas
      :type: dict
      :value: {'latitud': -32.8833, 'longitud': -71.25}

.. py:class:: UMBRALES_CRITICOS

   Configuration class for critical meteorological thresholds.

   .. py:attribute:: temperatura
      :type: dict
      :value: {'helada_severa': -2.0, 'calor_extremo': 35.0}

   .. py:attribute:: precipitacion
      :type: dict
      :value: {'lluvia_intensa': 20.0}

   .. py:attribute:: viento
      :type: dict
      :value: {'fuerte': 25.0}

   .. py:attribute:: humedad
      :type: dict
      :value: {'muy_baja': 30.0, 'muy_alta': 85.0}

Data Structures
----------------

.. py:class:: DatosMeteorologicos

   Data structure for meteorological data.

   .. py:attribute:: fecha
      :type: pandas.Timestamp
      :description: Date of the observation

   .. py:attribute:: temperatura_max
      :type: float
      :description: Maximum temperature in Celsius

   .. py:attribute:: temperatura_min
      :type: float
      :description: Minimum temperature in Celsius

   .. py:attribute:: precipitacion
      :type: float
      :description: Precipitation in millimeters

   .. py:attribute:: humedad_relativa
      :type: float
      :description: Relative humidity percentage

   .. py:attribute:: velocidad_viento
      :type: float
      :description: Wind speed in km/h

Error Handling
---------------

The system includes comprehensive error handling for:

* API connection errors
* Data validation errors
* Configuration errors
* File system errors
* Memory errors
* Processing errors

All functions return appropriate error codes and messages for debugging.

For more information, see the complete documentation.
