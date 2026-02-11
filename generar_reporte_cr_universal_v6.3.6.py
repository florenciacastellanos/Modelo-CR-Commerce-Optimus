"""
Universal CR Report Generator v6.4.9
====================================
Generador universal de reportes de Contact Rate con múltiples aperturas dinámicas.

Features v6.4.9:
- ⭐ **NUEVO v6.4.9: Muestreo proporcional a CONTRIB_ABS (contribución real a variación de CR)**
- ⭐ **NUEVO v6.4.9: Elimina sesgo por incoming - distribución basada en impacto porcentual**
- ⭐ **NUEVO v6.4.9: Mínimo garantizado de 20 conversaciones por elemento-período**
- ⭐ **NUEVO v6.4.9: Elementos con mayor contribución % a variación de CR reciben más muestra**
- ⭐ **v6.3.8: Análisis separado por período para detectar cambios REALES de patrones**
- ⭐ **v6.3.8: Porcentajes dinámicos por período (no asume patrones constantes)**
- ⭐ **v6.3.8: Exportación de CSVs separados por período (P1 y P2)**
- ⭐ **v6.3.8: Detección automática de causas que aparecen/desaparecen entre períodos**
- ⭐ **v6.3.8: Prompt inteligente que guía análisis separado con Cursor AI**
- ✅ Espera automática para análisis de conversaciones (polling sin intervención manual)
- ✅ Flujo completamente automático (exporta → espera → analiza → genera HTML)
- ✅ Modo Proceso Único (análisis de 1 proceso sin aperturas)
- ✅ Override opcional de driver por site para Shipping (--filter-driver-by-site)
- ✅ Muestreo optimizado con ponderación por picos (70% picos + 30% normales)
- ✅ Timeout handling en BigQuery (8 min límite)
- ✅ Auto-detección de dimensión más granular
- ✅ Nombres de JSON únicos por dimensión
- ✅ Encoding UTF-8 robusto para Windows
- ✅ Dimensión dinámica universal (PROCESO, CDU, TIPIFICACION, ENVIRONMENT, etc.)
- ✅ Generación automática de análisis comparativo con fallback a legacy
- ✅ División inteligente de citas por fecha real
- ⭐ Resumen Ejecutivo estructurado (3 bullets obligatorios) con evidencia cualitativa automática
- 8 cards ejecutivas (orden: CR → Var → Incoming → Drivers)
- Gráfico semanal después de cards
- Correlación con eventos comerciales (usando hard metrics)
- Cuadros cuantitativos por dimensión
- Análisis de conversaciones completo (integrado en resumen ejecutivo)
- Footer colapsable con queries ejecutadas
- Regla 80% aplicada en todas las dimensiones
- Hard metrics integrados (con fallback)
- Metodología v6.3.9

Usage:
    # Comportamiento por defecto (driver global - estándar oficial)
    python generar_reporte_cr_universal_v6.3.6.py --site MLB --p1-start 2025-11-01 --p1-end 2025-11-30 \
        --p2-start 2025-12-01 --p2-end 2025-12-31 --commerce-group FBM_SELLERS \
        --aperturas PROCESO --open-report

    # Modo Proceso Único (análisis de 1 proceso sin aperturas adicionales)
    python generar_reporte_cr_universal_v6.3.6.py --site MLB --p1-start 2025-11-01 --p1-end 2025-11-30 \
        --p2-start 2025-12-01 --p2-end 2025-12-31 --commerce-group "FBM Sellers" \
        --process-name "FBM - Inventario" --aperturas NONE --open-report

    # Con override de driver por site (requiere confirmación)
    python generar_reporte_cr_universal_v6.3.6.py --site MLB --p1-start 2025-11-01 --p1-end 2025-11-30 \
        --p2-start 2025-12-01 --p2-end 2025-12-31 --commerce-group FBM_SELLERS \
        --aperturas PROCESO --filter-driver-by-site --open-report

Version: 6.4.9
Fecha: 6 Febrero 2026
Mejoras Clave v6.4.9:
- Distribución de muestra por CONTRIB_ABS (contribución % real a variación de CR)
- Mínimo garantizado: 20 conversaciones por elemento-período
- Límite aumentado: 500 conversaciones totales (vs 400 anterior)
- Elementos con mayor impacto reciben proporcionalmente más análisis cualitativo
"""

import sys
import io

# ========================================
# FIX #9: ENCODING UTF-8 PARA WINDOWS
# ========================================
# Forzar UTF-8 en stdout/stderr para evitar UnicodeEncodeError en Windows PowerShell
if sys.platform == 'win32':
    try:
        # Reconfigurar stdout y stderr con UTF-8 y buffering de línea
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8', 
            errors='replace',  # Reemplazar caracteres no encodables en lugar de fallar
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8', 
            errors='replace',
            line_buffering=True
        )
    except Exception as e:
        # Si falla la reconfiguración, continuar con encoding por defecto
        # Esto puede suceder si stdout/stderr no son TTY
        pass

import argparse
import sys
from pathlib import Path
from datetime import datetime
import webbrowser
from google.cloud.bigquery import Client, QueryJobConfig
import pandas as pd
import json
import os
import re

# Importar módulos auxiliares
sys.path.append(str(Path(__file__).parent))

# Importar configuración de drivers
from config.drivers_mapping import get_driver_config, get_driver_description

# Importar soporte para agrupaciones de sites (ROLA, HSP)
from config.site_groups import resolve_site_sql, get_site_list, is_site_group, get_site_display_name

# ========================================
# CONFIGURACIÓN DE ANÁLISIS LLM
# ========================================

# SISTEMA DE ANÁLISIS DE CONVERSACIONES v2.2 (Auto-detección de Dimensión)
# ================================================================
# Este script usa análisis pre-generados por Claude (Cursor AI) que están guardados
# en output/analisis_conversaciones_claude_{site}_{commerce_group}_{dimension}_{p1_periodo}_{p2_periodo}.json
#
# CÓMO FUNCIONA:
# 1. El script detecta automáticamente la dimensión más granular de las aperturas solicitadas
# 2. Exporta CSVs con conversaciones muestreadas (distribuidas por impacto hasta 500 total, ponderadas por picos)
# 3. Claude (en Cursor) lee los CSVs y genera análisis estructurados con:
#    - Causas raíz específicas (cobertura ≥80%)
#    - Frecuencias y porcentajes
#    - Citas textuales con CASE_IDs reales
#    - Sentimiento por causa (frustración/satisfacción)
# 4. Los análisis se guardan en el JSON con nombre específico por análisis (incluye dimensión)
# 5. El script los carga automáticamente y los incluye en el HTML
#
# JERARQUÍA DE GRANULARIDAD (auto-detecta la más específica):
# CLA_REASON_DETAIL > SOLUTION_ID/CHANNEL_ID/SOURCE_ID > ENVIRONMENT > TIPIFICACION > CDU > PROCESO
#
# ACTUALIZAR ANÁLISIS:
# Si querés agregar o actualizar análisis para nuevos procesos/períodos:
# 1. Ejecutar este script con --export-only (generará CSVs en output/)
# 2. Pedir a Claude (Cursor AI) que analice los CSVs y cree el JSON con el nombre específico
# 3. Re-ejecutar el script sin --export-only → el reporte incluirá los análisis actualizados
#
# NOTA: La búsqueda de JSON es dinámica y se configura DESPUÉS de parsear argumentos
# ================================================================

# Variables globales (se configuran después de parsear argumentos)
ANALISIS_CLAUDE_PATH = None
USE_CLAUDE_ANALYSIS = False
ANALISIS_PREEXISTENTES = {}

print("\n" + "="*80)
print("UNIVERSAL CR REPORT GENERATOR v6.4.9 (Muestreo por CONTRIB_ABS)")
print("="*80 + "\n")
print("[INFO] Mejoras v6.4.9: Muestreo proporcional a CONTRIB_ABS (contribución real a variación de CR)")
print("[INFO] • Límite de 500 conversaciones distribuidas por CONTRIB_ABS (no por incoming)")
print("[INFO] • Mínimo 20 conversaciones por elemento-período garantizado")
print("[INFO] • 70% días pico + 30% normales por elemento")
print("[INFO] • Elementos con mayor contribución % a variación de CR reciben más muestra")
print("[INFO] • Timeout handling en BigQuery = Mayor estabilidad")
print()

# ========================================
# CONFIGURACIÓN DE MUESTREO DINÁMICO v6.4.9
# ========================================
MAX_TOTAL_CONVERSATIONS = 500  # Límite máximo optimizado para balance calidad/performance
UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO = 20  # Mínimo por elemento-período para análisis cualitativo válido

# Compatibilidad hacia atrás para validaciones globales
UMBRAL_MINIMO_CONVERSACIONES = UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO

# ========================================
# FUNCIÓN DE DISTRIBUCIÓN POR IMPACTO v6.4.9
# ========================================
def calcular_distribucion_por_impacto(df_elementos, max_total=500, min_por_elemento_periodo=20):
    """
    Distribuye muestra de conversaciones según CONTRIB_ABS (contribución real a variación de CR).
    
    Fórmula: CONTRIB_ABS = |VAR_CASOS| / TOTAL_VAR_CASOS × 100
    - Elementos con mayor contribución porcentual a la variación reciben más conversaciones
    - Garantiza mínimo de 20 conversaciones por elemento-período
    - Respeta límite global de 500 conversaciones
    - Mantiene ponderación 70% picos + 30% normales en query SQL
    
    Args:
        df_elementos: DataFrame con columnas DIMENSION_VAL, CONTRIB_ABS, INC_P1, INC_P2
        max_total: Presupuesto total de conversaciones (default: 500)
        min_por_elemento_periodo: Mínimo garantizado por elemento-período (default: 20)
    
    Returns:
        dict: {elemento: {'p1': casos_p1, 'p2': casos_p2, 'total': total, 'contribucion': valor}}
    """
    if len(df_elementos) == 0:
        return {}
    
    # Usar CONTRIB_ABS directamente (contribución porcentual real a la variación de casos)
    # Esto asegura que el muestreo sea proporcional al impacto en CR, no al incoming
    df_elementos = df_elementos.copy()
    df_elementos['CONTRIBUCION'] = df_elementos['CONTRIB_ABS'].fillna(0).abs()
    
    # Calcular peso relativo de cada elemento
    total_contribucion = df_elementos['CONTRIBUCION'].sum()
    
    if total_contribucion == 0:
        # Fallback: distribución equitativa si no hay variación
        peso_uniforme = 1.0 / len(df_elementos)
        df_elementos['PESO'] = peso_uniforme
    else:
        df_elementos['PESO'] = df_elementos['CONTRIBUCION'] / total_contribucion
    
    # Calcular muestra ideal por elemento (distribuida entre 2 períodos)
    df_elementos['MUESTRA_IDEAL_TOTAL'] = (df_elementos['PESO'] * max_total).round().astype(int)
    
    # Distribuir entre P1 y P2 según proporción de incoming
    df_elementos['PROPORCION_P1'] = df_elementos['INC_P1'] / (df_elementos['INC_P1'] + df_elementos['INC_P2'])
    df_elementos['MUESTRA_P1'] = (df_elementos['MUESTRA_IDEAL_TOTAL'] * df_elementos['PROPORCION_P1']).round().astype(int)
    df_elementos['MUESTRA_P2'] = df_elementos['MUESTRA_IDEAL_TOTAL'] - df_elementos['MUESTRA_P1']
    
    # Aplicar mínimo por período
    df_elementos['MUESTRA_P1'] = df_elementos['MUESTRA_P1'].clip(lower=min_por_elemento_periodo)
    df_elementos['MUESTRA_P2'] = df_elementos['MUESTRA_P2'].clip(lower=min_por_elemento_periodo)
    df_elementos['MUESTRA_TOTAL_AJUSTADA'] = df_elementos['MUESTRA_P1'] + df_elementos['MUESTRA_P2']
    
    # Verificar si excede presupuesto
    total_asignado = df_elementos['MUESTRA_TOTAL_AJUSTADA'].sum()
    
    if total_asignado > max_total:
        # Recortar de elementos que están por encima del mínimo
        exceso = total_asignado - max_total
        
        # Identificar elementos ajustables (aquellos con más del mínimo en algún período)
        df_elementos['AJUSTABLE_P1'] = df_elementos['MUESTRA_P1'] > min_por_elemento_periodo
        df_elementos['AJUSTABLE_P2'] = df_elementos['MUESTRA_P2'] > min_por_elemento_periodo
        df_elementos['ES_AJUSTABLE'] = df_elementos['AJUSTABLE_P1'] | df_elementos['AJUSTABLE_P2']
        
        if df_elementos['ES_AJUSTABLE'].sum() > 0:
            # Calcular excedente ajustable por elemento
            df_elementos['EXCEDENTE_P1'] = (df_elementos['MUESTRA_P1'] - min_por_elemento_periodo).clip(lower=0)
            df_elementos['EXCEDENTE_P2'] = (df_elementos['MUESTRA_P2'] - min_por_elemento_periodo).clip(lower=0)
            df_elementos['EXCEDENTE_TOTAL'] = df_elementos['EXCEDENTE_P1'] + df_elementos['EXCEDENTE_P2']
            
            total_excedente = df_elementos['EXCEDENTE_TOTAL'].sum()
            
            if total_excedente > 0:
                # Factor de reducción proporcional
                factor_reduccion = max(0, (total_excedente - exceso) / total_excedente)
                
                # Aplicar reducción proporcional al excedente
                df_elementos['REDUCCION_P1'] = (df_elementos['EXCEDENTE_P1'] * (1 - factor_reduccion)).round().astype(int)
                df_elementos['REDUCCION_P2'] = (df_elementos['EXCEDENTE_P2'] * (1 - factor_reduccion)).round().astype(int)
                
                df_elementos['MUESTRA_P1'] = df_elementos['MUESTRA_P1'] - df_elementos['REDUCCION_P1']
                df_elementos['MUESTRA_P2'] = df_elementos['MUESTRA_P2'] - df_elementos['REDUCCION_P2']
                df_elementos['MUESTRA_TOTAL_AJUSTADA'] = df_elementos['MUESTRA_P1'] + df_elementos['MUESTRA_P2']
    
    # Crear diccionario de resultado
    distribucion = {}
    for idx, row in df_elementos.iterrows():
        elemento = row['DIMENSION_VAL']
        distribucion[elemento] = {
            'p1': int(row['MUESTRA_P1']),
            'p2': int(row['MUESTRA_P2']),
            'total': int(row['MUESTRA_TOTAL_AJUSTADA']),
            'contribucion': float(row['CONTRIBUCION']),
            'peso': float(row['PESO'])
        }
    
    return distribucion

# ========================================
# CONFIGURAR BÚSQUEDA DINÁMICA DE ANÁLISIS
# ========================================
def validar_coherencia_analisis(json_procesos, elementos_priorizados):
    """
    Valida que los procesos en el JSON coincidan con los elementos priorizados actuales.
    
    Args:
        json_procesos: Lista de procesos en el JSON
        elementos_priorizados: Lista de elementos priorizados (regla 80%)
    
    Returns:
        tuple: (es_coherente: bool, mensaje: str)
    """
    json_set = set(json_procesos)
    priorizados_set = set(elementos_priorizados)
    
    if json_set == priorizados_set:
        return True, "Procesos coinciden perfectamente"
    
    missing_in_json = priorizados_set - json_set
    extra_in_json = json_set - priorizados_set
    
    mensaje_partes = []
    if missing_in_json:
        mensaje_partes.append(f"Faltan en JSON: {', '.join(missing_in_json)}")
    if extra_in_json:
        mensaje_partes.append(f"Sobran en JSON: {', '.join(extra_in_json)}")
    
    mensaje = " | ".join(mensaje_partes)
    return False, mensaje

def configurar_analisis_claude(site, commerce_group, muestreo_dimension, p1_start, p2_start, elementos_priorizados=None, usar_analisis_separado=True):
    """
    Configura la búsqueda dinámica de análisis de conversaciones.
    
    v6.3.8: Soporta análisis separado por período (P1 y P2 independientes)
    
    Busca:
    - Si usar_analisis_separado=True: 2 JSONs separados por período
      * analisis_conversaciones_claude_{site}_{cg}_{dim}_p1_{p1}.json
      * analisis_conversaciones_claude_{site}_{cg}_{dim}_p2_{p2}.json
    - Si usar_analisis_separado=False: JSON conjunto legacy
      * analisis_conversaciones_claude_{site}_{cg}_{dim}_{p1}_{p2}.json
    
    Args:
        site: Código del site (MLA, MLB, etc.)
        commerce_group: Commerce group (PDD, PNR, etc.)
        muestreo_dimension: Dimensión usada para muestreo (PROCESO, CDU, TIPIFICACION, etc.)
        p1_start: Fecha de inicio período 1 (YYYY-MM-DD)
        p2_start: Fecha de inicio período 2 (YYYY-MM-DD)
        elementos_priorizados: Lista de elementos priorizados (regla 80%) para validar coherencia
        usar_analisis_separado: Si True, busca análisis separado por período (v6.3.8+)
    """
    global ANALISIS_CLAUDE_PATH, USE_CLAUDE_ANALYSIS, ANALISIS_PREEXISTENTES
    
    # Construir nombres dinámicos
    p1_mes = p1_start[:7]  # YYYY-MM
    p2_mes = p2_start[:7]  # YYYY-MM
    
    if usar_analisis_separado:
        # v6.3.8: Buscar análisis separados por período
        analisis_p1_name = f"analisis_conversaciones_claude_{site.lower()}_{commerce_group.lower()}_{muestreo_dimension.lower()}_p1_{p1_mes}.json"
        analisis_p2_name = f"analisis_conversaciones_claude_{site.lower()}_{commerce_group.lower()}_{muestreo_dimension.lower()}_p2_{p2_mes}.json"
        
        analisis_p1_path = Path(__file__).parent / "output" / analisis_p1_name
        analisis_p2_path = Path(__file__).parent / "output" / analisis_p2_name
        
        # Guardar path legacy para compatibilidad
        analisis_json_name = f"analisis_conversaciones_claude_{site.lower()}_{commerce_group.lower()}_{muestreo_dimension.lower()}_{p1_mes}_{p2_mes}.json"
        ANALISIS_CLAUDE_PATH = Path(__file__).parent / "output" / analisis_json_name
        
        # Verificar si existen ambos JSONs
        ambos_existen = analisis_p1_path.exists() and analisis_p2_path.exists()
        
        if ambos_existen:
            try:
                # Cargar análisis P1
                with open(analisis_p1_path, 'r', encoding='utf-8') as f:
                    analisis_p1 = json.load(f)
                
                # Cargar análisis P2
                with open(analisis_p2_path, 'r', encoding='utf-8') as f:
                    analisis_p2 = json.load(f)
                
                # Combinar análisis en estructura compatible con código existente
                # Cada elemento tiene causas_p1 y causas_p2 separadas
                ANALISIS_PREEXISTENTES = {}
                
                for elemento in set(list(analisis_p1.keys()) + list(analisis_p2.keys())):
                    data_p1 = analisis_p1.get(elemento, {})
                    data_p2 = analisis_p2.get(elemento, {})
                    
                    # Crear estructura combinada (formato compatible con código existente)
                    ANALISIS_PREEXISTENTES[elemento] = {
                        "proceso": elemento,
                        "commerce_group": commerce_group,
                        "site": site,
                        "periodo": f"{p1_mes} vs {p2_mes}",
                        "total_conversaciones": data_p1.get('total_conversaciones', 0) + data_p2.get('total_conversaciones', 0),
                        "conversaciones_p1": data_p1.get('total_conversaciones', 0),
                        "conversaciones_p2": data_p2.get('total_conversaciones', 0),
                        # Mantener análisis separado
                        "causas_p1": data_p1.get('causas', []),
                        "causas_p2": data_p2.get('causas', []),
                        # Por compatibilidad, usar causas_p2 como "causas" principal
                        "causas": data_p2.get('causas', []),
                        "cobertura": data_p2.get('cobertura', {"target_pct": 80.0, "covered_pct": 100.0, "remainder_pct": 0.0}),
                        "hallazgo_principal": data_p2.get('hallazgo_principal', ''),
                        # Metadata
                        "analisis_separado": True,  # Flag para indicar que es análisis separado
                        "version": "v6.3.8"
                    }
                
                # VALIDACIÓN DE COHERENCIA (v6.3.1)
                if elementos_priorizados is not None:
                    json_procesos = list(ANALISIS_PREEXISTENTES.keys())
                    es_coherente, mensaje = validar_coherencia_analisis(json_procesos, elementos_priorizados)
                    
                    if not es_coherente:
                        print(f"[WARNING] Analisis existente NO coincide con procesos priorizados actuales")
                        print(f"[WARNING] {mensaje}")
                        print(f"[ACTION] Eliminando JSONs antiguos para forzar re-analisis...")
                        analisis_p1_path.unlink()
                        analisis_p2_path.unlink()
                        USE_CLAUDE_ANALYSIS = False
                        ANALISIS_PREEXISTENTES = {}
                        print(f"[INFO] JSONs eliminados. Re-ejecutar con --export-only para generar CSVs actualizados")
                        print()
                        return
                
                USE_CLAUDE_ANALYSIS = True
                print(f"[INFO] Analisis de Claude (separado) encontrados:")
                print(f"       - P1: {analisis_p1_name}")
                print(f"       - P2: {analisis_p2_name}")
                print(f"[INFO] {len(ANALISIS_PREEXISTENTES)} procesos con analisis cargados (v6.3.8)")
                if elementos_priorizados:
                    print(f"[VALIDACION] Coherencia verificada: procesos coinciden con priorizados actuales")
                    
            except Exception as e:
                print(f"[ERROR] No se pudieron cargar los análisis separados: {e}")
                USE_CLAUDE_ANALYSIS = False
                ANALISIS_PREEXISTENTES = {}
        else:
            USE_CLAUDE_ANALYSIS = False
            ANALISIS_PREEXISTENTES = {}
            print(f"[INFO] No se encontraron análisis pre-generados (separados por período)")
            print("[INFO] Se exportarán CSVs separados por período para análisis manual")
            print(f"[HINT] Crear JSONs:")
            print(f"       - {analisis_p1_name}")
            print(f"       - {analisis_p2_name}")
    
    else:
        # Comportamiento legacy (análisis conjunto)
        analisis_json_name = f"analisis_conversaciones_claude_{site.lower()}_{commerce_group.lower()}_{muestreo_dimension.lower()}_{p1_mes}_{p2_mes}.json"
        ANALISIS_CLAUDE_PATH = Path(__file__).parent / "output" / analisis_json_name
        
        if ANALISIS_CLAUDE_PATH.exists():
            try:
                with open(ANALISIS_CLAUDE_PATH, 'r', encoding='utf-8') as f:
                    ANALISIS_PREEXISTENTES = json.load(f)
                
                # VALIDACIÓN DE COHERENCIA
                if elementos_priorizados is not None:
                    json_procesos = list(ANALISIS_PREEXISTENTES.keys())
                    es_coherente, mensaje = validar_coherencia_analisis(json_procesos, elementos_priorizados)
                    
                    if not es_coherente:
                        print(f"[WARNING] Analisis existente NO coincide con procesos priorizados actuales")
                        print(f"[WARNING] {mensaje}")
                        print(f"[ACTION] Eliminando JSON antiguo para forzar re-analisis...")
                        ANALISIS_CLAUDE_PATH.unlink()
                        USE_CLAUDE_ANALYSIS = False
                        ANALISIS_PREEXISTENTES = {}
                        print(f"[INFO] JSON eliminado. Re-ejecutar con --export-only para generar CSVs actualizados")
                        print()
                        return
                
                USE_CLAUDE_ANALYSIS = True
                print(f"[INFO] Analisis de Claude encontrado: {analisis_json_name}")
                print(f"[INFO] {len(ANALISIS_PREEXISTENTES)} procesos con analisis cargados")
                if elementos_priorizados:
                    print(f"[VALIDACION] Coherencia verificada: procesos coinciden con priorizados actuales")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar {analisis_json_name}: {e}")
                USE_CLAUDE_ANALYSIS = False
                ANALISIS_PREEXISTENTES = {}
        else:
            USE_CLAUDE_ANALYSIS = False
            ANALISIS_PREEXISTENTES = {}
            print(f"[INFO] No se encontro analisis pre-generado: {analisis_json_name}")
            print("[INFO] Se exportaran CSVs para analisis manual")
            print(f"[HINT] Crear JSON con nombre: {analisis_json_name}")
    
    print()

# ========================================
# FUNCIÓN DE ESPERA AUTOMÁTICA PARA ANÁLISIS
# ========================================

def esperar_analisis_conversaciones(json_path, elementos_priorizados, timeout_seconds=600, check_interval=5, 
                                   site='', commerce_group='', p1_label='P1', p2_label='P2', 
                                   analisis_separado=True):
    """
    Espera automáticamente hasta que se genere el JSON de análisis de conversaciones.
    
    Args:
        json_path: Path al JSON esperado (análisis básico - DEPRECADO si analisis_separado=True)
        elementos_priorizados: Lista de elementos que deben estar en el JSON
        timeout_seconds: Tiempo máximo de espera en segundos (default: 600 = 10 min)
        check_interval: Intervalo de verificación en segundos (default: 5)
        site: Site (MLA, MLB, etc.)
        commerce_group: Commerce group (PDD, PNR, etc.)
        p1_label: Label del período 1 (ej: "Dic 2025")
        p2_label: Label del período 2 (ej: "Ene 2026")
        analisis_separado: Si True, espera 2 JSONs separados por período (v6.3.8+)
    
    Returns:
        bool: True si se detectó el JSON (o ambos JSONs), False si hubo timeout
    """
    import time
    
    if not analisis_separado:
        # Comportamiento legacy (análisis conjunto)
        print("\n" + "="*80)
        print("📊 ANÁLISIS DE CONVERSACIONES EN PROGRESO")
        print("="*80)
        print()
        print(f"[CURSOR AI] Por favor, analiza las conversaciones exportadas con este prompt:")
        print(f"━" * 80)
        print(f"Analiza las conversaciones de los CSVs exportados en output/.")
        print(f"Genera el JSON: {json_path.name}")
        print(f"━" * 80)
        print()
        print(f"[ESPERANDO] Monitoreando carpeta output/ esperando el JSON...")
        print(f"[ARCHIVO] {json_path.name}")
        print(f"[TIMEOUT] {timeout_seconds // 60} minutos máximo")
        print()
        
        elapsed = 0
        progress_interval = 30
        
        while not json_path.exists() and elapsed < timeout_seconds:
            time.sleep(check_interval)
            elapsed += check_interval
            
            if elapsed % progress_interval == 0:
                mins = elapsed // 60
                print(f"  ⏳ Esperando análisis... ({mins} min transcurridos)")
        
        if json_path.exists():
            print(f"\n✅ [OK] JSON detectado: {json_path.name}")
            print(f"[CONTINUANDO] Cargando análisis y generando reporte completo...\n")
            return True
        else:
            print(f"\n⚠️ [TIMEOUT] No se detectó el JSON después de {timeout_seconds//60} minutos")
            print(f"[INFO] El reporte se generará sin análisis comparativo de conversaciones")
            print(f"[SUGERENCIA] Genera el JSON y re-ejecuta el script para incluir el análisis")
            print()
            return False
    
    # ========================================
    # NUEVO: Análisis Separado por Período (v6.3.8)
    # ========================================
    
    # Construir nombres de JSON por período
    p1_mes = json_path.stem.split('_')[-2]  # Extraer YYYY-MM de P1
    p2_mes = json_path.stem.split('_')[-1]  # Extraer YYYY-MM de P2
    
    # Patrones de nombre para JSONs separados
    json_p1_name = json_path.name.replace(f'_{p1_mes}_{p2_mes}.json', f'_p1_{p1_mes}.json')
    json_p2_name = json_path.name.replace(f'_{p1_mes}_{p2_mes}.json', f'_p2_{p2_mes}.json')
    
    json_p1_path = json_path.parent / json_p1_name
    json_p2_path = json_path.parent / json_p2_name
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE CONVERSACIONES POR PERÍODO (v6.3.8 - Detección de Cambios)")
    print("="*80)
    print()
    print(f"[CURSOR AI] Analiza las conversaciones SEPARADAMENTE por período:")
    print(f"━" * 80)
    print()
    print(f"🔹 PASO 1: Analizar conversaciones de {p1_label}")
    print(f"   Archivos: conversaciones_*_p1_{p1_mes}.csv")
    print(f"   Generar JSON: {json_p1_name}")
    print()
    print(f"🔹 PASO 2: Analizar conversaciones de {p2_label}")
    print(f"   Archivos: conversaciones_*_p2_{p2_mes}.csv")
    print(f"   Generar JSON: {json_p2_name}")
    print()
    print(f"━" * 80)
    print()
    print(f"💡 PROMPT SUGERIDO:")
    print(f"━" * 80)
    print(f"""
Analiza las conversaciones de {site} - {commerce_group} SEPARADAS POR PERÍODO:

**PASO 1 - Análisis {p1_label}:**
1. Lee SOLO los CSVs con sufijo `_p1_{p1_mes}.csv` 
2. Para cada elemento, identifica causas raíz, porcentajes, sentimiento y citas
3. Genera: `{json_p1_name}`

**PASO 2 - Análisis {p2_label}:**
1. Lee SOLO los CSVs con sufijo `_p2_{p2_mes}.csv`
2. Para cada elemento, identifica causas raíz, porcentajes, sentimiento y citas  
3. Genera: `{json_p2_name}`

**Formato JSON requerido (para cada período):**
{{
  "Elemento 1": {{
    "proceso": "Nombre del Elemento",
    "commerce_group": "{commerce_group}",
    "site": "{site}",
    "periodo": "{p1_label}" o "{p2_label}",
    "total_conversaciones": N,
    "causas": [
      {{
        "causa": "Título corto 6-10 palabras",
        "porcentaje": X,
        "casos_estimados": Y,
        "descripcion": "Contexto específico 20-30 palabras",
        "sentimiento": {{"frustracion": X, "satisfaccion": Y}},
        "citas": [{{"case_id": "123456789", "fecha": "YYYY-MM-DD", "texto": "Texto de la conversación..."}}]
      }}
    ],
    "cobertura": {{"target_pct": 80, "covered_pct": 100, "remainder_pct": 0}},
    "hallazgo_principal": "Resumen ejecutivo con las causas raíz principales identificadas"
  }}
}}

**⚠️ IMPORTANTE - Campo 'fecha' OBLIGATORIO:**
- Cada cita DEBE incluir el campo "fecha" en formato YYYY-MM-DD
- La fecha se obtiene de la columna CONTACT_DATE_ID del CSV
- Formato final en reporte: "Caso 123456789 (2025-03-15): texto..."
""")
    print(f"━" * 80)
    print()
    print(f"[ESPERANDO] Monitoreando carpeta output/ esperando los 2 JSONs...")
    print(f"[ARCHIVOS P1] {json_p1_name}")
    print(f"[ARCHIVOS P2] {json_p2_name}")
    print(f"[TIMEOUT] {timeout_seconds // 60} minutos máximo")
    print()
    
    elapsed = 0
    progress_interval = 30
    json_p1_detectado = False
    json_p2_detectado = False
    
    while (not (json_p1_path.exists() and json_p2_path.exists())) and elapsed < timeout_seconds:
        time.sleep(check_interval)
        elapsed += check_interval
        
        # Verificar progreso y notificar
        if not json_p1_detectado and json_p1_path.exists():
            print(f"  ✅ [OK] JSON P1 detectado: {json_p1_name}")
            json_p1_detectado = True
        
        if not json_p2_detectado and json_p2_path.exists():
            print(f"  ✅ [OK] JSON P2 detectado: {json_p2_name}")
            json_p2_detectado = True
        
        # Mostrar progreso periódico
        if elapsed % progress_interval == 0:
            mins = elapsed // 60
            pendientes = []
            if not json_p1_detectado:
                pendientes.append("P1")
            if not json_p2_detectado:
                pendientes.append("P2")
            
            if pendientes:
                print(f"  ⏳ Esperando análisis de: {', '.join(pendientes)}... ({mins} min transcurridos)")
    
    # Verificar resultado final
    ambos_existen = json_p1_path.exists() and json_p2_path.exists()
    
    if ambos_existen:
        print(f"\n✅ [OK] Ambos JSONs detectados:")
        print(f"   - {json_p1_name}")
        print(f"   - {json_p2_name}")
        print(f"[CONTINUANDO] Generando análisis comparativo y reporte completo...\n")
        return True
    else:
        print(f"\n⚠️ [TIMEOUT] No se detectaron todos los JSONs después de {timeout_seconds//60} minutos")
        print(f"[STATUS] P1: {'✅ OK' if json_p1_path.exists() else '❌ Falta'}")
        print(f"[STATUS] P2: {'✅ OK' if json_p2_path.exists() else '❌ Falta'}")
        print(f"[INFO] El reporte se generará sin análisis comparativo de conversaciones")
        print(f"[SUGERENCIA] Completa ambos análisis y re-ejecuta el script")
        print()
        return False

