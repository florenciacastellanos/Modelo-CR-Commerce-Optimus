# 🗄️ Definiciones de Tablas BigQuery

## Tablas Principales

### BT_CX_CONTACTS

**Tabla principal** que centraliza todos los contactos de clientes con el área de CX.

**Ubicación:** `meli-bi-data.WHOWNER.BT_CX_CONTACTS`

**Descripción:** Consolidación de contactos incoming, claims, y otros canales de atención.

#### Campos Principales

| Campo | Tipo | Descripción | Uso en CR |
|-------|------|-------------|-----------|
| `CAS_CASE_ID` | STRING | ID único del caso | Identificador |
| `CUS_CUST_ID` | INT64 | ID del cliente | Segmentación |
| `CONTACT_DATE_ID` | DATETIME | Fecha/hora del contacto | **Filtro principal** |
| `SIT_SITE_ID` | STRING | Site (país): MLA, MLB, etc. | **Filtro obligatorio** |
| `PROCESS_ID` | INT64 | ID del proceso | Filtro/exclusión |
| `PROCESS_NAME` | STRING | Nombre del proceso | **Dimensión análisis** |
| `PROCESS_GROUP_ECOMMERCE` | STRING | Grupo de ecommerce | **User Type** |
| `PROCESS_BU_CR_REPORTING` | STRING | Business Unit | Filtro (ME, ML) |
| `PROCESS_PROBLEMATIC_REPORTING` | STRING | Reporting problemático | **Base AGRUP_COMMERCE** |
| `PROCESS_GROUP_UPDATE_REPORTING` | STRING | Group update reporting | Dimensión |
| `QUEUE_ID` | INT64 | ID de la queue | Filtro/exclusión |
| `ENVIRONMENT` | STRING | Ambiente logístico | **Dimensión análisis** |
| `CDU` | STRING | Caso de Uso | **Dimensión análisis** |
| `REASON_DETAIL_GROUP_REPORTING` | STRING | Motivo detallado | **Dimensión análisis** |
| `CLA_REASON_DETAIL` | STRING | Detalle del motivo | Análisis detallado |
| `CI_REASON_ID` | INT64 | ID de CI reason | Filtro/exclusión |
| `FLAG_EXCLUDE_NUMERATOR_CR` | INT64 | Excluir de CR (0/1) | **Filtro crítico** |
| `FLAG_EXCLUDE_NUMERATOR_HR` | INT64 | Excluir de HR (0/1) | Filtro HR |
| `FLAG_AUTO` | INT64 | Automático (0/1) | Segmentación |
| `ORIGIN_TABLE` | STRING | Tabla de origen | Clasificación incoming |
| `SOURCE_ID` | STRING | ID del source | Join con órdenes |
| `VERTICAL` | STRING | Vertical de negocio | ⚠️ NULL actualmente |
| `DOM_DOMAIN_AGG1` | STRING | Dominio agregado | ⚠️ NULL actualmente |

#### Valores Clave

##### ORIGIN_TABLE
- `BT_CX_INCOMING_CR`: Incoming sin conflicto
- `BT_CX_CLAIMS_CR`: Claims/conflictos

##### PROCESS_GROUP_ECOMMERCE (User Types)
- `Comprador`: Usuario comprador (~70%)
- `Vendedor`: Usuario vendedor (~25%)
- `Cuenta`: Gestión de cuenta (~5%)
- `Driver` / `Drivers`: Drivers de envíos

##### PROCESS_BU_CR_REPORTING (Business Units)
- `ME`: Mercado Envíos
- `ML`: Mercado Libre
- Otros: Excluidos del análisis

##### ENVIRONMENT (Ambientes Logísticos)
- `DS`: Drop Shipping
- `FBM`: Fulfillment by ML
- `FLEX`: Flex Logistics
- `XD`: Cross Docking
- `MP_ON`: Mercado Pago Online
- `MP_OFF`: Mercado Pago Offline

##### SIT_SITE_ID (Sites)
- `MLA`: Argentina
- `MLB`: Brasil (⚠️ requiere sampling)
- `MLC`: Chile
- `MCO`: Colombia
- `MLM`: México
- `MLU`: Uruguay
- `MPE`: Perú
- `MLV`: Venezuela (❌ EXCLUIDO)

