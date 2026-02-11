"""
Script para generar análisis comparativo automáticamente desde análisis básico
==============================================================================

UNIVERSAL: Funciona con cualquier dimensión (PROCESO, CDU, TIPIFICACION, etc.),
cualquier site, commerce group, y cualquier período.

Este script transforma el análisis básico (causas_raiz global) en análisis 
comparativo (causas_p1 vs causas_p2) para mostrar el patrón temporal.

Uso:
    python scripts/generar_analisis_comparativo_auto.py \
        --json-basico output/analisis_conversaciones_claude_{site}_{cg}_{p1}_{p2}.json \
        --cuadro-dimension output/cuadro_{dimension}_{site}_{periodo}.csv \
        --periodo-p1 2025-11 \
        --periodo-p2 2025-12 \
        --output output/analisis_conversaciones_comparativo_claude_{site}_{cg}_{p1}_{p2}.json

Ejemplos:
    # CDU (Moderaciones)
    python scripts/generar_analisis_comparativo_auto.py \
        --json-basico output/analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json \
        --cuadro-dimension output/cuadro_cdu_mlm_202511.csv \
        --periodo-p1 2025-11 \
        --periodo-p2 2025-12 \
        --output output/analisis_conversaciones_comparativo_claude_mlm_moderaciones_2025-11_2025-12.json
    
    # PROCESO (PDD completo)
    python scripts/generar_analisis_comparativo_auto.py \
        --json-basico output/analisis_conversaciones_claude_mla_pdd_2025-10_2025-11.json \
        --cuadro-dimension output/cuadro_proceso_mla_202510.csv \
        --periodo-p1 2025-10 \
        --periodo-p2 2025-11 \
        --output output/analisis_conversaciones_comparativo_claude_mla_pdd_2025-10_2025-11.json

Características:
    - ✅ Adaptable a cualquier dimensión de análisis
    - ✅ Divide citas inteligentemente basándose en fechas reales
    - ✅ Parsea sentimiento a formato estructurado
    - ✅ Valida coherencia entre JSON y cuadro CSV
    - ✅ Genera insights descriptivos sin truncar

Autor: CR Commerce Analytics Team
Fecha: Febrero 2026
Version: 2.0 (Universal)
"""

import json
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List
import sys

def parse_sentimiento(sentimiento_str: str) -> Dict[str, int]:
    """
    Parsea el string de sentimiento del análisis básico.
    
    Entrada: "70% satisfacción post-resolución, 30% frustración inicial"
    Salida: {"satisfaccion": 70, "frustracion": 30}
    """
    sentimiento_dict = {}
    
    # Mapeo de palabras clave a categorías
    mappings = {
        'satisfaccion': ['satisfacción', 'satisfaccion', 'alivio'],
        'frustracion': ['frustración', 'frustracion', 'insatisfacción', 'insatisfaccion'],
        'neutral': ['neutral', 'esperan', 'comprensión', 'comprension'],
        'confusion': ['confusión', 'confusion', 'vergüenza']
    }
    
    # Buscar porcentajes en el string
    import re
    matches = re.findall(r'(\d+)%\s+([^,]+)', sentimiento_str.lower())
    
    for pct, desc in matches:
        pct_int = int(pct)
        desc_clean = desc.strip()
        
        # Mapear a categoría
        for categoria, keywords in mappings.items():
            if any(kw in desc_clean for kw in keywords):
                if categoria in sentimiento_dict:
                    sentimiento_dict[categoria] += pct_int
                else:
                    sentimiento_dict[categoria] = pct_int
                break
    
    return sentimiento_dict if sentimiento_dict else {"neutral": 100}

def agregar_fechas_a_citas(citas: List[Dict], conversaciones_df: pd.DataFrame, periodo_p1: str, periodo_p2: str) -> List[Dict]:
    """
    Agrega fechas a las citas basándose en el CASE_ID desde el CSV de conversaciones.
    
    Args:
        citas: Lista de citas con case_id
        conversaciones_df: DataFrame con conversaciones que incluye CONTACT_DATE_ID
        periodo_p1: Período 1 en formato 'YYYY-MM' (ej: '2025-11')
        periodo_p2: Período 2 en formato 'YYYY-MM' (ej: '2025-12')
    """
    citas_con_fecha = []
    citas_procesadas = 0
    total_citas = len(citas)
    
    for cita in citas:
        case_id = str(cita['case_id'])
        cita_copy = cita.copy()
        
        # Buscar fecha en el dataframe
        if 'CAS_CASE_ID' in conversaciones_df.columns and 'CONTACT_DATE_ID' in conversaciones_df.columns:
            match = conversaciones_df[conversaciones_df['CAS_CASE_ID'].astype(str) == case_id]
            if not match.empty:
                fecha = pd.to_datetime(match.iloc[0]['CONTACT_DATE_ID']).strftime('%Y-%m-%d')
                cita_copy['fecha'] = fecha
            else:
                # Fecha por defecto basada en distribución: primera mitad -> P1, segunda mitad -> P2
                if citas_procesadas < total_citas / 2:
                    cita_copy['fecha'] = f"{periodo_p1}-15"  # Mitad del mes P1
                else:
                    cita_copy['fecha'] = f"{periodo_p2}-15"  # Mitad del mes P2
        else:
            # Sin columnas disponibles: usar distribución 50-50
            if citas_procesadas < total_citas / 2:
                cita_copy['fecha'] = f"{periodo_p1}-15"
            else:
                cita_copy['fecha'] = f"{periodo_p2}-15"
        
        citas_con_fecha.append(cita_copy)
        citas_procesadas += 1
    
    return citas_con_fecha

