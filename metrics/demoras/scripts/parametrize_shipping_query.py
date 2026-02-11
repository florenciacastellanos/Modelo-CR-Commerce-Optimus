"""
Utilidad para parametrizar la query de Shipping con filtros dinámicos.

Este script permite generar queries SQL parametrizadas para análisis de demoras
en Shipping, ajustadas a los filtros solicitados por el usuario (site, período,
picking type, granularidad).

Uso básico:
    from metrics.demoras.scripts.parametrize_shipping_query import parametrize_shipping_query
    
    query = parametrize_shipping_query(
        site='MLA',
        fecha_inicio='2025-11-01',
        fecha_fin='2026-01-01',
        granularidad='MONTH',
        picking_type=None  # None = todos
    )

Autor: Sistema CR Commerce
Versión: 1.0
Última actualización: 2026-01-29
"""

from pathlib import Path
from typing import Optional
import sys

# Agregar path del repositorio para imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from config.site_groups import resolve_site_sql


def parametrize_shipping_query(
    site: Optional[str] = None,
    fecha_inicio: str = None,
    fecha_fin: str = None,
    granularidad: str = 'MONTH',
    picking_type: Optional[str] = None
) -> str:
    """
    Parametriza la query de Shipping con filtros dinámicos.
    
    Args:
        site: Código de site ('MLA', 'MLB', etc.) o None para Cross-Site
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'
        granularidad: 'MONTH', 'WEEK', o 'DAY'
        picking_type: Tipo de picking ('fulfillment', 'cross_docking', etc.) o None
        
    Returns:
        Query SQL parametrizada lista para ejecutar
        
    Raises:
        ValueError: Si faltan parámetros obligatorios
        FileNotFoundError: Si no encuentra el template
        
    Example:
        >>> query = parametrize_shipping_query(
        ...     site='MLA',
        ...     fecha_inicio='2025-11-01',
        ...     fecha_fin='2026-01-01',
        ...     granularidad='MONTH'
        ... )
        >>> print(f"Query generada: {len(query)} caracteres")
    """
    
    # Validaciones
    if not fecha_inicio or not fecha_fin:
        raise ValueError("fecha_inicio y fecha_fin son obligatorios")
    
    if granularidad not in ['MONTH', 'WEEK', 'DAY']:
        raise ValueError(f"granularidad debe ser MONTH, WEEK o DAY. Recibido: {granularidad}")
    
    # Leer template
    template_path = Path(__file__).parent.parent / 'sql' / 'shipping_drivers_optimized_template.sql'
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template no encontrado: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        query = f.read()
    
    # Construir filtros dinámicos
    site_filter = f"AND {resolve_site_sql(site, 'SIT_SITE_ID')}" if site else ""
    picking_type_filter = f"AND lower(SHP_PICKING_TYPE) = '{picking_type.lower()}'" if picking_type else ""
    
    # Reemplazar parámetros
    query = query.replace('{site}', site or 'Cross-Site')
    query = query.replace('{fecha_inicio}', fecha_inicio)
    query = query.replace('{fecha_fin}', fecha_fin)
    query = query.replace('{granularidad}', granularidad)
    query = query.replace('{site_filter}', site_filter)
    query = query.replace('{picking_type_filter}', picking_type_filter)
    
    return query


