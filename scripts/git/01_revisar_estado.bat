@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo ===== METGO — Revisar antes de subir =====
echo  Carpeta: %CD%
echo.
echo --- Remoto ---
git remote -v
echo.
echo --- Rama actual ---
git branch --show-current
echo.
echo --- Estado (resumen) ---
git status -sb
echo.
echo --- Ultimos 5 commits ---
git log -5 --oneline --decorate
echo.
echo --- Archivos modificados (sin staging) ---
git diff --name-status
echo.
pause
