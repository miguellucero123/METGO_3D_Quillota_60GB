@echo off
echo ========================================
echo   METGO 3D - CIERRE Y APERTURA
echo ========================================
echo.

echo PASO 1: Cerrando proyecto actual...
echo.
taskkill /f /im python.exe 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im chrome.exe 2>nul
taskkill /f /im msedge.exe 2>nul

echo OK: Proyecto actual cerrado
echo.

echo PASO 2: Abriendo proyecto en disco D:...
echo.
cd /d "D:\METGO_3D_Quillota_60GB"

echo Directorio actual: %CD%
echo.

echo PASO 3: Verificando proyecto migrado...
if exist "sistema_unificado_con_conectores.py" (
    echo OK: Sistema principal encontrado
) else (
    echo ERROR: Sistema principal no encontrado en disco D:
    echo Verifique que la migracion se haya completado correctamente
    pause
    exit /b 1
)

echo.
echo PASO 4: Iniciando sistema...
echo.
echo Opciones disponibles:
echo 1. Ejecutar dashboard web (Streamlit)
echo 2. Abrir en Visual Studio Code
echo 3. Abrir Jupyter Lab
echo 4. Solo abrir explorador de archivos
echo.

set /p opcion="Seleccione una opcion (1-4): "

if "%opcion%"=="1" (
    echo Iniciando dashboard web...
    echo Dashboard disponible en: http://localhost:8501
    streamlit run sistema_unificado_con_conectores.py
) else if "%opcion%"=="2" (
    echo Abriendo Visual Studio Code...
    code .
) else if "%opcion%"=="3" (
    echo Abriendo Jupyter Lab...
    jupyter lab
) else if "%opcion%"=="4" (
    echo Abriendo explorador de archivos...
    explorer .
) else (
    echo Opcion no valida, abriendo dashboard por defecto...
    streamlit run sistema_unificado_con_conectores.py
)

echo.
echo Proyecto METGO 3D abierto en disco D:
echo Ubicacion: D:\METGO_3D_Quillota_60GB
echo.
pause


