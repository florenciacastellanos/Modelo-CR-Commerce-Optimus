# 🎉 Métricas de Correlación con Eventos Comerciales

**Propósito:** Pre-calcular correlaciones entre incoming de CR y eventos comerciales (Black Friday, Cyber Monday, etc.) basadas en fecha de orden (`ORD_CLOSED_DT`).

---

## 🎯 Problema que Resuelve

### **Situación Actual (Sin Métricas)**
- Golden Templates analizan **muestra** de 100 casos por tipificación
- Correlación se calcula on-the-fly en cada reporte
- Precisión limitada por tamaño de muestra
- Tiempo de ejecución: 8-10 minutos

### **Con Métricas Duras**
- Correlación sobre **TODO el incoming** del mes
- Pre-calculado 1 vez → usado N veces
- Precisión total (todos los casos)
- Tiempo de ejecución: 2-3 minutos

---

## 📊 Datos Generados

### **Archivos**

```
/metrics/eventos/data/
├── correlacion_mlb_2025_11.parquet  (Nov 2025 - Brasil)
├── correlacion_mlb_2025_12.parquet  (Dic 2025 - Brasil)
├── correlacion_mla_2025_11.parquet  (Nov 2025 - Argentina)
├── correlacion_mla_2025_12.parquet  (Dic 2025 - Argentina)
└── metadata.json                    (Metadata general)
```

### **Schema del Parquet**

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `SITE` | str | Site code | 'MLB' |
| `PERIODO` | date | Período YYYY-MM-DD | '2025-12-01' |
| `COMMERCE_GROUP` | str | Commerce Group | 'PDD' |
| `TIPIFICACION` | str | Tipificación | 'REPENTANT_BUYER' |
| `PROCESO` | str | Proceso (opcional) | 'PDD - ML' |
| `EVENTO` | str | Nombre del evento | 'Black Friday Brasil' |
| `FECHA_INICIO` | date | Inicio del evento | '2025-11-28' |
| `FECHA_FIN` | date | Fin del evento | '2025-11-28' |
| `CASOS` | int | # casos con orden en evento | 7653 |
| `CASOS_TOTALES` | int | Total casos en dimensión | 153014 |
| `PORCENTAJE` | float | % correlacionado | 5.0 |
| `GENERADO` | datetime | Timestamp generación | '2026-01-27 12:30:00' |

---

## 🛠️ Generación de Métricas

### **Script: `generar_correlaciones.py`**

**Uso:**
```bash
# Generar correlaciones para un site y período
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12

# Generar para múltiples sites
python metrics/eventos/generar_correlaciones.py --sites MLB,MLA,MCO --periodo 2025-12

# Generar para rango de períodos
python metrics/eventos/generar_correlaciones.py --site MLB --desde 2025-11 --hasta 2025-12
```

**Proceso:**
1. Lee **TODO el incoming** del período (no muestra)
2. Join con `DM_CX_POST_PURCHASE` para obtener `ORD_CLOSED_DT`
3. Calcula correlación por: site × periodo × commerce_group × tipificación × evento
4. Guarda parquet + metadata.json

**Tiempo estimado:**
- 1 site × 1 período: ~3-5 minutos
- 7 sites × 1 período: ~15-20 minutos

---

## 📖 Cómo Usar en Reportes

### **Ejemplo 1: Golden Template PDD**

```python
import pandas as pd
from pathlib import Path

# Leer métricas pre-calculadas
metrics_path = Path('metrics/eventos/data')
file_corr = metrics_path / f'correlacion_{site}_{periodo.replace("-", "_")}.parquet'

if file_corr.exists():
    df_correlaciones = pd.read_parquet(file_corr)
    
    # Filtrar por commerce group y tipificación
    corr_tipif = df_correlaciones[
        (df_correlaciones['COMMERCE_GROUP'] == 'PDD') &
        (df_correlaciones['TIPIFICACION'] == tipificacion_actual)
    ]
    
    # Usar en reporte
    for _, row in corr_tipif.iterrows():
        print(f"{row['EVENTO']}: {row['CASOS']:,} casos ({row['PORCENTAJE']:.1f}%)")
else:
    print(f"[WARNING] Métricas no encontradas: {file_corr}")
    print("[INFO] Calculando correlación on-the-fly (modo fallback)")
    # ... calcular como antes
```

### **Ejemplo 2: Análisis Cross-Site**

```python
# Comparar correlación de Black Friday entre sites
sites = ['MLB', 'MLA', 'MCO', 'MLC']
evento = 'Black Friday'

for site in sites:
    df = pd.read_parquet(f'metrics/eventos/data/correlacion_{site}_2025_11.parquet')
    bf_data = df[df['EVENTO'].str.contains('Black Friday')]
    print(f"{site}: {bf_data['CASOS'].sum():,} casos correlacionados")
```

---

## 🎯 Eventos Comerciales - Fuente Dinámica

### **⭐ IMPORTANTE: Fuente Oficial de Eventos**

Los eventos comerciales y sus fechas se obtienen **dinámicamente** desde:

```
meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT
```

**Ventajas:**
- ✅ Fechas siempre actualizadas desde fuente oficial
- ✅ No requiere hardcodear fechas en código
- ✅ Captura rangos completos de eventos (fecha_inicio a fecha_fin)
- ✅ Incluye todos los eventos comerciales registrados

