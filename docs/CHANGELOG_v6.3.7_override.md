# 📝 Changelog v6.3.7 - Override de Driver por Site

**Versión:** 6.3.7  
**Fecha:** 3 Febrero 2026  
**Tipo:** Feature - Flexibilidad de configuración  
**Status:** ✅ Implementado

---

## 🎯 Resumen

Implementación de modo **override opcional** para permitir filtrar drivers de Shipping por site, manteniendo el comportamiento por defecto (driver global) como estándar oficial.

---

## ✨ Nueva Funcionalidad

### Modo Override de Driver por Site (Shipping)

**Problema resuelto:**
- La regla oficial indica que drivers de Shipping deben ser GLOBALES
- Algunos análisis regionales requieren drivers filtrados por site específico
- No había forma de anular la regla sin modificar código

**Solución implementada:**
- ✅ **Por defecto:** Driver GLOBAL (comportamiento estándar, sin cambios)
- ✅ **Con flag `--filter-driver-by-site`:** Driver filtrado por site (requiere confirmación explícita)
- ✅ **Warning interactivo:** Solicita confirmación antes de aplicar override
- ✅ **Indicador visual:** Banner naranja en HTML cuando se usa override
- ✅ **Trazabilidad completa:** Footer indica claramente qué modo se usó

---

## 🔧 Cambios Técnicos

### 1. Nuevo Parámetro CLI

```bash
--filter-driver-by-site
```

**Características:**
- Tipo: `action='store_true'`
- Valor por defecto: `False`
- Solo aplica a commerce groups de Shipping (FBM_SELLERS, ME_PREDESPACHO, ME_DISTRIBUCION, ME_DRIVERS)
- Ignora silenciosamente para otras categorías

### 2. Validación con Warning Interactivo

Cuando se usa el flag con commerce groups de Shipping:

```
================================================================================
⚠️  WARNING: OVERRIDE DE REGLA OFICIAL
================================================================================

Estás solicitando filtrar el driver de Shipping por site.

📋 Regla oficial (docs/SHIPPING_DRIVERS.md):
   • Driver de Shipping debe ser GLOBAL (todos los sites)
   • Incoming se filtra por site específico

🔧 Con --filter-driver-by-site:
   • Driver: Será filtrado solo por MLB
   • ⚠️  Esto NO es el estándar oficial

================================================================================

¿Continuar con override? (y/n): _
```

**Opciones:**
- `y` → Aplica override, genera reporte con indicador visual
- `n` → Cancela override, usa driver global (estándar)

### 3. Modificación de Query

**Antes (v6.3.6):**
```sql
SELECT ...
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
-- Sin filtro de site (GLOBAL)
```

**Ahora (v6.3.7):**
```sql
SELECT ...
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
-- Filtro condicional:
AND drv.SIT_SITE_ID = 'MLB'  -- Solo si --filter-driver-by-site
```

### 4. Indicador Visual en HTML

**Banner de advertencia (solo cuando override activo):**

```html
<div class="warning-banner">
    <div class="icon">⚠️</div>
    <div class="text">
        <div class="title">MODO OVERRIDE ACTIVO: Driver Filtrado por Site</div>
        <div class="description">
            Este reporte usa driver de Shipping filtrado por MLB (no estándar).
            La regla oficial indica que el driver debe ser GLOBAL (todos los sites).
            Ver docs/SHIPPING_DRIVERS.md para más información.
        </div>
    </div>
</div>
```

