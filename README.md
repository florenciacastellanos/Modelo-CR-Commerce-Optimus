# 📊 Contact Rate Analysis Repository

> **Sistema Universal v6.3.4** - Framework completo para análisis de Contact Rate en Commerce (Mercado Libre)

## 🎯 Propósito

Repositorio centralizado con lógica, cálculos, queries SQL y contexto para análisis de Contact Rate (CR) en operaciones de Commerce. Diseñado para generar reportes automatizados completos con análisis cualitativo y cuantitativo.

---

## ⚡ Quick Start (v6.3.4)

```bash
# Generar reporte completo en 1 comando
py generar_reporte_cr_universal_v6.3.6.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas PROCESO,CDU \
    --open-report
```

**Resultado:** Reporte HTML en `output/` con:
- 📊 Métricas consolidadas (incoming, drivers, CR)
- 📈 Gráfico semanal evolutivo
- 🔍 Drill-down por dimensiones
- 💬 Análisis cualitativo de conversaciones
- 🔄 Análisis comparativo automático (período 1 vs período 2)
- 🎯 Correlación con eventos comerciales

---

## 🆕 Novedades v6.3.4 (Febrero 2026)

### **✨ Sistema Verdaderamente Universal**

1. **Soporta cualquier dimensión de análisis:**
   - ✅ PROCESO, CDU, TIPIFICACION
   - ✅ ENVIRONMENT, SOLUTION_ID, CHANNEL_ID
   - ✅ SOURCE_ID, CLA_REASON_DETAIL
   - ✅ Cualquier dimensión futura

2. **Generación automática de análisis comparativo:**
   - Sin intervención manual
   - Divide citas por fecha real
   - Compara patrones entre períodos

3. **Encoding UTF-8 robusto para Windows:**
   - No más `UnicodeEncodeError`
   - Soporta emojis y caracteres especiales
   - Fallback graceful

4. **Control de errores mejorado:**
   - Diagnóstico detallado cuando falla
   - Identifica archivos faltantes
   - Continúa con análisis básico si falta comparativo

### **📊 Validado con:**
- 3 dimensiones (CDU, ENVIRONMENT, TIPIFICACION)
- 2 sites (MLA, MLM)
- 3 commerce groups (PDD, PNR, MODERACIONES)
- 100% funcional

**Changelog completo:** [`docs/CHANGELOG_v6.3.4.md`](docs/CHANGELOG_v6.3.4.md)

---

## ⭐ Features Principales v6.3.4

### 1. **Template Universal Adaptable**
- Se adapta automáticamente a cualquier filtro
- No requiere configuración adicional
- Funciona con cualquier site/commerce group/dimensión

### 2. **Análisis Comparativo Automático**
- Genera JSON comparativo desde análisis básico
- Muestra patrones que cambiaron entre períodos
- Incluye sentimiento, citas y frecuencias

### 3. **Hard Metrics Integradas** (v4.0)
- Correlación con eventos comerciales
- Incoming por evento (100% precisión)
- 16x más rápido que muestreo

---

## ⭐ Sistema de Detección Automática de Dimensiones (v5.0)

El agente identifica automáticamente en qué dimensión se encuentra un valor:

```python
from utils.dimension_detector import DimensionDetector

detector = DimensionDetector()
result = detector.detect_and_lookup("Pre Compra")

# Resultado: {'found': True, 'dimension': 'PROCESO', 'commerce_groups': ['Generales Compra']}
```

**Beneficios:**
- ⚡ **99% más rápido:** 0.1 segundos vs 2-3 minutos
- 🎯 **50% menos interacciones:** Confirmación directa
- 🧠 **Fuzzy matching:** Sugiere valores similares
- 📊 **568 valores mapeados**

**Documentación:** [`docs/DIMENSION_DETECTOR_GUIDE.md`](docs/DIMENSION_DETECTOR_GUIDE.md)

---

## 🚨 REGLAS CRÍTICAS

### 1. Clasificación de Commerce Groups (v3.5)

> **⚠️ CRÍTICO:** Usar CASE statement para clasificar Commerce Groups. NO usar filtros simples de texto.

