"""
Script para generar análisis comparativo desde análisis separados por período
==============================================================================

NUEVO v6.3.8: Genera análisis comparativo desde 2 JSONs independientes (P1 y P2).
Esto permite detectar cambios REALES de patrones entre períodos.

Uso:
    python scripts/generar_analisis_comparativo_desde_separados.py \
        --json-p1 output/analisis_conversaciones_claude_{site}_{cg}_{dim}_p1_{p1}.json \
        --json-p2 output/analisis_conversaciones_claude_{site}_{cg}_{dim}_p2_{p2}.json \
        --cuadro-dimension output/cuadro_{dimension}_{site}_{periodo}.csv \
        --periodo-p1 2025-12 \
        --periodo-p2 2026-01 \
        --output output/analisis_conversaciones_comparativo_claude_{site}_{cg}_{p1}_{p2}.json

Diferencias vs generar_analisis_comparativo_auto.py:
- ✅ Usa análisis separados reales (no divide un análisis conjunto)
- ✅ Detecta cambios de patrones entre períodos
- ✅ Calcula porcentajes dinámicos por período
- ✅ Identifica causas que aparecen/desaparecen entre períodos

Autor: CR Commerce Analytics Team
Fecha: 4 Febrero 2026
Version: 1.0 (v6.3.8)
"""

import json
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List
import sys

# Agregar path al config para importar sinónimos
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.causas_sinonimos import consolidar_causas_similares, finalizar_aprendizaje, obtener_gestor

def calcular_incoming_por_elemento(cuadro_path: Path) -> Dict[str, Dict[str, int]]:
    """
    Extrae incoming P1 y P2 desde el cuadro de dimensión.
    
    Returns:
        Dict con estructura: {elemento: {'inc_p1': X, 'inc_p2': Y}}
    """
    df = pd.read_csv(cuadro_path)
    
    # FIX DEFENSIVO: Calcular VAR_INC_PCT si no existe (compatibilidad con CSVs antiguos)
    if 'VAR_INC_PCT' not in df.columns:
        print(f"[WARNING] Columna VAR_INC_PCT no encontrada en CSV. Calculando...")
        df['VAR_INC_PCT'] = (df['VAR_INC'] / df['INC_P1']) * 100
    
    resultado = {}
    
    for _, row in df.iterrows():
        elemento = row['DIMENSION_VAL']
        resultado[elemento] = {
            'inc_p1': int(row['INC_P1']),
            'inc_p2': int(row['INC_P2']),
            'var_casos': int(row['VAR_INC']),
            'var_pct': float(row['VAR_INC_PCT'])
        }
    
    return resultado

