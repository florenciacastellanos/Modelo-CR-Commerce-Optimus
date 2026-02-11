"""
Script para insertar análisis comparativo en HTML existente
"""
import json
import sys
from pathlib import Path

def generar_seccion_html_comparativo(analisis_comp, p1_label="Diciembre 2025", p2_label="Enero 2026"):
    """Genera la sección HTML del análisis comparativo"""
    
    html = """
        <!-- ANÁLISIS COMPARATIVO DE PATRONES ENRIQUECIDO -->
        <div class="section">
            <h2>🔍 Análisis Comparativo de Patrones por Período</h2>
            <p style="margin-bottom: 30px; font-size: 15px; color: #555;">
                Identificación de qué patrones específicos explican la variación de Contact Rate entre períodos.
                Este análisis integra evidencia cualitativa, sentimiento y comparación temporal.
            </p>
        
        <script>
            function toggleCitas(procesoid) {
                var elem = document.getElementById('citas_' + procesoid);
                var btn = document.getElementById('btn_' + procesoid);
                if (elem.style.display === 'none') {
                    elem.style.display = 'block';
                    btn.innerHTML = 'Ocultar citas adicionales ▲';
                } else {
                    elem.style.display = 'none';
                    btn.innerHTML = 'Ver citas adicionales ▼';
                }
            }
        </script>
"""
    
    # Iterar por cada proceso en el análisis comparativo
    for proceso_key, data in analisis_comp.items():
        if data.get('conversaciones_nov', 0) == 0 and data.get('conversaciones_dic', 0) == 0:
            continue
        
        proceso = data['proceso']
        proceso_id = proceso.replace(' ', '_').replace('-', '_').replace('/', '_')
        inc_nov = data.get('incoming_nov', 0)
        inc_dic = data.get('incoming_dic', 0)
        var_casos = data.get('variacion_casos', 0)
        var_pct = data.get('variacion_pct', 0)
        total_conv = data.get('conversaciones_nov', 0) + data.get('conversaciones_dic', 0)
        
        # Calcular cobertura promedio
        causas_nov = data.get('causas_nov', [])
        cobertura_total = sum([c.get('porcentaje', 0) for c in causas_nov[:4]]) if len(causas_nov) > 0 else 100
        
        insight = data.get('analisis_comparativo', {}).get('insight_principal', 'Análisis en progreso')
        
        html += f"""
            <div style="background: #f0f4ff; border-left: 5px solid #3498db; padding: 25px; margin-bottom: 30px; border-radius: 8px;">
                <h3 style="color: #2c3e50; margin-bottom: 10px; font-size: 20px; font-weight: 600;">🔹 {proceso}</h3>
                <p style="font-size: 13px; color: #7f8c8d; margin-bottom: 15px;">
                    📊 <strong>Conversaciones analizadas:</strong> {total_conv} casos ({data.get('conversaciones_nov', 0)} {p1_label.split()[0]} + {data.get('conversaciones_dic', 0)} {p2_label.split()[0]}) | 
                    <strong>Cobertura:</strong> {cobertura_total:.0f}% del incoming
                </p>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <strong style="color: #856404;">💡 Insight Principal:</strong>
                    <p style="margin: 8px 0 0 0; color: #856404; line-height: 1.6;">{insight}</p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; background: white;">
                    <thead>
                        <tr>
                            <th rowspan="2" style="background: #2c3e50; color: white; padding: 12px; text-align: left; vertical-align: middle; border: 1px solid #ddd; min-width: 180px;">
                                Patrón / Causa Raíz
                            </th>
                            <th colspan="3" style="background: #FFE600; color: #2c3e50; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #ddd;">
                                {p1_label}
                            </th>
                            <th colspan="3" style="background: #FFE600; color: #2c3e50; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #ddd;">
                                {p2_label}
                            </th>
                            <th rowspan="2" style="background: #2c3e50; color: white; padding: 12px; text-align: center; vertical-align: middle; border: 1px solid #ddd;">
                                Var Casos
                            </th>
                            <th rowspan="2" style="background: #2c3e50; color: white; padding: 12px; text-align: center; vertical-align: middle; border: 1px solid #ddd;">
                                Var %
                            </th>
                            <th rowspan="2" style="background: #2c3e50; color: white; padding: 12px; text-align: center; vertical-align: middle; border: 1px solid #ddd;">
                                Δ Prop
                            </th>
                        </tr>
                        <tr>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">%</th>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">Casos</th>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd; min-width: 100px;">Sentimiento</th>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">%</th>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">Casos</th>
                            <th style="background: #34495e; color: white; padding: 10px; text-align: center; border: 1px solid #ddd; min-width: 100px;">Sentimiento</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Crear diccionario para mapear causas entre períodos
        causas_dict = {}
        sentimiento_dict = {}
        
        for causa_nov in causas_nov:
            causa_nombre = causa_nov.get('causa', '')
            causas_dict[causa_nombre] = {
                'nov_pct': causa_nov.get('porcentaje', 0),
                'nov_casos': causa_nov.get('casos_estimados', 0),
                'dic_pct': 0,
                'dic_casos': 0,
                'causa_data_nov': causa_nov
            }
            sent = causa_nov.get('sentimiento', {})
            frust_nov = sent.get('frustracion', 0)
            satisf_nov = sent.get('satisfaccion', 0) + sent.get('alivio', 0)
            sentimiento_dict[causa_nombre] = {
                'nov_frust': frust_nov,
                'nov_satisf': satisf_nov,
                'dic_frust': 0,
                'dic_satisf': 0
            }
        
        for causa_dic in data.get('causas_dic', []):
            causa_nombre = causa_dic.get('causa', '')
            if causa_nombre in causas_dict:
                causas_dict[causa_nombre]['dic_pct'] = causa_dic.get('porcentaje', 0)
                causas_dict[causa_nombre]['dic_casos'] = causa_dic.get('casos_estimados', 0)
                causas_dict[causa_nombre]['causa_data_dic'] = causa_dic
            else:
                causas_dict[causa_nombre] = {
                    'nov_pct': 0,
                    'nov_casos': 0,
                    'dic_pct': causa_dic.get('porcentaje', 0),
                    'dic_casos': causa_dic.get('casos_estimados', 0),
                    'causa_data_dic': causa_dic
                }
            
            sent = causa_dic.get('sentimiento', {})
            frust_dic = sent.get('frustracion', 0)
            satisf_dic = sent.get('satisfaccion', 0) + sent.get('alivio', 0)
            if causa_nombre in sentimiento_dict:
                sentimiento_dict[causa_nombre]['dic_frust'] = frust_dic
                sentimiento_dict[causa_nombre]['dic_satisf'] = satisf_dic
            else:
                sentimiento_dict[causa_nombre] = {
                    'nov_frust': 0,
                    'nov_satisf': 0,
                    'dic_frust': frust_dic,
                    'dic_satisf': satisf_dic
                }
        
        # Ordenar causas por impacto (mayor variación absoluta)
        causas_ordenadas = sorted(
            causas_dict.items(),
            key=lambda x: abs(x[1]['dic_casos'] - x[1]['nov_casos']),
            reverse=True
        )
        
        # Generar filas de la tabla
        for causa_nombre, valores in causas_ordenadas:
            var_casos_causa = valores['dic_casos'] - valores['nov_casos']
            var_pct_causa = ((valores['dic_casos'] - valores['nov_casos']) / valores['nov_casos'] * 100) if valores['nov_casos'] > 0 else 0
            delta_prop = valores['dic_pct'] - valores['nov_pct']
            
            sent = sentimiento_dict.get(causa_nombre, {})
            nov_frust = sent.get('nov_frust', 0)
            nov_satisf = sent.get('nov_satisf', 0)
            dic_frust = sent.get('dic_frust', 0)
            dic_satisf = sent.get('dic_satisf', 0)
            
            var_class = 'negative' if var_casos_causa > 0 else 'positive'
            delta_class = 'negative' if delta_prop > 0 else 'positive'
            
            html += f"""
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: 500;">{causa_nombre}</td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{valores['nov_pct']:.0f}%</td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{valores['nov_casos']:,}</td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-size: 11px;">
                                😠 {nov_frust}%<br>😊 {nov_satisf}%
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{valores['dic_pct']:.0f}%</td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{valores['dic_casos']:,}</td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-size: 11px;">
                                😠 {dic_frust}%<br>😊 {dic_satisf}%
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: {'#f23d4f' if var_casos_causa > 0 else '#00a650'}; font-weight: 600;">
                                {var_casos_causa:+,}
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: {'#f23d4f' if var_casos_causa > 0 else '#00a650'};">
                                {var_pct_causa:+.1f}%
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: {'#f23d4f' if delta_prop > 0 else '#00a650'};">
                                {delta_prop:+.1f} pp
                            </td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += """
        </div>
"""
    
    return html

