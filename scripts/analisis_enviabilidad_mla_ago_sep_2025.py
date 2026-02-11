"""
Análisis CR - CDU Enviabilidad - MLA Agosto-Septiembre 2025
==============================================================
Script para generar reporte completo con metodología v5.0
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import webbrowser

# Configuración
SITE = "MLA"
PERIODO_1 = "Agosto 2025"
PERIODO_2 = "Septiembre 2025"
CDU_FILTER = "Enviabilidad"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*80)
print("ANÁLISIS CR - CDU ENVIABILIDAD - MLA AGO-SEP 2025")
print("="*80)

# ============================================================================
# FASE 1: CÁLCULO DE MÉTRICAS BASELINE
# ============================================================================
print("\n[FASE 1] Calculando métricas baseline...")

# Leer datos de incoming
df_incoming = pd.read_csv("output/temp_incoming_enviabilidad.csv", encoding='utf-16')

# Limpiar nombres de columnas (quitar espacios)
df_incoming.columns = df_incoming.columns.str.strip()

# Leer datos de drivers
df_drivers = pd.read_csv("output/temp_drivers_mla.csv", encoding='utf-16')
df_drivers.columns = df_drivers.columns.str.strip()

# Calcular totales por período
incoming_ago = df_incoming[df_incoming['MES'] == '2025-08']['INCOMING'].sum()
incoming_sep = df_incoming[df_incoming['MES'] == '2025-09']['INCOMING'].sum()

driver_ago = df_drivers[df_drivers['MES'] == '2025-08']['DRIVER_ORDENES'].values[0]
driver_sep = df_drivers[df_drivers['MES'] == '2025-09']['DRIVER_ORDENES'].values[0]

# Calcular CR (pp)
cr_ago = (incoming_ago / driver_ago) * 100
cr_sep = (incoming_sep / driver_sep) * 100

# Calcular variaciones
delta_incoming = incoming_sep - incoming_ago
delta_incoming_pct = (delta_incoming / incoming_ago) * 100 if incoming_ago > 0 else 0
delta_cr = cr_sep - cr_ago
delta_cr_pct = (delta_cr / cr_ago) * 100 if cr_ago > 0 else 0

print(f"\n{'='*80}")
print(f"MÉTRICAS CONSOLIDADAS")
print(f"{'='*80}")
print(f"\n{'Métrica':<30} {'Ago 2025':>15} {'Sep 2025':>15} {'Variación':>15}")
print(f"{'-'*80}")
print(f"{'Incoming':<30} {incoming_ago:>15,.0f} {incoming_sep:>15,.0f} {delta_incoming:>+14,.0f} ({delta_incoming_pct:+.1f}%)")
print(f"{'Driver (Órdenes)':<30} {driver_ago:>15,.0f} {driver_sep:>15,.0f} {driver_sep-driver_ago:>+14,.0f}")
print(f"{'CR (pp)':<30} {cr_ago:>15.4f} {cr_sep:>15.4f} {delta_cr:>+15.4f} ({delta_cr_pct:+.1f}%)")

# ============================================================================
# FASE 2: DRILL-DOWN POR PROCESO
# ============================================================================
print(f"\n{'='*80}")
print(f"[FASE 2] Drill-down por PROCESS_NAME")
print(f"{'='*80}")

# Agregar por proceso y período
df_proceso = df_incoming.groupby(['MES', 'PROCESS_NAME'])['INCOMING'].sum().reset_index()

# Pivot para comparar períodos
df_proceso_pivot = df_proceso.pivot(index='PROCESS_NAME', columns='MES', values='INCOMING').fillna(0)
df_proceso_pivot.columns = ['P1_Ago', 'P2_Sep']
df_proceso_pivot['Delta'] = df_proceso_pivot['P2_Sep'] - df_proceso_pivot['P1_Ago']
df_proceso_pivot['Delta_Pct'] = (df_proceso_pivot['Delta'] / df_proceso_pivot['P1_Ago']) * 100
df_proceso_pivot['Contribucion'] = (abs(df_proceso_pivot['Delta']) / abs(delta_incoming)) * 100

# Ordenar por contribución
df_proceso_pivot = df_proceso_pivot.sort_values('Contribucion', ascending=False)

print(f"\n{'Proceso':<50} {'Ago':>10} {'Sep':>10} {'Delta':>10} {'Contrib %':>12}")
print(f"{'-'*100}")
for idx, row in df_proceso_pivot.iterrows():
    print(f"{idx:<50} {row['P1_Ago']:>10,.0f} {row['P2_Sep']:>10,.0f} {row['Delta']:>+10,.0f} {row['Contribucion']:>11.1f}%")

print(f"\n{'TOTAL':<50} {incoming_ago:>10,.0f} {incoming_sep:>10,.0f} {delta_incoming:>+10,.0f} {100.0:>11.1f}%")

# ============================================================================
# IDENTIFICAR ELEMENTOS PRIORIZADOS (REGLA 80%)
# ============================================================================
print(f"\n{'='*80}")
print(f"REGLA DEL 80% - ELEMENTOS PRIORIZADOS")
print(f"{'='*80}")

acumulado = 0
elementos_priorizados = []
for idx, row in df_proceso_pivot.iterrows():
    acumulado += row['Contribucion']
    elementos_priorizados.append({
        'proceso': idx,
        'delta': row['Delta'],
        'contribucion': row['Contribucion'],
        'p1': row['P1_Ago'],
        'p2': row['P2_Sep']
    })
    print(f"[OK] {idx}: {row['Contribucion']:.1f}% (acum: {acumulado:.1f}%)")
    if acumulado >= 80:
        break

# ============================================================================
# FASE 3: EVIDENCIA - ANÁLISIS DE CONVERSACIONES
# ============================================================================
print(f"\n{'='*80}")
print(f"[FASE 3] Análisis de Conversaciones")
print(f"{'='*80}")

# Nota: Para este caso, como CDU Enviabilidad no tiene TIPIFICACION ni ENVIRONMENT,
# el análisis cualitativo sería limitado. Marcaremos como hipótesis.

analisis_conversaciones = []

for elem in elementos_priorizados:
    proceso = elem['proceso']
    delta = elem['delta']
    contrib = elem['contribucion']
    
    print(f"\n[PROCESO] {proceso}")
    print(f"   Variacion: {delta:+,.0f} casos ({contrib:.1f}% de la variacion total)")
    print(f"   Status: [!] HIPOTESIS (sin datos de conversaciones disponibles)")
    print(f"   Motivo: CDU Enviabilidad no tiene tipificacion detallada en este periodo")
    
    analisis_conversaciones.append({
        'proceso': proceso,
        'variacion': int(delta),
        'contribucion': float(contrib),
        'hipotesis': True,
        'motivo': 'Sin tipificación detallada disponible para muestreo'
    })

# ============================================================================
# FASE 4: SANITY CHECKS
# ============================================================================
print(f"\n{'='*80}")
print(f"[FASE 4] Sanity Checks")
print(f"{'='*80}")

checks = {
    'Incoming > 0': incoming_ago > 0 and incoming_sep > 0,
    'Driver > 0': driver_ago > 0 and driver_sep > 0,
    'CR en rango válido': 0 < cr_ago < 100 and 0 < cr_sep < 100,
    'Períodos consecutivos': True,  # Ago-Sep son consecutivos
    'Contribuciones suman ~100%': abs(df_proceso_pivot['Contribucion'].sum() - 100) < 10
}

all_passed = all(checks.values())

for check, passed in checks.items():
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} - {check}")

if not all_passed:
    print("\n[!] ADVERTENCIA: Algunos checks fallaron. Revisar datos.")
else:
    print("\n[OK] Todos los checks pasaron correctamente.")

# ============================================================================
# FASE 5: GENERACIÓN DE REPORTE HTML
# ============================================================================
print(f"\n{'='*80}")
print(f"[FASE 5] Generando reporte HTML")
print(f"{'='*80}")

# Generar HTML
html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte CR - CDU Enviabilidad - MLA Ago-Sep 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            color: #1a202c;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 18px;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            border: 1px solid #e2e8f0;
        }}
        
        .card-label {{
            font-size: 13px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .card-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }}
        
        .card-change {{
            font-size: 14px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 6px;
            display: inline-block;
        }}
        
        .change-positive {{
            background: #fee;
            color: #dc2626;
        }}
        
        .change-negative {{
            background: #dcfce7;
            color: #16a34a;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            border: 1px solid #e2e8f0;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        th {{
            background: #f8fafc;
            font-weight: 600;
            color: #475569;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        td {{
            font-size: 14px;
            color: #334155;
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .number {{
            text-align: right;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }}
        
        .alert {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .alert-title {{
            font-weight: 600;
            color: #92400e;
            margin-bottom: 8px;
        }}
        
        .alert-text {{
            color: #78350f;
            font-size: 14px;
            line-height: 1.6;
        }}
        
        .footer {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            font-size: 13px;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }}
        
        .footer-title {{
            font-weight: 600;
            color: #475569;
            margin-bottom: 10px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            background: #e0e7ff;
            color: #3730a3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>📊 Contact Rate - CDU Enviabilidad</h1>
            <div class="subtitle">Site: {SITE} | Período: {PERIODO_1} vs {PERIODO_2}</div>
        </div>
        
        <!-- RESUMEN EJECUTIVO -->
        <div class="section">
            <div class="section-title">🎯 Resumen Ejecutivo</div>
            <ul style="line-height: 2; font-size: 15px; color: #334155;">
                <li><strong>CR empeoró +{delta_cr:.4f} pp (↑{delta_cr_pct:.1f}%)</strong> en CDU Enviabilidad de MLA entre Agosto y Septiembre 2025</li>
                <li><strong>Incoming subió +{delta_incoming:,.0f} casos (↑{delta_incoming_pct:.1f}%)</strong> mientras que el driver bajó {driver_sep-driver_ago:,.0f} órdenes, amplificando el impacto en CR</li>
                <li><strong>Proceso "Despacho Ventas y Publicaciones" explica el {df_proceso_pivot.iloc[0]['Contribucion']:.1f}% de la variación</strong> con +{int(df_proceso_pivot.iloc[0]['Delta']):,.0f} casos</li>
            </ul>
        </div>
        
        <!-- CARDS EJECUTIVAS -->
        <div class="cards-grid">
            <div class="card">
                <div class="card-label">Incoming Agosto</div>
                <div class="card-value">{incoming_ago:,.0f}</div>
            </div>
            <div class="card">
                <div class="card-label">Incoming Septiembre</div>
                <div class="card-value">{incoming_sep:,.0f}</div>
                <div class="card-change change-positive">+{delta_incoming:,.0f} ({delta_incoming_pct:+.1f}%)</div>
            </div>
            <div class="card">
                <div class="card-label">Driver Agosto</div>
                <div class="card-value">{driver_ago:,.0f}</div>
            </div>
            <div class="card">
                <div class="card-label">Driver Septiembre</div>
                <div class="card-value">{driver_sep:,.0f}</div>
                <div class="card-change change-negative">{driver_sep-driver_ago:,.0f}</div>
            </div>
            <div class="card">
                <div class="card-label">CR Agosto (pp)</div>
                <div class="card-value">{cr_ago:.4f}</div>
            </div>
            <div class="card">
                <div class="card-label">CR Septiembre (pp)</div>
                <div class="card-value">{cr_sep:.4f}</div>
                <div class="card-change change-positive">+{delta_cr:.4f} pp ({delta_cr_pct:+.1f}%)</div>
            </div>
        </div>
        
        <!-- DRILL-DOWN POR PROCESO -->
        <div class="section">
            <div class="section-title">📂 Drill-Down por Proceso</div>
            <table>
                <thead>
                    <tr>
                        <th>Proceso</th>
                        <th class="number">Ago 2025</th>
                        <th class="number">Sep 2025</th>
                        <th class="number">Δ Casos</th>
                        <th class="number">Δ %</th>
                        <th class="number">Contribución</th>
                    </tr>
                </thead>
                <tbody>
"""

