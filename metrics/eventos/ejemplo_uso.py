"""
Ejemplo de Uso - Métricas de Correlación con Eventos
Versión: 1.0

Este ejemplo muestra cómo integrar las métricas pre-calculadas
en tus scripts de reportes (Golden Templates, dashboards, etc.)
"""

import pandas as pd
from pathlib import Path

# ========================================
# EJEMPLO 1: Uso Básico en Golden Template
# ========================================

def ejemplo_golden_template():
    """
    Ejemplo de cómo usar métricas en un Golden Template
    """
    print("EJEMPLO 1: Uso en Golden Template")
    print("="*60)
    
    # Configuración del reporte
    site = 'MLB'
    periodo = '2025-12'
    tipificacion_actual = 'REPENTANT_BUYER'
    
    # Construir path al archivo de métricas
    metrics_path = Path('metrics/eventos/data')
    periodo_str = periodo.replace('-', '_')
    file_corr = metrics_path / f'correlacion_{site.lower()}_{periodo_str}.parquet'
    
    # Verificar si existe
    if file_corr.exists():
        print(f"✅ Métricas encontradas: {file_corr}")
        
        # Leer métricas pre-calculadas
        df_correlaciones = pd.read_parquet(file_corr)
        
        # Filtrar por tipificación actual
        corr_tipif = df_correlaciones[
            df_correlaciones['TIPIFICACION'] == tipificacion_actual
        ]
        
        print(f"\nCorrelación para {tipificacion_actual}:")
        print(f"Total casos en tipificación: {corr_tipif['CASOS_TOTALES'].iloc[0]:,}")
        print("\nEventos correlacionados:")
        
        for _, row in corr_tipif.iterrows():
            if row['CASOS'] > 0:
                print(f"  - {row['EVENTO']}: {row['CASOS']:,} casos ({row['PORCENTAJE']:.1f}%)")
        
        # Generar texto para insight
        insight_text = ""
        correlaciones_encontradas = []
        
        for _, row in corr_tipif.iterrows():
            if row['CASOS'] > 0:
                correlaciones_encontradas.append(
                    f"{row['EVENTO']}: {row['CASOS']:,} casos ({row['PORCENTAJE']:.1f}% del total)"
                )
        
        if correlaciones_encontradas:
            insight_text = "Correlación con eventos comerciales (basada en ORD_CLOSED_DT): " + "; ".join(correlaciones_encontradas)
        else:
            insight_text = "No se detectó correlación directa con eventos comerciales específicos."
        
        print(f"\nTexto para reporte:\n{insight_text}")
        
    else:
        print(f"❌ Métricas no encontradas: {file_corr}")
        print("💡 Ejecuta: python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12")
        print("🔄 Fallback: Calculando correlación on-the-fly...")
        # Aquí iría el código de cálculo on-the-fly como backup

# ========================================
# EJEMPLO 2: Análisis Cross-Tipificación
# ========================================

def ejemplo_cross_tipificacion():
    """
    Analizar correlación de un evento a través de múltiples tipificaciones
    """
    print("\n\nEJEMPLO 2: Análisis Cross-Tipificación")
    print("="*60)
    
    site = 'MLB'
    periodo = '2025-12'
    evento = 'Black Friday Brasil'
    
    metrics_path = Path('metrics/eventos/data')
    periodo_str = periodo.replace('-', '_')
    file_corr = metrics_path / f'correlacion_{site.lower()}_{periodo_str}.parquet'
    
    if file_corr.exists():
        df = pd.read_parquet(file_corr)
        
        # Filtrar por evento
        bf_data = df[df['EVENTO'] == evento]
        
        print(f"\nImpacto de {evento} por Tipificación:")
        print(f"{'Tipificación':<30} {'Casos':>10} {'% Corr':>10} {'Total':>10}")
        print("-"*60)
        
        for _, row in bf_data.sort_values('CASOS', ascending=False).head(10).iterrows():
            print(f"{row['TIPIFICACION']:<30} {row['CASOS']:>10,} {row['PORCENTAJE']:>9.1f}% {row['CASOS_TOTALES']:>10,}")
        
        # Total
        total_casos_bf = bf_data['CASOS'].sum()
        total_casos = bf_data['CASOS_TOTALES'].sum()
        pct_global = (total_casos_bf / total_casos * 100) if total_casos > 0 else 0
        
        print("-"*60)
        print(f"{'TOTAL':<30} {total_casos_bf:>10,} {pct_global:>9.1f}% {total_casos:>10,}")

