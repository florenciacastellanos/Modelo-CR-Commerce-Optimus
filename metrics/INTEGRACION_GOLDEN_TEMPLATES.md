# 🔗 Guía de Integración - Métricas en Golden Templates

**Versión:** 1.0  
**Fecha:** Enero 2026

Esta guía explica cómo integrar las métricas duras de correlación con eventos en tus scripts Golden Templates existentes.

---

## 📋 Resumen de Cambios

### **Antes (Sin Métricas)**
- Calcular correlación en cada reporte sobre muestra (100 casos)
- Tiempo: 8-10 minutos
- Precisión: Limitada por muestra

### **Después (Con Métricas)**
- Leer métricas pre-calculadas sobre TODO el incoming
- Tiempo: 2-3 minutos
- Precisión: 100% (todos los casos)

---

## 🛠️ Pasos de Integración

### **Paso 1: Pre-requisito - Generar Métricas**

Antes de ejecutar tu reporte, genera las métricas para el período:

```bash
# Ejemplo: PDD MLB Nov-Dic 2025
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-11
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12
```

### **Paso 2: Modificar Script Golden Template**

#### **2.1 Agregar imports al inicio**

```python
from pathlib import Path
import json
```

#### **2.2 Función para cargar métricas (agregar después de imports)**

```python
def cargar_metricas_eventos(site, periodo):
    """
    Carga métricas pre-calculadas de eventos.
    Si no existen, retorna None para calcular on-the-fly.
    """
    metrics_path = Path('metrics/eventos/data')
    periodo_str = periodo.replace('-', '_')
    file_corr = metrics_path / f'correlacion_{site.lower()}_{periodo_str}.parquet'
    
    if file_corr.exists():
        print(f"[METRICS] ✅ Cargando métricas pre-calculadas: {file_corr}")
        return pd.read_parquet(file_corr)
    else:
        print(f"[METRICS] ⚠️  Métricas no encontradas: {file_corr}")
        print(f"[METRICS] 💡 Ejecuta: python metrics/eventos/generar_correlaciones.py --site {site} --periodo {periodo}")
        print(f"[METRICS] 🔄 Fallback: Calculando correlación on-the-fly...")
        return None
```

#### **2.3 Cargar métricas al inicio del script**

```python
# Después de definir site y periodo
print("\n[GOLDEN] Cargando métricas de eventos...")
df_metricas_nov = cargar_metricas_eventos(site, '2025-11')
df_metricas_dic = cargar_metricas_eventos(site, '2025-12')
```

#### **2.4 Modificar función de análisis de correlación**

**ANTES:**
```python
def analizar_correlacion_eventos(casos_periodo):
    """Analiza correlación REAL con eventos basada en ORD_CLOSED_DATE"""
    correlaciones = {}
    
    for evento_key, evento_info in EVENTOS_COMERCIALES.items():
        fecha_inicio = pd.to_datetime(evento_info['fecha_inicio'])
        fecha_fin = pd.to_datetime(evento_info['fecha_fin'])
        
        casos_en_evento = casos_periodo[
            (casos_periodo['ORD_CLOSED_DATE'] >= fecha_inicio) & 
            (casos_periodo['ORD_CLOSED_DATE'] <= fecha_fin)
        ]
        
        count = len(casos_en_evento)
        porcentaje = (count / len(casos_periodo) * 100) if len(casos_periodo) > 0 else 0
        
        correlaciones[evento_key] = {
            'nombre': evento_info['nombre'],
            'casos': count,
            'porcentaje': porcentaje
        }
    
    return correlaciones
```