**✅ MÉTODO CORRECTO (v3.5+):**
```sql
-- Clasificar primero, filtrar después
CASE 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD' 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD' 
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR'  
    WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
         AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'PCF Comprador'
    WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
         AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'PCF Vendedor'
    ELSE 'OTRO' 
END AS AGRUP_COMMERCE_PROPIO

WHERE AGRUP_COMMERCE_PROPIO = 'PDD'
```

**❌ INCORRECTO (deprecado):**
```sql
WHERE PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'  -- Pierde "Conflict Others" (~2% casos)
```

**📖 Documentación completa:** [`docs/COMMERCE_GROUPS_REFERENCE.md`](docs/COMMERCE_GROUPS_REFERENCE.md)

**Razón:** El CASE captura casos especiales como "Conflict Others" → PDD y "Conflict Stale" → PNR que un filtro simple pierde.

**Validado:** Enero 2026 - 100% alineado con queries de producción

### 2. Campo de Fecha para Incoming

> **⚠️ CRÍTICO:** SIEMPRE usar `DATE_TRUNC(CONTACT_DATE_ID, MONTH)` para calcular incoming. NUNCA usar `OFC_MONTH_ID` a menos que se solicite explícitamente.

**Ejemplo:**
```sql
-- ✅ CORRECTO
WHERE DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')

-- ❌ INCORRECTO (usar solo si se solicita explícitamente)
WHERE C.OFC_MONTH_ID IN (202511, 202512)
```

**📖 Documentación completa:** [`docs/DATE_FIELD_RULE.md`](docs/DATE_FIELD_RULE.md)

**Razón:** `CONTACT_DATE_ID` representa la fecha real del contacto y coincide 100% con los reportes oficiales de producción. `OFC_MONTH_ID` puede causar diferencias del 3-10% en los casos.

**Validado:** Enero 2026 con datos reales de PDD MLA

### 3. Filtros Base para Órdenes (Drivers)

> **⚠️ CRÍTICO:** SIEMPRE aplicar filtros base obligatorios al calcular drivers desde `BT_ORD_ORDERS`.

**Filtros base obligatorios:**
```sql
WHERE ORD.ORD_GMV_FLG = TRUE              -- Solo GMV válido
  AND ORD.ORD_MARKETPLACE_FLG = TRUE      -- Solo marketplace
  AND ORD.SIT_SITE_ID NOT IN ('MLV')      -- Excluir Venezuela
  AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS') -- Excluir propinas
```

**📖 Documentación completa:** [`docs/BASE_FILTERS_ORDERS.md`](docs/BASE_FILTERS_ORDERS.md)

**Razón:** Estos filtros aseguran que solo se cuenten órdenes válidas para el cálculo de CR. Sin ellos, el driver está inflado con órdenes canceladas, de otros canales, y propinas.

**Impacto:** Reduce el volumen de órdenes ~30-40% pero mejora la precisión del CR.

**Validado:** Enero 2026 con queries de producción

## ✅ Estado de Validación

**✅ MODELO VALIDADO (Enero 2026)** - 100% match con data real de producción

- ✅ **PROCESS_NAME**: Validado contra Jupyter Lab y BigQuery
- ✅ **CDU (Caso de Uso)**: Funcionamiento perfecto en todas las aperturas
- ✅ **TIPIFICACION**: Validado correctamente
- ✅ **CLA_REASON_DETAIL**: Validado correctamente
- ✅ **ENVIRONMENT**: Validado correctamente

Ver documentación completa: [`/docs/VALIDACION.md`](docs/VALIDACION.md)

## 🌎 Sites Soportados

**Incluidos (8 sites):** MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE  
**Excluido:** MLV (Venezuela) - siempre excluido por política de negocio

| Site | País |
|------|------|
| MLA | Argentina |
| MLB | Brasil |
| MLC | Chile |
| MCO | Colombia |
| MEC | Ecuador |
| MLM | México |
| MLU | Uruguay |
| MPE | Perú |

## 📁 Estructura del Repositorio (v4.0 - Limpia y Optimizada)

