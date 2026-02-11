"""
══════════════════════════════════════════════════════════════════════════════
CONTACT RATE CALCULATION - COMMERCE v2.5
══════════════════════════════════════════════════════════════════════════════
Description: Core calculation logic for Contact Rate (CR)
Formula: CR = (Incoming Cases / Driver) × 100
Result: Percentage points (pp)
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

CR_MULTIPLIER = 100  # Conversion to percentage points
CR_DECIMALS = 4  # Number of decimal places


# ══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def calculate_contact_rate(incoming, driver):
    """
    Calculate Contact Rate in percentage points (pp)
    
    Formula:
        CR = (Incoming Cases / Driver) × 100
    
    Args:
        incoming (float): Total incoming cases (numerator)
        driver (float): Driver value (denominator)
    
    Returns:
        float: Contact Rate in percentage points (pp) with 4 decimals
               None if driver is 0 or invalid
    
    Examples:
        >>> calculate_contact_rate(150, 10000)
        1.5000
        
        >>> calculate_contact_rate(50, 1000)
        5.0000
        
        >>> calculate_contact_rate(0, 1000)
        0.0000
        
        >>> calculate_contact_rate(100, 0)
        None
    
    Notes:
        - Result is in percentage points (pp), not percentage (%)
        - Example: CR = 1.5 pp means 1.5 out of 100 events generate contact
        - Lower CR is better (less problems)
        - Higher CR is worse (more problems)
    """
    # Validate driver
    if driver is None or driver <= 0:
        return None
    
    # Validate incoming (allow 0)
    if incoming is None:
        return None
    
    # Calculate CR
    cr = (incoming / driver) * CR_MULTIPLIER
    
    # Round to specified decimals
    return round(cr, CR_DECIMALS)


# ══════════════════════════════════════════════════════════════════════════════
# BATCH CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def calculate_contact_rate_batch(data, incoming_col='INCOMING_CASES', 
                                  driver_col='DRIVER', output_col='CR'):
    """
    Calculate Contact Rate for multiple rows in a DataFrame
    
    Args:
        data (pandas.DataFrame): DataFrame with incoming and driver columns
        incoming_col (str): Name of incoming cases column
        driver_col (str): Name of driver column
        output_col (str): Name of output CR column
    
    Returns:
        pandas.DataFrame: Original DataFrame with CR column added
    
    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     'SITE': ['MLA', 'MLC'],
        ...     'PERIODO': ['2026-01', '2026-01'],
        ...     'INCOMING_CASES': [150, 50],
        ...     'DRIVER': [10000, 2000]
        ... })
        >>> data = calculate_contact_rate_batch(data)
        >>> print(data)
           SITE  PERIODO  INCOMING_CASES  DRIVER      CR
        0  MLA  2026-01             150   10000  1.5000
        1  MLC  2026-01              50    2000  2.5000
    """
    import pandas as pd
    
    # Validate columns exist
    if incoming_col not in data.columns:
        raise ValueError(f"Column '{incoming_col}' not found in DataFrame")
    if driver_col not in data.columns:
        raise ValueError(f"Column '{driver_col}' not found in DataFrame")
    
    # Calculate CR
    data[output_col] = data.apply(
        lambda row: calculate_contact_rate(row[incoming_col], row[driver_col]),
        axis=1
    )
    
    return data


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate_contact_rate(cr, min_expected=0.1, max_expected=20.0):
    """
    Validate Contact Rate value is within expected range
    
    Args:
        cr (float): Contact Rate value
        min_expected (float): Minimum expected CR (default: 0.1 pp)
        max_expected (float): Maximum expected CR (default: 20.0 pp)
    
    Returns:
        tuple: (is_valid, message)
    
    Examples:
        >>> validate_contact_rate(5.0)
        (True, 'CR within expected range')
        
        >>> validate_contact_rate(0.05)
        (False, 'CR too low - possible data issue')
        
        >>> validate_contact_rate(25.0)
        (False, 'CR too high - possible data issue')
    """
    if cr is None:
        return (False, 'CR is None - check driver value')
    
    if cr < 0:
        return (False, 'CR is negative - invalid calculation')
    
    if cr < min_expected:
        return (False, f'CR too low ({cr:.4f} pp < {min_expected} pp) - possible data issue')
    
    if cr > max_expected:
        return (False, f'CR too high ({cr:.4f} pp > {max_expected} pp) - possible data issue')
    
    return (True, 'CR within expected range')


def validate_contact_rate_batch(data, cr_col='CR', min_expected=0.1, max_expected=20.0):
    """
    Validate Contact Rate values for multiple rows
    
    Args:
        data (pandas.DataFrame): DataFrame with CR column
        cr_col (str): Name of CR column
        min_expected (float): Minimum expected CR
        max_expected (float): Maximum expected CR
    
    Returns:
        dict: Validation summary with counts and invalid rows
    
    Example:
        >>> validation = validate_contact_rate_batch(data)
        >>> print(validation)
        {
            'total_rows': 100,
            'valid_rows': 95,
            'invalid_rows': 5,
            'null_rows': 2,
            'too_low': 1,
            'too_high': 2,
            'invalid_data': [...]  # List of invalid rows
        }
    """
    import pandas as pd
    
    # Validate column exists
    if cr_col not in data.columns:
        raise ValueError(f"Column '{cr_col}' not found in DataFrame")
    
    # Initialize summary
    summary = {
        'total_rows': len(data),
        'valid_rows': 0,
        'invalid_rows': 0,
        'null_rows': 0,
        'too_low': 0,
        'too_high': 0,
        'negative': 0,
        'invalid_data': []
    }
    
    # Validate each row
    for idx, row in data.iterrows():
        cr = row[cr_col]
        is_valid, message = validate_contact_rate(cr, min_expected, max_expected)
        
        if is_valid:
            summary['valid_rows'] += 1
        else:
            summary['invalid_rows'] += 1
            
            # Categorize error
            if cr is None:
                summary['null_rows'] += 1
            elif cr < 0:
                summary['negative'] += 1
            elif cr < min_expected:
                summary['too_low'] += 1
            elif cr > max_expected:
                summary['too_high'] += 1
            
            # Store invalid row
            summary['invalid_data'].append({
                'index': idx,
                'cr': cr,
                'message': message,
                'row_data': row.to_dict()
            })
    
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# INTERPRETATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def interpret_contact_rate(cr):
    """
    Provide human-readable interpretation of CR value
    
    Args:
        cr (float): Contact Rate value
    
    Returns:
        str: Interpretation message
    
    Examples:
        >>> interpret_contact_rate(0.5)
        'Excellent - 0.5 contacts per 100 events'
        
        >>> interpret_contact_rate(2.0)
        'Good - 2.0 contacts per 100 events'
        
        >>> interpret_contact_rate(8.0)
        'Poor - 8.0 contacts per 100 events'
    """
    if cr is None:
        return 'N/A - Cannot calculate CR (invalid driver)'
    
    if cr < 0:
        return 'Invalid - Negative CR'
    
    if cr < 1.0:
        return f'Excellent - {cr:.1f} contacts per 100 events'
    elif cr < 2.0:
        return f'Very Good - {cr:.1f} contacts per 100 events'
    elif cr < 3.0:
        return f'Good - {cr:.1f} contacts per 100 events'
    elif cr < 5.0:
        return f'Fair - {cr:.1f} contacts per 100 events'
    elif cr < 8.0:
        return f'Poor - {cr:.1f} contacts per 100 events'
    else:
        return f'Critical - {cr:.1f} contacts per 100 events (requires immediate action)'


# ══════════════════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Test basic calculation
    print("Testing calculate_contact_rate():")
    print(f"  CR(150, 10000) = {calculate_contact_rate(150, 10000)}")  # Expected: 1.5000
    print(f"  CR(50, 1000) = {calculate_contact_rate(50, 1000)}")      # Expected: 5.0000
    print(f"  CR(0, 1000) = {calculate_contact_rate(0, 1000)}")        # Expected: 0.0000
    print(f"  CR(100, 0) = {calculate_contact_rate(100, 0)}")          # Expected: None
    
    # Test validation
    print("\nTesting validate_contact_rate():")
    print(f"  Validate(5.0): {validate_contact_rate(5.0)}")
    print(f"  Validate(0.05): {validate_contact_rate(0.05)}")
    print(f"  Validate(25.0): {validate_contact_rate(25.0)}")
    
    # Test interpretation
    print("\nTesting interpret_contact_rate():")
    print(f"  CR 0.5: {interpret_contact_rate(0.5)}")
    print(f"  CR 2.0: {interpret_contact_rate(2.0)}")
    print(f"  CR 8.0: {interpret_contact_rate(8.0)}")
    
    # Test batch calculation
    print("\nTesting calculate_contact_rate_batch():")
    import pandas as pd
    data = pd.DataFrame({
        'SITE': ['MLA', 'MLC', 'MCO'],
        'PERIODO': ['2026-01', '2026-01', '2026-01'],
        'INCOMING_CASES': [150, 50, 200],
        'DRIVER': [10000, 2000, 15000]
    })
    data = calculate_contact_rate_batch(data)
    print(data)
    
    # Test batch validation
    print("\nTesting validate_contact_rate_batch():")
    validation = validate_contact_rate_batch(data)
    print(f"  Total rows: {validation['total_rows']}")
    print(f"  Valid rows: {validation['valid_rows']}")
    print(f"  Invalid rows: {validation['invalid_rows']}")


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENTATION
# ══════════════════════════════════════════════════════════════════════════════

"""
USAGE EXAMPLES:

