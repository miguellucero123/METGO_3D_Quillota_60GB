# 🌾 METGO 3D - Configuration Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Configuration Guide
===================

This guide explains how to configure METGO 3D for your specific needs.

Configuration Files
-------------------

The system uses several configuration files:

* `config/config.yaml` - Main configuration file
* `requirements.txt` - Python dependencies
* `metgo.env` - Environment variables
* `.gitignore` - Git ignore patterns
* `Dockerfile` - Docker configuration
* `docker-compose.yml` - Docker Compose configuration

Main Configuration File
------------------------

The main configuration file (`config/config.yaml`) contains:

.. code-block:: yaml

   # Configuración de Quillota
   QUILLOTA:
     nombre: "Quillota"
     region: "Valparaíso"
     pais: "Chile"
     coordenadas:
       latitud: -32.8833
       longitud: -71.25
     elevacion: 120
     poblacion: 97572
     superficie_agricola: 15000

   # Configuración meteorológica
   METEOROLOGIA:
     umbrales:
       temperatura:
         helada_severa: -2.0
         helada_moderada: 0.0
         calor_extremo: 35.0
         calor_moderado: 30.0
       precipitacion:
         lluvia_intensa: 20.0
         lluvia_moderada: 10.0
       viento:
         fuerte: 25.0
         moderado: 15.0
       humedad:
         muy_baja: 30.0
         muy_alta: 85.0

Location Configuration
----------------------

Configure the location settings:

.. code-block:: yaml

   QUILLOTA:
     nombre: "Quillota"
     region: "Valparaíso"
     pais: "Chile"
     coordenadas:
       latitud: -32.8833
       longitud: -71.25
     elevacion: 120
     poblacion: 97572
     superficie_agricola: 15000

Meteorological Thresholds
--------------------------

Configure meteorological thresholds:

.. code-block:: yaml

   METEOROLOGIA:
     umbrales:
       temperatura:
         helada_severa: -2.0
         helada_moderada: 0.0
         calor_extremo: 35.0
         calor_moderado: 30.0
       precipitacion:
         lluvia_intensa: 20.0
         lluvia_moderada: 10.0
       viento:
         fuerte: 25.0
         moderado: 15.0
       humedad:
         muy_baja: 30.0
         muy_alta: 85.0

System Configuration
---------------------

Configure system parameters:

.. code-block:: yaml

   SISTEMA:
     version: "2.0.0"
     fecha_actualizacion: "2025-01-02"
     directorio_datos: "data"
     directorio_logs: "logs"
     directorio_reportes: "reportes_revision"
     directorio_tests: "test_results"
     directorio_backups: "backups"

API Configuration
------------------

Configure API settings:

.. code-block:: yaml

   APIS:
     openmeteo:
       url_base: "https://api.open-meteo.com/v1"
       timeout: 30
       max_retries: 3
       rate_limit: 1000
     fallback:
       usar_datos_sinteticos: true
       semilla_reproducibilidad: 42

Logging Configuration
---------------------

Configure logging settings:

.. code-block:: yaml

   LOGGING:
     nivel: "INFO"
     formato: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     archivo_log: "logs/metgo_operativo.log"
     max_tamaño_mb: 10
     backup_count: 5

Visualization Configuration
--------------------------

Configure visualization settings:

.. code-block:: yaml

   VISUALIZACION:
     tema: "quillota"
     colores:
       primary: "#2E7D32"
       secondary: "#8BC34A"
       accent: "#FFEB3B"
       temperature_hot: "#FF5722"
       temperature_cold: "#2196F3"
       precipitation: "#03A9F4"
       humidity: "#00BCD4"
       wind: "#607D8B"
       pressure: "#9E9E9E"
       radiation: "#FFC107"
       cloud_cover: "#B0BEC5"
       alert: "#FF9800"
       danger: "#F44336"
       success: "#4CAF50"
       warning: "#FFC107"
       info: "#17A2B8"
     figura:
       tamano: [12, 8]
       dpi: 100
       estilo: "default"

Machine Learning Configuration
------------------------------

Configure ML settings:

.. code-block:: yaml

   ML:
     modelos:
       - "RandomForestRegressor"
       - "LinearRegression"
       - "GradientBoostingRegressor"
       - "SVR"
       - "KNeighborsRegressor"
     validacion_cruzada:
       cv_folds: 5
       scoring: "neg_mean_squared_error"
     hiperparametros:
       RandomForestRegressor:
         n_estimators: [50, 100, 200]
         max_depth: [10, 20, None]
         min_samples_split: [2, 5, 10]
       LinearRegression:
         fit_intercept: [true, false]
       GradientBoostingRegressor:
         n_estimators: [50, 100, 200]
         learning_rate: [0.01, 0.1, 0.2]
         max_depth: [3, 5, 7]

Environment Variables
---------------------

Configure environment variables in `metgo.env`:

.. code-block:: bash

   # Configuración del sistema
   METGO_VERSION=2.0.0
   METGO_LOCATION=Quillota
   METGO_REGION=Valparaíso
   METGO_COUNTRY=Chile

   # Configuración de Python
   PYTHONPATH=.
   PYTHONWARNINGS=ignore
   OMP_NUM_THREADS=4

   # Configuración de Jupyter
   JUPYTER_ENABLE_LAB=yes
   JUPYTER_DATA_DIR=./jupyter_data

   # Configuración de Streamlit
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   STREAMLIT_SERVER_PORT=8501
   STREAMLIT_SERVER_ADDRESS=localhost

Customization
--------------

You can customize the system by:

1. **Modifying Configuration Files**: Edit YAML and environment files
2. **Adjusting Thresholds**: Change meteorological thresholds
3. **Changing Themes**: Modify visualization themes
4. **Updating APIs**: Change API settings
5. **Modifying Logging**: Adjust logging levels

Best Practices
--------------

1. **Backup Configuration**: Always backup configuration files
2. **Test Changes**: Test configuration changes thoroughly
3. **Document Changes**: Document any customizations
4. **Version Control**: Use version control for configuration files
5. **Environment Separation**: Separate development and production configs

Troubleshooting
---------------

Common Configuration Issues:

1. **YAML Syntax Errors**: Check YAML syntax carefully
2. **Missing Values**: Ensure all required values are present
3. **Type Mismatches**: Verify data types match expectations
4. **Path Issues**: Check file and directory paths
5. **Permission Issues**: Verify file permissions

For more information, see the complete documentation.
