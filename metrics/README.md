# 📊 Métricas Duras - Contact Rate Framework

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Status:** ✅ ACTIVO

---

## 📋 Propósito

Esta carpeta contiene **métricas pre-calculadas** que sirven como fuente de verdad para análisis de Contact Rate. Las métricas son:

- ✅ **Inmutables**: Una vez calculadas para un período cerrado, no cambian
- ✅ **Reutilizables**: Múltiples reportes pueden consumir las mismas métricas
- ✅ **Auditables**: Versionadas y con metadata completa
- ✅ **Performantes**: Pre-cálculo = reportes más rápidos

---

## 📂 Estructura

```
/metrics/
├── README.md                    (este archivo)
├── eventos/                     (correlaciones con eventos comerciales)
│   ├── README.md               (documentación específica)
│   ├── generar_correlaciones.py (script generador)
│   └── data/                   (archivos parquet)
│       ├── correlacion_mlb_2025_11.parquet
│       ├── correlacion_mlb_2025_12.parquet
│       └── metadata.json
├── verticales/                  (métricas de verticales y dominios)
│   ├── README.md               (documentación específica)
│   ├── FUENTE_VERTICALES.md    (contexto de negocio)
│   ├── CUANDO_REGENERAR.md     (workflow de mantenimiento)
│   ├── generar_agregados.py    (script generador)
│   └── data/                   (archivos parquet)
│       ├── verticales_mla_2025_12.parquet
│       ├── metadata_mla_2025_12.json
│       └── README.md
├── demoras/                     (métricas de demoras en Shipping) ⭐ NUEVA
│   ├── README.md               (documentación específica)
│   ├── FUENTE_DEMORAS.md       (tablas y campos de Shipping)
│   ├── CUANDO_REGENERAR.md     (workflow de mantenimiento)
│   ├── INTEGRACION_CR.md       (relación con Contact Rate)
│   ├── sql/
│   │   └── shipping_drivers_optimized_template.sql
│   ├── scripts/
│   │   └── parametrize_shipping_query.py
│   └── data/                   (placeholder para futuros parquets)
├── incoming/                    (métricas agregadas de incoming)
│   └── (futuro)
└── drivers/                     (métricas agregadas de drivers)
    └── (futuro)
```

---

## 🎯 Casos de Uso

### **1. Correlación con Eventos Comerciales**

**Problema que resuelve:**
- Los Golden Templates calculan correlación sobre una **muestra** (100 casos)
- Necesitamos correlación sobre **TODO el incoming** para mayor precisión
- Recalcular esto en cada reporte es ineficiente

**Solución:**
- Pre-calcular correlaciones mensuales: site × período × tipificación × evento
- Obtener eventos dinámicamente desde tabla oficial: **`WHOWNER.LK_MKP_PROMOTIONS_EVENT`**
- Guardar en parquet ligero
- Reportes leen y filtran según necesidad

**⭐ Fuente de Eventos:**
```
meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT
```
Las fechas de eventos se obtienen **dinámicamente** desde esta tabla oficial, garantizando que siempre usamos los rangos correctos (fecha_inicio a fecha_fin) para cada evento comercial.

**Uso en reportes:**
```python
# En lugar de calcular en el reporte:
df_corr = pd.read_parquet('metrics/eventos/data/correlacion_mlb_2025_12.parquet')
corr_tipif = df_corr[df_corr['TIPIFICACION'] == 'REPENTANT_BUYER']
# Ya tienes correlación sobre TODO el incoming con fechas oficiales
```

### **2. Análisis de Verticales y Dominios**

**Problema que resuelve:**
- Necesitamos identificar si incrementos de CR están concentrados en categorías específicas de productos
- Join con `DM_CX_POST_PURCHASE` en cada reporte es lento
- Difícil detectar patrones históricos por vertical

**Solución:**
- Pre-calcular agregados mensuales: site × período × commerce_group × vertical × dominio
- Solo para PDD/PNR (Post-Compra con productos)
- Guardar en parquet con métricas de incoming y % contribución
- Detectar automáticamente variaciones >10%

**⭐ Fuente de Verticales:**
```
meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE
```
Cada orden tiene un producto asociado con su vertical (categoría alto nivel) y dominio (subcategoría).

**Uso en reportes:**
```python
# Leer métricas de dos períodos
df_p1 = pd.read_parquet('metrics/verticales/data/verticales_mla_2025_11.parquet')
df_p2 = pd.read_parquet('metrics/verticales/data/verticales_mla_2025_12.parquet')

# Comparar y detectar anomalías
df_comp = df_p1.merge(df_p2, on=['VERTICAL', 'DOMINIO'], suffixes=('_P1', '_P2'))
df_comp['VAR_PCT'] = (df_comp['INCOMING_P2'] - df_comp['INCOMING_P1']) / df_comp['INCOMING_P1'] * 100

# Filtrar verticales con variación >10%
anomalias = df_comp[abs(df_comp['VAR_PCT']) > 10].sort_values('VAR_PCT', ascending=False)
```

