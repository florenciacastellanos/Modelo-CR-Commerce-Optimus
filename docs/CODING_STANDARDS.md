# 💻 Coding Standards - Contact Rate Analysis

> **Estándares de código** para mantener consistencia y calidad en el repositorio

---

## 🎯 Propósito

Este documento define los estándares de código para:
- **Python**: Scripts de análisis y cálculos
- **SQL**: Queries de BigQuery
- **Markdown**: Documentación
- **Estructura**: Organización de archivos

---

## 🐍 Python Standards

### Convenciones Generales

#### PEP 8 Compliance
```python
# ✅ BIEN: Snake case para funciones y variables
def calculate_contact_rate(incoming_cases, driver_volume):
    contact_rate = (incoming_cases / driver_volume) * 100
    return contact_rate

# ❌ MAL: CamelCase para funciones
def CalculateContactRate(IncomingCases, DriverVolume):
    ContactRate = (IncomingCases / DriverVolume) * 100
    return ContactRate
```

#### Nombres Descriptivos
```python
# ✅ BIEN: Nombres claros y específicos
def filter_processes_by_threshold(df, min_incoming=50):
    return df[df['incoming'] >= min_incoming]

# ❌ MAL: Nombres ambiguos
def filt(d, t=50):
    return d[d['i'] >= t]
```

### Estructura de Archivos Python

#### Header Template
```python
"""
Module: [nombre_del_modulo].py
Purpose: [Descripción breve del propósito]
Author: Contact Rate Analysis Team
Date: YYYY-MM-DD
Version: X.Y.Z

Dependencies:
    - pandas
    - google.cloud.bigquery
    - [otras dependencias]

Usage:
    from calculations import contact_rate
    cr = contact_rate.calculate(incoming=100, driver=1000)
"""

import sys
import os
from typing import Optional, Dict, List
import pandas as pd

# Constants
CR_MULTIPLIER = 100
MIN_THRESHOLD = 50
```

#### Funciones con Docstrings
```python
def calculate_contact_rate(incoming: int, driver: int) -> Optional[float]:
    """
    Calculate Contact Rate in percentage points.
    
    Formula: CR = (Incoming / Driver) × 100
    
    Args:
        incoming (int): Number of incoming cases/contacts
        driver (int): Business metric (orders, transactions, etc.)
    
    Returns:
        Optional[float]: Contact Rate in percentage points (pp)
                        Returns None if driver is 0 or negative
    
    Raises:
        ValueError: If incoming is negative
    
    Examples:
        >>> calculate_contact_rate(50, 1000)
        5.0
        
        >>> calculate_contact_rate(100, 0)
        None
    """
    if incoming < 0:
        raise ValueError("Incoming cases cannot be negative")
    
    if driver is None or driver <= 0:
        return None
    
    return round((incoming / driver) * CR_MULTIPLIER, 4)
```

### Type Hints (Recomendado)
```python
from typing import Optional, Dict, List, Tuple
import pandas as pd

def analyze_variation(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
    dimension: str = "PROCESS_NAME"
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Analyze CR variation between two periods.
    
    Args:
        df_current: DataFrame with current period data
        df_previous: DataFrame with previous period data
        dimension: Dimension to analyze (default: PROCESS_NAME)
    
    Returns:
        Tuple containing:
            - DataFrame with variation analysis
            - Dictionary with summary statistics
    """
    # Implementation
    pass
```

### Error Handling
```python
# ✅ BIEN: Manejo específico de errores
try:
    df = pd.read_gbq(query, project_id=project_id)
except Exception as e:
    print(f"❌ Error al ejecutar query: {e}")
    print(f"Query: {query[:200]}...")  # Primeros 200 caracteres
    return None

# ❌ MAL: Catch genérico sin información
try:
    df = pd.read_gbq(query, project_id=project_id)
except:
    pass
```

