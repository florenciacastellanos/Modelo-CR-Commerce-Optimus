"""
Script para calcular priorización según regla del 80%
PDD MLA Nov-Dic 2025
"""

import pandas as pd
import sys

# Leer CSV con encoding correcto
df = pd.read_csv('output/incoming_por_proceso.csv', encoding='utf-16')

# Limpiar nombres de columnas (pueden tener espacios)
df.columns = df.columns.str.strip()

print("Columnas detectadas:", df.columns.tolist())
print(f"\nTotal registros: {len(df)}")

# Calcular variación total absoluta (suma de valores absolutos)
df['VAR_ABS'] = df['VAR_ABSOLUTA'].abs()
total_var_abs = df['VAR_ABS'].sum()

print(f"\nVariación total absoluta: {total_var_abs:,.0f}")
print(f"Variación neta: {df['VAR_ABSOLUTA'].sum():,.0f}")

# Calcular contribución de cada proceso
df['CONTRIBUCION_PCT'] = (df['VAR_ABS'] / total_var_abs) * 100

# Ordenar por contribución descendente
df_sorted = df.sort_values('CONTRIBUCION_PCT', ascending=False).reset_index(drop=True)

# Calcular contribución acumulada
df_sorted['CONTRIBUCION_ACUM'] = df_sorted['CONTRIBUCION_PCT'].cumsum()

# Identificar procesos que suman 80%+
df_priorizados = df_sorted[df_sorted['CONTRIBUCION_ACUM'] <= 80.0].copy()

# Si el último no llega a 80%, agregar el siguiente
if df_priorizados['CONTRIBUCION_ACUM'].iloc[-1] < 80.0:
    next_idx = len(df_priorizados)
    if next_idx < len(df_sorted):
        df_priorizados = df_sorted.iloc[:next_idx+1].copy()

print("\n" + "="*100)
print("PROCESOS PRIORIZADOS (Regla del 80%)")
print("="*100)
print(f"\n{'#':<3} {'Proceso':<50} {'Inc Nov':<10} {'Inc Dic':<10} {'Variación':<12} {'Contrib %':<10} {'Acum %':<10}")
print("-"*100)

for idx, row in df_priorizados.iterrows():
    signo = "+" if row['VAR_ABSOLUTA'] > 0 else ""
    print(f"{idx+1:<3} {row['PROCESS_NAME'][:48]:<50} {row['INC_NOV']:>9,.0f} {row['INC_DIC']:>9,.0f} {signo}{row['VAR_ABSOLUTA']:>10,.0f} {row['CONTRIBUCION_PCT']:>9.1f}% {row['CONTRIBUCION_ACUM']:>9.1f}%")

print("-"*100)
print(f"\nTotal priorizados: {len(df_priorizados)} procesos")
print(f"Contribución acumulada: {df_priorizados['CONTRIBUCION_ACUM'].iloc[-1]:.1f}%")
print(f"Casos explicados: {df_priorizados['VAR_ABS'].sum():,.0f} de {total_var_abs:,.0f}")

# Guardar resultados
df_priorizados.to_csv('output/procesos_priorizados_80.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Resultados guardados en: output/procesos_priorizados_80.csv")

# Mostrar resumen de ambientes
print("\n" + "="*100)
print("RESUMEN POR AMBIENTE (de procesos priorizados)")
print("="*100)

# Extraer ambiente del nombre del proceso (último segmento después de " - ")
df_priorizados['AMBIENTE'] = df_priorizados['PROCESS_NAME'].str.split(' - ').str[-1]

resumen = df_priorizados.groupby('AMBIENTE').agg({
    'VAR_ABSOLUTA': 'sum',
    'VAR_ABS': 'sum',
    'CONTRIBUCION_PCT': 'sum'
}).sort_values('VAR_ABS', ascending=False)

print(f"\n{'Ambiente':<15} {'Variación':<15} {'Contrib %':<10}")
print("-"*40)
for ambiente, row in resumen.iterrows():
    signo = "+" if row['VAR_ABSOLUTA'] > 0 else ""
    print(f"{ambiente:<15} {signo}{row['VAR_ABSOLUTA']:>13,.0f} {row['CONTRIBUCION_PCT']:>9.1f}%")

print("\n✅ Priorización completada")
