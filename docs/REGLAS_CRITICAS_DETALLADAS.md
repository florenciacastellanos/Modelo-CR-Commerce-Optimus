# 🚨 Reglas Críticas - Documentación Detallada

**Versión:** 1.0
**Fecha:** 4 Febrero 2026

Este documento contiene la explicación completa de las **9 Reglas Críticas** que invalidan un análisis de CR si no se cumplen.

---

## ❌ ERROR 1: Fórmula de CR incorrecta

### Única fórmula válida:
```
CR = (Incoming Cases / Driver) × 100
```

### Especificaciones:
- **Resultado:** Puntos porcentuales (pp)
- **Multiplicador:** SIEMPRE 100 (no 1, ni 1000)
- **Precisión:** Mínimo 2 decimales (ej: 3.45 pp)

### Ejemplos correctos:

**Ejemplo 1:**
```
Incoming = 1,500 casos
Driver = 50,000 órdenes
CR = (1,500 / 50,000) × 100 = 3.00 pp ✅
```

**Ejemplo 2:**
```
Incoming = 8,234 casos
Driver = 125,000 órdenes
CR = (8,234 / 125,000) × 100 = 6.59 pp ✅
```

### ❌ Errores comunes:

**Error A: Sin multiplicar por 100**
```
CR = 1,500 / 50,000 = 0.03 ❌
```
**Problema:** El resultado es una proporción decimal, no pp.

**Error B: Multiplicar por 1000**
```
CR = (1,500 / 50,000) × 1000 = 30.00 ❌
```
**Problema:** El resultado está inflado 10 veces.

**Error C: Usar porcentaje del driver**
```
CR = (Incoming / Total_Incoming) × 100 ❌
```
**Problema:** No está calculando contactabilidad sobre driver.

### Validación automática:

```python
def validar_cr(cr_value):
    """Valida que el CR esté en rango razonable."""
    if cr_value < 0:
        return "ERROR: CR negativo (revisar signos)"
    if cr_value > 100:
        return "ERROR: CR > 100 pp (revisar fórmula)"
    if cr_value < 0.01:
        return "WARNING: CR muy bajo (¿falta ×100?)"
    return "OK"
```

### Referencias:
- Fórmula oficial: `docs/business-context.md`
- Cálculo en código: `calculations/cr_calculator.py`

---

## ❌ ERROR 2: Reportar variaciones solo como porcentaje

### Regla obligatoria:
**SIEMPRE reportar variaciones de CR en puntos porcentuales (pp) + porcentaje relativo**

### Formato correcto:

**Para CR:**
```
CR empeoró +0.02 pp (↑33%)
```
- `+0.02 pp`: Variación absoluta (diferencia de CR)
- `↑33%`: Variación relativa ((0.02 / 0.06) × 100)

**Para Incoming:**
```
+150 casos (↑25%)
```
- `+150 casos`: Variación absoluta
- `↑25%`: Variación relativa

### ❌ Incorrecto:
```
"CR empeoró +33%"
```
**Problema:** No queda claro si subió 0.33 pp o 33 pp.

### ✅ Correcto:
```
"CR empeoró +0.33 pp (↑33%)"
```

### Ejemplo completo:

**Caso:**
- CR Nov: 0.06 pp
- CR Dic: 0.08 pp

**Reporte correcto:**
```
El CR empeoró +0.02 pp (↑33%) pasando de 0.06 pp en noviembre a 0.08 pp en diciembre.
```

**Desglose:**
- Variación absoluta: 0.08 - 0.06 = +0.02 pp ✅
- Variación relativa: (0.02 / 0.06) × 100 = 33% ✅

### Validación en código:

```python
def formatear_variacion_cr(cr_p1, cr_p2):
    """Formatea variación de CR correctamente."""
    var_abs = cr_p2 - cr_p1
    var_rel = (var_abs / cr_p1 * 100) if cr_p1 > 0 else 0
    signo = "+" if var_abs > 0 else ""
    return f"{signo}{var_abs:.4f} pp ({var_rel:+.1f}%)"

# Ejemplo:
print(formatear_variacion_cr(0.06, 0.08))
# Output: "+0.0200 pp (+33.3%)"
```

