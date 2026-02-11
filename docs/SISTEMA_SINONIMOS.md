# Sistema de Consolidación de Causas Raíz con Auto-Aprendizaje

**Versión:** 1.0  
**Fecha:** 6 Febrero 2026  
**Estado:** Implementado

---

## Problema Resuelto

En análisis comparativos de CR, frecuentemente aparecen causas raíz que son **semánticamente equivalentes pero con redacción diferente**:

| P1 | P2 |
|----|-----|
| "Cancelación por arrepentimiento o compra errónea" | "Cancelación por arrepentimiento o producto no necesario" |
| "Demora o incumplimiento en fecha de entrega prometida" | "Demora en fecha de entrega" |

Esto generaba:
- Reportes con causas duplicadas
- Dificultad para comparar tendencias entre períodos
- Insights fragmentados

---

## Solución Implementada

### Componentes

| Archivo | Descripción |
|---------|-------------|
| `config/causas_sinonimos.py` | Módulo principal con lógica de consolidación |
| `config/causas_biblioteca_aprendida.json` | Biblioteca persistente de sinónimos aprendidos |
| `config/__init__.py` | Exports del paquete config |

### Flujo de Consolidación

```
1. Análisis P1 genera: causas_p1 = [causa_A1, causa_B1, causa_C1]
2. Análisis P2 genera: causas_p2 = [causa_A2, causa_B2, causa_D2]
                                    ↓
3. consolidar_causas_similares(causas_p1, causas_p2)
                                    ↓
4. Por cada causa de P1:
   - Buscar match en sinónimos conocidos
   - Calcular similaridad de texto con causas P2
   - Detectar palabras clave comunes
                                    ↓
5. Si match encontrado:
   - Unificar bajo nombre canónico
   - Combinar métricas de ambos períodos
   - Registrar para aprendizaje (si es nueva)
                                    ↓
6. Resultado: causas_consolidadas = [
     {causa: "nombre_canónico", pct_p1: X, pct_p2: Y, ...}
   ]
```

---

## Métodos de Detección

### 1. Grupo Conocido (score: 1.0)
Usa diccionario `SINONIMOS_SEMILLA` con variantes predefinidas:

```python
SINONIMOS_SEMILLA = {
    "arrepentimiento": {
        "nombre_canonico": "Cancelación por arrepentimiento del comprador",
        "variantes": [
            "cancelación por arrepentimiento",
            "arrepentimiento o compra errónea",
            "arrepentimiento o producto no necesario",
            ...
        ]
    }
}
```

### 2. Similaridad Alta (score >= 0.80)
Usa `difflib.SequenceMatcher` para comparar texto normalizado.

### 3. Palabras Comunes (score >= 0.65 + 2 palabras)
Detecta palabras significativas compartidas (ignorando stopwords).

### 4. Palabras Clave (score >= 0.50 + match de grupo)
Usa diccionario `PALABRAS_CLAVE` para detectar temas:

```python
PALABRAS_CLAVE = {
    "arrepentimiento": ["arrepent", "error", "errone", "no necesit"],
    "tracking": ["seguimiento", "tracking", "actualiz", "rastreo"],
    "demora": ["demor", "retras", "tard", "incumpl"],
    ...
}
```

---

## Auto-Aprendizaje

### Flujo de Retroalimentación

```
Nueva similitud detectada
         ↓
   score >= 0.80?
   /           \
 SÍ             NO
  ↓              ↓
Auto-confirmar  Agregar a "pendientes"
  ↓              ↓
Agregar a      Revisar manualmente
"confirmados"
  ↓
Disponible en próximos análisis
```

### Estructura de Biblioteca

```json
{
  "version": "1.0",
  "ultima_actualizacion": "2026-02-06T12:34:56",
  "confirmados": {
    "auto_20260206_123456": {
      "nombre_canonico": "Causa consolidada",
      "variantes": ["variante_1", "variante_2"],
      "auto_detectado": true,
      "score_original": 0.85
    }
  },
  "pendientes": [
    {
      "causas": ["causa_1", "causa_2"],
      "score": 0.72,
      "metodo": "palabras_comunes",
      "fecha_deteccion": "2026-02-06T12:34:56"
    }
  ],
  "rechazados": []
}
```

---

## Uso en Scripts

### Desde `generar_analisis_comparativo_desde_separados.py`

El script automáticamente:
1. Importa el módulo de sinónimos
2. Llama `consolidar_causas_similares(causas_p1, causas_p2)`
3. Guarda causas consolidadas en el JSON de salida
4. Persiste nuevos aprendizajes con `finalizar_aprendizaje()`

### Uso Directo

```python
from config.causas_sinonimos import (
    consolidar_causas_similares,
    finalizar_aprendizaje,
    obtener_gestor
)

# Consolidar causas
causas_p1 = [{"causa": "texto1", "porcentaje": 20, ...}]
causas_p2 = [{"causa": "texto2", "porcentaje": 25, ...}]

consolidadas = consolidar_causas_similares(causas_p1, causas_p2)

# Guardar aprendizajes de la sesión
n = finalizar_aprendizaje()
print(f"{n} nuevas similitudes detectadas")
```

---

## Configuración

### Umbrales

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `UMBRAL_SIMILARIDAD` | 0.65 | Mínimo para considerar candidato |
| `UMBRAL_CONFIRMADO` | 0.80 | Auto-confirmar como sinónimo |
| `MIN_PALABRAS_COMUNES` | 2 | Mínimo de palabras en común |

### Agregar Sinónimos Manualmente

Editar `config/causas_sinonimos.py`:

```python
SINONIMOS_SEMILLA = {
    # Agregar nuevo grupo
    "nuevo_grupo": {
        "nombre_canonico": "Nombre canónico del grupo",
        "variantes": [
            "variante 1",
            "variante 2",
            "variante 3"
        ]
    }
}
```

### Confirmar Pendientes

1. Revisar `config/causas_biblioteca_aprendida.json`
2. Mover de `pendientes` a `confirmados`
3. Asignar `nombre_canonico` descriptivo

---

## Output Esperado

### Antes (sin consolidación)
```
P1: "Cancelación por arrepentimiento o compra errónea" - 20%
P2: "Cancelación por arrepentimiento o producto no necesario" - 20%
→ Aparecen como 2 causas distintas
```

### Después (con consolidación)
```
"Cancelación por arrepentimiento del comprador"
  - P1: 20% (100 casos)
  - P2: 20% (150 casos)
  - Var: +50 casos (+50.0%)
→ Una sola causa con datos de ambos períodos
```

---

## Test del Módulo

```powershell
py config\causas_sinonimos.py
```

Resultado esperado:
```
================================================================================
TEST: Gestor de Sinónimos con Auto-Aprendizaje
================================================================================

[OK] SIMILARES (score: 1.00, metodo: grupo_conocido)
  1: Cancelación por arrepentimiento o compra errónea...
  2: Cancelación por arrepentimiento o producto no necesario...

Resultado: 3 causas consolidadas (de 3 + 3 originales)
[OK] 0 nuevas similitudes registradas
```

---

## Changelog

### v1.0 (2026-02-06)
- Implementación inicial
- Diccionario semilla con 8 grupos de causas
- Auto-aprendizaje con persistencia JSON
- Integración con script comparativo
