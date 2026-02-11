# Cuándo Regenerar Hard Metrics de Demoras

## 🎯 Propósito

Este documento define **triggers y criterios** para regenerar las queries y métricas de demoras en Shipping.

A diferencia de hard metrics pre-calculados (como `eventos`), las métricas de demoras se **generan bajo demanda** según los parámetros del análisis (site, período, granularidad).

---

## 🔄 Modelo de Actualización

### **Modelo Actual: Generación Bajo Demanda**

```
Usuario solicita análisis de CR
         ↓
Sistema parametriza query de demoras
         ↓
Ejecuta query en BigQuery (tiempo real)
         ↓
Obtiene métricas de demoras del período
         ↓
Correlaciona con incoming de CR
```

**Ventaja:** Siempre datos actualizados (D+1)  
**Desventaja:** Requiere ~2-8 min por ejecución

### **Modelo Futuro: Pre-cálculo Mensual (Roadmap)**

```
Fin de mes detectado
         ↓
Script automático genera demoras del mes
         ↓
Guarda en data/demoras_{site}_{YYYYMM}.parquet
         ↓
Usuario consulta → carga Parquet (instantáneo)
```

**Ventaja:** Instantáneo (~2-5 segundos)  
**Desventaja:** Requiere pipeline de actualización mensual

---

## ⏰ Triggers de Regeneración (Modelo Actual)

### 1. **Nuevo Análisis de CR**

**Trigger:** Usuario solicita análisis de ME Distribución (Shipping)

**Criterios:**
```python
if commerce_group in ['ME Distribución', 'ME PreDespacho', 'ME Despacho']:
    generar_query_demoras(
        site=user_site,
        fecha_inicio=periodo_p1_inicio,
        fecha_fin=periodo_p2_fin,
        granularidad=granularidad_analisis
    )
```

**Acción:** Parametrizar y ejecutar query de demoras

**Frecuencia:** Cada análisis de CR en Shipping

---

### 2. **Cambio de Parámetros de Análisis**

**Trigger:** Usuario cambia site, período, o granularidad

**Ejemplo:**
```
Usuario inicial: MLA Nov-Dic mensual
Usuario actualiza: MLA Nov-Dic semanal
  ↓
Regenerar query con granularidad='WEEK'
```

**Acción:** Regenerar query con nuevos parámetros

**Frecuencia:** Cada cambio de parámetros

---

### 3. **Deep Dive en Picking Type**

**Trigger:** Usuario profundiza en Fulfillment, XD, DS, o FLEX

**Ejemplo:**
```
Baseline: Todos los picking types
Deep Dive: Solo Fulfillment
  ↓
Generar query filtrada: picking_type='fulfillment'
```

**Acción:** Parametrizar query con filtro de picking type

**Frecuencia:** Cada deep dive

---

## 📅 Triggers de Pre-cálculo (Modelo Futuro)

### 1. **Fin de Mes**

**Trigger:** Día 1 del mes siguiente (a las 10:00 AM)

**Criterios:**
```python
if today.day == 1 and today.hour == 10:
    for site in ['MLA', 'MLB', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE']:
        generar_parquet_demoras(
            site=site,
            mes=last_month,
            granularidad='MONTH'
        )
```

**Acción:** Generar Parquet por site-mes

**Salida:** `data/demoras_MLA_202511.parquet`, etc.

**Tiempo estimado:** ~30-45 min (todos los sites)

---

### 2. **Pico de CR Detectado**

**Trigger:** Alerta de pico de CR en ME Distribución

**Criterios:**
```python
if cr_variacion > threshold and commerce_group == 'ME Distribución':
    # Generar métricas granulares (semanal/diario)
    generar_query_demoras(
        site=site_alerta,
        fecha_inicio=inicio_pico - 7 days,
        fecha_fin=fin_pico + 7 days,
        granularidad='DAY'  # Más granular para análisis
    )
```

**Acción:** Generar métricas diarias del período afectado

**Frecuencia:** Cada alerta de pico

---

### 3. **Actualización de Tablas Fuente**

**Trigger:** Cambio en esquema de `BT_SHP_SHIPMENTS_SUMMARY` o `BT_SHP_MT_SHIPMENT_SNAPSHOT`

**Monitorear:**
- Nuevos campos en `BUFFERING_TIME`
- Nuevas razones en `DEFERRAL.REASON`
- Cambios en `TM_LT_DEV_TYPE` / `TM_HT_DEV_TYPE`

**Acción:**
1. Actualizar query template
2. Regenerar Parquets del último trimestre
3. Actualizar documentación

**Frecuencia:** Trimestral (revisión proactiva)

---

## 🚨 Casos Especiales

### **Caso 1: Análisis Cross-Site**

**Situación:** Usuario pide análisis de todos los sites

**Acción:**
- Generar query sin filtro de site
- ⚠️ Advertir: tiempo de ejecución ~10-15 min (3 meses)
- Recomendar: reducir ventana temporal a 1 mes

