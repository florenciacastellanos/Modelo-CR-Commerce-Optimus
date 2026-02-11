# 📚 Documentación v6.3.8 - Análisis Separado por Período

**Versión:** 6.3.8  
**Fecha:** 4 Febrero 2026  
**Status:** ✅ PRODUCTION READY

---

## 🎯 ¿Qué es v6.3.8?

**Mejora principal:** Análisis separado por período para detectar cambios REALES de patrones.

**Problema resuelto:** Los porcentajes ya no son iguales en ambos períodos (antes asumían patrones constantes).

**Beneficio clave:** Detectas qué causas están creciendo (prioridad alta) vs disminuyendo (low priority).

---

## 📖 Documentación Disponible

### **1. Resumen Ejecutivo (EMPEZAR ACÁ)**

**Archivo:** [`RESUMEN_EJECUTIVO_v6.3.8.md`](./RESUMEN_EJECUTIVO_v6.3.8.md)

**Contenido:**
- Explicación en pocas palabras
- Ejemplo real con datos
- Impacto en el negocio
- Comparación técnica v6.3.7 vs v6.3.8

**Para quién:** Managers, analistas, cualquiera que quiera entender el cambio

**Tiempo de lectura:** 5 minutos

---

### **2. Guía Rápida de Uso**

**Archivo:** [`GUIA_RAPIDA_v6.3.8.md`](./GUIA_RAPIDA_v6.3.8.md)

**Contenido:**
- Flujo de trabajo paso a paso
- Qué verás diferente en el reporte
- Casos de uso prácticos
- FAQ y troubleshooting

**Para quién:** Analistas que ejecutan el script

**Tiempo de lectura:** 3 minutos

---

### **3. Changelog Técnico Completo**

**Archivo:** [`CHANGELOG_v6.3.8.md`](./CHANGELOG_v6.3.8.md)

**Contenido:**
- Cambios técnicos detallados
- Archivos modificados (líneas específicas)
- Nuevos scripts creados
- Testing y validaciones

**Para quién:** Desarrolladores, mantenedores del código

**Tiempo de lectura:** 15 minutos

---

## 🚀 Quick Start

### **Uso Básico (3 pasos)**

**1. Ejecutar script:**
```powershell
py generar_reporte_cr_universal_v6.3.6.py `
  --site MLM `
  --p1-start 2025-12-01 --p1-end 2025-12-31 `
  --p2-start 2026-01-01 --p2-end 2026-01-31 `
  --commerce-group PAGOS `
  --aperturas PROCESO `
  --open-report
```

**2. Copiar prompt del terminal:**

El script muestra automáticamente el prompt para analizar con Cursor AI.

**3. Pegar en Cursor AI y esperar:**

Cursor AI analiza P1 y P2 → Script detecta automáticamente → Genera reporte

**Resultado:** Reporte HTML con porcentajes dinámicos por período

---

## 📊 Ejemplo de Output

### **Tabla Comparativa (v6.3.8)**

| Patrón / Causa Raíz | Diciembre 2025 | | Enero 2026 | | **Δ** |
|---------------------|----------------|---|------------|---|-------|
| | % | Casos | % | Casos | |
| Errores técnicos | 20% | 1,026 | **45%** | 1,805 | **+25pp** 🚨 |
| Cupones inválidos | 35% | 1,794 | **25%** | 1,003 | **-10pp** ✅ |
| Gift cards | 25% | 1,282 | **15%** | 602 | **-10pp** ✅ |

**Insight clave:** Errores técnicos crecieron +25pp → Prioridad crítica

---

## 🔄 Comparación con Versión Anterior

| Aspecto | v6.3.7 (Legacy) | v6.3.8 (Nuevo) |
|---------|-----------------|----------------|
| **Porcentajes** | Iguales en ambos períodos | Diferentes (reales) |
| **Detecta cambios** | ❌ No | ✅ Sí |
| **Columna Δ** | ❌ No | ✅ Sí |
| **Causas emergentes** | ❌ No identifica | ✅ Identifica |
| **Validación mejoras** | ⚠️ No concluyente | ✅ Concluyente |
| **Flujo trabajo** | Igual | Igual (automático) |

---

## ❓ FAQ Rápido

### **¿Cambió algo en mi flujo de trabajo?**

No. Ejecutas el script igual que antes. Todo es automático.

### **¿Qué es la columna Δ?**

Cambio en puntos porcentuales entre períodos.  
Ejemplo: +25pp = aumentó 25 puntos porcentuales.

### **¿Cómo sé si mi reporte usa análisis separado?**

Verás este mensaje:
```
[AUTO-GEN] Usando análisis separados (v6.3.8 - detección de cambios de patrones)
```

### **¿Los reportes antiguos siguen funcionando?**

Sí. 100% retrocompatible. Fallback automático a legacy si es necesario.

### **¿Qué pasa si solo genero un JSON?**

El script espera ambos (P1 y P2). Te indica cuál falta y espera hasta que lo generes.

---

## 📁 Estructura de Archivos

### **Scripts Principales:**