def insertar_analisis_en_html(html_path, json_comp_path, output_path=None):
    """Inserta el análisis comparativo en el HTML existente"""
    
    if output_path is None:
        output_path = html_path
    
    # Leer HTML actual
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Leer JSON comparativo
    with open(json_comp_path, 'r', encoding='utf-8') as f:
        analisis_comp = json.load(f)
    
    # Generar sección HTML
    seccion_html = generar_seccion_html_comparativo(analisis_comp)
    
    # Buscar dónde insertar (antes del footer)
    footer_marker = '<div class="footer" style="background: #f8f8f8'
    
    if footer_marker in html_content:
        # Insertar antes del footer
        parts = html_content.split(footer_marker)
        nuevo_html = parts[0] + seccion_html + '\n\n        ' + footer_marker + parts[1]
    else:
        # Si no encuentra footer, agregar al final antes de </body>
        nuevo_html = html_content.replace('</body>', seccion_html + '\n</body>')
    
    # Guardar HTML actualizado
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(nuevo_html)
    
    print(f"[OK] Analisis comparativo insertado en: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: py insertar_analisis_comparativo_html.py <html_path> <json_comp_path> [output_path]")
        sys.exit(1)
    
    html_path = Path(sys.argv[1])
    json_comp_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    insertar_analisis_en_html(html_path, json_comp_path, output_path)