---

## ❌ ERROR 3: Clasificación de Commerce Groups con filtro simple

### Regla obligatoria:
**Usar CASE WHEN completo, NO filtros simples con LIKE**

### ✅ CORRECTO:
```sql
CASE 
  WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
  WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD' 
  WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR' 
  WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
  WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
    AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'PCF Comprador'
  WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
    AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'PCF Vendedor'
  ELSE 'OTRO' 
END AS AGRUP_COMMERCE_PROPIO
```

### ❌ INCORRECTO:
```sql
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
```

**Problema:** Pierde ~2% de casos que se clasifican indirectamente (ej: "Conflict Others" = PDD)

### Impacto cuantitativo:

**Ejemplo real:**
- Total casos PDD: 10,000
- Con filtro simple: 9,800 casos (98%)
- Con CASE completo: 10,000 casos (100%)
- **Diferencia:** 200 casos perdidos (2%)

### Mapeo completo por Commerce Group:

```sql
-- PDD
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'
WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'

-- PNR
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'
WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'

-- PCF Comprador
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
  AND C.PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'PCF Comprador'

-- PCF Vendedor
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
  AND C.PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'PCF Vendedor'

-- ME PreDespacho
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PreDespacho%') THEN 'ME PreDespacho'

-- ME Distribución
WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Distribución%') THEN 'ME Distribución'

-- Etc.
```

### Referencias:
- Mapeo completo: `docs/COMMERCE_GROUPS_REFERENCE.md`
- Query template: `sql/base-query.sql`

---

## ❌ ERROR 4: Campo de fecha incorrecto

### Regla obligatoria:
**SIEMPRE usar `CONTACT_DATE_ID` para filtrar períodos**

### ✅ CORRECTO:
```sql
WHERE DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-11-01'
```

### ❌ INCORRECTO:
```sql
WHERE OFC_MONTH_ID = '202511'
```

**Motivo:** `CONTACT_DATE_ID` = fecha real de contacto, 100% match con reportes productivos.

### Diferencia entre campos:

| Campo | Significado | Usar para CR |
|-------|-------------|--------------|
| `CONTACT_DATE_ID` | Fecha real de contacto del usuario | ✅ SÍ |
| `OFC_MONTH_ID` | Mes de cierre del caso (puede diferir) | ❌ NO |
| `CREATION_DATE` | Fecha de creación del caso | ❌ NO |

### Ejemplo de impacto:

**Caso real:**
- Case ID: 123456
- `CONTACT_DATE_ID`: 2025-11-28 (contacto)
- `OFC_MONTH_ID`: 202512 (cerrado en dic)

**Con CONTACT_DATE_ID:** Se cuenta en noviembre ✅
**Con OFC_MONTH_ID:** Se cuenta en diciembre ❌

**Resultado:** Inconsistencia con reportes productivos.

### Query correcta completa:

```sql
SELECT 
  DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS MONTH,
  COUNT(DISTINCT C.CAS_CASE_ID) AS INCOMING
FROM 
  `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE 
  DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) BETWEEN '2025-11-01' AND '2025-12-31'
  AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
