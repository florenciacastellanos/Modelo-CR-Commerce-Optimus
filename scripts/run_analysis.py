"""
Module: run_analysis.py
Purpose: Main script to run Contact Rate analysis
Author: Contact Rate Analysis Team
Date: 2026-01-22
Version: 3.0.0

Description:
    Production-ready script to execute Contact Rate analysis for any Commerce Group,
    site, dimension, and period. Generates CSV and HTML reports automatically.

Dependencies:
    - pandas
    - google.cloud.bigquery
    - sys, os, io

Usage:
    python run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \\
                           --period1 "2025-11" --period2 "2025-12"

Parameters:
    --commerce-group: Commerce Group name (e.g., PDD, PNR, ME Distribución)
    --site: Site code (MLA, MLB, MLC, MCO, MLM, MLU, MPE)
    --dimension: Analysis dimension (PROCESS_NAME, CDU, TIPIFICACION, CLA_REASON_DETAIL, ENVIRONMENT)
    --period1: First period (YYYY-MM)
    --period2: Second period (YYYY-MM)
    --output-dir: Output directory (default: test/outputs/)
    --threshold: Minimum incoming cases (default: 50)
    --format: Output format (csv, html, both) (default: both)

Examples:
    # Analyze PDD in MLA by PROCESS_NAME for Nov-Dec 2025
    python run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \\
                           --period1 "2025-11" --period2 "2025-12"
    
    # Analyze ME Distribución in MLB by CDU for Sep-Oct 2025
    python run_analysis.py --commerce-group "ME Distribución" --site "MLB" --dimension "CDU" \\
                           --period1 "2025-09" --period2 "2025-10"
"""

import sys
import os
import io
import argparse
import webbrowser
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from config
try:
    from config import business_constants, thresholds, commerce_groups
except ImportError:
    print("⚠️ Warning: Could not import config modules. Using default values.")
    business_constants = None
    thresholds = None
    commerce_groups = None

# Constants
CR_MULTIPLIER = 100
MIN_THRESHOLD = 50
PROJECT_ID = 'meli-bi-data'

