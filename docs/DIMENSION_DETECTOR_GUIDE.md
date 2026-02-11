# 🔍 Sistema de Detección Automática de Dimensiones v5.0

## Propósito

Permitir que el agente identifique automáticamente **en qué dimensión se encuentra un valor** sin necesidad de que el usuario lo especifique, mejorando la experiencia y reduciendo preguntas innecesarias.

---

## Problema que resuelve

### Antes (v4.x):

```
Usuario: "mlb pre compra nov dic"
Agente: "¿A qué commerce group pertenece Pre Compra?"
Usuario: "No sé, buscalo vos"
Agente: "Ejecutando query..." (2 minutos)
Agente: "Pre Compra pertenece a Generales Compra. ¿Confirmo?"
```

**Resultado:** 3-4 interacciones, usuario frustrado.

### Después (v5.0):

```
Usuario: "mlb pre compra nov dic"
Agente: [ejecuta lookup silenciosamente - 0.1 segundos]
Agente: "Voy a analizar:
- Proceso: Pre Compra (pertenece a Generales Compra)
- Site: MLB
- Período: Nov vs Dic 2025
- Aperturas: CDU, TIPIFICACION (recomendadas)
¿Es correcto y avanzo?"
```

**Resultado:** 1 interacción, usuario satisfecho.

---

## Arquitectura

### 1. Mapeo de dimensiones (`config/dimensions-mapping.json`)

Archivo JSON con todos los valores de todas las dimensiones y sus commerce groups relacionados.

**Estructura:**
```json
{
  "metadata": {
    "last_updated": "2026-02-01T12:00:00",
    "source": "BT_CX_CONTACTS - últimos 3 meses",
    "dimensions_available": ["PROCESO", "CDU", "TIPIFICACION", "ENVIRONMENT"],
    "total_values": 568
  },
  "mappings": {
    "PROCESO": {
      "Pre Compra": {
        "commerce_groups": ["Generales Compra"],
        "avg_monthly_cases": 24271,
        "total_cases_3m": 72813
      },
      "Arrepentimiento - XD": {
        "commerce_groups": ["PDD", "PNR"],
        "avg_monthly_cases": 92707,
        "total_cases_3m": 278121
      }
    },
    "ENVIRONMENT": {
      "XD": {
        "commerce_groups": ["PDD", "PNR"],
        "avg_monthly_cases": 333997,
        "total_cases_3m": 1001991
      }
    }
    // ... etc
  }
}
```

**Actualización:**
- Ejecutar mensualmente: `python scripts/actualizar_mapeo_dimensiones.py`
- O cuando hay cambios en taxonomía de Commerce

---

### 2. Detector (`utils/dimension_detector.py`)

Clase Python que hace lookup en el mapeo.

**Métodos principales:**

```python
detector = DimensionDetector()

# Buscar un valor en todas las dimensiones
result = detector.detect_and_lookup("Pre Compra")
# Returns: {'found': True, 'dimension': 'PROCESO', 'commerce_groups': ['Generales Compra'], ...}

# Listar todos los valores de una dimensión
valores = detector.list_all_values_by_dimension("PROCESO")

# Buscar valores por commerce group
valores_pdd = detector.search_by_commerce_group("PDD")
# Returns: {'PROCESO': ['Arrepentimiento - XD', ...], 'CDU': [...], ...}
```

**Features:**
- ✅ Exact match (case sensitive)
- ✅ Case-insensitive match
- ✅ Fuzzy matching (sugerencias si no encuentra)
- ✅ Cache interno (performance)
- ✅ Soporte para múltiples commerce groups por valor

---

### 3. Integración en `.cursorrules`

**Protocolo obligatorio (línea 254-296):**

```markdown
### 🔍 PASO 0: DETECCIÓN AUTOMÁTICA DE DIMENSIONES (v5.0 - CRÍTICO)

ANTES de preguntar CUALQUIER COSA al usuario, SIEMPRE ejecutar:

from utils.dimension_detector import DimensionDetector
detector = DimensionDetector()
result = detector.detect_and_lookup(valor_mencionado)

if result['found']:
    # CONFIRMAR con usuario, NO preguntar
else:
    # Mostrar sugerencias
```

---

## Dimensiones soportadas

| Dimensión | Valores únicos | Ejemplos |
|-----------|----------------|----------|
| **PROCESO** | 184 | Pre Compra, Arrepentimiento - XD, Despacho Ventas y Publicaciones |
| **CDU** | 374 | Arrepentimiento - Cambio de opinión, Defectuoso - Producto dañado |
| **TIPIFICACION** | 5 | Solicitud de devolución, Consulta de estado de envío |
| **ENVIRONMENT** | 5 | XD, FBM, FLEX, DS, MP_ON |

**Total:** 568 valores únicos mapeados.

---

## Casos de uso

### Caso 1: Usuario menciona un proceso

