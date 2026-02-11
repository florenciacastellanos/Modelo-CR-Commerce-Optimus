-- ══════════════════════════════════════════════════════════════════════════════
-- CLASIFICACIÓN DE COMMERCE GROUPS - CASE STATEMENT OFICIAL
-- ══════════════════════════════════════════════════════════════════════════════
-- Versión: 3.5
-- Fecha: Enero 2026
-- Estado: VALIDADO - Método oficial del repositorio
-- ══════════════════════════════════════════════════════════════════════════════

-- Este CASE debe usarse SIEMPRE para clasificar Commerce Groups
-- NO usar filtros simples como LIKE '%PDD%' (pierde ~2% de casos)

CASE 
    -- ══════════════════════════════════════════════════════════════════════════
    -- POST-COMPRA (2 grupos)
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- PDD (Producto Dañado/Defectuoso)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'  -- ← CRÍTICO: Caso especial
    
    -- PNR (Producto No Recibido)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'  
    WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'  -- ← CRÍTICO: Caso especial
    
    -- Post Compra Funcionalidades (separado por tipo de usuario)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
         AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'PCF Comprador'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
         AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'PCF Vendedor'
    
    -- ══════════════════════════════════════════════════════════════════════════
    -- SHIPPING (4 grupos - requieren PROCESS_GROUP_ECOMMERCE)
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- ME Distribución (Comprador)
    WHEN (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
          AND C.PROCESS_GROUP_ECOMMERCE = 'Comprador')
         OR (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
             AND C.PROCESS_BU_CR_REPORTING = 'ME') THEN 'ME Distribución'
    
    -- ME PreDespacho (Vendedor)
    WHEN (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
          AND C.PROCESS_GROUP_ECOMMERCE = 'Vendedor')
         OR (C.PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
             AND C.PROCESS_BU_CR_REPORTING = 'ME') THEN 'ME PreDespacho'
    
    -- ME Drivers
    WHEN C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
    
    -- FBM Sellers
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
    
    -- ══════════════════════════════════════════════════════════════════════════
    -- MARKETPLACE (6 grupos)
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- Pre Venta
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PreVenta%' THEN 'Pre Venta'
    
    -- Post Venta
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PostVenta%' THEN 'Post Venta'
    
    -- Generales Compra
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Compra%' THEN 'Generales Compra'
    
    -- Moderaciones (incluye Prustomer)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' THEN 'Moderaciones'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Moderaciones%' THEN 'Moderaciones'
    
    -- Full Sellers
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Full Sellers%' THEN 'Full Sellers'
    
    -- Pagos (Marketplace)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' 
         AND C.PROCESS_GROUP_ECOMMERCE NOT IN ('MP') THEN 'Pagos'
    
    -- ══════════════════════════════════════════════════════════════════════════
    -- PAGOS (1 grupo)
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- MP On (Mercado Pago Online)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' 
         AND C.PROCESS_GROUP_ECOMMERCE IN ('MP') THEN 'MP On'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%MP Payer%' THEN 'MP On'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' THEN 'MP On'
    
    -- ══════════════════════════════════════════════════════════════════════════
    -- CUENTA (2 grupos)
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- Cuenta (incluye Seguridad 360)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Seguridad 360%' THEN 'Cuenta'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Cuenta%' THEN 'Cuenta'
    
    -- Experiencia Impositiva
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Experiencia Impositiva%' THEN 'Experiencia Impositiva'
    
    -- ══════════════════════════════════════════════════════════════════════════
    -- OTROS / SHARED SERVICES
    -- ══════════════════════════════════════════════════════════════════════════
    
    -- Shared Services (incluye Redes, CAP, etc.)
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Redes%' THEN 'Shared Services'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%CAP%' THEN 'Shared Services'
    WHEN C.USER_TEAM_ID IN (672, 673) THEN 'Shared Services'
    
    -- Default
    ELSE 'OTRO'
    
END AS AGRUP_COMMERCE_PROPIO

-- ══════════════════════════════════════════════════════════════════════════════
-- NOTAS IMPORTANTES
-- ══════════════════════════════════════════════════════════════════════════════
-- 
-- 1. SIEMPRE clasificar primero con este CASE, filtrar después
-- 2. NO usar filtros directos tipo: WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
-- 3. Casos especiales críticos:
--    - "Conflict Others" → PDD (NO contiene "PDD")
--    - "Conflict Stale" → PNR (NO contiene "PNR")
-- 4. Shipping requiere PROCESS_GROUP_ECOMMERCE para diferenciar:
--    - Comprador → ME Distribución
--    - Vendedor → ME PreDespacho
-- 5. Validado Enero 2026 - 100% alineado con producción
-- 
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- EJEMPLO DE USO
-- ══════════════════════════════════════════════════════════════════════════════

-- Para obtener solo casos PDD:
WITH CLASIFICACION AS (
    SELECT
        C.*,
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            -- ... (resto del CASE)
        END AS AGRUP_COMMERCE_PROPIO
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE 1=1
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
)
SELECT *
FROM CLASIFICACION
WHERE AGRUP_COMMERCE_PROPIO = 'PDD'  -- ← Filtrar DESPUÉS de clasificar

-- ══════════════════════════════════════════════════════════════════════════════
