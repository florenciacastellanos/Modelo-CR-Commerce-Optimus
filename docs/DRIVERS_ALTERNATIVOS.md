# Drivers Alternativos - Documentación

> **Drivers opcionales por proceso/caso de uso para recalcular CR con denominadores específicos.**

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Status:** ACTIVO  
**Configuración:** `config/drivers_alternativos.py`

---

## Concepto

Los **drivers alternativos** permiten recalcular el Contact Rate (CR) usando un denominador diferente al estándar del Commerce Group. Son complementarios, no reemplazan el driver principal.

### Cuándo usar drivers alternativos

| Situación | Driver a usar |
|-----------|---------------|
| Análisis estándar de CR | Driver del Commerce Group (como siempre) |
| El usuario pide recalcular con un denominador específico | Driver alternativo |
| Deep dive sobre un proceso/CDU con métrica operativa propia | Driver alternativo |

### Flujo de uso

```
1. Se ejecuta el análisis estándar con el driver del Commerce Group
2. El usuario solicita: "recalculame con paradas de colecta"
3. Se busca en DRIVERS_ALTERNATIVOS la combinación CG > Proceso > CDU > driver_key
4. Se ejecuta la query del driver alternativo
5. Se recalcula CR = Incoming / Driver Alternativo × 100
6. Se presenta como información complementaria
```

**IMPORTANTE:** El análisis estándar siempre se mantiene. El driver alternativo es una vista adicional.

---

## Catálogo de Drivers Alternativos

---

### 1. ME PreDespacho > Reputación ME > HT Colecta

#### `paradas_colecta` - Paradas de Colecta

| Campo | Valor |
|-------|-------|
| **Label** | Paradas de Colecta |
| **Tabla** | `meli-bi-data.WHOWNER.DM_SHP_FBM_PICKUP` |
| **Campo fecha** | `DATES_DT` |
| **Expresión de conteo** | `COUNT(DISTINCT CONCAT(CUST_ID, '-', DATES_DT, '-', WAREHOUSE_ID))` |
| **Filtro por site** | Si (directo: `SITE_ID`) |
| **Sites disponibles** | MLA, MLB, MLC, MCO, MLM |
| **Driver estándar** | `SUM(drv.OS_WITHOUT_FBM)` (Shipping) |

**Descripción:**  
Cada "parada" es una visita única de colecta definida por la combinación vendedor + fecha + warehouse. Permite evaluar cuántos contactos genera cada operación de colecta, en lugar de usar órdenes como denominador.

**Clasificaciones disponibles:**

| Clasificación | Descripción | Valores |
|--------------|-------------|---------|
| `INCIDENT_TYPE` | Tipo de incidencia en la parada | No había paquetes, Local Cerrado, Sin espacio, Ruta No Iniciada, Problemas con dirección, No pasó, Otros, Colecta Parcial, Sin Incidencia, etc. |
| `CULPA` | Atribución de responsabilidad | Seller, MELI, Colecta parcial, Problemas con dirección, Sin Problema |
| `STATUS_ON_TIME` | Puntualidad de la colecta | ON_TIME, LATE, EARLY |
| `COVERAGE` | Cobertura geográfica | DENTRO_COBERTURA, etc. |

**Caso de uso típico:**  
"Quiero ver el CR de HT Colecta sobre paradas de colecta en MLA, no sobre órdenes"

---

### 2. FBM Sellers > (Todos los procesos) > CDUs que contienen "INBOUND"

#### `inbounds` - Inbounds (Cantidad de INBOUND_ID)

| Campo | Valor |
|-------|-------|
| **Label** | Inbounds (Cantidad de INBOUND_ID) |
| **Tabla principal** | `meli-bi-data.WHOWNER.BT_FBM_INBOUND_OPERATION_AGG` |
| **Tabla JOIN** | `meli-bi-data.WHOWNER.LK_CUS_CBT_ITEM_ORIGIN` (excluir CBT) |
| **Campo fecha** | `min_arrival_datetime_tz` |
| **Expresión de conteo** | `COUNT(DISTINCT i.INBOUND_ID)` |
| **Filtro por site** | Si (indirecto: prefijo de `warehouse_id`) |
| **Tipo filtro site** | `warehouse_prefix` (AR=MLA, BR=MLB, MX=MLM, CO=MCO, CL=MLC) |
| **Sites disponibles** | MLA, MLB, MLC, MCO, MLM |
| **Driver estándar** | `SUM(drv.OS_WITH_FBM)` (Shipping) |

