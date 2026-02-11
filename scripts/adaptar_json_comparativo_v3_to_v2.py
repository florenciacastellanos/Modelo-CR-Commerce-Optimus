"""
Adaptador de JSON Comparativo v3.0 → v2.0
==========================================

Convierte el formato nuevo (v3.0 - detección directa de patrones) al formato
esperado por generar_reporte_cr_universal_v6.3.6.py

Formato v3.0 (entrada):
{
  "Elemento": {
    "causas": [
      {
        "patron": "PERSISTENTE | NUEVO | DESAPARECE",
        "frecuencia_p1": 12,
        "frecuencia_p2": 18,
        "porcentaje_p1": 40,
        "porcentaje_p2": 60,
        ...
      }
    ]
  }
}

Formato v2.0 (salida esperada por v6.3.6):
{
  "Elemento": {
    "causas_nov": [...],
    "causas_dic": [...],
    "incoming_nov": X,
    "incoming_dic": Y,
    ...
  }
}

Uso:
    python scripts/adaptar_json_comparativo_v3_to_v2.py \
        --input output/analisis_comparativo_v3_mlm_pagos_2025-12_2026-01.json \
        --output output/analisis_conversaciones_comparativo_claude_mlm_pagos_2025-12_2026-01.json \
        --cuadro-dimension output/cuadro_cdu_mlm_202512.csv

Autor: CR Commerce Analytics Team
Fecha: Febrero 2026
Version: 1.0
"""

import json
import pandas as pd
import argparse
from pathlib import Path
import sys

def adaptar_causa_v3_to_v2(causa_v3: dict, periodo: str) -> dict:
    """
    Adapta una causa del formato v3.0 al formato v2.0 para un período específico.
    
    Args:
        causa_v3: Causa en formato v3.0
        periodo: 'p1' o 'p2'
    
    Returns:
        Causa en formato v2.0
    """
    
    if periodo == 'p1':
        pct_key = 'porcentaje_p1'
        casos_key = 'casos_estimados_p1'
        freq_key = 'frecuencia_p1'
        citas_key = 'citas_p1'
        sent_key = 'sentimiento_p1'
    else:
        pct_key = 'porcentaje_p2'
        casos_key = 'casos_estimados_p2'
        freq_key = 'frecuencia_p2'
        citas_key = 'citas_p2'
        sent_key = 'sentimiento_p2'
    
    # Calcular casos_estimados si no existe
    casos_estimados = causa_v3.get(casos_key, causa_v3.get(freq_key, 0))
    
    causa_v2 = {
        'causa': causa_v3['causa'],
        'porcentaje': causa_v3.get(pct_key, 0),
        'casos_estimados': casos_estimados,
        'descripcion': causa_v3['descripcion'],
        'sentimiento': causa_v3.get(sent_key, {}),
        'citas': causa_v3.get(citas_key, [])
    }
    
    return causa_v2

