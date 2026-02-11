# 🚀 Workflow Completo - Ejemplo Concreto PDD MLA Nov-Dic 2025

Este documento muestra el flujo completo paso a paso usando el caso real de PDD MLA.

---

## 🎯 **Contexto del Análisis**

- **Commerce Group:** PDD (Producto Defectuoso/Diferente)
- **Site:** MLA (Argentina)
- **Períodos:** Noviembre 2025 vs Diciembre 2025
- **Dimensión:** PROCESS_NAME
- **Procesos priorizados (regla 80%):** 6 procesos que explican 80.5% de la variación
- **Análisis:** 100 conversaciones por proceso con muestreo ponderado

---

## ⏱️ **Comparativa de Tiempos**

| Paso | Método v4.0 (anterior) | Método v5.0 (nuevo) | Reducción |
|------|------------------------|---------------------|-----------|
| **1. Query muestreo** | 7 min (6 queries × 1.2 min) | 2 min (1 query) | 71% ↓ |
| **2. Análisis conversaciones** | 30 min (6 × 5 min manual) | 3 min (6 × 30s LLM) | 90% ↓ |
| **3. Validación** | 3 min | 1 min | 67% ↓ |
| **TOTAL** | **40 minutos** | **6 minutos** | **🚀 85% ↓** |

---

## 📝 **PASO 1: Crear Query Unificada (5 min)**

### 1.1 Identificar Parámetros

```yaml
Site: MLA
Period Start: 2025-12-01
Period End: 2025-12-31
Dimension: PROCESS_NAME
Commerce Group: PDD
Procesos Priorizados:
  - Arrepentimiento - XD
  - Defectuoso - XD
  - Defectuoso - Flex  # ← Con pico 29-30 dic
  - Arrepentimiento - Flex
  - Incompleto - Flex
  - Diferente - Flex
Fechas Pico: 2025-12-29, 2025-12-30  # ← Del peak detection
```

### 1.2 Usar Template

**Archivo base:** `sql/templates/muestreo_unificado_template.sql`

**Archivo generado:** `sql/ejemplo_muestreo_unificado_pdd_mla_dic_2025.sql`

**Reemplazos realizados:**
- `{site}` → `'MLA'`
- `{period_start}` → `'2025-12-01'`
- `{period_end}` → `'2025-12-31'`
- `{dimension}` → `PROCESS_NAME`
- `{commerce_group}` → `'PDD'`
- `{lista_procesos_priorizados}` → `'Arrepentimiento - XD', 'Defectuoso - XD', ...`
- `{fechas_pico}` → `'2025-12-29', '2025-12-30'`

### 1.3 Ejecutar Query

```powershell
Get-Content "sql\ejemplo_muestreo_unificado_pdd_mla_dic_2025.sql" -Raw | 
bq query --use_legacy_sql=false --format=csv > 
output\muestreo_unificado_ejemplo.csv
```

**⏱️ Tiempo:** ~2 minutos

**📊 Resultado:** CSV con ~600 filas (100 por proceso)

---

## 🤖 **PASO 2: Analizar con LLM (3 min para 6 procesos)**

### 2.1 Cargar CSV y Dividir por Proceso

```python
import pandas as pd

# Cargar CSV
df = pd.read_csv('output/muestreo_unificado_ejemplo.csv')

# Dividir por proceso
procesos = [
    'Arrepentimiento - XD',
    'Defectuoso - XD', 
    'Defectuoso - Flex',
    'Arrepentimiento - Flex',
    'Incompleto - Flex',
    'Diferente - Flex'
]

for proceso in procesos:
    df_proceso = df[df['PROCESS_NAME'] == proceso]
    print(f"{proceso}: {len(df_proceso)} conversaciones")
```

### 2.2 Formatear Conversaciones para Prompt

```python
def formatear_conversaciones(df_proceso):
    """Formatear conversaciones según template de prompt"""
    convs_text = ""
    for i, row in df_proceso.iterrows():
        conv_preview = row['CONVERSATION_SUMMARY'][:200] + "..."
        convs_text += f"{i+1}. CASE_ID: {row['CAS_CASE_ID']} | Fecha: {row['FECHA_CONTACTO']}\n"
        convs_text += f'   "{conv_preview}"\n\n'
    return convs_text

# Ejemplo para Defectuoso - Flex
df_defectuoso_flex = df[df['PROCESS_NAME'] == 'Defectuoso - Flex']
conversaciones_formateadas = formatear_conversaciones(df_defectuoso_flex)
```

