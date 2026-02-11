# 🏢 Fuente de Datos - Verticales y Dominios

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Propósito:** Explicar qué son verticales y dominios, su origen y cómo usarlos en análisis de CR

---

> ## ⚠️ IMPORTANTE - Sobre los Ejemplos en este Documento
> 
> Los ejemplos de verticales y dominios en este documento (ELECTRONICS, HOME & INDUSTRY, GROCERIES, etc.) son **SOLO ILUSTRATIVOS** para explicar el concepto.
> 
> **El análisis real:**
> - ✅ Obtiene las verticales **directamente de BigQuery** (`DM_CX_POST_PURCHASE.VERTICAL`)
> - ✅ **NO asume** ni filtra valores específicos
> - ✅ **NO hardcodea** verticales o dominios
> - ✅ Usa **exactamente lo que devuelva la tabla**, sin inventar ni sesgar
> 
> **Si la tabla devuelve verticales con nombres diferentes, esos son los que se usan en el análisis.**

---

## 🎯 ¿Qué son Verticales y Dominios?

### **Verticales**

Agrupaciones de **categorías de productos de alto nivel** que clasifican el catálogo de Mercado Libre.

**Características:**
- Nivel 1 de jerarquía de productos
- Cobertura amplia (por ejemplo: todo lo relacionado con hogar)
- Usado para análisis estratégico de categorías

**Ejemplos reales:**

| Vertical | Descripción |
|----------|-------------|
| `HOME & INDUSTRY` | Productos para hogar, construcción, industria |
| `ELECTRONICS` | Electrónica, computación, audio/video |
| `TOYS_AND_BABIES` | Juguetes, artículos para bebés |
| `FASHION` | Ropa, calzado, accesorios |
| `GROCERIES` | Alimentos, bebidas, supermercado |
| `SPORTS_AND_FITNESS` | Deportes, fitness, aire libre |
| `HEALTH` | Salud, belleza, cuidado personal |
| `AUTOMOTIVE` | Vehículos, repuestos, accesorios |

> **⚠️ RECORDATORIO:** Estos son **ejemplos ilustrativos** para entender el concepto. Los valores reales se obtienen dinámicamente de BigQuery sin asumir estos nombres específicos.

---

### **Dominios**

**Subcategorías dentro de cada vertical** (nivel 2 de granularidad).

**Características:**
- Más específico que vertical
- Un dominio pertenece a una única vertical
- Útil para identificar productos concretos problemáticos

**Ejemplos dentro de HOME & INDUSTRY:**

| Dominio | Descripción |
|---------|-------------|
| `DOOR_PEEPHOLES_AND_VIEWERS` | Mirillas para puertas |
| `ELECTRIC_FENCE_POSTS` | Postes para cerco eléctrico |
| `ROOF_TILES` | Tejas para techo |
| `POWER_TOOLS` | Herramientas eléctricas |
| `LIGHTING` | Iluminación |

**Ejemplos dentro de ELECTRONICS:**

| Dominio | Descripción |
|---------|-------------|
| `SMARTPHONES` | Teléfonos inteligentes |
| `LAPTOPS` | Computadoras portátiles |
| `TELEVISIONS` | Televisores |
| `HEADPHONES` | Auriculares |
| `GAMING_CONSOLES` | Consolas de videojuegos |

> **⚠️ RECORDATORIO:** Estos son **ejemplos ilustrativos**. Los valores reales se obtienen dinámicamente de BigQuery.

---

## 📊 Fuente de Datos

### **Tabla oficial:**

```sql
meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE
```

### **Campos relevantes:**

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `CLA_CLAIM_ID` | INT64 | ID del caso (join key) | 12345678 |
| `VERTICAL` | STRING | Vertical del producto | 'HOME & INDUSTRY' |
| `DOM_DOMAIN_AGG1` | STRING | Dominio agregado nivel 1 | 'DOOR_PEEPHOLES_AND_VIEWERS' |

### **Join con Contacts:**

