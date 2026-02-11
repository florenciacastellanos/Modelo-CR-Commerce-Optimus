# 🌟 Examples - Golden Templates de Referencia

**Propósito:** Mantener ejemplos validados de reportes que sirven como estructura "golden" para nuevos scripts.

---

## 📋 Contenido

Esta carpeta contiene **reportes de referencia perfectos** que cumplen con la estructura oficial y sirven como guía para:

1. ✅ Nuevos scripts de análisis
2. ✅ Validación de estructura
3. ✅ Documentación visual
4. ✅ Onboarding de nuevos usuarios

---

## 🎯 Tipos de Examples

### **RCA (Root Cause Analysis)**

| Archivo | Commerce Group | Descripción |
|---------|----------------|-------------|
| `rca_reference.html` | General | Template RCA completo (todos los componentes) |
| `rca_pdd_reference.html` | Post-Compra (PDD) | Ejemplo PDD con análisis de daños |
| `rca_preventa_reference.html` | Marketplace (Pre Venta) | Ejemplo Pre Venta con publicaciones |

### **CR (Contact Rate Reports)**

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `cr_cross_site_reference.html` | Cross Site | 3 tablas consolidadas |
| `cr_single_site_reference.html` | Single Site | Análisis por site con CDU |

---

## ✅ Criterios de un "Golden Template"

Para que un reporte sea promovido a example, debe cumplir:

### **Estructura Completa**
- ✅ Header con metadata
- ✅ Cards ejecutivas (8 para RCA, 4 para CR)
- ✅ Eventos comerciales (RCA)
- ✅ Gráfico semanal (RCA)
- ✅ Tabla detallada con datos reales
- ✅ Insights contextuales (RCA)
- ✅ Casos de ejemplo (RCA)
- ✅ Footer con metadata técnica

### **Calidad de Datos**
- ✅ Valores 100% calculados dinámicamente
- ✅ Muestra representativa (≥100 casos por dimensión-mes)
- ✅ Insights no genéricos
- ✅ Correlación explícita con eventos

### **UX/UI**
- ✅ CSS optimizado
- ✅ Responsive design
- ✅ Elementos interactivos funcionando
- ✅ Colores según commerce group

### **Metadata**
- ✅ Timestamp de generación
- ✅ Versión del framework
- ✅ Fuentes de datos claras
- ✅ Trazabilidad completa

---

## 🔄 Cómo Crear un Example

### **Paso 1: Generar Reporte**
```bash
python generar_rca_preventa_MLB.py
```

### **Paso 2: Validar Calidad**
- [ ] Todos los componentes presentes
- [ ] Datos correctos (validar con BigQuery)
- [ ] Insights profundos y contextuales
- [ ] UX óptima

### **Paso 3: Promover a Example**
```bash
# Copiar a examples con nombre descriptivo
cp output/rca/marketplace/pre-venta/rca-preventa-cdu-mlb-nov-dic-2025.html \
   output/examples/rca_preventa_reference.html
```

### **Paso 4: Documentar**
- Actualizar tabla en este README
- Referenciar en `docs/RCA_STRUCTURE.md`
- Commitear al git

---

## 📖 Uso de Examples

### **Para Nuevos Scripts**
```python
# Abrir example para ver estructura esperada
import webbrowser
webbrowser.open('output/examples/rca_reference.html')

# Copiar estructura HTML del example
# Adaptar para tu commerce group
```

### **Para Validación**
```bash
# Comparar tu reporte vs el example
diff output/rca/mi-reporte.html output/examples/rca_reference.html
```

### **Para Documentación**
```markdown
Ver ejemplo completo en: `output/examples/rca_reference.html`
```

---

## 🚫 Qué NO Incluir

- ❌ Reportes con datos hardcodeados
- ❌ Reportes incompletos (falta algún componente)
- ❌ Reportes con insights genéricos
- ❌ Reportes sin validar
- ❌ Versiones intermedias/experimentales

---

## 📊 Estado Actual

| Example | Status | Commerce Group | Última Actualización |
|---------|--------|----------------|---------------------|
| `rca_reference.html` | ⏳ Pendiente | General | - |
| `rca_pdd_reference.html` | ⏳ Pendiente | Post-Compra | - |
| `rca_preventa_reference.html` | ⏳ Pendiente | Marketplace | - |
| `cr_cross_site_reference.html` | ⏳ Pendiente | CR Multi-site | - |
| `cr_single_site_reference.html` | ⏳ Pendiente | CR Single | - |

**Próximo:** Generar primer golden template validado.

---

## 🎯 Roadmap

1. ⏳ Crear `rca_preventa_reference.html` (MLB con análisis contextual)
2. ⏳ Crear `rca_pdd_reference.html` (PDD con tipificaciones)
3. ⏳ Crear `cr_cross_site_reference.html` (PCF cross-site 3 tablas)
4. ⏳ Documentar en `docs/RCA_STRUCTURE.md`
5. ⏳ Crear `templates/rca_template.html` basado en examples

---

**Última actualización:** Enero 2026  
**Mantenedor:** Framework CR - Mercado Libre