**Descripción:**  
Total de inbounds únicos recibidos en el período. Cada inbound se identifica por `INBOUND_ID`. Permite calcular el CR sobre el volumen real de operaciones de ingreso de mercadería a warehouses FBM.

**Filtro de numerador (incoming):**

| Campo | Condición | Descripción |
|-------|-----------|-------------|
| `PROCESS_ID` | `IN (615, 1981, 2418)` | El incoming debe filtrarse solo por estos Process IDs al usar este driver alternativo |

**Filtros base del denominador (siempre aplicados):**

| Filtro | Condición | Razón |
|--------|-----------|-------|
| `inb_shipment_type` | `NOT IN ('transfer')` | Excluir transferencias internas |
| `warehouse_id` | `NOT LIKE '%TW%' AND NOT LIKE '%TR%'` | Excluir warehouses TW y TR |
| `CUS_CBT_MERCHANT_ID` | `IS NULL` (via LEFT JOIN) | Excluir merchants CBT |
| `INB_FLAG_REMOVAL` | `IN (0)` | Excluir removals |

**CDU match:** Este driver aplica a todos los CDUs cuyo nombre contiene "INBOUND" (`cdu_match_type: contains`, `cdu_match_value: INBOUND`).

**Proceso match:** Aplica a todos los procesos dentro de FBM Sellers (`_TODOS`).

**Nota sobre site:** La tabla no tiene columna `SITE_ID`. El site se deriva del prefijo del `warehouse_id`:

| Prefijo warehouse | Site |
|-------------------|------|
| `AR%` | MLA |
| `BR%` | MLB |
| `MX%` | MLM |
| `CO%` | MCO |
| `CL%` | MLC |

**Caso de uso típico:**  
"Quiero ver el CR de FBM Sellers para CDUs de INBOUND sobre cantidad de inbounds en MLB, no sobre órdenes con FBM"

---

### 3. FBM Sellers > FBM-Retiro de Stock > (Todos los CDUs)

#### `retiro_requests` - Requests de Retiro de Stock

| Campo | Valor |
|-------|-------|
| **Label** | Requests de Retiro de Stock |
| **Tabla principal** | `meli-bi-data.WHOWNER.BT_FBM_WITHDRAWALS_V2` |
| **Tablas JOIN (detalle)** | `meli-bi-data.EXPLOTACION.SEGMENTO` (segmento seller), `meli-bi-data.WHOWNER.DM_SUGGESTION_KVS_DATA` (retiros sugeridos) |
| **Campo fecha** | `FBM_WIT_DATE_CREATED` |
| **Expresión de conteo** | `COUNT(DISTINCT FBM_WIT_REQUEST_ID)` |
| **Filtro por site** | Si (directo: `SIT_SITE_ID`) |
| **Tipo filtro site** | `direct` |
| **Sites disponibles** | MLA, MLB, MLC, MCO, MLM |
| **Driver estándar** | `SUM(drv.OS_WITH_FBM)` (Shipping) |

**Descripción:**  
Total de requests de retiro de stock únicos realizados en el período. Cada request se identifica por `FBM_WIT_REQUEST_ID` y se deduplica tomando la primera fecha de creación. Permite calcular el CR sobre el volumen real de operaciones de retiro de stock en FBM, en lugar de usar órdenes con FBM como denominador.

**Filtros base (siempre aplicados):**

| Filtro | Condición | Razón |
|--------|-----------|-------|
| `warehouse_id` | `NOT LIKE '%TW%' AND NOT LIKE '%TR%'` | Excluir warehouses TW y TR |
| Deduplicación | `QUALIFY ROW_NUMBER() OVER(PARTITION BY FBM_WIT_REQUEST_ID ORDER BY FBM_WIT_DATE_CREATED ASC) = 1` | Tomar primera ocurrencia de cada request |

