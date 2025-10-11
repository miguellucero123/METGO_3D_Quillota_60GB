"""
GUÍA DE MIGRACIÓN A LA NUBE - METGO 3D QUILLOTA
Guía completa para migrar el sistema a Google Cloud Platform
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

class GuiaMigracionCloud:
    def __init__(self):
        self.configuracion_cloud = {
            'proyecto_id': 'metgo-3d-quillota',
            'region': 'us-central1',
            'zona': 'us-central1-a',
            'servicios_requeridos': [
                'compute.googleapis.com',
                'storage.googleapis.com',
                'aiplatform.googleapis.com',
                'run.googleapis.com',
                'cloudsql.googleapis.com'
            ]
        }
    
    def generar_guia_completa(self):
        """Generar guía completa de migración"""
        guia = f"""
# 🚀 **GUÍA COMPLETA DE MIGRACIÓN A LA NUBE - METGO 3D QUILLOTA**

## 📋 **PASO 1: PREPARACIÓN INICIAL**

### **1.1 Crear Cuenta Google Cloud**
1. Ir a: https://console.cloud.google.com/
2. Crear proyecto: `metgo-3d-quillota`
3. Habilitar facturación
4. Obtener $300 créditos gratuitos (nuevos usuarios)

### **1.2 Instalar Google Cloud SDK**
```bash
# Windows (PowerShell como Administrador)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
Start-Process -FilePath "$env:Temp\GoogleCloudSDKInstaller.exe" -ArgumentList "/S" -Wait

# Verificar instalación
gcloud --version
```

### **1.3 Configurar Autenticación**
```bash
# Inicializar gcloud
gcloud init

# Autenticar
gcloud auth login

# Configurar proyecto
gcloud config set project metgo-3d-quillota
```

## 📋 **PASO 2: CONFIGURACIÓN DE SERVICIOS**

### **2.1 Habilitar APIs Necesarias**
```bash
# Habilitar servicios requeridos
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudsql.googleapis.com
```

### **2.2 Crear Bucket de Almacenamiento**
```bash
# Crear bucket para modelos y datos
gsutil mb -p metgo-3d-quillota -c STANDARD -l us-central1 gs://metgo-3d-quillota-models

# Crear bucket para datos meteorológicos
gsutil mb -p metgo-3d-quillota -c STANDARD -l us-central1 gs://metgo-3d-quillota-data
```

## 📋 **PASO 3: CONFIGURACIÓN DE COMPUTE ENGINE**

### **3.1 Crear Instancia VM Optimizada para ML**
```bash
# Crear instancia con GPU (opcional pero recomendado)
gcloud compute instances create metgo-ml-server \\
    --zone=us-central1-a \\
    --machine-type=n1-standard-4 \\
    --accelerator=type=nvidia-tesla-t4,count=1 \\
    --image-family=deeplearning-platform-release \\
    --image-project=deeplearning-platform-release \\
    --boot-disk-size=50GB \\
    --boot-disk-type=pd-ssd \\
    --maintenance-policy=TERMINATE \\
    --restart-on-failure

# Sin GPU (más económico)
gcloud compute instances create metgo-ml-server \\
    --zone=us-central1-a \\
    --machine-type=c2-standard-8 \\
    --image-family=ubuntu-2004-lts \\
    --image-project=ubuntu-os-cloud \\
    --boot-disk-size=50GB \\
    --boot-disk-type=pd-ssd
```

### **3.2 Configurar Instancia**
```bash
# Conectar a la instancia
gcloud compute ssh metgo-ml-server --zone=us-central1-a

# Instalar dependencias
sudo apt update
sudo apt install -y python3-pip git

# Instalar Python packages
pip3 install -r requirements.txt
pip3 install google-cloud-storage google-cloud-aiplatform
```

## 📋 **PASO 4: MIGRACIÓN DE DATOS Y MODELOS**