#### Exclusiones Críticas

##### Queues Excluidas
```sql
QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2131, 2294, 2295)
```
**Razón:** Queues de testing, desarrollo o fuera de scope.

##### Processes Excluidos
```sql
PROCESS_ID NOT IN (1312)
```
**Razón:** Procesos administrativos internos.

##### CI Reasons Excluidos
```sql
COALESCE(CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
```
**Razón:** Razones no relevantes para Contact Rate.

##### Flag CR
```sql
FLAG_EXCLUDE_NUMERATOR_CR = 0
```
**Razón:** Flag específico para excluir casos del cálculo de CR.

#### AGRUP_COMMERCE Logic

La lógica de asignación a Commerce Groups se basa principalmente en `PROCESS_PROBLEMATIC_REPORTING`:

```sql
CASE
    -- POST-COMPRA
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' THEN 'PNR'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%' THEN 'PDD'
    
    -- SHIPPING - ME DISTRIBUCIÓN (Comprador)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'ME Distribución'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
         AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME Distribución'
    
    -- SHIPPING - ME PREDESPACHO (Vendedor)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'ME PreDespacho'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
         AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME PreDespacho'
    
    -- SHIPPING - DRIVERS
    WHEN PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
    
    -- SHIPPING - FBM
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
    
    -- MARKETPLACE
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PreVenta%' THEN 'Pre Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PostVenta%' THEN 'Post Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Redes%' THEN 'Generales Compra'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' THEN 'Moderaciones'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%' THEN 'Generales Compra'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Compra%' THEN 'Generales Compra'
    
    -- PAGOS
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' THEN 'Pagos'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP Payer%' THEN 'MP On'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' THEN 'MP On'
    
    -- CUENTA
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Seguridad 360%' THEN 'Cuenta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Experiencia Impositiva%' THEN 'Experiencia Impositiva'
    
    -- DEFAULT
    ELSE 'Generales Compra'
END AS AGRUP_COMMERCE
```

#### Ejemplo de Query Base

```sql
SELECT 
    CAS_CASE_ID,
    CUS_CUST_ID,
    FORMAT_DATETIME('%Y-%m', CONTACT_DATE_ID) AS MES,
    SIT_SITE_ID,
    CAST(CONTACT_DATE_ID AS DATE) AS CONTACT_DATE_ID,
    PROCESS_NAME,
    ENVIRONMENT,
    REASON_DETAIL_GROUP_REPORTING,
    CDU,
    PROCESS_GROUP_ECOMMERCE,
    
    -- Calcular AGRUP_COMMERCE
    CASE
        WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' THEN 'PDD'
        WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' THEN 'PNR'
        -- ... resto de lógica
        ELSE 'Generales Compra'
    END AS AGRUP_COMMERCE,
    
    -- Clasificar incoming
    CASE WHEN ORIGIN_TABLE = 'BT_CX_INCOMING_CR' THEN 1.0 ELSE 0.0 END AS INCOMING_NO_CONFLICT,
    CASE WHEN ORIGIN_TABLE = 'BT_CX_CLAIMS_CR' THEN 1.0 ELSE 0.0 END AS INCOMING_CONFLICT,
    
    1.0 AS CANT_CASES
    
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`

