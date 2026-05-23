# METGO - Publicar en GitHub (PowerShell)
# Uso:
#   .\publicar_github.ps1
#   .\publicar_github.ps1 -Mensaje "Reorganización layout backend/frontend"
#   .\publicar_github.ps1 -SoloRevisar

param(
    [string]$Mensaje = "",
    [switch]$SoloRevisar
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
while ($root -and -not (Test-Path (Join-Path $root "metgo_paths.py"))) {
    $parent = Split-Path $root -Parent
    if ($parent -eq $root) { throw "No se encontró metgo_paths.py" }
    $root = $parent
}
Set-Location $root

function Show-Status {
    Write-Host "`n=== Rama ===" -ForegroundColor Cyan
    git branch -vv
    Write-Host "`n=== Remotos ===" -ForegroundColor Cyan
    git remote -v
    Write-Host "`n=== Status ===" -ForegroundColor Cyan
    git status -sb
    Write-Host "`n=== Últimos commits ===" -ForegroundColor Cyan
    git log -5 --oneline --decorate
}

Show-Status
if ($SoloRevisar) { exit 0 }

if (-not $Mensaje) {
    $Mensaje = Read-Host "Mensaje de commit"
}
if ([string]::IsNullOrWhiteSpace($Mensaje)) {
    throw "Mensaje de commit vacío"
}

$stagedEnv = git diff --cached --name-only 2>$null | Where-Object { $_ -match '\.env' }
if ($stagedEnv) { throw "Hay .env en staging. No publique credenciales." }

git add -A
$stagedEnv = git diff --cached --name-only | Where-Object { $_ -match '\.env' }
if ($stagedEnv) { throw "Tras git add, hay .env en staging." }

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Sin cambios para commitear." -ForegroundColor Yellow
    exit 0
}

git diff --cached --name-status
$ok = Read-Host "¿Commit y push? (S/N)"
if ($ok -notmatch '^[sS]') { git reset HEAD; exit 0 }

git commit -m $Mensaje
$branch = git branch --show-current
if (-not $branch) { $branch = "main" }

$upstream = git rev-parse --abbrev-ref "@{u}" 2>$null
if ($LASTEXITCODE -ne 0) {
    git push -u origin $branch
} else {
    git push origin $branch
}

Write-Host "`nPublicado en rama $branch" -ForegroundColor Green
