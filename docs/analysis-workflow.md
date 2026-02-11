# 🔄 Workflow de Análisis de Contact Rate

## Visión General

Este documento describe el flujo completo para realizar un análisis de Contact Rate, desde la configuración inicial hasta la generación de insights accionables.

## Flujo Completo (6 Pasos)

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: CONFIGURACIÓN                                      │
│  • Definir periodo (fechas)                                 │
│  • Seleccionar sites (países)                               │
│  • Seleccionar Commerce Groups                              │
│  • Aplicar filtros opcionales (User Types, Environments)    │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: EXTRACCIÓN DE DATOS                                │
│  • Ejecutar query BigQuery                                  │
│  • Aplicar exclusiones automáticas                          │
│  • Calcular AGRUP_COMMERCE                                  │
│  • Agregar por dimensión seleccionada                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: CONFIGURACIÓN DE DRIVERS                           │
│  • Por cada Site                                            │
│  • Por cada Periodo detectado                               │
│  • Configurar valor de Driver manualmente                   │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 4: CÁLCULO DE CONTACT RATE                            │
│  • CR = (Incoming Cases / Driver) × 100                     │
│  • Calcular para cada combinación Site × Periodo            │
│  • Validar resultados                                       │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 5: ANÁLISIS DE VARIACIONES                            │
│  • Variación absoluta (pp)                                  │
│  • Variación relativa (%)                                   │
│  • Impacto en volumen                                       │
│  • Detectar patrones (spikes, drops, strong variations)     │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 6: INTERPRETACIÓN Y ACCIONABLES                       │
│  • Identificar top drivers de variación                     │
│  • Analizar distribución temporal                           │
│  • Comparar con periodos anteriores                         │
│  • Generar insights y recomendaciones                       │
└─────────────────────────────────────────────────────────────┘
```

---

## PASO 1: Configuración

### 1.1 Definir Periodo

**Objetivo:** Establecer el rango de fechas para el análisis.

**Opciones:**
- **Monthly:** Análisis mes a mes
- **Quarterly:** Análisis trimestral

**Ejemplo:**
```python
analysis_parameters = {
    'start_date': '2026-01-01',
    'end_date': '2026-02-28',
    'date_format': 'month'
}
```

**Resultado:** Sistema detecta automáticamente periodos completos:
- 2026-01 (Enero 2026)
- 2026-02 (Febrero 2026)

### 1.2 Seleccionar Sites

**Objetivo:** Definir países a analizar.

**Opciones disponibles:**
- MLA (Argentina)
- MLB (Brasil) ⚠️ Requiere sampling
- MLC (Chile)
- MCO (Colombia)
- MLM (México)
- MLU (Uruguay)
- MPE (Perú)

**Ejemplo:**
```python
analysis_parameters['selected_sites'] = ['MLA', 'MLC', 'MCO']
```

**Consideración:** MLB genera alto volumen → sampling automático.

### 1.3 Seleccionar Commerce Groups

**Objetivo:** Definir grupos de Commerce a analizar.

**Opciones disponibles:** 15 Commerce Groups en 5 categorías.

**Ejemplo:**
```python
analysis_parameters['selected_agrup_commerce'] = ['PDD', 'PNR', 'ME Distribución']
```

**Tip:** Comenzar con 2-3 grupos para análisis inicial.

### 1.4 Filtros Opcionales

#### User Types
```python
analysis_parameters['selected_user_types'] = ['COMPRADOR', 'VENDEDOR']
# Si se omite o se incluyen los 3, no se aplica filtro
```

#### Environments
```python
analysis_parameters['selected_environments'] = ['DS', 'FBM']
# Si se omite o está vacío, no se aplica filtro
```

### 1.5 Dimensión de Análisis

**Objetivo:** Definir cómo se agruparán los datos.

**Opciones:**
- PROCESS (Process Name)
- CDU (Caso de Uso)
- REASON_DETAIL (Reason Detail Group)
- COMMERCE_GROUP (Commerce Group)
- REPORTING_TYPE (Reporting Type)
- ENVIRONMENT (Environment)
- VERTICAL (⚠️ NULL actualmente)
- DOMAIN (⚠️ NULL actualmente)

**Ejemplo:**
```python
analysis_parameters['output_dimension'] = 'PROCESS'
```

### 1.6 Threshold de Casos

**Objetivo:** Filtrar dimensiones con volumen insuficiente manteniendo procesos significativos.

**⚠️ REGLA VALIDADA (Enero 2026):** 

**Si la SUMA TOTAL de un PROCESS_NAME es >= 50 casos en CUALQUIER período de comparación,
se incluyen TODOS los CDUs/dimensiones de ese proceso.**

```python
MIN_PROCESS_INCOMING = 50  # Mínimo de casos TOTALES por proceso por período
```

**Lógica de aplicación:**
```python
# 1. Calcular total por proceso en cada período
process_totals = df.groupby('PROCESS_NAME').agg({
    'INCOMING_PERIOD1': 'sum',
    'INCOMING_PERIOD2': 'sum'
}).reset_index()