### Logging
```python
import logging

# Configuración al inicio del script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Uso en funciones
def run_analysis(commerce_group: str, site: str):
    logger.info(f"Iniciando análisis para {commerce_group} en {site}")
    
    try:
        # Procesamiento
        logger.debug(f"Ejecutando query para {commerce_group}")
        result = execute_query(query)
        logger.info(f"✅ Análisis completado: {len(result)} registros")
        return result
    
    except Exception as e:
        logger.error(f"❌ Error en análisis: {e}")
        raise
```

### Constantes
```python
# ✅ BIEN: Constantes en MAYÚSCULAS al inicio del archivo
CR_MULTIPLIER = 100
MIN_CASES_THRESHOLD = 50
MAX_SAMPLE_SIZE = 200000
EXCLUDED_QUEUES = [2131, 230, 1102, 1241, 2075, 2294, 2295]

# ❌ MAL: Valores hardcodeados en el código
def filter_data(df):
    return df[~df['queue_id'].isin([2131, 230, 1102])]  # ¿De dónde vienen estos números?
```

### Imports Organization
```python
# 1. Standard library
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# 2. Third-party libraries
import pandas as pd
import numpy as np
from google.cloud import bigquery

# 3. Local modules
from config import business_constants
from calculations import contact_rate
from utils import date_helpers
```

---

## 🗄️ SQL Standards

### Naming Conventions

#### Tables and CTEs
```sql
-- ✅ BIEN: MAYÚSCULAS para CTEs, snake_case para tablas
WITH BASE_CONTACTS AS (
    SELECT *
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
),

FILTERED_DATA AS (
    SELECT *
    FROM BASE_CONTACTS
    WHERE site_id = 'MLA'
)

-- ❌ MAL: Inconsistente
with baseContacts as (
    select *
    from `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
)
```

#### Columns
```sql
-- ✅ BIEN: snake_case consistente
SELECT
    process_name,
    incoming_cases,
    driver_volume,
    contact_rate_pp
FROM analysis_table

-- ❌ MAL: Mezcla de estilos
SELECT
    ProcessName,
    incoming_cases,
    DriverVolume,
    ContactRate
FROM analysis_table
```

### Query Structure

#### Template Estándar
```sql
-- ============================================
-- Query: [Nombre descriptivo]
-- Purpose: [Descripción del propósito]
-- Author: Contact Rate Analysis Team
-- Date: YYYY-MM-DD
-- Version: X.Y
--
-- Parameters:
--   @site_id: Site code (e.g., 'MLA', 'MLB')
--   @period_start: Start period (YYYY-MM)
--   @period_end: End period (YYYY-MM)
--
-- Returns:
--   - process_name: Process name
--   - incoming_cases: Total incoming cases
--   - driver_volume: Total driver volume
--   - contact_rate: CR in percentage points
--
-- Notes:
--   - Excludes specific queues (see config)
--   - Applies threshold of 50 cases minimum
-- ============================================

WITH BASE_CONTACTS AS (
    -- Step 1: Extract base contact data
    SELECT
        site_id,
        period_month,
        process_name,
        COUNT(*) AS incoming_cases
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
    WHERE 1=1
        AND site_id = @site_id
        AND period_month BETWEEN @period_start AND @period_end
        AND flag_exclude_numerator_cr = 0
    GROUP BY 1, 2, 3
),

DRIVER_DATA AS (
    -- Step 2: Get driver volumes
    SELECT
        site_id,
        period_month,
        process_name,
        SUM(driver_volume) AS driver_volume
    FROM `meli-bi-data.WHOWNER.BT_DRIVERS`
    WHERE site_id = @site_id
    GROUP BY 1, 2, 3
),

FINAL_CALCULATION AS (
    -- Step 3: Calculate Contact Rate
    SELECT
        c.site_id,
        c.period_month,
        c.process_name,
        c.incoming_cases,
        d.driver_volume,
        ROUND((c.incoming_cases / NULLIF(d.driver_volume, 0)) * 100, 4) AS contact_rate_pp
    FROM BASE_CONTACTS c
    LEFT JOIN DRIVER_DATA d
        ON c.site_id = d.site_id
        AND c.period_month = d.period_month
        AND c.process_name = d.process_name
    WHERE d.driver_volume > 0
)

