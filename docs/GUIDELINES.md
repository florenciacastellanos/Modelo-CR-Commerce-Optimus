# 📋 Guidelines - Contact Rate Analysis

> **Recomendaciones y mejores prácticas** para usar el repositorio de análisis de Contact Rate de forma efectiva

---

## 🎯 Propósito de este Documento

Este documento contiene **recomendaciones** (SHOULD) para trabajar con el repositorio de Contact Rate Analysis. A diferencia de las **RULES** (`.cursorrules`), estas son sugerencias que mejoran la experiencia pero no son obligatorias.

---

## 📚 Mejores Prácticas de Consulta

### 🚨 REGLA CRÍTICA: Referencias a Commerce Groups

Cuando menciones **"PDD"**, **"PNR"**, **"ME Distribución"**, etc., te refieres al **Commerce Group completo**, NO a un filtro de palabras clave en `PROCESS_NAME`.

#### ❌ ERROR COMÚN:

```python
# INCORRECTO - Filtrar por palabras en PROCESS_NAME
df_pdd = df[df['PROCESS_NAME'].str.contains('PDD|Dañado|Defectuoso')]
```

**Problema:** Esto excluye procesos que pertenecen a PDD pero no contienen esas palabras, como **"Arrepentimiento"**.

#### ✅ MÉTODO CORRECTO:

**Opción 1 - BigQuery (Recomendado):**
```sql
-- Usar la lógica oficial de AGRUP_COMMERCE
WHERE (
    PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
    OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'
    OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'
)
```

**Opción 2 - Datos Pre-calculados:**
```python
# Trabajar con datos que ya tienen AGRUP_COMMERCE calculado
df_pdd = df[df['AGRUP_COMMERCE'] == 'PDD']
```

#### 📋 Ejemplos de Interpretación:

| Usuario dice | Significa | NUNCA significa |
|--------------|-----------|----------------|
| "Analiza PDD" | Commerce Group PDD (todos los procesos clasificados como PDD) | Solo procesos con "PDD" en el nombre |
| "Incoming de PNR" | Todos los casos del Commerce Group PNR | Solo procesos con "PNR" en el nombre |
| "Procesos de ME Distribución" | Todos los procesos del Commerce Group ME Distribución | Solo procesos con "ME" o "Distribución" en el nombre |

#### 🎯 Regla de Oro:

> **"PDD" NO es un filtro de texto, es una categoría de negocio definida por `PROCESS_PROBLEMATIC_REPORTING`**

**Procesos incluidos en PDD (ejemplos reales):**
- ✅ Arrepentimiento - XD
- ✅ Defectuoso - XD  
- ✅ Dañado - DS
- ✅ Roto - FBM
- ✅ Diferente al Publicado - Flex
- ✅ Incompleto - CBT
- ✅ Caja Vacía - 1P&PL

**Fuente:** `docs/commerce-structure.md` - Keywords identificadores de PDD

#### 🚛 Caso Especial: Shipping (Criterio más complejo)

Para **Shipping** (ME Distribución, ME PreDespacho, ME Drivers, FBM Sellers), además del principio general, se requiere **un campo adicional**:

| Commerce Group | Campo 1 | Campo 2 | Ejemplo |
|----------------|---------|---------|---------|
| **PDD** | `PROCESS_PROBLEMATIC_REPORTING` | - | Simple ⚡ |
| **ME Distribución** | `PROCESS_PROBLEMATIC_REPORTING` | `PROCESS_GROUP_ECOMMERCE = 'Comprador'` | Compuesta 🔥 |
| **ME PreDespacho** | `PROCESS_PROBLEMATIC_REPORTING` | `PROCESS_GROUP_ECOMMERCE = 'Vendedor'` | Compuesta 🔥 |

**¿Por qué?** Porque el **mismo proceso** puede pertenecer a diferentes Commerce Groups según el **User Type**.

**Ejemplo:**
```
PROCESS_NAME: "Reclamo Mercado Envíos - Demora"
├─ User Type = Comprador → ME Distribución ✅
└─ User Type = Vendedor → ME PreDespacho ✅
```