**Alternativa (Modelo Futuro):**
- Cargar Parquets de todos los sites
- Consolidar en dataframe unificado
- Tiempo: ~10-15 segundos

---

### **Caso 2: Período Histórico (>6 meses)**

**Situación:** Usuario pide análisis de varios meses atrás

**Validación:**
```python
if (today - fecha_inicio).days > 180:
    # Verificar disponibilidad de datos históricos
    if not parquet_exists(site, periodo):
        # Generar bajo demanda (puede tardar 15-20 min)
        generar_query_demoras(...)
    else:
        # Cargar Parquet pre-calculado
        load_parquet(site, periodo)
```

**Acción:** Intentar cargar Parquet; si no existe, generar bajo demanda

---

### **Caso 3: Comparación Multi-Período**

**Situación:** Usuario compara Q3 vs Q4

**Acción:**
- Generar 1 query con ambos períodos incluidos
- Usar `DATE_TRUNC(..., QUARTER)` para agrupar
- Evitar 2 queries separadas (más eficiente)

**Optimización:**
```python
# ❌ Ineficiente: 2 queries
query_q3 = generar_query(fecha_inicio='2025-07-01', fecha_fin='2025-10-01')
query_q4 = generar_query(fecha_inicio='2025-10-01', fecha_fin='2026-01-01')

# ✅ Eficiente: 1 query
query_q3_q4 = generar_query(
    fecha_inicio='2025-07-01', 
    fecha_fin='2026-01-01',
    granularidad='MONTH'  # Luego agrupar en Python por quarter
)
```

---

## 📊 Métricas de Validación

Después de regenerar, validar:

### 1. **Volumen de Datos**

```python
# Esperado por configuración
volumenes_esperados = {
    ('MLA', '1_mes'): (3_000_000, 5_000_000),
    ('MLA', '3_meses'): (10_000_000, 15_000_000),
    ('Cross-Site', '3_meses'): (50_000_000, 80_000_000)
}

# Validar
if not (min_esperado <= filas_resultado <= max_esperado):
    raise ValidationError("Volumen fuera de rango esperado")
```

### 2. **Distribución de Performance**

```python
# Delays no deben ser >60% de shipments (indicaría problema en filtros)
delay_rate = (shipments_lt_delay + shipments_ht_delay) / shipments_total

if delay_rate > 0.60:
    raise ValidationError(f"Delay rate anormal: {delay_rate:.1%}")
```

### 3. **Completitud de Métricas**

```python
# Validar que métricas clave no son NULL
required_metrics = [
    'SHIPMENTS', 'SHIPMENTS_LT_DELAY', 'SHIPMENTS_HT_DELAY',
    'CO_ST_SHIPMENTS', 'SHIPMENTS_FF', 'SHIPMENTS_XD'
]

for metric in required_metrics:
    if df[metric].isna().sum() > 0:
        raise ValidationError(f"Métrica {metric} contiene NULLs")
```

---

## 🔧 Scripts de Mantenimiento

### **Script 1: Regeneración Manual**

```python
# scripts/regenerar_demoras_manual.py
from metrics.demoras.scripts.parametrize_shipping_query import generate_query_for_analysis

# Regenerar para período específico
queries = generate_query_for_analysis(
    site='MLA',
    periodo_inicio='2025-11-01',
    periodo_fin='2026-01-01',
    tipo_variacion='mensual'
)

# Ejecutar y validar
# ... (implementación)
```

### **Script 2: Pre-cálculo Automático (Futuro)**

```python
# scripts/precalcular_demoras_mensual.py
import schedule
from datetime import datetime

def precalcular_mes_anterior():
    """Ejecutar el día 1 de cada mes a las 10:00 AM"""
    # ... (implementación)

schedule.every().month.at("10:00").do(precalcular_mes_anterior)
```

---

## 📋 Checklist de Regeneración

Antes de regenerar:

- [ ] Verificar que tablas fuente tienen datos del período solicitado
- [ ] Validar que filtros de negocio están actualizados
- [ ] Confirmar que permisos de BigQuery están vigentes
- [ ] Revisar si existe Parquet pre-calculado (evitar regenerar innecesariamente)

Después de regenerar:

- [ ] Validar volumen de datos (dentro de rango esperado)
- [ ] Validar distribución de métricas (delays, custom offsets, etc.)
- [ ] Validar completitud (sin NULLs en métricas clave)
- [ ] Guardar resultado en `output/` con nomenclatura estándar
- [ ] Actualizar log de ejecuciones (fecha, parámetros, tiempo, resultado)

---

## 📚 Referencias

- **Query template:** `sql/shipping_drivers_optimized_template.sql`
- **Script parametrización:** `scripts/parametrize_shipping_query.py`
- **Fuente de datos:** `FUENTE_DEMORAS.md`
- **Integración CR:** `INTEGRACION_CR.md`

---

**Versión:** 1.0  
**Estado:** ✅ IMPLEMENTADO (modelo bajo demanda)  
**Roadmap:** Pre-cálculo mensual (Q2 2026)  
**Última actualización:** 2026-01-29