```
.
├── README.md                          # Este archivo
├── .cursorrules                       # 🎯 RULES obligatorias (SIMPLIFICADO v4.0)
├── .gitignore                         # Exclusiones de Git
├── CHANGELOG.md                       # Historial completo de versiones
├── CHANGELOG_v4.0_HARD_METRICS.md     # 🆕 Release notes v4.0
├── STRUCTURE.md                       # Mapa/estructura del repositorio
├── requirements.txt                   # Dependencias Python
├── .pylintrc                          # Configuración de linting
├── pytest.ini                         # Configuración de tests
│
├── generar_reporte_cr_universal_v6.2.py            # ⭐ ÚNICO TEMPLATE OFICIAL (v6.2)
├── _archived_templates/                            # ⚠️ Templates obsoletos (NO USAR)
│
├── 📁 scripts/                        # 🚀 Scripts ejecutables (CLI / CR ad-hoc)
│   ├── run_analysis.py
│   ├── generar_cr_generales_compra_MLA_nov_dic_2025.py
│   ├── generar_cr_me_predespacho_MLB_nov_dic_2025.py
│   └── README.md
│
├── 📁 metrics/                        # ⭐ Sistema de Hard Metrics (v4.0)
│   ├── README.md                      # Overview del sistema
│   ├── INDICE.md                      # 🗺️ Mapa de navegación
│   ├── GUIA_USUARIO.md                # 🎯 START HERE - Guía práctica
│   ├── COMPARATIVA.md                 # Antes vs Después (ROI)
│   ├── INTEGRACION_GOLDEN_TEMPLATES.md
│   │
│   └── eventos/                       # Métricas de eventos comerciales
│       ├── README.md
│       ├── FUENTE_EVENTOS.md          # Tabla oficial LK_MKP_PROMOTIONS_EVENT
│       ├── CUANDO_REGENERAR.md        # ⚠️ CRITICAL - Mantenimiento
│       ├── generar_correlaciones.py   # Script generador v2.0
│       ├── ejemplo_uso.py             # Ejemplos de código
│       └── data/                      # ⚙️ Métricas generadas (Parquet + JSON)
│
├── 📁 docs/                           # 📚 Documentación de negocio y técnica
│   ├── business-context.md            # Contexto de negocio
│   ├── table-definitions.md           # Tablas BigQuery
│   ├── commerce-structure.md          # 15 Commerce Groups
│   ├── COMMERCE_GROUPS_REFERENCE.md   # 🚨 CRITICAL - Clasificación
│   ├── DATE_FIELD_RULE.md             # 🚨 CRITICAL - CONTACT_DATE_ID
│   ├── BASE_FILTERS_ORDERS.md         # 🚨 CRITICAL - Filtros drivers
│   ├── GOLDEN_TEMPLATES.md            # Estructura oficial reportes
│   ├── REPORT_STRUCTURE.md            # Estructura HTML
│   ├── SHIPPING_DRIVERS.md            # Drivers específicos Shipping
│   ├── VALIDACION.md                  # Estado de validación
│   ├── GUIDELINES.md                  # Best practices
│   ├── CODING_STANDARDS.md
│   ├── ARCHITECTURE.md
│   ├── TROUBLESHOOTING.md
│   └── API_REFERENCE.md
│
├── 📁 sql/                            # 🔍 Queries SQL
│   ├── base-query.sql                 # Query principal CR
│   ├── aggregations.sql
│   ├── sampling-strategy.sql          # MLB sampling
│   └── filters/
│       ├── site-filters.sql
│       ├── environment-filters.sql
│       └── commerce-group-filters.sql
│
├── 📁 calculations/                   # 🧮 Lógica de cálculos
│   ├── contact-rate.py
│   ├── variation-analysis.py
│   ├── pattern-detection.py
│   └── drivers-management.py
│
├── 📁 config/                         # ⚙️ Configuraciones
│   ├── business-constants.py          # Constantes y exclusiones
│   ├── dimensions.py                  # 8 dimensiones
│   ├── commerce-groups.py             # 15 commerce groups
│   └── thresholds.py                  # Umbrales
│
├── 📁 templates/                      # 📄 Templates reutilizables
│   ├── analysis_template.py
│   ├── report_template.html
│   └── README.md
│
├── 📁 utils/                          # 🛠️ Utilidades
│   ├── date-helpers.py
│   └── memory-optimization.py
│
├── 📁 validations/                    # ✅ Casos de validación
│   ├── test_cases.json
│   └── README.md
│
├── 📁 tests/                          # 🧪 Unit tests
│   ├── test_contact_rate.py
│   └── README.md
│
├── 📁 output/                         # 📂 Reportes generados
│   ├── rca/
│   │   └── post-compra/
│   │       ├── pdd/
│   │       │   └── golden-pdd-mla-nov-dic-2025-tipificacion.html
│   │       └── pnr/
│   │           └── golden-pnr-mlb-nov-dic-2025.html
│   ├── examples/
│   └── README.md
│
└── 📁 examples/                       # 💡 Ejemplos de uso
    └── basic-analysis.md
```

