# Migración a v6.3.6 - Espera Automática

**Fecha:** 2 Febrero 2026  
**De:** v6.3.5 → v6.3.6  
**Tipo:** Feature Enhancement (sin breaking changes)

---

## 🎯 Cambio Principal

**v6.3.6 introduce espera automática para análisis de conversaciones**, eliminando la necesidad de ejecutar el script dos veces.

### Antes (v6.3.5)

```bash
# Paso 1: Exportar
py generar_reporte_cr_universal_v6.3.py ... --export-only

# Paso 2: Usuario solicita a Cursor AI que analice (manual)

# Paso 3: Re-ejecutar
py generar_reporte_cr_universal_v6.3.py ... --open-report
```

**Problema:** 3 pasos, 2 ejecuciones, manual

### Ahora (v6.3.6)

```bash
# UN SOLO COMANDO
py generar_reporte_cr_universal_v6.3.6.py ... --open-report

# El script:
# 1. Exporta CSVs
# 2. Muestra prompt para Cursor AI
# 3. ESPERA automáticamente (polling)
# 4. Detecta JSON
# 5. Recarga análisis
# 6. Genera HTML completo
# 7. Abre navegador
```

**Beneficio:** 1 comando, 1 ejecución, automático

---

## 📦 Qué Incluye esta Versión

### Archivos Nuevos

1. **`generar_reporte_cr_universal_v6.3.6.py`**
   - Script principal con espera automática
   - Función `esperar_analisis_conversaciones()` (líneas ~216-259)
   - Sección de espera automática en PASO 5 (líneas ~1240-1296)

2. **`docs/CHANGELOG_v6.3.6.md`**
   - Changelog completo con detalles técnicos

3. **`docs/GUIA_RAPIDA_v6.3.6.md`**
   - Guía de usuario rápida (30 segundos)

4. **`docs/MIGRACION_v6.3.6.md`**
   - Este archivo (guía de migración)

### Archivos Actualizados

1. **`.cursorrules`**
   - Version: 5.2 (Universal v6.3.6)
   - Protocolo actualizado con flujo automático
   - Referencias actualizadas a v6.3.6
   - Tabla de referencias con nuevas guías

---

## 🔧 Cambios Técnicos

### Nueva Función: `esperar_analisis_conversaciones()`

```python
def esperar_analisis_conversaciones(json_path, elementos_priorizados, timeout_seconds=600, check_interval=5):
    """
    Espera automáticamente hasta que se genere el JSON de análisis de conversaciones.
    
    - Polling cada 5 segundos
    - Feedback cada 30 segundos
    - Timeout configurable (default: 10 min)
    - Degradación elegante si timeout
    """
```

### Nueva Sección en PASO 5: "ESPERA AUTOMÁTICA PARA ANÁLISIS (v6.3.6)"

Ubicación: después de guardar CSVs, antes de generar HTML

**Lógica:**
```python
if not USE_CLAUDE_ANALYSIS and len(conversaciones_por_proceso) > 0 and not args.export_only:
    # Mostrar CSVs exportados
    # Llamar a esperar_analisis_conversaciones()
    # Si se detecta JSON:
        # Reconfigurar análisis
        # Re-ejecutar analyze_conversations_with_llm()
        # Actualizar conversaciones_por_proceso
```

---

## ✅ Checklist de Migración

### Para Usuarios

- [x] Actualizar comando de `v6.3.py` a `v6.3.6.py`
- [x] Leer guía rápida: `docs/GUIA_RAPIDA_v6.3.6.md`
- [x] Probar con caso existente (con JSON previo)
- [x] Probar con caso nuevo (sin JSON previo)

### Para Desarrolladores

- [x] Script principal renombrado a `v6.3.6.py`
- [x] Función `esperar_analisis_conversaciones()` agregada
- [x] Sección de espera automática implementada
- [x] Versión actualizada en docstring y prints
- [x] `.cursorrules` actualizado a versión 5.2
- [x] Changelog creado (`CHANGELOG_v6.3.6.md`)
- [x] Guía rápida creada (`GUIA_RAPIDA_v6.3.6.md`)
- [x] Guía de migración creada (este archivo)

---

## 🧪 Testing

### Caso 1: JSON No Existe (Flujo Nuevo)

```bash
# Pre-condición: Eliminar JSON previo
rm output/analisis_conversaciones_claude_*.json

# Ejecutar
py generar_reporte_cr_universal_v6.3.6.py --site MLM \
    --p1-start 2025-08-01 --p1-end 2025-08-31 \
    --p2-start 2025-09-01 --p2-end 2025-09-30 \
    --commerce-group GENERALES_COMPRA \
    --process-name "Loyalty" \
    --aperturas CDU \
    --open-report
```

**Resultado esperado:**
- ✅ Exporta CSVs
- ✅ Muestra prompt para Cursor AI
- ✅ Entra en espera (polling cada 5 seg)
- ✅ Usuario solicita análisis a Cursor AI
- ✅ Script detecta JSON automáticamente
- ✅ Recarga análisis
- ✅ Genera HTML completo
- ✅ Abre navegador

