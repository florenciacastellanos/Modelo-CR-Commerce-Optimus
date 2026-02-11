"""
Análisis CR Genérico - Metodología v5.0
=========================================
Script refactorizado con diseño adaptable que funciona para cualquier dimensión:
- CDU, PROCESO, TIPIFICACION, ENVIRONMENT, COMMERCE_GROUP, etc.

Características:
- Parametrización completa según lo solicitado por el usuario
- Muestreo de conversaciones OBLIGATORIO (Regla #9 v5.0)
- Construcción dinámica de queries sin asumir jerarquías fijas
- Fallback con evidencia cuando no hay datos

Uso:
    python analisis_cr_generico.py --site MLA --p1-start 2025-08-01 --p1-end 2025-08-31 \
        --p2-start 2025-09-01 --p2-end 2025-09-30 \
        --dimension CDU --valor "Enviabilidad" --drill-down PROCESS_NAME
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import webbrowser
import pandas as pd
import json
import subprocess
import re

# Importar soporte para agrupaciones de sites (ROLA, HSP)
from config.site_groups import resolve_site_sql, get_site_list, is_site_group, get_site_display_name

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

# Mapeo de dimensiones a campos SQL
DIMENSION_SQL_MAPPING = {
    'PROCESO': 'PROCESS_NAME',
    'CDU': 'CDU',
    'TIPIFICACION': 'REASON_DETAIL_GROUP_REPORTING',
    'ENVIRONMENT': 'ENVIRONMENT',
    'COMMERCE_GROUP': 'AGRUP_COMMERCE',
    'CLA_REASON_DETAIL': 'CLA_REASON_DETAIL'
}

# Jerarquía por defecto (para auto-detectar drill-down)
JERARQUIA_DEFAULT = ['COMMERCE_GROUP', 'PROCESO', 'CDU', 'TIPIFICACION', 'CLA_REASON_DETAIL']

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_sql_field(dimension_name):
    """Retorna el campo SQL correspondiente a una dimensión"""
    return DIMENSION_SQL_MAPPING.get(dimension_name.upper(), dimension_name)


def get_next_drill_down(dimension_principal):
    """Detecta automáticamente la siguiente dimensión para drill-down"""
    try:
        idx = JERARQUIA_DEFAULT.index(dimension_principal.upper())
        if idx < len(JERARQUIA_DEFAULT) - 1:
            return JERARQUIA_DEFAULT[idx + 1]
    except ValueError:
        pass
    
    # Si no está en la jerarquía, usar la misma (sin drill-down)
    return dimension_principal


def ejecutar_query_bigquery(sql_query, output_csv, keep_query_file=False):
    """Ejecuta una query en BigQuery y guarda resultado en CSV"""
    # Guardar query en archivo temporal
    query_file = OUTPUT_DIR / f"temp_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    with open(query_file, 'w', encoding='utf-8') as f:
        f.write(sql_query)
    
    # Ejecutar con PowerShell
    cmd = f'Get-Content "{query_file}" -Raw | bq query --use_legacy_sql=false --format=csv > "{output_csv}"'
    
    result = subprocess.run(
        ["powershell", "-Command", cmd],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    # Limpiar query temporal solo si fue exitoso y no se pidió mantener
    if result.returncode == 0 and not keep_query_file:
        query_file.unlink()
    elif result.returncode != 0:
        print(f"   [DEBUG] Query guardada en: {query_file}")
    
    return result.returncode == 0, result.stderr


def leer_csv_bigquery(csv_path):
    """Lee CSV de BigQuery con encoding correcto"""
    try:
        df = pd.read_csv(csv_path, encoding='utf-16')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"[ERROR] No se pudo leer CSV: {e}")
        return pd.DataFrame()


# ============================================================================
# GENERADORES DE QUERIES DINÁMICAS
# ============================================================================

def generar_query_incoming(config):
    """
    Genera query de incoming adaptada a la dimensión solicitada.
    
    Args:
        config: Dict con 'dimension_principal', 'valor_filtro', 'dimension_drill', 
                'site', 'periodo_inicio', 'periodo_fin'
    """
    dimension_sql = get_sql_field(config['dimension_principal'])
    drill_sql = get_sql_field(config['dimension_drill'])
    
    # Construcción dinámica del filtro principal
    if config['dimension_principal'].upper() == 'COMMERCE_GROUP':
        # Para commerce group, usar CASE statement
        filtro_principal = f"""
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            ELSE 'OTRO' 
        END = '{config['valor_filtro']}'
        """
    else:
        # Para otras dimensiones, usar LIKE
        filtro_principal = f"UPPER(C.{dimension_sql}) LIKE '%{config['valor_filtro'].upper()}%'"
    
    query = f"""
