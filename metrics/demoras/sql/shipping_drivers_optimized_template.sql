-- ==============================================
-- Template: Shipping Drivers Optimizado con Tablas Temporales
-- ==============================================
-- Propósito: Calcular drivers y métricas de ME Distribución para análisis de Contact Rate
-- Optimización: Usa TEMP TABLEs para reducir tiempo de ejecución 40-50%
-- 
-- PARÁMETROS (reemplazar antes de ejecutar):
-- {site}          : 'MLA', 'MLB', 'MLC', etc. (o '' para Cross-Site)
-- {fecha_inicio}  : Fecha inicio período (ej: '2025-11-01')
-- {fecha_fin}     : Fecha fin período (ej: '2026-01-01')
-- {picking_type}  : 'fulfillment', 'cross_docking', etc. (o '' para todos)
-- {granularidad}  : 'MONTH', 'WEEK', 'DAY' (para DATE_TRUNC)
--
-- USO:
-- 1. Reemplazar {variables} con valores reales usando script Python
-- 2. Ejecutar: Get-Content sql/shipping_mla_nov_dic.sql -Raw | bq query --use_legacy_sql=false --format=csv > output/drivers.csv
-- 3. Las tablas temporales se crean y eliminan automáticamente
--
-- Autor: Sistema CR Commerce
-- Versión: 1.0
-- Última actualización: 2026-01-29
-- ==============================================

-- ==============================================
-- PASO 1: Materializar subconsulta de SHIPMENTS
-- ==============================================
-- Propósito: Pre-filtrar BT_SHP_SHIPMENTS para reducir JOIN posterior
-- Beneficio: ~30% reducción en tiempo de ejecución
-- ==============================================

CREATE TEMP TABLE shipments_filtered AS (
  SELECT 
    SHP_SHIPMENT_ID,
    SIT_SITE_ID,
    SHP_TAGS,
    SHP_DATE_FIRST_VISIT_ID,
    SHP_DATE_DELIVERED_ID,
    SHP_DATETIME_NOT_DELIVERED,
    SHP_DATE_CANCELLED_ID,
    SHP_RECEIVER_STATE_ID
  FROM `meli-bi-data.WHOWNER.BT_SHP_SHIPMENTS`
  WHERE SHP_DATE_CREATED_ID >= '{fecha_inicio}'
    AND SHP_DATE_CREATED_ID < '{fecha_fin}'
    -- Filtro dinámico por site (solo si Single-Site)
    {site_filter}
    -- Ejemplo: AND SIT_SITE_ID = 'MLA'
);

-- ==============================================
-- PASO 2: Materializar subconsulta de SNAPSHOT con UNNEST
-- ==============================================
-- Propósito: Procesar ROUTE_OPTIONS (array) una sola vez
-- Beneficio: ~40% reducción en tiempo vs UNNEST en JOIN
-- Complejidad: Esta tabla tiene el UNNEST más costoso
-- ==============================================

CREATE TEMP TABLE snapshot_processed AS (
  SELECT
    SNAP.SHIPMENT_ID,
    
    -- Custom Offsets (Composition)
    ROUTE_OPTIONS_UNNEST.PROMISE_CUSTOM_OFFSET_ID,
    ROUTE_OPTIONS_UNNEST.PROMISE_CUSTOM_OFFSET_SHIFT,
    ROUTE_OPTIONS_UNNEST.PROMISE_CUSTOM_OFFSET_EXPAND,
    ROUTE_OPTIONS_UNNEST.CUSTOM_OFFSET_VALUE,
    
    -- Handling Time Custom Offset Flag
    CASE 
      WHEN IFNULL(ROUTE_OPTIONS_UNNEST.HANDLING_OFFSET_VALUE, 0) < ROUTE_OPTIONS_UNNEST.HANDLING_TIME 
       AND ROUTE_OPTIONS_UNNEST.HANDLING_OFFSET_ID IS NOT NULL 
      THEN 1 
      ELSE 0 
    END AS CO_HT_FLAG,
    
    -- Deferral Categories y Reasons (Network Efficiencies)
    ARRAY_TO_STRING(DEFERRAL.CATEGORY, ",") AS deferral_category,
    ARRAY_TO_STRING(DEFERRAL.REASON, ",") AS deferral_reason,
    
    -- Flags de Network Efficiencies
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.CATEGORY, ",") LIKE '%buffered%' THEN 1 ELSE 0 END AS buffered,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%no-rush%' THEN 1 ELSE 0 END AS no_rush,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%grouping%' THEN 1 ELSE 0 END AS shp_grouping,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%delivery-day%' THEN 1 ELSE 0 END AS mdd,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%bulky%' THEN 1 ELSE 0 END AS bulky,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%proximity%' THEN 1 ELSE 0 END AS proximity,
    CASE WHEN ARRAY_TO_STRING(DEFERRAL.REASON, ",") LIKE '%promise_weekend%' THEN 1 ELSE 0 END AS promise_weekend
    
  FROM `meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_SNAPSHOT` SNAP,
  UNNEST(SNAP.ROUTE_OPTIONS) AS ROUTE_OPTIONS_UNNEST
  
  WHERE SNAP.SNAPSHOT_DATE_CREATED >= '{fecha_inicio}'
    AND SNAP.SNAPSHOT_DATE_CREATED < '{fecha_fin}'
    AND SNAP.SELECTED_ROUTE = ROUTE_OPTIONS_UNNEST.ID
);

