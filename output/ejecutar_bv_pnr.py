"""
Ejecuta las 5 variables de negocio de PNR (MLB, Nov-Dic 2025)
y guarda los resultados como CSVs en la carpeta output/
"""
import warnings
warnings.filterwarnings("ignore")

from google.cloud import bigquery
import pandas as pd
import os

client = bigquery.Client()

SITES = "'MLB'"
FECHA_INICIO = "2025-11-01"
FECHA_FIN = "2026-01-01"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_query(name, sql):
    sql_rendered = sql.replace("{sites}", SITES)\
                      .replace("{fecha_inicio}", FECHA_INICIO)\
                      .replace("{fecha_fin}", FECHA_FIN)
    print(f"\n[BV] Ejecutando: {name}...")
    df = client.query(sql_rendered).to_dataframe()
    out_path = os.path.join(OUT_DIR, f"bv_{name}_mlb_nov_dic_2025.csv")
    df.to_csv(out_path, index=False)
    print(f"[OK] {name}: {len(df)} filas -> {out_path}")
    return df

# ── 1. Verticales y Dominios ──────────────────────────────────────────────────
verticales_sql = """
WITH BASE_CONTACTS AS (
    SELECT
        C.CLA_CLAIM_ID,
        C.SIT_SITE_ID,
        DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
        CASE
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            ELSE 'OTRO'
        END AS COMMERCE_GROUP
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE C.SIT_SITE_ID IN ({sites})
        AND C.CONTACT_DATE_ID >= '{fecha_inicio}'
        AND C.CONTACT_DATE_ID < '{fecha_fin}'
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.CLA_CLAIM_ID IS NOT NULL
),
VERTICALES_DATA AS (
    SELECT PP.CLA_CLAIM_ID, PP.VERTICAL, PP.DOM_DOMAIN_AGG1 AS DOMINIO
    FROM `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP
    WHERE PP.VERTICAL IS NOT NULL
)
SELECT
    B.SIT_SITE_ID AS SITE,
    B.PERIODO,
    B.COMMERCE_GROUP,
    COALESCE(V.VERTICAL, 'SIN_VERTICAL') AS VERTICAL,
    COALESCE(V.DOMINIO, 'SIN_DOMINIO') AS DOMINIO,
    COUNT(DISTINCT B.CLA_CLAIM_ID) AS INCOMING
FROM BASE_CONTACTS B
LEFT JOIN VERTICALES_DATA V ON B.CLA_CLAIM_ID = V.CLA_CLAIM_ID
WHERE B.COMMERCE_GROUP IN ('PDD', 'PNR')
GROUP BY 1,2,3,4,5
ORDER BY 1,2,3,6 DESC
LIMIT 10000
"""

# ── 2. Seller ID Incoming ─────────────────────────────────────────────────────
seller_sql = """
WITH BASE_CONTACTS AS (
    SELECT C.CLA_CLAIM_ID, C.SIT_SITE_ID, DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE C.SIT_SITE_ID IN ({sites})
        AND C.CONTACT_DATE_ID >= '{fecha_inicio}'
        AND C.CONTACT_DATE_ID < '{fecha_fin}'
        AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.CLA_CLAIM_ID IS NOT NULL
        AND (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale')
),
SELLER_INCOMING AS (
    SELECT B.SIT_SITE_ID AS SITE, B.PERIODO, PP.ORD_SELLER_ID AS SELLER_ID,
           COUNT(DISTINCT B.CLA_CLAIM_ID) AS INCOMING
    FROM BASE_CONTACTS B
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP ON PP.CLA_CLAIM_ID = B.CLA_CLAIM_ID
    GROUP BY 1,2,3
),
RANKED AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY SITE, PERIODO ORDER BY INCOMING DESC) AS RNK
    FROM SELLER_INCOMING
)
SELECT SITE, PERIODO, SELLER_ID, INCOMING, RNK
FROM RANKED
WHERE RNK <= 10
ORDER BY SITE, PERIODO, RNK
LIMIT 10000
"""

