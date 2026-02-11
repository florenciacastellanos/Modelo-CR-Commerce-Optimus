# 🧭 Metodología de Análisis CR - 5 FASES Detalladas

**Versión:** 1.0
**Fecha:** 4 Febrero 2026

Este documento describe la metodología completa de análisis de Contact Rate en 5 fases.

---

## 📋 FASE 0: Confirmación de Parámetros (PRE-ANÁLISIS)

### Objetivo:
Validar y confirmar todos los parámetros ANTES de ejecutar el análisis.

### Parámetros Obligatorios:

1. **Site:** MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE
2. **Períodos:** P1 (fecha inicio + fin) y P2 (fecha inicio + fin)
3. **Tipo de variación:** Mensual, semanal, quarter
4. **Alcance:** Commerce group completo O proceso específico
5. **Aperturas:** PROCESO, CDU, TIPIFICACION, etc.

### Template de Confirmación:

**Para Commerce Group completo:**
```
Voy a analizar:
- Site: [X]
- Período: [P1] vs [P2]
- Tipo de variación: [mensual/semanal/quarter]
- Commerce Group: [X] (análisis completo de todos los procesos)
- Aperturas: [X, Y, Z]

Confirmame si es correcto y avanzo.
```

**Para Proceso Específico:**
```
Voy a analizar:
- Site: [X]
- Período: [P1] vs [P2]
- Tipo de variación: [mensual/semanal/quarter]
- Proceso específico: [X] (dentro de commerce group [Y])
- Aperturas: [X, Y, Z]

Confirmame si es correcto y avanzo.
```

### Validación:

- [ ] Todos los parámetros especificados
- [ ] Site válido (uno de los 8)
- [ ] Períodos en formato correcto (YYYY-MM-DD)
- [ ] Commerce group existe
- [ ] Si proceso específico: pertenece al commerce group

---

## FASE 1: Baseline (Resultado Macro)

### Objetivo:
Calcular métricas principales y validar reglas críticas.

### Paso 1.1: Calcular Incoming

**Query base:**
```sql
SELECT 
  DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS MONTH,
  COUNT(DISTINCT C.CAS_CASE_ID) AS INCOMING
FROM 
  `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE 
  DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) BETWEEN '{p1_start}' AND '{p2_end}'
  AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
  AND C.COMMERCE_GROUP = '{commerce_group}'
  AND C.SIT_SITE_ID = '{site}'
GROUP BY 1
ORDER BY 1
```

**Validaciones:**
- [ ] Incoming > 0 en ambos períodos
- [ ] Usar `CONTACT_DATE_ID` (no `OFC_MONTH_ID`)
- [ ] Aplicar exclusiones automáticas

### Paso 1.2: Calcular Driver

**Depende de la categoría del commerce group:**

#### Post-Compra (PDD, PNR):
```sql
-- Driver: Órdenes GLOBALES
SELECT 
  DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) AS MONTH,
  COUNT(DISTINCT ORD.ORD_ORDER_ID) AS DRIVER
FROM 
  `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
WHERE 
  DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) BETWEEN '{p1_start}' AND '{p2_end}'
  AND ORD.ORD_GMV_FLG = TRUE
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
  DATE_TRUNC(ORD.ORD_CLOSED_DT, MONTH) BETWEEN '{p1_start}' AND '{p2_end}'
  AND ORD.ORD_GMV_FLG = TRUE
  AND ORD.ORD_MARKETPLACE_FLG = TRUE
  AND ORD.SIT_SITE_ID = '{site}'  -- ✅ FILTRO POR SITE
  AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
GROUP BY 1
```

**Validaciones:**
- [ ] Driver > 0 en ambos períodos
- [ ] Driver correcto según categoría (ver `docs/DRIVERS_BY_CATEGORY.md`)
- [ ] Aplicar filtros base correctos

### Paso 1.3: Calcular CR