def _read_report_template() -> str:
    """
    Read the reusable HTML report template.
    """
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    template_path = os.path.join(templates_dir, 'report_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def _format_int(value) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

def _format_signed_int(value) -> str:
    try:
        return f"{int(value):+,}"
    except Exception:
        return str(value)

def _variation_class(var_abs: float) -> str:
    if var_abs > 0:
        return 'positive'
    if var_abs < 0:
        return 'negative'
    return 'neutral'

def _df_to_table_rows(df: pd.DataFrame, dimension: str) -> str:
    rows = []
    for _, row in df.iterrows():
        var_abs = row.get('VARIATION_ABS', 0)
        var_pct = row.get('VARIATION_PCT', 0)
        var_class = _variation_class(var_abs)
        rows.append(
            f"""
            <tr>
                <td>{row[dimension]}</td>
                <td>{_format_int(row.get('INCOMING_PERIOD1', 0))}</td>
                <td>{_format_int(row.get('INCOMING_PERIOD2', 0))}</td>
                <td class="{var_class}">{_format_signed_int(var_abs)}</td>
                <td class="{var_class}">{float(var_pct):+.2f}%</td>
            </tr>
            """.strip()
        )
    return "\n".join(rows)

def get_commerce_group_filter(commerce_group: str) -> str:
    """
    Get the SQL filter for a specific Commerce Group.
    
    Args:
        commerce_group: Commerce Group name
    
    Returns:
        SQL WHERE clause for the Commerce Group
    """
    # This is a simplified version. In production, import from config/commerce-groups.py
    commerce_filters = {
        'PDD': "PROCESS_PROBLEMATIC_REPORTING LIKE '%Dañado%' OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Defectuoso%'",
        'PNR': "PROCESS_PROBLEMATIC_REPORTING LIKE '%No recibido%'",
        'ME Distribución': "PROCESS_PROBLEMATIC_REPORTING LIKE '%Distribución%'",
        # Add more as needed
    }
    
    return commerce_filters.get(commerce_group, "1=1")

def build_query(commerce_group: str, site: str, dimension: str, period1: str, period2: str) -> str:
    """
    Build BigQuery SQL for CR analysis.
    
    Args:
        commerce_group: Commerce Group name
        site: Site code
        dimension: Analysis dimension
        period1: First period (YYYY-MM)
        period2: Second period (YYYY-MM)
    
    Returns:
        SQL query string
    """
    commerce_filter = get_commerce_group_filter(commerce_group)
    
    query = f"""
    WITH BASE_CONTACTS AS (
        SELECT
            PERIOD_MONTH,
            {dimension},
            COUNT(*) AS INCOMING
        FROM `meli-bi-data.WHOWNER.BT_CX_CONTACTS`
        WHERE 1=1
            AND SITE_ID = '{site}'
            AND PERIOD_MONTH IN ('{period1}', '{period2}')
            AND ({commerce_filter})
            AND FLAG_EXCLUDE_NUMERATOR_CR = 0
            AND QUEUE_ID NOT IN (2131, 230, 1102, 1241, 2075, 2294, 2295)
        GROUP BY 1, 2
    )
    
    SELECT
        {dimension},
        SUM(CASE WHEN PERIOD_MONTH = '{period1}' THEN INCOMING ELSE 0 END) AS INCOMING_PERIOD1,
        SUM(CASE WHEN PERIOD_MONTH = '{period2}' THEN INCOMING ELSE 0 END) AS INCOMING_PERIOD2
    FROM BASE_CONTACTS
    GROUP BY 1
    HAVING (INCOMING_PERIOD1 >= {MIN_THRESHOLD} OR INCOMING_PERIOD2 >= {MIN_THRESHOLD})
    ORDER BY INCOMING_PERIOD2 DESC
    """
    
    return query

def calculate_variation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate CR variation metrics.
    
    Args:
        df: DataFrame with INCOMING_PERIOD1 and INCOMING_PERIOD2
    
    Returns:
        DataFrame with variation calculations
    """
    df['VARIATION_ABS'] = df['INCOMING_PERIOD2'] - df['INCOMING_PERIOD1']
    df['VARIATION_PCT'] = ((df['INCOMING_PERIOD2'] - df['INCOMING_PERIOD1']) / df['INCOMING_PERIOD1'] * 100).round(2)
    df['VARIATION_PCT'] = df['VARIATION_PCT'].fillna(0)
    
    return df

def generate_html_report(df: pd.DataFrame, commerce_group: str, site: str,
                         dimension: str, period1: str, period2: str, output_path: str,
                         deep_dive_title: str | None = None, deep_dive_html: str | None = None):
    """
    Generate HTML report from analysis results.
    
    Args:
        df: Analysis results DataFrame
        commerce_group: Commerce Group name
        site: Site code
        dimension: Analysis dimension
        period1: First period
        period2: Second period
        output_path: Output file path
        deep_dive_title: Optional title for deep dive tab
        deep_dive_html: Optional HTML content for deep dive tab
    """
    template = _read_report_template()

    total_p1 = df['INCOMING_PERIOD1'].sum() if 'INCOMING_PERIOD1' in df.columns else 0
    total_p2 = df['INCOMING_PERIOD2'].sum() if 'INCOMING_PERIOD2' in df.columns else 0
    total_var = total_p2 - total_p1
    total_var_pct = (total_var / total_p1 * 100) if total_p1 else 0
    var_class = _variation_class(total_var)

    tab2_style = "display:none;" if not deep_dive_html else ""
    tab1_title = "Resumen"
    tab2_title = deep_dive_title or "Deep dive"
    tab2_content = deep_dive_html or ""

    html_content = template
    html_content = html_content.replace('{{COMMERCE_GROUP}}', str(commerce_group))
    html_content = html_content.replace('{{SITE}}', str(site))
    html_content = html_content.replace('{{DIMENSION}}', str(dimension))
    html_content = html_content.replace('{{PERIOD1}}', str(period1))
    html_content = html_content.replace('{{PERIOD2}}', str(period2))
    html_content = html_content.replace('{{TIMESTAMP}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    html_content = html_content.replace('{{TOTAL_PERIOD1}}', _format_int(total_p1))
    html_content = html_content.replace('{{TOTAL_PERIOD2}}', _format_int(total_p2))
    html_content = html_content.replace('{{TOTAL_VARIATION}}', _format_signed_int(total_var))
    html_content = html_content.replace('{{TOTAL_VARIATION_PCT}}', f"{total_var_pct:+.2f}")
    html_content = html_content.replace('{{VAR_CLASS}}', var_class)
    html_content = html_content.replace('{{TABLE_ROWS}}', _df_to_table_rows(df, dimension))
    html_content = html_content.replace('{{TAB1_TITLE}}', tab1_title)
    html_content = html_content.replace('{{TAB2_TITLE}}', tab2_title)
    html_content = html_content.replace('{{TAB2_STYLE}}', tab2_style)
    html_content = html_content.replace('{{TAB2_CONTENT}}', tab2_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def _build_deep_dive_html(df: pd.DataFrame, deep_dimension: str, period1: str, period2: str) -> str:
    """
    Build the HTML content shown inside the deep dive tab.
    """
    table_rows = _df_to_table_rows(df, deep_dimension)
    return f"""
    <div class="summary">
        <h2 style="margin-top: 0;">🔎 Deep dive: {deep_dimension}</h2>
        <p class="neutral" style="margin: 0;">
            Desglose adicional para explicar el resultado, usando los mismos filtros iniciales.
        </p>
    </div>
    <table>
        <thead>
            <tr>
                <th>{deep_dimension}</th>
                <th>Incoming {period1}</th>
                <th>Incoming {period2}</th>
                <th>Variación Abs</th>
                <th>Variación %</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """.strip()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run Contact Rate Analysis')
    parser.add_argument('--commerce-group', required=True, help='Commerce Group name')
    parser.add_argument('--site', required=True, help='Site code (MLA, MLB, etc.)')
    parser.add_argument('--dimension', required=True, help='Analysis dimension')
    parser.add_argument('--deep-dive-dimension', default=None, help='Optional deep dive dimension (second tab)')
    parser.add_argument('--period1', required=True, help='First period (YYYY-MM)')
    parser.add_argument('--period2', required=True, help='Second period (YYYY-MM)')
    parser.add_argument('--output-dir', default='test/outputs', help='Output directory')
    parser.add_argument('--threshold', type=int, default=50, help='Minimum incoming threshold')
    parser.add_argument('--format', default='both', choices=['csv', 'html', 'both'], help='Output format')
    parser.add_argument('--open-report', action='store_true', help='Open the HTML report after generation')
    
    args = parser.parse_args()
    
    print(f"\n🚀 Iniciando análisis de Contact Rate")
    print(f"   Commerce Group: {args.commerce_group}")
    print(f"   Site: {args.site}")
    print(f"   Dimensión: {args.dimension}")
    if args.deep_dive_dimension:
        print(f"   Deep dive: {args.deep_dive_dimension}")
    print(f"   Períodos: {args.period1} vs {args.period2}")
    print(f"   Threshold: {args.threshold}")
    
    # Build query
    print(f"\n📊 Construyendo query...")
    query = build_query(args.commerce_group, args.site, args.dimension, args.period1, args.period2)
    
    # Execute query
    print(f"⚙️ Ejecutando query en BigQuery...")
    try:
        client = bigquery.Client(project=PROJECT_ID)
        df = client.query(query).to_dataframe()
        print(f"✅ Query ejecutado: {len(df)} registros obtenidos")
    except Exception as e:
        print(f"❌ Error al ejecutar query: {e}")
        return 1
    
    # Calculate variations
    print(f"🧮 Calculando variaciones...")
    df = calculate_variation(df)

    deep_df = None
    if args.deep_dive_dimension:
        print(f"\n🔎 Construyendo query deep dive...")
        deep_query = build_query(args.commerce_group, args.site, args.deep_dive_dimension, args.period1, args.period2)
        print(f"⚙️ Ejecutando query deep dive en BigQuery...")
        try:
            deep_df = client.query(deep_query).to_dataframe()
            print(f"✅ Deep dive obtenido: {len(deep_df)} registros")
            deep_df = calculate_variation(deep_df)
        except Exception as e:
            print(f"⚠️ No se pudo ejecutar deep dive: {e}")
            deep_df = None
    
    # Generate outputs
    os.makedirs(args.output_dir, exist_ok=True)
    
    filename_base = f"{args.commerce_group.lower().replace(' ', '-')}-{args.site.lower()}-{args.dimension.lower()}-{args.period1}-{args.period2}"
    
    if args.format in ['csv', 'both']:
        csv_path = os.path.join(args.output_dir, f"{filename_base}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV generado: {csv_path}")
    
    if args.format in ['html', 'both']:
        html_filename = f"reporte-{filename_base}.html"
        deep_title = None
        deep_html = None
        if deep_df is not None and len(deep_df) > 0:
            deep_title = f"Deep dive ({args.deep_dive_dimension})"
            deep_html = _build_deep_dive_html(deep_df, args.deep_dive_dimension, args.period1, args.period2)
            html_filename = f"reporte-{filename_base}-deepdive-{args.deep_dive_dimension.lower()}.html"

        html_path = os.path.join(args.output_dir, html_filename)
        generate_html_report(
            df,
            args.commerce_group,
            args.site,
            args.dimension,
            args.period1,
            args.period2,
            html_path,
            deep_dive_title=deep_title,
            deep_dive_html=deep_html
        )
        print(f"✅ HTML generado: {html_path}")
        if args.open_report:
            try:
                abs_path = os.path.abspath(html_path)
                webbrowser.open(f"file:///{abs_path.replace(os.sep, '/')}")
                print(f"🌐 Reporte abierto en el navegador.")
            except Exception as e:
                print(f"⚠️ No se pudo abrir el reporte automáticamente: {e}")
    
    print(f"\n✅ Análisis completado exitosamente!\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
