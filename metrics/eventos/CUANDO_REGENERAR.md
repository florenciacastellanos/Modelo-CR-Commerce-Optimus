# 🔄 Cuándo Regenerar Métricas de Eventos

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Criticidad:** ⚠️ ALTA - Afecta precisión de reportes

---

## 🎯 Propósito de este Documento

Este documento define **claramente cuándo es necesario regenerar** las métricas precalculadas de correlación con eventos comerciales, y cuándo NO es necesario.

**Audiencia:** Analistas de CR, Data Engineers, mantenedores del repositorio

---

## ✅ Casos que REQUIEREN Regeneración (OBLIGATORIO)

### **1. Cambio en Fechas de Eventos Comerciales**

**Trigger:**
```
La tabla WHOWNER.LK_MKP_PROMOTIONS_EVENT tiene fechas actualizadas
para eventos existentes
```

**Ejemplo:**
```
Black Friday MLA originalmente: 2025-11-28 a 2025-11-29 (2 días)
Actualización: 2025-11-28 a 2025-11-30 (3 días)
→ REGENERAR para capturar el día adicional
```

**Comando:**
```bash
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-11
```

**Validación:**
```python
# Verificar metadata después de regenerar
import json
with open('metrics/eventos/data/metadata_mla_2025_11.json') as f:
    metadata = json.load(f)
    print(metadata['eventos_detalle'])
    # Confirmar que Black Friday ahora muestra duracion_dias: 3
```

---

### **2. Nuevos Eventos Comerciales Agregados**

**Trigger:**
```
Se agregó un nuevo evento a LK_MKP_PROMOTIONS_EVENT que NO estaba
en la generación anterior
```

**Ejemplo:**
```
Nuevo evento: "Hot Sale" (2025-12-15 a 2025-12-18)
→ REGENERAR para incluir correlaciones con este nuevo evento
```

**¿Cómo detectarlo?**
```sql
-- Comparar eventos actuales vs. los que están en metadata
SELECT EVENT_NAME, EVENT_START_DTTM, EVENT_END_DTTM
FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT
WHERE SIT_SITE_ID = 'MLA'
  AND DATE(EVENT_START_DTTM) >= '2025-11-01'
  AND DATE(EVENT_START_DTTM) <= '2026-01-31'
ORDER BY EVENT_START_DTTM
```

Comparar con:
```python
import json
with open('metrics/eventos/data/metadata_mla_2025_12.json') as f:
    metadata = json.load(f)
    eventos_en_metadata = metadata['eventos_incluidos']
    print("Eventos en metadata:", eventos_en_metadata)
```

---

### **3. Corrección de Datos en Incoming**

**Trigger:**
```
Se detectó un error en BT_CX_CONTACTS que afecta la clasificación
de casos (ej: cambio en FLAG_EXCLUDE_NUMERATOR_CR)
```

**Ejemplo:**
```
Se corrigió FLAG_EXCLUDE_NUMERATOR_CR para 500 casos que estaban
mal marcados
→ REGENERAR porque esos casos ahora entran/salen del cálculo
```

**¿Cómo detectarlo?**
- Notificación del equipo de Data Engineering
- Cambio en totales de incoming al correr queries de validación
- Diferencias entre metadata antiguo y nuevo cálculo

---

### **4. Cambio en Filtros Base de Incoming**

**Trigger:**
```
Se modificó la lógica de clasificación de Commerce Groups
(ej: nuevo CASE para PDD, cambio en criterio de PCF)
```

**Ejemplo:**
```
Antes: Solo PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
Ahora: Agregado "Conflict Others" → PDD
→ REGENERAR porque más casos entran en PDD
```

**Comando para regenerar todos los sites afectados:**
```bash
python metrics/eventos/generar_correlaciones.py --sites MLA,MLB,MLC,MCO,MEC,MLM,MLU,MPE --periodo 2025-12
```

---

### **5. Cambio en Lógica de Correlación**

**Trigger:**
```
Se modificó cómo se determina la correlación con eventos
```

**Ejemplo:**
```
Antes: Correlación basada en fecha de contacto
Ahora: Correlación basada en ORD_CLOSED_DT
→ REGENERAR porque la lógica cambió completamente
```

**⚠️ Este es un cambio MAYOR - regenerar TODO:**
```bash
# Regenerar todos los sites y períodos disponibles
for site in MLA MLB MLC MCO MEC MLM MLU MPE; do
    for periodo in 2025-11 2025-12; do
        python metrics/eventos/generar_correlaciones.py --site $site --periodo $periodo
    done
done
```

---

## ❌ Casos que NO Requieren Regeneración

### **1. Cambios Estéticos en Reportes**

**Ejemplos:**
- Cambio de colores en HTML
- Modificación de tamaños de fuente
- Reordenamiento de tablas
- Cambio en labels o títulos

**Razón:** Las métricas son independientes de cómo se muestran.

---

### **2. Cambio en Análisis de Keywords**

**Ejemplo:**
```python
# Agregar nueva keyword
KEYWORDS = {
    'demora_entrega': ['demora', 'atraso', 'tardanza'],  # ✅ NUEVO
    ...
}
```

**Razón:** Las keywords se aplican en el reporte sobre los summaries, NO en las métricas de eventos.

---

### **3. Actualización de Documentación**

**Ejemplos:**
- Agregar comentarios al código
- Mejorar README
- Actualizar ejemplos

**Razón:** No afecta los datos, solo la comprensión.