**Estilos:**
- Color: Naranja (#ff9800)
- Posición: Justo después del header, antes del resumen ejecutivo
- Visible en primera pantalla

**Descripción del driver actualizada:**
```
Driver: OS_FULL (MLB únicamente) ⚠️ MODO OVERRIDE
```

### 5. Actualización de Documentación

**Archivos modificados:**
- `.cursorrules`: Sección ERROR 5 actualizada con información de override
- `docs/CHANGELOG_v6.3.7_override.md`: Este documento (nuevo)

---

## 📊 Ejemplos de Uso

### Caso 1: Comportamiento por Defecto (Sin Override)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --open-report
```

**Resultado:**
- ✅ Driver: GLOBAL (todos los sites)
- ✅ Sin warnings
- ✅ Sin banner naranja en HTML
- ✅ Footer: "Driver: OS_FULL (GLOBAL - todos los sites)"

---

### Caso 2: Con Override (Filtrado por Site)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --filter-driver-by-site \  # ← FLAG EXPLÍCITO
  --open-report
```

**Flujo:**
1. Script muestra warning de override
2. Solicita confirmación (y/n)
3. Si confirma "y":
   - ✅ Driver: Filtrado por MLB únicamente
   - ⚠️ Banner naranja visible en HTML
   - ⚠️ Footer: "Driver: OS_FULL (MLB únicamente) ⚠️ MODO OVERRIDE"
4. Si confirma "n":
   - ✅ Driver: GLOBAL (estándar)
   - ✅ Sin banner naranja

---

### Caso 3: Override en Commerce Group No-Shipping (Ignorado)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLA \
  --commerce-group PDD \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --filter-driver-by-site \  # ← Se ignora silenciosamente
  --open-report
```

**Resultado:**
- ✅ Driver: GLOBAL (BT_ORD_ORDERS sin filtro site)
- ✅ Sin warnings (PDD no es Shipping)
- ✅ Flag ignorado (no aplica a Post-Compra)

---

## ✅ Ventajas del Diseño

| Aspecto | Beneficio |
|---------|-----------|
| **Comportamiento por defecto** | ✅ Mantiene regla oficial automáticamente |
| **Flexibilidad** | ✅ Permite anular cuando hay razón válida |
| **Seguridad** | ✅ Requiere confirmación explícita (evita errores) |
| **Transparencia** | ✅ Warning visible + banner HTML |
| **Trazabilidad** | ✅ Queda registrado en reporte |
| **Sin romper nada** | ✅ Código existente funciona igual |
| **Documentación** | ✅ No contradice reglas actuales |

---

## 🚦 Reglas de Uso

### ✅ USAR Override Cuando:
- Análisis regional requiere comparar drivers locales vs globales
- Necesitas aislar el comportamiento de un site específico
- Hay razón de negocio documentada para filtrar por site
- El usuario solicita explícitamente este comportamiento

### ❌ NO USAR Override Si:
- No tienes razón específica (usar estándar global)
- Es un análisis de rutina siguiendo metodología oficial
- No estás seguro de por qué lo necesitas

---

## 📋 Checklist de Implementación

- [x] Agregar parámetro `--filter-driver-by-site` al CLI
- [x] Implementar validación con warning interactivo
- [x] Modificar generación de query de drivers (agregar filtro condicional)
- [x] Actualizar descripción de driver en logs y HTML
- [x] Agregar estilos CSS para banner de advertencia
- [x] Implementar banner naranja en HTML
- [x] Actualizar `.cursorrules` (sección ERROR 5)
- [x] Crear changelog (este documento)
- [ ] Actualizar `docs/GUIA_RAPIDA_v6.3.6.md` (pendiente)
- [ ] Testing con diferentes commerce groups de Shipping

---

## 🧪 Testing Recomendado

### Test 1: Override con FBM Sellers
```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO --filter-driver-by-site
```

**Verificar:**
- [ ] Warning aparece correctamente
- [ ] Confirmación funciona (y/n)
- [ ] Driver se filtra por MLB si confirma "y"
- [ ] Banner naranja visible en HTML
- [ ] Footer indica "MODO OVERRIDE"

### Test 2: Override con ME PreDespacho
```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLA --commerce-group ME_PREDESPACHO \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO --filter-driver-by-site
```

**Verificar:**
- [ ] Warning aparece correctamente
- [ ] Driver OS_WITHOUT_FBM se filtra por MLA si confirma

### Test 3: Sin Override (Comportamiento por Defecto)
```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO
```

**Verificar:**
- [ ] Sin warnings
- [ ] Driver GLOBAL (sin filtro site)
- [ ] Sin banner naranja en HTML
- [ ] Footer indica "GLOBAL - todos los sites"

### Test 4: Override en PDD (Debe Ignorarse)
```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLA --commerce-group PDD \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO --filter-driver-by-site
```

**Verificar:**
- [ ] Sin warnings (flag ignorado)
- [ ] Driver BT_ORD_ORDERS GLOBAL (estándar PDD)
- [ ] Sin banner naranja

---

## 🔗 Referencias

- **Script modificado:** `generar_reporte_cr_universal_v6.3.6.py`
- **Reglas actualizadas:** `.cursorrules` (sección ERROR 5)
- **Documentación oficial:** `docs/SHIPPING_DRIVERS.md`
- **Drivers por categoría:** `docs/DRIVERS_BY_CATEGORY.md`

---

## 📌 Notas Finales

- Esta funcionalidad NO cambia el comportamiento por defecto
- El estándar oficial sigue siendo driver GLOBAL para Shipping
- El override es una opción explícita para casos especiales
- Siempre requiere confirmación del usuario
- Queda claramente indicado en el reporte cuando se usa

---

**Versión:** 6.3.7  
**Status:** ✅ IMPLEMENTADO  
**Fecha:** 3 Febrero 2026  
**Autor:** Cursor AI + Flo Castellanos
