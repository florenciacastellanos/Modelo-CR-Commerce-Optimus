-- ══════════════════════════════════════════════════════════════════════════════
-- 📊 PEAK DETECTION - Detección de Picos por Elemento Priorizado
-- ══════════════════════════════════════════════════════════════════════════════
--
-- PROPÓSITO:
-- Identificar días anómalos (picos) por elemento específico (CDU, Proceso, Tipificación)
-- para priorizar muestreo cualitativo en esos días.
--
-- ⚠️ REGLA CRÍTICA:
-- Peak detection se ejecuta **por cada elemento priorizado** (regla 80%), NO a nivel general.
--
-- ¿POR QUÉ POR ELEMENTO?
-- - Cada elemento puede tener patrones temporales distintos
-- - Un pico general puede ser causado por un solo elemento → el resto no tuvo anomalía
-- - Permite priorizar el muestreo en los días pico de ese elemento específico
--
-- REGLA DIRECCIONAL:
-- - CR subió → buscar peaks en período **actual** (identificar qué días causaron incremento)
-- - CR bajó → buscar peaks en período **anterior** (identificar qué días explicaban CR alto previo)
--
-- PARÁMETROS A REEMPLAZAR:
-- {site}                           → Ej: 'MLA', 'MLB'
-- {period_start}                   → Ej: '2025-12-01'
-- {period_end}                     → Ej: '2025-12-31'
-- {dimension}                      → Ej: 'CDU', 'PROCESS_NAME', 'TIPIFICACION'
-- {dimension_value}                → Ej: 'Arrepentimiento', 'Defectuoso - Flex'
-- {commerce_group}                 → Ej: 'PDD', 'PNR', 'ME PreDespacho'
-- {commerce_group_case_statement}  → CASE completo de commerce group (ver base-query.sql)
-- {filtros_adicionales}            → Filtros específicos del análisis (opcional)
--
-- TIEMPO ESPERADO: 30-60 segundos
--
-- ══════════════════════════════════════════════════════════════════════════════

WITH daily_incoming AS (
    -- Paso 1: Calcular incoming diario para el elemento específico
    SELECT 
        DATE(CONTACT_DATE_ID) as fecha,
        COUNT(*) as casos_dia
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE C.SIT_SITE_ID = '{site}'
        AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) BETWEEN '{period_start}' AND '{period_end}'
        AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.{dimension} = '{dimension_value}'
        AND (
            {commerce_group_case_statement}
        ) = '{commerce_group}'
        {filtros_adicionales}
    GROUP BY fecha
),

stats AS (
    -- Paso 2: Calcular estadísticas descriptivas (promedio y desviación estándar)
    SELECT 
        AVG(casos_dia) as promedio,
        STDDEV(casos_dia) as std_dev,
        MIN(casos_dia) as minimo,
        MAX(casos_dia) as maximo
    FROM daily_incoming
)

-- Paso 3: Identificar picos usando desviación estándar
-- Criterio: Pico si casos > promedio + 1.5 × desviación estándar
SELECT 
    d.fecha,
    d.casos_dia,
    ROUND(s.promedio, 2) as promedio_periodo,
    ROUND(s.std_dev, 2) as desviacion_std,
    ROUND((d.casos_dia - s.promedio) / s.std_dev, 2) as z_score,
    ROUND((d.casos_dia / s.promedio) * 100, 1) as pct_vs_promedio,
    CASE 
        WHEN d.casos_dia > (s.promedio + 1.5 * s.std_dev) THEN 'PICO' 
        WHEN d.casos_dia < (s.promedio - 1.5 * s.std_dev) THEN 'VALLE'
        ELSE 'NORMAL' 
    END as tipo_dia,
    -- Metadata adicional
    s.minimo as min_periodo,
    s.maximo as max_periodo
FROM daily_incoming d
CROSS JOIN stats s
ORDER BY d.casos_dia DESC;

-- ══════════════════════════════════════════════════════════════════════════════
-- INTERPRETACIÓN DEL OUTPUT:
--
-- | fecha      | casos_dia | promedio | std_dev | z_score | pct_vs_promedio | tipo_dia |
-- |------------|-----------|----------|---------|---------|-----------------|----------|
-- | 2025-12-29 | 250       | 140      | 45      | 2.44    | 178.6%          | PICO     |
-- | 2025-12-15 | 200       | 140      | 45      | 1.33    | 142.9%          | NORMAL   |
-- | 2025-12-01 | 50        | 140      | 45      | -2.00   | 35.7%           | VALLE    |
--
-- - **PICO:** Día anómalo alto (≥ 1.5 desviaciones estándar por encima del promedio)
-- - **NORMAL:** Día dentro del rango esperado
-- - **VALLE:** Día anómalo bajo (≥ 1.5 desviaciones estándar por debajo del promedio)
--
-- ══════════════════════════════════════════════════════════════════════════════
-- USO EN MUESTREO PONDERADO:
--
-- 1. Ejecutar esta query para identificar fechas con tipo_dia = 'PICO'
-- 2. Extraer las fechas de picos: ['2025-12-29', '2025-12-30', ...]
-- 3. Usar esas fechas en {fechas_pico} del template muestreo_unificado_template.sql
-- 4. Resultado: 70% de muestras de días pico, 30% del resto
--
-- ══════════════════════════════════════════════════════════════════════════════
-- CASOS ESPECIALES:
--
-- **SI NO HAY PICOS DETECTADOS:**
-- - Usar muestreo uniforme/aleatorio distribuido en el período
-- - No forzar picos donde no existen
-- - En muestreo_unificado_template.sql: ajustar límites a 100 casos NORMAL
--
-- **SI HAY MÚLTIPLES PICOS:**
-- - Priorizar los 2-3 días con mayor z_score
-- - Distribuir muestreo ponderado entre esos días
--
-- **SI EL PERÍODO ES MUY CORTO (<10 días):**
-- - La desviación estándar puede no ser representativa
-- - Considerar usar percentiles en vez de desviación estándar
--
-- ══════════════════════════════════════════════════════════════════════════════
-- EJEMPLO DE EJECUCIÓN:
--
-- PowerShell:
-- Get-Content sql/peak_detection_cdu_arrepentimiento_mla_dic.sql -Raw | 
-- bq query --use_legacy_sql=false --format=csv > output/peaks_arrepentimiento.csv
--
-- Python:
-- df_peaks = pd.read_csv('output/peaks_arrepentimiento.csv')
-- picos = df_peaks[df_peaks['tipo_dia'] == 'PICO']['fecha'].tolist()
-- print(f"Fechas con picos: {picos}")
--
-- ══════════════════════════════════════════════════════════════════════════════
-- REFERENCIAS:
--
-- - Regla CRÍTICA de peak detection por elemento: `.cursorrules` FASE 3
-- - Muestreo unificado: `sql/templates/muestreo_unificado_template.sql`
-- - Análisis de conversaciones: `templates/prompt_analisis_conversaciones.md`
--
-- ══════════════════════════════════════════════════════════════════════════════
