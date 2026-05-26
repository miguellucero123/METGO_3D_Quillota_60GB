@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo  PASO 1 — Revisar (aun no sube nada)
echo  Repo: github.com/miguellucero123/METGO_3D_Quillota_60GB
echo  Rama: master
echo.
git remote -v
echo.
git branch --show-current
echo.
git status -sb
echo.
git log -3 --oneline
echo.
echo  Siguiente: doble clic en 2_subir_agregar_archivos.bat
echo.
pause
