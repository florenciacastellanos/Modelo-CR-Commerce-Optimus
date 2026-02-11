-- ══════════════════════════════════════════════════════════════════════════════
-- AGGREGATION QUERIES - CONTACT RATE COMMERCE
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Common aggregation patterns for CR analysis
-- Base: Assumes BASE_CONTACTS CTE exists (from base-query.sql)
-- Version: 2.5 (Commerce)
-- Last Update: Enero 2026
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- 1. AGGREGATION BY SITE AND PERIOD
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Calculate total incoming cases by Site × Period

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    COUNT(DISTINCT CUS_CUST_ID) AS UNIQUE_CUSTOMERS,
    SUM(INCOMING_NO_CONFLICT) AS INCOMING_NO_CONFLICT,
    SUM(INCOMING_CONFLICT) AS INCOMING_CONFLICT
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES
ORDER BY SIT_SITE_ID, MES;


-- ══════════════════════════════════════════════════════════════════════════════
-- 2. AGGREGATION BY PROCESS (Dimension: PROCESS)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR drivers by specific process

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    PROCESS_NAME,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    COUNT(DISTINCT CUS_CUST_ID) AS UNIQUE_CUSTOMERS,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, PROCESS_NAME
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 3. AGGREGATION BY CDU (Dimension: CDU - Caso de Uso)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR drivers by use case

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    CDU,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
WHERE CDU IS NOT NULL
GROUP BY SIT_SITE_ID, MES, CDU
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 4. AGGREGATION BY REASON DETAIL (Dimension: REASON_DETAIL)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR drivers by detailed reason

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    REASON_DETAIL_GROUP_REPORTING,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
WHERE REASON_DETAIL_GROUP_REPORTING IS NOT NULL
GROUP BY SIT_SITE_ID, MES, REASON_DETAIL_GROUP_REPORTING
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 5. AGGREGATION BY COMMERCE GROUP (Dimension: COMMERCE_GROUP)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR distribution by Commerce Group

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    AGRUP_COMMERCE,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    COUNT(DISTINCT PROCESS_NAME) AS PROCESS_COUNT,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, AGRUP_COMMERCE
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 6. AGGREGATION BY ENVIRONMENT (Dimension: ENVIRONMENT)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR by logistic environment

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    ENVIRONMENT,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
WHERE ENVIRONMENT IS NOT NULL
GROUP BY SIT_SITE_ID, MES, ENVIRONMENT
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 7. AGGREGATION BY USER TYPE (Dimension: USER_TYPE)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR by user type (Comprador, Vendedor, Cuenta, Driver)

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    PROCESS_GROUP_ECOMMERCE AS USER_TYPE,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    COUNT(DISTINCT CUS_CUST_ID) AS UNIQUE_CUSTOMERS,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, PROCESS_GROUP_ECOMMERCE
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 8. AGGREGATION BY REPORTING TYPE (Dimension: REPORTING_TYPE)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze CR by problematic reporting type

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    PROBLEMATIC_REPORTING,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
FROM BASE_CONTACTS
WHERE PROBLEMATIC_REPORTING IS NOT NULL
GROUP BY SIT_SITE_ID, MES, PROBLEMATIC_REPORTING
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 9. DAILY DISTRIBUTION (Temporal Analysis)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze daily distribution to detect concentration patterns

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    EXTRACT(DAY FROM CONTACT_DATE_ID) AS DAY_OF_MONTH,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, DAY_OF_MONTH
ORDER BY SIT_SITE_ID, MES, DAY_OF_MONTH;


-- ══════════════════════════════════════════════════════════════════════════════
-- 10. MULTI-DIMENSIONAL AGGREGATION (Process × Commerce Group)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Detailed analysis by Process within Commerce Group

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    AGRUP_COMMERCE,
    PROCESS_NAME,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES, AGRUP_COMMERCE), 2) AS PCT_OF_COMMERCE_GROUP
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, AGRUP_COMMERCE, PROCESS_NAME
HAVING SUM(CANT_CASES) >= 100  -- Threshold: minimum 100 cases
ORDER BY SIT_SITE_ID, MES, AGRUP_COMMERCE, INCOMING_CASES DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 11. TOP N PROCESSES (Pareto Analysis)
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Identify top processes that drive CR

WITH PROCESS_AGG AS (
    SELECT 
        SIT_SITE_ID,
        MES AS PERIODO,
        PROCESS_NAME,
        SUM(CANT_CASES) AS INCOMING_CASES,
        ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (PARTITION BY SIT_SITE_ID, MES), 2) AS PCT_OF_TOTAL
    FROM BASE_CONTACTS
    GROUP BY SIT_SITE_ID, MES, PROCESS_NAME
    HAVING SUM(CANT_CASES) >= 100
),
RANKED_PROCESSES AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY SIT_SITE_ID, PERIODO ORDER BY INCOMING_CASES DESC) AS RANK,
        SUM(PCT_OF_TOTAL) OVER (PARTITION BY SIT_SITE_ID, PERIODO ORDER BY INCOMING_CASES DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CUMULATIVE_PCT
    FROM PROCESS_AGG
)
SELECT 
    SIT_SITE_ID,
    PERIODO,
    PROCESS_NAME,
    INCOMING_CASES,
    PCT_OF_TOTAL,
    CUMULATIVE_PCT,
    RANK
FROM RANKED_PROCESSES
WHERE RANK <= 10  -- Top 10 processes
ORDER BY SIT_SITE_ID, PERIODO, RANK;


-- ══════════════════════════════════════════════════════════════════════════════
-- 12. AUTOMATION RATE ANALYSIS
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Measure automation effectiveness

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    AGRUP_COMMERCE,
    SUM(CANT_CASES) AS TOTAL_CASES,
    SUM(CASE WHEN FLAG_AUTO = 1 THEN CANT_CASES ELSE 0 END) AS AUTO_CASES,
    ROUND(100.0 * SUM(CASE WHEN FLAG_AUTO = 1 THEN CANT_CASES ELSE 0 END) / SUM(CANT_CASES), 2) AS AUTO_RATE_PCT
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, AGRUP_COMMERCE
HAVING SUM(CANT_CASES) >= 100
ORDER BY SIT_SITE_ID, MES, AUTO_RATE_PCT DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- 13. CONFLICT VS NON-CONFLICT DISTRIBUTION
-- ══════════════════════════════════════════════════════════════════════════════
-- Use: Analyze severity of contacts (conflicts are more serious)

SELECT 
    SIT_SITE_ID,
    MES AS PERIODO,
    AGRUP_COMMERCE,
    SUM(INCOMING_NO_CONFLICT) AS NO_CONFLICT_CASES,
    SUM(INCOMING_CONFLICT) AS CONFLICT_CASES,
    SUM(CANT_CASES) AS TOTAL_CASES,
    ROUND(100.0 * SUM(INCOMING_CONFLICT) / SUM(CANT_CASES), 2) AS CONFLICT_RATE_PCT
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, AGRUP_COMMERCE
HAVING SUM(CANT_CASES) >= 100
ORDER BY SIT_SITE_ID, MES, CONFLICT_RATE_PCT DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- NOTES:
-- ══════════════════════════════════════════════════════════════════════════════
-- 1. All queries assume BASE_CONTACTS CTE exists (from base-query.sql)
-- 2. Default threshold: 100 cases (HAVING clause)
-- 3. Adjust threshold per dimension as needed
-- 4. Use PCT_OF_TOTAL for relative importance
-- 5. Pareto analysis (query 11) helps prioritize initiatives
-- 6. Temporal analysis (query 9) helps detect patterns
-- ══════════════════════════════════════════════════════════════════════════════
