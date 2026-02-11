"""
══════════════════════════════════════════════════════════════════════════════
PATTERN DETECTION - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: Detect anomalies and patterns in CR data (spikes, drops, etc.)
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

SPIKE_THRESHOLD_MULTIPLIER = 1.5       # 150% of average
DROP_THRESHOLD_MULTIPLIER = 0.5        # 50% of average
STRONG_VARIATION_PCT = 20              # ±20% MoM
CONCENTRATION_THRESHOLD_PCT = 30       # 30% volume in critical days
ROLLING_AVG_WINDOW = 7                 # 7 days rolling average
ROLLING_AVG_MIN_PERIODS = 3            # Minimum 3 days for rolling avg


# ══════════════════════════════════════════════════════════════════════════════
# SPIKE DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_spikes(data, value_col='CR', threshold_multiplier=SPIKE_THRESHOLD_MULTIPLIER,
                  rolling_window=ROLLING_AVG_WINDOW):
    """
    Detect spikes (sudden increases) in CR
    
    Criteria:
        CR > Rolling_Average × threshold_multiplier
    
    Args:
        data (pandas.DataFrame): DataFrame with CR values over time
        value_col (str): Column name with values to analyze
        threshold_multiplier (float): Spike threshold (default: 1.5 = 150%)
        rolling_window (int): Rolling average window (default: 7)
    
    Returns:
        pandas.DataFrame: Data with spike detection columns added
    """
    data = data.copy()
    
    # Calculate rolling average
    data['rolling_avg'] = data[value_col].rolling(
        window=rolling_window, 
        min_periods=ROLLING_AVG_MIN_PERIODS
    ).mean()
    
    # Detect spikes
    data['is_spike'] = data[value_col] > (data['rolling_avg'] * threshold_multiplier)
    data['spike_magnitude'] = (data[value_col] / data['rolling_avg']) - 1  # % over average
    
    return data


# ══════════════════════════════════════════════════════════════════════════════
# DROP DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_drops(data, value_col='CR', threshold_multiplier=DROP_THRESHOLD_MULTIPLIER,
                 rolling_window=ROLLING_AVG_WINDOW):
    """
    Detect drops (sudden decreases) in CR
    
    Criteria:
        CR < Rolling_Average × threshold_multiplier
    
    Args:
        data (pandas.DataFrame): DataFrame with CR values over time
        value_col (str): Column name with values to analyze
        threshold_multiplier (float): Drop threshold (default: 0.5 = 50%)
        rolling_window (int): Rolling average window (default: 7)
    
    Returns:
        pandas.DataFrame: Data with drop detection columns added
    """
    data = data.copy()
    
    # Calculate rolling average
    data['rolling_avg'] = data[value_col].rolling(
        window=rolling_window, 
        min_periods=ROLLING_AVG_MIN_PERIODS
    ).mean()
    
    # Detect drops
    data['is_drop'] = data[value_col] < (data['rolling_avg'] * threshold_multiplier)
    data['drop_magnitude'] = 1 - (data[value_col] / data['rolling_avg'])  # % below average
    
    return data


# ══════════════════════════════════════════════════════════════════════════════
# STRONG VARIATION DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_strong_variations(data, value_col='CR', var_pct_col='VAR_REL_PCT',
                             threshold_pct=STRONG_VARIATION_PCT):
    """
    Detect strong MoM variations
    
    Criteria:
        |Variation_%| > threshold_pct
    
    Args:
        data (pandas.DataFrame): DataFrame with variation data
        value_col (str): Column name with CR values
        var_pct_col (str): Column name with relative variation (%)
        threshold_pct (float): Threshold for strong variation (default: 20%)
    
    Returns:
        pandas.DataFrame: Data with strong_variation flag added
    """
    data = data.copy()
    
    # Detect strong variations
    data['is_strong_variation'] = data[var_pct_col].abs() > threshold_pct
    
    return data


# ══════════════════════════════════════════════════════════════════════════════
# CONCENTRATION DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_temporal_concentration(data, date_col='CONTACT_DATE_ID', value_col='CANT_CASES',
                                  group_cols=['SIT_SITE_ID', 'MES'], top_n_days=3,
                                  threshold_pct=CONCENTRATION_THRESHOLD_PCT):
    """
    Detect temporal concentration (volume concentrated in specific days)
    
    Criteria:
        Top N days represent > threshold_pct% of total volume
    
    Args:
        data (pandas.DataFrame): DataFrame with daily data
        date_col (str): Date column name
        value_col (str): Value column name (e.g., 'CANT_CASES')
        group_cols (list): Columns to group by
        top_n_days (int): Number of top days to check (default: 3)
        threshold_pct (float): Threshold percentage (default: 30%)
    
    Returns:
        pandas.DataFrame: Concentration summary
    """
    concentrations = []
    
    for group, group_data in data.groupby(group_cols):
        # Total volume
        total_volume = group_data[value_col].sum()
        
        if total_volume == 0:
            continue
        
        # Top N days
        top_days = group_data.nlargest(top_n_days, value_col)
        top_volume = top_days[value_col].sum()
        concentration_pct = (top_volume / total_volume) * 100
        
        # Detect concentration
        is_concentrated = concentration_pct > threshold_pct
        
        # Store result
        result = {
            **{col: (group if isinstance(group, str) else group[i]) 
               for i, col in enumerate(group_cols)},
            'total_volume': total_volume,
            'top_volume': top_volume,
            'concentration_pct': round(concentration_pct, 2),
            'is_concentrated': is_concentrated,
            'top_days': top_days[date_col].tolist()
        }
        concentrations.append(result)
    
    return pd.DataFrame(concentrations)


# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE PATTERN DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_patterns(data, value_col='CR', var_pct_col='VAR_REL_PCT',
                    rolling_window=ROLLING_AVG_WINDOW):
    """
    Comprehensive pattern detection (spikes, drops, strong variations)
    
    Args:
        data (pandas.DataFrame): DataFrame with CR and variation data
        value_col (str): CR column name
        var_pct_col (str): Variation % column name
        rolling_window (int): Rolling average window
    
    Returns:
        dict: Pattern summary with detected patterns
    """
    results = {}
    
    # Detect spikes
    data_with_spikes = detect_spikes(data, value_col=value_col, rolling_window=rolling_window)
    spikes = data_with_spikes[data_with_spikes['is_spike'] == True]
    results['spikes'] = {
        'count': len(spikes),
        'data': spikes.to_dict('records')
    }
    
    # Detect drops
    data_with_drops = detect_drops(data, value_col=value_col, rolling_window=rolling_window)
    drops = data_with_drops[data_with_drops['is_drop'] == True]
    results['drops'] = {
        'count': len(drops),
        'data': drops.to_dict('records')
    }
    
    # Detect strong variations
    if var_pct_col in data.columns:
        data_with_variations = detect_strong_variations(data, value_col=value_col, var_pct_col=var_pct_col)
        strong_vars = data_with_variations[data_with_variations['is_strong_variation'] == True]
        results['strong_variations'] = {
            'count': len(strong_vars),
            'data': strong_vars.to_dict('records')
        }
    
    return results


# ══════════════════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Testing pattern detection...")
    
    # Sample data
    data = pd.DataFrame({
        'DAY': range(1, 11),
        'CR': [5.0, 5.2, 5.1, 8.5, 5.3, 5.0, 2.0, 5.1, 5.2, 5.0],
        'VAR_REL_PCT': [None, 4.0, -1.9, 66.7, -37.6, -5.7, -60.0, 155.0, 1.96, -3.8]
    })
    
    # Detect spikes
    data = detect_spikes(data)
    print("\nSpikes detected:")
    print(data[data['is_spike'] == True][['DAY', 'CR', 'rolling_avg', 'spike_magnitude']])
    
    # Detect drops
    data = detect_drops(data)
    print("\nDrops detected:")
    print(data[data['is_drop'] == True][['DAY', 'CR', 'rolling_avg', 'drop_magnitude']])