**Fórmula:**
```
CR = (Incoming / Driver) × 100
```

**Implementación:**
```python
def calcular_cr(incoming, driver):
    """Calcula CR en puntos porcentuales."""
    if driver == 0:
        return 0
    return (incoming / driver) * 100

# Ejemplo:
incoming_nov = 1500
driver_nov = 50000
cr_nov = calcular_cr(incoming_nov, driver_nov)
print(f"CR Nov: {cr_nov:.4f} pp")  # 3.0000 pp
```

**Validaciones:**
- [ ] CR entre 0 y 100 pp
- [ ] Multiplicar por 100 (no por 1 ni 1000)
- [ ] Resultado en pp (no en decimal)

### Paso 1.4: Validar Reglas Críticas

Ejecutar validaciones de los 8 errores críticos:

- [ ] Error 1: Fórmula CR correcta
- [ ] Error 2: Variaciones en pp + %
- [ ] Error 3: CASE WHEN para commerce groups
- [ ] Error 4: CONTACT_DATE_ID
- [ ] Error 5: Driver correcto por categoría
- [ ] Error 6-8: Se validan en fases posteriores

### Paso 1.5: Definir Tipo de Reporte

**Cross-Site** (si site = 'ALL' o múltiples sites):
- 3 tablas: Por Site, Por Proceso, Por CDU
- Comparación entre sites

**Single-Site** (si site específico):
- 2 tablas: Por Proceso, Por CDU/Tipificación
- Drill-down en un solo site

**Output FASE 1:**
```python
{
    'incoming_p1': 1500,
    'incoming_p2': 1650,
    'driver_p1': 50000,
    'driver_p2': 52000,
    'cr_p1': 3.0000,
    'cr_p2': 3.1731,
    'var_incoming': 150,
    'var_incoming_pct': 10.0,
    'var_cr': 0.1731,
    'var_cr_pct': 5.77,
    'tipo_reporte': 'single_site'
}
```

---

## FASE 2: Drill-Down Top-Down

### Objetivo:
Identificar qué elementos explican la variación (regla 80%).

### Jerarquía de Análisis:

```
1. Commerce Group (ej: PDD)
   ↓
2. PROCESS_NAME (ej: Arrepentimiento)
   ↓
3. CDU (ej: Arrepentimiento - Cambio de opinión) [si existe]
   ↓
4. TIPIFICACION (ej: Solicitud de devolución) [si existe]
   ↓
5. CLA_REASON_DETAIL (máxima granularidad) [si existe]
```

**⚠️ Regla de adaptabilidad:** Usar la dimensión más granular DISPONIBLE.

### 📊 REGLA DEL 80% (PRIORIZACIÓN OBLIGATORIA)

#### Fórmula de contribución:
```python
def calcular_contribucion(delta_incoming_elemento, delta_incoming_total):
    """Calcula contribución de un elemento a la variación total."""
    return abs(delta_incoming_elemento) / abs(delta_incoming_total) * 100
```

#### Proceso:

**PASO 1:** Calcular contribución de cada elemento
```sql
WITH variaciones AS (
  SELECT 
    PROCESO,
    SUM(CASE WHEN PERIODO = 'P1' THEN INCOMING ELSE 0 END) AS INC_P1,
    SUM(CASE WHEN PERIODO = 'P2' THEN INCOMING ELSE 0 END) AS INC_P2,
    SUM(CASE WHEN PERIODO = 'P2' THEN INCOMING ELSE 0 END) - 
    SUM(CASE WHEN PERIODO = 'P1' THEN INCOMING ELSE 0 END) AS DELTA_INC
  FROM incoming_por_proceso
  GROUP BY 1
),
total AS (
  SELECT SUM(ABS(DELTA_INC)) AS DELTA_TOTAL
  FROM variaciones
)
SELECT 
  v.PROCESO,
  v.DELTA_INC,
  (ABS(v.DELTA_INC) / t.DELTA_TOTAL * 100) AS CONTRIBUCION_PCT
FROM variaciones v
CROSS JOIN total t
ORDER BY ABS(v.DELTA_INC) DESC
```