# ========================================
# FUNCIÓN DE ANÁLISIS LLM
# ========================================

def analyze_conversations_with_llm(df_conversations, proceso, commerce_group):
    """
    Analiza conversaciones usando análisis de Claude (Cursor AI) o fallback manual.
    
    Args:
        df_conversations: DataFrame con columnas CAS_CASE_ID, CONVERSATION_SUMMARY, CONTACT_DATE_ID
        proceso: Nombre del proceso (o CDU)
        commerce_group: Commerce group (PDD, PNR, etc.)
    
    Returns:
        dict con causas raíz, frecuencias, citas, sentimiento y cobertura
    """
    n_conversaciones = len(df_conversations)
    
    # Validación 1: Sin conversaciones
    if df_conversations.empty:
        return {
            "proceso": proceso,
            "total_conversaciones": 0,
            "estado": "SIN_CONVERSACIONES",
            "causas": [],
            "cobertura": {"target_pct": 80.0, "covered_pct": 0.0, "remainder_pct": 100.0},
            "hallazgo_principal": "❌ Sin conversaciones disponibles."
        }
    
    # Validación 2: Muestra insuficiente (< UMBRAL_MINIMO)
    if n_conversaciones < UMBRAL_MINIMO_CONVERSACIONES:
        return {
            "proceso": proceso,
            "total_conversaciones": n_conversaciones,
            "estado": "MUESTRA_INSUFICIENTE",
            "causas": [],
            "cobertura": {"target_pct": 80.0, "covered_pct": 0.0, "remainder_pct": 100.0},
            "hallazgo_principal": f"⚠️ Muestra insuficiente: solo {n_conversaciones} conversaciones (mínimo requerido: {UMBRAL_MINIMO_CONVERSACIONES}). No es posible extraer conclusiones cualitativas válidas."
        }
    
    # PRIORIDAD 1: Usar análisis pre-generado por Claude si existe
    if USE_CLAUDE_ANALYSIS and proceso in ANALISIS_PREEXISTENTES:
        print(f"[CLAUDE] Usando análisis pre-generado para '{proceso}'")
        analisis = ANALISIS_PREEXISTENTES[proceso]
        # Agregar validación de umbral mínimo al análisis existente
        if analisis.get('total_conversaciones', 0) < UMBRAL_MINIMO_CONVERSACIONES:
            analisis['estado'] = 'MUESTRA_INSUFICIENTE'
            analisis['hallazgo_principal'] = f"⚠️ Muestra insuficiente: solo {analisis.get('total_conversaciones', 0)} conversaciones (mínimo requerido: {UMBRAL_MINIMO_CONVERSACIONES}). Análisis no concluyente."
        else:
            analisis['estado'] = 'ANALISIS_VALIDO'
        return analisis
    
    # FALLBACK: Sin análisis disponible (pero con muestra válida)
    return {
        "proceso": proceso,
        "total_conversaciones": n_conversaciones,
        "estado": "PENDIENTE_ANALISIS",
        "causas": [{
            "descripcion": "⚠️ Análisis disponible en CSV exportado (ejecutar analizar_conversaciones_claude.py para generar análisis)",
            "frecuencia_absoluta": n_conversaciones,
            "frecuencia_porcentaje": 100.0,
            "case_ids_ejemplo": df_conversations.head(3)['CAS_CASE_ID'].astype(str).tolist(),
            "citas": []
        }],
        "cobertura": {"target_pct": 80.0, "covered_pct": 100.0, "remainder_pct": 0.0},
        "hallazgo_principal": f"Análisis de {n_conversaciones} conversaciones disponible en CSV para revisión manual."
    }

# ========================================
# DETECCIÓN AUTOMÁTICA DE DIMENSIÓN
# ========================================

def detectar_dimension_muestreo(aperturas_list):
    """
    Detecta automáticamente la dimensión más granular de las aperturas solicitadas.
    
    Jerarquía de granularidad (de más a menos específica):
    CLA_REASON_DETAIL > SOLUTION_ID/CHANNEL_ID/SOURCE_ID > ENVIRONMENT > TIPIFICACION > CDU > PROCESO
    
    Args:
        aperturas_list: Lista de dimensiones solicitadas (ej: ['PROCESO', 'CDU'])
    
    Returns:
        str: Dimensión más granular encontrada
    """
    jerarquia_granularidad = {
        'CLA_REASON_DETAIL': 6,
        'SOLUTION_ID': 5,
        'CHANNEL_ID': 5,
        'SOURCE_ID': 5,
        'ENVIRONMENT': 4,
        'TIPIFICACION': 3,
        'CDU': 2,
        'PROCESO': 1
    }
    
    # Filtrar solo dimensiones reconocidas
    dimensiones_validas = [d for d in aperturas_list if d in jerarquia_granularidad]
    
    if not dimensiones_validas:
        return 'PROCESO'  # Fallback por defecto
    
    # Retornar la más granular (mayor valor numérico)
    return max(dimensiones_validas, key=lambda d: jerarquia_granularidad[d])

# ========================================
# CONFIGURACIÓN Y PARSEO DE ARGUMENTOS
# ========================================

parser = argparse.ArgumentParser(description='Generador Universal de Reportes CR v6.1')

# Parámetros obligatorios
parser.add_argument('--site', required=True, help='Site a analizar (ej: MLA, MLB, MLC) o grupo (ROLA, HSP)')
parser.add_argument('--p1-start', required=True, help='Fecha inicio período 1 (YYYY-MM-DD)')
parser.add_argument('--p1-end', required=True, help='Fecha fin período 1 (YYYY-MM-DD)')
parser.add_argument('--p2-start', required=True, help='Fecha inicio período 2 (YYYY-MM-DD)')
parser.add_argument('--p2-end', required=True, help='Fecha fin período 2 (YYYY-MM-DD)')
parser.add_argument('--commerce-group', required=True, 
                   help='Commerce group a analizar (PDD, PNR, PCF_COMPRADOR, PCF_VENDEDOR, ME_PREDESPACHO, etc.)')

# Parámetros opcionales
parser.add_argument('--aperturas', required=True,
                   help='Dimensiones a analizar separadas por coma (ej: PROCESO,TIPIFICACION,ENVIRONMENT,CLA_REASON_DETAIL)')
parser.add_argument('--process-name', default=None,
                   help='Filtro adicional por proceso específico (ej: "Despacho Ventas y Publicaciones")')
parser.add_argument('--output-dir', default='output', help='Directorio de salida')
parser.add_argument('--open-report', action='store_true', help='Abrir reporte al finalizar')
parser.add_argument('--skip-conversations', action='store_true', help='Saltar análisis de conversaciones')
parser.add_argument('--export-only', action='store_true',
                   help='Solo exportar CSVs de conversaciones sin generar HTML (para análisis con Cursor AI)')
parser.add_argument('--muestreo-dimension', default=None,
                   help='Dimensión para muestreo de conversaciones (auto-detecta la más granular si no se especifica)')
parser.add_argument('--filter-driver-by-site', action='store_true', default=False,
                   help='[OVERRIDE] Filtrar driver de Shipping por site (no estándar, requiere confirmación)')

args = parser.parse_args()

# Validar dates
try:
    p1_start_dt = pd.to_datetime(args.p1_start)
    p1_end_dt = pd.to_datetime(args.p1_end)
    p2_start_dt = pd.to_datetime(args.p2_start)
    p2_end_dt = pd.to_datetime(args.p2_end)
except Exception as e:
    print(f"[ERROR] Fechas inválidas: {e}")
    sys.exit(1)

# Parsear aperturas
aperturas_list = [a.strip().upper() for a in args.aperturas.split(',')]

# Auto-detectar dimensión de muestreo si no fue especificada
if args.muestreo_dimension is None:
    args.muestreo_dimension = detectar_dimension_muestreo(aperturas_list)
    print(f"[AUTO] Dimensión de muestreo detectada automáticamente: {args.muestreo_dimension}")
else:
    args.muestreo_dimension = args.muestreo_dimension.upper()

# ========================================
# RESOLUCIÓN DE SITE GROUPS (ROLA, HSP)
# ========================================
# Normalizar site a uppercase
args.site = args.site.upper()

# Pre-computar display name para site groups
site_display = get_site_display_name(args.site)
if is_site_group(args.site):
    print(f"[CONFIG] Site Group: {site_display}")
    print(f"[CONFIG] Sites incluidos: {', '.join(get_site_list(args.site))}")
else:
    print(f"[CONFIG] Site: {args.site}")

print(f"[CONFIG] Período 1: {args.p1_start} a {args.p1_end}")
print(f"[CONFIG] Período 2: {args.p2_start} a {args.p2_end}")
print(f"[CONFIG] Commerce Group: {args.commerce_group}")
if args.process_name:
    print(f"[CONFIG] Proceso específico: {args.process_name}")
print(f"[CONFIG] Aperturas: {', '.join(aperturas_list)}")
print(f"[CONFIG] Dimensión muestreo: {args.muestreo_dimension}")
print()

# ========================================
# VALIDACIÓN: OVERRIDE DE DRIVER POR SITE (SHIPPING)
# ========================================
SHIPPING_COMMERCE_GROUPS = ['FBM_SELLERS', 'ME_PREDESPACHO', 'ME_DISTRIBUCION', 'ME_DRIVERS']

if args.commerce_group.upper() in SHIPPING_COMMERCE_GROUPS and args.filter_driver_by_site:
    print("\n" + "="*80)
    print("⚠️  WARNING: OVERRIDE DE REGLA OFICIAL")
    print("="*80)
    print("\nEstás solicitando filtrar el driver de Shipping por site.")
    print("\n📋 Regla oficial (docs/SHIPPING_DRIVERS.md):")
    print("   • Driver de Shipping debe ser GLOBAL (todos los sites)")
    print("   • Incoming se filtra por site específico")
    print("\n🔧 Con --filter-driver-by-site:")
    print(f"   • Driver: Será filtrado solo por {args.site}")
    print("   • ⚠️  Esto NO es el estándar oficial")
    print("\n" + "="*80)
    
    confirmacion = input("\n¿Continuar con override? (y/n): ").strip().lower()
    
    if confirmacion != 'y':
        print("\n❌ Operación cancelada por el usuario.")
        print("✅ El driver se calculará de forma GLOBAL (estándar oficial).\n")
        args.filter_driver_by_site = False
    else:
        print("\n✅ Override confirmado. Driver será filtrado por site.")
        print("⚠️  Esto quedará indicado en el reporte HTML.\n")

# Nota: configurar_analisis_claude se llamará después de calcular elementos_priorizados (FASE 4)

# ========================================
# MAPEO DE CAMPOS POR DIMENSIÓN
# ========================================

# Mapeo de dimensiones a campos de BigQuery
FIELD_MAPPING = {
    'PROCESO': 'C.PROCESS_NAME',
    'CDU': 'C.CDU',
    'TIPIFICACION': 'C.REASON_DETAIL_GROUP_REPORTING',
    'ENVIRONMENT': 'C.ENVIRONMENT',
    'CLA_REASON_DETAIL': 'C.CLA_REASON_DETAIL',
    'SOURCE_ID': 'C.CHANNEL_ID',
    'SOLUTION_ID': 'C.SOLUTION_ID'
}

# Mapeo de commerce groups a filtros CASE
COMMERCE_GROUP_FILTERS = {
    'PDD': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PDD%') THEN 'PDD'  
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others' THEN 'PDD'
            ELSE 'OTRO' 
        END
    """,
    'PNR': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%PNR%') THEN 'PNR' 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale' THEN 'PNR'
            ELSE 'OTRO' 
        END
    """,
    'PCF_COMPRADOR': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
            AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'PCF_COMPRADOR'
            ELSE 'OTRO' 
        END
    """,
    'PCF_VENDEDOR': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra%') 
            AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'PCF_VENDEDOR'
            ELSE 'OTRO' 
        END
    """,
    'ME_PREDESPACHO': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Vendedor') THEN 'ME_PREDESPACHO'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('Post Compra Funcionalidades Vendedor') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME_PREDESPACHO'
            ELSE 'OTRO' 
        END
    """,
    'ME_DISTRIBUCION': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Mercado Envíos%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'ME_DISTRIBUCION'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Post Compra Comprador%') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME_DISTRIBUCION'
            ELSE 'OTRO' 
        END
    """,
    'ME_DRIVERS': """
        CASE 
            WHEN C.PROCESS_NAME = 'Drivers' THEN 'ME_DRIVERS'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Drivers%') THEN 'ME_DRIVERS'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Extra%') 
                 AND C.PROCESS_BU_CR_REPORTING IN ('ME') THEN 'ME_DRIVERS'
            ELSE 'OTRO' 
        END
    """,
    'GENERALES_COMPRA': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Compra%') 
                 AND C.PROCESS_GROUP_ECOMMERCE IN ('Comprador') THEN 'GENERALES_COMPRA'
            ELSE 'OTRO' 
        END
    """,
    'MODERACIONES': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Prustomer%') THEN 'MODERACIONES'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Moderaciones%') THEN 'MODERACIONES'
            ELSE 'OTRO' 
        END
    """,
    'PAGOS': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%Pagos%') THEN 'PAGOS'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP On%') THEN 'PAGOS'
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%MP Payer%') THEN 'PAGOS'
            ELSE 'OTRO' 
        END
    """,
    'FBM Sellers': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%FBM Sellers%') THEN 'FBM Sellers'
            ELSE 'OTRO' 
        END
    """,
    'FBM_SELLERS': """
        CASE 
            WHEN C.PROCESS_PROBLEMATIC_REPORTING LIKE ('%FBM Sellers%') THEN 'FBM_SELLERS'
            ELSE 'OTRO' 
        END
    """
}

# Colores por commerce group
COLORS = {
    'PDD': {'primary': '#00a650', 'badge': '#00a650'},  # Verde
    'PNR': {'primary': '#00a650', 'badge': '#00a650'},  # Verde
    'PCF_COMPRADOR': {'primary': '#00a650', 'badge': '#00a650'},  # Verde
    'PCF_VENDEDOR': {'primary': '#00a650', 'badge': '#00a650'},  # Verde
    'ME_PREDESPACHO': {'primary': '#3483fa', 'badge': '#3483fa'},  # Azul
    'ME_DISTRIBUCION': {'primary': '#3483fa', 'badge': '#3483fa'},  # Azul
    'ME_DRIVERS': {'primary': '#7c3aed', 'badge': '#7c3aed'},  # Morado (Shipping Drivers)
    'FBM Sellers': {'primary': '#3483fa', 'badge': '#3483fa'},  # Azul (Shipping FBM)
    'FBM_SELLERS': {'primary': '#3483fa', 'badge': '#3483fa'},  # Azul (Shipping FBM)
    'GENERALES_COMPRA': {'primary': '#2196f3', 'badge': '#2196f3'},  # Azul Marketplace
    'MODERACIONES': {'primary': '#2196f3', 'badge': '#2196f3'},  # Azul Marketplace
    'PAGOS': {'primary': '#ec4899', 'badge': '#ec4899'},  # Rosa (Pagos)
}

color_config = COLORS.get(args.commerce_group, {'primary': '#00a650', 'badge': '#00a650'})

# ========================================
# INICIALIZAR CLIENTE BIGQUERY
# ========================================

print("[INIT] Inicializando cliente BigQuery...")
try:
    client = Client()
    print("[OK] Cliente BigQuery inicializado\n")
except Exception as e:
    print(f"[ERROR] No se pudo inicializar BigQuery: {e}")
    sys.exit(1)

# Inicializar lista de queries ejecutadas
queries_ejecutadas = []

# ========================================
# PASO 0: CARGAR HARD METRICS (si existen)
# ========================================

print("="*80)
print("PASO 0: HARD METRICS")
print("="*80 + "\n")

def cargar_hard_metrics(site, year, month):
    """Intenta cargar hard metrics de eventos para un período dado.
    Para site groups (ROLA, HSP), carga y combina métricas de cada site individual.
    Solo combina si TODOS los sites del grupo tienen métricas; si falta alguno → fallback.
    """
    if is_site_group(site):
        # Para grupos: cargar cada site individual y combinar
        sites = get_site_list(site)
        dfs = []
        for s in sites:
            metrics_path = Path(f'metrics/eventos/data/correlacion_{s.lower()}_{year}_{month:02d}.parquet')
            if metrics_path.exists():
                try:
                    df = pd.read_parquet(metrics_path)
                    dfs.append(df)
                    print(f"[OK] Hard metrics cargadas: {metrics_path.name} ({len(df)} registros)")
                except Exception as e:
                    print(f"[WARNING] Error al cargar {metrics_path.name}: {e}")
            else:
                print(f"[INFO] No existen hard metrics para {s} {year}-{month:02d}")
        
        if len(dfs) == len(sites):
            # TODAS las métricas disponibles: combinar con pd.concat
            combined = pd.concat(dfs, ignore_index=True)
            print(f"[OK] Hard metrics combinadas para {get_site_display_name(site)}: {len(combined)} registros totales")
            return combined
        elif len(dfs) > 0:
            # Solo algunas disponibles → fallback (no usar datos parciales)
            print(f"[WARNING] Solo {len(dfs)}/{len(sites)} sites tienen hard metrics para {site}. Usando fallback.")
            return None
        else:
            print(f"[INFO] No existen hard metrics para ningún site de {site} {year}-{month:02d}")
            return None
    else:
        # Site individual: comportamiento original (sin cambios)
        metrics_path = Path(f'metrics/eventos/data/correlacion_{site.lower()}_{year}_{month:02d}.parquet')
        if metrics_path.exists():
            try:
                df = pd.read_parquet(metrics_path)
                print(f"[OK] Hard metrics cargadas: {metrics_path.name} ({len(df)} registros)")
                return df
            except Exception as e:
                print(f"[WARNING] Error al cargar {metrics_path.name}: {e}")
                return None
        else:
            print(f"[INFO] No existen hard metrics para {site} {year}-{month:02d}")
            return None

# Cargar métricas para ambos períodos
p1_year, p1_month = p1_start_dt.year, p1_start_dt.month
p2_year, p2_month = p2_start_dt.year, p2_start_dt.month

df_metrics_p1 = cargar_hard_metrics(args.site, p1_year, p1_month)
df_metrics_p2 = cargar_hard_metrics(args.site, p2_year, p2_month)

use_hard_metrics = (df_metrics_p1 is not None and df_metrics_p2 is not None)

if use_hard_metrics:
    print(f"[OK] Hard metrics disponibles para ambos períodos")
    
    # Registrar en queries ejecutadas
    queries_ejecutadas.append({
        'nombre': 'Hard Metrics - Eventos Comerciales',
        'descripcion': f'Correlación pre-calculada entre incoming y eventos (P1: {len(df_metrics_p1)} registros, P2: {len(df_metrics_p2)} registros)',
        'tabla': 'metrics/eventos/data/*.parquet',
        'output': f'Fuente: WHOWNER.LK_MKP_PROMOTIONS_EVENT'
    })
else:
    print(f"[INFO] Usando análisis fallback (sin hard metrics)")

print()

# ========================================
# PROCESAR EVENTOS COMERCIALES (v6.4.2 - Híbrido: Hard Metrics + Fallback)
# ========================================

eventos_comerciales = {}
eventos_comerciales_p1 = {}
eventos_comerciales_p2 = {}
eventos_html = ""
eventos_fuente = "No disponible"
total_casos_correlacionados = 0
porcentaje_correlacion_global = 0

def ejecutar_query_eventos_fallback(site, p1_start, p1_end, p2_start, p2_end, commerce_filter_sql):
    """Query on-the-fly para correlación con eventos comerciales cuando no hay hard metrics"""
    
    query = f"""
    -- Query Fallback: Correlación con Eventos Comerciales v6.4.2
    WITH eventos AS (
        SELECT 
            EVENT_NAME,
            DATE(EVENT_START_DTTM) as fecha_inicio,
            DATE(EVENT_END_DTTM) as fecha_fin
        FROM `meli-bi-data.WHOWNER.LK_MKP_PROMOTIONS_EVENT`
        WHERE {resolve_site_sql(site, 'SIT_SITE_ID')}
            AND (
                DATE(EVENT_START_DTTM) BETWEEN '{p1_start}' AND '{p2_end}'
                OR DATE(EVENT_END_DTTM) BETWEEN '{p1_start}' AND '{p2_end}'
            )
            AND UPPER(EVENT_NAME) NOT LIKE '%PRUEBA%'
            AND UPPER(EVENT_NAME) NOT LIKE '%TEST%'
    ),
    incoming_base AS (
        SELECT 
            c.CAS_CASE_ID,
            c.CONTACT_DATE_ID,
            pp.ORD_CLOSED_DT
        FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` c
        LEFT JOIN `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` pp 
            ON c.CLA_CLAIM_ID = pp.CLA_CLAIM_ID
        WHERE {resolve_site_sql(site, 'c.SIT_SITE_ID')}
            AND c.CONTACT_DATE_ID BETWEEN '{p1_start}' AND '{p2_end}'
            AND COALESCE(c.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
            AND COALESCE(c.QUEUE_ID, 0) NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
            AND COALESCE(c.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
            {commerce_filter_sql}
    ),
    casos_por_evento AS (
        SELECT 
            e.EVENT_NAME,
            e.fecha_inicio,
            e.fecha_fin,
            CASE 
                WHEN i.CONTACT_DATE_ID <= '{p1_end}' THEN 'P1'
                ELSE 'P2'
            END as periodo,
            COUNT(DISTINCT i.CAS_CASE_ID) as casos
        FROM incoming_base i
        JOIN eventos e 
            ON DATE(i.ORD_CLOSED_DT) BETWEEN e.fecha_inicio AND e.fecha_fin
        WHERE i.ORD_CLOSED_DT IS NOT NULL
        GROUP BY 1,2,3,4
    ),
    totales AS (
        SELECT 
            CASE 
                WHEN CONTACT_DATE_ID <= '{p1_end}' THEN 'P1'
                ELSE 'P2'
            END as periodo,
            COUNT(DISTINCT CAS_CASE_ID) as total
        FROM incoming_base
        GROUP BY 1
    )
    SELECT 
        c.EVENT_NAME,
        c.fecha_inicio,
        c.fecha_fin,
        c.periodo,
        c.casos,
        t.total as casos_totales,
        ROUND(c.casos * 100.0 / NULLIF(t.total, 0), 2) as porcentaje
    FROM casos_por_evento c
    JOIN totales t ON c.periodo = t.periodo
    ORDER BY c.casos DESC
    """
    return query

# Intentar usar hard metrics primero
eventos_from_hard_metrics = False

if use_hard_metrics:
    print("[EVENTOS] Intentando cargar desde hard metrics...")
    
    # Combinar ambos períodos
    df_metrics_combined = pd.concat([df_metrics_p1, df_metrics_p2], ignore_index=True)
    
    # Filtrar por commerce group actual
    df_eventos_cg = df_metrics_combined[
        df_metrics_combined['COMMERCE_GROUP'] == args.commerce_group
    ]
    
    
    if len(df_eventos_cg) > 0 and 'EVENTO' in df_eventos_cg.columns:
        eventos_from_hard_metrics = True
        eventos_fuente = "Hard Metrics (pre-calculadas)"
        
        # Separar por período
        for _, row in df_eventos_cg.iterrows():
            fecha_inicio = row.get('FECHA_INICIO', '')
            fecha_fin = row.get('FECHA_FIN', '')
            
            if hasattr(fecha_inicio, 'strftime'):
                fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            else:
                fecha_inicio_str = str(fecha_inicio).split(' ')[0] if fecha_inicio else ''
                
            if hasattr(fecha_fin, 'strftime'):
                fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            else:
                fecha_fin_str = str(fecha_fin).split(' ')[0] if fecha_fin else ''
            
            evento_key = row['EVENTO']
            
            # Excluir eventos de prueba/test
            if evento_key and ('PRUEBA' in str(evento_key).upper() or 'TEST' in str(evento_key).upper()):
                continue
            
            casos = int(row.get('CASOS', 0))
            porcentaje = float(row.get('PORCENTAJE', 0))
            
            # Determinar período basado en fechas
            if fecha_inicio_str <= args.p1_end:
                if evento_key not in eventos_comerciales_p1:
                    eventos_comerciales_p1[evento_key] = {
                        'nombre': evento_key,
                        'fecha_inicio': fecha_inicio_str,
                        'fecha_fin': fecha_fin_str,
                        'casos': 0,
                        'porcentaje': 0
                    }
                eventos_comerciales_p1[evento_key]['casos'] += casos
                eventos_comerciales_p1[evento_key]['porcentaje'] = porcentaje
            else:
                if evento_key not in eventos_comerciales_p2:
                    eventos_comerciales_p2[evento_key] = {
                        'nombre': evento_key,
                        'fecha_inicio': fecha_inicio_str,
                        'fecha_fin': fecha_fin_str,
                        'casos': 0,
                        'porcentaje': 0
                    }
                eventos_comerciales_p2[evento_key]['casos'] += casos
                eventos_comerciales_p2[evento_key]['porcentaje'] = porcentaje
        
        print(f"[OK] Eventos cargados desde hard metrics: P1={len(eventos_comerciales_p1)}, P2={len(eventos_comerciales_p2)}")

# Fallback: Query on-the-fly si no hay hard metrics o no tienen datos de eventos

if not eventos_from_hard_metrics:
    print("[EVENTOS] Ejecutando query fallback on-the-fly...")
    
    # Mapeo específico de commerce groups a filtros SQL para eventos (fix v6.3.9.1)
    COMMERCE_GROUP_EVENTS_FILTERS = {
        'PDD': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%PDD%' OR c.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Others')",
        'PNR': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%PNR%' OR c.PROCESS_PROBLEMATIC_REPORTING = 'Conflict Stale')",
        'PCF_COMPRADOR': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%' AND c.PROCESS_GROUP_ECOMMERCE = 'Comprador')",
        'PCF_VENDEDOR': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra%' AND c.PROCESS_GROUP_ECOMMERCE = 'Vendedor')",
        'ME_PREDESPACHO': "AND ((c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' AND c.PROCESS_GROUP_ECOMMERCE = 'Vendedor') OR (c.PROCESS_PROBLEMATIC_REPORTING LIKE 'Post Compra Funcionalidades Vendedor' AND c.PROCESS_BU_CR_REPORTING = 'ME'))",
        'ME_DISTRIBUCION': "AND ((c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Mercado Envíos%' AND c.PROCESS_GROUP_ECOMMERCE = 'Comprador') OR (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Post Compra Comprador%' AND c.PROCESS_BU_CR_REPORTING = 'ME'))",
        'GENERALES_COMPRA': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Compra%' AND c.PROCESS_GROUP_ECOMMERCE = 'Comprador')",
        'MODERACIONES': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Prustomer%' OR c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Moderaciones%')",
        'PAGOS': "AND (c.PROCESS_PROBLEMATIC_REPORTING LIKE '%Pagos%' OR c.PROCESS_PROBLEMATIC_REPORTING LIKE '%MP On%' OR c.PROCESS_PROBLEMATIC_REPORTING LIKE '%MP Payer%')",
    }
    
    # Construir filtro SQL del commerce group
    commerce_filter_sql = COMMERCE_GROUP_EVENTS_FILTERS.get(args.commerce_group, "")
    
    query_eventos = ejecutar_query_eventos_fallback(
        args.site, 
        p1_start_dt.strftime('%Y-%m-%d'), 
        p1_end_dt.strftime('%Y-%m-%d'), 
        p2_start_dt.strftime('%Y-%m-%d'), 
        p2_end_dt.strftime('%Y-%m-%d'), 
        commerce_filter_sql
    )
    
    try:
        # Ejecutar query usando cliente Python de BigQuery (fix v6.3.9.2 - compatible Windows)
        # Antes usaba subprocess.run(['bq', ...]) que fallaba en Windows con WinError 2
        print(f"[QUERY] Ejecutando query de eventos comerciales...")
        
        df_eventos = client.query(query_eventos).to_dataframe()
        
        if len(df_eventos) > 0:
            eventos_fuente = "Query On-the-fly (WHOWNER.LK_MKP_PROMOTIONS_EVENT)"
            
            # Procesar resultados por período
            for _, row in df_eventos.iterrows():
                evento_key = row['EVENT_NAME']
                periodo = row['periodo']
                
                evento_data = {
                    'nombre': evento_key,
                    'fecha_inicio': str(row['fecha_inicio']),
                    'fecha_fin': str(row['fecha_fin']),
                    'casos': int(row['casos']),
                    'porcentaje': float(row['porcentaje'])
                }
                
                if periodo == 'P1':
                    eventos_comerciales_p1[evento_key] = evento_data
                else:
                    eventos_comerciales_p2[evento_key] = evento_data
            
            print(f"[OK] Eventos desde query fallback: P1={len(eventos_comerciales_p1)}, P2={len(eventos_comerciales_p2)}")
            
            # Registrar query ejecutada
            queries_ejecutadas.append({
                'nombre': 'Eventos Comerciales (Fallback)',
                'query': query_eventos[:500] + '...',
                'output': f'{len(df_eventos)} eventos correlacionados'
            })
        else:
            print(f"[INFO] No se encontraron eventos comerciales para el período analizado")
            
    except Exception as e:
        print(f"[WARNING] Error en query fallback de eventos: {e}")