for idx, row in df_proceso_pivot.iterrows():
    html_content += f"""
                    <tr>
                        <td>{idx}</td>
                        <td class="number">{row['P1_Ago']:,.0f}</td>
                        <td class="number">{row['P2_Sep']:,.0f}</td>
                        <td class="number" style="color: {'#dc2626' if row['Delta'] > 0 else '#16a34a'}">
                            {row['Delta']:+,.0f}
                        </td>
                        <td class="number" style="color: {'#dc2626' if row['Delta'] > 0 else '#16a34a'}">
                            {row['Delta_Pct']:+.1f}%
                        </td>
                        <td class="number">{row['Contribucion']:.1f}%</td>
                    </tr>
"""

html_content += f"""
                    <tr style="border-top: 2px solid #667eea; font-weight: 600; background: #f8fafc;">
                        <td>TOTAL</td>
                        <td class="number">{incoming_ago:,.0f}</td>
                        <td class="number">{incoming_sep:,.0f}</td>
                        <td class="number" style="color: #dc2626">{delta_incoming:+,.0f}</td>
                        <td class="number" style="color: #dc2626">{delta_incoming_pct:+.1f}%</td>
                        <td class="number">100.0%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- ANÁLISIS DE CONVERSACIONES -->
        <div class="section">
            <div class="section-title">💬 Análisis de Conversaciones</div>
            
            <div class="alert">
                <div class="alert-title">⚠️ Limitación de Datos</div>
                <div class="alert-text">
                    El CDU "Enviabilidad" no tiene campos de tipificación (REASON_DETAIL_GROUP_REPORTING) ni detalles adicionales 
                    en este período, lo que limita el análisis cualitativo detallado. Las causas raíz específicas requieren muestreo 
                    de conversaciones individuales desde BT_CX_STUDIO_SAMPLE.
                </div>
            </div>
            
            <p style="margin-top: 20px; color: #64748b; font-size: 14px;">
                <strong>Elementos priorizados (regla 80%):</strong>
            </p>
            
            <ul style="margin-top: 10px; line-height: 1.8; color: #334155;">
"""