def adaptar_elemento_v3_to_v2(elemento_v3: dict, cuadro_df: pd.DataFrame, elemento_nombre: str) -> dict:
    """
    Adapta un elemento completo del formato v3.0 al v2.0.
    
    Args:
        elemento_v3: Elemento en formato v3.0
        cuadro_df: DataFrame con métricas cuantitativas (incoming)
        elemento_nombre: Nombre del elemento (para buscar en cuadro)
    
    Returns:
        Elemento en formato v2.0
    """
    
    # Obtener incoming desde cuadro
    elemento_row = cuadro_df[cuadro_df['DIMENSION_VAL'] == elemento_nombre]
    if elemento_row.empty:
        print(f"[WARNING] '{elemento_nombre}' no encontrado en cuadro, usando valores por defecto")
        incoming_p1 = 1000
        incoming_p2 = 800
    else:
        incoming_p1 = int(elemento_row.iloc[0]['INC_P1'])
        incoming_p2 = int(elemento_row.iloc[0]['INC_P2'])
    
    # Dividir causas por período
    causas_nov = []
    causas_dic = []
    
    for causa in elemento_v3['causas']:
        # Adaptar causa para P1 (nov)
        if causa.get('frecuencia_p1', 0) > 0 or causa.get('porcentaje_p1', 0) > 0:
            causa_nov = adaptar_causa_v3_to_v2(causa, 'p1')
            causas_nov.append(causa_nov)
        
        # Adaptar causa para P2 (dic)
        if causa.get('frecuencia_p2', 0) > 0 or causa.get('porcentaje_p2', 0) > 0:
            causa_dic = adaptar_causa_v3_to_v2(causa, 'p2')
            causas_dic.append(causa_dic)
    
    # Construir elemento v2.0
    elemento_v2 = {
        'proceso': elemento_v3['proceso'],
        'commerce_group': elemento_v3['commerce_group'],
        'site': elemento_v3['site'],
        'incoming_nov': incoming_p1,
        'incoming_dic': incoming_p2,
        'variacion_casos': incoming_p2 - incoming_p1,
        'variacion_pct': round((incoming_p2 - incoming_p1) / incoming_p1 * 100, 1) if incoming_p1 > 0 else 0,
        'conversaciones_nov': elemento_v3.get('total_conversaciones_p1', 30),
        'conversaciones_dic': elemento_v3.get('total_conversaciones_p2', 30),
        'causas_nov': causas_nov,
        'causas_dic': causas_dic,
        'analisis_comparativo': {
            'insight_principal': elemento_v3.get('hallazgo_principal', 'Análisis comparativo'),
            'patron_dominante': causas_nov[0]['causa'] if causas_nov else 'N/A',
            'cambio_principal': f"Variación del {abs((incoming_p2 - incoming_p1) / incoming_p1 * 100):.1f}% en incoming"
        }
    }
    
    return elemento_v2

def main():
    parser = argparse.ArgumentParser(description='Adaptar JSON comparativo v3.0 → v2.0')
    parser.add_argument('--input', required=True, help='JSON v3.0 de entrada')
    parser.add_argument('--output', required=True, help='JSON v2.0 de salida')
    parser.add_argument('--cuadro-dimension', required=True, help='CSV con métricas cuantitativas (incoming)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    cuadro_path = Path(args.cuadro_dimension)
    
    # Validar archivos
    if not input_path.exists():
        print(f"[ERROR] No se encontró: {input_path}")
        sys.exit(1)
    
    if not cuadro_path.exists():
        print(f"[ERROR] No se encontró: {cuadro_path}")
        sys.exit(1)
    
    print("="*80)
    print("ADAPTADOR JSON COMPARATIVO v3.0 → v2.0")
    print("="*80)
    print()
    print(f"[INPUT] JSON v3.0: {input_path.name}")
    print(f"[INPUT] Cuadro dimensión: {cuadro_path.name}")
    print(f"[OUTPUT] JSON v2.0: {output_path.name}")
    print()
    
    # Cargar datos
    with open(input_path, 'r', encoding='utf-8') as f:
        data_v3 = json.load(f)
    
    cuadro_df = pd.read_csv(cuadro_path)
    
    print(f"[OK] {len(data_v3)} elementos en JSON v3.0")
    print()
    
    # Adaptar cada elemento
    data_v2 = {}
    
    for elemento_nombre, elemento_v3 in data_v3.items():
        print(f"[{elemento_nombre}]")
        
        # Validar formato v3.0
        if 'causas' not in elemento_v3:
            print(f"  ⚠️ Formato inválido, omitiendo")
            continue
        
        # Adaptar
        elemento_v2 = adaptar_elemento_v3_to_v2(elemento_v3, cuadro_df, elemento_nombre)
        data_v2[elemento_nombre] = elemento_v2
        
        print(f"  ✅ Adaptado: {len(elemento_v2['causas_nov'])} causas P1, {len(elemento_v2['causas_dic'])} causas P2")
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data_v2, f, indent=2, ensure_ascii=False)
    
    print()
    print("="*80)
    print("[SUCCESS] Adaptación completada")
    print("="*80)
    print(f"[SAVED] {output_path}")
    print()
    print("[NEXT STEP] Ejecutar:")
    print(f"  py generar_reporte_cr_universal_v6.3.6.py --open-report")
    print()

if __name__ == '__main__':
    main()