**PASO 2:** Ordenar por contribución absoluta (descendente)

**PASO 3:** Seleccionar hasta acumular ≥80%

```python
def seleccionar_priorizados(elementos, umbral=80):
    """
    Selecciona elementos hasta acumular ≥umbral% de contribución.
    
    Args:
        elementos: Lista de dicts con 'nombre', 'contribucion'
        umbral: Porcentaje mínimo a acumular (default 80)
    
    Returns:
        Lista de elementos priorizados
    """
    # Ordenar por contribución descendente
    elementos_sorted = sorted(
        elementos, 
        key=lambda x: abs(x['contribucion']), 
        reverse=True
    )
    
    acumulado = 0
    priorizados = []
    
    for elem in elementos_sorted:
        priorizados.append(elem)
        acumulado += abs(elem['contribucion'])
        
        if acumulado >= umbral:
            break
    
    return priorizados
```

**Ejemplo:**
```
Proceso A: +150 casos → 75.0% → ✅ Priorizado (Top 1)
Proceso B: +30 casos → 15.0% → ✅ Priorizado (acum 90%)
Proceso C: +10 casos → 5.0% → ❌ No priorizado
```

**PASO 4:** Analizar SOLO los elementos priorizados en FASE 3

### Query Template (Drill-Down por PROCESO):

```sql
WITH incoming_por_proceso AS (
  SELECT 
    C.PROCESS_NAME AS PROCESO,
    DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
    COUNT(DISTINCT C.CAS_CASE_ID) AS INCOMING
  FROM 
    `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
  WHERE 
    DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('{p1_month}', '{p2_month}')
    AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
    AND C.COMMERCE_GROUP = '{commerce_group}'
    AND C.SIT_SITE_ID = '{site}'
  GROUP BY 1, 2
)
SELECT 
  PROCESO,
  SUM(CASE WHEN PERIODO = '{p1_month}' THEN INCOMING ELSE 0 END) AS INC_P1,
  SUM(CASE WHEN PERIODO = '{p2_month}' THEN INCOMING ELSE 0 END) AS INC_P2,
  SUM(CASE WHEN PERIODO = '{p2_month}' THEN INCOMING ELSE 0 END) - 
  SUM(CASE WHEN PERIODO = '{p1_month}' THEN INCOMING ELSE 0 END) AS VAR_CASOS