WHERE
    CAST(CONTACT_DATE_ID AS DATE) BETWEEN '2026-01-01' AND '2026-01-31'
    AND SIT_SITE_ID IN ('MLA')
    AND SIT_SITE_ID NOT IN ('MLV')
    AND PROCESS_ID NOT IN (1312)
    AND PROCESS_BU_CR_REPORTING IN ('ME', 'ML')
    AND QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
    AND PROCESS_GROUP_ECOMMERCE IN ('Comprador', 'Vendedor', 'Cuenta', 'Driver', 'Drivers')
    AND COALESCE(CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
    AND FLAG_EXCLUDE_NUMERATOR_CR = 0
```

---

### BT_ORD_ORDERS

**Tabla de órdenes** (join opcional para enriquecer datos).

**Ubicación:** `meli-bi-data.WHOWNER.BT_ORD_ORDERS`

**Descripción:** Información de órdenes cerradas.

#### Campos Relevantes

| Campo | Tipo | Descripción | Uso |
|-------|------|-------------|-----|
| `ORD_ORDER_ID` | INT64 | ID de la orden | Join con SOURCE_ID |
| `SIT_SITE_ID` | STRING | Site de la orden | Join key |
| `ORD_CLOSED_DT` | DATETIME | Fecha de cierre | Correlación temporal |
| `ORD_STATUS` | STRING | Estado de la orden | Filtro |

#### Join Logic

```sql
LEFT JOIN `meli-bi-data.WHOWNER.BT_ORD_ORDERS` O 
    ON C.SOURCE_ID = O.ORD_ORDER_ID 
    AND C.SIT_SITE_ID = O.SIT_SITE_ID
```

**Propósito:** Correlacionar contactos con eventos comerciales (fecha de cierre de orden).

---

### BT_CX_POST_PURCHASE

**Estado:** ⚠️ **NO DISPONIBLE** (removida de v2.6)

**Razón:** Tabla no encontrada o sin acceso.

**Impact:** Campos VERTICAL y DOM_DOMAIN_AGG1 actualmente NULL.

**Solución pendiente:** Identificar tabla alternativa para Vertical y Domain.

---

## Campos Calculados

### MES
```sql
FORMAT_DATETIME('%Y-%m', CONTACT_DATE_ID) AS MES
```
**Formato:** YYYY-MM (Ejemplo: 2026-01)  
**Uso:** Agregación mensual.

### INCOMING_NO_CONFLICT
```sql
CASE WHEN ORIGIN_TABLE = 'BT_CX_INCOMING_CR' THEN 1.0 ELSE 0.0 END
```
**Uso:** Contar casos incoming sin conflicto.

### INCOMING_CONFLICT
```sql
CASE WHEN ORIGIN_TABLE = 'BT_CX_CLAIMS_CR' THEN 1.0 ELSE 0.0 END
```
**Uso:** Contar casos de claims/conflictos.

### CANT_CASES
```sql
1.0 AS CANT_CASES
```
**Uso:** Contador universal para agregaciones (SUM).

### AGRUP_COMMERCE
Calculado mediante lógica CASE WHEN (ver arriba).

---

## Agregaciones Comunes

### Total Incoming Cases
```sql
SUM(CANT_CASES) AS INCOMING_CASES
```

### Por Dimensión (ejemplo: PROCESS_NAME)
```sql
SELECT 
    PROCESS_NAME,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES,
    COUNT(DISTINCT CUS_CUST_ID) AS UNIQUE_CUSTOMERS
FROM BASE_CONTACTS
GROUP BY PROCESS_NAME
HAVING SUM(CANT_CASES) >= 100  -- Threshold
ORDER BY INCOMING_CASES DESC
```

### Por Site y Mes
```sql
SELECT 
    SIT_SITE_ID,
    MES,
    AGRUP_COMMERCE,
    SUM(CANT_CASES) AS INCOMING_CASES
FROM BASE_CONTACTS
GROUP BY SIT_SITE_ID, MES, AGRUP_COMMERCE
ORDER BY SIT_SITE_ID, MES, INCOMING_CASES DESC
```

### Por Commerce Group
```sql
SELECT 
    AGRUP_COMMERCE,
    SUM(CANT_CASES) AS INCOMING_CASES,
    COUNT(DISTINCT PROCESS_NAME) AS PROCESS_COUNT
FROM BASE_CONTACTS
GROUP BY AGRUP_COMMERCE
HAVING SUM(CANT_CASES) >= 100
ORDER BY INCOMING_CASES DESC
```

---

## Performance y Optimización

### Particiones
`BT_CX_CONTACTS` está particionada por `CONTACT_DATE_ID`.

**Best Practice:** Siempre incluir filtro de fecha:
```sql
WHERE CAST(CONTACT_DATE_ID AS DATE) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
```

### Clustering
La tabla puede estar clustered por `SIT_SITE_ID`.

**Best Practice:** Filtrar por site temprano:
```sql
WHERE SIT_SITE_ID IN ('MLA', 'MLB', 'MLC')
```

### Sampling (MLB)

Para MLB (Brasil), volumen extremadamente alto requiere sampling:

```sql
-- Estimar filas
WITH ESTIMATE AS (
    SELECT 
        COUNT(DISTINCT AGRUP_COMMERCE) AS num_agrup,
        COUNT(DISTINCT MES) AS num_months
    FROM BASE_CONTACTS
    WHERE SIT_SITE_ID = 'MLB'
)
SELECT 
    num_agrup * num_months * 50000 AS estimated_rows
FROM ESTIMATE;

-- Si estimated_rows > 150,000, aplicar LIMIT
SELECT *
FROM BASE_CONTACTS
WHERE SIT_SITE_ID = 'MLB'
ORDER BY RAND()
LIMIT 150000;
```

Ver detalles en `/sql/sampling-strategy.sql`.

---

## Data Quality Checks

### Validar FLAG_EXCLUDE_NUMERATOR_CR
```sql
-- Deben estar solo casos con flag = 0
SELECT FLAG_EXCLUDE_NUMERATOR_CR, COUNT(*) 
FROM BT_CX_CONTACTS
GROUP BY FLAG_EXCLUDE_NUMERATOR_CR;
```

### Validar PROCESS_BU_CR_REPORTING
```sql
-- Deben estar solo ME y ML
SELECT PROCESS_BU_CR_REPORTING, COUNT(*) 
FROM BT_CX_CONTACTS
WHERE FLAG_EXCLUDE_NUMERATOR_CR = 0
GROUP BY PROCESS_BU_CR_REPORTING;
```

### Validar Queues Excluidas
```sql
-- No deben aparecer queues excluidas
SELECT QUEUE_ID, COUNT(*) 
FROM BT_CX_CONTACTS
WHERE QUEUE_ID IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
GROUP BY QUEUE_ID;
```

### Validar Sites
```sql
-- MLV no debe aparecer
SELECT SIT_SITE_ID, COUNT(*) 
FROM BT_CX_CONTACTS
WHERE SIT_SITE_ID = 'MLV';
```

---

## Tipos de Datos

### Optimización en Pandas

```python
# String → Category (si < 50% unique)
df['PROCESS_NAME'] = df['PROCESS_NAME'].astype('category')
df['SIT_SITE_ID'] = df['SIT_SITE_ID'].astype('category')
df['AGRUP_COMMERCE'] = df['AGRUP_COMMERCE'].astype('category')

# Numeric downcast
df['CANT_CASES'] = pd.to_numeric(df['CANT_CASES'], downcast='float')
df['INCOMING_NO_CONFLICT'] = pd.to_numeric(df['INCOMING_NO_CONFLICT'], downcast='float')
df['INCOMING_CONFLICT'] = pd.to_numeric(df['INCOMING_CONFLICT'], downcast='float')

# Datetime
df['CONTACT_DATE_ID'] = pd.to_datetime(df['CONTACT_DATE_ID'])
```

Ver `/utils/memory-optimization.py` para detalles.

---

## Limitaciones Conocidas

### VERTICAL y DOMAIN
- **Estado:** NULL actualmente
- **Razón:** Tabla `BT_CX_POST_PURCHASE` no disponible
- **Impact:** Dimensiones 7 y 8 no funcionales
- **Workaround:** Usar otras 6 dimensiones

### Campos Opcionales
Algunos campos pueden ser NULL:
- `ENVIRONMENT` (si no aplica)
- `CDU` (si no está clasificado)
- `CLA_REASON_DETAIL` (si no hay detalle)

**Best Practice:** Usar `COALESCE()` al filtrar:
```sql
WHERE COALESCE(CI_REASON_ID, 0) NOT IN (...)
```

### Historicidad
Datos disponibles típicamente de **últimos 24 meses**.

Para análisis históricos más antiguos, validar disponibilidad.

---

## Referencias

- **Query principal:** `/sql/base-query.sql`
- **Agregaciones:** `/sql/aggregations.sql`
- **Sampling MLB:** `/sql/sampling-strategy.sql`
- **Contexto negocio:** `/docs/business-context.md`
- **Constantes:** `/config/business-constants.py`

---

**Última actualización:** Enero 2026  
**Versión:** 2.5 (Commerce)  
**Source:** V37.ipynb
