# 🌾 METGO 3D - Deployment Guide
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Deployment Guide
================

This guide explains how to deploy METGO 3D in production environments.

Deployment Options
------------------

The system supports multiple deployment options:

* **Local Deployment**: Run on local machine
* **Docker Deployment**: Containerized deployment
* **Cloud Deployment**: Deploy to cloud platforms
* **Server Deployment**: Deploy to dedicated servers

Local Deployment
-----------------

1. **Install Dependencies**:

.. code-block:: bash

   pip install -r requirements.txt

2. **Run Installation Script**:

.. code-block:: bash

   python instalar_sistema.py

3. **Execute System**:

.. code-block:: bash

   python ejecutar_sistema_completo.py

Docker Deployment
------------------

1. **Build Docker Image**:

.. code-block:: bash

   docker build -t metgo-3d:latest .

2. **Run Container**:

.. code-block:: bash

   docker run -p 8501:8501 metgo-3d:latest

3. **Use Docker Compose**:

.. code-block:: bash

   docker-compose up -d

Docker Configuration
--------------------

The `Dockerfile` includes:

.. code-block:: dockerfile

   FROM python:3.9-slim

   # Metadatos del contenedor
   LABEL maintainer="METGO 3D Team"
   LABEL version="2.0.0"
   LABEL description="Sistema Meteorológico Agrícola Quillota"

   # Variables de entorno
   ENV PYTHONPATH=/app
   ENV PYTHONWARNINGS=ignore
   ENV OMP_NUM_THREADS=4
   ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ENV STREAMLIT_SERVER_PORT=8501
   ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

   # Instalar dependencias del sistema
   RUN apt-get update && apt-get install -y \
       build-essential \
       curl \
       software-properties-common \
       git \
       && rm -rf /var/lib/apt/lists/*

   # Crear directorio de trabajo
   WORKDIR /app

   # Copiar archivos de dependencias
   COPY requirements.txt .

   # Instalar dependencias Python
   RUN pip install --no-cache-dir -r requirements.txt

   # Copiar código del proyecto
   COPY . .

   # Crear directorios necesarios
   RUN mkdir -p logs data reportes_revision test_results tests app static templates backups config

   # Exponer puerto de Streamlit
   EXPOSE 8501

   # Comando por defecto
   CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

Docker Compose Configuration
-----------------------------

The `docker-compose.yml` includes:

.. code-block:: yaml

   version: '3.8'

   services:
     metgo-3d:
       build: .
       container_name: metgo-3d-app
       ports:
         - "8501:8501"
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
         - ./reportes_revision:/app/reportes_revision
         - ./backups:/app/backups
         - ./config:/app/config
       environment:
         - PYTHONPATH=/app
         - PYTHONWARNINGS=ignore
         - OMP_NUM_THREADS=4
         - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
         - STREAMLIT_SERVER_PORT=8501
         - STREAMLIT_SERVER_ADDRESS=0.0.0.0
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8501/healthz"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s

Cloud Deployment
-----------------

### AWS Deployment

1. **Create EC2 Instance**:

.. code-block:: bash

   aws ec2 run-instances \
     --image-id ami-0c02fb55956c7d316 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-groups your-security-group

2. **Install Dependencies**:

.. code-block:: bash

   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install -r requirements.txt

3. **Deploy Application**:

.. code-block:: bash

   git clone <repository-url>
   cd PROYECTO_METGO_3D
   python3 ejecutar_sistema_completo.py

### Azure Deployment

1. **Create Virtual Machine**:

.. code-block:: bash

   az vm create \
     --resource-group myResourceGroup \
     --name metgo-3d-vm \
     --image UbuntuLTS \
     --admin-username azureuser \
     --generate-ssh-keys

2. **Install Dependencies**:

.. code-block:: bash

   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install -r requirements.txt

3. **Deploy Application**:

.. code-block:: bash

   git clone <repository-url>
   cd PROYECTO_METGO_3D
   python3 ejecutar_sistema_completo.py

### Google Cloud Deployment

1. **Create Compute Instance**:

.. code-block:: bash

   gcloud compute instances create metgo-3d-vm \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --zone=us-central1-a

2. **Install Dependencies**:

.. code-block:: bash

   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install -r requirements.txt

3. **Deploy Application**:

.. code-block:: bash

   git clone <repository-url>
   cd PROYECTO_METGO_3D
   python3 ejecutar_sistema_completo.py

Production Considerations
--------------------------

Security
~~~~~~~~~

1. **Environment Variables**: Use environment variables for sensitive data
2. **Access Control**: Implement proper access controls
3. **Network Security**: Configure firewalls and security groups
4. **Data Encryption**: Encrypt sensitive data
5. **Regular Updates**: Keep system updated

Performance
~~~~~~~~~~~

1. **Resource Monitoring**: Monitor CPU, memory, and disk usage
2. **Load Balancing**: Implement load balancing for high availability
3. **Caching**: Use caching for frequently accessed data
4. **Database Optimization**: Optimize database queries
5. **CDN**: Use CDN for static assets

Monitoring
~~~~~~~~~~

1. **System Monitoring**: Monitor system resources
2. **Application Monitoring**: Monitor application performance
3. **Log Monitoring**: Monitor application logs
4. **Alerting**: Set up alerts for critical issues
5. **Health Checks**: Implement health checks

Backup and Recovery
~~~~~~~~~~~~~~~~~~~

1. **Regular Backups**: Create regular backups
2. **Data Backup**: Backup data regularly
3. **Configuration Backup**: Backup configuration files
4. **Disaster Recovery**: Implement disaster recovery plan
5. **Testing**: Test backup and recovery procedures

Maintenance
~~~~~~~~~~~

1. **Regular Updates**: Keep system updated
2. **Security Patches**: Apply security patches
3. **Performance Tuning**: Tune performance regularly
4. **Log Rotation**: Rotate logs regularly
5. **Cleanup**: Clean up temporary files

Troubleshooting
---------------

Common Deployment Issues:

1. **Port Conflicts**: Check for port conflicts
2. **Permission Issues**: Verify file permissions
3. **Dependency Issues**: Check dependency versions
4. **Configuration Issues**: Verify configuration files
5. **Resource Issues**: Check system resources

For more information, see the complete documentation.
