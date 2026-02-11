# 🌟 Golden Template Universal - Modelo Oficial v6.3.4

**Versión:** 6.3.4  
**Fecha:** Febrero 2026  
**Status:** ✅ OFICIAL - ÚNICO TEMPLATE ACTIVO

---

## 🔍 Análisis Comparativo de Patrones (v6.3.4)

### **¿Qué es?**

La sección **"Análisis Comparativo de Patrones por Período"** es el núcleo del análisis cualitativo en v6.3.4. Integra en una sola sección:
- ✅ Comparación temporal de causas raíz (Nov vs Dic)
- ✅ Sentimiento por causa y período
- ✅ Evidencia cualitativa con fechas
- ✅ Insights sobre qué cambió y por qué

### **Estructura de la Tabla Comparativa**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Patrón / Causa Raíz │  Nov 2025        │  Dic 2025        │ Variación      │
│                     │  %, Casos, 😠😊  │  %, Casos, 😠😊  │ Δ Casos, Δ%, Δpp│
├─────────────────────────────────────────────────────────────────────────────┤
│ Nota fiscal inválida│ 25% │ 3,710 │😠70% │ 20% │ 1,947 │😠65% │ -1,763 │...│
│                     │     │       │😊 0% │     │       │😊 0% │        │   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Columnas:**
1. **Patrón/Causa Raíz:** Nombre descriptivo del patrón identificado
2. **Nov 2025:**
   - `%`: Proporción del total de conversaciones muestreadas
   - `Casos`: Casos estimados
   - `Sentimiento`: 😠 Frustración % / 😊 Satisfacción %
3. **Dic 2025:** Mismas métricas
4. **Variación:**
   - `Δ Casos`: Variación absoluta de casos
   - `Δ %`: Variación porcentual
   - `Δ Prop`: Cambio en puntos porcentuales de proporción

### **Evidencia Cualitativa con Fechas**

```html
<div class="evidencia">
    <strong>Reactivaciones exitosas con nota fiscal válida</strong>
    <p>Vendedores que corrigieron su documentación...</p>
    
    <blockquote>
        <span class="case-id">Caso 413661025 (2025-11-02):</span>
        A representante Isa revisou a nota do item e confirmou...
    </blockquote>
</div>
```

**Características:**
- ✅ Top 2 causas visibles por defecto
- ✅ Fecha de cada caso: `(YYYY-MM-DD)`
- ✅ Botón "Ver citas adicionales ▼" para causas 3, 4+
- ✅ Cada cita incluye: CASE_ID, fecha, texto literal

### **Metadata de Cobertura**

```
📊 Conversaciones analizadas: 58 casos (30 Nov + 28 Dic)
   Cobertura: 100% del incoming
```

**Por qué importa:**
- Valida la representatividad del análisis
- Muestra transparencia en el sampling
- Indica si hay gaps de datos

### **Insight Principal**

```
💡 Insight Principal:
La reducción de 5,105 casos (-34.4%) se explica principalmente por:
(1) Menos problemas de documentación inválida (-1,763 casos)
(2) Menos denuncias de marca (-1,058 casos)
Sin embargo, los falsos positivos del sistema aumentaron proporcionalmente...
```

**Generado por:** Análisis LLM (Claude) sobre los datos comparativos

### **Botón Colapsable "Ver citas adicionales"**

**Por defecto:** Muestra solo top 2 causas (las de mayor impacto)

**Al expandir:**
- Muestra causas 3, 4 y adicionales
- Hasta 2 citas por causa adicional
- Mantiene el reporte compacto inicialmente

**JavaScript:**
```javascript
function toggleCitas(procesoid) {
    var elem = document.getElementById('citas_' + procesoid);
    var btn = document.getElementById('btn_' + procesoid);
    if (elem.style.display === 'none') {
        elem.style.display = 'block';
        btn.innerHTML = 'Ocultar citas adicionales ▲';
    } else {
        elem.style.display = 'none';
        btn.innerHTML = 'Ver citas adicionales ▼';
    }
}
```

---

## 💾 Formato JSON del Análisis Comparativo

### **Estructura del Archivo**

**Ubicación:** `output/analisis_conversaciones_comparativo_claude_{site}_{commerce_group}_{p1_mes}_{p2_mes}.json`

**Ejemplo:** `analisis_conversaciones_comparativo_claude_mlb_moderaciones_2025-11_2025-12.json`

### **Schema JSON**

