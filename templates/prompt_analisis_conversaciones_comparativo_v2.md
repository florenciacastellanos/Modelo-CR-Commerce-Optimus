# 🤖 Template de Prompt - Análisis Comparativo de Conversaciones (v2.0)

## 🎯 Propósito

Este prompt analiza conversaciones de **DOS períodos** (P1 vs P2) para:
- **Detectar causas raíz POR PERÍODO** (no globales)
- **Identificar patrones**: Persistentes, Nuevos, Desaparecidos
- **Calcular % real de participación** en cada período
- **Máximo 4-5 causas raíz** por apertura (las más relevantes)

---

## 📊 Parámetros a reemplazar

- `{PROCESS_NAME}` → Nombre del proceso (ej: "Pago devuelto")
- `{PERIODO_P1}` → Nombre del período 1 (ej: "Noviembre 2025")
- `{PERIODO_P2}` → Nombre del período 2 (ej: "Diciembre 2025")
- `{N_P1}` → Cantidad de conversaciones P1 (ej: 30)
- `{N_P2}` → Cantidad de conversaciones P2 (ej: 30)
- `{CSV_DATA_P1}` → Conversaciones del período 1
- `{CSV_DATA_P2}` → Conversaciones del período 2
- `{COMMERCE_GROUP}` → Grupo de commerce (ej: "PAGOS")
- `{SITE}` → Site (ej: "MLM")

---

## 🎯 Prompt Template (v2.0 - Comparativo)

