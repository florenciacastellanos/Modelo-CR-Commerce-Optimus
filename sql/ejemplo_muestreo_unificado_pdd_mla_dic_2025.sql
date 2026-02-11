-- ══════════════════════════════════════════════════════════════════════════════
-- EJEMPLO CONCRETO: MUESTREO UNIFICADO PDD MLA DICIEMBRE 2025
-- ══════════════════════════════════════════════════════════════════════════════
--
-- Basado en: sql/templates/muestreo_unificado_template.sql
-- Caso: 6 procesos priorizados de PDD (regla 80%)
-- Peak detectado: Defectuoso - Flex en 29-30 dic
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
    WHERE ARRIVAL_DATE BETWEEN DATE_SUB('2025-12-01', INTERVAL 30 DAY) 
        AND DATE_ADD('2025-12-31', INTERVAL 30 DAY)
),

INCOMING_BASE AS (
    -- Paso 2: Filtrar incoming por los 6 procesos priorizados
    SELECT
        INC.CAS_CASE_ID,
        INC.PROCESS_NAME,
        DATE(INC.CONTACT_DATE_ID) as FECHA_CONTACTO,
        CASE 
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'  
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            ELSE 'OTRO' 
        END AS AGRUP_COMMERCE
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` INC
    WHERE INC.SIT_SITE_ID = 'MLA'
        AND DATE_TRUNC(INC.CONTACT_DATE_ID, MONTH) = '2025-12-01'
        AND INC.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(INC.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND INC.PROCESS_NAME IN (
            'Arrepentimiento - XD',
            'Defectuoso - XD',
            'Defectuoso - Flex',
            'Arrepentimiento - Flex',
            'Incompleto - Flex',
            'Diferente - Flex'
        )
),

JOINED AS (
    -- Paso 3: Join con conversaciones válidas
    SELECT 
        INC.CAS_CASE_ID,
        INC.PROCESS_NAME,
        INC.FECHA_CONTACTO,
        ST.CONVERSATION_SUMMARY
    FROM INCOMING_BASE INC
    INNER JOIN STUDIO_SUMMARIES ST ON INC.CAS_CASE_ID = ST.CAS_CASE_ID
    WHERE INC.AGRUP_COMMERCE = 'PDD'
        AND ST.CONVERSATION_SUMMARY IS NOT NULL
        AND LENGTH(ST.CONVERSATION_SUMMARY) > 20
),

PEAK_INFO AS (
    -- Paso 4: Clasificar días (PICO vs NORMAL) por proceso
    -- Peak detectado: Defectuoso - Flex en 29-30 dic
    SELECT 
        PROCESS_NAME,
        FECHA_CONTACTO,
        CASE 
            WHEN PROCESS_NAME = 'Defectuoso - Flex' AND FECHA_CONTACTO IN ('2025-12-29', '2025-12-30') 
                THEN 'PICO'
            ELSE 'NORMAL' 
        END as TIPO_DIA
    FROM (SELECT DISTINCT PROCESS_NAME, FECHA_CONTACTO FROM JOINED)
),

MUESTRAS_PONDERADAS AS (
    -- Paso 5: Asignar ranking ponderado por tipo de día
    SELECT 
        J.CAS_CASE_ID,
        J.PROCESS_NAME,
        J.FECHA_CONTACTO,
        J.CONVERSATION_SUMMARY,
        P.TIPO_DIA,
        ROW_NUMBER() OVER (
            PARTITION BY J.PROCESS_NAME, P.TIPO_DIA
            ORDER BY RAND()
        ) as rn_by_tipo
    FROM JOINED J
    INNER JOIN PEAK_INFO P ON J.PROCESS_NAME = P.PROCESS_NAME AND J.FECHA_CONTACTO = P.FECHA_CONTACTO
)

-- Paso 6: Seleccionar muestra ponderada por proceso
-- Defectuoso - Flex: 70 casos pico (29-30 dic) + 30 resto
-- Otros 5 procesos: 100 casos uniformes (sin pico)
SELECT 
    CAS_CASE_ID,
    PROCESS_NAME,
    FECHA_CONTACTO,
    CONVERSATION_SUMMARY,
    TIPO_DIA
FROM MUESTRAS_PONDERADAS 
WHERE 
    -- Para Defectuoso - Flex: 70 pico + 30 normal
    (PROCESS_NAME = 'Defectuoso - Flex' AND TIPO_DIA = 'PICO' AND rn_by_tipo <= 70)
    OR (PROCESS_NAME = 'Defectuoso - Flex' AND TIPO_DIA = 'NORMAL' AND rn_by_tipo <= 30)
    -- Para otros procesos: 100 casos normales
    OR (PROCESS_NAME != 'Defectuoso - Flex' AND TIPO_DIA = 'NORMAL' AND rn_by_tipo <= 100)
ORDER BY PROCESS_NAME, TIPO_DIA DESC, rn_by_tipo;

-- ══════════════════════════════════════════════════════════════════════════════
-- RESULTADO ESPERADO:
-- ~600 filas (100 por cada uno de los 6 procesos)
-- Tiempo: ~2 minutos
--
-- SIGUIENTE PASO:
-- Ejecutar: Get-Content sql/ejemplo_muestreo_unificado_pdd_mla_dic_2025.sql -Raw | 
--           bq query --use_legacy_sql=false --format=csv > output/muestreo_unificado_ejemplo.csv
-- ══════════════════════════════════════════════════════════════════════════════
