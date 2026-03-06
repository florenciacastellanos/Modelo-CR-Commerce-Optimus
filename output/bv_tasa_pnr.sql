WITH claims AS (
    SELECT
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        c.VERTICAL,
        CASE
            WHEN cla.CLA_LABELS LIKE '%melinda%' THEN 'VERDI'
            WHEN cla.CLA_LABELS LIKE '%verdi%' THEN 'VERDI'
            ELSE 'NO VERDI'
        END AS FLAG_VERDI_CONTROL,
        CASE
            WHEN cla.cla_reason_detail IN ('invalid_shipment_status','delivered_but_not_receive','delivered_but_not_receive_package') THEN 'PNR C'
            ELSE 'PAD'
        END AS TIPIF_PNR,
        c.environment_ord,
        c.flow_claim,
        c.Fallo,
        COUNT(DISTINCT cla.CLA_CLAIM_ID) AS reclamos
    FROM `meli-bi-data.WHOWNER.BT_CM_CLAIMS_V1` cla, UNNEST(cla.ord_order_id) AS orders
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` c
        ON c.CLA_CLAIM_ID = cla.CLA_CLAIM_ID
        AND c.CLA_DATE_CLAIM_OPENED_DT >= '2025-11-01'
    WHERE c.REASON_CLAIM = 'PNR'
        AND cla.sit_site_id IN ('MLB')
        AND cla.CLA_DATE_CLAIM_OPENED_DT >= '2025-11-01'
        AND cla.CLA_DATE_CLAIM_OPENED_DT < '2026-01-01'
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
    cl.Mes_Claim AS PERIODO,
    cl.sit_site_id AS SITE,
    cl.VERTICAL,
    cl.FLAG_VERDI_CONTROL,
    cl.TIPIF_PNR,
    cl.environment_ord AS ENVIRONMENT_ORD,
    cl.flow_claim AS FLOW_CLAIM,
    cl.Fallo AS FALLO,
    SUM(cl.reclamos) AS CLAIMS,
    MAX(ot.ordenes) AS ORDENES,
    SAFE_DIVIDE(SUM(cl.reclamos), MAX(ot.ordenes)) AS TASA_PNR
FROM claims cl
LEFT JOIN orders_total ot
    ON cl.Mes_Claim = ot.Mes_Compra
    AND cl.sit_site_id = ot.sit_site_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
ORDER BY PERIODO, SITE, CLAIMS DESC

LIMIT 10000
