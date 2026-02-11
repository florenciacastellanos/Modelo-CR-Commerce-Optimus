# 📊 Contexto de Negocio - Contact Rate Analysis

## ¿Qué es Contact Rate (CR)?

**Contact Rate** es la métrica principal que mide la tasa de contactos de clientes respecto a un driver de negocio.

### Fórmula

```
Contact Rate (CR) = (Incoming Cases / Driver) × 100
```

**Resultado:** Porcentaje de eventos que generan un contacto con el área de soporte.

### Ejemplo Práctico

```
Incoming Cases: 150 (clientes que contactaron)
Driver: 10,000 (órdenes totales)
CR = (150 / 10,000) × 100 = 1.5 pp (puntos porcentuales)
```

**Interpretación:** De cada 100 órdenes, 1.5 generan un contacto de soporte.

## Componentes Clave

### 1. Incoming Cases (Numerador)

**Definición:** Casos reportados por clientes que llegan al sistema de soporte.

**Fuentes:**
- `BT_CX_INCOMING_CR`: Casos incoming sin conflicto
- `BT_CX_CLAIMS_CR`: Casos de claims/conflictos

**Condiciones:**
- `FLAG_EXCLUDE_NUMERATOR_CR = 0` (incluir en CR)
- No estar en queues excluidas
- No estar en processes excluidos
- No tener CI_REASON_ID excluidos

### 2. Driver (Denominador)

**Definición:** Métrica de negocio que representa el volumen de eventos susceptibles de generar contactos.

**Ejemplos según Commerce Group:**
- **PDD/PNR:** Órdenes cerradas
- **ME Distribución:** Shipments entregados
- **Pre Venta:** Listados activos
- **Pagos:** Transacciones procesadas
- **Cuenta:** Usuarios activos

**Configuración:**
- Los drivers se configuran manualmente por Site y Periodo
- Cada Commerce Group puede tener su propio driver
- Sin driver configurado, no se puede calcular CR

## Commerce Groups

El análisis se organiza en **15 Commerce Groups** agrupados en **5 categorías**:

### 📦 Post-Compra (2 groups)

#### PDD - Producto Dañado/Defectuoso
- **Descripción:** Productos que llegan en mal estado o defectuosos
- **Driver típico:** Órdenes cerradas
- **Impacto:** Alto (afecta satisfacción directa)
- **Keywords:** Dañado, Defectuoso, Roto, Mal estado, Others

#### PNR - Producto No Recibido
- **Descripción:** Productos reportados como no entregados
- **Driver típico:** Órdenes cerradas
- **Impacto:** Alto (pérdida de confianza)
- **Keywords:** No recibido, Extraviado, Perdido, Stale

### 🚛 Shipping (4 groups)

#### ME Distribución
- **Descripción:** Distribución de envíos vista desde Comprador
- **User Type:** Comprador
- **Driver típico:** Shipments entregados
- **Keywords:** Mercado Envíos + Comprador

#### ME PreDespacho
- **Descripción:** Pre-despacho de envíos vista desde Vendedor
- **User Type:** Vendedor
- **Driver típico:** Shipments despachados
- **Keywords:** Mercado Envíos + Vendedor

#### FBM Sellers
- **Descripción:** Fulfillment by Mercado Libre (Sellers)
- **User Type:** Vendedor
- **Driver típico:** Órdenes FBM
- **Keywords:** FBM Sellers

#### ME Drivers
- **Descripción:** Drivers de Mercado Envíos
- **User Type:** Driver
- **Driver típico:** Envíos asignados
- **Keywords:** PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers')

### 🛒 Marketplace (6 groups)

#### Pre Venta
- **Descripción:** Consultas antes de la compra
- **Driver típico:** Listados activos
- **Keywords:** PreVenta

#### Post Venta
- **Descripción:** Soporte después de la compra
- **Driver típico:** Órdenes cerradas
- **Keywords:** PostVenta

#### Generales Compra
- **Descripción:** Consultas generales sobre proceso de compra
- **Driver típico:** Transacciones
- **Keywords:** Post Compra, Compra, Redes

