"""
══════════════════════════════════════════════════════════════════════════════
CONTINGENCIAS MODULE - Ingesta de contingencias operacionales desde Google Sheets
══════════════════════════════════════════════════════════════════════════════

Lee contingencias (fenómenos climáticos, paros, cortes de servicio, etc.) desde
una Google Sheet, filtra por site y período, y genera la sección HTML para el
reporte de CR.

Uso:
    from utils.contingencias import cargar_contingencias, generar_contingencias_html

    data = cargar_contingencias(
        site='MLA',
        p1_start='2025-11-01', p1_end='2025-11-30',
        p2_start='2025-12-01', p2_end='2025-12-31',
    )
    html = generar_contingencias_html(data, 'Nov 2025', 'Dec 2025')

Version: 1.0
Fecha: Marzo 2026
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.contingencias_config import (
    CONTINGENCIAS_SHEET_ID,
    CONTINGENCIAS_SHEET_NAME,
    COLUMN_MAPPING,
    IGNORE_COLUMNS,
    LOGISTIC_TO_ENVIRONMENT,
    CACHE_DIR,
    CACHE_TTL_HOURS,
)
from config.site_groups import get_site_list


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def cargar_contingencias(
    site: str,
    p1_start: str, p1_end: str,
    p2_start: str, p2_end: str,
    skip: bool = False,
    environment_filter: Optional[List[str]] = None,
    force_refresh: bool = False,
) -> Dict:
    """
    Carga, filtra y clasifica contingencias operacionales.

    Args:
        site: Site individual (MLA) o grupo (ROLA, HSP)
        p1_start/p1_end: Rango de fechas P1 (YYYY-MM-DD)
        p2_start/p2_end: Rango de fechas P2 (YYYY-MM-DD)
        skip: Si True, retorna resultado vacío inmediatamente
        environment_filter: Lista opcional de ENVIRONMENT para filtrar
        force_refresh: Ignorar cache

    Returns:
        Dict con claves: contingencias_p1, contingencias_p2, contingencias_ambos,
        total, source, error
    """
    if skip:
        return _empty_result('skipped')

    # 1. Intentar cache
    if not force_refresh:
        cached = _read_cache()
        if cached is not None:
            print("[CONTINGENCIAS] Usando datos en cache")
            df = pd.DataFrame(cached)
            # Parsear fechas del cache
            for col in ['fecha_inicio', 'fecha_fin']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return _filter_and_classify(
                df, site, p1_start, p1_end, p2_start, p2_end,
                environment_filter, source='cache'
            )

    # 2. Intentar GSheet
    try:
        df = _fetch_from_gsheet()
        if df is not None and len(df) > 0:
            _write_cache(df)
            return _filter_and_classify(
                df, site, p1_start, p1_end, p2_start, p2_end,
                environment_filter, source='gsheet'
            )
    except Exception as e:
        print(f"[CONTINGENCIAS] [WARNING] Error al leer Google Sheet: {e}")
        print("[CONTINGENCIAS] Intentando fallback a cache expirado...")

        # Fallback a cache expirado
        cached = _read_cache(ignore_ttl=True)
        if cached is not None:
            print("[CONTINGENCIAS] Usando cache expirado como fallback")
            df = pd.DataFrame(cached)
            for col in ['fecha_inicio', 'fecha_fin']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return _filter_and_classify(
                df, site, p1_start, p1_end, p2_start, p2_end,
                environment_filter, source='cache_stale'
            )

    return _empty_result('unavailable')


# ══════════════════════════════════════════════════════════════════════════════
# LECTURA DE GOOGLE SHEETS
# ══════════════════════════════════════════════════════════════════════════════

def _fetch_from_gsheet() -> Optional[pd.DataFrame]:
    """Lee datos de la Google Sheet usando gspread + Application Default Credentials."""
    try:
        import gspread
        import google.auth
        from google.auth.transport.requests import Request
    except ImportError as e:
        print(f"[CONTINGENCIAS] [ERROR] Dependencia faltante: {e}")
        print("[CONTINGENCIAS] Ejecutar: pip install gspread google-auth")
        return None

    print(f"[CONTINGENCIAS] Leyendo Google Sheet {CONTINGENCIAS_SHEET_ID[:12]}...")

    # Usar Application Default Credentials (misma auth que BigQuery)
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/cloud-platform',
    ]
    creds, project = google.auth.default(scopes=scopes)
    creds.refresh(Request())
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(CONTINGENCIAS_SHEET_ID)

    if CONTINGENCIAS_SHEET_NAME:
        worksheet = sh.worksheet(CONTINGENCIAS_SHEET_NAME)
    else:
        worksheet = sh.sheet1

    records = worksheet.get_all_records()
    df = pd.DataFrame(records)

    if len(df) == 0:
        print("[CONTINGENCIAS] [WARNING] Sheet vacía")
        return None

    # Eliminar columnas ignoradas
    for col in IGNORE_COLUMNS:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Renombrar columnas según mapeo
    rename_map = {k: v for k, v in COLUMN_MAPPING.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Parsear fechas
    for date_col in ['fecha_inicio', 'fecha_fin']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)

    print(f"[CONTINGENCIAS] [OK] {len(df)} contingencias leídas del Sheet")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILTRADO Y CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def _filter_and_classify(
    df: pd.DataFrame,
    site: str,
    p1_start: str, p1_end: str,
    p2_start: str, p2_end: str,
    environment_filter: Optional[List[str]],
    source: str,
) -> Dict:
    """Filtra por site y fecha, clasifica contingencias por período."""
    p1_start_dt = pd.to_datetime(p1_start)
    p1_end_dt = pd.to_datetime(p1_end)
    p2_start_dt = pd.to_datetime(p2_start)
    p2_end_dt = pd.to_datetime(p2_end)

    # Filtro por site (soporta multi-valor separado por ";", ej: "MLA;MLC")
    sites = get_site_list(site)
    sites_upper = {s.upper() for s in sites}

    def matches_site(site_val):
        if pd.isna(site_val) or str(site_val).strip() == '':
            return False
        parts = [p.strip().upper() for p in str(site_val).split(';')]
        return bool(sites_upper & set(parts))

    site_mask = df['site'].apply(matches_site)
    df_filtered = df[site_mask].copy()

    # Filtro por ENVIRONMENT (opcional, para análisis de shipping)
    # Maneja valores múltiples separados por ";" (ej: "Fulfillment;Cross Docking;Logistics")
    if environment_filter and len(df_filtered) > 0:
        def matches_environment(logistic_val):
            if pd.isna(logistic_val) or str(logistic_val).strip() == '':
                return False
            parts = [p.strip() for p in str(logistic_val).split(';')]
            for part in parts:
                envs = LOGISTIC_TO_ENVIRONMENT.get(part)
                if envs is None:  # "Logistics" = aplica a todos
                    return True
                if any(e in environment_filter for e in envs):
                    return True
            return False

        df_filtered = df_filtered[df_filtered['logistic'].apply(matches_environment)]

    if len(df_filtered) == 0:
        print(f"[CONTINGENCIAS] Sin contingencias para site={site}")
        return _empty_result('no_match')

    # Clasificar por solapamiento con P1/P2
    def overlaps(row, period_start, period_end):
        if pd.isna(row.get('fecha_inicio')):
            return False
        c_start = row['fecha_inicio']
        c_end = row['fecha_fin'] if pd.notna(row.get('fecha_fin')) else pd.Timestamp.now()
        return c_start <= period_end and c_end >= period_start

    p1_mask = df_filtered.apply(lambda r: overlaps(r, p1_start_dt, p1_end_dt), axis=1)
    p2_mask = df_filtered.apply(lambda r: overlaps(r, p2_start_dt, p2_end_dt), axis=1)

    contingencias_p1 = df_filtered[p1_mask & ~p2_mask]
    contingencias_p2 = df_filtered[p2_mask & ~p1_mask]
    contingencias_ambos = df_filtered[p1_mask & p2_mask]

    total = len(contingencias_p1) + len(contingencias_p2) + len(contingencias_ambos)

    print(
        f"[CONTINGENCIAS] Filtradas: {total} relevantes "
        f"(P1: {len(contingencias_p1)}, P2: {len(contingencias_p2)}, "
        f"ambos: {len(contingencias_ambos)})"
    )

    return {
        'contingencias_p1': _to_serializable_records(contingencias_p1),
        'contingencias_p2': _to_serializable_records(contingencias_p2),
        'contingencias_ambos': _to_serializable_records(contingencias_ambos),
        'total': total,
        'source': source,
        'error': None,
    }


# ══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN HTML
# ══════════════════════════════════════════════════════════════════════════════

def generar_contingencias_html(
    contingencias_data: Dict,
    p1_label: str,
    p2_label: str,
) -> str:
    """
    Genera la sección HTML de contingencias para el reporte.
    Retorna string vacío si no hay contingencias.
    """
    if contingencias_data['total'] == 0:
        return ""

    all_contingencias = (
        [(c, 'P1') for c in contingencias_data['contingencias_p1']]
        + [(c, 'P2') for c in contingencias_data['contingencias_p2']]
        + [(c, 'Ambos') for c in contingencias_data['contingencias_ambos']]
    )

    # Ordenar por fecha de inicio
    all_contingencias.sort(key=lambda x: x[0].get('fecha_inicio', '') or '')

    source_label = contingencias_data.get('source', 'gsheet')
    source_display = {
        'gsheet': 'Google Sheets (lectura en tiempo real)',
        'cache': 'Google Sheets (cache local)',
        'cache_stale': 'Google Sheets (cache expirado - fallback)',
    }.get(source_label, source_label)

    html = f"""
        <div class="contingencias-operacionales">
            <h2>⚠️ Contingencias Operacionales</h2>
            <div class="info-box">
                ℹ️ Contingencias detectadas que pueden haber impactado el incoming
                en el período analizado. Fuente: {source_display}.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Clave</th>
                        <th>Resumen</th>
                        <th>Origin</th>
                        <th>Site</th>
                        <th>Logística</th>
                        <th>Inicio</th>
                        <th>Fin</th>
                        <th>Estado</th>
                        <th>Período</th>
                    </tr>
                </thead>
                <tbody>
    """

    for c, periodo in all_contingencias:
        # Badge de período
        if periodo == 'P1':
            badge_class = "badge-p1"
            periodo_text = f"P1 ({p1_label})"
        elif periodo == 'P2':
            badge_class = "badge-p2"
            periodo_text = f"P2 ({p2_label})"
        else:
            badge_class = "badge-ambos"
            periodo_text = "P1 + P2"

        # Badge de estado
        estado = str(c.get('estado', 'N/A'))
        estado_lower = estado.lower()
        if 'open' in estado_lower or 'abierto' in estado_lower or 'abierta' in estado_lower:
            estado_class = "badge-open"
        else:
            estado_class = "badge-closed"

        # Logistic → ENVIRONMENT display (maneja múltiples valores separados por ";")
        logistic = str(c.get('logistic', '')).strip()
        if not logistic:
            env_display = 'N/A'
            logistic = '-'
        else:
            parts = [p.strip() for p in logistic.split(';')]
            all_envs = []
            for part in parts:
                envs = LOGISTIC_TO_ENVIRONMENT.get(part)
                if envs is None:  # "Logistics" = TODOS
                    all_envs = ['TODOS']
                    break
                all_envs.extend(envs)
            env_display = ', '.join(dict.fromkeys(all_envs))  # deduplica preservando orden

        # Fechas
        fecha_inicio = c.get('fecha_inicio', 'N/A')
        fecha_fin = c.get('fecha_fin', 'N/A')

        html += f"""
                    <tr>
                        <td><strong>{c.get('clave', 'N/A')}</strong></td>
                        <td>{c.get('resumen', 'N/A')}</td>
                        <td>{c.get('origin', 'N/A')}</td>
                        <td>{c.get('site', 'N/A')}</td>
                        <td>{logistic} <span class="env-tag">({env_display})</span></td>
                        <td class="number">{fecha_inicio}</td>
                        <td class="number">{fecha_fin}</td>
                        <td><span class="badge {estado_class}">{estado}</span></td>
                        <td><span class="badge {badge_class}">{periodo_text}</span></td>
                    </tr>
        """

    n_p1 = len(contingencias_data['contingencias_p1'])
    n_p2 = len(contingencias_data['contingencias_p2'])
    n_ambos = len(contingencias_data['contingencias_ambos'])

    html += f"""
                </tbody>
            </table>
            <div class="summary">
                <span class="summary-icon">💡</span>
                <span class="summary-text">
                    <strong>{contingencias_data['total']}</strong> contingencia(s) operacional(es)
                    detectada(s): <strong>{n_p1}</strong> en P1,
                    <strong>{n_p2}</strong> en P2,
                    <strong>{n_ambos}</strong> en ambos períodos.
                    Las contingencias pueden explicar variaciones atípicas de incoming
                    en procesos logísticos.
                </span>
            </div>
        </div>
    """

    return html


# ══════════════════════════════════════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════════════════════════════════════

def _cache_path() -> Path:
    """Retorna el path del archivo de cache."""
    cache_dir = Path(CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    sheet_hash = hashlib.md5(CONTINGENCIAS_SHEET_ID.encode()).hexdigest()[:8]
    return cache_dir / f"contingencias_{sheet_hash}.json"


def _read_cache(ignore_ttl: bool = False) -> Optional[List[Dict]]:
    """Lee registros del cache local. Retorna None si no hay cache o expiró."""
    path = _cache_path()
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data['cached_at'])
        if not ignore_ttl and (datetime.now() - cached_at).total_seconds() > CACHE_TTL_HOURS * 3600:
            return None
        return data['records']
    except Exception:
        return None


def _write_cache(df: pd.DataFrame):
    """Guarda DataFrame como JSON en cache local."""
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    records_df = df.copy()
    for col in records_df.columns:
        if pd.api.types.is_datetime64_any_dtype(records_df[col]):
            if col == 'fecha_fin':
                records_df[col] = records_df[col].apply(
                    lambda x: 'Vigente' if pd.isna(x) else x.strftime('%Y-%m-%d')
                )
            else:
                records_df[col] = records_df[col].apply(
                    lambda x: None if pd.isna(x) else x.strftime('%Y-%m-%d')
                )

    data = {
        'cached_at': datetime.now().isoformat(),
        'record_count': len(records_df),
        'records': records_df.to_dict('records'),
    }

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[CONTINGENCIAS] Cache guardado: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _to_serializable_records(df: pd.DataFrame) -> List[Dict]:
    """Convierte DataFrame a lista de dicts con fechas como strings."""
    records = df.to_dict('records')
    for r in records:
        for key in ['fecha_inicio', 'fecha_fin']:
            if key not in r:
                continue
            try:
                is_nat = pd.isna(r[key])
            except (ValueError, TypeError):
                is_nat = r[key] is None
            if is_nat:
                r[key] = 'Vigente' if key == 'fecha_fin' else None
            elif hasattr(r[key], 'strftime'):
                r[key] = r[key].strftime('%Y-%m-%d')
    return records


def _empty_result(reason: str) -> Dict:
    """Retorna estructura vacía para cuando no hay datos."""
    return {
        'contingencias_p1': [],
        'contingencias_p2': [],
        'contingencias_ambos': [],
        'total': 0,
        'source': 'empty',
        'error': reason,
    }
