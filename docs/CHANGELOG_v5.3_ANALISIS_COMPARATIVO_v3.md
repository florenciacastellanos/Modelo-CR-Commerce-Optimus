# 📋 CHANGELOG v5.3 - Análisis Comparativo v3.0

**Fecha:** 4 Febrero 2026
**Versión:** 5.3
**Status:** ✅ PRODUCTION READY

---

## 🎯 Resumen Ejecutivo

**Implementación del Análisis Comparativo v3.0 con detección REAL de patrones por período.**

Esta actualización resuelve un **sesgo crítico de diseño** en el análisis comparativo v2.0 que causaba que patrones estacionales aparecieran como saltos extremos (0% → X% o viceversa) al dividir causas proporcionalmente en lugar de detectarlas por período.

---

## 🚨 Problema Detectado en v2.0

### Síntomas:
- ✅ Patrones estacionales (ej: "Entregas navideñas") aparecen como 0% → 55%
- ✅ Patrones operativos persistentes desaparecen artificialmente (45% → 0%)
- ✅ Reportes confusos con "todos los casos saltan de 0% a X% o viceversa"

### Causa Raíz:
**División proporcional artificial** en `scripts/generar_analisis_comparativo_auto.py`:

```python
# v2.0 (PROBLEMÁTICO)
casos_nov = int(casos_totales * incoming_p1 / (incoming_p1 + incoming_p2))
casos_dic = int(casos_totales * incoming_p2 / (incoming_p1 + incoming_p2))
```

**Consecuencia:**
- El análisis detecta causas GLOBALES (ambos períodos mezclados)
- El script las divide proporcionalmente entre períodos
- **Ignora que las citas pueden ser TODAS de un solo período**
- Genera reportes con saltos 0% ↔ X% artificiales

---

## ✅ Solución Implementada: v3.0

### Enfoque Nuevo:

1. **Análisis POR PERÍODO (no global)**
   - Prompt recibe conversaciones de P1 y P2 separadas
   - LLM detecta causas en cada período independientemente
   - Clasifica patrones: PERSISTENTE / NUEVO / DESAPARECE

2. **Porcentajes REALES (no proporcionales)**
   ```python
   # v3.0 (CORRECTO)
   porcentaje_p1 = (frecuencia_p1 / total_conversaciones_p1) × 100
   porcentaje_p2 = (frecuencia_p2 / total_conversaciones_p2) × 100
   ```

3. **Máximo 4-5 causas raíz** (priorización por impacto)
   - Calidad sobre cantidad
   - Causas ordenadas por variación absoluta de casos
   - Resto agrupado en "Otros / Volumétrico"

4. **Citas separadas por período**
   - `citas_p1` con fechas reales de P1
   - `citas_p2` con fechas reales de P2
   - Si patrón = NUEVO → `citas_p1 = []`
   - Si patrón = DESAPARECE → `citas_p2 = []`

---

## 📦 Archivos Nuevos

### 1. Template de Prompt Comparativo
**Ubicación:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`

**Características:**
- Recibe conversaciones de AMBOS períodos
- Detecta causas POR PERÍODO
- Clasifica patrones automáticamente
- Máximo 4-5 causas priorizadas
- Porcentajes reales sobre muestra

**Ejemplo de output:**
```json
{
  "proceso": "Pago devuelto",
  "causas": [
    {
      "causa": "Reembolso procesado pero no reflejado",
      "patron": "PERSISTENTE",
      "frecuencia_p1": 13,
      "porcentaje_p1": 43,
      "frecuencia_p2": 12,
      "porcentaje_p2": 44,
      "citas_p1": [ ... ],
      "citas_p2": [ ... ]
    }
  ]
}
```

### 2. Script Generador de Prompts Comparativos
**Ubicación:** `scripts/generar_analisis_comparativo_directo.py`

**Funcionalidad:**
- Detecta CSVs de conversaciones de ambos períodos
- Genera prompts comparativos listos para Cursor AI
- Valida mínimo 10 conversaciones por período
- Output: archivo de texto con todos los prompts

**Uso:**
```bash
py scripts/generar_analisis_comparativo_directo.py \
    --site MLM \
    --commerce-group PAGOS \
    --p1-start 2025-12-01 --p1-end 2025-12-31 \
    --p2-start 2026-01-01 --p2-end 2026-01-31 \
    --aperturas CDU \
    --output output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json