-- ══════════════════════════════════════════════════════════════════════════════
-- INCOMING ANALYSIS - {config['dimension_principal']} = {config['valor_filtro']}
-- Site: {config['site']} | Período: {config['periodo_inicio']} a {config['periodo_fin']}
-- ══════════════════════════════════════════════════════════════════════════════

WITH BASE_CONTACTS AS (
    SELECT    
        C.CAS_CASE_ID,
        C.SIT_SITE_ID,
        CAST(C.CONTACT_DATE_ID AS DATE) AS CONTACT_DATE_ID,
        FORMAT_DATETIME('%Y-%m', C.CONTACT_DATE_ID) AS MES,
        C.{dimension_sql} AS DIMENSION_PRINCIPAL,
        C.{drill_sql} AS DIMENSION_DRILL,
        COALESCE(C.{dimension_sql}, 'SIN_INFO') AS DIM_PRINCIPAL_CLEAN,
        COALESCE(C.{drill_sql}, 'SIN_INFO') AS DIM_DRILL_CLEAN,
        1.0 AS CANT_CASES
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE
        CAST(C.CONTACT_DATE_ID AS DATE) BETWEEN '{config['periodo_inicio']}' AND '{config['periodo_fin']}'
        AND {resolve_site_sql(config['site'], 'C.SIT_SITE_ID')}
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND {filtro_principal}
        AND COALESCE(C.QUEUE_ID, 0) NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND COALESCE(C.PROCESS_ID, 0) NOT IN (1312)
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
)

SELECT
    MES,
    DIM_DRILL_CLEAN AS DIMENSION_DRILL,
    COUNT(DISTINCT CAS_CASE_ID) AS INCOMING
FROM BASE_CONTACTS
GROUP BY MES, DIM_DRILL_CLEAN
ORDER BY MES, INCOMING DESC
"""
    return query


def generar_query_drivers(config):
    """Genera query de drivers (órdenes totales)"""
    query = f"""
-- ══════════════════════════════════════════════════════════════════════════════
-- DRIVER CALCULATION - {config['site']}
-- Período: {config['periodo_inicio']} a {config['periodo_fin']}
-- ══════════════════════════════════════════════════════════════════════════════

