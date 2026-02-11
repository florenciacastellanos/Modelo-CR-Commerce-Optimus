# 🚛 Shipping Drivers - Guía Oficial

**Versión:** 3.7  
**Fecha:** Enero 2026  
**Status:** ✅ OFICIAL - ME PreDespacho validado

---

## 🎯 Propósito

Este documento define los **drivers específicos para la categoría SHIPPING**, que son diferentes a los drivers de Post-Compra y Marketplace.

---

## ⚠️ REGLA CRÍTICA

**Los drivers de SHIPPING NO son órdenes totales (`BT_ORD_ORDERS`).**

Cada agrupación de Shipping tiene su **driver específico** que proviene de la tabla `BT_CX_DRIVERS_CR`.

---

## 📊 Tabla de Drivers de Shipping

| Agrupación Shipping | Usuario | Driver Code | Campo en BT_CX_DRIVERS_CR | Descripción |
|---------------------|---------|-------------|---------------------------|-------------|
| **ME Distribución** | Buyer/Comprador | **OS_TOTALES** | `ORDERS_SHIPPED` | Órdenes totales shipped |
| **ME PreDespacho** ⭐ | Seller/Vendedor | **OS_WO_FULL** | `OS_WITHOUT_FBM` | Órdenes sin FBM (sin Full) |
| **FBM Sellers** | Full | **OS_FULL** | `OS_WITH_FBM` | Órdenes con FBM (Full) |
| **ME Drivers** | Drivers | TBD | TBD | Pendiente de definir |

⭐ = Validado con datos reales (Enero 2026)

---

## 🔧 Query Templates

### **1. Driver: ME Distribución (OS_TOTALES)**

```sql
-- Órdenes totales shipped para ME Distribución (Buyer)
SELECT
    drv.MONTH_ID as period,
    SUM(drv.ORDERS_SHIPPED) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- NO filtrar por site: driver debe ser GLOBAL ❌
GROUP BY drv.MONTH_ID
ORDER BY drv.MONTH_ID
```

**Ejemplo:**
- Nov 2025: ~90M órdenes shipped (global)
- Dic 2025: ~91M órdenes shipped (global)

---

### **2. Driver: ME PreDespacho (OS_WO_FULL)** ✅ Validado

```sql
-- Órdenes sin FBM para ME PreDespacho (Seller)
SELECT
    drv.MONTH_ID as period,
    SUM(drv.OS_WITHOUT_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- NO filtrar por site: driver debe ser GLOBAL ❌
GROUP BY drv.MONTH_ID
ORDER BY drv.MONTH_ID
```

**Ejemplo validado (ME PreDespacho MLB Nov-Dic 2025):**
- Nov 2025: **87,851,825** órdenes sin FBM (global)
- Dic 2025: **88,496,573** órdenes sin FBM (global)
- Incoming MLB: 97,221 (Nov) → 116,118 (Dic)
- CR: 0.1107 pp (Nov) → 0.1312 pp (Dic)

---

### **3. Driver: FBM Sellers (OS_FULL)**

```sql
-- Órdenes con FBM para FBM Sellers (Full)
SELECT
    drv.MONTH_ID as period,
    SUM(drv.OS_WITH_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- NO filtrar por site: driver debe ser GLOBAL ❌
GROUP BY drv.MONTH_ID
ORDER BY drv.MONTH_ID
```

**Ejemplo:**
- Nov 2025: ~15M órdenes con FBM (global)
- Dic 2025: ~16M órdenes con FBM (global)

---

## 🚨 REGLA CRÍTICA: Drivers GLOBALES

### **✅ CORRECTO**

Los drivers de Shipping deben ser **GLOBALES** (sin filtrar por site):

```sql
-- ✅ CORRECTO: Driver global
SELECT
    drv.MONTH_ID as period,
    SUM(drv.OS_WITHOUT_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- Solo periodo, SIN otros filtros
GROUP BY drv.MONTH_ID
```

### **❌ INCORRECTO**

```sql
-- ❌ PROHIBIDO: NO filtrar driver por site
SELECT
    drv.MONTH_ID as period,
    drv.SIT_SITE_ID as sit_site_id,  -- ❌ NO USAR
    SUM(drv.OS_WITHOUT_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    AND drv.SIT_SITE_ID = 'MLB'  -- ❌ PROHIBIDO
GROUP BY drv.MONTH_ID, drv.SIT_SITE_ID
```

### **Razón**

