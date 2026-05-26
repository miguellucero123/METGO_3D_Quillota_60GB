# METGO — Subida manual a GitHub (PowerShell)
# Uso:  Set-Location D:\METGO_3D_Quillota_60GB
#       .\scripts\git\subir_github_manual.ps1
# Solo revisar: .\scripts\git\subir_github_manual.ps1 -SoloRevisar

param(
    [switch]$SoloRevisar
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git"
$RamaEsperada = "master"

$root = $PSScriptRoot
while ($root -and -not (Test-Path (Join-Path $root "metgo_paths.py"))) {
    $parent = Split-Path $root -Parent
    if ($parent -eq $root) { throw "No se encontró metgo_paths.py" }
    $root = $parent
}
Set-Location $root

Write-Host "`n=== METGO — GitHub manual ===" -ForegroundColor Cyan
Write-Host "Carpeta: $root"
Write-Host "Remoto esperado: $RepoUrl"
Write-Host "Rama: $(git branch --show-current)`n"

git remote -v
git status -sb
git log -3 --oneline

if ($SoloRevisar) { exit 0 }

$null = Read-Host "Enter = preparar staging (git add -A y quitar secretos)"
git add -A
foreach ($f in @(".env", ".env.local", ".streamlit/secrets.toml")) {
    if (Test-Path $f) { git reset HEAD $f 2>$null }
}
git reset HEAD -- .pytest_cache 2>$null
git reset HEAD -- backend/08_Gestion_Datos/datos_runtime 2>$null

Write-Host "`n--- Staging ---" -ForegroundColor Yellow
git diff --cached --name-status
$bad = git diff --cached --name-only | Where-Object {
    $_ -match '\.env$|secrets\.toml|datos_runtime|\.db$'
}
if ($bad) {
    Write-Host "BLOQUEADO: archivos prohibidos en staging:" -ForegroundColor Red
    $bad | ForEach-Object { Write-Host "  $_" }
    exit 1
}

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Sin cambios para commitear." -ForegroundColor Yellow
    exit 0
}

$msg = Read-Host "Mensaje de commit"
if ([string]::IsNullOrWhiteSpace($msg)) { throw "Mensaje vacío" }

git commit -m $msg
$rama = git branch --show-current
if ($rama -ne $RamaEsperada) {
    Write-Host "Aviso: rama '$rama' (esperada: $RamaEsperada)" -ForegroundColor Yellow
}
$confirm = Read-Host "¿Push origin $rama? (S/N)"
if ($confirm -notmatch '^[sS]') { exit 0 }

git push -u origin $rama
Write-Host "`nListo: $RepoUrl/tree/$rama" -ForegroundColor Green
