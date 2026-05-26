@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo ===== METGO — Preparar staging (NO hace commit) =====
echo.
git add -A
echo.
echo  Quitando del staging (secretos y caches locales)...
git reset HEAD .env 2>nul
git reset HEAD .env.local 2>nul
git reset HEAD .streamlit\secrets.toml 2>nul
git reset HEAD -- .pytest_cache 2>nul
REM Si datos_runtime apareciera (deberia estar en .gitignore):
git reset HEAD -- backend\08_Gestion_Datos\datos_runtime 2>nul
git reset HEAD -- 08_Gestion_Datos\datos_runtime 2>nul
echo.
echo --- Listo para commit (revisar bien) ---
git diff --cached --name-status
echo.
git diff --cached --shortstat
echo.
echo  Si ve .env o secrets.toml arriba, NO continúe: corrija con git reset HEAD ^<archivo^>
echo  Siguiente paso: 03_commit_manual.bat
echo.
pause
