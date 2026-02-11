# Fuente de Datos: Demoras en Shipping

## 📊 Tablas Fuente

### Tabla 1: `BT_SHP_SHIPMENTS_SUMMARY` (Principal)

**Ubicación:** `meli-bi-data.WHOWNER.BT_SHP_SHIPMENTS_SUMMARY`

**Propósito:** Tabla agregada de shipments con información general de envíos.

**Campos utilizados:**

| Campo | Tipo | Descripción | Uso en Análisis |
|-------|------|-------------|-----------------|
| `SHP_SHIPMENT_ID` | STRING | ID único del shipment | JOIN con otras tablas |
| `SIT_SITE_ID` | STRING | Site (MLA, MLB, etc.) | Filtro y agrupación |
| `SHP_CREATED_DATE_TZ` | TIMESTAMP | Fecha de creación del shipment | Filtro temporal principal |
| `SHP_FIRST_VISIT_DATE_TZ` | TIMESTAMP | Fecha de primera visita | Cálculo de FVD |
| `SHP_DELIVERED_DATE_TZ` | TIMESTAMP | Fecha de entrega | Cálculo de FVD (fallback) |
| `SHP_PICKING_TYPE` | STRING | Tipo de picking (fulfillment, cross_docking, etc.) | Dimensión de análisis |
| `SHP_SOURCE` | STRING | Fuente del shipment (MELI, etc.) | Filtro de negocio |
| `SHP_TYPE` | STRING | Tipo de shipment (forward, reverse) | Filtro de negocio |
| `SHP_SHIPPING_MODE` | STRING | Modo de envío (me2, etc.) | Filtro de negocio |
| `SHP_STATUS` | STRING | Estado del shipment | Filtro de negocio |
| `SHP_SUBSTATUS` | STRING | Subestado del shipment | Filtro de negocio |
| `SHP_CBT_FLAG` | BOOLEAN | Flag de Cross-Border Trade | Filtro de negocio |
| `SHP_SHIPMENT_TYPE` | STRING | Tipo de shipment (v1, v2) | Filtro de negocio |
| `PO_DATETIME_TZ` | TIMESTAMP | Fecha de promesa original | Cálculo de ventana |
| `PO_UB_DATETIME_TZ` | TIMESTAMP | Fecha de promesa actualizada | Cálculo de ventana |
| `BUFFERING_TIME` | STRUCT | Información de buffering por categoría | Métricas de composition |

**Cardinalidad:** ~50-100M registros/mes (todos los sites)

**Actualización:** Diaria (datos disponibles D+1)

---

### Tabla 2: `BT_SHP_SHIPMENTS` (Complementaria)

**Ubicación:** `meli-bi-data.WHOWNER.BT_SHP_SHIPMENTS`

**Propósito:** Información detallada de shipments (tags, fechas, estados).

**Campos utilizados:**

| Campo | Tipo | Descripción | Uso en Análisis |
|-------|------|-------------|-----------------|
| `SHP_SHIPMENT_ID` | INT64 | ID del shipment | JOIN con SUMMARY |
| `SIT_SITE_ID` | STRING | Site | JOIN + Filtro |
| `SHP_TAGS` | STRING | Tags del shipment | Filtro (proximity, etc.) |
| `SHP_DATE_FIRST_VISIT_ID` | DATE | Fecha de primera visita | Cálculo de completitud |
| `SHP_DATE_DELIVERED_ID` | DATE | Fecha de entrega | Cálculo de completitud |
| `SHP_DATETIME_NOT_DELIVERED` | TIMESTAMP | Fecha de no entregado | Cálculo de completitud |
| `SHP_DATE_CANCELLED_ID` | DATE | Fecha de cancelación | Cálculo de completitud |
| `SHP_RECEIVER_STATE_ID` | STRING | Estado destino | Dimensión adicional (futuro) |

**Por qué tabla separada:** Campos de baja cardinalidad que no están en SUMMARY.

**Optimización:** Se pre-filtra en tabla temporal `shipments_filtered` para reducir JOIN.

---

### Tabla 3: `BT_SHP_MT_SHIPMENT_METRICS` (Performance)

**Ubicación:** `meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_METRICS`

**Propósito:** Métricas calculadas de performance (Lead Time, Handling Time).

**Campos utilizados:**

| Campo | Tipo | Descripción | Uso en Análisis |
|-------|------|-------------|-----------------|
| `SHIPMENT_ID` | STRING | ID del shipment | JOIN con SUMMARY |
| `DATE_CREATED` | DATE | Fecha de cálculo de la métrica | Filtro temporal |
| `TM_LT_DEV_TYPE` | STRING | Tipo de desvío en Lead Time | Métrica de performance |
| `TM_HT_DEV_TYPE` | STRING | Tipo de desvío en Handling Time | Métrica de performance |