def generar_comparativo(
    json_p1_path: Path,
    json_p2_path: Path,
    cuadro_dimension_path: Path,
    periodo_p1: str,
    periodo_p2: str
) -> Dict:
    """
    Genera JSON comparativo desde análisis separados por período.
    
    Args:
        json_p1_path: Ruta al JSON de análisis P1
        json_p2_path: Ruta al JSON de análisis P2
        cuadro_dimension_path: Ruta al CSV con métricas cuantitativas
        periodo_p1: Período 1 en formato 'YYYY-MM'
        periodo_p2: Período 2 en formato 'YYYY-MM'
    
    Returns:
        Dict con estructura de análisis comparativo con porcentajes dinámicos
    """
    
    # 1. Cargar análisis separados
    with open(json_p1_path, 'r', encoding='utf-8') as f:
        analisis_p1 = json.load(f)
    
    with open(json_p2_path, 'r', encoding='utf-8') as f:
        analisis_p2 = json.load(f)
    
    # 2. Cargar incoming desde cuadro
    incoming_data = calcular_incoming_por_elemento(cuadro_dimension_path)
    
    # 3. Obtener metadata del primer elemento
    primer_elemento_p1 = list(analisis_p1.values())[0] if analisis_p1 else {}
    commerce_group = primer_elemento_p1.get('commerce_group', 'N/A')
    site = primer_elemento_p1.get('site', 'N/A')
    
    # 4. Procesar cada elemento
    analisis_comparativo = {}
    
    # Obtener todos los elementos (unión de P1 y P2)
    todos_elementos = set(list(analisis_p1.keys()) + list(analisis_p2.keys()))
    
    for elemento in todos_elementos:
        data_p1 = analisis_p1.get(elemento, {})
        data_p2 = analisis_p2.get(elemento, {})
        
        # Obtener incoming real
        inc_data = incoming_data.get(elemento, {'inc_p1': 0, 'inc_p2': 0, 'var_casos': 0, 'var_pct': 0})
        incoming_p1 = inc_data['inc_p1']
        incoming_p2 = inc_data['inc_p2']
        variacion_casos = inc_data['var_casos']
        variacion_pct = inc_data['var_pct']
        
        # Procesar causas P1
        # v6.4.4: Usar frecuencia real de muestra (casos_estimados del JSON original)
        # en lugar de recalcular proporcionalmente sobre incoming total
        causas_p1_raw = []
        for causa in data_p1.get('causas', []):
            porcentaje_p1 = causa.get('porcentaje', 0)
            # Usar casos_estimados original = frecuencia real de conversaciones testeadas
            frecuencia_muestra_p1 = causa.get('casos_estimados', 0)
            
            causa_p1 = {
                "causa": causa.get('causa', causa.get('descripcion', 'N/A')),
                "porcentaje": porcentaje_p1,  # Porcentaje real de P1
                "casos_estimados": frecuencia_muestra_p1,  # v6.4.4: Frecuencia real de muestra
                "descripcion": causa.get('descripcion', causa.get('causa', '')),
                "sentimiento": causa.get('sentimiento', {}),
                "citas": causa.get('citas', [])
            }
            causas_p1_raw.append(causa_p1)
        
        # Procesar causas P2
        causas_p2_raw = []
        for causa in data_p2.get('causas', []):
            porcentaje_p2 = causa.get('porcentaje', 0)
            # Usar casos_estimados original = frecuencia real de conversaciones testeadas
            frecuencia_muestra_p2 = causa.get('casos_estimados', 0)
            
            causa_p2 = {
                "causa": causa.get('causa', causa.get('descripcion', 'N/A')),
                "porcentaje": porcentaje_p2,  # Porcentaje real de P2
                "casos_estimados": frecuencia_muestra_p2,  # v6.4.4: Frecuencia real de muestra
                "descripcion": causa.get('descripcion', causa.get('causa', '')),
                "sentimiento": causa.get('sentimiento', {}),
                "citas": causa.get('citas', [])
            }
            causas_p2_raw.append(causa_p2)
        
        # ========================================
        # CONSOLIDAR CAUSAS SIMILARES (v6.4.3)
        # ========================================
        # Usa el gestor de sinónimos con auto-aprendizaje
        causas_consolidadas = consolidar_causas_similares(causas_p1_raw, causas_p2_raw)
        
        # Reconstruir causas_p1 y causas_p2 desde consolidadas (para compatibilidad)
        causas_p1 = []
        causas_p2 = []
        for cc in causas_consolidadas:
            # Solo agregar a P1 si tiene datos de P1
            if cc['pct_p1'] > 0:
                causas_p1.append({
                    "causa": cc['causa'],
                    "porcentaje": cc['pct_p1'],
                    "casos_estimados": cc['casos_p1'],
                    "descripcion": cc.get('descripcion', ''),
                    "sentimiento": cc.get('sentimiento_p1', {}),
                    "citas": cc.get('citas_p1', [])
                })
            # Solo agregar a P2 si tiene datos de P2
            if cc['pct_p2'] > 0:
                causas_p2.append({
                    "causa": cc['causa'],
                    "porcentaje": cc['pct_p2'],
                    "casos_estimados": cc['casos_p2'],
                    "descripcion": cc.get('descripcion', ''),
                    "sentimiento": cc.get('sentimiento_p2', {}),
                    "citas": cc.get('citas_p2', [])
                })
        
        # Generar insight principal
        if variacion_casos < 0:
            tendencia = "reducción"
            signo = ""
        else:
            tendencia = "aumento"
            signo = "+"
        
        # Detectar patron dominante
        patron_dominante_p1 = causas_p1[0]['causa'] if causas_p1 else "N/A"
        patron_dominante_p2 = causas_p2[0]['causa'] if causas_p2 else "N/A"
        
        # Verificar si el patrón cambió
        patron_cambio = "mantuvo" if patron_dominante_p1 == patron_dominante_p2 else "cambió"
        
        # Construir insight
        hallazgo_p1 = data_p1.get('hallazgo_principal', '')
        hallazgo_p2 = data_p2.get('hallazgo_principal', '')
        
        if abs(variacion_pct) < 5:
            insight_principal = f"Variación mínima de {signo}{abs(variacion_casos):,} casos ({variacion_pct:+.1f}%). Patrón dominante se {patron_cambio} entre períodos."
        else:
            insight_principal = f"La {tendencia} de {signo}{abs(variacion_casos):,} casos ({variacion_pct:+.1f}%) se explica principalmente por: {patron_dominante_p2}. {hallazgo_p2}"
        
        # Construir entrada comparativa
        analisis_comparativo[elemento] = {
            "proceso": elemento,
            "commerce_group": commerce_group,
            "site": site,
            "incoming_nov": incoming_p1,
            "incoming_dic": incoming_p2,
            "variacion_casos": variacion_casos,
            "variacion_pct": round(variacion_pct, 1),
            "conversaciones_nov": data_p1.get('total_conversaciones', 0),
            "conversaciones_dic": data_p2.get('total_conversaciones', 0),
            "causas_nov": causas_p1,
            "causas_dic": causas_p2,
            # v6.4.3: Causas consolidadas con matching semántico
            "causas_consolidadas": causas_consolidadas,
            "analisis_comparativo": {
                "insight_principal": insight_principal,
                "patron_dominante_p1": patron_dominante_p1,
                "patron_dominante_p2": patron_dominante_p2,
                "patron_cambio": patron_cambio,
                "cambio_principal": f"{tendencia.capitalize()} del {abs(variacion_pct):.1f}% en incoming"
            }
        }
    
    return analisis_comparativo

