# Ejemplo Concreto - Prompt para Defectuoso - Flex

## Contexto
Este es el prompt REAL que enviarías al LLM para analizar las 100 conversaciones de "Defectuoso - Flex" en Diciembre 2025.

---

## Prompt Completo

```
Eres un analista experto en Customer Experience de MercadoLibre.

Analiza estas 100 conversaciones del proceso "Defectuoso - Flex" del commerce group "PDD":

**CONVERSACIONES (100 casos):**

1. CASE_ID: 426491524 | Fecha: 2025-12-30
   "El comprador reporta que el producto pierde agua en la unión de la base con los laterales del recipiente. Solicita la devolución del producto y menciona que lo necesita por recomendación de su odontólogo. El vendedor confirma que se consultará la disponibilidad de repuestos para un cambio. Posteriormente, se habilita la devolución, pero el producto llega incompleto. El agente procesa un reembolso completo de manera excepcional y cierra el caso, agradeciendo la paciencia del comprador."

2. CASE_ID: 426253719 | Fecha: 2025-12-29
   "La compradora reportó que el aro inflable se desinfla rápidamente y no funciona, solicitando un cambio o la devolución del dinero. A pesar de que el vendedor inicialmente ofreció un cambio, luego indicó que no era posible, lo que generó confusión y frustración en la compradora. El agente de Mercado Libre intervino y confirmó que el vendedor no podía realizar el cambio. Se generó un código QR para la devolución gratuita del producto, y se informó a la compradora que recibiría un reembolso tras la devolución. Finalmente, el reclamo fue cerrado y se reembolsó el dinero a la compradora."

3. CASE_ID: 426206485 | Fecha: 2025-12-29
   "El usuario tuvo problemas con un producto defectuoso que no cumplía con sus expectativas y no pudo realizar la devolución a tiempo, ya que el producto fue rechazado en la agencia de devoluciones. El agente de Mercado Libre generó una etiqueta de devolución y guió al usuario en el proceso. Se acordó que el usuario podía devolver el producto de forma gratuita y recibir un reembolso. Finalmente, el reclamo fue cerrado y el reembolso fue procesado correctamente."

4. CASE_ID: 426645934 | Fecha: 2025-12-30
   "El comprador recibió una pileta inflable dañada, con parches y agujeros, y no obtuvo respuesta del vendedor tras reportar el problema. El agente de Mercado Libre generó un código QR para la devolución gratuita del producto. El comprador siguió el proceso de devolución, embalaron la pileta y la enviaron al vendedor. Tras recibir el producto, el reclamo fue cerrado y se reembolsó el dinero al comprador."

5. CASE_ID: 426235237 | Fecha: 2025-12-29
   "El comprador recibió un pedido con el embalaje roto y un frasco dañado. Se contactó con el vendedor para buscar una solución, ya que no podía acercarse a un punto de retiro debido a su trabajo. El agente de Mercado Libre generó una etiqueta de devolución gratuita y ofreció un reembolso completo de $14.999,00 sin necesidad de devolver el producto. El comprador aceptó la solución y se cerró el reclamo."

[... continuar hasta las 100 conversaciones ...]

---

**TAREA (sin cantidad fija):**
1. Identifica **causas raíz** lo más ESPECÍFICAS posible (no genéricas).
2. Ordénalas por frecuencia hasta que la suma alcance **≥80%** de las menciones.
3. Para cada causa, estima:
   - Frecuencia absoluta (X/100 conversaciones)
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
{
  "proceso": "Defectuoso - Flex",
  "total_conversaciones": 100,
  "causas": [
    {
      "descripcion": "Descripción ESPECÍFICA de la causa raíz",
      "frecuencia_absoluta": 42,
      "frecuencia_porcentaje": 42.0,
      "case_ids_ejemplo": ["426491524", "426253719", "426645934"],
      "citas": [
        {
          "caso_id": "426491524", 
          "texto": "El comprador reporta que el producto pierde agua en la unión de la base con los laterales del recipiente"
        },
        {
          "caso_id": "426253719", 
          "texto": "La compradora reportó que el aro inflable se desinfla rápidamente y no funciona"
        }
      ],
      "sentimiento": {
        "frustracion": 72,
        "satisfaccion_post_resolucion": 65
      }
    }
  ],
  "cobertura": {
    "target_pct": 80.0,
    "covered_pct": 82.0,
    "remainder_pct": 18.0
  },
  "hallazgo_principal": "42% de los casos corresponden a productos defectuosos de fábrica que llegaron con fallas de funcionamiento, concentrados en los días posteriores a Navidad (29-30 dic), sugiriendo presión operativa en centros Flex durante alta demanda."
}

**IMPORTANTE:**
- Los porcentajes son sobre la muestra analizada (100 casos)
- La suma de frecuencia_porcentaje debe ser ≥80%
- Sé específico, no genérico
- No inventes CASE_IDs ni citas

Responde SOLO con el JSON, sin texto adicional.
```