📖 **Ver ejemplos detallados:** `docs/COMMERCE_GROUPS_REFERENCE.md` (Sección "CASO ESPECIAL: Shipping")

---

### Cómo Hacer Preguntas Efectivas

#### ✅ Preguntas Bien Formuladas

```
❌ MAL: "¿Qué es CR?"
✅ BIEN: "¿Cómo se calcula el Contact Rate y qué componentes incluye?"

❌ MAL: "Muéstrame datos"
✅ BIEN: "¿Cuál es la variación de CR para PDD en MLA entre Nov-Dic 2025?"
       (Esto significa: el Commerce Group PDD completo, no un filtro de texto)

❌ MAL: "Query"
✅ BIEN: "Muéstrame la query SQL para obtener datos de Contact Rate con filtros por site"
```

#### Estructura Recomendada

1. **Contexto**: ¿Qué Commerce Group?
2. **Dimensión**: ¿Qué apertura? (PROCESS_NAME, CDU, etc.)
3. **Período**: ¿Qué fechas comparar?
4. **Site**: ¿Qué país? (MLA, MLB, etc.)

**Ejemplo completo**:
> "Necesito analizar la variación de CR por PROCESS_NAME para ME Distribución en MLA, comparando Septiembre vs Octubre 2025"

---

## 🔍 Navegación del Repositorio

### Orden Sugerido de Lectura

Para **nuevos usuarios**:

1. **Inicio**: `README.md` (visión general)
2. **Contexto**: `docs/business-context.md` (entender el negocio)
3. **Métricas**: `docs/metrics-glossary.md` (fórmulas clave)
4. **Queries**: `sql/base-query.sql` (query principal)
5. **Workflow**: `docs/analysis-workflow.md` (proceso completo)

Para **usuarios avanzados**:

1. **Configuración**: `config/` (personalizar thresholds)
2. **Cálculos**: `calculations/` (lógica de variaciones)
3. **Patrones**: `calculations/pattern-detection.py` (detección de anomalías)
4. **Optimización**: `utils/memory-optimization.py` (performance)

---

## 📊 Análisis de Variaciones

### Interpretación de Resultados

#### Variación Absoluta (pp)
```
Δ CR = CR_actual - CR_anterior

Interpretación:
• +0.5 pp → Incremento moderado
• +1.0 pp → Incremento significativo
• +2.0 pp → Incremento fuerte (requiere análisis)
• +5.0 pp → Spike crítico (alerta)
```

#### Variación Relativa (%)
```
% Δ = ((CR_actual - CR_anterior) / CR_anterior) × 100

Interpretación:
• ±10% → Variación normal
• ±20% → Variación fuerte (revisar)
• ±50% → Variación crítica (investigar)
• ±100% → Duplicación/reducción a la mitad
```

### Recomendaciones por Magnitud

| Variación | Acción Recomendada |
|-----------|-------------------|
| < ±10% | Monitorear tendencia |
| ±10-20% | Analizar por dimensión |
| ±20-50% | Investigar causas raíz |
| > ±50% | Alerta crítica - acción inmediata |

---

## 🛠️ Uso de Dimensiones

### Cuándo Usar Cada Dimensión

#### **PROCESS_NAME**
- **Cuándo**: Vista general de alto nivel
- **Ideal para**: Identificar procesos con mayor impacto
- **Ejemplo**: "¿Qué procesos de PDD generan más contactos?"

#### **CDU (Caso de Uso)**
- **Cuándo**: Análisis detallado dentro de un proceso
- **Ideal para**: Drill-down después de PROCESS_NAME
- **Ejemplo**: "Dentro de 'Arrepentimiento', ¿qué CDUs tienen mayor CR?"

#### **TIPIFICACION (REASON_DETAIL_GROUP_REPORTING)**
- **Cuándo**: Análisis de motivos agrupados
- **Ideal para**: Entender razones de contacto
- **Ejemplo**: "¿Qué tipificaciones explican el aumento en PNR?"

