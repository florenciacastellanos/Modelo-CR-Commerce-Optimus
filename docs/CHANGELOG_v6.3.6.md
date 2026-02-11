# Changelog v6.3.6 - Espera Automática para Análisis de Conversaciones

**Fecha:** 2 Febrero 2026  
**Versión:** 6.3.6  
**Tipo:** Feature Enhancement  

---

## 🎯 Resumen Ejecutivo

La v6.3.6 introduce **espera automática con polling** para análisis de conversaciones, eliminando la necesidad de ejecutar el script múltiples veces. Ahora el script exporta CSVs, espera automáticamente a que Cursor AI genere el JSON de análisis, y continúa con la generación del HTML completo **en una sola ejecución**.

---

## ✨ Nuevas Características

### 1. **Espera Automática con Polling** (Feature Principal)

El script ahora:
- ✅ Detecta cuando NO existe un JSON de análisis previo
- ✅ Exporta los CSVs de conversaciones automáticamente
- ✅ Muestra un prompt claro para que el usuario solicite el análisis a Cursor AI
- ✅ **Espera automáticamente** (polling cada 5 segundos) hasta detectar el JSON
- ✅ Recarga el análisis automáticamente cuando se detecta el JSON
- ✅ Continúa con la generación del HTML completo (incluyendo análisis comparativo)
- ✅ Todo en **una sola ejecución del script**

**Código nuevo:**
```python
def esperar_analisis_conversaciones(json_path, elementos_priorizados, timeout_seconds=600, check_interval=5):
    """
    Espera automáticamente hasta que se genere el JSON de análisis de conversaciones.
    """
    # Polling loop con feedback visual cada 30 segundos
    # Timeout configurable (default: 10 minutos)
    # Degradación elegante si no se detecta el JSON
```

### 2. **Flujo Completamente Automático**

**Antes (v6.3.5):**
```bash
# Paso 1: Exportar CSVs
py generar_reporte_cr_universal_v6.3.py ... --export-only

# Paso 2: Usuario solicita a Cursor AI que analice
# (manualmente)

# Paso 3: Re-ejecutar script completo
py generar_reporte_cr_universal_v6.3.py ... --open-report
```

**Ahora (v6.3.6):**
```bash
# UN SOLO COMANDO - TODO AUTOMÁTICO
py generar_reporte_cr_universal_v6.3.6.py --site MLM --p1-start 2025-08-01 --p1-end 2025-08-31 \
    --p2-start 2025-09-01 --p2-end 2025-09-30 --commerce-group GENERALES_COMPRA \
    --process-name "Loyalty" --aperturas CDU --open-report

# El script:
# 1. Exporta CSVs → 2. Muestra prompt para Cursor AI → 3. ESPERA automáticamente →
# 4. Detecta JSON → 5. Recarga análisis → 6. Genera HTML completo → 7. Abre navegador
```

### 3. **Feedback Visual en Tiempo Real**

Durante la espera, el script muestra:
```
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
  ⏳ Esperando análisis... (0 min transcurridos)
  ⏳ Esperando análisis... (1 min transcurridos)

✅ [OK] JSON detectado: analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
[CONTINUANDO] Cargando análisis y generando reporte completo...
```

### 4. **Degradación Elegante con Timeout**

Si no se detecta el JSON después de 10 minutos:
- ⚠️ Muestra advertencia de timeout
- ✅ Continúa generando el reporte **sin análisis comparativo** (no falla)
- 💡 Sugiere al usuario cómo completar el análisis manualmente después

---

## 🔧 Cambios Técnicos

### Nuevas Funciones

1. **`esperar_analisis_conversaciones()`** (líneas ~216-259)
   - Polling loop con timeout configurable
   - Feedback visual cada 30 segundos
   - Retorna `True` si detecta JSON, `False` si timeout

### Modificaciones en Flujo Principal

2. **PASO 5: GENERACIÓN HTML** (líneas ~1240-1296)
   - **NUEVO:** Sección "ESPERA AUTOMÁTICA PARA ANÁLISIS (v6.3.6)"
   - Detecta cuando `USE_CLAUDE_ANALYSIS == False` y hay conversaciones
   - Llama a `esperar_analisis_conversaciones()`
   - Si se detecta JSON:
     - Reconfigura con `configurar_analisis_claude()` de nuevo
     - Re-ejecuta `analyze_conversations_with_llm()` para todos los elementos
     - Actualiza `conversaciones_por_proceso` con análisis completo

### Parámetros Configurables

```python
# En llamada a esperar_analisis_conversaciones()
timeout_seconds=600   # 10 minutos (ajustable según necesidad)
check_interval=5      # Verificar cada 5 segundos
```

---

## 🎯 Beneficios

### Para el Usuario

1. **✅ Una sola ejecución**: No más "ejecutar → analizar → re-ejecutar"
2. **✅ Sin intervención manual**: El script espera automáticamente
3. **✅ Feedback constante**: El usuario sabe que el script está activo
4. **✅ Robustez**: Si algo falla, el script no se rompe (genera reporte básico)
5. **✅ Repetibilidad**: Fácil re-ejecutar si es necesario

### Para el Sistema

1. **✅ Universal**: Funciona con cualquier dimensión (PROCESO, CDU, TIPIFICACION, ENVIRONMENT)
2. **✅ Backward compatible**: No rompe funcionalidad existente
3. **✅ Modo export-only preservado**: Para casos donde se necesita exportar y analizar después
4. **✅ Sin dependencias externas**: Solo usa Cursor AI (sin APIs adicionales)

