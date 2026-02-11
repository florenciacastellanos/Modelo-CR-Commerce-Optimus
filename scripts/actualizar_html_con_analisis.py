"""
Script para actualizar el reporte HTML con análisis de conversaciones
"""
import json
from pathlib import Path

# Cargar análisis de conversaciones
analisis_path = Path("output/analisis_conversaciones_claude_mlb_arrepentimiento.json")
with open(analisis_path, 'r', encoding='utf-8') as f:
    analisis = json.load(f)

# Leer HTML original
html_path = Path("output/reporte_cr_pdd_mlb_nov_dec_2025_v6.2.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Función para generar HTML de una causa raíz
def generar_html_causa(causa, index):
    citas_html = ""
    for i, cita in enumerate(causa['citas'][:3], 1):  # Máximo 3 citas
        citas_html += f"""
                    <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; border-radius: 6px; margin-bottom: 12px;">
                        <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                            <span style="background: #3498db; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 600;">CASE {cita['case_id']}</span>
                        </div>
                        <p style="font-size: 14px; line-height: 1.7; color: #2c3e50; margin: 0;">
                            "{cita['texto']}"
                        </p>
                    </div>
"""
    
    # Parsear sentimiento para obtener frustración y satisfacción
    sentimiento_texto = causa['sentimiento']
    frustracion = 0
    satisfaccion = 0
    
    if "frustración" in sentimiento_texto.lower():
        try:
            frustracion = int(sentimiento_texto.split("%")[0].split()[-1])
        except:
            frustracion = 0
    
    if "satisfacción" in sentimiento_texto.lower():
        try:
            # Buscar el segundo porcentaje en el texto
            partes = sentimiento_texto.split("%")
            if len(partes) > 1:
                satisfaccion = int(partes[1].split()[-1])
        except:
            satisfaccion = 0
    
    # Si no se encontró satisfacción, usar el complemento de frustración
    if satisfaccion == 0 and frustracion > 0:
        satisfaccion = 100 - frustracion
    
    return f"""
                <div style="background: white; border: 2px solid #ecf0f1; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                    <h4 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px; font-weight: 600;">Causa {index}: {causa['causa']}</h4>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px;">
                        <div style="text-align: center;">
                            <div style="font-size: 11px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 5px;">Frecuencia</div>
                            <div style="font-size: 24px; font-weight: 700; color: #2c3e50;">{causa['casos_estimados']}/60</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 11px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 5px;">Porcentaje</div>
                            <div style="font-size: 24px; font-weight: 700; color: #2c3e50;">{causa['porcentaje']}%</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 11px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 5px;">Casos Ejemplo</div>
                            <div style="font-size: 24px; font-weight: 700; color: #2c3e50;">{len(causa['citas'])}</div>
                        </div>
                    </div>
                    
                    <div style="background: #fff9e6; border-left: 4px solid #f39c12; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 600; margin-bottom: 8px;">DESCRIPCIÓN</div>
                        <p style="font-size: 14px; line-height: 1.7; color: #34495e; margin: 0;">{causa['descripcion']}</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <div style="font-size: 13px; color: #7f8c8d; font-weight: 600; margin-bottom: 12px;">CITAS TEXTUALES</div>
{citas_html}
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <div style="margin-bottom: 10px;">
                            <div style="font-size: 13px; color: #555; margin-bottom: 5px; display: flex; align-items: center; gap: 6px;">
                                <span>😠 Frustración durante contacto</span>
                            </div>
                            <div style="height: 30px; background: #ecf0f1; border-radius: 15px; overflow: hidden; position: relative;">
                                <div style="height: 100%; background: linear-gradient(90deg, #e74c3c, #c0392b); border-radius: 15px; width: {frustracion}%;"></div>
                                <div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: {'white' if frustracion > 50 else '#2c3e50'}; font-weight: 700; font-size: 13px;">{frustracion}%</div>
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 13px; color: #555; margin-bottom: 5px; display: flex; align-items: center; gap: 6px;">
                                <span>😊 Satisfacción post-resolución</span>
                            </div>
                            <div style="height: 30px; background: #ecf0f1; border-radius: 15px; overflow: hidden; position: relative;">
                                <div style="height: 100%; background: linear-gradient(90deg, #2ecc71, #27ae60); border-radius: 15px; width: {satisfaccion}%;"></div>
                                <div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: {'white' if satisfaccion > 50 else '#2c3e50'}; font-weight: 700; font-size: 13px;">{satisfaccion}%</div>
                            </div>
                        </div>
                    </div>

                </div>
"""

# Función para generar HTML completo de un proceso
def generar_html_proceso(data_proceso):
    causas_html = ""
    for i, causa in enumerate(data_proceso['causas_raiz'], 1):
        causas_html += generar_html_causa(causa, i)
    
    return f"""
            <div style="background: #f8f9fa; border-left: 5px solid #3498db; padding: 25px; margin-bottom: 30px; border-radius: 8px;">
                <h3 style="color: #2c3e50; margin-bottom: 20px; font-size: 22px; font-weight: 600;">🔹 Proceso: {data_proceso['proceso']}</h3>
                <p style="font-size: 14px; color: #7f8c8d; margin-bottom: 20px;">
                    <strong>Conversaciones analizadas:</strong> {data_proceso['total_conversaciones']} casos | 
                    <strong>Cobertura:</strong> {data_proceso['cobertura']}%
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px; font-weight: 600;">📊 Hallazgo Principal</h4>
                    <p style="font-size: 15px; line-height: 1.8; color: #34495e;">{data_proceso['hallazgo_principal']}</p>
                </div>

{causas_html}
            </div>
"""

# Generar HTML completo de análisis de conversaciones
nueva_seccion_conversaciones = """
        <!-- ANÁLISIS DE CONVERSACIONES -->
        <div class="section">
            <h2>💬 Análisis de Conversaciones - Evidencia Cualitativa</h2>
            <p style="margin-bottom: 30px; font-size: 15px; color: #555;">
                Análisis basado en muestreo de conversaciones (30 casos por proceso-período, 60 total). Cobertura objetivo: 80%+.
            </p>
"""

# Agregar cada proceso
for proceso_key in ["Arrepentimiento - XD", "Arrepentimiento - FBM", "Arrepentimiento - MP"]:
    nueva_seccion_conversaciones += generar_html_proceso(analisis[proceso_key])

nueva_seccion_conversaciones += """
        </div>
"""

# Reemplazar la sección de análisis de conversaciones en el HTML
import re

# Buscar la sección completa de análisis de conversaciones (desde <!-- ANÁLISIS DE CONVERSACIONES --> hasta el siguiente <!-- o el final de section)
patron = r'<!-- ANÁLISIS DE CONVERSACIONES -->.*?</div>\s*<!-- FOOTER COLAPSABLE -->'
match = re.search(patron, html_content, re.DOTALL)

if match:
    # Reemplazar la sección encontrada
    html_actualizado = html_content[:match.start()] + nueva_seccion_conversaciones + "\n        " + html_content[match.end():]
    
    # Guardar HTML actualizado
    html_actualizado_path = Path("output/reporte_cr_pdd_mlb_nov_dec_2025_v6.2_CON_ANALISIS.html")
    with open(html_actualizado_path, 'w', encoding='utf-8') as f:
        f.write(html_actualizado)
    
    print(f"[OK] HTML actualizado generado: {html_actualizado_path}")
    print(f"[INFO] Se insertaron análisis de {len(analisis)} procesos")
    print(f"[INFO] Total de causas raíz identificadas:")
    for proceso_key, data in analisis.items():
        print(f"  - {proceso_key}: {len(data['causas_raiz'])} causas")
else:
    print("[ERROR] No se encontró la sección de análisis de conversaciones en el HTML")
