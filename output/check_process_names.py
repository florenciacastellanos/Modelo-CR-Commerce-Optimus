"""Query para verificar process names disponibles dentro de MODERACIONES"""
from google.cloud import bigquery
import warnings
warnings.filterwarnings("ignore")

client = bigquery.Client(project="meli-bi-data")

query = """
SELECT DISTINCT C.PROCESS_NAME, COUNT(*) as casos
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE C.CONTACT_DATE_ID BETWEEN '2026-01-01' AND '2026-02-28'
  AND C.SIT_SITE_ID = 'MLA'
  AND (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' OR C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Moderaciones%')
  AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
  AND C.SIT_SITE_ID NOT IN ('MLV')
  AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
  AND C.PROCESS_ID NOT IN (1312)
  AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
GROUP BY C.PROCESS_NAME
ORDER BY casos DESC
LIMIT 30
"""

df = client.query(query).to_dataframe()
print("PROCESS_NAME values within MODERACIONES (MLA, Jan-Feb 2026):")
print("=" * 70)
for _, row in df.iterrows():
    print(f"  {row['PROCESS_NAME']:<50} | {int(row['casos']):>8} casos")
print("=" * 70)
print(f"Total procesos: {len(df)}")

# Also check for anything with "prohib" in it across all commerce groups
query2 = """
SELECT DISTINCT C.PROCESS_NAME, C.PROCESS_PROBLEMATIC_REPORTING, COUNT(*) as casos
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE C.CONTACT_DATE_ID BETWEEN '2026-01-01' AND '2026-02-28'
  AND C.SIT_SITE_ID = 'MLA'
  AND LOWER(C.PROCESS_NAME) LIKE '%prohib%'
  AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
GROUP BY C.PROCESS_NAME, C.PROCESS_PROBLEMATIC_REPORTING
ORDER BY casos DESC
"""
df2 = client.query(query2).to_dataframe()
print("\nProcess names con 'prohib' (todas las categorías):")
print("=" * 70)
for _, row in df2.iterrows():
    print(f"  {row['PROCESS_NAME']:<40} | PPR: {row['PROCESS_PROBLEMATIC_REPORTING']:<30} | {int(row['casos']):>6}")
print("=" * 70)