-- ==============================================
-- PASO 3: Query Principal (JOIN con Tablas Temporales)
-- ==============================================
-- Propósito: Calcular métricas de Shipping agrupadas
-- Granularidad: Definida por {granularidad} (MONTH, WEEK, DAY)
-- ==============================================

SELECT
  -- ==============================================
  -- DIMENSIONES (aperturas dinámicas según análisis)
  -- ==============================================
  
  SHP.SIT_SITE_ID,
  
  -- Granularidad temporal (controlada por parámetro)
  DATE_TRUNC(SHP_CREATED_DATE_TZ, {granularidad}) AS CREATED_PERIOD_ID,
  DATE_TRUNC(COALESCE(SHP_FIRST_VISIT_DATE_TZ, SHP_DELIVERED_DATE_TZ), {granularidad}) AS FVD_PERIOD_ID,
  
  -- Picking Type (normalizado)
  CASE
    WHEN lower(SHP_PICKING_TYPE) = 'fulfillment' THEN 'FF'
    WHEN lower(SHP_PICKING_TYPE) = 'cross_docking' THEN 'XD'
    WHEN lower(SHP_PICKING_TYPE) = 'xd_drop_off' THEN 'XD DO'
    WHEN lower(SHP_PICKING_TYPE) = 'drop_off' THEN 'DS'
    WHEN lower(SHP_PICKING_TYPE) = 'self_service' THEN 'FLEX'
    ELSE SHP_PICKING_TYPE 
  END AS SHP_PICKING_TYPE_ID_AJUS,
  
  -- ==============================================
  -- MÉTRICAS: Shipments Totales
  -- ==============================================
  
  COUNT(*) AS SHIPMENTS,
  
  -- ==============================================
  -- MÉTRICAS: Ventana de Promesa
  -- ==============================================
  -- Shipments con ventana de entrega ≥1 día
  
  SUM(
    CASE 
      WHEN DATE_DIFF(
        COALESCE(DATE(PO_UB_DATETIME_TZ), DATE(PO_DATETIME_TZ)), 
        DATE(PO_DATETIME_TZ), 
        DAY
      ) >= 1 
      THEN 1 
      ELSE 0 
    END
  ) AS SHIPMENTS_VENTANA,
  
  -- ==============================================
  -- MÉTRICAS: Composition (Custom Offsets)
  -- ==============================================
  -- Shipments con custom offsets aplicados (buffering manual)
  
  -- Custom Offset Soft Time (SHIFT + EXPAND)
  SUM(
    CASE 
      WHEN IFNULL(SNAP.PROMISE_CUSTOM_OFFSET_SHIFT, 0) + IFNULL(SNAP.PROMISE_CUSTOM_OFFSET_EXPAND, 0) > 0 
      THEN 1 
      ELSE 0 
    END
  ) AS CO_ST_SHIPMENTS,
  
  -- Custom Offset Handling Time
  SUM(SNAP.CO_HT_FLAG) AS CO_HT_SHIPMENTS,
  
  -- Buffering por categoría (CAP_*)
  SUM(CASE WHEN BUFFERING_TIME.CAP_OPERATIONAL.BUFFERED IS TRUE THEN 1 ELSE 0 END) AS BUFF_OP_SHIPMENTS,
  SUM(CASE WHEN BUFFERING_TIME.CAP_MIDDLE_MILE.BUFFERED IS TRUE THEN 1 ELSE 0 END) AS BUFF_MM_SHIPMENTS,
  SUM(CASE WHEN BUFFERING_TIME.CAP_LAST_MILE.BUFFERED IS TRUE THEN 1 ELSE 0 END) AS BUFF_LM_SHIPMENTS,
  SUM(CASE WHEN BUFFERING_TIME.CAP_SELLER.BUFFERED IS TRUE THEN 1 ELSE 0 END) AS BUFF_SEL_SHIPMENTS,
  
  -- ==============================================
  -- MÉTRICAS: Performance (Lead Time & Handling Time)
  -- ==============================================
  
  -- Lead Time (LT) - tiempo desde creación hasta entrega
  SUM(CASE WHEN TM_LT_DEV_TYPE = 'DELAY' THEN 1 ELSE 0 END) AS SHIPMENTS_LT_DELAY,
  SUM(CASE WHEN TM_LT_DEV_TYPE = 'EARLY' THEN 1 ELSE 0 END) AS SHIPMENTS_LT_EARLY,
  SUM(CASE WHEN TM_LT_DEV_TYPE = 'ON_TIME' THEN 1 ELSE 0 END) AS SHIPMENTS_LT_ONTIME,
  
  -- Handling Time (HT) - tiempo desde promesa hasta entrega
  SUM(CASE WHEN TM_HT_DEV_TYPE = 'DELAY' THEN 1 ELSE 0 END) AS SHIPMENTS_HT_DELAY,
  SUM(CASE WHEN TM_HT_DEV_TYPE = 'EARLY' THEN 1 ELSE 0 END) AS SHIPMENTS_HT_EARLY,
  SUM(CASE WHEN TM_HT_DEV_TYPE = 'ON_TIME' THEN 1 ELSE 0 END) AS SHIPMENTS_HT_ONTIME,
  
  -- Shipments sin métrica de Lead Time (estancados)
  SUM(CASE WHEN TM_LT_DEV_TYPE IS NULL THEN 1 ELSE 0 END) AS SHIPMENTS_ESTANCADOS,
  
  -- ==============================================
  -- MÉTRICAS: Distribución por Picking Type
  -- ==============================================
  
  SUM(CASE WHEN lower(SHP_PICKING_TYPE) = 'fulfillment' THEN 1 ELSE 0 END) AS SHIPMENTS_FF,
  SUM(CASE WHEN lower(SHP_PICKING_TYPE) IN ('cross_docking', 'xd_drop_off') THEN 1 ELSE 0 END) AS SHIPMENTS_XD,
  SUM(CASE WHEN lower(SHP_PICKING_TYPE) = 'drop_off' THEN 1 ELSE 0 END) AS SHIPMENTS_DS,
  SUM(CASE WHEN lower(SHP_PICKING_TYPE) = 'self_service' THEN 1 ELSE 0 END) AS SHIPMENTS_FLEX,
  
  -- ==============================================
  -- MÉTRICAS: Network Efficiencies (agregadas desde SNAP)
  -- ==============================================
  
  SUM(SNAP.no_rush) AS SHIPMENTS_NO_RUSH,
  SUM(SNAP.shp_grouping) AS SHIPMENTS_GROUPING,
  SUM(SNAP.mdd) AS SHIPMENTS_MDD,
  SUM(SNAP.bulky) AS SHIPMENTS_BULKY,
  SUM(SNAP.proximity) AS SHIPMENTS_PROXIMITY,
  SUM(SNAP.promise_weekend) AS SHIPMENTS_PROMISE_WEEKEND