**Valores de `TM_LT_DEV_TYPE` / `TM_HT_DEV_TYPE`:**
- `'DELAY'`: Entrega demorada respecto a promesa
- `'EARLY'`: Entrega anticipada
- `'ON_TIME'`: Entrega en tiempo
- `NULL`: Sin métrica calculada (shipment estancado o sin completar)

**Importancia:** Estos campos son CRÍTICOS para identificar demoras reales que generan contactos.

---

### Tabla 4: `BT_SHP_MT_SHIPMENT_SNAPSHOT` (Composition)

**Ubicación:** `meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_SNAPSHOT`

**Propósito:** Snapshot de configuración de rutas (custom offsets, deferrals).

**Campos utilizados:**

| Campo | Tipo | Descripción | Uso en Análisis |
|-------|------|-------------|-----------------|
| `SHIPMENT_ID` | INT64 | ID del shipment | JOIN con SUMMARY |
| `SNAPSHOT_DATE_CREATED` | DATE | Fecha del snapshot | Filtro temporal |
| `SELECTED_ROUTE` | STRING | ID de la ruta seleccionada | Filtro para UNNEST |
| `ROUTE_OPTIONS` | ARRAY<STRUCT> | Array de opciones de ruta | UNNEST para extraer datos |

**Estructura de `ROUTE_OPTIONS` (STRUCT):**

| Subcampo | Tipo | Descripción | Uso |
|----------|------|-------------|-----|
| `ID` | STRING | ID de la opción de ruta | Match con SELECTED_ROUTE |
| `PROMISE_CUSTOM_OFFSET_ID` | STRING | ID del custom offset aplicado | Flag de composition |
| `PROMISE_CUSTOM_OFFSET_SHIFT` | INT64 | Días de shift aplicados | Cálculo de CO_ST |
| `PROMISE_CUSTOM_OFFSET_EXPAND` | INT64 | Días de expansión aplicados | Cálculo de CO_ST |
| `CUSTOM_OFFSET_VALUE` | INT64 | Valor total del offset | Métrica agregada |
| `HANDLING_OFFSET_VALUE` | INT64 | Offset en handling time | Cálculo de CO_HT |
| `HANDLING_OFFSET_ID` | STRING | ID del offset en HT | Flag de CO_HT |
| `HANDLING_TIME` | INT64 | Handling time base | Comparación para CO_HT |
| `DEFERRAL.CATEGORY` | ARRAY<STRING> | Categorías de deferral | Network efficiencies |
| `DEFERRAL.REASON` | ARRAY<STRING> | Razones de deferral | Network efficiencies |

**⚠️ CRÍTICO:** Esta tabla requiere `UNNEST(ROUTE_OPTIONS)` para acceder a los campos.

**Optimización:** Se materializa en tabla temporal `snapshot_processed` para evitar UNNEST repetido.

**Network Efficiencies - Razones de Deferral:**

| Razón | Descripción | Impacto en CR |
|-------|-------------|---------------|
| `no-rush` | Demora intencional para optimización de ruta | Bajo (usuario no espera rapidez) |
| `grouping` | Agrupación de envíos para eficiencia | Medio (puede retrasar entrega) |
| `delivery-day` | My Delivery Day (día elegido) | Bajo (usuario eligió la fecha) |
| `bulky` | Producto voluminoso requiere logística especial | Alto (demoras inesperadas) |
| `proximity` | Optimización por cercanía | Medio |
| `promise_weekend` | Promesa en fin de semana | Medio (posibles delays) |
| `buffered` | Buffering general aplicado | Alto (cambios de promesa) |

---

## 🔄 Relación entre Tablas

```
BT_SHP_SHIPMENTS_SUMMARY (principal)
│
├─> BT_SHP_SHIPMENTS (complementaria)
│   └─> Filtros: SHP_TAGS, fechas de completitud
│
├─> BT_SHP_MT_SHIPMENT_METRICS (performance)
│   └─> Métricas: TM_LT_DEV_TYPE, TM_HT_DEV_TYPE
│
└─> BT_SHP_MT_SHIPMENT_SNAPSHOT (composition)
    └─> Custom Offsets + Network Efficiencies
```

**JOINs aplicados:**
- SUMMARY ↔ SHIPMENTS: `SHP_SHIPMENT_ID` + `SIT_SITE_ID`
- SUMMARY ↔ METRICS: `CAST(SHP_SHIPMENT_ID AS STRING)` = `CAST(SHIPMENT_ID AS STRING)`
- SUMMARY ↔ SNAPSHOT: `CAST(SHP_SHIPMENT_ID AS STRING)` = `CAST(SHIPMENT_ID AS STRING)`

