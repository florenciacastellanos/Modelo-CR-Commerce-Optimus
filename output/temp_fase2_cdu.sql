-- FASE 2.2: DRILL-DOWN por CDU - Generales Compra MLA
-- Dic 2025 vs Ene 2026

WITH CLASIFICACION AS (
    SELECT 
        DATE_TRUNC(CAST(C.CONTACT_DATE_ID AS DATE), MONTH) AS PERIODO,
        C.CAS_CASE_ID,
        C.CDU,
        CASE
            -- POST-COMPRA
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Others%') THEN 'PDD'
            
            -- SHIPPING
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
            
            -- MARKETPLACE
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PreVenta%') THEN 'Pre Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PostVenta%') THEN 'Post Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Redes%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Prustomer%') THEN 'Moderaciones'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Compra%') THEN 'Generales Compra'
            
            -- PAGOS
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Pagos%') THEN 'Pagos'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP Payer%') THEN 'MP On'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP On%') THEN 'MP On'
            
            -- CUENTA
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
),
POR_CDU AS (
    SELECT 
        COALESCE(CDU, '(sin CDU)') AS CDU,
        SUM(CASE WHEN FORMAT_DATE('%Y-%m', PERIODO) = '2025-12' THEN 1 ELSE 0 END) AS INC_DIC,
        SUM(CASE WHEN FORMAT_DATE('%Y-%m', PERIODO) = '2026-01' THEN 1 ELSE 0 END) AS INC_ENE
    FROM CLASIFICACION
    WHERE AGRUP_COMMERCE = 'Generales Compra'
    GROUP BY CDU
)
SELECT 
    CDU,
    INC_DIC,
    INC_ENE,
    (INC_ENE - INC_DIC) AS VAR_CASOS,
    ROUND(SAFE_DIVIDE((INC_ENE - INC_DIC), INC_DIC) * 100, 2) AS VAR_PCT
FROM POR_CDU
ORDER BY ABS(INC_ENE - INC_DIC) DESC
LIMIT 20
