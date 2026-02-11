# 🏢 Estructura de Commerce Groups

## Visión General

El sistema de Contact Rate organiza los contactos en **15 Commerce Groups** distribuidos en **5 categorías** principales.

## Jerarquía Completa

```
COMMERCE STRUCTURE (15 Groups, 5 Categories)
│
├─── 📦 POST-COMPRA (2 groups)
│    ├── PDD - Producto Dañado/Defectuoso
│    └── PNR - Producto No Recibido
│
├─── 🚛 SHIPPING (4 groups)
│    ├── ME Distribución - Distribución de envíos (Comprador)
│    ├── ME PreDespacho - Pre-despacho de envíos (Vendedor)
│    ├── FBM Sellers - Fulfillment by Mercado Libre
│    └── ME Drivers - Drivers de Mercado Envíos
│
├─── 🛒 MARKETPLACE (6 groups)
│    ├── Pre Venta - Consultas pre-venta
│    ├── Post Venta - Soporte post-venta
│    ├── Generales Compra - Consultas generales de compra
│    ├── Moderaciones - Moderaciones y Prustomer
│    ├── Full Sellers - Full Sellers
│    └── Pagos - Pagos y transacciones (Marketplace)
│
├─── 💳 PAGOS (1 group)
│    └── MP On - Mercado Pago Online
│
└─── 👤 CUENTA (2 groups)
     ├── Cuenta - Gestión de cuenta y seguridad
     └── Experiencia Impositiva - Experiencia Impositiva
```

---

## Detalle por Categoría

### 📦 POST-COMPRA

**Descripción:** Problemas post-compra relacionados con calidad y entrega del producto.

**Volumen típico:** 25-35% del total

**Impacto:** Alto (satisfacción directa)

#### PDD - Producto Dañado/Defectuoso

**Icon:** 📦  
**Color:** `#dc2626` (rojo)

**Descripción:** Productos que llegan en mal estado, rotos o defectuosos.

**Keywords identificadores:**
- `PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%'`
- `PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others'`
- `PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%'`

**Driver típico:** Órdenes cerradas

**KPIs:**
- CR Target: < 2.0 pp
- CR Crítico: > 5.0 pp

**Causas comunes:**
- Empaque inadecuado
- Daño en transporte
- Producto defectuoso de fábrica
- Error en picking

#### PNR - Producto No Recibido

**Icon:** 🚚  
**Color:** `#f59e0b` (naranja)

**Descripción:** Productos reportados como no entregados o extraviados.

**Keywords identificadores:**
- `PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%'`
- `PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale'`

**Driver típico:** Órdenes cerradas

**KPIs:**
- CR Target: < 1.5 pp
- CR Crítico: > 4.0 pp

**Causas comunes:**
- Extravío en transporte
- Dirección incorrecta
- Robo
- Error en registro de entrega

---

### 🚛 SHIPPING

**Descripción:** Logística y distribución de envíos.

**Volumen típico:** 30-40% del total

**Impacto:** Alto (experiencia de entrega)

#### ME Distribución

**Icon:** 📦  
**Color:** `#14b8a6` (teal)

**Descripción:** Distribución de envíos desde perspectiva del Comprador.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
     AND PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'ME Distribución'

WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
     AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME Distribución'
```

**User Type:** Comprador

**Driver típico:** Shipments entregados

**KPIs:**
- CR Target: < 3.0 pp
- CR Crítico: > 8.0 pp

#### ME PreDespacho

**Icon:** 📤  
**Color:** `#06b6d4` (cyan)

**Descripción:** Pre-despacho de envíos desde perspectiva del Vendedor.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
     AND PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'ME PreDespacho'

WHEN PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
     AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME PreDespacho'
```

**User Type:** Vendedor

**Driver típico:** Shipments despachados

**KPIs:**
- CR Target: < 2.5 pp
- CR Crítico: > 6.0 pp

#### FBM Sellers

**Icon:** 🏪  
**Color:** `#0891b2` (teal oscuro)

**Descripción:** Fulfillment by Mercado Libre - Sellers.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
```

**User Type:** Vendedor

**Driver típico:** Órdenes FBM

**KPIs:**
- CR Target: < 2.0 pp
- CR Crítico: > 5.0 pp

#### ME Drivers

**Icon:** 🏍️  
**Color:** `#7c3aed` (púrpura)

**Descripción:** Drivers de Mercado Envíos (repartidores).

**Criterios de asignación:**
```sql
WHEN PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
```

**User Type:** Driver

**Driver típico:** Envíos asignados

