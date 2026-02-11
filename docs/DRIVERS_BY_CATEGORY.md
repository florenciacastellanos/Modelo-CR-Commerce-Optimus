# 🎯 Drivers por Categoría de Commerce Group

> **Documento oficial**: Reglas de selección de drivers según la categoría del Commerce Group

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Status:** ✅ OFICIAL - Implementado en v6.3.6+

---

## 🚨 REGLA DE ORO

> **Los drivers se seleccionan automáticamente según la categoría del Commerce Group.**  
> **NO todos los commerce groups usan el mismo driver.**

---

## 📊 Resumen Ejecutivo

| Categoría | Commerce Groups | Driver | Tabla | ¿Filtrar por Site? |
|-----------|----------------|--------|-------|-------------------|
| **Post-Compra** | PDD, PNR | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |
| **Shipping** | ME Distribución, ME PreDespacho, FBM Sellers, ME Drivers | Drivers específicos | `BT_CX_DRIVERS_CR` | ❌ NO (global) |
| **Marketplace** | Pre Venta, Post Venta, Generales Compra, Moderaciones, Full Sellers, Pagos, Loyalty | Órdenes totales | `BT_ORD_ORDERS` | ✅ **SÍ (por site)** |
| **Pagos** | MP On | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |
| **Cuenta** | Cuenta, Experiencia Impositiva | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |

---

## 📦 CATEGORÍA 1: Post-Compra

### Commerce Groups
- **PDD** (Producto Dañado/Defectuoso)
- **PNR** (Producto No Recibido)

### Driver
- **Tipo:** Órdenes totales **GLOBALES** (sin filtro site)
- **Tabla:** `BT_ORD_ORDERS`
- **Campo:** `COUNT(DISTINCT ORD_ORDER_ID)`
- **Filtros:**
  - `ORD_GMV_FLG = TRUE`
  - `ORD_MARKETPLACE_FLG = TRUE`
  - `SIT_SITE_ID NOT IN ('MLV')`
  - `DOM_DOMAIN_ID <> 'TIPS'`

### Razón
El incoming de Post-Compra está directamente relacionado con el volumen global de órdenes cerradas. Se usa driver global para calcular la tasa de contacto sobre el universo total de transacciones.

### Ejemplo Query
```sql
SELECT
    COUNT(DISTINCT ORD.ORD_ORDER_ID) as DRIVER_TOTAL
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE ORD.ORD_CLOSED_DT BETWEEN '2025-11-01' AND '2025-11-30'
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID NOT IN ('MLV')
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
-- NO filtrar por site
```

**Resultado esperado:** ~90M órdenes (Nov 2025, todos los sites)

---

## 🚛 CATEGORÍA 2: Shipping

### Commerce Groups
- **ME Distribución** (Mercado Envíos - Comprador)
- **ME PreDespacho** (Mercado Envíos - Vendedor)
- **FBM Sellers** (Fulfillment by Mercado Libre)
- **ME Drivers** (Drivers de Mercado Envíos)

### Drivers Específicos

| Commerce Group | Driver Code | Tabla | Campo | Descripción |
|----------------|-------------|-------|-------|-------------|
| **ME Distribución** | OS_TOTALES | `BT_CX_DRIVERS_CR` | `SUM(ORDERS_SHIPPED)` | Órdenes totales shipped |
| **ME PreDespacho** | OS_WO_FULL | `BT_CX_DRIVERS_CR` | `SUM(OS_WITHOUT_FBM)` | Órdenes sin FBM |
| **FBM Sellers** | OS_FULL | `BT_CX_DRIVERS_CR` | `SUM(OS_WITH_FBM)` | Órdenes con FBM |
| **ME Drivers** | OS_TOTALES | `BT_CX_DRIVERS_CR` | `SUM(ORDERS_SHIPPED)` | Pendiente driver específico |

### Características
- **Filtro por site:** ❌ NO (driver global)
- **Fecha:** `MONTH_ID` (tipo DATE, no INT64)
- **Agregación:** SUM (no COUNT)

### Razón
Los drivers de Shipping representan el universo logístico específico para cada tipo de operación (shipped, sin FBM, con FBM), calculado globalmente.

### Ejemplo Query (ME PreDespacho)
```sql
SELECT
    SUM(drv.OS_WITHOUT_FBM) as DRIVER_TOTAL
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-11-30'
-- NO filtrar por site
-- NO otros filtros
```

**Resultado esperado:** ~87.8M órdenes sin FBM (Nov 2025, global)

**Referencia completa:** `docs/SHIPPING_DRIVERS.md`

---

## 🛒 CATEGORÍA 3: Marketplace

### Commerce Groups
- **Pre Venta** (Consultas pre-venta)
- **Post Venta** (Soporte post-venta)
- **Generales Compra** (Consultas generales)
- **Moderaciones** (Moderaciones y Prustomer)
- **Full Sellers** (Full Sellers)
- **Pagos** (Pagos y transacciones)
- **Loyalty** (Programa de lealtad)

### Driver
- **Tipo:** Órdenes totales **FILTRADAS POR SITE**
- **Tabla:** `BT_ORD_ORDERS`
- **Campo:** `COUNT(DISTINCT ORD_ORDER_ID)`
- **Filtros:**
  - `ORD_GMV_FLG = TRUE`
  - `ORD_MARKETPLACE_FLG = TRUE`
  - `SIT_SITE_ID = '{site}'` ← **FILTRO POR SITE**
  - `DOM_DOMAIN_ID <> 'TIPS'`

### Razón
Los commerce groups de Marketplace están directamente relacionados con la actividad del marketplace en cada país específico. Se usa driver por site para reflejar el volumen de transacciones del mercado analizado.

