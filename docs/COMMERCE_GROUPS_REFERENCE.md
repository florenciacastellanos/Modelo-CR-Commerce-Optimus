# 🏷️ Commerce Groups - Guía de Referencia Rápida

> **Documento crítico**: Cómo interpretar y filtrar correctamente por Commerce Groups

**Versión:** 3.5  
**Última actualización:** Enero 26, 2026  
**Status:** ✅ VALIDADO - Método oficial

---

## 🚨 REGLA DE ORO (v3.5)

> **SIEMPRE usar CASE statement para clasificar Commerce Groups**  
> **NO usar filtros simples de texto (pierde casos ~2%)**

**Cambio crítico v3.5:**
- ✅ Incluye "Conflict Others" → PDD (antes se perdía)
- ✅ Incluye "Conflict Stale" → PNR (antes se perdía)
- ✅ Separa PCF Comprador vs PCF Vendedor correctamente
- ✅ 100% alineado con queries de producción

---

## ❓ ¿Qué es un Commerce Group?

Un **Commerce Group** (también llamado `AGRUP_COMMERCE`) es una **categoría de negocio** que agrupa múltiples `PROCESS_NAME` según su naturaleza problemática.

### Ejemplo Real: Commerce Group "PDD"

**Definición:** Producto Dañado/Defectuoso

**Procesos incluidos (ejemplos):**
- ✅ Arrepentimiento - XD
- ✅ Defectuoso - XD
- ✅ Dañado - DS
- ✅ Roto - FBM
- ✅ Diferente al Publicado - Flex
- ✅ Incompleto - CBT
- ✅ Caja Vacía - 1P&PL
- ✅ Producto no Corresponde - Super
- ✅ **Conflict Others** ← CRÍTICO: Caso especial (v3.5)

**Criterio de inclusión (v3.5):**
```sql
CASE 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'  -- ← Agregado v3.5
    ...
END AS AGRUP_COMMERCE_PROPIO
```

**⚠️ IMPORTANTE:** "Conflict Others" NO contiene "PDD" pero SÍ pertenece al Commerce Group PDD. Un filtro simple `LIKE '%PDD%'` lo pierde.

---

## ❌ ERROR COMÚN

### Lo que NO se debe hacer (DEPRECADO):

```sql
-- ❌ INCORRECTO - Filtro simple (método antiguo, deprecado en v3.5)
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
```

**Problema:**
- ❌ Excluye "Conflict Others" (debería ser PDD) → **Pierde ~2% de casos**
- ❌ No clasifica "Conflict Stale" como PNR
- ❌ No separa PCF Comprador vs PCF Vendedor
- ❌ NO alineado con queries de producción

**Impacto medido (Nov-Dic 2025 Cross Site):**
- ❌ **-19,360 casos en Noviembre** (-2.26%)
- ❌ **-18,936 casos en Diciembre** (-1.98%)
- ❌ **-55 procesos** no identificados

---

## ✅ MÉTODO CORRECTO (v3.5)

### SIEMPRE usar CASE Statement

```sql
-- ✅ CORRECTO - Clasificación con CASE (v3.5+)
-- Paso 1: Clasificar usando CASE
WITH CLASIFICACION AS (
    SELECT
        C.*,
        CASE 
            -- POST-COMPRA
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'  -- ← Caso especial
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'  
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'  -- ← Caso especial
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'PCF Comprador'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'PCF Vendedor'
            
            -- SHIPPING
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
                 AND C.PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'ME Distribución'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
                 AND C.PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'ME PreDespacho'
            WHEN C.PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
            
            -- Otros grupos...
            ELSE 'OTRO' 
        END AS AGRUP_COMMERCE_PROPIO
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE 1=1
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
)
-- Paso 2: Filtrar por el Commerce Group deseado
SELECT *
FROM CLASIFICACION
WHERE AGRUP_COMMERCE_PROPIO = 'PDD'
```

