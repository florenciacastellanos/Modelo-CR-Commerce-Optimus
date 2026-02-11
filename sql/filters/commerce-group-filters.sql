-- ══════════════════════════════════════════════════════════════════════════════
-- COMMERCE GROUP FILTERS - CONTACT RATE COMMERCE
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Commerce Group filter examples
-- Available Groups: 15 Commerce Groups in 5 categories
-- ══════════════════════════════════════════════════════════════════════════════

-- ══════════════════════════════════════════════════════════════════════════════
-- 1. SINGLE COMMERCE GROUP (PDD only)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE = 'PDD'

-- ══════════════════════════════════════════════════════════════════════════════
-- 2. POST-COMPRA CATEGORY (PDD + PNR)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN ('PDD', 'PNR')

-- ══════════════════════════════════════════════════════════════════════════════
-- 3. SHIPPING CATEGORY (All shipping groups)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN ('ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers')

-- ══════════════════════════════════════════════════════════════════════════════
-- 4. MARKETPLACE CATEGORY (All marketplace groups)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN ('Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 'Full Sellers', 'Pagos')

-- ══════════════════════════════════════════════════════════════════════════════
-- 5. PAGOS CATEGORY (Mercado Pago)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN ('MP On')

-- ══════════════════════════════════════════════════════════════════════════════
-- 6. CUENTA CATEGORY (Account management)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN ('Cuenta', 'Experiencia Impositiva')

-- ══════════════════════════════════════════════════════════════════════════════
-- 7. MULTIPLE CATEGORIES (Post-Compra + Shipping)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN (
    'PDD', 'PNR',  -- Post-Compra
    'ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers'  -- Shipping
)

-- ══════════════════════════════════════════════════════════════════════════════
-- 8. ALL COMMERCE GROUPS (No filter)
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE IN (
    -- Post-Compra
    'PDD', 'PNR',
    
    -- Shipping
    'ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers',
    
    -- Marketplace
    'Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 'Full Sellers', 'Pagos',
    
    -- Pagos
    'MP On',
    
    -- Cuenta
    'Cuenta', 'Experiencia Impositiva'
)

-- ══════════════════════════════════════════════════════════════════════════════
-- 9. EXCLUDE SPECIFIC GROUPS (All except 'Generales Compra')
-- ══════════════════════════════════════════════════════════════════════════════
WHERE AGRUP_COMMERCE NOT IN ('Generales Compra')

-- ══════════════════════════════════════════════════════════════════════════════
-- 10. FILTER BY USER TYPE AFFINITY
-- ══════════════════════════════════════════════════════════════════════════════

-- Comprador-focused groups:
WHERE AGRUP_COMMERCE IN ('PDD', 'PNR', 'ME Distribución', 'Pre Venta')

-- Vendedor-focused groups:
WHERE AGRUP_COMMERCE IN ('ME PreDespacho', 'FBM Sellers', 'Full Sellers', 'Moderaciones', 'Experiencia Impositiva')

-- Driver-focused groups:
WHERE AGRUP_COMMERCE IN ('ME Drivers')

-- Cuenta-focused groups:
WHERE AGRUP_COMMERCE IN ('Cuenta', 'Experiencia Impositiva')

-- ══════════════════════════════════════════════════════════════════════════════
-- COMMERCE GROUPS REFERENCE
-- ══════════════════════════════════════════════════════════════════════════════
/*
Category        | Commerce Group           | User Type Focus       | Volume % | Icon
----------------|--------------------------|----------------------|----------|------
POST-COMPRA     | PDD                      | Comprador            | 15-20%   | 📦
POST-COMPRA     | PNR                      | Comprador            | 10-15%   | 🚚
SHIPPING        | ME Distribución          | Comprador            | 15-20%   | 📦
SHIPPING        | ME PreDespacho           | Vendedor             | 10-15%   | 📤
SHIPPING        | FBM Sellers              | Vendedor             | 5-10%    | 🏪
SHIPPING        | ME Drivers               | Driver               | 2-5%     | 🏍️
MARKETPLACE     | Pre Venta                | Comprador            | 5-10%    | 🔍
MARKETPLACE     | Post Venta               | Comprador, Vendedor  | 5-10%    | 📞
MARKETPLACE     | Generales Compra         | Comprador, Vendedor  | 10-15%   | 🛍️
MARKETPLACE     | Moderaciones             | Vendedor             | 2-5%     | ⚖️
MARKETPLACE     | Full Sellers             | Vendedor             | 2-5%     | 🏬
MARKETPLACE     | Pagos                    | Comprador, Vendedor  | 2-5%     | 💳
PAGOS           | MP On                    | Comprador, Vendedor  | 5-10%    | 💰
CUENTA          | Cuenta                   | Cuenta               | 3-5%     | 👤
CUENTA          | Experiencia Impositiva   | Cuenta, Vendedor     | 1-3%     | 📄
*/

-- ══════════════════════════════════════════════════════════════════════════════
-- PYTHON IMPLEMENTATION (Recommended)
-- ══════════════════════════════════════════════════════════════════════════════
/*
Python code to generate commerce group filter:

AGRUP_COMMERCE_CATEGORIES = {
    'Post-Compra': ['PDD', 'PNR'],
    'Shipping': ['ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers'],
    'Marketplace': ['Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 'Full Sellers', 'Pagos'],
    'Pagos': ['MP On'],
    'Cuenta': ['Cuenta', 'Experiencia Impositiva']
}

def generate_commerce_group_filter(selected_groups):
    """
    Generate SQL filter for commerce groups
    
    Args:
        selected_groups: List of selected commerce groups (e.g., ['PDD', 'PNR'])
                        OR list of categories (e.g., ['Post-Compra', 'Shipping'])
    
    Returns:
        str: SQL IN clause values for commerce group filter
    """
    if not selected_groups or len(selected_groups) == 0:
        # Default: All commerce groups
        all_groups = []
        for groups in AGRUP_COMMERCE_CATEGORIES.values():
            all_groups.extend(groups)
        selected_groups = all_groups
    
    # Check if categories were provided
    final_groups = []
    for item in selected_groups:
        if item in AGRUP_COMMERCE_CATEGORIES:
            # It's a category, expand to groups
            final_groups.extend(AGRUP_COMMERCE_CATEGORIES[item])
        else:
            # It's a group, add directly
            final_groups.append(item)
    
    # Remove duplicates
    final_groups = list(set(final_groups))
    
    # Generate SQL values
    agrup_sql = ','.join([f"'{group}'" for group in final_groups])
    
    return agrup_sql


# Usage examples:

# 1. Specific groups:
selected_groups = ['PDD', 'PNR', 'ME Distribución']
agrup_filter = generate_commerce_group_filter(selected_groups)
# Result: "'PDD', 'PNR', 'ME Distribución'"

# 2. By category:
selected_categories = ['Post-Compra', 'Shipping']
agrup_filter = generate_commerce_group_filter(selected_categories)
# Result: "'PDD', 'PNR', 'ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers'"

# 3. Mixed (categories + groups):
selected_mixed = ['Post-Compra', 'MP On', 'Cuenta']
agrup_filter = generate_commerce_group_filter(selected_mixed)
# Result: "'PDD', 'PNR', 'MP On', 'Cuenta', 'Experiencia Impositiva'"

# Then replace placeholder in base query:
final_query = BASE_QUERY.format(
    fecha_inicio='2026-01-01',
    fecha_fin='2026-01-31',
    sites="'MLA', 'MLC'",
    agrup_commerce=agrup_filter,  # ← Insert generated filter
    user_types="'Comprador', 'Vendedor'",
    environment_filter=""
)
*/