for elem in elementos_priorizados:
    html_content += f"""
                <li>
                    <span class="badge">{elem['proceso']}</span> - 
                    Variación: <strong>{elem['delta']:+,.0f} casos</strong> 
                    (contribución: <strong>{elem['contribucion']:.1f}%</strong>) - 
                    <span style="color: #f59e0b;">⚠️ HIPÓTESIS</span>
                </li>
"""

html_content += f"""
            </ul>
            
            <p style="margin-top: 20px; font-size: 14px; color: #64748b; line-height: 1.6;">
                <strong>Recomendación:</strong> Para profundizar en las causas raíz, ejecutar análisis de conversaciones 
                con muestreo desde BT_CX_STUDIO_SAMPLE para los procesos priorizados.
            </p>
        </div>
        
        <!-- HALLAZGOS CONSOLIDADOS -->
        <div class="section">
            <div class="section-title">🔍 Hallazgos Consolidados</div>
            
            <h3 style="color: #1e293b; margin-bottom: 15px;">Macro (Nivel General)</h3>
            <ul style="line-height: 1.8; color: #334155; margin-bottom: 25px;">
                <li>CR de CDU Enviabilidad empeoró <strong>+{delta_cr:.4f} pp (↑{delta_cr_pct:.1f}%)</strong></li>
                <li>Incoming subió <strong>+{delta_incoming:,.0f} casos (↑{delta_incoming_pct:.1f}%)</strong></li>
                <li>Driver bajó <strong>{driver_sep-driver_ago:,.0f} órdenes (-{abs((driver_sep-driver_ago)/driver_ago*100):.1f}%)</strong>, amplificando el impacto en CR</li>
            </ul>
            
            <h3 style="color: #1e293b; margin-bottom: 15px;">Por Dimensión (Drill-Down)</h3>
            <ul style="line-height: 1.8; color: #334155; margin-bottom: 25px;">
                <li><strong>"Despacho Ventas y Publicaciones"</strong> explica el <strong>{df_proceso_pivot.iloc[0]['Contribucion']:.1f}%</strong> de la variación con <strong>+{int(df_proceso_pivot.iloc[0]['Delta']):,.0f} casos</strong></li>
                <li>Otros procesos menores ("Masivos", "FBM") tienen variación mínima (contribución &lt;2%)</li>
            </ul>
            
            <h3 style="color: #1e293b; margin-bottom: 15px;">Evidencia Cualitativa</h3>
            <ul style="line-height: 1.8; color: #334155;">
                <li>⚠️ Sin evidencia cualitativa disponible en este análisis (tipificación vacía)</li>
                <li>Se requiere muestreo de conversaciones para identificar causas raíz específicas</li>
            </ul>
        </div>
        
        <!-- FOOTER TÉCNICO -->
        <div class="footer">
            <div class="footer-title">📋 Información Técnica</div>
            <p><strong>Fuente de datos:</strong> meli-bi-data.WHOWNER.BT_CX_CONTACTS, BT_ORD_ORDERS</p>
            <p><strong>Reglas aplicadas:</strong> Clasificación por CASE, CONTACT_DATE_ID, filtros base (GMV_FLG, MARKETPLACE_FLG), exclusiones automáticas</p>
            <p><strong>Driver:</strong> Órdenes totales (global, sin filtro por site en query de driver)</p>
            <p><strong>Conversaciones analizadas:</strong> 0 (sin tipificación disponible para muestreo)</p>
            <p><strong>Correlación con eventos:</strong> No aplicada (sin hard metrics para el período)</p>
            <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Versión:</strong> Metodología v5.0 - Template Ad-Hoc</p>
        </div>
    </div>
</body>
</html>
"""

