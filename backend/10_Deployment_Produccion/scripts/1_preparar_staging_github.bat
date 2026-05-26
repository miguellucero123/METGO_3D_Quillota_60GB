@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
call "%~dp0_git_ir_a_raiz.bat" || exit /b 1

echo ======================================================================
echo  PASO 1/3 — Preparar staging (git add) — SIN commit ni push
echo  Repo: %CD%
echo ======================================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1 || (
  echo [ERROR] No es un repositorio Git.
  exit /b 1
)

echo --- Estado antes ---
git status -sb
echo.

echo Agregando cambios: git add -A
echo (Respeta .gitignore: .env, node_modules, backups, etc.)
git add -A
if errorlevel 1 exit /b 1

REM Quitar secretos del staging
git rm --cached -f .env 2>nul
git reset HEAD .env 2>nul
git reset HEAD .env.local 2>nul
git reset HEAD .streamlit\secrets.toml 2>nul

git diff --cached --name-only 2>nul | findstr /i /r "\\.env$ secrets\.toml$" >nul 2>&1
if not errorlevel 1 (
  echo.
  echo [ERROR] Hay credenciales en staging. Ejecute:
  echo   quitar_secretos_del_staging.bat
  exit /b 1
)

git diff --cached --quiet
if not errorlevel 1 (
  echo.
  echo No hay cambios para commitear.
  goto :fin
)

echo.
echo --- Archivos listos para commit (staging) ---
git diff --cached --shortstat
git diff --cached --name-status
echo.
echo ======================================================================
echo  PASO 2 — Haga el commit USTED (elija una opcion):
echo.
echo  A) Mensaje sugerido (integracion fases 4-10):
echo     2_commit_github.bat
echo.
echo  B) Mensaje personalizado:
echo     2_commit_github.bat "Su mensaje aqui"
echo.
echo  C) Manual en esta ventana:
echo     git commit -m "Su mensaje"
echo.
echo  PASO 3 — Subir a GitHub:
echo     3_push_github.bat
echo ======================================================================

:fin
pause