**Clasificaciones disponibles:**

| Clasificación | Descripción | Valores |
|--------------|-------------|---------|
| `TIPO_LOGISTICO` | Tipo logístico con detección de transfers | TRANSFER, CROSS_DOCKING, SAME_WAREHOUSE, DROP_OFF, etc. |
| `TIPO_LOGISTICO2` | Tipo logístico original (`FBM_SHIPMENT_TYPE`) | Valores dinámicos |
| `SEGMENTO` | Segmento del seller (desde tabla EXPLOTACION.SEGMENTO) | Valores dinámicos |
| `flag_sugerido` | Si el retiro fue sugerido por el sistema (confirmed en DM_SUGGESTION_KVS_DATA) | 0 (no sugerido), 1 (sugerido) |

**Proceso match:** Aplica al proceso `FBM-Retiro de Stock` dentro de FBM Sellers.

**CDU match:** Aplica a todos los CDUs del proceso (`_TODOS`).

**Caso de uso típico:**  
"Quiero ver el CR de FBM-Retiro de Stock sobre cantidad de requests de retiro en MLA, no sobre órdenes con FBM"

---

### 4. Moderaciones > (Todos los procesos) > (Todos los CDUs)

#### `items_moderados` - Items Moderados (Cantidad de mod_event_id)

| Campo | Valor |
|-------|-------|
| **Label** | Items Moderados (Cantidad de mod_event_id) |
| **Tabla** | `meli-bi-data.SBOX_CX_BI_ADS_CORE.BT_MODERATIONS` |
| **Campo fecha** | `MONTH_ID` (partición mensual) |
| **Expresión de conteo** | `COUNT(DISTINCT mod_event_id)` |
| **Filtro por site** | Si (directo: `SIT_SITE_ID`) |
| **Tipo filtro site** | `direct` |
| **Sites disponibles** | MLA, MLB, MLM, MCO, MLC, MLU, MEC, MPE |
| **Driver estándar** | `COUNT(DISTINCT ORD_ORDER_ID)` (Órdenes por site) |

**Descripción:**  
Total de eventos de moderación únicos en el período. Solo considera primera moderación (`FLG_FIRST_MOD = true`). A más items moderados, más contactos potenciales en Moderaciones. Un aumento en órdenes NO explica la variación de Moderaciones; este driver refleja el volumen real de acciones de moderación.

**Filtros base (siempre aplicados):**

| Filtro | Condición | Razón |
|--------|-----------|-------|
| `FLG_FIRST_MOD` | `= true` | Solo primera moderación de cada item |
| `SIT_SITE_ID` | `<> 'MLV'` | Excluir MLV (exclusión global) |

**Clasificaciones disponibles:**

| Clasificación | Descripción | Valores |
|--------------|-------------|---------|
| `FILTER_GROUP` | Grupo de filtro original | PI, DP, AP, TP |
| `FILTER_GROUP_CX` | Grupo CX (separa calidad foto de TP) | PI (Propiedad Intelectual), DP (Datos Personales), AP (Artículos Prohibidos), TP (Técnica Prohibida sin foto), PQ (Calidad de Foto) |
| `FILTER_GROUP_CX3` | Sub-agrupación granular | Calidad de Foto, Mal Categorizado, Duplicados, Labels, Evasion, Out of Topic, Contenido Sensible, Otros TP |
| `FLG_CBT` | Flag Cross-Border Trade | Valores dinámicos |
| `FILTER_NAME` | Nombre individual de filtro de moderación | Valores dinámicos |

**Proceso match:** Aplica a todos los procesos dentro de Moderaciones (`_TODOS`).

**CDU match:** Aplica a todos los CDUs (`_TODOS`).

**Nota sobre temporalidad:** `MONTH_ID` es partición mensual, por lo que el gráfico de tendencia es MENSUAL (no semanal). Se muestran 12 meses de historia.

