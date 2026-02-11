# 🏗️ Architecture - Contact Rate Analysis System

> **Diseño y arquitectura** del sistema de análisis de Contact Rate

---

## 🎯 Visión General

Este repositorio implementa un **framework modular** para análisis de Contact Rate, diseñado para:
- **Mantenibilidad**: Código organizado y documentado
- **Escalabilidad**: Soporta múltiples Commerce Groups y dimensiones
- **Reutilización**: Templates y componentes reusables
- **AI-First**: Optimizado para consumo por Cursor AI

---

## 📐 Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    CURSOR AI AGENT                          │
│              (Consume .cursorrules + docs/)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  REPOSITORIO ESTRUCTURADO                    │
├─────────────────────────────────────────────────────────────┤
│  📚 docs/          │  Contexto de negocio y técnico         │
│  🔍 sql/           │  Queries de BigQuery                   │
│  🧮 calculations/  │  Lógica de cálculos Python             │
│  ⚙️ config/        │  Configuraciones y constantes          │
│  🚀 scripts/       │  Scripts de producción                 │
│  📄 templates/     │  Templates reutilizables               │
│  ✅ validations/   │  Casos de prueba                       │
│  🧪 tests/         │  Unit tests                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BIGQUERY (meli-bi-data)                  │
│              BT_CX_CONTACTS + BT_ORD_ORDERS                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. **Documentation Layer** (`/docs/`)

**Propósito**: Proporcionar contexto de negocio y técnico

**Componentes**:
- `business-context.md`: Reglas de negocio, Commerce Groups
- `table-definitions.md`: Esquemas de BigQuery
- `metrics-glossary.md`: Fórmulas y métricas
- `analysis-workflow.md`: Flujo de análisis
- `GUIDELINES.md`: Mejores prácticas
- `CODING_STANDARDS.md`: Estándares de código
- `ARCHITECTURE.md`: Este documento
- `TROUBLESHOOTING.md`: Solución de problemas
- `API_REFERENCE.md`: Referencia de funciones

**Consumidores**: Cursor AI, desarrolladores, analistas

---

### 2. **Query Layer** (`/sql/`)

**Propósito**: Queries SQL para extraer datos de BigQuery

**Componentes**:
- `base-query.sql`: Query principal de CR
- `aggregations.sql`: Patrones de agregación
- `sampling-strategy.sql`: Estrategia de sampling MLB
- `filters/`: Filtros específicos

**Flujo**:
```
Usuario → Script Python → SQL Query → BigQuery → DataFrame
```

**Optimizaciones**:
- CTEs para legibilidad
- Sampling para MLB
- Exclusiones automáticas
- Índices implícitos en BigQuery

---

### 3. **Calculation Layer** (`/calculations/`)

**Propósito**: Lógica de cálculos de CR y variaciones

**Componentes**:
- `contact-rate.py`: CR = (Incoming / Driver) × 100
- `variation-analysis.py`: Variaciones MoM, YoY
- `pattern-detection.py`: Spikes, drops, anomalías
- `drivers-management.py`: Gestión de drivers

**Flujo**:
```
DataFrame → Cálculos → DataFrame Enriquecido → Output (CSV/HTML)
```

---

### 4. **Configuration Layer** (`/config/`)

**Propósito**: Centralizar configuraciones y constantes

**Componentes**:
- `business-constants.py`: Constantes de negocio
- `commerce-groups.py`: 15 Commerce Groups
- `dimensions.py`: 8 dimensiones
- `thresholds.py`: Umbrales y límites

**Patrón**: Configuración como código (Config as Code)

---

### 5. **Execution Layer** (`/scripts/`)

**Propósito**: Scripts production-ready para ejecutar análisis

**Componentes**:
- `run_analysis.py`: Script principal parametrizado
- `README.md`: Documentación de uso

**Características**:
- Argumentos CLI
- Logging estructurado
- Error handling robusto
- Output en múltiples formatos

---

### 6. **Template Layer** (`/templates/`)

**Propósito**: Templates reutilizables para crear análisis personalizados

**Componentes**:
- `analysis_template.py`: Template de script Python
- `report_template.html`: Template de reporte HTML
- `query_template.sql`: Template de query SQL

**Uso**:
```bash
cp templates/analysis_template.py mi_analisis.py
# Personalizar y ejecutar
```

---

### 7. **Validation Layer** (`/validations/`)

**Propósito**: Casos de prueba y resultados de validación

**Componentes**:
- `test_cases.json`: 7+ casos de prueba documentados
- `README.md`: Documentación de validación

**Estado**: ✅ 100% pass rate (Enero 2026)

