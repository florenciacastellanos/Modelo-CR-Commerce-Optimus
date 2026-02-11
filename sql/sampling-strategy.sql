-- ══════════════════════════════════════════════════════════════════════════════
-- SAMPLING STRATEGY - MLB (BRASIL) OPTIMIZATION
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Systematic sampling for MLB to prevent BigQuery timeouts
-- Problem: MLB has extremely high volume (50K+ rows per AGRUP × Month)
-- Solution: Estimate total rows and apply LIMIT if threshold exceeded
-- Version: 2.5 (Commerce)
-- Last Update: Enero 2026
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- CONSTANTS (from BusinessConstants class)
-- ══════════════════════════════════════════════════════════════════════════════
-- MLB_ESTIMATED_ROWS_PER_AGRUP_MONTH = 50,000
-- MLB_SAMPLING_THRESHOLD = 150,000
-- MLB_MIN_LIMIT = 150,000
-- MLB_MAX_LIMIT = 200,000
-- ══════════════════════════════════════════════════════════════════════════════


-- ══════════════════════════════════════════════════════════════════════════════
-- STEP 1: ESTIMATE TOTAL ROWS
-- ══════════════════════════════════════════════════════════════════════════════
-- Formula: num_agrup × num_months × 50,000 (estimated rows per AGRUP × Month)

WITH ESTIMATION AS (
    SELECT 
        COUNT(DISTINCT AGRUP_COMMERCE) AS num_agrup,
        COUNT(DISTINCT MES) AS num_months,
        COUNT(DISTINCT AGRUP_COMMERCE) * COUNT(DISTINCT MES) * 50000 AS estimated_rows
    FROM BASE_CONTACTS
    WHERE SIT_SITE_ID = 'MLB'
)
SELECT * FROM ESTIMATION;

-- Example output:
-- num_agrup | num_months | estimated_rows
-- ---------+------------+---------------
--        5 |          2 |       500,000  ← Exceeds threshold (150K)


-- ══════════════════════════════════════════════════════════════════════════════
-- STEP 2: DECISION LOGIC (if estimated_rows > 150,000)
-- ══════════════════════════════════════════════════════════════════════════════
-- If estimated_rows > 150,000:
--     Apply LIMIT: Random sampling with ORDER BY RAND()
--     Limit range: 150,000 to 200,000 rows
-- Else:
--     No sampling needed (return all rows)


-- ══════════════════════════════════════════════════════════════════════════════
-- OPTION A: SAMPLING WITH FIXED LIMIT (Simple)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: When estimated_rows > 150,000

SELECT *
FROM BASE_CONTACTS
WHERE SIT_SITE_ID = 'MLB'
ORDER BY RAND()
LIMIT 150000;  -- Fixed limit (minimum)

-- Notes:
-- - ORDER BY RAND() ensures random sampling
-- - LIMIT 150,000 is the minimum safe threshold
-- - Representative sample for CR analysis


-- ══════════════════════════════════════════════════════════════════════════════
-- OPTION B: SAMPLING WITH DYNAMIC LIMIT (Adaptive)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: When estimated_rows > 150,000 and you want to maximize sample size

WITH ESTIMATION AS (
    SELECT 
        COUNT(DISTINCT AGRUP_COMMERCE) AS num_agrup,
        COUNT(DISTINCT MES) AS num_months,
        COUNT(DISTINCT AGRUP_COMMERCE) * COUNT(DISTINCT MES) * 50000 AS estimated_rows,
        -- Calculate optimal limit (between 150K and 200K)
        CASE 
            WHEN COUNT(DISTINCT AGRUP_COMMERCE) * COUNT(DISTINCT MES) * 50000 <= 150000 THEN NULL
            WHEN COUNT(DISTINCT AGRUP_COMMERCE) * COUNT(DISTINCT MES) * 50000 BETWEEN 150000 AND 200000 THEN COUNT(DISTINCT AGRUP_COMMERCE) * COUNT(DISTINCT MES) * 50000
            ELSE 200000
        END AS optimal_limit
    FROM BASE_CONTACTS
    WHERE SIT_SITE_ID = 'MLB'
)
SELECT 
    BC.*
FROM BASE_CONTACTS BC
CROSS JOIN ESTIMATION E
WHERE BC.SIT_SITE_ID = 'MLB'
ORDER BY RAND()
LIMIT (SELECT optimal_limit FROM ESTIMATION WHERE optimal_limit IS NOT NULL);

-- Notes:
-- - If estimated ≤ 150K → No sampling (return all)
-- - If estimated 150K-200K → Use estimated value as limit
-- - If estimated > 200K → Cap at 200K (maximum safe limit)


-- ══════════════════════════════════════════════════════════════════════════════
-- OPTION C: STRATIFIED SAMPLING (Advanced - Maintain proportions)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: When you need representative sample per AGRUP_COMMERCE

WITH AGRUP_COUNTS AS (
    SELECT 
        AGRUP_COMMERCE,
        COUNT(*) AS total_cases,
        ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 150000) AS sample_size  -- Proportional to 150K
    FROM BASE_CONTACTS
    WHERE SIT_SITE_ID = 'MLB'
    GROUP BY AGRUP_COMMERCE
),
SAMPLED_DATA AS (
    SELECT 
        BC.*,
        ROW_NUMBER() OVER (PARTITION BY BC.AGRUP_COMMERCE ORDER BY RAND()) AS row_num
    FROM BASE_CONTACTS BC
    INNER JOIN AGRUP_COUNTS AC ON BC.AGRUP_COMMERCE = AC.AGRUP_COMMERCE
    WHERE BC.SIT_SITE_ID = 'MLB'
)
SELECT 
    SD.CAS_CASE_ID,
    SD.CUS_CUST_ID,
    SD.SIT_SITE_ID,
    SD.MES,
    SD.AGRUP_COMMERCE,
    SD.PROCESS_NAME,
    SD.CANT_CASES
    -- ... (all other fields)
