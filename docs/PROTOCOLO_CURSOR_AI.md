# 🤖 Protocolo de Análisis con Cursor AI (v6.3.6)

**Versión:** 1.0
**Fecha:** 4 Febrero 2026

Este documento describe el protocolo completo para generar análisis de conversaciones usando Cursor AI en el flujo v6.3.6.

---

## 🎯 Objetivo

Generar un único reporte HTML con análisis de conversaciones completo, usando **solo Cursor AI** (sin API keys externas).

---

## 🚀 Flujo de Ejecución Obligatorio (v6.3.6 - AUTOMÁTICO)

### ⭐ NUEVO: Flujo Completamente Automático (Una Sola Ejecución)

**Comando único (TODO automático):**
```bash
py generar_reporte_cr_universal_v6.3.6.py \
  --site {SITE} \
  --p1-start {P1_START} --p1-end {P1_END} \
  --p2-start {P2_START} --p2-end {P2_END} \
  --commerce-group {COMMERCE_GROUP} \
  --aperturas {APERTURAS} \
  --open-report
```

**El script hace TODO automáticamente:**
1. ✅ Calcula métricas cuantitativas
2. ✅ Exporta CSVs de conversaciones
3. ✅ **ESPERA AUTOMÁTICAMENTE** (polling cada 5 seg) hasta detectar JSON
4. ✅ Muestra prompt claro para que solicites análisis a Cursor AI
5. ✅ Cuando detecta el JSON → recarga análisis automáticamente
6. ✅ Genera HTML completo con análisis comparativo
7. ✅ Abre navegador automáticamente

**TU ACCIÓN (mientras el script espera):**
1. Copiar el prompt que el script muestra
2. Pegarlo a Cursor AI (en chat)
3. Esperar a que genere el JSON
4. El script detecta automáticamente y continúa

**Resultado esperado:**
```
✅ [OK] JSON detectado: analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
[CONTINUANDO] Cargando análisis y generando reporte completo...

[SUCCESS] Análisis completado exitosamente para 3 elementos

[HTML] Generando reporte HTML...
[OK] Reporte guardado: reporte_cr_loyalty_mlm_ago_sep_2025_v6.3.html
🌐 Abriendo reporte en navegador...
```

---

## 📋 Casos Especiales

### Caso 1: JSON ya existe (`tiene_analisis_previo == True`)

```bash
# Ejecución inmediata (sin espera)
py generar_reporte_cr_universal_v6.3.6.py ... --open-report

# El script:
# - Detecta JSON existente
# - NO entra en modo de espera
# - Genera HTML directamente
# ⏱️ Tiempo: ~3-5 min (sin polling)
```

### Caso 2: Solo exportar (sin HTML)

```bash
# Modo export-only (sin espera, sin HTML)
py generar_reporte_cr_universal_v6.3.6.py ... --export-only

# El script:
# - Exporta CSVs
# - Sale inmediatamente (sin espera)
```

---

## 📝 Formato del JSON de Análisis (Estándar Obligatorio)

### ⚠️ REGLAS DE LONGITUD OBLIGATORIAS:
- ✅ `"causa"`: 6-10 palabras máximo (título ejecutivo conciso)
- ✅ `"descripcion"`: 1-2 oraciones, 20-30 palabras (contexto específico sin duplicar la causa)
- ❌ NO duplicar texto entre "causa" y "descripcion"
- ⚠️ Usar `"causas"` (no `"causas_raiz"`) para compatibilidad con script v6.3.6

### Ejemplos de formato CORRECTO:

#### ✅ BUENO:
```json
{
  "causa": "Reembolso procesado pero no reflejado en cuenta",
  "descripcion": "Usuarios reportan que ML procesó el reembolso pero el dinero no aparece en su cuenta bancaria. ML indica que el banco debe acreditar."
}
```

#### ✅ BUENO:
```json
{
  "causa": "Colectas no realizadas por falta de espacio",
  "descripcion": "Vendedores con alto volumen reportan colectas parciales o canceladas por falta de espacio en camión. Solicitan exclusión masiva de impacto en reputación."
}
```

#### ❌ MALO (causa demasiado larga):
```json
{
  "causa": "Vendedores con alto volumen reportan que las colectas no se realizaron o fueron parciales por falta de espacio en el camión"
}
```

#### ❌ MALO (texto duplicado entre causa y descripción):
```json
{
  "causa": "Reembolso procesado pero no reflejado",
  "descripcion": "Reembolso procesado pero no reflejado en cuenta bancaria"
}
```

### Estructura JSON completa:

```json
{
  "Elemento Priorizado 1": {
    "proceso": "Nombre del Elemento",
    "commerce_group": "PDD|PNR|etc",
    "site": "MLA|MLB|etc",
    "periodo": "Nov-Dic 2025",
    "total_conversaciones": 60,
    "causas": [
      {
        "causa": "Título corto de 6-10 palabras",
        "porcentaje": 45,
        "casos_estimados": 27,
        "descripcion": "Contexto específico de 20-30 palabras máximo. No duplicar la causa.",
        "citas": [
          {
            "case_id": "123456789",
            "texto": "Cita textual"
          }
        ],
        "sentimiento": "60% frustración, 40% neutral"
      }
    ],
    "cobertura": 100,
    "hallazgo_principal": "Resumen ejecutivo del hallazgo"
  }
}
```

---

## 🔄 Análisis Comparativo v3.0 (Detección Real de Patrones)

### ⚠️ NUEVO: Para análisis comparativos mejorados

Ver documentación completa en: `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`

**Características:**
- Detecta patrones POR PERÍODO (no división proporcional)
- Clasifica: PERSISTENTE / NUEVO / DESAPARECE
- Máximo 4-5 causas raíz priorizadas
- Porcentajes reales sobre muestra

**Formato JSON v3.0:**
```json
{
  "Elemento": {
    "proceso": "Nombre",
    "causas": [
      {
        "causa": "Título",
        "patron": "PERSISTENTE | NUEVO | DESAPARECE",
        "frecuencia_p1": 12,
        "porcentaje_p1": 40,
        "frecuencia_p2": 15,
        "porcentaje_p2": 50,
        "citas_p1": [ ... ],
        "citas_p2": [ ... ],
        "sentimiento_p1": { "frustracion": 75, ... },
        "sentimiento_p2": { "frustracion": 80, ... }
      }
    ]
  }
}
```

---

## 📊 Template de Prompt (Análisis Básico)

**Ubicación:** `templates/prompt_analisis_conversaciones.md`

**Variables a reemplazar:**
- `{PROCESS_NAME}`: Nombre del proceso
- `{N}`: Cantidad de conversaciones
- `{CSV_DATA_PROCESO}`: Conversaciones formateadas
- `{COMMERCE_GROUP}`: Grupo de commerce

**Ejemplo de uso:**
```python
with open('templates/prompt_analisis_conversaciones.md', 'r') as f:
    prompt_template = f.read()

prompt = prompt_template.replace('{PROCESS_NAME}', 'Arrepentimiento')
prompt = prompt.replace('{N}', '30')
prompt = prompt.replace('{CSV_DATA_PROCESO}', csv_data)
prompt = prompt.replace('{COMMERCE_GROUP}', 'PDD')

# Copiar prompt y pegar en Cursor AI
```

---

## 📊 Template de Prompt (Análisis Comparativo v3.0)

**Ubicación:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`

**Variables a reemplazar:**
- `{PROCESS_NAME}`: Nombre del proceso
- `{PERIODO_P1}`: Nombre del período 1 (ej: "Noviembre 2025")
- `{PERIODO_P2}`: Nombre del período 2 (ej: "Diciembre 2025")
- `{N_P1}`: Cantidad de conversaciones P1
- `{N_P2}`: Cantidad de conversaciones P2
- `{CSV_DATA_P1}`: Conversaciones P1
- `{CSV_DATA_P2}`: Conversaciones P2
- `{COMMERCE_GROUP}`: Grupo de commerce
- `{SITE}`: Site

**Uso automático:**
```bash
py scripts/generar_analisis_comparativo_directo.py \
    --site MLM \
    --commerce-group PAGOS \
    --p1-start 2025-12-01 --p1-end 2025-12-31 \
    --p2-start 2026-01-01 --p2-end 2026-01-31 \
    --aperturas CDU \
    --output output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json
```

Genera: `prompts_comparativos_mlm_pagos_202512_202601.txt` (listos para copiar)

---

## ✅ Validación del Output JSON

### Checklist de Validación Automática:

```python
def validar_json_analisis(json_data):
    """Valida estructura y calidad del JSON de análisis."""
    
    errores = []
    
    # 1. Parsear JSON
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
    except json.JSONDecodeError as e:
        return {'valido': False, 'errores': [f"JSON inválido: {str(e)}"]}
    
    # 2. Verificar estructura por elemento
    for elemento_key, elemento_data in data.items():
        # Campos obligatorios
        campos_requeridos = ['proceso', 'causas', 'cobertura', 'hallazgo_principal']
        for campo in campos_requeridos:
            if campo not in elemento_data:
                errores.append(f"{elemento_key}: falta campo '{campo}'")
        
        # Validar causas
        for i, causa in enumerate(elemento_data.get('causas', [])):
            # Longitud de "causa"
            if len(causa.get('causa', '').split()) > 10:
                errores.append(f"{elemento_key}, causa {i+1}: título demasiado largo (>10 palabras)")
            
            # Longitud de "descripcion"
            desc_words = len(causa.get('descripcion', '').split())
            if desc_words > 40:
                errores.append(f"{elemento_key}, causa {i+1}: descripción demasiado larga (>40 palabras)")
            
            # No duplicar texto
            if causa.get('causa', '').lower() in causa.get('descripcion', '').lower():
                errores.append(f"{elemento_key}, causa {i+1}: texto duplicado entre causa y descripción")
            
            # CASE_IDs reales
            for cita in causa.get('citas', []):
                if 'case_id' not in cita or 'texto' not in cita:
                    errores.append(f"{elemento_key}, causa {i+1}: cita sin case_id o texto")
        
        # Validar cobertura
        cobertura = elemento_data.get('cobertura', 0)
        if cobertura < 80:
            errores.append(f"{elemento_key}: cobertura insuficiente ({cobertura}%, mínimo 80%)")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }
```

### Validación Manual (Checklist):

- [ ] JSON válido (parseable)
- [ ] Todos los elementos tienen `proceso`, `causas`, `cobertura`, `hallazgo_principal`
- [ ] Cada causa tiene título corto (6-10 palabras)
- [ ] Cada causa tiene descripción (20-30 palabras)
- [ ] No hay texto duplicado entre causa y descripción
- [ ] CASE_IDs son reales (del CSV original)
- [ ] Citas son textuales (no parafraseadas)
- [ ] Cobertura ≥80% por elemento
- [ ] Sentimiento en formato correcto

---

## 🔧 Troubleshooting

### Problema 1: JSON no se genera

**Síntomas:**
- Cursor AI no responde con JSON
- Respuesta en texto plano

**Solución:**
1. Verificar que el prompt incluya "Responde SOLO con el JSON"
2. Copiar el prompt completo (no parcial)
3. Si persiste, pedir explícitamente: "Dame solo el JSON, sin texto adicional"

### Problema 2: JSON con formato incorrecto

**Síntomas:**
- Faltan campos obligatorios
- Estructura diferente a la esperada

**Solución:**
1. Verificar que el template de prompt sea el correcto (v6.3.6)
2. Validar el JSON con herramienta online (jsonlint.com)
3. Corregir manualmente los campos faltantes

### Problema 3: Script no detecta el JSON

**Síntomas:**
- El script sigue en modo de espera
- JSON guardado pero no detectado

**Solución:**
1. Verificar nombre del archivo JSON (debe coincidir con patrón esperado)
2. Verificar que el JSON esté en carpeta `output/`
3. Verificar que el JSON sea válido (parseable)

### Problema 4: Citas sin CASE_IDs reales

**Síntomas:**
- CASE_IDs inventados o genéricos ("ejemplo1", "caso_1")

**Solución:**
1. Verificar que el CSV de conversaciones se pasó correctamente en el prompt
2. Indicar explícitamente: "Usa los CASE_IDs reales del CSV proporcionado"
3. Validar manualmente y reemplazar si es necesario

---

## 📚 Referencias

- **Template prompt básico:** `templates/prompt_analisis_conversaciones.md`
- **Template prompt comparativo:** `templates/prompt_analisis_conversaciones_comparativo_v2.md`
- **Script principal:** `generar_reporte_cr_universal_v6.3.6.py`
- **Análisis comparativo v3.0:** `docs/GUIA_ANALISIS_COMPARATIVO_v3.md`
- **Metodología completa:** `docs/METODOLOGIA_5_FASES.md#fase-3`

---

## 🎯 Métricas de Éxito

| Métrica | Target | Actual (v6.3.6) |
|---------|--------|-----------------|
| **Conversaciones mínimas** | **≥10 por período** | **Validación automática** |
| Tiempo de análisis por elemento | <60s | ~30s |
| Cobertura | ≥80% | 85-95% |
| CASE_IDs válidos | 100% | 100% |
| Citas textuales | ≥2 por causa | 2-3 |
| Especificidad | Alta | ✅ |

---

## 🎓 Mejores Prácticas

### 1. Siempre validar el CSV antes de generar prompt
```python
df = pd.read_csv('conversaciones_elemento.csv')
print(f"Conversaciones: {len(df)}")
print(f"Columnas: {df.columns.tolist()}")
print(f"CASE_IDs únicos: {df['CAS_CASE_ID'].nunique()}")
```

### 2. Usar el script generador de prompts (v3.0)
```bash
# Genera prompts automáticamente con formato correcto
py scripts/generar_analisis_comparativo_directo.py ...
```

### 3. Validar JSON antes de usarlo
```bash
# Validar JSON con Python
py -c "import json; json.load(open('output/analisis.json'))"
```

### 4. Revisar manualmente el primer análisis
- Verificar que las causas sean específicas (no genéricas)
- Confirmar que los CASE_IDs son reales
- Validar que las citas son textuales

### 5. Iterar si es necesario
- Si el análisis no es satisfactorio, ajustar el prompt
- Agregar ejemplos de formato correcto
- Especificar claramente lo que se espera

---

**Versión:** 1.0
**Autor:** CR Commerce Analytics Team
**Fecha:** 4 Febrero 2026
**Status:** ✅ PRODUCTION READY
