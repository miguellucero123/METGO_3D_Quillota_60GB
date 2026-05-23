@echo off
echo ============================================================
echo METGO 3D QUILLOTA - SISTEMA OPTIMIZADO
echo ============================================================
echo.

echo [INICIANDO] Verificando sistema...
python -c "import streamlit, pandas, plotly, sqlite3; print('[OK] Dependencias verificadas')"

echo.
echo [OPTIMIZANDO] Aplicando optimizaciones...
python optimizador_dashboards_metgo.py

echo.
echo [INICIANDO] Lanzando dashboard principal...
start /B python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true

echo.
echo [INICIANDO] Lanzando dashboard agricola avanzado...
start /B python -m streamlit run dashboard_agricola_avanzado.py --server.port 8510 --server.headless true

echo.
echo ============================================================
echo SISTEMA METGO 3D QUILLOTA INICIADO
echo ============================================================
echo.
echo Dashboards disponibles:
echo - Principal: http://localhost:8501
echo - Agricola Avanzado: http://localhost:8510
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