#### **CLA_REASON_DETAIL**
- **Cuándo**: Análisis granular de motivos
- **Ideal para**: Investigación profunda
- **Ejemplo**: "¿Qué razones específicas causan el spike?"

#### **ENVIRONMENT**
- **Cuándo**: Comparar canales de fulfillment
- **Ideal para**: Análisis de DS vs FBM vs FLEX
- **Ejemplo**: "¿El CR de FBM es mayor que DS?"

---

## 📈 Estrategias de Análisis

### Análisis Top-Down (Recomendado)

```
1. Commerce Group (ej: PDD)
   ↓
2. PROCESS_NAME (ej: Arrepentimiento)
   ↓
3. CDU (ej: Arrepentimiento - Cambio de opinión)
   ↓
4. TIPIFICACION (ej: Solicitud de devolución)
   ↓
5. CLA_REASON_DETAIL (ej: No cumple expectativas)
```

### Análisis Comparativo

**Por Site**:
```
Comparar MLA vs MLB vs MCO
→ Identificar patrones regionales
```

**Por Período**:
```
MoM (Mes a mes) → Tendencias corto plazo
YoY (Año a año) → Estacionalidad
WoW (Semana a semana) → Spikes puntuales
```

**Por Environment**:
```
DS vs FBM vs FLEX
→ Identificar diferencias operativas
```

---

## 🚨 Detección de Anomalías

### Patrones a Buscar

#### **Spike (Pico)**
```
Definición: CR > 150% del promedio móvil
Acción: Investigar evento puntual
Ejemplo: Promoción especial, bug en sistema
```

#### **Drop (Caída)**
```
Definición: CR < 50% del promedio móvil
Acción: Validar datos, verificar exclusiones
Ejemplo: Feriado, cambio en proceso
```

#### **Tendencia Sostenida**
```
Definición: Δ consistente por 3+ períodos
Acción: Analizar cambio estructural
Ejemplo: Nueva política, mejora de proceso
```

#### **Concentración**
```
Definición: >30% del volumen en días específicos
Acción: Revisar eventos puntuales
Ejemplo: Hot Sale, Black Friday
```

---

## 🔧 Optimización de Queries

### Recomendaciones de Performance

#### Para Sites Pequeños (MLA, MCO, etc.)
```sql
-- No requiere sampling
-- Query directa sin optimizaciones especiales
```

#### Para MLB (Brasil)
```sql
-- SIEMPRE usar sampling strategy
-- Ver: /sql/sampling-strategy.sql
-- Threshold: 150,000 rows
```

#### Para Períodos Largos (>6 meses)
```sql
-- Considerar agregación mensual
-- Usar memory optimization
-- Ver: /utils/memory-optimization.py
```

### Filtros Recomendados

**Siempre incluir**:
```sql
WHERE SITE_ID IN ('MLA', 'MLB', ...)  -- Especificar sites
  AND PERIOD_MONTH BETWEEN 'YYYY-MM' AND 'YYYY-MM'  -- Rango específico
  AND FLAG_EXCLUDE_NUMERATOR_CR = 0  -- Exclusión automática
```

**Opcional según análisis**:
```sql
  AND ENVIRONMENT IN ('DS', 'FBM')  -- Si aplica
  AND QUEUE_ID NOT IN (2131, 230, ...)  -- Exclusiones adicionales
```

---

## 📊 Interpretación de Drivers

### Drivers por Categoría y Commerce Group

#### **Post-Compra y Marketplace**

| Commerce Group | Driver | Tabla | Interpretación |
|----------------|--------|-------|----------------|
| **PDD** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |
| **PNR** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |
| **PCF** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |
| **Generales Compra** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |
| **Pre Venta** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |
| **Post Venta** | Órdenes totales | `BT_ORD_ORDERS` | Casos / 100 órdenes |

**Filtros aplicados:** GMV_FLG + MARKETPLACE_FLG + sin MLV + sin TIPS

