-- FASE 3.2: MUESTREO CONVERSACIONES - Top Procesos Generales Compra MLA
-- 15 casos por proceso-período (total ~150 conversaciones)

WITH STUDIO_SUMMARIES AS (
    SELECT
        CAS_CASE_ID,
        TRIM(REGEXP_REPLACE(
            CONCAT(
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.problem'), ''),
                ' ',
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.solution'), '')
            ),
            r'\s+', ' '
        )) AS CONVERSATION_SUMMARY
    FROM `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE`
    WHERE ARRIVAL_DATE BETWEEN '2025-11-01' AND '2026-02-28'
),

CLASIFICACION AS (
    SELECT 
        CAST(C.CONTACT_DATE_ID AS DATE) AS FECHA,
        FORMAT_DATE('%Y-%m', C.CONTACT_DATE_ID) AS PERIODO,
        C.CAS_CASE_ID,
        C.PROCESS_NAME,
        C.CDU,
        CASE
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Others%') THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'ME Distribución'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra Comprador%') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME Distribución'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('Post Compra Funcionalidades Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME PreDespacho'
            WHEN C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%FBM Sellers%') THEN 'FBM Sellers'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PreVenta%') THEN 'Pre Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PostVenta%') THEN 'Post Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Redes%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Prustomer%') THEN 'Moderaciones'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Compra%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Pagos%') THEN 'Pagos'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP Payer%') THEN 'MP On'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP On%') THEN 'MP On'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Seguridad 360%') THEN 'Cuenta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Experiencia Impositiva%') THEN 'Experiencia Impositiva'
            ELSE 'Generales Compra'
        END AS AGRUP_COMMERCE
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE 
        CAST(C.CONTACT_DATE_ID AS DATE) BETWEEN '2025-12-01' AND '2026-01-31'
        AND C.SIT_SITE_ID = 'MLA'
        AND C.PROCESS_ID NOT IN (1312)
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
        AND C.PROCESS_NAME IN (
            'Post Compra funcionalidades Comprador - Proximity',
            'Reputación ME',
            'CBT - ME Reputation',
            'Post Compra Funcionalidades Vendedor',
            'Viaje del paquete - Comprador'
        )
),

CON_RESUMEN AS (
    SELECT 
        c.FECHA,
        c.PERIODO,
        c.CAS_CASE_ID,
        c.PROCESS_NAME,
        c.CDU,
        c.AGRUP_COMMERCE,
        s.CONVERSATION_SUMMARY
    FROM CLASIFICACION c
    INNER JOIN STUDIO_SUMMARIES s ON c.CAS_CASE_ID = s.CAS_CASE_ID
    WHERE c.AGRUP_COMMERCE = 'Generales Compra'
        AND s.CONVERSATION_SUMMARY IS NOT NULL
        AND LENGTH(s.CONVERSATION_SUMMARY) > 50
),

RANKED AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY PROCESS_NAME, PERIODO ORDER BY RAND()) AS RN
    FROM CON_RESUMEN
)

SELECT 
    PROCESS_NAME AS PROCESO,
    PERIODO,
    CAS_CASE_ID,
    FECHA,
    CDU,
    CONVERSATION_SUMMARY
FROM RANKED
WHERE RN <= 15
ORDER BY PROCESS_NAME, PERIODO, FECHA
