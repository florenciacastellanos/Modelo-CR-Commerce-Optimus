# 📖 Guía de Análisis Comparativo v3.0 - Detección Real de Patrones

## 🎯 ¿Qué es v3.0?

El análisis comparativo **v3.0** detecta patrones **REALES por período**, eliminando el problema de división proporcional del v2.0.

### Diferencias clave:

| Característica | v2.0 (Antiguo) | v3.0 (Nuevo) |
|----------------|----------------|--------------|
| **Análisis** | Global → división proporcional | Por período → detección real |
| **Patrones** | Asume distribución uniforme | Detecta: PERSISTENTE / NUEVO / DESAPARECE |
| **Causas máximas** | Sin límite (hasta 10+) | **4-5 priorizadas** |
| **Porcentajes** | Proporcionales al incoming | **Reales** sobre muestra |
| **Calidad** | Media (sesgo de muestreo) | **Alta** (patrones reales) |

---

## 🚀 Flujo Completo v3.0

### FASE 1: Exportar conversaciones (igual que siempre)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
    --site MLM \
    --commerce-group PAGOS \
    --p1-start 2025-12-01 --p1-end 2025-12-31 \
    --p2-start 2026-01-01 --p2-end 2026-01-31 \
    --aperturas CDU \
    --export-only
```

**Output:**
- `conversaciones_{elemento}_mlm_202512.csv` (30 casos por elemento en dic)
- `conversaciones_{elemento}_mlm_202601.csv` (30 casos por elemento en ene)

---

### FASE 2: Generar prompts comparativos

```bash
py scripts/generar_analisis_comparativo_directo.py \
    --site MLM \
    --commerce-group PAGOS \
    --p1-start 2025-12-01 --p1-end 2025-12-31 \
    --p2-start 2026-01-01 --p2-end 2026-01-31 \
    --aperturas CDU \
    --output output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json
```

**Output:**
- `prompts_comparativos_mlm_pagos_202512_202601.txt` (prompts listos para Cursor AI)

**Este archivo contiene un prompt por elemento (ej: "Pago devuelto", "Pago pendiente", etc.)**

---

### FASE 3: Analizar con Cursor AI

1. **Abrir el archivo de prompts:**
   ```
   output/prompts_comparativos_mlm_pagos_202512_202601.txt
   ```

2. **Para cada prompt (ej: elemento "Pago devuelto"):**
   - Copiar el prompt completo
   - Pegar en Cursor AI (chat)
   - Esperar respuesta JSON

3. **Cursor AI responderá con este formato:**

```json
{
  "proceso": "Pago devuelto",
  "commerce_group": "PAGOS",
  "site": "MLM",
  "periodo_p1": "Diciembre 2025",
  "periodo_p2": "Enero 2026",
  "total_conversaciones_p1": 30,
  "total_conversaciones_p2": 27,
  "causas": [
    {
      "causa": "Reembolso procesado pero no reflejado en cuenta bancaria",
      "descripcion": "Usuarios reportan que ML procesó el reembolso pero el dinero no aparece en su cuenta. ML indica que el banco debe acreditar.",
      "patron": "PERSISTENTE",
      "frecuencia_p1": 13,
      "porcentaje_p1": 43,
      "frecuencia_p2": 12,
      "porcentaje_p2": 44,
      "casos_estimados_variacion": -100,
      "variacion_pct": -8.4,
      "citas_p1": [
        {
          "case_id": "420196359",
          "fecha": "2025-12-02",
          "texto": "El usuario realizó una devolución..."
        }
      ],
      "citas_p2": [
        {
          "case_id": "430123456",
          "fecha": "2026-01-15",
          "texto": "La clienta no ha recibido el reembolso..."
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
    },
    {
      "causa": "Entregas críticas navideñas reprogramadas",
      "descripcion": "Regalos de Navidad reprogramados sin aviso, llegando después del 25 de diciembre.",
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
          "texto": "Mi regalo no llegó a tiempo..."
        }
      ],
      "sentimiento_p1": {},
      "sentimiento_p2": {
        "frustracion": 85,
        "satisfaccion": 5,
        "neutral": 10
      }
    }
  ],
  "cobertura_p1": 85,
  "cobertura_p2": 90,
  "hallazgo_principal": "La mayoría de casos (44%) involucran reembolsos procesados pero no reflejados. El segundo patrón (55% en Dic) son entregas navideñas reprogramadas sin aviso."
}
```

4. **Combinar todos los JSONs de elementos en un archivo:**

```json
{
  "Pago devuelto": {
    "proceso": "Pago devuelto",
    "causas": [ ... ]
  },
  "Pago pendiente": {
    "proceso": "Pago pendiente",
    "causas": [ ... ]
  },
  "Problemas con descuentos": {
    "proceso": "Problemas con descuentos",
    "causas": [ ... ]
  }
}
```

5. **Guardar como:**
   ```
   output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json
   ```

---

### FASE 4: Adaptar formato v3.0 → v2.0 (para compatibilidad con v6.3.6)

```bash
py scripts/adaptar_json_comparativo_v3_to_v2.py \
    --input output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json \
    --output output/analisis_conversaciones_comparativo_claude_mlm_pagos_2025-12_2026-01.json \
    --cuadro-dimension output/cuadro_cdu_mlm_202512.csv