---

### 8. **Testing Layer** (`/tests/`)

**Propósito**: Unit tests para cálculos y lógica

**Componentes**:
- `test_contact_rate.py`: Tests de cálculos
- `test_exclusions.py`: Tests de exclusiones (futuro)
- `test_queries.py`: Tests de queries (futuro)

**Framework**: pytest

---

## 🔄 Flujo de Datos

### Análisis Típico

```
1. Usuario define parámetros
   ├─ Commerce Group: PDD
   ├─ Site: MLA
   ├─ Dimensión: PROCESS_NAME
   └─ Períodos: 2025-11 vs 2025-12

2. Script construye query SQL
   ├─ Aplica filtros de Commerce Group
   ├─ Aplica exclusiones automáticas
   └─ Agrega por dimensión

3. Query se ejecuta en BigQuery
   ├─ Extrae datos de BT_CX_CONTACTS
   ├─ Aplica sampling si es MLB
   └─ Retorna DataFrame

4. Cálculos se aplican
   ├─ Calcula variación absoluta
   ├─ Calcula variación porcentual
   └─ Aplica threshold rule

5. Outputs se generan
   ├─ CSV para análisis de datos
   └─ HTML para visualización
```

---

## 🎨 Patrones de Diseño

### 1. **Separation of Concerns**
- Queries separadas de cálculos
- Configuración separada de lógica
- Documentación separada de código

### 2. **DRY (Don't Repeat Yourself)**
- Templates reutilizables
- Funciones parametrizadas
- Configuración centralizada

### 3. **Config as Code**
- Constantes en archivos Python
- Versionadas en Git
- Fácil de modificar y auditar

### 4. **Documentation as Code**
- Markdown versionado
- Co-ubicado con código
- Fácil de mantener actualizado

### 5. **Test-Driven Validation**
- Test cases documentados
- Validación automatizable
- Resultados rastreables

---

## 🔐 Seguridad y Permisos

### BigQuery Access
- **Autenticación**: `gcloud auth application-default login`
- **Proyecto**: `meli-bi-data`
- **Permisos requeridos**: `bigquery.jobs.create`, `bigquery.tables.getData`

### Datos Sensibles
- **No versionados**: Credenciales, API keys
- **Gitignore**: `*.json` (excepto configs)
- **Logs**: No incluir PII

---

## ⚡ Performance y Escalabilidad

### Optimizaciones Implementadas

1. **Sampling en MLB**
   - Threshold: 150,000 filas estimadas
   - Método: Systematic sampling

2. **Memory Optimization**
   - Reducción de tipos de datos
   - Liberación de memoria intermedia

3. **Query Optimization**
   - CTEs para reutilización
   - Filtros tempranos
   - Índices implícitos

4. **Batch Processing**
   - Priority BATCH para queries grandes
   - Reduce uso de quota

### Límites y Capacidad

| Métrica | Límite | Notas |
|---------|--------|-------|
| **Filas por query** | 200,000 | Con sampling |
| **Períodos** | 6 meses | Recomendado |
| **Commerce Groups** | 15 | Fijo |
| **Dimensiones** | 8 | Fijo |
| **Sites** | 7 | Excluyendo MLV |

---

## 🚀 Extensibilidad

### Agregar Nuevo Commerce Group

1. Actualizar `config/commerce-groups.py`
2. Agregar filtro en `sql/filters/commerce-group-filters.sql`
3. Documentar en `docs/commerce-structure.md`
4. Agregar test case en `validations/test_cases.json`

### Agregar Nueva Dimensión

1. Verificar disponibilidad en `BT_CX_CONTACTS`
2. Actualizar `config/dimensions.py`
3. Documentar en `docs/metrics-glossary.md`
4. Validar con test case

### Agregar Nuevo Cálculo

1. Crear función en `calculations/`
2. Agregar docstring completo
3. Agregar unit test en `tests/`
4. Documentar en `docs/API_REFERENCE.md`

---

## 🔮 Roadmap Técnico

### Corto Plazo (Q1 2026)
- [ ] CI/CD con GitHub Actions
- [ ] Coverage > 80%
- [ ] Validar 15/15 Commerce Groups

### Medio Plazo (Q2 2026)
- [ ] API REST para análisis
- [ ] Dashboard web interactivo
- [ ] Alertas automáticas

### Largo Plazo (H2 2026)
- [ ] Machine Learning para forecasting
- [ ] Detección automática de anomalías
- [ ] Integración con sistemas de ticketing

---

**Última actualización**: Enero 2026  
**Versión**: 3.0.0
