"""
══════════════════════════════════════════════════════════════════════════════
SITE GROUPS - Definiciones de agrupaciones de sites y funciones helper
para generar filtros SQL dinámicos según site individual o grupo.
══════════════════════════════════════════════════════════════════════════════

Grupos disponibles:
  - ROLA: Todos los sites EXCEPTO MLA, MLB y MLM → MLC, MCO, MEC, MLU, MPE
  - HSP:  Todos los sites EXCEPTO MLB → MLA, MLC, MCO, MEC, MLM, MLU, MPE

Uso:
  from config.site_groups import resolve_site_sql, get_site_list, is_site_group

  # En SQL queries:
  f"WHERE {resolve_site_sql(args.site, 'C.SIT_SITE_ID')}"
  # → Individual: "WHERE C.SIT_SITE_ID = 'MLA'"
  # → Grupo:     "WHERE C.SIT_SITE_ID IN ('MLC', 'MCO', 'MEC', 'MLU', 'MPE')"

Version: 1.0
Fecha: Febrero 2026
"""

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

VALID_SITES = ['MLA', 'MLB', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE']

SITE_GROUPS = {
    'ROLA': ['MLC', 'MCO', 'MEC', 'MLU', 'MPE'],        # Rest of Latin America (excl MLA, MLB, MLM)
    'HSP':  ['MLA', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE'],  # Hispanic (excl MLB)
}


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════════════════════════

def is_site_group(site: str) -> bool:
    """
    Verifica si el valor recibido es un grupo (ROLA, HSP) o un site individual.
    
    Args:
        site: Nombre del site o grupo (ej: 'MLA', 'ROLA', 'HSP')
    
    Returns:
        True si es un grupo, False si es un site individual
    """
    return site.upper() in SITE_GROUPS


def get_site_list(site: str) -> list:
    """
    Retorna la lista de sites individuales para un site o grupo.
    
    Args:
        site: Nombre del site o grupo
    
    Returns:
        Lista de sites individuales
        - Si es grupo → lista completa (ej: ROLA → ['MLC', 'MCO', 'MEC', 'MLU', 'MPE'])
        - Si es individual → lista con un elemento (ej: MLA → ['MLA'])
    """
    site_upper = site.upper()
    if site_upper in SITE_GROUPS:
        return SITE_GROUPS[site_upper]
    return [site_upper]


def resolve_site_sql(site: str, column: str = 'C.SIT_SITE_ID') -> str:
    """
    FUNCIÓN CLAVE. Genera la condición SQL para filtrar por site o grupo.
    
    Retorna SOLO la condición (sin WHERE ni AND al inicio).
    
    Args:
        site: Nombre del site o grupo (ej: 'MLA', 'ROLA', 'HSP')
        column: Columna SQL con alias de tabla (ej: 'C.SIT_SITE_ID', 'ORD.SIT_SITE_ID')
    
    Returns:
        Condición SQL como string:
        - Individual: "C.SIT_SITE_ID = 'MLA'"
        - Grupo:     "C.SIT_SITE_ID IN ('MLC', 'MCO', 'MEC', 'MLU', 'MPE')"
    
    Examples:
        >>> resolve_site_sql('MLA', 'C.SIT_SITE_ID')
        "C.SIT_SITE_ID = 'MLA'"
        
        >>> resolve_site_sql('ROLA', 'C.SIT_SITE_ID')
        "C.SIT_SITE_ID IN ('MLC', 'MCO', 'MEC', 'MLU', 'MPE')"
        
        >>> resolve_site_sql('HSP', 'ORD.SIT_SITE_ID')
        "ORD.SIT_SITE_ID IN ('MLA', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE')"
    """
    site_upper = site.upper()
    if site_upper in SITE_GROUPS:
        sites = SITE_GROUPS[site_upper]
        sites_str = ", ".join(f"'{s}'" for s in sites)
        return f"{column} IN ({sites_str})"
    else:
        return f"{column} = '{site_upper}'"


def get_site_display_name(site: str) -> str:
    """
    Retorna el nombre para mostrar del site o grupo.
    
    Args:
        site: Nombre del site o grupo
    
    Returns:
        - Site individual: retorna tal cual (ej: 'MLA')
        - Grupo: retorna con detalle (ej: 'ROLA (MLC, MCO, MEC, MLU, MPE)')
    """
    site_upper = site.upper()
    if site_upper in SITE_GROUPS:
        sites = SITE_GROUPS[site_upper]
        return f"{site_upper} ({', '.join(sites)})"
    return site_upper
