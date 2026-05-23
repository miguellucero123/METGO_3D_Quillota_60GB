@echo off
echo Iniciando METGO 3D - Version 60GB
echo ==================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no encontrado
    pause
    exit /b 1
)
echo Iniciando dashboard...
echo URL: http://localhost:8501
echo Usuario: admin
echo Contrasena: admin123
echo.
python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true
pause
