# Hard Metrics: Demoras en Shipping

## 🎯 Propósito

Esta sección contiene **hard data de demoras, performance y composition de Shipping** para enriquecer el análisis de Contact Rate en procesos de **ME Distribución** (Envíos).

## 📊 ¿Qué métricas incluye?

### 1. **Performance de Envíos**
- **Lead Time (LT):** Delays, early, on-time (desde creación hasta entrega)
- **Handling Time (HT):** Delays, early, on-time (desde promesa hasta entrega)
- **Shipments estancados:** Sin métrica de Lead Time

### 2. **Composition (Custom Offsets)**
- **Custom Offset Soft Time (CO_ST):** SHIFT + EXPAND aplicados
- **Custom Offset Handling Time (CO_HT):** Offsets en handling time
- **Buffering por categoría:** Operational, Middle Mile, Last Mile, Seller

### 3. **Network Efficiencies**
- No-rush (demora intencional para optimización)
- Grouping (agrupación de envíos)
- MDD (My Delivery Day - día elegido por usuario)
- Bulky (productos voluminosos)
- Proximity (cercanía geográfica)
- Promise Weekend (promesa en fin de semana)

### 4. **Distribución por Picking Type**
- Fulfillment (FF)
- Cross-docking (XD)
- Drop-off (DS)
- Flex (FLEX)

## 🔗 Relación con Contact Rate

Las demoras en Shipping pueden generar contactos por:

| Métrica de Demora | Proceso CR Relacionado | Tipificaciones Comunes |
|-------------------|------------------------|------------------------|
| **SHIPMENTS_LT_DELAY** | ME Distribución - Despacho | "¿Dónde está mi pedido?", Demora en entrega |
| **SHIPMENTS_HT_DELAY** | ME Distribución - Despacho | Promesa incumplida, Reclamo por demora |
| **SHIPMENTS_ESTANCADOS** | ME Distribución - PreDespacho | Sin actualización de tracking |
| **CO_ST_SHIPMENTS** | ME Distribución - Despacho | Cambio de promesa, Demora no comunicada |
| **BUFF_* (buffering)** | ME Distribución - Despacho | Cambio de fecha de entrega |

**Ver análisis completo en:** `INTEGRACION_CR.md`

## 📂 Estructura

```
metrics/demoras/
├── README.md (este archivo)
├── FUENTE_DEMORAS.md (detalle de tablas y campos)
├── CUANDO_REGENERAR.md (cuándo actualizar)
├── INTEGRACION_CR.md (análisis de relación con CR)
├── sql/
│   └── shipping_drivers_optimized_template.sql
├── scripts/
│   └── parametrize_shipping_query.py
└── data/ (placeholder para futuros parquets)
```

## 🚀 Uso Rápido

### Opción 1: Script Python (RECOMENDADO)

```python
from metrics.demoras.scripts.parametrize_shipping_query import parametrize_shipping_query, save_parametrized_query

# Generar query parametrizada
query = parametrize_shipping_query(
    site='MLA',
    fecha_inicio='2025-11-01',
    fecha_fin='2026-01-01',
    granularidad='MONTH'
)

# Guardar
output_path = save_parametrized_query(query, 'shipping_mla_nov_dic.sql')
print(f"Query guardada en: {output_path}")
```

### Opción 2: Ejecutar ejemplos predefinidos

```powershell
# Desde la raíz del repositorio
python -m metrics.demoras.scripts.parametrize_shipping_query
```

Esto genera queries de ejemplo en `sql/` listas para ejecutar.

### Opción 3: Ejecución directa en BigQuery

```powershell
Get-Content sql/shipping_mla_nov_dic.sql -Raw | bq query --use_legacy_sql=false --format=csv > output/demoras_mla.csv
```

## ⚡ Optimizaciones

Esta implementación usa **tablas temporales** para reducir tiempo de ejecución:

| Configuración | Sin TEMP TABLEs | Con TEMP TABLEs | Mejora |
|---------------|-----------------|-----------------|--------|
| 3 meses × Single-Site | 10-15 min | **5-8 min** | 40-50% |
| 1 mes × Single-Site | 5-7 min | **2-3 min** | 50-60% |

**Costo estimado:** $0.30-1.20 USD por ejecución (1-3 meses)

## 📋 Checklist de Integración

Antes de usar estas métricas en un análisis de CR:

- [ ] Verificar que el período coincide con el análisis de incoming
- [ ] Confirmar que el site está filtrado correctamente (o Cross-Site)
- [ ] Validar que la granularidad (MONTH/WEEK/DAY) es la misma que incoming
- [ ] Ejecutar query y guardar resultado en `output/demoras_{site}_{periodo}.csv`
- [ ] Cruzar con incoming por `SIT_SITE_ID` + `PERIOD_ID`

## 🔍 Próximos Pasos

1. **Análisis de Correlación:** Identificar qué métricas de demora correlacionan más con picos de CR
2. **Pre-cálculo Parquet:** Generar archivos `.parquet` mensuales (similar a eventos)
3. **Integración Automática:** Script que combine demoras + incoming + drivers automáticamente
4. **Alertas Proactivas:** Detectar cuando delays superan umbral y pueden generar picos de CR

## 📚 Referencias

- **Fuente de datos:** `FUENTE_DEMORAS.md`
- **Triggers de actualización:** `CUANDO_REGENERAR.md`
- **Análisis CR:** `INTEGRACION_CR.md`
- **Guía general de hard metrics:** `../GUIA_USUARIO.md`
- **Índice completo:** `../INDICE.md`

---

**Versión:** 1.0  
**Estado:** ✅ IMPLEMENTADO  
**Última actualización:** 2026-01-29