### 2.3 Construir Prompt Completo

```python
# Leer template de prompt
with open('templates/prompt_analisis_conversaciones.md', 'r', encoding='utf-8') as f:
    template = f.read()

# Reemplazar placeholders
prompt = template.replace('{PROCESS_NAME}', 'Defectuoso - Flex')
prompt = prompt.replace('{N}', '100')
prompt = prompt.replace('{CSV_DATA_PROCESO}', conversaciones_formateadas)
prompt = prompt.replace('{COMMERCE_GROUP}', 'PDD')
```

### 2.4 Enviar a LLM

```python
import openai  # o anthropic para Claude

# Configurar cliente
client = openai.OpenAI(api_key="tu-api-key")

# Enviar prompt
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Rápido y económico
    messages=[
        {
            "role": "system", 
            "content": "Eres un analista de datos experto. Respondes solo en formato JSON válido."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ],
    temperature=0.3,
    max_tokens=4096
)

# Parsear respuesta
import json
llm_output = response.choices[0].message.content

# Limpiar markdown si existe
if llm_output.startswith("```json"):
    llm_output = llm_output.replace("```json", "").replace("```", "").strip()

result = json.loads(llm_output)
```

**⏱️ Tiempo:** ~30 segundos por proceso

**📊 Output:** JSON estructurado con causas, citas, sentimiento

**Ejemplo de output:** Ver `templates/ejemplo_prompt_defectuoso_flex.md` sección "Output Esperado del LLM"

### 2.5 Repetir para los 6 Procesos

```python
resultados = {}

for proceso in procesos:
    print(f"Analizando {proceso}...")
    
    df_proceso = df[df['PROCESS_NAME'] == proceso]
    conversaciones = formatear_conversaciones(df_proceso)
    
    prompt = construir_prompt(proceso, conversaciones)
    result = analizar_con_llm(prompt)
    
    resultados[proceso] = result
    print(f"   ✅ {len(result['causas'])} causas identificadas")

print(f"\n✅ {len(resultados)} procesos analizados en ~3 minutos")
```

---

## ✅ **PASO 3: Validar Outputs (1 min)**

```python
# Ejecutar validaciones automáticas
from templates.ejemplo_validacion_json import validar_json

for proceso, result in resultados.items():
    print(f"\nValidando {proceso}...")
    result_validado = validar_json(result, df[df['PROCESS_NAME'] == proceso])
    resultados[proceso] = result_validado
```

**Validaciones:**
1. ✅ CASE_IDs existen en CSV
2. ✅ Cobertura ≥80%
3. ✅ Porcentajes suman ~100%
4. ✅ Citas son fragmentos textuales

**Código completo:** Ver `templates/ejemplo_validacion_json.py`

---

## 📄 **PASO 4: Insertar en HTML (automático)**

```python
def generar_seccion_evidencia(result):
    """Generar HTML con evidencia cualitativa"""
    html = f"""
    <div class="evidence-section">
        <h5>✅ EVIDENCIA CUALITATIVA REAL:</h5>
        <ul>
    """
    
    for causa in result['causas']:
        if causa['descripcion'] == 'Otros / Volumétrico':
            continue
        
        html += f"""
            <li><strong>{causa['descripcion']}:</strong> {causa['frecuencia_absoluta']}/{result['total_conversaciones']} ({causa['frecuencia_porcentaje']:.1f}%)
                <ul style="margin-left: 20px; margin-top: 5px;">
        """
        
        # Citas
        for cita in causa['citas'][:2]:
            html += f"""
                    <li>"{cita['texto']}" - Caso #{cita['caso_id']}</li>
            """
        
        # Sentimiento
        html += f"""
                    <li><strong>Sentimiento:</strong> Frustración {causa['sentimiento']['frustracion']}%, Satisfacción {causa['sentimiento']['satisfaccion_post_resolucion']}%</li>
                </ul>
            </li>
        """
    
    html += f"""
        </ul>
        
        <h5 style="margin-top: 15px;">🎯 HALLAZGO PRINCIPAL:</h5>
        <p>{result['hallazgo_principal']}</p>
    </div>
    """
    
    return html