### Caso 2: JSON Existe (Sin Espera)

```bash
# Pre-condición: JSON existe de ejecución previa

# Ejecutar (mismo comando)
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --open-report
```

**Resultado esperado:**
- ✅ NO entra en espera
- ✅ Carga JSON directamente
- ✅ Genera HTML completo
- ⏱️ Tiempo: ~3-5 min (sin polling)

### Caso 3: Modo Export-Only (Preservado)

```bash
py generar_reporte_cr_universal_v6.3.6.py --site MLM ... --export-only
```

**Resultado esperado:**
- ✅ Exporta CSVs
- ✅ Sale inmediatamente
- ✅ NO entra en espera
- ✅ NO genera HTML

---

## 🔄 Retrocompatibilidad

### ✅ 100% Compatible con v6.3.5

| Feature | v6.3.5 | v6.3.6 | Compatible |
|---------|--------|--------|------------|
| Todos los argumentos CLI | ✅ | ✅ | ✅ 100% |
| Modo `--export-only` | ✅ | ✅ | ✅ Preservado |
| JSON naming con dimensión | ✅ | ✅ | ✅ Igual |
| Carga de JSON existente | ✅ | ✅ | ✅ Sin cambios |
| Análisis comparativo | ✅ | ✅ | ✅ Sin cambios |
| Hard metrics | ✅ | ✅ | ✅ Sin cambios |
| **Espera automática** | ❌ | ✅ | ➕ NUEVO |

### No Requiere Cambios de Código

Los scripts que llaman al generador pueden seguir usando los mismos argumentos:

```bash
# Funciona igual en v6.3.5 y v6.3.6
--site MLM \
--p1-start 2025-08-01 \
--p1-end 2025-08-31 \
--p2-start 2025-09-01 \
--p2-end 2025-09-30 \
--commerce-group GENERALES_COMPRA \
--process-name "Loyalty" \
--aperturas CDU \
--open-report
```

**Único cambio:** Nombre del script (`v6.3.py` → `v6.3.6.py`)

---

## 📊 Comparación de Flujos

| Aspecto | v6.3.5 | v6.3.6 |
|---------|--------|--------|
| **Ejecuciones del script** | 2 | 1 ✅ |
| **Pasos manuales** | 3 | 1 ✅ |
| **Intervención del usuario** | Re-ejecutar | Copiar prompt ✅ |
| **Tiempo de espera visible** | No | Sí (feedback cada 30s) ✅ |
| **Riesgo de error** | Medio | Bajo ✅ |
| **Experiencia** | Manual | Automática ✅ |

---

## 🚀 Beneficios

1. **✅ Menos fricción**: Un comando vs múltiples pasos
2. **✅ Menos errores**: No olvidar re-ejecutar con parámetros diferentes
3. **✅ Más claridad**: El usuario ve que el script está esperando
4. **✅ Más eficiencia**: Paralelización natural (script espera, usuario solicita análisis)
5. **✅ Más robustez**: Degradación elegante si timeout

---

## 📝 Próximos Pasos

### Para Usuarios

1. Leer **`docs/GUIA_RAPIDA_v6.3.6.md`** (2 minutos)
2. Probar un análisis completo con el nuevo flujo
3. Verificar que el HTML generado incluye análisis comparativo
4. Usar `v6.3.6.py` en futuros análisis

### Para Desarrolladores

1. Leer **`docs/CHANGELOG_v6.3.6.md`** (detalles técnicos)
2. Revisar implementación de `esperar_analisis_conversaciones()`
3. Considerar ajustes de timeout si es necesario (línea ~1254)
4. Documentar casos de uso específicos de tu equipo

---

## ❓ FAQ

### ¿Puedo seguir usando v6.3.5?

Sí, pero **v6.3.6 es más eficiente** y recomendado para nuevos análisis.

### ¿Tengo que cambiar algo en mis scripts?

Solo el nombre del archivo:
- Antes: `py generar_reporte_cr_universal_v6.3.py ...`
- Ahora: `py generar_reporte_cr_universal_v6.3.6.py ...`

### ¿Qué pasa si no quiero la espera automática?

Usa `--export-only` para salir después de exportar CSVs (sin espera).

### ¿La espera es configurable?

Sí, edita líneas ~1254-1255 en el script:
```python
timeout_seconds=900,  # Cambiar de 600 (10 min) a 900 (15 min)
check_interval=3      # Cambiar de 5 seg a 3 seg
```

### ¿Funciona con todas las dimensiones?

**Sí**, funciona con:
- PROCESO
- CDU
- TIPIFICACION
- ENVIRONMENT
- SOLUTION_ID
- CHANNEL_ID
- SOURCE_ID

---

## 📚 Recursos

- **Guía Rápida:** `docs/GUIA_RAPIDA_v6.3.6.md`
- **Changelog:** `docs/CHANGELOG_v6.3.6.md`
- **Script:** `generar_reporte_cr_universal_v6.3.6.py`
- **Rules:** `.cursorrules` (version 5.2)

---

**¿Preguntas?** Consulta el **`CHANGELOG_v6.3.6.md`** para detalles técnicos completos.
