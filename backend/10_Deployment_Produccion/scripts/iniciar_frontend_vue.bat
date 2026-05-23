@echo off
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
  cd frontend\vue
) else (
  cd /d "%~dp0..\.."
  cd 04_Dashboards_Unificados\frontend_vue
)
echo.
echo METGO Frontend Vue - http://127.0.0.1:5173
echo Requiere API en puerto 8080 (iniciar_api_rest.py en otra terminal)
echo Abra esa URL en Chrome o Edge (no use el preview embebido de Cursor).
echo.
call npm run dev
