# 📋 Ejemplos de JSON de Análisis de Conversaciones

Este archivo contiene ejemplos reales de análisis bien estructurados para diferentes Commerce Groups. Usar como referencia al generar nuevos análisis.

---

## ✅ Ejemplo 1: Pagos (MLB) - "Pago devuelto"

**Commerce Group:** PAGOS  
**Site:** MLB  
**Período:** Dic 2025 - Ene 2026

```json
{
  "Pago devuelto ": {
    "proceso": "Pago devuelto ",
    "commerce_group": "PAGOS",
    "site": "MLB",
    "periodo": "Dic 2025 - Ene 2026",
    "total_conversaciones": 51,
    "causas": [
      {
        "causa": "Estorno processado mas não creditado na conta bancária",
        "porcentaje": 40,
        "casos_estimados": 20,
        "descripcion": "Usuarios reportan que el estorno fue procesado por ML pero no aparece en su cuenta. ML indica que el banco debe acreditar.",
        "citas": [
          {
            "case_id": "421367980",
            "fecha": "2025-12-08",
            "texto": "Elizangela está enfrentando dificuldades com um reembolso de R$23,89 que foi processado, mas não caiu em sua conta. O representante confirmou que o reembolso foi processado e enviou um comprovante."
          }
        ],
        "sentimiento": "75% frustración, 15% satisfacción"
      },
      {
        "causa": "Confusión sobre reembolso en Mercado Pago vs cuenta bancaria",
        "porcentaje": 30,
        "casos_estimados": 15,
        "descripcion": "Usuarios no entienden que el reembolso se acreditó en Mercado Pago y no en su tarjeta, o no saben cómo acceder al saldo.",
        "citas": [
          {
            "case_id": "426144756",
            "fecha": "2025-12-30",
            "texto": "Usuario tiene dudas sobre un reembolso que no ve en su tarjeta. El agente explicó que el dinero está en su cuenta de Mercado Pago."
          }
        ],
        "sentimiento": "60% frustración, 30% alivio"
      }
    ],
    "cobertura": 100,
    "hallazgo_principal": "La reducción de casos se explica por menor volumen de reembolsos pendientes, manteniéndose el patrón principal de usuarios esperando acreditación bancaria."
  }
}
```

**✅ Por qué es correcto:**
- ✅ "causa": 6-9 palabras (conciso)
- ✅ "descripcion": 20-26 palabras (contexto específico sin duplicar causa)
- ✅ Citas textuales con CASE_IDs reales
- ✅ Sentimiento en formato string
- ✅ Cobertura como número simple

---

## ✅ Ejemplo 2: Pagos (MLM) - "Pago devuelto"

**Commerce Group:** PAGOS  
**Site:** MLM  
**Período:** Dic 2025 - Ene 2026

```json
{
  "Pago devuelto ": {
    "proceso": "Pago devuelto ",
    "commerce_group": "PAGOS",
    "site": "MLM",
    "periodo": "Dic 2025 - Ene 2026",
    "total_conversaciones": 57,
    "causas": [
      {
        "causa": "Reembolso procesado pero no reflejado en cuenta bancaria",
        "porcentaje": 45,
        "casos_estimados": 26,
        "descripcion": "Usuarios reportan que Mercado Libre procesó el reembolso pero el dinero no aparece en su cuenta bancaria. ML indica que el banco debe acreditar.",
        "citas": [
          {
            "case_id": "423589151",
            "fecha": "2025-12-16",
            "texto": "El usuario no recibió el reembolso correspondiente a la proteína que había comprado. El representante confirmó que se procesaron dos reembolsos y explicó que el usuario debe contactar a su banco."
          }
        ],
        "sentimiento": "75% frustración, 15% satisfacción"
      }
    ],
    "cobertura": 100,
    "hallazgo_principal": "Patrón consistente con MLB: usuarios esperan reembolso en cuenta bancaria que ya fue procesado por ML pero depende de tiempos del banco."
  }
}
```

---

## ✅ Ejemplo 3: ME PreDespacho (MLA) - "HT - Ventas"

**Commerce Group:** ME_PREDESPACHO  
**Site:** MLA  
**Período:** Nov-Dic 2025

