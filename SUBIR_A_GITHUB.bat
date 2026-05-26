@echo off
chcp 65001 >nul
cd /d "%~dp0"
start notepad "%~dp0backend\10_Deployment_Produccion\scripts\INSTRUCCIONES_SUBIR_A_GITHUB.txt"
call "%~dp0backend\10_Deployment_Produccion\scripts\subir_github_menu.bat"
