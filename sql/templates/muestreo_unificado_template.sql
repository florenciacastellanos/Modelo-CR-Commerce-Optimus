-- ══════════════════════════════════════════════════════════════════════════════
-- 🚀 MUESTREO UNIFICADO - TODOS LOS PROCESOS PRIORIZADOS
-- ══════════════════════════════════════════════════════════════════════════════
--
-- PROPÓSITO:
-- Obtener 100 conversaciones por cada proceso priorizado (regla 80%) en 1 sola query
--
-- BENEFICIO:
-- 7 minutos (6 queries × 1.2 min) → 2 minutos (1 query)
-- Reducción: 71% menos tiempo
--
-- MUESTREO PONDERADO:
-- - 70 casos de días con picos detectados (si existen)
-- - 30 casos del resto del período
--
-- PARÁMETROS A REEMPLAZAR:
-- {site}                           → Ej: 'MLA', 'MLB'
-- {period_start}                   → Ej: '2025-12-01'
-- {period_end}                     → Ej: '2025-12-31'
-- {dimension}                      → Ej: 'PROCESS_NAME', 'CDU', 'TIPIFICACION'
-- {commerce_group_case_statement}  → CASE completo de commerce group (ver base-query.sql)
-- {commerce_group}                 → Ej: 'PDD', 'PNR', 'ME Distribución'
-- {lista_procesos_priorizados}     → Ej: 'Arrepentimiento - XD', 'Defectuoso - Flex', ...
-- {fechas_pico}                    → Ej: '2025-12-29', '2025-12-30' (resultado de peak detection)
--
-- ══════════════════════════════════════════════════════════════════════════════

WITH STUDIO_SUMMARIES AS (
    -- Paso 1: Extraer conversaciones de Studio Sample
    SELECT
        CAS_CASE_ID,
        TRIM(REGEXP_REPLACE(
            CONCAT(
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.problem'), ''),
                ' ',
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.solution'), '')
            ),
            r'\\s+', ' '
        )) AS CONVERSATION_SUMMARY
    FROM `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE`
    WHERE ARRIVAL_DATE BETWEEN DATE_SUB('{period_start}', INTERVAL 30 DAY) 
        AND DATE_ADD('{period_end}', INTERVAL 30 DAY)
),

INCOMING_BASE AS (
    -- Paso 2: Filtrar incoming por procesos priorizados
    SELECT
        INC.CAS_CASE_ID,
        INC.{dimension},
        DATE(INC.CONTACT_DATE_ID) as FECHA_CONTACTO,
        {commerce_group_case_statement} AS AGRUP_COMMERCE
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` INC
    WHERE INC.SIT_SITE_ID = '{site}'
        AND DATE_TRUNC(INC.CONTACT_DATE_ID, MONTH) BETWEEN '{period_start}' AND '{period_end}'
        AND INC.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(INC.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND INC.{dimension} IN ({lista_procesos_priorizados})
),

JOINED AS (
    -- Paso 3: Join con conversaciones válidas
    SELECT 
        INC.CAS_CASE_ID,
        INC.{dimension},
        INC.FECHA_CONTACTO,
        ST.CONVERSATION_SUMMARY
    FROM INCOMING_BASE INC
    INNER JOIN STUDIO_SUMMARIES ST ON INC.CAS_CASE_ID = ST.CAS_CASE_ID
    WHERE INC.AGRUP_COMMERCE = '{commerce_group}'
        AND ST.CONVERSATION_SUMMARY IS NOT NULL
        AND LENGTH(ST.CONVERSATION_SUMMARY) > 20
),

PEAK_INFO AS (
    -- Paso 4: Clasificar días (PICO vs NORMAL) por proceso
    -- Usar fechas de picos detectados en peak detection previo
    SELECT 
        {dimension},
        FECHA_CONTACTO,
        CASE 
            WHEN FECHA_CONTACTO IN ({fechas_pico}) THEN 'PICO' 
            ELSE 'NORMAL' 
        END as TIPO_DIA
    FROM (SELECT DISTINCT {dimension}, FECHA_CONTACTO FROM JOINED)
),

MUESTRAS_PONDERADAS AS (
    -- Paso 5: Asignar ranking ponderado por tipo de día
    SELECT 
        J.CAS_CASE_ID,
        J.{dimension},
        J.FECHA_CONTACTO,
        J.CONVERSATION_SUMMARY,
        P.TIPO_DIA,
        ROW_NUMBER() OVER (
            PARTITION BY J.{dimension}, P.TIPO_DIA
            ORDER BY RAND()
        ) as rn_by_tipo
    FROM JOINED J
    INNER JOIN PEAK_INFO P ON J.{dimension} = P.{dimension} AND J.FECHA_CONTACTO = P.FECHA_CONTACTO
)

-- Paso 6: Seleccionar 70 casos de picos + 30 del resto por cada proceso
SELECT 
    CAS_CASE_ID,
    {dimension},
    FECHA_CONTACTO,
    CONVERSATION_SUMMARY,
    TIPO_DIA
FROM MUESTRAS_PONDERADAS 
WHERE (TIPO_DIA = 'PICO' AND rn_by_tipo <= 70)
   OR (TIPO_DIA = 'NORMAL' AND rn_by_tipo <= 30)
ORDER BY {dimension}, TIPO_DIA DESC, rn_by_tipo;

-- ══════════════════════════════════════════════════════════════════════════════
-- NOTAS:
--
-- 1. Si NO hay picos detectados, usar {fechas_pico} = '' para que todos sean NORMAL
--    y ajustar límites a: TIPO_DIA = 'NORMAL' AND rn_by_tipo <= 100
--
-- 2. El output tendrá máximo 100 filas por proceso (600 filas para 6 procesos)
--
-- 3. Tiempo esperado de ejecución: 1.5 - 2.5 minutos (depende del volumen)
--
-- 4. Este template debe guardarse como archivo concreto reemplazando los placeholders
--    antes de ejecutar: Get-Content archivo.sql -Raw | bq query ...
--
-- ══════════════════════════════════════════════════════════════════════════════