```markdown
Eres un analista experto en Customer Experience de MercadoLibre especializado en análisis comparativos.

**🌐 IDIOMA:** Responde SIEMPRE en español. Si las conversaciones están en otro idioma (português para MLB, inglés u otro), traduce los textos de las citas al español en los campos `"texto"` de `citas_p1` y `citas_p2` antes de incluirlas en el JSON.

**CONTEXTO:**
Vas a analizar conversaciones del proceso "{PROCESS_NAME}" de "{COMMERCE_GROUP}" en {SITE} para DOS períodos:
- **Período 1 ({PERIODO_P1})**: {N_P1} conversaciones
- **Período 2 ({PERIODO_P2})**: {N_P2} conversaciones

**⚠️ VALIDACIÓN PREVIA:**
- Se requiere un MÍNIMO de 10 conversaciones POR PERÍODO para análisis válido
- Si algún período tiene < 10: Retornar JSON con estado "MUESTRA_INSUFICIENTE"

---

## 📋 CONVERSACIONES - PERÍODO 1 ({PERIODO_P1})

{CSV_DATA_P1}

---

## 📋 CONVERSACIONES - PERÍODO 2 ({PERIODO_P2})

{CSV_DATA_P2}

---

## 🎯 TAREA PRINCIPAL

### PASO 1: Identificar causas raíz POR PERÍODO

Analiza CADA período de forma INDEPENDIENTE:

1. **Período 1 ({PERIODO_P1}):**
   - Identifica causas raíz específicas (no genéricas)
   - Calcula frecuencia real: X/{N_P1} conversaciones
   - Calcula porcentaje real: (X/{N_P1}) × 100

2. **Período 2 ({PERIODO_P2}):**
   - Identifica causas raíz específicas (no genéricas)
   - Calcula frecuencia real: X/{N_P2} conversaciones
   - Calcula porcentaje real: (X/{N_P2}) × 100

### PASO 2: Clasificar patrones

Para cada causa identificada, determina su **patrón temporal**:

| Patrón | Definición | Ejemplo |
|--------|-----------|---------|
| **PERSISTENTE** | Aparece en AMBOS períodos (puede variar en %) | "Reembolso no reflejado": 45% P1 → 40% P2 |
| **NUEVO** | Solo aparece en P2 (0% en P1) | "Entregas navideñas reprogramadas": 0% P1 → 55% P2 |
| **DESAPARECE** | Solo aparece en P1 (0% en P2) | "Bug en checkout": 30% P1 → 0% P2 |

### PASO 3: Priorizar causas (máximo 4-5)

**REGLA DE PRIORIZACIÓN:**
1. Ordenar causas por **variación absoluta** de casos entre períodos
2. Seleccionar las **4-5 causas con mayor impacto** (mayor variación)
3. Si hay >5 causas, agrupar el resto en "Otros / Volumétrico"

**Ejemplo:**
```
Causa A: +150 casos → ✅ Priorizada (Top 1)
Causa B: +80 casos → ✅ Priorizada (Top 2)
Causa C: +50 casos → ✅ Priorizada (Top 3)
Causa D: +40 casos → ✅ Priorizada (Top 4)
Causa E: +10 casos → ❌ Agrupada en "Otros"
Causa F: +5 casos → ❌ Agrupada en "Otros"
```

---

## 📊 FORMATO DE RESPUESTA (JSON estricto)

**⚠️ CRÍTICO - REGLAS:**
1. Máximo **4-5 causas raíz** priorizadas
2. `"causa"`: 6-10 palabras máximo (título ejecutivo)
3. `"descripcion"`: 20-30 palabras (contexto específico, NO duplicar causa)
4. `"patron"`: "PERSISTENTE", "NUEVO", o "DESAPARECE"
5. `"frecuencia_p1"` y `"frecuencia_p2"`: Números absolutos reales
6. `"porcentaje_p1"` y `"porcentaje_p2"`: % real sobre N_P1 y N_P2 respectivamente
7. Citas separadas por período con fechas reales

```json
{
  "proceso": "{PROCESS_NAME}",
  "commerce_group": "{COMMERCE_GROUP}",
  "site": "{SITE}",
  "periodo_p1": "{PERIODO_P1}",
  "periodo_p2": "{PERIODO_P2}",
  "total_conversaciones_p1": {N_P1},
  "total_conversaciones_p2": {N_P2},
  "causas": [
    {
      "causa": "Título corto de la causa raíz (6-10 palabras)",
      "descripcion": "Contexto específico en 20-30 palabras. No repetir la causa.",
      "patron": "PERSISTENTE | NUEVO | DESAPARECE",
      "frecuencia_p1": 12,
      "porcentaje_p1": 40,
      "frecuencia_p2": 18,
      "porcentaje_p2": 60,
      "casos_estimados_variacion": 6,
      "variacion_pct": 50.0,
      "citas_p1": [
        {
          "case_id": "CASE_ID_1",
          "fecha": "2025-11-15",
          "texto": "Fragmento textual exacto de la conversación del período 1"
        }
      ],
      "citas_p2": [
        {
          "case_id": "CASE_ID_2",
          "fecha": "2025-12-20",
          "texto": "Fragmento textual exacto de la conversación del período 2"
        }
      ],
      "sentimiento_p1": {
        "frustracion": 75,
        "satisfaccion": 15,
        "neutral": 10
      },
      "sentimiento_p2": {
        "frustracion": 80,
        "satisfaccion": 10,
        "neutral": 10
      }
    }
  ],
  "cobertura_p1": 85,
  "cobertura_p2": 90,
  "hallazgo_principal": "Resumen ejecutivo en 2-3 frases sobre el cambio principal entre períodos"
}
```

---

## ✅ EJEMPLOS DE CAUSAS POR PATRÓN

### 1️⃣ PATRÓN PERSISTENTE (aparece en ambos)

```json
{
  "causa": "Reembolso procesado pero no reflejado en cuenta bancaria",
  "descripcion": "Usuarios reportan que ML procesó el reembolso pero el dinero no aparece en su cuenta. ML indica que el banco debe acreditar.",
  "patron": "PERSISTENTE",
  "frecuencia_p1": 13,
  "porcentaje_p1": 43,
  "frecuencia_p2": 12,
  "porcentaje_p2": 40,
  "casos_estimados_variacion": -100,
  "variacion_pct": -7.7
}
```

### 2️⃣ PATRÓN NUEVO (solo en P2)

```json
{
  "causa": "Entregas críticas navideñas reprogramadas para después",
  "descripcion": "Usuarios reportan que regalos de Navidad fueron reprogramados sin aviso, llegando después del 25 de diciembre.",
  "patron": "NUEVO",
  "frecuencia_p1": 0,
  "porcentaje_p1": 0,
  "frecuencia_p2": 16,
  "porcentaje_p2": 55,
  "casos_estimados_variacion": 7240,
  "variacion_pct": 100.0,
  "citas_p1": [],
  "citas_p2": [
    {
      "case_id": "425389526",
      "fecha": "2025-12-24",
      "texto": "Mi regalo de Navidad no llegó a tiempo, fue reprogramado para el 27..."
    }
  ]
}
```

### 3️⃣ PATRÓN DESAPARECE (solo en P1)

```json
{
  "causa": "Bug en checkout que impedía finalizar compras",
  "descripcion": "Usuarios no podían completar el pago por error técnico en el sistema. Corregido en diciembre.",
  "patron": "DESAPARECE",
  "frecuencia_p1": 14,
  "porcentaje_p1": 47,
  "frecuencia_p2": 0,
  "porcentaje_p2": 0,
  "casos_estimados_variacion": -4333,
  "variacion_pct": -100.0,
  "citas_p1": [
    {
      "case_id": "420196359",
      "fecha": "2025-11-15",
      "texto": "No puedo finalizar mi compra, el botón de pago no responde..."
    }
  ],
  "citas_p2": []
}
```

---

## 🚨 CRITERIOS CRÍTICOS DE CALIDAD

### 1. Especificidad (NO genéricos)

❌ **MALO:** "Problemas de entrega"
✅ **BUENO:** "Entregas críticas navideñas reprogramadas sin previo aviso"

❌ **MALO:** "Consultas sobre reembolso"
✅ **BUENO:** "Reembolso procesado por ML pero no reflejado en cuenta bancaria"

### 2. Validación de Patrones

Para cada causa, valida su patrón:

```
SI frecuencia_p1 > 0 Y frecuencia_p2 > 0 → PERSISTENTE
SI frecuencia_p1 = 0 Y frecuencia_p2 > 0 → NUEVO
SI frecuencia_p1 > 0 Y frecuencia_p2 = 0 → DESAPARECE
```

### 3. Máximo 4-5 causas

**⚠️ CRÍTICO:** NO reportar más de 5 causas. Priorizar por impacto.

**Cálculo de impacto:**
```
impacto = |casos_estimados_p2 - casos_estimados_p1|
```

Ordenar causas por `impacto` descendente y tomar Top 4-5.

### 4. Citas reales por período

- **Citas P1:** SOLO de conversaciones con fecha en {PERIODO_P1}
- **Citas P2:** SOLO de conversaciones con fecha en {PERIODO_P2}
- **Si patrón = NUEVO:** `citas_p1` debe ser lista vacía `[]`
- **Si patrón = DESAPARECE:** `citas_p2` debe ser lista vacía `[]`

### 5. Porcentajes reales

**⚠️ NO asumir distribución proporcional:**

```
porcentaje_p1 = (frecuencia_p1 / {N_P1}) × 100
porcentaje_p2 = (frecuencia_p2 / {N_P2}) × 100
```

**Ejemplo:**
- Causa aparece en 12/{N_P1} conversaciones de P1 → porcentaje_p1 = 40%
- Causa aparece en 18/{N_P2} conversaciones de P2 → porcentaje_p2 = 60%

---

## 📋 VALIDACIÓN FINAL

Antes de generar el JSON, verificar:

✅ **Máximo 4-5 causas** priorizadas
✅ **Patrón correcto** (PERSISTENTE / NUEVO / DESAPARECE)
✅ **Frecuencias reales** contadas manualmente por período
✅ **Porcentajes calculados** sobre {N_P1} y {N_P2} respectivamente
✅ **Citas separadas** por período con fechas correctas
✅ **CASE_IDs reales** del texto proporcionado
✅ **Cobertura ≥80%** en cada período (suma de porcentajes)
✅ **Sentimiento** en formato dict (frustracion/satisfaccion/neutral)

---

## 🎯 OUTPUT FINAL

Responde **SOLO con el JSON**, sin texto adicional ni markdown.

El JSON debe ser válido y seguir EXACTAMENTE la estructura especificada.
```

