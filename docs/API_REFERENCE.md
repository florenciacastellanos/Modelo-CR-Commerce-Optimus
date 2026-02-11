# 📚 API Reference - Funciones y Módulos

> **Referencia técnica** de funciones Python en el repositorio

---

## 📦 Módulos

### `calculations/contact-rate.py`

#### `calculate_contact_rate(incoming, driver)`
Calcula Contact Rate en puntos porcentuales.

**Parámetros**:
- `incoming` (int): Número de casos incoming
- `driver` (int): Métrica de negocio

**Retorna**:
- `float`: CR en pp, o `None` si driver <= 0

**Ejemplo**:
```python
cr = calculate_contact_rate(100, 1000)
# Retorna: 10.0
```

---

### `calculations/variation-analysis.py`

#### `calculate_variation_absolute(cr_current, cr_previous)`
Calcula variación absoluta.

**Fórmula**: `Δ = CR_actual - CR_anterior`

#### `calculate_variation_percentage(cr_current, cr_previous)`
Calcula variación porcentual.

**Fórmula**: `% = ((CR_actual - CR_anterior) / CR_anterior) × 100`

---

### `utils/memory-optimization.py`

#### `optimize_dataframe_memory(df)`
Optimiza uso de memoria de DataFrame.

**Parámetros**:
- `df` (pd.DataFrame): DataFrame a optimizar

**Retorna**:
- `pd.DataFrame`: DataFrame optimizado

**Reducción típica**: 40-60%

---

## 🔧 Scripts

### `scripts/run_analysis.py`

**Uso**:
```bash
python run_analysis.py --commerce-group "PDD" --site "MLA" \\
                       --dimension "PROCESS_NAME" \\
                       --period1 "2025-11" --period2 "2025-12"
```

**Parámetros**:
- `--commerce-group`: Commerce Group name
- `--site`: Site code
- `--dimension`: Analysis dimension
- `--period1`, `--period2`: Períodos (YYYY-MM)
- `--output-dir`: Output directory (default: test/outputs/)
- `--threshold`: Minimum threshold (default: 50)
- `--format`: Output format (csv, html, both)

---

## 📊 Constantes

### `config/business-constants.py`

```python
CR_MULTIPLIER = 100
MIN_CASES_THRESHOLD = 100
MIN_PROCESS_INCOMING = 50
EXCLUDED_QUEUES = [2131, 230, 1102, 1241, 2075, 2294, 2295]
EXCLUDED_PROCESSES = [1312]
EXCLUDED_CI_REASONS = [2592, 6588, 10068, 2701, 10048]
EXCLUDED_SITE = 'MLV'
```

---

**Última actualización**: Enero 2026
