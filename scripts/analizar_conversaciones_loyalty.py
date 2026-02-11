"""
Análisis de Conversaciones Loyalty MLB - Nov vs Dic 2025
=========================================================
Analiza 60 conversaciones (30 por período) para identificar causas raíz
y diferencias entre períodos.
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import re

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Leer CSVs de conversaciones
df_nov = pd.read_csv(OUTPUT_DIR / "conversaciones_loyalty_nov_v2.csv", encoding='utf-16-le')
df_dic = pd.read_csv(OUTPUT_DIR / "conversaciones_loyalty_dic_v2.csv", encoding='utf-16-le')

# Limpiar columnas
df_nov.columns = df_nov.columns.str.strip()
df_dic.columns = df_dic.columns.str.strip()

print("\n" + "="*80)
print("ANÁLISIS DE CONVERSACIONES LOYALTY MLB - NOV VS DIC 2025")
print("="*80 + "\n")

print(f"Conversaciones Nov: {len(df_nov)}")
print(f"Conversaciones Dic: {len(df_dic)}")

# Función para extraer palabras clave y temas principales
def extraer_temas(texto):
    """Extrae temas principales del texto"""
    texto_lower = texto.lower()
    
    temas = []
    
    # Cashback
    if 'cashback' in texto_lower or 'cash back' in texto_lower:
        temas.append('Cashback não recebido')
    
    # Cobranças
    if any(x in texto_lower for x in ['cobrança', 'cobrado', 'cobranca', 'duplicada', 'valor a mais']):
        temas.append('Problemas de cobrança')
    
    # Cancelamento/Reembolso
    if any(x in texto_lower for x in ['cancelar', 'reembolso', 'estorno']):
        temas.append('Cancelamento/Reembolso')
    
    # Vinculação de streaming
    if any(x in texto_lower for x in ['netflix', 'disney', 'hbo', 'universal', 'apple tv', 'max', 'vincular', 'ativar conta']):
        temas.append('Problemas de vinculación streaming')
    
    # Upgrades/Downgrades
    if any(x in texto_lower for x in ['upgrade', 'downgrade', 'trocar', 'mudar plano', 'migrar']):
        temas.append('Cambio de plan')
    
    # Bugs/Errores técnicos
    if any(x in texto_lower for x in ['bug', 'erro', 'erro', 'problema tecnico', 'nao consegue', 'não consegue', 'dificuldade']):
        temas.append('Errores técnicos')
    
    # Consultas informativas
    if any(x in texto_lower for x in ['como', 'duvida', 'dúvida', 'informações', 'informacoes', 'gostaria de saber']):
        temas.append('Consultas informativas')
    
    # Pagos rechazados
    if any(x in texto_lower for x in ['pagamento recusado', 'cartão recusado', 'recusa', 'negado']):
        temas.append('Pago rechazado')
    
    return temas if temas else ['Otros']

# Analizar noviembre
print("\n" + "="*80)
print("ANÁLISIS NOVIEMBRE 2025")
print("="*80 + "\n")

temas_nov = []
for _, row in df_nov.iterrows():
    texto = str(row['CONVERSATION_SUMMARY'])
    temas_nov.extend(extraer_temas(texto))

counter_nov = Counter(temas_nov)
total_nov = len(temas_nov)

print("Temas identificados (pueden ser múltiples por conversación):\n")
for tema, count in counter_nov.most_common():
    pct = (count / total_nov) * 100
    print(f"  {tema}: {count} menciones ({pct:.1f}%)")

# Analizar diciembre
print("\n" + "="*80)
print("ANÁLISIS DICIEMBRE 2025")
print("="*80 + "\n")

temas_dic = []
for _, row in df_dic.iterrows():
    texto = str(row['CONVERSATION_SUMMARY'])
    temas_dic.extend(extraer_temas(texto))

counter_dic = Counter(temas_dic)
total_dic = len(temas_dic)

print("Temas identificados (pueden ser múltiples por conversación):\n")
for tema, count in counter_dic.most_common():
    pct = (count / total_dic) * 100
    print(f"  {tema}: {count} menciones ({pct:.1f}%)")

# Comparación Nov vs Dic
print("\n" + "="*80)
print("COMPARACIÓN NOV VS DIC - VARIACIÓN DE TEMAS")
print("="*80 + "\n")

todos_temas = set(counter_nov.keys()) | set(counter_dic.keys())

comparacion = []
for tema in todos_temas:
    count_nov = counter_nov.get(tema, 0)
    count_dic = counter_dic.get(tema, 0)
    variacion = count_dic - count_nov
    pct_nov = (count_nov / total_nov) * 100 if total_nov > 0 else 0
    pct_dic = (count_dic / total_dic) * 100 if total_dic > 0 else 0
    
    comparacion.append({
        'tema': tema,
        'nov': count_nov,
        'dic': count_dic,
        'variacion': variacion,
        'pct_nov': pct_nov,
        'pct_dic': pct_dic
    })

# Ordenar por variación absoluta
comparacion_sorted = sorted(comparacion, key=lambda x: abs(x['variacion']), reverse=True)

print(f"{'Tema':<45} {'Nov':>6} {'Dic':>6} {'Var':>6} {'%Nov':>7} {'%Dic':>7}")
print("-" * 85)
for item in comparacion_sorted:
    signo = "+" if item['variacion'] > 0 else ""
    print(f"{item['tema']:<45} {item['nov']:>6} {item['dic']:>6} {signo}{item['variacion']:>5} {item['pct_nov']:>6.1f}% {item['pct_dic']:>6.1f}%")

# Hallazgos clave
print("\n" + "="*80)
print("HALLAZGOS CLAVE")
print("="*80 + "\n")

print("1. CAUSAS RAÍZ PRINCIPALES (Nov):")
for tema, count in counter_nov.most_common(3):
    pct = (count / total_nov) * 100
    print(f"   - {tema}: {count} menciones ({pct:.1f}%)")

print("\n2. CAUSAS RAÍZ PRINCIPALES (Dic):")
for tema, count in counter_dic.most_common(3):
    pct = (count / total_dic) * 100
    print(f"   - {tema}: {count} menciones ({pct:.1f}%)")

print("\n3. CAMBIOS MÁS SIGNIFICATIVOS:")
for item in comparacion_sorted[:3]:
    if item['variacion'] != 0:
        direccion = "creció" if item['variacion'] > 0 else "decreció"
        print(f"   - {item['tema']} {direccion} {abs(item['variacion'])} menciones ({item['pct_nov']:.1f}% → {item['pct_dic']:.1f}%)")

# Extraer ejemplos de casos por tema
print("\n" + "="*80)
print("EJEMPLOS DE CASOS POR TEMA PRINCIPAL")
print("="*80 + "\n")

def extraer_ejemplos(df, periodo):
    print(f"\n{periodo.upper()}:\n")
    ejemplos = {}
    
    for _, row in df.head(5).iterrows():
        texto = str(row['CONVERSATION_SUMMARY'])
        case_id = row['CAS_CASE_ID']
        temas = extraer_temas(texto)
        
        for tema in temas:
            if tema not in ejemplos:
                ejemplos[tema] = []
            if len(ejemplos[tema]) < 1:  # Solo 1 ejemplo por tema
                # Truncar texto a 200 caracteres
                texto_corto = texto[:200] + "..." if len(texto) > 200 else texto
                ejemplos[tema].append({'case_id': case_id, 'texto': texto_corto})
    
    for tema, casos in ejemplos.items():
        print(f"\n{tema}:")
        for caso in casos:
            print(f"  - Case {caso['case_id']}: {caso['texto']}")

extraer_ejemplos(df_nov, "Noviembre")
extraer_ejemplos(df_dic, "Diciembre")

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80 + "\n")

# Guardar resumen
resumen = {
    'periodo': ['Nov 2025', 'Dic 2025'],
    'conversaciones': [len(df_nov), len(df_dic)],
    'top_tema': [counter_nov.most_common(1)[0][0], counter_dic.most_common(1)[0][0]],
    'top_menciones': [counter_nov.most_common(1)[0][1], counter_dic.most_common(1)[0][1]]
}

df_resumen = pd.DataFrame(resumen)
df_resumen.to_csv(OUTPUT_DIR / "analisis_loyalty_resumen.csv", index=False, encoding='utf-8')
print("Resumen guardado: analisis_loyalty_resumen.csv")