**Ventajas:**
- ✅ Captura "Conflict Others" → PDD (+2% casos)
- ✅ Captura "Conflict Stale" → PNR
- ✅ Separa PCF Comprador vs PCF Vendedor
- ✅ 100% alineado con producción
- ✅ Método validado (Enero 2026)
        
        -- (resto de lógica...)
        ELSE 'Generales Compra'
    END AS AGRUP_COMMERCE
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE AGRUP_COMMERCE = 'PDD'  -- Filtrar por Commerce Group
```

**Ventaja:** Garantiza consistencia con la lógica oficial de negocio.

---

### Opción 2: Usar datos con AGRUP_COMMERCE ya calculado

```python
# ✅ CORRECTO - Trabajar con campo AGRUP_COMMERCE
df_pdd = df[df['AGRUP_COMMERCE'] == 'PDD']
```

**Requisito:** El dataset debe incluir la columna `AGRUP_COMMERCE` ya calculada por BigQuery.

---

### Opción 3: Usar la query base del repositorio

```python
# Usar sql/base-query.sql como template
# Ya incluye la lógica completa de AGRUP_COMMERCE
query = open('sql/base-query.sql').read()
df = client.query(query).to_dataframe()
df_pdd = df[df['AGRUP_COMMERCE'] == 'PDD']
```

**Ventaja:** Reutiliza la lógica validada del repositorio.

---

## 🚛 CASO ESPECIAL: Shipping (Criterio Compuesto)

### ⚠️ Diferencia Crítica

A diferencia de **Post-Compra, Marketplace, Pagos y Cuenta** que solo usan `PROCESS_PROBLEMATIC_REPORTING`, los Commerce Groups de **Shipping** requieren **criterios compuestos**:

| Commerce Group | Criterio | Complejidad |
|----------------|----------|-------------|
| **PDD, PNR** | Solo `PROCESS_PROBLEMATIC_REPORTING` | ⚡ Simple |
| **Marketplace** | Solo `PROCESS_PROBLEMATIC_REPORTING` | ⚡ Simple |
| **Pagos** | Solo `PROCESS_PROBLEMATIC_REPORTING` | ⚡ Simple |
| **Cuenta** | Solo `PROCESS_PROBLEMATIC_REPORTING` | ⚡ Simple |
| **Shipping** | `PROCESS_PROBLEMATIC_REPORTING` + `PROCESS_GROUP_ECOMMERCE` | 🔥 Compuesta |

---

### 📦 Criterios de Shipping

#### ME Distribución (Comprador)

```sql
WHERE (
    -- Criterio 1: Keyword + User Type
    (PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
     AND PROCESS_GROUP_ECOMMERCE = 'Comprador')
    
    OR
    
    -- Criterio 2: Post Compra Comprador + BU
    (PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
     AND PROCESS_BU_CR_REPORTING = 'ME')
)
```

**Campos requeridos:**
- ✅ `PROCESS_PROBLEMATIC_REPORTING`
- ✅ `PROCESS_GROUP_ECOMMERCE` (debe ser 'Comprador')
- ✅ `PROCESS_BU_CR_REPORTING` (alternativo)

---

#### ME PreDespacho (Vendedor)

```sql
WHERE (
    -- Criterio 1: Keyword + User Type
    (PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
     AND PROCESS_GROUP_ECOMMERCE = 'Vendedor')
    
    OR
    
    -- Criterio 2: Post Compra Vendedor + BU
    (PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
     AND PROCESS_BU_CR_REPORTING = 'ME')
)
```

**Campos requeridos:**
- ✅ `PROCESS_PROBLEMATIC_REPORTING`
- ✅ `PROCESS_GROUP_ECOMMERCE` (debe ser 'Vendedor')
- ✅ `PROCESS_BU_CR_REPORTING` (alternativo)

---

#### ME Drivers

```sql
WHERE PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers')
```

**Campos requeridos:**
- ✅ `PROCESS_GROUP_ECOMMERCE` (debe ser 'Driver' o 'Drivers')

---

#### FBM Sellers

```sql
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%'
```

**Campos requeridos:**
- ✅ `PROCESS_PROBLEMATIC_REPORTING`

---

### 🎯 Ejemplo Crítico: Mismo PROCESS_NAME, Diferentes Commerce Groups

```
PROCESS_NAME: "Reclamo Mercado Envíos - Demora en Entrega"
PROCESS_PROBLEMATIC_REPORTING: "Mercado Envíos"