### 🎯 Cambios v4.0 (Limpieza Agresiva)
- ✅ **117 archivos eliminados** (scripts de testing, versiones antiguas, docs obsoletos)
- ✅ **`.cursorrules` reducido 59%** (1,089 → 450 líneas)
- ✅ **6 changelogs consolidados** en 2 archivos
- ✅ **30 reportes HTML** de testing eliminados
- ✅ **Carpeta `/test/`** eliminada (25 archivos)
- ✅ **Estructura ultra-clara** para navegación

## 🚀 Quick Start

### Para Cursor AI Agent

1. **Abre este repositorio en Cursor**
2. **El archivo `.cursorrules` se cargará automáticamente**
3. **Comienza a hacer preguntas:**
   - "¿Cuál es la variación de CR entre enero y febrero 2026 para MLA?"
   - "¿Qué drivers están disponibles para analizar PDD?"
   - "Muéstrame la query SQL para obtener datos de Contact Rate"
   - "¿Cómo se calcula el Contact Rate?"

### Para Desarrolladores

```bash
# Clonar repositorio
git clone <repository-url>

# Instalar dependencias (si aplica)
pip install -r requirements.txt

# Ver documentación
cd docs/
```

## 📊 Conceptos Clave

### Contact Rate (CR)

**Definición:** Tasa de contacto = (Incoming Cases / Driver) × 100

- **Incoming Cases:** Casos reportados por clientes
- **Driver:** Métrica de negocio (órdenes, transacciones, etc.)
- **Resultado:** Porcentaje de eventos que generan contacto

### Commerce Groups

El análisis se organiza en **15 Commerce Groups**:

#### 📦 Post-Compra (2)
- **PDD** - Producto Dañado/Defectuoso
- **PNR** - Producto No Recibido

#### 🚛 Shipping (4)
- **ME Distribución** - Distribución de envíos (Comprador)
- **ME PreDespacho** - Pre-despacho (Vendedor)
- **FBM Sellers** - Fulfillment by Mercado Libre
- **ME Drivers** - Drivers de Mercado Envíos

#### 🛒 Marketplace (6)
- **Pre Venta** - Consultas pre-venta
- **Post Venta** - Soporte post-venta
- **Generales Compra** - Consultas generales
- **Moderaciones** - Moderaciones y Prustomer
- **Full Sellers** - Full Sellers
- **Pagos** - Pagos y transacciones

#### 💳 Pagos (1)
- **MP On** - Mercado Pago Online

#### 👤 Cuenta (2)
- **Cuenta** - Gestión de cuenta
- **Experiencia Impositiva** - Experiencia Impositiva

## 🔍 Dimensiones de Análisis

El sistema analiza Contact Rate por **8 dimensiones**:

1. **PROCESS** - Nombre del proceso
2. **CDU** - Caso de Uso
3. **REASON_DETAIL** - Motivo detallado
4. **COMMERCE_GROUP** - Grupo de Commerce
5. **REPORTING_TYPE** - Tipo de reporte
6. **ENVIRONMENT** - Ambiente (DS, FBM, FLEX, XD, MP_ON, MP_OFF)
7. **VERTICAL** - Vertical de negocio
8. **DOMAIN** - Dominio agregado

**Umbral mínimo por defecto:** 100 casos

## 🎯 Uso con Cursor

### Preguntas que puedes hacer:

#### Sobre Cálculos
- "¿Cómo se calcula el Contact Rate?"
- "¿Qué es un driver y cómo se configura?"
- "Explica la fórmula de variación de CR"

#### Sobre Queries
- "Muéstrame la query principal de Contact Rate"
- "¿Cómo filtrar por site MLA?"
- "¿Qué filtros aplica la query base?"

#### Sobre Datos
- "¿Qué tablas de BigQuery se utilizan?"
- "¿Cuál es la estructura de BT_CX_CONTACTS?"
- "¿Qué campos son obligatorios?"

#### Sobre Análisis
- "¿Cómo detectar patrones en variaciones?"
- "¿Qué es un spike en Contact Rate?"
- "¿Cómo se maneja el sampling en MLB?"

