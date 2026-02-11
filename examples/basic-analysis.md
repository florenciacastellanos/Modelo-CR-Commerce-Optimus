# Ejemplos Básicos de Análisis de Contact Rate

## Ejemplo 1: Análisis Simple - Un Site, Un Mes

### Objetivo
Calcular Contact Rate para MLA (Argentina) en Enero 2026 para PDD y PNR.

### Paso 1: Configurar Parámetros

```python
analysis_parameters = {
    'start_date': '2026-01-01',
    'end_date': '2026-01-31',
    'selected_sites': ['MLA'],
    'selected_agrup_commerce': ['PDD', 'PNR'],
    'output_dimension': 'PROCESS'
}
```

### Paso 2: Ejecutar Query

Ver `/sql/base-query.sql` y reemplazar placeholders.

### Paso 3: Configurar Drivers

```python
drivers_by_site = {
    'MLA': {
        '2026-01': 1500000  # 1.5M órdenes cerradas en Enero
    }
}
```

### Paso 4: Calcular CR

```python
from calculations.contact_rate import calculate_contact_rate

incoming = 22500  # casos incoming
driver = 1500000  # órdenes

cr = calculate_contact_rate(incoming, driver)
print(f"Contact Rate: {cr} pp")
# Output: Contact Rate: 1.5000 pp
```

---

## Ejemplo 2: Análisis MoM - Comparar Dos Meses

### Paso 1: Configurar Parámetros

```python
analysis_parameters = {
    'start_date': '2026-01-01',
    'end_date': '2026-02-28',
    'selected_sites': ['MLA'],
    'selected_agrup_commerce': ['PDD'],
    'output_dimension': 'PROCESS'
}
```

### Paso 2: Configurar Drivers

```python
drivers_by_site = {
    'MLA': {
        '2026-01': 1500000,
        '2026-02': 1600000
    }
}
```

### Paso 3: Calcular Variaciones

```python
from calculations.variation_analysis import calculate_variations_batch
import pandas as pd

data = pd.DataFrame({
    'SITE': ['MLA', 'MLA'],
    'PERIODO': ['2026-01', '2026-02'],
    'INCOMING': [22500, 27200],
    'DRIVER': [1500000, 1600000]
})

# Calculate CR
from calculations.contact_rate import calculate_contact_rate_batch
data = calculate_contact_rate_batch(data, incoming_col='INCOMING', driver_col='DRIVER')

# Calculate variations
data = calculate_variations_batch(data, group_cols=['SITE'])

print(data[['PERIODO', 'CR', 'VAR_ABS_PP', 'VAR_REL_PCT', 'VOLUME_IMPACT']])
```

**Resultado esperado:**
```
  PERIODO      CR  VAR_ABS_PP  VAR_REL_PCT  VOLUME_IMPACT
  2026-01  1.5000        NaN          NaN            NaN
  2026-02  1.7000     0.2000        13.33          3200.0
```

**Interpretación:**
- CR aumentó +0.2 pp (de 1.5 a 1.7)
- Variación relativa: +13.33% (moderada)
- Impacto: +3,200 casos adicionales

---

## Ejemplo 3: Top Drivers de Variación

### Paso 1: Agregar por Proceso

```python
# Supongamos que 'data' tiene datos por proceso
data_by_process = pd.DataFrame({
    'PROCESS_NAME': ['Proceso A', 'Proceso B', 'Proceso C'],
    'VAR_ABS_PP': [0.5, -0.3, 1.2],
    'VOLUME_IMPACT': [800, -500, 1920]
})
```

### Paso 2: Identificar Top Drivers

```python
from calculations.variation_analysis import identify_top_drivers

top_drivers = identify_top_drivers(data_by_process, by='VOLUME_IMPACT', top_n=3, ascending=False)
print(top_drivers)
```

**Resultado:**
```
  PROCESS_NAME  VAR_ABS_PP  VOLUME_IMPACT
  Proceso C           1.2           1920  ← Mayor impacto
  Proceso A           0.5            800
  Proceso B          -0.3           -500  ← Mejora
```

---

## Ver También

- `/docs/analysis-workflow.md` - Flujo completo paso a paso
- `/examples/advanced-queries.md` - Queries avanzadas
- `/calculations/` - Código de cálculos