# ========================================
# EJEMPLO 3: Comparación Cross-Site
# ========================================

def ejemplo_cross_site():
    """
    Comparar correlación de un evento entre diferentes sites
    """
    print("\n\nEJEMPLO 3: Comparación Cross-Site")
    print("="*60)
    
    sites = ['MLB', 'MLA', 'MCO', 'MLC']
    periodo = '2025-11'  # Noviembre (Black Friday)
    evento_pattern = 'Black Friday'
    
    metrics_path = Path('metrics/eventos/data')
    periodo_str = periodo.replace('-', '_')
    
    print(f"\nCorrelación con Black Friday - Nov 2025")
    print(f"{'Site':<10} {'Casos BF':>15} {'Total Casos':>15} {'% Corr':>10}")
    print("-"*60)
    
    for site in sites:
        file_corr = metrics_path / f'correlacion_{site.lower()}_{periodo_str}.parquet'
        
        if file_corr.exists():
            df = pd.read_parquet(file_corr)
            bf_data = df[df['EVENTO'].str.contains(evento_pattern)]
            
            casos_bf = bf_data['CASOS'].sum()
            casos_total = bf_data['CASOS_TOTALES'].sum()
            pct = (casos_bf / casos_total * 100) if casos_total > 0 else 0
            
            print(f"{site:<10} {casos_bf:>15,} {casos_total:>15,} {pct:>9.1f}%")
        else:
            print(f"{site:<10} {'NO DISPONIBLE':>15}")

# ========================================
# EJEMPLO 4: Validación de Calidad de Datos
# ========================================

def ejemplo_validacion():
    """
    Validar calidad de métricas generadas
    """
    print("\n\nEJEMPLO 4: Validación de Calidad")
    print("="*60)
    
    site = 'MLB'
    periodo = '2025-12'
    
    metrics_path = Path('metrics/eventos/data')
    periodo_str = periodo.replace('-', '_')
    file_corr = metrics_path / f'correlacion_{site.lower()}_{periodo_str}.parquet'
    
    if file_corr.exists():
        df = pd.read_parquet(file_corr)
        
        print(f"✅ Archivo: {file_corr}")
        print(f"   Tamaño: {file_corr.stat().st_size / 1024:.1f} KB")
        print(f"   Rows: {len(df):,}")
        
        # Validaciones
        checks = []
        
        # Check 1: Porcentajes válidos
        check1 = df['PORCENTAJE'].between(0, 100).all()
        checks.append(("Porcentajes 0-100%", check1))
        
        # Check 2: Consistencia casos
        check2 = (df['CASOS'] <= df['CASOS_TOTALES']).all()
        checks.append(("Casos <= Totales", check2))
        
        # Check 3: No duplicados
        check3 = not df.duplicated(['SITE', 'PERIODO', 'TIPIFICACION', 'EVENTO']).any()
        checks.append(("Sin duplicados", check3))
        
        # Check 4: Datos completos
        check4 = df.notna().all().all()
        checks.append(("Sin valores NULL", check4))
        
        print("\nValidaciones:")
        for nombre, resultado in checks:
            status = "✅" if resultado else "❌"
            print(f"  {status} {nombre}")
        
        # Estadísticas
        print("\nEstadísticas:")
        print(f"  - Commerce Groups: {', '.join(df['COMMERCE_GROUP'].unique())}")
        print(f"  - Tipificaciones: {len(df['TIPIFICACION'].unique())}")
        print(f"  - Eventos: {', '.join(df['EVENTO'].unique())}")
        print(f"  - Total casos: {df['CASOS_TOTALES'].sum():,}")
        print(f"  - Casos correlacionados: {df['CASOS'].sum():,}")
        print(f"  - % correlacionado global: {df['CASOS'].sum() / df['CASOS_TOTALES'].sum() * 100:.1f}%")

# ========================================
# EJECUTAR EJEMPLOS
# ========================================

if __name__ == "__main__":
    print("🚀 EJEMPLOS DE USO - MÉTRICAS DE EVENTOS")
    print("="*60)
    
    ejemplo_golden_template()
    ejemplo_cross_tipificacion()
    ejemplo_cross_site()
    ejemplo_validacion()
    
    print("\n\n✅ EJEMPLOS COMPLETADOS")
    print("\n💡 Tip: Copia estos patrones a tus scripts de reportes")
