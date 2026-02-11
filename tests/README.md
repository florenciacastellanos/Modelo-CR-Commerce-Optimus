# 🧪 Tests - Unit Tests

> **Unit tests** para validar la lógica de cálculos y funciones

---

## 📂 Contenido

### `test_contact_rate.py`
Tests unitarios para cálculos de Contact Rate.

**Tests incluidos**:
- Cálculo de CR con inputs válidos
- Manejo de división por cero
- Cálculo de variaciones (absoluta y porcentual)
- Regla de threshold (>= 50 en ANY período)
- Exclusiones automáticas (queues, sites, processes)

---

## 🚀 Ejecutar Tests

### Todos los tests
```bash
python -m pytest tests/ -v
```

### Test específico
```bash
python -m pytest tests/test_contact_rate.py -v
```

### Con coverage
```bash
python -m pytest tests/ --cov=calculations --cov=config --cov-report=html
```

---

## 📊 Estructura de Tests

### Test Case Template

```python
def test_nombre_descriptivo(self):
    """Descripción del test"""
    # Arrange
    input_value = 100
    expected_output = 10.0
    
    # Act
    result = calculate_function(input_value)
    
    # Assert
    self.assertEqual(result, expected_output)
```

---

## ✅ Tests Actuales

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_calculate_contact_rate_valid` | CR con inputs válidos | ✅ |
| `test_calculate_contact_rate_zero_driver` | Manejo de driver = 0 | ✅ |
| `test_calculate_variation_absolute` | Variación absoluta | ✅ |
| `test_calculate_variation_percentage` | Variación porcentual | ✅ |
| `test_threshold_rule_sum_any_period` | Threshold rule validada | ✅ |
| `test_queue_exclusion` | Exclusión de queues | ✅ |
| `test_site_exclusion` | Exclusión de sites | ✅ |

---

## 📋 Agregar Nuevos Tests

### 1. Crear archivo de test

```python
# tests/test_new_feature.py
import unittest

class TestNewFeature(unittest.TestCase):
    def test_feature(self):
        # Test implementation
        pass
```

### 2. Ejecutar

```bash
python -m pytest tests/test_new_feature.py -v
```

---

## 🎯 Coverage Goals

- **Target**: 80% code coverage
- **Current**: TBD
- **Priority**: `calculations/` y `config/`

---

**Última actualización**: Enero 2026