GROUP BY 1
ORDER BY 1
```

### Referencias:
- Regla oficial: `docs/DATE_FIELD_RULE.md`
- Query base: `sql/base-query.sql`

---

## ❌ ERROR 5: Drivers incorrectos por categoría

### Regla obligatoria:
**Los drivers NO son iguales para todos los commerce groups**

### ✅ REGLAS POR CATEGORÍA (Comportamiento por defecto):

| Categoría | Driver | Tabla | ¿Filtrar por site? |
|-----------|--------|-------|-------------------|
| **Post-Compra** (PDD, PNR) | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |
| **Shipping** (ME, FBM) | Drivers específicos | `BT_CX_DRIVERS_CR` | ❌ NO (global) ⚠️ |
| **Marketplace** (todos) | Órdenes totales | `BT_ORD_ORDERS` | ✅ **SÍ (por site)** |
| **Pagos** (MP On) | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |
| **Cuenta** (todos) | Órdenes totales | `BT_ORD_ORDERS` | ❌ NO (global) |

### ⚠️ MODO OVERRIDE DISPONIBLE (v6.3.7+):

Para Shipping, el usuario puede explícitamente anular la regla usando `--filter-driver-by-site`:
- **Por defecto (estándar):** Driver GLOBAL (todos los sites) ✅
- **Con flag:** Driver filtrado por site específico (requiere confirmación) ⚠️
- **Indicador visual:** Reporte HTML muestra banner naranja cuando se usa override
- **Trazabilidad:** Footer indica claramente qué modo se usó

### Ejemplos por categoría:

#### Post-Compra (PDD, PNR):
```sql
-- Driver: Órdenes GLOBALES (todos los sites)
SELECT 
  DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) AS MONTH,
  COUNT(DISTINCT ORD.ORD_ORDER_ID) AS DRIVER
FROM 
  `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 
  ORD.ORD_GMV_FLG = TRUE
  AND ORD.ORD_MARKETPLACE_FLG = TRUE
  AND ORD.SIT_SITE_ID NOT IN ('MLV')
  AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
GROUP BY 1
```

#### Marketplace (Reputación, Moderaciones, etc.):
```sql
-- Driver: Órdenes FILTRADAS por site
SELECT 
  DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) AS MONTH,
  COUNT(DISTINCT ORD.ORD_ORDER_ID) AS DRIVER
FROM 
  `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 
  ORD.ORD_GMV_FLG = TRUE
  AND ORD.ORD_MARKETPLACE_FLG = TRUE
  AND ORD.SIT_SITE_ID = 'MLA'  -- ✅ FILTRO POR SITE
  AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
GROUP BY 1
```

#### Shipping (ME PreDespacho, ME Distribución):
```sql
-- Driver: Drivers específicos de BT_CX_DRIVERS_CR
SELECT 
  DATE_TRUNC(DRV.DRIVER_DATE, MONTH) AS MONTH,
  SUM(DRV.DRIVER_VALUE) AS DRIVER
FROM 
  `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` DRV
WHERE 
  DRV.DRIVER_TYPE = 'ME_PREDESPACHO'  -- Específico por commerce group
  -- SIN FILTRO POR SITE (comportamiento por defecto)
GROUP BY 1
```

### Filtros base para `BT_ORD_ORDERS`:

```sql
WHERE 
  ORD.ORD_GMV_FLG = TRUE
  AND ORD.ORD_MARKETPLACE_FLG = TRUE
  AND ORD.SIT_SITE_ID NOT IN ('MLV')  -- Excluir MLV siempre
  AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')  -- Excluir TIPS
```

### Configuración en código:

```python
# config/drivers_mapping.py
def get_driver_config(commerce_group):
    """Retorna configuración de driver según commerce group."""
    
    mapping = {
        'PDD': {
            'source': 'BT_ORD_ORDERS',
            'filter_by_site': False,
            'type': 'orders_global'
        },
        'PNR': {
            'source': 'BT_ORD_ORDERS',
            'filter_by_site': False,
            'type': 'orders_global'
        },
        'ME_PREDESPACHO': {
            'source': 'BT_CX_DRIVERS_CR',
            'filter_by_site': False,  # Por defecto
            'type': 'driver_specific',
            'driver_name': 'ME_PREDESPACHO'
        },
        'MODERACIONES': {
            'source': 'BT_ORD_ORDERS',
            'filter_by_site': True,  # ✅ Filtrar por site
            'type': 'orders_by_site'
        }
    }
    
    return mapping.get(commerce_group, {
        'source': 'BT_ORD_ORDERS',
        'filter_by_site': False,
        'type': 'orders_global'
    })
