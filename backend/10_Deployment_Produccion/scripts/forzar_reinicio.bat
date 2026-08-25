@echo off
echo ==============================================
echo MATANDO CUALQUIER API ANTERIOR PEGADA EN MEMORIA
echo ==============================================
taskkill /F /IM python.exe /T 2>nul
echo.
echo ==============================================
echo INICIANDO LA API CON EL CODIGO CORREGIDO...
echo ==============================================
cd /d "%~dp0..\..\..\"
set METGO_ML_AUTO_TRAIN=0
python backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
pause