### Ejemplo Query (Generales Compra - MLM)
```sql
SELECT
    COUNT(DISTINCT ORD.ORD_ORDER_ID) as DRIVER_TOTAL
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE ORD.ORD_CLOSED_DT BETWEEN '2025-11-01' AND '2025-11-30'
    AND ORD.ORD_GMV_FLG = TRUE
    AND ORD.ORD_MARKETPLACE_FLG = TRUE
    AND ORD.SIT_SITE_ID = 'MLM'  -- ✅ Filtrado por site
    AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
```

**Resultado esperado:** ~15M órdenes (Nov 2025, solo MLM)

---

## 💳 CATEGORÍA 4: Pagos

### Commerce Groups
- **MP On** (Mercado Pago Online)

### Driver
- **Tipo:** Órdenes totales **GLOBALES** (sin filtro site)
- **Tabla:** `BT_ORD_ORDERS`
- **Campo:** `COUNT(DISTINCT ORD_ORDER_ID)`
- **Filtros:** Mismos que Post-Compra

### Razón
MP On es un servicio transversal a todos los sites, por lo que se usa driver global.

---

## 👤 CATEGORÍA 5: Cuenta

### Commerce Groups
- **Cuenta** (Gestión de cuenta y seguridad)
- **Experiencia Impositiva** (Gestión impositiva)

### Driver
- **Tipo:** Órdenes totales **GLOBALES** (sin filtro site)
- **Tabla:** `BT_ORD_ORDERS`
- **Campo:** `COUNT(DISTINCT ORD_ORDER_ID)`
- **Filtros:** Mismos que Post-Compra

### Razón
Los temas de Cuenta son transversales a la actividad del usuario en la plataforma global.

---

## 🔧 Implementación en Scripts

### Configuración Automática

El script `generar_reporte_cr_universal_v6.3.6.py` usa el módulo `config/drivers_mapping.py` para seleccionar automáticamente el driver correcto.

**Flujo:**
1. Usuario especifica `--commerce-group GENERALES_COMPRA --site MLM`
2. Script lee configuración: `get_driver_config('GENERALES_COMPRA')`
3. Detecta que es tipo `orders_by_site` con `filter_by_site: True`
4. Genera query con filtro `SIT_SITE_ID = 'MLM'`

### Código de Ejemplo

```python
from config.drivers_mapping import get_driver_config

# Obtener configuración
driver_config = get_driver_config('GENERALES_COMPRA')

# Resultado:
# {
#   'type': 'orders_by_site',
#   'table': 'BT_ORD_ORDERS',
#   'filter_by_site': True,
#   'description': 'Órdenes totales del site específico'
# }

# Generar query
if driver_config['filter_by_site']:
    query = f"""
    SELECT COUNT(*) as DRIVER
    FROM BT_ORD_ORDERS
    WHERE SIT_SITE_ID = '{site}'
    """
else:
    query = f"""
    SELECT COUNT(*) as DRIVER
    FROM BT_ORD_ORDERS
    WHERE SIT_SITE_ID NOT IN ('MLV')
    """
```

---

## 📋 Tabla de Referencia Rápida

| Commerce Group | Driver | Filtrar por Site | Tabla |
|----------------|--------|------------------|-------|
| PDD | Órdenes totales | ❌ NO | BT_ORD_ORDERS |
| PNR | Órdenes totales | ❌ NO | BT_ORD_ORDERS |
| ME Distribución | OS_TOTALES | ❌ NO | BT_CX_DRIVERS_CR |
| ME PreDespacho | OS_WO_FULL | ❌ NO | BT_CX_DRIVERS_CR |
| FBM Sellers | OS_FULL | ❌ NO | BT_CX_DRIVERS_CR |
| ME Drivers | OS_TOTALES | ❌ NO | BT_CX_DRIVERS_CR |
| Pre Venta | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Post Venta | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Generales Compra | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Moderaciones | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Full Sellers | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Pagos | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| Loyalty | Órdenes totales | ✅ SÍ | BT_ORD_ORDERS |
| MP On | Órdenes totales | ❌ NO | BT_ORD_ORDERS |
| Cuenta | Órdenes totales | ❌ NO | BT_ORD_ORDERS |
| Exp. Impositiva | Órdenes totales | ❌ NO | BT_ORD_ORDERS |

---

## ✅ Checklist de Validación

Cuando generes un reporte, verifica:

### Para Marketplace
- [ ] ¿El driver se filtró por el site correcto?
- [ ] ¿El volumen de driver es razonable para ese site?
- [ ] ¿La descripción del driver dice "site específico - {SITE}"?

### Para Post-Compra/Pagos/Cuenta
- [ ] ¿El driver es GLOBAL (sin filtro site)?
- [ ] ¿El volumen de driver refleja todos los sites (excepto MLV)?
- [ ] ¿La descripción del driver dice "GLOBALES (sin filtro site)"?

### Para Shipping
- [ ] ¿Se usó la tabla BT_CX_DRIVERS_CR?
- [ ] ¿Se usó el campo correcto (ORDERS_SHIPPED, OS_WITHOUT_FBM, OS_WITH_FBM)?
- [ ] ¿El driver es GLOBAL (sin filtro site)?

---

## 🔗 Referencias

- **Configuración de drivers:** `config/drivers-mapping.py`
- **Drivers de Shipping:** `docs/SHIPPING_DRIVERS.md`
- **Filtros base de órdenes:** `docs/BASE_FILTERS_ORDERS.md`
- **Commerce Groups:** `docs/COMMERCE_GROUPS_REFERENCE.md`
- **Script principal:** `generar_reporte_cr_universal_v6.3.6.py`

---

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Status:** ✅ OFICIAL - Implementado  
**Changelog:** Primera versión - separación de Marketplace con filtro por site