-- Final output
SELECT *
FROM FINAL_CALCULATION
WHERE incoming_cases >= 50  -- Threshold
ORDER BY contact_rate_pp DESC;
```

### Formatting Rules

#### Indentation
```sql
-- ✅ BIEN: Indentación consistente (4 espacios)
SELECT
    field1,
    field2,
    CASE
        WHEN condition1 THEN 'value1'
        WHEN condition2 THEN 'value2'
        ELSE 'default'
    END AS field3
FROM table1
WHERE 1=1
    AND field1 = 'value'
    AND field2 > 100

-- ❌ MAL: Sin indentación
SELECT field1,field2,CASE WHEN condition1 THEN 'value1' WHEN condition2 THEN 'value2' ELSE 'default' END AS field3 FROM table1 WHERE field1='value' AND field2>100
```

#### JOIN Clauses
```sql
-- ✅ BIEN: JOIN explícito con ON en nueva línea
SELECT
    a.field1,
    b.field2
FROM table_a a
INNER JOIN table_b b
    ON a.id = b.id
    AND a.site_id = b.site_id
LEFT JOIN table_c c
    ON b.id = c.id

-- ❌ MAL: JOIN implícito
SELECT
    a.field1,
    b.field2
FROM table_a a, table_b b
WHERE a.id = b.id
```

#### WHERE Clauses
```sql
-- ✅ BIEN: WHERE 1=1 para facilitar comentarios
WHERE 1=1
    AND site_id = 'MLA'
    AND period_month >= '2025-01'
    -- AND process_name = 'Test'  -- Fácil comentar/descomentar

-- ✅ BIEN: Agrupación lógica
WHERE 1=1
    -- Site filters
    AND site_id IN ('MLA', 'MLB', 'MCO')
    
    -- Period filters
    AND period_month BETWEEN '2025-01' AND '2025-12'
    
    -- Exclusions
    AND queue_id NOT IN (2131, 230, 1102)
    AND flag_exclude_numerator_cr = 0
```

### Comments
```sql
-- Single line comment for brief explanations

/*
 * Multi-line comment for:
 * - Complex logic explanation
 * - Business rules documentation
 * - Important notes
 */

-- ============================================
-- Section separator for major query parts
-- ============================================
```

---

## 📝 Markdown Standards

### Document Structure

#### Header Template
```markdown
# 📊 [Título del Documento]

> **Descripción breve** del propósito del documento

---

## 🎯 Propósito

[Explicación detallada]

---

## 📋 Contenido

[Secciones principales]
```

### Formatting Rules

#### Headers
```markdown
# H1: Título Principal (solo uno por documento)
## H2: Secciones Principales
### H3: Subsecciones
#### H4: Detalles Específicos
```

#### Code Blocks
```markdown
# ✅ BIEN: Especificar lenguaje
```python
def example():
    return True
```

# ❌ MAL: Sin especificar lenguaje
```
def example():
    return True
```
```

#### Lists
```markdown
# ✅ BIEN: Consistente con guiones
- Item 1
- Item 2
  - Sub-item 2.1
  - Sub-item 2.2

# ✅ BIEN: Numeración para pasos
1. Primer paso
2. Segundo paso
3. Tercer paso

# ❌ MAL: Mezcla de estilos
- Item 1
* Item 2
+ Item 3
```

#### Links
```markdown
# ✅ BIEN: Descriptivo
Ver [documentación de Business Context](docs/business-context.md)

# ❌ MAL: Genérico
Ver [aquí](docs/business-context.md)
```

#### Tables
```markdown
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Valor 1   | Valor 2   | Valor 3   |
| Valor 4   | Valor 5   | Valor 6   |
```

---

## 📁 File Organization

### Naming Conventions

#### Python Files
```
✅ BIEN: snake_case.py
contact_rate.py
variation_analysis.py
pattern_detection.py

❌ MAL:
ContactRate.py
variation-analysis.py
patternDetection.py
```

#### SQL Files
```
✅ BIEN: kebab-case.sql
base-query.sql
aggregations.sql
site-filters.sql