```json
{
  "PR - Propiedad intelectual": {
    "proceso": "PR - Propiedad intelectual",
    "commerce_group": "MODERACIONES",
    "site": "MLB",
    "periodo": "Nov-Dic 2025",
    "incoming_nov": 14839,
    "incoming_dic": 9734,
    "variacion_casos": -5105,
    "variacion_pct": -34.4,
    "conversaciones_nov": 30,
    "conversaciones_dic": 28,
    
    "causas_nov": [
      {
        "causa": "Nota fiscal inválida o CNPJ no coincidente",
        "porcentaje": 25,
        "casos_estimados": 8,
        "descripcion": "Vendedores con nota fiscal...",
        "sentimiento": {
          "frustracion": 70,
          "satisfaccion": 0,
          "alivio": 0
        },
        "citas": [
          {
            "case_id": "413661025",
            "fecha": "2025-11-02",
            "texto": "A representante Isa revisou..."
          }
        ]
      }
    ],
    
    "causas_dic": [
      {
        "causa": "Nota fiscal inválida o CNPJ no coincidente",
        "porcentaje": 20,
        "casos_estimados": 6,
        "descripcion": "...",
        "sentimiento": {
          "frustracion": 65,
          "satisfaccion": 0,
          "alivio": 0
        },
        "citas": [...]
      }
    ],
    
    "analisis_comparativo": {
      "insight_principal": "La reducción de 5,105 casos...",
      "hallazgos_clave": [
        "Menos problemas de documentación inválida (-1,763 casos)",
        "Falsos positivos aumentaron proporcionalmente (60% vs 50%)"
      ]
    }
  }
}
```

### **Campos Obligatorios**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `proceso` | string | Nombre del proceso/elemento |
| `incoming_nov` | int | Incoming total Nov |
| `incoming_dic` | int | Incoming total Dic |
| `variacion_casos` | int | Δ casos (Dic - Nov) |
| `variacion_pct` | float | % variación |
| `conversaciones_nov` | int | Conversaciones analizadas Nov |
| `conversaciones_dic` | int | Conversaciones analizadas Dic |
| `causas_nov` | array | Causas del período Nov |
| `causas_dic` | array | Causas del período Dic |
| `analisis_comparativo.insight_principal` | string | Insight generado por LLM |

### **Estructura de Causa**

```json
{
  "causa": "Nombre descriptivo de la causa raíz",
  "porcentaje": 25,
  "casos_estimados": 8,
  "descripcion": "Explicación detallada...",
  "sentimiento": {
    "frustracion": 70,
    "satisfaccion": 0,
    "alivio": 0
  },
  "citas": [
    {
      "case_id": "413661025",
      "fecha": "2025-11-02",
      "texto": "Cita textual del caso..."
    }
  ]
}
```