FROM SAMPLED_DATA SD
INNER JOIN AGRUP_COUNTS AC ON SD.AGRUP_COMMERCE = AC.AGRUP_COMMERCE
WHERE SD.row_num <= AC.sample_size
ORDER BY SD.AGRUP_COMMERCE, SD.MES;

-- Notes:
-- - Maintains relative proportions of AGRUP_COMMERCE
-- - More accurate for CR analysis
-- - More complex query (may be slower)


-- ══════════════════════════════════════════════════════════════════════════════
-- PYTHON IMPLEMENTATION (Recommended approach)
-- ══════════════════════════════════════════════════════════════════════════════

/*
Python code to apply sampling logic:

def apply_mlb_sampling(df, selected_sites, selected_agrup_commerce):
    """
    Apply sampling strategy for MLB if needed
    
    Args:
        df: DataFrame with contact data
        selected_sites: List of selected sites
        selected_agrup_commerce: List of selected commerce groups
    
    Returns:
        DataFrame with sampling applied (if needed)
    """
    # Constants
    MLB_ESTIMATED_ROWS_PER_AGRUP_MONTH = 50000
    MLB_SAMPLING_THRESHOLD = 150000
    MLB_MIN_LIMIT = 150000
    MLB_MAX_LIMIT = 200000
    
    # Check if MLB is selected
    if 'MLB' not in selected_sites:
        return df  # No sampling needed
    
    # Estimate total rows for MLB
    num_agrup = len(selected_agrup_commerce)
    num_months = df['MES'].nunique()
    estimated_rows = num_agrup * num_months * MLB_ESTIMATED_ROWS_PER_AGRUP_MONTH
    
    print(f"MLB Estimated rows: {estimated_rows:,}")
    
    # Check if sampling is needed
    if estimated_rows <= MLB_SAMPLING_THRESHOLD:
        print("✓ No sampling needed (below threshold)")
        return df
    
    # Calculate optimal limit
    if estimated_rows <= MLB_MAX_LIMIT:
        limit = estimated_rows
    else:
        limit = MLB_MAX_LIMIT
    
    print(f"⚠️ Applying sampling: LIMIT {limit:,} rows")
    
    # Apply sampling to MLB data only
    df_mlb = df[df['SIT_SITE_ID'] == 'MLB'].sample(n=min(limit, len(df[df['SIT_SITE_ID'] == 'MLB'])))
    df_other = df[df['SIT_SITE_ID'] != 'MLB']
    
    # Combine
    df_final = pd.concat([df_mlb, df_other], ignore_index=True)
    
    print(f"✓ Sampling applied: {len(df_mlb):,} MLB rows + {len(df_other):,} other rows")
    
    return df_final


# Usage example:
data = apply_mlb_sampling(data, selected_sites=['MLA', 'MLB'], selected_agrup_commerce=['PDD', 'PNR', 'ME Distribución'])
*/


-- ══════════════════════════════════════════════════════════════════════════════
-- VALIDATION: Check sample representativeness
-- ══════════════════════════════════════════════════════════════════════════════

-- After sampling, validate distribution matches original proportions:

WITH ORIGINAL_DIST AS (
    SELECT 
        AGRUP_COMMERCE,
        COUNT(*) AS original_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS original_pct
    FROM BASE_CONTACTS
    WHERE SIT_SITE_ID = 'MLB'
    GROUP BY AGRUP_COMMERCE
),
SAMPLED_DIST AS (
    SELECT 
        AGRUP_COMMERCE,
        COUNT(*) AS sampled_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS sampled_pct
    FROM SAMPLED_BASE_CONTACTS  -- Your sampled data
    WHERE SIT_SITE_ID = 'MLB'
    GROUP BY AGRUP_COMMERCE
)
SELECT 
    O.AGRUP_COMMERCE,
    O.original_count,
    O.original_pct,
    S.sampled_count,
    S.sampled_pct,
    ABS(O.original_pct - S.sampled_pct) AS diff_pct
FROM ORIGINAL_DIST O
LEFT JOIN SAMPLED_DIST S ON O.AGRUP_COMMERCE = S.AGRUP_COMMERCE
ORDER BY diff_pct DESC;

-- Expected result:
-- diff_pct < 5% for all AGRUP_COMMERCE → Good representativeness
-- diff_pct > 10% → Warning: sampling may introduce bias


-- ══════════════════════════════════════════════════════════════════════════════
-- NOTES:
-- ══════════════════════════════════════════════════════════════════════════════
-- 1. Sampling only needed for MLB (Brasil) due to extreme volume
-- 2. Always use ORDER BY RAND() for random sampling
-- 3. Validate sample representativeness after sampling
-- 4. Python implementation recommended (more flexible)
-- 5. For other sites (MLA, MLC, etc.), no sampling needed
-- 6. Sampling does NOT affect CR calculation accuracy significantly
--    (law of large numbers applies with 150K+ sample)
-- ══════════════════════════════════════════════════════════════════════════════