# Consolidar eventos de ambos períodos
all_eventos = set(list(eventos_comerciales_p1.keys()) + list(eventos_comerciales_p2.keys()))

for evento_key in all_eventos:
    p1_data = eventos_comerciales_p1.get(evento_key, {'casos': 0, 'porcentaje': 0})
    p2_data = eventos_comerciales_p2.get(evento_key, {'casos': 0, 'porcentaje': 0})
    
    # Usar datos del período que tenga info de fechas
    base_data = p1_data if p1_data.get('fecha_inicio') else p2_data
    
    eventos_comerciales[evento_key] = {
        'nombre': evento_key,
        'fecha_inicio': base_data.get('fecha_inicio', ''),
        'fecha_fin': base_data.get('fecha_fin', ''),
        'casos_p1': p1_data.get('casos', 0),
        'casos_p2': p2_data.get('casos', 0),
        'casos_total': p1_data.get('casos', 0) + p2_data.get('casos', 0),
        'porcentaje_p1': p1_data.get('porcentaje', 0),
        'porcentaje_p2': p2_data.get('porcentaje', 0),
        'delta_casos': p2_data.get('casos', 0) - p1_data.get('casos', 0)
    }

# Calcular totales globales
total_casos_correlacionados = sum(e['casos_total'] for e in eventos_comerciales.values())

# Generar HTML de eventos mejorado (v6.4.2)
# Definir etiquetas de período para eventos (antes de usarlas en HTML)
p1_label_eventos = f"{p1_start_dt.strftime('%b %Y')}"
p2_label_eventos = f"{p2_start_dt.strftime('%b %Y')}"

if len(eventos_comerciales) > 0:
    # Filtrar eventos con al menos 1% de correlación en algún período
    eventos_relevantes = {k: v for k, v in eventos_comerciales.items() 
                          if v['porcentaje_p1'] >= 1.0 or v['porcentaje_p2'] >= 1.0}
    
    if len(eventos_relevantes) > 0:
        # Ordenar por total de casos
        eventos_ordenados = sorted(eventos_relevantes.items(), key=lambda x: x[1]['casos_total'], reverse=True)[:10]
        
        # Determinar iconos por tipo de evento
        def get_evento_icon(nombre):
            nombre_lower = nombre.lower()
            if 'black' in nombre_lower or 'friday' in nombre_lower:
                return '🛒'
            elif 'cyber' in nombre_lower:
                return '💻'
            elif 'natal' in nombre_lower or 'navidad' in nombre_lower or 'christmas' in nombre_lower:
                return '🎄'
            elif 'hot' in nombre_lower or 'sale' in nombre_lower:
                return '🔥'
            elif 'dia' in nombre_lower or 'madre' in nombre_lower or 'padre' in nombre_lower:
                return '🎁'
            else:
                return '📅'
        
        eventos_html = f"""
        <div class="eventos-comerciales">
            <h2>🎉 Correlación con Eventos Comerciales</h2>
            <div class="info-box">
                ℹ️ Análisis basado en fecha de cierre de orden (ORD_CLOSED_DT). 
                Fuente: {eventos_fuente}
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Evento</th>
                        <th>Período del Evento</th>
                        <th>Casos {p1_label_eventos}</th>
                        <th>Casos {p2_label_eventos}</th>
                        <th>Δ Casos</th>
                        <th>% Correlación</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for evento_nombre, evento_data in eventos_ordenados:
            icon = get_evento_icon(evento_nombre)
            delta = evento_data['delta_casos']
            
            # Badge de variación
            if delta > 0:
                badge_class = "badge-negative"
                delta_text = f"+{delta:,}"
            elif delta < 0:
                badge_class = "badge-positive"
                delta_text = f"{delta:,}"
            else:
                badge_class = "badge-neutral"
                delta_text = "0"
            
            # Porcentaje promedio
            pct_avg = (evento_data['porcentaje_p1'] + evento_data['porcentaje_p2']) / 2 if evento_data['porcentaje_p1'] > 0 and evento_data['porcentaje_p2'] > 0 else max(evento_data['porcentaje_p1'], evento_data['porcentaje_p2'])
            
            eventos_html += f"""
                    <tr>
                        <td class="evento-nombre"><span class="evento-icon">{icon}</span>{evento_data['nombre']}</td>
                        <td>{evento_data['fecha_inicio']} → {evento_data['fecha_fin']}</td>
                        <td class="number">{evento_data['casos_p1']:,}</td>
                        <td class="number">{evento_data['casos_p2']:,}</td>
                        <td class="number"><span class="badge {badge_class}">{delta_text}</span></td>
                        <td class="number">{pct_avg:.1f}%</td>
                    </tr>
            """
        
        eventos_html += """
                </tbody>
            </table>
            <div class="summary">
                <span class="summary-icon">💡</span>
                <span class="summary-text">
        """
        eventos_html += f"<strong>{total_casos_correlacionados:,}</strong> casos del incoming están correlacionados con eventos comerciales del período analizado."
        eventos_html += """
                </span>
            </div>
        </div>
        """
        
        print(f"[OK] HTML de eventos generado con {len(eventos_ordenados)} eventos relevantes")
    else:
        # v6.4.3: Ocultar sección si no hay eventos con correlación significativa
        print("[INFO] No se encontraron eventos con correlacion >=1% - sección oculta")
        eventos_html = ""
else:
    # v6.4.3: Ocultar sección si no hay datos de eventos comerciales
    print("[INFO] No hay datos de eventos comerciales disponibles - sección oculta")
    eventos_html = ""

print()

# ========================================
# CUADRO CROSS-SITE (Vista Comparativa Pre-Reporte)
# ========================================

def generar_cuadro_cross_site(client, commerce_group, p1_start, p1_end, p2_start, p2_end, process_name=None):
    """
    Genera un cuadro cuantitativo cross-site con métricas de CR desglosadas por site.
    
    Muestra una tabla en consola con sites en filas (MLA, MLB, MLM, ROLA, TOTAL)
    y métricas en columnas (Incoming, Variación, CR, Variación CR).
    
    Además, genera una sección HTML que se inyecta automáticamente en el reporte
    a través de la variable global eventos_html (aparece después de Eventos Comerciales
    y antes de los Cuadros Cuantitativos por Dimensión).
    
    Driver: SIEMPRE global (sin filtro de site) independientemente del commerce group.
    
    Este cuadro es ADITIVO al flujo existente y NO modifica ninguna funcionalidad.
    Si ocurre un error, se loguea y el flujo principal continúa sin interrupción.
    
    Args:
        client: Cliente BigQuery inicializado
        commerce_group: Nombre del commerce group (ej: 'PDD', 'PNR', 'ME_DISTRIBUCION')
        p1_start: Fecha inicio P1 (str YYYY-MM-DD)
        p1_end: Fecha fin P1 (str YYYY-MM-DD)
        p2_start: Fecha inicio P2 (str YYYY-MM-DD)
        p2_end: Fecha fin P2 (str YYYY-MM-DD)
        process_name: Nombre del proceso específico (opcional)
    """
    global eventos_html
    
    # Obtener filtro del commerce group
    commerce_filter = COMMERCE_GROUP_FILTERS.get(commerce_group)
    if not commerce_filter:
        print(f"[CROSS-SITE] Commerce group '{commerce_group}' no tiene filtro definido - saltando cuadro cross-site")
        return
    
    # Obtener configuración de driver
    try:
        driver_config = get_driver_config(commerce_group)
    except KeyError:
        print(f"[CROSS-SITE] Commerce group '{commerce_group}' no tiene driver configurado - saltando cuadro cross-site")
        return
    
    # Filtro de proceso (si aplica)
    process_filter_sql = ""
    if process_name:
        process_name_escaped = process_name.replace("'", "''")
        process_filter_sql = f"AND C.PROCESS_NAME LIKE '%{process_name_escaped}%'"
    
    print("=" * 80)
    print("CUADRO CROSS-SITE (Vista Comparativa)")
    print("=" * 80 + "\n")
    
    # ─────────────────────────────────────────────────
    # Query 1: Incoming por site (GROUP BY SIT_SITE_ID)
    # ─────────────────────────────────────────────────
    print("[CROSS-SITE] Calculando incoming por site...")
    
    query_incoming_cross = f"""
    WITH BASE_CONTACTS AS (
        SELECT
            C.SIT_SITE_ID,
            DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
            {commerce_filter} AS AGRUP_COMMERCE,
            1.0 AS CANT_CASES
        FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
        WHERE C.SIT_SITE_ID IN ('MLA', 'MLB', 'MLC', 'MCO', 'MEC', 'MLM', 'MLU', 'MPE')
            AND C.CONTACT_DATE_ID BETWEEN '{p1_start}' AND '{p2_end}'
            AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
            AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
            AND C.SIT_SITE_ID NOT IN ('MLV')
            AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
            AND C.PROCESS_ID NOT IN (1312)
            AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
            {process_filter_sql}
    ),
    BASE_FILTERED AS (
        SELECT * FROM BASE_CONTACTS
        WHERE AGRUP_COMMERCE = '{commerce_group}'
    )
    SELECT 
        SIT_SITE_ID,
        SUM(CASE WHEN PERIODO BETWEEN '{p1_start}' AND '{p1_end}' THEN CANT_CASES ELSE 0 END) as INC_P1,
        SUM(CASE WHEN PERIODO BETWEEN '{p2_start}' AND '{p2_end}' THEN CANT_CASES ELSE 0 END) as INC_P2
    FROM BASE_FILTERED
    GROUP BY SIT_SITE_ID
    ORDER BY SIT_SITE_ID
    """
    
    try:
        df_inc_cross = client.query(query_incoming_cross).to_dataframe()
        print(f"[CROSS-SITE] OK - Incoming obtenido para {len(df_inc_cross)} sites")
    except Exception as e:
        print(f"[CROSS-SITE] Error en query de incoming: {e}")
        print("[CROSS-SITE] Continuando con flujo normal...\n")
        return
    
    # ─────────────────────────────────────────────────
    # Query 2: Driver GLOBAL (sin filtro de site)
    # ─────────────────────────────────────────────────
    print("[CROSS-SITE] Calculando driver global (sin filtro site)...")
    
    if driver_config['type'] == 'shipping_drivers':
        # Shipping: usar BT_CX_DRIVERS_CR sin filtro de site
        count_expr_raw = driver_config['count_expression'].replace('SUM(drv.', 'drv.').replace(')', '')
        query_driver_global = f"""
        SELECT
            SUM(CASE WHEN drv.MONTH_ID BETWEEN '{p1_start}' AND '{p1_end}' THEN {count_expr_raw} ELSE 0 END) as DRV_P1,
            SUM(CASE WHEN drv.MONTH_ID BETWEEN '{p2_start}' AND '{p2_end}' THEN {count_expr_raw} ELSE 0 END) as DRV_P2
        FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
        WHERE drv.MONTH_ID BETWEEN '{p1_start}' AND '{p2_end}'
        """
    else:
        # Orders-based driver (global, sin filtro site)
        query_driver_global = f"""
        SELECT
            SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{p1_start}' AND '{p1_end}' THEN 1 ELSE 0 END) as DRV_P1,
            SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{p2_start}' AND '{p2_end}' THEN 1 ELSE 0 END) as DRV_P2
        FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
        WHERE ORD.ORD_CLOSED_DT BETWEEN '{p1_start}' AND '{p2_end}'
            AND ORD.ORD_CLOSED_DT IS NOT NULL
            AND ORD.ORD_GMV_FLG = TRUE
            AND ORD.ORD_MARKETPLACE_FLG = TRUE
            AND ORD.SIT_SITE_ID NOT IN ('MLV')
            AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
        """
    
    try:
        df_drv_global = client.query(query_driver_global).to_dataframe()
        drv_p1 = int(df_drv_global['DRV_P1'].iloc[0])
        drv_p2 = int(df_drv_global['DRV_P2'].iloc[0])
        print(f"[CROSS-SITE] OK - Driver global P1: {drv_p1:,} | P2: {drv_p2:,}")
    except Exception as e:
        print(f"[CROSS-SITE] Error en query de driver: {e}")
        print("[CROSS-SITE] Continuando con flujo normal...\n")
        return
    
    if drv_p1 == 0 or drv_p2 == 0:
        print("[CROSS-SITE] Driver es 0 en algún período - no se puede calcular CR")
        print("[CROSS-SITE] Continuando con flujo normal...\n")
        return
    
    # ─────────────────────────────────────────────────
    # Construir datos por site
    # ─────────────────────────────────────────────────
    ROLA_SITES = ['MLC', 'MCO', 'MEC', 'MLU', 'MPE']
    default_site_data = {'inc_p1': 0, 'inc_p2': 0}
    
    site_data = {}
    for _, row in df_inc_cross.iterrows():
        site_id = row['SIT_SITE_ID']
        site_data[site_id] = {
            'inc_p1': int(row['INC_P1']),
            'inc_p2': int(row['INC_P2'])
        }
    
    def calcular_metricas_site(site_label, inc_p1, inc_p2, drv_p1, drv_p2):
        """Calcula métricas de CR para un site dado."""
        var_inc = inc_p2 - inc_p1
        var_inc_pct = (var_inc / inc_p1 * 100) if inc_p1 > 0 else 0
        cr_p1 = (inc_p1 / drv_p1 * 100) if drv_p1 > 0 else 0
        cr_p2 = (inc_p2 / drv_p2 * 100) if drv_p2 > 0 else 0
        var_cr = cr_p2 - cr_p1
        return {
            'site': site_label,
            'inc_p1': inc_p1, 'inc_p2': inc_p2,
            'var_inc': var_inc, 'var_inc_pct': var_inc_pct,
            'cr_p1': cr_p1, 'cr_p2': cr_p2,
            'var_cr': var_cr, 'contrib_pct': 0  # Se calcula después con el total
        }
    
    # Sites individuales: MLA, MLB, MLM
    display_rows = []
    for site_name in ['MLA', 'MLB', 'MLM']:
        data = site_data.get(site_name, default_site_data)
        display_rows.append(
            calcular_metricas_site(site_name, data['inc_p1'], data['inc_p2'], drv_p1, drv_p2)
        )
    
    # ROLA: suma de MLC + MCO + MEC + MLU + MPE
    rola_inc_p1 = sum(site_data.get(s, default_site_data)['inc_p1'] for s in ROLA_SITES)
    rola_inc_p2 = sum(site_data.get(s, default_site_data)['inc_p2'] for s in ROLA_SITES)
    display_rows.append(
        calcular_metricas_site('ROLA', rola_inc_p1, rola_inc_p2, drv_p1, drv_p2)
    )
    
    # TOTAL: suma de todos los sites (MLA + MLB + MLM + ROLA)
    total_inc_p1 = sum(r['inc_p1'] for r in display_rows)
    total_inc_p2 = sum(r['inc_p2'] for r in display_rows)
    total_row = calcular_metricas_site('TOTAL', total_inc_p1, total_inc_p2, drv_p1, drv_p2)
    
    # Calcular contribución % de cada site a la variación total de CR
    total_var_cr = total_row['var_cr']
    for row in display_rows:
        row['contrib_pct'] = (row['var_cr'] / total_var_cr * 100) if total_var_cr != 0 else 0
    total_row['contrib_pct'] = 100.0
    
    # ─────────────────────────────────────────────────
    # Imprimir tabla en consola
    # ─────────────────────────────────────────────────
    sep = "\u2500"
    
    proceso_label = f" > {process_name}" if process_name else ""
    print(f"\n  \U0001F4CA CUADRO CROSS-SITE | {commerce_group}{proceso_label}")
    print(f"  Driver: GLOBAL (sin filtro site) | {driver_config['description']}")
    print()
    
    # Encabezados
    header = (
        f"  {'Site':<8} \u2502 {'Inc P1':>10} \u2502 {'Inc P2':>10} \u2502 "
        f"{'Var Inc':>10} \u2502 {'Var %':>8} \u2502 "
        f"{'CR P1 (pp)':>10} \u2502 {'CR P2 (pp)':>10} \u2502 "
        f"{'Var CR pp':>10} \u2502 {'Contrib %':>9}"
    )
    
    line_top = (
        f"  {sep*8}\u252C{sep*12}\u252C{sep*12}\u252C"
        f"{sep*12}\u252C{sep*10}\u252C"
        f"{sep*12}\u252C{sep*12}\u252C"
        f"{sep*12}\u252C{sep*11}"
    )
    line_mid = (
        f"  {sep*8}\u253C{sep*12}\u253C{sep*12}\u253C"
        f"{sep*12}\u253C{sep*10}\u253C"
        f"{sep*12}\u253C{sep*12}\u253C"
        f"{sep*12}\u253C{sep*11}"
    )
    line_bot = (
        f"  {sep*8}\u2534{sep*12}\u2534{sep*12}\u2534"
        f"{sep*12}\u2534{sep*10}\u2534"
        f"{sep*12}\u2534{sep*12}\u2534"
        f"{sep*12}\u2534{sep*11}"
    )
    
    print(line_top)
    print(header)
    print(line_mid)
    
    # Filas de sites
    for row in display_rows:
        print(
            f"  {row['site']:<8} \u2502 {row['inc_p1']:>10,} \u2502 {row['inc_p2']:>10,} \u2502 "
            f"{row['var_inc']:>+10,} \u2502 {row['var_inc_pct']:>+7.1f}% \u2502 "
            f"{row['cr_p1']:>10.4f} \u2502 {row['cr_p2']:>10.4f} \u2502 "
            f"{row['var_cr']:>+10.4f} \u2502 {row['contrib_pct']:>8.1f}%"
        )
    
    # Separador antes del total
    print(line_mid)
    
    # Fila TOTAL
    print(
        f"  {total_row['site']:<8} \u2502 {total_row['inc_p1']:>10,} \u2502 {total_row['inc_p2']:>10,} \u2502 "
        f"{total_row['var_inc']:>+10,} \u2502 {total_row['var_inc_pct']:>+7.1f}% \u2502 "
        f"{total_row['cr_p1']:>10.4f} \u2502 {total_row['cr_p2']:>10.4f} \u2502 "
        f"{total_row['var_cr']:>+10.4f} \u2502 {total_row['contrib_pct']:>8.1f}%"
    )
    
    print(line_bot)
    
    # Nota al pie
    print(f"\n  Nota: Driver P1={drv_p1:,} | Driver P2={drv_p2:,} (global, aplicado a todos los sites)")
    print()
    
    # ─────────────────────────────────────────────────
    # Generar HTML e inyectar en reporte via eventos_html
    # ─────────────────────────────────────────────────
    # Se usa la variable global eventos_html (ya definida antes de esta llamada)
    # para inyectar la tabla cross-site en el HTML del reporte. Aparece después
    # de Eventos Comerciales y antes de Cuadros Cuantitativos por Dimensión.
    
    try:
        # Derivar labels de período desde las fechas
        _p1_dt = datetime.strptime(p1_start, '%Y-%m-%d')
        _p2_dt = datetime.strptime(p2_start, '%Y-%m-%d')
        _p1_lbl = _p1_dt.strftime('%b %Y')
        _p2_lbl = _p2_dt.strftime('%b %Y')
        
        _proceso_html = f" &gt; {process_name}" if process_name else ""
        
        # Mapeo de banderas por site
        _site_flags = {
            'MLA': '\U0001F1E6\U0001F1F7',  # Argentina
            'MLB': '\U0001F1E7\U0001F1F7',  # Brasil
            'MLM': '\U0001F1F2\U0001F1FD',  # México
            'ROLA': '\U0001F30E',            # Resto de LATAM
        }
        
        # Construir filas HTML de sites
        _rows_html = ""
        for row in display_rows:
            _flag = _site_flags.get(row['site'], '')
            _var_inc_cls = 'negative' if row['var_inc'] > 0 else ('positive' if row['var_inc'] < 0 else '')
            _var_cr_cls = 'negative' if row['var_cr'] > 0 else ('positive' if row['var_cr'] < 0 else '')
            
            # Barra visual proporcional a contrib % (máximo 100px)
            _bar_width = min(abs(row['contrib_pct']), 100)
            _bar_color = '#F23D4F' if (row['contrib_pct'] > 0 and total_var_cr > 0) or (row['contrib_pct'] < 0 and total_var_cr < 0) else '#00A650'
            if total_var_cr == 0:
                _bar_color = '#666666'
            
            _rows_html += f"""
                    <tr>
                        <td><strong>{_flag} {row['site']}</strong></td>
                        <td class="number">{row['inc_p1']:,.0f}</td>
                        <td class="number">{row['inc_p2']:,.0f}</td>
                        <td class="number {_var_inc_cls}">{row['var_inc']:+,.0f}</td>
                        <td class="number {_var_inc_cls}">{row['var_inc_pct']:+.1f}%</td>
                        <td class="number">{row['cr_p1']:.4f}</td>
                        <td class="number">{row['cr_p2']:.4f}</td>
                        <td class="number {_var_cr_cls}">{row['var_cr']:+.4f}</td>
                        <td class="number">
                            <div style="display:flex;align-items:center;justify-content:flex-end;gap:6px;">
                                <span>{abs(row['contrib_pct']):.1f}%</span>
                                <div style="width:{_bar_width}px;height:8px;background:{_bar_color};border-radius:4px;min-width:2px;"></div>
                            </div>
                        </td>
                    </tr>"""
        
        # Fila TOTAL
        _var_inc_cls_total = 'negative' if total_row['var_inc'] > 0 else ('positive' if total_row['var_inc'] < 0 else '')
        _var_cr_cls_total = 'negative' if total_row['var_cr'] > 0 else ('positive' if total_row['var_cr'] < 0 else '')
        
        _total_html = f"""
                    <tr class="row-total">
                        <td><strong>\U0001F310 TOTAL</strong></td>
                        <td class="number">{total_row['inc_p1']:,.0f}</td>
                        <td class="number">{total_row['inc_p2']:,.0f}</td>
                        <td class="number">{total_row['var_inc']:+,.0f}</td>
                        <td class="number">{total_row['var_inc_pct']:+.1f}%</td>
                        <td class="number">{total_row['cr_p1']:.4f}</td>
                        <td class="number">{total_row['cr_p2']:.4f}</td>
                        <td class="number">{total_row['var_cr']:+.4f}</td>
                        <td class="number">100.0%</td>
                    </tr>"""
        
        # Determinar dirección general del CR para el highlight
        if total_row['var_cr'] < 0:
            _highlight_icon = '\U0001F4C9'  # chart decreasing = mejora
            _highlight_text = f"CR mejoró <strong>{total_row['var_cr']:+.4f} pp</strong> ({total_row['var_inc_pct']:+.1f}% incoming)"
            _highlight_border = '#00A650'
        elif total_row['var_cr'] > 0:
            _highlight_icon = '\U0001F4C8'  # chart increasing = empeora
            _highlight_text = f"CR empeoró <strong>{total_row['var_cr']:+.4f} pp</strong> ({total_row['var_inc_pct']:+.1f}% incoming)"
            _highlight_border = '#F23D4F'
        else:
            _highlight_icon = '\u2796'  # minus = sin cambio
            _highlight_text = "CR sin variación entre períodos"
            _highlight_border = '#666666'
        
        # Encontrar el site con mayor contribución absoluta (excluyendo TOTAL)
        _top_site = max(display_rows, key=lambda r: abs(r['contrib_pct']))
        _top_flag = _site_flags.get(_top_site['site'], '')
        _top_direction = 'empeora' if _top_site['var_cr'] > 0 else 'mejora'
        
        # Ensamblar HTML completo de la sección
        _cross_site_html = f"""
        <div class="section">
            <h2>\U0001F30E Vista Cross-Site | {commerce_group}{_proceso_html}</h2>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;padding:12px 16px;background:#F5F5F5;border-radius:8px;border-left:4px solid {_highlight_border};">
                <span style="font-size:24px;">{_highlight_icon}</span>
                <span style="font-size:14px;color:#333;">{_highlight_text} &mdash; Mayor contribución: <strong>{_top_flag} {_top_site['site']}</strong> ({_top_direction} {abs(_top_site['var_cr']):.4f} pp, {abs(_top_site['contrib_pct']):.1f}% del total)</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Site</th>
                        <th class="number">Inc {_p1_lbl}</th>
                        <th class="number">Inc {_p2_lbl}</th>
                        <th class="number">Var Inc</th>
                        <th class="number">Var %</th>
                        <th class="number">CR {_p1_lbl} (pp)</th>
                        <th class="number">CR {_p2_lbl} (pp)</th>
                        <th class="number">Var CR (pp)</th>
                        <th class="number">Contrib %</th>
                    </tr>
                </thead>
                <tbody>{_rows_html}{_total_html}
                </tbody>
            </table>
            <div class="note">
                <strong>\u2699\uFE0F Driver:</strong> GLOBAL (sin filtro de site) | {driver_config['description']} | P1: {drv_p1:,} | P2: {drv_p2:,}
            </div>
        </div>"""
        
        eventos_html += _cross_site_html
        print("[CROSS-SITE] HTML cross-site generado e inyectado en el reporte")
        
    except Exception as e:
        print(f"[CROSS-SITE] Error generando HTML (no afecta consola ni flujo): {e}")
        print("[CROSS-SITE] El cuadro en consola se generó correctamente, continuando...")


# Ejecutar cuadro cross-site (aditivo, no modifica el flujo principal)
try:
    generar_cuadro_cross_site(
        client, 
        args.commerce_group, 
        args.p1_start, args.p1_end, 
        args.p2_start, args.p2_end, 
        args.process_name
    )
except Exception as e:
    print(f"[CROSS-SITE] Error inesperado: {e}")
    print("[CROSS-SITE] Continuando con flujo normal...\n")

# ========================================
# PASO 1: CALCULAR MÉTRICAS CONSOLIDADAS
# ========================================

print("="*80)
print("PASO 1: MÉTRICAS CONSOLIDADAS")
print("="*80 + "\n")

# Obtener filtro del commerce group
commerce_filter = COMMERCE_GROUP_FILTERS.get(args.commerce_group)
if not commerce_filter:
    print(f"[ERROR] Commerce group '{args.commerce_group}' no tiene filtro definido")
    sys.exit(1)

print(f"[QUERY] Calculando incoming total...")

# Agregar filtro de proceso si está especificado
process_filter = ""
if args.process_name:
    # Escapar comillas simples en el nombre del proceso
    process_name_escaped = args.process_name.replace("'", "''")
    process_filter = f"AND C.PROCESS_NAME LIKE '%{process_name_escaped}%'"
    print(f"[INFO] Filtrando por proceso: {args.process_name}")

query_incoming_total = f"""
WITH BASE_CONTACTS AS (
    SELECT
        DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
        {commerce_filter} AS AGRUP_COMMERCE,
        1.0 AS CANT_CASES
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE {resolve_site_sql(args.site, 'C.SIT_SITE_ID')}
        AND C.CONTACT_DATE_ID BETWEEN '{args.p1_start}' AND '{args.p2_end}'
        AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND C.PROCESS_ID NOT IN (1312)
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        {process_filter}
),
BASE_FILTERED AS (
    SELECT * FROM BASE_CONTACTS
    WHERE AGRUP_COMMERCE = '{args.commerce_group}'
)
SELECT 
    SUM(CASE WHEN PERIODO BETWEEN '{args.p1_start}' AND '{args.p1_end}' THEN CANT_CASES ELSE 0 END) as INC_P1,
    SUM(CASE WHEN PERIODO BETWEEN '{args.p2_start}' AND '{args.p2_end}' THEN CANT_CASES ELSE 0 END) as INC_P2
