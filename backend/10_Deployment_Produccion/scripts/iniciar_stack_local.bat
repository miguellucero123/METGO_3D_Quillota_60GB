@echo off
REM METGO — API + Vue + dashboards Streamlit meteorologicos (8502, 8506)
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else (
  cd /d "%~dp0..\.."
)
echo Stack local METGO: API 8080, Vue 5173, Streamlit 8502 y 8506
echo.
start "METGO API :8080" cmd /k "set METGO_ML_AUTO_TRAIN=0&& python backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py"
timeout /t 4 /nobreak >nul
start "METGO Vue :5173" cmd /k "cd frontend\vue && npm run dev"
timeout /t 2 /nobreak >nul
start "METGO Meteo Pro 8502" cmd /k "streamlit run frontend\dashboards\dashboard_meteorologico_profesional.py --server.port 8502"
start "METGO Visual 8506" cmd /k "streamlit run frontend\dashboards\dashboard_visualizaciones_avanzadas.py --server.port 8506"
start "METGO Agricola 8503" cmd /k "streamlit run frontend\dashboards\dashboard_agricola_inteligente.py --server.port 8503"
start "METGO ML 8505" cmd /k "streamlit run frontend\dashboards\dashboard_ia_ml_avanzado.py --server.port 8505"
start "METGO Precision 8508" cmd /k "streamlit run frontend\dashboards\dashboard_agricultura_precision.py --server.port 8508"
echo.
echo Vue:        http://127.0.0.1:5173
echo API:        http://127.0.0.1:8080/api/health
echo Streamlit:  8502 8503 8505 8506 8508
pause
