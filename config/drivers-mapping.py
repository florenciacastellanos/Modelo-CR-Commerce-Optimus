"""
══════════════════════════════════════════════════════════════════════════════
DRIVERS MAPPING CONFIGURATION - v1.0
══════════════════════════════════════════════════════════════════════════════
Description: Dynamic driver selection based on Commerce Group category
Version: 1.0
Last Update: Febrero 2026
══════════════════════════════════════════════════════════════════════════════

REGLAS DE DRIVERS POR CATEGORÍA:
- Post-Compra (PDD, PNR): Órdenes totales GLOBALES (sin filtro site)
- Shipping (ME, FBM): Drivers específicos de BT_CX_DRIVERS_CR GLOBALES (sin filtro site)
- Marketplace: Órdenes totales FILTRADAS POR SITE
- Pagos (MP On): Órdenes totales GLOBALES
- Cuenta: Órdenes totales GLOBALES

Referencias:
- Post-Compra/Marketplace: docs/BASE_FILTERS_ORDERS.md
- Shipping: docs/SHIPPING_DRIVERS.md
- Commerce Groups: config/commerce-groups.py
══════════════════════════════════════════════════════════════════════════════
"""


# ══════════════════════════════════════════════════════════════════════════════
# DRIVER CONFIGURATION BY COMMERCE GROUP
# ══════════════════════════════════════════════════════════════════════════════

