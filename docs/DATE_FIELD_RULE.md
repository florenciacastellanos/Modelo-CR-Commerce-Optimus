# 📅 REGLA CRÍTICA: Campo de Fecha para Incoming

**Versión**: 3.1  
**Última actualización**: Enero 2026  
**Estado**: ✅ VALIDADO - Obligatorio para todos los análisis

---

## ⚠️ REGLA CRÍTICA

**SIEMPRE** usar `CONTACT_DATE_ID` para calcular incoming de contactos.

**NUNCA** usar `OFC_MONTH_ID` o `PERIOD_MONTH` a menos que el usuario lo solicite **explícitamente**.

---

## 🎯 Campo Correcto por Tabla

### BT_CX_CONTACTS (Incoming Cases)

**✅ CORRECTO:**
```sql
DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS FECHA_MONTH
```

**❌ INCORRECTO:**
```sql
C.OFC_MONTH_ID  -- Puede causar diferencias significativas
C.PERIOD_MONTH  -- No usar
```

### BT_ORD_ORDERS (Drivers)

**✅ CORRECTO:**
```sql
DATE_TRUNC(ORD_CLOSED_DT, MONTH) AS FECHA_MONTH
```

---

## 📊 Diferencias Observadas

### Ejemplo Real (PDD MLA Nov-Dic 2025)

| Métrica | Con OFC_MONTH_ID | Con CONTACT_DATE_ID | Diferencia |
|---------|------------------|---------------------|------------|
| **Incoming Nov** | 95,604 | 98,981 | +3,377 (+3.5%) |
| **Incoming Dic** | 101,004 | 111,808 | +10,804 (+10.7%) |
| **Procesos** | 70 | 73 | +3 |

**Conclusión:** `CONTACT_DATE_ID` captura más casos reales y coincide con los reportes oficiales de producción.

---

## 🔧 Implementación Correcta

### Query Template para Incoming

```sql
WITH BASE_CONTACTS AS (
    SELECT
        DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS FECHA_MONTH,
        C.PROCESS_NAME,
        C.PROCESS_PROBLEMATIC_REPORTING,
        1.0 AS CANT_CASES
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE 1=1
        AND DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
        AND C.SIT_SITE_ID = 'MLA'
        AND C.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
)
SELECT
    FECHA_MONTH,
    PROCESS_NAME,
    SUM(CANT_CASES) AS INCOMING_CASES
FROM BASE_CONTACTS
GROUP BY FECHA_MONTH, PROCESS_NAME
ORDER BY FECHA_MONTH, INCOMING_CASES DESC
```

### Query Template para Drivers

```sql
SELECT
    DATE_TRUNC(ORD_CLOSED_DT, MONTH) AS FECHA_MONTH,
    COUNT(DISTINCT ORD_ORDER_ID) AS TOTAL_ORDERS
FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
WHERE 1=1
    AND SIT_SITE_ID = 'MLA'
    AND DATE_TRUNC(ORD_CLOSED_DT, MONTH) IN ('2025-11-01', '2025-12-01')
    AND ORD_CLOSED_DT IS NOT NULL
GROUP BY FECHA_MONTH
ORDER BY FECHA_MONTH
```

---

## 🔄 Formato de Fechas

### Para Filtros SQL

**✅ CORRECTO:**
```sql
WHERE DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) IN ('2025-11-01', '2025-12-01')
```

**Formato**: `'YYYY-MM-DD'` (siempre primer día del mes)

**Ejemplos válidos:**
- `'2025-11-01'` → Noviembre 2025
- `'2025-12-01'` → Diciembre 2025
- `'2024-10-01'` → Octubre 2024

### Para Display/Reportes

**Formato amigable**: `YYYY-MM` o `Mes YYYY`
- `2025-11` → Noviembre 2025
- `2025-12` → Diciembre 2025

**Nota:** Usar formato ISO solo internamente en las queries. En reportes HTML/CSV mostrar formato legible.

---

## 📝 Python Implementation

### Procesamiento en Pandas

