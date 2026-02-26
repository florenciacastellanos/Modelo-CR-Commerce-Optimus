# 📊 Estructura Oficial de Reportes CR

**Versión:** 3.7  
**Fecha:** Enero 2026  
**Status:** ✅ OFICIAL - Aplicar a Post-Compra y Marketplace

---

## 🎯 Alcance

Esta estructura oficial aplica para:

### **Post-Compra (Validado v3.6)**
- ✅ **PDD** (Producto Dañado/Defectuoso)
- ✅ **PNR** (Producto No Recibido)
- ✅ **PCF** (Post Compra Funcionalidades - Comprador/Vendedor)

### **Marketplace (Validado v3.7)**
- ✅ **Pre Venta** (Consultas pre-venta)
- ✅ **Post Venta** (Soporte post-venta)
- ✅ **Generales Compra** (Consultas generales de compra) ⭐ NUEVO
- ✅ **Moderaciones** (Moderaciones y Prustomer)
- ✅ **Full Sellers** (Full Sellers)
- ✅ **Pagos** (Pagos y transacciones)

**Nota:** Otras categorías (Shipping, Pagos, Cuenta) se incorporarán progresivamente según se validen.

---

## 📐 Dos Tipos de Reportes

### **Tipo 1: Reporte CROSS SITE**
Para análisis que consolidan múltiples sites (MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE)

### **Tipo 2: Reporte SINGLE SITE**
Para análisis de un único site específico (ej: MLA, MLB)

---

## 🏗️ TIPO 1: Estructura CROSS SITE (3 Tablas)

### Casos de Uso
- PCF Cross Site Sep-Oct 2025
- PDD Cross Site Nov-Dic 2025
- PNR Cross Site Mensual

### Estructura de 3 Tablas

#### **TABLA 1: Consolidado por Proceso (sin site)**
```
┌─────────────────────────────────────────────────┐
│ PROCESS_NAME │ Inc M1 │ Inc M2 │ Var │ CR │ %  │
├─────────────────────────────────────────────────┤
│ Proceso A    │ 50,000 │ 52,000 │ ... │ .. │ .. │
│ Proceso B    │ 30,000 │ 28,000 │ ... │ .. │ .. │
│ ...          │ ...    │ ...    │ ... │ .. │ .. │
├─────────────────────────────────────────────────┤
│ TOTAL        │ 80,000 │ 80,000 │ ... │ .. │100%│
└─────────────────────────────────────────────────┘
```

**Columnas:**
- PROCESS_NAME
- Incoming Mes 1, Incoming Mes 2
- Var Abs, Var %
- CR Mes 1 (pp), CR Mes 2 (pp)
- Var CR (pp), Var CR %
- % Contrib (participación en variación CR total)

**Ordenamiento:** Por incoming total descendente + participación en variación CR

#### **TABLA 2: Consolidado por Site (sin procesos)**
```
┌─────────────────────────────────────────────────┐
│ SITE     │ País      │ Inc M1 │ Inc M2 │ CR │ %│
├─────────────────────────────────────────────────┤
│ MLB      │ Brasil    │ 40,000 │ 42,000 │ .. │..│
│ MLA      │ Argentina │ 25,000 │ 24,000 │ .. │..│
│ MLM      │ México    │ 15,000 │ 14,000 │ .. │..│
│ ...      │ ...       │ ...    │ ...    │ .. │..│
├─────────────────────────────────────────────────┤
│ TOTAL    │           │ 80,000 │ 80,000 │ .. │100│
└─────────────────────────────────────────────────┘
```

**Columnas:** SITE, País, Incoming M1/M2, Var, CR M1/M2, Var CR, % Contrib

**Ordenamiento:** Por incoming total descendente

