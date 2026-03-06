WITH pnr_claims AS (
    SELECT
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        CASE
            WHEN cla.CLA_LABELS LIKE '%melinda%' THEN 'VERDI'
            WHEN cla.CLA_LABELS LIKE '%verdi%' THEN 'VERDI'
            ELSE 'NO VERDI'
        END AS FLAG_VERDI_CONTROL,
        CASE
            WHEN cla.cla_reason_detail IN ('invalid_shipment_status','delivered_but_not_receive','delivered_but_not_receive_package') THEN 'PNR C'
            ELSE 'PAD'
        END AS TIPIF_PNR,
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

totals AS (
    SELECT
        Mes_Claim,
        sit_site_id,
        SUM(reclamos) AS total_claims
    FROM pnr_claims
    GROUP BY 1, 2
)

SELECT
    p.Mes_Claim AS PERIODO,
    p.sit_site_id AS SITE,
    p.FLAG_VERDI_CONTROL,
    p.TIPIF_PNR,
    SUM(p.reclamos) AS CLAIMS,
    MAX(t.total_claims) AS TOTAL_CLAIMS_PNR,
    SAFE_DIVIDE(SUM(p.reclamos), MAX(t.total_claims)) AS SHARE
FROM pnr_claims p
LEFT JOIN totals t
    ON p.Mes_Claim = t.Mes_Claim
    AND p.sit_site_id = t.sit_site_id
GROUP BY 1, 2, 3, 4
ORDER BY PERIODO, SITE, FLAG_VERDI_CONTROL, TIPIF_PNR

LIMIT 10000
