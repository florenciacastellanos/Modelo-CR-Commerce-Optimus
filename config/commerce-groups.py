"""
══════════════════════════════════════════════════════════════════════════════
COMMERCE GROUPS CONFIGURATION - v2.5
══════════════════════════════════════════════════════════════════════════════
Description: 15 Commerce Groups configuration (5 categories)
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════════════
# AVAILABLE COMMERCE GROUPS (15 total)
# ══════════════════════════════════════════════════════════════════════════════

AVAILABLE_AGRUP_COMMERCE = [
    # Post-Compra (2)
    'PDD', 'PNR',
    
    # Shipping (4)
    'ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers',
    
    # Marketplace (6)
    'Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 
    'Full Sellers', 'Pagos',
    
    # Pagos (1)
    'MP On',
    
    # Cuenta (2)
    'Cuenta', 'Experiencia Impositiva'
]


# ══════════════════════════════════════════════════════════════════════════════
# COMMERCE GROUPS METADATA
# ══════════════════════════════════════════════════════════════════════════════

AGRUP_COMMERCE_INFO = {
    # POST-COMPRA
    'PDD': {
        'label': 'PDD',
        'icon': '📦',
        'description': 'Producto Dañado/Defectuoso',
        'color': '#dc2626',
        'category': 'Post-Compra'
    },
    'PNR': {
        'label': 'PNR',
        'icon': '🚚',
        'description': 'Producto No Recibido',
        'color': '#f59e0b',
        'category': 'Post-Compra'
    },
    
    # SHIPPING
    'ME Distribución': {
        'label': 'ME Distribución',
        'icon': '📦',
        'description': 'Distribución de envíos (Comprador)',
        'color': '#14b8a6',
        'category': 'Shipping'
    },
    'ME PreDespacho': {
        'label': 'ME PreDespacho',
        'icon': '📤',
        'description': 'Pre-despacho de envíos (Vendedor)',
        'color': '#06b6d4',
        'category': 'Shipping'
    },
    'FBM Sellers': {
        'label': 'FBM Sellers',
        'icon': '🏪',
        'description': 'Fulfillment by Mercado Libre Sellers',
        'color': '#0891b2',
        'category': 'Shipping'
    },
    'ME Drivers': {
        'label': 'ME Drivers',
        'icon': '🏍️',
        'description': 'Drivers de Mercado Envíos',
        'color': '#7c3aed',
        'category': 'Shipping'
    },
    
    # MARKETPLACE
    'Pre Venta': {
        'label': 'Pre Venta',
        'icon': '🔍',
        'description': 'Consultas pre-venta',
        'color': '#3b82f6',
        'category': 'Marketplace'
    },
    'Post Venta': {
        'label': 'Post Venta',
        'icon': '📞',
        'description': 'Soporte post-venta',
        'color': '#2563eb',
        'category': 'Marketplace'
    },
    'Generales Compra': {
        'label': 'Generales Compra',
        'icon': '🛍️',
        'description': 'Consultas generales de compra',
        'color': '#1d4ed8',
        'category': 'Marketplace'
    },
    'Moderaciones': {
        'label': 'Moderaciones',
        'icon': '⚖️',
        'description': 'Moderaciones y Prustomer',
        'color': '#1e40af',
        'category': 'Marketplace'
    },
    'Full Sellers': {
        'label': 'Full Sellers',
        'icon': '🏬',
        'description': 'Full Sellers',
        'color': '#6d28d9',
        'category': 'Marketplace'
    },
    'Pagos': {
        'label': 'Pagos',
        'icon': '💳',
        'description': 'Pagos y transacciones (Marketplace)',
        'color': '#ec4899',
        'category': 'Marketplace'
    },
    
    # PAGOS
    'MP On': {
        'label': 'MP On',
        'icon': '💰',
        'description': 'Mercado Pago Online',
        'color': '#db2777',
        'category': 'Pagos'
    },
    
    # CUENTA
    'Cuenta': {
        'label': 'Cuenta',
        'icon': '👤',
        'description': 'Gestión de cuenta y seguridad',
        'color': '#64748b',
        'category': 'Cuenta'
    },
    'Experiencia Impositiva': {
        'label': 'Exp. Impositiva',
        'icon': '📄',
        'description': 'Experiencia Impositiva',
        'color': '#475569',
        'category': 'Cuenta'
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIES STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

AGRUP_COMMERCE_CATEGORIES = {
    'Post-Compra': {
        'icon': '📦',
        'color': '#dc2626',
        'items': ['PDD', 'PNR']
    },
    'Shipping': {
        'icon': '🚛',
        'color': '#10b981',
        'items': ['ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers']
    },
    'Marketplace': {
        'icon': '🛒',
        'color': '#3b82f6',
        'items': ['Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 'Full Sellers', 'Pagos']
    },
    'Pagos': {
        'icon': '💳',
        'color': '#db2777',
        'items': ['MP On']
    },
    'Cuenta': {
        'icon': '👤',
        'color': '#64748b',
        'items': ['Cuenta', 'Experiencia Impositiva']
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_commerce_group_info(agrup_commerce: str) -> dict:
    """Get metadata for a commerce group"""
    return AGRUP_COMMERCE_INFO.get(agrup_commerce, {})


def get_category_groups(category: str) -> list:
    """Get all groups in a category"""
    return AGRUP_COMMERCE_CATEGORIES.get(category, {}).get('items', [])


def get_group_category(agrup_commerce: str) -> str:
    """Get category for a commerce group"""
    info = AGRUP_COMMERCE_INFO.get(agrup_commerce, {})
    return info.get('category', 'Unknown')
