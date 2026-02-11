# 🚀 `scripts/` - Scripts ejecutables

> Acá van los **scripts ad-hoc** para análisis específicos y validaciones históricas.  
> El **Template Universal v6.2 (oficial)** se ejecuta desde la **raíz** (`generar_reporte_cr_universal_v6.2.py`).

---

## 📂 Contenido

### 1) `run_analysis.py` (CLI genérico)
Script principal para ejecutar análisis de Contact Rate por Commerce Group / site / dimensión / períodos.

**Uso**:
```bash
python run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \
                       --period1 "2025-11" --period2 "2025-12"
```

**Parámetros**:
- `--commerce-group`: Nombre del Commerce Group (ej: PDD, PNR, ME Distribución)
- `--site`: Código de site (MLA, MLB, MLC, MCO, MLM, MLU, MPE)
- `--dimension`: Dimensión de análisis (PROCESS_NAME, CDU, TIPIFICACION, etc.)
- `--period1`: Primer período (YYYY-MM)
- `--period2`: Segundo período (YYYY-MM)
- `--output-dir`: Directorio de salida (default: `test/outputs/`)
- `--threshold`: Threshold mínimo de casos (default: 50)
- `--format`: Formato de salida (csv, html, both) (default: both)

**Ejemplos**:
```bash
# Análisis por PROCESS_NAME
python run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \
                       --period1 "2025-11" --period2 "2025-12"

# Análisis por CDU
python run_analysis.py --commerce-group "ME Distribución" --site "MLB" --dimension "CDU" \
                       --period1 "2025-09" --period2 "2025-10"

# Solo CSV
python run_analysis.py --commerce-group "PNR" --site "MLA" --dimension "TIPIFICACION" \
                       --period1 "2025-07" --period2 "2025-08" --format csv
```

### 2) Scripts CR ad-hoc (validaciones históricas / ejemplos)

- `generar_cr_generales_compra_MLA_nov_dic_2025.py`
  - **Qué hace**: Genera CR para *Generales Compra (Marketplace)* en MLA (Nov vs Dic 2025), con tablas HTML + CSV.
  - **Cuándo usar**: como referencia/validación del estándar Marketplace v3.7.

- `generar_cr_me_predespacho_MLB_nov_dic_2025.py`
  - **Qué hace**: Genera CR para *ME PreDespacho (Shipping)* en MLB (Nov vs Dic 2025), usando driver shipping (`BT_CX_DRIVERS_CR`).
  - **Cuándo usar**: como referencia/validación del estándar Shipping v3.7.

---

## 🔧 Requisitos

```bash
pip install pandas google-cloud-bigquery
```

## 🔑 Autenticación

Asegúrate de tener configurado `gcloud`:
```bash
gcloud auth application-default login
gcloud config set project meli-bi-data
```

---

## 📊 Outputs

Los scripts generan automáticamente:
- **CSV**: Datos tabulares para análisis
- **HTML**: Reportes visuales interactivos

### Recomendación de ubicación
- Para ejecuciones rápidas/temporales: dejar el default `test/outputs/` (se crea solo).
- Para reportes "ordenados" dentro del repo: usar `--output-dir` apuntando a `output/` (ver `output/README.md`).

Ejemplo:

```bash
python run_analysis.py --commerce-group "PDD" --site "MLA" --dimension "PROCESS_NAME" \
  --period1 "2025-11" --period2 "2025-12" --output-dir "output/cr/single-site"
```

---

## 🎯 Diferencia con Template Universal v6.2

| Aspecto | `scripts/` | Raíz (`generar_reporte_cr_universal_v6.2.py`) |
|---------|-----------|----------------------------------------------|
| **Objetivo** | Scripts ad-hoc / validaciones | Template Universal oficial |
| **Parametrización** | Específica por script | Completa (site, períodos, commerce group, dimensiones) |
| **Output típico** | CSV + HTML simples | HTML completo + hard metrics + análisis LLM |
| **Cuándo usar** | Exploración, checks, ejemplos específicos | Reporte oficial para stakeholders |
| **Mantenimiento** | Scripts puntuales, no unificados | Único script, fácil de mantener |

---

**Última actualización**: 30 de Enero de 2026
