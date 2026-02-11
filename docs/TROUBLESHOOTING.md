# 🔧 Troubleshooting - Solución de Problemas

> **Guía de solución** para problemas comunes en Contact Rate Analysis

---

## 🚨 Errores de BigQuery

### Error: "403 Quota exceeded"

**Síntoma**:
```
403 POST https://bigquery.googleapis.com/bigquery/v2/projects/meli-bi-data/jobs
Quota exceeded: Your project exceeded quota for max number of jobs
```

**Solución**:
```python
# Cambiar prioridad a BATCH
job_config = bigquery.QueryJobConfig(priority="BATCH")
df = client.query(query, job_config=job_config).to_dataframe()
```

---

### Error: "403 Caller does not have required permission"

**Síntoma**:
```
403: Caller does not have required permission to use project meli-bi-data
```

**Solución**:
```bash
# Re-autenticar
gcloud auth application-default login
gcloud config set project meli-bi-data
```

---

### Error: "Division by zero"

**Síntoma**:
```python
ZeroDivisionError: division by zero
```

**Causa**: Driver = 0

**Solución**:
```python
if driver and driver > 0:
    cr = (incoming / driver) * 100
else:
    cr = None
```

---

## 📊 Errores de Datos

### "No se encontraron datos"

**Causas posibles**:
1. **Formato de fecha incorrecto**: Usar `YYYY-MM`
2. **Site incorrecto**: Verificar código (MLA, MLB, etc.)
3. **Commerce Group sin datos**: Verificar filtro
4. **Período sin datos**: Verificar disponibilidad en BigQuery

**Solución**:
```python
# Verificar datos disponibles
query = """
SELECT PERIOD_MONTH, COUNT(*) as total
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE SITE_ID = 'MLA'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 12
"""
```

---

### "Proceso no aparece en resultados"

**Causas**:
1. **Threshold**: Incoming < 50 en ambos períodos
2. **Exclusión automática**: Queue/Process/CI Reason excluido
3. **FLAG_EXCLUDE_NUMERATOR_CR = 1**

**Solución**:
Ver `config/business-constants.py` para exclusiones.

---

## 💻 Errores de Código

### UnicodeEncodeError en Windows

**Síntoma**:
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solución**:
```python
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

### ModuleNotFoundError

**Síntoma**:
```
ModuleNotFoundError: No module named 'google.cloud'
```

**Solución**:
```bash
pip install google-cloud-bigquery pandas
```

---

## 🐛 Errores de Lógica

### Threshold rule no aplicada

**Síntoma**: Procesos con suma >= 50 no aparecen

**Solución**:
Verificar lógica en query:
```sql
HAVING (INCOMING_PERIOD1 >= 50 OR INCOMING_PERIOD2 >= 50)
```

---

### Variación porcentual incorrecta

**Síntoma**: Variación % no coincide con esperado

**Causa**: División por cero o período anterior = 0

**Solución**:
```python
if previous > 0:
    var_pct = ((current - previous) / previous) * 100
else:
    var_pct = None
```

---

## ⚡ Problemas de Performance

### Query muy lenta

**Soluciones**:
1. Usar sampling para MLB
2. Limitar rango de fechas
3. Usar BATCH priority
4. Filtrar temprano en WHERE

---

### Memoria insuficiente

**Solución**:
```python
from utils import memory_optimization
df = memory_optimization.optimize_dataframe_memory(df)
```

---

## 📝 Más Ayuda

Si tu problema no está aquí:
1. Revisa `FAQ.md`
2. Revisa `docs/GUIDELINES.md`
3. Abre un Issue en GitHub

---

**Última actualización**: Enero 2026
