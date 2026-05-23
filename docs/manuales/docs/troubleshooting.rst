# 🌾 METGO 3D - Troubleshooting Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Troubleshooting Guide
====================

This guide helps you resolve common issues with METGO 3D.

Common Issues
-------------

Installation Issues
~~~~~~~~~~~~~~~~~~~

**Problem**: Python version not compatible

.. code-block:: bash

   python --version

**Solution**: Install Python 3.8 or higher

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.9

   # CentOS/RHEL
   sudo yum install python39

   # macOS
   brew install python@3.9

**Problem**: Dependencies not installed

.. code-block:: bash

   pip install -r requirements.txt

**Solution**: Install missing dependencies

.. code-block:: bash

   pip install pandas numpy matplotlib seaborn scikit-learn requests plotly streamlit pyyaml jupyter nbconvert

**Problem**: Permission denied errors

.. code-block:: bash

   chmod +x ejecutar_sistema.sh

**Solution**: Make scripts executable

.. code-block:: bash

   chmod +x *.sh
   chmod +x *.py

Configuration Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem**: YAML syntax errors

.. code-block:: yaml

   # Incorrect
   temperatura:
     helada_severa: -2.0
     calor_extremo: 35.0

   # Correct
   temperatura:
     helada_severa: -2.0
     calor_extremo: 35.0

**Solution**: Check YAML syntax carefully

**Problem**: Missing configuration values

.. code-block:: yaml

   QUILLOTA:
     nombre: "Quillota"
     region: "Valparaíso"
     coordenadas:
       latitud: -32.8833
       longitud: -71.25

**Solution**: Ensure all required values are present

**Problem**: Configuration file not found

.. code-block:: bash

   ls -la config/

**Solution**: Create configuration directory and file

.. code-block:: bash

   mkdir -p config
   touch config/config.yaml

Data Issues
~~~~~~~~~~~

**Problem**: Data validation errors

.. code-block:: python

   # Check data types
   print(df.dtypes)
   
   # Check for missing values
   print(df.isnull().sum())
   
   # Check data ranges
   print(df.describe())

**Solution**: Validate and clean data

.. code-block:: python

   # Remove missing values
   df = df.dropna()
   
   # Fix data types
   df['fecha'] = pd.to_datetime(df['fecha'])
   
   # Fix data ranges
   df['humedad_relativa'] = df['humedad_relativa'].clip(0, 100)

**Problem**: API connection errors

.. code-block:: python

   import requests
   
   try:
       response = requests.get('https://api.open-meteo.com/v1/forecast', timeout=30)
       response.raise_for_status()
   except requests.exceptions.RequestException as e:
       print(f"API Error: {e}")

**Solution**: Check internet connection and API limits

.. code-block:: python

   # Use fallback data
   datos = crear_datos_sinteticos_respaldo(30)

**Problem**: Data format errors

.. code-block:: python

   # Check data format
   print(df.head())
   print(df.info())

**Solution**: Verify data format and structure

.. code-block:: python

   # Ensure proper data types
   df['temperatura_max'] = pd.to_numeric(df['temperatura_max'], errors='coerce')
   df['temperatura_min'] = pd.to_numeric(df['temperatura_min'], errors='coerce')

Performance Issues
~~~~~~~~~~~~~~~~~~

**Problem**: Slow execution

.. code-block:: bash

   # Check system resources
   top
   htop
   free -h
   df -h

**Solution**: Optimize system resources

.. code-block:: python

   # Set environment variables
   import os
   os.environ['OMP_NUM_THREADS'] = '4'
   os.environ['PYTHONWARNINGS'] = 'ignore'

**Problem**: Memory issues

.. code-block:: python

   import psutil
   
   # Check memory usage
   memory = psutil.virtual_memory()
   print(f"Memory usage: {memory.percent}%")

**Solution**: Optimize memory usage

.. code-block:: python

   # Use chunking for large datasets
   chunk_size = 1000
   for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
       process_chunk(chunk)

**Problem**: CPU usage issues

.. code-block:: python

   import psutil
   
   # Check CPU usage
   cpu_percent = psutil.cpu_percent(interval=1)
   print(f"CPU usage: {cpu_percent}%")

**Solution**: Optimize CPU usage

.. code-block:: python

   # Use multiprocessing
   from multiprocessing import Pool
   
   with Pool(processes=4) as pool:
       results = pool.map(process_data, data_chunks)

Visualization Issues
~~~~~~~~~~~~~~~~~~~~

