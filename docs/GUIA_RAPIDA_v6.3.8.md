# 🚀 Guía Rápida v6.3.8 - Análisis Separado por Período

**Versión:** 6.3.8  
**Fecha:** 4 Febrero 2026  
**Tiempo de lectura:** 3 minutos

---

## ⚡ Resumen Ejecutivo

**¿Qué cambió?**  
Ahora el análisis detecta cambios **REALES** de patrones entre períodos.

**¿Qué gano?**  
Porcentajes dinámicos que reflejan variaciones reales (no asume patrones constantes).

**¿Cambia mi flujo de trabajo?**  
No. Todo es automático. Solo necesitas ejecutar el script como siempre.

---

## 📋 Flujo de Trabajo (Igual que antes)

### **PASO 1: Ejecutar script**

```powershell
py generar_reporte_cr_universal_v6.3.6.py `
  --site MLM `
  --p1-start 2025-12-01 --p1-end 2025-12-31 `
  --p2-start 2026-01-01 --p2-end 2026-01-31 `
  --commerce-group PAGOS `
  --aperturas PROCESO `
  --open-report
```

### **PASO 2: El script exporta CSVs automáticamente**

```
[OK] conversaciones_reembolsos_mlm_p1_202512.csv (30 conversaciones)
[OK] conversaciones_reembolsos_mlm_p2_202601.csv (30 conversaciones)
[OK] conversaciones_cupones_mlm_p1_202512.csv (27 conversaciones)
[OK] conversaciones_cupones_mlm_p2_202601.csv (28 conversaciones)
```

### **PASO 3: El script muestra el prompt**

```
📊 ANÁLISIS DE CONVERSACIONES POR PERÍODO (v6.3.8 - Detección de Cambios)

[CURSOR AI] Analiza las conversaciones SEPARADAMENTE por período:

🔹 PASO 1: Analizar conversaciones de Dic 2025
   Archivos: conversaciones_*_p1_202512.csv
   Generar JSON: analisis_conversaciones_claude_mlm_pagos_proceso_p1_2025-12.json

🔹 PASO 2: Analizar conversaciones de Ene 2026
   Archivos: conversaciones_*_p2_202601.csv
   Generar JSON: analisis_conversaciones_claude_mlm_pagos_proceso_p2_2026-01.json

💡 PROMPT SUGERIDO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analiza las conversaciones de MLM - PAGOS SEPARADAS POR PERÍODO:

**PASO 1 - Análisis Dic 2025:**
1. Lee SOLO los CSVs con sufijo `_p1_202512.csv` 
2. Para cada elemento, identifica causas raíz, porcentajes, sentimiento y citas
3. Genera: `analisis_conversaciones_claude_mlm_pagos_proceso_p1_2025-12.json`

**PASO 2 - Análisis Ene 2026:**
1. Lee SOLO los CSVs con sufijo `_p2_202601.csv`
2. Para cada elemento, identifica causas raíz, porcentajes, sentimiento y citas  
3. Genera: `analisis_conversaciones_claude_mlm_pagos_proceso_p2_2026-01.json`
```

### **PASO 4: Copiar y pegar el prompt en Cursor AI**

Copiar el prompt del output y pegarlo en el chat de Cursor AI.

### **PASO 5: Cursor AI analiza automáticamente**

Cursor AI:
1. Lee los CSVs de P1 → Genera JSON P1
2. Lee los CSVs de P2 → Genera JSON P2

**Tiempo estimado:** 3-5 minutos por período

### **PASO 6: El script detecta automáticamente**

```
✅ [OK] JSON P1 detectado: analisis_conversaciones_claude_mlm_pagos_proceso_p1_2025-12.json
✅ [OK] JSON P2 detectado: analisis_conversaciones_claude_mlm_pagos_proceso_p2_2026-01.json
[CONTINUANDO] Generando análisis comparativo y reporte completo...

[AUTO-GEN] Usando análisis separados (v6.3.8 - detección de cambios de patrones)
[AUTO-GEN] ✅ Análisis comparativo generado: 7 elementos
[INFO] Porcentajes dinámicos por período (detecta cambios reales de patrones)

[HTML] Generando reporte HTML...
[OK] Reporte guardado: reporte_cr_pagos_mlm_dec_jan_2025_v6.3.html
🌐 Abriendo reporte en navegador...
```

### **PASO 7: El navegador se abre automáticamente**

¡Listo! El reporte tiene porcentajes dinámicos por período.

---

## 🎯 ¿Qué verás diferente en el reporte?

### **ANTES (v6.3.7):**

| Patrón / Causa Raíz | Diciembre 2025 | | Enero 2026 | |
|---------------------|----------------|---|------------|---|
| | % | Casos | % | Casos |
| Reembolso no reflejado | **45%** | 2,257 | **45%** | 1,510 |
| Confusión MP vs banco | **30%** | 1,505 | **30%** | 1,006 |

❌ Porcentajes iguales (no detecta cambios)