# 2. Identificar procesos que cumplen el threshold
valid_processes = process_totals[
    (process_totals['INCOMING_PERIOD1'] >= 50) | 
    (process_totals['INCOMING_PERIOD2'] >= 50)
]['PROCESS_NAME'].tolist()

# 3. Incluir TODOS los CDUs de procesos válidos
df = df[df['PROCESS_NAME'].isin(valid_processes)]
```

**Beneficios validados:**
- ✅ Captura procesos significativos con CDUs distribuidos
- ✅ No pierde información relevante
- ✅ Permite análisis completo (ej: "Post Compra Posterior a la Entrega ME" con 146 casos en 16 CDUs)

**Threshold agregado (opcional):**
```python
analysis_parameters['custom_threshold'] = 100  # Para nivel agregado (default)
```

---

## PASO 2: Extracción de Datos

### 2.1 Construir Query BigQuery

**Archivo:** `/sql/base-query.sql`

**Proceso:**
1. Reemplazar placeholders con parámetros
2. Aplicar filtros de sites, commerce groups, user types, environments
3. Ejecutar query en BigQuery

**Ejemplo de ejecución:**
```python
from melitk.bigquery import BigQueryClientBuilder

connector = BigQueryClientBuilder().with_encoded_secret('DME000131_DEV').build()

final_query = BASE_QUERY.format(
    fecha_inicio='2026-01-01',
    fecha_fin='2026-02-28',
    sites="'MLA', 'MLC'",
    agrup_commerce="'PDD', 'PNR'",
    user_types="'Comprador', 'Vendedor'",
    environment_filter=""  # o filtro específico
)

response = connector.query_to_df(final_query)
data = response.df
```

### 2.2 Validar Datos Extraídos

**Checks:**
```python
# 1. Volumen total
print(f"Total cases: {data['CANT_CASES'].sum()}")

# 2. Distribución por site
print(data.groupby('SIT_SITE_ID')['CANT_CASES'].sum())

# 3. Distribución por Commerce Group
print(data.groupby('AGRUP_COMMERCE')['CANT_CASES'].sum())

# 4. Periodos detectados
print(data['MES'].unique())
```

### 2.3 Optimizar Memoria (si aplica)

**Trigger:** Datasets > 50,000 filas

**Proceso automático:**
```python
from utils.memory_optimization import optimize_dataframe_memory

data = optimize_dataframe_memory(data)
```

**Resultado:** 50-70% reducción de memoria.

### 2.4 Aplicar Threshold

**Filtrar dimensiones con volumen insuficiente:**
```python
threshold = analysis_parameters['custom_threshold']

# Agregar por dimensión
agg_data = data.groupby(['SIT_SITE_ID', 'MES', 'PROCESS_NAME']).agg({
    'CANT_CASES': 'sum',
    'CAS_CASE_ID': 'nunique'
}).reset_index()

