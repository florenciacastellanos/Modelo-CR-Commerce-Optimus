"""
Detector universal de dimensiones
Identifica automaticamente en que dimension se encuentra un valor dado

Uso:
    from utils.dimension_detector import DimensionDetector
    
    detector = DimensionDetector()
    result = detector.detect_and_lookup("Pre Compra")
    
    if result['found']:
        print(f"Dimension: {result['dimension']}")
        print(f"Commerce groups: {result['commerce_groups']}")
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from difflib import get_close_matches

class DimensionDetector:
    """
    Detecta automaticamente que dimension/apertura es un valor dado
    y obtiene su contexto (commerce groups, procesos relacionados, etc.)
    """
    
    def __init__(self, mapping_path='config/dimensions-mapping.json'):
        self.mapping_path = Path(mapping_path)
        self.mapping = self._load_mapping()
        self.dimensions = list(self.mapping['mappings'].keys()) if self.mapping else []
        
        # Cache de busquedas (para performance)
        self._cache = {}
    
    def _load_mapping(self) -> Optional[Dict]:
        """Carga el mapping desde JSON"""
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Advertencia: No se encontro {self.mapping_path}")
            print("Ejecuta: python scripts/actualizar_mapeo_dimensiones.py")
            return None
        except Exception as e:
            print(f"Error al cargar mapping: {e}")
            return None
    
    def detect_and_lookup(self, value: str) -> Dict:
        """
        Busca un valor en todas las dimensiones disponibles
        
        Args:
            value: Valor a buscar (ej: "Pre Compra", "XD", "Reembolso")
        
        Returns:
            {
                'found': True/False,
                'dimension': 'PROCESO' | 'CDU' | etc.,
                'value': valor original,
                'commerce_groups': ['PDD', ...],
                'context': { ... metadata adicional },
                'source': 'local_mapping'
            }
        """
        # Check cache
        if value in self._cache:
            return self._cache[value]
        
        # Verificar si hay mapping cargado
        if not self.mapping:
            return {
                'found': False,
                'value': value,
                'error': 'Mapping no disponible'
            }
        
        # 1. Buscar en mapeo local (todas las dimensiones)
        result = self._search_local(value)
        
        # Guardar en cache
        self._cache[value] = result
        
        return result
    
    def _search_local(self, value: str) -> Dict:
        """Busca en el mapping local"""
        for dimension in self.dimensions:
            if dimension in self.mapping['mappings']:
                dim_data = self.mapping['mappings'][dimension]
                
                # Exact match (case sensitive)
                if value in dim_data:
                    return self._build_result(dimension, value, dim_data[value])
                
                # Case-insensitive match
                for key in dim_data.keys():
                    if key.lower() == value.lower():
                        return self._build_result(dimension, key, dim_data[key])
        
        # Not found - buscar similares
        suggestions = self._get_similar_values(value)
        
        return {
            'found': False,
            'value': value,
            'suggestions': suggestions
        }
    
    def _build_result(self, dimension: str, value: str, context: Dict) -> Dict:
        """Construye el resultado exitoso"""
        return {
            'found': True,
            'dimension': dimension,
            'value': value,
            'commerce_groups': context.get('commerce_groups', []),
            'context': context,
            'source': 'local_mapping'
        }
    
    def _get_similar_values(self, value: str, limit=5) -> List[Dict]:
        """Sugiere valores similares usando fuzzy matching"""
        all_values = []
        
        for dimension in self.dimensions:
            dim_data = self.mapping['mappings'].get(dimension, {})
            for key in dim_data.keys():
                all_values.append({
                    'value': key,
                    'dimension': dimension,
                    'commerce_groups': dim_data[key].get('commerce_groups', [])
                })
        
        # Fuzzy matching
        value_lower = value.lower()
        matches = []
        
        for item in all_values:
            item_lower = item['value'].lower()
            
            # Substring match
            if value_lower in item_lower or item_lower in value_lower:
                matches.append(item)
        
        # Si no hay matches por substring, usar difflib
        if not matches:
            all_value_strings = [v['value'] for v in all_values]
            close_matches = get_close_matches(value, all_value_strings, n=limit, cutoff=0.6)
            
            for match in close_matches:
                for item in all_values:
                    if item['value'] == match:
                        matches.append(item)
                        break
        
        return matches[:limit]
    
    def list_all_values_by_dimension(self, dimension: str) -> List[str]:
        """Lista todos los valores de una dimension especifica"""
        if not self.mapping or dimension not in self.dimensions:
            return []
        
        return list(self.mapping['mappings'][dimension].keys())
    
    def get_commerce_groups_for_value(self, value: str) -> List[str]:
        """Obtiene los commerce groups asociados a un valor"""
        result = self.detect_and_lookup(value)
        if result['found']:
            return result['commerce_groups']
        return []
    
    def search_by_commerce_group(self, commerce_group: str, dimension: Optional[str] = None) -> Dict:
        """
        Busca todos los valores que pertenecen a un commerce group
        
        Args:
            commerce_group: Ej: 'PDD', 'Generales Compra'
            dimension: Opcional, filtra por dimension especifica
        
        Returns:
            {
                'PROCESO': ['Pre Compra', ...],
                'CDU': ['Arrepentimiento - Cambio de opinion', ...],
                ...
            }
        """
        results = {}
        
        dimensions_to_search = [dimension] if dimension else self.dimensions
        
        for dim in dimensions_to_search:
            dim_data = self.mapping['mappings'].get(dim, {})
            matching_values = []
            
            for value, context in dim_data.items():
                if commerce_group in context.get('commerce_groups', []):
                    matching_values.append(value)
            
            if matching_values:
                results[dim] = matching_values
        
        return results


# Funcion helper para uso rapido
def quick_lookup(value: str) -> Dict:
    """
    Funcion rapida para hacer lookup de un valor
    
    Uso:
        >>> from utils.dimension_detector import quick_lookup
        >>> result = quick_lookup("Pre Compra")
        >>> print(result['dimension'])  # 'PROCESO'
    """
    detector = DimensionDetector()
    return detector.detect_and_lookup(value)


# Main para testing
if __name__ == '__main__':
    print("=== Test DimensionDetector ===\n")
    
    detector = DimensionDetector()
    
    # Test cases
    test_values = [
        "Pre Compra",
        "XD",
        "Arrepentimiento - XD",
        "pre compra",  # case insensitive
        "VALOR_INEXISTENTE",
        "Reputacion ME"
    ]
    
    for test_value in test_values:
        print(f"\nBuscando: '{test_value}'")
        result = detector.detect_and_lookup(test_value)
        
        if result['found']:
            print(f"  -> Dimension: {result['dimension']}")
            print(f"  -> Commerce Groups: {', '.join(result['commerce_groups'])}")
            print(f"  -> Casos mensuales promedio: {result['context'].get('avg_monthly_cases', 'N/A')}")
        else:
            print(f"  -> NO ENCONTRADO")
            if result.get('suggestions'):
                print(f"  -> Sugerencias:")
                for sugg in result['suggestions']:
                    print(f"     - {sugg['value']} ({sugg['dimension']})")
