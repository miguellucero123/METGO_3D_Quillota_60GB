#!/bin/bash
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
gcloud compute instances create metgo-ml-server \
    --zone=$ZONE \
    --machine-type=c2-standard-8 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd \
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
