# 🚀 Driver Calculation - Query Modular con ENVIRONMENT

> **Query oficial para calcular drivers con diferentes niveles de agregación**

---

## 🎯 Objetivo

Calcular drivers (órdenes) desde `BT_ORD_ORDERS` con flexibilidad para:
- Total agregado (sin apertura)
- Por Site
- Por Environment (logística)
- Por Site + Environment (combinado)

---

## 📊 Query Base Modular

```sql
-- ============================================================================
-- DRIVER CALCULATION - MODULAR QUERY
-- ============================================================================
-- Versión: 1.0
-- Fecha: Enero 2026
-- Tabla: meli-bi-data.WHOWNER.BT_ORD_ORDERS
-- ============================================================================

WITH 

-- ============================================================================
-- CTE 1: BASE_ORDERS - Extracción base con ENVIRONMENT
-- ============================================================================
BASE_ORDERS AS (
    SELECT
        ORD_ORDER_ID,
        SIT_SITE_ID,
        CAST(FORMAT_DATETIME('%Y%m', ORD_CLOSED_DT) AS INT64) AS OFC_MONTH_ID,
        
        -- ENVIRONMENT desde ORD_SHIPPING.LOGISTIC_TYPE
        CASE 
            WHEN ORD_SHIPPING.LOGISTIC_TYPE = 'cross_docking' 
                 OR ORD_SHIPPING.LOGISTIC_TYPE = 'xd_drop_off' THEN 'XD'
            WHEN ORD_SHIPPING.LOGISTIC_TYPE = 'fulfillment' THEN 'FBM'
            WHEN ORD_SHIPPING.LOGISTIC_TYPE = 'self_service' THEN 'FLEX'
            WHEN ORD_SHIPPING.LOGISTIC_TYPE = 'drop_off' THEN 'DS'
            ELSE 'MP-ON'
        END AS ENVIRONMENT
        
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
    WHERE 1=1
        AND ORD_CLOSED_DT IS NOT NULL
        AND SIT_SITE_ID NOT IN ('MLV')  -- Excluir Venezuela
        
        -- FILTROS DINÁMICOS (ajustar según necesidad) --
        AND CAST(FORMAT_DATETIME('%Y%m', ORD_CLOSED_DT) AS INT64) IN (202511, 202512)
        -- Agregar filtros según solicitud:
        -- AND SIT_SITE_ID = 'MLA'  -- Si se pide un site específico
        -- AND SIT_SITE_ID IN ('MLA', 'MLB')  -- Si se piden múltiples sites
),

-- ============================================================================
-- AGREGACIONES SEGÚN NECESIDAD
-- ============================================================================

-- NIVEL 1: Total agregado (sin apertura) - MÁS RÁPIDA
DRIVER_TOTAL AS (
    SELECT
        OFC_MONTH_ID,
        COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
    FROM BASE_ORDERS
    GROUP BY OFC_MONTH_ID
),

-- NIVEL 2: Por Site - RÁPIDA
DRIVER_BY_SITE AS (
    SELECT
        OFC_MONTH_ID,
        SIT_SITE_ID,
        COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
    FROM BASE_ORDERS
    GROUP BY OFC_MONTH_ID, SIT_SITE_ID
),

-- NIVEL 3: Por Environment - MEDIA
DRIVER_BY_ENV AS (
    SELECT
        OFC_MONTH_ID,
        ENVIRONMENT,
        COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
    FROM BASE_ORDERS
    GROUP BY OFC_MONTH_ID, ENVIRONMENT
),

-- NIVEL 4: Por Site + Environment - MÁS LENTA (máximo detalle)
DRIVER_BY_SITE_ENV AS (
    SELECT
        OFC_MONTH_ID,
        SIT_SITE_ID,
        ENVIRONMENT,
        COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
    FROM BASE_ORDERS
    GROUP BY OFC_MONTH_ID, SIT_SITE_ID, ENVIRONMENT
)

-- ============================================================================
-- SELECCIONAR EL NIVEL DESEADO (descomentar según necesidad)
-- ============================================================================

-- Opción 1: Total agregado (sin apertura) - Más rápida
SELECT * FROM DRIVER_TOTAL 
ORDER BY OFC_MONTH_ID;

-- Opción 2: Por site
-- SELECT * FROM DRIVER_BY_SITE 
-- ORDER BY OFC_MONTH_ID, SIT_SITE_ID;

-- Opción 3: Por environment
-- SELECT * FROM DRIVER_BY_ENV 
-- ORDER BY OFC_MONTH_ID, ENVIRONMENT;

-- Opción 4: Por site + environment (máximo detalle)
-- SELECT * FROM DRIVER_BY_SITE_ENV 
-- ORDER BY OFC_MONTH_ID, SIT_SITE_ID, ENVIRONMENT;
```