# Aplicar threshold
agg_data = agg_data[agg_data['CANT_CASES'] >= threshold]
```

---

## PASO 3: Configuración de Drivers

### 3.1 Detectar Periodos y Sites

**Automático:** El sistema detecta combinaciones únicas de Site × Periodo.

**Ejemplo:**
```python
sites = ['MLA', 'MLC']
periodos = ['2026-01', '2026-02']

# Resultado: 4 combinaciones
# MLA × 2026-01
# MLA × 2026-02
# MLC × 2026-01
# MLC × 2026-02
```

### 3.2 Configurar Drivers Manualmente

**Proceso:**

Para cada combinación Site × Periodo, configurar valor de Driver:

```python
drivers_by_site = {
    'MLA': {
        '2026-01': 1500000,  # 1.5M órdenes en Enero MLA
        '2026-02': 1600000   # 1.6M órdenes en Febrero MLA
    },
    'MLC': {
        '2026-01': 250000,   # 250K órdenes en Enero MLC
        '2026-02': 270000    # 270K órdenes en Febrero MLC
    }
}
```

**Fuentes de Drivers:**
- Dashboards internos
- Tablas de órdenes (BT_ORD_ORDERS)
- Reportes de BI
- Datos históricos

### 3.3 Validar Drivers

**Checks:**
```python
# 1. Todos los periodos tienen driver
for site in sites:
    for periodo in periodos:
        assert drivers_by_site[site][periodo] > 0, f"Missing driver for {site} × {periodo}"

# 2. Drivers son coherentes (variación < 50% MoM)
for site in sites:
    values = list(drivers_by_site[site].values())
    for i in range(1, len(values)):
        variation_pct = abs((values[i] - values[i-1]) / values[i-1] * 100)
        if variation_pct > 50:
            print(f"⚠️ Warning: {site} driver variation > 50% MoM")
```

---

## PASO 4: Cálculo de Contact Rate

### 4.1 Fórmula

```python
def calculate_contact_rate(incoming, driver):
    """
    Calculate Contact Rate in percentage points (pp)
    
    Args:
        incoming (float): Total incoming cases
        driver (float): Driver value
    
    Returns:
        float: Contact Rate in pp (4 decimals)
    """
    if driver and driver > 0:
        return round((incoming / driver) * 100, 4)
    return None
```

### 4.2 Aplicar Cálculo

```python
# Agregar incoming por Site × Periodo
incoming_by_site_periodo = data.groupby(['SIT_SITE_ID', 'MES'])['CANT_CASES'].sum().reset_index()
incoming_by_site_periodo.rename(columns={'CANT_CASES': 'INCOMING_CASES'}, inplace=True)

# Agregar drivers
incoming_by_site_periodo['DRIVER'] = incoming_by_site_periodo.apply(
    lambda row: drivers_by_site.get(row['SIT_SITE_ID'], {}).get(row['MES'], 0),
    axis=1
)

# Calcular CR
incoming_by_site_periodo['CR'] = incoming_by_site_periodo.apply(
    lambda row: calculate_contact_rate(row['INCOMING_CASES'], row['DRIVER']),
    axis=1
)
```

### 4.3 Validar Resultados

```python
# 1. CRs dentro de rango esperado (0.5 - 15.0 pp)
assert incoming_by_site_periodo['CR'].min() >= 0.5, "CR too low - check data"
assert incoming_by_site_periodo['CR'].max() <= 15.0, "CR too high - check data"

# 2. No hay NULLs
assert incoming_by_site_periodo['CR'].notna().all(), "NULL CRs found"

# 3. Visualizar
print(incoming_by_site_periodo)
```

---

## PASO 5: Análisis de Variaciones

### 5.1 Variación Absoluta (pp)

```python
# Ordenar por Site y Periodo
incoming_by_site_periodo = incoming_by_site_periodo.sort_values(['SIT_SITE_ID', 'MES'])