---

#### **Shipping** ⭐ NUEVO v3.7

| Commerce Group | Driver Code | Campo en BT_CX_DRIVERS_CR | Tabla | Interpretación |
|----------------|-------------|---------------------------|-------|----------------|
| **ME Distribución** | OS_TOTALES | `ORDERS_SHIPPED` | `BT_CX_DRIVERS_CR` | Casos / 100 órdenes shipped |
| **ME PreDespacho** ✅ | OS_WO_FULL | `OS_WITHOUT_FBM` | `BT_CX_DRIVERS_CR` | Casos / 100 órdenes sin FBM |
| **FBM Sellers** | OS_FULL | `OS_WITH_FBM` | `BT_CX_DRIVERS_CR` | Casos / 100 órdenes con FBM |

✅ = Validado con datos reales (Enero 2026)

**⚠️ CRÍTICO:** Drivers de Shipping son **GLOBALES** (sin filtro de site). Ver `docs/SHIPPING_DRIVERS.md`.

---

### Consideraciones

#### **Drivers Post-Compra/Marketplace:**
- **Driver = 0**: Excluir del análisis (división por cero)
- **Driver muy bajo**: Revisar threshold (< 50 casos)
- **Driver anómalo**: Validar data source
- **Driver GLOBAL**: Sin filtro de site (órdenes de todos los sites)

#### **Drivers Shipping (NUEVO v3.7):**
- **Driver GLOBAL**: SIN filtro de site ❌ (solo periodo)
- **Driver específico**: Usar campo correcto según agrupación (ORDERS_SHIPPED, OS_WITHOUT_FBM, OS_WITH_FBM)
- **Tabla diferente**: `BT_CX_DRIVERS_CR`, NO `BT_ORD_ORDERS`
- **Sin filtros adicionales**: Solo filtro de periodo en `MONTH_ID`

---

## 🎨 Visualización de Resultados

### Formatos Recomendados

#### Para Presentaciones Ejecutivas
```
✅ Gráfico de barras: Variación por proceso
✅ Tabla resumen: Top 5 procesos con mayor Δ
✅ Semáforo: Verde/Amarillo/Rojo según threshold
```

#### Para Análisis Técnico
```
✅ Serie temporal: Evolución mensual de CR
✅ Heatmap: CR por proceso × mes
✅ Waterfall: Contribución de cada proceso a Δ total
```

#### Para Reportes HTML (Generados)
```
✅ Tabla interactiva con sorting
✅ Colores por magnitud de variación
✅ Drill-down por dimensión
```

---

## 🔄 Workflow Recomendado

### Análisis Estándar (Mensual)

```
1. Ejecutar query base para Commerce Group
   → Obtener CR actual vs anterior

2. Identificar procesos con Δ > ±20%
   → Listar top 5 por impacto

3. Drill-down por CDU en procesos críticos
   → Entender causas específicas

4. Validar con tipificación
   → Confirmar motivos de contacto

5. Generar reporte HTML
   → Compartir con stakeholders

6. Documentar hallazgos
   → Actualizar knowledge base
```

### Análisis de Crisis (Spike Crítico)

```
1. Confirmar spike en data
   → Validar no es error de datos

2. Identificar proceso específico
   → Aislar causa raíz

3. Revisar eventos externos
   → Promociones, bugs, cambios

4. Analizar por CDU y tipificación
   → Drill-down completo

5. Comunicar hallazgos
   → Alerta a equipo responsable

6. Monitorear evolución
   → Seguimiento diario hasta normalización
```

---

## 🧪 Testing y Validación

### Antes de Usar Resultados

#### Sanity Checks
```python
# 1. Validar totales
assert incoming_total > 0, "Incoming debe ser > 0"
assert driver_total > 0, "Driver debe ser > 0"

# 2. Validar CR razonable
assert 0 < cr < 100, "CR debe estar entre 0 y 100 pp"

# 3. Validar períodos
assert period_current > period_previous, "Período actual debe ser posterior"
```

