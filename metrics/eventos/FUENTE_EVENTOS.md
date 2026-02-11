# 📅 Fuente de Eventos Comerciales

**Versión:** 2.0  
**Fecha:** Enero 2026  
**Status:** ✅ ACTIVO

---

## 🎯 Tabla Fuente Oficial

Los eventos comerciales y sus fechas se obtienen desde:

```
meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT
```

---

## 📊 Schema Esperado

La tabla debe contener los siguientes campos:

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `SIT_SITE_ID` | STRING | Código del site | 'MLB', 'MLA', 'MCO' |
| `EVENT_NAME` | STRING | Nombre del evento | 'Black Friday Brasil' |
| `EVENT_START_DATE` | DATE/TIMESTAMP | Fecha de inicio | '2025-11-28' |
| `EVENT_END_DATE` | DATE/TIMESTAMP | Fecha de fin | '2025-11-30' |

---

## 🔍 Query Utilizada

El script ejecuta la siguiente consulta para obtener eventos:

```sql
SELECT DISTINCT
    SIT_SITE_ID as SITE,
    EVENT_NAME as NOMBRE_EVENTO,
    DATE(EVENT_START_DATE) as FECHA_INICIO,
    DATE(EVENT_END_DATE) as FECHA_FIN
FROM `meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT`
WHERE SIT_SITE_ID = '{site}'
    AND EVENT_START_DATE >= DATE_SUB('{periodo}', INTERVAL 1 MONTH)
    AND EVENT_START_DATE <= DATE_ADD('{periodo}', INTERVAL 2 MONTH)
    AND EVENT_NAME IS NOT NULL
    AND EVENT_START_DATE IS NOT NULL
    AND EVENT_END_DATE IS NOT NULL
ORDER BY EVENT_START_DATE
```

**Rango de fechas:**
- Se consultan eventos que comienzan hasta 1 mes antes del período
- Hasta 2 meses después del período
- Esto captura eventos que pueden afectar al incoming del mes analizado

---

## 📝 Ejemplo de Datos

### **MLB (Brasil) - Nov-Dic 2025**

| SITE | EVENT_NAME | EVENT_START_DATE | EVENT_END_DATE | Duración |
|------|-----------|------------------|----------------|----------|
| MLB | Black Friday Brasil | 2025-11-28 | 2025-11-30 | 3 días |
| MLB | Cyber Monday | 2025-12-01 | 2025-12-05 | 5 días |
| MLB | Natal | 2025-12-20 | 2025-12-25 | 6 días |

### **MLA (Argentina) - Nov-Dic 2025**

| SITE | EVENT_NAME | EVENT_START_DATE | EVENT_END_DATE | Duración |
|------|-----------|------------------|----------------|----------|
| MLA | Black Friday | 2025-11-28 | 2025-11-29 | 2 días |
| MLA | Cyber Monday | 2025-12-01 | 2025-12-03 | 3 días |
| MLA | Navidad | 2025-12-20 | 2025-12-25 | 6 días |

### **MLM (México) - Nov-Dic 2025**

| SITE | EVENT_NAME | EVENT_START_DATE | EVENT_END_DATE | Duración |
|------|-----------|------------------|----------------|----------|
| MLM | Buen Fin | 2025-11-15 | 2025-11-18 | 4 días |
| MLM | Cyber Monday | 2025-12-01 | 2025-12-05 | 5 días |
| MLM | Navidad | 2025-12-20 | 2025-12-25 | 6 días |

---

## 🔄 Lógica de Correlación

### **Paso 1: Obtener Eventos**
```python
eventos = obtener_eventos_comerciales(client, site='MLB', periodo='2025-12')
# Resultado:
# {
#   'black_friday_brasil': {
#     'nombre': 'Black Friday Brasil',
#     'fecha_inicio': '2025-11-28',
#     'fecha_fin': '2025-11-30'
#   },
#   ...
# }
```

### **Paso 2: Filtrar Incoming por ORD_CLOSED_DT**
```python
# Para cada evento
for evento in eventos:
    # Casos donde la orden se cerró DENTRO del rango del evento
    casos_correlacionados = incoming[
        (incoming['ORD_CLOSED_DATE'] >= evento['fecha_inicio']) & 
        (incoming['ORD_CLOSED_DATE'] <= evento['fecha_fin'])
    ]
```

