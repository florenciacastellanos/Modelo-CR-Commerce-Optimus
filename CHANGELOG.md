# 📝 Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [3.0.0] - 2026-01-22

### 🎉 Added - Reestructuración Mayor del Repositorio
- **Nueva estructura de carpetas**: `scripts/`, `templates/`, `validations/`, `tests/`
- **Separación Rules vs Guidelines**: `.cursorrules` (MUST) vs `docs/GUIDELINES.md` (SHOULD)
- **Coding Standards**: `docs/CODING_STANDARDS.md` con estándares de Python, SQL y Markdown
- **Templates reutilizables**: `templates/analysis_template.py` y `templates/report_template.html`
- **Validations framework**: `validations/test_cases.json` con 7 test cases documentados
- **Unit tests**: `tests/test_contact_rate.py` con tests de cálculos y exclusiones
- **Scripts de producción**: `scripts/run_analysis.py` production-ready
- **Documentación adicional**: `CHANGELOG.md`, `CONTRIBUTING.md`, `FAQ.md`
- **Arquitectura**: `docs/ARCHITECTURE.md` con diseño del sistema
- **Troubleshooting**: `docs/TROUBLESHOOTING.md` con soluciones a problemas comunes
- **API Reference**: `docs/API_REFERENCE.md` con referencia de funciones
- **Configuración de calidad**: `.gitignore`, `.pylintrc`, `pytest.ini`

### 🔄 Changed
- **`.cursorrules`**: Reducido a solo RULES obligatorias (de 269 líneas a ~200 líneas)
- **Carpeta `test/`**: Reorganizada con subcarpetas `scripts/`, `diagnostics/`, `outputs/`
- **README.md**: Actualizado con nueva estructura y badges de validación
- **STRUCTURE.md**: Actualizado con árbol completo de carpetas

### 🗂️ Organized
- Movidos 30+ archivos CSV/HTML del root a `test/outputs/`
- Separados scripts de prueba (`test/scripts/`) de scripts de producción (`scripts/`)
- Creado `.gitignore` robusto con 200+ reglas

### ✅ Validated
- **5 dimensiones validadas**: PROCESS_NAME, CDU, TIPIFICACION, CLA_REASON_DETAIL, ENVIRONMENT
- **12 Commerce Groups validados**: PDD, PNR, ME Distribución, ME PreDespacho, FBM Sellers, y más
- **Threshold rule validada**: Regla "SUM >= 50 en ANY período" funcionando correctamente
- **100% match**: Resultados coinciden 100% con data real de Jupyter Lab

---

## [2.5.0] - 2026-01-20

### ✅ Added - Validación del Modelo
- **Validación completa**: 50+ análisis ejecutados con 100% de precisión
- **Documentación de validación**: `docs/VALIDACION.md` con resultados detallados
- **Threshold rule refinada**: Implementada regla "SUM >= 50 en ANY período"
- **Nuevos Commerce Groups**: Validados Experiencia Impositiva, Despacho, Reputación

### 🔧 Fixed
- **Threshold logic**: Corregida lógica para incluir procesos con suma >= 50 en cualquier período
- **AGRUP_COMMERCE**: Actualizada lógica de agrupación para ME Distribución, ME PreDespacho, FBM Sellers
- **Encoding issues**: Resueltos problemas de encoding en Windows con emojis

### 📊 Improved
- **Reportes HTML**: Mejorado diseño visual con colores de Mercado Libre
- **Performance**: Optimizado para datasets grandes con sampling en MLB

---

## [2.0.0] - 2026-01-15

### 🎉 Added - Creación del Repositorio
- **Estructura inicial**: Carpetas `docs/`, `sql/`, `calculations/`, `config/`, `utils/`, `examples/`
- **Documentación completa**:
  - `docs/business-context.md`: Contexto de negocio y 15 Commerce Groups
  - `docs/table-definitions.md`: Esquemas de BigQuery
  - `docs/metrics-glossary.md`: Métricas y fórmulas
  - `docs/commerce-structure.md`: Estructura de Commerce Groups
  - `docs/analysis-workflow.md`: Flujo de análisis paso a paso
- **SQL Queries**:
  - `sql/base-query.sql`: Query principal de CR
  - `sql/aggregations.sql`: 13 patrones de agregación
  - `sql/sampling-strategy.sql`: Estrategia de sampling para MLB
  - `sql/filters/`: Filtros específicos por site, environment, commerce group
- **Cálculos Python**:
  - `calculations/contact-rate.py`: Cálculo de CR
  - `calculations/variation-analysis.py`: Análisis de variaciones MoM
  - `calculations/pattern-detection.py`: Detección de spikes y drops
  - `calculations/drivers-management.py`: Gestión de drivers
- **Configuración**:
  - `config/business-constants.py`: Constantes de negocio
  - `config/commerce-groups.py`: 15 Commerce Groups
  - `config/dimensions.py`: 8 dimensiones de análisis
  - `config/thresholds.py`: Umbrales y límites
- **Utilidades**:
  - `utils/memory-optimization.py`: Optimización de memoria
  - `utils/date-helpers.py`: Helpers de fechas
- **Ejemplos**:
  - `examples/basic-analysis.md`: 3 ejemplos de uso
- **Cursor AI**:
  - `.cursorrules`: Reglas para Cursor AI Agent (versión inicial)
  - `README.md`: Documentación principal
  - `STRUCTURE.md`: Estructura del repositorio

### 🔧 Configuration
- **BigQuery**: Configurado acceso a `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
- **Exclusiones automáticas**: Queues, processes, CI reasons, MLV
- **Thresholds**: MIN_CASES_THRESHOLD = 100, MIN_PROCESS_INCOMING = 50

---

## [1.0.0] - 2025-12-01

### 📓 Initial - Jupyter Notebook (`docs/V37.ipynb`)
- **Dashboard interactivo**: Jupyter Lab con widgets
- **Cálculos de CR**: Implementación inicial
- **Queries SQL**: Queries embebidas en notebook
- **Visualizaciones**: Gráficos con matplotlib/plotly
- **Análisis manual**: Proceso manual de análisis

---

## Tipos de Cambios

- **Added**: Nuevas funcionalidades
- **Changed**: Cambios en funcionalidades existentes
- **Deprecated**: Funcionalidades obsoletas (próximas a eliminarse)
- **Removed**: Funcionalidades eliminadas
- **Fixed**: Corrección de bugs
- **Security**: Correcciones de seguridad
- **Validated**: Validaciones completadas
- **Organized**: Reorganización de archivos/estructura

---

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/lang/es/):

- **MAJOR** (X.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (0.X.0): Nuevas funcionalidades compatibles
- **PATCH** (0.0.X): Correcciones de bugs

---

**Última actualización**: 2026-01-22  
**Versión actual**: 3.0.0