#### **TABLA 3: Detalle por Site (proceso × site)**
```
┌──────────────────────────────────────────────────────┐
│ SITE │ PROCESS_NAME │ Inc M1 │ Inc M2 │ CR │ % │ ... │
├──────────────────────────────────────────────────────┤
│ MLB  │ Proceso A    │ 20,000 │ 21,000 │ .. │ ..│ ... │
│ MLB  │ Proceso B    │ 15,000 │ 16,000 │ .. │ ..│ ... │
│ MLB  │ Proceso C    │  5,000 │  5,000 │ .. │ ..│ ... │
│ MLA  │ Proceso A    │ 15,000 │ 14,000 │ .. │ ..│ ... │
│ MLA  │ Proceso B    │ 10,000 │ 10,000 │ .. │ ..│ ... │
│ ...  │ ...          │ ...    │ ...    │ .. │ ..│ ... │
├──────────────────────────────────────────────────────┤
│ TOTAL│              │ 80,000 │ 80,000 │ .. │100│ ... │
└──────────────────────────────────────────────────────┘
```

**Columnas:** SITE, PROCESS_NAME, Incoming M1/M2, Var, CR M1/M2, Var CR, % Contrib

**Ordenamiento:** 
1. Sites ordenados según aparecen en Tabla 2 (mayor incoming primero)
2. Dentro de cada site: procesos ordenados por incoming descendente

**Regla Crítica:** El orden de sites en Tabla 3 DEBE coincidir con Tabla 2.

---

## 🏗️ TIPO 2: Estructura SINGLE SITE (2 Tablas)

### Casos de Uso
- PDD MLA Nov-Dic 2025
- PNR MLB Mensual
- PCF MLA por CDU

### Estructura de 2 Tablas

#### **TABLA 1: Consolidado por Proceso (sin CDU)**
```
┌─────────────────────────────────────────────────┐
│ PROCESS_NAME │ Inc M1 │ Inc M2 │ Var │ CR │ %  │
├─────────────────────────────────────────────────┤
│ Proceso A    │ 15,000 │ 16,000 │ ... │ .. │ .. │
│ Proceso B    │ 10,000 │  9,500 │ ... │ .. │ .. │
│ Proceso C    │  5,000 │  5,200 │ ... │ .. │ .. │
│ ...          │ ...    │ ...    │ ... │ .. │ .. │
├─────────────────────────────────────────────────┤
│ TOTAL        │ 30,000 │ 30,700 │ ... │ .. │100%│
└─────────────────────────────────────────────────┘
```

**Columnas:** PROCESS_NAME, Incoming M1/M2, Var, CR M1/M2, Var CR, % Contrib

**Ordenamiento:** Por incoming total descendente + participación en variación CR

#### **TABLA 2: Detalle por Proceso y CDU (proceso × CDU)**
```
┌───────────────────────────────────────────────────────┐
│ PROCESS_NAME │ CDU        │ Inc M1 │ Inc M2 │ CR │ % │
├───────────────────────────────────────────────────────┤
│ Proceso A    │ CDU-001    │  8,000 │  9,000 │ .. │ ..│
│ Proceso A    │ CDU-002    │  5,000 │  5,500 │ .. │ ..│
│ Proceso A    │ CDU-003    │  2,000 │  1,500 │ .. │ ..│
│ Proceso B    │ CDU-004    │  6,000 │  6,000 │ .. │ ..│
│ Proceso B    │ CDU-005    │  4,000 │  3,500 │ .. │ ..│
│ Proceso C    │ CDU-001    │  5,000 │  5,200 │ .. │ ..│
│ ...          │ ...        │ ...    │ ...    │ .. │ ..│
├───────────────────────────────────────────────────────┤
│ TOTAL        │            │ 30,000 │ 30,700 │ .. │100│
└───────────────────────────────────────────────────────┘
```

**Columnas:** PROCESS_NAME, CDU, Incoming M1/M2, Var, CR M1/M2, Var CR, % Contrib

**Ordenamiento:**
1. Procesos ordenados según aparecen en Tabla 1 (mayor incoming primero)
2. Dentro de cada proceso: CDUs ordenados por incoming descendente

**Regla Crítica:** El orden de procesos en Tabla 2 DEBE coincidir con Tabla 1.

---

## 🎨 Estándares Visuales

### **1. Resumen Ejecutivo**

