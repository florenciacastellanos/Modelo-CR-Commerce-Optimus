# 📘 Guía de Migración v6.3.5 - Auto-detección de Dimensión

**Para usuarios existentes del repositorio CR Commerce**

---

## 🎯 ¿Qué Cambió?

El script **ahora detecta automáticamente** qué dimensión usar para el análisis de conversaciones basándose en las aperturas que solicitas.

### ❌ Antes (v6.3.4)
```bash
# Si pedías solo CDU, fallaba porque buscaba PROCESO por defecto
py generar_reporte_cr_universal_v6.3.py --aperturas CDU ...

# Output:
# [WARNING] Dimensión 'PROCESO' no existe en cuadros cuantitativos
# [INFO] Saltando análisis de conversaciones  ❌
```

### ✅ Ahora (v6.3.5)
```bash
# Detecta automáticamente que CDU es la más granular
py generar_reporte_cr_universal_v6.3.py --aperturas CDU ...

# Output:
# [AUTO] Dimensión de muestreo detectada automáticamente: CDU
# [OK] Análisis de conversaciones por CDU  ✅
```

---

## 🔄 ¿Necesito Cambiar Mis Comandos?

### **NO** - Los comandos existentes siguen funcionando igual

**Tus scripts actuales son 100% compatibles:**

```bash
# Esto sigue funcionando igual que antes
py generar_reporte_cr_universal_v6.3.py --site MLA --commerce-group PDD \
    --aperturas PROCESO,CDU --muestreo-dimension CDU ...
```

### **SÍ** - Puedes simplificar comandos nuevos

**Ahora puedes omitir `--muestreo-dimension`:**

```bash
# Antes (v6.3.4)
py generar_reporte_cr_universal_v6.3.py --site MLM --commerce-group GENERALES_COMPRA \
    --aperturas CDU --muestreo-dimension CDU  # ← Redundante

# Ahora (v6.3.5) - Más simple
py generar_reporte_cr_universal_v6.3.py --site MLM --commerce-group GENERALES_COMPRA \
    --aperturas CDU  # ← Auto-detecta CDU
```

---

## 📊 Jerarquía de Granularidad (Auto-detección)

El sistema usa esta jerarquía para elegir la dimensión más específica:

```
CLA_REASON_DETAIL      (6) ← Más granular
    ↓
SOLUTION_ID / CHANNEL_ID / SOURCE_ID  (5)
    ↓
ENVIRONMENT            (4)
    ↓
TIPIFICACION           (3)
    ↓
CDU                    (2)
    ↓
PROCESO                (1) ← Menos granular
```

### Ejemplos de Auto-detección

| Comando | Dimensión Detectada | Razón |
|---------|---------------------|-------|
| `--aperturas PROCESO` | PROCESO | Es la única |
| `--aperturas CDU` | CDU | Es la única |
| `--aperturas PROCESO,CDU` | **CDU** | CDU es más granular que PROCESO |
| `--aperturas CDU,TIPIFICACION` | **TIPIFICACION** | TIPIFICACION es más granular que CDU |
| `--aperturas PROCESO,CDU,TIPIFICACION` | **TIPIFICACION** | Es la más granular de las 3 |

---

## 📁 Nombres de Archivos JSON - CAMBIO IMPORTANTE

### ⚠️ Los JSONs ahora incluyen la dimensión en el nombre

**Antes (v6.3.4):**
```
analisis_conversaciones_claude_mlm_generales_compra_2025-08_2025-09.json
```

**Ahora (v6.3.5):**
```
analisis_conversaciones_claude_mlm_generales_compra_cdu_2025-08_2025-09.json
                                                       ^^^^ ← Nueva parte
```

### ¿Por qué?

Evita **conflictos** cuando analizas el mismo commerce group con diferentes dimensiones:

```
# Ahora puedes tener ambos sin conflictos:
analisis_conversaciones_claude_mla_pdd_proceso_2025-11_2025-12.json
analisis_conversaciones_claude_mla_pdd_cdu_2025-11_2025-12.json
analisis_conversaciones_claude_mla_pdd_tipificacion_2025-11_2025-12.json
```

### ¿Qué hacer con JSONs antiguos?