**Problem**: Matplotlib display issues

.. code-block:: python

   import matplotlib
   matplotlib.use('Agg')  # Use non-interactive backend

**Solution**: Configure matplotlib backend

.. code-block:: python

   import matplotlib.pyplot as plt
   plt.ioff()  # Turn off interactive mode

**Problem**: Plotly display issues

.. code-block:: python

   import plotly
   plotly.offline.init_notebook_mode(connected=True)

**Solution**: Configure plotly for offline use

.. code-block:: python

   import plotly.graph_objects as go
   fig = go.Figure()
   fig.show()

**Problem**: Seaborn style issues

.. code-block:: python

   import seaborn as sns
   sns.set_style("whitegrid")
   sns.set_palette("husl")

**Solution**: Configure seaborn style

.. code-block:: python

   # Reset seaborn settings
   sns.reset_defaults()

Machine Learning Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Model training errors

.. code-block:: python

   # Check data quality
   print(X.isnull().sum())
   print(y.isnull().sum())

**Solution**: Ensure data quality

.. code-block:: python

   # Remove missing values
   X = X.dropna()
   y = y.dropna()
   
   # Check data types
   print(X.dtypes)
   print(y.dtypes)

**Problem**: Model performance issues

.. code-block:: python

   # Check model metrics
   from sklearn.metrics import mean_squared_error, r2_score
   
   mse = mean_squared_error(y_test, y_pred)
   r2 = r2_score(y_test, y_pred)
   
   print(f"MSE: {mse}")
   print(f"R²: {r2}")

**Solution**: Optimize model parameters

.. code-block:: python

   # Use grid search
   from sklearn.model_selection import GridSearchCV
   
   param_grid = {
       'n_estimators': [50, 100, 200],
       'max_depth': [10, 20, None]
   }
   
   grid_search = GridSearchCV(model, param_grid, cv=5)
   grid_search.fit(X_train, y_train)

**Problem**: Model persistence issues

.. code-block:: python

   import joblib
   
   # Save model
   joblib.dump(model, 'model.pkl')
   
   # Load model
   model = joblib.load('model.pkl')

**Solution**: Use proper model persistence

.. code-block:: python

   # Check file permissions
   import os
   print(os.access('model.pkl', os.W_OK))

Logging Issues
~~~~~~~~~~~~~~

**Problem**: Log files not created

.. code-block:: python

   import logging
   
   # Check logging configuration
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('logs/metgo_operativo.log'),
           logging.StreamHandler()
       ]
   )

**Solution**: Configure logging properly

.. code-block:: python

   # Create logs directory
   import os
   os.makedirs('logs', exist_ok=True)

**Problem**: Log rotation issues

.. code-block:: python

   from logging.handlers import RotatingFileHandler
   
   handler = RotatingFileHandler(
       'logs/metgo_operativo.log',
       maxBytes=10*1024*1024,  # 10MB
       backupCount=5
   )

**Solution**: Use rotating file handler

.. code-block:: python

   # Configure rotating handler
   logging.basicConfig(handlers=[handler])

Testing Issues
~~~~~~~~~~~~~~

**Problem**: Test failures

.. code-block:: bash

   python test_sistema.py

**Solution**: Check test output and fix issues

.. code-block:: python

   # Run specific tests
   pytest tests/test_data_processing.py -v

**Problem**: Test coverage issues

.. code-block:: bash

   pytest --cov=. --cov-report=html

**Solution**: Improve test coverage

.. code-block:: python

   # Add more test cases
   def test_data_validation():
       assert validate_data(test_data) == True

**Problem**: Test performance issues

.. code-block:: bash

   pytest --durations=10

**Solution**: Optimize test performance

.. code-block:: python

   # Use fixtures for setup
   @pytest.fixture
   def sample_data():
       return create_sample_data()

Debugging Tips
--------------

1. **Check Logs**: Review log files for error messages
2. **Use Debug Mode**: Enable debug mode for detailed output
3. **Test Components**: Test individual components separately
4. **Verify Dependencies**: Check all dependencies are installed
5. **Check Permissions**: Verify file and directory permissions

Getting Help
------------

1. **Check Documentation**: Review the complete documentation
2. **Review Logs**: Check system logs for error messages
3. **Run Diagnostics**: Use diagnostic tools
4. **Check System Status**: Monitor system status
5. **Contact Support**: Reach out for technical support

For more information, see the complete documentation.
