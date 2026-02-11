# 🤖 Template de Prompt - Análisis de Conversaciones con LLM

## Propósito

Este prompt está diseñado para analizar conversaciones de atención al cliente y extraer:
- **Causas raíz específicas** (no genéricas)
- **Frecuencias exactas** con cobertura ≥80%
- **Citas textuales reales** con CASE_IDs
- **Sentimiento** (frustración/satisfacción)

---

## 📊 Parámetros a reemplazar

- `{PROCESS_NAME}` → Nombre del proceso analizado (ej: "Defectuoso - Flex")
- `{N}` → Cantidad de conversaciones en la muestra (ej: 100)
- `{CSV_DATA_PROCESO}` → Datos del CSV en formato estructurado (ver formato abajo)
- `{COMMERCE_GROUP}` → Grupo de commerce (ej: "PDD")

---

## 🎯 Prompt Template

```markdown
Eres un analista experto en Customer Experience de MercadoLibre.

**⚠️ VALIDACIÓN PREVIA:**
- Se requiere un MÍNIMO de 10 conversaciones para realizar análisis válido
- Si N < 10: Retornar JSON con estado "MUESTRA_INSUFICIENTE" y sin causas

Analiza estas {N} conversaciones del proceso "{PROCESS_NAME}" del commerce group "{COMMERCE_GROUP}":

**CONVERSACIONES ({N} casos):**

{CSV_DATA_PROCESO}

---

**TAREA (sin cantidad fija):**
1. Identifica **causas raíz** lo más ESPECÍFICAS posible (no genéricas).
2. Ordénalas por frecuencia hasta que la suma alcance **≥80%** de las menciones.
3. Para cada causa, estima:
   - Frecuencia absoluta (X/{N} conversaciones)
   - Porcentaje (%)
   - CASE_IDs de ejemplo (usar IDs reales del texto arriba)
4. Extrae 2-3 citas textuales representativas por causa.
5. Estima sentimiento por causa (frustración % / satisfacción post-resolución %).

**CRITERIOS CRÍTICOS:**
- Ser MUY ESPECÍFICO:
  - ❌ "Problemas de entrega" 
  - ✅ "Productos dañados por mal embalaje en despachos post-Navidad"
  - ❌ "Consultas sobre producto" 
  - ✅ "Validación de fotos rechazada por formato incorrecto"
- Solo incluir causas con ≥3 menciones en la muestra
- Los CASE_IDs deben ser reales (de los mostrados arriba)
- Las citas deben ser fragmentos exactos de las conversaciones (no parafrasear)
- Los porcentajes deben sumar ≥80% (idealmente ~100% incluyendo remanente "Otros")

**FORMATO DE RESPUESTA (JSON estricto):**

⚠️ **CRÍTICO - REGLAS DE LONGITUD:**
1. `"causa"`: Máximo 6-10 palabras (título ejecutivo)
2. `"descripcion"`: 1-2 oraciones, 20-30 palabras (contexto específico)
3. **NO duplicar texto entre "causa" y "descripcion"**
4. `"sentimiento"`: Formato string "X% frustración, Y% satisfacción"
5. `"cobertura"`: Número simple (no objeto)

{
  "proceso": "{PROCESS_NAME}",
  "total_conversaciones": {N},
  "causas": [
    {
      "causa": "Título corto de la causa raíz (6-10 palabras)",
      "porcentaje": 42,
      "casos_estimados": 42,  // ← round((porcentaje / 100) × total_conversaciones). Frecuencia REAL de la muestra, NO extrapolar a incoming total.
      "descripcion": "Contexto específico en 1-2 oraciones (20-30 palabras). No repetir la causa.",
      "citas": [
        {
          "case_id": "CASE_ID_1", 
          "texto": "Fragmento textual exacto de la conversación"
        },
        {
          "case_id": "CASE_ID_2", 
          "texto": "Otro fragmento textual exacto"
        }
      ],
      "sentimiento": "72% frustración, 28% satisfacción"
    }
  ],
  "cobertura": 100,
  "hallazgo_principal": "Resumen ejecutivo de 1-2 frases con el patrón dominante"
}

**EJEMPLOS DE FORMATO CORRECTO:**

✅ **BUENO:**
```json
{
  "causa": "Reembolso procesado pero no reflejado en cuenta",
  "descripcion": "Usuarios reportan que ML procesó el reembolso pero el dinero no aparece en su cuenta bancaria. ML indica que el banco debe acreditar."
}
```

✅ **BUENO:**
```json
{
  "causa": "Colectas no realizadas por falta de espacio",
  "descripcion": "Vendedores con alto volumen reportan colectas parciales o canceladas por falta de espacio en camión. Solicitan exclusión masiva."
}
```

✅ **BUENO:**
```json
{
  "causa": "Demoras por cambios de horario sin aviso",
  "descripcion": "Vendedores reportan modificaciones de horarios de colecta sin notificación previa, generando demoras masivas en múltiples ventas simultáneas."
}
```

❌ **MALO (causa demasiado larga):**
```json
{
  "causa": "Vendedores con alto volumen reportan que las colectas no se realizaron o fueron parciales por falta de espacio"
}
```

❌ **MALO (texto duplicado):**
```json
{
  "causa": "Reembolso procesado pero no reflejado",
  "descripcion": "Reembolso procesado pero no reflejado en cuenta bancaria"
}
```

❌ **MALO (descripción demasiado genérica):**
```json
{
  "causa": "Problemas con reputación",
  "descripcion": "Usuarios tienen problemas con su reputación"
}
```

**IMPORTANTE:**
- Los porcentajes son sobre la muestra analizada ({N} casos)
- La suma de porcentajes debe ser ≥80%
- `"causa"` debe ser concisa (6-10 palabras)
- `"descripcion"` debe agregar contexto específico (no repetir causa)
- Sé específico, no genérico
- No inventes CASE_IDs ni citas

Responde SOLO con el JSON, sin texto adicional.
```