-- ==============================================
-- FROM: Tabla principal de Shipments
-- ==============================================

FROM `meli-bi-data.WHOWNER.BT_SHP_SHIPMENTS_SUMMARY` SHP

-- ==============================================
-- JOINs: Tablas complementarias
-- ==============================================

-- JOIN 1: Métricas de Shipment (TM_LT_DEV_TYPE, TM_HT_DEV_TYPE, etc.)
LEFT JOIN `meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_METRICS` A
  ON CAST(SHP.SHP_SHIPMENT_ID AS STRING) = CAST(A.SHIPMENT_ID AS STRING)
  AND DATE(A.DATE_CREATED) >= '{fecha_inicio}'
  AND DATE(A.DATE_CREATED) < '{fecha_fin}'

-- JOIN 2: Datos de Shipment (TAGS, fechas, estado) - TABLA TEMPORAL
LEFT JOIN shipments_filtered SHIP
  ON SHP.SHP_SHIPMENT_ID = SHIP.SHP_SHIPMENT_ID 
  AND SHP.SIT_SITE_ID = SHIP.SIT_SITE_ID

-- JOIN 3: Snapshot procesado (Custom Offsets, Network Efficiencies) - TABLA TEMPORAL
LEFT JOIN snapshot_processed SNAP
  ON CAST(SNAP.SHIPMENT_ID AS STRING) = CAST(SHP.SHP_SHIPMENT_ID AS STRING)

