# 📊 Changelog v6.3.8 - Análisis Separado por Período

**Fecha:** 4 Febrero 2026  
**Versión:** 6.3.8  
**Objetivo:** Detectar cambios REALES de patrones entre períodos mediante análisis separado

---

## 🎯 Problema Resuelto

### **Antes (v6.3.7 y anteriores):**

❌ **Análisis conjunto:** Las conversaciones de ambos períodos se analizaban juntas  
❌ **Porcentajes estáticos:** Mismo % para ambos períodos (ej: 45% Dic → 45% Ene)  
❌ **No detecta cambios:** No podía identificar si un patrón aumentó o disminuyó entre períodos  

**Ejemplo del problema:**
```
REAL (en datos):
- Dic: "Cupones inválidos" = 60% | "Errores técnicos" = 20%
- Ene: "Cupones inválidos" = 30% | "Errores técnicos" = 50%

REPORTADO (v6.3.7):
- Dic: "Cupones inválidos" = 45% | "Errores técnicos" = 35%
- Ene: "Cupones inválidos" = 45% | "Errores técnicos" = 35%
       ↑ PERDÍAMOS la información temporal
```

### **Ahora (v6.3.8):**

✅ **Análisis separado:** Cada período se analiza independientemente  
✅ **Porcentajes dinámicos:** Refleja proporciones reales por período  
✅ **Detecta cambios:** Identifica patrones que surgen, desaparecen o cambian  

**Ejemplo mejorado:**
```
REAL (en datos) = REPORTADO (v6.3.8):
- Dic: "Cupones inválidos" = 60% | "Errores técnicos" = 20%
- Ene: "Cupones inválidos" = 30% | "Errores técnicos" = 50%
      ↑ DETECTA que errores técnicos EXPLOTARON en Enero
```

---

## 🚀 Cambios Principales

### 1. **Exportación de CSVs Separados por Período**

**Antes:**
```
output/conversaciones_reembolsos_mlm_202512.csv  (60 conversaciones mezcladas)
```

**Ahora:**
```
output/conversaciones_reembolsos_mlm_p1_202512.csv  (30 conversaciones Dic)
output/conversaciones_reembolsos_mlm_p2_202601.csv  (30 conversaciones Ene)
```

**Código modificado:** `generar_reporte_cr_universal_v6.3.6.py` (líneas 1583-1594)

---

### 2. **Análisis Separado con Cursor AI**

**Antes:**
```
Usuario: "Analiza las conversaciones de output/"
Claude: Analiza 60 conversaciones juntas → 1 JSON con % globales
```

**Ahora:**
```
Usuario: "Analiza P1 y P2 separadamente"
Claude: 
  - Analiza 30 conversaciones Dic → JSON P1 con % de Dic
  - Analiza 30 conversaciones Ene → JSON P2 con % de Ene
```

**Prompt mejorado:** `esperar_analisis_conversaciones()` (líneas 254-430)

**Formato JSON por período:**
```json
{
  "Elemento 1": {
    "proceso": "Reembolsos",
    "periodo": "Dic 2025",
    "total_conversaciones": 30,
    "causas": [
      {
        "causa": "Reembolso procesado pero no reflejado",
        "porcentaje": 45,  ← % REAL de Dic
        "casos_estimados": 2257,
        "sentimiento": {"frustracion": 75, "satisfaccion": 15}
      }
    ]
  }
}
```

---

### 3. **Carga Inteligente de Análisis Separados**

**Nueva función:** `configurar_analisis_claude()` (líneas 184-310)

**Lógica de búsqueda:**
```
PRIORIDAD 1: Análisis separados (v6.3.8)
  - analisis_conversaciones_claude_{site}_{cg}_{dim}_p1_{p1}.json
  - analisis_conversaciones_claude_{site}_{cg}_{dim}_p2_{p2}.json
  ↓ Si ambos existen → Cargar y combinar

FALLBACK: Análisis conjunto (legacy)
  - analisis_conversaciones_claude_{site}_{cg}_{dim}_{p1}_{p2}.json
  ↓ Si existe → Cargar (con warning de % estáticos)
```

**Estructura combinada:**
```python
ANALISIS_PREEXISTENTES[elemento] = {
    "causas_p1": [...],  # Causas de P1 con % de P1
    "causas_p2": [...],  # Causas de P2 con % de P2
    "analisis_separado": True,  # Flag v6.3.8
    "version": "v6.3.8"
}
```

---

### 4. **Generación de Análisis Comparativo Mejorado**

**Nuevo script:** `scripts/generar_analisis_comparativo_desde_separados.py`

**Diferencias vs `generar_analisis_comparativo_auto.py`:**

| Característica | Legacy (auto.py) | Nuevo (desde_separados.py) |
|----------------|------------------|----------------------------|
| Input | 1 JSON conjunto | 2 JSONs separados |
| Porcentajes | Estáticos (mismo para ambos) | Dinámicos (recalculados por período) |
| Detecta cambios | ❌ No | ✅ Sí |
| Causas nuevas | ❌ No detecta | ✅ Detecta |
| Causas desaparecidas | ❌ No detecta | ✅ Detecta |

**Cálculo de porcentajes dinámicos:**
```python
# ANTES (legacy):
porcentaje_p1 = porcentaje_global  # ej: 45%
porcentaje_p2 = porcentaje_global  # ej: 45% (igual!)

# AHORA (v6.3.8):
porcentaje_p1 = (casos_p1 / incoming_p1) * 100  # ej: 60%
porcentaje_p2 = (casos_p2 / incoming_p2) * 100  # ej: 30% (real!)
```

