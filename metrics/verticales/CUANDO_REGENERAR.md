# 🔄 Cuándo Regenerar Métricas de Verticales

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Propósito:** Workflow de decisión para regenerar métricas de verticales/dominios

---

## 🎯 Decisión Rápida

### ✅ **REGENERAR SI:**

1. ✅ **Período cerrado** (fin de mes + 2-3 días para consolidación)
2. ✅ **Cambió la tabla `DM_CX_POST_PURCHASE`** (schema o datos)
3. ✅ **Cambió el mapping de verticales/dominios** en la taxonomía
4. ✅ **Se detectó error en métricas actuales** (validación falló)
5. ✅ **Primera vez para un site/período nuevo**
6. ✅ **Cambió la lógica de filtros de PDD/PNR** en `.cursorrules`

### ❌ **NO REGENERAR SI:**

1. ❌ **Solo cambió un reporte** (seguir usando métricas existentes)
2. ❌ **Período aún activo** (datos inestables, esperá al cierre)
3. ❌ **Solo cambió presentación HTML** (métricas son independientes)
4. ❌ **Cambió análisis de conversaciones** (no afecta verticales)
5. ❌ **Cambió correlación con eventos** (son métricas separadas)

---

## 📋 Workflow de Regeneración

### **PASO 1: Verificar si existe métrica**

```bash
# Listar métricas disponibles
ls metrics/verticales/data/*.parquet

# Verificar período específico
ls metrics/verticales/data/verticales_mla_2025_12.parquet
```

**Resultado:**
- ✅ **Existe** → Evaluar si necesita regenerarse (pasar a PASO 2)
- ❌ **No existe** → Generar por primera vez (ir a PASO 3)

---

### **PASO 2: Evaluar necesidad de regeneración**

#### **2.1. Período cerrado?**

```python
from datetime import datetime, timedelta

# Período considerado "cerrado" si pasaron >3 días desde fin de mes
periodo = "2025-12"
ultimo_dia_mes = datetime(2025, 12, 31)
hoy = datetime.now()

dias_desde_cierre = (hoy - ultimo_dia_mes).days

if dias_desde_cierre >= 3:
    print("✅ Período cerrado, datos consolidados")
else:
    print(f"⚠️ Período activo o recién cerrado (esperá {3 - dias_desde_cierre} días más)")
```

#### **2.2. Validar métricas actuales**

```python
import pandas as pd
import json

# Leer metadata
with open('metrics/verticales/data/metadata_mla_2025_12.json') as f:
    metadata = json.load(f)

# Verificar fecha de generación
fecha_generacion = datetime.fromisoformat(metadata['generated_at'])
dias_antiguedad = (datetime.now() - fecha_generacion).days

print(f"Métrica generada hace {dias_antiguedad} días")

# Verificar completitud
if metadata['pct_sin_vertical'] > 5.0:
    print(f"⚠️ ALERTA: {metadata['pct_sin_vertical']:.1f}% de casos sin vertical (esperado <5%)")
    print("→ Considerar regenerar")

# Verificar total de casos
df = pd.read_parquet('metrics/verticales/data/verticales_mla_2025_12.parquet')
total_casos = df['INCOMING'].sum()

if abs(total_casos - metadata['total_incoming']) > 10:
    print(f"⚠️ ALERTA: Inconsistencia entre metadata y parquet")
    print(f"   Metadata: {metadata['total_incoming']:,} | Parquet: {total_casos:,}")
    print("→ REGENERAR OBLIGATORIO")
```

#### **2.3. Comparar con fuente (BigQuery)**

```sql
-- Query de validación: comparar total con fuente
SELECT 
    COUNT(DISTINCT C.CLA_CLAIM_ID) as total_casos_bigquery
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
WHERE 
    C.SIT_SITE_ID = 'MLA'
    AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-12-01'
    AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
    AND (
        C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' 
        OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'
        OR C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%'
        OR C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale'
    )
```

**Comparar resultado con `metadata['total_incoming']`:**
- Diferencia <1% → ✅ Métrica válida
- Diferencia >1% → ⚠️ Considerar regenerar
- Diferencia >5% → 🚨 REGENERAR OBLIGATORIO

---

### **PASO 3: Ejecutar regeneración**

```bash
# Generar para un site y período
python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12

# Generar para múltiples sites (batch)
python metrics/verticales/generar_agregados.py --sites MLA,MLB,MCO,MLC --periodo 2025-12

# Regenerar rango completo (ej: últimos 3 meses)
python metrics/verticales/generar_agregados.py --site MLA --desde 2025-10 --hasta 2025-12
```

**Tiempo estimado:**
- 1 site × 1 período: 2-3 minutos
- 4 sites × 1 período: 8-12 minutos
- 1 site × 3 períodos: 6-9 minutos

---

### **PASO 4: Validar nueva métrica**

```bash
# 1. Verificar que se crearon los archivos
ls metrics/verticales/data/verticales_mla_2025_12.parquet
ls metrics/verticales/data/metadata_mla_2025_12.json

# 2. Leer metadata y verificar
cat metrics/verticales/data/metadata_mla_2025_12.json
```

**Checks obligatorios:**

