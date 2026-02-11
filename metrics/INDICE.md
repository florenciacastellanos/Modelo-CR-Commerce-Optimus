# 🗺️ Índice de Documentación - Sistema de Hard Metrics

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Propósito:** Mapa completo de navegación por toda la documentación del sistema

---

## 🎯 ¿Qué quieres hacer?

### **🆕 Soy nuevo, ¿por dónde empiezo?**
1. ⭐ Lee **[GUIA_USUARIO.md](GUIA_USUARIO.md)** (30 min)
2. Ejecuta tu primer comando:
   ```bash
   ls -lh metrics/eventos/data/*.parquet
   ```
3. Lee un metadata de ejemplo:
   ```bash
   cat metrics/eventos/data/metadata_mla_2025_12.json
   ```
4. Consulta **[README.md](README.md)** para visión general

---

### **📊 Quiero generar un reporte usando hard metrics**
1. Verifica si las métricas existen:
   ```bash
   ls metrics/eventos/data/correlacion_{site}_{periodo}.parquet
   ```
2. Si NO existen, ve a: **[Generar métricas nuevas](#-quiero-generar-métricas-para-un-período-nuevo)**
3. Si SÍ existen, consulta: **[INTEGRACION_GOLDEN_TEMPLATES.md](INTEGRACION_GOLDEN_TEMPLATES.md)**
4. Código de ejemplo: **[eventos/ejemplo_uso.py](eventos/ejemplo_uso.py)**

---

### **🔧 Quiero generar métricas para un período nuevo**
1. Lee: **[eventos/README.md](eventos/README.md)** - Cómo funcionan las métricas
2. Ejecuta el generador:
   ```bash
   python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
   ```
3. Valida el resultado:
   - Verifica archivos creados
   - Lee el metadata
   - Ejecuta query de validación (en **[eventos/CUANDO_REGENERAR.md](eventos/CUANDO_REGENERAR.md)**)

---

### **🔄 Tengo métricas pero son viejas, ¿cuándo regenero?**
1. ⭐ Lee: **[eventos/CUANDO_REGENERAR.md](eventos/CUANDO_REGENERAR.md)**
2. Checklist de decisión:
   - ¿Cambió la tabla de eventos?
   - ¿Hay nuevos eventos comerciales?
   - ¿Cambió la lógica de filtros?
3. Si respuesta es SÍ → Regenera:
   ```bash
   python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
   ```

---

### **❓ Quiero entender de dónde vienen las fechas de eventos**
1. Lee: **[eventos/FUENTE_EVENTOS.md](eventos/FUENTE_EVENTOS.md)**
2. Consulta la tabla oficial:
   ```sql
   SELECT * FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT
   WHERE SIT_SITE_ID = 'MLA'
   ORDER BY EVENT_START_DTTM DESC LIMIT 10
   ```
3. Compara con metadata generado

---

### **📊 Quiero analizar verticales y dominios (PDD/PNR)**
1. ⭐ Lee: **[verticales/FUENTE_VERTICALES.md](verticales/FUENTE_VERTICALES.md)** - ¿Qué son verticales?
2. Verifica si existen métricas:
   ```bash
   ls metrics/verticales/data/verticales_{site}_{periodo}.parquet
   ```
3. Si NO existen → Genera:
   ```bash
   python metrics/verticales/generar_agregados.py --site MLA --periodo 2025-12
   ```
4. Consulta: **[verticales/README.md](verticales/README.md)** - Cómo usar en reportes

---

### **🚚 Quiero analizar demoras en Shipping (ME Distribución)**
1. ⭐ Lee: **[demoras/README.md](demoras/README.md)** - Visión general de métricas
2. Lee: **[demoras/FUENTE_DEMORAS.md](demoras/FUENTE_DEMORAS.md)** - ¿Qué son delays, custom offsets, buffering?
3. Genera query parametrizada:
   ```python
   python -m metrics.demoras.scripts.parametrize_shipping_query
   ```
4. Ejecuta query en BigQuery:
   ```powershell
   Get-Content sql/shipping_mla_nov_dic.sql -Raw | bq query --use_legacy_sql=false --format=csv > output/demoras_mla.csv
   ```
5. Consulta: **[demoras/INTEGRACION_CR.md](demoras/INTEGRACION_CR.md)** - Cómo correlacionar con CR

---

### **🚀 Quiero integrar hard metrics en mi script**
1. ⭐ Lee: **[INTEGRACION_GOLDEN_TEMPLATES.md](INTEGRACION_GOLDEN_TEMPLATES.md)**
2. Copia código de ejemplo (Paso 1-4)
3. Implementa fallback mechanism
4. Prueba con y sin métricas disponibles

---

### **📈 Quiero ver el valor del sistema (convencer a mi equipo)**
1. ⭐ Lee: **[COMPARATIVA.md](COMPARATIVA.md)**
2. Muestra:
   - Tabla de mejoras (16x performance, 100% precisión)
   - Casos reales con números
   - Análisis de costo-beneficio

---

### **🐛 Tengo un problema/error**
1. Busca tu error en: **[INTEGRACION_GOLDEN_TEMPLATES.md](INTEGRACION_GOLDEN_TEMPLATES.md)** (sección Troubleshooting)
2. Errores comunes:
   - FileNotFoundError → Genera métricas
   - JSON serialization → Convierte int64 a int
   - Quota exceeded → Configura proyecto BigQuery
3. Si no encuentras solución, consulta: **[eventos/CUANDO_REGENERAR.md](eventos/CUANDO_REGENERAR.md)** (sección Señales de Alerta)

---

### **🔍 Quiero ver ejemplos de código**
1. **[eventos/ejemplo_uso.py](eventos/ejemplo_uso.py)** - 4 ejemplos completos:
   - Golden Templates
   - Análisis cross-tipificación
   - Comparación cross-site
   - Validación de datos
2. **[INTEGRACION_GOLDEN_TEMPLATES.md](INTEGRACION_GOLDEN_TEMPLATES.md)** - Código paso a paso

---

### **📚 Quiero entender el sistema completo**
1. **Visión general:** [README.md](README.md)
2. **Arquitectura:** [eventos/README.md](eventos/README.md)
3. **Fuente de datos:** [eventos/FUENTE_EVENTOS.md](eventos/FUENTE_EVENTOS.md)
4. **Workflow:** [eventos/CUANDO_REGENERAR.md](eventos/CUANDO_REGENERAR.md)
5. **Comparativa:** [COMPARATIVA.md](COMPARATIVA.md)

---

## 📁 Mapa de Archivos

### **Documentación (lectura):**
```
metrics/
├── INDICE.md                          ← ESTÁS AQUÍ
├── README.md                          → Visión general
├── GUIA_USUARIO.md                    → Guía práctica ⭐ EMPEZAR AQUÍ
├── COMPARATIVA.md                     → Antes vs Después
├── INTEGRACION_GOLDEN_TEMPLATES.md    → Cómo integrar en scripts
│
├── eventos/
│   ├── README.md                      → Métricas de eventos (técnico)
│   ├── FUENTE_EVENTOS.md              → Tabla oficial LK_MKP_PROMOTIONS_EVENT
│   ├── CUANDO_REGENERAR.md            → Workflow de mantenimiento ⭐
│   └── data/
│       └── README.md                  → Qué contiene esta carpeta
│
├── verticales/
│   ├── README.md                      → Métricas de verticales (técnico)
│   ├── FUENTE_VERTICALES.md           → Qué son verticales y dominios
│   ├── CUANDO_REGENERAR.md            → Workflow de mantenimiento
│   └── data/
│       └── README.md                  → Qué contiene esta carpeta
│
└── demoras/                           → ⭐ NUEVA - Métricas de Shipping
    ├── README.md                      → Visión general de demoras
    ├── FUENTE_DEMORAS.md              → Tablas y campos de Shipping
    ├── CUANDO_REGENERAR.md            → Cuándo actualizar métricas
    ├── INTEGRACION_CR.md              → Relación con Contact Rate
    ├── sql/
    │   └── shipping_drivers_optimized_template.sql
    ├── scripts/
    │   └── parametrize_shipping_query.py
    └── data/
        └── (placeholder para futuros parquets)
```

### **Scripts (ejecución):**
```
metrics/eventos/
├── generar_correlaciones.py           → Genera métricas de eventos
└── ejemplo_uso.py                     → Ejemplos de código

metrics/verticales/
└── generar_agregados.py               → Genera métricas de verticales (próximamente)

metrics/demoras/scripts/
└── parametrize_shipping_query.py      → Genera queries parametrizadas de demoras
```

### **Datos (output):**
```
metrics/eventos/data/
├── correlacion_{site}_{periodo}.parquet    → Métricas (datos)
├── metadata_{site}_{periodo}.json          → Información (metadata)
└── .gitignore                              → Ignora .parquet, permite .json

metrics/verticales/data/
├── verticales_{site}_{periodo}.parquet     → Métricas (datos)
├── metadata_{site}_{periodo}.json          → Información (metadata)
└── .gitignore                              → Ignora .parquet, permite .json

metrics/demoras/data/
└── (placeholder para futuros parquets pre-calculados)
```

---

## 🎓 Rutas de Aprendizaje

### **Ruta 1: Usuario Casual (1 hora)**
```
1. GUIA_USUARIO.md (secciones 1-4)
2. Generar 1 métrica de ejemplo
3. Usar en 1 reporte
```

**Resultado:** Puedes usar hard metrics en tus reportes

---

### **Ruta 2: Analista Avanzado (3 horas)**
```
1. GUIA_USUARIO.md (completo)
2. eventos/README.md
3. INTEGRACION_GOLDEN_TEMPLATES.md
4. ejemplo_uso.py (ejecutar todos)
5. CUANDO_REGENERAR.md
```

**Resultado:** Puedes generar, usar y mantener métricas

---

### **Ruta 3: Mantenedor del Sistema (1 día)**
```
1. Toda la documentación en orden
2. Leer código de generar_correlaciones.py
3. Entender FUENTE_EVENTOS.md
4. CUANDO_REGENERAR.md (checklist completo)
5. Practicar regeneración en diferentes escenarios
```

**Resultado:** Puedes mantener y evolucionar el sistema

---

## 📋 Quick Reference Card

### **Comandos Esenciales:**

```bash
# Listar métricas disponibles
ls metrics/eventos/data/*.parquet

# Generar métrica nueva
python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12

# Ver metadata
cat metrics/eventos/data/metadata_mla_2025_12.json

# Validar métricas (Python)
python -c "import pandas as pd; df = pd.read_parquet('metrics/eventos/data/correlacion_mla_2025_12.parquet'); print(df.head())"

# Consultar tabla oficial de eventos
# (desde BigQuery console o script Python)
SELECT * FROM WHOWNER.LK_MKP_PROMOTIONS_EVENT WHERE SIT_SITE_ID = 'MLA'
```

---

## 🆘 Ayuda Rápida

| Problema | Solución |
|----------|----------|
| No encuentro las métricas | `ls metrics/eventos/data/` → Si vacío, genera métricas |
| Error al cargar parquet | Regenera métricas para ese site/período |
| Correlaciones raras | Lee `CUANDO_REGENERAR.md` sección "Señales de Alerta" |
| ¿Debo regenerar? | Consulta checklist en `eventos/CUANDO_REGENERAR.md` |
| ¿Cómo integro en mi script? | Código en `INTEGRACION_GOLDEN_TEMPLATES.md` |
| Ejemplos de código | `eventos/ejemplo_uso.py` |

---

## 📞 Próximos Pasos Sugeridos

Después de leer esta documentación:

1. **Prueba el sistema:**
   ```bash
   # Genera una métrica
   python metrics/eventos/generar_correlaciones.py --site MLA --periodo 2025-12
   
   # Úsala en un reporte
   python generar_golden_pdd_mla_tipificacion.py
   ```

2. **Comparte con tu equipo:**
   - Envía `GUIA_USUARIO.md` a nuevos usuarios
   - Envía `COMPARATIVA.md` a stakeholders (para mostrar valor)

3. **Documenta tu experiencia:**
   - ¿Encontraste algún problema?
   - ¿Falta alguna guía?
   - ¿Tienes sugerencias de mejora?

---

**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Mantenedor:** CR Analytics Team  
**Feedback:** Bienvenido para mejorar esta documentación
