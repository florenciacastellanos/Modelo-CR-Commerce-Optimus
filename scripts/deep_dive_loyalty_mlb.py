"""
Deep Dive Loyalty MLB - Análisis Completo
==========================================
Genera análisis exhaustivo de Loyalty para MLB Nov-Dic 2025 incluyendo:
- Peak detection
- Evolución temporal
- Análisis de sub-causas (CDU, Tipificación)
- Distribución por canal (Source ID)
- Distribución por solución (Solution ID)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# Configuración
OUTPUT_DIR = Path(__file__).parent.parent / "output"
SQL_DIR = Path(__file__).parent.parent / "sql"

def analizar_peaks(df_daily):
    """Identifica picos usando desviación estándar"""
    promedio = df_daily['casos_dia'].mean()
    std_dev = df_daily['casos_dia'].std()
    
    df_daily['promedio'] = promedio
    df_daily['std_dev'] = std_dev
    df_daily['z_score'] = (df_daily['casos_dia'] - promedio) / std_dev
    df_daily['pct_vs_promedio'] = (df_daily['casos_dia'] / promedio) * 100
    df_daily['tipo_dia'] = df_daily['z_score'].apply(
        lambda x: 'PICO' if x > 1.5 else ('VALLE' if x < -1.5 else 'NORMAL')
    )
    
    return df_daily

def leer_datos_daily():
    """Lee datos diarios de Loyalty"""
    csv_path = OUTPUT_DIR / "temp_loyalty_daily.csv"
    
    # Leer con encoding correcto
    df = pd.read_csv(csv_path, encoding='utf-16-le')
    
    # Limpiar espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'].str.strip())
    df['casos_dia'] = df['casos_dia'].astype(int)
    
    return df

print("\n" + "="*80)
print("DEEP DIVE LOYALTY MLB - Nov-Dic 2025")
print("="*80 + "\n")

# 1. ANÁLISIS DE PEAKS
print("[1/6] Analizando peaks...")
df_daily = leer_datos_daily()
df_peaks = analizar_peaks(df_daily)

# Separar por período
df_nov = df_peaks[df_peaks['fecha'].dt.month == 11].copy()
df_dec = df_peaks[df_peaks['fecha'].dt.month == 12].copy()

# Identificar picos
picos_nov = df_nov[df_nov['tipo_dia'] == 'PICO']['fecha'].tolist()
picos_dec = df_dec[df_dec['tipo_dia'] == 'PICO']['fecha'].tolist()

print(f"   - Picos Nov: {len(picos_nov)} días")
if picos_nov:
    print(f"     Fechas: {[d.strftime('%Y-%m-%d') for d in picos_nov]}")

print(f"   - Picos Dic: {len(picos_dec)} días")
if picos_dec:
    print(f"     Fechas: {[d.strftime('%Y-%m-%d') for d in picos_dec]}")

# Guardar análisis de peaks
df_peaks.to_csv(OUTPUT_DIR / "deepdive_loyalty_peaks.csv", index=False, encoding='utf-8')
print(f"   [OK] Guardado: deepdive_loyalty_peaks.csv")

# 2. MÉTRICAS CONSOLIDADAS
print("\n[2/6] Calculando métricas consolidadas...")
total_nov = df_nov['casos_dia'].sum()
total_dec = df_dec['casos_dia'].sum()
promedio_nov = df_nov['casos_dia'].mean()
promedio_dec = df_dec['casos_dia'].mean()

variacion_abs = total_dec - total_nov
variacion_pct = ((total_dec / total_nov) - 1) * 100 if total_nov > 0 else 0

print(f"   - Nov 2025: {total_nov:,} casos ({promedio_nov:.1f} casos/día)")
print(f"   - Dic 2025: {total_dec:,} casos ({promedio_dec:.1f} casos/día)")
print(f"   - Variación: +{variacion_abs:,} casos (+{variacion_pct:.1f}%)")

# 3. ANÁLISIS SEMANAL
print("\n[3/6] Análisis de tendencia semanal...")
df_peaks['semana'] = df_peaks['fecha'].dt.isocalendar().week
df_peaks['periodo'] = df_peaks['fecha'].apply(lambda x: 'Nov 2025' if x.month == 11 else 'Dic 2025')

df_semanal = df_peaks.groupby(['periodo', 'semana']).agg({
    'casos_dia': 'sum',
    'fecha': 'count'
}).rename(columns={'casos_dia': 'casos_semana', 'fecha': 'dias'}).reset_index()

df_semanal['promedio_dia'] = df_semanal['casos_semana'] / df_semanal['dias']

print("   Evolución semanal:")
for idx, row in df_semanal.iterrows():
    print(f"     Semana {row['semana']} ({row['periodo']}): {row['casos_semana']:,} casos ({row['promedio_dia']:.1f}/día)")

df_semanal.to_csv(OUTPUT_DIR / "deepdive_loyalty_semanal.csv", index=False, encoding='utf-8')
print(f"   [OK] Guardado: deepdive_loyalty_semanal.csv")

# 4. QUERY PARA SUB-CAUSAS (CDU, TIPIFICACION)
print("\n[4/6] Generando query para análisis de sub-causas...")

query_subcausas = """
-- Análisis de Sub-Causas Loyalty MLB Nov-Dic 2025
WITH INCOMING_LOYALTY AS (
    SELECT
        DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) as PERIODO,
        C.CAS_CASE_ID,
        C.CDU,
        C.REASON_DETAIL_GROUP_REPORTING as TIPIFICACION
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE C.SIT_SITE_ID = 'MLB'
        AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
        AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.PROCESS_NAME = 'Loyalty'
)