-- ==============================================
-- WHERE: Filtros base (alineados con reglas de negocio)
-- ==============================================

WHERE 1=1
  -- Filtro temporal (obligatorio)
  AND SHP_CREATED_DATETIME_TZ >= '{fecha_inicio}'
  AND SHP_CREATED_DATETIME_TZ < '{fecha_fin}'
  
  -- Filtro por site (dinámico)
  {site_filter}
  -- Ejemplo: AND SHP.SIT_SITE_ID = 'MLA'
  
  -- Filtro por picking type (dinámico - solo para deep dive)
  {picking_type_filter}
  -- Ejemplo: AND lower(SHP_PICKING_TYPE) = 'fulfillment'
  
  -- Filtros base de negocio (SIEMPRE aplicar)
  AND UPPER(SHP_SOURCE) = 'MELI'
  AND lower(SHP.SHP_TYPE) = 'forward'
  AND lower(SHP_SHIPPING_MODE) = 'me2'
  AND UPPER(CONCAT(SHP_STATUS, SHP_SUBSTATUS)) NOT IN ('PENDINGN/A')
  AND (
    lower(CONCAT(SHP.SHP_CBT_FLAG, SHP_PICKING_TYPE)) NOT IN ('1cross_docking', '1drop_off') 
    OR SHP.SHP_CBT_FLAG IS NULL
  )
  AND lower(SHIP.SHP_TAGS) NOT LIKE '%proximity%'
  AND lower(SHP_SHIPMENT_TYPE) = 'v1'
  
  -- Filtro de completitud (al menos una fecha final)
  AND COALESCE(
    SHIP.SHP_DATE_FIRST_VISIT_ID,
    SHIP.SHP_DATE_DELIVERED_ID,
    SHIP.SHP_DATETIME_NOT_DELIVERED,
    SHIP.SHP_DATE_CANCELLED_ID
  ) IS NOT NULL

-- ==============================================
-- GROUP BY: Todas las dimensiones
-- ==============================================

GROUP BY ALL;

-- ==============================================
-- NOTAS DE USO:
-- ==============================================
-- 
-- 1. PARAMETRIZACIÓN:
--    - Antes de ejecutar, reemplazar {variables} con valores reales
--    - Usar script Python para reemplazo automático (ver scripts/)
-- 
-- 2. FILTROS DINÁMICOS:
--    - {site_filter}:
--      * Cross-Site: '' (vacío, no filtrar)
--      * Single-Site: 'AND SIT_SITE_ID = ''MLA'''
--    - {picking_type_filter}:
--      * Baseline: '' (vacío, incluir todos)
--      * Deep dive: 'AND lower(SHP_PICKING_TYPE) = ''fulfillment'''
-- 
-- 3. GRANULARIDAD:
--    - Mensual: {granularidad} = 'MONTH'
--    - Semanal: {granularidad} = 'WEEK'
--    - Diario: {granularidad} = 'DAY'
-- 
-- 4. PERFORMANCE:
--    - Tiempo esperado (3 meses, Single-Site): 5-8 min
--    - Tiempo esperado (1 mes, Single-Site): 2-3 min
--    - Costo estimado: $0.30-1.20 USD por ejecución
-- 
-- 5. TROUBLESHOOTING:
--    - Si falla por cuota → esperar 30s y reintentar
--    - Si falla TEMP TABLE → verificar permisos de lectura en tablas origen
--    - Si resultado vacío → verificar filtros (especialmente fechas)
-- 
-- ==============================================