---

## 📋 Casos de Uso

### Caso 1: Análisis Completo Automático (Nuevo Flujo)

```bash
# ÚNICA ejecución necesaria
py generar_reporte_cr_universal_v6.3.6.py --site MLM \
    --p1-start 2025-08-01 --p1-end 2025-08-31 \
    --p2-start 2025-09-01 --p2-end 2025-09-30 \
    --commerce-group GENERALES_COMPRA \
    --process-name "Loyalty" \
    --aperturas CDU \
    --open-report

# El script:
# 1. Calcula métricas cuantitativas
# 2. Exporta CSVs de conversaciones
# 3. Muestra prompt para Cursor AI
# 4. ESPERA automáticamente (polling)
# 5. Usuario pega prompt a Cursor AI en paralelo
# 6. Cursor AI genera JSON
# 7. Script detecta JSON y continúa
# 8. Genera HTML completo con análisis comparativo
# 9. Abre navegador
```

### Caso 2: Con JSON Previo (Comportamiento Existente)

```bash
# Si ya existe el JSON → ejecución inmediata (sin espera)
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# Flujo:
# 1. Detecta JSON existente
# 2. Carga análisis directamente
# 3. Genera HTML completo
# 4. Abre navegador
# ⏱️ Tiempo: ~3-5 minutos (sin polling)
```

### Caso 3: Modo Export-Only (Preservado)

```bash
# Si solo se quiere exportar CSVs → sin espera
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --export-only

# Flujo:
# 1. Exporta CSVs
# 2. Sale inmediatamente (sin espera, sin HTML)
```

---

## 🔄 Compatibilidad

### Retrocompatibilidad

- ✅ **100% compatible con v6.3.5**: Todos los argumentos funcionan igual
- ✅ **Preserva modo `--export-only`**: No se activa espera en este modo
- ✅ **Preserva comportamiento con JSON existente**: Si existe JSON → sin espera
- ✅ **JSON naming v6.3.5**: Sigue usando nombres únicos por dimensión

### Migración desde v6.3.5

**No requiere cambios de código.** Solo actualizar el comando:

```bash
# Antes (v6.3.5)
py generar_reporte_cr_universal_v6.3.py ...

# Ahora (v6.3.6)
py generar_reporte_cr_universal_v6.3.6.py ...
```

---

## 📝 Testing

### Escenario 1: JSON No Existe (Flujo Nuevo)

```bash
# Pre-condición: Eliminar JSON previo
rm output/analisis_conversaciones_claude_*.json

# Ejecutar
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# Resultado esperado:
# - Exporta CSVs ✅
# - Muestra prompt ✅
# - Entra en espera ✅
# - Usuario solicita análisis a Cursor AI
# - JSON se genera
# - Script detecta JSON ✅
# - Recarga análisis ✅
# - Genera HTML completo ✅
```

### Escenario 2: JSON Existe (Sin Espera)

```bash
# Pre-condición: JSON existe de ejecución previa

# Ejecutar
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# Resultado esperado:
# - NO entra en espera ✅
# - Carga JSON directamente ✅
# - Genera HTML completo ✅
# ⏱️ Tiempo: ~3-5 min (sin polling)
```

### Escenario 3: Timeout (Degradación Elegante)

```bash
# Ejecutar SIN generar el JSON (probar timeout)
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report

# NO solicitar análisis a Cursor AI (forzar timeout)

# Resultado esperado (después de 10 min):
# - Muestra warning de timeout ✅
# - Genera HTML básico (sin análisis comparativo) ✅
# - NO falla ✅
# - Sugiere cómo completar manualmente ✅
```

---

## 🐛 Bugs Corregidos

Ninguno. Esta versión solo agrega funcionalidad nueva sin modificar existente.

---

## 📚 Documentación Actualizada

1. **README.md**: Actualizar sección "Usage" con flujo v6.3.6
2. **GOLDEN_TEMPLATES.md**: Referenciar v6.3.6 como template actual
3. **.cursorrules**: Actualizar protocolo de ejecución para mencionar espera automática

---

## 🚀 Próximos Pasos

### Para v6.3.7 (Futuro)

- [ ] Configuración de timeout desde CLI (`--timeout-minutes`)
- [ ] Notificación sonora cuando se detecta el JSON (opcional)
- [ ] Guardar log de polling para debugging
- [ ] Soporte para múltiples JSONs en paralelo (análisis multi-site)

---

## 📌 Notas Importantes

1. **Timeout por defecto: 10 minutos**
   - Ajustable modificando `timeout_seconds=600` en línea ~1254
   - Para análisis muy grandes, considerar aumentar a 900 (15 min)

2. **Intervalo de verificación: 5 segundos**
   - Ajustable modificando `check_interval=5` en línea ~1255
   - No se recomienda menos de 3 segundos (puede sobrecargar I/O)

3. **Progress feedback: cada 30 segundos**
   - Definido en `progress_interval = 30` (línea ~239)
   - Para feedback más frecuente, reducir a 15 o 20 segundos

4. **La espera NO se activa si:**
   - Ya existe el JSON previo (carga directa)
   - Se usa `--export-only` (salida temprana)
   - Se usa `--skip-conversations` (sin análisis)

---

**Autor:** CR Commerce Analytics Team  
**Review:** ✅ Aprobado  
**Status:** 🚀 Production Ready