**Opción 1: Dejarlos (recomendado)**
- Los JSONs antiguos se ignoran automáticamente
- El script buscará/generará el nuevo formato

**Opción 2: Renombrarlos (opcional)**
```bash
# Si tenías un JSON antiguo de análisis por PROCESO:
mv analisis_conversaciones_claude_mla_pdd_2025-11_2025-12.json \
   analisis_conversaciones_claude_mla_pdd_proceso_2025-11_2025-12.json
```

---

## 🧪 Validación Rápida

### Test 1: CDU Solo (Caso de uso original)
```bash
py generar_reporte_cr_universal_v6.3.py --site MLM --p1-start 2025-08-01 --p1-end 2025-08-31 \
    --p2-start 2025-09-01 --p2-end 2025-09-30 --commerce-group GENERALES_COMPRA \
    --process-name "Loyalty" --aperturas CDU --open-report
```

**Esperado:**
- ✅ `[AUTO] Dimensión de muestreo detectada automáticamente: CDU`
- ✅ Analiza conversaciones por CDU
- ✅ JSON generado con nombre: `..._cdu_2025-08_2025-09.json`

### Test 2: Múltiples Dimensiones
```bash
py generar_reporte_cr_universal_v6.3.py --site MLA --p1-start 2025-11-01 --p1-end 2025-11-30 \
    --p2-start 2025-12-01 --p2-end 2025-12-31 --commerce-group PDD \
    --aperturas PROCESO,CDU,TIPIFICACION --open-report
```

**Esperado:**
- ✅ `[AUTO] Dimensión de muestreo detectada automáticamente: TIPIFICACION`
- ✅ Analiza conversaciones por TIPIFICACION (la más granular)
- ✅ JSON: `..._tipificacion_2025-11_2025-12.json`

### Test 3: Override Manual
```bash
py generar_reporte_cr_universal_v6.3.py --site MLA --commerce-group PDD \
    --aperturas PROCESO,CDU,TIPIFICACION --muestreo-dimension PROCESO --open-report
```

**Esperado:**
- ✅ Respeta el override: usa PROCESO (no auto-detecta)
- ✅ JSON: `..._proceso_2025-11_2025-12.json`

---

## ❓ FAQ

### ¿Mis scripts existentes dejan de funcionar?
**NO.** Son 100% compatibles. Si ya especificas `--muestreo-dimension`, se respeta.

### ¿Necesito regenerar JSONs antiguos?
**NO.** El sistema busca el nuevo formato automáticamente. Si no existe, analiza de nuevo.

### ¿Qué pasa si tengo JSONs antiguos sin dimensión en el nombre?
El script los ignora y busca/genera el nuevo formato con dimensión incluida.

### ¿Puedo forzar una dimensión específica?
**SÍ.** Usa `--muestreo-dimension NOMBRE_DIMENSION` para forzar una dimensión.

### ¿Qué pasa si no especifico aperturas reconocidas?
Usa PROCESO como fallback (comportamiento seguro).

---

## 🎓 Buenas Prácticas

### ✅ Recomendado
```bash
# Dejar que el sistema auto-detecte (más simple)
--aperturas CDU

# O especificar múltiples y dejar que elija la más granular
--aperturas PROCESO,CDU,TIPIFICACION
```

### ⚠️ Solo cuando necesites
```bash
# Forzar una dimensión menos granular (casos especiales)
--aperturas CDU,TIPIFICACION --muestreo-dimension CDU
```

### ❌ Evitar
```bash
# Redundante (el sistema ya lo detecta)
--aperturas CDU --muestreo-dimension CDU  # ← Funciona pero es redundante
```

---

## 📞 Soporte

**Si algo no funciona como esperabas:**

1. Verifica que estés usando v6.3.5:
   ```bash
   py generar_reporte_cr_universal_v6.3.py --help | Select-String "v6.3.5"
   ```

2. Revisa el output del script en `[AUTO]` o `[CONFIG] Dimensión muestreo:`

3. Comprueba el nombre del JSON generado en `output/`

4. Consulta: `docs/CHANGELOG_v6.3.5.md` para detalles técnicos

---

**Última actualización:** 2 Febrero 2026  
**Versión:** 6.3.5  
**Status:** ✅ ACTIVO