---

### **4. Cambios en Metadata (sin afectar datos)**

**Ejemplo:**
```python
# Agregar campo descriptivo al metadata
metadata['descripcion'] = "Métricas de correlación con eventos"
```

**Razón:** Si solo agregas campos informativos que no cambian el cálculo, no es necesario.

---

## 🕒 Frecuencia de Regeneración

### **Recomendaciones:**

| Escenario | Frecuencia | Comando |
|-----------|-----------|---------|
| **Período nuevo** (ej: Enero 2026) | Al iniciar análisis de ese mes | `--periodo 2026-01` |
| **Validación mensual** | Una vez por mes | Regenerar mes anterior |
| **Cambio en tabla eventos** | Inmediatamente después del cambio | Todos los períodos afectados |
| **Auditoría** | Trimestral | Regenerar últimos 3 meses |

---

## 📋 Checklist de Regeneración

Cuando regeneres métricas, sigue este proceso:

### **Antes de regenerar:**
- [ ] Identificar qué cambió (eventos, filtros, datos)
- [ ] Determinar qué sites y períodos se ven afectados
- [ ] Hacer backup del metadata actual (opcional)

### **Durante la regeneración:**
- [ ] Ejecutar script con parámetros correctos
- [ ] Monitorear output para detectar errores
- [ ] Verificar que se crearon ambos archivos (.parquet + .json)

### **Después de regenerar:**
- [ ] Comparar metadata nuevo vs. anterior (si aplica)
- [ ] Validar que los totales tienen sentido
- [ ] Revisar eventos_detalle en metadata
- [ ] Ejecutar query de validación (ver abajo)

---

## ✅ Query de Validación Post-Regeneración

Después de regenerar métricas, ejecuta esta query para confirmar:

```python
import pandas as pd
import json

# Cargar métricas
df = pd.read_parquet('metrics/eventos/data/correlacion_mla_2025_12.parquet')

# Validaciones
print("="*60)
print("VALIDACIÓN DE MÉTRICAS")
print("="*60)

# 1. Totales por Commerce Group
print("\n1. TOTALES POR COMMERCE GROUP:")
print(df.groupby('COMMERCE_GROUP')['CASOS'].sum())

# 2. Eventos detectados
print("\n2. EVENTOS DETECTADOS:")
print(df['EVENTO'].unique())

# 3. Porcentajes (deben estar entre 0-100)
print("\n3. RANGO DE PORCENTAJES:")
print(f"   Min: {df['PORCENTAJE'].min():.2f}%")
print(f"   Max: {df['PORCENTAJE'].max():.2f}%")
assert df['PORCENTAJE'].min() >= 0, "Porcentaje negativo detectado!"
assert df['PORCENTAJE'].max() <= 100, "Porcentaje > 100% detectado!"

# 4. Casos <= Casos Totales
print("\n4. CONSISTENCIA DE CASOS:")
invalidos = df[df['CASOS'] > df['CASOS_TOTALES']]
if len(invalidos) > 0:
    print(f"   ❌ {len(invalidos)} registros con CASOS > CASOS_TOTALES")
else:
    print(f"   ✅ Todos los registros son consistentes")

# 5. Metadata
print("\n5. METADATA:")
with open('metrics/eventos/data/metadata_mla_2025_12.json') as f:
    meta = json.load(f)
    print(f"   Total incoming: {meta['total_incoming']:,}")
    print(f"   Correlaciones: {meta['total_rows']}")
    print(f"   % correlacionado global: {meta['porcentaje_correlacionado_global']}%")
    print(f"   Eventos: {len(meta['eventos_incluidos'])}")
    print(f"   Fuente: {meta['eventos_source']}")

print("\n" + "="*60)
print("✅ VALIDACIÓN COMPLETADA")
print("="*60)
```

---

## 🚨 Señales de Alerta

**Regenera INMEDIATAMENTE si ves:**

⚠️ **Error en reporte:**
```
KeyError: 'EVENTO'
FileNotFoundError: correlacion_mla_2025_12.parquet
```
→ Faltan métricas o están corruptas

⚠️ **Correlaciones sospechosas:**
```
Black Friday: 0 casos (0.0%)
```
→ Probable error en lógica o fechas

⚠️ **Porcentajes imposibles:**
```
PORCENTAJE: 150.5%
```
→ Error en cálculo de casos totales

⚠️ **Metadata desactualizada:**
```
"eventos_dinamicos": false
"version": "1.0"
```
→ Usando versión antigua del script

---

## 📞 Contacto y Soporte

**Si tienes dudas sobre si regenerar o no:**

1. **Revisa el metadata** del archivo actual:
   ```bash
   cat metrics/eventos/data/metadata_{site}_{periodo}.json
   ```

2. **Compara con la tabla oficial:**
   ```sql
   SELECT * FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT
   WHERE SIT_SITE_ID = 'MLA' 
   ORDER BY EVENT_START_DTTM DESC LIMIT 10
   ```

3. **Consulta este documento** en caso de ambigüedad

---

## 📊 Log de Regeneraciones (Tracking)

Para mantener historial, documenta aquí las regeneraciones importantes:

| Fecha | Site | Período | Motivo | Usuario |
|-------|------|---------|--------|---------|
| 2026-01-27 | MLA | 2025-11, 2025-12 | Implementación inicial sistema v2.0 | FloC |
| | | | | |
| | | | | |

---

**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Mantenedor:** CR Analytics Team