```python
# Después de obtener datos de BigQuery
df_drivers = client.query(query_drivers).to_dataframe()

# Convertir FECHA_MONTH a string para comparación
df_drivers['FECHA_MONTH_STR'] = df_drivers['FECHA_MONTH'].astype(str)

# Filtrar por mes (flexible)
driver_nov = int(df_drivers[
    df_drivers['FECHA_MONTH_STR'].str.startswith('2025-11')
]['TOTAL_ORDERS'].iloc[0])

driver_dic = int(df_drivers[
    df_drivers['FECHA_MONTH_STR'].str.startswith('2025-12')
]['TOTAL_ORDERS'].iloc[0])
```

**Razón:** BigQuery puede devolver fechas en distintos formatos (date, datetime, timestamp). Convertir a string garantiza compatibilidad.

---

## ✅ Validación

### Checklist para Queries

Antes de ejecutar una query de incoming, verificar:

- [ ] ✅ Usa `DATE_TRUNC(C.CONTACT_DATE_ID, MONTH)`
- [ ] ✅ Formato de fechas: `'YYYY-MM-DD'`
- [ ] ✅ Primer día del mes: `'2025-11-01'` (no `'2025-11-15'`)
- [ ] ✅ No usa `OFC_MONTH_ID` ni `PERIOD_MONTH`
- [ ] ✅ Para drivers: `DATE_TRUNC(ORD_CLOSED_DT, MONTH)`

### Test Query

```sql
-- Verificar diferencia entre campos
SELECT 
    DATE_TRUNC(CONTACT_DATE_ID, MONTH) AS FECHA_CONTACT,
    OFC_MONTH_ID,
    COUNT(*) AS CASOS,
    COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC(CONTACT_DATE_ID, MONTH)) AS DIFERENCIA
FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
WHERE SIT_SITE_ID = 'MLA'
  AND DATE_TRUNC(CONTACT_DATE_ID, MONTH) >= '2025-10-01'
GROUP BY FECHA_CONTACT, OFC_MONTH_ID
ORDER BY FECHA_CONTACT
```

---

## 🚨 Excepciones

**Única excepción:** Si el usuario solicita **explícitamente** usar `OFC_MONTH_ID`:

❌ Usuario: "Calcula el CR de PDD"  
→ Usar `CONTACT_DATE_ID` (default)

✅ Usuario: "Calcula el CR de PDD **usando OFC_MONTH_ID**"  
→ Usar `OFC_MONTH_ID` (explícito)

✅ Usuario: "Compara CONTACT_DATE_ID vs OFC_MONTH_ID"  
→ Calcular ambos (comparación solicitada)

---

## 📚 Alcance

Esta regla aplica a:

### ✅ Todos los Commerce Groups
- PDD (Producto Dañado/Defectuoso)
- PNR (Producto No Recibido)
- ME Distribución
- ME PreDespacho
- ME Drivers
- FBM Sellers
- Pre Venta
- Post Venta
- Generales Compra
- Moderaciones
- Full Sellers
- Pagos
- MP On
- Cuenta
- Experiencia Impositiva

### ✅ Todos los Tipos de Análisis
- Contact Rate (CR)
- Variaciones MoM
- Top procesos
- Análisis por dimensión (CDU, REASON_DETAIL, etc.)
- Reportes HTML/CSV
- Dashboards
- Validaciones

### ✅ Todos los Sites
- MLA, MLB, MLC, MCO, MLM, MLU, MPE

---

## 🔗 Referencias

- **Reglas principales**: `.cursorrules` (sección 10)
- **Table definitions**: `docs/table-definitions.md`
- **Script ejemplo**: `generar_cr_pdd_nov_dic_CONTACT_DATE.py`
- **Validación**: Tests con datos reales (Enero 2026)

---

## ⚡ TL;DR

```
INCOMING → DATE_TRUNC(CONTACT_DATE_ID, MONTH)
DRIVERS  → DATE_TRUNC(ORD_CLOSED_DT, MONTH)
FORMATO  → 'YYYY-MM-DD' (e.g., '2025-11-01')
EXCEPCIÓN → Solo si se solicita explícitamente otro campo
```

**¿Por qué?** Porque coincide con los reportes oficiales y captura la data real completa.

---

**Última validación**: Enero 2026 con datos PDD MLA Nov-Dic 2025  
**Estado**: ✅ OBLIGATORIO para todo el repositorio