#### Moderaciones
- **Descripción:** Moderaciones de contenido y Prustomer
- **Driver típico:** Publicaciones moderadas
- **Keywords:** Prustomer, Moderaciones

#### Full Sellers
- **Descripción:** Sellers con fulfillment completo
- **Driver típico:** Órdenes Full
- **Keywords:** Full Sellers

#### Pagos
- **Descripción:** Pagos y transacciones en Marketplace
- **Driver típico:** Transacciones
- **Keywords:** Pagos

### 💳 Pagos (1 group)

#### MP On
- **Descripción:** Mercado Pago Online
- **Driver típico:** Transacciones MP
- **Keywords:** MP Payer, MP On

### 👤 Cuenta (2 groups)

#### Cuenta
- **Descripción:** Gestión de cuenta y seguridad
- **Driver típico:** Usuarios activos
- **Keywords:** Seguridad 360

#### Experiencia Impositiva
- **Descripción:** Gestión impositiva y fiscal
- **Driver típico:** Usuarios con actividad fiscal
- **Keywords:** Experiencia Impositiva

## Lógica de Asignación (AGRUP_COMMERCE)

La asignación a Commerce Groups sigue esta jerarquía en SQL:

```sql
CASE
    -- 1. POST-COMPRA (mayor prioridad)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' THEN 'PNR'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
    
    -- 2. SHIPPING - por User Type
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'ME Distribución'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'ME PreDespacho'
    WHEN PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
    
    -- 3. MARKETPLACE
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PreVenta%' THEN 'Pre Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PostVenta%' THEN 'Post Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' THEN 'Moderaciones'
    
    -- 4. PAGOS
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' THEN 'MP On'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' THEN 'Pagos'
    
    -- 5. CUENTA
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Seguridad 360%' THEN 'Cuenta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Experiencia Impositiva%' THEN 'Experiencia Impositiva'
    
    -- 6. DEFAULT
    ELSE 'Generales Compra'
END AS AGRUP_COMMERCE
```

## Segmentos de Usuario

### 3 User Types principales:

| User Type | % Casos | Descripción | SQL Value |
|-----------|---------|-------------|-----------|
| **COMPRADOR** | ~70% | Usuarios que compran | 'Comprador' |
| **VENDEDOR** | ~25% | Usuarios que venden | 'Vendedor' |
| **CUENTA** | ~5% | Gestión de cuenta | 'Cuenta' |

**Nota:** Drivers ('Driver', 'Drivers') se incluyen automáticamente.

## Environments (Ambientes Logísticos)

6 Environments disponibles:

| Environment | Descripción | Caso de Uso |
|-------------|-------------|-------------|
| **DS** | Drop Shipping | Envío directo desde vendedor |
| **FBM** | Fulfillment by ML | Fulfillment por Mercado Libre |
| **FLEX** | Flex Logistics | Logística flexible |
| **XD** | Cross Docking | Cross docking |
| **MP_ON** | Mercado Pago Online | Pagos online |
| **MP_OFF** | Mercado Pago Offline | Pagos offline |

## Dimensiones de Análisis

El sistema permite analizar CR por **8 dimensiones**:

### 1. PROCESS (Process Name)
- **Campo:** `PROCESS_NAME`
- **Descripción:** Nombre específico del proceso
- **Threshold:** 100 casos
- **Ejemplo:** "Reclamo por PDD", "Consulta de envío"

### 2. CDU (Caso de Uso)
- **Campo:** `CDU`
- **Descripción:** Caso de uso del contacto
- **Threshold:** 100 casos
- **Ejemplo:** "Reclamo", "Consulta", "Soporte"

### 3. REASON_DETAIL (Reason Detail Group)
- **Campo:** `REASON_DETAIL_GROUP_REPORTING`
- **Descripción:** Motivo detallado del contacto
- **Threshold:** 100 casos
- **Ejemplo:** "Producto dañado", "Retraso en entrega"

### 4. COMMERCE_GROUP
- **Campo:** `AGRUP_COMMERCE`
- **Descripción:** Agrupación de Commerce
- **Threshold:** 100 casos
- **Valores:** 15 Commerce Groups