```

**Este script:**
- Convierte formato v3.0 al formato esperado por v6.3.6
- Agrega `incoming_nov`, `incoming_dic` desde el cuadro CSV
- Separa `causas` en `causas_nov` y `causas_dic`

---

### FASE 5: Generar reporte HTML

```bash
py generar_reporte_cr_universal_v6.3.6.py \
    --site MLM \
    --commerce-group PAGOS \
    --p1-start 2025-12-01 --p1-end 2025-12-31 \
    --p2-start 2026-01-01 --p2-end 2026-01-31 \
    --aperturas CDU \
    --open-report
```

**Output:**
- `reporte_cr_pagos_mlm_dec_jan_2025_v6.3.html` (con análisis comparativo real)

---

## ✅ Validación de Calidad

### 1. Máximo 4-5 causas por elemento

```json
{
  "causas": [
    { "causa": "Causa 1" },  // ✅
    { "causa": "Causa 2" },  // ✅
    { "causa": "Causa 3" },  // ✅
    { "causa": "Causa 4" },  // ✅
    { "causa": "Causa 5" }   // ✅ (máximo)
  ]
}
```

❌ **Si hay más de 5 causas**, el análisis NO cumple con el estándar de calidad.

### 2. Patrones correctamente identificados

```json
{
  "patron": "PERSISTENTE",  // ✅ frecuencia_p1 > 0 Y frecuencia_p2 > 0
  "frecuencia_p1": 13,
  "frecuencia_p2": 12
}
```

```json
{
  "patron": "NUEVO",  // ✅ frecuencia_p1 = 0 Y frecuencia_p2 > 0
  "frecuencia_p1": 0,
  "frecuencia_p2": 16
}
```

```json
{
  "patron": "DESAPARECE",  // ✅ frecuencia_p1 > 0 Y frecuencia_p2 = 0
  "frecuencia_p1": 14,
  "frecuencia_p2": 0
}
```

### 3. Porcentajes reales (no proporcionales)

**✅ CORRECTO:**
```json
{
  "porcentaje_p1": 43,  // 13/30 conversaciones = 43%
  "frecuencia_p1": 13,
  "total_conversaciones_p1": 30
}
```

**❌ INCORRECTO (proporcional):**
```json
{
  "porcentaje_p1": 50,  // Asumido (casos totales / 2)
  "porcentaje_p2": 50   // Asumido
}
```

### 4. Citas separadas por período

**✅ CORRECTO:**
```json
{
  "citas_p1": [
    {
      "case_id": "420196359",
      "fecha": "2025-12-15",  // ✅ Fecha en P1
      "texto": "..."
    }
  ],
  "citas_p2": [
    {
      "case_id": "430123456",
      "fecha": "2026-01-20",  // ✅ Fecha en P2
      "texto": "..."
    }
  ]
}
```

**❌ INCORRECTO (fechas mezcladas):**
```json
{
  "citas_p1": [
    {
      "case_id": "425389526",
      "fecha": "2025-12-24",  // ✅ P1
      "texto": "..."
    },
    {
      "case_id": "430123456",
      "fecha": "2026-01-15",  // ❌ P2 (no debería estar en citas_p1)
      "texto": "..."
    }
  ]
}
```

---

## 🆚 Ejemplo Comparativo: v2.0 vs v3.0

### Caso: "Demoras en entrega sin información clara"

#### ❌ v2.0 (División Proporcional - PROBLEMÁTICO)

```json
{
  "Demoras en entrega sin información clara": {
    "causas_nov": [
      {
        "causa": "Demoras en entrega sin información clara",
        "porcentaje": 45,
        "casos_estimados": 4333  // ⚠️ Asumido proporcionalmente
      }
    ],
    "causas_dic": [
      {
        "causa": "Demoras en entrega sin información clara",
        "porcentaje": 45,
        "casos_estimados": 0  // ⚠️ Pero las citas son TODAS de dic
      }
    ]
  }
}
```

**Problema:** El análisis global detectó esta causa, pero al dividir proporcionalmente asume que existe en ambos períodos. Sin embargo, todas las citas son de diciembre, sugiriendo que es un patrón NUEVO.

#### ✅ v3.0 (Detección Real - CORRECTO)

```json
{
  "Demoras en entrega sin información clara": {
    "causas": [
      {
        "causa": "Demoras en entrega sin información clara",
        "patron": "NUEVO",  // ✅ Detectado como nuevo
        "frecuencia_p1": 0,  // ✅ 0 conversaciones en nov
        "porcentaje_p1": 0,
        "frecuencia_p2": 14,  // ✅ 14 conversaciones en dic
        "porcentaje_p2": 47,
        "citas_p1": [],  // ✅ Sin citas en nov
        "citas_p2": [
          {
            "case_id": "425389526",
            "fecha": "2025-12-24",
            "texto": "Mi entrega se demoró sin información..."
          }
        ]
      }
    ]
  }
}
```

**Resultado:** El análisis detecta correctamente que este patrón es NUEVO en diciembre (posiblemente por temporada navideña).

---

## 🎯 Ventajas del Enfoque v3.0

| Beneficio | Descripción |
|-----------|-------------|
| ✅ **Patrones reales** | Detecta si una causa es nueva, desaparece, o persiste |
| ✅ **Porcentajes reales** | Basados en frecuencias reales de conversaciones |
| ✅ **Máximo 4-5 causas** | Prioriza las causas con mayor impacto (calidad > cantidad) |
| ✅ **Citas correctas** | Separadas por período con fechas reales |
| ✅ **Sin sesgo proporcional** | Elimina el problema de dividir casos artificialmente |
| ✅ **Mayor confiabilidad** | Los hallazgos son validables con las conversaciones |

---

## 📋 Checklist de Validación

Antes de dar por válido un análisis comparativo v3.0, verificar:

- [ ] ✅ Máximo 4-5 causas por elemento
- [ ] ✅ Cada causa tiene patrón: PERSISTENTE / NUEVO / DESAPARECE
- [ ] ✅ Frecuencias reales: frecuencia_p1 y frecuencia_p2
- [ ] ✅ Porcentajes calculados: (frecuencia / total_conversaciones) × 100
- [ ] ✅ Citas separadas: citas_p1 con fechas de P1, citas_p2 con fechas de P2
- [ ] ✅ Si patrón = NUEVO → frecuencia_p1 = 0 y citas_p1 = []
- [ ] ✅ Si patrón = DESAPARECE → frecuencia_p2 = 0 y citas_p2 = []
- [ ] ✅ Cobertura ≥80% en cada período

---

## 🚨 Errores Comunes y Cómo Evitarlos

### Error 1: Más de 5 causas por elemento

**❌ Problema:**
```json
{
  "causas": [
    { "causa": "Causa 1" },
    { "causa": "Causa 2" },
    { "causa": "Causa 3" },
    { "causa": "Causa 4" },
    { "causa": "Causa 5" },
    { "causa": "Causa 6" },  // ❌ Excede el máximo
    { "causa": "Causa 7" }   // ❌ Excede el máximo
  ]
}
```

**✅ Solución:**
- Priorizar por `casos_estimados_variacion` (impacto)
- Agrupar causas menores en "Otros / Volumétrico"

### Error 2: Patrón inconsistente

**❌ Problema:**
```json
{
  "patron": "NUEVO",
  "frecuencia_p1": 5,  // ❌ Debería ser 0
  "frecuencia_p2": 16
}
```

**✅ Solución:**
- Si frecuencia_p1 > 0 Y frecuencia_p2 > 0 → PERSISTENTE
- Si frecuencia_p1 = 0 Y frecuencia_p2 > 0 → NUEVO
- Si frecuencia_p1 > 0 Y frecuencia_p2 = 0 → DESAPARECE

### Error 3: Citas con fechas incorrectas

**❌ Problema:**
```json
{
  "citas_p1": [
    {
      "case_id": "425389526",
      "fecha": "2026-01-15",  // ❌ Fecha de P2 en citas_p1
      "texto": "..."
    }
  ]
}
```

**✅ Solución:**
- Validar que fecha de cita_p1 esté en rango de P1
- Validar que fecha de cita_p2 esté en rango de P2

---

## 📚 Referencias

- **Template de prompt:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`
- **Script generador:** `scripts/generar_analisis_comparativo_directo.py`
- **Adaptador de formato:** `scripts/adaptar_json_comparativo_v3_to_v2.py`
- **Script de reporte:** `generar_reporte_cr_universal_v6.3.6.py`

---

## 🎓 Conclusión

El análisis comparativo **v3.0** garantiza:

1. **Patrones reales** detectados por el LLM (no asumidos)
2. **Máximo 4-5 causas** priorizadas por impacto
3. **Porcentajes reales** basados en frecuencias de conversaciones
4. **Citas validables** separadas por período con fechas reales

Esto elimina el sesgo de división proporcional del v2.0 y permite identificar correctamente:
- ✅ Patrones estacionales (NUEVO en dic: entregas navideñas)
- ✅ Patrones persistentes (PERSISTENTE: reembolsos no reflejados)
- ✅ Patrones resueltos (DESAPARECE: bugs corregidos)

---

**Versión:** 3.0
**Fecha:** Febrero 2026
**Status:** ✅ PRODUCTION READY
**Autor:** CR Commerce Analytics Team