```
Usuario: "analiza arrepentimiento mlb nov dic"
```

**Flujo:**
1. Detector identifica: `PROCESO: Arrepentimiento - XD → PDD`
2. Agente confirma: "Voy a analizar Proceso Arrepentimiento - XD (PDD) en MLB Nov vs Dic"
3. Ejecuta análisis con `--commerce-group PDD --process-name "Arrepentimiento - XD"`

---

### Caso 2: Usuario menciona un environment

```
Usuario: "cr de xd en mla dic"
```

**Flujo:**
1. Detector identifica: `ENVIRONMENT: XD → PDD, PNR`
2. Agente confirma: "Environment XD cruza PDD y PNR. ¿Querés analizar ambos o solo uno?"
3. Usuario elige (o agente analiza ambos por defecto)

---

### Caso 3: Valor no encontrado con sugerencias

```
Usuario: "reputacion me mlb"
```

**Flujo:**
1. Detector NO encuentra "reputacion me" (sin tilde)
2. Detector sugiere: "Reputación ME" (con tilde)
3. Agente: "No encontré 'reputacion me'. ¿Quisiste decir: Reputación ME (PROCESO)?"
4. Usuario confirma
5. Ejecuta análisis

---

## Mantenimiento

### Actualizar el mapeo

**Cuándo:**
- Mensualmente (mínimo)
- Cuando se agregan nuevos procesos/CDUs a Commerce
- Cuando cambia la taxonomía

**Cómo:**
```bash
# 1. Generar datos desde BigQuery (16 segundos)
Get-Content sql/temp_generar_mapeo_dimensiones.sql -Raw | bq query --use_legacy_sql=false --format=csv > output/temp_mapeo_dimensiones_raw.csv

# 2. Procesar CSV y generar JSON (5 segundos)
py scripts/actualizar_mapeo_dimensiones.py
```

**Output:**
- `config/dimensions-mapping.json` actualizado
- Resumen en consola con estadísticas

---

## Beneficios

| Métrica | Antes (v4.x) | Después (v5.0) | Mejora |
|---------|--------------|----------------|--------|
| **Tiempo de confirmación** | 2-3 min (query a BQ) | 0.1 seg (lookup JSON) | **99% más rápido** |
| **Interacciones usuario** | 3-4 | 1 | **75% reducción** |
| **Experiencia** | Frustración (usuario da info que el sistema ya tiene) | Fluida (agente sabe automáticamente) | **100% mejor** |
| **Errores de tipeo** | Usuario escribe mal → análisis falla | Fuzzy matching → sugerencias | **0 errores** |

---

## Testing

### Test manual:

```bash
py utils/dimension_detector.py
```

**Output esperado:**
```
=== Test DimensionDetector ===

Buscando: 'Pre Compra'
  -> Dimension: PROCESO
  -> Commerce Groups: Generales Compra
  -> Casos mensuales promedio: 24271

Buscando: 'XD'
  -> Dimension: ENVIRONMENT
  -> Commerce Groups: PDD, PNR
  -> Casos mensuales promedio: 333997
```

---

## Limitaciones conocidas

1. **Solo últimos 3 meses:** El mapeo se genera con data de últimos 3 meses. Procesos antiguos descontinuados no aparecen.

2. **Threshold de 100 casos:** Valores con < 100 casos en 3 meses no se incluyen (para evitar ruido).

3. **No incluye VERTICAL ni DOMAIN:** Estas dimensiones aún no están disponibles en `BT_CX_CONTACTS` (campos NULL).

4. **No incluye SOLUTION_ID, CHANNEL_ID, SOURCE_ID:** La query actual solo genera 4 dimensiones. Para agregar más, editar `sql/temp_generar_mapeo_dimensiones.sql`.

---

## Roadmap

### v5.1 (próximo)
- [ ] Agregar SOLUTION_ID, CHANNEL_ID, SOURCE_ID al mapeo
- [ ] Incluir metadata de "procesos relacionados" (ej: CDU → mostrar sus procesos)
- [ ] API REST opcional para lookup desde otras herramientas

### v5.2 (futuro)
- [ ] Fallback automático a BigQuery si valor no está en mapeo local
- [ ] Actualización automática del mapeo (cronjob mensual)
- [ ] Versionado del mapeo (rollback si hay problemas)

---

## Documentación relacionada

- **Implementación:** `utils/dimension_detector.py`
- **Generador:** `scripts/actualizar_mapeo_dimensiones.py`
- **Query base:** `sql/temp_generar_mapeo_dimensiones.sql`
- **Integración en agente:** `.cursorrules` líneas 254-296
- **Changelog:** `CHANGELOG_v5.0_DIMENSION_DETECTOR.md` (este archivo)

---

**Última actualización:** Febrero 2026  
**Versión:** 5.0  
**Status:** ✅ PRODUCTION READY
