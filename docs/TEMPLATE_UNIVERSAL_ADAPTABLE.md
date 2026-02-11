# Template Universal Adaptable v6.3.4

**Fecha:** Febrero 2026  
**Status:** ✅ IMPLEMENTADO - Template universal con análisis comparativo automático (robusto)

---

## 🎯 ¿Qué se implementó en v6.3.4?

Se agregaron **8 mejoras críticas** al sistema de generación automática para hacerlo verdaderamente universal y robusto:

### **Mejoras Implementadas:**

1. **✅ Dimensión de muestreo dinámica** (Fix #1 - CRÍTICO)
   - Ya no asume que siempre es `CDU`
   - Funciona con `PROCESO`, `CDU`, `TIPIFICACION`, `ENVIRONMENT`, etc.

2. **✅ Path del script robusto** (Fix #2)
   - Maneja correctamente la ubicación de `scripts/`
   - Evita errores de importación

3. **✅ Búsqueda inteligente de CSVs** (Fix #3 - CRÍTICO)
   - Parsea períodos correctamente desde el JSON
   - Normaliza nombres con múltiples caracteres especiales
   - Usa expresiones regulares para extraer fechas

4. **✅ División de citas por fecha real** (Fix #4)
   - Asigna citas a P1 o P2 basándose en `CONTACT_DATE_ID`
   - Fallback inteligente si no hay fecha disponible
   - Maneja fechas fuera de rango

5. **✅ Validación de coherencia** (Fix #5)
   - Verifica que elementos en JSON existan en cuadro CSV
   - Imprime warnings cuando falta información
   - Usa valores por defecto si es necesario

6. **✅ Fecha por defecto inteligente** (Fix #6)
   - Primera mitad de citas → fecha de P1
   - Segunda mitad de citas → fecha de P2
   - Ya no usa fecha hardcoded

7. **✅ Insight completo sin truncar** (Fix #7)
   - Usa el hallazgo principal completo
   - Agrega contexto cuando variación es mínima (<5%)
   - Mejora descripción de tendencias

8. **✅ Control de errores robusto** (Fix #8)
   - Captura y muestra errores detallados
   - Incluye traceback completo
   - Diagnóstico de archivos faltantes
   - El reporte continúa sin análisis comparativo si falla

---

## 📋 Cambios en la Firma de Funciones

### **Script: `generar_analisis_comparativo_auto.py`**

#### **Antes (v6.3.3):**
```python
def generar_analisis_comparativo(
    json_basico_path: Path,
    cuadro_cdu_path: Path,
    conversaciones_csv_dir: Path
) -> Dict:
```

#### **Ahora (v6.3.4):**
```python
def generar_analisis_comparativo(
    json_basico_path: Path,
    cuadro_dimension_path: Path,  # ✅ Ya no asume CDU
    conversaciones_csv_dir: Path,
    periodo_p1: str,               # ✅ Nuevo: "2025-11"
    periodo_p2: str                # ✅ Nuevo: "2025-12"
) -> Dict:
```

### **Nuevos parámetros CLI:**

```bash
python scripts/generar_analisis_comparativo_auto.py \
    --json-basico PATH \
    --cuadro-dimension PATH \  # Antes: --cuadro-cdu
    --periodo-p1 YYYY-MM \     # Nuevo
    --periodo-p2 YYYY-MM \     # Nuevo
    --output PATH \
    --conversaciones-dir PATH
```

---

## 🚀 Ejemplos de Uso Universal

### **Ejemplo 1: CDU (Moderaciones - MLM)**
```bash
python scripts/generar_analisis_comparativo_auto.py \
    --json-basico output/analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json \
    --cuadro-dimension output/cuadro_cdu_mlm_202511.csv \
    --periodo-p1 2025-11 \
    --periodo-p2 2025-12 \
    --output output/analisis_conversaciones_comparativo_claude_mlm_moderaciones_2025-11_2025-12.json
```

### **Ejemplo 2: PROCESO (PDD completo - MLA)**
```bash
python scripts/generar_analisis_comparativo_auto.py \
    --json-basico output/analisis_conversaciones_claude_mla_pdd_2025-09_2025-10.json \
    --cuadro-dimension output/cuadro_proceso_mla_202509.csv \
    --periodo-p1 2025-09 \
    --periodo-p2 2025-10 \
    --output output/analisis_conversaciones_comparativo_claude_mla_pdd_2025-09_2025-10.json
```

### **Ejemplo 3: TIPIFICACION (PCF Comprador - MLB)**
```bash
python scripts/generar_analisis_comparativo_auto.py \
    --json-basico output/analisis_conversaciones_claude_mlb_pcf_comprador_2024-12_2025-01.json \
    --cuadro-dimension output/cuadro_tipificacion_mlb_202412.csv \
    --periodo-p1 2024-12 \
    --periodo-p2 2025-01 \
    --output output/analisis_conversaciones_comparativo_claude_mlb_pcf_comprador_2024-12_2025-01.json
```

### **Ejemplo 4: ENVIRONMENT (Ventas y Publicaciones - MCO)**
```bash
python scripts/generar_analisis_comparativo_auto.py \
    --json-basico output/analisis_conversaciones_claude_mco_ventas_publicaciones_2025-06_2025-07.json \
    --cuadro-dimension output/cuadro_environment_mco_202506.csv \
    --periodo-p1 2025-06 \
    --periodo-p2 2025-07 \
    --output output/analisis_conversaciones_comparativo_claude_mco_ventas_publicaciones_2025-06_2025-07.json
```

---

## 🔧 Cambios en `generar_reporte_cr_universal_v6.3.py`

### **Antes (v6.3.3):**
```python
cuadro_cdu_path = Path("output") / f"cuadro_cdu_{args.site.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"

analisis_comp = generar_analisis_comparativo(
    json_basico_path,
    cuadro_cdu_path,
    Path("output")
)
```

### **Ahora (v6.3.4):**
```python
# FIX #1: Dimensión dinámica
cuadro_dimension_path = Path("output") / f"cuadro_{args.muestreo_dimension.lower()}_{args.site.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"

# FIX #2: Path robusto
scripts_dir = Path(__file__).parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# FIX #3: Pasar períodos
periodo_p1_str = f"{p1_start_dt.year}-{p1_start_dt.month:02d}"
periodo_p2_str = f"{p2_start_dt.year}-{p2_start_dt.month:02d}"

analisis_comp = generar_analisis_comparativo(
    json_basico_path,
    cuadro_dimension_path,  # ✅
    Path("output"),
    periodo_p1_str,         # ✅
    periodo_p2_str          # ✅
)
```

### **Control de Errores Mejorado:**
```python
except Exception as e:
    print(f"[ERROR] No se pudo generar análisis comparativo automáticamente")
    print(f"[ERROR] Tipo: {type(e).__name__}")
    print(f"[ERROR] Detalle: {str(e)}")
    
    import traceback
    print(f"\n[DEBUG] Traceback completo:")
    traceback.print_exc()
    
    print(f"\n[INFO] Diagnóstico de archivos:")
    print(f"  ✓ JSON básico: {json_basico_path.name}")
    print(f"    - Existe: {'✓ SÍ' if json_basico_path.exists() else '✗ NO'}")
    # ... más diagnóstico
```

---

## 🎯 Validación de Universalidad

El sistema ahora soporta **CUALQUIER combinación** de:

| Parámetro | Valores Soportados | Ejemplo |
|-----------|-------------------|---------|
| **Site** | MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE | `--site MLB` |
| **Commerce Group** | PDD, PNR, PCF_COMPRADOR, ME_PREDESPACHO, MODERACIONES, etc. | `--commerce-group PDD` |
| **Proceso Específico** | Cualquier proceso dentro del CG | `--process-name "Arrepentimiento"` |
| **Dimensión Muestreo** | PROCESO, CDU, TIPIFICACION, ENVIRONMENT, SOLUTION_ID, etc. | `--muestreo-dimension CDU` |
| **Aperturas** | Cualquier combinación | `--aperturas PROCESO,CDU,TIPIFICACION` |
| **Períodos** | Cualquier mes/año | `--p1-start 2024-06-01 --p1-end 2024-06-30` |

---

## 📊 Mejora en División de Citas

### **Antes:**
```python
# División 50-50 sin considerar fechas
mid_point = len(citas) // 2
citas_nov = citas[:mid_point]
citas_dic = citas[mid_point:]
```

### **Ahora:**
```python
# División inteligente por fecha real
for cita in citas_con_fecha:
    fecha = pd.to_datetime(cita['fecha'])
    fecha_str = fecha.strftime('%Y-%m')
    
    if fecha_str == periodo_p1:
        citas_p1.append(cita)
    elif fecha_str == periodo_p2:
        citas_p2.append(cita)
    else:
        # Asignar al período más cercano
        if distancia(fecha, p1) < distancia(fecha, p2):
            citas_p1.append(cita)
        else:
            citas_p2.append(cita)
```

---

## 🔍 Mejora en Búsqueda de CSVs

### **Antes (problemático):**
```python
csv_path = f"conversaciones_{proceso.replace('/', '_')}_{site}_{json_path.stem.split('_')[-2][-4:]}.csv"
# Problema: split frágil, no maneja bien los nombres
```

### **Ahora (robusto):**
```python
# Extraer períodos con regex
periodos = re.findall(r'(\d{4})-(\d{2})', json_basico_path.stem)
p1_year, p1_month = periodos[0]
periodo_str = f"{p1_year}{p1_month}"

# Normalizar nombre del elemento
elemento_norm = elemento.replace('/', '_').replace(' ', '_').replace('-', '').lower()

csv_path = f"conversaciones_{elemento_norm}_{site}_{periodo_str}.csv"
```

---

## ✅ Checklist de Validación

Antes de implementar cualquier análisis, el sistema valida:

- [x] JSON básico existe
- [x] Cuadro de dimensión existe (nombre correcto según `--muestreo-dimension`)
- [x] Períodos en formato válido (YYYY-MM)
- [x] Elementos en JSON coinciden con elementos en cuadro
- [x] CSVs de conversaciones existen (con nombres normalizados)
- [x] Fechas en citas son parseables
- [x] Incoming > 0 para ambos períodos

---

## 📝 Output de Diagnóstico Mejorado

### **Cuando falla la generación:**
```
[ERROR] No se pudo generar análisis comparativo automáticamente
[ERROR] Tipo: FileNotFoundError
[ERROR] Detalle: No se encontró 'conversaciones_fakes_mlm_202511.csv'

[DEBUG] Traceback completo:
  File "...", line 123, in generar_analisis_comparativo
    df_conv = pd.read_csv(conversaciones_csv_path)
  FileNotFoundError: [Errno 2] No such file or directory: '...'

[INFO] Diagnóstico de archivos:
  ✓ JSON básico: analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json
    - Existe: ✓ SÍ
    - Tamaño: 45,832 bytes
  ✓ Cuadro dimensión: cuadro_cdu_mlm_202511.csv
    - Existe: ✓ SÍ
    - Tamaño: 1,245 bytes
  ✓ Conversaciones: 3 elementos priorizados

[INFO] El reporte se generará sin análisis comparativo detallado
[INFO] Los insights cualitativos estarán disponibles en el resumen ejecutivo
```

---

## 🚀 Flujo de Ejecución Actualizado

```
Usuario ejecuta: generar_reporte_cr_universal_v6.3.py
  ↓
1. Calcula métricas (incoming, drivers, CR)
  ↓
2. Genera cuadros cuantitativos por dimensión
  ↓
3. Muestrea conversaciones (30 por elemento-período)
  ↓
4. Analiza conversaciones con Cursor AI
  ↓
5. Guarda: analisis_conversaciones_claude_{site}_{cg}_{p1}_{p2}.json
  ↓
6. ¿Existe análisis comparativo?
   │
   ├─ SÍ → Usar el existente
   │
   └─ NO → Auto-generar:
       ├─ Validar archivos necesarios
       ├─ Parsear períodos desde JSON
       ├─ Dividir citas por fecha real
       ├─ Generar insight descriptivo
       ├─ Guardar JSON comparativo
       └─ Agregar al HTML
  ↓
7. Genera HTML completo con análisis comparativo
  ↓
8. Abre reporte en navegador
```

---

## 📌 Archivos Actualizados

```
scripts/generar_analisis_comparativo_auto.py   # v2.0 (Universal)
  - agregar_fechas_a_citas() → +periodo_p1, +periodo_p2
  - generar_analisis_comparativo() → +cuadro_dimension_path, +periodo_p1, +periodo_p2
  - main() → +--periodo-p1, +--periodo-p2, validaciones

generar_reporte_cr_universal_v6.3.py           # v6.3.4
  - cuadro_cdu_path → cuadro_dimension_path
  - Pasa períodos a generar_analisis_comparativo()
  - Control de errores robusto
  - Diagnóstico detallado

docs/TEMPLATE_UNIVERSAL_ADAPTABLE.md           # v6.3.4 (este archivo)
```

---

**Version:** 6.3.4  
**Last Updated:** Febrero 2026  
**Status:** ✅ PRODUCCIÓN - Template universal robusto con validaciones completas

### **Antes (v6.3.2)**
```
Usuario solicita análisis
  ↓
Script genera análisis básico (causas_raiz global)
  ↓
Reporte muestra: Resumen ejecutivo + Cuadros cuantitativos
  ↓
❌ NO hay análisis comparativo detallado (Nov vs Dic)
```

### **Ahora (v6.3.3)**
```
Usuario solicita análisis
  ↓
Script genera análisis básico
  ↓
Script AUTOM genera análisis comparativo desde el básico
  ↓
Reporte muestra: Resumen ejecutivo + Cuadros cuantitativos + Análisis Comparativo Enriquecido
  ↓
✅ TODO en un solo paso, sin intervención manual
```

---

## 🔧 Cambios Técnicos

### 1. Nuevo script: `scripts/generar_analisis_comparativo_auto.py`

**Función:** Transforma análisis básico en análisis comparativo automáticamente

**Input:**
- `analisis_conversaciones_claude_{site}_{cg}_{p1}_{p2}.json` (básico)
- `cuadro_cdu_{site}_{periodo}.csv` (métricas cuantitativas)
- CSVs de conversaciones (para fechas)

**Output:**
- `analisis_conversaciones_comparativo_claude_{site}_{cg}_{p1}_{p2}.json`

**Uso standalone:**
```bash
py scripts/generar_analisis_comparativo_auto.py \
    --json-basico output/analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json \
    --cuadro-cdu output/cuadro_cdu_mlm_202511.csv \
    --output output/analisis_conversaciones_comparativo_claude_mlm_moderaciones_2025-11_2025-12.json
```

### 2. Integración automática en `generar_reporte_cr_universal_v6.3.py`

**Modificación en líneas ~1746-1850:**

```python
# ANTES
else:
    print(f"[COMPARATIVO] No se encontró análisis comparativo (opcional)")

# AHORA
else:
    print(f"[COMPARATIVO] No se encontró análisis comparativo (opcional)")
    print(f"[AUTO-GEN] Generando análisis comparativo automáticamente...")
    
    # Importar y ejecutar generación automática
    from generar_analisis_comparativo_auto import generar_analisis_comparativo
    analisis_comp = generar_analisis_comparativo(...)
    
    # Guardar JSON
    with open(analisis_comparativo_path, 'w', encoding='utf-8') as f:
        json.dump(analisis_comp, f, indent=2, ensure_ascii=False)
    
    # Agregar HTML al reporte (mismo código que cuando existe JSON)
    [... genera tablas comparativas, citas, sentimiento ...]
```

**Lógica:**
1. Si existe JSON comparativo → usar el existente
2. Si NO existe pero SÍ hay análisis básico → **generar automáticamente**
3. Agregar siempre al reporte HTML

---

## 📊 Estructura del Análisis Comparativo Auto-Generado

### **Schema JSON**

```json
{
  "Fakes": {
    "proceso": "Fakes",
    "commerce_group": "Moderaciones",
    "site": "MLM",
    "incoming_nov": 6385,
    "incoming_dic": 4905,
    "variacion_casos": -1480,
    "variacion_pct": -23.2,
    "conversaciones_nov": 30,
    "conversaciones_dic": 30,
    "causas_nov": [
      {
        "causa": "Reactivación tras validación de factura",
        "porcentaje": 65,
        "casos_estimados": 2250,
        "descripcion": "...",
        "sentimiento": {
          "satisfaccion": 70,
          "frustracion": 30
        },
        "citas": [
          {
            "case_id": "418002128",
            "texto": "...",
            "fecha": "2025-11-15"
          }
        ]
      }
    ],
    "causas_dic": [
      {
        "causa": "Reactivación tras validación de factura",
        "porcentaje": 65,
        "casos_estimados": 1730,
        "descripcion": "...",
        "sentimiento": {
          "satisfaccion": 70,
          "frustracion": 30
        },
        "citas": [...]
      }
    ],
    "analisis_comparativo": {
      "insight_principal": "La reducción de 1,480 casos (-23.2%) se explica principalmente por: Reactivación tras validación de factura...",
      "patron_dominante": "Reactivación tras validación de factura",
      "cambio_principal": "Reducción del 23.2% en incoming"
    }
  }
}
```

### **Diferencias clave vs Análisis Básico**

| Campo | Análisis Básico | Análisis Comparativo |
|-------|----------------|---------------------|
| **Causas** | `causas` (global Nov+Dic) | `causas_nov` y `causas_dic` (separadas) |
| **Sentimiento** | String (`"70% satisfacción, 30% frustración"`) | Dict (`{"satisfaccion": 70, "frustracion": 30}`) |
| **Citas** | Sin fecha | Con fecha (`"fecha": "2025-11-15"`) |
| **Incoming** | No incluido | `incoming_nov`, `incoming_dic`, `variacion_casos` |
| **Insight** | `hallazgo_principal` (global) | `analisis_comparativo.insight_principal` (temporal) |

---

## 🎨 Secciones del Reporte (Template Completo)

### **Estructura HTML Resultante:**

1. **Header** (con proceso específico si aplica)
2. **Resumen Ejecutivo** (3 bullets con causas raíz)
3. **Cards Ejecutivas** (8 cards)
4. **Gráfico Semanal** (14+ semanas)
5. **Eventos Comerciales** (si hay hard metrics)
6. **Cuadros Cuantitativos** (sin PROCESO si hay filtro)
7. **✨ Análisis Comparativo de Patrones** (automático)
   - Insight principal por proceso
   - Tabla comparativa (Nov vs Dic) con sentimiento
   - Evidencia cualitativa con fechas
   - Botón colapsable "Ver más citas"
8. **Footer Técnico** (colapsable)

---

## 🚀 Flujo de Ejecución (Usuario Final)

### **Caso 1: Análisis nuevo (MLM Moderaciones - PR Propiedad Intelectual)**

```bash
# UN SOLO COMANDO
py generar_reporte_cr_universal_v6.3.py \
    --site MLM \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --commerce-group MODERACIONES \
    --process-name "PR - Propiedad intelectual" \
    --aperturas PROCESO,CDU \
    --muestreo-dimension CDU \
    --open-report
```

**¿Qué sucede internamente?**
```
1. Calcula métricas (incoming, drivers, CR)
2. Genera cuadros cuantitativos por dimensión
3. Muestrea conversaciones (30 por CDU-período)
4. Analiza conversaciones con Cursor AI
5. Guarda: analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json
6. ✨ Auto-genera análisis comparativo desde el básico
7. Guarda: analisis_conversaciones_comparativo_claude_mlm_moderaciones_2025-11_2025-12.json
8. Genera HTML completo con análisis comparativo
9. Abre reporte en navegador
```

**Resultado:** Reporte completo con análisis comparativo, sin pasos manuales.

---

### **Caso 2: Análisis con JSON comparativo pre-existente**

Si ya existe `analisis_conversaciones_comparativo_claude_...json`:

```bash
# MISMO COMANDO
py generar_reporte_cr_universal_v6.3.py ... --open-report
```

**¿Qué sucede?**
```
1-4. (igual)
5. Detecta que YA EXISTE JSON comparativo
6. ✅ Usa el existente (no lo regenera)
7. Genera HTML con el análisis existente
8. Abre reporte en navegador
```

**Resultado:** Usa el análisis comparativo que ya tenías (puede ser manual o auto-generado previo).

---

## 🎯 Adaptabilidad Universal

El template ahora se adapta automáticamente a:

### **1. Filtros**
| Filtro | Comportamiento |
|--------|---------------|
| **Sin --process-name** | Muestra tabla PROCESO completa |
| **Con --process-name** | Oculta tabla PROCESO, muestra dimensión siguiente (CDU) |
| **Cualquier --aperturas** | Procesa las dimensiones solicitadas |
| **Cualquier --site** | Funciona para MLA, MLB, MLC, MCO, MEC, MLM, MLU, MPE |
| **Cualquier --commerce-group** | PDD, PNR, PCF, ME_PREDESPACHO, etc. |

### **2. Análisis Comparativo**
| Situación | Resultado |
|-----------|-----------|
| ❌ No existe JSON básico | Reporte sin análisis cualitativo |
| ✅ Existe JSON básico | **Auto-genera** JSON comparativo + reporte completo |
| ✅ Existe JSON comparativo | Usa el existente + reporte completo |

### **3. Título y Referencias**
- **Header:** Incluye proceso específico si existe `--process-name`
- **Subtítulo:** Menciona commerce group + proceso (si aplica) + site
- **Footer:** Agrega "▸ Proceso específico: X" si aplica
- **Nombre archivo:** Incluye proceso en el nombre

---

## 📝 Ejemplo de Salida

### **Archivo generado:**
```
output/reporte_cr_moderaciones_pr__propiedad_intelectual_mlm_nov_dec_2025_v6.3.html
```

### **Título en HTML:**
```
📊 Contact Rate Analysis - MODERACIONES - PR - Propiedad intelectual MLM
```

### **Subtítulo:**
```
Período: Nov 2025 vs Dec 2025 | Commerce Group: MODERACIONES | Proceso: PR - Propiedad intelectual | Site: MLM
```

### **Sección Análisis Comparativo:**
```
🔍 Análisis Comparativo de Patrones por Período

🔹 Fakes
📊 Conversaciones analizadas: 60 casos (30 Nov + 30 Dic) | Cobertura: 100% del incoming

💡 Insight Principal:
La reducción de 1,480 casos (-23.2%) se explica principalmente por: Reactivación de publicación tras validación de factura...

[TABLA COMPARATIVA NOV VS DIC CON SENTIMIENTO]
[EVIDENCIA CUALITATIVA CON FECHAS Y CITAS]
```

---

## ✅ Beneficios

1. **Sin intervención manual:** Todo automático en un solo comando
2. **Adaptable:** Funciona con cualquier site, commerce group, proceso, aperturas
3. **Completo:** Siempre incluye análisis comparativo (Nov vs Dic)
4. **Reutilizable:** JSONs generados se reutilizan en futuras ejecuciones
5. **Consistente:** Mismo template y estructura para todos los análisis

---

## 🔄 Migración desde v6.3.2

**No requiere cambios en comandos existentes.** Los usuarios pueden seguir ejecutando:

```bash
py generar_reporte_cr_universal_v6.3.py --site X --commerce-group Y ... --open-report
```

**Diferencia:**
- **v6.3.2:** Reporte sin análisis comparativo (solo si existía JSON manual)
- **v6.3.3:** Reporte CON análisis comparativo (siempre, auto-generado)

---

## 📌 Archivos Clave

```
generar_reporte_cr_universal_v6.3.py        # Script principal (actualizado)
scripts/generar_analisis_comparativo_auto.py  # Generador automático (nuevo)
docs/TEMPLATE_UNIVERSAL_ADAPTABLE.md        # Esta documentación
```

---

**Version:** 6.3.3  
**Last Updated:** Febrero 2026  
**Status:** ✅ PRODUCCIÓN - Template universal con auto-generación completa