## 🛠️ Tecnologías

- **BigQuery** - Base de datos analítica
- **Python 3.8+** - Lenguaje de programación
- **Pandas** - Manipulación de datos
- **melitk** - Librerías internas de Mercado Libre
- **IPyWidgets** - Interfaz interactiva (notebook original)

## 📈 Métricas Principales

| Métrica | Descripción | Fórmula |
|---------|-------------|---------|
| **Contact Rate** | Tasa de contacto | `(Incoming / Driver) × 100` |
| **Variación MoM** | Cambio mes a mes | `CR_actual - CR_anterior` |
| **Variación %** | Cambio porcentual | `((CR_actual - CR_anterior) / CR_anterior) × 100` |
| **Volume Impact** | Impacto en volumen | `Variación × Volume_actual` |

## ⚙️ Constantes de Negocio

```python
CR_MULTIPLIER = 100                    # Conversión a puntos porcentuales
DEFAULT_CASES_THRESHOLD = 100          # Umbral mínimo de casos
MIN_SAMPLE_SIZE = 50                   # Tamaño mínimo de muestra
MAX_SAMPLE_SIZE = 5000                 # Tamaño máximo de muestra
SPIKE_THRESHOLD_MULTIPLIER = 1.5       # 150% del promedio
STRONG_VARIATION_PCT = 20              # ±20% MoM
```

## 🌍 Sites Disponibles

- **MLA** - Argentina
- **MLB** - Brasil
- **MLC** - Chile
- **MCO** - Colombia
- **MLM** - México
- **MLU** - Uruguay
- **MPE** - Perú

## 🚨 Exclusiones Importantes

El análisis excluye automáticamente:

- **QUEUE_IDs:** 2131, 230, 1102, 1241, 2075, 2294, 2295
- **PROCESS_IDs:** 1312
- **CI_REASON_IDs:** 2592, 6588, 10068, 2701, 10048
- **Site:** MLV (Venezuela)
- **FLAG_EXCLUDE_NUMERATOR_CR = 1**

## 📝 Notas Importantes

1. **Threshold:** Todas las dimensiones usan un umbral mínimo de 100 casos por defecto
2. **Sampling MLB:** Para Brasil se aplica estrategia especial de sampling debido al volumen
3. **Memory Optimization:** El sistema optimiza memoria automáticamente para datasets grandes
4. **Vertical & Domain:** Temporalmente en NULL hasta encontrar tabla source

## 📖 Documentación Completa

### ⭐ Nuevos en el Repositorio? Empieza Aquí:
1. **[README.md](README.md)** - Visión general del repositorio (este archivo)
2. ⭐ **[metrics/GUIA_USUARIO.md](metrics/GUIA_USUARIO.md)** - **NUEVO v4.0** Guía práctica de hard metrics
3. **[GUIDELINES.md](docs/GUIDELINES.md)** - Mejores prácticas

### Documentos de Sistema (v4.0 - Hard Metrics)
- ⭐ **[metrics/README.md](metrics/README.md)** - **NUEVO v4.0** Sistema de métricas precalculadas
- ⭐ **[metrics/GUIA_USUARIO.md](metrics/GUIA_USUARIO.md)** - Guía paso a paso para usuarios
- ⭐ **[metrics/eventos/CUANDO_REGENERAR.md](metrics/eventos/CUANDO_REGENERAR.md)** - Cuándo regenerar métricas
- **[metrics/eventos/README.md](metrics/eventos/README.md)** - Métricas de eventos comerciales
- **[metrics/eventos/FUENTE_EVENTOS.md](metrics/eventos/FUENTE_EVENTOS.md)** - Tabla oficial de eventos
- **[metrics/INTEGRACION_GOLDEN_TEMPLATES.md](metrics/INTEGRACION_GOLDEN_TEMPLATES.md)** - Cómo integrar en scripts

### Documentos de Reportes y Templates
- **[REPORT_STRUCTURE.md](docs/REPORT_STRUCTURE.md)** - ⭐ **v3.7** Estructura oficial de reportes HTML
- **[GOLDEN_TEMPLATES.md](docs/GOLDEN_TEMPLATES.md)** - ⭐ **v3.9** Templates oficiales validados
- **[SHIPPING_DRIVERS.md](docs/SHIPPING_DRIVERS.md)** - ⭐ **v3.7** Drivers específicos de Shipping