```python
import pandas as pd
import json

# Leer archivos
df = pd.read_parquet('metrics/verticales/data/verticales_mla_2025_12.parquet')
with open('metrics/verticales/data/metadata_mla_2025_12.json') as f:
    metadata = json.load(f)

# CHECK 1: Tamaño razonable
assert len(df) > 50, f"Muy pocas filas: {len(df)}"
assert len(df) < 5000, f"Demasiadas filas: {len(df)}"

# CHECK 2: Verticales únicas razonable
assert metadata['verticales_unicas'] > 5, "Muy pocas verticales"
assert metadata['verticales_unicas'] < 50, "Demasiadas verticales"

# CHECK 3: % sin vertical razonable
assert metadata['pct_sin_vertical'] < 10.0, f"Muchos casos sin vertical: {metadata['pct_sin_vertical']:.1f}%"

# CHECK 4: Suma de % = 100% (aprox)
total_pct = df.groupby('COMMERCE_GROUP')['PCT_DEL_TOTAL'].sum()
for cg, pct in total_pct.items():
    assert 99 < pct < 101, f"{cg}: suma de % = {pct:.1f}% (esperado ~100%)"

# CHECK 5: No duplicados
assert not df.duplicated(['SITE', 'PERIODO', 'COMMERCE_GROUP', 'VERTICAL', 'DOMINIO']).any()

print("✅ Todas las validaciones pasaron")
```

---

### **PASO 5: Commitear (opcional)**

```bash
# Commitear metadata (SÍ se versiona)
git add metrics/verticales/data/metadata_mla_2025_12.json
git commit -m "Add: Metadata verticales MLA 2025-12"

# NO commitear parquet (ignorado en .gitignore)
# Los parquets se regeneran según necesidad
```

---

## 🚨 Señales de Alerta

### **Señales que indican necesidad de regenerar:**

| Señal | Severidad | Acción |
|-------|-----------|--------|
| Metadata antiguo (>30 días en período cerrado) | ⚠️ Media | Considerar regenerar |
| % sin vertical >10% | 🚨 Alta | Regenerar + investigar data |
| Diferencia con BigQuery >5% | 🚨 Alta | Regenerar obligatorio |
| Suma de % ≠ 100% (diferencia >2%) | 🚨 Alta | Regenerar obligatorio |
| Filas duplicadas en parquet | 🚨 Alta | Regenerar obligatorio |
| Menos de 5 verticales únicas | 🚨 Alta | Regenerar + investigar data |
| Script generador cambió lógica | 🟡 Baja | Regenerar todos los períodos relevantes |

---

## 📅 Calendario de Regeneración

### **Frecuencia Recomendada:**

| Tipo de Período | Frecuencia | Timing |
|-----------------|------------|--------|
| **Período cerrado (histórico)** | 1 vez (inmutable) | Al cierre + 3 días |
| **Período activo (mes actual)** | No regenerar | Esperar al cierre |
| **Período con error detectado** | Inmediato | Apenas se detecta |
| **Cambio de taxonomía** | 1 vez | Después del cambio |

### **Ejemplo de Workflow Mensual:**

```
Mes de análisis: Diciembre 2025

1. Diciembre 31 → Fin del mes
2. Enero 3 → Datos consolidados
3. Enero 4 → Generar métricas de Diciembre
4. Enero 5 → Validar y commitear metadata
5. Todo Enero → Usar métricas de Diciembre para reportes

NO regenerar en:
- Diciembre 15 (período activo)
- Enero 10 (ya existe y es válido)
- Enero 20 (sin cambios en data)
```

---

## 🔧 Troubleshooting

### **Problema 1: Script falla con timeout**

**Síntoma:** Query de BigQuery supera timeout

**Solución:**
```bash
# Opción 1: Aumentar timeout en script
python metrics/verticales/generar_agregados.py --site MLB --periodo 2025-12 --timeout 600

# Opción 2: Usar sampling para sites grandes (Brasil)
python metrics/verticales/generar_agregados.py --site MLB --periodo 2025-12 --sample 0.3
```

---

### **Problema 2: % sin vertical muy alto**

**Síntoma:** `metadata['pct_sin_vertical'] > 10%`

**Diagnóstico:**
```sql
-- Verificar si hay problema en DM_CX_POST_PURCHASE
SELECT 
    COUNT(*) as total_casos,
    COUNT(PP.VERTICAL) as casos_con_vertical,
    COUNT(*) - COUNT(PP.VERTICAL) as casos_sin_vertical,
    (COUNT(*) - COUNT(PP.VERTICAL)) / COUNT(*) * 100 as pct_sin_vertical
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP 
    ON PP.CLA_CLAIM_ID = C.CLA_CLAIM_ID
WHERE 
    C.SIT_SITE_ID = 'MLA'
    AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) = '2025-12-01'
    AND C.FLAG_EXCLUDE_NUMERATOR_CR = 0
```

**Solución:**
- Si problema es de data → Reportar a equipo de Data
- Si es esperado para el período → Documentar en metadata

---

### **Problema 3: Métricas inconsistentes entre reportes**

**Síntoma:** Dos reportes del mismo período muestran números diferentes

**Causa probable:** Uno usa métricas duras, otro calcula on-the-fly

**Solución:**
1. Verificar ambos reportes usan la misma fuente
2. Regenerar métricas si es necesario
3. Actualizar todos los reportes para usar hard metrics

---

## 📚 Referencias

- **`FUENTE_VERTICALES.md`**: Contexto de negocio de verticales/dominios
- **`README.md`**: Documentación técnica completa
- **`../eventos/CUANDO_REGENERAR.md`**: Workflow similar para eventos (referencia)
- **`.cursorrules` Regla 10**: Reglas oficiales de verticales

---

**Mantenedor:** CR Analytics Team  
**Última actualización:** Enero 2026  
**Versión:** 1.0
