# 🌾 METGO 3D - User Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

User Guide
==========

This guide provides detailed information on using METGO 3D.

System Overview
---------------

METGO 3D is a comprehensive meteorological agricultural system designed specifically for Quillota, Chile. It provides:

* Real-time meteorological data analysis
* Agricultural weather forecasting
* Intelligent alerts and recommendations
* Interactive dashboards and visualizations
* Machine learning-based predictions
* Automated reporting

Getting Started
---------------

1. **Installation**: Follow the :doc:`installation` guide
2. **Configuration**: Review the :doc:`configuration` section
3. **Quick Start**: Use the :doc:`quickstart` guide
4. **Testing**: Run system tests to verify functionality

System Components
-----------------

Configuration and Imports
~~~~~~~~~~~~~~~~~~~~~~~~~~

The first component (`01_Configuracion_e_imports.ipynb`) handles:

* Centralized configuration loading
* Dependency verification
* Logging system setup
* Environment optimization
* Import management

Data Loading and Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second component (`02_Carga_y_Procesamiento_Datos.ipynb`) manages:

* Data loading from APIs
* Synthetic data generation
* Data validation and cleaning
* Agricultural index calculations
* Data export functionality

Meteorological Analysis
~~~~~~~~~~~~~~~~~~~~~~~

The third component (`03_Analisis_Meteorologico.ipynb`) provides:

* Temperature analysis
* Precipitation analysis
* Wind and humidity analysis
* Extreme weather detection
* Seasonal pattern analysis

Visualizations
~~~~~~~~~~~~~~~

The fourth component (`04_Visualizaciones.ipynb`) creates:

* Interactive dashboards
* Temperature charts
* Precipitation graphs
* Wind roses
* Agricultural indices plots

Machine Learning Models
~~~~~~~~~~~~~~~~~~~~~~~~

The fifth component (`05_Modelos_ML.ipynb`) includes:

* Weather forecasting models
* Temperature prediction
* Precipitation forecasting
* Model validation
* Performance metrics

Interactive Dashboard
~~~~~~~~~~~~~~~~~~~~~~

The sixth component (`06_Dashboard_Interactivo.ipynb`) offers:

* Streamlit-based dashboard
* Real-time data visualization
* Interactive controls
* Alert management
* Report generation

Automatic Reports
~~~~~~~~~~~~~~~~~~

The seventh component (`07_Reportes_Automaticos.ipynb`) generates:

* Daily weather reports
* Agricultural recommendations
* Alert summaries
* Performance metrics
* Export functionality

External APIs
~~~~~~~~~~~~~~

The eighth component (`08_APIs_Externas.ipynb`) handles:

* OpenMeteo API integration
* Data fetching and processing
* Error handling and fallbacks
* Rate limiting
* Data validation

Testing and Validation
~~~~~~~~~~~~~~~~~~~~~~~

The ninth component (`09_Testing_Validacion.ipynb`) provides:

* System testing
* Data validation
* Performance testing
* Quality assurance
* Error detection

Production Deployment
~~~~~~~~~~~~~~~~~~~~~~~

The tenth component (`10_Deployment_Produccion.ipynb`) covers:

* Production deployment
* Performance optimization
* Security considerations
* Monitoring setup
* Maintenance procedures

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~~

.. code-block:: python

   # Run complete system
   python ejecutar_sistema_completo.py

   # Run in quick mode
   python ejecutar_sistema_completo.py rapido

   # Run analysis only
   python ejecutar_sistema_completo.py analisis

Advanced Usage
~~~~~~~~~~~~~~~

.. code-block:: python

   # Custom configuration
   import yaml
   with open('config/config.yaml', 'r') as f:
       config = yaml.safe_load(f)

   # Modify configuration
   config['METEOROLOGIA']['umbrales']['temperatura']['helada_severa'] = -3.0

   # Save configuration
   with open('config/config.yaml', 'w') as f:
       yaml.dump(config, f)

System Monitoring
-----------------

Monitor System Status
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python monitor_sistema.py

Test System Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python test_sistema.py

Clean System Files
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python limpiar_sistema.py

Backup System Data
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python backup_sistema.py

Configuration
-------------

The system uses YAML configuration files for:

* Location settings
* Meteorological thresholds
* System parameters
* API configurations
* Logging settings
* Visualization themes
* Machine learning parameters

Customization
--------------

You can customize the system by:

1. Modifying configuration files
2. Adjusting meteorological thresholds
3. Changing visualization themes
4. Updating API settings
5. Modifying logging levels

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~~

1. **Import Errors**: Check Python version and dependencies
2. **Configuration Errors**: Verify YAML syntax
3. **API Errors**: Check internet connection and API limits
4. **Data Errors**: Verify data format and validation
5. **Performance Issues**: Check system resources

Getting Help
~~~~~~~~~~~~~

1. Check the :doc:`troubleshooting` section
2. Review system logs
3. Run diagnostic tests
4. Check system status
5. Consult documentation

Best Practices
--------------

1. **Regular Backups**: Create backups regularly
2. **System Monitoring**: Monitor system status
3. **Data Validation**: Validate data quality
4. **Error Handling**: Handle errors gracefully
5. **Performance Optimization**: Optimize for performance

For more information, see the complete documentation.
