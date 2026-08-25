@echo off
cd /d "%~dp0..\..\..\"
set METGO_ML_AUTO_TRAIN=0
echo Iniciando METGO API (Veras los errores aqui mismo)...
python backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
pause