```

### Referencias completas:
- **Drivers por categoría:** `docs/DRIVERS_BY_CATEGORY.md`
- **Drivers Shipping:** `docs/SHIPPING_DRIVERS.md`
- **Filtros base:** `docs/BASE_FILTERS_ORDERS.md`
- **Configuración código:** `config/drivers_mapping.py`

---

## ❌ ERROR 6: Saltarse el análisis de conversaciones

### Regla obligatoria:
**FASE 3 (conversaciones) es AUTOMÁTICA y OBLIGATORIA**

### ❌ NO preguntar:
```
"¿Querés continuar con el análisis de conversaciones?"
```

### ✅ FLUJO CORRECTO:
```
FASE 0 (confirmar) → FASE 1-5 (sin interrupciones) → Entregar reporte completo
```

### Validación:

**Cada hallazgo en el reporte DEBE tener evidencia cualitativa:**
- ✅ Frecuencia real (X/Y conversaciones)
- ✅ Porcentaje sobre muestra
- ✅ Citas textuales con CASE_IDs
- ✅ Sentimiento (frustración %, satisfacción %)

### Umbral mínimo:

| Conversaciones | Estado | Acción |
|----------------|--------|--------|
| ≥10 por período | ✅ Válido | Análisis concluyente |
| <10 por período | ⚠️ Insuficiente | Marcar como "Muestra insuficiente" |
| 0 | ❌ Sin datos | Reportar "Sin conversaciones disponibles" |

### Referencias:
- **Flujo completo:** `docs/METODOLOGIA_5_FASES.md#fase-3`
- **Template prompt:** `templates/prompt_analisis_conversaciones.md`

---

## ❌ ERROR 7: Reportar hallazgos sin evidencia cualitativa

### ⚠️ REGLA DE ORO:
**SI REPORTÁS UN HALLAZGO → DEBE TENER EVIDENCIA CUALITATIVA**

### Checklist antes de reportar:

| Situación | Acción |
|-----------|--------|
| ✅ Con conversaciones | Incluir: frecuencia + citas + sentimiento |
| ⚠️ Sin conversaciones | Marcar: "⚠️ HIPÓTESIS (pendiente validación)" |
| ❌ Inventado/estimado | **NO REPORTAR** - es inválido |

### Validación paso a paso:

```
1. ¿Tengo conversaciones muestreadas?
   → SÍ: incluir evidencia
   → NO: marcar hipótesis

2. ¿Tengo frecuencia/porcentaje + citas reales?
   → SÍ: incluir
   → NO: no es válido

3. ¿Estoy inventando/asumiendo?
   → SÍ: ❌ NO REPORTAR
   → NO: ✅ proceder
```

### Ejemplo VÁLIDO:

```markdown
**Hallazgo:** Reembolsos procesados pero no reflejados en cuenta bancaria

**Evidencia:**
- Frecuencia: 13/30 conversaciones (43%)
- Casos estimados: 3,768 (sobre 8,786 incoming)
- Sentimiento: 75% frustración, 15% satisfacción

**Citas:**
1. Case 420196359 (2025-12-02): "El usuario realizó una devolución de dos productos, pero solo recibió el reembolso de uno..."
2. Case 425389526 (2025-12-24): "La clienta no ha recibido el reembolso de una tablet que canceló hace dos días..."
```

### Ejemplo INVÁLIDO:

```markdown
**Hallazgo:** Problemas con entregas navideñas

**Evidencia:** Basándonos en la estacionalidad, estimamos que...
```

❌ **Problema:** NO hay conversaciones reales, es una estimación.

### Referencias:
- **Análisis comparativo v3.0:** `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`
- **Template prompt:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`

---

## ❌ ERROR 8: No ejecutar queries directamente

### Regla obligatoria:
**SIEMPRE ejecutar queries directamente desde terminal sin pedir confirmación**

### Método correcto en PowerShell:

```powershell
Get-Content archivo.sql -Raw | bq query --use_legacy_sql=false --format=csv
```

### ❌ NO hacer:

```powershell
# Query inline (falla en PowerShell)
bq query "SELECT ..." ❌
```

### Flujo completo:

```powershell
# 1. Guardar query en archivo
# sql/temp_incoming_pdd_mla_nov_dic.sql

