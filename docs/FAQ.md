# ❓ FAQ - Preguntas Frecuentes

> **Respuestas rápidas** a las preguntas más comunes sobre Contact Rate Analysis

---

## 📋 Índice

1. [General](#general)
2. [Cálculos](#cálculos)
3. [Queries](#queries)
4. [Commerce Groups](#commerce-groups)
5. [Thresholds](#thresholds)
6. [Errores Comunes](#errores-comunes)
7. [Performance](#performance)

---

## 🌐 General

### ¿Qué es Contact Rate (CR)?

**R:** Contact Rate es la tasa de contacto calculada como:
```
CR = (Incoming Cases / Driver) × 100
```
Representa cuántos casos de contacto se generan por cada 100 unidades del driver (órdenes, transacciones, etc.).

### ¿Para qué sirve este repositorio?

**R:** Este repositorio centraliza toda la lógica, cálculos, queries y contexto para analizar variaciones de Contact Rate en Commerce. Está optimizado para ser consumido por Cursor AI Agent.

### ¿Cuál es la diferencia con el notebook V37.ipynb?

**R:** El notebook es interactivo pero manual. Este repositorio:
- Está estructurado para consumo por AI
- Tiene documentación completa
- Incluye tests y validaciones
- Es más mantenible y escalable

---

## 🧮 Cálculos

### ¿Cómo se calcula el Contact Rate?

**R:** Ver `calculations/contact-rate.py`:
```python
CR = (incoming_cases / driver) * 100
```
- **Incoming**: Casos reportados por clientes
- **Driver**: Métrica de negocio (órdenes, transacciones, etc.)
- **Resultado**: Porcentaje en puntos porcentuales (pp)

### ¿Qué es la variación MoM?

**R:** Month-over-Month (MoM) es el cambio entre dos meses:
```
Variación Absoluta = CR_actual - CR_anterior
Variación % = ((CR_actual - CR_anterior) / CR_anterior) × 100
```

### ¿Cuándo es significativa una variación?

**R:** Según `docs/GUIDELINES.md`:
- **< ±10%**: Variación normal
- **±10-20%**: Variación fuerte (revisar)
- **±20-50%**: Variación crítica (investigar)
- **> ±50%**: Alerta crítica (acción inmediata)

---

## 🔍 Queries

### ¿Cuál es la query principal?

**R:** Ver `sql/base-query.sql`. Es la query base que:
- Extrae datos de `BT_CX_CONTACTS`
- Aplica exclusiones automáticas
- Agrupa por dimensión
- Calcula CR

### 🚨 ¿Cómo filtro correctamente por Commerce Group? (CRÍTICO)

**R:** ⚠️ **NO** filtres por palabras clave en `PROCESS_NAME`. Un Commerce Group es una **categoría de negocio** basada en `PROCESS_PROBLEMATIC_REPORTING`.

**❌ INCORRECTO:**
```python
# NO hagas esto - excluye procesos válidos
df[df['PROCESS_NAME'].str.contains('PDD|Dañado|Defectuoso')]
```

**✅ CORRECTO - Opción 1 (BigQuery):**
```sql
-- Usa la lógica de PROCESS_PROBLEMATIC_REPORTING
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
   OR PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' 
   OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'
```

**✅ CORRECTO - Opción 2 (Python):**
```python
# Usa datos con AGRUP_COMMERCE ya calculado
df_pdd = df[df['AGRUP_COMMERCE'] == 'PDD']
```

**Razón:** "PDD" incluye procesos como "Arrepentimiento" que no contienen "PDD" en su nombre pero pertenecen al Commerce Group según su clasificación de negocio.

📖 **Lee obligatoriamente:** `docs/COMMERCE_GROUPS_REFERENCE.md`

### ¿Por qué MLB necesita sampling?

**R:** Brasil tiene un volumen muy alto de datos. El sampling se aplica cuando se estiman > 150,000 filas. Ver `sql/sampling-strategy.sql`.

---

## 🏢 Commerce Groups

### ¿Cuántos Commerce Groups hay?

**R:** **15 Commerce Groups** en 5 categorías:
- **Post-Compra (2)**: PDD, PNR
- **Shipping (4)**: ME Distribución, ME PreDespacho, FBM Sellers, ME Drivers
- **Marketplace (6)**: Pre Venta, Post Venta, Generales Compra, Moderaciones, Full Sellers, Pagos
- **Pagos (1)**: MP On
- **Cuenta (2)**: Cuenta, Experiencia Impositiva

Ver `docs/commerce-structure.md` para detalles.

### ¿Cómo sé qué Commerce Group usar?

**R:** Depende de tu análisis:
- **Problemas de producto**: PDD, PNR
- **Problemas de envío**: ME Distribución, ME PreDespacho, FBM Sellers
- **Consultas pre/post venta**: Pre Venta, Post Venta
- **Pagos**: MP On, Pagos

### 🚛 ¿Por qué Shipping es diferente a los demás Commerce Groups?

**R:** Porque **Shipping requiere criterios compuestos** (más de un campo para clasificar):

**Post-Compra, Marketplace, Pagos, Cuenta:**
```sql
-- Criterio SIMPLE: Solo PROCESS_PROBLEMATIC_REPORTING
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
```

**Shipping:**
```sql
-- Criterio COMPUESTO: PROCESS_PROBLEMATIC_REPORTING + PROCESS_GROUP_ECOMMERCE
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
  AND PROCESS_GROUP_ECOMMERCE = 'Comprador'  -- ME Distribución
  
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
  AND PROCESS_GROUP_ECOMMERCE = 'Vendedor'   -- ME PreDespacho
```

**¿Por qué?** Porque el **mismo proceso** puede ir a diferentes Commerce Groups según el **User Type** (Comprador vs Vendedor).

**Ejemplo crítico:**
```
PROCESS_NAME: "Reclamo Mercado Envíos - Demora"
├─ Si User Type = Comprador → ME Distribución
└─ Si User Type = Vendedor → ME PreDespacho
```

📖 **Ver ejemplos completos:** `docs/COMMERCE_GROUPS_REFERENCE.md` (Sección "CASO ESPECIAL: Shipping")

---

## 🎯 Thresholds

### ¿Qué es el threshold de 50 casos?

**R:** Es el mínimo de incoming cases para que un proceso sea incluido en el análisis. **Regla validada**:
```
Si la SUMA TOTAL de un PROCESS_NAME es >= 50 casos en CUALQUIER período,
se incluyen TODOS los CDUs de ese proceso.
```

Ver `config/thresholds.py` y `docs/analysis-workflow.md`.

### ¿Por qué mi proceso no aparece en el análisis?

**R:** Posibles razones:
1. **Threshold**: Incoming < 50 en ambos períodos
2. **Exclusiones**: Queue/Process/CI Reason excluido
3. **FLAG_EXCLUDE_NUMERATOR_CR = 1**
4. **Site MLV** (Venezuela está excluido)

Ver `config/business-constants.py` para exclusiones.

### ¿Puedo cambiar el threshold?

**R:** Sí, pero no es recomendado. El threshold de 50 está validado para asegurar significancia estadística. Si necesitas cambiarlo, modifica `MIN_PROCESS_INCOMING` en `config/thresholds.py`.

---

## ❌ Errores Comunes

### Error: "403 Quota exceeded"

**R:** Cambiar prioridad de query a BATCH:
```python
job_config = bigquery.QueryJobConfig(priority="BATCH")
```

### Error: "Division by zero"

**R:** El driver es 0. Verifica:
1. Que el período tenga datos
2. Que el Commerce Group tenga driver configurado
3. Que no haya filtros que excluyan todo

### Error: "No se encontraron datos"

**R:** Verifica:
1. **Fechas**: Formato YYYY-MM
2. **Site**: Código correcto (MLA, MLB, etc.)
3. **Commerce Group**: Filtro correcto
4. **Período**: Que tenga datos en BigQuery

### Error: "UnicodeEncodeError" en Windows

**R:** Agregar al inicio del script:
```python
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## ⚡ Performance

### ¿Cómo optimizo queries lentas?

**R:**
1. **Usa sampling** para MLB (ver `sql/sampling-strategy.sql`)
2. **Limita períodos**: No más de 6 meses
3. **Usa BATCH priority** para queries grandes
4. **Filtra temprano**: Aplica filtros en WHERE, no en HAVING

Ver `utils/memory-optimization.py`.

### ¿Cuánto tarda un análisis típico?

**R:**
- **MLA, MCO, etc.**: 10-30 segundos
- **MLB con sampling**: 30-60 segundos
- **Análisis multi-período**: 1-3 minutos

### ¿Cómo reduzco el uso de memoria?

**R:** Ver `utils/memory-optimization.py`:
```python
df = optimize_dataframe_memory(df)
```
Reduce tipos de datos (int64 → int32, float64 → float32).

---

## 🔧 Uso del Repositorio

### ¿Cómo ejecuto un análisis?

**R:** Usa el script de producción:
```bash
python scripts/run_analysis.py --commerce-group "PDD" --site "MLA" \\
                                --dimension "PROCESS_NAME" \\
                                --period1 "2025-11" --period2 "2025-12"
```

### ¿Cómo creo un script personalizado?

**R:** Copia el template:
```bash
cp templates/analysis_template.py mi_analisis.py
# Edita la sección CONFIGURATION
python mi_analisis.py
```

### ¿Dónde se guardan los resultados?

**R:** Por defecto en `test/outputs/`:
- **CSV**: Datos tabulares
- **HTML**: Reportes visuales

---

## 📚 Documentación

### ¿Dónde encuentro información sobre...?

| Tema | Archivo |
|------|---------|
| **Fórmulas** | `docs/metrics-glossary.md` |
| **Queries** | `sql/base-query.sql` |
| **Commerce Groups** | `docs/commerce-structure.md` |
| **Tablas BigQuery** | `docs/table-definitions.md` |
| **Workflow** | `docs/analysis-workflow.md` |
| **Mejores prácticas** | `docs/GUIDELINES.md` |
| **Estándares de código** | `docs/CODING_STANDARDS.md` |
| **Troubleshooting** | `docs/TROUBLESHOOTING.md` |

### ¿Cómo contribuyo al repositorio?

**R:** Ver `CONTRIBUTING.md` para guías completas.

---

## 🤖 Cursor AI

### ¿Cómo uso este repositorio con Cursor?

**R:**
1. Abre el repositorio en Cursor
2. El archivo `.cursorrules` se carga automáticamente
3. Haz preguntas en lenguaje natural:
   - "¿Cuál es la variación de CR para PDD en MLA en Nov-Dic 2025?"
   - "Muéstrame la query para obtener datos de ME Distribución"
   - "¿Cómo se calcula el Contact Rate?"

### ¿Qué puede hacer Cursor con este repositorio?

**R:** Cursor puede:
- Explicar cálculos y queries
- Generar análisis personalizados
- Responder preguntas sobre el negocio
- Ayudar a debuggear errores
- Sugerir optimizaciones

---

## 🆘 ¿Más Preguntas?

Si tu pregunta no está aquí:

1. **Revisa la documentación**: `/docs/`
2. **Busca en el código**: Usa `grep` o búsqueda de Cursor
3. **Abre un Issue**: En GitHub
4. **Consulta TROUBLESHOOTING.md**: Para problemas técnicos

---

**Última actualización**: Enero 2026  
**Versión**: 3.0.0
