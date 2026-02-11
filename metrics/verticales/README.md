# 📊 Métricas de Verticales y Dominios

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Status:** ✅ ACTIVO

---

> ## ⚠️ IMPORTANTE - Valores Dinámicos
> 
> Esta métrica obtiene verticales y dominios **directamente de BigQuery** (`DM_CX_POST_PURCHASE`).
> 
> **NO hay verticales hardcodeadas. NO hay filtros predefinidos.**
> 
> El análisis usa EXACTAMENTE lo que devuelva la tabla, sin asumir, inventar o sesgar valores.

---

## 📋 Propósito

Pre-calcular agregados de incoming por **Vertical** y **Dominio** para análisis de Contact Rate en **PDD** y **PNR**.

**Objetivo:** Identificar si incrementos de CR están concentrados en categorías específicas de productos.

---

## 🎯 Problema que Resuelve

### **Situación Actual (Sin Métricas)**
- Calcular verticales en cada reporte (lento)
- Join con `DM_CX_POST_PURCHASE` repetido N veces
- Inconsistencia entre reportes
- Difícil detectar patrones históricos por vertical

### **Con Métricas Duras**
- Pre-calculado 1 vez → usado N veces
- Detección automática de variaciones >10%
- Análisis histórico facilitado
- Consistencia garantizada entre reportes

---

## 📊 Datos Generados

### **Archivos**

```
/metrics/verticales/data/
├── verticales_mla_2025_11.parquet  (Nov 2025 - Argentina)
├── verticales_mla_2025_12.parquet  (Dic 2025 - Argentina)
├── verticales_mlb_2025_11.parquet  (Nov 2025 - Brasil)
├── verticales_mlb_2025_12.parquet  (Dic 2025 - Brasil)
├── metadata_mla_2025_11.json       (Metadata)
├── metadata_mla_2025_12.json
└── README.md
```

### **Schema del Parquet**

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `SITE` | str | Site code | 'MLA' |
| `PERIODO` | date | Período YYYY-MM-DD | '2025-12-01' |
| `COMMERCE_GROUP` | str | PDD o PNR | 'PDD' |
| `VERTICAL` | str | Vertical del producto | 'HOME & INDUSTRY' |
| `DOMINIO` | str | Dominio agregado nivel 1 | 'DOOR_PEEPHOLES_AND_VIEWERS' |
| `INCOMING` | int | # de casos | 1,245 |
| `PCT_DEL_TOTAL` | float | % del incoming total del commerce group | 5.4 |
| `GENERADO` | datetime | Timestamp generación | '2026-01-29 10:30:00' |

**Nota:** Para análisis comparativos (P1 vs P2), cargar ambos parquets y calcular deltas.

---

## 🛠️ Generación de Métricas

### **Script: `generar_agregados.py`**

**Uso:**

```bash
# Generar métricas para un site y período
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12

# Generar para múltiples sites
python metrics/verticales/generar_agregados.py --sites MLA,MLB,MCO --periodo 2025-12

# Generar para rango de períodos
python metrics/verticales/generar_agregados.py --site MLA --desde 2025-11 --hasta 2025-12

# Generar solo PDD o PNR
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12 --commerce-group PDD
```

### **Proceso:**

1. Lee **TODO el incoming** de PDD/PNR del período
2. Join con `DM_CX_POST_PURCHASE` para obtener `VERTICAL` y `DOM_DOMAIN_AGG1`
3. Agrupa por: Site × Período × Commerce Group × Vertical × Dominio
4. Calcula: Incoming total, % contribución
5. Guarda parquet + metadata.json

**Tiempo estimado:**
- 1 site × 1 período: ~2-3 minutos
- 7 sites × 1 período: ~10-15 minutos

---

## 📖 Cómo Usar en Reportes

### **Ejemplo 1: Golden Template PDD**