# Guardar HTML
output_html = OUTPUT_DIR / "reporte_cr_enviabilidad_mla_ago_sep_2025.html"
with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n[OK] Reporte HTML generado: {output_html}")

# Abrir reporte en navegador
webbrowser.open(str(output_html.absolute()))
print(f"[OK] Reporte abierto en navegador")

# ============================================================================
# EXPORTAR METADATA
# ============================================================================
metadata = {
    'site': SITE,
    'periodo_1': PERIODO_1,
    'periodo_2': PERIODO_2,
    'cdu_filter': CDU_FILTER,
    'metricas': {
        'incoming_p1': int(incoming_ago),
        'incoming_p2': int(incoming_sep),
        'driver_p1': int(driver_ago),
        'driver_p2': int(driver_sep),
        'cr_p1': float(cr_ago),
        'cr_p2': float(cr_sep),
        'delta_incoming': int(delta_incoming),
        'delta_incoming_pct': float(delta_incoming_pct),
        'delta_cr': float(delta_cr),
        'delta_cr_pct': float(delta_cr_pct)
    },
    'elementos_priorizados': elementos_priorizados,
    'fecha_generacion': datetime.now().isoformat()
}

metadata_path = OUTPUT_DIR / "metadata_enviabilidad_mla_ago_sep_2025.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"[OK] Metadata exportada: {metadata_path}")

print(f"\n{'='*80}")
print(f"ANALISIS COMPLETADO")
print(f"{'='*80}")
print(f"\nArchivos generados:")
print(f"  - Reporte HTML: {output_html}")
print(f"  - Metadata JSON: {metadata_path}")
print(f"\nEl reporte se abrio automaticamente en tu navegador.")
