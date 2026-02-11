# Script de Verificación - OpenAI API Key
# ========================================
# Verifica que OpenAI esté configurado correctamente

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "VERIFICACIÓN DE OPENAI API KEY" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Test 1: Variable de entorno
Write-Host "[TEST 1] Verificando variable de entorno..." -ForegroundColor Yellow
if ($env:OPENAI_API_KEY) {
    $key_preview = $env:OPENAI_API_KEY.Substring(0, [Math]::Min(10, $env:OPENAI_API_KEY.Length)) + "..."
    Write-Host "[OK] API Key configurada: $key_preview" -ForegroundColor Green
    $test1_pass = $true
} else {
    Write-Host "[FAIL] API Key NO configurada" -ForegroundColor Red
    Write-Host "       Ejecutar: `$env:OPENAI_API_KEY = 'sk-proj-...'" -ForegroundColor Yellow
    $test1_pass = $false
}

Write-Host ""

# Test 2: Módulo openai instalado
Write-Host "[TEST 2] Verificando módulo openai..." -ForegroundColor Yellow
$openai_check = py -c "import openai; print('OK')" 2>&1
if ($openai_check -eq "OK") {
    Write-Host "[OK] Módulo openai instalado" -ForegroundColor Green
    $test2_pass = $true
} else {
    Write-Host "[FAIL] Módulo openai NO instalado" -ForegroundColor Red
    Write-Host "       Ejecutar: py -m pip install openai" -ForegroundColor Yellow
    $test2_pass = $false
}

Write-Host ""

# Test 3: OpenAI Client funciona
if ($test1_pass -and $test2_pass) {
    Write-Host "[TEST 3] Verificando conexión con OpenAI..." -ForegroundColor Yellow
    $connection_check = py -c "from openai import OpenAI; client = OpenAI(); print('OK')" 2>&1
    if ($connection_check -eq "OK") {
        Write-Host "[OK] Conexión con OpenAI exitosa" -ForegroundColor Green
        $test3_pass = $true
    } else {
        Write-Host "[FAIL] Error de conexión:" -ForegroundColor Red
        Write-Host "       $connection_check" -ForegroundColor Yellow
        $test3_pass = $false
    }
} else {
    Write-Host "[TEST 3] Saltado (tests previos fallaron)" -ForegroundColor Yellow
    $test3_pass = $false
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

# Resumen
if ($test1_pass -and $test2_pass -and $test3_pass) {
    Write-Host "[OK] OPENAI CONFIGURADO CORRECTAMENTE" -ForegroundColor Green
    Write-Host "`nPuedes ejecutar el Masterfile v6.1 con análisis LLM:" -ForegroundColor Green
    Write-Host "  .\ejemplos\ejecutar_reporte_pdd_mla.ps1" -ForegroundColor White
} else {
    Write-Host "[ATENCION] OPENAI NO CONFIGURADO" -ForegroundColor Red
    Write-Host "`nEl Masterfile funcionará sin análisis LLM (exportará CSVs)." -ForegroundColor Yellow
    Write-Host "`nPara habilitar análisis LLM:" -ForegroundColor Yellow
    if (-not $test2_pass) {
        Write-Host "  1. Instalar openai: py -m pip install openai" -ForegroundColor White
    }
    if (-not $test1_pass) {
        Write-Host "  2. Configurar API Key: `$env:OPENAI_API_KEY = 'sk-proj-...'" -ForegroundColor White
        Write-Host "     (Obtener key en: https://platform.openai.com/api-keys)" -ForegroundColor White
    }
    Write-Host "  3. Re-ejecutar este script para verificar" -ForegroundColor White
}

Write-Host "`n============================================`n" -ForegroundColor Cyan

# Pausar
Write-Host "Presiona Enter para salir..."
Read-Host