1. Basic calculation:
    >>> from contact_rate import calculate_contact_rate
    >>> cr = calculate_contact_rate(incoming=150, driver=10000)
    >>> print(f"Contact Rate: {cr} pp")
    Contact Rate: 1.5000 pp

2. Batch calculation (pandas DataFrame):
    >>> import pandas as pd
    >>> from contact_rate import calculate_contact_rate_batch
    >>> 
    >>> data = pd.DataFrame({
    ...     'SITE': ['MLA', 'MLB', 'MLC'],
    ...     'INCOMING': [150, 500, 50],
    ...     'DRIVER': [10000, 50000, 2000]
    ... })
    >>> 
    >>> data = calculate_contact_rate_batch(data, 
    ...                                     incoming_col='INCOMING', 
    ...                                     driver_col='DRIVER', 
    ...                                     output_col='CR')
    >>> print(data)

3. Validation:
    >>> from contact_rate import validate_contact_rate
    >>> is_valid, message = validate_contact_rate(5.0)
    >>> if not is_valid:
    ...     print(f"Warning: {message}")

4. Interpretation:
    >>> from contact_rate import interpret_contact_rate
    >>> interpretation = interpret_contact_rate(2.5)
    >>> print(interpretation)
    Good - 2.5 contacts per 100 events

REFERENCES:
- Business context: /docs/business-context.md
- Metrics glossary: /docs/metrics-glossary.md
- Config constants: /config/business-constants.py
"""
