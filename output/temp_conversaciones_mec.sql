-- ══════════════════════════════════════════════════════════════════════════════
-- FASE 3: MUESTREO CONVERSACIONES - MEC GENERALES_COMPRA - Dic 2025 vs Ene 2026
-- Procesos priorizados (>80% contribución):
-- 1. Viaje del paquete - Comprador (32.63%)
-- 2. Pre Compra (18.83%)
-- 3. Viaje del paquete - Vendedor (11.85%)
-- 4. Durante la Entrega (8.28%)
-- 5. Reputación ME (7.95%)
-- 6. Posterior a la Entrega (7.63%)
-- ══════════════════════════════════════════════════════════════════════════════

WITH BASE_CONTACTS AS (
    SELECT    
        C.CAS_CASE_ID,
        C.SIT_SITE_ID,
        CAST(C.CONTACT_DATE_ID AS DATE) AS CONTACT_DATE_ID,
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
        AND C.SIT_SITE_ID = 'MEC'
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND C.PROCESS_ID NOT IN (1312)
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND (C.PROCESS_GROUP_ECOMMERCE IN ('Comprador', 'Vendedor', 'Cuenta') 
             OR C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers'))
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
),

CASOS_PRIORIZADOS AS (
    SELECT 
        B.CAS_CASE_ID,
        B.CONTACT_DATE_ID,
        B.PROCESS_NAME,
        B.CDU,
        CASE 
            WHEN B.CONTACT_DATE_ID BETWEEN '2025-12-01' AND '2025-12-31' THEN 'P1_DIC2025'
            WHEN B.CONTACT_DATE_ID BETWEEN '2026-01-01' AND '2026-01-31' THEN 'P2_ENE2026'
        END AS PERIODO
    FROM BASE_CONTACTS B
    WHERE B.AGRUP_COMMERCE = 'Generales Compra'
      AND B.PROCESS_NAME IN (
          'Viaje del paquete - Comprador',
          'Pre Compra',
          'Viaje del paquete - Vendedor',
          'Durante la Entrega',
          'Reputación ME',
          'Posterior a la Entrega'
      )
),

-- JOIN con tabla de resúmenes de conversaciones
CON_RESUMEN AS (
    SELECT 
        CP.CAS_CASE_ID,
        CP.CONTACT_DATE_ID,
        CP.PROCESS_NAME,
        CP.CDU,
        CP.PERIODO,
        CONV.CONVERSATION_SUMMARY
    FROM CASOS_PRIORIZADOS CP
    INNER JOIN `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE` CONV
        ON CP.CAS_CASE_ID = CONV.CAS_CASE_ID
    WHERE CONV.CONVERSATION_SUMMARY IS NOT NULL
      AND LENGTH(CONV.CONVERSATION_SUMMARY) > 50
),

-- Muestreo: 15 por proceso-período
MUESTREADO AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY PROCESS_NAME, PERIODO ORDER BY RAND()) AS RN
    FROM CON_RESUMEN
)

SELECT 
    PERIODO,
    PROCESS_NAME,
    CDU,
    CAS_CASE_ID,
    CONTACT_DATE_ID,
    SUBSTR(CONVERSATION_SUMMARY, 1, 500) AS RESUMEN_CONV
FROM MUESTREADO
WHERE RN <= 15
ORDER BY PROCESS_NAME, PERIODO, RN