---

## 📁 Archivos Modificados

### **Modificaciones mayores:**

1. **`generar_reporte_cr_universal_v6.3.6.py`**
   - Líneas 1-54: Actualización de docstring v6.3.8
   - Líneas 137: Print de versión
   - Líneas 184-310: `configurar_analisis_claude()` con soporte de análisis separado
   - Líneas 254-430: `esperar_analisis_conversaciones()` con prompt mejorado
   - Líneas 1583-1594: Exportación de CSVs separados
   - Líneas 1607-1639: Espera automática con parámetros actualizados
   - Líneas 1672-1685: Mensajes de export-only actualizados
   - Líneas 2604-2648: Generación de análisis comparativo con prioridad a separados

### **Archivos nuevos:**

2. **`scripts/generar_analisis_comparativo_desde_separados.py`**
   - Generador de análisis comparativo desde análisis separados
   - Cálculo de porcentajes dinámicos por período
   - Detección de cambios de patrones

3. **`docs/CHANGELOG_v6.3.8.md`**
   - Este archivo - documentación completa de cambios

---

## 🎯 Flujo Completo v6.3.8

```
1. Usuario ejecuta script
   ↓
2. [EXPORTACIÓN] Genera 2 CSVs por elemento (P1 y P2)
   ↓
3. [ESPERA AUTOMÁTICA] Muestra prompt para análisis separado
   ↓
4. [CURSOR AI] Usuario analiza P1 → genera JSON P1
   ↓
5. [CURSOR AI] Usuario analiza P2 → genera JSON P2
   ↓
6. [SCRIPT] Detecta ambos JSONs automáticamente
   ↓
7. [SCRIPT] Carga y combina análisis separados
   ↓
8. [SCRIPT] Genera análisis comparativo con porcentajes dinámicos
   ↓
9. [HTML] Renderiza reporte con detección de cambios
   ↓
10. [NAVEGADOR] Abre reporte automáticamente
```

---

## 📊 Beneficios para el Analista

### **Detección de Cambios Reales:**

✅ **Antes no podías ver:** "Errores técnicos pasaron de 20% a 50%"  
✅ **Ahora sí puedes ver:** Columnas con % diferentes por período  

### **Identificación de Causas Emergentes:**

✅ **Antes:** Todas las causas aparecían en ambos períodos (aunque fueran 0)  
✅ **Ahora:** Detecta causas que solo aparecen en P2 (nuevas) o solo en P1 (resueltas)  

### **Precisión en Porcentajes:**

✅ **Antes:** % estimados asumiendo distribución constante  
✅ **Ahora:** % reales basados en análisis independiente de cada período  

### **Insights Mejorados:**

```
ANTES: "Patrón X representa 45% de casos en ambos períodos"
AHORA: "Patrón X disminuyó de 60% a 30% entre períodos (cambio detectado)"
```

---

## 🔄 Retrocompatibilidad

### **Modo Legacy (análisis conjunto):**

El script mantiene soporte para análisis conjunto:

```python
# Si solo existe JSON conjunto → usa generador legacy
if json_basico_path.exists():
    from generar_analisis_comparativo_auto import generar_analisis_comparativo
    analisis_comp = generar_analisis_comparativo(...)
    print("[WARNING] Usando análisis conjunto (sin detección de cambios)")
```

### **Migración automática:**

- ✅ Análisis antiguos siguen funcionando
- ✅ Nuevos análisis usan formato separado automáticamente
- ✅ Prompt guía al usuario al nuevo formato
- ✅ Fallback a legacy si no encuentra análisis separados

---

## 🧪 Testing

### **Casos de prueba cubiertos:**

1. ✅ Análisis separado completo (happy path)
2. ✅ Solo existe análisis P1 (partial)
3. ✅ Solo existe análisis P2 (partial)
4. ✅ Análisis conjunto legacy (fallback)
5. ✅ Sin análisis (export-only)
6. ✅ Elementos con 0 conversaciones en P1 o P2
7. ✅ Causas que aparecen solo en un período

### **Validaciones:**

- ✅ Coherencia de elementos entre JSONs y cuadro cuantitativo
- ✅ Porcentajes suman 100% en cada período
- ✅ Casos estimados coherentes con incoming real
- ✅ Sentimiento parseado correctamente
- ✅ Citas con fechas asignadas correctamente

---

## 📝 Próximos Pasos

### **Para el usuario (analista):**

1. Ejecutar script normalmente (sin cambios)
2. Cuando aparezca el prompt → copiar y pegar en Cursor AI
3. Analizar P1 y P2 separadamente (2 prompts)
4. El script detecta automáticamente y continúa

### **Resultado esperado:**

- 🎯 Reporte HTML con porcentajes dinámicos por período
- 🎯 Detección de cambios de patrones claramente visible
- 🎯 Identificación de causas emergentes o desaparecidas
- 🎯 Análisis de excelencia para toma de decisiones

---

## 🏆 Conclusión

**v6.3.8 transforma el análisis de Contact Rate de:**

❌ **Análisis estático** (asume patrones constantes)  
✅ **Análisis dinámico** (detecta cambios reales)

**Impacto:**
- 📈 Insights más precisos
- 🔍 Detección de tendencias reales
- 💡 Decisiones basadas en cambios verificados
- ⚡ Sin cambios en el flujo del usuario (automático)

---

**Autor:** CR Commerce Analytics Team  
**Versión:** 6.3.8  
**Fecha:** 4 Febrero 2026  
**Status:** ✅ PRODUCTION READY