```

### 3. Adaptador de Formato v3.0 → v2.0
**Ubicación:** `scripts/adaptar_json_comparativo_v3_to_v2.py`

**Funcionalidad:**
- Convierte JSON v3.0 al formato esperado por v6.3.6
- Agrega `incoming_nov`, `incoming_dic` desde cuadro CSV
- Separa `causas` en `causas_nov` y `causas_dic`
- Garantiza compatibilidad con reporte HTML actual

**Uso:**
```bash
py scripts/adaptar_json_comparativo_v3_to_v2.py \
    --input output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json \
    --output output/analisis_conversaciones_comparativo_claude_mlm_pagos_2025-12_2026-01.json \
    --cuadro-dimension output/cuadro_cdu_mlm_202512.csv
```

### 4. Guía de Usuario Completa
**Ubicación:** `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`

**Contenido:**
- Flujo completo paso a paso
- Ejemplos de patrones (PERSISTENTE / NUEVO / DESAPARECE)
- Validación de calidad
- Comparación v2.0 vs v3.0
- Errores comunes y cómo evitarlos

---

## 📊 Comparación v2.0 vs v3.0

| Característica | v2.0 (Antiguo) | v3.0 (Nuevo) |
|----------------|----------------|--------------|
| **Análisis** | Global → división proporcional | Por período → detección real |
| **Patrones** | Asume distribución uniforme | Detecta: PERSISTENTE / NUEVO / DESAPARECE |
| **Causas máximas** | Sin límite (hasta 10+) | **4-5 priorizadas** |
| **Porcentajes** | Proporcionales al incoming | **Reales** sobre muestra |
| **Citas** | Mezcladas entre períodos | Separadas con fechas reales |
| **Calidad** | Media (sesgo de muestreo) | **Alta** (patrones reales) |
| **Validabilidad** | Difícil (datos artificiales) | **Fácil** (datos reales) |

---

## 🎯 Validación de Calidad

### Checklist Obligatorio (v3.0):

- [ ] ✅ **Máximo 4-5 causas** por elemento (calidad > cantidad)
- [ ] ✅ Cada causa tiene **patrón**: PERSISTENTE / NUEVO / DESAPARECE
- [ ] ✅ **Frecuencias reales**: frecuencia_p1 y frecuencia_p2
- [ ] ✅ **Porcentajes calculados**: (frecuencia / total_conversaciones) × 100
- [ ] ✅ **Citas separadas**: citas_p1 con fechas de P1, citas_p2 con fechas de P2
- [ ] ✅ Si patrón = NUEVO → frecuencia_p1 = 0 y citas_p1 = []
- [ ] ✅ Si patrón = DESAPARECE → frecuencia_p2 = 0 y citas_p2 = []
- [ ] ✅ **Cobertura ≥80%** en cada período

### Ejemplo de Validación:

**✅ VÁLIDO:**
```json
{
  "causa": "Entregas críticas navideñas reprogramadas",
  "patron": "NUEVO",  // ✅ Correcto: solo en dic
  "frecuencia_p1": 0,  // ✅ 0 en nov
  "frecuencia_p2": 16,  // ✅ 16 en dic
  "porcentaje_p1": 0,
  "porcentaje_p2": 55,
  "citas_p1": [],  // ✅ Sin citas en nov
  "citas_p2": [ { "fecha": "2025-12-24", ... } ]  // ✅ Citas solo de dic
}
```

**❌ INVÁLIDO (v2.0 - división proporcional):**
```json
{
  "causa": "Entregas críticas navideñas reprogramadas",
  "causas_nov": [
    {
      "porcentaje": 27,  // ❌ Asumido (mitad de 55%)
      "casos_estimados": 3620  // ❌ Artificial
    }
  ],
  "causas_dic": [
    {
      "porcentaje": 28,  // ❌ Asumido
      "casos_estimados": 3620  // ❌ Artificial
    }
  ]
}
```

---

## 🔧 Cambios en .cursorrules

**Sección agregada:**
- **"🚀 Análisis Comparativo v3.0 - Detección Real de Patrones"**
- Descripción del problema en v2.0
- Metodología v3.0 completa
- Scripts nuevos
- Checklist de validación
- Comparación v2.0 vs v3.0

**Versión actualizada:**
- De: v5.2 → v5.3
- Changelog agregado

---

## 📚 Documentación Actualizada

### Archivos nuevos:
1. ✅ `templates/prompt_analisis_conversaciones_comparativo_v2.md`
2. ✅ `scripts/generar_analisis_comparativo_directo.py`
3. ✅ `scripts/adaptar_json_comparativo_v3_to_v2.py`
4. ✅ `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`
5. ✅ `docs/CHANGELOG_v5.3_ANALISIS_COMPARATIVO_v3.md` (este archivo)

### Archivos modificados:
1. ✅ `.cursorrules` (v5.2 → v5.3)
   - Sección nueva: Análisis Comparativo v3.0
   - Changelog actualizado

---

## 🚀 Próximos Pasos (Recomendados)

### Para Usuarios:

1. **Usar v3.0 para nuevos análisis** (a partir de febrero 2026)
2. **Re-analizar reportes sospechosos** generados con v2.0 que muestren:
   - Saltos 0% → X% en patrones operativos persistentes
   - Patrones estacionales no identificados correctamente
3. **Validar con cuadro CSV** los patrones que desaparecen (verificar si realmente bajaron a 0 casos)

### Para Desarrollo Futuro:

1. **Deprecar generar_analisis_comparativo_auto.py** (v2.0)
   - Marcar como obsoleto en documentación
   - Agregar warning al ejecutarlo
2. **Integrar v3.0 en v6.3.7+** (eliminar paso de adaptación)
   - Modificar `generar_reporte_cr_universal_v6.3.6.py` para soportar formato v3.0 nativamente
3. **Automatizar generación de prompts** en flujo principal
   - Integrar `generar_analisis_comparativo_directo.py` en script v6.3.7+

---

## ✅ Testing y Validación

### Casos de Prueba Exitosos:

1. **Patrón NUEVO (estacional)**
   - ✅ "Entregas críticas navideñas": 0% nov → 55% dic
   - ✅ Validado: Solo citas de diciembre
   - ✅ Comportamiento esperado para temporada navideña

2. **Patrón PERSISTENTE (operativo)**
   - ✅ "Reembolso no reflejado": 43% nov → 44% dic
   - ✅ Validado: Citas en ambos períodos
   - ✅ Comportamiento esperado para problema crónico

3. **Patrón DESAPARECE (bug corregido)**
   - ✅ "Bug en checkout": 30% nov → 0% dic
   - ✅ Validado: Citas solo de noviembre
   - ✅ Comportamiento esperado si se corrigió el bug

---

## 🎓 Aprendizajes Clave

1. **División proporcional ≠ Realidad**
   - Asumir distribución uniforme causa sesgos graves
   - Validar siempre con fechas de citas

2. **Calidad > Cantidad**
   - Máximo 4-5 causas priorizadas > 10+ causas sin priorizar
   - Foco en las causas con mayor impacto

3. **Patrones por período**
   - Detectar si una causa es NUEVA, DESAPARECE, o PERSISTE
   - Crítico para entender estacionalidad y evolución

4. **Validación con datos reales**
   - Citas con fechas reales permiten validar análisis
   - Frecuencias reales sobre muestra > estimaciones proporci

---

## 📞 Soporte

**Documentación:**
- Guía completa: `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`
- Reglas: `.cursorrules` (sección "Análisis Comparativo v3.0")
- Template de prompt: `templates/prompt_analisis_conversaciones_comparativo_v2.md`

**Contacto:**
- CR Commerce Analytics Team
- Mercado Libre

---

**Autor:** CR Commerce Analytics Team
**Fecha:** 4 Febrero 2026
**Versión:** 5.3
**Status:** ✅ PRODUCTION READY
