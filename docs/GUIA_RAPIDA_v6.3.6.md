# Guía Rápida v6.3.6 - Espera Automática

**Nueva versión:** 6.3.6  
**Mejora principal:** Análisis completo en UNA SOLA EJECUCIÓN (sin re-ejecutar el script)

---

## 🎯 Lo Nuevo en 30 Segundos

El script ahora:
1. Exporta CSVs de conversaciones automáticamente
2. Te muestra un prompt para que solicites el análisis a Cursor AI
3. **ESPERA AUTOMÁTICAMENTE** hasta que generes el JSON
4. Cuando detecta el JSON → continúa automáticamente con el HTML completo

**Resultado:** TODO en una sola ejecución, sin pausas manuales ni re-ejecutar el script.

---

## 🚀 Cómo Usar

### Comando Único

```bash
py generar_reporte_cr_universal_v6.3.6.py --site MLM \
    --p1-start 2025-08-01 --p1-end 2025-08-31 \
    --p2-start 2025-09-01 --p2-end 2025-09-30 \
    --commerce-group GENERALES_COMPRA \
    --process-name "Loyalty" \
    --aperturas CDU \
    --open-report
```

### Qué Esperar Durante la Ejecución

**Paso 1-3:** Cálculo de métricas (igual que antes)

**Paso 4:** Análisis de conversaciones
```
[INFO] CSVs de conversaciones exportados:
  ✅ conversaciones_Bugs_mlm_202508.csv
  ✅ conversaciones_Administración_de_la_suscripción_mlm_202508.csv
  ✅ conversaciones_Problemas_con_la_suscripción___beneficio_mlm_202508.csv

📊 ANÁLISIS DE CONVERSACIONES EN PROGRESO
════════════════════════════════════════════════════════════════════════════════

[CURSOR AI] Por favor, analiza las conversaciones exportadas con este prompt:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analiza las conversaciones de los CSVs exportados en output/.
Genera el JSON: analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ESPERANDO] Monitoreando carpeta output/ esperando el JSON...
[ARCHIVO] analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
[TIMEOUT] 10 minutos máximo

  ⏳ Esperando análisis... (0 min transcurridos)
```

**TU ACCIÓN (en paralelo mientras el script espera):**
1. Copia el prompt que el script te mostró
2. Pégalo en Cursor AI (en la ventana de chat)
3. Espera a que Cursor AI genere el JSON

**Paso 5:** El script detecta el JSON y continúa automáticamente
```
✅ [OK] JSON detectado: analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
[CONTINUANDO] Cargando análisis y generando reporte completo...

[RELOADING] Recargando análisis con JSON detectado...
  [OK] 'Bugs': 3 causas raíz (cobertura: 85%)
  [OK] 'Administración de la suscripción': 2 causas raíz (cobertura: 90%)
  [OK] 'Problemas con la suscripción / beneficio': 4 causas raíz (cobertura: 95%)

[SUCCESS] Análisis completado exitosamente para 3 elementos

[HTML] Generando reporte HTML...
[OK] Reporte guardado: reporte_cr_loyalty_mlm_ago_sep_2025_v6.3.html
🌐 Abriendo reporte en navegador...
```

---

## ⚡ Ventajas vs v6.3.5

| Aspecto | v6.3.5 (Antes) | v6.3.6 (Ahora) |
|---------|----------------|----------------|
| **Ejecuciones del script** | 2 veces (export → analizar → re-ejecutar) | **1 vez** (todo automático) |
| **Intervención manual** | Re-ejecutar script después de análisis | **Ninguna** (espera automática) |
| **Tiempo de espera visible** | No (usuario debe recordar re-ejecutar) | **Sí** (feedback cada 30 seg) |
| **Riesgo de error** | Medio (olvidar re-ejecutar, usar parámetros diferentes) | **Bajo** (flujo único, parámetros garantizados) |
| **Experiencia de usuario** | Manual, requiere seguimiento | **Automática**, "fire and forget" |

---

## 🔄 Casos de Uso

### 1. Primera vez (sin JSON previo)

```bash
# Ejecutar una vez
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# Script exporta CSVs → muestra prompt → ESPERA
# Tú: copias el prompt y lo pegas a Cursor AI
# Cursor AI: genera el JSON
# Script: detecta JSON y continúa → genera HTML → abre navegador
```

### 2. Segunda vez (con JSON previo del mismo período)

```bash
# Ejecutar (mismo comando)
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# Script detecta JSON existente → NO espera → genera HTML directo → abre navegador
# ⏱️ Tiempo: ~3-5 min (sin polling)
```

### 3. Solo exportar CSVs (sin análisis)

```bash
# Si solo quieres los CSVs sin generar HTML
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --export-only

# Script exporta CSVs → sale inmediatamente (sin espera, sin HTML)
```

---

## 🛠️ Configuración Avanzada

### Ajustar Timeout (Si el Análisis Tarda Más de 10 min)

Editar línea ~1254 en `generar_reporte_cr_universal_v6.3.6.py`:

```python
# Cambiar de 600 (10 min) a 900 (15 min)
timeout_seconds=900,  # 15 minutos
```

### Ajustar Frecuencia de Verificación

Editar línea ~1255:

```python
# Cambiar de 5 segundos a 3 segundos (verificación más frecuente)
check_interval=3
```

**Nota:** No recomendamos menos de 3 segundos (puede sobrecargar I/O del sistema).

---

## ❓ FAQ

### ¿Qué pasa si no genero el JSON a tiempo?

El script esperará 10 minutos (configurable) y luego:
- Mostrará un warning de timeout
- Generará el HTML **sin análisis comparativo** (reporte básico)
- Te sugerirá cómo completar el análisis después

**No falla, degrada elegantemente.**

### ¿Puedo desactivar la espera automática?

Sí, usa `--export-only` para exportar CSVs y salir inmediatamente:

```bash
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --export-only
```

### ¿Funciona con cualquier dimensión?

**Sí**, funciona con:
- PROCESO
- CDU
- TIPIFICACION
- ENVIRONMENT
- SOLUTION_ID
- CHANNEL_ID
- SOURCE_ID

La espera automática es **universal**.

### ¿Qué pasa si el JSON ya existe?

Si el JSON ya existe de una ejecución previa:
- El script lo detecta inmediatamente
- **NO entra en modo de espera**
- Genera el HTML directamente
- ⏱️ Tiempo: ~3-5 minutos (sin polling)

---

## 📝 Resumen

**Una línea:**
```bash
# TODO en una sola ejecución - exportar + esperar + analizar + HTML
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report
```

**Lo que hace:**
1. ✅ Calcula métricas
2. ✅ Exporta CSVs
3. ✅ **Espera automáticamente** (polling)
4. ✅ Detecta JSON cuando lo generas
5. ✅ Recarga análisis
6. ✅ Genera HTML completo
7. ✅ Abre navegador

**Sin intervención manual. Sin re-ejecutar. Todo automático.** 🚀

---

**¿Preguntas?** Consulta el [CHANGELOG_v6.3.6.md](./CHANGELOG_v6.3.6.md) para detalles técnicos completos.