---

## 🎯 Casos de Uso

### Caso 1: Driver total de MLA

```sql
-- Solo cambiar el WHERE en BASE_ORDERS:
AND SIT_SITE_ID = 'MLA'

-- Y usar: SELECT * FROM DRIVER_TOTAL
```

**Resultado esperado:**
| OFC_MONTH_ID | TOTAL_ORDERS |
|--------------|--------------|
| 202511 | 25,123,456 |
| 202512 | 27,234,567 |

---

### Caso 2: Driver de MLA por Environment

```sql
-- Filtro en BASE_ORDERS:
AND SIT_SITE_ID = 'MLA'

-- Seleccionar: SELECT * FROM DRIVER_BY_ENV
```

**Resultado esperado:**
| OFC_MONTH_ID | ENVIRONMENT | TOTAL_ORDERS |
|--------------|-------------|--------------|
| 202511 | XD | 8,234,567 |
| 202511 | FBM | 5,678,901 |
| 202511 | FLEX | 4,567,890 |
| 202511 | DS | 3,456,789 |
| 202511 | MP-ON | 3,185,309 |
| 202512 | XD | 8,890,123 |
| ... | ... | ... |

---

### Caso 3: Driver global (todos los sites)

```sql
-- Sin filtro adicional en BASE_ORDERS (ya excluye MLV)

-- Seleccionar: SELECT * FROM DRIVER_TOTAL
```

**Resultado esperado:**
| OFC_MONTH_ID | TOTAL_ORDERS |
|--------------|--------------|
| 202511 | 147,234,567 |
| 202512 | 158,456,789 |

---

### Caso 4: Driver de MLA + MLB por site y environment

```sql
-- Filtro en BASE_ORDERS:
AND SIT_SITE_ID IN ('MLA', 'MLB')

-- Seleccionar: SELECT * FROM DRIVER_BY_SITE_ENV
```

**Resultado esperado:**
| OFC_MONTH_ID | SIT_SITE_ID | ENVIRONMENT | TOTAL_ORDERS |
|--------------|-------------|-------------|--------------|
| 202511 | MLA | XD | 8,234,567 |
| 202511 | MLA | FBM | 5,678,901 |
| 202511 | MLB | XD | 20,456,789 |
| 202511 | MLB | FBM | 18,234,567 |
| ... | ... | ... | ... |

---

## ⚡ Versión Simplificada (sin ENVIRONMENT)

Si **NO se necesita apertura por ENVIRONMENT**, usar esta versión más rápida:

```sql
WITH BASE_ORDERS AS (
    SELECT
        ORD_ORDER_ID,
        SIT_SITE_ID,
        CAST(FORMAT_DATETIME('%Y%m', ORD_CLOSED_DT) AS INT64) AS OFC_MONTH_ID
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
    WHERE ORD_CLOSED_DT IS NOT NULL
        AND SIT_SITE_ID NOT IN ('MLV')
        AND CAST(FORMAT_DATETIME('%Y%m', ORD_CLOSED_DT) AS INT64) IN (202511, 202512)
        -- FILTROS DINÁMICOS --
)

-- Total sin apertura
SELECT
    OFC_MONTH_ID,
    COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
FROM BASE_ORDERS
GROUP BY OFC_MONTH_ID
ORDER BY OFC_MONTH_ID;

-- O por site
-- SELECT
--     OFC_MONTH_ID,
--     SIT_SITE_ID,
--     COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
-- FROM BASE_ORDERS
-- GROUP BY OFC_MONTH_ID, SIT_SITE_ID
-- ORDER BY OFC_MONTH_ID, SIT_SITE_ID;
```