#### Comparación con Fuente
```
✅ Comparar totales con Jupyter Lab (si disponible)
✅ Validar contra dashboard existente
✅ Revisar con analista de negocio
```

---

## 📝 Documentación de Análisis

### Template Recomendado

```markdown
# Análisis CR - [Commerce Group] - [Período]

## Resumen Ejecutivo
- CR actual: X.XX pp
- CR anterior: X.XX pp
- Variación: ±X.XX pp (±X.X%)

## Procesos con Mayor Impacto
1. [Proceso 1]: +X.XX pp
2. [Proceso 2]: +X.XX pp
3. [Proceso 3]: -X.XX pp

## Causas Identificadas
- [Causa 1]: Descripción
- [Causa 2]: Descripción

## Recomendaciones
- [Acción 1]
- [Acción 2]

## Próximos Pasos
- [ ] Monitorear proceso X
- [ ] Investigar causa Y
```

---

## 🚀 Tips Avanzados

### Para Usuarios Expertos

1. **Combinar Dimensiones**:
   ```
   PROCESS_NAME + ENVIRONMENT
   → Ver si spike es específico de DS o FBM
   ```

2. **Análisis de Concentración**:
   ```
   Identificar si 80% del Δ viene de 20% de procesos
   → Principio de Pareto
   ```

3. **Benchmarking**:
   ```
   Comparar CR de MLA vs otros sites
   → Identificar best practices
   ```

4. **Forecasting**:
   ```
   Usar tendencia histórica para predecir CR futuro
   → Alertas proactivas
   ```

---

## ⚠️ Errores Comunes a Evitar

### ❌ No Hacer

1. **Analizar sin threshold**:
   - Procesos con < 50 casos no son significativos

2. **Ignorar sampling en MLB**:
   - Resultados incorrectos por volumen

3. **Comparar períodos no comparables**:
   - Ej: Diciembre (alta estacionalidad) vs Enero

4. **No validar exclusiones**:
   - Queues y procesos excluidos pueden sesgar resultados

5. **Confundir variación absoluta con relativa**:
   - +1 pp puede ser +100% si CR base es 1 pp

---

## 🎓 Recursos de Aprendizaje

### Para Profundizar

| Tema | Archivo | Nivel |
|------|---------|-------|
| Fórmulas básicas | `docs/metrics-glossary.md` | Básico |
| Query principal | `sql/base-query.sql` | Intermedio |
| Detección de patrones | `calculations/pattern-detection.py` | Avanzado |
| Optimización | `utils/memory-optimization.py` | Experto |

---

## 🤝 Colaboración

### Cómo Contribuir Mejoras

1. **Nuevas queries**: Agregar a `/sql/`
2. **Nuevos cálculos**: Agregar a `/calculations/`
3. **Nueva documentación**: Agregar a `/docs/`
4. **Nuevos ejemplos**: Agregar a `/examples/`

Ver `CONTRIBUTING.md` para detalles.

---

## 📞 Soporte

### Dónde Buscar Ayuda

| Pregunta | Recurso |
|----------|---------|
| "¿Cómo funciona X?" | `docs/business-context.md` |
| "¿Qué significa Y?" | `docs/metrics-glossary.md` |
| "¿Cómo hacer Z?" | `docs/analysis-workflow.md` |
| "Error en query" | `docs/TROUBLESHOOTING.md` |
| "¿Qué es este campo?" | `docs/table-definitions.md` |

---

## 📌 Recordatorios Finales

### Principios Clave

1. **Siempre validar datos** antes de reportar
2. **Contextualizar variaciones** (eventos, estacionalidad)
3. **Usar thresholds apropiados** (50-100 casos)
4. **Documentar hallazgos** para futuras referencias
5. **Iterar análisis** (top-down approach)

---

**Última actualización**: Enero 2026  
**Versión**: 1.0

---

> 💡 **Tip**: Estas son **recomendaciones**, no reglas obligatorias. Adáptalas según tu caso de uso específico.