### Documentos de Negocio
- **[business-context.md](docs/business-context.md)** - Contexto de negocio y Commerce Groups
- **[COMMERCE_GROUPS_REFERENCE.md](docs/COMMERCE_GROUPS_REFERENCE.md)** - Referencia completa
- **[VALIDACION.md](docs/VALIDACION.md)** - Estado de validación

### Documentos Técnicos
- **[CODING_STANDARDS.md](docs/CODING_STANDARDS.md)** - Estándares de código
- **[DATE_FIELD_RULE.md](docs/DATE_FIELD_RULE.md)** - Campo de fecha obligatorio
- **[BASE_FILTERS_ORDERS.md](docs/BASE_FILTERS_ORDERS.md)** - Filtros base para drivers

### Documentos Técnicos
- **[commerce-groups-classification.sql](sql/filters/commerce-groups-classification.sql)** - Clasificación oficial CASE v3.5
- **[CHANGELOG_PDD_CLASSIFICATION.md](CHANGELOG_PDD_CLASSIFICATION.md)** - Corrección PDD v3.5
- **[CHANGELOG_MEC_INCLUSION.md](CHANGELOG_MEC_INCLUSION.md)** - Inclusión de Ecuador (MEC)

## 🤝 Contribuir

Este repositorio está optimizado para consumo por agentes AI. Si necesitas agregar:
- Nuevas queries → `/sql/`
- Nuevos cálculos → `/calculations/`
- Nueva documentación → `/docs/`
- Nuevas constantes → `/config/`

## 📞 Soporte

Para preguntas sobre:
- **Negocio:** Ver `docs/business-context.md`
- **Técnico:** Ver `docs/table-definitions.md`
- **Queries:** Ver carpeta `/sql/`
- **Cálculos:** Ver carpeta `/calculations/`

## 📚 Documentación Adicional

### Changelogs de Versiones
- **[CHANGELOG.md](CHANGELOG.md)**: Historial completo de versiones y cambios
- **[CHANGELOG_v4.0_HARD_METRICS.md](CHANGELOG_v4.0_HARD_METRICS.md)**: ⭐ **NUEVO v4.0** Sistema de Hard Metrics (Enero 2026)

### Guías Generales
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)**: Guía para contribuir al repositorio
- **[docs/FAQ.md](docs/FAQ.md)**: Preguntas frecuentes
- **[docs/GUIDELINES.md](docs/GUIDELINES.md)**: Mejores prácticas (SHOULD)
- **[docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md)**: Estándares de código
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Diseño del sistema
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**: Solución de problemas
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)**: Referencia de funciones
- **[scripts/README.md](scripts/README.md)**: Cómo ejecutar scripts (CLI y CR ad-hoc)

## 🔄 Versión

**Versión:** 4.0.0 (Hard Metrics System)  
**Última actualización:** Enero 2026  
**Basado en:** `docs/V37.ipynb` (Jupyter Notebook) + Sistema de Métricas Precalculadas

### 🎯 Novedades v4.0.0 ⭐ NUEVO
- ✅ **Sistema de Hard Metrics:** Métricas precalculadas en Parquet para mejor performance y precisión
- ✅ **Fuente dinámica de eventos:** Integración con `WHOWNER.LK_MKP_PROMOTIONS_EVENT` (tabla oficial)
- ✅ **Correlaciones sobre incoming completo:** Ya no basado en muestras, análisis de TODOS los casos
- ✅ **Rangos completos de eventos:** Captura fecha_inicio a fecha_fin (no 1 día puntual)
- ✅ **Performance mejorado 16x:** Reportes de 8 min → 30 seg (leyendo métricas precalculadas)
- ✅ **Precisión 100%:** Correlaciones basadas en TODO el incoming, no muestra
- ✅ **Metadata enriquecido:** Tracking completo de eventos, fechas y versiones
- ✅ **Template único universal:** `generar_reporte_cr_universal_v6.2.py` (todos los sites, commerce groups y dimensiones)
- ✅ **Documentación completa:** 
  - `metrics/GUIA_USUARIO.md` - Guía práctica
  - `metrics/eventos/CUANDO_REGENERAR.md` - Workflow de mantenimiento
  - `metrics/eventos/FUENTE_EVENTOS.md` - Tabla oficial de eventos
  - `metrics/INTEGRACION_GOLDEN_TEMPLATES.md` - Integración en scripts
