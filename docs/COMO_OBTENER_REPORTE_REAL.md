# 🎯 Cómo Obtener el Reporte de Contact Rate con Datos Reales

Tu máquina local no tiene permisos directos en `meli-bi-data` por seguridad. Aquí tienes **3 formas** de obtener el reporte con datos reales:

---

## ✅ **OPCIÓN 1: Jupyter Lab** (⭐ RECOMENDADO - Más rápido)

### Paso a paso:
1. Abre tu **Jupyter Lab** (donde ya tienes acceso a BigQuery)
2. Crea un nuevo notebook
3. Copia y pega todo el código de: **`ejecutar_en_jupyter.py`**
4. Ejecuta todas las celdas
5. ✨ Se generará automáticamente el HTML y se abrirá en tu navegador

**Tiempo estimado:** 2-3 minutos

**Archivos generados:**
- `reporte-cr-mla-process-name-2025-11-2025-12-REAL.html`
- `cr-analysis-mla-process-name-2025-11-2025-12-REAL.csv`

---

## ✅ **OPCIÓN 2: BigQuery Console + Script Local** (3 minutos)

### Paso a paso:

#### 1. Ejecutar query en BigQuery Console
- Abre: [BigQuery Console](https://console.cloud.google.com/bigquery?project=meli-bi-data)
- Copia TODO el contenido de: **`QUERY_COMPLETA_PARA_BIGQUERY.sql`**
- Pégalo en el editor de BigQuery
- Click en "Ejecutar" (RUN)
- Espera 30-60 segundos

#### 2. Descargar resultados
- Click en "SAVE RESULTS"
- Selecciona "CSV (local file)"
- Guarda como: `resultados_bigquery.csv`
- Mueve el archivo a esta carpeta del repositorio

#### 3. Generar HTML
- Ejecuta: `py generar_html_desde_csv.py`
- ✨ Se generará el HTML automáticamente

**Tiempo estimado:** 3 minutos

---

## ✅ **OPCIÓN 3: Configurar Permisos Locales** (Solo una vez, 5 minutos)

### Si quieres ejecutar desde tu máquina local siempre:

#### 1. Configurar credenciales
```bash
gcloud auth application-default login
```

Esto abrirá tu navegador para autenticarte.

#### 2. Ejecutar script
```bash
py ejecutar_con_gcloud_auth.py
```

#### 3. Si sigue fallando con permisos:
Solicita al administrador de IAM que te agregue el rol:
- **roles/serviceusage.serviceUsageConsumer**
- O permiso: **serviceusage.services.use**

En el proyecto: `meli-bi-data`

---

## 📊 ¿Qué hace la query?

La query completa (`QUERY_COMPLETA_PARA_BIGQUERY.sql`) obtiene:

1. **Incoming cases** por PROCESS_NAME
   - Filtrados por MLA, Nov-Dic 2025
   - Con exclusiones automáticas (queues, processes, flags)
   - Threshold: >= 50 casos en cualquier período

2. **Drivers** (órdenes completadas)
   - Por proceso desde BT_ORD_ORDERS
   - Fallback al total del site si no hay match

3. **Contact Rate** calculado
   - Fórmula: `CR = (Incoming / Driver) × 100`
   - Resultado en puntos porcentuales (pp)

4. **Variaciones**
   - Absoluta: Dif - Nov
   - Porcentual: % de cambio

---

## 📁 Archivos Disponibles

| Archivo | Para qué sirve |
|---------|----------------|
| **`ejecutar_en_jupyter.py`** | Ejecutar en Jupyter Lab (RECOMENDADO) |
| **`QUERY_COMPLETA_PARA_BIGQUERY.sql`** | Query lista para copiar/pegar en BigQuery Console |
| **`generar_html_desde_csv.py`** | Convierte CSV de BigQuery a HTML bonito |
| **`ejecutar_con_gcloud_auth.py`** | Para ejecutar local (requiere permisos) |
| **`INSTRUCCIONES_ANALISIS_CR.md`** | Documentación completa del análisis |

---

## 🎨 Resultado Final

El reporte HTML incluye:

✅ **Header** con badge "DATOS REALES"  
✅ **Resumen ejecutivo** con 6 métricas principales  
✅ **Tabla detallada** con 11 columnas:
   - PROCESS_NAME
   - Incoming Nov y Dic
   - Variación incoming (abs y %)
   - Driver Nov y Dic  
   - CR Nov y Dic (en pp)
   - Variación CR (abs en pp y %)

✅ **Colores semánticos**:
   - 🔴 Rojo: Empeoramiento (aumento de CR)
   - 🟢 Verde: Mejora (reducción de CR)

---

## ❓ Problemas Comunes

### "No tengo Jupyter Lab"
👉 Usa **OPCIÓN 2**: BigQuery Console + script local

### "No puedo ejecutar Python"
👉 Ejecuta la query en BigQuery Console y descarga el CSV  
👉 Abre el CSV en Excel/Google Sheets para ver los resultados

### "La query tarda mucho"
👉 Es normal, procesa millones de registros  
👉 Debería completar en 30-90 segundos

### "Error de permisos en BigQuery"
👉 Usa Jupyter Lab (ya tiene permisos)  
👉 O pide al admin agregar rol serviceUsageConsumer

---

## 💡 Recomendación Final

**Usa Jupyter Lab** (`ejecutar_en_jupyter.py`). Es la forma más rápida y no requiere configuración adicional.

---

¿Necesitas ayuda? Abre `INSTRUCCIONES_ANALISIS_CR.md` para documentación detallada.