FROM BASE_FILTERED
"""

df_inc_total = client.query(query_incoming_total).to_dataframe()
inc_p1_total = int(df_inc_total['INC_P1'].iloc[0])
inc_p2_total = int(df_inc_total['INC_P2'].iloc[0])

# Registrar query ejecutada
queries_ejecutadas.append({
    'nombre': 'Incoming Total',
    'descripcion': f'Casos totales para {args.commerce_group} en ambos períodos',
    'tabla': 'BT_CX_CONTACTS',
    'output': f'P1: {inc_p1_total:,} casos | P2: {inc_p2_total:,} casos'
})
var_inc_total = inc_p2_total - inc_p1_total

print(f"[OK] Incoming P1: {inc_p1_total:,}")
print(f"[OK] Incoming P2: {inc_p2_total:,}")
print(f"[OK] Variación: {var_inc_total:+,} casos")
print()

# ========================================
# CALCULAR DRIVERS DINÁMICAMENTE SEGÚN COMMERCE GROUP
# ========================================
# Obtener configuración de driver para este commerce group
driver_config = get_driver_config(args.commerce_group)
driver_desc = get_driver_description(args.commerce_group, args.site)

# Agregar indicador de override si corresponde
if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site:
    driver_desc = f"{driver_desc} ({args.site} únicamente) ⚠️ MODO OVERRIDE"

print(f"[DRIVER] Commerce Group: {args.commerce_group}")
print(f"[DRIVER] Tipo: {driver_config['type']}")
print(f"[DRIVER] Tabla: {driver_config['table']}")
print(f"[DRIVER] Filtrar por site: {'SÍ' if driver_config['filter_by_site'] or (driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site) else 'NO (GLOBAL)'}")
print(f"[DRIVER] Descripción: {driver_desc}")
print()

print(f"[QUERY] Calculando drivers totales...")

# Generar query según tipo de driver
if driver_config['type'] == 'shipping_drivers':
    # Drivers de Shipping: usar BT_CX_DRIVERS_CR
    # Por defecto es GLOBAL, pero puede filtrarse por site con --filter-driver-by-site
    site_filter = f"AND {resolve_site_sql(args.site, 'drv.SIT_SITE_ID')}" if args.filter_driver_by_site else ""
    
    query_drivers_total = f"""
    SELECT
        SUM(CASE WHEN drv.MONTH_ID BETWEEN '{args.p1_start}' AND '{args.p1_end}' THEN {driver_config['count_expression'].replace('SUM(drv.', 'drv.').replace(')', '')} ELSE 0 END) as DRV_P1,
        SUM(CASE WHEN drv.MONTH_ID BETWEEN '{args.p2_start}' AND '{args.p2_end}' THEN {driver_config['count_expression'].replace('SUM(drv.', 'drv.').replace(')', '')} ELSE 0 END) as DRV_P2
    FROM `meli-bi-data.WHOWNER.BT_CX_DRIVERS_CR` drv
    WHERE drv.MONTH_ID BETWEEN '{args.p1_start}' AND '{args.p2_end}'
    {site_filter}
    """
    
elif driver_config['filter_by_site']:
    # Marketplace: Órdenes filtradas por site
    query_drivers_total = f"""
    SELECT
        SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{args.p1_start}' AND '{args.p1_end}' THEN 1 ELSE 0 END) as DRV_P1,
        SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{args.p2_start}' AND '{args.p2_end}' THEN 1 ELSE 0 END) as DRV_P2
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
    WHERE ORD.ORD_CLOSED_DT BETWEEN '{args.p1_start}' AND '{args.p2_end}'
        AND ORD.ORD_CLOSED_DT IS NOT NULL
        AND ORD.ORD_GMV_FLG = TRUE
        AND ORD.ORD_MARKETPLACE_FLG = TRUE
        AND {resolve_site_sql(args.site, 'ORD.SIT_SITE_ID')}
        AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
    """
    
else:
    # Post-Compra, Pagos, Cuenta: Órdenes globales (sin filtro site)
    query_drivers_total = f"""
    SELECT
        SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{args.p1_start}' AND '{args.p1_end}' THEN 1 ELSE 0 END) as DRV_P1,
        SUM(CASE WHEN ORD.ORD_CLOSED_DT BETWEEN '{args.p2_start}' AND '{args.p2_end}' THEN 1 ELSE 0 END) as DRV_P2
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
    WHERE ORD.ORD_CLOSED_DT BETWEEN '{args.p1_start}' AND '{args.p2_end}'
        AND ORD.ORD_CLOSED_DT IS NOT NULL
        AND ORD.ORD_GMV_FLG = TRUE
        AND ORD.ORD_MARKETPLACE_FLG = TRUE
        AND ORD.SIT_SITE_ID NOT IN ('MLV')
        AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
    """

df_drv_total = client.query(query_drivers_total).to_dataframe()
drv_p1_total = int(df_drv_total['DRV_P1'].iloc[0])
drv_p2_total = int(df_drv_total['DRV_P2'].iloc[0])

# Registrar query ejecutada
queries_ejecutadas.append({
    'nombre': f'Drivers ({driver_config["type"]})',
    'descripcion': driver_desc,
    'tabla': driver_config['table'],
    'output': f'P1: {drv_p1_total:,} | P2: {drv_p2_total:,}'
})

print(f"[OK] Drivers P1: {drv_p1_total:,}")
print(f"[OK] Drivers P2: {drv_p2_total:,}")
print()

# Calcular CR
cr_p1 = (inc_p1_total / drv_p1_total) * 100
cr_p2 = (inc_p2_total / drv_p2_total) * 100
var_cr = cr_p2 - cr_p1
var_cr_pct = (var_cr / cr_p1) * 100 if cr_p1 > 0 else 0
var_inc_pct = (var_inc_total / inc_p1_total) * 100 if inc_p1_total > 0 else 0

print(f"[RESULTADO] CR P1: {cr_p1:.4f} pp")
print(f"[RESULTADO] CR P2: {cr_p2:.4f} pp")
print(f"[RESULTADO] Variación CR: {var_cr:+.4f} pp ({var_cr_pct:+.1f}%)")
print()

# Guardar métricas consolidadas
metrics_consolidadas = {
    'inc_p1': inc_p1_total,
    'inc_p2': inc_p2_total,
    'var_inc': var_inc_total,
    'var_inc_pct': var_inc_pct,
    'drv_p1': drv_p1_total,
    'drv_p2': drv_p2_total,
    'cr_p1': cr_p1,
    'cr_p2': cr_p2,
    'var_cr': var_cr,
    'var_cr_pct': var_cr_pct
}

# ========================================
# PASO 2: GRÁFICO SEMANAL
# ========================================

print("="*80)
print("PASO 2: GRÁFICO SEMANAL")
print("="*80 + "\n")

print(f"[QUERY] Calculando CR semanal (últimas 25 semanas)...")

query_weekly = f"""
WITH BASE_CONTACTS AS (
    SELECT
        DATE_TRUNC(C.CONTACT_DATE_ID, WEEK(MONDAY)) as SEMANA,
        {commerce_filter} AS AGRUP_COMMERCE,
        1.0 AS CANT_CASES
    FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
    WHERE {resolve_site_sql(args.site, 'C.SIT_SITE_ID')}
        AND C.CONTACT_DATE_ID BETWEEN DATE_SUB('{args.p2_end}', INTERVAL 25 WEEK) AND '{args.p2_end}'
        AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
        AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
        AND C.SIT_SITE_ID NOT IN ('MLV')
        AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        AND C.PROCESS_ID NOT IN (1312)
        AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
        {process_filter}
),
WEEKLY_INCOMING AS (
    SELECT SEMANA, SUM(CANT_CASES) as CASOS
    FROM BASE_CONTACTS
    WHERE AGRUP_COMMERCE = '{args.commerce_group}'
    GROUP BY SEMANA
),
WEEKLY_DRIVERS AS (
    SELECT 
        DATE_TRUNC(ORD.ORD_CLOSED_DT, WEEK(MONDAY)) as SEMANA,
        COUNT(DISTINCT ORD.ORD_ORDER_ID) as ORDERS
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS` ORD
    WHERE ORD.ORD_CLOSED_DT BETWEEN DATE_SUB('{args.p2_end}', INTERVAL 25 WEEK) AND '{args.p2_end}'
        AND ORD.ORD_GMV_FLG = TRUE
        AND ORD.ORD_MARKETPLACE_FLG = TRUE
        {'AND ' + resolve_site_sql(args.site, 'ORD.SIT_SITE_ID') if driver_config['filter_by_site'] else 'AND ORD.SIT_SITE_ID NOT IN (\'MLV\')'}
        AND (UPPER(ORD.DOM_DOMAIN_ID) <> 'TIPS')
    GROUP BY SEMANA
)
SELECT 
    I.SEMANA,
    I.CASOS as INCOMING,
    D.ORDERS as DRIVER,
    (I.CASOS / D.ORDERS) * 100 as CR
FROM WEEKLY_INCOMING I
LEFT JOIN WEEKLY_DRIVERS D ON I.SEMANA = D.SEMANA
ORDER BY I.SEMANA
"""

df_weekly = client.query(query_weekly).to_dataframe()
df_weekly['SEMANA'] = pd.to_datetime(df_weekly['SEMANA'])
df_weekly['SEMANA_LABEL'] = df_weekly['SEMANA'].dt.strftime('%d-%b')

# Registrar query ejecutada
queries_ejecutadas.append({
    'nombre': 'Evolución Semanal',
    'descripcion': f'CR semanal para {args.commerce_group} desde 14+ semanas antes',
    'tabla': 'BT_CX_CONTACTS + BT_ORD_ORDERS',
    'output': f'{len(df_weekly)} semanas analizadas'
})

print(f"[OK] {len(df_weekly)} semanas calculadas")
print()

# ========================================
# PASO 3: CUADROS CUANTITATIVOS POR DIMENSIÓN
# ========================================

print("="*80)
print("PASO 3: CUADROS CUANTITATIVOS")
print("="*80 + "\n")

# Almacenar resultados de cada dimensión
cuadros_cuantitativos = {}

# Rastrear queries ejecutadas (para footer técnico)
queries_ejecutadas = []

# ========================================
# MODO PROCESO ÚNICO: Generar cuadro sintético
# ========================================
# Si se especifica --process-name con --aperturas NONE, generar cuadro de 1 fila
# para que el análisis de conversaciones pueda funcionar correctamente
modo_proceso_unico = (args.process_name is not None and 'NONE' in aperturas_list)

if modo_proceso_unico:
    print("[MODO] Proceso único detectado: análisis de 1 proceso sin drill-down")
    print(f"[INFO] Proceso: {args.process_name}")
    print(f"[INFO] Generando cuadro sintético con 1 elemento (100% contribución)")
    print()
    
    # Crear cuadro sintético con 1 fila
    df_proceso_unico = pd.DataFrame([{
        'DIMENSION_VAL': args.process_name,
        'INC_P1': inc_p1_total,
        'INC_P2': inc_p2_total,
        'VAR_INC': var_inc_total,
        'VAR_ABS': abs(var_inc_total),
        'CONTRIB_ABS': 100.0,
        'VAR_INC_PCT': (var_inc_total / inc_p1_total) * 100 if inc_p1_total > 0 else 0,
        'DRV_P1': drv_p1_total,
        'DRV_P2': drv_p2_total,
        'CR_P1': cr_p1,
        'CR_P2': cr_p2,
        'VAR_CR': var_cr
    }])
    
    # Fila TOTAL (para mantener estructura consistente)
    fila_total = {
        'DIMENSION_VAL': 'TOTAL',
        'INC_P1': inc_p1_total,
        'INC_P2': inc_p2_total,
        'VAR_INC': var_inc_total,
        'VAR_ABS': abs(var_inc_total),
        'CONTRIB_ABS': 100.0,
        'VAR_INC_PCT': (var_inc_total / inc_p1_total) * 100 if inc_p1_total > 0 else 0,
        'DRV_P1': drv_p1_total,
        'DRV_P2': drv_p2_total,
        'CR_P1': cr_p1,
        'CR_P2': cr_p2,
        'VAR_CR': var_cr
    }
    df_proceso_unico = pd.concat([df_proceso_unico, pd.DataFrame([fila_total])], ignore_index=True)
    
    # Agregar a cuadros cuantitativos con dimensión PROCESO
    cuadros_cuantitativos['PROCESO'] = df_proceso_unico
    
    # Guardar CSV del cuadro
    p1_month = args.p1_start[:7]  # 2025-11
    p2_month = args.p2_start[:7]  # 2025-12
    commerce_group_safe = args.commerce_group.lower().replace(' ', '_')
    output_path = Path(args.output_dir)
    output_path.mkdir(exist_ok=True)
    csv_path = output_path / f"cuadro_proceso_{args.site.lower()}_{commerce_group_safe}_{p1_month}_{p2_month}.csv"
    df_proceso_unico.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"[OK] Cuadro proceso único generado: {csv_path.name}")
    print(f"[OK] 1 elemento (100% contribución) + TOTAL")
    print()
    
    # Registrar query sintética
    queries_ejecutadas.append({
        'nombre': 'Cuadro Cuantitativo - PROCESO (sintético)',
        'descripcion': f'Cuadro sintético para proceso único: {args.process_name}',
        'tabla': 'Métricas consolidadas',
        'output': '1 elemento (modo proceso único)'
    })

for apertura in aperturas_list:
    # Si estamos en modo proceso único, saltar bucle (ya generamos cuadro sintético)
    if modo_proceso_unico:
        print(f"[SKIP] Saltando bucle de aperturas (modo proceso único activo)")
        break
    
    print(f"[DIMENSIÓN] Procesando: {apertura}")
    
    # Saltar dimensión PROCESO si hay filtro por proceso específico EXACTO (1 solo proceso)
    # Si process_name matchea múltiples procesos (ej: "Apelaciones"), NO saltar
    if apertura == 'PROCESO' and args.process_name:
        print(f"[INFO] Dimensión PROCESO con filtro process-name '{args.process_name}' - permitido (puede matchear múltiples procesos)")
        # No saltar: permitir breakdown por PROCESO incluso con process_name
    
    # Obtener campo de BigQuery
    campo_bq = FIELD_MAPPING.get(apertura)
    if not campo_bq:
        print(f"[WARNING] Dimensión '{apertura}' no tiene campo mapeado. Saltando...")
        continue
    
    # Query para obtener datos de la dimensión
    query_dimension = f"""
    WITH BASE_CONTACTS AS (
        SELECT
            {campo_bq} as DIMENSION_VAL,
            DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
            {commerce_filter} AS AGRUP_COMMERCE,
            1.0 AS CANT_CASES
        FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
        WHERE {resolve_site_sql(args.site, 'C.SIT_SITE_ID')}
            AND C.CONTACT_DATE_ID BETWEEN '{args.p1_start}' AND '{args.p2_end}'
            AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
            AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
            AND C.SIT_SITE_ID NOT IN ('MLV')
            AND C.QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
            AND C.PROCESS_ID NOT IN (1312)
            AND COALESCE(C.CI_REASON_ID, 0) NOT IN (2592, 6588, 10068, 2701, 10048)
            AND {campo_bq} IS NOT NULL
            {process_filter}
    ),
    BASE_FILTERED AS (
        SELECT * FROM BASE_CONTACTS
        WHERE AGRUP_COMMERCE = '{args.commerce_group}'
    ),
    AGGREGATED AS (
        SELECT
            DIMENSION_VAL,
            SUM(CASE WHEN PERIODO BETWEEN '{args.p1_start}' AND '{args.p1_end}' THEN CANT_CASES ELSE 0 END) as INC_P1,
            SUM(CASE WHEN PERIODO BETWEEN '{args.p2_start}' AND '{args.p2_end}' THEN CANT_CASES ELSE 0 END) as INC_P2
        FROM BASE_FILTERED
        GROUP BY DIMENSION_VAL
    )
    SELECT 
        DIMENSION_VAL,
        INC_P1,
        INC_P2,
        (INC_P2 - INC_P1) as VAR_INC,
        ABS(INC_P2 - INC_P1) as VAR_ABS
    FROM AGGREGATED
    WHERE INC_P1 > 0 OR INC_P2 > 0
    ORDER BY VAR_ABS DESC
    """
    
    df_dimension = client.query(query_dimension).to_dataframe()
    
    # Registrar query ejecutada
    queries_ejecutadas.append({
        'nombre': f'Cuadro Cuantitativo - {apertura}',
        'descripcion': f'Desglose de incoming por {apertura} para ambos períodos',
        'tabla': 'BT_CX_CONTACTS',
        'output': f'{len(df_dimension)} elementos encontrados'
    })
    
    if len(df_dimension) == 0:
        print(f"[WARNING] No hay datos para {apertura}")
        continue
    
    # Aplicar regla 80%
    df_dimension['CONTRIB_ABS'] = df_dimension['VAR_ABS'] / df_dimension['VAR_ABS'].sum() * 100
    df_dimension['CONTRIB_CUMSUM'] = df_dimension['CONTRIB_ABS'].cumsum()
    
    # Calcular variación porcentual (VAR_INC_PCT) - Requerido por análisis comparativo
    df_dimension['VAR_INC_PCT'] = (df_dimension['VAR_INC'] / df_dimension['INC_P1']) * 100
    
    df_80 = df_dimension[df_dimension['CONTRIB_CUMSUM'] <= 80].copy()
    df_otros = df_dimension[df_dimension['CONTRIB_CUMSUM'] > 80].copy()
    
    # Si regla 80% no cubre suficiente, tomar al menos top 3
    if len(df_80) < 3 and len(df_dimension) >= 3:
        df_80 = df_dimension.head(3).copy()
        df_otros = df_dimension.iloc[3:].copy()
    
    # Agregar drivers (globales para todos los elementos)
    df_80['DRV_P1'] = drv_p1_total
    df_80['DRV_P2'] = drv_p2_total
    df_80['CR_P1'] = (df_80['INC_P1'] / df_80['DRV_P1']) * 100
    df_80['CR_P2'] = (df_80['INC_P2'] / df_80['DRV_P2']) * 100
    df_80['VAR_CR'] = df_80['CR_P2'] - df_80['CR_P1']
    
    # Fila "Otros" si aplica
    if len(df_otros) > 0:
        inc_p1_otros = df_otros['INC_P1'].sum()
        inc_p2_otros = df_otros['INC_P2'].sum()
        var_inc_otros = df_otros['VAR_INC'].sum()
        
        fila_otros = {
            'DIMENSION_VAL': f"Otros ({len(df_otros)} agrupados)",
            'INC_P1': inc_p1_otros,
            'INC_P2': inc_p2_otros,
            'VAR_INC': var_inc_otros,
            'VAR_ABS': df_otros['VAR_ABS'].sum(),
            'CONTRIB_ABS': df_otros['CONTRIB_ABS'].sum(),
            'VAR_INC_PCT': (var_inc_otros / inc_p1_otros) * 100 if inc_p1_otros > 0 else 0,
            'DRV_P1': drv_p1_total,
            'DRV_P2': drv_p2_total,
            'CR_P1': (inc_p1_otros / drv_p1_total) * 100,
            'CR_P2': (inc_p2_otros / drv_p2_total) * 100,
            'VAR_CR': ((inc_p2_otros / drv_p2_total) - (inc_p1_otros / drv_p1_total)) * 100
        }
        df_80 = pd.concat([df_80, pd.DataFrame([fila_otros])], ignore_index=True)
    
    # Fila TOTAL
    fila_total = {
        'DIMENSION_VAL': 'TOTAL',
        'INC_P1': inc_p1_total,
        'INC_P2': inc_p2_total,
        'VAR_INC': var_inc_total,
        'VAR_ABS': abs(var_inc_total),
        'CONTRIB_ABS': 100.0,
        'VAR_INC_PCT': (var_inc_total / inc_p1_total) * 100 if inc_p1_total > 0 else 0,
        'DRV_P1': drv_p1_total,
        'DRV_P2': drv_p2_total,
        'CR_P1': cr_p1,
        'CR_P2': cr_p2,
        'VAR_CR': var_cr
    }
    df_80 = pd.concat([df_80, pd.DataFrame([fila_total])], ignore_index=True)
    
    cuadros_cuantitativos[apertura] = df_80
    
    print(f"[OK] {apertura}: {len(df_80)-2} elementos + Otros + Total")

print()

# ========================================
# PASO 4: ANÁLISIS DE CONVERSACIONES
# ========================================

conversaciones_por_proceso = {}

if not args.skip_conversations:
    print("="*80)
    print("PASO 4: ANÁLISIS DE CONVERSACIONES")
    print("="*80 + "\n")
    
    # Obtener dimensión para muestreo
    dimension_muestreo = args.muestreo_dimension.upper()
    
    # En modo proceso único, forzar dimensión PROCESO si existe en cuadros
    if modo_proceso_unico and 'PROCESO' in cuadros_cuantitativos:
        dimension_muestreo = 'PROCESO'
        print(f"[MODO] Usando dimensión PROCESO (cuadro sintético generado)")
    
    if dimension_muestreo not in cuadros_cuantitativos:
        print(f"[WARNING] Dimensión '{dimension_muestreo}' no existe en cuadros cuantitativos")
        print(f"[INFO] Saltando análisis de conversaciones")
    else:
        # Identificar elementos priorizados (regla 80%)
        df_muestreo = cuadros_cuantitativos[dimension_muestreo]
        df_muestreo = df_muestreo[~df_muestreo['DIMENSION_VAL'].isin(['TOTAL'])].copy()
        df_muestreo = df_muestreo[~df_muestreo['DIMENSION_VAL'].str.contains('Otros', na=False)].copy()
        
        elementos_priorizados = df_muestreo['DIMENSION_VAL'].tolist()
        
        print(f"[INFO] Dimensión de muestreo: {dimension_muestreo}")
        print(f"[INFO] Elementos priorizados (regla 80%): {len(elementos_priorizados)}")
        print(f"[INFO] Elementos: {', '.join(elementos_priorizados[:3])}...")
        print()
        
        # Configurar análisis de Claude CON validación de coherencia (v6.3.1)
        configurar_analisis_claude(args.site, args.commerce_group, args.muestreo_dimension, args.p1_start, args.p2_start, elementos_priorizados, usar_analisis_separado=True)
        
        # Obtener campo de BigQuery para la dimensión de muestreo
        campo_muestreo = FIELD_MAPPING.get(dimension_muestreo)
        
        if not campo_muestreo:
            print(f"[ERROR] No hay campo mapeado para {dimension_muestreo}")
        else:
            # Preparar lista IN para SQL
            elementos_in = ','.join([f"'{str(e).replace(chr(39), chr(39)+chr(39))}'" for e in elementos_priorizados])
            
            # ========================================
            # CÁLCULO DINÁMICO DE MUESTREO v6.4.9 (Por CONTRIB_ABS)
            # ========================================
            # Distribución inteligente por impacto en variación de CR
            num_elementos_priorizados = len(elementos_priorizados)
            
            print(f"[MUESTREO] Calculando distribución por impacto en variación de CR...")
            distribucion_muestra = calcular_distribucion_por_impacto(
                df_elementos=df_muestreo,
                max_total=MAX_TOTAL_CONVERSATIONS,
                min_por_elemento_periodo=UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO
            )
            
            # Evitar división por cero cuando no hay elementos priorizados (ej. volumen muy bajo)
            if num_elementos_priorizados == 0 or not distribucion_muestra:
                print(f"[INFO] Sin elementos priorizados o distribución vacía: se omite muestreo de conversaciones.")
                df_conversaciones = pd.DataFrame()
                queries_ejecutadas.append({
                    'nombre': 'Muestreo de Conversaciones',
                    'descripcion': 'Sin elementos priorizados (volumen insuficiente para drill-down)',
                    'tabla': 'BT_CX_CONTACTS + BT_CX_STUDIO_SAMPLE + DM_CX_POST_PURCHASE',
                    'output': '0 conversaciones'
                })
                print(f"[OK] 0 conversaciones obtenidas")
                print(f"[INFO] Continuando sin conversaciones (solo métricas cuantitativas)...")
                for elemento in elementos_priorizados:
                    conversaciones_por_proceso[elemento] = {
                        'status': 'sin_data',
                        'casos_p1': 0,
                        'casos_p2': 0
                    }
                print()
            else:
                # Calcular totales para logging
                total_esperado = sum(d['total'] for d in distribucion_muestra.values())
                casos_promedio_por_periodo = total_esperado / (num_elementos_priorizados * 2)
                
                # Para la query, usar el máximo de casos por elemento-período como límite superior
                max_casos_elemento_periodo = max(max(d['p1'], d['p2']) for d in distribucion_muestra.values())
                casos_pico = int(max_casos_elemento_periodo * 0.7)
                casos_normal = max_casos_elemento_periodo - casos_pico
                
                print(f"[INFO] Distribución por impacto calculada:")
                print(f"[INFO] • Elementos priorizados: {num_elementos_priorizados}")
                print(f"[INFO] • Total esperado: {total_esperado} conversaciones (máx {MAX_TOTAL_CONVERSATIONS})")
                print(f"[INFO] • Mínimo por elemento-período: {UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO}")
                print(f"[INFO] • Promedio por elemento-período: {casos_promedio_por_periodo:.1f}")
                
                # Mostrar top 3 elementos por muestra asignada
                top_elementos = sorted(distribucion_muestra.items(), key=lambda x: x[1]['total'], reverse=True)[:3]
                print(f"[INFO] • Top 3 elementos por muestra:")
                for elemento, dist in top_elementos:
                    elemento_corto = elemento[:50] + '...' if len(elemento) > 50 else elemento
                    print(f"    - {elemento_corto}: {dist['total']} casos (P1:{dist['p1']} + P2:{dist['p2']}) | Impacto: {dist['contribucion']:.1f}")
                
                print(f"[QUERY] Muestreando conversaciones con ponderación por picos (70/30)...")
                print(f"[INFO] Esto puede tardar 3-6 minutos...")
                
                query_conversaciones = f"""
            WITH INCOMING_DATA AS (
                SELECT 
                    C.CLA_CLAIM_ID,
                    {campo_muestreo} as DIMENSION_VAL,
                    C.CONTACT_DATE_ID,
                    DATE_TRUNC(C.CONTACT_DATE_ID, MONTH) AS PERIODO,
                    C.CAS_CASE_ID,
                    {commerce_filter} AS AGRUP_COMMERCE
                FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS` C
                WHERE {resolve_site_sql(args.site, 'C.SIT_SITE_ID')}
                    AND C.CONTACT_DATE_ID BETWEEN '{args.p1_start}' AND '{args.p2_end}'
                    AND C.PROCESS_BU_CR_REPORTING IN ('ME','ML')
                    AND COALESCE(C.FLAG_EXCLUDE_NUMERATOR_CR, 0) = 0
                    AND {campo_muestreo} IN ({elementos_in})
                    AND C.CAS_CASE_ID IS NOT NULL
                    {process_filter}
            ),
            -- Calcular volumen diario para detectar picos
            DAILY_VOLUME AS (
                SELECT 
                    DIMENSION_VAL,
                    PERIODO,
                    CONTACT_DATE_ID,
                    COUNT(*) as CASOS_DIA
                FROM INCOMING_DATA
                WHERE AGRUP_COMMERCE = '{args.commerce_group}'
                GROUP BY DIMENSION_VAL, PERIODO, CONTACT_DATE_ID
            ),
            -- Calcular estadísticas temporales (promedio y desviación estándar)
            TEMPORAL_STATS AS (
                SELECT 
                    DIMENSION_VAL,
                    PERIODO,
                    AVG(CASOS_DIA) as PROMEDIO,
                    STDDEV(CASOS_DIA) as STD
                FROM DAILY_VOLUME
                GROUP BY DIMENSION_VAL, PERIODO
            ),
            -- Clasificar días en PICO o NORMAL (pico = promedio + 1.5σ)
            PEAK_CLASSIFICATION AS (
                SELECT 
                    DV.DIMENSION_VAL,
                    DV.PERIODO,
                    DV.CONTACT_DATE_ID,
                    CASE 
                        WHEN DV.CASOS_DIA > (TS.PROMEDIO + 1.5 * TS.STD) THEN 'PICO'
                        ELSE 'NORMAL'
                    END as TIPO_DIA
                FROM DAILY_VOLUME DV
                JOIN TEMPORAL_STATS TS 
                    ON DV.DIMENSION_VAL = TS.DIMENSION_VAL 
                    AND DV.PERIODO = TS.PERIODO
            ),
            -- Enriquecer datos con clasificación de día
            INCOMING_ENRICHED AS (
                SELECT 
                    I.*,
                    COALESCE(PC.TIPO_DIA, 'NORMAL') as TIPO_DIA,
                    ROW_NUMBER() OVER (
                        PARTITION BY I.DIMENSION_VAL, I.PERIODO, COALESCE(PC.TIPO_DIA, 'NORMAL')
                        ORDER BY RAND()
                    ) as rn_tipo
                FROM INCOMING_DATA I
                LEFT JOIN PEAK_CLASSIFICATION PC
                    ON I.DIMENSION_VAL = PC.DIMENSION_VAL 
                    AND I.PERIODO = PC.PERIODO
                    AND I.CONTACT_DATE_ID = PC.CONTACT_DATE_ID
                WHERE I.AGRUP_COMMERCE = '{args.commerce_group}'
            ),
            -- Muestreo ponderado: 70% picos + 30% normales (distribución dinámica)
            INCOMING_FILTERED AS (
                SELECT 
                    CLA_CLAIM_ID,
                    DIMENSION_VAL,
                    CONTACT_DATE_ID,
                    PERIODO,
                    CAS_CASE_ID,
                    TIPO_DIA
                FROM INCOMING_ENRICHED
                WHERE (TIPO_DIA = 'PICO' AND rn_tipo <= {casos_pico})
                   OR (TIPO_DIA = 'NORMAL' AND rn_tipo <= {casos_normal})
            ),
            STUDIO_DATA AS (
                SELECT 
                    ST.CAS_CASE_ID,
                    TRIM(REGEXP_REPLACE(
                        CONCAT(
                            COALESCE(JSON_VALUE(ST.SUMMARY_CX_STUDIO, '$.problem'), ''), 
                            ' ', 
                            COALESCE(JSON_VALUE(ST.SUMMARY_CX_STUDIO, '$.solution'), '')
                        ), 
                        r'\\s+', ' '
                    )) AS CONVERSATION_SUMMARY
                FROM `meli-bi-data.WHOWNER.BT_CX_STUDIO_SAMPLE` ST
                WHERE ST.ARRIVAL_DATE BETWEEN DATE_SUB('{args.p1_start}', INTERVAL 1 MONTH) AND DATE_ADD('{args.p2_end}', INTERVAL 1 MONTH)
            ),
            ORDERS_DATA AS (
                SELECT
                    PP.CLA_CLAIM_ID,
                    PP.ORD_CLOSED_DT as ORD_CLOSED_DATE
                FROM `meli-bi-data.WHOWNER.DM_CX_POST_PURCHASE` PP
                WHERE PP.ORD_CLOSED_DT BETWEEN DATE_SUB('{args.p1_start}', INTERVAL 1 MONTH) AND '{args.p2_end}'
            )
            SELECT 
                I.DIMENSION_VAL,
                I.PERIODO,
                I.CONTACT_DATE_ID,
                I.CAS_CASE_ID,
                I.TIPO_DIA,
                S.CONVERSATION_SUMMARY,
                O.ORD_CLOSED_DATE
            FROM INCOMING_FILTERED I
            LEFT JOIN STUDIO_DATA S ON I.CAS_CASE_ID = S.CAS_CASE_ID
            LEFT JOIN ORDERS_DATA O ON I.CLA_CLAIM_ID = O.CLA_CLAIM_ID
            WHERE S.CONVERSATION_SUMMARY IS NOT NULL 
                AND LENGTH(TRIM(S.CONVERSATION_SUMMARY)) > 10
            ORDER BY I.DIMENSION_VAL, I.PERIODO, I.TIPO_DIA DESC
            """
                
                # Configurar timeout y límites de BigQuery
                job_config = QueryJobConfig(
                    use_query_cache=True,
                    maximum_bytes_billed=5_000_000_000_000  # Límite 5TB - Cubre todos los casos incluyendo Shipping de alto volumen
                )
                
                try:
                    print(f"[BQ] Ejecutando query con timeout de 8 minutos...")
                    query_job = client.query(query_conversaciones, job_config=job_config)
                    df_conversaciones = query_job.result(timeout=480).to_dataframe()  # 8 min timeout
                    
                    bytes_processed = query_job.total_bytes_processed / (1024**3)  # GB
                    print(f"[BQ] Bytes procesados: {bytes_processed:.2f} GB")
                    
                except Exception as e:
                    print(f"[ERROR] Query de muestreo falló: {e}")
                    print(f"[INFO] Continuando sin análisis de conversaciones...")
                    df_conversaciones = pd.DataFrame()
                
                # Solo convertir tipos si hay datos
                if len(df_conversaciones) > 0:
                    df_conversaciones['PERIODO'] = pd.to_datetime(df_conversaciones['PERIODO'])
                    df_conversaciones['CONTACT_DATE_ID'] = pd.to_datetime(df_conversaciones['CONTACT_DATE_ID'])
                    
                    # ========================================
                    # FILTRADO POR DISTRIBUCIÓN ESPECÍFICA v6.4.9
                    # ========================================
                    print(f"[FILTRADO] Aplicando distribución por impacto...")
                    
                    # Aplicar límite específico por elemento-período
                    df_filtered_list = []
                    for elemento, dist in distribucion_muestra.items():
                        df_elem = df_conversaciones[df_conversaciones['DIMENSION_VAL'] == elemento].copy()
                        
                        if len(df_elem) > 0:
                            # Separar por período
                            df_elem_p1 = df_elem[df_elem['PERIODO'].dt.strftime('%Y-%m') == pd.to_datetime(args.p1_start).strftime('%Y-%m')]
                            df_elem_p2 = df_elem[df_elem['PERIODO'].dt.strftime('%Y-%m') == pd.to_datetime(args.p2_start).strftime('%Y-%m')]
                            
                            # Aplicar límite específico por período
                            if len(df_elem_p1) > dist['p1']:
                                df_elem_p1 = df_elem_p1.sample(n=dist['p1'], random_state=42)
                            if len(df_elem_p2) > dist['p2']:
                                df_elem_p2 = df_elem_p2.sample(n=dist['p2'], random_state=42)
                            
                            df_filtered_list.append(df_elem_p1)
                            df_filtered_list.append(df_elem_p2)
                    
                    # Reconstruir DataFrame filtrado
                    if df_filtered_list:
                        df_conversaciones = pd.concat(df_filtered_list, ignore_index=True)
                        print(f"[OK] Filtrado completado: {len(df_conversaciones)} conversaciones finales")
                    else:
                        df_conversaciones = pd.DataFrame()
                        print(f"[WARNING] Sin conversaciones después del filtrado")
                
                # Registrar query ejecutada
                if len(df_conversaciones) > 0:
                    picos = len(df_conversaciones[df_conversaciones.get('TIPO_DIA', 'NORMAL') == 'PICO'])
                    normales = len(df_conversaciones[df_conversaciones.get('TIPO_DIA', 'NORMAL') == 'NORMAL'])
                    
                    queries_ejecutadas.append({
                        'nombre': 'Muestreo de Conversaciones (v6.4.9 - Por CONTRIB_ABS)',
                        'descripcion': f'Muestreo proporcional a CONTRIB_ABS (contribución % a variación de CR). Distribución dinámica: {total_esperado} conversaciones (mín {UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO}/elemento-período, máx {MAX_TOTAL_CONVERSATIONS} total)',
                        'tabla': 'BT_CX_CONTACTS + BT_CX_STUDIO_SAMPLE + DM_CX_POST_PURCHASE',
                        'output': f'{len(df_conversaciones)} conversaciones ({picos} picos + {normales} normales) | Estrategia: 70/30 pico/normal por elemento'
                    })
                else:
                    queries_ejecutadas.append({
                        'nombre': 'Muestreo de Conversaciones',
                        'descripcion': f'Muestreo intentado pero falló',
                        'tabla': 'BT_CX_CONTACTS + BT_CX_STUDIO_SAMPLE + DM_CX_POST_PURCHASE',
                        'output': '0 conversaciones'
                    })
                
                if 'ORD_CLOSED_DATE' in df_conversaciones.columns:
                    df_conversaciones['ORD_CLOSED_DATE'] = pd.to_datetime(df_conversaciones['ORD_CLOSED_DATE'])
                
                print(f"[OK] {len(df_conversaciones)} conversaciones obtenidas")
                if len(df_conversaciones) == 0:
                    print(f"[DEBUG] Query devolvió 0 resultados. Verificar:")
                    print(f"[DEBUG] - Elementos priorizados: {len(elementos_priorizados)}")
                    print(f"[DEBUG] - Campo muestreo: {campo_muestreo}")
                    print(f"[DEBUG] - Commerce group: {args.commerce_group}")
                    print(f"[INFO] Continuando sin conversaciones (solo métricas cuantitativas)...")
                    # Marcar todos los elementos como sin data
                    for elemento in elementos_priorizados:
                        conversaciones_por_proceso[elemento] = {
                            'status': 'sin_data',
                            'casos_p1': 0,
                            'casos_p2': 0
                        }
                print()
            
            # Agrupar por elemento y período (solo si hay datos)
            if len(df_conversaciones) > 0 and 'DIMENSION_VAL' in df_conversaciones.columns:
                for elemento in elementos_priorizados:
                    df_elem = df_conversaciones[df_conversaciones['DIMENSION_VAL'] == elemento]
                    
                    if len(df_elem) == 0:
                        print(f"[WARNING] No hay conversaciones para '{elemento}'")
                        conversaciones_por_proceso[elemento] = {
                            'status': 'sin_data',
                            'casos_p1': 0,
                            'casos_p2': 0
                        }
                        continue
                    
                    df_p1 = df_elem[df_elem['PERIODO'].between(args.p1_start, args.p1_end)]
                    df_p2 = df_elem[df_elem['PERIODO'].between(args.p2_start, args.p2_end)]
                    
                    conversaciones_por_proceso[elemento] = {
                        'status': 'con_data',
                        'casos_p1': len(df_p1),
                        'casos_p2': len(df_p2),
                        'df_p1': df_p1,
                        'df_p2': df_p2,
                        'df_all': df_elem
                    }
                    
                    print(f"[OK] '{elemento}': {len(df_p1)} conversaciones P1, {len(df_p2)} conversaciones P2")
            
            print()
            
            # Ejecutar análisis usando Claude (Cursor AI) o fallback
            print(f"[ANÁLISIS] Cargando análisis para {len(conversaciones_por_proceso)} procesos...")
            print()
            
            for elemento, data in conversaciones_por_proceso.items():
                if data['status'] != 'con_data':
                    continue
                
                # Ejecutar análisis (usa Claude si está disponible, sino fallback)
                analisis = analyze_conversations_with_llm(
                    df_conversations=data['df_all'],
                    proceso=elemento,
                    commerce_group=args.commerce_group
                )
                
                # Guardar resultado
                conversaciones_por_proceso[elemento]['analisis_llm'] = analisis
                
                # Mostrar resultado
                if USE_CLAUDE_ANALYSIS and elemento in ANALISIS_PREEXISTENTES:
                    cobertura = analisis['cobertura']['covered_pct']
                    num_causas = len([c for c in analisis['causas'] if '⚠️' not in c['descripcion']])
                    print(f"[OK] '{elemento}': {num_causas} causas raíz (cobertura: {cobertura:.0f}%)")
                else:
                    print(f"[SKIP] '{elemento}': CSV exportado para análisis manual")
            
            print()
            if USE_CLAUDE_ANALYSIS:
                print(f"[OK] Análisis de Claude cargados: {len([p for p in conversaciones_por_proceso if conversaciones_por_proceso[p].get('analisis_llm', {}).get('cobertura', {}).get('covered_pct', 0) > 0])} procesos")
            else:
                print(f"[INFO] Los CSVs con conversaciones están disponibles para análisis manual")
                print(f"[INFO] Ejecutar: py analizar_conversaciones_claude.py")

else:
    print("[INFO] Análisis de conversaciones saltado (--skip-conversations)")
    print()

# ========================================
# PASO 5: GENERAR HTML
# ========================================

print("="*80)
print("PASO 5: GENERACIÓN HTML")
print("="*80 + "\n")

# Guardar CSVs intermedios
output_dir = Path(args.output_dir)
output_dir.mkdir(exist_ok=True)

print("[SAVE] Guardando CSVs intermedios...")

for dimension, df in cuadros_cuantitativos.items():
    csv_path = output_dir / f"cuadro_{dimension.lower()}_{args.site.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"  [OK] {csv_path.name}")

# Guardar conversaciones si existen - SEPARADAS POR PERÍODO (v6.3.8)
if len(conversaciones_por_proceso) > 0:
    for elemento, data in conversaciones_por_proceso.items():
        if data['status'] == 'con_data':
            elem_safe = elemento.replace('/', '_').replace(' ', '_')
            
            # Exportar CSV separado para P1
            csv_path_p1 = output_dir / f"conversaciones_{elem_safe}_{args.site.lower()}_p1_{p1_start_dt.strftime('%Y%m')}.csv"
            data['df_p1'].to_csv(csv_path_p1, index=False)
            print(f"  [OK] {csv_path_p1.name} ({len(data['df_p1'])} conversaciones)")
            
            # Exportar CSV separado para P2
            csv_path_p2 = output_dir / f"conversaciones_{elem_safe}_{args.site.lower()}_p2_{p2_start_dt.strftime('%Y%m')}.csv"
            data['df_p2'].to_csv(csv_path_p2, index=False)
            print(f"  [OK] {csv_path_p2.name} ({len(data['df_p2'])} conversaciones)")

# Guardar weekly
csv_weekly = output_dir / f"weekly_{args.site.lower()}_{args.commerce_group.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"
df_weekly.to_csv(csv_weekly, index=False)
print(f"  [OK] {csv_weekly.name}")

print()

# ========================================
# ESPERA AUTOMÁTICA PARA ANÁLISIS (v6.3.6)
# ========================================

# Si no existe análisis previo Y hay conversaciones exportadas → esperar automáticamente
if not USE_CLAUDE_ANALYSIS and len(conversaciones_por_proceso) > 0 and not args.export_only:
    # Obtener elementos priorizados
    elementos_priorizados = list(conversaciones_por_proceso.keys())
    
    # Mostrar lista de CSVs exportados
    print("[INFO] CSVs de conversaciones exportados (separados por período):")
    for elemento in elementos_priorizados:
        elem_safe = elemento.replace('/', '_').replace(' ', '_')
        csv_p1_name = f"conversaciones_{elem_safe}_{args.site.lower()}_p1_{p1_start_dt.strftime('%Y%m')}.csv"
        csv_p2_name = f"conversaciones_{elem_safe}_{args.site.lower()}_p2_{p2_start_dt.strftime('%Y%m')}.csv"
        print(f"  ✅ {csv_p1_name}")
        print(f"  ✅ {csv_p2_name}")
    print()
    
    # Esperar automáticamente hasta que se generen los JSONs (análisis separado por período)
    json_detectado = esperar_analisis_conversaciones(
        json_path=ANALISIS_CLAUDE_PATH,
        elementos_priorizados=elementos_priorizados,
        timeout_seconds=600,  # 10 minutos
        check_interval=5,     # Verificar cada 5 segundos
        site=args.site,
        commerce_group=args.commerce_group,
        p1_label=p1_start_dt.strftime('%b %Y'),
        p2_label=p2_start_dt.strftime('%b %Y'),
        analisis_separado=True  # v6.3.8: Análisis separado por período
    )
    
    # Si se detectó el JSON → recargar análisis
    if json_detectado:
        # Reconfigurar con los nuevos JSONs
        configurar_analisis_claude(
            args.site, 
            args.commerce_group, 
            args.muestreo_dimension, 
            args.p1_start, 
            args.p2_start,
            elementos_priorizados,
            usar_analisis_separado=True
        )
        
        # Re-ejecutar análisis para todos los elementos con el JSON cargado
        print("[RELOADING] Recargando análisis con JSON detectado...")
        for elemento, data in conversaciones_por_proceso.items():
            if data['status'] == 'con_data':
                analisis = analyze_conversations_with_llm(
                    df_conversations=data['df_all'],
                    proceso=elemento,
                    commerce_group=args.commerce_group
                )
                conversaciones_por_proceso[elemento]['analisis_llm'] = analisis
                
                if USE_CLAUDE_ANALYSIS and elemento in ANALISIS_PREEXISTENTES:
                    cobertura = analisis['cobertura']['covered_pct']
                    num_causas = len([c for c in analisis['causas'] if '⚠️' not in c['descripcion']])
                    print(f"  [OK] '{elemento}': {num_causas} causas raíz (cobertura: {cobertura:.0f}%)")
        
        print(f"\n[SUCCESS] Análisis completado exitosamente para {len(elementos_priorizados)} elementos\n")

# ========================================
# CHECKPOINT: EXPORT-ONLY MODE
# ========================================

if args.export_only:
    print()
    print("="*80)
    print("[EXPORT-ONLY MODE] CSVs de conversaciones exportados exitosamente")
    print("="*80)
    print()
    print(f"[ARCHIVOS] {len(conversaciones_por_proceso) * 2} CSVs de conversaciones generados (separados por período):")
    for elemento in conversaciones_por_proceso.keys():
        elem_safe = elemento.replace('/', '_').replace(' ', '_')
        csv_p1_name = f"conversaciones_{elem_safe}_{args.site.lower()}_p1_{p1_start_dt.strftime('%Y%m')}.csv"
        csv_p2_name = f"conversaciones_{elem_safe}_{args.site.lower()}_p2_{p2_start_dt.strftime('%Y%m')}.csv"
        print(f"  OK output/{csv_p1_name}")
        print(f"  OK output/{csv_p2_name}")
    print()
    print("[NEXT STEP] El asistente de Cursor AI analizará las conversaciones automáticamente")
    print("[ACCIÓN] No se requiere intervención manual")
    print("[INFO] Re-ejecutar script sin --export-only para generar HTML con análisis")
    print()
    sys.exit(0)  # Salir limpiamente sin generar HTML

# Generar HTML
print("[HTML] Generando reporte HTML...")

# Preparar datos para template
p1_label = f"{p1_start_dt.strftime('%b %Y')}"
p2_label = f"{p2_start_dt.strftime('%b %Y')}"

# Determinar color de variación
var_cr_class = 'negative' if var_cr > 0 else 'positive'
var_inc_class = 'negative' if var_inc_total > 0 else 'positive'

# ========================================
# GENERAR RESUMEN EJECUTIVO (3 BULLETS ESTRUCTURADOS - v6.3)
# ========================================

# BULLET 1: Variación de CR + Métricas Consolidadas
direccion_cr = "empeoró" if var_cr > 0 else "mejoró"
signo_cr = "+" if var_cr > 0 else ""
bullet_1 = f"CR {direccion_cr} {signo_cr}{var_cr:.4f} pp ({signo_cr}{var_cr_pct:.1f}%) | {p1_start_dt.strftime('%b')}: {cr_p1:.4f} pp → {p2_start_dt.strftime('%b')}: {cr_p2:.4f} pp | {signo_cr}{var_inc_total:,} casos de {args.commerce_group} en {args.site}"

# BULLET 2: Principal elemento + contribución + causa raíz (si existe análisis de conversaciones)
# Usar dimensión de muestreo cuando hay análisis, para que los elementos coincidan con conversaciones_por_proceso
bullet_2 = ""
if len(cuadros_cuantitativos) > 0:
    if conversaciones_por_proceso and args.muestreo_dimension and args.muestreo_dimension.upper() in cuadros_cuantitativos:
        apertura_bullets = args.muestreo_dimension.upper()
    else:
        apertura_bullets = list(cuadros_cuantitativos.keys())[0]
    df_primera = cuadros_cuantitativos[apertura_bullets]
    
    df_sin_total = df_primera[
        (~df_primera['DIMENSION_VAL'].str.contains('TOTAL', na=False)) &
        (~df_primera['DIMENSION_VAL'].str.contains('Otros', na=False))
    ].copy()
    
    if len(df_sin_total) > 0:
        df_sin_total = df_sin_total.sort_values('CONTRIB_ABS', ascending=False)
        top_elemento = df_sin_total.iloc[0]
        top_nombre = top_elemento['DIMENSION_VAL']
        top_var_inc = int(top_elemento['VAR_INC'])
        top_contrib = top_elemento['CONTRIB_ABS']
        
        # Buscar si existe análisis de conversaciones para este elemento
        causa_raiz_texto = ""
        if top_nombre in conversaciones_por_proceso:
            analisis_llm = conversaciones_por_proceso[top_nombre].get('analisis_llm', {})
            # Aceptar tanto 'causas_raiz' como 'causas' (retrocompatibilidad)
            causas_list = analisis_llm.get('causas_raiz') or analisis_llm.get('causas')
            if causas_list and len(causas_list) > 0:
                causa_top = causas_list[0]
                causa_desc = causa_top.get('descripcion', '')
                # Extraer primera oración como descripción corta
                causa_desc_corta = causa_desc.split('.')[0] if causa_desc else ''
                causa_raiz_texto = f" | Causa raíz principal: {causa_top.get('causa', 'N/A')} ({causa_top.get('porcentaje', 0)}% de casos) - {causa_desc_corta}"
        
        bullet_2 = f"{top_nombre} lidera la variación ({top_contrib:.0f}% de contribución, {signo_cr}{top_var_inc:,} casos){causa_raiz_texto}"

# BULLET 3: Segundo elemento o hallazgo adicional relevante
# Misma dimensión que bullet_2 para que causas raíz coincidan con conversaciones_por_proceso
bullet_3 = ""
if len(cuadros_cuantitativos) > 0:
    if conversaciones_por_proceso and args.muestreo_dimension and args.muestreo_dimension.upper() in cuadros_cuantitativos:
        apertura_bullets = args.muestreo_dimension.upper()
    else:
        apertura_bullets = list(cuadros_cuantitativos.keys())[0]
    df_primera = cuadros_cuantitativos[apertura_bullets]
    
    df_sin_total = df_primera[
        (~df_primera['DIMENSION_VAL'].str.contains('TOTAL', na=False)) &
        (~df_primera['DIMENSION_VAL'].str.contains('Otros', na=False))
    ].copy()
    
    if len(df_sin_total) > 1:
        df_sin_total = df_sin_total.sort_values('CONTRIB_ABS', ascending=False)
        segundo_elemento = df_sin_total.iloc[1]
        segundo_nombre = segundo_elemento['DIMENSION_VAL']
        segundo_var_inc = int(segundo_elemento['VAR_INC'])
        segundo_var_inc_pct = ((segundo_elemento['INC_P2'] - segundo_elemento['INC_P1']) / segundo_elemento['INC_P1'] * 100) if segundo_elemento['INC_P1'] > 0 else 0
        
        # Buscar si existe análisis de conversaciones para este segundo elemento
        causa_raiz_texto_2 = ""
        if segundo_nombre in conversaciones_por_proceso:
            analisis_llm_2 = conversaciones_por_proceso[segundo_nombre].get('analisis_llm', {})
            # Aceptar tanto 'causas_raiz' como 'causas' (retrocompatibilidad)
            causas_list_2 = analisis_llm_2.get('causas_raiz') or analisis_llm_2.get('causas')
            if causas_list_2 and len(causas_list_2) > 0:
                # Tomar la causa principal (mayor porcentaje)
                causa_critica = causas_list_2[0]
                
                causa_desc_2 = causa_critica.get('descripcion', '')
                causa_desc_corta_2 = causa_desc_2.split('.')[0] if causa_desc_2 else ''
                
                causa_raiz_texto_2 = f" | Causa crítica: {causa_critica.get('causa', 'N/A')} ({causa_critica.get('porcentaje', 0)}% casos) - {causa_desc_corta_2}"
        
        # Determinar si es crecimiento o reducción según el signo
        termino_variacion = "crecimiento" if segundo_var_inc_pct >= 0 else "reducción"
        bullet_3 = f"{segundo_nombre} muestra la mayor {termino_variacion} relativa ({signo_cr}{abs(segundo_var_inc_pct):.0f}% vs periodo anterior){causa_raiz_texto_2}"
    elif len(eventos_comerciales) > 0:
        # Si no hay segundo elemento, usar eventos comerciales
        evento_top = list(eventos_comerciales.values())[0]
        bullet_3 = f"Eventos relevantes: {evento_top['nombre']} explica {evento_top['porcentaje']:.1f}% de los casos ({evento_top['casos']:,} casos correlacionados)"
    elif len(df_weekly) > 0:
        # Si no hay eventos, usar análisis de picos semanales
        promedio_incoming = df_weekly['INCOMING'].mean()
        std_incoming = df_weekly['INCOMING'].std()
        umbral_pico = promedio_incoming + (1.5 * std_incoming)
        df_picos = df_weekly[df_weekly['INCOMING'] > umbral_pico].copy()
        
        if len(df_picos) > 0:
            df_picos = df_picos.sort_values('INCOMING', ascending=False).head(2)
            picos_info = []
            for _, row in df_picos.iterrows():
                fecha = row['SEMANA'].strftime('%d-%b')
                casos = int(row['INCOMING'])
                picos_info.append(f"{fecha} ({casos:,} casos)")
            
            picos_str = " y ".join(picos_info)
            bullet_3 = f"Días pico: {picos_str} registraron valores por encima del promedio de {int(promedio_incoming):,} casos/semana"

# Asegurar que siempre tengamos 3 bullets
if not bullet_2:
    bullet_2 = f"Incoming total aumentó {signo_cr}{var_inc_total:,} casos ({signo_cr}{var_inc_pct:.1f}%) mientras los drivers se mantuvieron estables"
if not bullet_3:
    total_conversaciones = sum(d.get('analisis_llm', {}).get('total_conversaciones', 0) for d in conversaciones_por_proceso.values()) if conversaciones_por_proceso else 0
    bullet_3 = f"Análisis basado en {len(cuadros_cuantitativos)} dimensiones y {total_conversaciones} conversaciones muestreadas"

# ========================================
# GENERAR HALLAZGO PRINCIPAL (v6.4.1 - Interpretación de Negocio Automática)
# ========================================

# Detectar contexto temporal
meses_temporada_alta = [11, 12]  # Nov, Dic (Black Friday, Navidad)
meses_post_temporada = [1, 2]    # Ene, Feb (normalización)
meses_hot_sale = [5, 6]          # May, Jun (Hot Sale en LATAM)

p1_mes = p1_start_dt.month
p2_mes = p2_start_dt.month

# Determinar si hay efecto de temporada
es_post_temporada = (p1_mes in meses_temporada_alta and p2_mes in meses_post_temporada)
es_durante_temporada = (p1_mes not in meses_temporada_alta and p2_mes in meses_temporada_alta)
es_hot_sale = (p2_mes in meses_hot_sale)

# Calcular variación porcentual del incoming
var_inc_abs = abs(var_inc_pct)

# Determinar patrones según datos
cr_mejoro = var_cr < 0
incoming_bajo = var_inc_pct < 0
incoming_subio = var_inc_pct > 0
variacion_significativa = abs(var_cr_pct) >= 10  # Cambio >= 10%

# Generar lista de explicaciones basadas en el contexto
hallazgo_explicaciones = []

# 1. Análisis del cambio de volumen
if incoming_bajo and var_inc_abs >= 20:
    if es_post_temporada:
        hallazgo_explicaciones.append(f"Menor volumen de incoming ({var_inc_pct:.0f}% casos) post-temporada alta (Black Friday + Navidad)")
    else:
        hallazgo_explicaciones.append(f"Reducción significativa del volumen de incoming ({var_inc_pct:.0f}% casos)")
elif incoming_subio and var_inc_abs >= 20:
    if es_durante_temporada:
        hallazgo_explicaciones.append(f"Aumento de volumen ({var_inc_pct:+.0f}% casos) por temporada alta (Black Friday/Navidad)")
    elif es_hot_sale:
        hallazgo_explicaciones.append(f"Incremento de incoming ({var_inc_pct:+.0f}% casos) durante campaña Hot Sale")
    else:
        hallazgo_explicaciones.append(f"Crecimiento en volumen de incoming ({var_inc_pct:+.0f}% casos)")

# 2. Análisis de patrones logísticos/operativos según commerce group
commerce_group_upper = args.commerce_group.upper()
if commerce_group_upper in ['PNR', 'PDD']:
    if cr_mejoro and es_post_temporada:
        hallazgo_explicaciones.append("Normalización logística de transportistas después del pico de diciembre")
    elif not cr_mejoro and es_durante_temporada:
        hallazgo_explicaciones.append("Saturación logística por alto volumen de órdenes en temporada pico")
elif 'ME' in commerce_group_upper or 'FBM' in commerce_group_upper or 'SHIPPING' in commerce_group_upper:
    if cr_mejoro:
        hallazgo_explicaciones.append("Menor saturación en fulfillment y envíos rápidos")
    else:
        hallazgo_explicaciones.append("Mayor presión operativa en fulfillment y distribución")
elif 'PAGOS' in commerce_group_upper or 'MP' in commerce_group_upper:
    if cr_mejoro:
        hallazgo_explicaciones.append("Estabilización en procesamiento de pagos y flujos transaccionales")
    else:
        hallazgo_explicaciones.append("Incremento en consultas relacionadas a transacciones y disputas de pagos")

# 3. Buscar patrones en las causas raíz del análisis de conversaciones
if conversaciones_por_proceso:
    causas_principales = []
    for proceso, data in conversaciones_por_proceso.items():
        analisis_llm = data.get('analisis_llm', {})
        causas_list = analisis_llm.get('causas_raiz') or analisis_llm.get('causas', [])
        for causa in causas_list[:2]:  # Top 2 causas por proceso
            causa_nombre = causa.get('causa', '')
            causa_pct = causa.get('porcentaje', 0)
            if causa_pct >= 20:  # Solo causas con >= 20% de menciones
                causas_principales.append(f"{causa_nombre} ({causa_pct}%)")
    
    if causas_principales:
        # Eliminar duplicados manteniendo orden
        causas_unicas = list(dict.fromkeys(causas_principales))[:3]
        if len(causas_unicas) > 0:
            hallazgo_explicaciones.append(f"Causas raíz predominantes: {', '.join(causas_unicas)}")

# 4. Integrar eventos comerciales relevantes (v6.4.2)
if eventos_comerciales:
    # Encontrar el evento con mayor impacto (mayor correlación)
    evento_top = max(eventos_comerciales.values(), key=lambda x: x.get('casos_total', 0))
    pct_correlacion = (evento_top.get('porcentaje_p1', 0) + evento_top.get('porcentaje_p2', 0)) / 2
    
    if pct_correlacion >= 3:  # Solo mencionar si es significativo (≥3%)
        delta_evento = evento_top.get('delta_casos', 0)
        
        if es_post_temporada and delta_evento < 0:
            # Post-temporada con menos casos correlacionados = efecto positivo
            hallazgo_explicaciones.append(
                f"Efecto post-{evento_top['nombre']}: reducción de {abs(delta_evento):,} casos correlacionados vs período anterior ({pct_correlacion:.1f}% del incoming)"
            )
        elif es_durante_temporada and delta_evento > 0:
            # Durante temporada con más casos = presión
            hallazgo_explicaciones.append(
                f"Impacto de {evento_top['nombre']}: +{delta_evento:,} casos adicionales correlacionados con el evento ({pct_correlacion:.1f}% del incoming)"
            )
        elif pct_correlacion >= 5:
            # Alta correlación general
            hallazgo_explicaciones.append(
                f"Correlación con {evento_top['nombre']}: {evento_top.get('casos_total', 0):,} casos ({pct_correlacion:.1f}% del incoming) originados durante el evento"
            )

# 5. Si no hay suficientes explicaciones, agregar una genérica basada en métricas
if len(hallazgo_explicaciones) < 2:
    if cr_mejoro:
        hallazgo_explicaciones.append(f"Mejora operativa reflejada en reducción del CR ({var_cr:.4f} pp)")
    else:
        hallazgo_explicaciones.append(f"Incremento de contactos que requiere atención ({var_cr:+.4f} pp)")

# Generar texto introductorio del hallazgo
if cr_mejoro:
    hallazgo_intro = f"La <strong>mejora del {abs(var_cr_pct):.1f}%</strong> en CR se explica principalmente por:"
else:
    hallazgo_intro = f"El <strong>empeoramiento del {abs(var_cr_pct):.1f}%</strong> en CR se debe principalmente a:"

# Generar HTML del hallazgo principal
hallazgo_items_html = "\n                ".join([f"<li>{exp}</li>" for exp in hallazgo_explicaciones])

hallazgo_principal_html = f"""
        <!-- HALLAZGO PRINCIPAL - v6.4.1 -->
        <div class="hallazgo-principal">
            <h3><span class="emoji">💡</span> Hallazgo Principal</h3>
            <p class="intro">{hallazgo_intro}</p>
            <ul>
                {hallazgo_items_html}
            </ul>
        </div>