```sql
SELECT 
    C.CLA_CLAIM_ID,
    C.SIT_SITE_ID,
    C.CONTACT_DATE_ID,
    C.PROCESS_PROBLEMATIC_REPORTING,
    PP.VERTICAL,
    PP.DOM_DOMAIN_AGG1,
    -- otros campos...
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP 
    ON PP.CLA_CLAIM_ID = C.CLA_CLAIM_ID
WHERE 
    -- Filtros normales de CR
    C.FLAG_EXCLUDE_NUMERATOR_CR = 0
    AND C.SIT_SITE_ID NOT IN ('MLV')
    -- otros filtros...
```

---

## ⚠️ Alcance y Restricciones

### **✅ APLICA SOLO PARA:**

- **PDD** (Post-Delivery Disputes)
- **PNR** (Payment Not Received)

**Motivo:** Solo estos commerce groups tienen casos asociados a **órdenes con productos**.

### **❌ NO APLICA PARA:**

- Shipping (ME PreDespacho, ME Distribución, etc.)
- Marketplace (Ventas y Publicaciones, etc.)
- Pagos (Problemas de Pago)
- Cuenta (Seguridad de Cuenta, etc.)

**Motivo:** Estos commerce groups no tienen productos asociados o el análisis por vertical no es relevante.

---

## 🎯 Casos de Uso

### **1. Detección de Problemas Específicos de Categoría**

**Objetivo:** Identificar si el incremento de CR está concentrado en una vertical específica.

**Ejemplo real:**
```
Análisis: PDD MLA Nov → Dic 2025
- CR total: +0.15 pp (+8%)
- GROCERIES: +0.45 pp (+35%) ← ALERTA
- Resto de verticales: +0.05 pp (+3%)

Acción: Investigar si hubo recall de alimentos o problema de calidad en GROCERIES.
```

**Pregunta clave:** ¿El problema es de toda la operación o de una categoría específica?

---

### **2. Correlación con Eventos Comerciales**

**Objetivo:** Asociar variaciones con eventos y validar si son esperadas o anómalas.

**Ejemplos esperados (estacionales):**

| Vertical | Época | Evento | Comportamiento |
|----------|-------|--------|----------------|
| `TOYS_AND_BABIES` | Diciembre | Navidad/Reyes | ✅ Incremento esperado |
| `ELECTRONICS` | Noviembre | Black Friday | ✅ Incremento esperado |
| `GROCERIES` | Diciembre | Fiestas | ✅ Incremento esperado |
| `FASHION` | Cambios estación | Liquidaciones | ✅ Incremento esperado |

**Ejemplos anómalos (requieren investigación):**

| Vertical | Situación | Posible Causa |
|----------|-----------|---------------|
| `GROCERIES` | Pico puntual fuera de temporada | Contaminación/recall de producto |
| `HEALTH` | Incremento sostenido | Problema con medicamentos/cosméticos |
| `AUTOMOTIVE` | Pico específico | Defecto en lote de repuestos |
| `ELECTRONICS` | Incremento fuera de Black Friday | Problema de calidad en modelo específico |

**Pregunta clave:** ¿El incremento es estacional o hay un problema real?

---

### **3. Priorización de Acciones**

**Objetivo:** Enfocar recursos en verticales con mayor impacto.

**Criterio:**
- Top 5 verticales con mayor variación absoluta
- O verticales con variación >10% respecto período anterior
- O picos puntuales detectados (>1.5 × desviación estándar)

**Output esperado en reporte:**

```markdown
## ⚠️ VERTICALES DESTACADAS

### 1. GROCERIES (+450 casos, +35%)
- **Incoming P1:** 1,245 casos
- **Incoming P2:** 1,695 casos
- **Correlación eventos:** 20% en fechas navideñas
- **Dominios más afectados:**
  - BEVERAGES: +180 casos (+40%)
  - SNACKS: +120 casos (+32%)

**Hipótesis:** Incremento esperado por temporada + posible problema de calidad en BEVERAGES.

### 2. ELECTRONICS (+320 casos, +18%)
- **Incoming P1:** 1,780 casos
- **Incoming P2:** 2,100 casos
- **Correlación eventos:** 45% en Black Friday
- **Dominios más afectados:**
  - SMARTPHONES: +200 casos (+25%)
  - HEADPHONES: +80 casos (+15%)

**Hipótesis:** Incremento estacional por Black Friday (comportamiento esperado).
```

