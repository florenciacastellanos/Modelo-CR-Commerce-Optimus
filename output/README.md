# 📊 Output - Reportes Generados

**Versión:** 3.9  
**Fecha:** Enero 2026  
**Status:** ✅ Estructura Oficial

---

## 🎯 Propósito

Esta carpeta contiene **todos los reportes generados** por el framework de análisis de Contact Rate, organizados por tipo y commerce group.

**Filosofía de Reportes:**
- ✅ **Datos 100% dinámicos** (Regla 14 - sin hardcoding)
- ✅ **Estructura estandarizada** por tipo de reporte
- ✅ **Trazabilidad completa** (metadata en footer)
- ✅ **Versionamiento selectivo** (solo ejemplos en git)

---

## 📂 Estructura

```
output/
├── rca/                         # Root Cause Analysis
│   ├── post-compra/
│   │   ├── pdd/                # Producto Dañado/Defectuoso
│   │   ├── pnr/                # Producto No Recibido
│   │   └── pcf/                # Post Compra Funcionalidades
│   ├── marketplace/
│   │   ├── pre-venta/          # Consultas pre-venta
│   │   ├── post-venta/         # Soporte post-venta
│   │   ├── generales-compra/   # Consultas generales
│   │   ├── moderaciones/       # Moderaciones y Prustomer
│   │   ├── full-sellers/       # Full Sellers
│   │   └── pagos/              # Pagos y transacciones
│   ├── shipping/               # Shipping (ME, FBM, Drivers)
│   ├── pagos/                  # MP On
│   └── cuenta/                 # Gestión de cuenta
│
├── cr/                          # Contact Rate Reports (Métricas)
│   ├── cross-site/             # Análisis multi-site
│   └── single-site/            # Análisis por site individual
│
└── examples/                    # 🌟 Ejemplos de Referencia (Golden)
    ├── rca_reference.html      # Template RCA de referencia
    ├── cr_cross_site_reference.html
    └── cr_single_site_reference.html
```

---

## 📋 Tipos de Reportes

### **1. RCA (Root Cause Analysis)** 🔍

**Objetivo**: Análisis profundo de variaciones con causas raíz extraídas de conversaciones.

**Componentes Obligatorios:**
1. ✅ **8 Cards Ejecutivas**
   - Inc Mes 1, Inc Mes 2
   - Drv Mes 1, Drv Mes 2
   - CR Mes 1 (pp), CR Mes 2 (pp)
   - Var Inc, Var CR (pp)

2. ✅ **Eventos Comerciales**
   - 2-3 eventos relevantes por site/período
   - Descripción + Impacto esperado
   - Correlación con variaciones

3. ✅ **Gráfico Semanal CR**
   - Chart.js interactivo
   - Mínimo 8 semanas
   - Tendencia visualizada

4. ✅ **Tabla Detallada Collapsible**
   - Por dimensión (Proceso/CDU/Tipificación)
   - Insights contextuales por fila
   - Top 80% de variación

5. ✅ **Causas Raíz**
   - Análisis de summaries (BT_CX_STUDIO_SAMPLE)
   - Keywords contextuales (no solo menciones)
   - Detección de cambios significativos (>10pp)
   - Top 2 problemáticas identificadas

6. ✅ **Casos de Ejemplo**
   - 3 casos por dimensión
   - Case ID + CDU/Tipificación
   - Summary completo (200-250 chars)

7. ✅ **Footer con Metadata**
   - Valores 100% calculados dinámicamente
   - Muestra (N casos por dimensión-mes)
   - Timestamp de generación

**Muestra mínima:** 100 casos por dimensión-mes

**Ejemplo:** `rca-preventa-cdu-mlb-nov-dic-2025.html`

---

### **2. CR (Contact Rate Reports)** 📈

**Objetivo**: Métricas de Contact Rate con tablas de variación estándar.

**Componentes:**
- Resumen ejecutivo
- Tabla de variación por dimensión
- Totales y agregaciones
- Sin análisis de causas raíz

**Subtipos:**

#### **2.1 Cross Site**
Consolida múltiples sites (MLA, MLB, MLC, MCO, MLM, MLU, MPE).

**3 Tablas:**
1. Por Proceso (sin site)
2. Por Site (sin procesos)
3. Detalle (Proceso × Site)

**Ejemplo:** `cr-pdd-cross-site-nov-dic-2025.html`

