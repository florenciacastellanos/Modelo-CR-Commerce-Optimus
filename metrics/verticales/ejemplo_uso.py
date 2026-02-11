"""
Ejemplos de Uso - Métricas de Verticales y Dominios
====================================================

Este archivo contiene ejemplos de cómo usar las métricas pre-calculadas
de verticales y dominios en análisis de Contact Rate.

Versión: 1.0
Fecha: Enero 2026
Status: ✅ ACTIVO (script generador implementado)

⚠️ IMPORTANTE - Valores Dinámicos:
Los ejemplos en este código NO asumen verticales específicas.
Las verticales y dominios se obtienen DINÁMICAMENTE de BigQuery
sin hardcodeo, filtros ni sesgos.

Referencias:
- README.md: Documentación completa
- FUENTE_VERTICALES.md: Contexto de negocio
- ../INTEGRACION_GOLDEN_TEMPLATES.md: Integración en reportes
"""

import pandas as pd
from pathlib import Path
import json

# =============================================================================
# EJEMPLO 1: Cargar métricas y detectar variaciones
# =============================================================================

def ejemplo_1_detectar_variaciones():
    """
    Cargar métricas de dos períodos y detectar verticales con variaciones >10%
    """
    print("\n" + "="*80)
    print("EJEMPLO 1: Detectar variaciones en verticales")
    print("="*80)
    
    # Configuración
    site = 'MLA'
    periodo_p1 = '2025_11'
    periodo_p2 = '2025_12'
    commerce_group = 'PDD'
    
    # Paths
    metrics_path = Path('metrics/verticales/data')
    file_p1 = metrics_path / f'verticales_{site}_{periodo_p1}.parquet'
    file_p2 = metrics_path / f'verticales_{site}_{periodo_p2}.parquet'
    
    # Verificar existencia
    if not file_p1.exists() or not file_p2.exists():
        print(f"[WARNING] Métricas no encontradas")
        print(f"[INFO] Generar con: python metrics/verticales/generar_agregados.py --site {site} --periodo 2025-11")
        return
    
    # Leer métricas
    df_p1 = pd.read_parquet(file_p1)
    df_p2 = pd.read_parquet(file_p2)
    
    # Filtrar por commerce group
    df_p1_filtered = df_p1[df_p1['COMMERCE_GROUP'] == commerce_group]
    df_p2_filtered = df_p2[df_p2['COMMERCE_GROUP'] == commerce_group]
    
    # Agregar por vertical (sumar dominios)
    # ⚠️ IMPORTANTE: No filtramos verticales específicas, usamos TODAS las que existan
    vert_p1 = df_p1_filtered.groupby('VERTICAL')['INCOMING'].sum().reset_index()
    vert_p2 = df_p2_filtered.groupby('VERTICAL')['INCOMING'].sum().reset_index()
    
    # Comparar
    df_comp = vert_p1.merge(vert_p2, on='VERTICAL', suffixes=('_P1', '_P2'))
    df_comp['VARIACION_ABS'] = df_comp['INCOMING_P2'] - df_comp['INCOMING_P1']
    df_comp['VARIACION_PCT'] = (df_comp['VARIACION_ABS'] / df_comp['INCOMING_P1']) * 100
    
    # Detectar anomalías (>10% o >100 casos)
    anomalias = df_comp[
        (abs(df_comp['VARIACION_PCT']) > 10) | 
        (abs(df_comp['VARIACION_ABS']) > 100)
    ].sort_values('VARIACION_ABS', ascending=False)
    
    # Mostrar resultados
    print(f"\nAnálisis: {commerce_group} {site} - {periodo_p1} vs {periodo_p2}")
    print(f"Total verticales analizadas: {len(df_comp)}")
    print(f"Verticales con variación significativa: {len(anomalias)}")
    print("\nTop 5 variaciones:")
    print(anomalias[['VERTICAL', 'INCOMING_P1', 'INCOMING_P2', 'VARIACION_ABS', 'VARIACION_PCT']].head())


# =============================================================================
# EJEMPLO 2: Deep dive en una vertical específica (análisis de dominios)
# =============================================================================

