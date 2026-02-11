-- ══════════════════════════════════════════════════════════════════════════════
-- DRIVER - MEC (Ecuador) - Dic 2025 vs Ene 2026
-- CATEGORÍA: Marketplace → Driver filtrado por SITE
-- ══════════════════════════════════════════════════════════════════════════════

SELECT
    CASE 
        WHEN ORD.ORD_CLOSED_DT BETWEEN '2025-12-01' AND '2025-12-31' THEN 'P1_DIC2025'
        WHEN ORD.ORD_CLOSED_DT BETWEEN '2026-01-01' AND '2026-01-31' THEN 'P2_ENE2026'
    END AS PERIODO,
    COUNT(DISTINCT ORD.ORD_ORDER_ID) AS DRIVER
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 
    ORD.ORD_CLOSED_DT BETWEEN '2025-12-01' AND '2026-01-31'
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID = 'MEC'  -- ✅ FILTRO POR SITE (Marketplace)
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
GROUP BY 1
ORDER BY 1