#### **2.2 Single Site**
Análisis de un único site con apertura por proceso y CDU.

**Ejemplo:** `cr-pdd-mla-nov-dic-2025.html`

---

## 🏷️ Nomenclatura de Archivos

### **RCA:**
```
rca-{commerce-group}-{dimension}-{site}-{mes1}-{mes2}-{year}.html
```

**Ejemplos:**
- `rca-pdd-proceso-mlb-nov-dic-2025.html`
- `rca-preventa-cdu-mla-sep-oct-2025.html`
- `rca-pnr-tipificacion-mlc-nov-dic-2025.html`

### **CR:**
```
cr-{commerce-group}-{type}-{site}-{mes1}-{mes2}-{year}.html
```

**Ejemplos:**
- `cr-pdd-cross-site-nov-dic-2025.html`
- `cr-pcf-single-site-mla-sep-oct-2025.html`

---

## 🌟 Golden Templates - Modelos Oficiales

**Propósito:** Reportes de referencia validados que sirven como estructura oficial para cada commerce group.

### **Post-Compra - PNR (Modelo Oficial)** ⭐
**Archivo:** `output/rca/post-compra/pnr/golden-pnr-mlb-nov-dic-2025.html`  
**Status:** ✅ Golden Template v3.9  
**Validado:** Enero 2026

**Características:**
- ✅ Drivers totales GLOBALES (todos los sites)
- ✅ Incoming filtrado por site específico
- ✅ Análisis por tipificación (`REASON_DETAIL_GROUP_REPORTING`)
- ✅ Fallback automático a `PROCESS_NAME` si solo 1 tipificación
- ✅ Correlación real con eventos (basada en `ORD_CLOSED_DT`)
- ✅ 100 casos/muestra por dimensión-período (mín 80)
- ✅ Keywords contextuales en español/portugués
- ✅ Análisis de cambios significativos (>10pp)
- ✅ Gráfico semanal (14 semanas mínimo)
- ✅ Footer técnico completo

**Uso como Base:**
- Todos los reportes de PNR deben seguir esta estructura
- Script generador: `generar_golden_pnr_mlb.py`
- Aplicable a todos los sites ajustando eventos comerciales

### **Post-Compra - PDD (Modelo Oficial)** ⭐
**Archivo:** `output/rca/post-compra/pdd/golden-pdd-mla-nov-dic-2025.html`  
**Status:** ✅ Golden Template v3.9  
**Validado:** Enero 2026

**Características:**
- ✅ Misma estructura que PNR Golden
- ✅ Adaptado para PDD (`Conflict Others` → PDD mapping)
- ✅ Eventos comerciales argentinos
- ✅ Keywords en español para MLA

**Uso como Base:**
- Todos los reportes de PDD deben seguir esta estructura
- Script generador: `generar_golden_pdd_mla.py`

### **Carpeta `/examples` - Referencias Adicionales**

**Contenido:**
- Mejores reportes generados (validados)
- Estructura completa y correcta
- Referencia para nuevos scripts
- **SÍ se commitean al git** (a diferencia de outputs temporales)

**Referencias en Documentación:**
- `docs/GOLDEN_TEMPLATES.md` → documentación de estructura golden
- `docs/RCA_STRUCTURE.md` → referencia estructura RCA
- Script base: `generar_golden_pnr_mlb.py`, `generar_golden_pdd_mla.py`

---

## 🔄 Ciclo de Vida de Reportes

### **Generación**
```python
# Script ejecuta query, analiza data, genera HTML
python generar_rca_preventa_MLB.py

# Output: output/rca/marketplace/pre-venta/rca-preventa-cdu-mlb-nov-dic-2025.html
```

### **Validación**
- Revisar estructura completa
- Validar datos con BigQuery
- Confirmar insights contextuales

### **Ejemplo (Si es perfecto)**
```bash
# Promover a example si es un template golden
cp output/rca/marketplace/pre-venta/rca-preventa-cdu-mlb-nov-dic-2025.html \
   output/examples/rca_marketplace_reference.html
```

### **Retención**
- ✅ Examples: **Permanentes** (commiteados)
- ⚠️ Outputs: **Temporales** (gitignored)
- 🗑️ Limpieza: Manual según necesidad

---

## 🚫 .gitignore

Los reportes temporales **NO se commitean** al git:

```gitignore
# Outputs temporales
output/rca/**/*.html
output/cr/**/*.html

# EXCEPCIONES: Mantener ejemplos
!output/examples/**
!output/**/README.md
```

**Razón:** Los reportes pueden ser muy grandes y se regeneran fácilmente.

---

## 📊 Estructura de Salida por Commerce Group

### **Post-Compra**
| Commerce Group | Carpeta | Dimensiones Típicas |
|----------------|---------|---------------------|
| PDD | `rca/post-compra/pdd/` | Proceso, CDU, Tipificación |
| PNR | `rca/post-compra/pnr/` | Proceso, CDU, Tipificación |
| PCF | `rca/post-compra/pcf/` | Proceso, CDU |

### **Marketplace**
| Commerce Group | Carpeta | Dimensiones Típicas |
|----------------|---------|---------------------|
| Pre Venta | `rca/marketplace/pre-venta/` | Proceso, CDU |
| Post Venta | `rca/marketplace/post-venta/` | Proceso, CDU |
| Generales Compra | `rca/marketplace/generales-compra/` | Proceso, CDU |
| Moderaciones | `rca/marketplace/moderaciones/` | Proceso, CDU |
| Full Sellers | `rca/marketplace/full-sellers/` | Proceso, CDU |
| Pagos | `rca/marketplace/pagos/` | Proceso, CDU |

### **Shipping**
| Commerce Group | Carpeta | Driver Específico |
|----------------|---------|-------------------|
| ME Distribución | `rca/shipping/` | OS_TOTALES |
| ME PreDespacho | `rca/shipping/` | OS_WO_FULL |
| FBM Sellers | `rca/shipping/` | OS_FULL |
| ME Drivers | `rca/shipping/` | - |

### **Otros**
| Commerce Group | Carpeta | Notas |
|----------------|---------|-------|
| MP On | `rca/pagos/` | Mercado Pago Online |
| Cuenta | `rca/cuenta/` | Gestión de cuenta |
| Experiencia Impositiva | `rca/cuenta/` | - |

---

## 🎨 Componentes de Reportes RCA

### **Resumen Ejecutivo (Cards)**
```html
<div class="cards-grid">
    <!-- 8 cards con métricas clave -->
    Inc Nov, Inc Dic, Drv Nov, Drv Dic, CR Nov, CR Dic, Var Inc, Var CR
</div>
```

### **Eventos Comerciales**
```html
<div class="eventos-box">
    <h3>Eventos Comerciales Nov-Dic 2025</h3>
    <div class="evento">
        <div class="evento-nombre">Black Friday (29 Nov)</div>
        <div class="evento-desc">Descripción + Impacto esperado</div>
    </div>
    <!-- Más eventos... -->
</div>
```

### **Tabla con Insights**
```html
<table>
    <tr onclick="toggle('d1')">
        <td>Dimensión</td><td>Nov</td><td>Dic</td><td>Var</td><td>%</td>
    </tr>
    <tr class="detail" id="d1">
        <td colspan="5">
            <div class="insight-box">
                <div class="insight-text">
                    Cambio significativo: custos de frete aumentou de 10.0% (Nov) 
                    para 23.3% (Dez) = +13.3 pp. Correlaciona com Black Friday...
                </div>
            </div>
            <div class="casos">
                <!-- 3 casos de ejemplo con summaries -->
            </div>
        </td>
    </tr>
</table>
```

### **Gráfico Semanal**
```html
<div class="chart-container">
    <canvas id="ch" height="70"></canvas>
</div>
<script>
    // Chart.js con CR semanal
</script>
```

---

## 📖 Referencias

- **Estructura RCA**: `docs/RCA_STRUCTURE.md` (próximamente)
- **Templates**: `templates/rca_template.html` (próximamente)
- **Reglas**: `.cursorrules` → Regla 14 (No Hardcoding), Regla 15 (RCA Structure)
- **Ejemplos**: `output/examples/`

---

## 🚀 Próximos Pasos

1. ✅ Estructura de carpetas creada
2. ⏳ Crear `docs/RCA_STRUCTURE.md`
3. ⏳ Crear `templates/rca_template.html`
4. ⏳ Actualizar `.cursorrules` con Regla 15
5. ⏳ Generar primer example golden para cada commerce group

---

**Última actualización:** Enero 2026  
**Mantenedor:** Framework CR - Mercado Libre
