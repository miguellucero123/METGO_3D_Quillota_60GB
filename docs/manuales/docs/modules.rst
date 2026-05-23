# 🌾 METGO 3D - Module Index
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Module Index
============

This section provides an index of all modules in METGO 3D.

Core Modules
------------

Configuration Module
~~~~~~~~~~~~~~~~~~~~~

.. py:module:: config

   Configuration management module.

   .. py:function:: cargar_configuracion()
   
      Load centralized configuration from YAML file.

   .. py:function:: crear_configuracion_default()
   
      Create default configuration if YAML file doesn't exist.

Data Processing Module
~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: data_processing

   Data processing and validation module.

   .. py:function:: cargar_datos_historicos()
   
      Load historical meteorological data.

   .. py:function:: crear_datos_meteorologicos_mejorados()
   
      Create improved synthetic meteorological data.

   .. py:function:: procesar_datos_meteorologicos_mejorados()
   
      Process meteorological data with improved functions.

   .. py:function:: validar_datos_meteorologicos()
   
      Validate meteorological data with robust system.

   .. py:function:: corregir_datos_meteorologicos()
   
      Correct meteorological data based on validation.

Analysis Module
~~~~~~~~~~~~~~~

.. py:module:: analysis

   Meteorological analysis module.

   .. py:function:: analizar_temperaturas_avanzado()
   
      Advanced temperature analysis for Quillota.

   .. py:function:: analizar_precipitacion_avanzado()
   
      Advanced precipitation analysis with hydrological statistics.

   .. py:function:: analizar_viento_humedad_avanzado()
   
      Advanced wind and humidity analysis.

   .. py:function:: realizar_analisis_meteorologico_completo()
   
      Perform complete meteorological analysis.

Visualization Module
~~~~~~~~~~~~~~~~~~~~

.. py:module:: visualization

   Visualization and dashboard module.

   .. py:function:: crear_dashboard_temperaturas()
   
      Create complete temperature dashboard.

   .. py:function:: crear_dashboard_precipitacion()
   
      Create complete precipitation dashboard.

   .. py:function:: crear_dashboard_ambiental()
   
      Create environmental variables dashboard.

   .. py:function:: crear_dashboard_agricola()
   
      Create agricultural indices dashboard.

   .. py:function:: crear_dashboard_interactivo_plotly()
   
      Create interactive Plotly dashboard.

Machine Learning Module
~~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: machine_learning

   Machine learning and forecasting module.

   .. py:function:: entrenar_modelo_temperatura()
   
      Train temperature prediction model.

   .. py:function:: entrenar_modelo_precipitacion()
   
      Train precipitation prediction model.

   .. py:function:: evaluar_modelo()
   
      Evaluate machine learning model performance.

   .. py:function:: hacer_prediccion()
   
      Make weather prediction using trained model.

API Integration Module
~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: api_integration

   External API integration module.

   .. py:function:: obtener_datos_openmeteo()
   
      Get meteorological data from OpenMeteo API.

   .. py:function:: crear_datos_sinteticos_respaldo()
   
      Create realistic synthetic data as backup.

   .. py:function:: procesar_respuesta_api()
   
      Process API response data.

Testing Module
~~~~~~~~~~~~~~

.. py:module:: testing

   Testing and validation module.

   .. py:function:: test_imports()
   
      Test critical imports.

   .. py:function:: test_configuration()
   
      Test system configuration.

   .. py:function:: test_data_generation()
   
      Test synthetic data generation.

   .. py:function:: test_analysis_functions()
   
      Test analysis functions.

   .. py:function:: test_visualization()
   
      Test visualization functions.

   .. py:function:: test_ml_models()
   
      Test machine learning models.

Utility Modules
---------------

Logging Module
~~~~~~~~~~~~~~

.. py:module:: logging

   Logging and monitoring module.

   .. py:function:: configurar_logging()
   
      Configure structured logging system.

   .. py:function:: crear_logger()
   
      Create logger instance.

   .. py:function:: log_error()
   
      Log error message.

   .. py:function:: log_info()
   
      Log info message.

   .. py:function:: log_warning()
   
      Log warning message.

File Management Module
~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: file_management

   File and directory management module.

   .. py:function:: crear_directorios()
   
      Create necessary directories.

   .. py:function:: limpiar_archivos_temporales()
   
      Clean temporary files.

   .. py:function:: respaldar_archivos()
   
      Backup important files.

   .. py:function:: restaurar_archivos()
   
      Restore files from backup.

