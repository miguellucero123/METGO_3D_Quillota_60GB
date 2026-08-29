@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =======================================================
echo Guardando arreglos de SPATI (Graficos ECharts)
echo =======================================================
git add backend/05_APIs_Externas/api_rest/spati_routes.py
git commit -m "patch json serialization of numpy floats to fix ECharts"
git push
echo =======================================================
echo Listo. Los cambios se han subido a Github y Render.
echo =======================================================
pause
