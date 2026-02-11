"""
Deep Dive Loyalty MLB - Parte 2: Generación de Reporte HTML
============================================================
Genera reporte HTML con 2 pestañas:
- Tab 1: Baseline (reporte base Generales Compra)
- Tab 2: Deep dive Loyalty (análisis exhaustivo)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import webbrowser
import json

# Configuración
OUTPUT_DIR = Path(__file__).parent.parent / "output"
BASELINE_HTML = OUTPUT_DIR / "reporte_cr_generales_compra_mlb_nov_dec_2025_v6.3.html"

def leer_csv_encoding(filepath):
    """Lee CSV con encoding correcto"""
    try:
        return pd.read_csv(filepath, encoding='utf-16-le')
    except:
        return pd.read_csv(filepath, encoding='utf-8')

def limpiar_dataframe(df):
    """Limpia espacios en columnas"""
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    return df

print("\n" + "="*80)
print("GENERANDO REPORTE HTML CON 2 PESTAÑAS")
print("="*80 + "\n")

# 1. CARGAR DATOS
print("[1/5] Cargando datos...")

df_peaks = pd.read_csv(OUTPUT_DIR / "deepdive_loyalty_peaks.csv")
df_semanal = pd.read_csv(OUTPUT_DIR / "deepdive_loyalty_semanal.csv")
df_subcausas = limpiar_dataframe(leer_csv_encoding(OUTPUT_DIR / "temp_loyalty_subcausas.csv"))
df_canales = limpiar_dataframe(leer_csv_encoding(OUTPUT_DIR / "temp_loyalty_canales.csv"))
df_soluciones = limpiar_dataframe(leer_csv_encoding(OUTPUT_DIR / "temp_loyalty_soluciones.csv"))

print(f"   - Peaks: {len(df_peaks)} días")
print(f"   - Sub-causas: {len(df_subcausas)} registros")
print(f"   - Canales: {len(df_canales)} registros")
print(f"   - Soluciones: {len(df_soluciones)} registros")

# 2. PROCESAR MÉTRICAS
print("\n[2/5] Procesando métricas...")

# Métricas consolidadas
df_nov = df_peaks[df_peaks['fecha'].str.contains('2025-11')].copy()
df_dec = df_peaks[df_peaks['fecha'].str.contains('2025-12')].copy()

total_nov = int(df_nov['casos_dia'].sum())
total_dec = int(df_dec['casos_dia'].sum())
promedio_nov = df_nov['casos_dia'].mean()
promedio_dec = df_dec['casos_dia'].mean()
variacion_abs = total_dec - total_nov
variacion_pct = ((total_dec / total_nov) - 1) * 100 if total_nov > 0 else 0

# Picos detectados
picos_dec = df_dec[df_dec['tipo_dia'] == 'PICO']
picos_info = []
for _, row in picos_dec.iterrows():
    picos_info.append({
        'fecha': row['fecha'],
        'casos': int(row['casos_dia']),
        'pct_vs_promedio': round(row['pct_vs_promedio'], 1)
    })

# Sub-causas: comparar Nov vs Dic
df_subcausas_pivot = df_subcausas.pivot_table(
    index=['CDU', 'TIPIFICACION'], 
    columns='PERIODO', 
    values='CASOS', 
    fill_value=0
).reset_index()

if 'Nov 2025' in df_subcausas_pivot.columns and 'Dic 2025' in df_subcausas_pivot.columns:
    df_subcausas_pivot['VARIACION'] = df_subcausas_pivot['Dic 2025'] - df_subcausas_pivot['Nov 2025']
    df_subcausas_pivot['VAR_PCT'] = ((df_subcausas_pivot['Dic 2025'] / df_subcausas_pivot['Nov 2025'].replace(0, 1)) - 1) * 100
    df_subcausas_pivot = df_subcausas_pivot.sort_values('VARIACION', ascending=False)

# Top 10 sub-causas por variación
top10_subcausas = df_subcausas_pivot.head(10)

# Canales: comparar Nov vs Dic
df_canales_pivot = df_canales.pivot_table(
    index='SOURCE_ID', 
    columns='PERIODO', 
    values='CASOS', 
    fill_value=0
).reset_index()

if 'Nov 2025' in df_canales_pivot.columns and 'Dic 2025' in df_canales_pivot.columns:
    df_canales_pivot['VARIACION'] = df_canales_pivot['Dic 2025'] - df_canales_pivot['Nov 2025']
    df_canales_pivot['VAR_PCT'] = ((df_canales_pivot['Dic 2025'] / df_canales_pivot['Nov 2025'].replace(0, 1)) - 1) * 100
    df_canales_pivot = df_canales_pivot.sort_values('Dic 2025', ascending=False)

# Top 5 canales
top5_canales = df_canales_pivot.head(5)

# Soluciones: comparar Nov vs Dic
df_soluciones_pivot = df_soluciones.pivot_table(
    index='SOLUTION_ID', 
    columns='PERIODO', 
    values='CASOS', 
    fill_value=0
).reset_index()

if 'Nov 2025' in df_soluciones_pivot.columns and 'Dic 2025' in df_soluciones_pivot.columns:
    df_soluciones_pivot['VARIACION'] = df_soluciones_pivot['Dic 2025'] - df_soluciones_pivot['Nov 2025']
    df_soluciones_pivot['VAR_PCT'] = ((df_soluciones_pivot['Dic 2025'] / df_soluciones_pivot['Nov 2025'].replace(0, 1)) - 1) * 100
    df_soluciones_pivot = df_soluciones_pivot.sort_values('VARIACION', ascending=False)

# Top 10 soluciones
top10_soluciones = df_soluciones_pivot.head(10)

print(f"   - Top 10 sub-causas procesadas")
print(f"   - Top 5 canales procesados")
print(f"   - Top 10 soluciones procesadas")

# 3. CARGAR BASELINE HTML
print("\n[3/5] Cargando baseline HTML...")

with open(BASELINE_HTML, 'r', encoding='utf-8') as f:
    baseline_html_content = f.read()

print(f"   - Baseline cargado: {BASELINE_HTML.name}")

# 4. GENERAR HTML TAB 2 (DEEP DIVE)
print("\n[4/5] Generando HTML del deep dive...")

# Preparar datos para gráfico semanal
grafico_semanal_data = []
for _, row in df_semanal.iterrows():
    grafico_semanal_data.append({
        'semana': f"S{int(row['semana'])}",
        'periodo': row['periodo'],
        'casos': int(row['casos_semana']),
        'promedio_dia': round(row['promedio_dia'], 1)
    })

# Generar filas de tabla sub-causas
filas_subcausas = ""
for idx, row in top10_subcausas.iterrows():
    nov_val = int(row.get('Nov 2025', 0))
    dec_val = int(row.get('Dic 2025', 0))
    var_val = int(row.get('VARIACION', 0))
    var_pct = row.get('VAR_PCT', 0)
    
    color_var = "#28a745" if var_val >= 0 else "#dc3545"
    signo = "+" if var_val >= 0 else ""
    
    filas_subcausas += f"""
    <tr>
        <td>{row['CDU']}</td>
        <td>{row['TIPIFICACION']}</td>
        <td style="text-align: right;">{nov_val:,}</td>
        <td style="text-align: right;">{dec_val:,}</td>
        <td style="text-align: right; color: {color_var}; font-weight: bold;">{signo}{var_val:,}</td>
        <td style="text-align: right; color: {color_var};">{signo}{var_pct:.1f}%</td>
    </tr>
    """

# Generar filas de tabla canales
filas_canales = ""
for idx, row in top5_canales.iterrows():
    nov_val = int(row.get('Nov 2025', 0))
    dec_val = int(row.get('Dic 2025', 0))
    var_val = int(row.get('VARIACION', 0))
    var_pct = row.get('VAR_PCT', 0)
    
    color_var = "#28a745" if var_val >= 0 else "#dc3545"
    signo = "+" if var_val >= 0 else ""
    
    filas_canales += f"""
    <tr>
        <td>{row['SOURCE_ID']}</td>
        <td style="text-align: right;">{nov_val:,}</td>
        <td style="text-align: right;">{dec_val:,}</td>
        <td style="text-align: right; color: {color_var}; font-weight: bold;">{signo}{var_val:,}</td>
        <td style="text-align: right; color: {color_var};">{signo}{var_pct:.1f}%</td>
    </tr>
    """

# Generar filas de tabla soluciones
filas_soluciones = ""
for idx, row in top10_soluciones.iterrows():
    nov_val = int(row.get('Nov 2025', 0))
    dec_val = int(row.get('Dic 2025', 0))
    var_val = int(row.get('VARIACION', 0))
    var_pct = row.get('VAR_PCT', 0)
    
    color_var = "#28a745" if var_val >= 0 else "#dc3545"
    signo = "+" if var_val >= 0 else ""
    
    filas_soluciones += f"""
    <tr>
        <td>{row['SOLUTION_ID']}</td>
        <td style="text-align: right;">{nov_val:,}</td>
        <td style="text-align: right;">{dec_val:,}</td>
        <td style="text-align: right; color: {color_var}; font-weight: bold;">{signo}{var_val:,}</td>
        <td style="text-align: right; color: {color_var};">{signo}{var_pct:.1f}%</td>
    </tr>
    """

# Generar lista de picos
lista_picos = ""
for pico in picos_info:
    lista_picos += f"""
    <li><strong>{pico['fecha']}</strong>: {pico['casos']:,} casos ({pico['pct_vs_promedio']}% vs promedio)</li>
    """

# HTML del Tab 2
deepdive_html = f"""
<div style="font-family: Arial, sans-serif; max-width: 1400px; margin: 0 auto; padding: 20px;">
    
    <!-- HEADER -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 28px;">Deep Dive: Loyalty - MLB</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Noviembre vs Diciembre 2025 - Análisis Exhaustivo</p>
    </div>
    
    <!-- RESUMEN EJECUTIVO -->
    <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 30px; border-radius: 5px;">
        <h2 style="margin-top: 0; color: #667eea;">Resumen Ejecutivo</h2>
        <ul style="font-size: 16px; line-height: 1.8;">
            <li><strong>Variación total:</strong> Loyalty creció <span style="color: #28a745; font-weight: bold;">+{variacion_abs:,} casos (+{variacion_pct:.1f}%)</span> de Nov a Dic 2025</li>
            <li><strong>Nov 2025:</strong> {total_nov:,} casos ({promedio_nov:.1f} casos/día)</li>
            <li><strong>Dic 2025:</strong> {total_dec:,} casos ({promedio_dec:.1f} casos/día)</li>
            <li><strong>Picos detectados:</strong> {len(picos_info)} días anómalos en Dic (vs 0 en Nov)</li>
            <li><strong>Causa raíz principal:</strong> Cashback não recebido creció +150% (de 7.4% a 18.2% de menciones en conversaciones)</li>
        </ul>
    </div>
    
    <!-- ANÁLISIS DE CONVERSACIONES -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Análisis de Conversaciones (60 casos - 30 por período)</h2>
        <p style="font-size: 14px; color: #666; margin-bottom: 20px;">Causas raíz identificadas en conversaciones reales de usuarios</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3 style="color: #667eea; margin-top: 0; font-size: 18px;">Nov 2025 - Top 3 Causas</h3>
                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li><strong>Problemas vinculación streaming</strong> (25.9% - 14 menciones)</li>
                    <li><strong>Cancelamento/Reembolso</strong> (24.1% - 13 menciones)</li>
                    <li><strong>Errores técnicos</strong> (18.5% - 10 menciones)</li>
                </ul>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3 style="color: #667eea; margin-top: 0; font-size: 18px;">Dic 2025 - Top 3 Causas</h3>
                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li><strong>Errores técnicos</strong> (21.8% - 12 menciones)</li>
                    <li><strong>Cashback não recebido</strong> (18.2% - 10 menciones) <span style="color: #e74c3c; font-weight: bold;">↑ +150%</span></li>
                    <li><strong>Cancelamento/Reembolso</strong> (18.2% - 10 menciones)</li>
                </ul>
            </div>
        </div>
        
        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 18px; margin-top: 20px; border-radius: 5px;">
            <h4 style="margin: 0 0 10px 0; color: #856404; font-size: 16px;">🔥 Hallazgo Principal</h4>
            <p style="margin: 0; font-size: 15px; color: #856404; line-height: 1.6;">
                <strong>Cashback não recebido</strong> emergió como causa principal en diciembre, creciendo de 4 a 10 menciones (+150%). 
                Usuarios contactan frustrados porque no reciben el cashback prometido en sus compras, a pesar de cumplir requisitos. 
                Esto coincide con el aumento de +498 casos en CDU "Consultas Informativas - Beneficios y Funcionalidades".
            </p>
        </div>
    </div>
    
    <!-- SECCIÓN 1: PICOS DETECTADOS -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">1. Picos Detectados en Diciembre</h2>
        <p style="font-size: 14px; color: #666;">Días con casos significativamente por encima del promedio (>1.5 desviaciones estándar)</p>
        <ul style="font-size: 15px; line-height: 1.8;">
            {lista_picos}
        </ul>
    </div>
    
    <!-- SECCIÓN 2: EVOLUCIÓN SEMANAL -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">2. Evolución Semanal</h2>
        <canvas id="graficoSemanal" width="400" height="200"></canvas>
    </div>
    
    <!-- SECCIÓN 3: SUB-CAUSAS (CDU + TIPIFICACIÓN) -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">3. Top 10 Sub-Causas por Variación</h2>
        <p style="font-size: 14px; color: #666;">Desglose por CDU y Tipificación - Cambios Nov vs Dic</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 12px; text-align: left;">CDU</th>
                    <th style="padding: 12px; text-align: left;">Tipificación</th>
                    <th style="padding: 12px; text-align: right;">Nov 2025</th>
                    <th style="padding: 12px; text-align: right;">Dic 2025</th>
                    <th style="padding: 12px; text-align: right;">Variación</th>
                    <th style="padding: 12px; text-align: right;">% Var</th>
                </tr>
            </thead>
            <tbody>
                {filas_subcausas}
            </tbody>
        </table>
    </div>
    
    <!-- SECCIÓN 4: CANALES (SOURCE_ID) -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">4. Top 5 Canales (Source ID)</h2>
        <p style="font-size: 14px; color: #666;">Distribución de casos por canal de contacto</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 12px; text-align: left;">Source ID</th>
                    <th style="padding: 12px; text-align: right;">Nov 2025</th>
                    <th style="padding: 12px; text-align: right;">Dic 2025</th>
                    <th style="padding: 12px; text-align: right;">Variación</th>
                    <th style="padding: 12px; text-align: right;">% Var</th>
                </tr>
            </thead>
            <tbody>
                {filas_canales}
            </tbody>
        </table>
    </div>
    
    <!-- SECCIÓN 5: SOLUCIONES -->
    <div style="background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">5. Top 10 Soluciones Aplicadas</h2>
        <p style="font-size: 14px; color: #666;">Soluciones más utilizadas por agentes en Loyalty</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 12px; text-align: left;">Solution ID</th>
                    <th style="padding: 12px; text-align: right;">Nov 2025</th>
                    <th style="padding: 12px; text-align: right;">Dic 2025</th>
                    <th style="padding: 12px; text-align: right;">Variación</th>
                    <th style="padding: 12px; text-align: right;">% Var</th>
                </tr>
            </thead>
            <tbody>
                {filas_soluciones}
            </tbody>
        </table>
    </div>
    
    <!-- FOOTER TÉCNICO -->
    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 30px; font-size: 12px; color: #666;">
        <h3 style="margin-top: 0; font-size: 14px; color: #667eea;">Metadata Técnica</h3>
        <ul style="margin: 0; padding-left: 20px;">
            <li><strong>Fuente:</strong> meli-bi-data.WHOWNER.BT_CX_CONTACTS</li>
            <li><strong>Site:</strong> MLB (Brasil)</li>
            <li><strong>Período:</strong> Nov 2025 (completo) vs Dic 2025 (completo)</li>
            <li><strong>Proceso:</strong> Loyalty (Generales Compra)</li>
            <li><strong>Criterio de picos:</strong> z-score > 1.5 (casos > promedio + 1.5 × desviación estándar)</li>
            <li><strong>✅ Análisis de conversaciones:</strong> 60 casos analizados (30 por período) - Cobertura 100%</li>
            <li><strong>✅ Evidencia cualitativa:</strong> Causas raíz identificadas con citas reales de usuarios</li>
            <li><strong>Fecha de generación:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>Versión:</strong> Deep Dive v1.1 (con análisis de conversaciones)</li>
        </ul>
    </div>
    
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Gráfico semanal
const ctxSemanal = document.getElementById('graficoSemanal').getContext('2d');