**KPIs:**
- CR Target: < 1.0 pp
- CR Crítico: > 3.0 pp

---

### 🛒 MARKETPLACE

**Descripción:** Procesos de compra-venta en el marketplace.

**Volumen típico:** 25-35% del total

**Impacto:** Medio-Alto (experiencia de compra)

#### Pre Venta

**Icon:** 🔍  
**Color:** `#3b82f6` (azul)

**Descripción:** Consultas y dudas antes de realizar la compra.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PreVenta%' THEN 'Pre Venta'
```

**Driver típico:** Listados activos

**KPIs:**
- CR Target: < 1.5 pp
- CR Crítico: > 4.0 pp

#### Post Venta

**Icon:** 📞  
**Color:** `#2563eb` (azul oscuro)

**Descripción:** Soporte después de la compra (no relacionado con producto dañado/perdido).

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PostVenta%' THEN 'Post Venta'
```

**Driver típico:** Órdenes cerradas

**KPIs:**
- CR Target: < 2.0 pp
- CR Crítico: > 5.0 pp

#### Generales Compra

**Icon:** 🛍️  
**Color:** `#1d4ed8` (azul muy oscuro)

**Descripción:** Consultas generales sobre el proceso de compra.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%' THEN 'Generales Compra'
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Compra%' THEN 'Generales Compra'
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Redes%' THEN 'Generales Compra'
ELSE 'Generales Compra'  -- DEFAULT
```

**Driver típico:** Transacciones

**KPIs:**
- CR Target: < 2.5 pp
- CR Crítico: > 6.0 pp

#### Moderaciones

**Icon:** ⚖️  
**Color:** `#1e40af` (azul marino)

**Descripción:** Moderaciones de contenido y gestión de Prustomer.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' THEN 'Moderaciones'
```

**Driver típico:** Publicaciones moderadas

**KPIs:**
- CR Target: < 1.0 pp
- CR Crítico: > 3.0 pp

#### Full Sellers

**Icon:** 🏬  
**Color:** `#6d28d9` (púrpura)

**Descripción:** Sellers con fulfillment completo por Mercado Libre.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Full Sellers%' THEN 'Full Sellers'
```

**Driver típico:** Órdenes Full

**KPIs:**
- CR Target: < 1.5 pp
- CR Crítico: > 4.0 pp

#### Pagos (Marketplace)

**Icon:** 💳  
**Color:** `#ec4899` (rosa)

**Descripción:** Pagos y transacciones dentro del Marketplace.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' THEN 'Pagos'
```

**Driver típico:** Transacciones

**KPIs:**
- CR Target: < 1.0 pp
- CR Crítico: > 3.0 pp

---

### 💳 PAGOS

**Descripción:** Mercado Pago Online.

**Volumen típico:** 5-10% del total

**Impacto:** Alto (confianza financiera)

#### MP On

**Icon:** 💰  
**Color:** `#db2777` (rosa oscuro)

**Descripción:** Mercado Pago Online - transacciones digitales.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' THEN 'MP On'
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP Payer%' THEN 'MP On'
```

**Driver típico:** Transacciones MP

**KPIs:**
- CR Target: < 0.5 pp
- CR Crítico: > 2.0 pp

---

### 👤 CUENTA

**Descripción:** Gestión de cuenta de usuario.

**Volumen típico:** 5-10% del total

**Impacto:** Medio (experiencia de usuario)

#### Cuenta

**Icon:** 👤  
**Color:** `#64748b` (gris oscuro)

**Descripción:** Gestión de cuenta y seguridad (login, registro, configuración).

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Seguridad 360%' THEN 'Cuenta'
```

**Driver típico:** Usuarios activos

**KPIs:**
- CR Target: < 1.0 pp
- CR Crítico: > 3.0 pp

#### Experiencia Impositiva

**Icon:** 📄  
**Color:** `#475569` (gris muy oscuro)

**Descripción:** Gestión de aspectos fiscales e impositivos.

**Criterios de asignación:**
```sql
WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Experiencia Impositiva%' THEN 'Experiencia Impositiva'
```

**Driver típico:** Usuarios con actividad fiscal

**KPIs:**
- CR Target: < 0.5 pp
- CR Crítico: > 2.0 pp

---

## Lógica de Asignación (Orden de Prioridad)

La asignación a Commerce Groups sigue esta **jerarquía estricta** en SQL:

```sql
CASE
    -- 1️⃣ POST-COMPRA (máxima prioridad)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' THEN 'PNR'
    WHEN PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Others%' THEN 'PDD'
    
    -- 2️⃣ SHIPPING (segunda prioridad, diferenciado por User Type)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Comprador' THEN 'ME Distribución'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' 
         AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME Distribución'
         
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' 
         AND PROCESS_GROUP_ECOMMERCE = 'Vendedor' THEN 'ME PreDespacho'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' 
         AND PROCESS_BU_CR_REPORTING = 'ME' THEN 'ME PreDespacho'
    
    WHEN PROCESS_GROUP_ECOMMERCE IN ('Driver', 'Drivers') THEN 'ME Drivers'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM Sellers%' THEN 'FBM Sellers'
    
    -- 3️⃣ MARKETPLACE (tercera prioridad)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PreVenta%' THEN 'Pre Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%PostVenta%' THEN 'Post Venta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Redes%' THEN 'Generales Compra'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' THEN 'Moderaciones'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%' THEN 'Generales Compra'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Compra%' THEN 'Generales Compra'
    
    -- 4️⃣ PAGOS (cuarta prioridad)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' THEN 'Pagos'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP Payer%' THEN 'MP On'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' THEN 'MP On'
    
    -- 5️⃣ CUENTA (quinta prioridad)
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Seguridad 360%' THEN 'Cuenta'
    WHEN PROCESS_PROBLEMATIC_REPORTING LIKE '%Experiencia Impositiva%' THEN 'Experiencia Impositiva'
    
    -- 6️⃣ DEFAULT (si nada coincide)
    ELSE 'Generales Compra'
END AS AGRUP_COMMERCE
```

**Nota importante:** La prioridad importa. Si un caso cumple múltiples condiciones, se asigna al primer match.

---

## User Types por Commerce Group

| Commerce Group | User Types | Nota |
|----------------|------------|------|
| PDD | Comprador | Principal |
| PNR | Comprador | Principal |
| ME Distribución | Comprador | Exclusivo |
| ME PreDespacho | Vendedor | Exclusivo |
| FBM Sellers | Vendedor | Exclusivo |
| ME Drivers | Driver | Exclusivo |
| Pre Venta | Comprador | Principal |
| Post Venta | Comprador, Vendedor | Mixto |
| Generales Compra | Comprador, Vendedor, Cuenta | Mixto |
| Moderaciones | Vendedor | Principal |
| Full Sellers | Vendedor | Exclusivo |
| Pagos | Comprador, Vendedor | Mixto |
| MP On | Comprador, Vendedor | Mixto |
| Cuenta | Cuenta | Exclusivo |
| Experiencia Impositiva | Cuenta, Vendedor | Mixto |

---

## Configuración en Código

### Python (`/config/commerce-groups.py`)

```python
AVAILABLE_AGRUP_COMMERCE = [
    # Post-Compra
    'PDD', 'PNR',
    
    # Shipping
    'ME Distribución', 'ME PreDespacho', 'FBM Sellers', 'ME Drivers',
    
    # Marketplace
    'Pre Venta', 'Post Venta', 'Generales Compra', 'Moderaciones', 
    'Full Sellers', 'Pagos',
    
    # Pagos
    'MP On',
    
    # Cuenta
    'Cuenta', 'Experiencia Impositiva'
]

AGRUP_COMMERCE_INFO = {
    'PDD': {
        'label': 'PDD',
        'icon': '📦',
        'description': 'Producto Dañado/Defectuoso',
        'color': '#dc2626',
        'category': 'Post-Compra'
    },
    # ... (resto de configuración)
}

AGRUP_COMMERCE_CATEGORIES = {
    'Post-Compra': {
        'icon': '📦',
        'color': '#dc2626',
        'items': ['PDD', 'PNR']
    },
    # ... (resto de categorías)
}
```

---

## Análisis por Categoría

### Distribución Esperada

| Categoría | % Volumen | CR Promedio | Impacto |
|-----------|-----------|-------------|---------|
| Post-Compra | 25-35% | 3-5 pp | Alto |
| Shipping | 30-40% | 2-4 pp | Alto |
| Marketplace | 25-35% | 1-3 pp | Medio |
| Pagos | 5-10% | 0.5-1.5 pp | Alto |
| Cuenta | 5-10% | 0.5-1.5 pp | Medio |

---

## Referencias

- **Contexto de negocio:** `/docs/business-context.md`
- **Query principal:** `/sql/base-query.sql`
- **Configuración:** `/config/commerce-groups.py`
- **Métricas:** `/docs/metrics-glossary.md`

---

**Última actualización:** Enero 2026  
**Versión:** 2.5 (Commerce)  
**Source:** V37.ipynb
