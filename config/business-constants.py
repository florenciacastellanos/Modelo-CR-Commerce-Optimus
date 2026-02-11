"""
══════════════════════════════════════════════════════════════════════════════
BUSINESS CONSTANTS - CONTACT RATE COMMERCE v2.5
══════════════════════════════════════════════════════════════════════════════
Description: Centralized business rules, thresholds, and constants
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

class BusinessConstants:
    """Centralized business rules and thresholds"""
    
    # ══════════════════════════════════════════════════════════════════════════
    # CONTACT RATE CALCULATION
    # ══════════════════════════════════════════════════════════════════════════
    CR_MULTIPLIER = 100  # Percentage points conversion
    CR_DECIMALS = 4      # Number of decimal places
    
    # ══════════════════════════════════════════════════════════════════════════
    # DEFAULT THRESHOLDS
    # ══════════════════════════════════════════════════════════════════════════
    DEFAULT_CASES_THRESHOLD = 100  # Minimum cases for analysis
    MIN_SAMPLE_SIZE = 50           # Minimum sample size
    MAX_SAMPLE_SIZE = 5000         # Maximum sample size
    
    # ══════════════════════════════════════════════════════════════════════════
    # MLB SAMPLING (Brasil specific)
    # ══════════════════════════════════════════════════════════════════════════
    MLB_ESTIMATED_ROWS_PER_AGRUP_MONTH = 50000
    MLB_SAMPLING_THRESHOLD = 150000
    MLB_MIN_LIMIT = 150000
    MLB_MAX_LIMIT = 200000
    
    # ══════════════════════════════════════════════════════════════════════════
    # MEMORY OPTIMIZATION
    # ══════════════════════════════════════════════════════════════════════════
    MEMORY_OPTIMIZATION_THRESHOLD = 50000  # Rows threshold for optimization
    
    # ══════════════════════════════════════════════════════════════════════════
    # EXCLUSIONS (Business rules)
    # ══════════════════════════════════════════════════════════════════════════
    EXCLUDED_CI_REASON_IDS = [2592, 6588, 10068, 2701, 10048]
    EXCLUDED_PROCESS_IDS = [1312]
    EXCLUDED_QUEUE_IDS = [2131, 230, 1102, 1241, 2075, 2131, 2294, 2295]
    EXCLUDED_SITES = ['MLV']  # Venezuela
    
    # Sites válidos y agrupaciones (ver config/site_groups.py para lógica completa)
    VALID_SITES = ['MLA', 'MLB', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE']
    SITE_GROUPS = {
        'ROLA': ['MLC', 'MCO', 'MEC', 'MLU', 'MPE'],       # Rest of Latin America (excl MLA, MLB, MLM)
        'HSP':  ['MLA', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE'],  # Hispanic (excl MLB)
    }
    
    # ══════════════════════════════════════════════════════════════════════════
    # PATTERN DETECTION THRESHOLDS
    # ══════════════════════════════════════════════════════════════════════════
    SPIKE_THRESHOLD_MULTIPLIER = 1.5       # 150% of average
    DROP_THRESHOLD_MULTIPLIER = 0.5        # 50% of average
    STRONG_VARIATION_PCT = 20              # ±20% MoM
    CONCENTRATION_THRESHOLD_PCT = 30       # 30% volume in critical days
    CRITICAL_DAY_DEVIATION_PCT = 50        # 50% deviation from rolling avg
    
    # ══════════════════════════════════════════════════════════════════════════
    # WEEKLY PATTERN THRESHOLDS
    # ══════════════════════════════════════════════════════════════════════════
    WEEKLY_STEP_DELTA_THRESHOLD = 0.02
    WEEKLY_GRADUAL_DELTA_THRESHOLD = 0.005
    WEEKLY_SPIKE_DELTA_THRESHOLD = 0.015
    WEEKLY_STABLE_DELTA_THRESHOLD = 0.01
    
    # ══════════════════════════════════════════════════════════════════════════
    # VOLUME SIGNIFICANCE
    # ══════════════════════════════════════════════════════════════════════════
    VOLUME_MATERIAL_CHANGE_PCT = 10  # 10% change considered material
    
    # ══════════════════════════════════════════════════════════════════════════
    # CONVERSATION VALIDATION
    # ══════════════════════════════════════════════════════════════════════════
    MIN_SUMMARY_LENGTH = 20
    MAX_SUMMARY_LENGTH = 5000
    MIN_CONVERSATION_LENGTH = 50
    
    # ══════════════════════════════════════════════════════════════════════════
    # SAMPLING STRATEGY
    # ══════════════════════════════════════════════════════════════════════════
    MIN_DAYS_FOR_PATTERN = 7      # Minimum days for pattern detection
    ROLLING_AVG_WINDOW = 7        # 7-day rolling average
    ROLLING_AVG_MIN_PERIODS = 3   # Minimum 3 periods for rolling avg


# Global instance
CONST = BusinessConstants()


# ══════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ══════════════════════════════════════════════════════════════════════════════

"""
from config.business_constants import CONST

# Use constants:
cr = (incoming / driver) * CONST.CR_MULTIPLIER
if cases_count >= CONST.DEFAULT_CASES_THRESHOLD:
    # Process data
    pass

# Exclusions:
WHERE QUEUE_ID NOT IN {tuple(CONST.EXCLUDED_QUEUE_IDS)}
WHERE PROCESS_ID NOT IN {tuple(CONST.EXCLUDED_PROCESS_IDS)}
WHERE SITE_ID NOT IN {tuple(CONST.EXCLUDED_SITES)}
"""