```json
{
  "HT - Ventas": {
    "proceso": "HT - Ventas",
    "commerce_group": "ME_PREDESPACHO",
    "site": "MLA",
    "periodo": "Nov-Dic 2025",
    "total_conversaciones": 60,
    "causas": [
      {
        "causa": "Demoras por problemas logísticos no atribuibles al vendedor",
        "porcentaje": 75,
        "casos_estimados": 45,
        "descripcion": "Vendedores reportan demoras por cambios de horario sin aviso, errores de escaneo del correo o problemas en Flex. Solicitan exclusión de su reputación.",
        "citas": [
          {
            "case_id": "415211231",
            "fecha": "2025-11-15",
            "texto": "Erich reportó que su reputación fue afectada por envíos que supuestamente despachó tarde, aunque tenía un correo que indicaba un horario diferente. Se generó una exclusión."
          }
        ],
        "sentimiento": "80% frustración, 15% alivio tras solución"
      },
      {
        "causa": "Feriados y horarios especiales sin blindaje automático",
        "porcentaje": 15,
        "casos_estimados": 9,
        "descripcion": "Vendedores tienen ventas que deben despachar en días feriados o con horarios cerrados, generando demoras automáticas. Solicitan protección de reputación.",
        "citas": [
          {
            "case_id": "417856792",
            "fecha": "2025-12-24",
            "texto": "El vendedor reporta ventas con plazo de despacho en día feriado sin posibilidad de despachar. Solicita extensión de plazo."
          }
        ],
        "sentimiento": "70% frustración, 20% neutral"
      }
    ],
    "cobertura": 100,
    "hallazgo_principal": "El aumento de casos se debe principalmente a problemas logísticos de ME (cambios de horario, errores de escaneo) que afectan la reputación del vendedor de forma injusta."
  }
}
```

---

## ✅ Ejemplo 4: PDD (MLA) - "Arrepentimiento"

**Commerce Group:** PDD  
**Site:** MLA  
**Período:** Nov-Dic 2025

```json
{
  "Arrepentimiento - Cambio de opinión": {
    "proceso": "Arrepentimiento - Cambio de opinión",
    "commerce_group": "PDD",
    "site": "MLA",
    "periodo": "Nov-Dic 2025",
    "total_conversaciones": 60,
    "causas": [
      {
        "causa": "Comprador solicita devolución antes de recibir producto",
        "porcentaje": 55,
        "casos_estimados": 33,
        "descripcion": "Compradores se arrepienten de la compra y solicitan cancelación o devolución antes de que el producto sea entregado o lo reciban.",
        "citas": [
          {
            "case_id": "419234567",
            "fecha": "2025-11-20",
            "texto": "Comprador solicita cancelar la compra porque encontró el producto más barato en otro lado. El producto aún no fue despachado."
          }
        ],
        "sentimiento": "40% frustración, 50% neutral"
      },
      {
        "causa": "Producto no cumple expectativas según descripción",
        "porcentaje": 30,
        "casos_estimados": 18,
        "descripcion": "Compradores reciben el producto pero no coincide con la descripción de la publicación en características, color o tamaño. Solicitan devolución.",
        "citas": [
          {
            "case_id": "420567890",
            "fecha": "2025-12-05",
            "texto": "Compradora recibió vestido en color diferente al publicado. La foto mostraba azul pero llegó verde. Solicita devolución."
          }
        ],
        "sentimiento": "65% frustración, 25% satisfacción post-resolución"
      }
    ],
    "cobertura": 100,
    "hallazgo_principal": "Mayor volumen de arrepentimientos preventivos (antes de recibir) vs post-recepción, sugiriendo comportamiento de compra impulsiva seguida de reconsideración."
  }
}
```

---

## ❌ Ejemplo INCORRECTO (No seguir)

```json
{
  "HT - Ventas": {
    "causas": [
      {
        "causa": "Vendedores con alto volumen reportan que las colectas no se realizaron o fueron parciales por falta de espacio en el camión dejando múltiples paquetes sin despachar",
        "descripcion": "Vendedores con alto volumen reportan que las colectas no se realizaron o fueron parciales (por falta de espacio en el camión), dejando múltiples paquetes sin despachar. Solicitan exclusión masiva de estas ventas de su reputación."
      }
    ]
  }
}
```

**❌ Problemas:**
1. "causa" tiene 24 palabras (debe ser 6-10)
2. "causa" y "descripcion" tienen texto duplicado
3. Dificulta lectura en tablas del reporte HTML
4. **Falta campo "fecha" en las citas** (obligatorio desde v6.3.9)

---

## 📋 Checklist de Validación

Antes de entregar un JSON de análisis, verificar:

- [ ] `"causa"` tiene entre 6-10 palabras
- [ ] `"descripcion"` tiene entre 20-30 palabras
- [ ] No hay texto duplicado entre causa y descripción
- [ ] Todos los CASE_IDs existen en el CSV fuente
- [ ] **⚠️ Todas las citas tienen campo "fecha" en formato YYYY-MM-DD**
- [ ] Las citas son textuales (no parafraseadas)
- [ ] Sentimiento en formato string "X% frustración, Y% satisfacción"
- [ ] Cobertura es número simple (no objeto)
- [ ] Suma de porcentajes ≥80%
- [ ] Causas específicas (no genéricas)
- [ ] `"hallazgo_principal"` resume las causas raíz identificadas

---

**Última actualización:** 2 Febrero 2026  
**Versión:** 1.0
