# 🔧 Guía de Uso: Override de Driver por Site

**Versión:** 6.3.7  
**Fecha:** 3 Febrero 2026  
**Funcionalidad:** Override opcional de driver por site para Shipping

---

## 📋 Índice

1. [¿Qué es el Override?](#qué-es-el-override)
2. [¿Cuándo Usarlo?](#cuándo-usarlo)
3. [¿Cuándo NO Usarlo?](#cuándo-no-usarlo)
4. [Cómo Usar](#cómo-usar)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 ¿Qué es el Override?

El **override de driver por site** es una funcionalidad que permite **anular temporalmente** la regla oficial de drivers globales para commerce groups de **Shipping** (FBM Sellers, ME PreDespacho, ME Distribución, ME Drivers).

### Comportamiento Normal (Estándar Oficial)

**Por defecto**, los drivers de Shipping se calculan de forma **GLOBAL**:

```
Incoming: Solo casos de MLB (filtrado por site)
Driver: Órdenes de TODOS los sites (global)
CR: Tasa de contacto de MLB sobre universo global
```

**Ejemplo:**
- Incoming MLB: 10,000 casos
- Driver GLOBAL: 100,000,000 órdenes (todos los sites)
- CR: 0.0100 pp (10,000 / 100M × 100)

### Con Override Activo

Cuando se usa `--filter-driver-by-site`:

```
Incoming: Solo casos de MLB (filtrado por site)
Driver: Órdenes solo de MLB (filtrado por site) ← CAMBIO
CR: Tasa de contacto de MLB sobre su propio volumen
```

**Ejemplo:**
- Incoming MLB: 10,000 casos
- Driver MLB: 20,000,000 órdenes (solo MLB)
- CR: 0.0500 pp (10,000 / 20M × 100)

**⚠️ Nota:** El CR será diferente (generalmente más alto) cuando se filtra el driver por site.

---

## ✅ ¿Cuándo Usarlo?

### Casos Válidos

| Situación | Razón |
|-----------|-------|
| **Análisis regional comparativo** | Necesitas comparar CR "local" de MLB vs MLA usando drivers específicos de cada site |
| **Aislamiento de comportamiento** | Quieres entender el CR de un site sin el denominador del universo global |
| **Benchmarking interno** | Comparar eficiencia de diferentes sites en términos relativos a su volumen |
| **Solicitud explícita del usuario** | El usuario tiene razón documentada para usar este modo |

### Ejemplo de Caso Válido

**Pregunta de negocio:**
> "¿MLB tiene un CR más alto que MLA en FBM Sellers, cuando se compara cada site contra su propio volumen?"

**Análisis requerido:**
1. **MLB con override:**
   - Incoming: FBM Sellers MLB
   - Driver: Órdenes FBM solo de MLB
   - CR: X pp

2. **MLA con override:**
   - Incoming: FBM Sellers MLA
   - Driver: Órdenes FBM solo de MLA
   - CR: Y pp

3. **Comparar:** X pp vs Y pp (comparación "justa" por volumen local)

**En este caso, usar override es válido.**

---

## ❌ ¿Cuándo NO Usarlo?

### Casos NO Válidos

| Situación | Por Qué NO |
|-----------|------------|
| **Análisis de rutina** | La metodología oficial usa driver global |
| **Reportes estándar** | Mantener consistencia con reportes anteriores |
| **Sin razón específica** | "Por si acaso" no es una razón válida |
| **Comparación con reportes globales** | Los números no serán comparables |

### Ejemplo de Caso NO Válido

**Pregunta de negocio:**
> "¿Cómo varió el CR de FBM Sellers en MLB de Nov a Dic 2025?"

**Análisis requerido:**
- Incoming: FBM Sellers MLB (Nov vs Dic)
- Driver: **GLOBAL** (estándar oficial)
- CR: Variación estándar

**En este caso, NO usar override (usar comportamiento por defecto).**

---

## 🚀 Cómo Usar

### Paso 1: Construir el Comando Base

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO
```

**Este comando usa el comportamiento por defecto (driver global).**

### Paso 2: Agregar el Flag de Override

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --filter-driver-by-site  # ← AGREGAR ESTE FLAG
```

### Paso 3: Confirmar el Override

El script mostrará un warning:

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
- Escribe `y` y presiona Enter → Aplica override
- Escribe `n` y presiona Enter → Cancela override, usa driver global

### Paso 4: Verificar el Resultado

Si confirmaste el override, el reporte HTML mostrará:

**Banner naranja visible:**
```
⚠️ MODO OVERRIDE ACTIVO: Driver Filtrado por Site

Este reporte usa driver de Shipping filtrado por MLB (no estándar).
La regla oficial indica que el driver debe ser GLOBAL (todos los sites).
Ver docs/SHIPPING_DRIVERS.md para más información.
```

**Footer actualizado:**
```
Driver: OS_FULL (MLB únicamente) ⚠️ MODO OVERRIDE
```

---

## 📊 Ejemplos Prácticos

### Ejemplo 1: FBM Sellers MLB (Sin Override - Estándar)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --open-report
```

**Resultado esperado:**
- Incoming MLB: ~5,000 casos
- Driver GLOBAL: ~15,000,000 órdenes FBM (todos los sites)
- CR: ~0.0333 pp
- Sin banner naranja
- Footer: "Driver: OS_FULL (GLOBAL - todos los sites)"

---

### Ejemplo 2: FBM Sellers MLB (Con Override)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLB \
  --commerce-group FBM_SELLERS \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --filter-driver-by-site \
  --open-report
```

**Flujo:**
1. Script muestra warning
2. Usuario escribe "y" y confirma
3. Script ejecuta con driver filtrado

**Resultado esperado:**
- Incoming MLB: ~5,000 casos (mismo)
- Driver MLB: ~4,000,000 órdenes FBM (solo MLB)
- CR: ~0.1250 pp (más alto que sin override)
- Banner naranja visible
- Footer: "Driver: OS_FULL (MLB únicamente) ⚠️ MODO OVERRIDE"

---

### Ejemplo 3: ME PreDespacho MLA (Con Override)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLA \
  --commerce-group ME_PREDESPACHO \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas CDU,TIPIFICACION \
  --filter-driver-by-site \
  --open-report
```

**Resultado esperado:**
- Driver: OS_WITHOUT_FBM (MLA únicamente)
- Banner naranja visible
- Footer: "Driver: OS_WITHOUT_FBM (MLA únicamente) ⚠️ MODO OVERRIDE"

---

### Ejemplo 4: PDD (Override Ignorado)

```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site MLA \
  --commerce-group PDD \
  --p1-start 2025-11-01 --p1-end 2025-11-30 \
  --p2-start 2025-12-01 --p2-end 2025-12-31 \
  --aperturas PROCESO \
  --filter-driver-by-site \  # ← Se ignora (PDD no es Shipping)
  --open-report
```

**Resultado:**
- Sin warnings (flag se ignora)
- Driver: BT_ORD_ORDERS GLOBAL (comportamiento estándar de PDD)
- Sin banner naranja
- Footer: "Driver: Órdenes totales GLOBALES"

---

## ❓ Preguntas Frecuentes

### 1. ¿Por qué necesito confirmar con "y/n"?

**Respuesta:** Para evitar usar el override accidentalmente. Es una medida de seguridad que garantiza que el usuario entiende que está anulando la regla oficial.

---

### 2. ¿Qué pasa si confirmo "n"?

**Respuesta:** El script ignora el flag `--filter-driver-by-site` y usa el driver GLOBAL (estándar oficial). Es como si nunca hubieras agregado el flag.

---

### 3. ¿El override cambia el incoming?

**Respuesta:** **NO.** El incoming siempre se filtra por el site especificado (ej: MLB). El override solo afecta el **driver** (denominador del CR).

---

### 4. ¿Puedo usar override en PDD o PNR?

**Respuesta:** Puedes agregar el flag, pero se ignora. El override solo aplica a commerce groups de **Shipping** (FBM Sellers, ME PreDespacho, ME Distribución, ME Drivers).

---

### 5. ¿El CR será diferente con override?

**Respuesta:** **Sí, generalmente será más alto.** Al filtrar el driver por site, reduces el denominador, lo que aumenta el CR.

**Ejemplo:**
- Sin override: CR = 10,000 / 100,000,000 × 100 = 0.0100 pp
- Con override: CR = 10,000 / 20,000,000 × 100 = 0.0500 pp

---

### 6. ¿Cómo sé si un reporte usó override?

**Respuesta:** Hay 3 indicadores:

1. **Banner naranja** en la parte superior del HTML
2. **Footer** indica "⚠️ MODO OVERRIDE"
3. **Descripción del driver** incluye "(site únicamente)"

---

### 7. ¿Puedo comparar reportes con y sin override?

**Respuesta:** **NO directamente.** Los números no son comparables porque usan denominadores diferentes. Si necesitas comparar, genera ambos reportes y analiza las diferencias.

---

### 8. ¿Qué pasa si ejecuto el script sin terminal interactiva?

**Respuesta:** Si el script detecta que no puede solicitar confirmación (ej: ejecución automatizada), el override se **cancela automáticamente** y usa driver global.

---

### 9. ¿El override afecta el análisis de conversaciones?

**Respuesta:** **NO.** El análisis de conversaciones es independiente del cálculo del driver. Solo afecta las métricas cuantitativas (CR, Driver P1/P2).

---

### 10. ¿Debo documentar por qué usé override?

**Respuesta:** **Sí, es recomendable.** Agrega un comentario en el reporte o en tus notas explicando la razón de negocio para usar el override.

---

## 📚 Referencias

- **Script:** `generar_reporte_cr_universal_v6.3.6.py`
- **Changelog:** `docs/CHANGELOG_v6.3.7_override.md`
- **Reglas oficiales:** `.cursorrules` (sección ERROR 5)
- **Drivers de Shipping:** `docs/SHIPPING_DRIVERS.md`
- **Drivers por categoría:** `docs/DRIVERS_BY_CATEGORY.md`

---

## 🎯 Resumen Ejecutivo

| Aspecto | Detalle |
|---------|---------|
| **¿Qué hace?** | Permite filtrar driver de Shipping por site específico |
| **¿Cuándo usar?** | Análisis regionales, benchmarking interno, casos especiales |
| **¿Cuándo NO usar?** | Análisis de rutina, reportes estándar, sin razón específica |
| **¿Cómo activar?** | Agregar `--filter-driver-by-site` al comando |
| **¿Requiere confirmación?** | Sí, interactiva (y/n) |
| **¿Cómo identificarlo?** | Banner naranja + footer con "⚠️ MODO OVERRIDE" |
| **¿Afecta incoming?** | No, solo el driver |
| **¿Cambia el CR?** | Sí, generalmente será más alto |

---

**Versión:** 6.3.7  
**Fecha:** 3 Febrero 2026  
**Status:** ✅ Documentado
