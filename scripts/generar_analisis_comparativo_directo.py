"""
Script para generar análisis comparativo DIRECTO con detección de patrones por período
========================================================================================

NUEVA METODOLOGÍA (v3.0):
- Detecta patrones POR PERÍODO (no división proporcional)
- Identifica: PERSISTENTE, NUEVO, DESAPARECE
- Máximo 4-5 causas raíz por proceso
- Porcentajes reales de participación

DIFERENCIA vs v2.0 (generar_analisis_comparativo_auto.py):
- v2.0: Análisis global → división proporcional (PROBLEMÁTICO)
- v3.0: Análisis por período → detección real (CORRECTO)

Uso:
    python scripts/generar_analisis_comparativo_directo.py \
        --site MLM \
        --commerce-group PAGOS \
        --p1-start 2025-12-01 --p1-end 2025-12-31 \
        --p2-start 2026-01-01 --p2-end 2026-01-31 \
        --aperturas CDU \
        --output output/analisis_conversaciones_comparativo_claude_mlm_pagos_2025-12_2026-01.json

Características v3.0:
    - ✅ Prompt comparativo con conversaciones de ambos períodos
    - ✅ Detección automática de patrones (PERSISTENTE/NUEVO/DESAPARECE)
    - ✅ Máximo 4-5 causas raíz priorizadas por impacto
    - ✅ Porcentajes reales (no proporcionales)
    - ✅ Citas separadas por período con fechas reales
    - ✅ Validación de calidad (mínimo 10 conversaciones por período)

Autor: CR Commerce Analytics Team
Fecha: Febrero 2026
Version: 3.0 (Detección Directa de Patrones)
"""

import pandas as pd
import argparse
import json
from pathlib import Path
from datetime import datetime
import sys
import re

def detectar_csvs_conversaciones(output_dir: Path, site: str, commerce_group: str, dimension: str, periodo_p1: str, periodo_p2: str):
    """
    Detecta CSVs de conversaciones para ambos períodos.
    
    Args:
        output_dir: Directorio output/
        site: Site (MLM, MLA, etc.)
        commerce_group: Commerce group
        dimension: Dimensión de análisis (CDU, PROCESO, etc.)
        periodo_p1: Período 1 en formato YYYYMM (ej: 202511)
        periodo_p2: Período 2 en formato YYYYMM (ej: 202512)
    
    Returns:
        Dict con paths a CSVs por proceso
    """
    
    # Buscar CSVs con patrón: conversaciones_{elemento}_{site}_{periodo}.csv
    pattern_p1 = f"conversaciones_*_{site.lower()}_{periodo_p1}.csv"
    pattern_p2 = f"conversaciones_*_{site.lower()}_{periodo_p2}.csv"
    
    csvs_p1 = list(output_dir.glob(pattern_p1))
    csvs_p2 = list(output_dir.glob(pattern_p2))
    
    print(f"[INFO] CSVs P1 encontrados: {len(csvs_p1)}")
    print(f"[INFO] CSVs P2 encontrados: {len(csvs_p2)}")
    
    # Extraer elementos únicos
    elementos = set()
    for csv_path in csvs_p1 + csvs_p2:
        # Formato: conversaciones_{ELEMENTO}_{site}_{periodo}.csv
        match = re.match(r'conversaciones_(.+?)_([a-z]{3})_(\d{6})\.csv', csv_path.name)
        if match:
            elemento = match.group(1)
            elementos.add(elemento)
    
    print(f"[INFO] Elementos únicos detectados: {len(elementos)}")
    
    # Mapear CSVs por elemento
    csvs_map = {}
    for elemento in elementos:
        csv_p1_path = output_dir / f"conversaciones_{elemento}_{site.lower()}_{periodo_p1}.csv"
        csv_p2_path = output_dir / f"conversaciones_{elemento}_{site.lower()}_{periodo_p2}.csv"
        
        if csv_p1_path.exists() and csv_p2_path.exists():
            csvs_map[elemento] = {
                'p1': csv_p1_path,
                'p2': csv_p2_path
            }
        else:
            print(f"[WARNING] Elemento '{elemento}' no tiene ambos períodos, omitiendo")
    
    return csvs_map