**Caso de uso típico:**  
"Quiero ver el CR de Moderaciones sobre cantidad de items moderados en MLA, no sobre órdenes"

---

## Referencia Técnica

### Estructura del archivo de configuración

```
DRIVERS_ALTERNATIVOS = {
    'Commerce Group': {
        'driver_estandar_ref': '...',          # Referencia al driver estándar
        'procesos': {
            'Proceso': {
                'cdus': {
                    'CDU': {
                        'alternativas': {
                            'driver_key': {
                                'label': '...',
                                'description': '...',
                                'tabla_fuente': '...',
                                'fecha_field': '...',
                                'count_expression': '...',
                                'filter_by_site': True/False,
                                'sites_disponibles': [...],
                                'query_driver': '...',       # Query P1/P2
                                'query_driver_semanal': '...', # Query semanal
                                'query_detalle': '...',      # Query con clasificaciones
                                'clasificaciones': {...},    # Metadata de clasificaciones
                                'notas': '...'
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### Funciones disponibles

| Función | Uso |
|---------|-----|
| `listar_drivers_disponibles(cg)` | Lista todos los drivers alternativos (opcionalmente por CG) |
| `get_drivers_alternativos(cg, proceso, cdu)` | Retorna alternativas para una combinación |
| `get_driver_alternativo(cg, proc, cdu, key)` | Retorna config de un driver específico |
| `build_driver_query(...)` | Construye query SQL del driver con parámetros |
| `build_detail_query(...)` | Construye query SQL de detalle con clasificaciones |
| `build_weekly_query(...)` | Construye query SQL semanal para gráficos |

### Ejemplo de uso

```python
from config.drivers_alternativos import build_driver_query, listar_drivers_disponibles

# Ver qué hay disponible
for d in listar_drivers_disponibles():
    print(f"{d['commerce_group']} > {d['proceso']} > {d['cdu']} > {d['label']}")

# Construir query
query = build_driver_query(
    commerce_group='ME PreDespacho',
    proceso='Reputación ME',
    cdu='HT Colecta',
    driver_key='paradas_colecta',
    p1_start='2025-12-01', p1_end='2025-12-31',
    p2_start='2026-01-01', p2_end='2026-01-31',
    site='MLA'
)
```

---

## Agregar un nuevo driver alternativo

Para agregar un nuevo driver, añadir una entrada en `DRIVERS_ALTERNATIVOS` en `config/drivers_alternativos.py` siguiendo la estructura existente:

1. Ubicar (o crear) el Commerce Group
2. Ubicar (o crear) el Proceso
3. Ubicar (o crear) el CDU
4. Agregar la alternativa con su key, queries y metadata
5. Agregar aliases en `DRIVER_ALT_ALIASES` si corresponde
6. Actualizar este documento con el nuevo driver

---

## Referencias

- **Drivers estándar:** `config/drivers_mapping.py`
- **Drivers por categoría:** `docs/DRIVERS_BY_CATEGORY.md`
- **Drivers Shipping:** `docs/SHIPPING_DRIVERS.md`
- **Script principal:** `generar_reporte_cr_universal_v6.3.6.py`

---

**Versión:** 1.3  
**Changelog:**
- v1.3 (Feb 2026): Agregado driver Items Moderados para Moderaciones. Tabla BT_MODERATIONS, partición mensual. Clasificaciones: FILTER_GROUP_CX (PI/DP/AP/TP/PQ), FILTER_GROUP_CX3 (sub-agrupación granular), FLG_CBT, FILTER_NAME
- v1.2 (Feb 2026): Agregado driver Requests de Retiro de Stock para FBM Sellers > FBM-Retiro de Stock. Filtro directo por SIT_SITE_ID. Clasificaciones: TIPO_LOGISTICO, SEGMENTO, flag_sugerido
- v1.1 (Feb 2026): Agregado driver Inbounds para FBM Sellers (CDUs con INBOUND). Soporte para site via warehouse_prefix
- v1.0 (Feb 2026): Primera versión con driver de Paradas de Colecta para ME PreDespacho > Reputación ME > HT Colecta
