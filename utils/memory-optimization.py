"""
══════════════════════════════════════════════════════════════════════════════
MEMORY OPTIMIZATION - CONTACT RATE COMMERCE
══════════════════════════════════════════════════════════════════════════════
Description: Memory optimization for large DataFrames
Savings: 50-70% memory reduction
Version: 2.5 (Commerce)
Last Update: Enero 2026
══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import gc


MEMORY_OPTIMIZATION_THRESHOLD = 50000  # Rows threshold


def optimize_dataframe_memory(df):
    """
    Reduce DataFrame memory usage by 50-70%
    
    Optimizations:
    1. String → Category (if < 50% unique values)
    2. Int downcast (int64 → int32/int16/int8)
    3. Float downcast (float64 → float32)
    
    Args:
        df (pandas.DataFrame): DataFrame to optimize
    
    Returns:
        pandas.DataFrame: Optimized DataFrame
    
    Example:
        >>> df = optimize_dataframe_memory(df)
        💾 Optimizing memory (initial: 150.5 MB)...
        ✅ Memory optimized (final: 45.2 MB | saved: 105.3 MB)
    """
    
    if df is None or len(df) == 0:
        return df
    
    initial_memory = df.memory_usage(deep=True).sum() / 1024**2
    print(f"  💾 Optimizing memory (initial: {initial_memory:.1f} MB)...")
    
    # 1. String → Category (if < 50% unique)
    for col in df.columns:
        if df[col].dtype == 'object':
            num_unique = df[col].nunique()
            num_total = len(df[col])
            if num_unique / num_total < 0.5:
                df[col] = df[col].astype('category')
    
    # 2. Int downcast
    for col in df.select_dtypes(include=['int']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # 3. Float downcast
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    final_memory = df.memory_usage(deep=True).sum() / 1024**2
    saved = initial_memory - final_memory
    print(f"  ✅ Memory optimized (final: {final_memory:.1f} MB | saved: {saved:.1f} MB)")
    
    # Force garbage collection
    gc.collect()
    
    return df