### **3. Análisis de Demoras en Shipping** ⭐ NUEVA

**Problema que resuelve:**
- Picos de CR en ME Distribución pueden estar relacionados con delays en entregas
- Query de demoras (BT_SHP_SHIPMENTS_SUMMARY + SNAPSHOT) es muy pesada (~10-15 min)
- Difícil correlacionar delays con variaciones de incoming sin métricas pre-calculadas

**Solución:**
- Generar queries optimizadas con tablas temporales (40-50% más rápido)
- Parametrización dinámica según site, período, picking type, granularidad
- Métricas de performance (LT/HT delays), composition (custom offsets), network efficiencies

**⭐ Fuentes de Demoras:**
```
meli-bi-data.WHOWNER.BT_SHP_SHIPMENTS_SUMMARY (principal)
meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_METRICS (performance)
meli-bi-data.SHIPPING_BI.BT_SHP_MT_SHIPMENT_SNAPSHOT (composition)
```

**Uso en reportes:**
```python
# Generar query parametrizada
from metrics.demoras.scripts.parametrize_shipping_query import parametrize_shipping_query

query = parametrize_shipping_query(
    site='MLA',
    fecha_inicio='2025-11-01',
    fecha_fin='2026-01-01',
    granularidad='MONTH'
)

# Ejecutar y analizar
# (ejecutar query en BigQuery, obtener CSV)
df_demoras = pd.read_csv('output/demoras_mla_nov_dic.csv')

# Correlacionar con incoming
if df_demoras['SHIPMENTS_LT_DELAY'].mean() > threshold:
    print("⚠️ Aumento de delays detectado - posible causa de pico de CR")
```

**Roadmap:** Pre-cálculo mensual en Parquets (similar a eventos/verticales)

### **4. Métricas Agregadas de Incoming** (Futuro)

Pre-cálculo de incoming por:
- Site × Período × Commerce Group
- Site × Período × Tipificación
- Site × Período × Proceso

### **5. Métricas Agregadas de Drivers** (Futuro)

Pre-cálculo de drivers por:
- Site × Período (órdenes totales)
- Site × Período × Categoría
- Global × Período (para comparaciones cross-site)

---

## ⚙️ Flujo de Trabajo

### **Paso 1: Generar Métricas** (Mensual o Bajo Demanda)

```bash
# Generar correlaciones de eventos para un período
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12

# Output: metrics/eventos/data/correlacion_mlb_2025_12.parquet
```

### **Paso 2: Usar Métricas en Reportes**

```python
# En tu script de reporte (ej: generar_golden_pdd_mlb.py)
import pandas as pd

# Leer métricas pre-calculadas
df_corr = pd.read_parquet('metrics/eventos/data/correlacion_mlb_2025_12.parquet')

# Filtrar por tu dimensión
corr_eventos = df_corr[
    (df_corr['TIPIFICACION'] == tipificacion_actual) &
    (df_corr['PERIODO'] == '2025-12-01')
]

# Usar en reporte
for _, row in corr_eventos.iterrows():
    print(f"{row['EVENTO']}: {row['CASOS']} casos ({row['PORCENTAJE']:.1f}%)")
```

---

## 📊 Formato de Datos

### **Correlaciones de Eventos**

**Archivo:** `eventos/data/correlacion_{site}_{periodo}.parquet`

**Schema:**
```
SITE              str      Site code (MLB, MLA, etc.)
PERIODO           date     Period in YYYY-MM-DD format
COMMERCE_GROUP    str      Commerce Group (PNR, PDD, etc.)
TIPIFICACION      str      Tipificación/Dimension name
EVENTO            str      Event name (Black Friday, etc.)
FECHA_INICIO      date     Event start date
FECHA_FIN         date     Event end date
CASOS             int      # of cases with ORD_CLOSED_DT in event
CASOS_TOTALES     int      Total cases in that dimension/period
PORCENTAJE        float    % of cases correlated (casos/casos_totales * 100)
GENERADO          datetime Timestamp when metric was calculated
```

**Ejemplo:**
| SITE | PERIODO | TIPIFICACION | EVENTO | CASOS | CASOS_TOTALES | PORCENTAJE |
|------|---------|--------------|--------|-------|---------------|------------|
| MLB | 2025-12-01 | REPENTANT_BUYER | Black Friday Brasil | 7,653 | 153,014 | 5.0% |
| MLB | 2025-12-01 | REPENTANT_BUYER | Cyber Monday | 3,060 | 153,014 | 2.0% |

---

## 🔍 Validación de Datos

