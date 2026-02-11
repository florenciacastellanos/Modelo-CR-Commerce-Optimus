"""
Template: analysis_template.py
Purpose: Reusable template for Contact Rate analysis scripts
Author: Contact Rate Analysis Team
Date: 2026-01-22
Version: 1.0.0

Description:
    This template provides a standardized structure for creating CR analysis scripts.
    Copy this file and customize the parameters for your specific analysis.

Usage:
    1. Copy this template to your working directory
    2. Rename to your analysis name (e.g., analyze_pdd_mla.py)
    3. Customize the CONFIGURATION section
    4. Run: python your_analysis_name.py
"""

import sys
import os
import io
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================
# CONFIGURATION - CUSTOMIZE THIS SECTION
# ============================================

# Analysis parameters
COMMERCE_GROUP = "PDD"  # Change to your Commerce Group
SITE = "MLA"  # Change to your site
DIMENSION = "PROCESS_NAME"  # Change to your dimension
PERIOD_1 = "2025-11"  # First period
PERIOD_2 = "2025-12"  # Second period

# Output configuration
OUTPUT_DIR = "test/outputs"
OUTPUT_FORMAT = "both"  # Options: 'csv', 'html', 'both'

# Thresholds
MIN_THRESHOLD = 50  # Minimum incoming cases per process

# BigQuery configuration
PROJECT_ID = "meli-bi-data"
PRIORITY = "BATCH"  # Options: 'INTERACTIVE', 'BATCH'

# ============================================
# COMMERCE GROUP FILTERS
# ============================================

COMMERCE_FILTERS = {
    'PDD': "PROCESS_PROBLEMATIC_REPORTING LIKE '%Dañado%' OR PROCESS_PROBLEMATIC_REPORTING LIKE '%Defectuoso%'",
    'PNR': "PROCESS_PROBLEMATIC_REPORTING LIKE '%No recibido%'",
    'ME Distribución': "PROCESS_PROBLEMATIC_REPORTING LIKE '%Distribución%'",
    'ME PreDespacho': "PROCESS_PROBLEMATIC_REPORTING LIKE '%PreDespacho%'",
    'FBM Sellers': "PROCESS_PROBLEMATIC_REPORTING LIKE '%FBM%'",
    # Add more Commerce Groups as needed
}

# ============================================
# QUERY BUILDER
# ============================================

def build_query(commerce_group, site, dimension, period1, period2, threshold):
    """
    Build BigQuery SQL for CR analysis.
    
    Args:
        commerce_group: Commerce Group name
        site: Site code
        dimension: Analysis dimension
        period1: First period (YYYY-MM)
        period2: Second period (YYYY-MM)
        threshold: Minimum incoming threshold
    
    Returns:
        SQL query string
    """
    commerce_filter = COMMERCE_FILTERS.get(commerce_group, "1=1")
    
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
            AND PROCESS_ID NOT IN (1312)
        GROUP BY 1, 2
    )
    
    SELECT
        {dimension},
        SUM(CASE WHEN PERIOD_MONTH = '{period1}' THEN INCOMING ELSE 0 END) AS INCOMING_PERIOD1,
        SUM(CASE WHEN PERIOD_MONTH = '{period2}' THEN INCOMING ELSE 0 END) AS INCOMING_PERIOD2
    FROM BASE_CONTACTS
    GROUP BY 1
    HAVING (INCOMING_PERIOD1 >= {threshold} OR INCOMING_PERIOD2 >= {threshold})
    ORDER BY INCOMING_PERIOD2 DESC
    """
    
    return query

# ============================================
# CALCULATION FUNCTIONS
# ============================================

def calculate_variation(df):
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

# ============================================
# REPORT GENERATION
# ============================================

def generate_html_report(df, commerce_group, site, dimension, period1, period2, output_path):
    """
    Generate HTML report from analysis results.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Análisis CR - {commerce_group} - {site}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: #fff159;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #333;
                margin: 0;
            }}
            .metadata {{
                color: #666;
                font-size: 14px;
                margin-top: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{
                background-color: #3483fa;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 10px 12px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background-color: #f8f8f8;
            }}
            .positive {{
                color: #00a650;
                font-weight: bold;
            }}
            .negative {{
                color: #f23d4f;
                font-weight: bold;
            }}
            .neutral {{
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Análisis de Contact Rate</h1>
            <div class="metadata">
                <strong>Commerce Group:</strong> {commerce_group} | 
                <strong>Site:</strong> {site} | 
                <strong>Dimensión:</strong> {dimension}<br>
                <strong>Períodos:</strong> {period1} vs {period2} | 
                <strong>Generado:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>{dimension}</th>
                    <th>Incoming {period1}</th>
                    <th>Incoming {period2}</th>
                    <th>Variación Abs</th>
                    <th>Variación %</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df.iterrows():
        var_class = 'positive' if row['VARIATION_ABS'] > 0 else ('negative' if row['VARIATION_ABS'] < 0 else 'neutral')
        html_content += f"""
                <tr>
                    <td>{row[dimension]}</td>
                    <td>{int(row['INCOMING_PERIOD1']):,}</td>
                    <td>{int(row['INCOMING_PERIOD2']):,}</td>
                    <td class="{var_class}">{int(row['VARIATION_ABS']):+,}</td>
                    <td class="{var_class}">{row['VARIATION_PCT']:+.2f}%</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution function"""
    print(f"\n🚀 Iniciando análisis de Contact Rate")
    print(f"   Commerce Group: {COMMERCE_GROUP}")
    print(f"   Site: {SITE}")
    print(f"   Dimensión: {DIMENSION}")
    print(f"   Períodos: {PERIOD_1} vs {PERIOD_2}")
    print(f"   Threshold: {MIN_THRESHOLD}")
    
    # Build query
    print(f"\n📊 Construyendo query...")
    query = build_query(COMMERCE_GROUP, SITE, DIMENSION, PERIOD_1, PERIOD_2, MIN_THRESHOLD)
    
    # Execute query
    print(f"⚙️ Ejecutando query en BigQuery...")
    try:
        client = bigquery.Client(project=PROJECT_ID)
        job_config = bigquery.QueryJobConfig(priority=PRIORITY)
        df = client.query(query, job_config=job_config).to_dataframe()
        print(f"✅ Query ejecutado: {len(df)} registros obtenidos")
    except Exception as e:
        print(f"❌ Error al ejecutar query: {e}")
        return 1
    
    if len(df) == 0:
        print(f"⚠️ No se encontraron datos para los parámetros especificados")
        return 0
    
    # Calculate variations
    print(f"🧮 Calculando variaciones...")
    df = calculate_variation(df)
    
    # Generate outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filename_base = f"{COMMERCE_GROUP.lower().replace(' ', '-')}-{SITE.lower()}-{DIMENSION.lower()}-{PERIOD_1}-{PERIOD_2}"
    
    if OUTPUT_FORMAT in ['csv', 'both']:
        csv_path = os.path.join(OUTPUT_DIR, f"{filename_base}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV generado: {csv_path}")
    
    if OUTPUT_FORMAT in ['html', 'both']:
        html_path = os.path.join(OUTPUT_DIR, f"reporte-{filename_base}.html")
        generate_html_report(df, COMMERCE_GROUP, SITE, DIMENSION, PERIOD_1, PERIOD_2, html_path)
        print(f"✅ HTML generado: {html_path}")
    
    print(f"\n✅ Análisis completado exitosamente!\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