---

## 🛡️ Filtros de Negocio (SIEMPRE Aplicar)

### Filtros obligatorios:

```sql
WHERE 1=1
  -- Fuente y tipo
  AND UPPER(SHP_SOURCE) = 'MELI'
  AND lower(SHP.SHP_TYPE) = 'forward'
  AND lower(SHP_SHIPPING_MODE) = 'me2'
  
  -- Estado válido
  AND UPPER(CONCAT(SHP_STATUS, SHP_SUBSTATUS)) NOT IN ('PENDINGN/A')
  
  -- Excluir CBT (Cross-Border Trade) DS y XD
  AND (
    lower(CONCAT(SHP.SHP_CBT_FLAG, SHP_PICKING_TYPE)) NOT IN ('1cross_docking', '1drop_off') 
    OR SHP.SHP_CBT_FLAG IS NULL
  )
  
  -- Excluir proximity
  AND lower(SHIP.SHP_TAGS) NOT LIKE '%proximity%'
  
  -- Versión v1
  AND lower(SHP_SHIPMENT_TYPE) = 'v1'
  
  -- Completitud (al menos una fecha final)
  AND COALESCE(
    SHIP.SHP_DATE_FIRST_VISIT_ID,
    SHIP.SHP_DATE_DELIVERED_ID,
    SHIP.SHP_DATETIME_NOT_DELIVERED,
    SHIP.SHP_DATE_CANCELLED_ID
  ) IS NOT NULL
```

**Motivo de cada filtro:** Ver `docs/SHIPPING_DRIVERS.md` para justificación detallada.

---

## 📊 Volumen de Datos

| Configuración | Registros Procesados | Tamaño Escaneado | Tiempo Estimado |
|---------------|----------------------|------------------|-----------------|
| 1 mes × MLA | ~3-5M registros | ~50-80 GB | 2-3 min |
| 3 meses × MLA | ~10-15M registros | ~150-250 GB | 5-8 min |
| 3 meses × Cross-Site | ~50-80M registros | ~500-800 GB | 10-15 min |

**Con tablas temporales:** Reducción de 40-50% en tiempo de ejecución.

---

## 🔍 Campos Calculados

### Ventana de Promesa

```sql
DATE_DIFF(
  COALESCE(DATE(PO_UB_DATETIME_TZ), DATE(PO_DATETIME_TZ)), 
  DATE(PO_DATETIME_TZ), 
  DAY
) >= 1
```

**Lógica:** Compara promesa actualizada vs original. Si hay ≥1 día de diferencia, hay ventana.

### Custom Offset Soft Time (CO_ST)

```sql
IFNULL(PROMISE_CUSTOM_OFFSET_SHIFT, 0) + IFNULL(PROMISE_CUSTOM_OFFSET_EXPAND, 0) > 0
```

**Lógica:** Si hay SHIFT o EXPAND aplicado, se considera custom offset en soft time.

### Custom Offset Handling Time (CO_HT)

```sql
IFNULL(HANDLING_OFFSET_VALUE, 0) < HANDLING_TIME 
AND HANDLING_OFFSET_ID IS NOT NULL
```

**Lógica:** Si el offset en HT es menor al HT base y existe ID, hay CO en handling time.

---

## ⚠️ Consideraciones de Performance

### 1. **Tabla SNAPSHOT es la más pesada**

El `UNNEST(ROUTE_OPTIONS)` puede generar millones de filas intermedias.

**Solución:** Materializar en tabla temporal ANTES del JOIN principal.

### 2. **CAST de SHIPMENT_ID**

Diferentes tipos (INT64 vs STRING) requieren casting explícito.

**Solución:** `CAST(SHP_SHIPMENT_ID AS STRING)` consistente en todos los JOINs.

### 3. **Filtro temporal en cada tabla**

Aplicar filtro de fecha en CADA tabla del JOIN, no solo en WHERE final.

**Beneficio:** Reduce escaneo antes del JOIN (particionamiento de BigQuery).

---

## 📚 Referencias

- **Query optimizada:** `sql/shipping_drivers_optimized_template.sql`
- **Script de parametrización:** `scripts/parametrize_shipping_query.py`
- **Integración CR:** `INTEGRACION_CR.md`
- **Documentación Shipping:** `../../docs/SHIPPING_DRIVERS.md`

---

**Versión:** 1.0  
**Estado:** ✅ VALIDADO  
**Última actualización:** 2026-01-29