### **Paso 3: Calcular Porcentaje**
```python
# Por tipificación
for tipif in tipificaciones:
    casos_totales = len(incoming[incoming['TIPIFICACION'] == tipif])
    casos_en_evento = len(casos_correlacionados[...])
    porcentaje = (casos_en_evento / casos_totales) * 100
```

---

## 📐 Ejemplo Completo

**Datos de entrada:**
- **Site:** MLB
- **Período:** Diciembre 2025
- **Tipificación:** REPENTANT_BUYER
- **Total casos:** 153,014

**Evento: Black Friday Brasil**
- **Fecha inicio:** 2025-11-28
- **Fecha fin:** 2025-11-30
- **Casos con ORD_CLOSED_DT en rango:** 7,653
- **Porcentaje:** 5.0%

**Interpretación:**
De los 153,014 casos de arrepentimiento en Diciembre 2025, 7,653 (5.0%) corresponden a órdenes que se cerraron durante el Black Friday Brasil (28-30 Nov).

---

## ✅ Validaciones

El script valida automáticamente:

1. **Tabla existe**: Verifica acceso a `WHOWNER.LK_MKP_PROMOTIONS_EVENT`
2. **Eventos encontrados**: Confirma que hay eventos para el site/período
3. **Fechas válidas**: `EVENT_START_DATE <= EVENT_END_DATE`
4. **Datos completos**: No hay NULL en campos críticos

---

## 🐛 Troubleshooting

### **Error: Tabla no encontrada**
```
Error: Table meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT not found
```

**Causa:** No tienes permisos de acceso a la tabla

**Solución:**
1. Verifica permisos en BigQuery
2. Solicita acceso a `WHOWNER.LK_MKP_PROMOTIONS_EVENT`
3. Confirma que la tabla existe en tu proyecto

### **Warning: No se encontraron eventos**
```
[EVENTOS] ⚠️ No se encontraron eventos en tabla oficial
```

**Posibles causas:**
1. No hay eventos registrados para ese site/período
2. Los eventos están fuera del rango de búsqueda
3. Filtros de la query son muy restrictivos

**Solución:**
1. Verifica manualmente la tabla para el site:
   ```sql
   SELECT * FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT
   WHERE SIT_SITE_ID = 'MLB'
   ORDER BY EVENT_START_DATE DESC
   LIMIT 10
   ```
2. Ajusta el rango de búsqueda si es necesario

### **Error: Fechas inválidas**
```
EVENT_START_DATE > EVENT_END_DATE
```

**Causa:** Datos inconsistentes en la tabla fuente

**Solución:**
1. Reportar inconsistencia al equipo de data
2. Temporalmente excluir esos eventos con filtro adicional

---

## 📚 Referencias

### **Documentación del sistema:**
- ⭐ **Guía de usuario:** `../GUIA_USUARIO.md` - Si eres nuevo, empieza aquí
- **Documentación principal:** `../README.md`
- **README eventos:** `README.md` (este archivo)
- ⭐ **Cuándo regenerar:** `CUANDO_REGENERAR.md` - Mantenimiento del sistema

### **Scripts y código:**
- **Script generador:** `generar_correlaciones.py`
- **Ejemplos de uso:** `ejemplo_uso.py`

### **Integración:**
- **Integración en templates:** `../INTEGRACION_GOLDEN_TEMPLATES.md`
- **Reglas oficiales:** `../../.cursorrules` (Regla 16)

---

## 🔄 Actualización de Datos

### **¿Cuándo regenerar métricas?**

1. **Cambio en fechas de eventos** en la tabla fuente
2. **Nuevos eventos agregados** al calendario
3. **Corrección de datos** en `LK_MKP_PROMOTIONS_EVENT`

### **Proceso:**
```bash
# Regenerar métricas para un período
python metrics/eventos/generar_correlaciones.py --site MLB --periodo 2025-12

# Las métricas se actualizan con las fechas más recientes de la tabla
```

---

**Última actualización:** Enero 2026  
**Versión:** 2.0  
**Mantenedor:** CR Analytics Team
