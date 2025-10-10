# 🌾 METGO 3D - Quick Start Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Quick Start Guide
==================

This guide will help you get started with METGO 3D quickly.

Running the System
------------------

1. **Complete System Execution**:

.. code-block:: bash

   python ejecutar_sistema_completo.py

2. **Quick Mode** (essential notebooks only):

.. code-block:: bash

   python ejecutar_sistema_completo.py rapido

3. **Analysis Mode** (analysis notebooks only):

.. code-block:: bash

   python ejecutar_sistema_completo.py analisis

4. **Testing Mode**:

.. code-block:: bash

   python ejecutar_sistema_completo.py testing

5. **Deployment Mode**:

.. code-block:: bash

   python ejecutar_sistema_completo.py deployment

Using Scripts
--------------

**Windows (PowerShell)**:

.. code-block:: powershell

   .\ejecutar_sistema.ps1
   .\ejecutar_sistema.ps1 rapido
   .\ejecutar_sistema.ps1 analisis

**Linux/macOS (Bash)**:

.. code-block:: bash

   ./ejecutar_sistema.sh
   ./ejecutar_sistema.sh rapido
   ./ejecutar_sistema.sh analisis

**Makefile**:

.. code-block:: bash

   make run
   make run-fast
   make test
   make clean
   make backup
   make monitor

System Components
-----------------

The METGO 3D system consists of the following components:

1. **Configuration and Imports** (`01_Configuracion_e_imports.ipynb`)
2. **Data Loading and Processing** (`02_Carga_y_Procesamiento_Datos.ipynb`)
3. **Meteorological Analysis** (`03_Analisis_Meteorologico.ipynb`)
4. **Visualizations** (`04_Visualizaciones.ipynb`)
5. **Machine Learning Models** (`05_Modelos_ML.ipynb`)
6. **Interactive Dashboard** (`06_Dashboard_Interactivo.ipynb`)
7. **Automatic Reports** (`07_Reportes_Automaticos.ipynb`)
8. **External APIs** (`08_APIs_Externas.ipynb`)
9. **Testing and Validation** (`09_Testing_Validacion.ipynb`)
10. **Production Deployment** (`10_Deployment_Produccion.ipynb`)

Key Features
-------------

* **Centralized Configuration**: YAML-based configuration system
* **Robust Error Handling**: Comprehensive error management
* **Structured Logging**: Detailed logging system
* **Data Validation**: Automatic data quality checks
* **Advanced Analysis**: Meteorological analysis with agricultural indices
* **Interactive Visualizations**: Plotly and Matplotlib dashboards
* **Machine Learning**: Predictive models for weather forecasting
* **API Integration**: OpenMeteo API with fallback to synthetic data
* **Testing Suite**: Comprehensive testing and validation
* **Production Ready**: Deployment-ready system

Configuration
--------------

The system uses a centralized configuration file (`config/config.yaml`) that includes:

* Quillota location settings
* Meteorological thresholds
* System parameters
* API configurations
* Logging settings
* Visualization themes
* Machine learning parameters

Data Flow
----------

1. **Data Loading**: Load meteorological data from APIs or generate synthetic data
2. **Data Processing**: Clean, validate, and process the data
3. **Analysis**: Perform meteorological analysis and calculate agricultural indices
4. **Visualization**: Create interactive dashboards and charts
5. **Modeling**: Train machine learning models for forecasting
6. **Reporting**: Generate automatic reports and recommendations
7. **Deployment**: Deploy the system for production use

Monitoring and Maintenance
--------------------------

* **System Monitoring**: `python monitor_sistema.py`
* **System Testing**: `python test_sistema.py`
* **System Cleaning**: `python limpiar_sistema.py`
* **System Backup**: `python backup_sistema.py`

Next Steps
----------

1. Read the :doc:`user_guide` for detailed usage instructions
2. Check the :doc:`api_reference` for API documentation
3. Review the :doc:`configuration` section for customization
4. See the :doc:`deployment` guide for production deployment
5. Consult the :doc:`troubleshooting` section for common issues

For more information, see the complete documentation.
