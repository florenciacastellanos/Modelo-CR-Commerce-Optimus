"""
══════════════════════════════════════════════════════════════════════════════
THRESHOLDS AND LIMITS - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: All thresholds and limits for CR analysis
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════════════
# CASES THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

MIN_CASES_THRESHOLD = 100  # Default minimum cases for analysis
MIN_SAMPLE_SIZE = 50       # Minimum sample size for statistical significance
MAX_SAMPLE_SIZE = 5000     # Maximum sample size for performance

# PROCESS-LEVEL THRESHOLDS (Applied per period)
MIN_PROCESS_INCOMING = 50  # Minimum incoming cases per process per period
                          # REGLA: Si la SUMA TOTAL de un PROCESS_NAME >= 50 en CUALQUIER período,
                          # se incluyen TODOS los CDUs/dimensiones de ese proceso
                          # Esto permite análisis completo de procesos significativos


# ══════════════════════════════════════════════════════════════════════════════
# CONTACT RATE THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

CR_EXPECTED_MIN = 0.1   # Minimum expected CR (pp)
CR_EXPECTED_MAX = 20.0  # Maximum expected CR (pp)

# CR Quality levels
CR_EXCELLENT = 1.0   # < 1.0 pp: Excellent
CR_VERY_GOOD = 2.0   # < 2.0 pp: Very Good
CR_GOOD = 3.0        # < 3.0 pp: Good
CR_FAIR = 5.0        # < 5.0 pp: Fair
CR_POOR = 8.0        # < 8.0 pp: Poor
CR_CRITICAL = 8.0    # >= 8.0 pp: Critical


# ══════════════════════════════════════════════════════════════════════════════
# VARIATION THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

VAR_STRONG_PCT = 20     # ±20% MoM: Strong variation
VAR_MODERATE_PCT = 10   # ±10% MoM: Moderate variation
VAR_SLIGHT_PCT = 5      # ±5% MoM: Slight variation

VAR_NOTABLE_PP = 0.5    # ±0.5 pp: Notable change
VAR_SIGNIFICANT_PP = 1.0  # ±1.0 pp: Significant change
VAR_CRITICAL_PP = 2.0     # ±2.0 pp: Critical change


# ══════════════════════════════════════════════════════════════════════════════
# PATTERN DETECTION THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

SPIKE_THRESHOLD = 1.5   # 150% of rolling average
DROP_THRESHOLD = 0.5    # 50% of rolling average

CONCENTRATION_THRESHOLD = 0.30  # 30% volume in critical days
CRITICAL_DAY_DEVIATION = 0.50   # 50% deviation from rolling avg


# ══════════════════════════════════════════════════════════════════════════════
# TEMPORAL THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

MIN_DAYS_FOR_PATTERN = 7      # Minimum days for pattern detection
ROLLING_AVG_WINDOW = 7        # 7-day rolling average
ROLLING_AVG_MIN_PERIODS = 3   # Minimum 3 periods for rolling avg


# ══════════════════════════════════════════════════════════════════════════════
# MLB SAMPLING THRESHOLDS (Brasil specific)
# ══════════════════════════════════════════════════════════════════════════════

MLB_ESTIMATED_ROWS_PER_AGRUP_MONTH = 50000
MLB_SAMPLING_THRESHOLD = 150000
MLB_MIN_LIMIT = 150000
MLB_MAX_LIMIT = 200000


# ══════════════════════════════════════════════════════════════════════════════
# MEMORY THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

MEMORY_OPTIMIZATION_THRESHOLD = 50000  # Rows threshold for memory optimization
