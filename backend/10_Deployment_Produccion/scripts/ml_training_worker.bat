@echo off
REM Worker cola ML Fase 8 (cron / Task Scheduler tras encolar trabajos).
cd /d "%~dp0..\..\.."
python backend\08_Gestion_Datos\scripts\run_ml_training_worker.py --max 3
exit /b %ERRORLEVEL%