System Monitoring Module
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: system_monitoring

   System monitoring and health checks module.

   .. py:function:: monitorear_recursos()
   
      Monitor system resources.

   .. py:function:: verificar_dependencias()
   
      Verify system dependencies.

   .. py:function:: verificar_configuracion()
   
      Verify system configuration.

   .. py:function:: generar_reporte_estado()
   
      Generate system status report.

Data Export Module
~~~~~~~~~~~~~~~~~~

.. py:module:: data_export

   Data export and reporting module.

   .. py:function:: exportar_datos()
   
      Export data in different formats.

   .. py:function:: generar_reporte_html()
   
      Generate HTML report.

   .. py:function:: generar_reporte_pdf()
   
      Generate PDF report.

   .. py:function:: generar_reporte_excel()
   
      Generate Excel report.

Configuration Classes
---------------------

Location Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: QUILLOTA_CONFIG

   Configuration class for Quillota location settings.

   .. py:attribute:: nombre
      :type: str
      :value: 'Quillota'

   .. py:attribute:: region
      :type: str
      :value: 'Valparaíso'

   .. py:attribute:: pais
      :type: str
      :value: 'Chile'

   .. py:attribute:: coordenadas
      :type: dict
      :value: {'latitud': -32.8833, 'longitud': -71.25}

   .. py:attribute:: elevacion
      :type: int
      :value: 120

   .. py:attribute:: poblacion
      :type: int
      :value: 97572

   .. py:attribute:: superficie_agricola
      :type: int
      :value: 15000

Meteorological Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: UMBRALES_CRITICOS

   Configuration class for critical meteorological thresholds.

   .. py:attribute:: temperatura
      :type: dict
      :value: {'helada_severa': -2.0, 'helada_moderada': 0.0, 'calor_extremo': 35.0, 'calor_moderado': 30.0}

   .. py:attribute:: precipitacion
      :type: dict
      :value: {'lluvia_intensa': 20.0, 'lluvia_moderada': 10.0}

   .. py:attribute:: viento
      :type: dict
      :value: {'fuerte': 25.0, 'moderado': 15.0}

   .. py:attribute:: humedad
      :type: dict
      :value: {'muy_baja': 30.0, 'muy_alta': 85.0}

System Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:class:: SISTEMA_CONFIG

   Configuration class for system parameters.

   .. py:attribute:: version
      :type: str
      :value: '2.0.0'

   .. py:attribute:: fecha_actualizacion
      :type: str
      :value: '2025-01-02'

   .. py:attribute:: directorio_datos
      :type: str
      :value: 'data'

   .. py:attribute:: directorio_logs
      :type: str
      :value: 'logs'

   .. py:attribute:: directorio_reportes
      :type: str
      :value: 'reportes_revision'

Data Structures
----------------

Meteorological Data
~~~~~~~~~~~~~~~~~~~

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

   .. py:attribute:: temperatura_promedio
      :type: float
      :description: Average temperature in Celsius

   .. py:attribute:: precipitacion
      :type: float
      :description: Precipitation in millimeters

   .. py:attribute:: humedad_relativa
      :type: float
      :description: Relative humidity percentage

   .. py:attribute:: velocidad_viento
      :type: float
      :description: Wind speed in km/h

   .. py:attribute:: direccion_viento
      :type: str
      :description: Wind direction

   .. py:attribute:: presion_atmosferica
      :type: float
      :description: Atmospheric pressure in hPa

   .. py:attribute:: radiacion_solar
      :type: float
      :description: Solar radiation in MJ/m²

   .. py:attribute:: nubosidad
      :type: int
      :description: Cloud cover percentage

Agricultural Indices
~~~~~~~~~~~~~~~~~~~~

.. py:class:: IndicesAgricolas

   Data structure for agricultural indices.

   .. py:attribute:: grados_dia
      :type: float
      :description: Growing degree days

   .. py:attribute:: confort_termico
      :type: str
      :description: Thermal comfort index

   .. py:attribute:: necesidad_riego
      :type: str
      :description: Irrigation need index

   .. py:attribute:: riesgo_helada
      :type: str
      :description: Frost risk index

   .. py:attribute:: riesgo_hongos
      :type: str
      :description: Fungal risk index

For more information, see the complete documentation.