**DESPUÉS:**
```python
def analizar_correlacion_eventos_desde_metricas(df_metricas, tipificacion_actual, periodo):
    """
    Obtiene correlación desde métricas pre-calculadas.
    Si no existen métricas, retorna dict vacío.
    """
    if df_metricas is None:
        return {}
    
    correlaciones = {}
    
    # Filtrar por tipificación actual
    df_tipif = df_metricas[
        df_metricas['TIPIFICACION'] == tipificacion_actual
    ]
    
    for _, row in df_tipif.iterrows():
        evento_key = row['EVENTO'].lower().replace(' ', '_')
        correlaciones[evento_key] = {
            'nombre': row['EVENTO'],
            'casos': int(row['CASOS']),
            'porcentaje': float(row['PORCENTAJE'])
        }
    
    return correlaciones

# Mantener función vieja como fallback
def analizar_correlacion_eventos(casos_periodo):
    """
    [FALLBACK] Calcula correlación on-the-fly si no hay métricas.
    Solo se usa si cargar_metricas_eventos() retornó None.
    """
    # ... código original ...
```

#### **2.5 Usar métricas en el análisis por tipificación**

**ANTES:**
```python
# Análisis de correlación con eventos (solo Dic, donde están los eventos principales)
correlacion_eventos = analizar_correlacion_eventos(df_dic)
```

**DESPUÉS:**
```python
# Análisis de correlación con eventos
# Primero intentar desde métricas, sino calcular on-the-fly
if df_metricas_dic is not None:
    correlacion_eventos = analizar_correlacion_eventos_desde_metricas(
        df_metricas_dic, 
        tipif, 
        '2025-12'
    )
    print(f"[METRICS] ✅ Correlación cargada desde métricas para {tipif}")
else:
    # Fallback: calcular desde muestra
    correlacion_eventos = analizar_correlacion_eventos(df_dic)
    print(f"[METRICS] 🔄 Correlación calculada on-the-fly para {tipif}")
```

---

## 📄 Ejemplo Completo

Ver archivo: `metrics/eventos/ejemplo_integracion_golden.py` para un ejemplo completo de integración.

---

## ✅ Checklist de Integración

- [ ] Generar métricas para los períodos necesarios
- [ ] Agregar imports `Path` y `json`
- [ ] Agregar función `cargar_metricas_eventos()`
- [ ] Cargar métricas al inicio del script
- [ ] Agregar función `analizar_correlacion_eventos_desde_metricas()`
- [ ] Mantener función original como fallback
- [ ] Modificar llamadas para usar métricas primero
- [ ] Agregar logs para indicar si usa métricas o fallback
- [ ] Probar con métricas existentes
- [ ] Probar sin métricas (fallback)

---

## 🎯 Ventajas Post-Integración

| Aspecto | Antes | Después |
|---------|-------|---------|
| Tiempo ejecución | 8-10 min | 2-3 min |
| Precisión | Muestra (100) | Total (todos) |
| Casos analizados | ~400 | ~491,334 |
| Consistencia | Variable (sampling) | Siempre igual |
| Reutilización | ❌ | ✅ |

---

## 🐛 Troubleshooting

### **Error: FileNotFoundError**
```
FileNotFoundError: [Errno 2] No such file or directory: 'metrics/eventos/data/correlacion_mlb_2025_12.parquet'
```

**Solución:**
```bash
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12
```

### **Warning: Métricas no encontradas**
```
[METRICS] ⚠️  Métricas no encontradas
[METRICS] 🔄 Fallback: Calculando correlación on-the-fly...
```

**Explicación:**  
El script funciona normalmente, pero calcula correlación desde la muestra (modo antiguo). Para mejor precisión, genera las métricas.

### **Error: Tipificación no encontrada en métricas**
```
KeyError: 'REPENTANT_BUYER'
```

**Causa:**  
La tipificación no existe en las métricas (puede ser nueva o mal escrita).

**Solución:**
1. Verificar nombre correcto de tipificación
2. Regenerar métricas si la tipificación es nueva
3. El fallback on-the-fly manejará este caso automáticamente

---

### **Error: Correlaciones suman más del 100%**
```
Total correlacionado: 125.3% (imposible)
```

**Causa:**  
Un caso puede correlacionar con múltiples eventos si se superponen (ej: Black Friday termina 2025-12-03, Navidad empieza 2025-12-03).