### 5. REPORTING_TYPE
- **Campo:** `PROBLEMATIC_REPORTING`
- **Descripción:** Tipo de reporte problematic
- **Threshold:** 100 casos

### 6. ENVIRONMENT
- **Campo:** `ENVIRONMENT`
- **Descripción:** Ambiente logístico
- **Threshold:** 100 casos
- **Valores:** DS, FBM, FLEX, XD, MP_ON, MP_OFF

### 7. VERTICAL
- **Campo:** `VERTICAL`
- **Descripción:** Vertical de negocio
- **Threshold:** 100 casos
- **Estado:** ⚠️ Actualmente NULL (tabla pendiente)

### 8. DOMAIN
- **Campo:** `DOM_DOMAIN_AGG1`
- **Descripción:** Dominio agregado nivel 1
- **Threshold:** 100 casos
- **Estado:** ⚠️ Actualmente NULL (tabla pendiente)

## Sites (Países)

7 Sites disponibles:

| Site | País | Volumen | Consideraciones |
|------|------|---------|-----------------|
| **MLA** | Argentina | Alto | Principal mercado |
| **MLB** | Brasil | Muy Alto | ⚠️ Requiere sampling |
| **MLC** | Chile | Medio | - |
| **MCO** | Colombia | Medio | - |
| **MLM** | México | Alto | - |
| **MLU** | Uruguay | Bajo | - |
| **MPE** | Perú | Medio | - |

**Excluido:** MLV (Venezuela)

## Exclusiones Automáticas

### Queues Excluidas
**IDs:** 2131, 230, 1102, 1241, 2075, 2294, 2295

**Razón:** Queues de testing, desarrollo o fuera de scope.

### Processes Excluidos
**IDs:** 1312

**Razón:** Procesos internos o administrativos.

### CI Reasons Excluidos
**IDs:** 2592, 6588, 10068, 2701, 10048

**Razón:** Razones de contacto no relevantes para CR.

### Flags
- `FLAG_EXCLUDE_NUMERATOR_CR = 0` (incluir en CR)
- `FLAG_EXCLUDE_NUMERATOR_HR = 0` (opcional, para HR)

### BU (Business Unit)
**Incluidos:** 'ME', 'ML'

**Excluidos:** Otros BUs fuera de Commerce.

## Umbrales y Constantes

### Threshold de Casos
- **Default:** 100 casos mínimos
- **Razón:** Significancia estadística
- **Personalizable:** Sí, por dimensión

### Contact Rate
- **Multiplier:** 100 (conversión a pp)
- **Decimales:** 4
- **Rango esperado:** 0.5 - 15.0 pp

### Variaciones
- **Strong Variation:** ±20% MoM
- **Spike Threshold:** 150% del promedio
- **Drop Threshold:** 50% del promedio

### Sampling (MLB)
- **Threshold:** 150,000 filas estimadas
- **Min Limit:** 150,000 filas
- **Max Limit:** 200,000 filas
- **Método:** Systematic sampling por AGRUP × Mes

### Memory Optimization
- **Threshold:** 50,000 filas
- **Acciones:** Downcast tipos, categorizar strings
- **Saving esperado:** 50-70% memoria

## Periodos de Análisis

### Formatos Soportados

#### Monthly (por mes)
- **Formato:** YYYY-MM
- **Ejemplo:** 2026-01 (Enero 2026)
- **Uso:** Análisis mes a mes

#### Quarterly (por trimestre)
- **Formato:** Q{1-4}-YYYY
- **Ejemplo:** Q1-2026 (Enero-Marzo 2026)
- **Uso:** Análisis trimestral

### Detección Automática
El sistema detecta automáticamente periodos completos entre fechas inicio y fin.

## Análisis de Variaciones

### Variación Absoluta (pp)
```
Variación = CR_actual - CR_anterior
```

**Ejemplo:**
- CR Enero: 5.2 pp
- CR Febrero: 6.8 pp
- Variación: +1.6 pp

### Variación Relativa (%)
```
Variación % = ((CR_actual - CR_anterior) / CR_anterior) × 100
```