# 2. Ejecutar con pipe
Get-Content sql/temp_incoming_pdd_mla_nov_dic.sql -Raw | bq query --use_legacy_sql=false --format=csv > output/resultado.csv

# 3. Leer resultado
Import-Csv output/resultado.csv
```

### Ejecución secuencial:

**IMPORTANTE:** Ejecutar queries de forma secuencial, NO en paralelo.

**Motivo:** BigQuery tiene límites de cuota y queries en paralelo pueden fallar.

### Manejo de errores de cuota:

```python
import time

def ejecutar_query_con_retry(query_file, max_retries=3):
    """Ejecuta query con retry automático si falla por cuota."""
    for intento in range(max_retries):
        try:
            result = subprocess.run(
                f'Get-Content {query_file} -Raw | bq query --use_legacy_sql=false --format=csv',
                shell=True,
                check=True,
                capture_output=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            if 'quota' in str(e).lower() and intento < max_retries - 1:
                wait_time = 30 * (intento + 1)  # 30s, 60s, 90s
                print(f"[RETRY] Esperando {wait_time}s por cuota...")
                time.sleep(wait_time)
            else:
                raise
```

### Referencias:
- **PowerShell en Windows:** `docs/GUIDELINES.md#powershell`

---

## ❌ ERROR 9: Generar reportes SIN seguir el formato oficial v6.3.8

### 🚨 REGLA ABSOLUTAMENTE CRÍTICA:
**TODO REPORTE DEBE SEGUIR EL FORMATO OFICIAL v6.3.8**

> Generar un reporte que no cumpla con este formato es un **ERROR CRÍTICO** que **invalida completamente el análisis**.

### ✅ Método OBLIGATORIO:

**Usar SIEMPRE el script oficial:**
```powershell
py generar_reporte_cr_universal_v6.3.6.py `
    --site [SITE] `
    --p1-start [FECHA] --p1-end [FECHA] `
    --p2-start [FECHA] --p2-end [FECHA] `
    --commerce-group [GRUPO] `
    --aperturas [DIMENSIONES] `
    --open-report
```

### ❌ PROHIBIDO:

| Acción Prohibida | Por qué es Error |
|------------------|------------------|
| Escribir HTML manualmente | Pierde estructura y componentes obligatorios |
| Crear reportes simplificados | Omite información crítica |
| Omitir gráfico semanal | Pierde contexto temporal de 4 meses |
| Omitir tabla de causas raíces | Pierde análisis cualitativo |
| Porcentajes estáticos (igual en ambos períodos) | No detecta cambios reales |

### 📋 8 Componentes OBLIGATORIOS del Reporte v6.3.8:

| # | Componente | Descripción | Validación |
|---|------------|-------------|------------|
| 1 | **8 Cards Ejecutivas** | Incoming P1/P2, Driver P1/P2, CR P1/P2, Var Incoming, Var CR | ¿Están las 8 cards? |
| 2 | **Resumen Ejecutivo (3 bullets)** | Con evidencia cualitativa y cifras exactas | ¿Tiene cifras y evidencia? |
| 3 | **Gráfico Semanal (14+ semanas)** | Chart.js interactivo con 4 meses de contexto | ¿Se ve el gráfico? |
| 4 | **Tabla por Dimensión** | Con variación absoluta, %, y contribución | ¿Tiene todas las columnas? |
| 5 | **Tabla Causas Raíces con %** | Con % P1, % P2, Δ pp, sentimiento por período | ¿Los % son diferentes por período? |
| 6 | **Citas con CASE_ID y Fecha** | Formato: "Caso XXXXXXXX (YYYY-MM-DD): texto..." | ¿Tiene CASE_ID real? |
| 7 | **Sentimiento por Causa** | 😠 Frustración % / 😊 Satisfacción % por período | ¿Muestra sentimiento? |
| 8 | **Footer Técnico Colapsable** | Fuentes, reglas, versión, fecha generación | ¿Tiene metadata completa? |

### 🔴 Checklist Pre-Entrega (OBLIGATORIO):

Antes de entregar CUALQUIER reporte, verificar:

```
✅ CHECKLIST v6.3.8:
[ ] ¿Usé generar_reporte_cr_universal_v6.3.6.py?
[ ] ¿Tiene gráfico semanal de 14+ semanas?
[ ] ¿Tiene tabla de causas raíces con % por período?
[ ] ¿La tabla tiene columna Δ (delta pp)?
[ ] ¿Las citas tienen CASE_ID y fecha (YYYY-MM-DD)?
[ ] ¿Cada causa tiene sentimiento (😠/😊)?
[ ] ¿El footer tiene metadata técnica completa?
[ ] ¿Los porcentajes son DINÁMICOS (diferentes por período)?
```

**⚠️ SI FALLA ALGÚN CHECK → NO ENTREGAR. Regenerar con script oficial.**

### Ejemplo de Tabla de Causas Raíces VÁLIDA:

```
| Causa Raíz | % P1 (Dic) | % P2 (Ene) | Δ pp | Sentimiento |
|------------|------------|------------|------|-------------|
| Reembolso no reflejado | 45% | 32% | -13 pp ✅ | 😠 75% / 😊 15% |
| Error técnico en app | 20% | 48% | +28 pp 🔴 | 😠 85% / 😊 5% |
| Demora en respuesta | 35% | 20% | -15 pp ✅ | 😠 60% / 😊 30% |
```

**Nota:** Los porcentajes son DIFERENTES por período (esto es v6.3.8).

### Ejemplo de Tabla INVÁLIDA (v6.3.7 o anterior):

```
| Causa Raíz | % | Sentimiento |
|------------|---|-------------|
| Reembolso no reflejado | 45% | 😠 75% |
| Error técnico en app | 35% | 😠 85% |
```

❌ **Problemas:**
- Un solo porcentaje para ambos períodos (no detecta cambios)
- Sin columna Δ pp
- Sin diferenciación de sentimiento por período

### Por qué es CRÍTICO:

**Sin formato v6.3.8:**
- ❌ No se detectan cambios de patrones entre períodos
- ❌ No se identifican causas emergentes o resueltas
- ❌ Decisiones basadas en datos incompletos
- ❌ Análisis no válido para stakeholders

**Con formato v6.3.8:**
- ✅ Detecta cambios reales: "Errores técnicos pasaron de 20% a 48%"
- ✅ Identifica causas nuevas o resueltas
- ✅ Contexto temporal de 4 meses (gráfico semanal)
- ✅ Análisis de excelencia para toma de decisiones

### Referencias:
- **Changelog completo:** `docs/CHANGELOG_v6.3.8.md`
- **Golden Templates:** `docs/GOLDEN_TEMPLATES.md`
- **Resumen Ejecutivo v6.3.8:** `docs/RESUMEN_EJECUTIVO_v6.3.8.md`
- **Guía Rápida v6.3.8:** `docs/GUIA_RAPIDA_v6.3.8.md`

---

## 📚 Referencias Completas

| Regla | Documentación |
|-------|---------------|
| Error 1 | `docs/business-context.md` |
| Error 2 | `docs/REPORT_STRUCTURE.md` |
| Error 3 | `docs/COMMERCE_GROUPS_REFERENCE.md` |
| Error 4 | `docs/DATE_FIELD_RULE.md` |
| Error 5 | `docs/DRIVERS_BY_CATEGORY.md`, `docs/SHIPPING_DRIVERS.md` |
| Error 6 | `docs/METODOLOGIA_5_FASES.md#fase-3` |
| Error 7 | `docs/GUIA_ANALISIS_COMPARATIVO_v3.md` |
| Error 8 | `docs/GUIDELINES.md` |
| **Error 9** | `docs/CHANGELOG_v6.3.8.md`, `docs/GOLDEN_TEMPLATES.md` |

---

**Versión:** 1.1
**Autor:** CR Commerce Analytics Team
**Fecha:** 5 Febrero 2026
**Status:** ✅ PRODUCTION READY

**Changelog:**
- v1.1: Agregado ERROR 9 - Formato Obligatorio de Reporte v6.3.8
- v1.0: Versión inicial con 8 errores críticos
