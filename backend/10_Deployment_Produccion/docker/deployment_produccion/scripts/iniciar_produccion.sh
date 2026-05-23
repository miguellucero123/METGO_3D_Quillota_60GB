#!/bin/bash
echo "============================================================"
echo "METGO 3D QUILLOTA - SISTEMA DE PRODUCCION"
echo "============================================================"
echo

echo "[INICIANDO] Verificando sistema..."
python3 -c "import streamlit, pandas, plotly, sklearn; print('[OK] Dependencias verificadas')"

echo
echo "[INICIANDO] Lanzando sistema de produccion..."
python3 scripts/iniciar_produccion.py

echo
echo "[COMPLETADO] Sistema iniciado"
echo
echo "Servicios disponibles:"
echo "- Dashboard Principal: http://localhost:8501"
echo "- Dashboard Agricola: http://localhost:8510"
echo "- Monitoreo: http://localhost:8502"
