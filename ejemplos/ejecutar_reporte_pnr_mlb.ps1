# Ejemplo de Ejecución - Reporte PNR MLB Nov-Dic 2025
# ======================================================
# Este script ejecuta el Template Universal v6.3.4 para PNR MLB (Brasil)
# Versión Oficial: v6.3.4 (Sistema Verdaderamente Universal)

Write-Host "============================================" -ForegroundColor Green
Write-Host "EJECUTANDO TEMPLATE UNIVERSAL v6.3.4" -ForegroundColor Green
Write-Host "Caso: PNR MLB (Brasil) Nov-Dic 2025" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green

# Navegar al directorio del repositorio (ajustar si es necesario)
# Set-Location "c:\Users\flocastellanos\OneDrive - Mercado Libre S.R.L\Escritorio\Repositorios\CR COMMERCE - Repo 30-1 version para limpiar el output"

py generar_reporte_cr_universal_v6.3.6.py `
    --site MLB `
    --p1-start 2025-11-01 `
    --p1-end 2025-11-30 `
    --p2-start 2025-12-01 `
    --p2-end 2025-12-31 `
    --commerce-group PNR `
    --aperturas "PROCESO,TIPIFICACION,ENVIRONMENT" `
    --muestreo-dimension PROCESO `
    --output-dir output `
    --open-report

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Reporte generado exitosamente" -ForegroundColor Green
} else {
    Write-Host "`n❌ Error al generar reporte (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host "`nPresiona Enter para salir..."
Read-Host
