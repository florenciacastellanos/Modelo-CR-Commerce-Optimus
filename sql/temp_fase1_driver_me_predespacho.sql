-- ══════════════════════════════════════════════════════════════════════════════
-- FASE 1: Driver ME PreDespacho - OS_WITHOUT_FBM (GLOBAL, sin filtro site)
-- Dic 2025 vs Ene 2026
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    drv.MONTH_ID AS period,
    SUM(drv.OS_WITHOUT_FBM) AS driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE drv.MONTH_ID BETWEEN '2025-12-01' AND '2026-01-31'
GROUP BY drv.MONTH_ID
ORDER BY drv.MONTH_ID
