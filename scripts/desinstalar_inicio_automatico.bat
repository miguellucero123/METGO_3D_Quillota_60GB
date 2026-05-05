@echo off
echo ============================================================
echo DESINSTALANDO INICIO AUTOMATICO DEL SISTEMA METGO
echo ============================================================
echo.

echo Eliminando entrada del registro...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "SistemaMETGO" /f

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo DESINSTALACION COMPLETADA EXITOSAMENTE
    echo ============================================================
    echo.
    echo El Sistema METGO ya no se iniciara automaticamente.
    echo.
    echo Para iniciar manualmente, ejecuta:
    echo iniciar_metgo.bat
    echo.
    echo Para detener el sistema, ejecuta:
    echo detener_sistema.py
    echo.
) else (
    echo.
    echo ============================================================
    echo ERROR EN LA DESINSTALACION
    echo ============================================================
    echo.
    echo No se pudo desinstalar el inicio automatico.
    echo La entrada puede no existir o necesitas permisos de administrador.
    echo.
)

pause
