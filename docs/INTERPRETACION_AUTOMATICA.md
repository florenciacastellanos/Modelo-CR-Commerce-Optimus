# ⚙️ Reglas de Interpretación Automática

**Versión:** 1.0
**Fecha:** 4 Febrero 2026

Este documento detalla el sistema de interpretación automática de términos mencionados por usuarios para mapearlos a commerce groups y procesos específicos.

---

## 🎯 Objetivo

Cuando un usuario menciona términos como "PDD", "Arrepentimiento", "Prustomer", etc., el sistema debe:
1. Detectar automáticamente si es un commerce group completo o un proceso específico
2. Mapear al commerce group correcto
3. Construir el comando adecuado con los parámetros correctos

---

## 📋 Mapeo Completo

### Tabla de Interpretación

| Usuario menciona | Interpretación | Commerce Group | Usar --process-name | Aperturas recomendadas |
|------------------|----------------|----------------|---------------------|------------------------|
| "PDD" o "Post-Compra" | Commerce group completo | PDD | ❌ NO | PROCESO, CDU |
| "PNR" | Commerce group completo | PNR | ❌ NO | PROCESO, CDU |
| "PCF Comprador" | Commerce group completo | PCF_COMPRADOR | ❌ NO | PROCESO, CDU |
| "PCF Vendedor" | Commerce group completo | PCF_VENDEDOR | ❌ NO | PROCESO, CDU |
| "ME PreDespacho" o "Shipping PreDespacho" | Commerce group completo | ME_PREDESPACHO | ❌ NO | PROCESO, CDU |
| "ME Distribución" o "Shipping Distribución" | Commerce group completo | ME_DISTRIBUCION | ❌ NO | PROCESO, CDU |
| "Moderaciones" | Commerce group completo | MODERACIONES | ❌ NO | PROCESO, CDU |
| "Reputación" o "Reputación ME" | Commerce group completo | REPUTACION_ME | ❌ NO | PROCESO, CDU |
| "Ventas y Publicaciones" | Commerce group completo | VENTAS_PUBLICACIONES | ❌ NO | PROCESO, CDU |
| "Pagos" o "MP" o "MP On" | Commerce group completo | PAGOS | ❌ NO | PROCESO, CDU |
| "Cuenta" o "Generales Compra" | Commerce group completo | GENERALES_COMPRA | ❌ NO | PROCESO, CDU |
| "Loyalty" o "Nivel" | Commerce group completo | LOYALTY | ❌ NO | PROCESO, CDU |
| **"Arrepentimiento"** | ✅ Proceso específico | PDD | ✅ SÍ | CDU, TIPIFICACION |
| **"Defectuoso"** | ✅ Proceso específico | PDD | ✅ SÍ | CDU, TIPIFICACION |
| **"Diferente"** | ✅ Proceso específico | PDD | ✅ SÍ | CDU, TIPIFICACION |
| **"Incompleto"** | ✅ Proceso específico | PDD | ✅ SÍ | CDU, TIPIFICACION |
| **"Caja Vacía"** | ✅ Proceso específico | PDD | ✅ SÍ | CDU, TIPIFICACION |
| **"No Recibido"** | ✅ Proceso específico | PNR | ✅ SÍ | CDU, TIPIFICACION |
| **"Despacho"** | ✅ Proceso específico | ME_PREDESPACHO | ✅ SÍ | CDU, TIPIFICACION |
| **"Enviabilidad"** | ✅ Proceso específico | ME_PREDESPACHO | ✅ SÍ | CDU, TIPIFICACION |
| **"Colecta"** | ✅ Proceso específico | ME_PREDESPACHO | ✅ SÍ | CDU, TIPIFICACION |
| **"Entrega"** | ✅ Proceso específico | ME_DISTRIBUCION | ✅ SÍ | CDU, TIPIFICACION |
| **"Prustomer"** | ✅ Proceso específico | MODERACIONES | ✅ SÍ | CDU, TIPIFICACION |
| **"Pre Compra"** | ✅ Proceso específico | VENTAS_PUBLICACIONES | ✅ SÍ | CDU, TIPIFICACION |

---

## 🤖 Lógica de Ejecución Automática

### Regla General:

```python
def generar_comando(termino_usuario):
    """
    Genera el comando correcto según el término mencionado por el usuario.
    
    Args:
        termino_usuario: Término mencionado (ej: "PDD", "Arrepentimiento")
    
    Returns:
        Diccionario con parámetros del comando
    """
    
    # Detectar si es commerce group o proceso específico
    mapping = detectar_mapping(termino_usuario)
    
    if mapping['tipo'] == 'commerce_group':
        # Commerce group completo: analizar todos los procesos
        return {
            'commerce_group': mapping['commerce_group'],
            'process_name': None,
            'aperturas': ['PROCESO', 'CDU']
        }
    else:
        # Proceso específico: drill-down en ese proceso
        return {
            'commerce_group': mapping['commerce_group'],
            'process_name': mapping['process_name'],
            'aperturas': ['CDU', 'TIPIFICACION']
        }
```