❌ MAL:
base_query.sql
Aggregations.sql
siteFilters.sql
```

#### Markdown Files
```
✅ BIEN: UPPERCASE.md para archivos principales
README.md
CHANGELOG.md
CONTRIBUTING.md

✅ BIEN: kebab-case.md para documentación
business-context.md
table-definitions.md
metrics-glossary.md
```

#### Output Files
```
✅ BIEN: Descriptivo con fecha
pdd-mla-process-nov-dic-2025.csv
reporte-pnr-mlb-cdu-sep-oct-2025.html

❌ MAL:
output.csv
report.html
data_final_v2_FINAL.csv
```

### Directory Structure

```
📁 Carpeta raíz: kebab-case
contact-rate-analysis/

📁 Subcarpetas: snake_case
calculations/
test_results/

📁 Archivos: Según tipo (ver arriba)
```

---

## 🧪 Testing Standards

### Unit Test Structure

```python
"""
test_contact_rate.py
Unit tests for contact rate calculations
"""

import unittest
from calculations import contact_rate

class TestContactRateCalculation(unittest.TestCase):
    """Test suite for Contact Rate calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_incoming = 100
        self.valid_driver = 1000
    
    def test_calculate_contact_rate_valid(self):
        """Test CR calculation with valid inputs"""
        result = contact_rate.calculate(
            incoming=self.valid_incoming,
            driver=self.valid_driver
        )
        self.assertEqual(result, 10.0)
    
    def test_calculate_contact_rate_zero_driver(self):
        """Test CR calculation with zero driver"""
        result = contact_rate.calculate(
            incoming=100,
            driver=0
        )
        self.assertIsNone(result)
    
    def test_calculate_contact_rate_negative_incoming(self):
        """Test CR calculation with negative incoming"""
        with self.assertRaises(ValueError):
            contact_rate.calculate(
                incoming=-10,
                driver=1000
            )

if __name__ == '__main__':
    unittest.main()
```

---

## 🔍 Code Review Checklist

### Python
- [ ] PEP 8 compliant
- [ ] Docstrings en todas las funciones
- [ ] Type hints donde sea apropiado
- [ ] Error handling adecuado
- [ ] Logging configurado
- [ ] Constantes definidas al inicio
- [ ] Imports organizados

### SQL
- [ ] CTEs con nombres descriptivos
- [ ] Indentación consistente
- [ ] Comentarios explicativos
- [ ] WHERE 1=1 para filtros
- [ ] JOINs explícitos
- [ ] Header con metadata

### Markdown
- [ ] Estructura clara con headers
- [ ] Code blocks con lenguaje especificado
- [ ] Links descriptivos
- [ ] Tablas bien formateadas
- [ ] Sin errores de ortografía

### General
- [ ] Nombres de archivos consistentes
- [ ] Documentación actualizada
- [ ] Sin código comentado innecesario
- [ ] Sin TODOs sin resolver

---

## 📊 Métricas de Calidad

### Python
```bash
# Linting con pylint
pylint calculations/*.py --rcfile=.pylintrc

# Formateo con black
black calculations/ --line-length 100

# Type checking con mypy
mypy calculations/ --ignore-missing-imports
```

### SQL
```bash
# Formateo con sqlfluff
sqlfluff format sql/*.sql --dialect bigquery
```

---

## 🚀 Pre-commit Hooks (Recomendado)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/PyCQA/pylint
    rev: v2.17.0
    hooks:
      - id: pylint
  
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.0.0
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix
```

---

## 📚 Referencias

- **PEP 8**: https://pep8.org/
- **Google Python Style Guide**: https://google.github.io/styleguide/pyguide.html
- **BigQuery SQL Style Guide**: https://cloud.google.com/bigquery/docs/best-practices-costs

---

**Última actualización**: Enero 2026  
**Versión**: 1.0

---

> 💡 **Tip**: Usa un linter automático para mantener estos estándares sin esfuerzo manual.
