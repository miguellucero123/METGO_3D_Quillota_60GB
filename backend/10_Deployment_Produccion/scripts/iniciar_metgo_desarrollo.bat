@echo off
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
  set API_SCRIPT=backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
  set VUE_DIR=frontend\vue
) else (
  cd /d "%~dp0..\.."
  set API_SCRIPT=10_Deployment_Produccion\scripts\iniciar_api_rest.py
  set VUE_DIR=04_Dashboards_Unificados\frontend_vue
)
echo Iniciando METGO (API + Vue)...
echo Arranque rapido: sin auto-entrenamiento ML al boot.
echo.
start "METGO API :8080" cmd /k "set METGO_ML_AUTO_TRAIN=0&& python %API_SCRIPT%"
timeout /t 3 /nobreak >nul
start "METGO Vue :5173" cmd /k "cd %VUE_DIR% && npm run dev"
echo.
echo Abra en el navegador: http://127.0.0.1:5173
echo Login: admin / admin123 (desarrollo)
echo API health: http://127.0.0.1:8080/api/health
pause
