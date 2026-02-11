# 👤 Guía de Usuario - Sistema de Hard Metrics

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Audiencia:** Analistas de CR, usuarios del repositorio

---

## 🎯 ¿Qué son las Hard Metrics?

Las **Hard Metrics** son **métricas precalculadas** que se generan una vez y se reutilizan en múltiples reportes. 

**Analogía:** Es como tener un "resumen financiero" mensual ya calculado, en lugar de recalcular todas las transacciones cada vez que necesitas un dato.

---

## ❓ ¿Por qué usar Hard Metrics?

### **Problema que resuelven:**

**Antes (sin hard metrics):**
```
Usuario solicita: "Reporte PDD MLA Dic 2025"
→ Script calcula correlación con eventos sobre 100 casos (muestra)
→ Resultado: ~2% de error, no muy preciso
→ Tiempo: 5-8 minutos por reporte
```

**Ahora (con hard metrics):**
```
Usuario solicita: "Reporte PDD MLA Dic 2025"
→ Script LEE correlación de parquet precalculado (TODO el incoming)
→ Resultado: 100% preciso
→ Tiempo: 30 segundos (16x más rápido)
```

### **Beneficios concretos:**

| Beneficio | Detalle |
|-----------|---------|
| ✅ **Precisión** | Analiza TODO el incoming, no solo muestra |
| ✅ **Performance** | Reportes 10-15x más rápidos |
| ✅ **Reutilización** | Una métrica sirve para múltiples reportes |
| ✅ **Consistencia** | Todos los reportes usan los mismos datos |
| ✅ **Trazabilidad** | Metadata documenta origen y versión |

---

## 🚀 Cómo Usar el Sistema (Paso a Paso)

### **Caso 1: Generar un Reporte con Métricas Existentes**

**Escenario:** Quieres generar reporte PDD MLA Nov-Dic 2025

**Paso 1:** Verifica si las métricas ya existen
```bash
ls metrics/eventos/data/correlacion_mla_2025_*.parquet
```

**Resultado esperado:**
```
correlacion_mla_2025_11.parquet
correlacion_mla_2025_12.parquet
```

**Paso 2:** Ejecuta el Template Universal
```bash
python generar_reporte_cr_universal_v6.2.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

**Resultado:**
- ✅ El script carga automáticamente las métricas
- ✅ Muestra correlaciones precisas en el reporte
- ✅ Indica en footer: "Hard metrics: ACTIVAS"

---

### **Caso 2: Generar Métricas para un Período Nuevo**

**Escenario:** Es enero 2026 y quieres analizar Diciembre 2025 por primera vez

**Paso 1:** Genera las métricas para el período
```bash
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
```

**Duración:** ~1-2 minutos (consulta TODO el incoming)

**Paso 2:** Verifica que se crearon los archivos
```bash
ls metrics/eventos/data/correlacion_mla_2025_12.*
```

**Deberías ver:**
```
correlacion_mla_2025_12.parquet  (datos)
metadata_mla_2025_12.json        (información)
```

**Paso 3:** Genera el reporte
```bash
python generar_reporte_cr_universal_v6.2.py \
    --site MLA \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report
```

---

### **Caso 3: Generar Métricas para Múltiples Sites**

**Escenario:** Quieres generar un reporte Cross-Site y necesitas métricas de todos los sites

**Comando:**
```bash
python metrics/eventos/generar_correlaciones.py \
    --sites MLA,MLB,MLC,MCO,MEC,MLM,MLU,MPE \
    --periodo 2025-12
```

**Duración:** ~10-15 minutos (procesa 8 sites)

**Validación:**
```bash
ls metrics/eventos/data/correlacion_*_2025_12.parquet | wc -l
# Debería mostrar: 8 (uno por site)
```

---

## 📊 Cómo Interpretar las Métricas

### **Leer un archivo Parquet:**

```python
import pandas as pd

# Cargar métricas
df = pd.read_parquet('metrics/eventos/data/correlacion_mla_2025_12.parquet')