---

## 📋 Manejo de Casos Especiales

### **Casos sin Vertical (NULL)**

**Situación:** Algunos casos pueden no tener vertical asociada.

**Acción:**
- Agrupar como `"SIN_VERTICAL"`
- Reportar % de casos sin vertical
- Si >5% del total → alertar (posible problema de data)

**Ejemplo:**
```
SIN_VERTICAL: 120 casos (2.3% del total) ← OK
SIN_VERTICAL: 1,200 casos (15% del total) ← ⚠️ REVISAR DATA
```

---

### **Verticales con Poco Volumen**

**Situación:** Algunas verticales pueden tener muy pocos casos.

**Acción:**
- Solo reportar top 5 con mayor variación
- O verticales que superen umbral mínimo (ej: >100 casos o >5% del total)
- No reportar variaciones de verticales con <50 casos (ruido estadístico)

---

### **Dominios Inconsistentes**

**Situación:** Algunos dominios pueden tener valores raros o inconsistentes.

**Acción:**
- Priorizar análisis a nivel **vertical** (más robusto)
- Usar dominios solo para profundizar en vertical específica
- No generar hallazgos basados únicamente en 1 dominio con pocos casos

---

## 🔍 Validación de Datos

### **Checks Automáticos al Generar Métricas:**

```python
# 1. Completitud
assert df['VERTICAL'].notna().sum() / len(df) > 0.90, "Más de 10% sin vertical"

# 2. Distribución razonable
assert len(df['VERTICAL'].unique()) > 5, "Muy pocas verticales (posible error)"

# 3. Consistencia con incoming total
assert df['INCOMING'].sum() == incoming_total_pdd_pnr, "Suma no cuadra"

# 4. Dominios dentro de verticales
# Cada dominio debe pertenecer a UNA sola vertical
```

---

## 📊 Umbrales de Reporte

### **Criterios para incluir en reporte:**

| Criterio | Umbral | Acción |
|----------|--------|--------|
| Variación porcentual | >10% | ✅ Reportar |
| Variación absoluta | >100 casos | ✅ Reportar si también >5% |
| Pico detectado | >1.5 × std | ✅ Reportar siempre |
| % del total | <2% del incoming total | ❌ No reportar (poco relevante) |
| Volumen mínimo | <50 casos en ambos períodos | ❌ No reportar (ruido) |

### **Orden de presentación:**

1. Ordenar por **variación absoluta** (impacto)
2. Mostrar top 5
3. Si hay más de 5 con criterio, colapsar el resto

---

## 📚 Documentación Relacionada

### **Sistema de Métricas:**
- **`../README.md`**: Overview del sistema de hard metrics
- **`../INDICE.md`**: Mapa de navegación
- **`README.md`**: Docs técnicas de esta métrica
- **`CUANDO_REGENERAR.md`**: Workflow de actualización

### **Contexto de Negocio:**
- **`../../docs/business-context.md`**: Commerce Groups y reglas
- **`../../docs/COMMERCE_GROUPS_REFERENCE.md`**: Clasificación de PDD/PNR
- **`../../docs/GOLDEN_TEMPLATES.md`**: Cómo integrar en reportes

---

## ⚙️ Evolución Futura

**Posibles extensiones:**

1. **Análisis cross-site:** Comparar verticales entre países
2. **Series temporales:** Detectar tendencias de largo plazo por vertical
3. **Clustering:** Agrupar verticales con patrones similares
4. **Predicción:** Alertas tempranas de incrementos por vertical

---

**Mantenedor:** CR Analytics Team  
**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Feedback:** Bienvenido para mejorar esta documentación
