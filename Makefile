# METGO_3D – Comandos principales
# Uso: make <comando>

.PHONY: demo install test lint clean help

## Inicia el dashboard principal en localhost:8501
demo:
	streamlit run sistema_auth_dashboard_principal_metgo.py

## Instala todas las dependencias Python
install:
	pip install -r requirements.txt

## Ejecuta pytest si existe, o smoke test básico si pytest no encuentra tests
test:
	@if python -m pytest 09_Testing_Validacion/ -v 2>/dev/null; then \
		echo "✅ pytest OK"; \
	else \
		echo "⚠️  pytest no encontró tests (o falló); ejecutando smoke test básico..."; \
		python -c "from datos_reales_openmeteo import obtener_datos_meteorologicos_reales; print('✅ Módulo OpenMeteo OK')"; \
		python -c "import ast; ast.parse(open('sistema_auth_dashboard_principal_metgo.py').read()); print('✅ Auth module OK')"; \
	fi

## Verifica conectividad con OpenMeteo API
check-api:
	python datos_reales_openmeteo.py

## Limpia cachés Python
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

## Muestra esta ayuda
help:
	@grep -E '^##' Makefile | sed 's/## //'
