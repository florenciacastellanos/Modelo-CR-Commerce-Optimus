-- ══════════════════════════════════════════════════════════════════════════════
-- ENVIRONMENT FILTERS - CONTACT RATE COMMERCE
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Logistic environment filter examples
-- Available Environments: DS, FBM, FLEX, XD, MP_ON, MP_OFF
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- 1. SINGLE ENVIRONMENT (Drop Shipping)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.ENVIRONMENT = 'DS'

-- ══════════════════════════════════════════════════════════════════════════════
-- 2. MULTIPLE ENVIRONMENTS (FBM + FLEX)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.ENVIRONMENT IN ('FBM', 'FLEX')

-- ══════════════════════════════════════════════════════════════════════════════
-- 3. FULFILLMENT ENVIRONMENTS (FBM + FLEX + XD)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.ENVIRONMENT IN ('FBM', 'FLEX', 'XD')

-- ══════════════════════════════════════════════════════════════════════════════
-- 4. MERCADO PAGO ENVIRONMENTS (MP_ON + MP_OFF)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.ENVIRONMENT IN ('MP_ON', 'MP_OFF')

-- ══════════════════════════════════════════════════════════════════════════════
-- 5. ALL ENVIRONMENTS (No filter)
-- ══════════════════════════════════════════════════════════════════════════════
-- Simply omit the environment filter from WHERE clause

-- ══════════════════════════════════════════════════════════════════════════════
-- 6. EXCLUDE SPECIFIC ENVIRONMENT (All except DS)
-- ══════════════════════════════════════════════════════════════════════════════
AND C.ENVIRONMENT NOT IN ('DS')
AND C.ENVIRONMENT IN ('FBM', 'FLEX', 'XD', 'MP_ON', 'MP_OFF')

-- ══════════════════════════════════════════════════════════════════════════════
-- 7. HANDLE NULL ENVIRONMENTS (Include or Exclude)
-- ══════════════════════════════════════════════════════════════════════════════

-- Include NULL:
AND (C.ENVIRONMENT IN ('FBM', 'FLEX') OR C.ENVIRONMENT IS NULL)

-- Exclude NULL:
AND C.ENVIRONMENT IS NOT NULL
AND C.ENVIRONMENT IN ('FBM', 'FLEX')

-- ══════════════════════════════════════════════════════════════════════════════
-- ENVIRONMENT INFORMATION
-- ══════════════════════════════════════════════════════════════════════════════
/*
Environment | Description                  | Icon | Color    | Use Case
------------|------------------------------|------|----------|---------------------------
DS          | Drop Shipping                | 📦   | #3b82f6  | Direct from seller
FBM         | Fulfillment by ML            | 🏪   | #10b981  | ML warehouse fulfillment
FLEX        | Flex Logistics               | 🚚   | #f59e0b  | Flexible logistics
XD          | Cross Docking                | 📍   | #8b5cf6  | Cross docking operations
MP_ON       | Mercado Pago Online          | 💳   | #06b6d4  | Online payments
MP_OFF      | Mercado Pago Offline         | 🏦   | #ec4899  | Offline payments
*/

-- ══════════════════════════════════════════════════════════════════════════════
-- PYTHON IMPLEMENTATION (Recommended)
-- ══════════════════════════════════════════════════════════════════════════════
/*
Python code to generate environment filter:

def generate_environment_filter(selected_environments):
    """
    Generate SQL filter for environments
    
    Args:
        selected_environments: List of selected environments (e.g., ['DS', 'FBM'])
                               If empty or None, no filter applied
    
    Returns:
        str: SQL WHERE clause for environment filter (or empty string)
    """
    if not selected_environments or len(selected_environments) == 0:
        return ""  # No filter
    
    # Remove None/empty values
    valid_envs = [env for env in selected_environments if env is not None and env != '']
    
    if len(valid_envs) == 0:
        return ""  # No valid environments
    
    # Generate SQL IN clause
    env_values = ','.join([f"'{env}'" for env in valid_envs])
    filter_sql = f"\\n        AND C.ENVIRONMENT IN ({env_values})"
    
    return filter_sql


# Usage example:
selected_environments = ['FBM', 'FLEX']
env_filter = generate_environment_filter(selected_environments)

# Result:
# "
#         AND C.ENVIRONMENT IN ('FBM', 'FLEX')"

# Then replace placeholder in base query:
final_query = BASE_QUERY.format(
    fecha_inicio='2026-01-01',
    fecha_fin='2026-01-31',
    sites="'MLA', 'MLC'",
    agrup_commerce="'PDD', 'PNR'",
    user_types="'Comprador', 'Vendedor'",
    environment_filter=env_filter  # ← Insert generated filter
)
*/