def ejemplo_2_analisis_dominios():
    """
    Profundizar en una vertical específica analizando sus dominios
    """
    print("\n" + "="*80)
    print("EJEMPLO 2: Análisis de dominios dentro de una vertical")
    print("="*80)
    
    # Configuración
    site = 'MLA'
    periodo_p1 = '2025_11'
    periodo_p2 = '2025_12'
    # ⚠️ NOTA: 'ELECTRONICS' es solo un ejemplo para el código
    # En producción, el usuario selecciona de las verticales REALES que existan en el parquet
    vertical_seleccionada = 'ELECTRONICS'
    
    # Leer métricas
    metrics_path = Path('metrics/verticales/data')
    df_p1 = pd.read_parquet(metrics_path / f'verticales_{site}_{periodo_p1}.parquet')
    df_p2 = pd.read_parquet(metrics_path / f'verticales_{site}_{periodo_p2}.parquet')
    
    # Filtrar por vertical
    vert_p1 = df_p1[df_p1['VERTICAL'] == vertical_seleccionada]
    vert_p2 = df_p2[df_p2['VERTICAL'] == vertical_seleccionada]
    
    # Comparar dominios
    df_comp = vert_p1.merge(
        vert_p2, 
        on=['VERTICAL', 'DOMINIO'], 
        suffixes=('_P1', '_P2')
    )
    df_comp['VARIACION_ABS'] = df_comp['INCOMING_P2'] - df_comp['INCOMING_P1']
    df_comp['VARIACION_PCT'] = (df_comp['VARIACION_ABS'] / df_comp['INCOMING_P1']) * 100
    
    # Ordenar por impacto
    df_comp = df_comp.sort_values('VARIACION_ABS', ascending=False)
    
    # Mostrar resultados
    print(f"\nAnálisis de Dominios - {vertical_seleccionada}")
    print(f"Total dominios: {len(df_comp)}")
    print("\nTop 5 dominios con mayor variación:")
    for _, row in df_comp.head(5).iterrows():
        print(f"  - {row['DOMINIO']}: {row['VARIACION_ABS']:+,} casos ({row['VARIACION_PCT']:+.1f}%)")


# =============================================================================
# EJEMPLO 3: Validar métricas vs metadata
# =============================================================================

def ejemplo_3_validar_metricas():
    """
    Validar consistencia entre parquet y metadata
    """
    print("\n" + "="*80)
    print("EJEMPLO 3: Validar métricas")
    print("="*80)
    
    # Configuración
    site = 'MLA'
    periodo = '2025_12'
    
    # Paths
    metrics_path = Path('metrics/verticales/data')
    file_parquet = metrics_path / f'verticales_{site}_{periodo}.parquet'
    file_metadata = metrics_path / f'metadata_{site}_{periodo}.json'
    
    # Verificar existencia
    if not file_parquet.exists() or not file_metadata.exists():
        print(f"[WARNING] Archivos no encontrados")
        return
    
    # Leer archivos
    df = pd.read_parquet(file_parquet)
    with open(file_metadata) as f:
        metadata = json.load(f)
    
    # Validaciones
    print("\n🔍 Ejecutando validaciones...")
    
    # 1. Total de casos
    total_parquet = df['INCOMING'].sum()
    total_metadata = metadata['total_incoming']
    diff_pct = abs(total_parquet - total_metadata) / total_metadata * 100
    
    print(f"\n1. Total de casos:")
    print(f"   Parquet: {total_parquet:,}")
    print(f"   Metadata: {total_metadata:,}")
    print(f"   Diferencia: {diff_pct:.2f}%")
    print(f"   ✅ OK" if diff_pct < 1 else "   ❌ ERROR: Diferencia >1%")
    
    # 2. Verticales únicas
    vert_parquet = df['VERTICAL'].nunique()
    vert_metadata = metadata['verticales_unicas']
    
    print(f"\n2. Verticales únicas:")
    print(f"   Parquet: {vert_parquet}")
    print(f"   Metadata: {vert_metadata}")
    print(f"   ✅ OK" if vert_parquet == vert_metadata else "   ❌ ERROR: No coinciden")
    
    # 3. % sin vertical
    pct_sin_vert = metadata['pct_sin_vertical']
    print(f"\n3. Casos sin vertical:")
    print(f"   {pct_sin_vert:.2f}%")
    print(f"   ✅ OK" if pct_sin_vert < 5 else f"   ⚠️ ALERTA: >5% sin vertical")
    
    # 4. Duplicados
    duplicados = df.duplicated(['SITE', 'PERIODO', 'COMMERCE_GROUP', 'VERTICAL', 'DOMINIO']).sum()
    print(f"\n4. Duplicados:")
    print(f"   {duplicados} filas duplicadas")
    print(f"   ✅ OK" if duplicados == 0 else "   ❌ ERROR: Hay duplicados")
    
    print("\n✅ Validación completada")


