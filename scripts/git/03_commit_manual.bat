@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo ===== METGO — Commit MANUAL =====
echo.
git diff --cached --quiet
if %ERRORLEVEL%==0 (
  echo  No hay nada en staging. Ejecute primero: 02_preparar_staging.bat
  pause
  exit /b 1
)
echo  Archivos en staging:
git diff --cached --name-status
echo.
set /p MSG=Mensaje de commit: 
if "%MSG%"=="" (
  echo  Mensaje vacio. Cancelado.
  pause
  exit /b 1
)
git commit -m "%MSG%"
if %ERRORLEVEL%==0 (
  echo.
  echo  Commit OK. Siguiente: 04_push_master.bat
) else (
  echo  Error en commit.
)
echo.
pause