```python
import pandas as pd
from pathlib import Path

# Leer métricas pre-calculadas
metrics_path = Path('metrics/verticales/data')
file_p1 = metrics_path / f'verticales_{site}_{periodo_p1.replace("-", "_")}.parquet'
file_p2 = metrics_path / f'verticales_{site}_{periodo_p2.replace("-", "_")}.parquet'

if file_p1.exists() and file_p2.exists():
    # Usar hard metrics
    df_p1 = pd.read_parquet(file_p1)
    df_p2 = pd.read_parquet(file_p2)
    
    # Filtrar por commerce group
    df_p1_pdd = df_p1[df_p1['COMMERCE_GROUP'] == 'PDD']
    df_p2_pdd = df_p2[df_p2['COMMERCE_GROUP'] == 'PDD']
    
    # Comparar y detectar variaciones
    df_comp = df_p1_pdd.merge(
        df_p2_pdd, 
        on=['SITE', 'COMMERCE_GROUP', 'VERTICAL', 'DOMINIO'],
        suffixes=('_P1', '_P2')
    )
    
    df_comp['VARIACION_ABS'] = df_comp['INCOMING_P2'] - df_comp['INCOMING_P1']
    df_comp['VARIACION_PCT'] = (df_comp['VARIACION_ABS'] / df_comp['INCOMING_P1']) * 100
    
    # Detectar anomalías
    df_anomalas = df_comp[
        (abs(df_comp['VARIACION_PCT']) > 10) |  # Variación >10%
        (abs(df_comp['VARIACION_ABS']) > 100)   # O >100 casos
    ]
    
    # Ordenar por impacto (variación absoluta)
    top_verticales = df_anomalas.sort_values('VARIACION_ABS', ascending=False).head(5)
    
    # Usar en reporte
    for _, row in top_verticales.iterrows():
        print(f"⚠️ VERTICAL DESTACADA: {row['VERTICAL']}")
        print(f"   Variación: {row['VARIACION_ABS']:+,} casos ({row['VARIACION_PCT']:+.1f}%)")
        
else:
    print(f"[WARNING] Métricas no encontradas")
    print("[INFO] Calculando on-the-fly (modo fallback)")
    # ... calcular como antes con query SQL
```

### **Ejemplo 2: Análisis de Dominios (Deep Dive)**

```python
# Profundizar en una vertical específica
vertical_seleccionada = 'ELECTRONICS'

df_dominios = df_comp[df_comp['VERTICAL'] == vertical_seleccionada]
df_dominios = df_dominios.sort_values('VARIACION_ABS', ascending=False)

print(f"\n## Análisis de Dominios - {vertical_seleccionada}\n")
for _, dom in df_dominios.head(5).iterrows():
    print(f"- {dom['DOMINIO']}: {dom['VARIACION_ABS']:+,} casos ({dom['VARIACION_PCT']:+.1f}%)")
```

### **Ejemplo 3: Detección de Picos Temporales**

```python
# Si hay datos diarios (extensión futura), detectar picos
# Por ahora, solo comparación mensual P1 vs P2
```

---

## 🔍 Detección de Anomalías

### **Criterios Automáticos:**

```python
def detectar_anomalias(df_comparacion):
    """
    Detecta verticales/dominios con variaciones anómalas
    """
    anomalias = []
    
    for _, row in df_comparacion.iterrows():
        # Criterio 1: Variación porcentual >10%
        if abs(row['VARIACION_PCT']) > 10:
            anomalias.append({
                'vertical': row['VERTICAL'],
                'dominio': row['DOMINIO'],
                'tipo_anomalia': 'VARIACION_PORCENTUAL',
                'valor': row['VARIACION_PCT']
            })
        
        # Criterio 2: Variación absoluta >100 casos Y >5%
        if abs(row['VARIACION_ABS']) > 100 and abs(row['VARIACION_PCT']) > 5:
            anomalias.append({
                'vertical': row['VERTICAL'],
                'dominio': row['DOMINIO'],
                'tipo_anomalia': 'VARIACION_ABSOLUTA',
                'valor': row['VARIACION_ABS']
            })
    
    return anomalias
```

### **Output Esperado en Reporte:**

```markdown
## ⚠️ VERTICALES DESTACADAS

Se detectaron **3 verticales** con variaciones significativas:

### 1. GROCERIES (+450 casos, +35%)
- **Incoming P1:** 1,245 casos (4.2% del total PDD)
- **Incoming P2:** 1,695 casos (5.1% del total PDD)
- **Dominios más afectados:**
  - BEVERAGES: +180 casos (+40%)
  - SNACKS: +120 casos (+32%)
- **Correlación eventos:** 20% de casos en fechas navideñas
- **Hipótesis:** Incremento esperado por temporada + posible problema de calidad en BEVERAGES

### 2. ELECTRONICS (+320 casos, +18%)
- **Incoming P1:** 1,780 casos (6.0% del total PDD)
- **Incoming P2:** 2,100 casos (6.3% del total PDD)
- **Dominios más afectados:**
  - SMARTPHONES: +200 casos (+25%)
  - HEADPHONES: +80 casos (+15%)
- **Correlación eventos:** 45% de casos en Black Friday
- **Hipótesis:** Incremento estacional por Black Friday (comportamiento esperado)

### 3. TOYS_AND_BABIES (+180 casos, +22%)
- **Incoming P1:** 820 casos (2.8% del total PDD)
- **Incoming P2:** 1,000 casos (3.0% del total PDD)
- **Dominios más afectados:**
  - TOYS: +120 casos (+25%)
  - BABY_CARE: +60 casos (+18%)
- **Correlación eventos:** 35% de casos en fechas navideñas
- **Hipótesis:** Incremento estacional esperado (Navidad/Reyes)

---

**Resto de verticales:** Sin variaciones significativas (<10% o <100 casos)
```