def cargar_template_prompt():
    """Carga el template de prompt comparativo v2.0"""
    template_path = Path(__file__).parent.parent / 'templates' / 'prompt_analisis_conversaciones_comparativo_v2.md'
    
    if not template_path.exists():
        print(f"[ERROR] No se encontró el template de prompt: {template_path}")
        sys.exit(1)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo la sección del prompt (entre ```markdown y ```)
    match = re.search(r'```markdown\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1)
    else:
        print("[ERROR] No se pudo extraer el prompt del template")
        sys.exit(1)

def formatear_conversaciones_csv(df: pd.DataFrame, periodo_nombre: str) -> str:
    """
    Formatea conversaciones de un CSV en texto para el prompt.
    
    Args:
        df: DataFrame con conversaciones
        periodo_nombre: Nombre del período (ej: "Noviembre 2025")
    
    Returns:
        String formateado para el prompt
    """
    csv_text = ""
    for i, row in df.iterrows():
        case_id = row.get('CAS_CASE_ID', 'N/A')
        fecha = row.get('CONTACT_DATE_ID', 'N/A')
        if isinstance(fecha, str) and len(fecha) >= 10:
            fecha = fecha[:10]  # Formato YYYY-MM-DD
        
        conv = row.get('CONVERSATION_SUMMARY', '')
        # Limitar a ~300 caracteres para no exceder tokens
        conv_truncated = conv[:300] + '...' if len(conv) > 300 else conv
        
        csv_text += f"{i+1}. CASE_ID: {case_id} | Fecha: {fecha}\n"
        csv_text += f'   "{conv_truncated}"\n\n'
    
    return csv_text

def generar_prompt_comparativo(
    proceso_nombre: str,
    commerce_group: str,
    site: str,
    periodo_p1_nombre: str,
    periodo_p2_nombre: str,
    df_p1: pd.DataFrame,
    df_p2: pd.DataFrame,
    template: str
) -> str:
    """
    Genera el prompt comparativo para un proceso específico.
    
    Args:
        proceso_nombre: Nombre del proceso (ej: "Pago devuelto")
        commerce_group: Commerce group
        site: Site
        periodo_p1_nombre: Nombre legible del período 1 (ej: "Noviembre 2025")
        periodo_p2_nombre: Nombre legible del período 2 (ej: "Diciembre 2025")
        df_p1: DataFrame con conversaciones del período 1
        df_p2: DataFrame con conversaciones del período 2
        template: Template del prompt
    
    Returns:
        Prompt completo con todas las variables reemplazadas
    """
    
    n_p1 = len(df_p1)
    n_p2 = len(df_p2)
    
    # Validar mínimo 10 conversaciones por período
    if n_p1 < 10 or n_p2 < 10:
        print(f"[WARNING] {proceso_nombre}: P1={n_p1} P2={n_p2} conversaciones (mínimo 10 por período)")
        return None
    
    # Formatear conversaciones
    csv_data_p1 = formatear_conversaciones_csv(df_p1, periodo_p1_nombre)
    csv_data_p2 = formatear_conversaciones_csv(df_p2, periodo_p2_nombre)
    
    # Reemplazar variables en el template
    prompt = template
    prompt = prompt.replace('{PROCESS_NAME}', proceso_nombre)
    prompt = prompt.replace('{COMMERCE_GROUP}', commerce_group)
    prompt = prompt.replace('{SITE}', site)
    prompt = prompt.replace('{PERIODO_P1}', periodo_p1_nombre)
    prompt = prompt.replace('{PERIODO_P2}', periodo_p2_nombre)
    prompt = prompt.replace('{N_P1}', str(n_p1))
    prompt = prompt.replace('{N_P2}', str(n_p2))
    prompt = prompt.replace('{CSV_DATA_P1}', csv_data_p1)
    prompt = prompt.replace('{CSV_DATA_P2}', csv_data_p2)
    
    return prompt

def validar_json_comparativo(data: dict) -> bool:
    """
    Valida la estructura y calidad del JSON comparativo.
    
    Args:
        data: Dict con el análisis comparativo
    
    Returns:
        True si es válido, False si tiene errores críticos
    """
    
    errores = []
    
    # 1. Validar campos obligatorios
    campos_requeridos = ['proceso', 'causas', 'cobertura_p1', 'cobertura_p2', 'hallazgo_principal']
    for campo in campos_requeridos:
        if campo not in data:
            errores.append(f"Falta campo obligatorio: {campo}")
    
    # 2. Validar máximo 4-5 causas
    if len(data.get('causas', [])) > 5:
        errores.append(f"❌ CRÍTICO: {len(data['causas'])} causas (máximo 5 permitido)")
    
    # 3. Validar estructura de causas
    for i, causa in enumerate(data.get('causas', [])):
        campos_causa = ['causa', 'descripcion', 'patron', 'frecuencia_p1', 'frecuencia_p2', 
                       'porcentaje_p1', 'porcentaje_p2', 'sentimiento_p1', 'sentimiento_p2']
        for campo in campos_causa:
            if campo not in causa:
                errores.append(f"Causa {i+1}: falta campo '{campo}'")
        
        # Validar patrón
        patron = causa.get('patron', '')
        if patron not in ['PERSISTENTE', 'NUEVO', 'DESAPARECE']:
            errores.append(f"Causa {i+1}: patrón inválido '{patron}' (debe ser PERSISTENTE/NUEVO/DESAPARECE)")
        
        # Validar consistencia de patrón
        freq_p1 = causa.get('frecuencia_p1', 0)
        freq_p2 = causa.get('frecuencia_p2', 0)
        
        if patron == 'NUEVO' and freq_p1 != 0:
            errores.append(f"Causa {i+1}: patrón NUEVO pero frecuencia_p1={freq_p1} (debe ser 0)")
        
        if patron == 'DESAPARECE' and freq_p2 != 0:
            errores.append(f"Causa {i+1}: patrón DESAPARECE pero frecuencia_p2={freq_p2} (debe ser 0)")
        
        if patron == 'PERSISTENTE' and (freq_p1 == 0 or freq_p2 == 0):
            errores.append(f"Causa {i+1}: patrón PERSISTENTE pero alguna frecuencia es 0")
    
    # 4. Reportar errores
    if errores:
        print("\n[VALIDATION] Errores encontrados:")
        for error in errores:
            print(f"  - {error}")
        return False
    
    print("[VALIDATION] ✅ JSON válido")
    return True

def main():
    parser = argparse.ArgumentParser(description='Generar análisis comparativo DIRECTO con detección de patrones (v3.0)')
    parser.add_argument('--site', required=True, help='Site (MLM, MLA, etc.)')
    parser.add_argument('--commerce-group', required=True, help='Commerce group')
    parser.add_argument('--p1-start', required=True, help='Fecha inicio P1 (YYYY-MM-DD)')
    parser.add_argument('--p1-end', required=True, help='Fecha fin P1 (YYYY-MM-DD)')
    parser.add_argument('--p2-start', required=True, help='Fecha inicio P2 (YYYY-MM-DD)')
    parser.add_argument('--p2-end', required=True, help='Fecha fin P2 (YYYY-MM-DD)')
    parser.add_argument('--aperturas', required=True, help='Dimensión de análisis (CDU, PROCESO, etc.)')
    parser.add_argument('--output', required=True, help='Ruta de salida para JSON comparativo')
    parser.add_argument('--conversaciones-dir', default='output', help='Directorio con CSVs de conversaciones')
    
    args = parser.parse_args()
    
    # Parsear períodos
    p1_start = datetime.strptime(args.p1_start, '%Y-%m-%d')
    p2_start = datetime.strptime(args.p2_start, '%Y-%m-%d')
    
    periodo_p1_str = p1_start.strftime('%Y%m')  # "202511"
    periodo_p2_str = p2_start.strftime('%Y%m')  # "202512"
    
    periodo_p1_nombre = p1_start.strftime('%B %Y')  # "November 2025"
    periodo_p2_nombre = p2_start.strftime('%B %Y')  # "December 2025"
    
    # Traducir nombres de meses a español
    meses_es = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    for en, es in meses_es.items():
        periodo_p1_nombre = periodo_p1_nombre.replace(en, es)
        periodo_p2_nombre = periodo_p2_nombre.replace(en, es)
    
    print("="*80)
    print("GENERADOR DIRECTO DE ANÁLISIS COMPARATIVO (v3.0)")
    print("="*80)
    print()
    print(f"[INPUT] Site: {args.site}")
    print(f"[INPUT] Commerce Group: {args.commerce_group}")
    print(f"[INPUT] Período P1: {periodo_p1_nombre} ({periodo_p1_str})")
    print(f"[INPUT] Período P2: {periodo_p2_nombre} ({periodo_p2_str})")
    print(f"[INPUT] Dimensión: {args.aperturas}")
    print(f"[OUTPUT] {args.output}")
    print()
    
    # Detectar CSVs de conversaciones
    output_dir = Path(args.conversaciones_dir)
    csvs_map = detectar_csvs_conversaciones(
        output_dir,
        args.site,
        args.commerce_group,
        args.aperturas,
        periodo_p1_str,
        periodo_p2_str
    )
    
    if not csvs_map:
        print("[ERROR] No se encontraron CSVs de conversaciones para ambos períodos")
        sys.exit(1)
    
    print(f"[OK] {len(csvs_map)} elementos con conversaciones en ambos períodos")
    print()
    
    # Cargar template de prompt
    print("[LOADING] Template de prompt comparativo v2.0...")
    template = cargar_template_prompt()
    print("[OK] Template cargado")
    print()
    
    # Generar prompts por elemento
    print("="*80)
    print("GENERANDO PROMPTS COMPARATIVOS")
    print("="*80)
    print()
    
    prompts_generados = {}
    
    for elemento, paths in csvs_map.items():
        # Desnormalizar nombre del elemento
        elemento_real = elemento.replace('_', ' ').title()
        
        print(f"[{elemento_real}]")
        
        # Cargar conversaciones
        df_p1 = pd.read_csv(paths['p1'])
        df_p2 = pd.read_csv(paths['p2'])
        
        print(f"  - P1: {len(df_p1)} conversaciones")
        print(f"  - P2: {len(df_p2)} conversaciones")
        
        # Generar prompt
        prompt = generar_prompt_comparativo(
            elemento_real,
            args.commerce_group,
            args.site,
            periodo_p1_nombre,
            periodo_p2_nombre,
            df_p1,
            df_p2,
            template
        )
        
        if prompt:
            prompts_generados[elemento_real] = {
                'prompt': prompt,
                'n_p1': len(df_p1),
                'n_p2': len(df_p2)
            }
            print(f"  ✅ Prompt generado ({len(prompt)} caracteres)")
        else:
            print(f"  ⚠️ Omitido (< 10 conversaciones por período)")
        
        print()
    
    # Guardar prompts en archivo temporal
    prompts_file = Path(args.output).parent / f"prompts_comparativos_{args.site.lower()}_{args.commerce_group.lower()}_{periodo_p1_str}_{periodo_p2_str}.txt"
    
    with open(prompts_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("PROMPTS COMPARATIVOS PARA ANÁLISIS CON CURSOR AI\n")
        f.write("="*80 + "\n\n")
        f.write(f"Site: {args.site}\n")
        f.write(f"Commerce Group: {args.commerce_group}\n")
        f.write(f"Período P1: {periodo_p1_nombre}\n")
        f.write(f"Período P2: {periodo_p2_nombre}\n")
        f.write(f"Elementos: {len(prompts_generados)}\n\n")
        
        for i, (elemento, data) in enumerate(prompts_generados.items(), 1):
            f.write("="*80 + "\n")
            f.write(f"PROMPT {i}/{len(prompts_generados)}: {elemento}\n")
            f.write("="*80 + "\n\n")
            f.write(data['prompt'])
            f.write("\n\n")
    
    print("="*80)
    print("PROMPTS GENERADOS")
    print("="*80)
    print()
    print(f"[OK] {len(prompts_generados)} prompts generados")
    print(f"[SAVED] {prompts_file}")
    print()
    print("="*80)
    print("PRÓXIMOS PASOS")
    print("="*80)
    print()
    print("1. Abrir el archivo de prompts:")
    print(f"   {prompts_file}")
    print()
    print("2. Para cada prompt, copiar y pegar en Cursor AI")
    print()
    print("3. Cursor AI te devolverá un JSON con el análisis comparativo")
    print()
    print("4. Guardar el JSON combinado en:")
    print(f"   {args.output}")
    print()
    print("5. El JSON debe tener esta estructura:")
    print("""
{
  "Elemento 1": {
    "proceso": "Elemento 1",
    "causas": [
      {
        "causa": "Título corto",
        "descripcion": "Descripción",
        "patron": "PERSISTENTE | NUEVO | DESAPARECE",
        "frecuencia_p1": 12,
        "porcentaje_p1": 40,
        "frecuencia_p2": 18,
        "porcentaje_p2": 60,
        ...
      }
    ],
    ...
  },
  "Elemento 2": { ... }
}
""")
    print()
    print("6. Una vez guardado el JSON, ejecutar:")
    print(f"   py generar_reporte_cr_universal_v6.3.6.py --open-report")
    print()
    print("="*80)

if __name__ == '__main__':
    main()
