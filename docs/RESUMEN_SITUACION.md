# 📊 Resumen de la Situación - Contact Rate Analysis

## ✅ Estado Actual de Autenticación:

```
✅ Token de acceso: VÁLIDO
✅ Proyecto gcloud: meli-bi-data
✅ Cuenta activa: florencia.castellanos@mercadolibre.com
✅ Credenciales: C:\Users\flocastellanos\AppData\Roaming\gcloud\application_default_credentials.json
```

## ❌ Problema Identificado:

**Error 403 Forbidden**: Tu cuenta NO tiene el permiso necesario para ejecutar jobs de BigQuery desde Python local.

**Rol faltante**: `roles/serviceusage.serviceUsageConsumer`

**Esto NO significa** que tus credenciales estén mal. Significa que Google Cloud tiene **2 niveles de permisos**:
1. ✅ **Autenticación** (quién eres) → CORRECTO
2. ❌ **Autorización IAM** (qué puedes hacer) → FALTA ROL

---

## 🎯 Cómo Calcular los Drivers (Respuesta a tu pregunta):

### **Drivers desde BigQuery (MÉTODO CORRECTO)**:

Los drivers se calculan así en la query SQL:

```sql
-- Paso 1: Contar órdenes únicas por proceso y período
ORDERS_BY_PROCESS AS (
    SELECT
        FORMAT_DATETIME('%Y-%m', O.ORD_CLOSED_DT) AS PERIOD_MONTH,  -- Período de cierre
        C.PROCESS_NAME,
        COUNT(DISTINCT O.ORD_ORDER_ID) AS ORDERS_COUNT  -- ← CUENTA ÓRDENES ÚNICAS
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` O
    INNER JOIN `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
        ON O.ORD_ORDER_ID = C.SOURCE_ID        -- ← Join por ID de orden
        AND O.SIT_SITE_ID = C.SIT_SITE_ID
    WHERE ...
    GROUP BY 1, 2
)

-- Paso 2: Pivotar por período
DRIVERS_PIVOTED AS (
    SELECT
        PROCESS_NAME,
        SUM(CASE WHEN PERIOD_MONTH = '2025-11' THEN ORDERS_COUNT ELSE 0 END) AS DRIVER_NOV,
        SUM(CASE WHEN PERIOD_MONTH = '2025-12' THEN ORDERS_COUNT ELSE 0 END) AS DRIVER_DIC
    FROM ORDERS_BY_PROCESS
    GROUP BY 1
)

-- Paso 3: Si un proceso no tiene órdenes linkadas, usar total del site
COMBINED AS (
    SELECT
        I.PROCESS_NAME,
        I.INCOMING_NOV,
        I.INCOMING_DIC,
        -- Fallback al total de órdenes del site
        COALESCE(D.DRIVER_NOV, (SELECT TOTAL_ORDERS FROM TOTAL_ORDERS WHERE PERIOD_MONTH = '2025-11')) AS DRIVER_NOV,
        COALESCE(D.DRIVER_DIC, (SELECT TOTAL_ORDERS FROM TOTAL_ORDERS WHERE PERIOD_MONTH = '2025-12')) AS DRIVER_DIC
    FROM INCOMING_PIVOTED I
    LEFT JOIN DRIVERS_PIVOTED D ON I.PROCESS_NAME = D.PROCESS_NAME
)
```

**Explicación**:
- **BT_ORD_ORDERS**: Tabla de órdenes de Mercado Libre
- **ORD_ORDER_ID**: ID único de la orden (es el driver)
- **ORD_CLOSED_DT**: Fecha de cierre de la orden
- **SOURCE_ID en BT_CX_CONTACTS**: Referencia al ORD_ORDER_ID

**Resultado**:
- `DRIVER_NOV`: Total de órdenes completadas en Nov 2025 para ese proceso
- `DRIVER_DIC`: Total de órdenes completadas en Dic 2025 para ese proceso

---

## 🚀 Soluciones para Obtener el Reporte REAL:

### **OPCIÓN 1: BigQuery Console** (⭐ YA ABIERTO EN TU NAVEGADOR)

```
1. Copia la query de: QUERY_COMPLETA_PARA_BIGQUERY.sql
2. Pégala en BigQuery Console (ya abierto)
3. Click en RUN
4. SAVE RESULTS → CSV
5. Guárdalo como: resultados_bigquery_real.csv
6. Ejecuta: py generar_html_desde_csv.py
```

**Tiempo**: 2-3 minutos  
**Resultado**: HTML con datos 100% reales de BigQuery

---

### **OPCIÓN 2: Solicitar Permisos IAM** (una sola vez)

Envía este mensaje a tu líder o administrador de IAM:

```
Hola, necesito el siguiente permiso para ejecutar queries de BigQuery:

Cuenta: florencia.castellanos@mercadolibre.com
Proyecto: meli-bi-data
Rol necesario: roles/serviceusage.serviceUsageConsumer

Esto me permitirá ejecutar análisis de Contact Rate desde Python local.
Gracias!
```

Una vez otorgado, ejecuta:
```bash
py ejecutar_directo.py
```

Y funcionará automáticamente siempre.

---

## 📝 Archivos Creados para Ti:

| Archivo | Propósito |
|---------|-----------|
| `QUERY_COMPLETA_PARA_BIGQUERY.sql` | Query completa para copiar en Console |
| `generar_html_desde_csv.py` | Convierte CSV descargado a HTML |
| `ejecutar_directo.py` | Script completo (requiere permisos IAM) |
| `EJECUTAR_EN_BIGQUERY_CONSOLE.md` | Guía paso a paso |
| `ejecutar_en_jupyter.py` | Para Jupyter Lab |

---

## 💡 Recomendación:

**Ahora mismo**: Usa BigQuery Console (ya está abierto)  
**Para el futuro**: Solicita el rol IAM para automatizar todo desde Python

---

¿Quieres que te guíe paso a paso mientras ejecutas la query en BigQuery Console? Puedo ayudarte en tiempo real.