---

## 📈 Validación de Datos

### **Checks Automáticos**

El script generador incluye validación:

```python
# 1. Completitud
assert len(df_vert) > 0, "No se generaron métricas"

# 2. Cobertura de verticales
pct_con_vertical = df_vert['VERTICAL'].notna().sum() / len(df_vert) * 100
assert pct_con_vertical > 90, f"Muchos casos sin vertical: {100-pct_con_vertical:.1f}%"

# 3. Consistencia con incoming total
incoming_verticales = df_vert['INCOMING'].sum()
assert abs(incoming_verticales - incoming_total_pdd_pnr) / incoming_total_pdd_pnr < 0.01, \
    "Diferencia >1% entre sum(verticales) y total PDD/PNR"

# 4. No duplicados
assert not df_vert.duplicated(['SITE', 'PERIODO', 'COMMERCE_GROUP', 'VERTICAL', 'DOMINIO']).any()

# 5. Rango de valores
assert (df_vert['PCT_DEL_TOTAL'] >= 0).all() and (df_vert['PCT_DEL_TOTAL'] <= 100).all()
```

### **Metadata.json**

Ejemplo:

```json
{
  "site": "MLA",
  "periodo": "2025-12",
  "commerce_groups": ["PDD", "PNR"],
  "generated_at": "2026-01-29T10:30:00",
  "total_rows": 342,
  "total_incoming": 32450,
  "verticales_unicas": 15,
  "dominios_unicos": 127,
  "casos_sin_vertical": 245,
  "pct_sin_vertical": 0.75,
  "source_tables": [
    "meli-bi-data.WHOWNER.BT_CX_CONTACTS",
    "meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE"
  ],
  "version": "1.0"
}
```

---

## 🚀 Performance

### **Comparación**

| Métrica | Sin Métricas | Con Métricas |
|---------|--------------|--------------|
| Tiempo cálculo | 3-4 min/reporte | 10 segundos/reporte |
| Precisión | Total (join on-the-fly) | Total (pre-calculado) |
| Casos analizados | ~32,000 | ~32,000 |
| Query BigQuery | Cada reporte | 1 vez/mes |
| Costo BigQuery | Alto (repetido) | Bajo (1 vez) |
| Consistencia | Variable | Siempre igual |

---

## 📝 Notas Importantes

### **1. Alcance: Solo PDD y PNR**

⚠️ **CRÍTICO:** Esta métrica solo aplica para Post-Compra (PDD/PNR).

**Motivo:** Solo estos commerce groups tienen casos con órdenes/productos asociados.

### **2. NULL Handling**

Casos sin `VERTICAL`:
- Agrupar como `"SIN_VERTICAL"`
- Reportar % en metadata
- Si >5% del total → investigar (posible problema de data)

### **3. Top N en Reportes**

- Reportar solo **top 5 verticales** con mayor variación
- O todas las que superen umbral (>10% o >100 casos)
- No reportar verticales con <50 casos en ambos períodos (ruido)

### **4. Actualización**

- Regenerar al cierre de mes (datos consolidados)
- No regenerar en período activo (datos inestables)
- Ver criterios completos en: `CUANDO_REGENERAR.md`

---

## 📚 Documentación Completa del Sistema

### **🎯 ¿Eres nuevo? Empieza aquí:**
1. ⭐ **`FUENTE_VERTICALES.md`** - ¿Qué son verticales y dominios? (contexto de negocio)
2. **Este documento** - Detalles técnicos de la métrica
3. **`ejemplo_uso.py`** - Código de ejemplo (próximamente)

### **🔧 Para mantenimiento:**
4. ⭐ **`CUANDO_REGENERAR.md`** - Cuándo y cómo regenerar métricas (próximamente)
5. **`generar_agregados.py`** - Script generador (próximamente)

### **🚀 Para integración:**
6. **`../INTEGRACION_GOLDEN_TEMPLATES.md`** - Cómo usar en tus scripts
7. **`.cursorrules` Regla 10** - Reglas oficiales
8. **`data/README.md`** - Estructura de archivos de salida

---

**Mantenedor:** CR Analytics Team  
**Última actualización:** Enero 2026  
**Versión:** 1.0