"""

# Generar HTML inline (sin Jinja2 por ahora)
html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CR Report v6.3 - {args.commerce_group} {args.site}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ========================================
           DISEÑO MELI INSTITUCIONAL v2.0 - PROFESIONAL
           Paleta: Amarillo #FFE600, Azul #3483FA, Verde #00A650
           Tipografía: Nunito Sans (similar a Proxima Nova)
           ======================================== */
        
        :root {{
            --meli-yellow: #FFE600;
            --meli-blue: #3483FA;
            --meli-green: #00A650;
            --meli-red: #F23D4F;
            --meli-dark: #333333;
            --meli-gray: #666666;
            --meli-light: #EDEDED;
            --meli-white: #FFFFFF;
            --meli-bg: #F5F5F5;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-md: 0 2px 6px rgba(0,0,0,0.1);
            --radius: 8px;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: 'Nunito Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: var(--meli-light); 
            color: var(--meli-dark); 
            line-height: 1.6;
            font-size: 14px;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        
        /* ========== HEADER ========== */
        .header {{ 
            background: var(--meli-yellow); 
            color: var(--meli-dark); 
            padding: 32px 40px; 
            border-radius: var(--radius); 
            margin-bottom: 24px; 
            box-shadow: var(--shadow-sm);
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.5px; }}
        .header .subtitle {{ font-size: 15px; opacity: 0.8; font-weight: 400; }}
        
        /* ========== CARDS KPI ========== */
        .cards-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 16px; 
            margin-bottom: 24px; 
        }}
        .card {{ 
            background: var(--meli-white); 
            padding: 20px 24px; 
            border-radius: var(--radius); 
            box-shadow: var(--shadow-sm);
            border-top: 3px solid var(--meli-blue);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-md); }}
        .card.negative {{ border-top-color: var(--meli-red); }}
        .card.positive {{ border-top-color: var(--meli-green); }}
        .card-label {{ 
            font-size: 11px; 
            color: var(--meli-gray); 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            margin-bottom: 8px; 
            font-weight: 700; 
        }}
        .card-value {{ 
            font-size: 26px; 
            font-weight: 800; 
            color: var(--meli-dark); 
            line-height: 1.1;
            letter-spacing: -0.5px;
        }}
        .card-change {{ font-size: 13px; margin-top: 8px; font-weight: 600; }}
        .card-change.positive {{ color: var(--meli-green); }}
        .card-change.negative {{ color: var(--meli-red); }}
        
        /* ========== SECCIONES ========== */
        .section {{ 
            background: var(--meli-white); 
            padding: 28px 32px; 
            border-radius: var(--radius); 
            margin-bottom: 24px; 
            box-shadow: var(--shadow-sm);
        }}
        .section h2 {{ 
            color: var(--meli-dark); 
            margin-bottom: 24px; 
            font-size: 20px; 
            padding-bottom: 12px; 
            border-bottom: 2px solid var(--meli-yellow); 
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section h3 {{ 
            color: var(--meli-dark); 
            margin: 20px 0 16px 0; 
            font-size: 16px; 
            font-weight: 700; 
        }}
        
        .chart-container {{ position: relative; height: 400px; margin: 24px 0; }}
        
        /* ========== TABLAS UNIFICADAS ========== */
        table {{ 
            width: 100%; 
            border-collapse: separate;
            border-spacing: 0;
            margin: 16px 0; 
            font-size: 13px;
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}
        thead {{ background: var(--meli-dark); }}
        thead th {{ 
            color: white; 
            padding: 14px 16px; 
            text-align: left; 
            font-weight: 700; 
            font-size: 11px; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        thead th:first-child {{ border-radius: var(--radius) 0 0 0; }}
        thead th:last-child {{ border-radius: 0 var(--radius) 0 0; }}
        tbody td {{ 
            padding: 12px 16px; 
            border-bottom: 1px solid var(--meli-light);
            background: var(--meli-white);
        }}
        tbody tr:last-child td {{ border-bottom: none; }}
        tbody tr:last-child td:first-child {{ border-radius: 0 0 0 var(--radius); }}
        tbody tr:last-child td:last-child {{ border-radius: 0 0 var(--radius) 0; }}
        td.number {{ text-align: right; font-family: 'Consolas', 'Monaco', monospace; font-weight: 600; }}
        td.positive {{ color: var(--meli-green); font-weight: 700; }}
        td.negative {{ color: var(--meli-red); font-weight: 700; }}
        tbody tr:hover td {{ background: var(--meli-bg); }}
        tbody tr.row-otros td {{ background: var(--meli-bg); color: var(--meli-gray); font-style: italic; }}
        tbody tr.row-total td {{ background: var(--meli-dark); color: white; font-weight: 700; }}
        
        /* ========== NOTAS Y ALERTAS ========== */
        .note {{ 
            background: var(--meli-bg); 
            border-left: 3px solid var(--meli-blue); 
            padding: 14px 18px; 
            margin: 16px 0; 
            border-radius: 0 var(--radius) var(--radius) 0; 
            font-size: 13px; 
        }}
        
        .badge-pico {{ 
            display: inline-block; 
            background: var(--meli-red); 
            color: white; 
            padding: 3px 10px; 
            border-radius: 12px; 
            font-size: 10px; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }}
        .badge-normal {{ 
            display: inline-block; 
            background: var(--meli-gray); 
            color: white; 
            padding: 3px 10px; 
            border-radius: 12px; 
            font-size: 10px; 
            font-weight: 700; 
            text-transform: uppercase; 
        }}
        
        .case-header {{ 
            display: flex; 
            align-items: center; 
            margin-bottom: 8px; 
            padding-bottom: 8px; 
            border-bottom: 1px solid var(--meli-light); 
        }}
        .case-info {{ color: var(--meli-dark); font-size: 12px; font-weight: 700; }}
        .case-fecha {{ color: var(--meli-gray); font-size: 11px; margin-left: 12px; }}
        
        /* ========== RESUMEN EJECUTIVO ========== */
        .resumen-ejecutivo {{ 
            background: var(--meli-white); 
            padding: 28px 32px; 
            border-radius: var(--radius); 
            margin-bottom: 24px; 
            box-shadow: var(--shadow-sm);
            border-top: 3px solid var(--meli-yellow);
        }}
        .resumen-ejecutivo h2 {{ 
            color: var(--meli-dark); 
            font-size: 20px; 
            font-weight: 700; 
            margin-bottom: 20px; 
            padding-bottom: 12px; 
            border-bottom: 2px solid var(--meli-yellow);
        }}
        .resumen-ejecutivo ul {{ list-style: none; padding: 0; margin: 0; }}
        .resumen-ejecutivo li {{ 
            margin-bottom: 16px; 
            padding-left: 24px; 
            position: relative; 
            font-size: 14px; 
            line-height: 1.7; 
        }}
        .resumen-ejecutivo li:before {{ 
            content: ''; 
            position: absolute; 
            left: 0; 
            top: 7px; 
            width: 8px; 
            height: 8px; 
            background: var(--meli-blue); 
            border-radius: 50%; 
        }}
        .resumen-ejecutivo li strong {{ font-weight: 700; }}
        
        /* ========== HALLAZGO PRINCIPAL ========== */
        .hallazgo-principal {{ 
            background: linear-gradient(135deg, #F0F7FF 0%, #E8F4FC 100%);
            border-left: 4px solid var(--meli-blue); 
            padding: 24px 28px; 
            border-radius: 0 var(--radius) var(--radius) 0; 
            margin-bottom: 24px;
        }}
        .hallazgo-principal h3 {{ 
            color: var(--meli-blue); 
            font-size: 16px; 
            font-weight: 700; 
            margin-bottom: 14px; 
        }}
        .hallazgo-principal .intro {{ font-size: 14px; color: var(--meli-dark); margin-bottom: 12px; }}
        .hallazgo-principal ul {{ list-style: none; padding: 0; margin: 0; }}
        .hallazgo-principal li {{ 
            margin-bottom: 10px; 
            padding-left: 22px; 
            position: relative; 
            font-size: 13px; 
            line-height: 1.6; 
        }}
        .hallazgo-principal li:before {{ 
            content: '✓'; 
            position: absolute; 
            left: 0; 
            color: var(--meli-green); 
            font-weight: 700; 
        }}
        
        /* ========== EVENTOS COMERCIALES ========== */
        .eventos-comerciales {{ 
            background: var(--meli-white); 
            padding: 28px 32px; 
            border-radius: var(--radius); 
            margin-bottom: 24px; 
            box-shadow: var(--shadow-sm);
        }}
        .eventos-comerciales h2 {{ 
            color: var(--meli-dark); 
            font-size: 20px; 
            font-weight: 700; 
            margin-bottom: 16px; 
            padding-bottom: 12px; 
            border-bottom: 2px solid var(--meli-yellow);
        }}
        .eventos-comerciales .info-box {{ 
            background: var(--meli-bg); 
            border-left: 3px solid var(--meli-blue); 
            padding: 10px 14px; 
            margin-bottom: 16px; 
            border-radius: 0 var(--radius) var(--radius) 0; 
            font-size: 12px; 
        }}
        .eventos-comerciales .evento-nombre {{ font-weight: 600; }}
        .eventos-comerciales .badge {{ 
            display: inline-block; 
            padding: 3px 8px; 
            border-radius: 10px; 
            font-size: 10px; 
            font-weight: 700; 
        }}
        .eventos-comerciales .badge-positive {{ background: #D4EDDA; color: var(--meli-green); }}
        .eventos-comerciales .badge-negative {{ background: #F8D7DA; color: var(--meli-red); }}
        .eventos-comerciales .badge-neutral {{ background: var(--meli-light); color: var(--meli-gray); }}
        .eventos-comerciales .summary {{ 
            background: var(--meli-bg); 
            padding: 12px 16px; 
            border-radius: var(--radius); 
            margin-top: 16px; 
            font-size: 13px;
        }}
        .eventos-comerciales .no-data {{ text-align: center; padding: 24px; color: var(--meli-gray); font-style: italic; }}
        
        /* ========== WARNING BANNER ========== */
        .warning-banner {{ 
            background: var(--meli-yellow); 
            color: var(--meli-dark); 
            padding: 14px 20px; 
            border-radius: var(--radius); 
            margin-bottom: 16px; 
            display: flex; 
            align-items: center; 
            gap: 12px;
        }}
        .warning-banner .title {{ font-weight: 700; font-size: 14px; margin-bottom: 4px; }}
        .warning-banner .description {{ font-size: 13px; opacity: 0.85; }}
        
        /* ========== FOOTER ========== */
        .footer-container {{ margin-top: 32px; }}
        .footer-toggle {{ 
            background: var(--meli-dark); 
            color: white; 
            cursor: pointer; 
            padding: 16px 24px; 
            border: none; 
            text-align: left; 
            width: 100%; 
            font-size: 15px; 
            font-weight: 700; 
            border-radius: var(--radius); 
            transition: background 0.2s; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .footer-toggle:hover {{ background: #444; }}
        .footer-toggle:after {{ content: '▼'; font-size: 12px; }}
        .footer-toggle.active:after {{ content: '▲'; }}
        .footer-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }}
        .footer {{ 
            background: var(--meli-dark); 
            color: var(--meli-light); 
            padding: 28px 32px; 
            border-radius: 0 0 var(--radius) var(--radius); 
            font-size: 12px; 
            line-height: 1.8;
        }}
        .footer h4 {{ color: var(--meli-yellow); margin: 12px 0 8px 0; font-size: 14px; font-weight: 700; }}
        
        /* ========== CARDS COLAPSABLES ANÁLISIS ========== */
        .analysis-card {{ 
            background: var(--meli-white); 
            border-radius: var(--radius); 
            box-shadow: var(--shadow-sm); 
            margin-bottom: 16px; 
            overflow: hidden; 
            transition: box-shadow 0.2s;
            border: 1px solid var(--meli-light);
        }}
        .analysis-card:hover {{ box-shadow: var(--shadow-md); }}
        .analysis-card-header {{ 
            padding: 18px 24px; 
            cursor: pointer; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            transition: background 0.2s;
        }}
        .analysis-card-header:hover {{ background: var(--meli-bg); }}
        .analysis-card-header.expanded {{ background: #FFF9E0; border-bottom: 2px solid var(--meli-yellow); }}
        .analysis-card-header-left {{ display: flex; align-items: center; gap: 14px; flex: 1; }}
        .analysis-card-rank {{ 
            width: 36px; 
            height: 36px; 
            background: var(--meli-blue); 
            color: white; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: 800; 
            font-size: 14px;
        }}
        .analysis-card-rank.top-3 {{ background: var(--meli-yellow); color: var(--meli-dark); }}
        .analysis-card-title {{ font-size: 15px; font-weight: 700; color: var(--meli-dark); }}
        .analysis-card-badges {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .analysis-card-badge {{ 
            padding: 4px 10px; 
            border-radius: 12px; 
            font-size: 11px; 
            font-weight: 700;
        }}
        .analysis-card-badge.contrib {{ background: #E8F4FC; color: var(--meli-blue); }}
        .analysis-card-badge.positive {{ background: #D4EDDA; color: var(--meli-green); }}
        .analysis-card-badge.negative {{ background: #F8D7DA; color: var(--meli-red); }}
        .analysis-card-badge.conv {{ background: var(--meli-light); color: var(--meli-dark); }}
        .analysis-card-toggle {{ 
            width: 32px; 
            height: 32px; 
            border-radius: 50%; 
            background: var(--meli-light); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            transition: all 0.2s;
        }}
        .analysis-card-toggle svg {{ transition: transform 0.3s; width: 12px; height: 12px; }}
        .analysis-card-header.expanded .analysis-card-toggle {{ background: var(--meli-blue); }}
        .analysis-card-header.expanded .analysis-card-toggle svg {{ transform: rotate(180deg); fill: white; }}
        .analysis-card-content {{ max-height: 0; overflow: hidden; transition: max-height 0.4s ease-out; }}
        .analysis-card-content.expanded {{ max-height: 5000px; transition: max-height 0.6s ease-in; }}
        .analysis-card-content-inner {{ padding: 24px; background: var(--meli-bg); }}
        
        /* ========== TABLAS DE CAUSAS (UNIFICADAS) ========== */
        .causa-table {{ 
            width: 100%; 
            border-collapse: separate;
            border-spacing: 0;
            margin: 16px 0; 
            font-size: 13px;
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}
        .causa-table thead tr:first-child th {{ background: var(--meli-dark); color: white; }}
        .causa-table thead tr:first-child th:first-child {{ border-radius: var(--radius) 0 0 0; }}
        .causa-table thead tr:first-child th:last-child {{ border-radius: 0 var(--radius) 0 0; }}
        .causa-table thead th {{ 
            padding: 12px 14px; 
            text-align: center; 
            font-weight: 700; 
            font-size: 11px; 
            text-transform: uppercase;
            letter-spacing: 0.3px;
            border: none;
        }}
        .causa-table thead th.col-periodo {{ background: var(--meli-yellow); color: var(--meli-dark); }}
        .causa-table thead th.col-subheader {{ background: #444; color: white; font-size: 10px; }}
        .causa-table tbody td {{ 
            padding: 11px 14px; 
            border-bottom: 1px solid var(--meli-light);
            background: var(--meli-white);
            text-align: center;
        }}
        .causa-table tbody td:first-child {{ text-align: left; font-weight: 600; color: var(--meli-dark); }}
        .causa-table tbody tr:last-child td {{ border-bottom: none; }}
        .causa-table tbody tr:last-child td:first-child {{ border-radius: 0 0 0 var(--radius); }}
        .causa-table tbody tr:last-child td:last-child {{ border-radius: 0 0 var(--radius) 0; }}
        .causa-table tbody tr:hover td {{ background: var(--meli-bg); }}
        .causa-table tbody tr.row-total td {{ background: var(--meli-dark); color: white; font-weight: 700; }}
        .causa-table .val-positive {{ color: var(--meli-green); font-weight: 700; }}
        .causa-table .val-negative {{ color: var(--meli-red); font-weight: 700; }}
        .causa-table .val-neutral {{ color: var(--meli-gray); }}
        
        /* ========== INSIGHT BOX ========== */
        .insight-box {{
            background: linear-gradient(135deg, #FFF9E0 0%, #FFF3CD 100%);
            border-left: 4px solid var(--meli-yellow);
            padding: 16px 20px;
            margin: 16px 0;
            border-radius: 0 var(--radius) var(--radius) 0;
        }}
        .insight-box strong {{ color: var(--meli-dark); font-size: 14px; }}
        .insight-box p {{ margin: 8px 0 0 0; color: #5a4a00; line-height: 1.6; font-size: 13px; }}
        
        /* ========== MINI CARDS MÉTRICAS ========== */
        .metrics-row {{ display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
        .metric-box {{ 
            background: var(--meli-bg); 
            padding: 16px 20px; 
            border-radius: var(--radius); 
            flex: 1; 
            min-width: 160px;
            border-top: 3px solid var(--meli-blue);
        }}
        .metric-box.variation-positive {{ background: #D4EDDA; border-top-color: var(--meli-green); }}
        .metric-box.variation-negative {{ background: #F8D7DA; border-top-color: var(--meli-red); }}
        .metric-box.contrib {{ background: #E8F4FC; border-top-color: var(--meli-blue); }}
        .metric-box-label {{ font-size: 11px; color: var(--meli-gray); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }}
        .metric-box-value {{ font-size: 20px; font-weight: 800; color: var(--meli-dark); }}
        .metric-box.variation-positive .metric-box-value {{ color: var(--meli-green); }}
        .metric-box.variation-negative .metric-box-value {{ color: var(--meli-red); }}
        .metric-box.contrib .metric-box-value {{ color: var(--meli-blue); }}
        
        /* ========== ALERT BOX ========== */
        .alert-box {{
            background: #FFF3CD;
            border-left: 4px solid var(--meli-yellow);
            padding: 14px 18px;
            margin: 14px 0;
            border-radius: 0 var(--radius) var(--radius) 0;
        }}
        .alert-box strong {{ color: #856404; font-size: 13px; }}
        .alert-box p {{ margin: 6px 0 0 0; color: #856404; line-height: 1.5; font-size: 12px; }}
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 1200px) {{
            .cards-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 768px) {{
            .cards-grid {{ grid-template-columns: 1fr; }}
            .container {{ padding: 16px; }}
        }}
        @media print {{ 
            body {{ background: white; }} 
            .section, .card {{ box-shadow: none; }} 
            .footer-container {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Contact Rate Analysis - {args.commerce_group}{f' - {args.process_name}' if args.process_name else ''} {args.site}</h1>
            <div class="subtitle">
                Período: {p1_label} vs {p2_label} | Commerce Group: {args.commerce_group}{f' | Proceso: {args.process_name}' if args.process_name else ''} | Site: {args.site}
            </div>
        </div>
        
        {'<!-- WARNING BANNER: DRIVER OVERRIDE -->' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
        {'<div class="warning-banner">' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
            {'<div class="icon">⚠️</div>' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
            {'<div class="text">' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
                {'<div class="title">MODO OVERRIDE ACTIVO: Driver Filtrado por Site</div>' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
                {f'<div class="description">Este reporte usa driver de Shipping filtrado por {args.site} (no estándar). La regla oficial indica que el driver debe ser GLOBAL (todos los sites). Ver docs/SHIPPING_DRIVERS.md para más información.</div>' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
            {'</div>' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
        {'</div>' if driver_config['type'] == 'shipping_drivers' and args.filter_driver_by_site else ''}
        
        <!-- RESUMEN EJECUTIVO -->
        <div class="resumen-ejecutivo">
            <h2>📊 Resumen Ejecutivo</h2>
            <ul>
                <li><strong>{bullet_1}</strong></li>
                <li><strong>{bullet_2}</strong></li>
                <li><strong>{bullet_3}</strong></li>
            </ul>
        </div>
        
        {hallazgo_principal_html}
        
        <!-- CARDS (8 en orden v6.1) -->
        <div class="cards-grid">
            <div class="card">
                <div class="card-label">CR {p1_label}</div>
                <div class="card-value">{cr_p1:.4f}</div>
                <div class="card-change">pp</div>
            </div>
            <div class="card {var_cr_class}">
                <div class="card-label">CR {p2_label}</div>
                <div class="card-value">{cr_p2:.4f}</div>
                <div class="card-change {var_cr_class}">{var_cr:+.4f} pp</div>
            </div>
            <div class="card {var_cr_class}">
                <div class="card-label">Variación CR</div>
                <div class="card-value">{var_cr:+.4f}</div>
                <div class="card-change {var_cr_class}">pp ({var_cr_pct:+.1f}%)</div>
            </div>
            <div class="card {var_inc_class}">
                <div class="card-label">Variación Incoming</div>
                <div class="card-value">{var_inc_total:+,}</div>
                <div class="card-change {var_inc_class}">casos ({var_inc_pct:+.1f}%)</div>
            </div>
            
            <div class="card">
                <div class="card-label">Incoming {p1_label}</div>
                <div class="card-value">{inc_p1_total:,}</div>
                <div class="card-change">casos</div>
            </div>
            <div class="card {var_inc_class}">
                <div class="card-label">Incoming {p2_label}</div>
                <div class="card-value">{inc_p2_total:,}</div>
                <div class="card-change {var_inc_class}">{var_inc_total:+,} casos</div>
            </div>
            <div class="card">
                <div class="card-label">Driver {p1_label}</div>
                <div class="card-value">{drv_p1_total:,.0f}</div>
                <div class="card-change">órdenes</div>
            </div>
            <div class="card">
                <div class="card-label">Driver {p2_label}</div>
                <div class="card-value">{drv_p2_total:,.0f}</div>
                <div class="card-change">órdenes</div>
            </div>
        </div>
        
        <!-- GRÁFICO SEMANAL -->
        <div class="section">
            <h2>📈 Evolución Semanal CR</h2>
            <div class="chart-container">
                <canvas id="weeklyChart"></canvas>
            </div>
        </div>
        
        <!-- EVENTOS COMERCIALES -->
        {eventos_html}
        
        <!-- CUADROS CUANTITATIVOS -->
        <div class="section">
            <h2>📊 Cuadros Cuantitativos por Dimensión</h2>
"""