### Ejemplos de Comandos Generados:

#### Caso 1: Usuario menciona "PDD"
```bash
# Interpretación: Commerce group completo
# Acción: Analizar TODOS los procesos de PDD

py generar_reporte_cr_universal_v6.3.6.py \
    --site MLA \
    --commerce-group PDD \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --aperturas PROCESO,CDU \
    --open-report
```

**Output esperado:**
- Tabla 1: Por PROCESO (Arrepentimiento, Defectuoso, Diferente, etc.)
- Tabla 2: Por CDU dentro de cada proceso
- Análisis comparativo de conversaciones para procesos priorizados (regla 80%)

#### Caso 2: Usuario menciona "Arrepentimiento"
```bash
# Interpretación: Proceso específico dentro de PDD
# Acción: Drill-down SOLO en Arrepentimiento

py generar_reporte_cr_universal_v6.3.6.py \
    --site MLA \
    --commerce-group PDD \
    --process-name "Arrepentimiento" \
    --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 \
    --aperturas CDU,TIPIFICACION \
    --open-report
```

**Output esperado:**
- Tabla 1: Por CDU dentro de Arrepentimiento (Cambio de opinión, etc.)
- Tabla 2: Por TIPIFICACION dentro de cada CDU
- Análisis comparativo de conversaciones solo para Arrepentimiento

---

## 🔧 Implementación Técnica

### Detector de Dimensiones (v5.0)

```python
# utils/dimension_detector.py
from pathlib import Path
import json

class DimensionDetector:
    """Detecta automáticamente dimensiones desde config."""
    
    def __init__(self):
        config_path = Path(__file__).parent.parent / 'config' / 'dimensions-mapping.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)
    
    def detect_and_lookup(self, valor_mencionado):
        """
        Detecta dimensión y commerce group basándose en valor mencionado.
        
        Args:
            valor_mencionado: Término del usuario (ej: "Prustomer", "PDD")
        
        Returns:
            Dict con 'found', 'dimension', 'commerce_groups', 'suggestions'
        """
        valor_norm = valor_mencionado.lower().strip()
        
        # Buscar coincidencia exacta
        for dimension, valores in self.mapping.items():
            for valor_data in valores:
                if valor_norm == valor_data['valor'].lower():
                    return {
                        'found': True,
                        'dimension': dimension,
                        'commerce_groups': valor_data['commerce_groups'],
                        'tipo': valor_data.get('tipo', 'commerce_group'),
                        'valor_original': valor_data['valor']
                    }
        
        # Buscar coincidencia parcial (sugerencias)
        sugerencias = []
        for dimension, valores in self.mapping.items():
            for valor_data in valores:
                if valor_norm in valor_data['valor'].lower() or \
                   valor_data['valor'].lower() in valor_norm:
                    sugerencias.append({
                        'valor': valor_data['valor'],
                        'dimension': dimension,
                        'commerce_groups': valor_data['commerce_groups']
                    })
        
        return {
            'found': False,
            'suggestions': sugerencias[:5]  # Top 5 sugerencias
        }
```

### Uso en Script Principal:

```python
from utils.dimension_detector import DimensionDetector

# Usuario menciona: "Arrepentimiento"
detector = DimensionDetector()
result = detector.detect_and_lookup("Arrepentimiento")

if result['found']:
    print(f"✅ Detectado: {result['dimension']}")
    print(f"   Commerce Group(s): {result['commerce_groups']}")
    print(f"   Tipo: {result['tipo']}")
    
    if result['tipo'] == 'proceso_especifico':
        # Usar --process-name
        comando = f"--commerce-group {result['commerce_groups'][0]} --process-name 'Arrepentimiento'"
    else:
        # Analizar commerce group completo
        comando = f"--commerce-group {result['commerce_groups'][0]}"
else:
    print(f"⚠️ No encontrado. Sugerencias:")
    for sugg in result['suggestions']:
        print(f"   - {sugg['valor']} ({sugg['dimension']})")
```

---

## 📂 Configuración: `dimensions-mapping.json`

