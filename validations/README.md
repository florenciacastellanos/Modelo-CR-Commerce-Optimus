# ✅ Validations - Test Cases & Results

> **Casos de prueba y resultados de validación** del framework de Contact Rate

---

## 📂 Contenido

### `test_cases.json`
Casos de prueba documentados con resultados esperados.

**Estructura**:
```json
{
  "id": "TC001",
  "name": "Nombre descriptivo",
  "commerce_group": "PDD",
  "site": "MLA",
  "dimension": "PROCESS_NAME",
  "period1": "2025-11",
  "period2": "2025-12",
  "expected_total_period1": 99798,
  "expected_total_period2": 112554,
  "status": "PASSED",
  "validation_date": "2026-01-20",
  "notes": "Notas adicionales"
}
```

---

## 📊 Estado de Validación

**✅ MODELO VALIDADO (Enero 2026)**

- **Total Tests**: 7
- **Passed**: 7 (100%)
- **Failed**: 0
- **Precision**: 100% match con data real

### Dimensiones Validadas
- ✅ PROCESS_NAME
- ✅ CDU (Caso de Uso)
- ✅ TIPIFICACION
- ✅ CLA_REASON_DETAIL
- ✅ ENVIRONMENT

### Commerce Groups Validados
- ✅ PDD
- ✅ PNR
- ✅ ME Distribución
- ✅ ME PreDespacho
- ✅ FBM Sellers
- ✅ Pre Venta
- ✅ Post Venta
- ✅ Generales Compra
- ✅ Moderaciones
- ✅ Pagos
- ✅ Full Sellers
- ✅ Experiencia Impositiva

---

## 🧪 Casos de Prueba Clave

### TC001: PDD MLA PROCESS_NAME
- **Período**: Nov-Dic 2025
- **Resultado**: ✅ PASSED
- **Match**: 100% con Jupyter Lab
- **Total Nov**: 99,798 casos
- **Total Dic**: 112,554 casos

### TC007: Threshold Rule Validation
- **Regla**: Si SUM(PROCESS_NAME) >= 50 en CUALQUIER período, incluir TODOS los CDUs
- **Resultado**: ✅ PASSED
- **Caso**: "Post Compra Posterior a la Entrega ME" visible con 45 casos en un período y 55 en otro

---

## 🔍 Cómo Validar

### 1. Ejecutar Test Case

```bash
# Usar el script de producción
python scripts/run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \
                                --period1 "2025-11" --period2 "2025-12"
```

### 2. Comparar Resultados

```python
import json
import pandas as pd

# Cargar test case
with open('validations/test_cases.json', 'r') as f:
    test_cases = json.load(f)

tc = test_cases['test_cases'][0]  # TC001

# Cargar resultado actual
df = pd.read_csv('test/outputs/pdd-mla-process_name-2025-11-2025-12.csv')

# Validar
actual_total_p1 = df['INCOMING_PERIOD1'].sum()
expected_total_p1 = tc['expected_total_period1']

assert actual_total_p1 == expected_total_p1, f"Mismatch: {actual_total_p1} != {expected_total_p1}"
print("✅ Validación exitosa")
```

### 3. Actualizar Test Case

Si el test pasa, actualizar `test_cases.json`:

```json
{
  "status": "PASSED",
  "validation_date": "2026-01-22",
  "notes": "Validado correctamente"
}
```

---

## 📋 Agregar Nuevo Test Case

### Template

```json
{
  "id": "TC00X",
  "name": "[Descripción del test]",
  "commerce_group": "[Commerce Group]",
  "site": "[Site]",
  "dimension": "[Dimension]",
  "period1": "YYYY-MM",
  "period2": "YYYY-MM",
  "expected_total_period1": null,
  "expected_total_period2": null,
  "status": "PENDING",
  "validation_date": null,
  "notes": ""
}
```

---

## 🎯 Criterios de Validación

### PASSED
- Resultados coinciden 100% con data esperada
- Query ejecuta sin errores
- Threshold rule aplicada correctamente
- Exclusiones automáticas funcionando

### FAILED
- Discrepancia en totales (> 1%)
- Errores en ejecución de query
- Threshold rule no aplicada
- Exclusiones incorrectas

### PENDING
- Test no ejecutado aún
- Esperando data de referencia

---

## 📈 Métricas de Calidad

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Pass Rate** | 100% | ✅ |
| **Dimensiones Validadas** | 5/8 | 🟡 |
| **Commerce Groups Validados** | 12/15 | 🟡 |
| **Precision** | 100% | ✅ |
| **Coverage** | 80% | 🟢 |

---

**Última actualización**: Enero 2026  
**Próxima validación**: Febrero 2026
