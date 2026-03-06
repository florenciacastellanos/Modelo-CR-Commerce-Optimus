"""
══════════════════════════════════════════════════════════════════════════════
CONTINGENCIAS CONFIG - Google Sheets integration for operational contingencies
══════════════════════════════════════════════════════════════════════════════

Configuración para la ingesta de contingencias operacionales desde Google Sheets.
Las contingencias son sucesos impredecibles (climáticos, paros, cortes de servicio, etc.)
que impactan la operación logística y pueden explicar variaciones atípicas de CR.

Version: 1.0
Fecha: Marzo 2026
"""

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEET SOURCE
# ══════════════════════════════════════════════════════════════════════════════

CONTINGENCIAS_SHEET_ID = "1p_PFzAMawAGdWsZIj1UACVl8627KDf7TilvU1oesm38"
CONTINGENCIAS_SHEET_NAME = None  # None = usa la primera pestaña

# ══════════════════════════════════════════════════════════════════════════════
# MAPEO DE COLUMNAS (GSheet → nombre interno)
# ══════════════════════════════════════════════════════════════════════════════

COLUMN_MAPPING = {
    'Clave': 'clave',
    'Resumen': 'resumen',
    'Origin': 'origin',
    'Site': 'site',
    'Creada': 'fecha_inicio',
    'Logistic': 'logistic',
    'Estado': 'estado',
    'End Date': 'fecha_fin',
    'Descripción': 'descripcion',
}

# Columnas a ignorar
IGNORE_COLUMNS = ['customfield_16004']

# ══════════════════════════════════════════════════════════════════════════════
# MAPEO LOGISTIC → ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════════
# None = aplica a TODOS los environments (sin filtro)

LOGISTIC_TO_ENVIRONMENT = {
    'Flex': ['Flex'],
    'Fulfillment': ['Full', 'FBM'],
    'XD Drop Off': ['XDDO'],
    'Cross Docking': ['XD'],
    'Drop Off': ['DS'],
    'Logistics': None,
}

# ══════════════════════════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════════════════════════

CACHE_DIR = "output/cache"
CACHE_TTL_HOURS = 24