---

## Output Esperado del LLM

```json
{
  "proceso": "Defectuoso - Flex",
  "total_conversaciones": 100,
  "causas": [
    {
      "descripcion": "Productos defectuosos de fábrica - fallas de funcionamiento (aro se desinfla, lápiz 3D no funciona, tóner no imprime)",
      "frecuencia_absoluta": 42,
      "frecuencia_porcentaje": 42.0,
      "case_ids_ejemplo": ["426491524", "426253719", "426405269"],
      "citas": [
        {
          "caso_id": "426491524",
          "texto": "El comprador reporta que el producto pierde agua en la unión de la base con los laterales del recipiente"
        },
        {
          "caso_id": "426253719",
          "texto": "La compradora reportó que el aro inflable se desinfla rápidamente y no funciona"
        }
      ],
      "sentimiento": {
        "frustracion": 75,
        "satisfaccion_post_resolucion": 68
      }
    },
    {
      "descripcion": "Productos dañados en transporte - embalaje roto, producto mojado o golpeado durante envío post-Navidad",
      "frecuencia_absoluta": 38,
      "frecuencia_porcentaje": 38.0,
      "case_ids_ejemplo": ["426235237", "426322915", "426334137"],
      "citas": [
        {
          "caso_id": "426235237",
          "texto": "El comprador recibió un pedido con el embalaje roto y un frasco dañado"
        },
        {
          "caso_id": "426322915",
          "texto": "El pedido llegó tarde, con el empaque y producto mojados y con olor a humedad"
        }
      ],
      "sentimiento": {
        "frustracion": 68,
        "satisfaccion_post_resolucion": 62
      }
    },
    {
      "descripcion": "Incompatibilidad de producto - error en selección o descripción del vendedor",
      "frecuencia_absoluta": 12,
      "frecuencia_porcentaje": 12.0,
      "case_ids_ejemplo": ["426584283"],
      "citas": [
        {
          "caso_id": "426584283",
          "texto": "El vendedor argumentó que el comprador se había equivocado de modelo y que el tóner no era compatible con su impresora"
        }
      ],
      "sentimiento": {
        "frustracion": 80,
        "satisfaccion_post_resolucion": 55
      }
    },
    {
      "descripcion": "Falta de respuesta del vendedor - promete cambio pero no envía, deja de responder mensajes",
      "frecuencia_absoluta": 8,
      "frecuencia_porcentaje": 8.0,
      "case_ids_ejemplo": ["426514189", "426645934"],
      "citas": [
        {
          "caso_id": "426514189",
          "texto": "El vendedor finalmente envió el producto y la compradora lo recibió"
        },
        {
          "caso_id": "426645934",
          "texto": "El comprador recibió una pileta inflable dañada, con parches y agujeros, y no obtuvo respuesta del vendedor tras reportar el problema"
        }
      ],
      "sentimiento": {
        "frustracion": 85,
        "satisfaccion_post_resolucion": 70
      }
    }
  ],
  "cobertura": {
    "target_pct": 80.0,
    "covered_pct": 100.0,
    "remainder_pct": 0.0
  },
  "hallazgo_principal": "80% de los casos concentrados en productos defectuosos de fábrica (42%) y dañados en transporte (38%), con patrón temporal en días 29-30 dic (post-Navidad), sugiriendo presión operativa en centros Flex durante despachos de alta demanda."
}
```

---

## Notas
- Este prompt incluiría las 100 conversaciones completas (aquí solo mostré 5 como ejemplo)
- El LLM respondería en ~30 segundos con este JSON estructurado
- Luego validarías los CASE_IDs y lo insertarías en el HTML