```json
{
  "COMMERCE_GROUP": [
    {
      "valor": "PDD",
      "tipo": "commerce_group",
      "commerce_groups": ["PDD"],
      "alias": ["Post-Compra", "Post Delivery"]
    },
    {
      "valor": "PNR",
      "tipo": "commerce_group",
      "commerce_groups": ["PNR"],
      "alias": ["Package Not Received"]
    }
  ],
  "PROCESO": [
    {
      "valor": "Arrepentimiento",
      "tipo": "proceso_especifico",
      "commerce_groups": ["PDD"],
      "aperturas_recomendadas": ["CDU", "TIPIFICACION"]
    },
    {
      "valor": "Defectuoso",
      "tipo": "proceso_especifico",
      "commerce_groups": ["PDD"],
      "aperturas_recomendadas": ["CDU", "TIPIFICACION"]
    },
    {
      "valor": "Prustomer",
      "tipo": "proceso_especifico",
      "commerce_groups": ["MODERACIONES"],
      "aperturas_recomendadas": ["CDU", "TIPIFICACION"]
    }
  ]
}
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Usuario no especifica alcance

**Input:** "Quiero analizar PDD en MLA de nov a dic"

**Detección:**
```python
result = detector.detect_and_lookup("PDD")
# result['tipo'] = 'commerce_group'
```

**Confirmación al usuario:**
```
Voy a analizar:
- Site: MLA
- Período: Nov 2025 vs Dic 2025
- Commerce Group: PDD (análisis completo de todos los procesos)
- Aperturas: PROCESO, CDU

Confirmame si es correcto y avanzo.
```

### Caso 2: Usuario especifica proceso

**Input:** "Necesito ver el detalle de Arrepentimiento en MLA"

**Detección:**
```python
result = detector.detect_and_lookup("Arrepentimiento")
# result['tipo'] = 'proceso_especifico'
# result['commerce_groups'] = ['PDD']
```

**Confirmación al usuario:**
```
Voy a analizar:
- Site: MLA
- Período: [pendiente confirmar]
- Proceso específico: Arrepentimiento (dentro de PDD)
- Aperturas: CDU, TIPIFICACION

¿Qué períodos querés comparar?
```

### Caso 3: Término ambiguo

**Input:** "Quiero ver entregas"

**Detección:**
```python
result = detector.detect_and_lookup("entregas")
# result['found'] = False
# result['suggestions'] = [
#   {'valor': 'Entrega', 'dimension': 'PROCESO', 'commerce_groups': ['ME_DISTRIBUCION']},
#   {'valor': 'Entrega Pre Compra', 'dimension': 'PROCESO', ...}
# ]
```

**Respuesta al usuario:**
```
No encontré una coincidencia exacta para "entregas". ¿Te referís a alguno de estos?

1. Entrega (ME Distribución) - Proceso específico
2. Entrega Pre Compra (Ventas y Publicaciones) - Proceso específico

¿Cuál querés analizar?
```

---

## ✅ Validación Automática

### Checklist de Validación:

```python
def validar_interpretacion(result):
    """Valida que la interpretación sea correcta."""
    
    checks = []
    
    # 1. Término encontrado
    if not result['found']:
        checks.append({
            'ok': False,
            'mensaje': f"Término no encontrado. Sugerencias disponibles: {len(result.get('suggestions', []))}"
        })
        return checks
    
    # 2. Commerce group válido
    cgs_validos = ['PDD', 'PNR', 'PCF_COMPRADOR', 'PCF_VENDEDOR', ...]
    for cg in result['commerce_groups']:
        if cg not in cgs_validos:
            checks.append({
                'ok': False,
                'mensaje': f"Commerce group inválido: {cg}"
            })
    
    # 3. Si es proceso específico, debe tener commerce group único
    if result['tipo'] == 'proceso_especifico':
        if len(result['commerce_groups']) != 1:
            checks.append({
                'ok': False,
                'mensaje': f"Proceso específico debe tener 1 commerce group, tiene {len(result['commerce_groups'])}"
            })
    
    # 4. Aperturas recomendadas válidas
    aperturas_validas = ['PROCESO', 'CDU', 'TIPIFICACION', 'ENVIRONMENT', ...]
    if 'aperturas_recomendadas' in result:
        for apertura in result['aperturas_recomendadas']:
            if apertura not in aperturas_validas:
                checks.append({
                    'ok': False,
                    'mensaje': f"Apertura inválida: {apertura}"
                })
    
    # Si no hay errores
    if not checks:
        checks.append({
            'ok': True,
            'mensaje': "Interpretación válida"
        })
    
    return checks
```

---

## 📚 Referencias

- **Configuración:** `config/dimensions-mapping.json`
- **Detector:** `utils/dimension_detector.py`
- **Commerce Groups:** `docs/COMMERCE_GROUPS_REFERENCE.md`
- **Reglas críticas:** `docs/REGLAS_CRITICAS_DETALLADAS.md`

---

**Versión:** 1.0
**Autor:** CR Commerce Analytics Team
**Fecha:** 4 Febrero 2026
**Status:** ✅ PRODUCTION READY
