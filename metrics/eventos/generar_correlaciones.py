"""
Script Generador de Métricas - Correlación con Eventos Comerciales
Versión: 2.0
Fecha: Enero 2026

Propósito:
-----------
Pre-calcular correlaciones entre incoming de CR y eventos comerciales
basadas en fecha de orden (ORD_CLOSED_DT) sobre TODO el incoming,
no solo muestra.

Fuente de Eventos:
------------------
Los eventos comerciales y sus fechas se obtienen dinámicamente desde:
>>> meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT <<<

Esto garantiza que siempre usamos las fechas OFICIALES de inicio y fin
de cada evento comercial (Black Friday, Cyber Monday, etc.).

Output:
-------
- Parquet: metrics/eventos/data/correlacion_{site}_{periodo}.parquet
- Metadata: metrics/eventos/data/metadata_{site}_{periodo}.json

Uso:
----
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12
python metrics/eventos/generar_correlaciones.py --sites MLB,MLA --periodo 2025-12
"""

import argparse
import sys
from google.cloud.bigquery import Client
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# Agregar path del repositorio para imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
from config.site_groups import resolve_site_sql

print("[METRICS] Generador de Correlaciones con Eventos Comerciales v2.0")
print("[METRICS] Fuente de eventos: WHOWNER.LK_MKP_PROMOTIONS_EVENT")
print("="*70)

# ========================================
# FUNCIÓN: OBTENER EVENTOS DESDE TABLA OFICIAL
# ========================================

def obtener_eventos_comerciales(client, site, periodo):
    """
    Obtiene eventos comerciales desde la tabla oficial WHOWNER.LK_MKP_PROMOTIONS_EVENT
    
    Args:
        client: BigQuery client
        site: Site code (MLB, MLA, etc.)
        periodo: Período en formato YYYY-MM
    
    Returns:
        dict: Eventos con estructura {evento_key: {nombre, fecha_inicio, fecha_fin}}
    """
    print(f"[EVENTOS] Consultando tabla oficial WHOWNER.LK_MKP_PROMOTIONS_EVENT...")
    
    # Determinar rango de fechas del período para filtrar eventos relevantes
    periodo_inicio = f"{periodo}-01"
    periodo_fin = f"{periodo}-01"
    
    # Expandir rango para capturar eventos que puedan empezar antes del período
    # (ej: evento empieza en Nov pero afecta incoming de Dic)
    query_eventos = f"""
    SELECT DISTINCT
        SIT_SITE_ID as SITE,
        EVENT_NAME as NOMBRE_EVENTO,
        DATE(EVENT_START_DTTM) as FECHA_INICIO,
        DATE(EVENT_END_DTTM) as FECHA_FIN
    FROM `meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT`
    WHERE {resolve_site_sql(site, 'SIT_SITE_ID')}
        AND EVENT_START_DTTM >= DATE_SUB('{periodo_inicio}', INTERVAL 1 MONTH)
        AND EVENT_START_DTTM <= DATE_ADD('{periodo_fin}', INTERVAL 2 MONTH)
        AND EVENT_NAME IS NOT NULL
        AND EVENT_START_DTTM IS NOT NULL
        AND EVENT_END_DTTM IS NOT NULL
    ORDER BY FECHA_INICIO
    """
    
    try:
        df_eventos = client.query(query_eventos).to_dataframe()
        
        if len(df_eventos) == 0:
            print(f"[EVENTOS] [WARNING] No se encontraron eventos en tabla oficial para {site} periodo {periodo}")
            print(f"[EVENTOS] [INFO] Verifica que existan datos en WHOWNER.LK_MKP_PROMOTIONS_EVENT")
            return {}
        
        print(f"[EVENTOS] [OK] {len(df_eventos)} eventos encontrados desde tabla oficial")
        
        # Convertir a diccionario con estructura esperada
        eventos = {}
        for _, row in df_eventos.iterrows():
            evento_key = row['NOMBRE_EVENTO'].lower().replace(' ', '_').replace('-', '_')
            eventos[evento_key] = {
                'nombre': row['NOMBRE_EVENTO'],
                'fecha_inicio': row['FECHA_INICIO'].strftime('%Y-%m-%d'),
                'fecha_fin': row['FECHA_FIN'].strftime('%Y-%m-%d')
            }
            print(f"[EVENTOS]   - {row['NOMBRE_EVENTO']}: {row['FECHA_INICIO'].strftime('%Y-%m-%d')} a {row['FECHA_FIN'].strftime('%Y-%m-%d')}")
        
        return eventos
        
    except Exception as e:
        print(f"[EVENTOS] [ERROR] Error consultando tabla de eventos: {str(e)}")
        print(f"[EVENTOS] [INFO] Verifica permisos de acceso a WHOWNER.LK_MKP_PROMOTIONS_EVENT")
        return {}