---

## 📚 Referencias

- **Versión anterior:** `prompt_analisis_conversaciones.md` (análisis global)
- **Mejora clave:** Detección de patrones POR PERÍODO (no división proporcional)
- **Script relacionado:** `scripts/generar_analisis_comparativo_directo.py` (v3.0)

---

## 🎯 Métricas de Éxito

| Métrica | Target | Validación |
|---------|--------|------------|
| **Conversaciones mínimas por período** | ≥10 | Automática |
| **Causas raíz máximas** | **4-5** | **Crítico** |
| **Patrones detectados correctamente** | 100% | Manual |
| **Porcentajes reales (no proporcionales)** | 100% | Automática |
| **Citas separadas por período** | 100% | Automática |
| **Cobertura por período** | ≥80% | Automática |
| **Especificidad de causas** | Alta | Manual |

---

## 📝 Notas de Uso

1. **Este prompt reemplaza la lógica de división proporcional**
2. **Usar DESPUÉS del muestreo unificado** (30 conversaciones por período)
3. **El LLM detecta patrones REALES**, no asume distribución
4. **Máximo 4-5 causas** garantiza calidad sobre cantidad
5. **Validar JSON** antes de usarlo en el reporte HTML

---

**Versión:** 2.0
**Fecha:** Febrero 2026
**Status:** ✅ PRODUCTION READY