**Campos utilizados:**
```sql
SELECT
    SIT_SITE_ID,           -- Site (MLB, MLA, etc.)
    EVENT_NAME,            -- Nombre del evento
    DATE(EVENT_START_DATE) -- Fecha inicio del evento
    DATE(EVENT_END_DATE)   -- Fecha fin del evento
FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT
```

**Ejemplo de datos:**
| Site | Evento | Fecha Inicio | Fecha Fin | Días |
|------|--------|--------------|-----------|------|
| MLB | Black Friday Brasil | 2025-11-28 | 2025-11-30 | 3 |
| MLB | Cyber Monday | 2025-12-01 | 2025-12-05 | 5 |
| MLB | Natal | 2025-12-20 | 2025-12-25 | 6 |
| MLA | Black Friday | 2025-11-28 | 2025-11-29 | 2 |

**Nota:** Las fechas exactas varían por año y site. El script consulta automáticamente los eventos relevantes para el período solicitado.

---

## 🔍 Validación de Datos

### **Checks Automáticos**

El script generador incluye validación:

```python
# 1. Completitud
assert len(df_corr) > 0, "No se generaron correlaciones"

# 2. Rango de valores
assert df_corr['PORCENTAJE'].between(0, 100).all(), "Porcentajes fuera de rango"

# 3. Consistencia
assert (df_corr['CASOS'] <= df_corr['CASOS_TOTALES']).all(), "Casos > Total"

# 4. No duplicados
assert not df_corr.duplicated(['SITE', 'PERIODO', 'TIPIFICACION', 'EVENTO']).any()
```

### **Metadata.json**

Ejemplo:
```json
{
  "site": "MLB",
  "periodo": "2025-12",
  "generated_at": "2026-01-27T12:30:00",
  "total_rows": 156,
  "total_incoming": 491334,
  "total_casos_correlacionados": 45230,
  "porcentaje_correlacionado_global": 9.2,
  "eventos_incluidos": [
    "Black Friday Brasil",
    "Cyber Monday",
    "Natal"
  ],
  "commerce_groups": ["PDD", "PNR"],
  "tipificaciones_unicas": 8,
  "source_tables": [
    "meli-bi-data.WHOWNER.BT_CX_CONTACTS",
    "meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE"
  ],
  "version": "1.0"
}
```

---

## 📈 Ejemplos de Uso

### **Caso 1: Reporte Mensual**

```python
# En generar_reporte_cr_universal_v6.2.py
df_corr = pd.read_parquet('metrics/eventos/data/correlacion_mlb_2025_12.parquet')

for tipif in tipificaciones_top:
    corr = df_corr[df_corr['TIPIFICACION'] == tipif]
    
    insight_text += "Correlación con eventos: "
    for _, evento in corr.iterrows():
        if evento['CASOS'] > 0:
            insight_text += f"{evento['EVENTO']}: {evento['CASOS']:,} casos ({evento['PORCENTAJE']:.1f}%); "
```

### **Caso 2: Dashboard Ejecutivo**

```python
# Análisis cross-commerce de Black Friday
df = pd.read_parquet('metrics/eventos/data/correlacion_mlb_2025_11.parquet')
bf = df[df['EVENTO'] == 'Black Friday Brasil']

print("Impacto de Black Friday por Commerce Group:")
for _, row in bf.groupby('COMMERCE_GROUP').agg({'CASOS': 'sum', 'PORCENTAJE': 'mean'}).iterrows():
    print(f"{row.name}: {row['CASOS']:,} casos ({row['PORCENTAJE']:.1f}% promedio)")
```

---

## 🚀 Performance

### **Comparación**

| Métrica | Sin Métricas | Con Métricas |
|---------|--------------|--------------|
| Tiempo cálculo | 2-3 min/reporte | 5 segundos/reporte |
| Precisión | Muestra (100) | Total (todos) |
| Casos analizados | ~400 | ~491,334 |
| Query BigQuery | Cada reporte | 1 vez/mes |
| Costo BigQuery | Alto (repetido) | Bajo (1 vez) |

---

## 📝 Notas Importantes

1. **Fechas de orden**: Usa `ORD_CLOSED_DT` de `DM_CX_POST_PURCHASE`, no `CONTACT_DATE_ID`
2. **Ventana de correlación**: Solo órdenes cerradas en rango del evento (fecha exacta)
3. **NULL handling**: Casos sin `ORD_CLOSED_DT` no se correlacionan (se reportan en metadata)
4. **Actualización**: Regenerar si cambian fechas de eventos o se encuentran errores

---

## 📚 Documentación Completa del Sistema

### **🎯 ¿Eres nuevo? Empieza aquí:**
1. ⭐ **`../GUIA_USUARIO.md`** - Guía práctica paso a paso
2. **Este documento** - Detalles técnicos de métricas de eventos
3. **`ejemplo_uso.py`** - Código de ejemplo

### **🔧 Para mantenimiento:**
4. ⭐ **`CUANDO_REGENERAR.md`** - Cuándo y cómo regenerar métricas
5. **`FUENTE_EVENTOS.md`** - Tabla oficial de eventos comerciales
6. **`generar_correlaciones.py`** - Script generador

### **🚀 Para integración:**
7. **`../INTEGRACION_GOLDEN_TEMPLATES.md`** - Cómo usar en tus scripts
8. **`.cursorrules` Regla 16** - Reglas oficiales
9. **`data/README.md`** - Estructura de archivos de salida

---

**Mantenedor:** CR Analytics Team  
**Última actualización:** Enero 2026  
**Versión:** 2.0