# Calcular variación absoluta
incoming_by_site_periodo['CR_PREV'] = incoming_by_site_periodo.groupby('SIT_SITE_ID')['CR'].shift(1)
incoming_by_site_periodo['VAR_ABS_PP'] = incoming_by_site_periodo['CR'] - incoming_by_site_periodo['CR_PREV']
```

### 5.2 Variación Relativa (%)

```python
incoming_by_site_periodo['VAR_REL_PCT'] = (
    (incoming_by_site_periodo['CR'] - incoming_by_site_periodo['CR_PREV']) / 
    incoming_by_site_periodo['CR_PREV']
) * 100
```

### 5.3 Impacto en Volumen

```python
incoming_by_site_periodo['VOLUME_IMPACT'] = (
    incoming_by_site_periodo['VAR_ABS_PP'] / 100 * incoming_by_site_periodo['DRIVER']
)
```

### 5.4 Detectar Patrones

```python
from calculations.pattern_detection import detect_patterns

patterns = detect_patterns(incoming_by_site_periodo)

# Resultado:
# - spikes: [list of detected spikes]
# - drops: [list of detected drops]
# - strong_variations: [list of strong MoM variations]
# - concentrations: [list of temporal concentrations]
```

---

## PASO 6: Interpretación y Accionables

### 6.1 Identificar Top Drivers de Variación

**Por dimensión seleccionada:**

```python
# Agregar por dimensión (ej: PROCESS_NAME)
variations_by_process = data.groupby(['SIT_SITE_ID', 'MES', 'PROCESS_NAME']).agg({
    'CANT_CASES': 'sum'
}).reset_index()

# Calcular CR por proceso
# ... (similar a paso 4)

# Ordenar por variación absoluta
top_variations = variations_by_process.sort_values('VAR_ABS_PP', ascending=False).head(10)

print("Top 10 Drivers de Variación:")
print(top_variations[['PROCESS_NAME', 'VAR_ABS_PP', 'VAR_REL_PCT', 'VOLUME_IMPACT']])
```

### 6.2 Analizar Distribución Temporal

**Por día del mes:**

```python
# Extraer día del mes
data['DAY'] = data['CONTACT_DATE_ID'].dt.day

# Distribución diaria
daily_dist = data.groupby(['SIT_SITE_ID', 'MES', 'DAY'])['CANT_CASES'].sum().reset_index()

# Detectar días de concentración
threshold_concentration = 0.30
for site in sites:
    for periodo in periodos:
        subset = daily_dist[(daily_dist['SIT_SITE_ID'] == site) & (daily_dist['MES'] == periodo)]
        total_cases = subset['CANT_CASES'].sum()
        
        # Top 3 días
        top3_days = subset.nlargest(3, 'CANT_CASES')
        top3_cases = top3_days['CANT_CASES'].sum()
        concentration = top3_cases / total_cases
        
        if concentration > threshold_concentration:
            print(f"⚠️ {site} × {periodo}: Concentration = {concentration:.2%}")
            print(f"   Top 3 days: {top3_days['DAY'].tolist()}")
```

### 6.3 Comparar con Periodos Anteriores

**Tendencia histórica:**

```python
# Si hay datos de meses anteriores
historical_data = ...  # cargar datos históricos

# Calcular CR histórico
historical_cr = calculate_historical_cr(historical_data, drivers_historical)

# Comparar tendencia
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(historical_cr['MES'], historical_cr['CR'], marker='o', label='CR Histórico')
plt.axhline(y=historical_cr['CR'].mean(), color='r', linestyle='--', label='Promedio')
plt.xlabel('Periodo')
plt.ylabel('Contact Rate (pp)')
plt.title('Tendencia de CR - MLA')
plt.legend()
plt.grid(True)
plt.show()
```

### 6.4 Generar Insights y Recomendaciones

**Template de reporte:**

```markdown
## Executive Summary - Contact Rate Analysis

### Periodo Analizado
- Start: {start_date}
- End: {end_date}
- Sites: {sites}
- Commerce Groups: {commerce_groups}

### Hallazgos Principales