**Ejemplo:**
- CR Enero: 5.2 pp
- CR Febrero: 6.8 pp
- Variación %: +30.8%

### Impacto en Volumen
```
Impact = Variación_pp × Volumen_actual
```

**Ejemplo:**
- Variación: +1.6 pp
- Volumen actual: 10,000 órdenes
- Impact: +160 casos adicionales

## Patrones Detectables

### Spike (Pico)
- **Definición:** CR > 150% del promedio rolling
- **Indicador:** Aumento súbito anormal
- **Acción:** Investigar causa raíz

### Drop (Caída)
- **Definición:** CR < 50% del promedio rolling
- **Indicador:** Disminución súbita anormal
- **Acción:** Validar si es mejora real o problema de data

### Strong Variation
- **Definición:** Variación % > ±20% MoM
- **Indicador:** Cambio significativo mes a mes
- **Acción:** Analizar drivers de variación

### Concentration
- **Definición:** 30% del volumen en días críticos
- **Indicador:** Concentración temporal anormal
- **Acción:** Investigar eventos específicos

## Workflow de Análisis

### Paso 1: Configuración
1. Seleccionar **Sites** (países)
2. Seleccionar **Commerce Groups**
3. Seleccionar **User Types** (opcional)
4. Seleccionar **Environments** (opcional)
5. Definir **periodo** (start_date, end_date)

### Paso 2: Extracción de Datos
1. Ejecutar **base-query.sql**
2. Aplicar filtros
3. Calcular AGRUP_COMMERCE
4. Agregar por dimensión seleccionada

### Paso 3: Configuración de Drivers
1. Por cada **Site**
2. Por cada **Periodo detectado**
3. Configurar **Driver value** manualmente

### Paso 4: Cálculo de CR
```python
CR = (Incoming / Driver) × 100
```

### Paso 5: Análisis de Variaciones
1. Calcular variación absoluta (pp)
2. Calcular variación relativa (%)
3. Calcular impacto en volumen
4. Detectar patrones (spikes, drops, etc.)

### Paso 6: Interpretación
1. Identificar **top drivers** de variación
2. Analizar **distribución temporal**
3. Comparar con **periodos anteriores**
4. Generar **insights accionables**

## Consideraciones Especiales

### MLB (Brasil)
- **Problema:** Volumen extremadamente alto
- **Solución:** Sampling sistemático
- **Configuración:** Ver `/sql/sampling-strategy.sql`
- **Threshold:** 150,000 filas estimadas

### Vertical & Domain
- **Estado:** NULL actualmente
- **Razón:** Tabla source no identificada
- **Impact:** Dimensiones 7 y 8 no disponibles
- **Solución:** Pendiente identificar tabla

### Memory Management
- **Trigger:** Datasets > 50,000 filas
- **Acción:** Optimización automática
- **Resultado:** 50-70% reducción memoria
- **Código:** Ver `/utils/memory-optimization.py`

### Date Formats
- **SQL:** YYYY-MM-DD (string)
- **Display:** Month YYYY o Q# YYYY
- **Parsing:** Automático por sistema

## Métricas Secundarias

### Incoming No Conflict
```sql
CASE WHEN ORIGIN_TABLE = 'BT_CX_INCOMING_CR' THEN 1.0 ELSE 0.0 END
```

### Incoming Conflict
```sql
CASE WHEN ORIGIN_TABLE = 'BT_CX_CLAIMS_CR' THEN 1.0 ELSE 0.0 END
```

### Flag Auto
```sql
FLAG_AUTO (0 = Manual, 1 = Automático)
```

### Cant Cases
```sql
1.0 por cada registro (para agregaciones)
```

## Referencias

- **Queries:** Ver `/sql/base-query.sql`
- **Cálculos:** Ver `/calculations/contact-rate.py`
- **Constantes:** Ver `/config/business-constants.py`
- **Tablas:** Ver `/docs/table-definitions.md`
- **Workflow:** Ver `/docs/analysis-workflow.md`

---

**Última actualización:** Enero 2026  
**Versión:** 2.5 (Commerce)  
**Source:** V37.ipynb