FROM incoming_por_proceso
GROUP BY 1
ORDER BY ABS(VAR_CASOS) DESC
```

**Output FASE 2:**
```python
{
    'elementos_priorizados': [
        {
            'nombre': 'Arrepentimiento',
            'inc_p1': 500,
            'inc_p2': 650,
            'var_casos': 150,
            'contribucion': 75.0,
            'acumulado': 75.0
        },
        {
            'nombre': 'Defectuoso',
            'inc_p1': 300,
            'inc_p2': 330,
            'var_casos': 30,
            'contribucion': 15.0,
            'acumulado': 90.0
        }
    ],
    'elementos_no_priorizados': [
        {
            'nombre': 'Otros',
            'var_casos': 20,
            'contribucion': 10.0
        }
    ]
}
```

---

## FASE 3: Evidencia (Conversaciones + Eventos) ⭐ AUTOMÁTICA

### ⚠️ ESTA FASE ES AUTOMÁTICA Y OBLIGATORIA

### A) Peak Detection (ANTES del muestreo)

**Objetivo:** Identificar días con picos anormales de casos.

**Regla direccional:**
- CR subió → buscar peaks en período **actual** (P2)
- CR bajó → buscar peaks en período **anterior** (P1)

**Criterio:** Pico si casos > promedio + 1.5 × desviación estándar

**Query Template:**
```sql
WITH diario AS (
  SELECT 
    C.CONTACT_DATE_ID AS FECHA,
    COUNT(DISTINCT C.CAS_CASE_ID) AS CASOS
  FROM 
    `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
  WHERE 
    DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '{periodo_analizar}'
    AND C.PROCESS_NAME = '{proceso}'
    AND C.COMMERCE_GROUP = '{commerce_group}'
    AND C.SIT_SITE_ID = '{site}'
  GROUP BY 1
),
stats AS (
  SELECT 
    AVG(CASOS) AS PROMEDIO,
    STDDEV(CASOS) AS DESV_STD
  FROM diario
)
SELECT 
  d.FECHA,
  d.CASOS,
  s.PROMEDIO,
  s.DESV_STD,
  (s.PROMEDIO + 1.5 * s.DESV_STD) AS UMBRAL_PICO,
  CASE 
    WHEN d.CASOS > (s.PROMEDIO + 1.5 * s.DESV_STD) THEN 'PICO'
    ELSE 'NORMAL'
  END AS CLASIFICACION
FROM diario d
CROSS JOIN stats s
WHERE d.CASOS > (s.PROMEDIO + 1.5 * s.DESV_STD)
ORDER BY d.CASOS DESC
```

**Output:**
```
FECHA       | CASOS | PROMEDIO | UMBRAL_PICO | CLASIFICACION
------------|-------|----------|-------------|---------------
2025-12-24  | 450   | 150      | 300         | PICO
2025-12-25  | 380   | 150      | 300         | PICO
```

### B) Análisis de Conversaciones - MÉTODO OPTIMIZADO v5.0 (Comparativo v3.0)

**Estándar obligatorio:**
- **Umbral mínimo:** ≥10 conversaciones por elemento-período
- **Muestra:** 30 casos por dimensión-período (60 total por proceso)
- **Fuente:** `BT_CX_STUDIO_SAMPLE` (campo `CONVERSATION_SUMMARY`)
- **Cobertura:** ≥80% de las menciones
- **Evidencia:** Citas textuales con CASE_IDs reales

**PASO 1: Query Unificada de Muestreo**

```sql
-- Template: sql/templates/muestreo_unificado_template.sql
WITH dias_pico AS (
  -- Detectar días pico (query anterior)
  ...
),
muestra_ponderada AS (
  SELECT 
    CONV.CAS_CASE_ID,
    CONV.CONTACT_DATE_ID,
    CONV.PROCESS_NAME,
    CONV.CONVERSATION_SUMMARY,
    CASE 
      WHEN CONV.CONTACT_DATE_ID IN (SELECT FECHA FROM dias_pico) THEN 'PICO'
      ELSE 'NORMAL'
    END AS TIPO_DIA,
    ROW_NUMBER() OVER (
      PARTITION BY CONV.PROCESS_NAME, TIPO_DIA 
      ORDER BY RAND()
    ) AS RN
  FROM 
    `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE` CONV
  WHERE 
    DATE_TRUNC(CONV.CONTACT_DATE_ID, MONTH) IN ('{p1_month}', '{p2_month}')
    AND CONV.PROCESS_NAME IN ({procesos_priorizados})
    AND CONV.COMMERCE_GROUP = '{commerce_group}'
    AND CONV.SIT_SITE_ID = '{site}'
)
SELECT 
  CAS_CASE_ID,
  CONTACT_DATE_ID,
  PROCESS_NAME,
  CONVERSATION_SUMMARY
FROM muestra_ponderada
WHERE 
  (TIPO_DIA = 'PICO' AND RN <= 21)  -- 70% de días pico
  OR
  (TIPO_DIA = 'NORMAL' AND RN <= 9)  -- 30% de días normales
ORDER BY PROCESS_NAME, CONTACT_DATE_ID
```

**Muestreo ponderado:** 70% casos de días pico + 30% resto

**PASO 2: Análisis con Cursor AI (Comparativo v3.0)**

**Template:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`

**Proceso:**
1. Dividir CSV por proceso
2. Para cada proceso, generar prompt comparativo con conversaciones de AMBOS períodos
3. Cursor AI analiza y detecta patrones: PERSISTENTE / NUEVO / DESAPARECE
4. Capturar JSON con estructura v3.0
5. Validar: CASE_IDs reales + cobertura ≥80% + máximo 4-5 causas

**Output esperado (v3.0):**
```json
{
  "proceso": "Arrepentimiento",
  "causas": [
    {
      "causa": "Producto diferente al anunciado",
      "patron": "PERSISTENTE",
      "frecuencia_p1": 12,
      "porcentaje_p1": 40,
      "frecuencia_p2": 15,
      "porcentaje_p2": 50,
      "citas_p1": [ ... ],
      "citas_p2": [ ... ],
      "sentimiento_p1": { "frustracion": 80, ... },
      "sentimiento_p2": { "frustracion": 85, ... }
    }
  ]
}
```

**Tiempo esperado:** ~6 minutos para 6 procesos

### C) Correlación con Eventos Comerciales

**Estándar obligatorio:**

**CON hard metrics (v4.0):**
```python
import pandas as pd

# Cargar hard metrics
metrics_path = f'metrics/eventos/data/correlacion_{site}_{periodo}.parquet'
if os.path.exists(metrics_path):
    df_eventos = pd.read_parquet(metrics_path)
    
    # Correlación exacta (100% incoming)
    correlacion = df_eventos[
        (df_eventos['COMMERCE_GROUP'] == commerce_group) &
        (df_eventos['PROCESO'] == proceso)
    ]
else:
    # Fallback: muestra
    correlacion = calcular_correlacion_muestra()
    declarar_en_footer("Correlación sobre muestra, no hard metrics")
```

**Fuente:** `WHOWNER.LK_MKP_PROMOTIONS_EVENT`

---

## FASE 4: Sanity Checks (Antes de Concluir)

### Validaciones de Datos:

- [ ] Incoming total > 0
- [ ] Driver total > 0
- [ ] CR en rango razonable (0 < CR < 100 pp)
- [ ] Períodos consistentes (fechas válidas)
- [ ] No hay valores NULL en métricas clave

### Validaciones de Coherencia:

- [ ] Totales coinciden entre todas las tablas
- [ ] % Contribución suma 100.0% en cada tabla (±0.1% margen)
- [ ] Ordenamiento consistente (por variación absoluta desc)
- [ ] Colores semánticos correctos (verde=mejor, rojo=peor)

### Validaciones de Negocio:

- [ ] Driver correcto según categoría (ver `docs/DRIVERS_BY_CATEGORY.md`)
- [ ] Driver global cuando corresponde
- [ ] Exclusiones automáticas aplicadas (queues, processes, CI reasons, flag, MLV)
- [ ] CONTACT_DATE_ID usado (no OFC_MONTH_ID)

### Script de Validación:

```python
def validar_sanity_checks(data):
    """Ejecuta todas las validaciones de sanity checks."""
    
    errors = []
    warnings = []
    
    # Validaciones de datos
    if data['incoming_total'] <= 0:
        errors.append("Incoming total es 0 o negativo")
    
    if data['driver_total'] <= 0:
        errors.append("Driver total es 0 o negativo")
    
    if not (0 < data['cr'] < 100):
        errors.append(f"CR fuera de rango: {data['cr']} pp")
    
    # Validaciones de coherencia
    suma_contribucion = sum([elem['contribucion'] for elem in data['elementos']])
    if abs(suma_contribucion - 100) > 0.1:
        warnings.append(f"Contribución suma {suma_contribucion}%, no 100%")
    
    # Validaciones de negocio
    driver_esperado = get_driver_config(data['commerce_group'])
    if data['driver_usado'] != driver_esperado:
        errors.append(f"Driver incorrecto: {data['driver_usado']} (esperado: {driver_esperado})")
    
    return {
        'valido': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

---

## FASE 5: Entrega (Output Final)

### Componentes Obligatorios:

#### 1. Cards Ejecutivas (8):
- Incoming P1
- Incoming P2
- Driver P1
- Driver P2
- CR P1
- CR P2
- Variación Incoming (casos + %)
- Variación CR (pp + %)

#### 2. Resumen Ejecutivo (3 bullets):

**Bullet 1:** Variación de CR + métricas consolidadas
```
CR {empeoró|mejoró} +X.XXXX pp (+Y.Y%) | {P1_label}: X.XXXX pp → {P2_label}: X.XXXX pp | +Z casos de {COMMERCE_GROUP} en {SITE}
```

**Bullet 2:** Principal elemento + contribución + causa raíz (si existe análisis)
```
{ELEMENTO} lidera la variación (X% de contribución, +Y casos) | Causa raíz principal: {CAUSA} (X% de casos) - {DESCRIPCIÓN_CORTA}
```

**Bullet 3:** Segundo elemento relevante + causa crítica (≥70% frustración) o hallazgo adicional
```
{ELEMENTO_2} muestra el mayor crecimiento relativo (+X% vs periodo anterior) | Causa crítica: {CAUSA} (X% casos, Y% frustración) - {DESCRIPCIÓN_CORTA}
```

#### 3. Gráfico Semanal:
- Mínimo 14 semanas de contexto
- Chart.js para interactividad
- CR en puntos porcentuales (pp)
- Línea de tendencia

#### 4. Tablas con Insights:

**Cross-Site (3 tablas):**
- Tabla 1: Por Site
- Tabla 2: Por Proceso (consolidado)
- Tabla 3: Por CDU (drill-down)

**Single-Site (2 tablas):**
- Tabla 1: Por Proceso
- Tabla 2: Por CDU/Tipificación (según disponibilidad)

#### 5. Análisis Comparativo de Conversaciones (v3.0):

- Tabla con patrones por período (Nov vs Dic)
- Columnas: Patrón/Causa | % Nov | Casos Nov | Sentimiento Nov | % Dic | Casos Dic | Sentimiento Dic | Var Casos | Var % | Δ Prop
- Máximo 4-5 causas raíz por proceso
- Citas expandibles por período

#### 6. Footer Técnico:

- Fuentes de datos (tablas BigQuery)
- Reglas aplicadas (drivers, filtros, exclusiones)
- Conversaciones analizadas (N por período)
- Hard metrics usadas (sí/no)
- Fecha de generación
- Versión del script

### Estructura de Entrega: Pirámide Invertida

| Nivel | Contenido | Tiempo | Implementación |
|-------|-----------|--------|----------------|
| **1** | Resumen Ejecutivo (3 bullets) | 30s | Cards + resumen al inicio |
| **2** | Métricas Consolidadas | 2 min | Tablas expandidas |
| **3** | Principales Elementos e Hipótesis | 5 min | Drill-down por proceso |
| **4** | Evidencia Cualitativa | 10 min | Conversaciones + citas |
| **5** | Análisis Completo con Contexto | 15+ min | Secciones colapsables |

### Validación Final:

- [ ] Todos los componentes presentes
- [ ] Resumen ejecutivo con 3 bullets
- [ ] Gráfico semanal funcionando
- [ ] Tablas con datos correctos
- [ ] Footer técnico completo
- [ ] HTML válido (sin errores de sintaxis)
- [ ] Encoding UTF-8
- [ ] Abrir en navegador automáticamente

---

## 🔍 POST-ENTREGA: Oferta de Deep Dive Adicional (OBLIGATORIO)

### Objetivo:
Una vez completada la entrega del reporte (FASE 5) y mostrado el contenido del reporte en formato Markdown en la conversación (FASE 6), ofrecer al usuario la posibilidad de profundizar el análisis sin necesidad de iniciar un nuevo ciclo desde cero.

### ⚠️ ESTE PASO ES OBLIGATORIO
El agente DEBE presentar las opciones de deep dive al finalizar cada análisis. NO es opcional.

### ⚠️ UNA SOLA RONDA
Después de entregar el deep dive, el ciclo se cierra. NO se vuelve a ofrecer otro deep dive.

### Procedimiento:

**PASO 1:** Presentar opciones de deep dive contextualizadas al análisis realizado:

```markdown
## 🔍 ¿Querés profundizar en algún aspecto?

El análisis de CR para **[COMMERCE_GROUP]** en **[SITE]** ([P1_LABEL] vs [P2_LABEL]) ya está completo.

Basado en los resultados, estas son opciones de deep dive disponibles:

1. **Por [DIMENSIÓN_NO_ANALIZADA]** - Analizar con una apertura adicional no incluida en el análisis original
2. **Elemento específico** - Profundizar en [TOP_CONTRIBUTOR] que explica [X]% de la variación
3. **Muestrear conversaciones adicionales** - Ampliar la muestra de conversaciones para los elementos priorizados (muestra fresca de mayor tamaño)
4. **Temporal** - Análisis detallado enfocado en [PERÍODO_PICO]

⚠️ Nota: El deep dive cross-site no está soportado en el modelo actual.

¿Querés alguno de estos deep dives, otro diferente, o damos por finalizado?
```

**PASO 2:** Esperar respuesta del usuario.

**PASO 3:** Si el usuario acepta, aplicar las reglas de la opción seleccionada (ver detalle abajo). Si algo no está definido o es ambiguo → **PREGUNTAR al usuario** antes de ejecutar.

**PASO 4:** Generar nuevo reporte HTML v6.3.8 (cuantitativo + conversacional). El deep dive es un reporte independiente, no modifica el original.

**PASO 5:** Entregar deep dive → FASE 6 (mostrar contenido del reporte en Markdown en chat) → **FIN** (no re-ofrecer deep dive).

---

### Detalle por Opción

#### Opción 1: Nueva dimensión

| Campo | Valor |
|-------|-------|
| **Acción** | Re-ejecutar pipeline completo (FASE 1-5) con la nueva apertura |
| **Output** | HTML v6.3.8 completo (cuantitativo + conversacional) |
| **Fases** | FASE 1-5 completas |
| **Consulta al usuario** | No necesaria si la dimensión es clara. Si hay múltiples opciones disponibles, listarlas y preguntar cuál prefiere |

**Contexto dinámico:**
```python
# Detectar dimensiones NO analizadas
dimensiones_disponibles = ['PROCESO', 'CDU', 'TIPIFICACION', 'CLA_REASON_DETAIL', 'ENVIRONMENT', 'SOURCE_ID']
dimensiones_usadas = args.aperturas.split(',')
dimensiones_disponibles_deepdive = [d for d in dimensiones_disponibles if d not in dimensiones_usadas]
```

#### Opción 2: Elemento específico

| Campo | Valor |
|-------|-------|
| **Acción** | Drill-down en un solo elemento con mayor granularidad |
| **Output** | HTML v6.3.8 completo (cuantitativo + conversacional) |
| **Fases** | FASE 2-5 (reutiliza baseline) |
| **Consulta al usuario** | **OBLIGATORIA** — Preguntar en qué dimensión quiere profundizar |

**Consulta obligatoria:**
```
Para profundizar en [ELEMENTO], ¿en qué dimensión querés el drill-down?

Opciones disponibles:
- CDU
- TIPIFICACION
- CLA_REASON_DETAIL
- ENVIRONMENT
- [otras disponibles según contexto]
```

**Regla:** NUNCA asumir la dimensión de drill-down. Siempre confirmar con el usuario.

#### Opción 3: Muestrear conversaciones adicionales

| Campo | Valor |
|-------|-------|
| **Acción** | Re-ejecutar FASE 3 con muestra fresca de mayor tamaño |
| **Output** | HTML v6.3.8 completo (cuantitativo + conversacional) |
| **Fases** | FASE 3-5 (re-muestreo + re-análisis + re-reporte) |
| **Consulta al usuario** | **OBLIGATORIA** — Preguntar para qué elementos quiere ampliar |

**Consulta obligatoria:**
```
¿Querés ampliar la muestra para todos los elementos priorizados, o para alguno en particular?

Los elementos disponibles son:
1. [ELEMENTO_1] (contribución: [X]%)
2. [ELEMENTO_2] (contribución: [Y]%)
3. [ELEMENTO_N] (contribución: [Z]%)
```

**Reglas de muestreo:**
- **Muestra fresca**: Se re-muestrea TODO de cero con N ampliado (ej: 60 conv/elemento-período). NO es incremental sobre la muestra anterior
- Mantener misma lógica de CONTRIB_ABS (v6.4.9)
- Mantener proporción 70% picos + 30% normales
- Regenerar análisis comparativo v3.0 completo con la nueva muestra

#### Opción 4: Temporal

| Campo | Valor |
|-------|-------|
| **Acción** | Análisis detallado enfocado en un período/rango temporal específico |
| **Output** | HTML v6.3.8 completo (cuantitativo + conversacional) |
| **Fases** | FASE 1-5 con scope temporal ajustado |
| **Consulta al usuario** | **OBLIGATORIA** — Preguntar qué quiere analizar en detalle |

**Consulta obligatoria:**
```
¿Qué período querés analizar en detalle?

Opciones:
(a) Semana pico [FECHA_PICO] vs semana promedio
(b) Un rango de fechas específico (indicame las fechas)
(c) Otro (describime qué necesitás)
```

**Regla:** Una vez definido el scope temporal, ejecutar análisis cuantitativo + conversacional completo para el rango indicado.

#### Opción 5: Cross-site — ❌ NO SOPORTADA

Si el usuario pide cross-site, responder:

```
⚠️ El modelo actual no soporta deep dive cross-site. 
Para analizar otro site, iniciá un nuevo análisis con el site deseado.
```

---

### Naming del archivo de output

El deep dive se guarda con el **mismo nombre del reporte original** + `_deep_dive`:

```
Original:   reporte_cr_{cg}_{site}_{p1}_{p2}_v6.3.html
Deep dive:  reporte_cr_{cg}_{site}_{p1}_{p2}_v6.3_deep_dive.html
```

El reporte original NO se modifica ni se pisa.

### Validación:

- [ ] Opciones presentadas al usuario después de FASE 6 (Markdown en chat)
- [ ] Opciones adaptadas al contexto real (no genéricas)
- [ ] Top contributor identificado correctamente
- [ ] Dimensiones no analizadas detectadas correctamente
- [ ] Si algo no está definido → se consultó al usuario antes de ejecutar
- [ ] Si deep dive aceptado → nuevo reporte generado con formato v6.3.8
- [ ] Archivo guardado con sufijo `_deep_dive`
- [ ] NO se ofreció deep dive después del deep dive (una sola ronda)
- [ ] Cross-site rechazado con mensaje informativo

---

## 📚 Referencias

- **Reglas críticas:** `docs/REGLAS_CRITICAS_DETALLADAS.md`
- **Análisis comparativo v3.0:** `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`
- **Estructura de reporte:** `docs/REPORT_STRUCTURE.md`
- **Drivers por categoría:** `docs/DRIVERS_BY_CATEGORY.md`
- **Template prompt:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`

---

**Versión:** 1.1 (POST-ENTREGA: Deep Dive con definiciones completas)
**Autor:** CR Commerce Analytics Team
**Fecha:** 9 Febrero 2026
**Status:** ✅ PRODUCTION READY