1. **Variación Total:**
   - MLA: {var_mla_pp} pp ({var_mla_pct}%)
   - MLC: {var_mlc_pp} pp ({var_mlc_pct}%)

2. **Top Drivers de Variación:**
   - {process_1}: +{var_1} pp (impacto: +{impact_1} casos)
   - {process_2}: +{var_2} pp (impacto: +{impact_2} casos)
   - {process_3}: -{var_3} pp (impacto: -{impact_3} casos)

3. **Patrones Detectados:**
   - {num_spikes} Spikes detectados
   - {num_drops} Drops detectados
   - {num_strong_vars} Strong Variations

### Recomendaciones

1. **Inmediatas:**
   - Investigar causa raíz de spike en {process_spike}
   - Validar mejora en {process_improvement}

2. **Corto Plazo:**
   - Implementar mejoras en {process_target}
   - Monitorear evolución de {commerce_group}

3. **Mediano Plazo:**
   - Automatizar procesos con alto CR
   - Mejorar documentación/FAQs
```

---

## Consideraciones Especiales

### MLB (Brasil) - Sampling

**Problema:** Volumen extremadamente alto causa timeouts.

**Solución:** Aplicar sampling sistemático.

**Referencia:** `/sql/sampling-strategy.sql`

**Proceso:**
1. Estimar filas totales: `num_agrup × num_months × 50,000`
2. Si estimación > 150,000 → aplicar sampling
3. Límite min: 150,000 filas
4. Límite max: 200,000 filas
5. Método: `ORDER BY RAND() LIMIT {limit}`

### VERTICAL y DOMAIN NULL

**Problema:** Campos NULL por tabla no disponible.

**Workaround:** Usar otras 6 dimensiones disponibles.

**Esperado:** Resolución futura cuando tabla se identifique.

### Memory Optimization

**Trigger:** Datasets > 50,000 filas

**Acciones automáticas:**
- Categorizar strings con <50% unique values
- Downcast int/float a tipos menores
- Resultado: 50-70% reducción memoria

**Referencia:** `/utils/memory-optimization.py`

---

## Checklist de Análisis

### ✅ Pre-Análisis
- [ ] Periodo definido (fechas válidas)
- [ ] Sites seleccionados
- [ ] Commerce Groups seleccionados
- [ ] Dimensión de análisis definida
- [ ] Threshold configurado

### ✅ Extracción
- [ ] Query ejecutada sin errores
- [ ] Volumen de datos esperado
- [ ] Exclusiones aplicadas correctamente
- [ ] AGRUP_COMMERCE calculado
- [ ] Threshold aplicado

### ✅ Configuración de Drivers
- [ ] Drivers configurados para todos los Site × Periodo
- [ ] Drivers > 0 para todas las combinaciones
- [ ] Drivers coherentes (variación < 50% MoM)
- [ ] Fuentes de drivers documentadas

### ✅ Cálculo de CR
- [ ] CR calculado para todos los Site × Periodo
- [ ] CRs dentro de rango esperado (0.5-15.0 pp)
- [ ] No hay NULLs en CR
- [ ] Resultados validados

### ✅ Análisis de Variaciones
- [ ] Variación absoluta calculada
- [ ] Variación relativa calculada
- [ ] Impacto en volumen calculado
- [ ] Patrones detectados

### ✅ Interpretación
- [ ] Top drivers identificados
- [ ] Distribución temporal analizada
- [ ] Comparación histórica realizada
- [ ] Insights generados
- [ ] Recomendaciones documentadas

---

## Referencias

- **Queries:** `/sql/base-query.sql`
- **Cálculos:** `/calculations/contact-rate.py`
- **Patrones:** `/calculations/pattern-detection.py`
- **Drivers:** `/calculations/drivers-management.py`
- **Contexto:** `/docs/business-context.md`
- **Tablas:** `/docs/table-definitions.md`
- **Métricas:** `/docs/metrics-glossary.md`

---

**Última actualización:** Enero 2026  
**Versión:** 2.5 (Commerce)  
**Source:** V37.ipynb
