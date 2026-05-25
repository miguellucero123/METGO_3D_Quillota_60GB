@echo off
chcp 65001 >nul
setlocal

if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else (
  cd /d "%~dp0..\..\"
)

echo ======================================================================
echo  METGO - Preparar commit para GitHub
echo ======================================================================
echo.

REM Restos de migración (carpeta 04 vacía o cache Vue duplicado)
if exist "04_Dashboards_Unificados" (
  echo [Limpieza] Eliminando restos: 04_Dashboards_Unificados\
  rmdir /s /q "04_Dashboards_Unificados" 2>nul
)

echo --- Resumen corto ---
git status -sb 2>nul
echo.

echo --- ¿Cuántos archivos cambiarían? ---
git status --porcelain 2>nul | find /c /v ""
echo lineas en status
echo.

echo --- node_modules (NO deben subirse) ---
if exist "frontend\vue\node_modules" (
  echo OK: frontend\vue\node_modules existe localmente pero esta en .gitignore
) else (
  echo frontend\vue\node_modules no encontrado
)

echo --- Respaldos (NO deben subirse) ---
if exist "backend\12_Respaldos_Archivos\backups" (
  echo AVISO: backend\12_...\backups existe - debe estar ignorado por .gitignore
)

echo.
echo Siguiente paso (manual):
echo   docs\manuales\SUBIR_GITHUB_MANUAL.md
echo   SUBIR_GITHUB_MANUAL.bat
echo.
pause
