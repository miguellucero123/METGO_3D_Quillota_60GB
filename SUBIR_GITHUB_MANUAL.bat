@echo off
chcp 65001 >nul
cd /d "%~dp0"
call "%~dp0backend\10_Deployment_Produccion\scripts\subir_github_menu.bat"
