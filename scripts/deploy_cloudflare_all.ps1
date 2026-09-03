$ErrorActionPreference = "Stop"

Write-Host "=== Despliegue de SPAs a Cloudflare Pages ===" -ForegroundColor Cyan

$base_dir = Get-Location

$sites = @(
    @{ folder="frontend\vue"; project="metgo-quillota" },
    @{ folder="frontend\copiapo"; project="metgo-copiapo" },
    @{ folder="frontend\mantos_blancos"; project="metgo-mantos" },
    @{ folder="frontend\spati"; project="metgo-spati" }
)

foreach ($site in $sites) {
    Write-Host ""
    Write-Host ">> Procesando $($site.project) en $($site.folder)" -ForegroundColor Yellow
    Set-Location (Join-Path $base_dir $site.folder)

    Write-Host "Instalando dependencias (npm ci)..."
    cmd /c "npm ci"
    
    Write-Host "Construyendo (npm run build)..."
    cmd /c "npm run build"
    
    Write-Host "Desplegando a Cloudflare Pages ($($site.project))..."
    # Usa cmd /c para garantizar que npx se resuelva correctamente en Windows
    cmd /c "npx wrangler pages deploy dist --project-name=$($site.project)"
}

# Restaurar directorio
Set-Location $base_dir

# Opcional Paine (repositorio aparte)
$paine_dir = "D:\metgo-paine"
if (Test-Path $paine_dir) {
    Write-Host ""
    Write-Host ">> Procesando metgo-paine en $paine_dir" -ForegroundColor Yellow
    Set-Location $paine_dir
    Write-Host "Instalando dependencias (npm ci)..."
    cmd /c "npm ci"
    Write-Host "Desplegando Paine (npm run pages:deploy)..."
    cmd /c "npm run pages:deploy"
} else {
    Write-Host ""
    Write-Host ">> Repositorio Paine no encontrado en $paine_dir. Saltando..." -ForegroundColor Gray
}

Set-Location $base_dir
Write-Host ""
Write-Host "=== Todos los despliegues han terminado ===" -ForegroundColor Green
Write-Host "Seguridad Pages: scripts/ops/CLOUDFLARE_PAGES_HARDENING.md (previews, dominios, Access)." -ForegroundColor Yellow
Write-Host "No olvides actualizar METGO_CORS_ORIGINS en Render si cambian las URLs." -ForegroundColor Yellow
