"""
══════════════════════════════════════════════════════════════════════════════
VARIATION ANALYSIS - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: Analysis of CR variations (MoM, YoY, trends)
Includes: Absolute variation, relative variation, volume impact
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

STRONG_VARIATION_PCT = 20  # ±20% MoM considered strong variation


# ══════════════════════════════════════════════════════════════════════════════
# ABSOLUTE VARIATION (pp)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_absolute_variation(cr_current, cr_previous):
    """
    Calculate absolute variation in percentage points
    
    Formula:
        Variation (pp) = CR_current - CR_previous
    
    Args:
        cr_current (float): Current period CR
        cr_previous (float): Previous period CR
    
    Returns:
        float: Absolute variation in pp (4 decimals)
               None if either CR is invalid
    
    Examples:
        >>> calculate_absolute_variation(6.8, 5.2)
        1.6000
        
        >>> calculate_absolute_variation(4.5, 6.0)
        -1.5000
    
    Interpretation:
        - Positive: CR increased (worsened)
        - Negative: CR decreased (improved)
        - Zero: No change
    """
    if cr_current is None or cr_previous is None:
        return None
    
    variation = cr_current - cr_previous
    return round(variation, 4)


# ══════════════════════════════════════════════════════════════════════════════
# RELATIVE VARIATION (%)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_relative_variation(cr_current, cr_previous):
    """
    Calculate relative variation in percentage
    
    Formula:
        Variation (%) = ((CR_current - CR_previous) / CR_previous) × 100
    
    Args:
        cr_current (float): Current period CR
        cr_previous (float): Previous period CR
    
    Returns:
        float: Relative variation in % (2 decimals)
               None if either CR is invalid or previous is 0
    
    Examples:
        >>> calculate_relative_variation(6.8, 5.2)
        30.77
        
        >>> calculate_relative_variation(4.5, 6.0)
        -25.00
    
    Interpretation:
        - > 0%: CR increased (worsened)
        - < 0%: CR decreased (improved)
        - > ±20%: Strong variation (threshold)
    """
    if cr_current is None or cr_previous is None:
        return None
    
    if cr_previous == 0:
        return None  # Cannot calculate (division by zero)
    
    variation_pct = ((cr_current - cr_previous) / cr_previous) * 100
    return round(variation_pct, 2)


# ══════════════════════════════════════════════════════════════════════════════
# VOLUME IMPACT
# ══════════════════════════════════════════════════════════════════════════════

def calculate_volume_impact(variation_pp, driver_current):
    """
    Calculate impact in absolute number of cases due to CR variation
    
    Formula:
        Impact = (Variation_pp / 100) × Driver_current
    
    Args:
        variation_pp (float): Absolute variation in pp
        driver_current (float): Current period driver
    
    Returns:
        float: Volume impact in number of cases (0 decimals)
               None if either value is invalid
    
    Examples:
        >>> calculate_volume_impact(1.6, 10000)
        160.0
        
        >>> calculate_volume_impact(-0.5, 5000)
        -25.0
    
    Interpretation:
        - Positive: Additional cases generated
        - Negative: Cases avoided (improvement)
        - Magnitude: Operational impact
    """
    if variation_pp is None or driver_current is None:
        return None
    
    if driver_current <= 0:
        return None
    
    impact = (variation_pp / 100) * driver_current
    return round(impact, 0)


# ══════════════════════════════════════════════════════════════════════════════
# BATCH VARIATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def calculate_variations_batch(data, group_cols=['SIT_SITE_ID'], 
                               period_col='PERIODO', cr_col='CR', driver_col='DRIVER'):
    """
    Calculate all variations for multiple rows (MoM)
    
    Args:
        data (pandas.DataFrame): DataFrame with CR data
        group_cols (list): Columns to group by (e.g., ['SIT_SITE_ID', 'AGRUP_COMMERCE'])
        period_col (str): Period column name
        cr_col (str): CR column name
        driver_col (str): Driver column name
    
    Returns:
        pandas.DataFrame: Original data with variation columns added:
            - CR_PREV: Previous period CR
            - VAR_ABS_PP: Absolute variation (pp)
            - VAR_REL_PCT: Relative variation (%)
            - VOLUME_IMPACT: Volume impact (cases)
    
    Example:
        >>> data = calculate_variations_batch(data, 
        ...                                   group_cols=['SIT_SITE_ID'],
        ...                                   period_col='PERIODO',
        ...                                   cr_col='CR',
        ...                                   driver_col='DRIVER')
        >>> print(data[['SIT_SITE_ID', 'PERIODO', 'CR', 'VAR_ABS_PP', 'VAR_REL_PCT']])
    """
    # Sort by groups and period
    data = data.sort_values(group_cols + [period_col])
    
    # Calculate previous period CR
    data['CR_PREV'] = data.groupby(group_cols)[cr_col].shift(1)
    
    # Calculate absolute variation
    data['VAR_ABS_PP'] = data.apply(
        lambda row: calculate_absolute_variation(row[cr_col], row['CR_PREV']),
        axis=1
    )
    
    # Calculate relative variation
    data['VAR_REL_PCT'] = data.apply(
        lambda row: calculate_relative_variation(row[cr_col], row['CR_PREV']),
        axis=1
    )
    
    # Calculate volume impact
    data['VOLUME_IMPACT'] = data.apply(
        lambda row: calculate_volume_impact(row['VAR_ABS_PP'], row[driver_col]),
        axis=1
    )
    
    return data


# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def classify_variation(var_rel_pct):
    """
    Classify variation magnitude
    
    Args:
        var_rel_pct (float): Relative variation in %
    
    Returns:
        str: Classification category
    
    Classification:
        - |var| > 20%: Strong
        - |var| > 10%: Moderate
        - |var| > 5%: Slight
        - |var| <= 5%: Stable
    """
    if var_rel_pct is None:
        return 'Unknown'
    
    abs_var = abs(var_rel_pct)
    
    if abs_var > STRONG_VARIATION_PCT:
        return 'Strong'
    elif abs_var > 10:
        return 'Moderate'
    elif abs_var > 5:
        return 'Slight'
    else:
        return 'Stable'


def classify_direction(var_abs_pp):
    """
    Classify variation direction
    
    Args:
        var_abs_pp (float): Absolute variation in pp
    
    Returns:
        str: Direction classification
    
    Classification:
        - var > 0.5: Increase (Worsening)
        - var < -0.5: Decrease (Improvement)
        - |var| <= 0.5: Stable
    """
    if var_abs_pp is None:
        return 'Unknown'
    
    if var_abs_pp > 0.5:
        return 'Increase (Worsening)'
    elif var_abs_pp < -0.5:
        return 'Decrease (Improvement)'
    else:
        return 'Stable'


# ══════════════════════════════════════════════════════════════════════════════
# TOP DRIVERS IDENTIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def identify_top_drivers(data, by='VAR_ABS_PP', top_n=10, ascending=False):
    """
    Identify top drivers of variation
    
    Args:
        data (pandas.DataFrame): DataFrame with variation data
        by (str): Column to sort by ('VAR_ABS_PP', 'VAR_REL_PCT', 'VOLUME_IMPACT')
        top_n (int): Number of top drivers to return
        ascending (bool): Sort ascending (True) or descending (False)
    
    Returns:
        pandas.DataFrame: Top N drivers sorted by specified metric
    
    Example:
        >>> top_drivers = identify_top_drivers(data, by='VOLUME_IMPACT', top_n=10, ascending=False)
        >>> print(top_drivers[['PROCESS_NAME', 'VAR_ABS_PP', 'VOLUME_IMPACT']])
    """
    # Remove rows without variation (first period of each group)
    data_with_var = data[data[by].notna()].copy()
    
    # Sort and take top N
    top_drivers = data_with_var.sort_values(by=by, ascending=ascending).head(top_n)
    
    return top_drivers


# ══════════════════════════════════════════════════════════════════════════════
# TREND ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def calculate_trend(data, group_cols=['SIT_SITE_ID'], period_col='PERIODO', cr_col='CR'):
    """
    Calculate linear trend for CR over time
    
    Args:
        data (pandas.DataFrame): DataFrame with CR data over multiple periods
        group_cols (list): Columns to group by
        period_col (str): Period column name
        cr_col (str): CR column name
    
    Returns:
        pandas.DataFrame: Trend summary with slope and R²
    
    Columns:
        - slope: Trend slope (pp per period)
        - intercept: Y-intercept
        - r_squared: R² (goodness of fit)
        - trend_label: 'Increasing', 'Decreasing', 'Stable'
    
    Example:
        >>> trends = calculate_trend(data, group_cols=['SIT_SITE_ID', 'AGRUP_COMMERCE'])
        >>> print(trends)
    """
    from scipy import stats
    
    trends = []
    
    for group, group_data in data.groupby(group_cols):
        # Sort by period
        group_data = group_data.sort_values(period_col)
        
        # Extract CR values (remove NaN)
        cr_values = group_data[cr_col].dropna().values
        
        if len(cr_values) < 2:
            # Not enough data for trend
            continue
        
        # X values: 0, 1, 2, ... (period indices)
        x_values = np.arange(len(cr_values))
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, cr_values)
        
        # Classify trend
        if slope > 0.1:
            trend_label = 'Increasing (Worsening)'
        elif slope < -0.1:
            trend_label = 'Decreasing (Improving)'
        else:
            trend_label = 'Stable'
        
        # Store result
        trend_result = {
            **{col: (group if isinstance(group, str) else group[i]) 
               for i, col in enumerate(group_cols)},
            'slope': round(slope, 4),
            'intercept': round(intercept, 4),
            'r_squared': round(r_value ** 2, 4),
            'p_value': round(p_value, 4),
            'trend_label': trend_label,
            'num_periods': len(cr_values)
        }
        trends.append(trend_result)
    
    return pd.DataFrame(trends)


# ══════════════════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Test absolute variation
    print("Testing calculate_absolute_variation():")
    print(f"  Var(6.8, 5.2) = {calculate_absolute_variation(6.8, 5.2)}")  # +1.6
    print(f"  Var(4.5, 6.0) = {calculate_absolute_variation(4.5, 6.0)}")  # -1.5
    
    # Test relative variation
    print("\nTesting calculate_relative_variation():")
    print(f"  Var%(6.8, 5.2) = {calculate_relative_variation(6.8, 5.2)}%")  # +30.77%
    print(f"  Var%(4.5, 6.0) = {calculate_relative_variation(4.5, 6.0)}%")  # -25.00%
    
    # Test volume impact
    print("\nTesting calculate_volume_impact():")
    print(f"  Impact(1.6, 10000) = {calculate_volume_impact(1.6, 10000)} cases")  # +160
    print(f"  Impact(-0.5, 5000) = {calculate_volume_impact(-0.5, 5000)} cases")  # -25
    
    # Test classification
    print("\nTesting classify_variation():")
    print(f"  Classify(25%) = {classify_variation(25)}")  # Strong
    print(f"  Classify(15%) = {classify_variation(15)}")  # Moderate
    print(f"  Classify(3%) = {classify_variation(3)}")   # Stable
    
    # Test batch calculation
    print("\nTesting calculate_variations_batch():")
    data = pd.DataFrame({
        'SIT_SITE_ID': ['MLA', 'MLA', 'MLA'],
        'PERIODO': ['2026-01', '2026-02', '2026-03'],
        'CR': [5.2, 6.8, 6.5],
        'DRIVER': [10000, 10500, 11000]
    })
    data = calculate_variations_batch(data, group_cols=['SIT_SITE_ID'])
    print(data[['PERIODO', 'CR', 'CR_PREV', 'VAR_ABS_PP', 'VAR_REL_PCT', 'VOLUME_IMPACT']])


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENTATION
# ══════════════════════════════════════════════════════════════════════════════

"""
USAGE EXAMPLES:

1. Calculate variations for DataFrame:
    >>> from variation_analysis import calculate_variations_batch
    >>> data = calculate_variations_batch(data, group_cols=['SIT_SITE_ID'])

2. Identify top drivers:
    >>> from variation_analysis import identify_top_drivers
    >>> top_10 = identify_top_drivers(data, by='VOLUME_IMPACT', top_n=10)

3. Classify variations:
    >>> from variation_analysis import classify_variation, classify_direction
    >>> magnitude = classify_variation(25.0)  # 'Strong'
    >>> direction = classify_direction(1.5)   # 'Increase (Worsening)'

4. Calculate trends:
    >>> from variation_analysis import calculate_trend
    >>> trends = calculate_trend(data, group_cols=['SIT_SITE_ID', 'AGRUP_COMMERCE'])

REFERENCES:
- Business context: /docs/business-context.md
- Metrics glossary: /docs/metrics-glossary.md
- Contact Rate calc: /calculations/contact-rate.py
"""