**Orden de Cards:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Incoming M1 │ Incoming M2 │ Driver M1   │ Driver M2   │
└─────────────┴─────────────┴─────────────┴─────────────┘
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ CR M1 (pp)  │ CR M2 (pp)  │ Var Incoming│ Var CR (pp) │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Reglas:**
- ✅ Drivers DESPUÉS de Incoming (no antes)
- ✅ Colores drivers: Azul (`border-left-color: #1976d2`)
- ✅ Colores commerce group: Según tipo (PDD=#f44336, PNR=#ff5722, PCF=#4caf50)
- ✅ 8 cards siempre (4 superior, 4 inferior)

### **2. Colores Semánticos**

```css
.positive  { color: #00a650; } /* Verde - Mejora (CR baja o incoming baja) */
.negative  { color: #f23d4f; } /* Rojo - Empeora (CR sube o incoming sube) */
.neutral   { color: #666; }    /* Gris - Sin cambio */
```

**Aplicación:**
- Variación Incoming: Rojo si sube (+), Verde si baja (-)
- Variación CR: Rojo si sube (+), Verde si baja (-)

### **3. Fila de Totales**

```css
tr.total-row {
    background: #f0f0f0;
    font-weight: bold;
    border-top: 2px solid [COLOR_COMMERCE_GROUP];
}

tr.total-row td {
    font-weight: bold;
    border-bottom: 2px solid [COLOR_COMMERCE_GROUP];
}
```

**Contenido:**
- Primera columna: `<strong>TOTAL</strong>`
- Si tabla tiene 2 columnas de texto (ej: SITE + PROCESS): usar `colspan="2"`
- Última columna (% Contrib): Siempre `100.0%`

### **4. Headers de Tabla**

**Colores por Categoría y Commerce Group:**

| Categoría | Color | Hex | Uso |
|-----------|-------|-----|-----|
| **Post-Compra PDD** | Rojo | `#f44336` | 🔴 PDD únicamente |
| **Post-Compra PNR** | Naranja | `#ff5722` | 🟠 PNR únicamente |
| **Post-Compra PCF** | Verde | `#4caf50` | 🟢 PCF únicamente |
| **Marketplace** | Azul | `#2196f3` | 🔵 Pre Venta, Post Venta, Generales Compra, Moderaciones, Full Sellers, Pagos |
| **Shipping** ⭐ | Morado | `#9c27b0` | 🟣 ME Distribución, ME PreDespacho, FBM Sellers, ME Drivers |

**Nuevo v3.7:** Color morado para Shipping

### **5. Badges**

```html
<!-- Cross Site -->
<span class="badge-cross">CROSS SITE</span>

<!-- Site específico -->
<span class="badge-mla">MLA</span>
<span class="badge-mlb">MLB</span>

<!-- Commerce Group por Categoría -->
<span class="badge-pdd">PDD</span>
<span class="badge-pnr">PNR</span>
<span class="badge-pcf">PCF</span>
<span class="badge-marketplace">MARKETPLACE</span> <!-- v3.7 -->
<span class="badge-shipping">SHIPPING</span> <!-- Nuevo v3.7 -->
```

**CSS para Badges por Categoría:**
```css
/* Marketplace */
.badge-marketplace {
    background: #2196f3; 
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}

/* Shipping - NUEVO v3.7 */
.badge-shipping {
    background: #9c27b0; 
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}
```

---

## 📏 Reglas de Ordenamiento

### **Regla 1: Ordenamiento Principal**
Todas las tablas consolidadas se ordenan por:
1. **TOTAL_INCOMING** (Mes 1 + Mes 2) descendente
2. **PARTICIPACION_VAR_CR_PCT** descendente (como criterio de desempate)

### **Regla 2: Ordenamiento de Detalle**
Las tablas de detalle (Tabla 3 Cross Site, Tabla 2 Single Site) DEBEN:
1. Seguir el orden de la tabla consolidada que les precede
2. Dentro de cada grupo: ordenar por incoming total descendente

### **Regla 3: Sincronización**
```
CONSOLIDADO                    DETALLE
┌─────────────┐               ┌─────────────────┐
│ Grupo A (#1)│  ─────────>   │ Grupo A - Item 1│
│ Grupo B (#2)│               │ Grupo A - Item 2│
│ Grupo C (#3)│               │ Grupo B - Item 1│
└─────────────┘               │ Grupo B - Item 2│
                              │ Grupo C - Item 1│
                              └─────────────────┘
```

**Implementación:**
```python
# Paso 1: Crear dict de orden desde tabla consolidada
orden = {valor: idx for idx, valor in enumerate(df_consolidado['COLUMNA_KEY'].tolist())}

# Paso 2: Aplicar orden a tabla detalle
df_detalle['ORDEN'] = df_detalle['COLUMNA_KEY'].map(orden)
df_detalle = df_detalle.sort_values(by=['ORDEN', 'TOTAL_INCOMING'], ascending=[True, False])
```

---

## 🔢 Cálculos Estándar

### **Columnas Obligatorias**

Todas las tablas DEBEN incluir:

| Columna | Descripción | Fórmula |
|---------|-------------|---------|
| `INCOMING_M1` | Incoming mes 1 | `SUM(casos)` |
| `INCOMING_M2` | Incoming mes 2 | `SUM(casos)` |
| `VAR_INCOMING_ABS` | Variación absoluta | `M2 - M1` |
| `VAR_INCOMING_PCT` | Variación % | `((M2-M1)/M1) × 100` |
| `CR_M1_PP` | CR mes 1 en pp | `(M1/Driver) × 100` |
| `CR_M2_PP` | CR mes 2 en pp | `(M2/Driver) × 100` |
| `VAR_CR_ABS_PP` | Variación CR en pp | `CR_M2 - CR_M1` |
| `VAR_CR_PCT` | Variación CR % | `((CR_M2-CR_M1)/CR_M1) × 100` |
| `PARTICIPACION_VAR_CR_PCT` | % Contribución | `(VAR_CR_ABS / VAR_CR_TOTAL) × 100` |

### **Totales**

```python
# Calcular totales
total_inc_m1 = df['INCOMING_M1'].sum()
total_inc_m2 = df['INCOMING_M2'].sum()
total_var = total_inc_m2 - total_inc_m1

total_cr_m1 = (total_inc_m1 / driver_m1 * 100)
total_cr_m2 = (total_inc_m2 / driver_m2 * 100)
total_var_cr = total_cr_m2 - total_cr_m1

# Fila de totales
html += f"""
    <tr class="total-row">
        <td><strong>TOTAL</strong></td>
        <td class="number">{int(total_inc_m1):,}</td>
        <td class="number">{int(total_inc_m2):,}</td>
        <td class="number {var_class}">{int(total_var):+,}</td>
        <td class="number">{total_cr_m1:.4f}</td>
        <td class="number">{total_cr_m2:.4f}</td>
        <td class="number {var_cr_class}">{total_var_cr:+.4f}</td>
        <td class="number">100.0%</td>
    </tr>
"""
```

---

## 📦 Componentes Adicionales

### **1. Desglose por Tipo (Solo PCF)**

Para Post Compra Funcionalidades, agregar antes de las tablas:

```html
<div class="pcf-type-summary">
    <h3>📊 Desglose por Tipo PCF</h3>
    <div class="pcf-grid">
        <div class="pcf-card">
            <h4>PCF COMPRADOR</h4>
            <!-- Stats: Incoming, CR, Variación -->
        </div>
        <div class="pcf-card">
            <h4>PCF VENDEDOR</h4>
            <!-- Stats: Incoming, CR, Variación -->
        </div>
    </div>
</div>
```

### **2. Detalles Técnicos (Colapsable)**

Al final del reporte, SIEMPRE incluir:

```html
<details class="technical-details">
    <summary>📋 Detalles Técnicos (para validación)</summary>
    <p>
        <strong>Versión:</strong> 3.6<br>
        <strong>Fuente:</strong> BigQuery - BT_CX_CONTACTS + BT_ORD_ORDERS<br>
        <strong>Filtro BU:</strong> ME/ML<br>
        <strong>Clasificación:</strong> CASE v3.5 con 'Conflict Others/Stale'<br>
        <strong>Filtros BASE:</strong> GMV_FLG + MARKETPLACE_FLG + sin MLV + sin TIPS<br>
        <strong>Campo fecha:</strong> DATE_TRUNC(CONTACT_DATE_ID, MONTH)<br>
        <!-- Más detalles según el caso -->
    </p>
</details>
```

### **3. Pirámide Invertida - Estructura de Entrega**

**Objetivo:** Permitir que el usuario corte la lectura en cualquier nivel según el tiempo disponible.

Los reportes DEBEN estructurarse en 5 niveles de profundidad creciente, donde cada nivel contiene el anterior + información adicional.

#### **Estructura en 5 Niveles**

| Nivel | Contenido | Tiempo de lectura | Ubicación en reporte |
|-------|-----------|-------------------|---------------------|
| **1** | Resumen Ejecutivo (3 bullets) | 30 segundos | Cards ejecutivas + primer párrafo |
| **2** | Métricas Consolidadas | 2 minutos | Tablas consolidadas (sin detalle) |
| **3** | Principales Elementos e Hipótesis | 5 minutos | Tabla con elementos priorizados (regla 80%) |
| **4** | Evidencia Cualitativa | 10 minutos | Citas, patrones, sentimiento por elemento |
| **5** | Análisis Completo con Contexto | 15+ minutos | Correlaciones eventos, deep dive, insights |

#### **Ejemplo de Implementación**

**[Nivel 1] Resumen Ejecutivo (30s)**

```markdown
**CR de PDD MLA aumentó +0.05 pp (+15%) en Dic vs Nov 2025:**
- 80% del incremento explicado por 2 procesos: Arrepentimiento (+0.03 pp) y Defectuoso (+0.01 pp)
- Correlación con Black Friday: 25% de los casos de Arrepentimiento provienen de órdenes cerradas durante el evento
- Evidencia: 40/50 conversaciones mencionan "compra impulsiva" o "cambio de opinión"
```

---

**[Nivel 2] Métricas Consolidadas (2 min)**

```markdown
### Contact Rate General
| Período | Incoming | Driver | CR (pp) | Var |
|---------|----------|--------|---------|-----|
| Nov | 1,500 | 150,000 | 1.00 | - |
| Dic | 1,725 | 150,000 | 1.15 | +0.15 pp (+15%) |

### Distribución por Proceso (Consolidado)
| Proceso | Inc Nov | Inc Dic | Var | % Contrib |
|---------|---------|---------|-----|-----------|
| Arrepentimiento | 800 | 950 | +150 | 67% |
| Defectuoso | 400 | 450 | +50 | 22% |
| Otros | 300 | 325 | +25 | 11% |
| **TOTAL** | 1,500 | 1,725 | +225 | 100% |
```

---

**[Nivel 3] Principales Elementos (5 min)**

```markdown
**Elementos priorizados (regla 80%):**
1. **Arrepentimiento** (+150 casos, 67% contribución)
2. **Defectuoso** (+50 casos, 22% contribución)

**Hipótesis iniciales:**
- Arrepentimiento: Correlación con Black Friday (compras impulsivas)
- Defectuoso: Posible issue con nuevo proveedor
```

---

**[Nivel 4] Evidencia Cualitativa (10 min)**

```markdown
### Arrepentimiento (+150 casos)
- **Muestreo:** 50 conversaciones (70% del pico 29-nov, 30% resto)
- **Causa raíz:** 40/50 (80%) mencionan compra impulsiva durante Black Friday
- **Citas:**
  > *"Compré por el descuento pero no lo necesito"* - Caso #123
  > *"Me arrepentí al día siguiente"* - Caso #456
- **Sentimiento:** 75% satisfacción (proceso de devolución claro)

### Defectuoso (+50 casos)
[... evidencia similar ...]
```

---

**[Nivel 5] Análisis Completo (15+ min)**

```markdown
### Correlación con Eventos
- Black Friday (28-29 Nov): 150/950 casos de Arrepentimiento (16%)
- Peak detection: 29-nov con 180% del promedio diario
- Patrón temporal: incremento sostenido en semana post-evento

### Deep Dive por Sub-causa
[... análisis detallado ...]

### Contexto Comercial
[... eventos, campañas, cambios de producto ...]
```

#### **Beneficio de la Pirámide Invertida**

| Audiencia | Lee hasta | Tiempo | Obtiene |
|-----------|-----------|--------|---------|
| Ejecutivos | Nivel 1 | 30s | Decisión informada |
| Managers | Nivel 3 | 5 min | Entendimiento del problema |
| Analistas | Nivel 5 | 15+ min | Contexto para implementar acciones |

#### **Implementación en HTML**

```html
<!-- Nivel 1: Cards + resumen al inicio -->
<section class="executive-summary">
    <div class="cards-container">
        <!-- 8 cards ejecutivas -->
    </div>
    <div class="key-findings">
        <h2>Hallazgos Principales</h2>
        <ul>
            <li>80% del incremento explicado por...</li>
            <li>Correlación con Black Friday...</li>
            <li>Evidencia: 40/50 conversaciones...</li>
        </ul>
    </div>
</section>

<!-- Nivel 2: Tablas consolidadas expandibles -->
<section class="consolidated-metrics">
    <h2>Métricas Consolidadas</h2>
    <!-- Tablas sin detalle -->
</section>

<!-- Nivel 3: Tabla de elementos priorizados -->
<section class="prioritized-elements">
    <h2>Elementos Priorizados (Regla 80%)</h2>
    <!-- Tabla con top elementos -->
</section>

<!-- Nivel 4-5: Secciones colapsables con evidencia y deep dive -->
<details open>
    <summary>🔍 Evidencia Cualitativa</summary>
    <!-- Muestreo, citas, sentimiento -->
</details>

<details>
    <summary>📊 Análisis Completo</summary>
    <!-- Correlaciones, deep dive, contexto -->
</details>
```

#### **Reglas de Implementación**

1. **Nivel 1 siempre visible:** No colapsar el resumen ejecutivo
2. **Niveles 2-3 expandidos por defecto:** Fácil acceso a métricas clave
3. **Niveles 4-5 colapsables:** Para usuarios que quieren profundizar
4. **Navegación clara:** Botón "Ir a análisis completo" desde Nivel 1

**Referencias:**
- Principio de pirámide invertida aplicado al análisis de datos
- Inspirado en journalism inverted pyramid structure
- Validado en reportes PDD/PNR v3.6+

---

## 🗓️ Sección de Feriados (v6.4.10)

### Ubicación en el reporte
Después de **Eventos Comerciales** y antes de **Cuadros Cuantitativos por Dimensión**.

### Fuente de datos
```sql
SELECT SIT_SITE_ID, TIM_DAY as Fecha_feriado, HOLIDAY_DESC
FROM `meli-bi-data.WHOWNER.LK_TIM_HOLIDAYS`
WHERE SIT_SITE_ID = '{site}'
  AND TIM_DAY BETWEEN '{p1_start - 15 días}' AND '{p2_end}'
ORDER BY TIM_DAY ASC
```

### Rango temporal
- **15 días previos al inicio de P1**: Cubre efectos retardados (ej: demoras de entrega por cierre operativo que generan contactos días después)
- **P1 completo**: Feriados dentro del primer período de análisis
- **P2 completo**: Feriados dentro del segundo período de análisis

### Contenido de la card
| Columna | Descripción |
|---------|-------------|
| **Fecha** | Fecha del feriado (YYYY-MM-DD) |
| **Día** | Día de la semana en español |
| **Feriado** | Descripción del feriado (HOLIDAY_DESC) |
| **Site** | Site al que aplica el feriado |
| **Ubicación** | Pre-período (15d previos), P1 o P2 |

### Badges de ubicación
- **Amarillo**: Pre-período (15 días previos)
- **Verde**: P1
- **Azul**: P2

### Resumen
Conteo de feriados por ubicación temporal y nota sobre posibles impactos operacionales.

### Propósito
Dato informativo/contextual. No modifica cálculos de CR, incoming ni drivers. Permite al analista considerar el impacto de feriados en su interpretación del análisis.

---

## ✅ Checklist de Validación

Antes de entregar un reporte, verificar:

### **Estructura**
- [ ] Resumen ejecutivo con 8 cards
- [ ] Drivers DESPUÉS de incoming
- [ ] Número correcto de tablas (2 o 3 según tipo)
- [ ] Todas las tablas tienen fila de totales

### **Datos**
- [ ] Totales coinciden entre todas las tablas
- [ ] % Contribución suma 100.0% en todas las tablas
- [ ] Ordenamiento es consistente entre consolidado y detalle
- [ ] Colores semánticos aplicados correctamente

### **Estilo**
- [ ] Headers del color correcto según commerce group
- [ ] Badges apropiados (CROSS SITE, site específico, commerce group)
- [ ] Fila de totales con fondo gris y bordes del color del grupo
- [ ] Detalles técnicos en sección colapsable

### **Técnico**
- [ ] CSV generado con todos los registros detalle
- [ ] HTML se abre automáticamente en navegador
- [ ] Queries usan CASE v3.5 para clasificación
- [ ] Filtro BU aplicado (ME/ML)
- [ ] Filtros BASE en drivers

---

## 🔄 Casos Especiales

### **Cross Site con Tipos (PCF)**

Cuando hay tipos (Comprador/Vendedor), generar reportes separados:

1. **Reporte PCF Comprador Cross Site** (3 tablas)
2. **Reporte PCF Vendedor Cross Site** (3 tablas)

O bien, en un solo reporte:
- Tabla 1: Consolidado Proceso PCF Comprador
- Tabla 2: Consolidado Site PCF Comprador
- Tabla 3: Detalle Site PCF Comprador
- Tabla 4: Consolidado Proceso PCF Vendedor
- Tabla 5: Consolidado Site PCF Vendedor
- Tabla 6: Detalle Site PCF Vendedor

### **Sites Incluidos**

**Cross Site Standard (8 sites):**
- MLA (Argentina)
- MLB (Brasil)
- MLC (Chile)
- MCO (Colombia)
- MEC (Ecuador)
- MLM (México)
- MLU (Uruguay)
- MPE (Perú)

**Excluido:** MLV (Venezuela) - siempre

---

## 📝 Ejemplos de Nombres de Archivos

### **Scripts Python**
```
generar_cr_[COMMERCE]_[SCOPE]_[PERIODO].py

Ejemplos:
- generar_cr_pdd_MLA_nov_dic_2025_v2.py
- generar_cr_pcf_CROSS_SITE_CON_FILTRO_BU.py
- generar_cr_pnr_CROSS_SITE_sep_oct_2025.py
```

### **Reportes HTML**
```
reporte-cr-[COMMERCE]-[SCOPE]-[PERIODO].html

Ejemplos:
- reporte-cr-pdd-MLA-nov-dic-2025-v2.html
- reporte-cr-pcf-CROSS-SITE-sep-oct-2025-CON-FILTRO-BU.html
- reporte-cr-pnr-CROSS-SITE-sep-oct-2025.html
```

### **Archivos CSV**
```
cr-[COMMERCE]-[SCOPE]-[PERIODO].csv

Ejemplos:
- cr-pdd-MLA-nov-dic-2025-v2.csv
- cr-pcf-CROSS-SITE-sep-oct-2025-CON-FILTRO-BU.csv
```

---

## 🚀 Plantillas de Código

### **Template: Script Completo Single Site**

Ver: `templates/script-single-site-template.py`

### **Template: Script Completo Cross Site**

Ver: `templates/script-cross-site-template.py`

### **Template: HTML Generation**

Ver: `templates/html-generation-template.py`

---

## 🚛 Drivers de Shipping (NUEVO v3.7)

### **⚠️ CRÍTICO: Shipping usa drivers DIFERENTES**

Los reportes de **SHIPPING** NO usan órdenes totales de `BT_ORD_ORDERS`. Cada agrupación tiene su driver específico:

| Agrupación Shipping | Driver Code | Campo en BT_CX_DRIVERS_CR | Query |
|---------------------|-------------|---------------------------|-------|
| **ME Distribución** | OS_TOTALES | `ORDERS_SHIPPED` | Ver `docs/SHIPPING_DRIVERS.md` |
| **ME PreDespacho** ✅ | OS_WO_FULL | `OS_WITHOUT_FBM` | Ver `docs/SHIPPING_DRIVERS.md` |
| **FBM Sellers** | OS_FULL | `OS_WITH_FBM` | Ver `docs/SHIPPING_DRIVERS.md` |

✅ = Validado

### **Regla de Oro: Drivers GLOBALES**

**✅ CORRECTO:**
```sql
-- Driver GLOBAL (sin filtro de site)
SELECT
    drv.MONTH_ID as period,
    SUM(drv.OS_WITHOUT_FBM) as driver_value
FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
    -- Solo periodo, SIN otros filtros
GROUP BY drv.MONTH_ID
```

**❌ INCORRECTO:**
```sql
-- ❌ NO filtrar driver por site
WHERE drv.MONTH_ID BETWEEN '2025-11-01' AND '2025-12-31'
  AND drv.SIT_SITE_ID = 'MLB'  -- ❌ PROHIBIDO
```

### **Comparación: Shipping vs Post-Compra/Marketplace**

| Aspecto | Post-Compra/Marketplace | Shipping |
|---------|-------------------------|----------|
| **Tabla Driver** | `BT_ORD_ORDERS` | `BT_CX_DRIVERS_CR` |
| **Campo Driver** | `COUNT(DISTINCT ORD_ORDER_ID)` | `SUM(ORDERS_SHIPPED)` / `SUM(OS_WITHOUT_FBM)` / `SUM(OS_WITH_FBM)` |
| **Filtros Driver** | GMV_FLG + MARKETPLACE_FLG + sin MLV + sin TIPS | **Solo periodo** |
| **¿Filtrar por site?** | ❌ NO (global) | ❌ NO (global) |

**Documentación completa:** `docs/SHIPPING_DRIVERS.md`

---

## 📚 Referencias

- **Clasificación v3.5**: `sql/filters/commerce-groups-classification.sql`
- **Filtros BASE**: `config/business-constants.py`
- **Thresholds**: `config/thresholds.py`
- **Validación**: `docs/VALIDACION.md`

---

## 🔄 Changelog

### v3.7 (Enero 2026)
- ✅ **Extensión a Marketplace:** 6 commerce groups (color azul #2196f3)
- ✅ **Drivers de Shipping:** Documentados drivers específicos (OS_TOTALES, OS_WO_FULL, OS_FULL) de `BT_CX_DRIVERS_CR`
- ✅ **ME PreDespacho validado:** Primer reporte Shipping (MLB Nov-Dic 2025)
- ✅ **Color morado (#9c27b0) para Shipping:** Distintivo de categoría
- ✅ Regla crítica: Drivers de Shipping son GLOBALES (sin filtro de site)
- ✅ Nueva sección: "Drivers de Shipping" en documento

### v3.6 (Enero 2026)
- ✅ Estructura oficial documentada
- ✅ Separación clara entre Cross Site (3 tablas) y Single Site (2 tablas)
- ✅ Reglas de ordenamiento sincronizado
- ✅ Estándares visuales y colores
- ✅ Checklist de validación
- ✅ Ejemplos y plantillas

---

**Estado:** ✅ **OFICIAL v3.7** - Aplicar a Post-Compra, Marketplace y Shipping

**Post-Compra (v3.6):** PDD, PNR, PCF  
**Marketplace (v3.7):** Pre Venta, Post Venta, Generales Compra, Moderaciones, Full Sellers, Pagos  
**Shipping (v3.7):** ME PreDespacho (validado) | ME Distribución, FBM Sellers (pendientes)

**Próximos Pasos:**
- Validar ME Distribución y FBM Sellers con sus drivers específicos
- Validar estructura con categorías Pagos y Cuenta
- Crear templates automatizados para Shipping
- Documentar clasificaciones específicas por commerce group
