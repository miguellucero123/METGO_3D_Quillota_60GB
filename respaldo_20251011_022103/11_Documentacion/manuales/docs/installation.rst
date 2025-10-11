# 🌾 METGO 3D - Installation Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Installation
============

Prerequisites
-------------

Before installing METGO 3D, make sure you have the following prerequisites:

* Python 3.8 or higher
* pip (Python package installer)
* Git (for cloning the repository)

Quick Installation
-------------------

1. Clone the repository:

.. code-block:: bash

   git clone <repository-url>
   cd PROYECTO_METGO_3D

2. Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

3. Run the installation script:

.. code-block:: bash

   python instalar_sistema.py

Manual Installation
-------------------

If you prefer to install manually:

1. Create a virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

3. Create necessary directories:

.. code-block:: bash

   mkdir -p logs data reportes_revision test_results tests app static templates backups config

4. Run tests to verify installation:

.. code-block:: bash

   python test_sistema.py

Docker Installation
-------------------

For Docker installation:

1. Build the Docker image:

.. code-block:: bash

   docker build -t metgo-3d:latest .

2. Run the container:

.. code-block:: bash

   docker run -p 8501:8501 metgo-3d:latest

3. Or use docker-compose:

.. code-block:: bash

   docker-compose up -d

Verification
------------

To verify that METGO 3D is installed correctly:

1. Run the system test:

.. code-block:: bash

   python test_sistema.py

2. Check system status:

.. code-block:: bash

   python monitor_sistema.py

3. Run a quick analysis:

.. code-block:: bash

   python ejecutar_sistema_completo.py rapido

Troubleshooting
---------------

If you encounter issues during installation:

1. Check Python version:

.. code-block:: bash

   python --version

2. Check pip version:

.. code-block:: bash

   pip --version

3. Check dependencies:

.. code-block:: bash

   pip list

4. Check system requirements:

.. code-block:: bash

   python -c "import sys; print(sys.version_info)"

For more help, see the :doc:`troubleshooting` section.