DRIVER_CONFIG = {
    # ========================================
    # POST-COMPRA - Órdenes totales GLOBALES
    # ========================================
    'PDD': {
        'type': 'orders_global',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': False,
        'description': 'Órdenes totales GLOBALES (sin filtro site)'
    },
    'PNR': {
        'type': 'orders_global',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': False,
        'description': 'Órdenes totales GLOBALES (sin filtro site)'
    },
    
    # ========================================
    # SHIPPING - Drivers específicos GLOBALES
    # ========================================
    'ME Distribución': {
        'type': 'shipping_drivers',
        'table': 'BT_CX_DRIVERS_CR',
        'date_field': 'MONTH_ID',
        'count_expression': 'SUM(drv.ORDERS_SHIPPED)',
        'filter_by_site': False,
        'description': 'Órdenes shipped GLOBALES (OS_TOTALES)'
    },
    'ME PreDespacho': {
        'type': 'shipping_drivers',
        'table': 'BT_CX_DRIVERS_CR',
        'date_field': 'MONTH_ID',
        'count_expression': 'SUM(drv.OS_WITHOUT_FBM)',
        'filter_by_site': False,
        'description': 'Órdenes sin FBM GLOBALES (OS_WO_FULL)'
    },
    'FBM Sellers': {
        'type': 'shipping_drivers',
        'table': 'BT_CX_DRIVERS_CR',
        'date_field': 'MONTH_ID',
        'count_expression': 'SUM(drv.OS_WITH_FBM)',
        'filter_by_site': False,
        'description': 'Órdenes con FBM GLOBALES (OS_FULL)'
    },
    'ME Drivers': {
        'type': 'shipping_drivers',
        'table': 'BT_CX_DRIVERS_CR',
        'date_field': 'MONTH_ID',
        'count_expression': 'SUM(drv.ORDERS_SHIPPED)',  # TBD - pendiente definir campo específico
        'filter_by_site': False,
        'description': 'Órdenes shipped GLOBALES (pendiente driver específico)'
    },
    
    # ========================================
    # MARKETPLACE - Órdenes totales POR SITE
    # ========================================
    'Pre Venta': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Post Venta': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Generales Compra': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Moderaciones': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Full Sellers': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Pagos': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    'Loyalty': {
        'type': 'orders_by_site',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': True,
        'description': 'Órdenes totales del site específico'
    },
    
    # ========================================
    # PAGOS - Órdenes totales GLOBALES
    # ========================================
    'MP On': {
        'type': 'orders_global',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': False,
        'description': 'Órdenes totales GLOBALES (sin filtro site)'
    },
    
    # ========================================
    # CUENTA - Órdenes totales GLOBALES
    # ========================================
    'Cuenta': {
        'type': 'orders_global',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': False,
        'description': 'Órdenes totales GLOBALES (sin filtro site)'
    },
    'Experiencia Impositiva': {
        'type': 'orders_global',
        'table': 'BT_ORD_ORDERS',
        'date_field': 'ORD_CLOSED_DT',
        'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
        'filter_by_site': False,
        'description': 'Órdenes totales GLOBALES (sin filtro site)'
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# NORMALIZED COMMERCE GROUP NAMES (aliases)
# ══════════════════════════════════════════════════════════════════════════════

COMMERCE_GROUP_ALIASES = {
    # Post-Compra
    'pdd': 'PDD',
    'PDD': 'PDD',
    'pnr': 'PNR',
    'PNR': 'PNR',
    
    # Shipping
    'me_distribucion': 'ME Distribución',
    'ME_DISTRIBUCION': 'ME Distribución',
    'ME Distribucion': 'ME Distribución',
    'ME Distribución': 'ME Distribución',
    
    'me_predespacho': 'ME PreDespacho',
    'ME_PREDESPACHO': 'ME PreDespacho',
    'ME PreDespacho': 'ME PreDespacho',
    
    'fbm_sellers': 'FBM Sellers',
    'FBM_SELLERS': 'FBM Sellers',
    'FBM Sellers': 'FBM Sellers',
    
    'me_drivers': 'ME Drivers',
    'ME_DRIVERS': 'ME Drivers',
    'ME Drivers': 'ME Drivers',
    
    # Marketplace
    'pre_venta': 'Pre Venta',
    'PRE_VENTA': 'Pre Venta',
    'Pre Venta': 'Pre Venta',
    
    'post_venta': 'Post Venta',
    'POST_VENTA': 'Post Venta',
    'Post Venta': 'Post Venta',
    
    'generales_compra': 'Generales Compra',
    'GENERALES_COMPRA': 'Generales Compra',
    'Generales Compra': 'Generales Compra',
    
    'moderaciones': 'Moderaciones',
    'MODERACIONES': 'Moderaciones',
    'Moderaciones': 'Moderaciones',
    
    'full_sellers': 'Full Sellers',
    'FULL_SELLERS': 'Full Sellers',
    'Full Sellers': 'Full Sellers',
    
    'pagos': 'Pagos',
    'PAGOS': 'Pagos',
    'Pagos': 'Pagos',
    
    'loyalty': 'Loyalty',
    'LOYALTY': 'Loyalty',
    'Loyalty': 'Loyalty',
    
    # Pagos
    'mp_on': 'MP On',
    'MP_ON': 'MP On',
    'MP On': 'MP On',
    
    # Cuenta
    'cuenta': 'Cuenta',
    'CUENTA': 'Cuenta',
    'Cuenta': 'Cuenta',
    
    'experiencia_impositiva': 'Experiencia Impositiva',
    'EXPERIENCIA_IMPOSITIVA': 'Experiencia Impositiva',
    'Experiencia Impositiva': 'Experiencia Impositiva',
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_driver_config(commerce_group: str) -> dict:
    """
    Get driver configuration for a commerce group.
    
    Args:
        commerce_group: Commerce group name (can be normalized or alias)
    
    Returns:
        Dictionary with driver configuration
    
    Raises:
        KeyError: If commerce group not found
    """
    # Normalize commerce group name
    normalized = COMMERCE_GROUP_ALIASES.get(commerce_group, commerce_group)
    
    if normalized not in DRIVER_CONFIG:
        raise KeyError(f"Commerce group '{commerce_group}' not found in driver configuration. Available: {list(DRIVER_CONFIG.keys())}")
    
    return DRIVER_CONFIG[normalized]


def get_driver_description(commerce_group: str, site: str = None) -> str:
    """
    Get human-readable driver description.
    
    Args:
        commerce_group: Commerce group name
        site: Site code (optional, used for site-filtered drivers)
    
    Returns:
        Description string
    """
    config = get_driver_config(commerce_group)
    desc = config['description']
    
    if config['filter_by_site'] and site:
        return f"{desc} - {site}"
    
    return desc


# ══════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ══════════════════════════════════════════════════════════════════════════════

"""
from config.drivers_mapping import get_driver_config, get_driver_description

# Get driver config
config = get_driver_config('GENERALES_COMPRA')
# Returns: {
#   'type': 'orders_by_site',
#   'table': 'BT_ORD_ORDERS',
#   'date_field': 'ORD_CLOSED_DT',
#   'count_expression': 'COUNT(DISTINCT ORD.ORD_ORDER_ID)',
#   'filter_by_site': True,
#   'description': 'Órdenes totales del site específico'
# }

# Check if needs site filter
if config['filter_by_site']:
    query = f"WHERE {config['date_field']} BETWEEN ... AND SIT_SITE_ID = '{site}'"
else:
    query = f"WHERE {config['date_field']} BETWEEN ..."

# Get description
desc = get_driver_description('GENERALES_COMPRA', 'MLM')
# Returns: "Órdenes totales del site específico - MLM"
"""