**Validaciones:**
- ✅ `casos_estimados` = `round((porcentaje / 100) * total_conversaciones)` ← frecuencia real de la muestra, NO del incoming total
- ✅ Suma de `porcentaje` ≈ 100% (±5% tolerancia)
- ✅ `sentimiento.frustracion + satisfaccion + alivio` ≈ 100%
- ✅ Mínimo 1 cita por causa (hasta 3 citas máximo)
- ✅ Formato fecha: `YYYY-MM-DD`

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [¿Por qué un Template Universal?](#por-qué-un-template-universal)
3. [Template Universal v6.3.4](#template-universal-v634)
4. [Mejoras en v6.3.4](#mejoras-en-v634)
5. [Análisis Comparativo de Patrones](#análisis-comparativo-de-patrones-v634)
6. [Formato JSON del Análisis Comparativo](#formato-json-del-análisis-comparativo)
7. [Cómo Generar el Análisis Comparativo](#cómo-generar-el-análisis-comparativo)
8. [Uso y Ejemplos](#uso-y-ejemplos)
9. [Características Técnicas](#características-técnicas)
10. [Migración desde Golden Templates Antiguos](#migración-desde-golden-templates-antiguos)

---

## 📖 Introducción

El **Golden Template Universal v6.2** es el **único template oficial** para generar reportes de Contact Rate (CR) en Commerce. Este template unifica y supera todas las funcionalidades de los Golden Templates específicos (PDD, PNR) que existían anteriormente.

**Filosofía:**
> Un template único, completamente parametrizable, que genera reportes de calidad Golden Template para cualquier site, commerce group, período y dimensión de análisis.

---

## 🎯 ¿Por qué un Template Universal?

### **Problema con Golden Templates Específicos (v3.9 - v4.0)**

Antes existían **6 templates diferentes**:
- `generar_golden_pdd_mla.py`
- `generar_golden_pdd_mla_tipificacion.py`
- `generar_golden_pdd_mlb_tipificacion.py`
- `generar_golden_pnr_mlb.py`
- `generar_reporte_cr_universal_v6.py`

**❌ Problemas:**
- Duplicación masiva de código (80-90% idéntico)
- Mantenimiento complejo (cambios en 6 lugares)
- Parámetros fijos (Nov-Dic 2025 hardcoded)
- Keywords manuales por idioma
- Inconsistencias entre templates
- Bugs propagados entre versiones

### **Solución: Template Universal v6.2**

**✅ Ventajas:**
- **Código único:** 1 script = 1 punto de mantenimiento
- **Parametrización completa:** Site, períodos, commerce group, dimensiones
- **Consistencia garantizada:** Todos los reportes usan la misma lógica
- **Features superiores:** LLM analysis, hard metrics, eventos dinámicos
- **Más fácil de evolucionar:** Nuevas features se agregan 1 sola vez

---

## 🚀 Template Universal v6.3.4

### **Archivo Oficial**

```bash
generar_reporte_cr_universal_v6.3.py
```

### **Estructura del Reporte**

```
1. Resumen Ejecutivo (3 bullets con evidencia)
2. Cards Ejecutivas (8) + Gráfico Semanal
3. Eventos Comerciales (si hay hard metrics)
4. Cuadros Cuantitativos por Dimensión
5. Análisis Comparativo de Patrones ENRIQUECIDO
   ├─ Insight principal (qué explica la variación)
   ├─ Metadata (conversaciones, cobertura)
   ├─ Tabla comparativa con sentimiento Nov vs Dic
   ├─ Evidencia con fechas (top 2 causas)
   └─ Botón "Ver más citas" (causas adicionales)
6. Footer Técnico Colapsable
```

---

## 🆕 Mejoras en v6.3.4

**Versión 6.3.4 implementa 9 mejoras críticas que hacen el sistema verdaderamente universal:**

### **1. ✅ Dimensión de Muestreo Dinámica** (CRÍTICO)
- Ya no asume que siempre se usa CDU
- Se adapta automáticamente a la dimensión solicitada (PROCESO, TIPIFICACION, etc.)
- Path de archivos dinámico: `cuadro_{dimension}_{site}.csv`

### **2. ✅ Búsqueda Inteligente de CSVs** (CRÍTICO)
- Maneja nombres con caracteres especiales (/, -, espacios)
- Usa regex robusto para extraer períodos
- Normaliza nombres antes de buscar archivos

### **3. ✅ División de Citas por Fecha Real**
- Asigna cada cita al período correcto según su fecha
- Ya no divide 50-50 arbitrariamente
- Fallback inteligente si falta información de fecha

### **4. ✅ Validación de Coherencia**
- Detecta inconsistencias entre JSON y cuadros cuantitativos
- Usa valores por defecto si falta información
- Continúa generación con advertencias claras

### **5. ✅ Fechas Dinámicas**
- Ya no hardcodea Nov-Dic en fechas por defecto
- Se adapta automáticamente a los períodos solicitados
- Distribución inteligente entre P1 y P2

### **6. ✅ Insights Completos**
- No trunca información a 150 caracteres
- Contexto adicional para variaciones pequeñas
- Mejor comprensión de patrones

### **7. ✅ Control de Errores Robusto**
- Diagnóstico detallado cuando algo falla
- Identifica rápidamente archivos faltantes
- El reporte continúa sin análisis comparativo si hay error

### **8. ✅ Path del Script Robusto**
- Importaciones más estables
- Funciona desde cualquier ubicación
- Evita duplicados en sys.path

### **9. ✅ Encoding UTF-8 para Windows**
- Soluciona UnicodeEncodeError en PowerShell
- Soporta emojis y caracteres Unicode
- Fallback graceful si el encoding falla

**Referencia completa:** [`docs/CHANGELOG_v6.3.4.md`](CHANGELOG_v6.3.4.md)

---

### **Uso Básico**

```bash
python generar_reporte_cr_universal_v6.3.py \
    --site [SITE] \
    --p1-start [FECHA_INICIO_P1] \
    --p1-end [FECHA_FIN_P1] \
    --p2-start [FECHA_INICIO_P2] \
    --p2-end [FECHA_FIN_P2] \
    --commerce-group [GRUPO] \
    --aperturas [DIMENSIONES]
```

### **Parámetros Disponibles**

| Parámetro | Descripción | Ejemplo | Obligatorio |
|-----------|-------------|---------|-------------|
| `--site` | Site a analizar | `MLA`, `MLB`, `MCO` | ✅ |
| `--p1-start` | Fecha inicio período 1 | `2025-11-01` | ✅ |
| `--p1-end` | Fecha fin período 1 | `2025-11-30` | ✅ |
| `--p2-start` | Fecha inicio período 2 | `2025-12-01` | ✅ |
| `--p2-end` | Fecha fin período 2 | `2025-12-31` | ✅ |
| `--commerce-group` | Commerce group | `PDD`, `PNR`, `PCF` | ✅ |
| `--aperturas` | Dimensiones (separadas por coma) | `PROCESO,CDU,TIPIFICACION` | ✅ |
| `--process-name` | Filtro opcional de proceso | `Arrepentimiento` | ❌ |
| `--output-dir` | Directorio de salida | `output/custom/` | ❌ |
| `--open-report` | Abrir reporte automáticamente | (flag) | ❌ |
| `--skip-conversations` | Saltar análisis conversaciones | (flag) | ❌ |
| `--muestreo-dimension` | Dimensión para muestreo | `TIPIFICACION` | ❌ |

### **Dimensiones Soportadas**

El template soporta **7 dimensiones diferentes**:

1. **PROCESO** - Análisis por `PROCESS_NAME`
2. **CDU** - Análisis por Caso de Uso
3. **TIPIFICACION** - Análisis por `REASON_DETAIL_GROUP_REPORTING`
4. **ENVIRONMENT** - Análisis por ambiente (DS, FBM, FLEX, XD)
5. **SOLUTION_ID** - Análisis por tipo de solución
6. **CHANNEL_ID** - Análisis por canal de contacto
7. **SOURCE_ID** - Análisis por fuente (IVR, CHAT, FORM, etc.)

---

## 🎬 Cómo Generar el Análisis Comparativo

### **Flujo Completo (3 Pasos)**

#### **Paso 1: Exportar Conversaciones (--export-only)**

```bash
py generar_reporte_cr_universal_v6.3.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group MODERACIONES \
    --aperturas PROCESO,CDU \
    --export-only
```

**Resultado:**
```
output/
  ├─ conversaciones_PR_-_Propiedad_intelectual_mlb_202511.csv (30 Nov + 29 Dic)
  ├─ conversaciones_PR_-_Técnica_prohibida_mlb_202511.csv
  └─ conversaciones_PR_-_Artículos_prohibidos_mlb_202511.csv
```

**Qué hace:**
- ✅ Ejecuta muestreo de conversaciones (30 por elemento-período)
- ✅ Exporta CSVs con `CASE_ID`, `CONTACT_DATE_ID`, `CONVERSATION_SUMMARY`
- ✅ NO genera HTML (solo preparación de datos)

---

#### **Paso 2: Analizar con Cursor AI (LLM)**

**A) Separar conversaciones por período**

Usar el script `temp_analisis_por_periodo.py` (o manualmente en Cursor):

```python
# Ejemplo simplificado
import pandas as pd

# Cargar CSV completo
df = pd.read_csv('output/conversaciones_PR_-_Propiedad_intelectual_mlb_202511.csv')

# Separar por período
df['month'] = pd.to_datetime(df['CONTACT_DATE_ID']).dt.month
df_nov = df[df['month'] == 11]
df_dic = df[df['month'] == 12]

# Exportar
df_nov.to_csv('temp_PR_Propiedad_intelectual_NOV.csv', index=False)
df_dic.to_csv('temp_PR_Propiedad_intelectual_DIC.csv', index=False)
```

**B) Prompt para Cursor AI**

```markdown
Analiza las siguientes conversaciones de [PROCESO] para [SITE] [MES]:

**Contexto:**
- Incoming Nov: 14,839 casos
- Incoming Dic: 9,734 casos
- Variación: -5,105 casos (-34.4%)

**CSV Nov:** [30 conversaciones]
**CSV Dic:** [28 conversaciones]

**Tarea:**
1. Identifica las causas raíz principales (cobertura ≥80%)
2. Para cada causa:
   - Nombre descriptivo
   - Porcentaje del incoming
   - Casos estimados
   - Descripción (1-2 líneas)
   - Sentimiento (% frustración, satisfacción, alivio)
   - 1-3 citas textuales con CASE_ID y fecha
3. Genera insight principal comparando Nov vs Dic

**Output:** JSON estructurado según schema (ver sección anterior)
```

**C) Guardar resultado**

```bash
output/analisis_conversaciones_comparativo_claude_mlb_moderaciones_2025-11_2025-12.json
```

---

#### **Paso 3: Regenerar Reporte Completo**

```bash
py generar_reporte_cr_universal_v6.3.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group MODERACIONES \
    --aperturas PROCESO,CDU \
    --open-report
```

**Qué hace:**
- ✅ Detecta que existe `analisis_conversaciones_comparativo_claude_...json`
- ✅ Carga el análisis pre-generado
- ✅ Genera HTML completo con análisis comparativo enriquecido
- ✅ Abre reporte automáticamente

**Resultado:**
```
output/reporte_cr_moderaciones_mlb_nov_dec_2025_v6.3.html
```

---

### **Flujo Automático con Pre-verificación**

El script v6.3.4 implementa **pre-verificación automática**:

```python
# Dentro de generar_reporte_cr_universal_v6.3.py
analisis_json_name = f"analisis_conversaciones_comparativo_claude_{site}_{commerce_group}_{p1_mes}_{p2_mes}.json"
analisis_json_path = Path("output") / analisis_json_name

if analisis_json_path.exists():
    # ✅ Análisis ya existe → Genera reporte directamente (1 paso)
    generar_html_completo()
else:
    # ⚠️ Análisis no existe → Exportar CSVs primero (usar --export-only)
    if args.export_only:
        exportar_csvs()
        print("[INFO] CSVs exportados. Siguiente paso: analizar con LLM")
    else:
        print("[ERROR] No se encontró análisis comparativo. Ejecutar con --export-only primero")
```

**Beneficio:** Si el análisis ya existe, un solo comando regenera el reporte completo.

---

### **Script Helper: Mapeo de Fechas**

Para agregar fechas a citas ya existentes en el JSON:

```python
# temp_agregar_fechas_a_citas.py
import json
import pandas as pd
from pathlib import Path

# Cargar JSON
json_path = Path("output/analisis_conversaciones_comparativo_claude_mlb_moderaciones_2025-11_2025-12.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Para cada proceso
for proceso_key, proceso_data in data.items():
    # Cargar CSVs del proceso
    csv_nov = Path(f"output/temp_{proceso_key}_NOV.csv")
    csv_dic = Path(f"output/temp_{proceso_key}_DIC.csv")
    
    df_nov = pd.read_csv(csv_nov)
    df_dic = pd.read_csv(csv_dic)
    
    # Mapear fechas a citas Nov
    for causa in proceso_data['causas_nov']:
        for cita in causa['citas']:
            case_id = cita['case_id']
            fecha = df_nov[df_nov['CAS_CASE_ID'] == case_id]['CONTACT_DATE_ID'].iloc[0]
            cita['fecha'] = pd.to_datetime(fecha).strftime('%Y-%m-%d')
    
    # Mapear fechas a citas Dic
    for causa in proceso_data['causas_dic']:
        for cita in causa['citas']:
            case_id = cita['case_id']
            fecha = df_dic[df_dic['CAS_CASE_ID'] == case_id]['CONTACT_DATE_ID'].iloc[0]
            cita['fecha'] = pd.to_datetime(fecha).strftime('%Y-%m-%d')

# Guardar JSON actualizado
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Fechas agregadas a {len(data)} procesos")
```

---

## 💡 Uso y Ejemplos

### **Ejemplo 1: Reporte PDD MLA (reemplazo de Golden PDD MLA)**

**ANTES (deprecated):**
```bash
python generar_golden_pdd_mla_tipificacion.py
```

**AHORA (v6.3.4):**
```bash
python generar_reporte_cr_universal_v6.3.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

**Output:** `output/reporte_cr_pdd_mla_nov_dec_2025_v6.3.html`

---

### **Ejemplo 2: Reporte PNR MLB (reemplazo de Golden PNR MLB)**

**ANTES (deprecated):**
```bash
python generar_golden_pnr_mlb.py
```

**AHORA (v6.3.4):**
```bash
python generar_reporte_cr_universal_v6.3.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PNR \
    --aperturas TIPIFICACION \
    --open-report
```

---

### **Ejemplo 3: Análisis por Múltiples Dimensiones**

```bash
python generar_reporte_cr_universal_v6.3.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas PROCESO,CDU,TIPIFICACION \
    --open-report
```

**Output:** Reporte con **3 tablas** (1 por dimensión)

---

### **Ejemplo 4: Análisis con Filtro de Proceso**

```bash
python generar_reporte_cr_universal_v6.3.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --process-name "Arrepentimiento" \
    --open-report
```

**Output:** Solo casos de "Arrepentimiento"

---

### **Ejemplo 5: Análisis Cross-Commerce Group**

```bash
# Analizar PCF Comprador (Post-Compra)
python generar_reporte_cr_universal_v6.3.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group "PCF_COMPRADOR" \
    --aperturas PROCESO,TIPIFICACION \
    --open-report
```

---

### **Ejemplo 6: Exportar CSVs para Análisis Manual**

```bash
# Paso 1: Exportar conversaciones
python generar_reporte_cr_universal_v6.3.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group MODERACIONES \
    --aperturas PROCESO,CDU \
    --export-only

# Paso 2: Analizar con Cursor AI (manual)
# Paso 3: Regenerar reporte completo
python generar_reporte_cr_universal_v6.3.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group MODERACIONES \
    --aperturas PROCESO,CDU \
    --open-report
```

---

## 🔧 Características Técnicas

### **1. Hard Metrics con Fallback Automático**

```python
# Intenta cargar hard metrics
df_metrics_p1 = cargar_hard_metrics(site, year1, month1)
df_metrics_p2 = cargar_hard_metrics(site, year2, month2)

if df_metrics_p1 and df_metrics_p2:
    # ✅ Usa métricas precalculadas (100% precisión, 16x más rápido)
    use_hard_metrics = True
else:
    # ⚠️ Fallback: calcula en tiempo real sobre muestra
    use_hard_metrics = False
```

**Beneficios:**
- ✅ Reportes siempre funcionan (con o sin hard metrics)
- ✅ Performance óptimo cuando hard metrics disponibles
- ✅ Footer indica qué método se usó

**Documentación:** `metrics/GUIA_USUARIO.md`

---

### **2. Análisis de Conversaciones con LLM (Claude)**

```python
# Carga análisis pre-generado de Claude (Cursor AI)
if os.path.exists('output/analisis_conversaciones_claude.json'):
    with open('output/analisis_conversaciones_claude.json') as f:
        analisis_claude = json.load(f)
    # ✅ Usa análisis de Claude: causas raíz, frecuencia, sentimiento, citas
else:
    # ⚠️ Fallback: exporta CSVs para análisis manual
    export_csv_for_manual_analysis()
```

**Características del análisis LLM:**
- ✅ **Causas raíz específicas** (no genéricas)
- ✅ **Frecuencia/porcentaje** por causa
- ✅ **Citas textuales** con `CASE_ID`
- ✅ **Sentimiento** (frustración/satisfacción)
- ✅ **Cobertura ≥80%** garantizada
- ✅ **Badges "DÍA PICO/TÍPICO"** para contexto

**Template de prompt:** `templates/prompt_analisis_conversaciones.md`

---

### **3. Eventos Comerciales Dinámicos**

```python
# Carga eventos desde tabla oficial
eventos = obtener_eventos_comerciales(
    client=bq_client,
    site=site,
    periodo=periodo
)
# Fuente: WHOWNER.LK_MKP_PROMOTIONS_EVENT
```

**Ventajas vs hardcoded:**
- ✅ Fechas reales del calendario comercial
- ✅ Se actualiza automáticamente
- ✅ Incluye eventos específicos por site
- ✅ Rangos completos (fecha_inicio → fecha_fin)

**Documentación:** `metrics/eventos/FUENTE_EVENTOS.md`

---

### **4. Resumen Ejecutivo Estructurado**

```html
<div class="executive-summary">
    <h2>📊 Resumen Ejecutivo</h2>
    <ul>
        <li>• CR pasó de X.XX pp a Y.YY pp (+Z.ZZ pp, ↑W%)</li>
        <li>• Principal causa: [CAUSA] (+N casos, +P%)</li>
        <li>• Picos detectados: [FECHA] (evento X)</li>
    </ul>
</div>
```

**Regla:** 3 bullets máximo (pirámide invertida)

---

### **5. Metadata Técnica Completa**

```html
<div class="metadata-footer" style="display:none">
    <h3>⚙️ Metadata Técnica del Reporte</h3>
    
    <h4>📋 Configuración</h4>
    <ul>
        <li>Site: MLA | Commerce Group: PDD</li>
        <li>Períodos: 2025-11 vs 2025-12</li>
        <li>Dimensiones: TIPIFICACION</li>
    </ul>
    
    <h4>📊 Métricas Calculadas</h4>
    <ul>
        <li>Fórmula CR: (Incoming / Driver) × 100</li>
        <li>Driver: Órdenes totales (GLOBAL)</li>
        <li>Hard Metrics: ✅ ACTIVAS</li>
    </ul>
    
    <h4>🔍 Queries Ejecutadas</h4>
    <ol>
        <li><strong>Incoming P1:</strong> BT_CX_CONTACTS filtrado...</li>
        <li><strong>Drivers P1:</strong> BT_ORD_ORDERS globales...</li>
        <li><strong>Hard Metrics P1:</strong> Cargado desde Parquet...</li>
    </ol>
</div>
```

**Beneficio:** Trazabilidad completa del análisis

---

### **6. Regla del 80% (Priorización Automática)**

```python
# Identificar elementos que explican 80%+ de la variación
contribucion_acum = 0
elementos_priorizados = []

for elemento in elementos_ordenados:
    contribucion_acum += abs(elemento['delta_incoming']) / abs(delta_total)
    elementos_priorizados.append(elemento)
    
    if contribucion_acum >= 0.80:
        break

# Solo profundizar en elementos priorizados
for elemento in elementos_priorizados:
    analizar_conversaciones(elemento)
    detectar_picos(elemento)
```

**Beneficio:** Foco en lo que realmente importa

---

### **7. Peak Detection por Elemento**

```python
# Detectar picos para cada elemento priorizado (regla 80%)
for elemento in elementos_priorizados:
    picos = detectar_picos_temporales(
        df=df_elemento,
        threshold_multiplier=1.5
    )
    
    if len(picos) > 0:
        # Muestreo ponderado: 70% casos de días pico + 30% resto
        muestrar_conversaciones(elemento, picos)
```

**Template SQL:** `sql/templates/peak_detection_template.sql`

---

### **8. Estructura HTML Golden Template v6.3.4**

```html
<!-- 1. Header -->
<div class="header">
    <h1>Reporte CR [COMMERCE_GROUP] [SITE]</h1>
    <p>[P1] vs [P2]</p>
</div>

<!-- 2. Resumen Ejecutivo (3 bullets con evidencia cualitativa) -->
<div class="executive-summary">
    <ul>
        <li>• CR empeoró/mejoró +X.XX pp (+Y%) | Nov: X.XX pp → Dic: Y.YY pp</li>
        <li>• [ELEMENTO] lidera (X% contrib, +Y casos) | Causa: [CAUSA] (Z% casos) - [DESC]</li>
        <li>• [ELEMENTO_2] muestra mayor crecimiento/reducción (+X%) | Causa crítica: [CAUSA]</li>
    </ul>
</div>

<!-- 3. Cards Ejecutivas (8 cards) -->
<div class="cards-container">
    <!-- Incoming P1, P2, Var | Driver P1, P2 | CR P1, P2, Var -->
</div>

<!-- 4. Gráfico Semanal (14+ semanas) -->
<div class="chart-container">
    <canvas id="weeklyChart"></canvas>
</div>

<!-- 5. Eventos Comerciales (si hard metrics disponibles) -->
<div class="eventos-table">...</div>

<!-- 6. Tablas Cuantitativas (1 por dimensión) -->
<table class="data-table">
    <!-- PROCESO, CDU, TIPIFICACION, etc. -->
</table>

<!-- 7. ANÁLISIS COMPARATIVO ENRIQUECIDO (v6.3.4) ⭐ -->
<div class="section">
    <h2>🔍 Análisis Comparativo de Patrones por Período</h2>
    
    <!-- Por cada proceso priorizado -->
    <div class="proceso-analisis">
        <h3>🔹 [PROCESO]</h3>
        <p>📊 Conversaciones: X casos (Y Nov + Z Dic) | Cobertura: W%</p>
        
        <!-- Insight principal -->
        <div class="insight">
            <strong>💡 Insight Principal:</strong>
            <p>[Texto generado por LLM explicando qué cambió y por qué]</p>
        </div>
        
        <!-- Tabla comparativa con sentimiento -->
        <table>
            <thead>
                <tr>
                    <th>Patrón/Causa</th>
                    <th colspan="3">Nov 2025</th>
                    <th colspan="3">Dic 2025</th>
                    <th>Var</th>
                </tr>
                <tr>
                    <th></th>
                    <th>%</th><th>Casos</th><th>Sentimiento</th>
                    <th>%</th><th>Casos</th><th>Sentimiento</th>
                    <th>Δ Casos</th><th>Δ %</th><th>Δ pp</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Nota fiscal inválida</td>
                    <td>25%</td><td>3,710</td><td>😠70% 😊0%</td>
                    <td>20%</td><td>1,947</td><td>😠65% 😊0%</td>
                    <td>-1,763</td><td>-47.5%</td><td>-5pp</td>
                </tr>
            </tbody>
        </table>
        
        <!-- Evidencia cualitativa con fechas -->
        <div class="evidencia">
            <h4>📌 Evidencia Cualitativa con Citas</h4>
            
            <!-- Top 2 causas (siempre visibles) -->
            <div class="cita-card">
                <strong>Reactivaciones exitosas...</strong>
                <p>Descripción de la causa</p>
                <blockquote>
                    <span class="case-id">Caso 413661025 (2025-11-02):</span>
                    Texto literal de la conversación...
                </blockquote>
            </div>
            
            <!-- Botón colapsable para más citas -->
            <button onclick="toggleCitas('proceso_id')">
                Ver citas adicionales ▼
            </button>
            
            <div id="citas_proceso_id" style="display:none">
                <!-- Causas 3, 4, etc. -->
            </div>
        </div>
    </div>
</div>

<!-- 8. Metadata Técnica (collapsible) -->
<div class="footer-container">
    <button class="footer-toggle" onclick="toggleFooter()">
        📋 Metadata Técnica del Reporte v6.3.4
    </button>
    <div class="footer-content" id="footerContent">
        <!-- Configuración, métricas, queries ejecutadas -->
    </div>
</div>
```

**Evolución de versiones:**
- **v6.2:** Análisis comparativo básico
- **v6.3.2:** Análisis enriquecido con sentimiento + fechas + botón colapsable
- **v6.3.4:** Sistema verdaderamente universal - se adapta a cualquier dimensión, período y commerce group

---

## 🎨 Colores por Commerce Group

| Commerce Group | Color Primario | Hex | Uso |
|----------------|----------------|-----|-----|
| PDD | Rojo | `#f44336` | Producto Dañado/Defectuoso |
| PNR | Naranja | `#ff9800` | Producto No Recibido |
| PCF Comprador | Verde | `#00a650` | Post-Compra Comprador |
| PCF Vendedor | Verde Oscuro | `#008040` | Post-Compra Vendedor |
| Marketplace | Azul | `#2196f3` | Commerce Groups Marketplace |
| Shipping | Morado | `#9c27b0` | ME Distribución, PreDespacho |

---

## 🔄 Migración desde Golden Templates Antiguos

### **Tabla de Equivalencias**

| Golden Template Antiguo | Comando Equivalente v6.3.4 |
|-------------------------|--------------------------|
| `generar_golden_pdd_mla.py` | `--site MLA --commerce-group PDD --aperturas TIPIFICACION` |
| `generar_golden_pdd_mla_tipificacion.py` | `--site MLA --commerce-group PDD --aperturas TIPIFICACION` |
| `generar_golden_pdd_mlb_tipificacion.py` | `--site MLB --commerce-group PDD --aperturas TIPIFICACION` |
| `generar_golden_pnr_mlb.py` | `--site MLB --commerce-group PNR --aperturas TIPIFICACION` |
| `generar_reporte_cr_universal_v6.py` | `generar_reporte_cr_universal_v6.3.py` (v6.3.4) |

---

### **Scripts Wrapper (Opcional)**

Si necesitas mantener comandos simples tipo "Golden Template", puedes crear wrappers:

**Ejemplo: `ejemplos/ejecutar_reporte_pdd_mla.ps1`**

```powershell
# Golden Template PDD MLA - Wrapper para v6.3.4
$p1_start = "2025-11-01"
$p1_end = "2025-11-30"
$p2_start = "2025-12-01"
$p2_end = "2025-12-31"

python generar_reporte_cr_universal_v6.3.py `
    --site MLA `
    --p1-start $p1_start --p1-end $p1_end `
    --p2-start $p2_start --p2-end $p2_end `
    --commerce-group PDD `
    --aperturas TIPIFICACION `
    --open-report

Write-Host "✅ Reporte PDD MLA generado exitosamente"
```

**Uso:**
```powershell
.\ejemplos\ejecutar_reporte_pdd_mla.ps1
```

---

## 📚 Documentación Relacionada

### **Sistema de Hard Metrics**
- ⭐ **`metrics/GUIA_USUARIO.md`** - Guía práctica de hard metrics
- **`metrics/eventos/FUENTE_EVENTOS.md`** - Tabla oficial de eventos
- **`metrics/eventos/CUANDO_REGENERAR.md`** - Cuándo regenerar métricas

### **Análisis de Conversaciones**
- **`templates/prompt_analisis_conversaciones.md`** - Prompt LLM estructurado
- **`sql/templates/muestreo_unificado_template.sql`** - Query de muestreo

### **Estructura de Reportes**
- **`docs/REPORT_STRUCTURE.md`** - Estructura HTML oficial
- **`docs/COMMERCE_GROUPS_REFERENCE.md`** - Commerce groups completos

### **Reglas Críticas**
- **`.cursorrules`** - Reglas obligatorias del repositorio
- **`docs/GUIDELINES.md`** - Mejores prácticas

---

## 🎯 Mejoras Futuras

**Roadmap v6.5+:**
- [ ] Análisis de verticales y dominios (PDD/PNR)
- [ ] Soporte para análisis multi-site en un solo reporte
- [ ] Integración directa con API de Claude para análisis on-demand
- [ ] Export a PDF además de HTML
- [ ] Dashboard interactivo con filtros dinámicos
- [ ] Análisis de tendencias (comparación 3+ meses)

**Completado en v6.3.4:**
- [x] Sistema verdaderamente universal (cualquier dimensión/período/commerce group)
- [x] Dimensión de muestreo dinámica
- [x] Búsqueda inteligente de CSVs con caracteres especiales
- [x] División de citas por fecha real (no 50-50)
- [x] Validación de coherencia JSON vs cuadros
- [x] Fechas dinámicas (no hardcoded Nov-Dic)
- [x] Insights completos sin truncar
- [x] Control de errores robusto con diagnóstico
- [x] Encoding UTF-8 para Windows PowerShell
- [x] 100% backward compatible

---

## 📞 Soporte

**¿Necesitas ayuda?**

1. **Consulta la documentación:**
   - `README.md` (raíz del repositorio)
   - `metrics/GUIA_USUARIO.md` (hard metrics)
   - `docs/REPORT_STRUCTURE.md` (estructura HTML)
   - **`docs/GOLDEN_TEMPLATES.md`** (este documento - guía completa v6.3.2)

2. **Revisa ejemplos:**
   - Sección "Uso y Ejemplos" en este documento
   - `ejemplos/` (scripts wrapper)

3. **Contacta al equipo:**
   - CR Analytics Team
   - Mantenedor del repositorio

---

**Última actualización:** 2 de Febrero de 2026  
**Versión:** 6.3.4  
**Status:** ✅ ÚNICO TEMPLATE OFICIAL - VERSIÓN MÁS ROBUSTA Y UNIVERSAL  
**Reemplazo de:** Golden Templates v3.9, v4.0, v6.0-v6.3.2 (archivados en `_archived_templates/`)  
**Changelog completo:** [`docs/CHANGELOG_v6.3.4.md`](CHANGELOG_v6.3.4.md)
