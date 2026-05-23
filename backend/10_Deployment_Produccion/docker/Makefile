# 🌾 METGO 3D - Makefile
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

.PHONY: help install test clean run backup monitor deploy

# Variables
PYTHON = python3
PIP = pip3
VENV = venv
REQUIREMENTS = requirements.txt

# Ayuda
help:
	@echo "🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota"
	@echo "=================================================="
	@echo "Comandos disponibles:"
	@echo "  install    - Instalar dependencias del sistema"
	@echo "  test       - Ejecutar tests del sistema"
	@echo "  run        - Ejecutar sistema completo"
	@echo "  run-fast   - Ejecutar sistema en modo rápido"
	@echo "  clean      - Limpiar archivos temporales"
	@echo "  backup     - Crear backup del sistema"
	@echo "  monitor    - Monitorear estado del sistema"
	@echo "  deploy     - Desplegar sistema en producción"
	@echo "  docker     - Construir imagen Docker"
	@echo "  docker-run - Ejecutar contenedor Docker"

# Instalar dependencias
install:
	@echo "📦 Instalando dependencias del sistema METGO 3D..."
	$(PIP) install -r $(REQUIREMENTS)
	@echo "✅ Dependencias instaladas correctamente"

# Ejecutar tests
test:
	@echo "🧪 Ejecutando tests del sistema METGO 3D..."
	$(PYTHON) test_sistema.py
	@echo "✅ Tests completados"

# Ejecutar sistema completo
run:
	@echo "🚀 Ejecutando sistema METGO 3D completo..."
	$(PYTHON) ejecutar_sistema_completo.py completo
	@echo "✅ Sistema ejecutado correctamente"

# Ejecutar sistema en modo rápido
run-fast:
	@echo "⚡ Ejecutando sistema METGO 3D en modo rápido..."
	$(PYTHON) ejecutar_sistema_completo.py rapido
	@echo "✅ Sistema ejecutado en modo rápido"

# Limpiar archivos temporales
clean:
	@echo "🧹 Limpiando archivos temporales..."
	$(PYTHON) limpiar_sistema.py
	@echo "✅ Limpieza completada"

# Crear backup del sistema
backup:
	@echo "💾 Creando backup del sistema METGO 3D..."
	$(PYTHON) backup_sistema.py
	@echo "✅ Backup creado correctamente"

# Monitorear estado del sistema
monitor:
	@echo "📊 Monitoreando estado del sistema METGO 3D..."
	$(PYTHON) monitor_sistema.py
	@echo "✅ Monitoreo completado"

# Desplegar sistema en producción
deploy:
	@echo "🚀 Desplegando sistema METGO 3D en producción..."
	$(PYTHON) ejecutar_sistema_completo.py deployment
	@echo "✅ Sistema desplegado en producción"

# Construir imagen Docker
docker:
	@echo "🐳 Construyendo imagen Docker de METGO 3D..."
	docker build -t metgo-3d:latest .
	@echo "✅ Imagen Docker construida"

# Ejecutar contenedor Docker
docker-run:
	@echo "🐳 Ejecutando contenedor Docker de METGO 3D..."
	docker run -p 8501:8501 metgo-3d:latest
	@echo "✅ Contenedor Docker ejecutándose"

# Ejecutar con docker-compose
docker-compose:
	@echo "🐳 Ejecutando con docker-compose..."
	docker-compose up -d
	@echo "✅ Servicios ejecutándose con docker-compose"

# Detener servicios docker-compose
docker-stop:
	@echo "🐳 Deteniendo servicios docker-compose..."
	docker-compose down
	@echo "✅ Servicios detenidos"

# Instalar sistema completo
install-system:
	@echo "🔧 Instalando sistema METGO 3D completo..."
	$(PYTHON) instalar_sistema.py
	@echo "✅ Sistema instalado correctamente"

# Ejecutar análisis meteorológico
analyze:
	@echo "🌤️ Ejecutando análisis meteorológico..."
	$(PYTHON) ejecutar_sistema_completo.py analisis
	@echo "✅ Análisis meteorológico completado"

# Generar reportes
reports:
	@echo "📋 Generando reportes del sistema..."
	$(PYTHON) ejecutar_sistema_completo.py reportes
	@echo "✅ Reportes generados correctamente"

# Verificar estado del sistema
status:
	@echo "📊 Verificando estado del sistema METGO 3D..."
	$(PYTHON) monitor_sistema.py
	@echo "✅ Estado del sistema verificado"

# Actualizar dependencias
update:
	@echo "🔄 Actualizando dependencias del sistema..."
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	@echo "✅ Dependencias actualizadas"

# Formatear código
format:
	@echo "🎨 Formateando código del sistema..."
	black .
	@echo "✅ Código formateado"

# Linting del código
lint:
	@echo "🔍 Ejecutando linting del código..."
	flake8 .
	@echo "✅ Linting completado"

# Ejecutar todos los comandos de desarrollo
dev-setup: install test clean
	@echo "🔧 Configuración de desarrollo completada"

# Ejecutar todos los comandos de producción
prod-setup: install test clean backup deploy
	@echo "🚀 Configuración de producción completada"