# ========================================
# PARSEO DE ARGUMENTOS
# ========================================

parser = argparse.ArgumentParser(description='Generar correlaciones con eventos comerciales')
parser.add_argument('--site', type=str, help='Site code (MLB, MLA, etc.)')
parser.add_argument('--sites', type=str, help='Múltiples sites separados por coma (MLB,MLA,MCO)')
parser.add_argument('--periodo', type=str, required=True, help='Período en formato YYYY-MM (ej: 2025-12)')
parser.add_argument('--commerce-groups', type=str, help='Commerce groups específicos (ej: PDD,PNR)', default='ALL')

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

print(f"[CONFIG] Sites: {', '.join(sites_to_process)}")
print(f"[CONFIG] Período: {periodo}")
print(f"[CONFIG] Commerce Groups: {args.commerce_groups}")
print()

# ========================================
# INICIALIZAR BIGQUERY CLIENT
# ========================================

client = Client()

# ========================================
# FUNCIÓN: GENERAR CORRELACIONES PARA UN SITE
# ========================================

def generar_correlaciones_site(site, periodo_date):
    """
    Genera correlaciones para un site específico
    """
    print(f"\n[{site}] Procesando correlaciones para {periodo}...")
    
    # Obtener eventos desde tabla oficial
    eventos_site = obtener_eventos_comerciales(client, site, periodo)
    
    if not eventos_site or len(eventos_site) == 0:
        print(f"[{site}] [WARNING] No se encontraron eventos comerciales para este site y período.")
        print(f"[{site}] [INFO] Las métricas se generarán sin correlación de eventos (solo conteos).")
        return None
    
    # ========================================
    # PASO 1: Obtener TODO el incoming del período
    # ========================================
    print(f"[{site}] Paso 1: Obteniendo incoming completo...")
    
    # Filtros de commerce groups si se especificaron
    commerce_filter = ""
    if args.commerce_groups != 'ALL':
        commerce_groups_list = args.commerce_groups.split(',')
        commerce_conditions = []
        for cg in commerce_groups_list:
            if cg == 'PDD':
                commerce_conditions.append("C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'")
            elif cg == 'PNR':
                commerce_conditions.append("C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale'")
            # Agregar más commerce groups según necesidad
        
        if commerce_conditions:
            commerce_filter = f"AND ({' OR '.join(commerce_conditions)})"
    
    query_incoming = f"""
    WITH BASE_CONTACTS AS (
        SELECT
            C.CLA_CLAIM_ID,
            C.REASON_DETAIL_GROUP_REPORTING as TIPIFICACION,
            C.PROCESS_NAME as PROCESO,
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
            AND C.REASON_DETAIL_GROUP_REPORTING IS NOT NULL
            {commerce_filter}
    ),
    ORDERS_DATA AS (
        SELECT
            PP.CLA_CLAIM_ID,
            PP.ORD_CLOSED_DT as ORD_CLOSED_DATE
        FROM `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP
        WHERE PP.ORD_CLOSED_DT >= DATE_SUB('{periodo_date}', INTERVAL 1 MONTH)
            AND PP.ORD_CLOSED_DT < DATE_ADD('{periodo_date}', INTERVAL 2 MONTH)
    )
    SELECT 
        B.COMMERCE_GROUP,
        B.TIPIFICACION,
        B.PROCESO,
        B.PERIODO,
        O.ORD_CLOSED_DATE
    FROM BASE_CONTACTS B
    LEFT JOIN ORDERS_DATA O ON B.CLA_CLAIM_ID = O.CLA_CLAIM_ID
    """
    
    print(f"[{site}] Ejecutando query (puede tardar 2-3 min)...")
    df_incoming = client.query(query_incoming).to_dataframe()
    
    if len(df_incoming) == 0:
        print(f"[{site}] [WARNING] No se encontró incoming para este período")
        return None
    
    print(f"[{site}] [OK] {len(df_incoming):,} casos obtenidos")
    
    # Convertir fechas
    df_incoming['PERIODO'] = pd.to_datetime(df_incoming['PERIODO'])
    df_incoming['ORD_CLOSED_DATE'] = pd.to_datetime(df_incoming['ORD_CLOSED_DATE'], errors='coerce')
    
    casos_sin_fecha = df_incoming['ORD_CLOSED_DATE'].isna().sum()
    if casos_sin_fecha > 0:
        print(f"[{site}] [INFO] {casos_sin_fecha:,} casos sin ORD_CLOSED_DATE ({casos_sin_fecha/len(df_incoming)*100:.1f}%)")
    
    # ========================================
    # PASO 2: Calcular correlaciones por evento
    # ========================================
    print(f"[{site}] Paso 2: Calculando correlaciones...")
    
    resultados = []
    
    for evento_key, evento_info in eventos_site.items():
        fecha_inicio = pd.to_datetime(evento_info['fecha_inicio'])
        fecha_fin = pd.to_datetime(evento_info['fecha_fin'])
        
        # Casos que caen en el evento
        df_evento = df_incoming[
            (df_incoming['ORD_CLOSED_DATE'] >= fecha_inicio) & 
            (df_incoming['ORD_CLOSED_DATE'] <= fecha_fin)
        ]
        
        # Agrupar por commerce_group + tipificación
        for (commerce, tipif), group in df_incoming.groupby(['COMMERCE_GROUP', 'TIPIFICACION']):
            casos_totales = len(group)
            casos_en_evento = len(df_evento[
                (df_evento['COMMERCE_GROUP'] == commerce) & 
                (df_evento['TIPIFICACION'] == tipif)
            ])
            porcentaje = (casos_en_evento / casos_totales * 100) if casos_totales > 0 else 0
            
            resultados.append({
                'SITE': site,
                'PERIODO': pd.to_datetime(periodo_date),
                'COMMERCE_GROUP': commerce,
                'TIPIFICACION': tipif,
                'EVENTO': evento_info['nombre'],
                'FECHA_INICIO': fecha_inicio,
                'FECHA_FIN': fecha_fin,
                'CASOS': casos_en_evento,
                'CASOS_TOTALES': casos_totales,
                'PORCENTAJE': round(porcentaje, 2),
                'GENERADO': datetime.now()
            })
    
    df_correlaciones = pd.DataFrame(resultados)
    
    print(f"[{site}] [OK] {len(df_correlaciones)} correlaciones calculadas")
    
    # ========================================
    # PASO 3: Validar datos
    # ========================================
    print(f"[{site}] Paso 3: Validando datos...")
    
    # Check 1: Completitud
    assert len(df_correlaciones) > 0, "No se generaron correlaciones"
    
    # Check 2: Rango de valores
    assert df_correlaciones['PORCENTAJE'].between(0, 100).all(), "Porcentajes fuera de rango"
    
    # Check 3: Consistencia
    assert (df_correlaciones['CASOS'] <= df_correlaciones['CASOS_TOTALES']).all(), "Casos > Total"
    
    # Check 4: No duplicados
    assert not df_correlaciones.duplicated(['SITE', 'PERIODO', 'TIPIFICACION', 'EVENTO']).any(), "Duplicados encontrados"
    
    print(f"[{site}] [OK] Validacion completada")
    
    # ========================================
    # PASO 4: Guardar output
    # ========================================
    print(f"[{site}] Paso 4: Guardando output...")
    
    # Crear carpeta si no existe
    output_dir = Path('metrics/eventos/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nombre de archivo
    periodo_str = periodo.replace('-', '_')
    output_file = output_dir / f'correlacion_{site.lower()}_{periodo_str}.parquet'
    
    # Guardar parquet
    df_correlaciones.to_parquet(output_file, index=False)
    print(f"[{site}] [OK] Parquet guardado: {output_file}")
    
    # Guardar metadata
    # Preparar detalles de eventos para metadata
    eventos_detalle = []
    for evento_key, evento_info in eventos_site.items():
        eventos_detalle.append({
            'nombre': evento_info['nombre'],
            'fecha_inicio': evento_info['fecha_inicio'],
            'fecha_fin': evento_info['fecha_fin'],
            'duracion_dias': (pd.to_datetime(evento_info['fecha_fin']) - pd.to_datetime(evento_info['fecha_inicio'])).days + 1
        })
    
    metadata = {
        'site': site,
        'periodo': periodo,
        'generated_at': datetime.now().isoformat(),
        'total_rows': int(len(df_correlaciones)),
        'total_incoming': int(len(df_incoming)),
        'total_casos_correlacionados': int(df_correlaciones['CASOS'].sum()),
        'porcentaje_correlacionado_global': float(round(df_correlaciones['CASOS'].sum() / len(df_incoming) * 100, 2)),
        'eventos_incluidos': list(df_correlaciones['EVENTO'].unique()),
        'eventos_detalle': eventos_detalle,
        'commerce_groups': list(df_correlaciones['COMMERCE_GROUP'].unique()),
        'tipificaciones_unicas': int(len(df_correlaciones['TIPIFICACION'].unique())),
        'casos_sin_fecha_orden': int(casos_sin_fecha),
        'porcentaje_sin_fecha': float(round(casos_sin_fecha / len(df_incoming) * 100, 2)),
        'source_tables': [
            'meli-bi-data.WHOWNER.BT_CX_CONTACTS',
            'meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE',
            'meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT'
        ],
        'eventos_source': 'WHOWNER.LK_MKP_PROMOTIONS_EVENT',
        'eventos_dinamicos': True,
        'version': '2.0'
    }
    
    metadata_file = output_dir / f'metadata_{site.lower()}_{periodo_str}.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[{site}] [OK] Metadata guardado: {metadata_file}")
    
    return df_correlaciones

# ========================================
# EJECUTAR PARA CADA SITE
# ========================================

print("\n" + "="*70)
print("INICIANDO GENERACIÓN DE MÉTRICAS")
print("="*70)

resultados_totales = []

for site in sites_to_process:
    try:
        df_result = generar_correlaciones_site(site, periodo_date)
        if df_result is not None:
            resultados_totales.append(df_result)
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
    for i, df in enumerate(resultados_totales):
        site = sites_to_process[i]
        print(f"\n[{site}]")
        print(f"  - Correlaciones: {len(df):,}")
        print(f"  - Incoming total: {df['CASOS_TOTALES'].sum():,}")
        print(f"  - Casos correlacionados: {df['CASOS'].sum():,}")
        print(f"  - % correlacionado: {df['CASOS'].sum() / df['CASOS_TOTALES'].sum() * 100:.1f}%")
        print(f"  - Commerce Groups: {', '.join(df['COMMERCE_GROUP'].unique())}")
        print(f"  - Tipificaciones: {len(df['TIPIFICACION'].unique())}")
    
    print(f"\n[OK] METRICAS GENERADAS EXITOSAMENTE")
    print(f"[UBICACION] metrics/eventos/data/")
else:
    print("\n[ERROR] NO SE GENERARON METRICAS")

print("="*70)