Caso A:
└─ PROCESS_GROUP_ECOMMERCE = 'Comprador'
   → Commerce Group: ME Distribución ✅

Caso B:
└─ PROCESS_GROUP_ECOMMERCE = 'Vendedor'
   → Commerce Group: ME PreDespacho ✅
```

**⚠️ Por eso NO puedes filtrar solo por `PROCESS_NAME` o solo por `PROCESS_PROBLEMATIC_REPORTING` para Shipping.**

---

### ❌ Error Común con Shipping

```python
# ❌ INCORRECTO - Solo por keyword
df_me = df[df['PROCESS_PROBLEMATIC_REPORTING'].str.contains('Mercado Envíos')]
# Problema: Mezcla Comprador y Vendedor (ME Distribución + ME PreDespacho)
```

### ✅ Forma Correcta con Shipping

```python
# ✅ CORRECTO - Usar AGRUP_COMMERCE ya calculado
df_me_distribucion = df[df['AGRUP_COMMERCE'] == 'ME Distribución']
df_me_predespacho = df[df['AGRUP_COMMERCE'] == 'ME PreDespacho']
```

O en BigQuery:

```sql
-- ✅ CORRECTO - Aplicar criterio compuesto
SELECT *
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%'
  AND PROCESS_GROUP_ECOMMERCE = 'Comprador'  -- Solo ME Distribución