### **AHORA (v6.3.8):**

| Patrón / Causa Raíz | Diciembre 2025 | | Enero 2026 | | Δ |
|---------------------|----------------|---|------------|---|---|
| | % | Casos | % | Casos | |
| Reembolso no reflejado | **50%** | 2,500 | **35%** | 1,050 | **-15pp** |
| Confusión MP vs banco | **25%** | 1,250 | **40%** | 1,200 | **+15pp** |
| Errores técnicos | **10%** | 500 | **20%** | 600 | **+10pp** |

✅ Porcentajes diferentes (detecta cambios reales)  
✅ Nueva columna "Δ" muestra cambio en puntos porcentuales

---

## 💡 Casos de Uso

### **Caso 1: Detectar causa emergente**

```
ANTES: No podías ver que "Errores técnicos" pasó de 10% a 20%
AHORA: Columna Δ muestra +10pp → Causa emergente detectada
```

### **Caso 2: Validar mejora**

```
ANTES: No podías confirmar si "Reembolso no reflejado" disminuyó realmente
AHORA: % bajó de 50% a 35% → Mejora verificada con datos
```

### **Caso 3: Priorización de acciones**

```
ANTES: Todas las causas parecían estables
AHORA: Identificas cuáles están creciendo (prioridad alta) vs decreciendo (low priority)
```

---

## ❓ FAQ

### **¿Necesito cambiar algo en mi flujo?**

No. Todo es automático. Solo ejecutas el script y sigues las instrucciones.

### **¿Qué pasa si solo genero un JSON (P1 o P2)?**

El script espera ambos. Si falta uno, te lo indica y espera hasta que lo generes.

### **¿Puedo seguir usando análisis conjunto (legacy)?**

Sí. El script tiene fallback automático. Si detecta el JSON conjunto antiguo, lo usa (con warning de % estáticos).

### **¿Los análisis antiguos siguen funcionando?**

Sí. 100% retrocompatible. Tus análisis anteriores siguen funcionando sin cambios.

### **¿Cómo sé si mi reporte usa análisis separado?**

Verás este mensaje en el output:
```
[AUTO-GEN] Usando análisis separados (v6.3.8 - detección de cambios de patrones)
[INFO] Porcentajes dinámicos por período (detecta cambios reales de patrones)
```

### **¿Qué pasa si cambio de site o commerce group?**

El script genera nuevos JSONs automáticamente con nombres únicos. No hay conflictos.

---

## 🔧 Troubleshooting

### **Problema: El script no detecta los JSONs**

**Causa:** Nombres incorrectos de JSON

**Solución:** Verificar que los JSONs tengan EXACTAMENTE estos nombres:
```
analisis_conversaciones_claude_{site}_{cg}_{dim}_p1_{p1}.json
analisis_conversaciones_claude_{site}_{cg}_{dim}_p2_{p2}.json
```

**Ejemplo correcto:**
```
analisis_conversaciones_claude_mlm_pagos_proceso_p1_2025-12.json
analisis_conversaciones_claude_mlm_pagos_proceso_p2_2026-01.json
```

### **Problema: Cursor AI genera un solo JSON**

**Causa:** No seguiste el prompt paso a paso

**Solución:** Copiar el prompt completo y asegurarte de que Cursor AI:
1. Analiza P1 PRIMERO → Genera JSON P1
2. Analiza P2 DESPUÉS → Genera JSON P2

### **Problema: Porcentajes siguen siendo iguales**

**Causa:** El script está usando análisis conjunto legacy (fallback)

**Solución:** Verificar que AMBOS JSONs separados existan:
```powershell
ls output/analisis_conversaciones_claude_*_p1_*.json
ls output/analisis_conversaciones_claude_*_p2_*.json
```

Si falta alguno → Generar análisis separado siguiendo PASO 4-5

### **Problema: Error al generar análisis comparativo**

**Causa:** Falta el cuadro de dimensión

**Solución:** Verificar que existe:
```
output/cuadro_{dimension}_{site}_{periodo}.csv
```

Este archivo se genera automáticamente en PASO 1. Si falta, re-ejecutar el script.

---

## 🎓 Best Practices

### **✅ DO:**

- Ejecutar análisis separado para detectar cambios reales
- Revisar columna "Δ" para identificar tendencias
- Priorizar causas con Δ > +10pp (emergentes)
- Comparar sentimiento entre períodos

### **❌ DON'T:**

- No asumas que % iguales = patrón estable (puede ser legacy)
- No ignores la columna Δ (insight clave)
- No mezcles análisis de diferentes períodos en un solo JSON

---

## 📞 Soporte

**Documentación completa:** `docs/CHANGELOG_v6.3.8.md`

**Script de análisis comparativo:** `scripts/generar_analisis_comparativo_desde_separados.py`

**Reglas del agente:** `.cursorrules` (sección "v6.3.8")

---

**Versión:** 6.3.8  
**Status:** ✅ PRODUCTION READY  
**Última actualización:** 4 Febrero 2026