# Agregar cada cuadro cuantitativo
for dimension, df in cuadros_cuantitativos.items():
    # Ordenar por |VAR_CR| descendente (mayor impacto en CR primero)
    # Mantener "Otros" y "TOTAL" al final
    df_elementos = df[~df['DIMENSION_VAL'].str.contains('Otros|TOTAL', case=False, na=False)].copy()
    df_otros = df[df['DIMENSION_VAL'].str.contains('Otros', case=False, na=False)]
    df_total = df[df['DIMENSION_VAL'] == 'TOTAL']
    
    # Ordenar elementos por VAR_CR absoluto (mayor variación primero)
    df_elementos = df_elementos.sort_values('VAR_CR', key=lambda x: abs(x), ascending=False)
    
    # Reconstruir DataFrame ordenado: elementos + otros + total
    df_ordenado = pd.concat([df_elementos, df_otros, df_total], ignore_index=True)
    
    html_content += f"""
            <h3>🔹 Dimensión: {dimension}</h3>
            <table>
                <thead>
                    <tr>
                        <th>{dimension}</th>
                        <th class="number">Casos {p1_label}</th>
                        <th class="number">Casos {p2_label}</th>
                        <th class="number">CR {p1_label} (pp)</th>
                        <th class="number">CR {p2_label} (pp)</th>
                        <th class="number">Var CR (pp)</th>
                        <th class="number">Contrib %</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for idx, row in df_ordenado.iterrows():
        is_otros = 'Otros' in str(row['DIMENSION_VAL'])
        is_total = row['DIMENSION_VAL'] == 'TOTAL'
        
        row_class = ''
        if is_otros:
            row_class = 'row-otros'
        elif is_total:
            row_class = 'row-total'
        
        var_class = 'negative' if row['VAR_CR'] > 0 else 'positive' if row['VAR_CR'] < 0 else ''
        
        html_content += f"""
                    <tr class="{row_class}">
                        <td><strong>{row['DIMENSION_VAL']}</strong></td>
                        <td class="number">{int(row['INC_P1']):,}</td>
                        <td class="number">{int(row['INC_P2']):,}</td>
                        <td class="number">{row['CR_P1']:.4f}</td>
                        <td class="number">{row['CR_P2']:.4f}</td>
                        <td class="number {var_class}">{row['VAR_CR']:+.4f}</td>
                        <td class="number {var_class}">{row['CONTRIB_ABS']:.1f}%</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
"""

html_content += """
        </div>
"""

# ========================================
# AGREGAR ANÁLISIS COMPARATIVO DE PATRONES (v6.3.2)
# ========================================
p1_mes = args.p1_start[:7]  # YYYY-MM
p2_mes = args.p2_start[:7]  # YYYY-MM
analisis_comparativo_path = output_dir / f"analisis_conversaciones_comparativo_claude_{args.site.lower()}_{args.commerce_group.lower()}_{args.muestreo_dimension.lower()}_{p1_mes}_{p2_mes}.json"

# Definir cuadro_dimension_path para todos los bloques (v6.4.0)
cuadro_dimension_path = Path("output") / f"cuadro_{args.muestreo_dimension.lower()}_{args.site.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"

# ========================================
# v6.4.10 FIX: Siempre regenerar análisis comparativo fresco
# ========================================
# Se deshabilitó la carga de comparativos pre-existentes del disco.
# Motivo: el archivo podía contener datos de una dimensión diferente (ej: PROCESO vs CDU),
# causando que las keys no matchearan con el cuadro cuantitativo y la sección quedara vacía.
# Ahora siempre se regenera desde los JSONs separados (P1/P2) para garantizar consistencia.
# ========================================
if False:  # v6.4.10: DESHABILITADO - siempre regenerar fresco, nunca cargar comparativos stale
    analisis_comp = {}  # Dead code - nunca se ejecuta
    
    # Obtener orden por contribución desde el cuadro de dimensión (v6.4.0)
    df_orden_existente = None
    if cuadro_dimension_path.exists():
        try:
            df_orden_existente = pd.read_csv(cuadro_dimension_path)
            df_orden_existente = df_orden_existente[~df_orden_existente['DIMENSION_VAL'].str.contains('Otros|TOTAL', case=False, na=False)]
            # Ordenar por |VAR_CR| descendente (mayor impacto en CR primero) - v6.4.9
            df_orden_existente = df_orden_existente.sort_values('VAR_CR', key=lambda x: abs(x), ascending=False)
            orden_contribucion_existente = df_orden_existente['DIMENSION_VAL'].tolist()
        except:
            orden_contribucion_existente = list(analisis_comp.keys())
    else:
        orden_contribucion_existente = list(analisis_comp.keys())
    
    dimension_label_existente = aperturas_list[-1] if aperturas_list else "Elemento"
    
    html_content += f"""
        <!-- ANÁLISIS COMPARATIVO CON CARDS COLAPSABLES - v6.4.0 -->
        <div class="section">
            <h2>🔍 Análisis Comparativo por {dimension_label_existente}</h2>
            <p style="margin-bottom: 20px; font-size: 15px; color: #555;">
                Cada card representa un elemento de <strong>{dimension_label_existente}</strong>, ordenado por su <strong>contribución a la variación de CR</strong>.
                Haz clic para expandir el análisis detallado.
            </p>
        
        <script>
            function toggleAnalysisCard(cardId) {{
                var header = document.getElementById('header_' + cardId);
                var content = document.getElementById('content_' + cardId);
                var isExpanded = header.classList.contains('expanded');
                
                if (isExpanded) {{
                    header.classList.remove('expanded');
                    content.classList.remove('expanded');
                }} else {{
                    header.classList.add('expanded');
                    content.classList.add('expanded');
                }}
            }}
            
            function toggleCitas(procesoid) {{
                var elem = document.getElementById('citas_' + procesoid);
                var btn = document.getElementById('btn_' + procesoid);
                if (elem.style.display === 'none') {{
                    elem.style.display = 'block';
                    btn.innerHTML = 'Ocultar citas adicionales ▲';
                }} else {{
                    elem.style.display = 'none';
                    btn.innerHTML = 'Ver citas adicionales ▼';
                }}
            }}
            
            function expandAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.add('expanded'); }});
                contents.forEach(function(c) {{ c.classList.add('expanded'); }});
            }}
            
            function collapseAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.remove('expanded'); }});
                contents.forEach(function(c) {{ c.classList.remove('expanded'); }});
            }}
        </script>
        
        <div style="margin-bottom: 20px; display: flex; gap: 10px;">
            <button onclick="expandAllCards()" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📂 Expandir todas
            </button>
            <button onclick="collapseAllCards()" style="background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📁 Colapsar todas
            </button>
        </div>
"""
    
    # Iterar por cada elemento en orden de contribución (v6.4.0)
    rank_existente = 0
    for proceso_key in orden_contribucion_existente:
        if proceso_key not in analisis_comp:
            continue
        data = analisis_comp[proceso_key]
        if data['conversaciones_nov'] == 0 and data['conversaciones_dic'] == 0:
            continue
        
        rank_existente += 1
        proceso = data['proceso']
        proceso_id = proceso.replace(' ', '_').replace('-', '_').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        inc_nov = data['incoming_nov']
        inc_dic = data['incoming_dic']
        var_casos = data['variacion_casos']
        var_pct = data['variacion_pct']
        total_conv = data['conversaciones_nov'] + data['conversaciones_dic']
        
        # Obtener datos de contribución
        contrib_pct_exist = 0
        if df_orden_existente is not None and len(df_orden_existente) > 0:
            row = df_orden_existente[df_orden_existente['DIMENSION_VAL'] == proceso_key]
            if len(row) > 0:
                contrib_pct_exist = row['CONTRIB_ABS'].values[0] if pd.notna(row['CONTRIB_ABS'].values[0]) else 0
        
        # Verificar si hay muestra insuficiente
        muestra_insuficiente = total_conv < UMBRAL_MINIMO_CONVERSACIONES
        
        # Calcular cobertura promedio
        cobertura_nov = data['causas_nov'][0].get('porcentaje', 0) if len(data['causas_nov']) > 0 else 0
        cobertura_total = sum([c['porcentaje'] for c in data['causas_nov'][:4]]) if len(data['causas_nov']) > 0 else 100
        
        is_top_3_exist = rank_existente <= 3
        is_expanded_exist = rank_existente == 1
        expanded_class_exist = "expanded" if is_expanded_exist else ""
        rank_class_exist = "top-3" if is_top_3_exist else ""
        
        if var_casos < 0:
            var_badge_class_exist = "positive"
            var_badge_text_exist = f"✅ {var_casos:,} casos"
        else:
            var_badge_class_exist = "negative"
            var_badge_text_exist = f"🔴 +{var_casos:,} casos"
        
        html_content += f"""
            <!-- CARD #{rank_existente}: {proceso} -->
            <div class="analysis-card">
                <div id="header_{proceso_id}" class="analysis-card-header {expanded_class_exist}" onclick="toggleAnalysisCard('{proceso_id}')">
                    <div class="analysis-card-header-left">
                        <div class="analysis-card-rank {rank_class_exist}">#{rank_existente}</div>
                        <div>
                            <div class="analysis-card-title">{proceso}</div>
                            <div class="analysis-card-badges">
                                <span class="analysis-card-badge contrib">📊 Contrib: {contrib_pct_exist:.1f}%</span>
                                <span class="analysis-card-badge {var_badge_class_exist}">{var_badge_text_exist}</span>
                                <span class="analysis-card-badge conv">💬 {total_conv} conv.</span>
                            </div>
                        </div>
                    </div>
                    <div class="analysis-card-toggle">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="#555">
                            <path d="M4 6l4 4 4-4H4z"/>
                        </svg>
                    </div>
                </div>
                <div id="content_{proceso_id}" class="analysis-card-content {expanded_class_exist}">
                    <div class="analysis-card-content-inner">
                        <div class="metrics-row">
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p1_label}</div>
                                <div class="metric-box-value">{inc_nov:,}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p2_label}</div>
                                <div class="metric-box-value">{inc_dic:,}</div>
                            </div>
                            <div class="metric-box {'variation-positive' if var_casos < 0 else 'variation-negative'}">
                                <div class="metric-box-label">Variación</div>
                                <div class="metric-box-value">{var_casos:+,} ({var_pct:+.1f}%)</div>
                            </div>
                            <div class="metric-box contrib">
                                <div class="metric-box-label">Contrib. a Δ CR</div>
                                <div class="metric-box-value">{contrib_pct_exist:.1f}%</div>
                            </div>
                        </div>