---

## 📋 Mapeo de ENVIRONMENT

| ORD_SHIPPING.LOGISTIC_TYPE | ENVIRONMENT | Descripción |
|----------------------------|-------------|-------------|
| `cross_docking` | XD | Cross Docking |
| `xd_drop_off` | XD | XD Drop Off |
| `fulfillment` | FBM | Fulfillment by Mercado Libre |
| `self_service` | FLEX | Self Service (Flex) |
| `drop_off` | DS | Drop Shipping |
| Otros/NULL | MP-ON | Mercado Pago Online |

---

## 🚨 Reglas Críticas

### 1. NUNCA usar estimaciones

❌ **PROHIBIDO:**
```python
driver_global = driver_mla * 5.88  # NUNCA hacer esto
```

✅ **CORRECTO:**
```sql
-- Siempre query real de BigQuery
SELECT COUNT(DISTINCT ORD_ORDER_ID) FROM ...
```

### 2. Formato de período

✅ **CORRECTO:**
```sql
CAST(FORMAT_DATETIME('%Y%m', ORD_CLOSED_DT) AS INT64)  -- 202511, 202512
```

❌ **INCORRECTO:**
```sql
FORMAT_DATETIME('%Y-%m', ORD_CLOSED_DT)  -- '2025-11', '2025-12'
```

### 3. Exclusiones automáticas

Siempre excluir:
- ✅ `SIT_SITE_ID NOT IN ('MLV')`  -- Venezuela
- ✅ `ORD_CLOSED_DT IS NOT NULL`  -- Órdenes sin fecha

### 4. Uso modular

Para evitar timeouts:
1. ✅ Usar `DRIVER_TOTAL` si no se necesita apertura (más rápida)
2. ✅ Usar `DRIVER_BY_SITE` si solo se necesita por site
3. ✅ Usar `DRIVER_BY_ENV` solo si es necesario
4. ✅ Usar `DRIVER_BY_SITE_ENV` solo para máximo detalle

---

## 📊 Comparación de Performance

| Nivel | Campos GROUP BY | Filas Resultado | Velocidad | Uso |
|-------|----------------|-----------------|-----------|-----|
| **DRIVER_TOTAL** | `OFC_MONTH_ID` | ~2-12 | 🚀 Muy rápida | Driver total |
| **DRIVER_BY_SITE** | `OFC_MONTH_ID, SIT_SITE_ID` | ~14-84 | ⚡ Rápida | Por site |
| **DRIVER_BY_ENV** | `OFC_MONTH_ID, ENVIRONMENT` | ~10-60 | ⚡ Media | Por logística |
| **DRIVER_BY_SITE_ENV** | `OFC_MONTH_ID, SIT_SITE_ID, ENVIRONMENT` | ~70-420 | 🐢 Lenta | Máximo detalle |

---

## ✅ Validación

Para validar resultados:

```sql
-- Verificar que la suma por site = total global
WITH BY_SITE AS (
    SELECT OFC_MONTH_ID, SIT_SITE_ID, COUNT(DISTINCT ORD_ORDER_ID) AS ORDERS
    FROM BASE_ORDERS
    GROUP BY 1, 2
)
SELECT 
    OFC_MONTH_ID,
    SUM(ORDERS) AS TOTAL_BY_SUM,
    (SELECT COUNT(DISTINCT ORD_ORDER_ID) FROM BASE_ORDERS WHERE OFC_MONTH_ID = BY_SITE.OFC_MONTH_ID) AS TOTAL_DIRECT
FROM BY_SITE
GROUP BY OFC_MONTH_ID;
-- TOTAL_BY_SUM debe = TOTAL_DIRECT
```

---

## 📚 Referencias

- **Tabla fuente:** `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
- **Campo ENVIRONMENT:** `ORD_SHIPPING.LOGISTIC_TYPE`
- **Reglas:** `.cursorrules` (Sección 7 y 11)
- **Threshold:** `config/thresholds.py`

---

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Status:** ✅ OFICIAL - Query validada  
**Regla:** NUNCA usar estimaciones - siempre queries reales