### **4.1 Subir Datos a Cloud Storage**
```bash
# Subir datos históricos
gsutil cp -r data/ gs://metgo-3d-quillota-data/

# Subir modelos entrenados
gsutil cp -r modelos_ultra_optimizados/ gs://metgo-3d-quillota-models/
```

### **4.2 Configurar Cloud SQL**
```bash
# Crear instancia de Cloud SQL
gcloud sql instances create metgo-database \\
    --database-version=POSTGRES_13 \\
    --tier=db-f1-micro \\
    --region=us-central1

# Crear base de datos
gcloud sql databases create metgo_db --instance=metgo-database

# Crear usuario
gcloud sql users create metgo_user \\
    --instance=metgo-database \\
    --password=metgo_secure_password_2024
```

## 📋 **PASO 5: DEPLOYMENT CON CLOUD RUN**

### **5.1 Crear Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "streamlit", "run", "sistema_unificado_con_conectores.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

### **5.2 Deploy a Cloud Run**
```bash
# Construir y subir imagen
gcloud builds submit --tag gcr.io/metgo-3d-quillota/metgo-app

# Deploy a Cloud Run
gcloud run deploy metgo-app \\
    --image gcr.io/metgo-3d-quillota/metgo-app \\
    --platform managed \\
    --region us-central1 \\
    --allow-unauthenticated \\
    --memory 2Gi \\
    --cpu 2 \\
    --max-instances 10
```

## 📋 **PASO 6: CONFIGURACIÓN DE VERTEX AI**

### **6.1 Crear Endpoint para Modelos**
```python
# Código para configurar Vertex AI
from google.cloud import aiplatform

aiplatform.init(project="metgo-3d-quillota", location="us-central1")

# Crear endpoint para modelos híbridos
endpoint = aiplatform.Endpoint.create(
    display_name="metgo-hybrid-models",
    description="Endpoint para modelos híbridos de METGO 3D"
)
```

## 💰 **ESTIMACIÓN DE COSTOS MENSUALES**

### **Configuración Básica (Recomendada para empezar):**
- **Compute Engine (c2-standard-8):** $200/mes
- **Cloud Storage (100GB):** $2/mes
- **Cloud SQL (db-f1-micro):** $25/mes
- **Cloud Run:** $10/mes
- **Vertex AI:** $50/mes
- **Total:** ~$287/mes

### **Configuración Avanzada (Con GPU):**
- **Compute Engine (con T4 GPU):** $500/mes
- **Cloud Storage:** $5/mes
- **Cloud SQL:** $50/mes
- **Cloud Run:** $20/mes
- **Vertex AI:** $100/mes
- **Total:** ~$675/mes

## 🎯 **VENTAJAS DE LA MIGRACIÓN**

### **Rendimiento:**
- ✅ **Escalabilidad infinita**
- ✅ **GPU disponible para modelos complejos**
- ✅ **Redes de alta velocidad**
- ✅ **Almacenamiento ilimitado**

### **Funcionalidades:**
- ✅ **APIs automáticas**
- ✅ **Monitoreo avanzado**
- ✅ **Backup automático**
- ✅ **Seguridad empresarial**

### **Desarrollo:**
- ✅ **Colab Pro+ integrado**
- ✅ **Vertex AI para AutoML**
- ✅ **CI/CD automatizado**
- ✅ **Colaboración en equipo**

## 🚀 **PRÓXIMOS PASOS**

1. **Ejecutar script de migración automática**
2. **Probar sistema en la nube**
3. **Implementar Sistema de Riego Inteligente**
4. **Integrar IoT y sensores**
5. **Configurar alertas automáticas**