SELECT
    CASE 
        WHEN PERIODO = '2025-11-01' THEN 'Nov 2025'
        WHEN PERIODO = '2025-12-01' THEN 'Dic 2025'
    END as PERIODO,
    COALESCE(CDU, 'Sin CDU') as CDU,
    COALESCE(TIPIFICACION, 'Sin Tipificación') as TIPIFICACION,
    COUNT(DISTINCT CAS_CASE_ID) as CASOS
FROM INCOMING_LOYALTY
GROUP BY PERIODO, CDU, TIPIFICACION
ORDER BY PERIODO, CASOS DESC;
"""

query_path = SQL_DIR / "temp_loyalty_subcausas.sql"
with open(query_path, 'w', encoding='utf-8') as f:
    f.write(query_subcausas)

print(f"   [OK] Query generada: {query_path.name}")
print("   -> Ejecutar: Get-Content sql\\temp_loyalty_subcausas.sql -Raw | bq query --use_legacy_sql=false --format=csv > output\\temp_loyalty_subcausas.csv")

# 5. QUERY PARA CANALES (SOURCE_ID)
print("\n[5/6] Generando query para análisis de canales...")

query_canales = """
-- Análisis de Canales Loyalty MLB Nov-Dic 2025
SELECT
    CASE 
        WHEN DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-11-01' THEN 'Nov 2025'
        WHEN DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-12-01' THEN 'Dic 2025'
    END as PERIODO,
    COALESCE(C.SOURCE_ID, 'Sin Source') as SOURCE_ID,
    COALESCE(C.CHANNEL_ID, 'Sin Channel') as CHANNEL_ID,
    COUNT(DISTINCT C.CAS_CASE_ID) as CASOS
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE C.SIT_SITE_ID = 'MLB'
    AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
    AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
    AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
    AND C.PROCESS_NAME = 'Loyalty'
GROUP BY PERIODO, SOURCE_ID, CHANNEL_ID
ORDER BY PERIODO, CASOS DESC;
"""

query_path = SQL_DIR / "temp_loyalty_canales.sql"
with open(query_path, 'w', encoding='utf-8') as f:
    f.write(query_canales)

print(f"   [OK] Query generada: {query_path.name}")
print("   -> Ejecutar: Get-Content sql\\temp_loyalty_canales.sql -Raw | bq query --use_legacy_sql=false --format=csv > output\\temp_loyalty_canales.csv")

# 6. QUERY PARA SOLUCIONES (SOLUTION_ID)
print("\n[6/6] Generando query para análisis de soluciones...")

query_soluciones = """
-- Análisis de Soluciones Loyalty MLB Nov-Dic 2025
SELECT
    CASE 
        WHEN DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-11-01' THEN 'Nov 2025'
        WHEN DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-12-01' THEN 'Dic 2025'
    END as PERIODO,
    COALESCE(C.SOLUTION_ID, 'Sin Solución') as SOLUTION_ID,
    COUNT(DISTINCT C.CAS_CASE_ID) as CASOS
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE C.SIT_SITE_ID = 'MLB'
    AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
    AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
    AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
    AND C.PROCESS_NAME = 'Loyalty'
GROUP BY PERIODO, SOLUTION_ID
ORDER BY PERIODO, CASOS DESC;
"""

query_path = SQL_DIR / "temp_loyalty_soluciones.sql"
with open(query_path, 'w', encoding='utf-8') as f:
    f.write(query_soluciones)

print(f"   [OK] Query generada: {query_path.name}")
print("   -> Ejecutar: Get-Content sql\\temp_loyalty_soluciones.sql -Raw | bq query --use_legacy_sql=false --format=csv > output\\temp_loyalty_soluciones.csv")

# Resumen de hallazgos iniciales
print("\n" + "="*80)
print("HALLAZGOS INICIALES - LOYALTY MLB")
print("="*80)
print(f"""
1. VARIACIÓN GENERAL:
   - Loyalty creció +{variacion_abs:,} casos (+{variacion_pct:.1f}%) de Nov a Dic
   - Nov: {total_nov:,} casos | Dic: {total_dec:,} casos
   
2. PICOS DETECTADOS:
   - Nov: {len(picos_nov)} días anómalos
   - Dic: {len(picos_dec)} días anómalos
   {f"- Pico más alto Dic: {df_dec[df_dec['tipo_dia']=='PICO']['fecha'].iloc[0].strftime('%Y-%m-%d')} ({df_dec[df_dec['tipo_dia']=='PICO']['casos_dia'].iloc[0]} casos)" if len(picos_dec) > 0 else ""}

3. PROXIMOS PASOS:
   [OK] Ejecutar queries de sub-causas, canales y soluciones (ver comandos arriba)
   -> Luego ejecutar: py scripts\\analizar_deepdive_loyalty_parte2.py
   -> Esto generara el reporte HTML completo con 2 tabs
""")

print("\n" + "="*80)
print("FASE 1 COMPLETADA - Ejecutar queries de BigQuery antes de continuar")
print("="*80 + "\n")
