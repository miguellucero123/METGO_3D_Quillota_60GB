@echo off
cd /d "%~dp0..\..\..\frontend\spati"
echo Instalando dependencias (echarts)...
call npm install
echo Iniciando interfaz SPATI localmente...
call npm run dev
pause