---

## 📝 Formato de `{CSV_DATA_PROCESO}`

Formatear las conversaciones del CSV así:

```
1. CASE_ID: 426491524 | Fecha: 2025-12-30
   "El comprador reporta que el producto pierde agua en la unión de la base con los laterales del recipiente. Solicita la devolución del producto y menciona que lo necesita por recomendación de su odontólogo..."

2. CASE_ID: 426253719 | Fecha: 2025-12-29
   "La compradora reportó que el aro inflable se desinfla rápidamente y no funciona, solicitando un cambio o la devolución del dinero..."

[... continuar hasta las {N} conversaciones ...]
```

**Notas:**
- Limitar cada conversación a ~200 caracteres para no exceder límite de tokens
- Si hay >50 conversaciones, usar sample representativo de 50 y aclarar en el prompt

---

## ⚙️ Parámetros del LLM

**Modelo recomendado:** `gpt-4o-mini` o `claude-sonnet-3.5`
- **Ventaja:** Rápido (~30s), económico, preciso para tareas estructuradas

**Configuración:**
```python
{
  "model": "gpt-4o-mini",
  "temperature": 0.3,         # Balance precisión/creatividad
  "max_tokens": 4096,         # Suficiente para JSON estructurado
  "response_format": "json"   # Forzar output JSON (si disponible)
}
```

**System prompt:**
```
"Eres un analista de datos experto. Respondes solo en formato JSON válido."
```

**Max retries:** 2 (con backoff exponencial)

---

## ✅ Validación del Output

Después de recibir el JSON del LLM, validar:

```python
# 1. Parsear JSON
try:
    result = json.loads(llm_response)
except:
    # Fallback: análisis manual

# 2. Verificar estructura
assert 'causas' in result
assert 'cobertura' in result
assert len(result['causas']) > 0

# 3. Verificar CASE_IDs reales
for causa in result['causas']:
    for case_id in causa['case_ids_ejemplo']:
        if case_id not in df['CAS_CASE_ID'].astype(str).values:
            # Reemplazar con CASE_ID real del CSV
            causa['case_ids_ejemplo'] = [df.sample(1)['CAS_CASE_ID'].iloc[0]]

# 4. Verificar cobertura ≥80%
if result['cobertura']['covered'] < 80:
    # Agregar causa "Otros / Volumétrico"
    result['causas'].append({
        "descripcion": "Otros / Volumétrico",
        "frecuencia_porcentaje": result['cobertura']['remainder']
    })

# 5. Verificar suma de porcentajes
total_pct = sum([c['frecuencia_porcentaje'] for c in result['causas']])
if abs(total_pct - 100) > 10:
    # Recalcular proporcionalmente
    for causa in result['causas']:
        causa['frecuencia_porcentaje'] = (causa['frecuencia_porcentaje'] / total_pct) * 100
```

---

## 🚀 Ejemplo de Uso Completo

```python
# 1. Leer CSV de muestreo unificado
df = pd.read_csv('output/muestreo_unificado.csv')

# 2. Filtrar por proceso
proceso = "Defectuoso - Flex"
df_proceso = df[df['PROCESS_NAME'] == proceso]

# 3. Formatear conversaciones
csv_data = ""
for i, row in df_proceso.iterrows():
    csv_data += f"{i+1}. CASE_ID: {row['CAS_CASE_ID']} | Fecha: {row['FECHA_CONTACTO']}\n"
    csv_data += f'   "{row['CONVERSATION_SUMMARY'][:200]}..."\n\n'

# 4. Reemplazar placeholders en prompt
prompt = PROMPT_TEMPLATE.replace('{PROCESS_NAME}', proceso)
prompt = prompt.replace('{N}', str(len(df_proceso)))
prompt = prompt.replace('{CSV_DATA_PROCESO}', csv_data)
prompt = prompt.replace('{COMMERCE_GROUP}', 'PDD')

# 5. Llamar a LLM
response = llm_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un analista de datos experto. Respondes solo en JSON válido."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

# 6. Parsear y validar
result = json.loads(response.choices[0].message.content)
# ... validaciones ...

# 7. Usar en reporte HTML
for causa in result['causas']:
    html += f"<li><strong>{causa['descripcion']}</strong> ({causa['frecuencia_porcentaje']}%)</li>"
```

---

## 📚 Referencias

- **Inspirado en:** `docs/V37.ipynb` - función `analyze_conversations_with_gpt_v11()`
- **Reglas de Oro:** `.cursorrules` - Regla #9 (v5.0)
- **Query relacionada:** `sql/templates/muestreo_unificado_template.sql`

---

## 🎯 Métricas de Éxito

| Métrica | Target | Actual (ejemplo) |
|---------|--------|------------------|
| **Conversaciones mínimas** | **≥10** | **Validación automática** |
| Tiempo de análisis | <45s | ~30s |
| Cobertura | ≥80% | 82% |
| CASE_IDs válidos | 100% | 100% |
| Citas textuales | ≥2 por causa | 2-3 |
| Especificidad | Alta | ✅ "Productos dañados post-Navidad" |

**⚠️ Nota sobre Umbral Mínimo:**
- Con **< 10 conversaciones**: Se reporta automáticamente como "Muestra insuficiente"
- Con **≥ 10 conversaciones**: Análisis válido y concluyente
- El sistema valida esto ANTES de llamar al LLM para evitar análisis inválidos