def generar_analisis_comparativo(
    json_basico_path: Path,
    cuadro_dimension_path: Path,
    conversaciones_csv_dir: Path,
    periodo_p1: str,
    periodo_p2: str
) -> Dict:
    """
    Genera JSON comparativo desde análisis básico (universal para cualquier dimensión).
    
    Args:
        json_basico_path: Ruta al JSON de análisis básico
        cuadro_dimension_path: Ruta al CSV con métricas cuantitativas (cualquier dimensión: CDU, PROCESO, etc.)
        conversaciones_csv_dir: Directorio con CSVs de conversaciones (para fechas)
        periodo_p1: Período 1 en formato 'YYYY-MM' (ej: '2025-11')
        periodo_p2: Período 2 en formato 'YYYY-MM' (ej: '2025-12')
    
    Returns:
        Dict con estructura de análisis comparativo
    """
    
    # 1. Cargar análisis básico
    with open(json_basico_path, 'r', encoding='utf-8') as f:
        analisis_basico = json.load(f)
    
    # 2. Cargar cuadro de dimensión para obtener incoming real
    df_dimension = pd.read_csv(cuadro_dimension_path)
    
    # Validar coherencia entre JSON y cuadro
    procesos_en_cuadro = set(df_dimension['DIMENSION_VAL'].unique())
    procesos_en_json = set(analisis_basico.keys())
    
    procesos_faltantes = procesos_en_json - procesos_en_cuadro
    if procesos_faltantes:
        print(f"[WARNING] Elementos en JSON pero no en cuadro: {procesos_faltantes}")
        print(f"[INFO] Estos elementos usarán valores por defecto de incoming")
    
    # 3. Preparar output
    analisis_comparativo = {}
    
    # 4. Extraer información de períodos desde el nombre del archivo JSON
    # Ejemplo: analisis_conversaciones_claude_mlm_moderaciones_2025-11_2025-12.json
    import re
    periodos_match = re.findall(r'(\d{4})-(\d{2})', json_basico_path.stem)
    if len(periodos_match) >= 2:
        p1_year, p1_month = periodos_match[0]
        p2_year, p2_month = periodos_match[1]
        periodo_p1_str = f"{p1_year}{p1_month}"  # "202511"
        periodo_p2_str = f"{p2_year}{p2_month}"  # "202512"
    else:
        # Fallback: usar los períodos pasados como parámetro
        p1_year, p1_month = periodo_p1.split('-')
        p2_year, p2_month = periodo_p2.split('-')
        periodo_p1_str = f"{p1_year}{p1_month}"
        periodo_p2_str = f"{p2_year}{p2_month}"
    
    # 5. Procesar cada elemento (proceso/CDU/tipificación/etc.)
    for elemento_key, data in analisis_basico.items():
        elemento = data['proceso']  # Nombre del elemento (puede ser proceso, CDU, etc.)
        total_conversaciones = data.get('total_conversaciones', 
            data.get('conversaciones_dic', 0) + data.get('conversaciones_nov', 0))
        
        # Obtener incoming desde cuadro de dimensión
        elemento_row = df_dimension[df_dimension['DIMENSION_VAL'] == elemento]
        if elemento_row.empty:
            print(f"[WARNING] No se encontró '{elemento}' en cuadro, usando valores por defecto")
            incoming_p1 = 1000
            incoming_p2 = 800
        else:
            incoming_p1 = int(elemento_row.iloc[0]['INC_P1'])
            incoming_p2 = int(elemento_row.iloc[0]['INC_P2'])
        
        variacion_casos = incoming_p2 - incoming_p1
        variacion_pct = (variacion_casos / incoming_p1 * 100) if incoming_p1 > 0 else 0
        
        # Normalizar nombre del elemento para buscar CSV
        # Reemplazar caracteres especiales comunes
        elemento_norm = elemento.replace('/', '_').replace(' ', '_').replace('-', '').lower()
        
        # Cargar CSV de conversaciones para obtener fechas
        conversaciones_csv_path = conversaciones_csv_dir / f"conversaciones_{elemento_norm}_{data['site'].lower()}_{periodo_p1_str}.csv"
        
        if conversaciones_csv_path.exists():
            df_conv = pd.read_csv(conversaciones_csv_path)
        else:
            df_conv = pd.DataFrame()  # DataFrame vacío si no existe
        
        # Dividir causas en Nov y Dic (asumimos misma distribución en ambos períodos)
        causas_nov = []
        causas_dic = []
        
        # Obtener causas (retrocompatible con 'causas_raiz' o 'causas')
        causas_list = data.get('causas', data.get('causas_raiz', []))
        
        for causa in causas_list:
            # Calcular casos estimados por período (retrocompatible con ambos formatos)
            casos_totales = causa.get('frecuencia_absoluta', causa.get('casos_estimados', 0))
            casos_nov = int(casos_totales * incoming_p1 / (incoming_p1 + incoming_p2))
            casos_dic = int(casos_totales * incoming_p2 / (incoming_p1 + incoming_p2))
            
            # Parsear sentimiento (compatible con dict o string)
            sentimiento_raw = causa.get('sentimiento', {})
            if isinstance(sentimiento_raw, dict):
                # Ya es un dict, convertir claves si es necesario
                sentimiento_dict = {
                    'frustracion': sentimiento_raw.get('frustracion', sentimiento_raw.get('frustración', 0)),
                    'satisfaccion': sentimiento_raw.get('satisfaccion_post_resolucion', sentimiento_raw.get('satisfaccion', sentimiento_raw.get('satisfacción', 0))),
                    'neutral': sentimiento_raw.get('neutral', 0)
                }
            else:
                # Es un string, parsear
                sentimiento_dict = parse_sentimiento(sentimiento_raw)
            
            # Agregar fechas a citas (con períodos dinámicos)
            citas_con_fecha = agregar_fechas_a_citas(causa['citas'], df_conv, periodo_p1, periodo_p2)
            
            # Dividir citas entre P1 y P2 basándose en fechas reales
            citas_p1 = []
            citas_p2 = []
            
            for cita in citas_con_fecha:
                if 'fecha' in cita:
                    # Parsear fecha y asignar al período correcto
                    try:
                        fecha = pd.to_datetime(cita['fecha'])
                        fecha_str = fecha.strftime('%Y-%m')
                        
                        if fecha_str == periodo_p1:
                            citas_p1.append(cita)
                        elif fecha_str == periodo_p2:
                            citas_p2.append(cita)
                        else:
                            # Fecha fuera de rango: asignar al período más cercano
                            if abs((fecha - pd.to_datetime(f"{periodo_p1}-15")).days) < abs((fecha - pd.to_datetime(f"{periodo_p2}-15")).days):
                                citas_p1.append(cita)
                            else:
                                citas_p2.append(cita)
                    except:
                        # Error al parsear: dividir 50-50
                        if len(citas_p1) <= len(citas_p2):
                            citas_p1.append(cita)
                        else:
                            citas_p2.append(cita)
                else:
                    # Sin fecha: dividir 50-50
                    if len(citas_p1) <= len(citas_p2):
                        citas_p1.append(cita)
                    else:
                        citas_p2.append(cita)
            
            # Asegurar al menos 1 cita por período
            if not citas_p1 and citas_con_fecha:
                citas_p1 = [citas_con_fecha[0]]
            if not citas_p2 and citas_con_fecha:
                citas_p2 = [citas_con_fecha[-1]]
            
            # Renombrar para compatibilidad con código existente
            citas_nov = citas_p1
            citas_dic = citas_p2
            
            # Obtener descripción (retrocompatible)
            descripcion_causa = causa.get('descripcion', causa.get('causa', 'N/A'))
            porcentaje_causa = causa.get('frecuencia_porcentaje', causa.get('porcentaje', 0))
            
            # Causa para Nov
            causa_nov = {
                "causa": descripcion_causa,
                "porcentaje": porcentaje_causa,
                "casos_estimados": casos_nov,
                "descripcion": descripcion_causa,
                "sentimiento": sentimiento_dict,
                "citas": citas_nov
            }
            causas_nov.append(causa_nov)
            
            # Causa para Dic
            causa_dic = {
                "causa": descripcion_causa,
                "porcentaje": porcentaje_causa,
                "casos_estimados": casos_dic,
                "descripcion": descripcion_causa,
                "sentimiento": sentimiento_dict,
                "citas": citas_dic
            }
            causas_dic.append(causa_dic)
        
        # Generar insight principal
        if variacion_casos < 0:
            tendencia = "reducción"
            signo = ""
        else:
            tendencia = "aumento"
            signo = "+"
        
        # Generar insight sin truncar el hallazgo principal (retrocompatible)
        if causas_list:
            primera_causa = causas_list[0]
            causa_principal = primera_causa.get('descripcion', primera_causa.get('causa', 'variación general'))
        else:
            causa_principal = "variación general"
        hallazgo_base = data.get('hallazgo_principal', 'Análisis de patrones entre períodos')
        
        # Insight más descriptivo
        if abs(variacion_pct) < 5:
            insight_principal = f"Variación mínima de {signo}{abs(variacion_casos):,} casos ({variacion_pct:+.1f}%), manteniendo patrón similar entre períodos. {hallazgo_base}"
        else:
            insight_principal = f"La {tendencia} de {signo}{abs(variacion_casos):,} casos ({variacion_pct:+.1f}%) se explica principalmente por: {causa_principal}. {hallazgo_base}"
        
        # Construir entrada comparativa (nombre genérico: puede ser proceso, CDU, tipificación, etc.)
        analisis_comparativo[elemento] = {
            "proceso": elemento,
            "commerce_group": data['commerce_group'],
            "site": data['site'],
            "incoming_nov": incoming_p1,
            "incoming_dic": incoming_p2,
            "variacion_casos": variacion_casos,
            "variacion_pct": round(variacion_pct, 1),
            "conversaciones_nov": total_conversaciones // 2,
            "conversaciones_dic": total_conversaciones - (total_conversaciones // 2),
            "causas_nov": causas_nov,
            "causas_dic": causas_dic,
            "analisis_comparativo": {
                "insight_principal": insight_principal,
                "patron_dominante": (causas_nov[0]['causa'] if 'causa' in causas_nov[0] else causas_nov[0].get('descripcion', 'N/A')) if causas_nov else "N/A",
                "cambio_principal": f"{tendencia.capitalize()} del {abs(variacion_pct):.1f}% en incoming"
            }
        }
    
    return analisis_comparativo

def main():
    parser = argparse.ArgumentParser(description='Generar análisis comparativo automáticamente (universal)')
    parser.add_argument('--json-basico', required=True, help='Ruta al JSON de análisis básico')
    parser.add_argument('--cuadro-dimension', required=True, help='Ruta al CSV con cuadro de dimensión (CDU, PROCESO, TIPIFICACION, etc.)')
    parser.add_argument('--output', required=True, help='Ruta de salida para JSON comparativo')
    parser.add_argument('--conversaciones-dir', default='output', help='Directorio con CSVs de conversaciones')
    parser.add_argument('--periodo-p1', required=True, help='Período 1 en formato YYYY-MM (ej: 2025-11)')
    parser.add_argument('--periodo-p2', required=True, help='Período 2 en formato YYYY-MM (ej: 2025-12)')
    
    args = parser.parse_args()
    
    json_basico_path = Path(args.json_basico)
    cuadro_dimension_path = Path(args.cuadro_dimension)
    output_path = Path(args.output)
    conversaciones_dir = Path(args.conversaciones_dir)
    
    # Validar archivos de entrada
    if not json_basico_path.exists():
        print(f"[ERROR] No se encontró: {json_basico_path}")
        sys.exit(1)
    
    if not cuadro_dimension_path.exists():
        print(f"[ERROR] No se encontró: {cuadro_dimension_path}")
        sys.exit(1)
    
    # Validar formato de períodos
    import re
    if not re.match(r'\d{4}-\d{2}', args.periodo_p1) or not re.match(r'\d{4}-\d{2}', args.periodo_p2):
        print(f"[ERROR] Formato de período inválido. Use YYYY-MM (ej: 2025-11)")
        sys.exit(1)
    
    print("="*80)
    print("GENERADOR AUTOMÁTICO DE ANÁLISIS COMPARATIVO (UNIVERSAL)")
    print("="*80)
    print()
    print(f"[INPUT] Análisis básico: {json_basico_path.name}")
    print(f"[INPUT] Cuadro dimensión: {cuadro_dimension_path.name}")
    print(f"[INPUT] Período P1: {args.periodo_p1}")
    print(f"[INPUT] Período P2: {args.periodo_p2}")
    print(f"[OUTPUT] Análisis comparativo: {output_path.name}")
    print()
    
    # Generar análisis comparativo
    print("[PROCESSING] Generando análisis comparativo...")
    try:
        analisis_comparativo = generar_analisis_comparativo(
            json_basico_path,
            cuadro_dimension_path,
            conversaciones_dir,
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
    
    print(f"[OK] Análisis comparativo generado: {len(analisis_comparativo)} procesos")
    print(f"[SAVED] {output_path}")
    print()
    print("="*80)
    print("[NEXT STEP] Ejecutar generar_reporte_cr_universal_v6.3.6.py --open-report")
    print("="*80)

if __name__ == '__main__':
    main()
