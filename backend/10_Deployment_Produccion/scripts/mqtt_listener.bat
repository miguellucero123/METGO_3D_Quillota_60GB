@echo off
REM Worker MQTT Fase 8 (proceso aparte de la API).
cd /d "%~dp0..\..\.."
python backend\08_Gestion_Datos\scripts\run_mqtt_listener.py
exit /b %ERRORLEVEL%