**¿Es un error?**  
❌ NO - Es correcto. Un caso puede estar en 2+ eventos si las fechas se superponen.

**Solución:**  
Si necesitas porcentajes "mutuamente exclusivos", usa solo el primer evento en el que cae cada caso (lógica avanzada).

---

### **Error: JSON serialization error**
```
TypeError: Object of type int64 is not JSON serializable
```

**Causa:**  
Pandas devuelve `int64` que JSON no puede serializar directamente.

**Solución:**
```python
# Al crear metadata, convierte explícitamente
metadata = {
    'total_rows': int(len(df)),  # int64 → int nativo
    'total_incoming': int(df['CASOS_TOTALES'].sum()),
    'porcentaje': float(round(pct, 2))  # float64 → float nativo
}
```

---

### **Warning: BigQuery "quota exceeded"**
```
google.api_core.exceptions.ResourceExhausted: 403 Quota exceeded
```

**Causa:**  
Usuario autenticado sin proyecto de cuotas configurado.

**Solución temporal:**
Esperar y reintentar (las cuotas se recuperan)

**Solución permanente:**
Configurar proyecto de BigQuery:
```bash
gcloud config set project meli-bi-data
```

---

### **Performance: Script muy lento (>10 min)**

**Causa posible:**  
Consulta muy grande o sin optimización.

**Soluciones:**

1. **Usar QueryPriority.BATCH:**
```python
from google.cloud.bigquery import QueryJobConfig, QueryPriority

job_config = QueryJobConfig(priority=QueryPriority.BATCH)
df = client.query(query, job_config=job_config).to_dataframe()
```

2. **Limitar rango de fechas en joins:**
```sql
-- En lugar de:
LEFT JOIN DM_CX_POST_PURCHASE PP ON PP.CLA_CLAIM_ID = C.CLA_CLAIM_ID

-- Usar:
LEFT JOIN DM_CX_POST_PURCHASE PP 
    ON PP.CLA_CLAIM_ID = C.CLA_CLAIM_ID
    AND PP.ORD_CLOSED_DT BETWEEN '2025-10-01' AND '2025-12-31'
```

3. **Procesar sites en paralelo** (avanzado):
```bash
# En lugar de secuencial
for site in MLA MLB; do
    python metrics/eventos/generar_correlaciones.py --site $site --periodo 2025-12
done

# Usar paralelo (PowerShell)
$sites = @('MLA','MLB','MLC','MCO')
$sites | ForEach-Object -Parallel {
    python metrics/eventos/generar_correlaciones.py --site $_ --periodo 2025-12
} -ThrottleLimit 4
```

---

### **Diferencias en totales vs. query manual**

**Síntoma:**  
Tus métricas muestran 150,000 casos, pero tu query manual muestra 148,500

**Checklist de validación:**
- [ ] ¿Mismo período? Verifica `metadata['periodo']`
- [ ] ¿Mismos filtros? Compara `FLAG_EXCLUDE_NUMERATOR_CR`, `PROCESS_BU_CR_REPORTING`
- [ ] ¿Mismo CASE de clasificación? (PDD debe incluir "Conflict Others")
- [ ] ¿Tabla de eventos cambió? Verifica fecha de `generated_at` en metadata

**Solución:**
```bash
# Regenerar con datos más recientes
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
```

---

## 📚 Referencias

- **Guía de usuario:** `metrics/GUIA_USUARIO.md` ⭐ **NUEVO v4.0**
- **Cuándo regenerar:** `metrics/eventos/CUANDO_REGENERAR.md` ⭐ **NUEVO v4.0**
- **Documentación completa:** `metrics/README.md`
- **Eventos específicos:** `metrics/eventos/README.md`
- **Ejemplos de uso:** `metrics/eventos/ejemplo_uso.py`
- **Script generador:** `metrics/eventos/generar_correlaciones.py`

---

**Última actualización:** Enero 2026  
**Versión:** 2.0
