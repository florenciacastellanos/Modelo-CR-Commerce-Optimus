"""
Ejemplo de uso del DimensionDetector
Muestra casos de uso comunes y como integrar el detector en scripts

Ejecutar desde la raiz del repositorio: py examples/ejemplo_dimension_detector.py
"""

import sys
from pathlib import Path

# Agregar la raiz del repositorio al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dimension_detector import DimensionDetector

def ejemplo_1_deteccion_basica():
    """Ejemplo 1: Detección básica de un valor"""
    print("=" * 60)
    print("EJEMPLO 1: Deteccion basica")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    # El usuario menciona "Pre Compra"
    valor_usuario = "Pre Compra"
    print(f"\nUsuario menciona: '{valor_usuario}'")
    
    result = detector.detect_and_lookup(valor_usuario)
    
    if result['found']:
        print(f"\nDetectado automaticamente:")
        print(f"  - Dimension: {result['dimension']}")
        print(f"  - Commerce Groups: {', '.join(result['commerce_groups'])}")
        print(f"  - Casos mensuales promedio: {result['context']['avg_monthly_cases']:,}")
    else:
        print(f"\nNo se encontro '{valor_usuario}'")


def ejemplo_2_case_insensitive():
    """Ejemplo 2: Búsqueda case-insensitive"""
    print("\n\n" + "=" * 60)
    print("EJEMPLO 2: Busqueda case-insensitive")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    valores_test = ["pre compra", "PRE COMPRA", "Pre Compra", "PRE compRA"]
    
    for valor in valores_test:
        result = detector.detect_and_lookup(valor)
        status = "OK" if result['found'] else "FALLO"
        print(f"\n'{valor}' -> {status}")
        if result['found']:
            print(f"  Detectado como: {result['dimension']}")


def ejemplo_3_fuzzy_matching():
    """Ejemplo 3: Fuzzy matching con sugerencias"""
    print("\n\n" + "=" * 60)
    print("EJEMPLO 3: Fuzzy matching (errores de tipeo)")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    # Usuario escribe mal "Reputación ME" (sin tilde)
    valor_mal_escrito = "reputacion me"
    print(f"\nUsuario escribe: '{valor_mal_escrito}' (sin tilde)")
    
    result = detector.detect_and_lookup(valor_mal_escrito)
    
    if not result['found'] and result.get('suggestions'):
        print(f"\nNo se encontro exactamente, pero hay sugerencias:")
        for i, sugg in enumerate(result['suggestions'], 1):
            print(f"  {i}. {sugg['value']} ({sugg['dimension']})")


def ejemplo_4_multiple_commerce_groups():
    """Ejemplo 4: Valor que pertenece a múltiples commerce groups"""
    print("\n\n" + "=" * 60)
    print("EJEMPLO 4: Valores con multiples commerce groups")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    # "XD" está en PDD y PNR
    valor = "XD"
    print(f"\nValor: '{valor}'")
    
    result = detector.detect_and_lookup(valor)
    
    if result['found']:
        print(f"\nDimension: {result['dimension']}")
        print(f"Commerce Groups: {', '.join(result['commerce_groups'])}")
        print(f"\nEsto significa que '{valor}' cruza multiples commerce groups.")
        print(f"Necesitas elegir cual analizar o analizar ambos.")


def ejemplo_5_integracion_workflow():
    """Ejemplo 5: Integración en workflow de análisis"""
    print("\n\n" + "=" * 60)
    print("EJEMPLO 5: Integracion en workflow de analisis")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    # Simular pedido de usuario
    site = "MLB"
    valor_mencionado = "arrepentimiento - xd"
    periodo_1 = "2025-11-01"
    periodo_2 = "2025-12-01"
    
    print(f"\nUsuario pide: '{site} {valor_mencionado} nov dic'")
    print(f"\nProcesando...")
    
    # 1. Detectar dimensión
    result = detector.detect_and_lookup(valor_mencionado)
    
    if not result['found']:
        print(f"\nERROR: No se encontro '{valor_mencionado}'")
        return
    
    # 2. Construir parámetros del análisis
    dimension = result['dimension']
    commerce_groups = result['commerce_groups']
    
    print(f"\nDetectado:")
    print(f"  - Dimension: {dimension}")
    print(f"  - Commerce Group(s): {', '.join(commerce_groups)}")
    
    # 3. Determinar tipo de análisis
    if dimension == "PROCESO":
        tipo_analisis = "proceso_especifico"
        commerce_group_principal = commerce_groups[0]
        print(f"\nTipo de analisis: Proceso especifico dentro de {commerce_group_principal}")
        print(f"Comando sugerido:")
        print(f"  --commerce-group {commerce_group_principal}")
        print(f"  --process-name '{valor_mencionado}'")
        print(f"  --aperturas CDU,TIPIFICACION")
    elif dimension == "ENVIRONMENT":
        tipo_analisis = "cross_commerce_environment"
        print(f"\nTipo de analisis: Environment cruzando commerce groups")
        print(f"Commerce groups afectados: {', '.join(commerce_groups)}")
        print(f"Comando sugerido:")
        print(f"  --commerce-group {commerce_groups[0]}")
        print(f"  --environment {valor_mencionado}")
        print(f"  --aperturas PROCESO,CDU")
    
    print(f"\nConfirmacion al usuario:")
    print(f"'Voy a analizar {dimension} '{valor_mencionado}' en {site}")
    print(f" para {periodo_1} vs {periodo_2}. Es correcto?'")


def ejemplo_6_busqueda_por_commerce_group():
    """Ejemplo 6: Buscar todos los valores de un commerce group"""
    print("\n\n" + "=" * 60)
    print("EJEMPLO 6: Buscar valores por commerce group")
    print("=" * 60)
    
    detector = DimensionDetector()
    
    commerce_group = "PDD"
    print(f"\nBuscando todos los valores que pertenecen a '{commerce_group}'...")
    
    results = detector.search_by_commerce_group(commerce_group)
    
    for dimension, valores in results.items():
        print(f"\n{dimension} ({len(valores)} valores):")
        # Mostrar solo los primeros 5
        for valor in valores[:5]:
            print(f"  - {valor}")
        if len(valores) > 5:
            print(f"  ... y {len(valores) - 5} mas")


if __name__ == '__main__':
    print("\n")
    print("*" * 60)
    print(" EJEMPLOS DE USO - DimensionDetector v5.0")
    print("*" * 60)
    
    # Ejecutar todos los ejemplos
    ejemplo_1_deteccion_basica()
    ejemplo_2_case_insensitive()
    ejemplo_3_fuzzy_matching()
    ejemplo_4_multiple_commerce_groups()
    ejemplo_5_integracion_workflow()
    ejemplo_6_busqueda_por_commerce_group()
    
    print("\n\n" + "*" * 60)
    print(" FIN DE EJEMPLOS")
    print("*" * 60)
    print("\nDocumentacion completa: docs/DIMENSION_DETECTOR_GUIDE.md\n")
