"""
Script Generador de Métricas - Verticales y Dominios
Versión: 1.0
Fecha: Enero 2026

Propósito:
-----------
Pre-calcular agregados de incoming por Vertical y Dominio para análisis
de Contact Rate en PDD y PNR (Post-Compra).

⚠️ IMPORTANTE - Valores Dinámicos:
-----------------------------------
Las verticales y dominios se obtienen DIRECTAMENTE de BigQuery
(DM_CX_POST_PURCHASE.VERTICAL y DOM_DOMAIN_AGG1).

NO hay verticales hardcodeadas. NO hay filtros predefinidos.
El análisis usa EXACTAMENTE lo que devuelva la tabla, sin asumir, inventar o sesgar valores.

Alcance:
--------
SOLO PDD y PNR (Post-Compra). Otros commerce groups no tienen productos asociados.

Output:
-------
- Parquet: metrics/verticales/data/verticales_{site}_{periodo}.parquet
- Metadata: metrics/verticales/data/metadata_{site}_{periodo}.json

Uso:
----
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12
python metrics/verticales/generar_agregados.py --sites MLA,MLB --periodo 2025-12
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12 --commerce-group PDD
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12 --force
"""

import argparse
import sys
from google.cloud.bigquery import Client
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os

# Agregar path del repositorio para imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
from config.site_groups import resolve_site_sql

print("[METRICS] Generador de Agregados de Verticales y Dominios v1.0")
print("[METRICS] Fuente: WHOWNER.DM_CX_POST_PURCHASE (VERTICAL, DOM_DOMAIN_AGG1)")
print("[METRICS] Alcance: SOLO PDD y PNR (Post-Compra)")
print("="*70)

# ========================================
# PARSEO DE ARGUMENTOS
# ========================================

parser = argparse.ArgumentParser(description='Generar métricas de verticales y dominios')
parser.add_argument('--site', type=str, help='Site code (MLA, MLB, etc.)')
parser.add_argument('--sites', type=str, help='Múltiples sites separados por coma (MLA,MLB,MCO)')
parser.add_argument('--periodo', type=str, required=True, help='Período en formato YYYY-MM (ej: 2025-12)')
parser.add_argument('--commerce-group', type=str, help='Commerce group específico (PDD o PNR)', default='ALL')
parser.add_argument('--force', action='store_true', help='Forzar regeneración incluso si existe')

args = parser.parse_args()

# Determinar sites a procesar
if args.sites:
    sites_to_process = args.sites.split(',')
elif args.site:
    sites_to_process = [args.site]
else:
    print("[ERROR] Debe especificar --site o --sites")
    exit(1)

periodo = args.periodo
periodo_date = f"{periodo}-01"
periodo_str = periodo.replace('-', '_')

print(f"[CONFIG] Sites: {', '.join(sites_to_process)}")
print(f"[CONFIG] Período: {periodo}")
print(f"[CONFIG] Commerce Group: {args.commerce_group}")
print(f"[CONFIG] Force regeneration: {args.force}")
print()

# ========================================
# INICIALIZAR BIGQUERY CLIENT
# ========================================

client = Client()

# ========================================
# FUNCIÓN: VERIFICAR SI EXISTE MÉTRICA
# ========================================

def verificar_metrica_existente(site, periodo_str):
    """
    Verifica si ya existe métrica para este site y período
    
    Returns:
        tuple: (existe: bool, path: Path, dias_antiguedad: int)
    """
    output_dir = Path('metrics/verticales/data')
    output_file = output_dir / f'verticales_{site.lower()}_{periodo_str}.parquet'
    metadata_file = output_dir / f'metadata_{site.lower()}_{periodo_str}.json'
    
    if not output_file.exists():
        return False, output_file, None
    
    # Leer metadata para obtener fecha de generación
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            fecha_generacion = datetime.fromisoformat(metadata['generated_at'])
            dias_antiguedad = (datetime.now() - fecha_generacion).days
            
            return True, output_file, dias_antiguedad
        except:
            return True, output_file, None
    
    return True, output_file, None

# ========================================
# FUNCIÓN: GENERAR AGREGADOS PARA UN SITE
# ========================================

