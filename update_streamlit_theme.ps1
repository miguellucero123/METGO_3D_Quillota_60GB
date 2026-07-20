$files = @(
    "d:\METGO_3D_Quillota_60GB\streamlit_app.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_meteorologico_profesional.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_agricola_inteligente.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_monitoreo_tiempo_real.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_ia_ml_avanzado.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_visualizaciones_avanzadas.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_global_metricas.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_agricultura_precision.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_analisis_comparativo.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_alertas_automaticas.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_simple_optimizado.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_unificado_diferenciado.py",
    "d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_mobile_optimizado.py"
)

$importStmt = "from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout`n"

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        
        $original = $content
        
        # Add imports if missing
        if ($content -notmatch "from metgo.streamlit_theme import") {
            $content = $content -replace "(?m)^import streamlit as st", ("import streamlit as st`n" + $importStmt)
        }
        
        # Inject plotly_layout() into fig.update_layout calls.
        if ($content -notmatch "plotly_layout\(") {
            $content = $content -replace "fig\.update_layout\(\s*", "fig.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_temp\.update_layout\(\s*", "fig_temp.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_precip\.update_layout\(\s*", "fig_precip.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_viento\.update_layout\(\s*", "fig_viento.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_presion\.update_layout\(\s*", "fig_presion.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_condiciones\.update_layout\(\s*", "fig_condiciones.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_evolucion\.update_layout\(\s*", "fig_evolucion.update_layout(**plotly_layout(height=400), "
            $content = $content -replace "fig_barras\.update_layout\(\s*", "fig_barras.update_layout(**plotly_layout(height=400), "
        }
        
        if ($content -ne $original) {
            Set-Content $file $content -Encoding UTF8
            Write-Host "UPDATED: $file"
        } else {
            Write-Host "NO CHANGES: $file"
        }
    } else {
        Write-Host "NOT FOUND: $file"
    }
}
Write-Host "Done."