"""
        
        # Agregar alerta si muestra insuficiente
        if muestra_insuficiente:
            html_content += f"""
                <div class="alert-box">
                    <strong>⚠️ ADVERTENCIA - Muestra Insuficiente:</strong>
                    <p>Se encontraron solo {total_conv} conversaciones (mínimo requerido: {UMBRAL_MINIMO_CONVERSACIONES}).
                        Los patrones identificados pueden no ser representativos. Recomendamos validar con datos cuantitativos.</p>
                </div>
"""
        
        # Continuar con insight principal solo si NO es muestra insuficiente
        if not muestra_insuficiente and 'analisis_comparativo' in data:
            html_content += f"""
                <div class="insight-box">
                    <strong>💡 Insight Principal:</strong>
                    <p>{data['analisis_comparativo']['insight_principal']}</p>
                </div>
                
                <table class="causa-table">
                    <thead>
                        <tr>
                            <th rowspan="2">Patrón / Causa Raíz</th>
                            <th colspan="2" class="col-periodo">{p1_label}</th>
                            <th colspan="2" class="col-periodo">{p2_label}</th>
                            <th rowspan="2">Var Casos</th>
                            <th rowspan="2">Var %</th>
                            <th rowspan="2">Δ Prop</th>
                            <th rowspan="2">Contrib Δ</th>
                            <th rowspan="2">Contrib CR</th>
                        </tr>
                        <tr>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Crear diccionario para mapear causas entre períodos
        causas_dict = {}
        
        for causa_nov in data['causas_nov']:
            causas_dict[causa_nov['causa']] = {
                'nov_pct': causa_nov['porcentaje'],
                'nov_casos': causa_nov['casos_estimados'],
                'dic_pct': 0,
                'dic_casos': 0,
                'causa_data_nov': causa_nov  # Guardar data completa
            }
        
        for causa_dic in data['causas_dic']:
            if causa_dic['causa'] in causas_dict:
                causas_dict[causa_dic['causa']]['dic_pct'] = causa_dic['porcentaje']
                causas_dict[causa_dic['causa']]['dic_casos'] = causa_dic['casos_estimados']
                causas_dict[causa_dic['causa']]['causa_data_dic'] = causa_dic
            else:
                causas_dict[causa_dic['causa']] = {
                    'nov_pct': 0,
                    'nov_casos': 0,
                    'dic_pct': causa_dic['porcentaje'],
                    'dic_casos': causa_dic['casos_estimados'],
                    'causa_data_dic': causa_dic
                }
        
        # v6.4.5: Ordenar por % de aparición en P2 (período más reciente) - mayor participación primero
        causas_sorted = sorted(causas_dict.items(), key=lambda x: x[1]['dic_pct'], reverse=True)
        
        # v6.4.7: Calcular suma de casos muestreados (no incoming total)
        sum_casos_nov = sum(v['nov_casos'] for _, v in causas_sorted)
        sum_casos_dic = sum(v['dic_casos'] for _, v in causas_sorted)
        var_total_muestra = sum_casos_dic - sum_casos_nov  # v6.4.8: Para calcular contribuciones
        
        for causa_nombre, valores in causas_sorted:
            var_abs = valores['dic_casos'] - valores['nov_casos']
            var_pct_causa = ((valores['dic_casos'] - valores['nov_casos']) / valores['nov_casos'] * 100) if valores['nov_casos'] > 0 else (100 if valores['dic_casos'] > 0 else 0)
            cambio_prop = valores['dic_pct'] - valores['nov_pct']
            
            # v6.4.8: Calcular contribuciones
            contrib_delta = (var_abs / var_total_muestra * 100) if var_total_muestra != 0 else 0
            contrib_cr_global = contrib_delta * contrib_pct_exist / 100 if contrib_pct_exist else 0
            
            # Determinar clase CSS y color
            if var_abs < 0:
                clase_var = "positive"
                color_var = "#00A650"
            elif var_abs > 0:
                clase_var = "negative"
                color_var = "#E74C3C"
            else:
                clase_var = ""
                color_var = "#666"
            
            signo_abs = "" if var_abs < 0 else "+"
            signo_prop = "" if cambio_prop < 0 else "+"
            
            html_content += f"""
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px; font-weight: 600; color: #2c3e50; border: 1px solid #ddd;">{causa_nombre}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_abs}{var_abs:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{var_pct_causa:+.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_prop}{cambio_prop:+.0f} pp</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; border: 1px solid #ddd;">{contrib_delta:.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_cr_global:.1f}%</td>
                        </tr>
"""
        
        # Fila de totales (v6.4.7: usar suma de casos muestreados)
        var_casos_muestra = sum_casos_dic - sum_casos_nov
        var_pct_muestra = ((sum_casos_dic - sum_casos_nov) / sum_casos_nov * 100) if sum_casos_nov > 0 else 0
        html_content += f"""
                        <tr style="background: #f0f0f0; font-weight: bold; border-top: 2px solid #2c3e50;">
                            <td style="padding: 12px; border: 1px solid #ddd;">TOTAL</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_nov:,}</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_dic:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_casos_muestra:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_pct_muestra:.1f}%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">-</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd;">100.0%</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_pct_exist:.1f}%</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="margin-top: 20px;">
                    <h4 style="color: #2c3e50; margin-bottom: 12px; font-size: 16px;">📌 Evidencia Cualitativa con Citas</h4>
"""
        
        # Mostrar evidencia de las TOP causas (ordenadas por impacto)
        causas_con_evidencia = []
        for causa_nombre, valores in causas_sorted[:4]:  # Top 4 causas por impacto
            # Buscar la causa en nov o dic para obtener citas
            causa_data = valores.get('causa_data_nov') or valores.get('causa_data_dic')
            if causa_data and 'citas' in causa_data and len(causa_data['citas']) > 0:
                causas_con_evidencia.append((causa_nombre, causa_data, valores))
        
        # Mostrar primera cita de las top 2 causas
        for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[:2]):
            cita = causa_data['citas'][0]
            fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
            
            html_content += f"""
                    <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #3498db; border-radius: 5px;">
                        <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                        <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                        <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                            <span style="color: #3498db; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                            {cita['texto']}
                        </div>
                    </div>
"""
        
        # Toggle para ver más citas
        if len(causas_con_evidencia) > 2:
            html_content += f"""
                    <button id="btn_{proceso_id}" onclick="toggleCitas('{proceso_id}')" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 15px 0; font-size: 13px;">
                        Ver citas adicionales ▼
                    </button>
                    
                    <div id="citas_{proceso_id}" style="display: none; margin-top: 15px;">
"""
            
            # Mostrar citas adicionales (causa 3, 4 y más citas de las top)
            for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[2:], start=3):
                for cita in causa_data.get('citas', [])[:2]:  # Máx 2 citas por causa adicional
                    fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
                    html_content += f"""
                        <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #95a5a6; border-radius: 5px;">
                            <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                            <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                            <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                                <span style="color: #95a5a6; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                                {cita['texto']}
                            </div>
                        </div>
"""
            
            html_content += """
                    </div>
"""
        
        # Cerrar la card colapsable: analysis-card-content-inner, analysis-card-content, analysis-card
        html_content += """
                    </div>
                </div>
            </div>
"""
    
    html_content += """
        </div>
"""
    
    print(f"[COMPARATIVO] Análisis comparativo con cards colapsables cargado (v6.4.0)")
else:
    # ========================================
    # GENERAR ANÁLISIS COMPARATIVO AUTOMÁTICAMENTE (v6.3.8 / v6.4.10)
    # ========================================
    print(f"\n[COMPARATIVO] Generando análisis comparativo fresco desde JSONs separados (v6.4.10)...")
    
    # Verificar si existen análisis separados por período (v6.3.8)
    json_p1_path = Path("output") / f"analisis_conversaciones_claude_{args.site.lower()}_{args.commerce_group.lower()}_{args.muestreo_dimension.lower()}_p1_{p1_mes}.json"
    json_p2_path = Path("output") / f"analisis_conversaciones_claude_{args.site.lower()}_{args.commerce_group.lower()}_{args.muestreo_dimension.lower()}_p2_{p2_mes}.json"
    
    # Fallback: verificar análisis básico conjunto (legacy)
    json_basico_path = Path("output") / f"analisis_conversaciones_claude_{args.site.lower()}_{args.commerce_group.lower()}_{args.muestreo_dimension.lower()}_{p1_mes}_{p2_mes}.json"
    
    # Cuadro de dimensión (necesario en ambos casos)
    cuadro_dimension_path = Path("output") / f"cuadro_{args.muestreo_dimension.lower()}_{args.site.lower()}_{p1_start_dt.strftime('%Y%m')}.csv"
    
    # PRIORIDAD 1: Usar análisis separados si existen (v6.3.8 - Detección de cambios reales)
    if json_p1_path.exists() and json_p2_path.exists() and cuadro_dimension_path.exists() and len(conversaciones_por_proceso) > 0:
        try:
            import sys
            from pathlib import Path
            
            scripts_dir = Path(__file__).parent / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            
            from generar_analisis_comparativo_desde_separados import generar_comparativo
            
            periodo_p1_str = f"{p1_start_dt.year}-{p1_start_dt.month:02d}"
            periodo_p2_str = f"{p2_start_dt.year}-{p2_start_dt.month:02d}"
            
            print(f"[AUTO-GEN] Usando análisis separados (v6.3.8 - detección de cambios de patrones)")
            
            # Generar análisis comparativo desde análisis separados
            analisis_comp = generar_comparativo(
                json_p1_path,
                json_p2_path,
                cuadro_dimension_path,
                periodo_p1_str,
                periodo_p2_str
            )
            
            # Guardar JSON comparativo
            with open(analisis_comparativo_path, 'w', encoding='utf-8') as f:
                json.dump(analisis_comp, f, indent=2, ensure_ascii=False)
            
            print(f"[AUTO-GEN] ✅ Análisis comparativo generado: {len(analisis_comp)} elementos")
            print(f"[AUTO-GEN] Guardado en: {analisis_comparativo_path.name}")
            print(f"[INFO] Porcentajes dinámicos por período (detecta cambios reales de patrones)")
            
            # Ahora agregar al HTML con cards colapsables ordenadas por contribución (v6.4.0)
            
            # Obtener orden por contribución desde el cuadro de dimensión
            df_orden = None
            if cuadro_dimension_path.exists():
                try:
                    df_orden = pd.read_csv(cuadro_dimension_path)
                    # Excluir "Otros" y "TOTAL" del ordenamiento
                    df_orden = df_orden[~df_orden['DIMENSION_VAL'].str.contains('Otros|TOTAL', case=False, na=False)]
                    # Ordenar por |VAR_CR| descendente (mayor impacto en CR primero) - v6.4.9
                    df_orden = df_orden.sort_values('VAR_CR', key=lambda x: abs(x), ascending=False)
                    orden_contribucion = df_orden['DIMENSION_VAL'].tolist()
                except Exception as e:
                    print(f"[WARNING] No se pudo leer orden de contribución: {e}")
                    orden_contribucion = list(analisis_comp.keys())
            else:
                orden_contribucion = list(analisis_comp.keys())
            
            # Determinar qué dimensión se está analizando
            dimension_label = aperturas_list[-1] if aperturas_list else "Elemento"  # La última apertura es la más granular
            
            html_content += f"""
        <!-- ANÁLISIS COMPARATIVO DE PATRONES EN CARDS COLAPSABLES - v6.4.0 -->
        <div class="section">
            <h2>🔍 Análisis Comparativo por {dimension_label}</h2>
            <p style="margin-bottom: 20px; font-size: 15px; color: #555;">
                Cada card representa un elemento de <strong>{dimension_label}</strong>, ordenado por su <strong>contribución a la variación de CR</strong> (de mayor a menor impacto).
                Haz clic en cada card para expandir el análisis detallado con causas raíz y evidencia cualitativa.
            </p>
        
        <script>
            function toggleAnalysisCard(cardId) {{
                var header = document.getElementById('header_' + cardId);
                var content = document.getElementById('content_' + cardId);
                var isExpanded = header.classList.contains('expanded');
                
                if (isExpanded) {{
                    header.classList.remove('expanded');
                    content.classList.remove('expanded');
                }} else {{
                    header.classList.add('expanded');
                    content.classList.add('expanded');
                }}
            }}
            
            function toggleCitas(procesoid) {{
                var elem = document.getElementById('citas_' + procesoid);
                var btn = document.getElementById('btn_' + procesoid);
                if (elem.style.display === 'none') {{
                    elem.style.display = 'block';
                    btn.innerHTML = 'Ocultar citas adicionales ▲';
                }} else {{
                    elem.style.display = 'none';
                    btn.innerHTML = 'Ver citas adicionales ▼';
                }}
            }}
            
            function expandAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.add('expanded'); }});
                contents.forEach(function(c) {{ c.classList.add('expanded'); }});
            }}
            
            function collapseAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.remove('expanded'); }});
                contents.forEach(function(c) {{ c.classList.remove('expanded'); }});
            }}
        </script>
        
        <div style="margin-bottom: 20px; display: flex; gap: 10px;">
            <button onclick="expandAllCards()" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📂 Expandir todas
            </button>
            <button onclick="collapseAllCards()" style="background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📁 Colapsar todas
            </button>
        </div>
"""
            
            # Iterar por cada elemento en orden de contribución
            rank = 0
            for proceso_key in orden_contribucion:
                if proceso_key not in analisis_comp:
                    continue
                data = analisis_comp[proceso_key]
                if data['conversaciones_nov'] == 0 and data['conversaciones_dic'] == 0:
                    continue
                
                rank += 1
                proceso = data['proceso']
                proceso_id = proceso.replace(' ', '_').replace('-', '_').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                inc_nov = data['incoming_nov']
                inc_dic = data['incoming_dic']
                var_casos = data['variacion_casos']
                var_pct = data['variacion_pct']
                total_conv = data['conversaciones_nov'] + data['conversaciones_dic']
                
                # Obtener datos de contribución del cuadro
                contrib_pct = 0
                var_cr_pp = 0
                if df_orden is not None and len(df_orden) > 0:
                    row = df_orden[df_orden['DIMENSION_VAL'] == proceso_key]
                    if len(row) > 0:
                        contrib_pct = row['CONTRIB_ABS'].values[0] if pd.notna(row['CONTRIB_ABS'].values[0]) else 0
                        var_cr_pp = row['VAR_CR'].values[0] * 100 if pd.notna(row['VAR_CR'].values[0]) else 0  # Convertir a pp
                
                # Verificar si hay muestra insuficiente
                muestra_insuficiente = total_conv < UMBRAL_MINIMO_CONVERSACIONES
                
                # Calcular cobertura promedio
                cobertura_nov = data['causas_nov'][0].get('porcentaje', 0) if len(data['causas_nov']) > 0 else 0
                cobertura_total = sum([c['porcentaje'] for c in data['causas_nov'][:4]]) if len(data['causas_nov']) > 0 else 100
                
                # Determinar si es top 3 y estado expandido (solo el primero expandido por defecto)
                is_top_3 = rank <= 3
                is_expanded = rank == 1  # Solo el primero expandido
                expanded_class = "expanded" if is_expanded else ""
                rank_class = "top-3" if is_top_3 else ""
                
                # Badge de variación
                if var_casos < 0:
                    var_badge_class = "positive"
                    var_badge_text = f"✅ {var_casos:,} casos"
                else:
                    var_badge_class = "negative"
                    var_badge_text = f"🔴 +{var_casos:,} casos"
                
                html_content += f"""
            <!-- CARD #{rank}: {proceso} -->
            <div class="analysis-card">
                <div id="header_{proceso_id}" class="analysis-card-header {expanded_class}" onclick="toggleAnalysisCard('{proceso_id}')">
                    <div class="analysis-card-header-left">
                        <div class="analysis-card-rank {rank_class}">#{rank}</div>
                        <div>
                            <div class="analysis-card-title">{proceso}</div>
                            <div class="analysis-card-badges">
                                <span class="analysis-card-badge contrib">📊 Contrib: {contrib_pct:.1f}%</span>
                                <span class="analysis-card-badge {var_badge_class}">{var_badge_text}</span>
                                <span class="analysis-card-badge conv">💬 {total_conv} conv.</span>
                            </div>
                        </div>
                    </div>
                    <div class="analysis-card-toggle">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="#555">
                            <path d="M4 6l4 4 4-4H4z"/>
                        </svg>
                    </div>
                </div>
                <div id="content_{proceso_id}" class="analysis-card-content {expanded_class}">
                    <div class="analysis-card-content-inner">
                        <div class="metrics-row">
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p1_label}</div>
                                <div class="metric-box-value">{inc_nov:,}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p2_label}</div>
                                <div class="metric-box-value">{inc_dic:,}</div>
                            </div>
                            <div class="metric-box {'variation-positive' if var_casos < 0 else 'variation-negative'}">
                                <div class="metric-box-label">Variación</div>
                                <div class="metric-box-value">{var_casos:+,} ({var_pct:+.1f}%)</div>
                            </div>
                            <div class="metric-box contrib">
                                <div class="metric-box-label">Contrib. a Δ CR</div>
                                <div class="metric-box-value">{contrib_pct:.1f}%</div>
                            </div>
                        </div>
"""
                
                # Agregar alerta si muestra insuficiente
                if muestra_insuficiente:
                    html_content += f"""
                <div class="alert-box">
                    <strong>⚠️ ADVERTENCIA - Muestra Insuficiente:</strong>
                    <p>Se encontraron solo {total_conv} conversaciones (mínimo requerido: {UMBRAL_MINIMO_CONVERSACIONES}).
                        Los patrones identificados pueden no ser representativos. Recomendamos validar con datos cuantitativos.</p>
                </div>
"""
                
                # Continuar con insight principal solo si NO es muestra insuficiente
                if not muestra_insuficiente and 'analisis_comparativo' in data:
                    html_content += f"""
                <div class="insight-box">
                    <strong>💡 Insight Principal:</strong>
                    <p>{data['analisis_comparativo']['insight_principal']}</p>
                </div>
"""
                
                # Generar tabla comparativa
                html_content += f"""
                <table class="causa-table">
                    <thead>
                        <tr>
                            <th rowspan="2">Patrón / Causa Raíz</th>
                            <th colspan="2" class="col-periodo">{p1_label}</th>
                            <th colspan="2" class="col-periodo">{p2_label}</th>
                            <th rowspan="2">Var Casos</th>
                            <th rowspan="2">Var %</th>
                            <th rowspan="2">Δ Prop</th>
                            <th rowspan="2">Contrib Δ</th>
                            <th rowspan="2">Contrib CR</th>
                        </tr>
                        <tr>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                        </tr>
                    </thead>
                    <tbody>
"""
                
                # Crear diccionario para mapear causas entre períodos
                causas_dict = {}
                
                for causa_nov in data['causas_nov']:
                    causas_dict[causa_nov['causa']] = {
                        'nov_pct': causa_nov['porcentaje'],
                        'nov_casos': causa_nov['casos_estimados'],
                        'dic_pct': 0,
                        'dic_casos': 0,
                        'causa_data_nov': causa_nov
                    }
                
                for causa_dic in data['causas_dic']:
                    if causa_dic['causa'] in causas_dict:
                        causas_dict[causa_dic['causa']]['dic_pct'] = causa_dic['porcentaje']
                        causas_dict[causa_dic['causa']]['dic_casos'] = causa_dic['casos_estimados']
                        causas_dict[causa_dic['causa']]['causa_data_dic'] = causa_dic
                    else:
                        causas_dict[causa_dic['causa']] = {
                            'nov_pct': 0,
                            'nov_casos': 0,
                            'dic_pct': causa_dic['porcentaje'],
                            'dic_casos': causa_dic['casos_estimados'],
                            'causa_data_dic': causa_dic
                        }
                
                # v6.4.5: Ordenar por % de aparición en P2 (período más reciente) - mayor participación primero
                causas_sorted = sorted(causas_dict.items(), key=lambda x: x[1]['dic_pct'], reverse=True)
                
                # v6.4.7: Calcular suma de casos muestreados (no incoming total)
                sum_casos_nov = sum(v['nov_casos'] for _, v in causas_sorted)
                sum_casos_dic = sum(v['dic_casos'] for _, v in causas_sorted)
                var_total_muestra = sum_casos_dic - sum_casos_nov  # v6.4.8: Para calcular contribuciones
                
                for causa_nombre, valores in causas_sorted:
                    var_abs = valores['dic_casos'] - valores['nov_casos']
                    var_pct_causa = ((valores['dic_casos'] - valores['nov_casos']) / valores['nov_casos'] * 100) if valores['nov_casos'] > 0 else (100 if valores['dic_casos'] > 0 else 0)
                    cambio_prop = valores['dic_pct'] - valores['nov_pct']
                    
                    # v6.4.8: Calcular contribuciones
                    contrib_delta = (var_abs / var_total_muestra * 100) if var_total_muestra != 0 else 0
                    contrib_cr_global = contrib_delta * contrib_pct / 100 if contrib_pct else 0
                    
                    if var_abs < 0:
                        color_var = "#00A650"
                    elif var_abs > 0:
                        color_var = "#E74C3C"
                    else:
                        color_var = "#666"
                    
                    signo_abs = "" if var_abs < 0 else "+"
                    signo_prop = "" if cambio_prop < 0 else "+"
                    
                    html_content += f"""
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px; font-weight: 600; color: #2c3e50; border: 1px solid #ddd;">{causa_nombre}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_abs}{var_abs:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{var_pct_causa:+.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_prop}{cambio_prop:+.0f} pp</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; border: 1px solid #ddd;">{contrib_delta:.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_cr_global:.1f}%</td>
                        </tr>
"""
                
                # Fila totales (v6.4.7: usar suma de casos muestreados)
                var_casos_muestra = sum_casos_dic - sum_casos_nov
                var_pct_muestra = ((sum_casos_dic - sum_casos_nov) / sum_casos_nov * 100) if sum_casos_nov > 0 else 0
                html_content += f"""
                        <tr style="background: #f0f0f0; font-weight: bold; border-top: 2px solid #2c3e50;">
                            <td style="padding: 12px; border: 1px solid #ddd;">TOTAL</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_nov:,}</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_dic:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_casos_muestra:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_pct_muestra:.1f}%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">-</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd;">100.0%</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_pct:.1f}%</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="margin-top: 20px;">
                    <h4 style="color: #2c3e50; margin-bottom: 12px; font-size: 16px;">📌 Evidencia Cualitativa con Citas</h4>
"""
                
                # Evidencia con citas (top 2 causas visibles)
                causas_con_evidencia = []
                for causa_nombre, valores in causas_sorted[:4]:
                    causa_data = valores.get('causa_data_nov') or valores.get('causa_data_dic')
                    if causa_data and 'citas' in causa_data and len(causa_data['citas']) > 0:
                        causas_con_evidencia.append((causa_nombre, causa_data, valores))
                
                for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[:2]):
                    cita = causa_data['citas'][0]
                    fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
                    
                    html_content += f"""
                    <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #3498db; border-radius: 5px;">
                        <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                        <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                        <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                            <span style="color: #3498db; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                            {cita['texto']}
                        </div>
                    </div>
"""
                
                if len(causas_con_evidencia) > 2:
                    html_content += f"""
                    <button id="btn_{proceso_id}" onclick="toggleCitas('{proceso_id}')" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 15px 0; font-size: 13px;">
                        Ver citas adicionales ▼
                    </button>
                    <div id="citas_{proceso_id}" style="display: none; margin-top: 15px;">
"""
                    for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[2:], start=3):
                        for cita in causa_data.get('citas', [])[:2]:
                            fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
                            html_content += f"""
                        <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #95a5a6; border-radius: 5px;">
                            <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                            <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                            <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                                <span style="color: #95a5a6; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                                {cita['texto']}
                            </div>
                        </div>
"""
                    html_content += """
                    </div>
"""
                
                # Cerrar la card colapsable: analysis-card-content-inner, analysis-card-content, analysis-card
                html_content += """
                    </div>
                </div>
            </div>
"""
            
            html_content += """
        </div>
"""
            
            print(f"[COMPARATIVO] Análisis comparativo con cards colapsables agregado al reporte (v6.4.0)")
            
        except Exception as e:
            print(f"[ERROR] No se pudo generar análisis comparativo automáticamente: {e}")
            print(f"[INFO] Continuando sin análisis comparativo")
    
    # FALLBACK: Usar análisis básico conjunto (legacy - asume patrones constantes)
    elif json_basico_path.exists() and cuadro_dimension_path.exists() and len(conversaciones_por_proceso) > 0:
        try:
            import sys
            from pathlib import Path
            
            scripts_dir = Path(__file__).parent / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            
            from generar_analisis_comparativo_auto import generar_analisis_comparativo
            
            periodo_p1_str = f"{p1_start_dt.year}-{p1_start_dt.month:02d}"
            periodo_p2_str = f"{p2_start_dt.year}-{p2_start_dt.month:02d}"
            
            print(f"[AUTO-GEN] Usando análisis conjunto (legacy - sin detección de cambios de patrones)")
            print(f"[WARNING] Para análisis mejorado, usa análisis separado por período (v6.3.8+)")
            
            # Generar análisis comparativo desde análisis conjunto
            analisis_comp = generar_analisis_comparativo(
                json_basico_path,
                cuadro_dimension_path,
                Path("output"),
                periodo_p1_str,
                periodo_p2_str
            )
            
            # Guardar JSON comparativo
            with open(analisis_comparativo_path, 'w', encoding='utf-8') as f:
                json.dump(analisis_comp, f, indent=2, ensure_ascii=False)
            
            print(f"[AUTO-GEN] ⚠️  Análisis comparativo generado: {len(analisis_comp)} elementos")
            print(f"[AUTO-GEN] Guardado en: {analisis_comparativo_path.name}")
            
            # Obtener orden por contribución desde el cuadro de dimensión (v6.4.0 legacy)
            df_orden_legacy = None
            if cuadro_dimension_path.exists():
                try:
                    df_orden_legacy = pd.read_csv(cuadro_dimension_path)
                    df_orden_legacy = df_orden_legacy[~df_orden_legacy['DIMENSION_VAL'].str.contains('Otros|TOTAL', case=False, na=False)]
                    # Ordenar por |VAR_CR| descendente (mayor impacto en CR primero) - v6.4.9
                    df_orden_legacy = df_orden_legacy.sort_values('VAR_CR', key=lambda x: abs(x), ascending=False)
                    orden_contribucion_legacy = df_orden_legacy['DIMENSION_VAL'].tolist()
                except:
                    orden_contribucion_legacy = list(analisis_comp.keys())
            else:
                orden_contribucion_legacy = list(analisis_comp.keys())
            
            dimension_label_legacy = aperturas_list[-1] if aperturas_list else "Elemento"
            
            # Ahora agregar al HTML con cards colapsables (v6.4.0)
            html_content += f"""
        <!-- ANÁLISIS COMPARATIVO CON CARDS COLAPSABLES - v6.4.0 LEGACY -->
        <div class="section">
            <h2>🔍 Análisis Comparativo por {dimension_label_legacy}</h2>
            <p style="margin-bottom: 20px; font-size: 15px; color: #555;">
                Cada card representa un elemento de <strong>{dimension_label_legacy}</strong>, ordenado por su <strong>contribución a la variación de CR</strong>.
                Haz clic para expandir el análisis detallado.
            </p>
        
        <script>
            function toggleAnalysisCard(cardId) {{
                var header = document.getElementById('header_' + cardId);
                var content = document.getElementById('content_' + cardId);
                var isExpanded = header.classList.contains('expanded');
                
                if (isExpanded) {{
                    header.classList.remove('expanded');
                    content.classList.remove('expanded');
                }} else {{
                    header.classList.add('expanded');
                    content.classList.add('expanded');
                }}
            }}
            
            function toggleCitas(procesoid) {{
                var elem = document.getElementById('citas_' + procesoid);
                var btn = document.getElementById('btn_' + procesoid);
                if (elem.style.display === 'none') {{
                    elem.style.display = 'block';
                    btn.innerHTML = 'Ocultar citas adicionales ▲';
                }} else {{
                    elem.style.display = 'none';
                    btn.innerHTML = 'Ver citas adicionales ▼';
                }}
            }}
            
            function expandAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.add('expanded'); }});
                contents.forEach(function(c) {{ c.classList.add('expanded'); }});
            }}
            
            function collapseAllCards() {{
                var headers = document.querySelectorAll('.analysis-card-header');
                var contents = document.querySelectorAll('.analysis-card-content');
                headers.forEach(function(h) {{ h.classList.remove('expanded'); }});
                contents.forEach(function(c) {{ c.classList.remove('expanded'); }});
            }}
        </script>
        
        <div style="margin-bottom: 20px; display: flex; gap: 10px;">
            <button onclick="expandAllCards()" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📂 Expandir todas
            </button>
            <button onclick="collapseAllCards()" style="background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: 600;">
                📁 Colapsar todas
            </button>
        </div>
"""
            
            # Iterar por cada elemento en orden de contribución (v6.4.0)
            rank_legacy = 0
            for proceso_key in orden_contribucion_legacy:
                if proceso_key not in analisis_comp:
                    continue
                data = analisis_comp[proceso_key]
                if data['conversaciones_nov'] == 0 and data['conversaciones_dic'] == 0:
                    continue
                
                rank_legacy += 1
                proceso = data['proceso']
                proceso_id = proceso.replace(' ', '_').replace('-', '_').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                inc_nov = data['incoming_nov']
                inc_dic = data['incoming_dic']
                var_casos = data['variacion_casos']
                var_pct = data['variacion_pct']
                total_conv = data['conversaciones_nov'] + data['conversaciones_dic']
                
                # Obtener datos de contribución
                contrib_pct_legacy = 0
                if df_orden_legacy is not None and len(df_orden_legacy) > 0:
                    row = df_orden_legacy[df_orden_legacy['DIMENSION_VAL'] == proceso_key]
                    if len(row) > 0:
                        contrib_pct_legacy = row['CONTRIB_ABS'].values[0] if pd.notna(row['CONTRIB_ABS'].values[0]) else 0
                
                # Verificar si hay muestra insuficiente
                muestra_insuficiente = total_conv < UMBRAL_MINIMO_CONVERSACIONES
                
                # Calcular cobertura promedio
                cobertura_nov = data['causas_nov'][0].get('porcentaje', 0) if len(data['causas_nov']) > 0 else 0
                cobertura_total = sum([c['porcentaje'] for c in data['causas_nov'][:4]]) if len(data['causas_nov']) > 0 else 100
                
                is_top_3_legacy = rank_legacy <= 3
                is_expanded_legacy = rank_legacy == 1
                expanded_class_legacy = "expanded" if is_expanded_legacy else ""
                rank_class_legacy = "top-3" if is_top_3_legacy else ""
                
                if var_casos < 0:
                    var_badge_class_legacy = "positive"
                    var_badge_text_legacy = f"✅ {var_casos:,} casos"
                else:
                    var_badge_class_legacy = "negative"
                    var_badge_text_legacy = f"🔴 +{var_casos:,} casos"
                
                html_content += f"""
            <!-- CARD #{rank_legacy}: {proceso} (LEGACY) -->
            <div class="analysis-card">
                <div id="header_{proceso_id}" class="analysis-card-header {expanded_class_legacy}" onclick="toggleAnalysisCard('{proceso_id}')">
                    <div class="analysis-card-header-left">
                        <div class="analysis-card-rank {rank_class_legacy}">#{rank_legacy}</div>
                        <div>
                            <div class="analysis-card-title">{proceso}</div>
                            <div class="analysis-card-badges">
                                <span class="analysis-card-badge contrib">📊 Contrib: {contrib_pct_legacy:.1f}%</span>
                                <span class="analysis-card-badge {var_badge_class_legacy}">{var_badge_text_legacy}</span>
                                <span class="analysis-card-badge conv">💬 {total_conv} conv.</span>
                            </div>
                        </div>
                    </div>
                    <div class="analysis-card-toggle">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="#555">
                            <path d="M4 6l4 4 4-4H4z"/>
                        </svg>
                    </div>
                </div>
                <div id="content_{proceso_id}" class="analysis-card-content {expanded_class_legacy}">
                    <div class="analysis-card-content-inner">
                        <div class="metrics-row">
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p1_label}</div>
                                <div class="metric-box-value">{inc_nov:,}</div>
                            </div>
                            <div class="metric-box">
                                <div class="metric-box-label">Incoming {p2_label}</div>
                                <div class="metric-box-value">{inc_dic:,}</div>
                            </div>
                            <div class="metric-box {'variation-positive' if var_casos < 0 else 'variation-negative'}">
                                <div class="metric-box-label">Variación</div>
                                <div class="metric-box-value">{var_casos:+,} ({var_pct:+.1f}%)</div>
                            </div>
                            <div class="metric-box contrib">
                                <div class="metric-box-label">Contrib. a Δ CR</div>
                                <div class="metric-box-value">{contrib_pct_legacy:.1f}%</div>
                            </div>
                        </div>
"""
                
                # Agregar alerta si muestra insuficiente
                if muestra_insuficiente:
                    html_content += f"""
                <div class="alert-box">
                    <strong>⚠️ ADVERTENCIA - Muestra Insuficiente:</strong>
                    <p>Se encontraron solo {total_conv} conversaciones (mínimo requerido: {UMBRAL_MINIMO_CONVERSACIONES}).
                        Los patrones identificados pueden no ser representativos. Recomendamos validar con datos cuantitativos.</p>
                </div>
"""
                
                # Continuar con insight principal solo si NO es muestra insuficiente
                if not muestra_insuficiente and 'analisis_comparativo' in data:
                    html_content += f"""
                <div class="insight-box">
                    <strong>💡 Insight Principal:</strong>
                    <p>{data['analisis_comparativo']['insight_principal']}</p>
                </div>
"""
                
                # Generar tabla comparativa (mismo código que líneas 1534-1678)
                html_content += f"""
                <table class="causa-table">
                    <thead>
                        <tr>
                            <th rowspan="2">Patrón / Causa Raíz</th>
                            <th colspan="2" class="col-periodo">{p1_label}</th>
                            <th colspan="2" class="col-periodo">{p2_label}</th>
                            <th rowspan="2">Var Casos</th>
                            <th rowspan="2">Var %</th>
                            <th rowspan="2">Δ Prop</th>
                            <th rowspan="2">Contrib Δ</th>
                            <th rowspan="2">Contrib CR</th>
                        </tr>
                        <tr>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                            <th class="col-subheader">%</th>
                            <th class="col-subheader">Casos</th>
                        </tr>
                    </thead>
                    <tbody>
"""
                
                # Crear diccionario para mapear causas entre períodos
                causas_dict = {}
                
                for causa_nov in data['causas_nov']:
                    causas_dict[causa_nov['causa']] = {
                        'nov_pct': causa_nov['porcentaje'],
                        'nov_casos': causa_nov['casos_estimados'],
                        'dic_pct': 0,
                        'dic_casos': 0,
                        'causa_data_nov': causa_nov
                    }
                
                for causa_dic in data['causas_dic']:
                    if causa_dic['causa'] in causas_dict:
                        causas_dict[causa_dic['causa']]['dic_pct'] = causa_dic['porcentaje']
                        causas_dict[causa_dic['causa']]['dic_casos'] = causa_dic['casos_estimados']
                        causas_dict[causa_dic['causa']]['causa_data_dic'] = causa_dic
                    else:
                        causas_dict[causa_dic['causa']] = {
                            'nov_pct': 0,
                            'nov_casos': 0,
                            'dic_pct': causa_dic['porcentaje'],
                            'dic_casos': causa_dic['casos_estimados'],
                            'causa_data_dic': causa_dic
                        }
                
                # v6.4.5: Ordenar por % de aparición en P2 (período más reciente) - mayor participación primero
                causas_sorted = sorted(causas_dict.items(), key=lambda x: x[1]['dic_pct'], reverse=True)
                
                # v6.4.7: Calcular suma de casos muestreados (no incoming total)
                sum_casos_nov = sum(v['nov_casos'] for _, v in causas_sorted)
                sum_casos_dic = sum(v['dic_casos'] for _, v in causas_sorted)
                var_total_muestra = sum_casos_dic - sum_casos_nov  # v6.4.8: Para calcular contribuciones
                
                for causa_nombre, valores in causas_sorted:
                    var_abs = valores['dic_casos'] - valores['nov_casos']
                    var_pct_causa = ((valores['dic_casos'] - valores['nov_casos']) / valores['nov_casos'] * 100) if valores['nov_casos'] > 0 else (100 if valores['dic_casos'] > 0 else 0)
                    cambio_prop = valores['dic_pct'] - valores['nov_pct']
                    
                    # v6.4.8: Calcular contribuciones
                    contrib_delta = (var_abs / var_total_muestra * 100) if var_total_muestra != 0 else 0
                    contrib_cr_global = contrib_delta * contrib_pct_legacy / 100 if contrib_pct_legacy else 0
                    
                    if var_abs < 0:
                        color_var = "#00A650"
                    elif var_abs > 0:
                        color_var = "#E74C3C"
                    else:
                        color_var = "#666"
                    
                    signo_abs = "" if var_abs < 0 else "+"
                    signo_prop = "" if cambio_prop < 0 else "+"
                    
                    html_content += f"""
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 10px; font-weight: 600; color: #2c3e50; border: 1px solid #ddd;">{causa_nombre}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['nov_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_pct']}%</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{valores['dic_casos']:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_abs}{var_abs:,}</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{var_pct_causa:+.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: bold; color: {color_var}; border: 1px solid #ddd;">{signo_prop}{cambio_prop:+.0f} pp</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; border: 1px solid #ddd;">{contrib_delta:.1f}%</td>
                            <td style="padding: 10px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_cr_global:.1f}%</td>
                        </tr>
"""
                
                # Fila totales (v6.4.7: usar suma de casos muestreados)
                var_casos_muestra = sum_casos_dic - sum_casos_nov
                var_pct_muestra = ((sum_casos_dic - sum_casos_nov) / sum_casos_nov * 100) if sum_casos_nov > 0 else 0
                html_content += f"""
                        <tr style="background: #f0f0f0; font-weight: bold; border-top: 2px solid #2c3e50;">
                            <td style="padding: 12px; border: 1px solid #ddd;">TOTAL</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_nov:,}</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">100%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sum_casos_dic:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_casos_muestra:,}</td>
                            <td style="padding: 12px; text-align: center; font-weight: bold; color: #00A650; border: 1px solid #ddd;">{var_pct_muestra:.1f}%</td>
                            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">-</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd;">100.0%</td>
                            <td style="padding: 12px; text-align: center; font-weight: 600; color: #3483FA; border: 1px solid #ddd;">{contrib_pct_legacy:.1f}%</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="margin-top: 20px;">
                    <h4 style="color: #2c3e50; margin-bottom: 12px; font-size: 16px;">📌 Evidencia Cualitativa con Citas</h4>
"""
                
                # Evidencia con citas (top 2 causas visibles)
                causas_con_evidencia = []
                for causa_nombre, valores in causas_sorted[:4]:
                    causa_data = valores.get('causa_data_nov') or valores.get('causa_data_dic')
                    if causa_data and 'citas' in causa_data and len(causa_data['citas']) > 0:
                        causas_con_evidencia.append((causa_nombre, causa_data, valores))
                
                for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[:2]):
                    cita = causa_data['citas'][0]
                    fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
                    
                    html_content += f"""
                    <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #3498db; border-radius: 5px;">
                        <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                        <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                        <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                            <span style="color: #3498db; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                            {cita['texto']}
                        </div>
                    </div>
"""
                
                if len(causas_con_evidencia) > 2:
                    html_content += f"""
                    <button id="btn_{proceso_id}" onclick="toggleCitas('{proceso_id}')" style="background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 15px 0; font-size: 13px;">
                        Ver citas adicionales ▼
                    </button>
                    <div id="citas_{proceso_id}" style="display: none; margin-top: 15px;">
"""
                    for i, (causa_nombre, causa_data, valores) in enumerate(causas_con_evidencia[2:], start=3):
                        for cita in causa_data.get('citas', [])[:2]:
                            fecha_str = f" ({cita['fecha']})" if 'fecha' in cita else ""
                            html_content += f"""
                        <div style="background: white; padding: 15px; margin: 10px 0; border-left: 3px solid #95a5a6; border-radius: 5px;">
                            <strong style="color: #2c3e50; font-size: 14px;">{causa_nombre}</strong>
                            <p style="margin: 8px 0; font-size: 13px; color: #666;">{causa_data['descripcion']}</p>
                            <div style="background: #f9f9f9; padding: 10px; margin-top: 8px; border-radius: 3px; font-size: 12px; font-style: italic; color: #555;">
                                <span style="color: #95a5a6; font-weight: bold; font-style: normal;">Caso {cita['case_id']}{fecha_str}:</span> 
                                {cita['texto']}
                            </div>
                        </div>
"""
                    html_content += """
                    </div>
"""
                
                # Cerrar la card colapsable: analysis-card-content-inner, analysis-card-content, analysis-card
                html_content += """
                    </div>
                </div>
            </div>
"""
            
            html_content += """
        </div>
"""
            
            print(f"[COMPARATIVO] Análisis comparativo con cards colapsables (legacy) agregado (v6.4.0)")
            
        except Exception as e:
            # FIX #8: Control de errores robusto con información detallada
            print(f"[ERROR] No se pudo generar análisis comparativo automáticamente")
            print(f"[ERROR] Tipo: {type(e).__name__}")
            print(f"[ERROR] Detalle: {str(e)}")
            
            import traceback
            print(f"\n[DEBUG] Traceback completo:")
            traceback.print_exc()
            
            print(f"\n[INFO] Diagnóstico de archivos:")
            print(f"  OK JSON básico: {json_basico_path.name}")
            print(f"    - Existe: {'OK SI' if json_basico_path.exists() else 'X NO'}")
            if json_basico_path.exists():
                print(f"    - Tamaño: {json_basico_path.stat().st_size:,} bytes")
            
            print(f"  OK Cuadro dimensión: {cuadro_dimension_path.name}")
            print(f"    - Existe: {'OK SI' if cuadro_dimension_path.exists() else 'X NO'}")
            if cuadro_dimension_path.exists():
                print(f"    - Tamaño: {cuadro_dimension_path.stat().st_size:,} bytes")
            
            print(f"  OK Conversaciones: {len(conversaciones_por_proceso)} elementos priorizados")
            
            print(f"\n[INFO] El reporte se generará sin análisis comparativo detallado")
            print(f"[INFO] Los insights cualitativos estarán disponibles en el resumen ejecutivo")
    else:
        # Diagnóstico de por qué no se puede generar
        print(f"[INFO] No hay suficientes datos para generar análisis comparativo automático")
        print(f"[INFO] Diagnóstico:")
        print(f"  - JSON básico: {'OK existe' if json_basico_path.exists() else 'X falta'}")
        print(f"  - Cuadro dimensión: {'OK existe' if cuadro_dimension_path.exists() else 'X falta'}")
        print(f"  - Conversaciones priorizadas: {len(conversaciones_por_proceso)} elementos")
        print(f"[INFO] El reporte se generará con el análisis básico en el resumen ejecutivo")

