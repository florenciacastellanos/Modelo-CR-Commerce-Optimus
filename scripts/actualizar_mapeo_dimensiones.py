"""
Script para generar el archivo de mapeo universal de dimensiones
Convierte el CSV raw en un JSON estructurado para lookup rápido

Uso:
    python scripts/actualizar_mapeo_dimensiones.py
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def generar_mapeo_dimensiones():
    """
    Lee el CSV generado por BigQuery y crea el JSON estructurado
    """
    
    # Leer CSV raw
    csv_path = Path('output/temp_mapeo_dimensiones_raw.csv')
    if not csv_path.exists():
        print(f"Error: No se encontro {csv_path}")
        print("   Ejecuta primero: sql/temp_generar_mapeo_dimensiones.sql")
        return
    
    df = pd.read_csv(csv_path, encoding='utf-16')
    print(f"OK: CSV cargado - {len(df)} registros")
    
    # Estructura del mapeo
    mappings = defaultdict(dict)
    
    # Procesar cada dimensión
    for dimension in df['DIMENSION'].unique():
        print(f"\nProcesando dimension: {dimension}")
        
        dim_data = df[df['DIMENSION'] == dimension]
        
        for _, row in dim_data.iterrows():
            value = row['VALUE']
            commerce_group = row['COMMERCE_GROUP']
            casos = int(row['CASOS_3M'])
            
            # Si el value ya existe, agregar commerce group a la lista
            if value in mappings[dimension]:
                if commerce_group not in mappings[dimension][value]['commerce_groups']:
                    mappings[dimension][value]['commerce_groups'].append(commerce_group)
                mappings[dimension][value]['avg_monthly_cases'] += casos // 3
            else:
                # Crear nueva entrada
                mappings[dimension][value] = {
                    'commerce_groups': [commerce_group],
                    'avg_monthly_cases': casos // 3,
                    'total_cases_3m': casos
                }
        
        print(f"   OK: {len(mappings[dimension])} valores unicos")
    
    # Crear estructura final
    output = {
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'source': 'BT_CX_CONTACTS - últimos 3 meses',
            'dimensions_available': list(mappings.keys()),
            'total_values': sum(len(v) for v in mappings.values()),
            'generation_script': 'scripts/actualizar_mapeo_dimensiones.py'
        },
        'mappings': dict(mappings)
    }
    
    # Guardar JSON
    output_path = Path('config/dimensions-mapping.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nOK: Mapeo generado exitosamente - {output_path}")
    print(f"   Total dimensiones: {len(mappings)}")
    print(f"   Total valores unicos: {output['metadata']['total_values']}")
    
    # Mostrar resumen por dimensión
    print("\nResumen por dimension:")
    for dim, values in mappings.items():
        print(f"   * {dim}: {len(values)} valores")

if __name__ == '__main__':
    print("Generando mapeo de dimensiones...")
    generar_mapeo_dimensiones()
    print("\nProceso completado!")
