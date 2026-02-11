# 📋 Templates - CR Analysis Framework v5.0

Este directorio contiene templates reutilizables para análisis de Contact Rate optimizado.

---

## 📁 Contenido

### 🔥 **prompt_analisis_conversaciones.md**
Template de prompt para análisis automatizado con LLM (GPT-4o-mini, Claude Sonnet, etc.)

**Uso:**
- Analiza conversaciones de atención al cliente
- Extrae causas raíz específicas con cobertura ≥80%
- Genera output estructurado en JSON
- Incluye citas textuales y sentimiento

**Tiempo:** ~30 segundos por proceso (vs 5 minutos manual)

**Referencias:**
- Inspirado en `docs/V37.ipynb` - función `analyze_conversations_with_gpt_v11()`
- Compatible con `.cursorrules` Regla #9 (v5.0)

---

## 🎯 Workflow Completo

```
1. Ejecutar query unificada (sql/templates/muestreo_unificado_template.sql)
   ↓
2. Obtener CSV con conversaciones de todos los procesos priorizados
   ↓
3. Dividir CSV por proceso
   ↓
4. Para cada proceso:
   - Formatear conversaciones según template
   - Aplicar prompt_analisis_conversaciones.md
   - Validar JSON output
   - Insertar en reporte HTML
   ↓
5. Reporte completo con evidencia cualitativa para cada elemento
```

---

## 📊 Beneficios

| Aspecto | Antes (v4.0) | Ahora (v5.0) | Mejora |
|---------|--------------|--------------|---------|
| **Tiempo (6 procesos)** | ~40 min | ~6 min | 85% ↓ |
| **Queries ejecutadas** | 6 queries | 1 query | 83% ↓ |
| **Análisis por proceso** | 5 min manual | 30s LLM | 90% ↓ |
| **Cobertura** | Variable | ≥80% garantizado | Consistente |
| **Citas textuales** | Manual | Automático | Escalable |
| **Validación CASE_IDs** | Manual | Automático | Sin errores |

---

## 🚀 Próximos Pasos

Si querés implementar análisis con estos templates:

1. **Lee:** `prompt_analisis_conversaciones.md`
2. **Revisa:** Ejemplo de uso completo al final del archivo
3. **Adapta:** Reemplaza placeholders según tu análisis
4. **Ejecuta:** Según workflow arriba

---

## 📚 Referencias

- **Reglas:** `.cursorrules` - Regla #9 (v5.0)
- **Query relacionada:** `sql/templates/muestreo_unificado_template.sql`
- **Notebook base:** `docs/V37.ipynb`
- **Documentación:** `docs/GOLDEN_TEMPLATES.md`

---

## 🆕 Changelog

### v5.0 (Enero 2026)
- ✅ Creación de templates optimizados
- ✅ Integración con análisis LLM
- ✅ Validación automática de outputs
- ✅ Reducción 85% en tiempo de análisis

---

**Versión:** v5.0  
**Última actualización:** Enero 2026  
**Autor:** CR Analysis Framework Team