def save_parametrized_query(
    query: str,
    output_filename: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Guarda la query parametrizada en un archivo.
    
    Args:
        query: Query SQL parametrizada
        output_filename: Nombre del archivo de salida (ej: 'shipping_mla_nov_dic.sql')
        output_dir: Directorio de salida (default: sql/ en raíz del repo)
        
    Returns:
        Path del archivo guardado
        
    Example:
        >>> query = parametrize_shipping_query(site='MLA', ...)
        >>> path = save_parametrized_query(query, 'shipping_mla_nov.sql')
        >>> print(f"Guardado en: {path}")
    """
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent.parent / 'sql'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(query)
    
    return output_path


def generate_query_for_analysis(
    site: str,
    periodo_inicio: str,
    periodo_fin: str,
    tipo_variacion: str = 'mensual',
    deep_dive_picking: Optional[str] = None
) -> dict:
    """
    Genera queries parametrizadas para un análisis completo de CR.
    
    Esta función genera las queries necesarias para baseline y (opcionalmente)
    deep dive, siguiendo el protocolo del framework CR.
    
    Args:
        site: Site a analizar ('MLA', 'MLB', etc.)
        periodo_inicio: Fecha inicio (YYYY-MM-DD)
        periodo_fin: Fecha fin (YYYY-MM-DD)
        tipo_variacion: 'mensual', 'semanal', o 'quarter'
        deep_dive_picking: Picking type para deep dive (opcional)
        
    Returns:
        Dict con queries generadas:
        {
            'baseline': str (query baseline),
            'deep_dive': str (query deep dive, si aplica),
            'granularidad': str (MONTH/WEEK/DAY)
        }
        
    Example:
        >>> queries = generate_query_for_analysis(
        ...     site='MLA',
        ...     periodo_inicio='2025-11-01',
        ...     periodo_fin='2026-01-01',
        ...     tipo_variacion='mensual'
        ... )
        >>> print(f"Baseline generada: {len(queries['baseline'])} caracteres")
    """
    
    # Mapear tipo_variacion a granularidad
    granularidad_map = {
        'mensual': 'MONTH',
        'semanal': 'WEEK',
        'quarter': 'MONTH',  # Quarter usa MONTH y luego agrupa
        'diario': 'DAY'
    }
    
    granularidad = granularidad_map.get(tipo_variacion.lower(), 'MONTH')
    
    # Query baseline
    query_baseline = parametrize_shipping_query(
        site=site,
        fecha_inicio=periodo_inicio,
        fecha_fin=periodo_fin,
        granularidad=granularidad,
        picking_type=None  # Baseline incluye todos
    )
    
    result = {
        'baseline': query_baseline,
        'granularidad': granularidad
    }
    
    # Query deep dive (si aplica)
    if deep_dive_picking:
        query_deep_dive = parametrize_shipping_query(
            site=site,
            fecha_inicio=periodo_inicio,
            fecha_fin=periodo_fin,
            granularidad='WEEK' if granularidad == 'MONTH' else 'DAY',  # Más granular
            picking_type=deep_dive_picking
        )
        result['deep_dive'] = query_deep_dive
    
    return result


# ==============================================
# Ejemplo de uso (ejecutar con: python -m metrics.demoras.scripts.parametrize_shipping_query)
# ==============================================

if __name__ == '__main__':
    print("=" * 60)
    print("Sistema de Parametrización de Queries - Demoras Shipping")
    print("=" * 60)
    print()
    
    # Ejemplo 1: Single-Site (MLA) mensual
    print("📊 Ejemplo 1: Análisis MLA Nov-Dic 2025 (mensual)")
    print("-" * 60)
    
    query_mla = parametrize_shipping_query(
        site='MLA',
        fecha_inicio='2025-11-01',
        fecha_fin='2026-01-01',
        granularidad='MONTH'
    )
    
    output_path = save_parametrized_query(
        query_mla,
        'shipping_drivers_mla_nov_dic_2025.sql'
    )
    
    print(f"✅ Query parametrizada guardada en:")
    print(f"   {output_path}")
    print()
    print(f"📝 Ejecutar con:")
    print(f"   Get-Content {output_path} -Raw | bq query --use_legacy_sql=false --format=csv > output/drivers_mla.csv")
    print()
    
    # Ejemplo 2: Cross-Site semanal
    print("📊 Ejemplo 2: Análisis Cross-Site Dic 2025 (semanal)")
    print("-" * 60)
    
    query_cross = parametrize_shipping_query(
        site=None,  # Cross-Site
        fecha_inicio='2025-12-01',
        fecha_fin='2026-01-01',
        granularidad='WEEK'
    )
    
    output_path_cross = save_parametrized_query(
        query_cross,
        'shipping_drivers_cross_dic_2025_semanal.sql'
    )
    
    print(f"✅ Query Cross-Site guardada en:")
    print(f"   {output_path_cross}")
    print()
    
    # Ejemplo 3: Análisis completo (baseline + deep dive)
    print("📊 Ejemplo 3: Análisis completo con deep dive en Fulfillment")
    print("-" * 60)
    
    queries = generate_query_for_analysis(
        site='MLA',
        periodo_inicio='2025-11-01',
        periodo_fin='2026-01-01',
        tipo_variacion='mensual',
        deep_dive_picking='fulfillment'
    )
    
    # Guardar baseline
    path_baseline = save_parametrized_query(
        queries['baseline'],
        'shipping_mla_nov_dic_baseline.sql'
    )
    
    print(f"✅ Baseline guardada en: {path_baseline}")
    
    # Guardar deep dive
    if 'deep_dive' in queries:
        path_deep_dive = save_parametrized_query(
            queries['deep_dive'],
            'shipping_mla_nov_dic_deep_dive_ff.sql'
        )
        print(f"✅ Deep Dive guardado en: {path_deep_dive}")
    
    print()
    print("=" * 60)
    print("✅ Ejemplos generados correctamente")
    print("=" * 60)
