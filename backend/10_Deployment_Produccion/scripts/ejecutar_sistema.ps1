# 🚀 EJECUTOR MAESTRO DEL SISTEMA METGO 3D - SCRIPT POWERSHELL
# Sistema Meteorológico Agrícola Quillota - Versión Operativa

param(
    [string]$Modo = "completo",
    [switch]$Help
)

# Función para mostrar ayuda
function Show-Help {
    Write-Host "🚀 EJECUTOR MAESTRO DEL SISTEMA METGO 3D" -ForegroundColor Blue
    Write-Host "Sistema Meteorológico Agrícola Quillota - Versión Operativa" -ForegroundColor Blue
    Write-Host ""
    Write-Host "USO:" -ForegroundColor Cyan
    Write-Host "    .\ejecutar_sistema.ps1 [MODO]" -ForegroundColor White
    Write-Host ""
    Write-Host "MODOS DISPONIBLES:" -ForegroundColor Cyan
    Write-Host "    completo     - Ejecutar todos los notebooks (por defecto)" -ForegroundColor White
    Write-Host "    rapido      - Ejecutar solo notebooks esenciales" -ForegroundColor White
    Write-Host "    analisis    - Ejecutar solo notebooks de análisis" -ForegroundColor White
    Write-Host "    testing     - Ejecutar solo notebooks de testing" -ForegroundColor White
    Write-Host "    deployment  - Ejecutar solo notebooks de deployment" -ForegroundColor White
    Write-Host ""
    Write-Host "EJEMPLOS:" -ForegroundColor Cyan
    Write-Host "    .\ejecutar_sistema.ps1" -ForegroundColor White
    Write-Host "    .\ejecutar_sistema.ps1 completo" -ForegroundColor White
    Write-Host "    .\ejecutar_sistema.ps1 rapido" -ForegroundColor White
    Write-Host "    .\ejecutar_sistema.ps1 testing" -ForegroundColor White
    Write-Host ""
    Write-Host "CARACTERÍSTICAS:" -ForegroundColor Cyan
    Write-Host "    ✅ Ejecución automática de todos los notebooks" -ForegroundColor Green
    Write-Host "    ✅ Manejo robusto de errores" -ForegroundColor Green
    Write-Host "    ✅ Logging detallado" -ForegroundColor Green
    Write-Host "    ✅ Reportes de ejecución" -ForegroundColor Green
    Write-Host "    ✅ Verificación de dependencias" -ForegroundColor Green
    Write-Host "    ✅ Múltiples modos de ejecución" -ForegroundColor Green
}

# Función para imprimir mensajes con colores
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

# Función para verificar dependencias
function Test-Dependencies {
    Write-Info "Verificando dependencias del sistema..."
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python no está instalado o no está en el PATH"
            return $false
        }
        Write-Info "Python encontrado: $pythonVersion"
    }
    catch {
        Write-Error "Python no está instalado"
        return $false
    }
    
    # Verificar Jupyter
    try {
        $jupyterVersion = jupyter --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Jupyter Notebook no está instalado"
            Write-Info "Instalar con: pip install jupyter"
            return $false
        }
        Write-Info "Jupyter encontrado: $jupyterVersion"
    }
    catch {
        Write-Error "Jupyter Notebook no está instalado"
        Write-Info "Instalar con: pip install jupyter"
        return $false
    }
    
    # Verificar nbconvert
    try {
        python -c "import nbconvert" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "nbconvert no está instalado"
            Write-Info "Instalar con: pip install nbconvert"
            return $false
        }
        Write-Info "nbconvert encontrado"
    }
    catch {
        Write-Error "nbconvert no está instalado"
        Write-Info "Instalar con: pip install nbconvert"
        return $false
    }
    
    Write-Success "Todas las dependencias están disponibles"
    return $true
}

# Función para crear directorios necesarios
function New-RequiredDirectories {
    Write-Info "Creando directorios necesarios..."
    
    $directories = @("logs", "data", "reportes_revision", "test_results", "tests", "app", "static", "templates", "backups")
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "Directorio creado: $dir"
        }
        else {
            Write-Info "Directorio ya existe: $dir"
        }
    }
}

# Función para ejecutar notebook individual
function Invoke-Notebook {
    param(
        [string]$Notebook,
        [int]$Timeout = 300
    )
    
    Write-Info "Ejecutando notebook: $Notebook"
    
    if (!(Test-Path $Notebook)) {
        Write-Error "Notebook no encontrado: $Notebook"
        return $false
    }
    
    try {
        # Ejecutar notebook
        $process = Start-Process -FilePath "jupyter" -ArgumentList @(
            "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=$Timeout",
            $Notebook
        ) -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Success "Notebook ejecutado exitosamente: $Notebook"
            return $true
        }
        else {
            Write-Error "Error ejecutando notebook: $Notebook (Exit Code: $($process.ExitCode))"
            return $false
        }
    }
    catch {
        Write-Error "Excepción ejecutando notebook: $Notebook - $($_.Exception.Message)"
        return $false
    }
}

