@echo off
echo ============================================================
echo SISTEMA METGO - AUTOMATIZACION RAPIDA
echo ============================================================
echo.
echo 1. Iniciar Sistema
echo 2. Detener Sistema  
echo 3. Monitorear Sistema
echo 4. Reiniciar Sistema
echo 5. Salir
echo.
set /p opcion="Selecciona una opcion (1-5): "

if "%opcion%"=="1" (
    echo.
    echo Iniciando Sistema METGO...
    python iniciar_sistema_automatico.py
    pause
    goto :eof
)

if "%opcion%"=="2" (
    echo.
    echo Deteniendo Sistema METGO...
    python detener_sistema.py
    pause
    goto :eof
)

if "%opcion%"=="3" (
    echo.
    echo Monitoreando Sistema METGO...
    python monitorear_sistema.py
    pause
    goto :eof
)

if "%opcion%"=="4" (
    echo.
    echo Reiniciando Sistema METGO...
    python reiniciar_sistema.py
    pause
    goto :eof
)

if "%opcion%"=="5" (
    echo.
    echo Saliendo...
    goto :eof
)

echo.
echo Opcion no valida. Intenta de nuevo.
pause
goto :eof