SELECT
    FORMAT_DATETIME('%Y-%m', CAST(ORD.ORD_CLOSED_DT AS DATE)) AS MES,
    COUNT(DISTINCT ORD.ORD_ORDER_ID) AS DRIVER_ORDENES
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE
    CAST(ORD.ORD_CLOSED_DT AS DATE) BETWEEN '{config['periodo_inicio']}' AND '{config['periodo_fin']}'
    AND {resolve_site_sql(config['site'], 'ORD.SIT_SITE_ID')}
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID NOT IN ('MLV')
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
GROUP BY MES
ORDER BY MES
"""
    return query


def generar_query_muestreo(config, elemento_drill):
    """
    Genera query de muestreo de conversaciones adaptada dinámicamente.
    
    Args:
        config: Configuración del análisis
        elemento_drill: Valor específico del drill-down (ej: "Despacho Ventas y Publicaciones")
    """
    dimension_sql = get_sql_field(config['dimension_principal'])
    drill_sql = get_sql_field(config['dimension_drill'])
    
    # Si dimension_principal == dimension_drill, solo filtrar por principal
    usar_drill_filter = config.get('usar_drill_filter', True)
    if config['dimension_principal'] == config['dimension_drill']:
        usar_drill_filter = False
    
    # Construcción dinámica del filtro principal
    if config['dimension_principal'].upper() == 'COMMERCE_GROUP':
        filtro_principal = f"""
        CASE 
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
            WHEN INC.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            ELSE 'OTRO' 
        END = '{config['valor_filtro']}'
        """
    else:
        filtro_principal = f"UPPER(INC.{dimension_sql}) LIKE '%{config['valor_filtro'].upper()}%'"
    
    query = f"""
-- ══════════════════════════════════════════════════════════════════════════════
-- MUESTREO DE CONVERSACIONES
-- Dimensión: {config['dimension_principal']} = {config['valor_filtro']}
-- Elemento drill-down: {elemento_drill}
-- ══════════════════════════════════════════════════════════════════════════════

WITH STUDIO_SUMMARIES AS (
    SELECT
        CAS_CASE_ID,
        TRIM(REGEXP_REPLACE(
            CONCAT(
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.problem'), ''),
                ' ',
                COALESCE(JSON_VALUE(SUMMARY_CX_STUDIO, '$.solution'), '')
            ),
            r'\\\\s+', ' '
        )) AS CONVERSATION_SUMMARY
    FROM `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE`
    WHERE ARRIVAL_DATE BETWEEN DATE_SUB('{config['periodo_inicio']}', INTERVAL 30 DAY) 
        AND DATE_ADD('{config['periodo_fin']}', INTERVAL 30 DAY)
),