# Ver estructura
print(df.head())
```

**Output esperado:**
```
   SITE  PERIODO  COMMERCE_GROUP     TIPIFICACION              EVENTO    CASOS  CASOS_TOTALES  PORCENTAJE
0   MLA  2025-12             PDD  REPENTANT_BUYER  Black Friday MLA     7653         153014        5.0
1   MLA  2025-12             PDD  DEFECTIVE_ITEM  Black Friday MLA     2341          45123        5.2
...
```

**Interpretación:**
- **CASOS:** 7,653 casos de arrepentimiento correlacionan con Black Friday
- **CASOS_TOTALES:** 153,014 casos de arrepentimiento en total en Dic 2025
- **PORCENTAJE:** 5.0% del incoming de arrepentimiento viene de Black Friday

---

### **Leer Metadata:**

```python
import json

with open('metrics/eventos/data/metadata_mla_2025_12.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(json.dumps(metadata, indent=2, ensure_ascii=False))
```

**Información clave en metadata:**
```json
{
  "site": "MLA",
  "periodo": "2025-12",
  "generated_at": "2026-01-27T12:05:55",
  "total_incoming": 140954,
  "porcentaje_correlacionado_global": 13.5,
  "eventos_incluidos": ["Black Friday", "Cyber Monday", "Navidad"],
  "eventos_detalle": [
    {
      "nombre": "Black Friday",
      "fecha_inicio": "2025-11-25",
      "fecha_fin": "2025-12-03",
      "duracion_dias": 9
    }
  ],
  "source_tables": [
    "BT_CX_CONTACTS",
    "DM_CX_POST_PURCHASE",
    "LK_MKP_PROMOTIONS_EVENT"
  ],
  "eventos_source": "WHOWNER.LK_MKP_PROMOTIONS_EVENT",
  "eventos_dinamicos": true,
  "version": "2.0"
}
```

---

## 🔍 Casos de Uso Comunes

### **1. Validar si un evento tuvo impacto**

```python
import pandas as pd

df = pd.read_parquet('metrics/eventos/data/correlacion_mla_2025_12.parquet')

# Filtrar por evento específico
black_friday = df[df['EVENTO'].str.contains('Black Friday', case=False)]

print(f"Total casos correlacionados con Black Friday: {black_friday['CASOS'].sum():,}")
print(f"Commerce groups afectados: {black_friday['COMMERCE_GROUP'].unique()}")
print(f"\nTop 3 tipificaciones:")
print(black_friday.nlargest(3, 'CASOS')[['TIPIFICACION', 'CASOS', 'PORCENTAJE']])
```

---

### **2. Comparar impacto entre eventos**

```python
eventos_impacto = df.groupby('EVENTO').agg({
    'CASOS': 'sum',
    'PORCENTAJE': 'mean'
}).sort_values('CASOS', ascending=False)

print("Impacto por evento (ordenado por casos):")
print(eventos_impacto)
```

---

### **3. Analizar correlación por tipificación**

```python
# ¿Qué eventos afectan más a REPENTANT_BUYER?
arrepentimiento = df[df['TIPIFICACION'] == 'REPENTANT_BUYER']

print(arrepentimiento[['EVENTO', 'CASOS', 'PORCENTAJE']].sort_values('CASOS', ascending=False))
```

---

## ⚠️ Troubleshooting

### **Problema: "No se encontraron métricas"**

**Error:**
```
[WARNING] No se pudieron cargar métricas: [Errno 2] No such file or directory
```

**Solución:**
```bash
# Genera las métricas para ese período
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
```

---

### **Problema: "Métricas desactualizadas"**

**Síntoma:** Los eventos en el reporte no coinciden con el calendario

**Verificación:**
```python
import json
with open('metrics/eventos/data/metadata_mla_2025_12.json') as f:
    meta = json.load(f)
    print(f"Generado: {meta['generated_at']}")
    print(f"Versión: {meta['version']}")
    print(f"Eventos dinámicos: {meta.get('eventos_dinamicos', False)}")
```

**Solución:**
- Si `version` < `2.0` o `eventos_dinamicos` = `false` → REGENERAR
```bash
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
```

---

### **Problema: "Diferencias con query manual"**

**Síntoma:** Los números en hard metrics no coinciden con tu query

**Checklist de validación:**
1. ¿Usas el mismo período? (verifica `metadata['periodo']`)
2. ¿Usas los mismos filtros? (verifica `metadata['source_tables']`)
3. ¿La tabla de eventos cambió recientemente?
4. ¿Regeneraste las métricas después del cambio?

**Solución:**
```bash
# Regenerar métricas con datos más recientes
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12

# Comparar totales
python -c "
import pandas as pd
df = pd.read_parquet('metrics/eventos/data/correlacion_mla_2025_12.parquet')
print(f'Total incoming en métricas: {df[\"CASOS_TOTALES\"].max():,}')
"
```

---

## 📚 Recursos Adicionales

### **Documentación completa:**
- **README principal:** `metrics/README.md`
- **Eventos:** `metrics/eventos/README.md`
- **Fuente de eventos:** `metrics/eventos/FUENTE_EVENTOS.md`
- **Regeneración:** `metrics/eventos/CUANDO_REGENERAR.md` ⭐
- **Integración:** `metrics/INTEGRACION_GOLDEN_TEMPLATES.md`

### **Ejemplos prácticos:**
- **Ejemplo de uso:** `metrics/eventos/ejemplo_uso.py`
- **Template Universal con hard metrics:** `generar_reporte_cr_universal_v6.2.py`

### **Reglas del repositorio:**
- **Regla 16:** Hard Metrics System (en `.cursorrules`)

---

## 💡 Tips y Best Practices

### **1. Genera métricas al inicio del mes**
```bash
# Primera semana de cada mes, genera métricas del mes anterior
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
```

### **2. Mantén un set de métricas "rolling"**
```bash
# Mantén siempre los últimos 3 meses disponibles
# Ejemplo en Enero 2026: Nov 2025, Dic 2025, Ene 2026
```

### **3. Usa el metadata para validación rápida**
```bash
# Verifica rápidamente qué métricas tienes
cat metrics/eventos/data/metadata_*.json | grep '"site"' | grep '"periodo"'
```

### **4. Automatiza la regeneración (avanzado)**
```bash
# Crear script que regenere automáticamente al detectar cambios
# (futuro: integración con airflow/cron)
```

---

## 🎓 Preguntas Frecuentes

### **¿Cuánto espacio ocupan las métricas?**
- Típicamente 500KB - 2MB por archivo parquet
- Metadata JSON: ~5-10KB
- Total por site/período: ~1-2MB

### **¿Puedo borrar métricas antiguas?**
- ✅ Sí, si ya no las necesitas
- ⚠️ Recomendado: mantener al menos últimos 3 meses
- 📁 Considerar archivar en lugar de borrar

### **¿Las métricas funcionan offline?**
- ✅ Sí, una vez generadas
- ❌ Para generarlas necesitas conexión a BigQuery

### **¿Qué pasa si genero un reporte sin métricas?**
- El script usa **fallback automático**
- Calcula correlación sobre muestra (100 casos)
- Menos preciso pero funcional
- Footer indica: "Hard metrics: NO DISPONIBLES"

### **¿Puedo usar métricas de un site para otro?**
- ❌ NO - cada site tiene sus propios eventos
- Ejemplo: Black Friday Brasil ≠ Black Friday Argentina

---

## 📞 Soporte y Ayuda

**¿Necesitas ayuda?**

1. **Consulta primero:**
   - `metrics/README.md` (overview general)
   - Este documento (guía práctica)
   - `metrics/eventos/CUANDO_REGENERAR.md` (mantenimiento)

2. **Revisa ejemplos:**
   - `metrics/eventos/ejemplo_uso.py`
   - Scripts Golden Templates existentes

3. **Contacta al equipo:**
   - CR Analytics Team
   - Mantenedor del repositorio

---

## 🔗 Enlaces Rápidos

| Necesitas | Ve a |
|-----------|------|
| Generar métricas nuevas | `metrics/eventos/generar_correlaciones.py` |
| Ver métricas existentes | `metrics/eventos/data/` |
| Integrar en tu script | `metrics/INTEGRACION_GOLDEN_TEMPLATES.md` |
| Entender eventos | `metrics/eventos/FUENTE_EVENTOS.md` |
| Saber cuándo regenerar | `metrics/eventos/CUANDO_REGENERAR.md` |
| Ejemplos de código | `metrics/eventos/ejemplo_uso.py` |

---

## 🎯 Flujo de Trabajo Recomendado

### **Para Analistas (uso diario):**

```
1. ¿Necesitas un reporte de un período?
   └─> Verifica si existen métricas (ls metrics/eventos/data/)
       ├─> SÍ existen → Genera reporte directamente
       └─> NO existen → Genera métricas primero, luego reporte

2. ¿El reporte menciona "Hard metrics: NO DISPONIBLES"?
   └─> Genera las métricas y regenera el reporte para mayor precisión

3. ¿Cambió el calendario de eventos?
   └─> Consulta CUANDO_REGENERAR.md
```

### **Para Mantenedores (mensual):**

```
1. Inicio de mes:
   └─> Generar métricas del mes anterior para todos los sites

2. Mid-mes:
   └─> Validar que eventos en LK_MKP_PROMOTIONS_EVENT están correctos

3. Fin de mes:
   └─> Preparar métricas del mes actual (si datos completos)
```

---

## 📝 Ejemplo Completo End-to-End

**Objetivo:** Generar reporte PDD MLB Dic 2025 con hard metrics

```bash
# Paso 1: Generar métricas (si no existen)
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12

# Output esperado:
# [EVENTOS] [OK] 3 eventos encontrados desde tabla oficial
# [EVENTOS]   - Black Friday Brasil: 2025-11-28 a 2025-11-30
# [EVENTOS]   - Cyber Monday: 2025-12-01 a 2025-12-05
# [EVENTOS]   - Natal: 2025-12-20 a 2025-12-25
# [MLB] [OK] 153,014 casos obtenidos
# [MLB] [OK] 45 correlaciones calculadas
# [OK] METRICAS GENERADAS EXITOSAMENTE

# Paso 2: Verificar métricas generadas
ls metrics/eventos/data/correlacion_mlb_2025_12.*

# Paso 3: Generar reporte
python generar_reporte_cr_universal_v6.2.py \
    --site MLB \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group PDD \
    --aperturas TIPIFICACION \
    --open-report

# Output esperado:
# [OK] Métricas cargadas: Dic=45 registros
# [INSIGHT] REPENTANT_BUYER: correlación eventos desde hard metrics
# [OK] Reporte generado: output/rca/post-compra/pdd/...
# Hard metrics: ACTIVAS

# Paso 4: Validar correlaciones en el reporte HTML
# Busca secciones como:
# "Correlación con eventos comerciales (desde métricas oficiales): 
#  Black Friday Brasil: 7,653 casos (5.0% del total)"
```

---

## 🎉 ¡Listo para Empezar!

**Tu primer tarea práctica:**

1. Lista las métricas disponibles:
   ```bash
   ls -lh metrics/eventos/data/*.parquet
   ```

2. Lee un metadata para entender la estructura:
   ```bash
   cat metrics/eventos/data/metadata_mla_2025_12.json
   ```

3. Genera tu primer reporte usando hard metrics:
   ```bash
   python generar_reporte_cr_universal_v6.2.py \
       --site MLA \
       --p1-start 2025-11-01 --p1-end 2025-11-30 \
       --p2-start 2025-12-01 --p2-end 2025-12-31 \
       --commerce-group PDD \
       --aperturas TIPIFICACION \
       --open-report
   ```

4. Observa la diferencia en el footer:
   - Con métricas: "Hard metrics: ACTIVAS"
   - Sin métricas: "Hard metrics: NO DISPONIBLES"

---

**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Feedback:** Bienvenido para mejorar esta guía
