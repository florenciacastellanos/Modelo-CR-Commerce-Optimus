-- Debug: Verificar eventos comerciales en MEC para el período analizado
SELECT 
    SIT_SITE_ID,
    EVENT_NAME,
    DATE(EVENT_START_DTTM) as fecha_inicio,
    DATE(EVENT_END_DTTM) as fecha_fin
FROM `meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT`
WHERE SIT_SITE_ID = 'MEC'
    AND (
        DATE(EVENT_START_DTTM) BETWEEN '2025-12-01' AND '2026-01-31'
        OR DATE(EVENT_END_DTTM) BETWEEN '2025-12-01' AND '2026-01-31'
    )
ORDER BY fecha_inicio