---
**¿Listo para comenzar la migración?**
        """
        
        return guia
    
    def crear_script_migracion_automatica(self):
        """Crear script de migración automática"""
        script = '''#!/bin/bash
# Script de migración automática a Google Cloud Platform

echo "🚀 INICIANDO MIGRACIÓN AUTOMÁTICA - METGO 3D QUILLOTA"
echo "=================================================="

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK no está instalado"
    echo "Por favor instala gcloud primero"
    exit 1
fi

echo "✅ Google Cloud SDK encontrado"

# Configurar proyecto
PROJECT_ID="metgo-3d-quillota"
REGION="us-central1"
ZONE="us-central1-a"

echo "📋 Configurando proyecto: $PROJECT_ID"

# Habilitar APIs
echo "🔧 Habilitando APIs necesarias..."
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudsql.googleapis.com

# Crear buckets
echo "🗄️ Creando buckets de almacenamiento..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://metgo-3d-quillota-models 2>/dev/null || echo "Bucket ya existe"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://metgo-3d-quillota-data 2>/dev/null || echo "Bucket ya existe"

# Subir archivos locales
echo "📤 Subiendo archivos al cloud..."
if [ -d "modelos_ultra_optimizados" ]; then
    gsutil cp -r modelos_ultra_optimizados/ gs://metgo-3d-quillota-models/
    echo "✅ Modelos subidos"
fi

if [ -d "data" ]; then
    gsutil cp -r data/ gs://metgo-3d-quillota-data/
    echo "✅ Datos subidos"
fi

# Crear instancia VM
echo "🖥️ Creando instancia VM..."
gcloud compute instances create metgo-ml-server \\
    --zone=$ZONE \\
    --machine-type=c2-standard-8 \\
    --image-family=ubuntu-2004-lts \\
    --image-project=ubuntu-os-cloud \\
    --boot-disk-size=50GB \\
    --boot-disk-type=pd-ssd \\
    --tags=http-server,https-server 2>/dev/null || echo "Instancia ya existe"

echo "🎉 MIGRACIÓN COMPLETADA"
echo "======================="
echo "📊 Recursos creados:"
echo "  - Proyecto: $PROJECT_ID"
echo "  - Buckets: metgo-3d-quillota-models, metgo-3d-quillota-data"
echo "  - VM: metgo-ml-server"
echo ""
echo "🔗 Próximos pasos:"
echo "  1. gcloud compute ssh metgo-ml-server --zone=$ZONE"
echo "  2. Instalar dependencias en la VM"
echo "  3. Configurar aplicación"
echo ""
echo "💰 Costo estimado: ~$200-300/mes"
'''
        return script
    
    def crear_requirements_cloud(self):
        """Crear requirements.txt optimizado para cloud"""
        requirements = '''# METGO 3D QUILLOTA - Requirements para Cloud
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
scikit-learn>=1.3.0
joblib>=1.3.0
sqlite3
requests>=2.31.0

# Google Cloud
google-cloud-storage>=2.10.0
google-cloud-aiplatform>=1.35.0
google-cloud-sql-connector>=1.4.0
google-cloud-secret-manager>=2.16.0

# IoT y sensores
paho-mqtt>=1.6.0
Adafruit-DHT>=1.4.0

# Sistema de riego
RPi.GPIO>=0.7.1
schedule>=1.2.0

# Monitoreo
psutil>=5.9.0
python-dotenv>=1.0.0
'''
        return requirements

def main():
    """Función principal para generar guía de migración"""
    guia = GuiaMigracionCloud()
    
    # Generar guía completa
    guia_completa = guia.generar_guia_completa()
    
    # Guardar guía
    with open('GUIA_MIGRACION_CLOUD.md', 'w', encoding='utf-8') as f:
        f.write(guia_completa)
    
    # Crear script de migración
    script = guia.crear_script_migracion_automatica()
    with open('migrar_a_cloud.sh', 'w', encoding='utf-8') as f:
        f.write(script)
    
    # Crear requirements para cloud
    requirements = guia.crear_requirements_cloud()
    with open('requirements_cloud.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("[OK] GUIA DE MIGRACION CREADA")
    print("===========================")
    print("[ARCHIVOS] Archivos generados:")
    print("  - GUIA_MIGRACION_CLOUD.md")
    print("  - migrar_a_cloud.sh")
    print("  - requirements_cloud.txt")
    print("")
    print("[PROXIMO] Proximo paso: Ejecutar migrar_a_cloud.sh")

if __name__ == "__main__":
    main()