# ── 3. Tasa PNR ───────────────────────────────────────────────────────────────
tasa_sql = """
WITH claims AS (
    SELECT
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        c.VERTICAL,
        CASE WHEN cla.CLA_LABELS LIKE '%melinda%' OR cla.CLA_LABELS LIKE '%verdi%' THEN 'VERDI' ELSE 'NO VERDI' END AS FLAG_VERDI_CONTROL,
        CASE WHEN cla.cla_reason_detail IN ('invalid_shipment_status','delivered_but_not_receive','delivered_but_not_receive_package') THEN 'PNR C' ELSE 'PAD' END AS TIPIF_PNR,
        c.environment_ord, c.flow_claim, c.Fallo,
        COUNT(DISTINCT cla.CLA_CLAIM_ID) AS reclamos
    FROM `meli-bi-data.WHOWNER.BT_CM_CLAIMS_V1` cla, UNNEST(cla.ord_order_id) AS orders
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` c
        ON c.CLA_CLAIM_ID = cla.CLA_CLAIM_ID AND c.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
    WHERE c.REASON_CLAIM = 'PNR'
        AND cla.sit_site_id IN ({sites})
        AND cla.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
        AND cla.CLA_DATE_CLAIM_OPENED_DT < '{fecha_fin}'
    GROUP BY ALL
),
orders_total AS (
    SELECT Mes_Compra, sit_site_id, SUM(orders) AS ordenes
    FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.variaciones_orders`
    WHERE sit_site_id IN ({sites})
        AND Mes_Compra >= DATE('{fecha_inicio}')
        AND Mes_Compra < DATE('{fecha_fin}')
    GROUP BY 1,2
)
SELECT cl.Mes_Claim AS PERIODO, cl.sit_site_id AS SITE, cl.VERTICAL,
       cl.FLAG_VERDI_CONTROL, cl.TIPIF_PNR,
       cl.environment_ord AS ENVIRONMENT_ORD, cl.flow_claim AS FLOW_CLAIM, cl.Fallo AS FALLO,
       SUM(cl.reclamos) AS CLAIMS, MAX(ot.ordenes) AS ORDENES,
       SAFE_DIVIDE(SUM(cl.reclamos), MAX(ot.ordenes)) AS TASA_PNR
FROM claims cl
LEFT JOIN orders_total ot ON cl.Mes_Claim = ot.Mes_Compra AND cl.sit_site_id = ot.sit_site_id
GROUP BY 1,2,3,4,5,6,7,8
ORDER BY PERIODO, SITE, CLAIMS DESC
LIMIT 10000
"""

# ── 4. Estacionalidad PNR ─────────────────────────────────────────────────────
estac_sql = """
WITH pnr_claims_raw AS (
    SELECT
        cla.CLA_CLAIM_ID,
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        MIN(ord.ORD_CREATED_DT) AS orden_fecha_min
    FROM `meli-bi-data.WHOWNER.BT_CM_CLAIMS_V1` cla, UNNEST(cla.ord_order_id) AS order_id
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` c
        ON c.CLA_CLAIM_ID = cla.CLA_CLAIM_ID AND c.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
    LEFT JOIN `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ord
        ON ord.ORD_ORDER_ID = order_id
        AND ord.SIT_SITE_ID = cla.sit_site_id
        AND ord.ORD_CREATED_DT >= DATE_SUB(DATE('{fecha_inicio}'), INTERVAL 6 MONTH)
    WHERE c.REASON_CLAIM = 'PNR'
        AND cla.sit_site_id IN ({sites})
        AND cla.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
        AND cla.CLA_DATE_CLAIM_OPENED_DT < '{fecha_fin}'
    GROUP BY cla.CLA_CLAIM_ID, cla.CLA_DATE_CLAIM_OPENED_DT, cla.sit_site_id
),
claims_estacional AS (
    SELECT Mes_Claim, sit_site_id,
        CASE WHEN DATE_TRUNC(orden_fecha_min, MONTH) = Mes_Claim THEN 'PERIODO_ACTUAL' ELSE 'PERIODO_ANTERIOR' END AS tipo_estacionalidad,
        COUNT(DISTINCT CLA_CLAIM_ID) AS reclamos
    FROM pnr_claims_raw
    GROUP BY ALL
),
orders_total AS (
    SELECT Mes_Compra, sit_site_id, SUM(orders) AS ordenes
    FROM `meli-bi-data.SBOX_CX_BI_ADS_CORE.variaciones_orders`
    WHERE sit_site_id IN ({sites})
        AND Mes_Compra >= DATE('{fecha_inicio}')
        AND Mes_Compra < DATE('{fecha_fin}')
    GROUP BY 1,2
)
SELECT ce.Mes_Claim AS PERIODO, ce.sit_site_id AS SITE, ce.tipo_estacionalidad AS TIPO_ESTACIONALIDAD,
       SUM(ce.reclamos) AS CLAIMS, MAX(ot.ordenes) AS ORDENES,
       SAFE_DIVIDE(SUM(ce.reclamos), MAX(ot.ordenes)) AS TASA_PNR_COMPONENTE
FROM claims_estacional ce
LEFT JOIN orders_total ot ON ce.Mes_Claim = ot.Mes_Compra AND ce.sit_site_id = ot.sit_site_id
GROUP BY 1,2,3
ORDER BY PERIODO, SITE, TIPO_ESTACIONALIDAD
LIMIT 10000
"""