# =============================================================================
# EJEMPLO 4: Generar output para reporte HTML
# =============================================================================

def ejemplo_4_output_para_reporte():
    """
    Generar sección HTML para incluir en Golden Template
    """
    print("\n" + "="*80)
    print("EJEMPLO 4: Generar output para reporte")
    print("="*80)
    
    # Configuración
    site = 'MLA'
    periodo_p1 = '2025_11'
    periodo_p2 = '2025_12'
    commerce_group = 'PDD'
    
    # Leer y comparar
    metrics_path = Path('metrics/verticales/data')
    df_p1 = pd.read_parquet(metrics_path / f'verticales_{site}_{periodo_p1}.parquet')
    df_p2 = pd.read_parquet(metrics_path / f'verticales_{site}_{periodo_p2}.parquet')
    
    # Filtrar y agrupar
    vert_p1 = df_p1[df_p1['COMMERCE_GROUP'] == commerce_group].groupby('VERTICAL')['INCOMING'].sum()
    vert_p2 = df_p2[df_p2['COMMERCE_GROUP'] == commerce_group].groupby('VERTICAL')['INCOMING'].sum()
    
    # Comparar
    df_comp = pd.DataFrame({
        'INCOMING_P1': vert_p1,
        'INCOMING_P2': vert_p2
    }).reset_index()
    df_comp['VAR_ABS'] = df_comp['INCOMING_P2'] - df_comp['INCOMING_P1']
    df_comp['VAR_PCT'] = (df_comp['VAR_ABS'] / df_comp['INCOMING_P1']) * 100
    
    # Detectar anomalías
    anomalias = df_comp[abs(df_comp['VAR_PCT']) > 10].sort_values('VAR_ABS', ascending=False)
    
    # Generar HTML
    if len(anomalias) == 0:
        print("\n✅ No se detectaron verticales con variaciones significativas")
        return
    
    print(f"\n⚠️ Se detectaron {len(anomalias)} verticales con variaciones significativas\n")
    print("--- MARKDOWN para incluir en reporte ---\n")
    print("## ⚠️ VERTICALES DESTACADAS\n")
    
    for i, (_, row) in enumerate(anomalias.head(5).iterrows(), 1):
        print(f"### {i}. {row['VERTICAL']} ({row['VAR_ABS']:+,} casos, {row['VAR_PCT']:+.1f}%)")
        print(f"- **Incoming P1:** {row['INCOMING_P1']:,} casos")
        print(f"- **Incoming P2:** {row['INCOMING_P2']:,} casos")
        print(f"- **Hipótesis:** [A completar con análisis de conversaciones]\n")


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("EJEMPLOS DE USO - MÉTRICAS DE VERTICALES Y DOMINIOS")
    print("="*80)
    print("\n✅ Script generador implementado. Para generar métricas:")
    print("   python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12\n")
    
    # Ejecutar ejemplos
    try:
        ejemplo_1_detectar_variaciones()
        ejemplo_2_analisis_dominios()
        ejemplo_3_validar_metricas()
        ejemplo_4_output_para_reporte()
    except FileNotFoundError as e:
        print("\n⚠️  NOTA: Para ejecutar estos ejemplos, primero genera las métricas:")
        print("   python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-11")
        print("   python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12")
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {e}")
    
    print("\n" + "="*80 + "\n")
