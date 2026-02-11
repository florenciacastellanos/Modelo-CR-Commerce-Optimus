-- ══════════════════════════════════════════════════════════════════════════════
-- BASE QUERY - CONTACT RATE COMMERCE v2.6
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Main query to extract contact data for CR calculation
-- Source: BT_CX_CONTACTS (meli-bi-data.WHOWNER)
-- Version: 2.6 (without BT_CX_POST_PURCHASE)
-- Last Update: Enero 2026
-- ══════════════════════════════════════════════════════════════════════════════

-- PLACEHOLDERS TO REPLACE:
-- {fecha_inicio}         → Start date (YYYY-MM-DD)
-- {fecha_fin}            → End date (YYYY-MM-DD)
-- {sites}                → Sites list ('MLA', 'MLB', etc.)
-- {agrup_commerce}       → Commerce Groups list ('PDD', 'PNR', etc.)
-- {user_types}           → User Types list ('Comprador', 'Vendedor', 'Cuenta')
-- {environment_filter}   → Environment filter (optional SQL WHERE clause)

WITH BASE_CONTACTS AS (
    SELECT    
        -- ─────────────────────────────────────────────────────────────────────
        -- CORE IDENTIFIERS
        -- ─────────────────────────────────────────────────────────────────────
        C.CAS_CASE_ID,
        C.CUS_CUST_ID,
        C.SIT_SITE_ID,
        CAST(C.CONTACT_DATE_ID AS DATE) AS CONTACT_DATE_ID,
        FORMAT_DATETIME('%Y-%m', C.CONTACT_DATE_ID) AS MES,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- ORDER INFORMATION (for temporal correlation)
        -- ─────────────────────────────────────────────────────────────────────
        O.ORD_CLOSED_DT,  -- Order close date (to correlate with commercial events)
        
        -- ─────────────────────────────────────────────────────────────────────
        -- PROCESS CLASSIFICATION
        -- ─────────────────────────────────────────────────────────────────────
        C.PROCESS_ID,
        C.PROCESS_NAME,
        C.ENVIRONMENT,
        C.REASON_DETAIL_GROUP_REPORTING,
        C.CLA_REASON_DETAIL,
        C.CDU,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- VERTICAL AND DOMAIN (⚠️ Currently NULL - table not available)
        -- ─────────────────────────────────────────────────────────────────────
        CAST(NULL AS STRING) AS VERTICAL,
        CAST(NULL AS STRING) AS DOM_DOMAIN_AGG1,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- USER TYPE CLASSIFICATION
        -- ─────────────────────────────────────────────────────────────────────
        CASE 
            WHEN C.PROCESS_GROUP_ECOMMERCE = 'Drivers' THEN 'Driver'
            WHEN C.PROCESS_GROUP_ECOMMERCE = 'Driver' THEN 'Driver'
            ELSE C.PROCESS_GROUP_ECOMMERCE
        END AS PROCESS_GROUP_ECOMMERCE,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- REPORTING DIMENSIONS
        -- ─────────────────────────────────────────────────────────────────────
        C.PROCESS_BU_CR_REPORTING AS PROCESO_BU_CR_PLANNING,
        C.PROCESS_PROBLEMATIC_REPORTING AS PROBLEMATIC_REPORTING,
        C.PROCESS_GROUP_UPDATE_REPORTING AS PRO_PROCESS_GROUP_REPORTING,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- AGRUP_COMMERCE LOGIC (15 Commerce Groups)
        -- ─────────────────────────────────────────────────────────────────────
        CASE
            -- 📦 POST-COMPRA (Priority 1)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Others%') THEN 'PDD'
            
            -- 🚛 SHIPPING - ME DISTRIBUCIÓN (Comprador) (Priority 2a)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') 
                 THEN 'ME Distribución'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra Comprador%') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') 
                 THEN 'ME Distribución'
            
            -- 🚛 SHIPPING - ME PREDESPACHO (Vendedor) (Priority 2b)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') 
                 THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('Post Compra Funcionalidades Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') 
                 THEN 'ME PreDespacho'
            
            -- 🚛 SHIPPING - DRIVERS (Priority 2c)
            WHEN C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
            
            -- 🚛 SHIPPING - FBM (Priority 2d)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%FBM Sellers%') THEN 'FBM Sellers'
            
            -- 🛒 MARKETPLACE (Priority 3)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PreVenta%') THEN 'Pre Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PostVenta%') THEN 'Post Venta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Redes%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Prustomer%') THEN 'Moderaciones'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') THEN 'Generales Compra'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Compra%') THEN 'Generales Compra'
            
            -- 💳 PAGOS (Priority 4)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Pagos%') THEN 'Pagos'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP Payer%') THEN 'MP On'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP On%') THEN 'MP On'
            
            -- 👤 CUENTA (Priority 5)
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Seguridad 360%') THEN 'Cuenta'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Experiencia Impositiva%') THEN 'Experiencia Impositiva'
            
            -- DEFAULT (Priority 6)
            ELSE 'Generales Compra' 
        END AS AGRUP_COMMERCE,
        
        -- ─────────────────────────────────────────────────────────────────────
        -- FLAGS AND METRICS
        -- ─────────────────────────────────────────────────────────────────────
        C.FLAG_EXCLUDE_NUMERATOR_CR,
        C.FLAG_EXCLUDE_NUMERATOR_HR,
        C.FLAG_AUTO,
        
        -- Incoming classification by origin table
        CASE WHEN C.ORIGIN_TABLE = 'BT_CX_INCOMING_CR' THEN 1.0 ELSE 0.0 END AS INCOMING_NO_CONFLICT,
        CASE WHEN C.ORIGIN_TABLE = 'BT_CX_CLAIMS_CR' THEN 1.0 ELSE 0.0 END AS INCOMING_CONFLICT,
        
        -- Universal counter for aggregations
        1.0 AS CANT_CASES
        
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    
    -- ─────────────────────────────────────────────────────────────────────────
    -- LEFT JOIN WITH ORDERS (optional - for temporal correlation)
    -- ─────────────────────────────────────────────────────────────────────────
    LEFT JOIN `meli-bi-data.WHOWNER.BT_ORD_ORDERS` O 
        ON C.SOURCE_ID = O.ORD_ORDER_ID 
        AND C.SIT_SITE_ID = O.SIT_SITE_ID
    
    -- ═════════════════════════════════════════════════════════════════════════
    -- WHERE FILTERS (CRITICAL - DO NOT MODIFY)
    -- ═════════════════════════════════════════════════════════════════════════
    WHERE
        -- Date range filter (REQUIRED - uses partition)
        CAST(C.CONTACT_DATE_ID AS DATE) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        
        -- Site filter (REQUIRED)
        AND C.SIT_SITE_ID IN ({sites})
        AND C.SIT_SITE_ID NOT IN ('MLV')  -- Venezuela excluded
        
        -- Process exclusions
        AND C.PROCESS_ID NOT IN (1312)  -- Internal/administrative processes
        
        -- Business Unit filter
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        
        -- Queue exclusions (testing/development/out of scope)
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2131, 2294, 2295)
        
        -- User Type filter (includes Drivers automatically)
        AND (C.PROCESS_GROUP_ECOMMERCE IN ({user_types}) 
             OR C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers'))
        
        -- CI Reason exclusions (non-relevant reasons)
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        
        -- CR Flag (CRITICAL - only include cases eligible for CR)
        AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
        
        -- ─────────────────────────────────────────────────────────────────────
        -- ENVIRONMENT FILTER (optional - placeholder)
        -- ─────────────────────────────────────────────────────────────────────
        {environment_filter}
)

