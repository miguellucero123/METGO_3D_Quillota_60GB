#Requires -Version 5.1
<#
.SYNOPSIS
  Purga del historial git rutas sensibles (requiere git-filter-repo).

.NOTES
  1. Commit o stash de cambios pendientes ANTES de ejecutar.
  2. Instalar: pip install git-filter-repo
  3. Force-push a main/master SOLO con OK explícito del dueño del repo.
     Este script NO hace push.
#>
$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

if (-not (Get-Command git-filter-repo -ErrorAction SilentlyContinue)) {
    Write-Host "Instala git-filter-repo: pip install git-filter-repo"
    exit 1
}

$status = git status --porcelain
if ($status) {
    Write-Host "Working tree no limpio. Haz commit/stash antes de purgar historial."
    Write-Host $status
    exit 1
}

Write-Host "Purgando rutas sensibles del historial local..."
git filter-repo --force --invert-paths `
  --path-glob "**/.env" `
  --path-glob "**/.env.development" `
  --path-glob "**/.env.local" `
  --path-glob "**/.env.production" `
  --path-glob "**/secrets.toml" `
  --path-glob "**/metgo.env" `
  --path "backend/12_Respaldos_Archivos/archivos_obsoletos/metgo.env" `
  --path "backend/12_Respaldos_Archivos/archivos_obsoletos/config/usuarios.json" `
  --path "backend/01_Sistema_Meteorologico/scripts/api_keys_meteorologicas.json" `
  --path "frontend/vue/.env.development" `
  --path "frontend/vue_backup/.env.development"

Write-Host ""
Write-Host "Historial local limpio. Remoto aún tiene commits viejos."
Write-Host "Para publicar (DESTRUCTIVO, pide OK explícito al equipo):"
Write-Host "  git push --force-with-lease origin HEAD:main"
Write-Host "  # o master, según el branch canónico"
Write-Host "Luego: rotar secretos en Render/WP (docs/roadmap/deuda-tecnica/DT-4-ROTACION_SECRETOS.md)"
