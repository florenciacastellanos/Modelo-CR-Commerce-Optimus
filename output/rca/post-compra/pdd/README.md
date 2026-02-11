# 📊 Reportes PDD - Commerce Post-Compra

**Commerce Group:** PDD (Producto Dañado/Defectuoso)  
**Categoría:** Post-Compra

---

## ⚠️ IMPORTANTE - Actualización Enero 2026

Los **Golden Templates v3.9/v4.0** fueron **deprecados** y reemplazados por el **Template Universal v6.2**.

**Reportes históricos:** Movidos a `archive/`

---

## ✅ GENERAR REPORTES NUEVOS

**USAR EXCLUSIVAMENTE:**

```bash
python generar_reporte_cr_universal_v6.2.py \
    --site [MLA|MLB|MLC|MCO|etc.] \
    --p1-start [FECHA] --p1-end [FECHA] \
    --p2-start [FECHA] --p2-end [FECHA] \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

**Ejemplo para MLA Nov-Dic 2025:**
```bash
python generar_reporte_cr_universal_v6.2.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

**Output:** Reporte con estructura Golden Template + features v6.2

---

## 📦 Reportes Históricos (Archivados)

Los siguientes reportes fueron generados con Golden Templates antiguos y están en `archive/`:

| Archivo | Versión | Site | Período |
|---------|---------|------|---------|
| `golden-pdd-mla-nov-dic-2025-tipificacion.html` | v4.0 | MLA | Nov-Dic 2025 |
| `golden-pdd-mlb-nov-dic-2025-tipificacion.html` | v3.9 | MLB | Nov-Dic 2025 |
| `golden-pdd-mla-nov-dic-2025.html` | v3.9 | MLA | Nov-Dic 2025 |

**⚠️ NO USAR PARA PRODUCCIÓN** - Solo referencia histórica

---

## 🎯 Características del Template Universal v6.2

El nuevo template incluye **todo lo de los Golden Templates v3.9/v4.0** y más:

| Feature | Golden v3.9/v4.0 | Template Universal v6.2 |
|---------|------------------|-------------------------|
| **Parametrización** | ❌ Fechas hardcoded | ✅ CLI completo |
| **Hard metrics** | ⚠️ Solo v4.0 | ✅ Sí (con fallback) |
| **Análisis LLM** | ❌ Keywords manuales | ✅ Claude (Cursor AI) |
| **Eventos dinámicos** | ❌ Hardcoded | ✅ Tabla oficial |
| **Resumen ejecutivo** | ❌ No | ✅ 3 bullets estructurados |
| **Múltiples dimensiones** | ❌ 1 dimensión | ✅ 7 dimensiones en 1 reporte |
| **Metadata técnica** | ⚠️ Básica | ✅ Completa (queries ejecutadas) |
| **Estructura HTML** | ✅ 6-8 cards | ✅ 8 cards + más features |

---

## 📚 Documentación

**Para generar reportes:**
- **Guía completa:** `docs/GOLDEN_TEMPLATES.md` (Template Universal v6.2)
- **Ejemplos:** `ejemplos/ejecutar_reporte_pdd_mla.ps1`
- **README principal:** `README.md` (raíz del repositorio)

**Para entender Golden Templates antiguos:**
- **Archivos en:** `archive/`
- **Scripts antiguos en:** `_archived_templates/`

---

## 🔄 Migración de Golden Templates v3.9/v4.0

Si anteriormente usabas:
```bash
python generar_golden_pdd_mla_tipificacion.py
```

**Ahora usa:**
```bash
python generar_reporte_cr_universal_v6.2.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

**Beneficios:**
- ✅ Mismo output (estructura Golden Template)
- ✅ Más features (LLM analysis, eventos dinámicos, resumen ejecutivo)
- ✅ Parametrización completa (cualquier site/período/dimensión)
- ✅ Hard metrics con fallback automático

---

**Última actualización:** 30 de Enero de 2026  
**Status:** ✅ Migrado a Template Universal v6.2  
**Template oficial:** `generar_reporte_cr_universal_v6.2.py` (raíz)
