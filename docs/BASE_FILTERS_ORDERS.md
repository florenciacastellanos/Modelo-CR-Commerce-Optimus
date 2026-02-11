# 🔍 Filtros Base Obligatorios para Órdenes (Drivers)

> **⚠️ REGLA CRÍTICA** - Enero 2026

## 📋 Resumen

Todos los cálculos de drivers (denominador del CR) desde `BT_ORD_ORDERS` **DEBEN** aplicar estos filtros base obligatorios.

## ✅ Filtros Base (SIEMPRE aplicar)

```sql
WHERE 1=1
    -- Filtros de fecha
    AND ORD.ORD_CLOSED_DT >= 'YYYY-MM-01'  -- Fecha inicio período
    AND ORD.ORD_CLOSED_DT IS NOT NULL
    
    -- Filtros de negocio (BASE)
    AND ORD.ORD_GMV_FLG = TRUE              -- Solo órdenes GMV válidas
    AND ORD.ORD_MARKETPLACE_FLG = TRUE      -- Solo órdenes marketplace
    
    -- Exclusiones (BASE)
    AND ORD.SIT_SITE_ID NOT IN ('MLV')      -- Excluir Venezuela
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS') -- Excluir propinas
```

---

## 🎯 Razón de Cada Filtro

### 1. `ORD_GMV_FLG = TRUE`
**Propósito:** Solo órdenes que cuentan como GMV (Gross Merchandise Value)

**Excluye:**
- Órdenes canceladas
- Órdenes rechazadas
- Órdenes que no generaron valor comercial

**Impacto:** Reduce volumen ~15-20%

---

### 2. `ORD_MARKETPLACE_FLG = TRUE`
**Propósito:** Solo órdenes de marketplace

**Excluye:**
- Órdenes de otros canales (retail, directo)
- Transacciones no marketplace

**Impacto:** Reduce volumen ~10-15%

---

### 3. `SIT_SITE_ID NOT IN ('MLV')`
**Propósito:** Excluir Venezuela (site no operativo)

**Excluye:**
- Todas las órdenes de MLV (Venezuela)

**Impacto:** Mínimo (<1%)

---

### 4. `UPPER(DOM_DOMAIN_ID) <> 'TIPS'`
**Propósito:** Excluir propinas (no son órdenes de producto)

**Excluye:**
- Transacciones de propinas
- Donaciones

**Impacto:** Reduce volumen ~1-3%

---

## 📊 Impacto Total

**Reducción estimada del volumen de órdenes:** ~30-40%

**Ejemplo real (Nov-Dic 2025):**
- Sin filtros: ~220M órdenes/mes (global)
- Con filtros base: ~145-160M órdenes/mes (global)

---

## 📝 Query Completa de Ejemplo

### Drivers Totales (Global)

```sql
-- Query para calcular drivers globales (todos los sites)
SELECT
    DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) AS FECHA_MONTH,
    COUNT(DISTINCT ORD.ORD_ORDER_ID) AS TOTAL_ORDERS
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 1=1
    -- Filtros de fecha
    AND ORD.ORD_CLOSED_DT >= '2025-11-01'
    AND DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) IN ('2025-11-01', '2025-12-01')
    AND ORD.ORD_CLOSED_DT IS NOT NULL
    
    -- FILTROS BASE OBLIGATORIOS
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID NOT IN ('MLV')
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
    
    -- SIN FILTRO ADICIONAL DE SITE (drivers totales)
    
GROUP BY FECHA_MONTH
ORDER BY FECHA_MONTH
```

---

### Drivers por Site Específico (ej: MLA)

```sql
-- Query para calcular drivers de MLA solamente
SELECT
    DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) AS FECHA_MONTH,
    COUNT(DISTINCT ORD.ORD_ORDER_ID) AS TOTAL_ORDERS
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 1=1
    -- Filtros de fecha
    AND ORD.ORD_CLOSED_DT >= '2025-11-01'
    AND DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) IN ('2025-11-01', '2025-12-01')
    AND ORD.ORD_CLOSED_DT IS NOT NULL
    
    -- FILTROS BASE OBLIGATORIOS
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID NOT IN ('MLV')
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
    
    -- FILTRO ADICIONAL: Site específico
    AND ORD.SIT_SITE_ID = 'MLA'
    
GROUP BY FECHA_MONTH
ORDER BY FECHA_MONTH
```

---

## 🔄 Diferencia: Drivers Totales vs Drivers por Site

| Tipo | Filtros Base | Filtro Adicional de Site |
|------|--------------|--------------------------|
| **Drivers Totales** | ✅ Siempre aplicar | ❌ NO aplicar |
| **Drivers por Site** | ✅ Siempre aplicar | ✅ Aplicar (`SIT_SITE_ID = 'XXX'`) |

**Ejemplo:**
- Usuario pide: "CR PDD MLA con drivers totales"
  - Incoming: Filtrar por `SIT_SITE_ID = 'MLA'` + PDD
  - Driver: Filtros base solamente (SIN filtro adicional de site)

- Usuario pide: "CR PDD MLA con drivers de MLA"
  - Incoming: Filtrar por `SIT_SITE_ID = 'MLA'` + PDD
  - Driver: Filtros base + `SIT_SITE_ID = 'MLA'`

---

## 🚨 Importante

### ✅ SIEMPRE hacer:
1. Aplicar filtros base en **TODA** query de drivers
2. Aplicar filtros base **ANTES** de filtros adicionales
3. Documentar en el reporte que se usan filtros base

### ❌ NUNCA hacer:
1. Omitir filtros base
2. Usar estimaciones en lugar de queries reales
3. Cambiar los filtros base sin actualizar esta documentación

---

## 📅 Historial de Cambios

### Enero 2026
- ✅ Definición inicial de filtros base obligatorios
- ✅ Validación con datos reales de producción
- ✅ Documentación en `.cursorrules` como regla crítica

---

## 🔗 Referencias

- **`.cursorrules`**: Regla 11 - Base Filters for Orders/Drivers
- **`DATE_FIELD_RULE.md`**: Regla de campos de fecha
- **`DRIVER_CALCULATION_QUERY.md`**: Query modular para drivers

---

## 📊 Validación

**Estado:** ✅ VALIDADO (Enero 2026)

**Fuente de validación:**
- Queries de producción oficiales
- Reportes de negocio
- Análisis PDD MLA Nov-Dic 2025

**Precisión:** 100% match con reportes oficiales al aplicar filtros base

---

**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Status:** ✅ Production Ready
