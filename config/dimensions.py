"""
══════════════════════════════════════════════════════════════════════════════
OUTPUT DIMENSIONS CONFIGURATION - COMMERCE v2.5
══════════════════════════════════════════════════════════════════════════════
Description: 8 analysis dimensions configuration
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT DIMENSIONS (8 total)
# ══════════════════════════════════════════════════════════════════════════════

OUTPUT_DIMENSIONS = {
    'PROCESS': {
        'field': 'PROCESS_NAME',
        'label': 'Process Name',
        'description': 'Proceso específico de Commerce',
        'icon': '⚙️',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'CDU': {
        'field': 'CDU',
        'label': 'Caso de Uso',
        'description': 'Caso de uso del contacto',
        'icon': '🎯',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'REASON_DETAIL': {
        'field': 'REASON_DETAIL_GROUP_REPORTING',
        'label': 'Reason Detail',
        'description': 'Motivo detallado del contacto',
        'icon': '📋',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'COMMERCE_GROUP': {
        'field': 'AGRUP_COMMERCE',
        'label': 'Commerce Group',
        'description': 'Agrupación de Commerce (15 groups)',
        'icon': '🏷️',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'REPORTING_TYPE': {
        'field': 'PROBLEMATIC_REPORTING',
        'label': 'Reporting Type',
        'description': 'Tipo de reporte problematic',
        'icon': '📊',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'ENVIRONMENT': {
        'field': 'ENVIRONMENT',
        'label': 'Environment',
        'description': 'Ambiente logístico (DS, FBM, FLEX, XD, MP_ON, MP_OFF)',
        'icon': '🌐',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc'
    },
    'VERTICAL': {
        'field': 'VERTICAL',
        'label': 'Vertical',
        'description': 'Vertical de negocio',
        'icon': '🏢',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc',
        'status': 'NULL',  # ⚠️ Currently NULL (table not available)
        'note': 'Temporarily unavailable - table source pending'
    },
    'DOMAIN': {
        'field': 'DOM_DOMAIN_AGG1',
        'label': 'Domain',
        'description': 'Dominio agregado nivel 1',
        'icon': '🏷️',
        'grouping_logic': 'standard',
        'min_threshold_default': 100,
        'sort_by': 'volume_desc',
        'status': 'NULL',  # ⚠️ Currently NULL (table not available)
        'note': 'Temporarily unavailable - table source pending'
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# AVAILABLE DIMENSIONS (excluding NULL ones)
# ══════════════════════════════════════════════════════════════════════════════

AVAILABLE_DIMENSIONS = [
    'PROCESS', 'CDU', 'REASON_DETAIL', 'COMMERCE_GROUP', 
    'REPORTING_TYPE', 'ENVIRONMENT'
    # Note: VERTICAL and DOMAIN excluded (NULL status)
]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_dimension_field(dimension_key: str) -> str:
    """Get database field name for dimension"""
    dim = OUTPUT_DIMENSIONS.get(dimension_key, {})
    return dim.get('field', dimension_key)


def get_dimension_threshold(dimension_key: str) -> int:
    """Get default threshold for dimension"""
    dim = OUTPUT_DIMENSIONS.get(dimension_key, {})
    return dim.get('min_threshold_default', 100)


def is_dimension_available(dimension_key: str) -> bool:
    """Check if dimension is available (not NULL)"""
    dim = OUTPUT_DIMENSIONS.get(dimension_key, {})
    return dim.get('status') != 'NULL'