El driver de Shipping representa el **universo total de órdenes** (shipped, sin FBM, con FBM) a nivel **GLOBAL** para todos los sites.

El incoming sí se filtra por site específico (ej: MLB), lo que permite calcular la **tasa de contacto del site dentro del universo global**.

---

## 📐 Comparación: Categorías de Commerce Groups

| Aspecto | Post-Compra | Marketplace | Shipping |
|---------|-------------|-------------|----------|
| **Tabla Driver** | `BT_ORD_ORDERS` | `BT_ORD_ORDERS` | `BT_CX_DRIVERS_CR` |
| **Campo Driver** | `COUNT(DISTINCT ORD_ORDER_ID)` | `COUNT(DISTINCT ORD_ORDER_ID)` | `SUM(ORDERS_SHIPPED)`, `SUM(OS_WITHOUT_FBM)`, `SUM(OS_WITH_FBM)` |
| **Filtros Driver** | GMV_FLG + MARKETPLACE_FLG + sin MLV + sin TIPS | GMV_FLG + MARKETPLACE_FLG + sin TIPS | **Solo periodo** |
| **¿Filtrar por site?** | ❌ NO (global) | ✅ **SÍ (por site)** | ❌ NO (global) |
| **¿Filtrar por BU?** | ❌ NO | ❌ NO | ❌ NO |
| **Campo Fecha Driver** | `DATE_TRUNC(ORD_CLOSED_DT, MONTH)` | `DATE_TRUNC(ORD_CLOSED_DT, MONTH)` | `MONTH_ID` (tipo DATE) |

**⚠️ CAMBIO v1.0 (Feb 2026):** Marketplace ahora usa drivers **filtrados por site** para reflejar el volumen específico de cada mercado.

---

## 📅 Campos de Fecha

### **Incoming (BT_CX_CONTACTS):**
```sql
DATE_TRUNC(C.CONTACT_DATE_ID, MONTH)
-- o
DATE_TRUNC(CAST(C.FIRST_OUTGOING_CASE_DATE AS DATE), MONTH)
```

### **Driver (BT_CX_DRIVERS_CR):**
```sql
drv.MONTH_ID  -- Tipo DATE: '2025-11-01', '2025-12-01'
```

**⚠️ Importante:** `MONTH_ID` en `BT_CX_DRIVERS_CR` es de tipo **DATE**, NO INT64.

**✅ Correcto:**
```sql
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
```

**❌ Incorrecto:**
```sql
WHERE drv.MONTH_ID IN (202511, 202512)  -- ❌ Error de tipo
```

---

## 🧪 Ejemplo Completo: ME PreDespacho MLB

### **Paso 1: Query de Incoming (filtrado por MLB)**

```sql
WITH INCOMING_ME_ML AS (
    SELECT
        C.SIT_SITE_ID,
        DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS FECHA_MONTH,
        C.PROCESS_NAME,
        C.CDU,
        -- Clasificación ME PreDespacho completa
        CASE
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('Post Compra Funcionalidades Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') 
                 AND C.PROCESS_GROUP_UPDATE_REPORTING IN ('Post Compra Funcionalidades Vendedor') THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('Post Compra Funcionalidades Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') 
                 AND C.PROCESS_GROUP_UPDATE_REPORTING IN ('Post Compra Vendedor ME') THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Redes%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME PreDespacho'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%CAP%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME PreDespacho'
            ELSE 'OTRO' 
        END AS REPORTING,
        1.0 AS CANT_CASES
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    LEFT JOIN (
        SELECT DISTINCT
            CX_PR_ID as PROCESS_ID,
            CX_PR_NAME_HSP as PROCESS_NAME
        FROM `meli-bi-data.WHOWNER.LK_CX_PROCESS_ADM` PROCESOS
        LEFT JOIN `meli-bi-data.WHOWNER.LK_CX_PRO_GROUP` PROBLEMATICAS 
            ON PROCESOS.CX_PR_ID = PROBLEMATICAS.PROCESS_ID
    ) P ON C.PROCESS_ID = P.PROCESS_ID
    WHERE 1=1
        AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
        AND C.SIT_SITE_ID = 'MLB'  -- ✅ Filtrado por site
        AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
        AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND (C.PROCESS_GROUP_ECOMMERCE NOT IN ('Cuenta') OR C.PROCESS_GROUP_ECOMMERCE IS NULL)
)
SELECT * FROM INCOMING_ME_ML WHERE REPORTING = 'ME PreDespacho'
```