# ========================================
# SECCIÓN "ANÁLISIS DE CONVERSACIONES" ELIMINADA (v6.3.2)
# ========================================
# La información cualitativa ahora está integrada en "Análisis Comparativo de Patrones"
# que incluye: sentimiento, citas con fechas, cobertura y comparación temporal

# ========================================
# FOOTER COLAPSABLE
# ========================================

html_content += """
        
        <!-- FOOTER COLAPSABLE -->
        <div class="footer-container">
            <button class="footer-toggle" onclick="toggleFooter()">
                📋 Metadata Técnica del Reporte v6.3.7
            </button>
            <div class="footer-content" id="footerContent">
                <div class="footer">
                    <h4>Configuración del Análisis</h4>
                    <ul style="list-style: none; padding-left: 0;">
                        <li>▸ Site: """ + args.site + """</li>
                        <li>▸ Commerce Group: """ + args.commerce_group + """</li>""" + (f"""
                        <li>▸ Proceso específico: {args.process_name}</li>""" if args.process_name else "") + """
                        <li>▸ Período 1: """ + args.p1_start + """ a """ + args.p1_end + """</li>
                        <li>▸ Período 2: """ + args.p2_start + """ a """ + args.p2_end + """</li>
                        <li>▸ Aperturas: """ + ', '.join(aperturas_list) + """</li>
                        <li>▸ Análisis conversaciones: """ + ('OK Claude (Cursor AI)' if USE_CLAUDE_ANALYSIS else 'X Manual (ver CSVs)') + """</li>
                    </ul>
                    <h4 style="margin-top: 20px;">Métricas</h4>
                    <ul style="list-style: none; padding-left: 0;">
                        <li>▸ Fórmula CR: (Incoming / Driver) × 100</li>
                        <li>▸ Driver: """ + driver_desc + """</li>
                        <li>▸ Regla 80%: Aplicada en todas las dimensiones</li>
                        <li>▸ Muestreo v6.4.9 Por CONTRIB_ABS: Máx """ + str(MAX_TOTAL_CONVERSATIONS) + """ conversaciones distribuidas por contribución % a variación de CR (mín 20/elemento-período, 70% picos + 30% normales)</li>
                        <li>▸ Eventos Comerciales v6.4.2: """ + (f'OK {eventos_fuente} ({len(eventos_comerciales)} eventos, {total_casos_correlacionados:,} casos correlacionados)' if len(eventos_comerciales) > 0 else 'NO Sin datos disponibles') + """</li>
"""

if len(conversaciones_por_proceso) > 0 and USE_CLAUDE_ANALYSIS:
    total_conv_analizadas = sum(d.get('analisis_llm', {}).get('total_conversaciones', 0) for d in conversaciones_por_proceso.values())
    html_content += f"""
                        <li>▸ Conversaciones analizadas: {total_conv_analizadas} casos (umbral mínimo validez: {UMBRAL_MINIMO_CONVERSACIONES_POR_ELEMENTO_PERIODO} por elemento-período)</li>
"""

if len(eventos_comerciales) > 0:
    # Listar eventos identificados
    eventos_nombres = ', '.join([e['nombre'] for e in list(eventos_comerciales.values())[:5]])
    html_content += f"""
                        <li>▸ Eventos identificados: {eventos_nombres}</li>
"""

html_content += """
                    </ul>
                    <h4 style="margin-top: 20px;">Queries Ejecutadas</h4>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px;">
"""

# Agregar cada query ejecutada
for idx, query_info in enumerate(queries_ejecutadas, 1):
    html_content += f"""
                        <div style="margin-bottom: 15px; padding: 12px; background: white; border-left: 4px solid #00a650; border-radius: 4px;">
                            <div style="font-weight: 700; color: #2c3e50; margin-bottom: 5px;">
                                {idx}. {query_info['nombre']}
                            </div>
                            <div style="font-size: 13px; color: #555; margin-bottom: 5px;">
                                📋 {query_info['descripcion']}
                            </div>
                            <div style="font-size: 12px; color: #7f8c8d;">
                                <span style="background: #e8f5e9; padding: 2px 8px; border-radius: 3px; margin-right: 10px;">
                                    📊 {query_info['tabla']}
                                </span>
                                <span style="color: #00a650;">
                                    OK {query_info['output']}
                                </span>
                            </div>
                        </div>
"""

html_content += """
                    </div>
                    <p style="margin-top: 30px; text-align: center; font-size: 12px;">
                        <strong>Generado:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ | 
                        <strong>Script:</strong> generar_reporte_cr_universal_v6.3.6.py | 
                        <strong>Versión:</strong> v6.3.2
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function toggleFooter() {
            var toggle = document.querySelector('.footer-toggle');
            var content = document.getElementById('footerContent');
            
            toggle.classList.toggle('active');
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        }
        
        // Weekly Chart
        var ctx = document.getElementById('weeklyChart').getContext('2d');
        var weeklyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: """ + str(df_weekly['SEMANA_LABEL'].tolist()) + """,
                datasets: [{
                    label: 'CR (pp)',
                    data: """ + str(df_weekly['CR'].round(4).tolist()) + """,
                    borderColor: '""" + color_config['primary'] + """',
                    backgroundColor: 'rgba(0, 166, 80, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { 
                        beginAtZero: false,
                        title: { display: true, text: 'CR (pp)' }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

# Guardar HTML
process_suffix = f"_{args.process_name.lower().replace(' ', '_').replace('-', '')}" if args.process_name else ""
html_filename = f"reporte_cr_{args.commerce_group.lower()}{process_suffix}_{args.site.lower()}_{p1_start_dt.strftime('%b').lower()}_{p2_start_dt.strftime('%b').lower()}_{p1_start_dt.year}_v6.3.html"
html_path = output_dir / html_filename

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[OK] HTML generado: {html_path}")
print()

# ========================================
# FINALIZAR - RESUMEN COMPLETO EN CONSOLA (v6.4.10)
# ========================================

print()
print("="*80)
print("  REPORTE COMPLETADO - RESUMEN COMPLETO")
print("="*80)
print()

# --- 1. CONFIGURACIÓN ---
print(f"  Site: {args.site} | Commerce Group: {args.commerce_group} | Aperturas: {', '.join(aperturas_list)}")
print(f"  P1: {args.p1_start} a {args.p1_end} | P2: {args.p2_start} a {args.p2_end}")
print()

# --- 2. CARDS EJECUTIVAS ---
print("  📊 CARDS EJECUTIVAS")
print("  " + "─"*76)
print(f"  │ Incoming P1:  {inc_p1_total:>12,}   │  Incoming P2:  {inc_p2_total:>12,}   │")
print(f"  │ Driver P1:    {drv_p1_total:>12,}   │  Driver P2:    {drv_p2_total:>12,}   │")
print(f"  │ CR P1:        {cr_p1:>11.4f} pp  │  CR P2:        {cr_p2:>11.4f} pp  │")
print(f"  │ Var Incoming:    {var_inc_total:>+10,} ({var_inc_pct:+.1f}%)")
print(f"  │ Var CR:          {var_cr:>+10.4f} pp ({var_cr_pct:+.1f}%)")
print("  " + "─"*76)
print()

# --- 3. RESUMEN EJECUTIVO (3 bullets) ---
print("  📋 RESUMEN EJECUTIVO")
print("  " + "─"*76)
print(f"  1. {bullet_1}")
print(f"  2. {bullet_2}")
print(f"  3. {bullet_3}")
print()

# --- 4. HALLAZGO PRINCIPAL ---
print("  💡 HALLAZGO PRINCIPAL")
print("  " + "─"*76)
direccion_hallazgo = "mejora" if var_cr < 0 else "empeoramiento"
print(f"  El {direccion_hallazgo} del {abs(var_cr_pct):.1f}% en CR se debe principalmente a:")
for i, exp in enumerate(hallazgo_explicaciones, 1):
    print(f"    {i}. {exp}")
print()

# --- 5. CUADRO CUANTITATIVO POR DIMENSIÓN ---
for dimension, df in cuadros_cuantitativos.items():
    print(f"  📊 CUADRO POR {dimension}")
    print("  " + "─"*76)
    header = f"  {'Elemento':<25} {'Inc P1':>9} {'Inc P2':>9} {'Var':>8} {'Contrib%':>9} {'CR P1':>9} {'CR P2':>9} {'Var CR':>9}"
    print(header)
    print("  " + "─"*76)
    for _, row in df.iterrows():
        dim_val = str(row['DIMENSION_VAL'])[:24]
        r_inc_p1 = int(row['INC_P1'])
        r_inc_p2 = int(row['INC_P2'])
        r_var_inc = int(row['VAR_INC'])
        r_contrib = row.get('CONTRIB_ABS', 0)
        r_cr_p1 = row['CR_P1']
        r_cr_p2 = row['CR_P2']
        r_var_cr = row['VAR_CR']
        contrib_str = f"{r_contrib:.1f}%" if pd.notna(r_contrib) and str(r_contrib) != '' else ""
        print(f"  {dim_val:<25} {r_inc_p1:>9,} {r_inc_p2:>9,} {r_var_inc:>+8,} {contrib_str:>9} {r_cr_p1:>9.4f} {r_cr_p2:>9.4f} {r_var_cr:>+9.4f}")
    print()

# --- 6. ANÁLISIS COMPARATIVO DE CAUSAS RAÍZ ---
try:
    if analisis_comp and len(analisis_comp) > 0:
        print("  " + "="*76)
        print("  🔍 ANÁLISIS COMPARATIVO DE CAUSAS RAÍZ")
        print("  " + "="*76)
        print()
        
        # Usar orden por contribución si está disponible
        try:
            elementos_ordenados = orden_contribucion if 'orden_contribucion' in dir() else list(analisis_comp.keys())
        except:
            elementos_ordenados = list(analisis_comp.keys())
        
        for idx, elemento in enumerate(elementos_ordenados, 1):
            if elemento not in analisis_comp:
                continue
            data = analisis_comp[elemento]
            
            # Obtener métricas del elemento
            inc_elem_p1 = data.get('incoming_nov', 0)
            inc_elem_p2 = data.get('incoming_dic', 0)
            var_elem = data.get('variacion_casos', 0)
            var_pct_elem = data.get('variacion_pct', 0)
            conv_p1 = data.get('conversaciones_nov', 0)
            conv_p2 = data.get('conversaciones_dic', 0)
            
            # Buscar contrib% en el cuadro cuantitativo
            contrib_elem = ""
            for dim_key, df_dim in cuadros_cuantitativos.items():
                match = df_dim[df_dim['DIMENSION_VAL'] == elemento]
                if len(match) > 0:
                    contrib_val = match.iloc[0].get('CONTRIB_ABS', 0)
                    if pd.notna(contrib_val):
                        contrib_elem = f" | Contribución al CR: {contrib_val:.1f}%"
                    break
            
            print(f"  ┌{'─'*74}┐")
            print(f"  │ #{idx} 📌 {elemento:<68}│")
            print(f"  │ Incoming: {inc_elem_p1:,} → {inc_elem_p2:,} ({var_pct_elem:+.1f}%, {var_elem:+,} casos){contrib_elem}")
            print(f"  │ Conversaciones analizadas: P1={conv_p1} | P2={conv_p2}")
            print(f"  └{'─'*74}┘")
            
            # Mostrar causas consolidadas con % por período
            causas_consolidadas = data.get('causas_consolidadas', [])
            if causas_consolidadas:
                print(f"  {'Causa':<50} {'% P1':>6} {'% P2':>6} {'Δ':>5}  {'Patrón'}")
                print(f"  {'─'*50} {'─'*6} {'─'*6} {'─'*5}  {'─'*15}")
                for c in causas_consolidadas:
                    c_name = str(c.get('causa', ''))[:49]
                    c_pct_p1 = c.get('pct_p1', 0)
                    c_pct_p2 = c.get('pct_p2', 0)
                    c_delta = c_pct_p2 - c_pct_p1
                    # Determinar patrón
                    if c_pct_p1 > 0 and c_pct_p2 > 0:
                        patron = "PERSISTENTE"
                    elif c_pct_p1 == 0 and c_pct_p2 > 0:
                        patron = "🆕 NUEVO"
                    elif c_pct_p1 > 0 and c_pct_p2 == 0:
                        patron = "❌ DESAPARECE"
                    else:
                        patron = ""
                    print(f"  {c_name:<50} {c_pct_p1:>5.0f}% {c_pct_p2:>5.0f}% {c_delta:>+4.0f}  {patron}")
            else:
                # Fallback: mostrar causas P1 y P2 por separado
                causas_p1_list = data.get('causas_nov', [])
                causas_p2_list = data.get('causas_dic', [])
                if causas_p1_list:
                    print(f"\n  📅 P1 ({args.p1_start[:7]}):")
                    for c in causas_p1_list[:5]:
                        print(f"    • {c.get('causa', 'N/A')} ({c.get('porcentaje', 0)}%)")
                if causas_p2_list:
                    print(f"\n  📅 P2 ({args.p2_start[:7]}):")
                    for c in causas_p2_list[:5]:
                        print(f"    • {c.get('causa', 'N/A')} ({c.get('porcentaje', 0)}%)")
            
            # Insight del elemento
            analisis_elem = data.get('analisis_comparativo', {})
            insight = analisis_elem.get('insight_principal', '')
            patron_cambio = analisis_elem.get('patron_cambio', '')
            if insight:
                print(f"\n  💡 Insight: {insight}")
            if patron_cambio:
                patron_dom_p1 = analisis_elem.get('patron_dominante_p1', '')
                patron_dom_p2 = analisis_elem.get('patron_dominante_p2', '')
                if patron_cambio == 'cambió':
                    print(f"  ⚠️  Patrón dominante CAMBIÓ: \"{patron_dom_p1}\" → \"{patron_dom_p2}\"")
                else:
                    print(f"  ✅ Patrón dominante se mantuvo: \"{patron_dom_p1}\"")
            
            # Citas destacadas (top 2 por período)
            causas_p1_citas = data.get('causas_nov', [])
            causas_p2_citas = data.get('causas_dic', [])
            citas_mostradas = 0
            max_citas = 3
            
            todas_citas_p1 = []
            todas_citas_p2 = []
            for c in causas_p1_citas[:2]:
                for cita in c.get('citas', [])[:1]:
                    todas_citas_p1.append(cita)
            for c in causas_p2_citas[:2]:
                for cita in c.get('citas', [])[:1]:
                    todas_citas_p2.append(cita)
            
            if todas_citas_p1 or todas_citas_p2:
                print(f"\n  📝 Citas destacadas:")
                for cita in todas_citas_p1[:2]:
                    texto = str(cita.get('texto', ''))[:120]
                    print(f"    P1 - Caso {cita.get('case_id', 'N/A')} ({cita.get('fecha', 'N/A')}): {texto}...")
                for cita in todas_citas_p2[:2]:
                    texto = str(cita.get('texto', ''))[:120]
                    print(f"    P2 - Caso {cita.get('case_id', 'N/A')} ({cita.get('fecha', 'N/A')}): {texto}...")
            
            print()
except NameError:
    # analisis_comp no existe (no se ejecutó análisis comparativo)
    pass
except Exception as e:
    print(f"  [WARNING] Error al imprimir análisis comparativo: {e}")
    print()

# --- 7. EVENTOS COMERCIALES ---
if eventos_comerciales_p1 or eventos_comerciales_p2:
    print("  📅 EVENTOS COMERCIALES")
    print("  " + "─"*76)
    if eventos_comerciales_p1:
        print(f"  P1 ({args.p1_start[:7]}):")
        for nombre, ev in eventos_comerciales_p1.items():
            print(f"    • {nombre}: {ev.get('casos', 0):,} casos ({ev.get('porcentaje', 0):.1f}%)")
    if eventos_comerciales_p2:
        print(f"  P2 ({args.p2_start[:7]}):")
        for nombre, ev in eventos_comerciales_p2.items():
            print(f"    • {nombre}: {ev.get('casos', 0):,} casos ({ev.get('porcentaje', 0):.1f}%)")
    print()

# --- 8. ARCHIVOS GENERADOS ---
print("  📁 ARCHIVOS GENERADOS")
print("  " + "─"*76)
print(f"  HTML:            {html_path}")
print(f"  CSVs:            {len(cuadros_cuantitativos)} cuadro(s) cuantitativo(s)")
if len(conversaciones_por_proceso) > 0:
    total_conv = sum(d.get('analisis_llm', {}).get('total_conversaciones', 0) for d in conversaciones_por_proceso.values())
    print(f"  Conversaciones:  {len(conversaciones_por_proceso)} elementos ({total_conv} conversaciones analizadas)")
try:
    if analisis_comp and len(analisis_comp) > 0:
        print(f"  Comparativo:     {analisis_comparativo_path.name}")
except NameError:
    pass
print()

if args.open_report:
    print("[OPEN] Abriendo reporte en navegador...")
    webbrowser.open(str(html_path.absolute()))
    print()

print("="*80)