# Generar HTML para cada proceso
for proceso, result in resultados.items():
    html_evidencia = generar_seccion_evidencia(result)
    # Insertar en reporte HTML...
```

---

## 📊 **Resultado Final**

### Métricas del Análisis

```
✅ ANÁLISIS COMPLETADO

Procesos analizados: 6
Conversaciones totales: 600 (100 por proceso)
Causas raíz identificadas: ~24 (4 por proceso en promedio)
Cobertura promedio: 85% (target: ≥80%)
Citas textuales: ~48 (2 por causa)

⏱️ TIEMPO TOTAL: 6 minutos
   - Query unificada: 2 min
   - Análisis LLM (6 × 30s): 3 min
   - Validación: 1 min

🚀 REDUCCIÓN vs v4.0: 85% menos tiempo (40 min → 6 min)
✅ CALIDAD: Igual o superior (análisis estructurado + validación)
```

### Ejemplo de Evidencia Insertada en HTML

```html
<div class="evidence-section">
    <h5>✅ EVIDENCIA CUALITATIVA REAL:</h5>
    <ul>
        <li><strong>Productos defectuosos de fábrica - fallas de funcionamiento:</strong> 42/100 (42.0%)
            <ul style="margin-left: 20px; margin-top: 5px;">
                <li>"El comprador reporta que el producto pierde agua en la unión de la base" - Caso #426491524</li>
                <li>"La compradora reportó que el aro inflable se desinfla rápidamente y no funciona" - Caso #426253719</li>
                <li><strong>Sentimiento:</strong> Frustración 75%, Satisfacción 68%</li>
            </ul>
        </li>
        <li><strong>Productos dañados en transporte:</strong> 38/100 (38.0%)
            <ul style="margin-left: 20px; margin-top: 5px;">
                <li>"El comprador recibió un pedido con el embalaje roto" - Caso #426235237</li>
                <li>"El pedido llegó tarde, con el empaque y producto mojados" - Caso #426322915</li>
                <li><strong>Sentimiento:</strong> Frustración 68%, Satisfacción 62%</li>
            </ul>
        </li>
    </ul>
    
    <h5>🎯 HALLAZGO PRINCIPAL:</h5>
    <p>80% de casos en productos defectuosos y dañados en transporte post-Navidad, con patrón temporal en días 29-30 dic sugiriendo presión operativa en centros Flex.</p>
</div>
```

---

## 🎓 **Aprendizajes Clave**

### Lo que cambió

| Aspecto | v4.0 (manual) | v5.0 (optimizado) |
|---------|---------------|-------------------|
| **Queries** | 6 separadas | 1 unificada |
| **Análisis** | Manual (lectura fila por fila) | Automatizado (LLM) |
| **Citas** | Copiadas manualmente | Extraídas por LLM |
| **Validación** | Manual (riesgo error) | Automática |
| **Tiempo** | 40 min | 6 min |

### Beneficios

1. ✅ **85% menos tiempo** sin pérdida de calidad
2. ✅ **100% CASE_IDs reales** (validación automática)
3. ✅ **Cobertura ≥80% garantizada** (forzada por prompt)
4. ✅ **Citas textuales exactas** (extraídas del CSV)
5. ✅ **Escalable** (agregar más procesos no multiplica tiempo)

---

## 📚 **Archivos de Referencia**

- **Query SQL:** `sql/ejemplo_muestreo_unificado_pdd_mla_dic_2025.sql`
- **Prompt LLM:** `templates/ejemplo_prompt_defectuoso_flex.md`
- **Validación:** `templates/ejemplo_validacion_json.py`
- **Template SQL:** `sql/templates/muestreo_unificado_template.sql`
- **Template Prompt:** `templates/prompt_analisis_conversaciones.md`

---

## 🚀 **Próximos Pasos**

1. **Probá este workflow** en tu próximo análisis
2. **Medí el tiempo** y comparalo
3. **Iterá** si encontrás mejoras
4. **Compartí feedback** para versiones futuras

---

**Versión:** v5.0  
**Caso:** PDD MLA Nov-Dic 2025 (ejemplo real)  
**Tiempo total:** 6 minutos (vs 40 minutos v4.0)  
**Reducción:** 🚀 85%