# Función para ejecutar sistema completo
function Start-SystemExecution {
    param([string]$Mode)
    
    Write-Host "🚀 EJECUTOR MAESTRO DEL SISTEMA METGO 3D" -ForegroundColor Blue
    Write-Host "Sistema Meteorológico Agrícola Quillota - Versión Operativa" -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Info "Iniciando ejecución del sistema METGO 3D"
    Write-Info "Modo: $Mode"
    Write-Info "Fecha: $(Get-Date)"
    
    # Verificar dependencias
    if (!(Test-Dependencies)) {
        Write-Error "No se pueden ejecutar los notebooks sin las dependencias necesarias"
        exit 1
    }
    
    # Crear directorios
    New-RequiredDirectories
    
    # Determinar notebooks a ejecutar según el modo
    $notebooks = @()
    
    switch ($Mode.ToLower()) {
        "completo" {
            $notebooks = @(
                "01_Configuracion_e_imports.ipynb",
                "02_Carga_y_Procesamiento_Datos.ipynb",
                "03_Analisis_Meteorologico.ipynb",
                "04_Visualizaciones.ipynb",
                "05_Modelos_ML.ipynb",
                "06_Dashboard_Interactivo.ipynb",
                "07_Reportes_Automaticos.ipynb",
                "08_APIs_Externas.ipynb",
                "09_Testing_Validacion.ipynb",
                "10_Deployment_Produccion.ipynb"
            )
        }
        "rapido" {
            $notebooks = @(
                "01_Configuracion_e_imports.ipynb",
                "02_Carga_y_Procesamiento_Datos.ipynb",
                "03_Analisis_Meteorologico.ipynb",
                "04_Visualizaciones.ipynb",
                "05_Modelos_ML.ipynb"
            )
        }
        "analisis" {
            $notebooks = @(
                "01_Configuracion_e_imports.ipynb",
                "02_Carga_y_Procesamiento_Datos.ipynb",
                "03_Analisis_Meteorologico.ipynb",
                "04_Visualizaciones.ipynb"
            )
        }
        "testing" {
            $notebooks = @("09_Testing_Validacion.ipynb")
        }
        "deployment" {
            $notebooks = @("10_Deployment_Produccion.ipynb")
        }
        default {
            Write-Error "Modo no válido: $Mode"
            Show-Help
            exit 1
        }
    }
    
    # Ejecutar notebooks
    $startTime = Get-Date
    $successful = 0
    $failed = 0
    
    for ($i = 0; $i -lt $notebooks.Count; $i++) {
        $notebook = $notebooks[$i]
        $notebookNum = $i + 1
        $totalNotebooks = $notebooks.Count
        
        Write-Host ""
        Write-Info "Ejecutando notebook $notebookNum/$totalNotebooks : $notebook"
        Write-Host "--------------------------------------------------"
        
        if (Invoke-Notebook -Notebook $notebook) {
            $successful++
        }
        else {
            $failed++
            if ($Mode -ne "completo") {
                Write-Error "Deteniendo ejecución por error"
                break
            }
            else {
                Write-Warning "Continuando con el siguiente notebook..."
            }
        }
    }
    
    $endTime = Get-Date
    $totalTime = ($endTime - $startTime).TotalSeconds
    
    # Reporte final
    Write-Host ""
    Write-Host "============================================================"
    Write-Info "REPORTE FINAL DE EJECUCIÓN"
    Write-Host "============================================================"
    Write-Info "Fecha de ejecución: $(Get-Date)"
    Write-Info "Tiempo total: $([math]::Round($totalTime, 2)) segundos"
    Write-Info "Notebooks ejecutados: $($successful + $failed)"
    Write-Success "Exitosos: $successful"
    
    if ($failed -gt 0) {
        Write-Error "Con errores: $failed"
    }
    
    $successRate = [math]::Round(($successful * 100) / ($successful + $failed), 1)
    Write-Info "Tasa de éxito: $successRate%"
    
    if ($failed -eq 0) {
        Write-Host ""
        Write-Success "🎉 ¡SISTEMA METGO 3D EJECUTADO EXITOSAMENTE!"
        Write-Success "🌾 El sistema está listo para uso agrícola en Quillota"
        exit 0
    }
    else {
        Write-Host ""
        Write-Warning "⚠️ Sistema ejecutado con $failed errores"
        Write-Info "🔧 Revisar logs para detalles de errores"
        exit 1
    }
}

# Función principal
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Start-SystemExecution -Mode $Modo
}

# Ejecutar función principal
Main