**Resultado:**
- Nov 2025: **97,221** casos (MLB únicamente)
- Dic 2025: **116,118** casos (MLB únicamente)

---

### **Paso 2: Query de Driver (GLOBAL, sin filtro de site)**

```sql
SELECT
    drv.MONTH_ID as period,
    SUM(drv.OS_WITHOUT_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE 1=1
    AND drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- NO filtrar por site ❌
GROUP BY drv.MONTH_ID
ORDER BY drv.MONTH_ID
```

**Resultado:**
- Nov 2025: **87,851,825** órdenes sin FBM (GLOBAL - todos los sites)
- Dic 2025: **88,496,573** órdenes sin FBM (GLOBAL - todos los sites)

---

### **Paso 3: Cálculo del CR**

```python
# CR = (Incoming / Driver) × 100

CR_Nov = (97_221 / 87_851_825) * 100 = 0.1107 pp
CR_Dic = (116_118 / 88_496_573) * 100 = 0.1312 pp

Var_CR = CR_Dic - CR_Nov = 0.1312 - 0.1107 = +0.0205 pp
Var_CR_Pct = (Var_CR / CR_Nov) * 100 = (0.0205 / 0.1107) * 100 = +18.57%
```

**Resultado Final:**
- **CR Nov:** 0.1107 pp
- **CR Dic:** 0.1312 pp
- **Variación:** +0.0205 pp (+18.57%)

---

## 📋 Checklist para Implementación

Cuando implementes un reporte de Shipping, verifica:

### **Incoming:**
- [ ] Query usa `BT_CX_CONTACTS`
- [ ] Fecha: `DATE_TRUNC(CONTACT_DATE_ID, MONTH)`
- [ ] Filtrado por site específico (ej: `SIT_SITE_ID = 'MLB'`)
- [ ] Filtrado por BU: `PROCESS_BU_CR_REPORTING IN ('ME','ML')`
- [ ] Clasificación completa de la agrupación (incluye PROCESS_GROUP_UPDATE_REPORTING, Redes, CAP)
- [ ] Exclusiones: `FLAG_EXCLUDE_NUMERATOR_CR = 0`
- [ ] LEFT JOINs con LK_CX_PROCESS_ADM, LK_CX_PRO_GROUP si es necesario
- [ ] UNION con casos de MP si aplica

### **Driver:**
- [ ] Query usa `BT_CX_DRIVERS_CR` ✅
- [ ] Campo correcto según agrupación:
  - [ ] ME Distribución: `SUM(drv.ORDERS_SHIPPED)`
  - [ ] ME PreDespacho: `SUM(drv.OS_WITHOUT_FBM)`
  - [ ] FBM Sellers: `SUM(drv.OS_WITH_FBM)`
- [ ] Fecha: `MONTH_ID` (tipo DATE)
- [ ] **SIN filtro de site** ❌
- [ ] **SIN filtro de BU** ❌
- [ ] **SIN otros filtros** ❌
- [ ] Solo filtro de periodo: `MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'`

### **CR Calculation:**
- [ ] Formula: `(Incoming / Driver) × 100`
- [ ] Driver es GLOBAL (todos los sites)
- [ ] Incoming es específico del site solicitado
- [ ] Resultado en puntos porcentuales (pp)

---

## 🎨 Reportes HTML

Los reportes de Shipping usan:
- **Color:** Morado (#9c27b0) 🟣
- **Badge:** "SHIPPING" + site específico
- **Estructura:** v3.7 (Cross Site 3 tablas / Single Site 2 tablas)
- **Driver en metadata:** Indicar driver usado (OS_TOTALES, OS_WO_FULL, OS_FULL)

---

## 🔗 Referencias

- **`.cursorrules`**: Regla 12 - Shipping Drivers (CRITICAL)
- **Script validado**: `scripts/generar_cr_me_predespacho_MLB_nov_dic_2025.py`
- **Reporte validado**: `reporte-cr-me-predespacho-MLB-nov-dic-2025.html`
- **Tabla BigQuery**: `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR`

---

## 📊 Próximos Pasos

1. **Validar ME Distribución** con OS_TOTALES (ORDERS_SHIPPED)
2. **Validar FBM Sellers** con OS_FULL (OS_WITH_FBM)
3. **Definir driver para ME Drivers**
4. **Crear templates automatizados** para reportes de Shipping

---

**Versión:** 3.7  
**Status:** ✅ OFICIAL - ME PreDespacho validado  
**Fecha:** Enero 2026  
**Validado con:** ME PreDespacho MLB Nov-Dic 2025