# ── 5. Efecto Verdi PNR ───────────────────────────────────────────────────────
verdi_sql = """
WITH pnr_claims AS (
    SELECT
        DATE_TRUNC(cla.CLA_DATE_CLAIM_OPENED_DT, MONTH) AS Mes_Claim,
        cla.sit_site_id,
        CASE WHEN cla.CLA_LABELS LIKE '%melinda%' OR cla.CLA_LABELS LIKE '%verdi%' THEN 'VERDI' ELSE 'NO VERDI' END AS FLAG_VERDI_CONTROL,
        CASE WHEN cla.cla_reason_detail IN ('invalid_shipment_status','delivered_but_not_receive','delivered_but_not_receive_package') THEN 'PNR C' ELSE 'PAD' END AS TIPIF_PNR,
        COUNT(DISTINCT cla.CLA_CLAIM_ID) AS reclamos
    FROM `meli-bi-data.WHOWNER.BT_CM_CLAIMS_V1` cla, UNNEST(cla.ord_order_id) AS orders
    LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` c
        ON c.CLA_CLAIM_ID = cla.CLA_CLAIM_ID AND c.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
    WHERE c.REASON_CLAIM = 'PNR'
        AND cla.sit_site_id IN ({sites})
        AND cla.CLA_DATE_CLAIM_OPENED_DT >= '{fecha_inicio}'
        AND cla.CLA_DATE_CLAIM_OPENED_DT < '{fecha_fin}'
    GROUP BY ALL
),
totals AS (
    SELECT Mes_Claim, sit_site_id, SUM(reclamos) AS total_claims
    FROM pnr_claims GROUP BY 1,2
)
SELECT p.Mes_Claim AS PERIODO, p.sit_site_id AS SITE,
       p.FLAG_VERDI_CONTROL, p.TIPIF_PNR,
       SUM(p.reclamos) AS CLAIMS,
       MAX(t.total_claims) AS TOTAL_CLAIMS_PNR,
       SAFE_DIVIDE(SUM(p.reclamos), MAX(t.total_claims)) AS SHARE
FROM pnr_claims p
LEFT JOIN totals t ON p.Mes_Claim = t.Mes_Claim AND p.sit_site_id = t.sit_site_id
GROUP BY 1,2,3,4
ORDER BY PERIODO, SITE, FLAG_VERDI_CONTROL, TIPIF_PNR
LIMIT 10000
"""

if __name__ == "__main__":
    run_query("verticales_dominios", verticales_sql)
    run_query("seller_id_incoming", seller_sql)
    run_query("tasa_pnr", tasa_sql)
    run_query("estacionalidad_pnr", estac_sql)
    run_query("efecto_verdi_pnr", verdi_sql)
    print("\n✅ Todas las variables ejecutadas correctamente.")