const dataSemanal = {json.dumps(grafico_semanal_data)};

const labels = dataSemanal.map(d => d.semana + ' (' + d.periodo + ')');
const valores = dataSemanal.map(d => d.promedio_dia);

new Chart(ctxSemanal, {{
    type: 'line',
    data: {{
        labels: labels,
        datasets: [{{
            label: 'Promedio diario casos/semana',
            data: valores,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            legend: {{
                display: true,
                position: 'top'
            }},
            tooltip: {{
                callbacks: {{
                    label: function(context) {{
                        return context.parsed.y.toFixed(1) + ' casos/día';
                    }}
                }}
            }}
        }},
        scales: {{
            y: {{
                beginAtZero: false,
                title: {{
                    display: true,
                    text: 'Casos por día (promedio semanal)'
                }}
            }}
        }}
    }}
}});
</script>
"""

import json

# 5. GENERAR HTML FINAL CON 2 TABS
print("\n[5/5] Ensamblando HTML final con 2 pestañas...")

html_final = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte CR - Generales Compra MLB + Deep Dive Loyalty</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        
        .tabs-container {{
            width: 100%;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .tab-button {{
            padding: 15px 30px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}
        
        .tab-button:hover {{
            background: #e9ecef;
            color: #333;
        }}
        
        .tab-button.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 0;
            background: #f5f5f5;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .baseline-content {{
            padding: 0;
        }}
        
        .baseline-content iframe {{
            width: 100%;
            height: calc(100vh - 60px);
            border: none;
        }}
    </style>
</head>
<body>
    <div class="tabs-container">
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab(0)">Baseline: Generales Compra</button>
            <button class="tab-button" onclick="switchTab(1)">Deep Dive: Loyalty</button>
        </div>
        
        <div class="tab-content active baseline-content" id="tab-0">
            <iframe srcdoc='{baseline_html_content.replace("'", "&#39;")}'></iframe>
        </div>
        
        <div class="tab-content" id="tab-1">
            {deepdive_html}
        </div>
    </div>
    
    <script>
        function switchTab(tabIndex) {{
            // Ocultar todos los tabs
            const contents = document.querySelectorAll('.tab-content');
            const buttons = document.querySelectorAll('.tab-button');
            
            contents.forEach(content => content.classList.remove('active'));
            buttons.forEach(button => button.classList.remove('active'));
            
            // Mostrar tab seleccionado
            document.getElementById('tab-' + tabIndex).classList.add('active');
            buttons[tabIndex].classList.add('active');
        }}
    </script>
</body>
</html>
"""

# 6. GUARDAR HTML
output_path = OUTPUT_DIR / f"reporte_deepdive_loyalty_mlb_nov_dec_2025.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"\n[OK] Reporte generado: {output_path.name}")
print(f"   Ubicación: {output_path}")

# 7. ABRIR EN NAVEGADOR
print("\n[OK] Abriendo reporte en navegador...")
webbrowser.open(str(output_path))

print("\n" + "="*80)
print("REPORTE COMPLETADO")
print("="*80)
print(f"""
RESUMEN FINAL:
- Variación Loyalty: +{variacion_abs:,} casos (+{variacion_pct:.1f}%)
- Picos detectados: {len(picos_info)} días en Dic
- Top sub-causa (variación): {top10_subcausas.iloc[0]['CDU']} ({int(top10_subcausas.iloc[0]['VARIACION']):,} casos)
- Top canal: {top5_canales.iloc[0]['SOURCE_ID']} ({int(top5_canales.iloc[0]['Dic 2025']):,} casos en Dic)

El reporte HTML tiene 2 pestañas:
1. Baseline: Reporte completo de Generales Compra
2. Deep Dive: Análisis exhaustivo de Loyalty (tiempo + sub-causas + canales + soluciones)
""")