-- ═════════════════════════════════════════════════════════════════════════════
-- FINAL SELECT - Filter by Commerce Groups
-- ═════════════════════════════════════════════════════════════════════════════
SELECT *
FROM BASE_CONTACTS
WHERE AGRUP_COMMERCE IN ({agrup_commerce})

-- ═════════════════════════════════════════════════════════════════════════════
-- NOTES:
-- ═════════════════════════════════════════════════════════════════════════════
-- 1. This query returns RAW contact data (not aggregated)
-- 2. Use aggregation queries (see aggregations.sql) to group by dimensions
-- 3. For MLB (Brasil), apply sampling strategy (see sampling-strategy.sql)
-- 4. VERTICAL and DOM_DOMAIN_AGG1 are NULL (table not available)
-- 5. Always include date filter for performance (partition optimization)
-- 6. Default threshold: 100 cases minimum (apply in aggregation)
-- ═════════════════════════════════════════════════════════════════════════════

-- EXAMPLE USAGE:
-- 
-- Start Date: 2026-01-01
-- End Date: 2026-01-31
-- Sites: MLA, MLC
-- Commerce Groups: PDD, PNR
-- User Types: Comprador, Vendedor
-- Environment Filter: (empty - no filter)
--
-- Replace placeholders:
-- {fecha_inicio} → '2026-01-01'
-- {fecha_fin} → '2026-01-31'
-- {sites} → 'MLA', 'MLC'
-- {agrup_commerce} → 'PDD', 'PNR'
-- {user_types} → 'Comprador', 'Vendedor'
-- {environment_filter} → (empty string or specific filter like "AND C.ENVIRONMENT IN ('DS', 'FBM')")
