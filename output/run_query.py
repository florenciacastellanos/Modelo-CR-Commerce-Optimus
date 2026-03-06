from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
    FORMAT_DATE('%Y-%m', CAST(C.CONTACT_DATE_ID AS DATE)) AS MES,
    COUNT(*) AS INCOMING_CASES
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE
    CAST(C.CONTACT_DATE_ID AS DATE) BETWEEN '2025-11-01' AND '2025-12-31'
    AND C.SIT_SITE_ID = 'MLA'
    AND C.PROCESS_NAME = 'Reputación'
    AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
    AND C.PROCESS_ID NOT IN (1312)
    AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
    AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
    AND C.PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
GROUP BY MES
ORDER BY MES
"""

print("Ejecutando query...")
results = client.query(query).result()
print("MES,INCOMING_CASES")
for row in results:
    print(f"{row.MES},{row.INCOMING_CASES}")
print("Done.")
