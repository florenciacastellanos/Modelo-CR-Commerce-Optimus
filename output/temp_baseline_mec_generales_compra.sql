-- ══════════════════════════════════════════════════════════════════════════════
-- FASE 1: BASELINE - MEC GENERALES_COMPRA - Dic 2025 vs Ene 2026
-- ══════════════════════════════════════════════════════════════════════════════

-- QUERY 1: INCOMING POR PERÍODO
WITH BASE_CONTACTS AS (
    SELECT    
        C.CAS_CASE_ID,
        C.SIT_SITE_ID,
        CAST(C.CONTACT_DATE_ID AS DATE) AS CONTACT_DATE_ID,
        C.PROCESS_NAME,
        C.CDU,
        
        -- AGRUP_COMMERCE LOGIC
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
        AND C.SIT_SITE_ID = 'MEC'
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND C.PROCESS_ID NOT IN (1312)
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND (C.PROCESS_GROUP_ECOMMERCE IN ('Comprador', 'Vendedor', 'Cuenta') 
             OR C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers'))
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
)

SELECT 
    CASE 
        WHEN CONTACT_DATE_ID BETWEEN '2025-12-01' AND '2025-12-31' THEN 'P1_DIC2025'
        WHEN CONTACT_DATE_ID BETWEEN '2026-01-01' AND '2026-01-31' THEN 'P2_ENE2026'
    END AS PERIODO,
    COUNT(DISTINCT CAS_CASE_ID) AS INCOMING
FROM BASE_CONTACTS
WHERE AGRUP_COMMERCE = 'Generales Compra'
GROUP BY 1
ORDER BY 1
