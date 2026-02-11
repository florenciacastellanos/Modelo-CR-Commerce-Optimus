# Config package - CR Commerce Analytics
# Contiene configuraciones, constantes y utilidades

from .causas_sinonimos import (
    consolidar_causas_similares,
    finalizar_aprendizaje,
    obtener_gestor,
    GestorSinonimos,
    SINONIMOS_SEMILLA,
    UMBRAL_SIMILARIDAD,
    UMBRAL_CONFIRMADO
)

from .site_groups import (
    resolve_site_sql,
    get_site_list,
    is_site_group,
    get_site_display_name,
    SITE_GROUPS,
    VALID_SITES
)

__all__ = [
    'consolidar_causas_similares',
    'finalizar_aprendizaje',
    'obtener_gestor',
    'GestorSinonimos',
    'SINONIMOS_SEMILLA',
    'UMBRAL_SIMILARIDAD',
    'UMBRAL_CONFIRMADO',
    'resolve_site_sql',
    'get_site_list',
    'is_site_group',
    'get_site_display_name',
    'SITE_GROUPS',
    'VALID_SITES',
]
