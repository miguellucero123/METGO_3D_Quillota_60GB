@echo off
REM ETL meteorológico nocturno (módulo 08 → SQLite datos_runtime).
REM Programar en "Programador de tareas": diario ~03:00, usuario con Python en PATH.

cd /d "%~dp0..\..\.."

python backend\08_Gestion_Datos\scripts\run_etl_meteo_nightly.py
exit /b %ERRORLEVEL%
