WITH pnr_claims_raw AS (
    SELECT
        cla.CLA_CLAIM_ID,
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        MIN(ord.ORD_CREATED_DT) AS orden_fecha_min
    FROM `meli-bi-data.WHOWNER.BT_CM_CLAIMS_V1` cla, UNNEST(cla.ord_order_id) AS order_id
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` c
        ON c.CLA_CLAIM_ID = cla.CLA_CLAIM_ID
        AND c.CLA_DATE_CLAIM_OPENED_DT >= '2025-11-01'
    LEFT JOIN `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ord
        ON ord.ORD_ORDER_ID = order_id
        AND ord.SIT_SITE_ID = cla.sit_site_id
        AND ord.ORD_CREATED_DT >= DATE_SUB(PARSE_DATE('%Y-%m-%d', '2025-11-01'), INTERVAL 6 MONTH)
    WHERE c.REASON_CLAIM = 'PNR'
        AND cla.sit_site_id IN ('MLB')
        AND cla.CLA_DATE_CLAIM_OPENED_DT >= '2025-11-01'
        AND cla.CLA_DATE_CLAIM_OPENED_DT < '2026-01-01'
    GROUP BY cla.CLA_CLAIM_ID, cla.CLA_DATE_CLAIM_OPENED_DT, cla.sit_site_id
),

claims_estacional AS (
    SELECT
        Mes_Claim,
        sit_site_id,
        CASE
            WHEN DATE_TRUNC(orden_fecha_min, MONTH) = Mes_Claim THEN 'PERIODO_ACTUAL'
            ELSE 'PERIODO_ANTERIOR'
        END AS tipo_estacionalidad,
        COUNT(DISTINCT CLA_CLAIM_ID) AS reclamos
    FROM pnr_claims_raw
    GROUP BY ALL
),

orders_total AS (
    SELECT
        Mes_Compra,
        sit_site_id,
        SUM(orders) AS ordenes
    FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.variaciones_orders`
    WHERE sit_site_id IN ('MLB')
        AND Mes_Compra >= DATE('2025-11-01')
        AND Mes_Compra < DATE('2026-01-01')
    GROUP BY 1, 2
)

SELECT
    ce.Mes_Claim AS PERIODO,
    ce.sit_site_id AS SITE,
    ce.tipo_estacionalidad AS TIPO_ESTACIONALIDAD,
    SUM(ce.reclamos) AS CLAIMS,
    MAX(ot.ordenes) AS ORDENES,
    SAFE_DIVIDE(SUM(ce.reclamos), MAX(ot.ordenes)) AS TASA_PNR_COMPONENTE
FROM claims_estacional ce
LEFT JOIN orders_total ot
    ON ce.Mes_Claim = ot.Mes_Compra
    AND ce.sit_site_id = ot.sit_site_id
GROUP BY 1, 2, 3
ORDER BY PERIODO, SITE, TIPO_ESTACIONALIDAD

LIMIT 10000