def main():
    parser = argparse.ArgumentParser(description='Generar análisis comparativo desde análisis separados (v6.3.8)')
    parser.add_argument('--json-p1', required=True, help='Ruta al JSON de análisis P1')
    parser.add_argument('--json-p2', required=True, help='Ruta al JSON de análisis P2')
    parser.add_argument('--cuadro-dimension', required=True, help='Ruta al CSV con cuadro de dimensión')
    parser.add_argument('--output', required=True, help='Ruta de salida para JSON comparativo')
    parser.add_argument('--periodo-p1', required=True, help='Período 1 en formato YYYY-MM (ej: 2025-12)')
    parser.add_argument('--periodo-p2', required=True, help='Período 2 en formato YYYY-MM (ej: 2026-01)')
    
    args = parser.parse_args()
    
    json_p1_path = Path(args.json_p1)
    json_p2_path = Path(args.json_p2)
    cuadro_dimension_path = Path(args.cuadro_dimension)
    output_path = Path(args.output)
    
    # Validar archivos de entrada
    if not json_p1_path.exists():
        print(f"[ERROR] No se encontró: {json_p1_path}")
        sys.exit(1)
    
    if not json_p2_path.exists():
        print(f"[ERROR] No se encontró: {json_p2_path}")
        sys.exit(1)
    
    if not cuadro_dimension_path.exists():
        print(f"[ERROR] No se encontró: {cuadro_dimension_path}")
        sys.exit(1)
    
    # Validar formato de períodos
    import re
    if not re.match(r'\d{4}-\d{2}', args.periodo_p1) or not re.match(r'\d{4}-\d{2}', args.periodo_p2):
        print(f"[ERROR] Formato de período inválido. Use YYYY-MM (ej: 2025-12)")
        sys.exit(1)
    
    print("="*80)
    print("GENERADOR DE ANÁLISIS COMPARATIVO DESDE ANÁLISIS SEPARADOS (v6.3.8)")
    print("="*80)
    print()
    print(f"[INPUT] Análisis P1: {json_p1_path.name}")
    print(f"[INPUT] Análisis P2: {json_p2_path.name}")
    print(f"[INPUT] Cuadro dimensión: {cuadro_dimension_path.name}")
    print(f"[INPUT] Período P1: {args.periodo_p1}")
    print(f"[INPUT] Período P2: {args.periodo_p2}")
    print(f"[OUTPUT] Análisis comparativo: {output_path.name}")
    print()
    
    # Generar análisis comparativo
    print("[PROCESSING] Generando análisis comparativo con porcentajes dinámicos...")
    try:
        analisis_comparativo = generar_comparativo(
            json_p1_path,
            json_p2_path,
            cuadro_dimension_path,
            args.periodo_p1,
            args.periodo_p2
        )
    except Exception as e:
        print(f"[ERROR] Fallo al generar análisis comparativo: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Guardar JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analisis_comparativo, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Análisis comparativo generado: {len(analisis_comparativo)} elementos")
    print(f"[SAVED] {output_path}")
    print()
    
    # v6.4.3: Guardar aprendizajes de sinónimos detectados
    nuevas_similitudes = finalizar_aprendizaje()
    
    # Mostrar resumen de cambios detectados
    cambios_detectados = sum(1 for elem in analisis_comparativo.values() 
                             if elem['analisis_comparativo']['patron_cambio'] == 'cambió')
    
    # Contar causas consolidadas
    total_consolidadas = sum(len(elem.get('causas_consolidadas', [])) for elem in analisis_comparativo.values())
    total_causas_originales = sum(
        len(elem.get('causas_nov', [])) + len(elem.get('causas_dic', [])) 
        for elem in analisis_comparativo.values()
    )
    
    print("="*80)
    print("[RESUMEN]")
    print(f"  - Total elementos: {len(analisis_comparativo)}")
    print(f"  - Patrones que cambiaron: {cambios_detectados}")
    print(f"  - Patrones que se mantuvieron: {len(analisis_comparativo) - cambios_detectados}")
    print()
    print("[CONSOLIDACIÓN v6.4.3]")
    print(f"  - Causas originales (P1+P2): {total_causas_originales}")
    print(f"  - Causas consolidadas: {total_consolidadas}")
    if nuevas_similitudes > 0:
        print(f"  - Nuevas similitudes aprendidas: {nuevas_similitudes} [NUEVO]")
    print()
    print("[NEXT STEP] El análisis comparativo estará disponible en el reporte HTML")
    print("="*80)

if __name__ == '__main__':
    main()