```
generar_reporte_cr_universal_v6.3.6.py (v6.3.8)
  ├── Exporta CSVs separados (P1 y P2)
  ├── Espera análisis automáticamente
  ├── Detecta JSONs separados
  └── Genera reporte HTML

scripts/generar_analisis_comparativo_desde_separados.py (nuevo)
  ├── Lee JSON P1 y JSON P2
  ├── Calcula porcentajes dinámicos
  └── Genera análisis comparativo con Δ
```

### **Documentación:**

```
docs/
  ├── README_v6.3.8.md (este archivo)
  ├── RESUMEN_EJECUTIVO_v6.3.8.md
  ├── GUIA_RAPIDA_v6.3.8.md
  └── CHANGELOG_v6.3.8.md
```

### **Output Generado:**

```
output/
  ├── conversaciones_*_p1_{periodo}.csv (nuevo)
  ├── conversaciones_*_p2_{periodo}.csv (nuevo)
  ├── analisis_conversaciones_claude_*_p1_*.json (nuevo)
  ├── analisis_conversaciones_claude_*_p2_*.json (nuevo)
  ├── analisis_conversaciones_comparativo_*.json (mejorado)
  └── reporte_cr_*_v6.3.html
```

---

## 🎓 Mejores Prácticas

### **✅ DO:**

- Ejecutar análisis separado para todos los reportes nuevos
- Revisar columna Δ para identificar tendencias
- Priorizar causas con Δ > +10pp (emergentes)
- Validar mejoras con Δ < -10pp (mejoras verificadas)

### **❌ DON'T:**

- No ignorar la columna Δ (es el insight clave)
- No asumir que % iguales = patrón estable (puede ser legacy)
- No mezclar análisis de diferentes períodos en un solo JSON

---

## 🔧 Troubleshooting

### **Problema: Porcentajes siguen siendo iguales**

**Causa:** Script está usando análisis conjunto legacy (fallback)

**Solución:** Verificar que existan AMBOS JSONs separados:
```powershell
ls output/analisis_conversaciones_claude_*_p1_*.json
ls output/analisis_conversaciones_claude_*_p2_*.json
```

### **Problema: Script no detecta los JSONs**

**Causa:** Nombres incorrectos

**Solución:** Verificar nombres exactos en el output del script:
```
[HINT] Crear JSONs:
       - analisis_conversaciones_claude_{site}_{cg}_{dim}_p1_{p1}.json
       - analisis_conversaciones_claude_{site}_{cg}_{dim}_p2_{p2}.json
```

### **Problema: Cursor AI genera un solo JSON**

**Causa:** No seguiste el prompt paso a paso

**Solución:** Copiar el prompt completo del terminal y asegurarte de analizar:
1. PASO 1: P1 → Genera JSON P1
2. PASO 2: P2 → Genera JSON P2

---

## 📞 Recursos Adicionales

### **Reglas del Agente:**

Archivo: `.cursorrules`

Sección: "v6.3.8 - Análisis Separado por Período"

### **Templates:**

- Prompt de análisis: En output del script (automático)
- Formato JSON: `docs/GUIA_RAPIDA_v6.3.8.md` (sección "PASO 3")

### **Testing:**

Casos de prueba: `docs/CHANGELOG_v6.3.8.md` (sección "Testing")

---

## 🏆 Casos de Éxito

### **Caso 1: Detección de Causa Emergente**

**Antes:** No detectamos que "Errores de pago" pasó de 10% a 35%  
**Después:** Δ +25pp alertó al equipo → Fix implementado en 24h

### **Caso 2: Validación de Mejora**

**Antes:** Manager pregunta "¿Funcionó el fix?" → No podíamos confirmar  
**Después:** Δ -15pp confirma mejora → ROI validado

### **Caso 3: Priorización Objetiva**

**Antes:** Revisión general de todos los temas (sin prioridad)  
**Después:** Priorización basada en Δ (foco en +25pp crítico)

---

## 📈 Roadmap

### **v6.3.8 (Actual):**

✅ Análisis separado por período  
✅ Porcentajes dinámicos  
✅ Columna Δ en reporte  
✅ Detección de causas emergentes

### **v6.4.0 (Futuro):**

🔜 Alertas automáticas por Δ > +15pp  
🔜 Gráfico de tendencias por causa  
🔜 Comparación multi-período (3+ períodos)  
🔜 Export a dashboard interactivo

---

## ✅ Checklist de Implementación

**Para empezar a usar v6.3.8:**

- [ ] Leer Resumen Ejecutivo (5 min)
- [ ] Leer Guía Rápida (3 min)
- [ ] Ejecutar script con ejemplo de prueba
- [ ] Verificar que genera CSVs separados (P1 y P2)
- [ ] Copiar prompt y pegar en Cursor AI
- [ ] Verificar que genera 2 JSONs separados
- [ ] Abrir reporte y verificar columna Δ
- [ ] Validar que porcentajes son diferentes entre períodos

**Listo!** Ahora tienes análisis de excelencia con detección de cambios reales.

---

## 📧 Contacto

**Equipo:** CR Commerce Analytics Team  
**Repositorio:** CR COMMERCE - Repo final mvp  
**Documentación:** `docs/`  
**Scripts:** `scripts/`

---

**Última actualización:** 4 Febrero 2026  
**Versión:** 6.3.8  
**Status:** ✅ PRODUCTION READY