- ✅ **Regla 16 agregada:** Hard Metrics System en `.cursorrules`
- ✅ **Fallback mechanism:** Scripts funcionan con y sin hard metrics
- ✅ **Validado:** MLA Nov-Dic 2025 (121,803 y 140,954 casos analizados)

### 🎯 Novedades v3.7.0
- ✅ **Extensión de estructura oficial a Marketplace:** 6 commerce groups validados
- ✅ **Color azul (#2196f3) para Marketplace:** Estándar visual único
- ✅ **Generales Compra validado:** Primer reporte Marketplace (MLA Nov-Dic 2025)
- ✅ **Drivers de Shipping (CRÍTICO):** OS_TOTALES, OS_WO_FULL, OS_FULL de `BT_CX_DRIVERS_CR` (drivers GLOBALES, sin filtro de site)
- ✅ **ME PreDespacho validado:** Primer reporte Shipping (MLB Nov-Dic 2025)
- ✅ **9 commerce groups con formato oficial:** Post-Compra (3) + Marketplace (6)
- ✅ Nuevo documento: `docs/SHIPPING_DRIVERS.md` - Guía oficial de drivers de Shipping
- ✅ Actualización de `docs/REPORT_STRUCTURE.md` (v3.7)
- ✅ Nuevo changelog: `CHANGELOG_v3.7_MARKETPLACE.md`
- ✅ Actualización de `.cursorrules` - Regla 12: Shipping Drivers (CRITICAL)

### v3.6.0
- ✅ **Estructura oficial de reportes HTML:** Cross Site (3 tablas) y Single Site (2 tablas)
- ✅ **Ordenamiento sincronizado:** Entre tablas consolidadas y detalle
- ✅ **Resumen ejecutivo mejorado:** Drivers después de incoming, 8 cards
- ✅ **Colores estandarizados:** PDD (rojo), PNR (naranja), PCF (verde)
- ✅ **Documentación centralizada:** `docs/REPORT_STRUCTURE.md`

### v3.5.0
- ✅ **Filtro PDD corregido con CASE:** Ahora incluye "Conflict Others" → PDD (+2% casos adicionales)
- ✅ **MEC (Ecuador) agregado:** 8vo site soportado en todo el repositorio
- ✅ **100% alineado con producción:** Queries coinciden exactamente con queries de Juli
- ✅ CASE completo para PDD, PNR, PCF Comprador, PCF Vendedor
- ✅ Actualización de `.cursorrules` (v3.5)
- ✅ Todos los scripts actualizados con nuevo filtro

### v3.4.0
- ✅ **MEC (Ecuador) agregado:** Como 8vo site soportado

### v3.3.0
- ✅ **Threshold eliminado como regla obligatoria:** Por defecto se incluyen TODOS los procesos
- ✅ Threshold solo se aplica si el usuario lo solicita explícitamente

### v3.2.0
- ✅ **Nueva regla crítica:** Filtros base obligatorios para órdenes (drivers)
- ✅ Documentación completa: `docs/BASE_FILTERS_ORDERS.md`
- ✅ Validación con queries de producción
- ✅ Actualización de `.cursorrules` (v3.2)

### v3.0.0
- ✅ Separación Rules vs Guidelines
- ✅ Nueva estructura de carpetas (scripts/, templates/, validations/, tests/)
- ✅ Documentación completa (11 archivos nuevos)
- ✅ Templates reutilizables
- ✅ Unit tests
- ✅ Configuración de calidad (.gitignore, .pylintrc, pytest.ini)

Ver [CHANGELOG.md](CHANGELOG.md) para detalles completos.

---

**🎯 Este repositorio está optimizado para Cursor AI Agent**  
Cursor puede leer, entender y responder preguntas sobre cualquier aspecto del análisis de Contact Rate usando el contenido estructurado de este repositorio.

**📖 Diferencia entre RULES y GUIDELINES:**
- **RULES** (`.cursorrules`): Definiciones OBLIGATORIAS (MUST) - Fórmulas, thresholds, exclusiones
- **GUIDELINES** (`docs/GUIDELINES.md`): Recomendaciones (SHOULD) - Mejores prácticas, estrategias