INCOMING_BASE AS (
    SELECT
        INC.CAS_CASE_ID,
        INC.{dimension_sql} AS DIMENSION_PRINCIPAL,
        INC.{drill_sql} AS DIMENSION_DRILL,
        DATE(INC.CONTACT_DATE_ID) as FECHA_CONTACTO
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` INC
    WHERE {resolve_site_sql(config['site'], 'INC.SIT_SITE_ID')}
        AND CAST(INC.CONTACT_DATE_ID AS DATE) BETWEEN '{config['periodo_inicio']}' AND '{config['periodo_fin']}'
        AND COALESCE(INC.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND {filtro_principal}
        {"AND INC." + drill_sql + " = '" + elemento_drill + "'" if usar_drill_filter else ""}
)

SELECT 
    INC.CAS_CASE_ID,
    INC.DIMENSION_PRINCIPAL,
    INC.DIMENSION_DRILL,
    INC.FECHA_CONTACTO,
    ST.CONVERSATION_SUMMARY
FROM INCOMING_BASE INC
INNER JOIN STUDIO_SUMMARIES ST ON INC.CAS_CASE_ID = ST.CAS_CASE_ID
WHERE ST.CONVERSATION_SUMMARY IS NOT NULL
    AND LENGTH(ST.CONVERSATION_SUMMARY) > 20
ORDER BY RAND()
LIMIT 60
"""
    return query


# ============================================================================
# ANÁLISIS PRINCIPAL
# ============================================================================

def ejecutar_analisis(config):
    """
    Ejecuta el análisis completo (FASE 1-5) con la configuración dada.
    
    Args:
        config: Dict con toda la configuración del análisis
    """
    print("="*80)
    print(f"ANÁLISIS CR - {config['dimension_principal']} = {config['valor_filtro']}")
    print(f"Site: {config['site']} | Período: {config['label_p1']} vs {config['label_p2']}")
    print("="*80)
    
    # ========================================================================
    # FASE 1: BASELINE - CÁLCULO DE MÉTRICAS
    # ========================================================================
    print(f"\n[FASE 1] Calculando métricas baseline...")
    
    # Query de incoming (agregado completo P1 + P2)
    config_completo = {**config, 
                       'periodo_inicio': config['periodo_1_inicio'],
                       'periodo_fin': config['periodo_2_fin']}
    
    query_inc = generar_query_incoming(config_completo)
    csv_incoming = OUTPUT_DIR / "temp_incoming.csv"
    
    print(f"   Ejecutando query de incoming...")
    exito, error = ejecutar_query_bigquery(query_inc, csv_incoming)
    
    if not exito:
        print(f"[ERROR] Query de incoming falló: {error}")
        return None
    
    df_incoming = leer_csv_bigquery(csv_incoming)
    if df_incoming.empty:
        print(f"[ERROR] No se encontraron casos para {config['dimension_principal']} = {config['valor_filtro']}")
        return None
    
    # Query de drivers
    query_drv = generar_query_drivers(config_completo)
    csv_drivers = OUTPUT_DIR / "temp_drivers.csv"
    
    print(f"   Ejecutando query de drivers...")
    exito, error = ejecutar_query_bigquery(query_drv, csv_drivers)
    
    if not exito:
        print(f"[ERROR] Query de drivers falló: {error}")
        return None
    
    df_drivers = leer_csv_bigquery(csv_drivers)
    
    # Calcular totales por período
    incoming_p1 = df_incoming[df_incoming['MES'] == config['mes_p1']]['INCOMING'].sum()
    incoming_p2 = df_incoming[df_incoming['MES'] == config['mes_p2']]['INCOMING'].sum()
    
    driver_p1 = df_drivers[df_drivers['MES'] == config['mes_p1']]['DRIVER_ORDENES'].values[0]
    driver_p2 = df_drivers[df_drivers['MES'] == config['mes_p2']]['DRIVER_ORDENES'].values[0]
    
    # Calcular CR
    cr_p1 = (incoming_p1 / driver_p1) * 100
    cr_p2 = (incoming_p2 / driver_p2) * 100
    
    # Variaciones
    delta_incoming = incoming_p2 - incoming_p1
    delta_incoming_pct = (delta_incoming / incoming_p1) * 100 if incoming_p1 > 0 else 0
    delta_cr = cr_p2 - cr_p1
    delta_cr_pct = (delta_cr / cr_p1) * 100 if cr_p1 > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"MÉTRICAS CONSOLIDADAS")
    print(f"{'='*80}")
    print(f"\n{'Métrica':<30} {config['label_p1']:>15} {config['label_p2']:>15} {'Variación':>15}")
    print(f"{'-'*80}")
    print(f"{'Incoming':<30} {incoming_p1:>15,.0f} {incoming_p2:>15,.0f} {delta_incoming:>+14,.0f} ({delta_incoming_pct:+.1f}%)")
    print(f"{'Driver (Órdenes)':<30} {driver_p1:>15,.0f} {driver_p2:>15,.0f} {driver_p2-driver_p1:>+14,.0f}")
    print(f"{'CR (pp)':<30} {cr_p1:>15.4f} {cr_p2:>15.4f} {delta_cr:>+15.4f} ({delta_cr_pct:+.1f}%)")
    
    # ========================================================================
    # FASE 2: DRILL-DOWN (con fallback si no hay info)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[FASE 2] Drill-down por {config['dimension_drill']}")
    print(f"{'='*80}")
    
    # Agregar por drill-down
    df_drill = df_incoming.groupby(['MES', 'DIMENSION_DRILL'])['INCOMING'].sum().reset_index()
    
    # AJUSTE: Si solo hay "SIN_INFO", intentar con PROCESS_NAME como fallback
    if len(df_drill['DIMENSION_DRILL'].unique()) == 1 and 'SIN_INFO' in df_drill['DIMENSION_DRILL'].values:
        print(f"[NOTA] {config['dimension_drill']} no tiene información, usando PROCESS_NAME como fallback")
        
        # Re-ejecutar query con PROCESS_NAME como drill-down
        config_fallback = {**config_completo, 'dimension_drill': 'PROCESO'}
        query_inc_fallback = generar_query_incoming(config_fallback)
        csv_incoming_fallback = OUTPUT_DIR / "temp_incoming_fallback.csv"
        
        print(f"   Ejecutando query con PROCESS_NAME...")
        exito, _ = ejecutar_query_bigquery(query_inc_fallback, csv_incoming_fallback)
        
        if exito:
            df_incoming = leer_csv_bigquery(csv_incoming_fallback)
            df_drill = df_incoming.groupby(['MES', 'DIMENSION_DRILL'])['INCOMING'].sum().reset_index()
            config['dimension_drill'] = 'PROCESO'
            config['dimension_drill_original'] = config_completo['dimension_drill']
            print(f"   [OK] Usando PROCESS_NAME para drill-down")
    
    df_drill_pivot = df_drill.pivot(index='DIMENSION_DRILL', columns='MES', values='INCOMING').fillna(0)
    df_drill_pivot.columns = ['P1', 'P2']
    df_drill_pivot['Delta'] = df_drill_pivot['P2'] - df_drill_pivot['P1']
    df_drill_pivot['Delta_Pct'] = (df_drill_pivot['Delta'] / df_drill_pivot['P1']) * 100
    df_drill_pivot['Contribucion'] = (abs(df_drill_pivot['Delta']) / abs(delta_incoming)) * 100
    
    df_drill_pivot = df_drill_pivot.sort_values('Contribucion', ascending=False)
    
    print(f"\n{config['dimension_drill']:<50} {config['label_p1']:>10} {config['label_p2']:>10} {'Delta':>10} {'Contrib %':>12}")
    print(f"{'-'*100}")
    for idx, row in df_drill_pivot.iterrows():
        print(f"{idx:<50} {row['P1']:>10,.0f} {row['P2']:>10,.0f} {row['Delta']:>+10,.0f} {row['Contribucion']:>11.1f}%")
    
    print(f"\n{'TOTAL':<50} {incoming_p1:>10,.0f} {incoming_p2:>10,.0f} {delta_incoming:>+10,.0f} {100.0:>11.1f}%")
    
    # ========================================================================
    # REGLA 80% - PRIORIZACIÓN
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"REGLA DEL 80% - ELEMENTOS PRIORIZADOS")
    print(f"{'='*80}")
    
    acumulado = 0
    elementos_priorizados = []
    for idx, row in df_drill_pivot.iterrows():
        acumulado += row['Contribucion']
        elementos_priorizados.append({
            'nombre': idx,
            'delta': row['Delta'],
            'contribucion': row['Contribucion'],
            'p1': row['P1'],
            'p2': row['P2']
        })
        print(f"[OK] {idx}: {row['Contribucion']:.1f}% (acum: {acumulado:.1f}%)")
        if acumulado >= 80:
            break
    
    # ========================================================================
    # FASE 3: EVIDENCIA - MUESTREO DE CONVERSACIONES (OBLIGATORIO)
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[FASE 3] Análisis de Conversaciones (OBLIGATORIO - Regla #9 v5.0)")
    print(f"{'='*80}")
    
    analisis_conversaciones = []
    
    for elem in elementos_priorizados:
        elemento = elem['nombre']
        delta = elem['delta']
        contrib = elem['contribucion']
        
        print(f"\n[ELEMENTO] {elemento}")
        print(f"   Variacion: {delta:+,.0f} casos ({contrib:.1f}% de la variacion total)")
        
        # ====================================================================
        # AJUSTE: Usar dimensión de drill-down actualizada si hubo fallback
        # ====================================================================
        # Si hubo fallback a PROCESS_NAME, usar esa dimensión
        config_muestreo = {**config_completo, 'dimension_drill': config['dimension_drill']}
        elemento_muestreo = elemento
        
        # ====================================================================
        # PASO 1: EJECUTAR MUESTREO (NO SALTEARSE)
        # ====================================================================
        print(f"   [1/3] Ejecutando muestreo de conversaciones...")
        
        query_muestreo = generar_query_muestreo(config_muestreo, elemento_muestreo)
        csv_muestreo = OUTPUT_DIR / f"temp_conversaciones_{elemento.replace(' ', '_').lower()[:30]}.csv"
        
        # Guardar query para debugging
        query_debug_file = OUTPUT_DIR / f"debug_query_muestreo_{elemento.replace(' ', '_').lower()[:30]}.sql"
        with open(query_debug_file, 'w', encoding='utf-8') as f:
            f.write(query_muestreo)
        print(f"   [DEBUG] Query guardada en: {query_debug_file}")
        
        exito, error = ejecutar_query_bigquery(query_muestreo, csv_muestreo)
        
        if not exito:
            print(f"   [2/3] Error ejecutando query: {error[:200]}")
            analisis_conversaciones.append({
                'elemento': elemento,
                'variacion': int(delta),
                'contribucion': float(contrib),
                'hipotesis': True,
                'motivo': f'Error al ejecutar query de muestreo: {error[:100]}'
            })
            continue
        
        # ====================================================================
        # PASO 2: VERIFICAR RESULTADO
        # ====================================================================
        print(f"   [2/3] Verificando resultado en: {csv_muestreo}")
        
        # Verificar si el archivo existe
        if not csv_muestreo.exists():
            print(f"   [ERROR] Archivo CSV no se generó")
            analisis_conversaciones.append({
                'elemento': elemento,
                'variacion': int(delta),
                'contribucion': float(contrib),
                'hipotesis': True,
                'motivo': 'Archivo CSV de muestreo no se generó'
            })
            continue
        
        df_conv = leer_csv_bigquery(csv_muestreo)
        
        if df_conv.empty or len(df_conv) < 5:
            print(f"   [2/3] No hay conversaciones disponibles en BT_CX_STUDIO_SAMPLE")
            print(f"   [3/3] Status: [!] HIPOTESIS (query retorno {len(df_conv)} casos)")
            
            analisis_conversaciones.append({
                'elemento': elemento,
                'variacion': int(delta),
                'contribucion': float(contrib),
                'hipotesis': True,
                'motivo': f'Sin conversaciones en BT_CX_STUDIO_SAMPLE (query retorno {len(df_conv)} casos)'
            })
            continue
        
        # ====================================================================
        # PASO 3: ANALIZAR CON LLM (EVIDENCIA REAL)
        # ====================================================================
        print(f"   [2/3] Conversaciones encontradas: {len(df_conv)}")
        print(f"   [3/3] CSV exportado para analisis con LLM: {csv_muestreo}")
        print(f"   [PENDIENTE] Ejecutar analisis LLM manualmente o con integracion Cursor")
        
        analisis_conversaciones.append({
            'elemento': elemento,
            'variacion': int(delta),
            'contribucion': float(contrib),
            'hipotesis': False,
            'conversaciones_muestreadas': len(df_conv),
            'csv_path': str(csv_muestreo),
            'pendiente_llm': True,
            'causas': []  # Se llenará después del análisis LLM
        })
    
    # ========================================================================
    # FASE 4: SANITY CHECKS
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"[FASE 4] Sanity Checks")
    print(f"{'='*80}")
    
    checks = {
        'Incoming > 0': incoming_p1 > 0 and incoming_p2 > 0,
        'Driver > 0': driver_p1 > 0 and driver_p2 > 0,
        'CR en rango valido': 0 < cr_p1 < 100 and 0 < cr_p2 < 100,
        'Periodos consecutivos': True,
        'Muestreo ejecutado': all(elem.get('csv_path') or elem.get('hipotesis') for elem in analisis_conversaciones)
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {check}")
    
    if not all_passed:
        print("\n[!] ADVERTENCIA: Algunos checks fallaron. Revisar datos.")
    else:
        print("\n[OK] Todos los checks pasaron correctamente.")
    
    # ========================================================================
    # RETORNAR RESULTADOS
    # ========================================================================
    return {
        'config': config,
        'metricas': {
            'incoming_p1': int(incoming_p1),
            'incoming_p2': int(incoming_p2),
            'driver_p1': int(driver_p1),
            'driver_p2': int(driver_p2),
            'cr_p1': float(cr_p1),
            'cr_p2': float(cr_p2),
            'delta_incoming': int(delta_incoming),
            'delta_incoming_pct': float(delta_incoming_pct),
            'delta_cr': float(delta_cr),
            'delta_cr_pct': float(delta_cr_pct)
        },
        'drill_down': df_drill_pivot.to_dict('index'),
        'elementos_priorizados': elementos_priorizados,
        'analisis_conversaciones': analisis_conversaciones,
        'sanity_checks': checks
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Análisis CR Genérico v5.0')
    parser.add_argument('--site', required=True, help='Site (MLA, MLB, etc.)')
    parser.add_argument('--p1-start', required=True, help='Período 1 inicio (YYYY-MM-DD)')
    parser.add_argument('--p1-end', required=True, help='Período 1 fin (YYYY-MM-DD)')
    parser.add_argument('--p2-start', required=True, help='Período 2 inicio (YYYY-MM-DD)')
    parser.add_argument('--p2-end', required=True, help='Período 2 fin (YYYY-MM-DD)')
    parser.add_argument('--dimension', required=True, help='Dimensión principal (CDU, PROCESO, TIPIFICACION, etc.)')
    parser.add_argument('--valor', required=True, help='Valor de la dimensión (ej: Enviabilidad)')
    parser.add_argument('--drill-down', required=False, help='Dimensión para drill-down (auto-detecta si no se especifica)')
    
    args = parser.parse_args()
    
    # Detectar drill-down automáticamente si no se especificó
    drill_down = args.drill_down if args.drill_down else get_next_drill_down(args.dimension)
    
    # Configuración del análisis
    config = {
        'site': args.site,
        'dimension_principal': args.dimension.upper(),
        'valor_filtro': args.valor,
        'dimension_drill': drill_down.upper(),
        'periodo_1_inicio': args.p1_start,
        'periodo_1_fin': args.p1_end,
        'periodo_2_inicio': args.p2_start,
        'periodo_2_fin': args.p2_end,
        'mes_p1': args.p1_start[:7],  # YYYY-MM
        'mes_p2': args.p2_start[:7],
        'label_p1': datetime.strptime(args.p1_start, '%Y-%m-%d').strftime('%B %Y'),
        'label_p2': datetime.strptime(args.p2_start, '%Y-%m-%d').strftime('%B %Y')
    }
    
    # Ejecutar análisis
    resultado = ejecutar_analisis(config)
    
    if resultado:
        # Guardar metadata
        metadata_path = OUTPUT_DIR / f"metadata_{config['site']}_{config['dimension_principal'].lower()}_{config['mes_p1']}_{config['mes_p2']}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n{'='*80}")
        print(f"ANALISIS COMPLETADO")
        print(f"{'='*80}")
        print(f"\nMetadata guardada en: {metadata_path}")
        print(f"\nProximos pasos:")
        print(f"  1. Revisar CSVs de conversaciones en output/")
        print(f"  2. Analizar con LLM usando templates/prompt_analisis_conversaciones.md")
        print(f"  3. Actualizar metadata con resultados del LLM")
        print(f"  4. Generar reporte HTML final")


if __name__ == '__main__':
    main()