### **Checks Automáticos**

Cada métrica incluye validación:
- ✅ **Completitud**: Todas las dimensiones esperadas están presentes
- ✅ **Consistencia**: Sumas cuadran con totales
- ✅ **Freshness**: Timestamp de generación incluido
- ✅ **Schema**: Tipos de datos correctos

### **Metadata**

Cada carpeta incluye `metadata.json`:
```json
{
  "generated_at": "2026-01-27T12:30:00",
  "site": "MLB",
  "periodo": "2025-12",
  "rows": 156,
  "source_query": "BT_CX_CONTACTS + DM_CX_POST_PURCHASE",
  "total_incoming": 491334,
  "version": "1.0"
}
```

---

## 🚀 Ventajas

| Aspecto | Sin Métricas | Con Métricas |
|---------|--------------|--------------|
| **Tiempo ejecución** | 8-10 min | 2-3 min |
| **Precisión** | Muestra (100) | Total (todos) |
| **Consistencia** | Variable | Siempre igual |
| **Reutilización** | ❌ | ✅ |
| **Auditabilidad** | Baja | Alta |
| **Análisis histórico** | Difícil | Fácil |

---

## 📖 Documentación Relacionada

- **`/metrics/eventos/README.md`**: Detalles de correlaciones de eventos
- **`/docs/GOLDEN_TEMPLATES.md`**: Cómo usar métricas en Golden Templates
- **`.cursorrules`**: Reglas generales del repositorio

---

## 🔄 Actualización

### **Frecuencia**
- **Período activo**: Diaria (opcional, datos pueden cambiar)
- **Período cerrado**: 1 vez (inmutable)

### **Proceso**
1. Ejecutar script generador al cierre de mes
2. Validar output con checks automáticos
3. Commitear métricas al repositorio
4. Actualizar metadata.json

---

## 📝 Notas Importantes

1. **No hardcodear valores**: Siempre leer de parquet
2. **Validar existencia**: Verificar que el archivo exista antes de leer
3. **Fallback**: Si no existe métrica, calcular on-the-fly (con warning)
4. **Versionado**: Mantener métricas viejas para análisis histórico

---

## 📚 Documentación Completa del Sistema

### **🗺️ ¿Perdido? Usa el mapa:**
0. ⭐ **`INDICE.md`** - **MAPA DE NAVEGACIÓN** - Encuentra exactamente lo que necesitas

### **🎯 Para Usuarios Nuevos - Empieza aquí:**
1. **`GUIA_USUARIO.md`** ⭐ **GUÍA PRÁCTICA** - Paso a paso para usar el sistema
2. **`eventos/README.md`** - Cómo funcionan las métricas de eventos
3. **`eventos/ejemplo_uso.py`** - Ejemplos de código práctico

### **🔧 Para Mantenimiento y Operación:**
4. **`eventos/CUANDO_REGENERAR.md`** ⭐ **CRÍTICO** - Cuándo regenerar métricas
5. **`eventos/FUENTE_EVENTOS.md`** - Tabla oficial de eventos (LK_MKP_PROMOTIONS_EVENT)
6. **`eventos/generar_correlaciones.py`** - Script generador con documentación inline

### **🚀 Para Integración en Reportes:**
7. **`INTEGRACION_GOLDEN_TEMPLATES.md`** - Cómo integrar hard metrics en tus scripts
8. **`.cursorrules` - Regla 16** - Reglas oficiales del sistema

### **📊 Para Análisis y Presentación:**
9. ⭐ **`COMPARATIVA.md`** - Antes vs Después (muestra valor del sistema)
10. **`eventos/data/metadata_*.json`** - Metadata de cada métrica generada
11. **`eventos/data/README.md`** - Qué contiene la carpeta de datos

---

## 🎓 Roadmap de Aprendizaje Recomendado

**Nivel 1 - Usuario Básico (30 min):**
1. Lee `GUIA_USUARIO.md` secciones 1-3
2. Ejecuta: `ls metrics/eventos/data/*.parquet`
3. Genera tu primer reporte con hard metrics

**Nivel 2 - Usuario Intermedio (1 hora):**
1. Lee `eventos/README.md` completo
2. Aprende a leer y filtrar parquets
3. Ejecuta `eventos/ejemplo_uso.py`

**Nivel 3 - Generador de Métricas (2 horas):**
1. Lee `eventos/CUANDO_REGENERAR.md`
2. Genera métricas para un site/período
3. Valida con queries de comprobación

**Nivel 4 - Integrador (3 horas):**
1. Lee `INTEGRACION_GOLDEN_TEMPLATES.md`
2. Integra hard metrics en un script existente
3. Implementa fallback mechanism

---

**Mantenedor:** CR Analytics Team  
**Última actualización:** Enero 2026  
**Versión:** 2.0