```

---

## 📋 Los 15 Commerce Groups

### Post-Compra (2)
1. **PDD** - Producto Dañado/Defectuoso
2. **PNR** - Producto No Recibido

### Shipping (4)
3. **ME Distribución** - Mercado Envíos (Comprador)
4. **ME PreDespacho** - Mercado Envíos (Vendedor)
5. **FBM Sellers** - Fulfillment by Mercado Libre
6. **ME Drivers** - Drivers de Mercado Envíos

### Marketplace (6)
7. **Pre Venta** - Consultas pre-venta
8. **Post Venta** - Soporte post-venta
9. **Generales Compra** - Consultas generales
10. **Moderaciones** - Moderaciones y Prustomer
11. **Full Sellers** - Full Sellers
12. **Pagos** - Pagos y transacciones

### Pagos (1)
13. **MP On** - Mercado Pago Online

### Cuenta (2)
14. **Cuenta** - Gestión de cuenta
15. **Experiencia Impositiva** - Experiencia Impositiva

**Fuente completa:** `docs/commerce-structure.md`

---

## 🎯 Casos de Uso Comunes

### Caso 1: "Dame el incoming de PDD"

**Interpretación correcta:**
> Traer TODOS los casos que pertenecen al Commerce Group PDD, según su `PROCESS_PROBLEMATIC_REPORTING`

**Query correcta:**
```sql
SELECT 
    SUM(CANT_CASES) AS INCOMING_PDD
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE (
    PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
    OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'
)
```

---

### Caso 2: "Analiza la variación de PDD por PROCESS_NAME"

**Interpretación correcta:**
> Traer TODOS los procesos del Commerce Group PDD, y luego agrupar por `PROCESS_NAME` para ver el detalle

**Query correcta:**
```sql
SELECT 
    PROCESS_NAME,
    PERIOD_MONTH,
    SUM(CANT_CASES) AS INCOMING
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE (
    PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
    OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'
)
GROUP BY PROCESS_NAME, PERIOD_MONTH
```

**Resultado esperado:**
| PROCESS_NAME | PERIOD_MONTH | INCOMING |
|--------------|--------------|----------|
| Arrepentimiento - XD | 2025-11 | 9,083 |
| Defectuoso - XD | 2025-11 | 12,456 |
| Dañado - DS | 2025-11 | 8,234 |
| ... | ... | ... |

---

### Caso 3: "Compara PDD vs PNR"

**Interpretación correcta:**
> Comparar los dos Commerce Groups completos, cada uno con su criterio de clasificación

**Query correcta:**
```sql
SELECT 
    CASE
        WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' 
             OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' 
             OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%' THEN 'PDD'
        WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' 
             OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
    END AS COMMERCE_GROUP,
    PERIOD_MONTH,
    SUM(CANT_CASES) AS INCOMING
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE (
    PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale'
)
GROUP BY COMMERCE_GROUP, PERIOD_MONTH
```

---

### Caso 4: "Analiza ME Distribución en MLA Nov-Dic 2025" (SHIPPING)

**Interpretación correcta:**
> Traer TODOS los casos del Commerce Group ME Distribución (requiere criterio compuesto: keyword + User Type)

**Query correcta:**
```sql
SELECT 
    PROCESS_NAME,
    PERIOD_MONTH,
    SUM(CANT_CASES) AS INCOMING
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE (
    -- Criterio 1: Keyword + User Type = Comprador
    (PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
     AND PROCESS_GROUP_ECOMMERCE = 'Comprador')
    OR
    -- Criterio 2: Post Compra Comprador + BU
    (PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
     AND PROCESS_BU_CR_REPORTING = 'ME')
)
AND SIT_SITE_ID = 'MLA'
AND PERIOD_MONTH IN ('2025-11', '2025-12')
GROUP BY PROCESS_NAME, PERIOD_MONTH
```

**Resultado esperado:**
| PROCESS_NAME | PERIOD_MONTH | INCOMING | User Type |
|--------------|--------------|----------|-----------|
| Demora en Entrega - XD | 2025-11 | 15,234 | Comprador ✅ |
| Problema con Tracking - DS | 2025-11 | 8,567 | Comprador ✅ |
| Reclamo Envío - Flex | 2025-11 | 5,234 | Comprador ✅ |

**NO incluiría:**
| PROCESS_NAME | User Type | Commerce Group |
|--------------|-----------|----------------|
| Demora en Despacho - FBM | Vendedor | ME PreDespacho (no ME Distribución) |
| Problema con Sellers | Vendedor | FBM Sellers |

**⚠️ Nota crítica:** Un proceso con `PROCESS_PROBLEMATIC_REPORTING = 'Mercado Envíos'` puede ir a **ME Distribución** o **ME PreDespacho** según el `PROCESS_GROUP_ECOMMERCE`.

---

### Caso 5: "Compara ME Distribución vs ME PreDespacho" (SHIPPING)

**Interpretación correcta:**
> Comparar ambos Commerce Groups de Shipping diferenciados por User Type

**Query correcta:**
```sql
SELECT 
    CASE
        -- ME Distribución (Comprador)
        WHEN (PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
              AND PROCESS_GROUP_ECOMMERCE = 'Comprador')
             OR (PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
              AND PROCESS_BU_CR_REPORTING = 'ME')
        THEN 'ME Distribución'
        
        -- ME PreDespacho (Vendedor)
        WHEN (PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
              AND PROCESS_GROUP_ECOMMERCE = 'Vendedor')
             OR (PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
              AND PROCESS_BU_CR_REPORTING = 'ME')
        THEN 'ME PreDespacho'
    END AS COMMERCE_GROUP,
    PERIOD_MONTH,
    SUM(CANT_CASES) AS INCOMING
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE (
    PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%'
)
AND SIT_SITE_ID = 'MLA'
AND PERIOD_MONTH IN ('2025-11', '2025-12')
GROUP BY COMMERCE_GROUP, PERIOD_MONTH
HAVING COMMERCE_GROUP IS NOT NULL
```

**Resultado esperado:**
| COMMERCE_GROUP | PERIOD_MONTH | INCOMING | User Type Principal |
|----------------|--------------|----------|---------------------|
| ME Distribución | 2025-11 | 45,678 | Comprador |
| ME Distribución | 2025-12 | 48,234 | Comprador |
| ME PreDespacho | 2025-11 | 23,456 | Vendedor |
| ME PreDespacho | 2025-12 | 25,789 | Vendedor |

---

## 🔍 Validación de Resultados

### ¿Cómo saber si lo estás haciendo bien?

1. **Volumen esperado:**
   - PDD en MLA Nov 2025: ~100,000 casos
   - Si obtienes ~70,000 casos, probablemente estás filtrando mal

2. **Inclusión de "Arrepentimiento":**
   - Si "Arrepentimiento" NO está en tu dataset de PDD, estás filtrando mal
   - "Arrepentimiento" representa ~25% del volumen de PDD

3. **Cross-check con producción:**
   - Compara tus resultados con Jupyter Lab o BigQuery Console
   - Los números deben coincidir 100%

4. **Validación específica de Shipping:**
   - ME Distribución debe tener **solo** casos de `PROCESS_GROUP_ECOMMERCE = 'Comprador'`
   - ME PreDespacho debe tener **solo** casos de `PROCESS_GROUP_ECOMMERCE = 'Vendedor'`
   - Si ves mezclados Comprador y Vendedor en un mismo Commerce Group, estás filtrando mal
   - ME Distribución + ME PreDespacho NO deben sumar más que el total de "Mercado Envíos"

5. **Test rápido para Shipping:**
   ```sql
   -- Verificar que no hay mezcla de User Types
   SELECT 
       'ME Distribución' AS COMMERCE_GROUP,
       PROCESS_GROUP_ECOMMERCE,
       COUNT(*) AS CASOS
   FROM tu_dataset
   WHERE AGRUP_COMMERCE = 'ME Distribución'
   GROUP BY PROCESS_GROUP_ECOMMERCE
   -- Debe retornar SOLO 'Comprador'
   ```

---

## 📚 Referencias

| Tema | Archivo |
|------|---------|
| Lógica completa de clasificación | `docs/commerce-structure.md` |
| Keywords de cada Commerce Group | `docs/table-definitions.md` |
| Query base con AGRUP_COMMERCE | `sql/base-query.sql` |
| Configuración de Commerce Groups | `config/commerce-groups.py` |
| Reglas obligatorias | `.cursorrules` |
| Best practices | `docs/GUIDELINES.md` |

---

## ✅ Checklist de Verificación

### General (Todos los Commerce Groups)

- [ ] ¿Estoy usando `AGRUP_COMMERCE` o la lógica de `PROCESS_PROBLEMATIC_REPORTING`?
- [ ] ¿NO estoy filtrando por palabras en `PROCESS_NAME`?
- [ ] ¿Mi query incluye TODOS los criterios de clasificación del Commerce Group?
- [ ] ¿Los volúmenes son consistentes con producción?

### Específico para Post-Compra

- [ ] ¿"Arrepentimiento" está incluido en mi análisis de PDD?
- [ ] ¿El volumen de PDD es ~100,000 casos en MLA (Nov 2025)?

### Específico para Shipping (CRÍTICO)

- [ ] ¿Estoy usando `PROCESS_GROUP_ECOMMERCE` además de `PROCESS_PROBLEMATIC_REPORTING`?
- [ ] Para ME Distribución: ¿Solo incluyo `PROCESS_GROUP_ECOMMERCE = 'Comprador'`?
- [ ] Para ME PreDespacho: ¿Solo incluyo `PROCESS_GROUP_ECOMMERCE = 'Vendedor'`?
- [ ] ¿Verifiqué que NO hay mezcla de User Types en un mismo Commerce Group?
- [ ] ¿La suma de ME Distribución + ME PreDespacho no excede el total de "Mercado Envíos"?

---

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Status:** ✅ VALIDADO  
**Última actualización:** Post-error de exclusión de Arrepentimiento
