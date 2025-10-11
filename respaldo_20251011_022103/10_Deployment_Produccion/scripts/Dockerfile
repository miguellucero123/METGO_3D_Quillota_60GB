# 🌾 METGO 3D - Dockerfile
# Sistema Meteorológico Agrícola Quillota - Contenedor Principal

# Usar imagen base de Python 3.9
FROM python:3.9-slim

# Metadatos
LABEL maintainer="Sistema METGO 3D"
LABEL version="2.0"
LABEL description="Sistema Meteorológico Agrícola Quillota"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    vim \
    nano \
    htop \
    tree \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash metgo

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data logs config reportes graficos dashboard_html temp resultados

# Cambiar permisos
RUN chown -R metgo:metgo /app

# Cambiar a usuario no-root
USER metgo

# Exponer puertos
EXPOSE 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009 8050

# Variables de entorno para la aplicación
ENV METGO_ENV=production
ENV METGO_DEBUG=False
ENV METGO_LOG_LEVEL=INFO

# Comando por defecto
CMD ["python", "orquestador_metgo_avanzado.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=10)" || exit 1