def generar_agregados_site(site, periodo_date, force=False):
    """
    Genera agregados de verticales para un site específico
    """
    print(f"\n[{site}] Procesando agregados de verticales para {periodo}...")
    
    # ========================================
    # VERIFICAR SI YA EXISTE (a menos que --force)
    # ========================================
    
    if not force:
        existe, path_existente, dias_antiguedad = verificar_metrica_existente(site, periodo_str)
        
        if existe:
            if dias_antiguedad is not None and dias_antiguedad < 90:
                print(f"[{site}] [INFO] Métrica ya existe (generada hace {dias_antiguedad} días)")
                print(f"[{site}] [INFO] Ubicación: {path_existente}")
                print(f"[{site}] [INFO] Para regenerar, usar --force")
                return None
            else:
                print(f"[{site}] [WARNING] Métrica existe pero es antigua o sin metadata válido")
                print(f"[{site}] [INFO] Regenerando automáticamente...")
    
    # ========================================
    # PASO 1: Obtener TODO el incoming de PDD/PNR
    # ========================================
    
    print(f"[{site}] Paso 1: Obteniendo incoming de PDD/PNR...")
    
    # Filtro de commerce group si se especificó
    commerce_filter = ""
    if args.commerce_group == 'PDD':
        commerce_filter = "AND (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others')"
    elif args.commerce_group == 'PNR':
        commerce_filter = "AND (C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale')"
    # Si es 'ALL' o cualquier otro valor, no filtrar (obtener ambos PDD y PNR)
    
    query_verticales = f"""
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
        WHERE {resolve_site_sql(site, 'C.SIT_SITE_ID')}
            AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '{periodo_date}'
            AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
            AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
            AND C.CLA_CLAIM_ID IS NOT NULL
            {commerce_filter}
    ),
    VERTICALES_DATA AS (
        SELECT
            PP.CLA_CLAIM_ID,
            PP.VERTICAL,
            PP.DOM_DOMAIN_AGG1 as DOMINIO
        FROM `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP
        WHERE PP.VERTICAL IS NOT NULL
    )
    SELECT 
        B.SIT_SITE_ID as SITE,
        B.PERIODO,
        B.COMMERCE_GROUP,
        COALESCE(V.VERTICAL, 'SIN_VERTICAL') as VERTICAL,
        COALESCE(V.DOMINIO, 'SIN_DOMINIO') as DOMINIO,
        COUNT(DISTINCT B.CLA_CLAIM_ID) as INCOMING
    FROM BASE_CONTACTS B
    LEFT JOIN VERTICALES_DATA V ON B.CLA_CLAIM_ID = V.CLA_CLAIM_ID
    WHERE B.COMMERCE_GROUP IN ('PDD', 'PNR')
    GROUP BY 1, 2, 3, 4, 5
    """
    
    print(f"[{site}] Ejecutando query (puede tardar 2-3 min)...")
    df_verticales = client.query(query_verticales).to_dataframe()
    
    if len(df_verticales) == 0:
        print(f"[{site}] [WARNING] No se encontró incoming PDD/PNR para este período")
        return None
    
    print(f"[{site}] [OK] {len(df_verticales):,} filas obtenidas")
    
    # ========================================
    # PASO 2: Calcular porcentaje del total
    # ========================================
    
    print(f"[{site}] Paso 2: Calculando porcentajes...")
    
    # Calcular total por commerce group
    totales_por_cg = df_verticales.groupby('COMMERCE_GROUP')['INCOMING'].sum().to_dict()
    
    # Calcular % del total
    df_verticales['PCT_DEL_TOTAL'] = df_verticales.apply(
        lambda row: round((row['INCOMING'] / totales_por_cg[row['COMMERCE_GROUP']]) * 100, 2),
        axis=1
    )
    
    # Agregar timestamp de generación
    df_verticales['GENERADO'] = datetime.now()
    
    # Convertir fechas
    df_verticales['PERIODO'] = pd.to_datetime(df_verticales['PERIODO'])
    
    print(f"[{site}] [OK] Porcentajes calculados")
    
    # ========================================
    # PASO 3: Estadísticas y validaciones
    # ========================================
    
    print(f"[{site}] Paso 3: Validando datos...")
    
    # Estadísticas
    total_incoming = df_verticales['INCOMING'].sum()
    verticales_unicas = len(df_verticales['VERTICAL'].unique())
    dominios_unicos = len(df_verticales['DOMINIO'].unique())
    casos_sin_vertical = df_verticales[df_verticales['VERTICAL'] == 'SIN_VERTICAL']['INCOMING'].sum()
    pct_sin_vertical = (casos_sin_vertical / total_incoming * 100) if total_incoming > 0 else 0
    
    print(f"[{site}] [INFO] Total incoming: {total_incoming:,}")
    print(f"[{site}] [INFO] Verticales únicas: {verticales_unicas}")
    print(f"[{site}] [INFO] Dominios únicos: {dominios_unicos}")
    print(f"[{site}] [INFO] Casos sin vertical: {casos_sin_vertical:,} ({pct_sin_vertical:.1f}%)")
    
    # Validación 1: Completitud
    assert len(df_verticales) > 0, "No se generaron agregados"
    print(f"[{site}] [OK] Check 1: Completitud")
    
    # Validación 2: Cobertura de verticales razonable
    if pct_sin_vertical > 10:
        print(f"[{site}] [WARNING] ⚠️ Más del 10% de casos sin vertical ({pct_sin_vertical:.1f}%)")
        print(f"[{site}] [WARNING] Verifica integridad de DM_CX_POST_PURCHASE")
    else:
        print(f"[{site}] [OK] Check 2: Cobertura de verticales ({pct_sin_vertical:.1f}% sin vertical)")
    
    # Validación 3: Verticales únicas razonable
    assert verticales_unicas >= 3, f"Muy pocas verticales ({verticales_unicas}), posible error"
    print(f"[{site}] [OK] Check 3: Verticales únicas ({verticales_unicas})")
    
    # Validación 4: Suma de % por commerce group = ~100%
    for cg in df_verticales['COMMERCE_GROUP'].unique():
        suma_pct = df_verticales[df_verticales['COMMERCE_GROUP'] == cg]['PCT_DEL_TOTAL'].sum()
        assert 99 < suma_pct < 101, f"{cg}: suma de % = {suma_pct:.1f}% (esperado ~100%)"
    print(f"[{site}] [OK] Check 4: Suma de porcentajes por CG = 100%")
    
    # Validación 5: No duplicados
    duplicados = df_verticales.duplicated(['SITE', 'PERIODO', 'COMMERCE_GROUP', 'VERTICAL', 'DOMINIO'])
    assert not duplicados.any(), f"Duplicados encontrados: {duplicados.sum()}"
    print(f"[{site}] [OK] Check 5: Sin duplicados")
    
    # Validación 6: Rango de valores
    assert (df_verticales['PCT_DEL_TOTAL'] >= 0).all() and (df_verticales['PCT_DEL_TOTAL'] <= 100).all(), \
        "Porcentajes fuera de rango"
    print(f"[{site}] [OK] Check 6: Rango de valores")
    
    print(f"[{site}] [OK] Todas las validaciones pasaron")
    
    # ========================================
    # PASO 4: Guardar output
    # ========================================
    
    print(f"[{site}] Paso 4: Guardando output...")
    
    # Crear carpeta si no existe
    output_dir = Path('metrics/verticales/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nombres de archivos
    output_file = output_dir / f'verticales_{site.lower()}_{periodo_str}.parquet'
    metadata_file = output_dir / f'metadata_{site.lower()}_{periodo_str}.json'
    
    # Guardar parquet
    df_verticales.to_parquet(output_file, index=False)
    print(f"[{site}] [OK] Parquet guardado: {output_file}")
    
    # Top 5 verticales para metadata
    top_verticales = []
    for cg in ['PDD', 'PNR']:
        df_cg = df_verticales[df_verticales['COMMERCE_GROUP'] == cg]
        if len(df_cg) > 0:
            top_cg = df_cg.groupby('VERTICAL')['INCOMING'].sum().sort_values(ascending=False).head(5)
            for vertical, incoming in top_cg.items():
                if vertical != 'SIN_VERTICAL':
                    pct = (incoming / df_cg['INCOMING'].sum() * 100)
                    top_verticales.append({
                        'commerce_group': cg,
                        'vertical': vertical,
                        'incoming': int(incoming),
                        'pct': round(pct, 1)
                    })
    
    # Guardar metadata
    metadata = {
        'site': site,
        'periodo': periodo,
        'commerce_groups': sorted(df_verticales['COMMERCE_GROUP'].unique().tolist()),
        'generated_at': datetime.now().isoformat(),
        'total_rows': int(len(df_verticales)),
        'total_incoming': int(total_incoming),
        'incoming_pdd': int(df_verticales[df_verticales['COMMERCE_GROUP'] == 'PDD']['INCOMING'].sum()),
        'incoming_pnr': int(df_verticales[df_verticales['COMMERCE_GROUP'] == 'PNR']['INCOMING'].sum()),
        'verticales_unicas': int(verticales_unicas),
        'dominios_unicos': int(dominios_unicos),
        'casos_sin_vertical': int(casos_sin_vertical),
        'pct_sin_vertical': round(pct_sin_vertical, 2),
        'top_verticales': top_verticales,
        'source_tables': [
            'meli-bi-data.WHOWNER.BT_CX_CONTACTS',
            'meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE'
        ],
        'filters_applied': [
            'FLAG_EXCLUDE_NUMERATOR_CR = 0',
            'PROCESS_BU_CR_REPORTING IN (ME, ML)',
            'SIT_SITE_ID NOT IN (MLV)',
            'PROCESS_PROBLEMATIC_REPORTING: PDD/PNR only'
        ],
        'valores_dinamicos': True,
        'verticales_hardcodeadas': False,
        'version': '1.0'
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[{site}] [OK] Metadata guardado: {metadata_file}")
    
    return df_verticales

# ========================================
# EJECUTAR PARA CADA SITE
# ========================================

print("\n" + "="*70)
print("INICIANDO GENERACIÓN DE MÉTRICAS")
print("="*70)

resultados_totales = []

for site in sites_to_process:
    try:
        df_result = generar_agregados_site(site, periodo_date, force=args.force)
        if df_result is not None:
            resultados_totales.append({'site': site, 'data': df_result})
    except Exception as e:
        print(f"[{site}] [ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

# ========================================
# RESUMEN FINAL
# ========================================

print("\n" + "="*70)
print("RESUMEN FINAL")
print("="*70)

if len(resultados_totales) > 0:
    for resultado in resultados_totales:
        site = resultado['site']
        df = resultado['data']
        
        print(f"\n[{site}]")
        print(f"  - Filas generadas: {len(df):,}")
        print(f"  - Incoming total: {df['INCOMING'].sum():,}")
        
        # Por commerce group
        for cg in sorted(df['COMMERCE_GROUP'].unique()):
            df_cg = df[df['COMMERCE_GROUP'] == cg]
            incoming_cg = df_cg['INCOMING'].sum()
            vert_count = len(df_cg['VERTICAL'].unique())
            print(f"  - {cg}: {incoming_cg:,} casos, {vert_count} verticales")
        
        # Top 3 verticales
        top3 = df.groupby('VERTICAL')['INCOMING'].sum().sort_values(ascending=False).head(3)
        print(f"  - Top 3 verticales:")
        for vertical, count in top3.items():
            if vertical != 'SIN_VERTICAL':
                pct = (count / df['INCOMING'].sum() * 100)
                print(f"    · {vertical}: {count:,} ({pct:.1f}%)")
    
    print(f"\n[OK] ✅ METRICAS GENERADAS EXITOSAMENTE")
    print(f"[UBICACION] metrics/verticales/data/")
    print(f"\n[INFO] Para usar en reportes:")
    print(f"       df = pd.read_parquet('metrics/verticales/data/verticales_{{site}}_{{periodo}}.parquet')")
else:
    print("\n[ERROR] ❌ NO SE GENERARON METRICAS")
    print("[INFO] Verifica los errores arriba para más detalles")

print("="*70)
