# 🧹 Guía de Mantenimiento del Repositorio

**Versión:** 1.0  
**Fecha:** Enero 2026  
**Objetivo:** Mantener el repositorio limpio y organizado post-limpieza v4.0

---

## 🎯 Filosofía de Mantenimiento

**Principio básico:** **"Si no lo usas en producción, no lo guardes"**

Este repositorio debe mantenerse:
- ✅ **Limpio** - Solo archivos necesarios
- ✅ **Claro** - Estructura lógica y fácil navegación
- ✅ **Actualizado** - Documentación sincronizada con código
- ✅ **Profesional** - Listo para nuevos usuarios en cualquier momento

---

## ⚠️ REGLAS DE ORO (NUNCA ROMPER)

### **Regla 1: NO Scripts de Testing en Raíz**

**❌ MAL:**
```
CR COMMERCE/
├── test_nueva_feature.py
├── validar_datos_temporal.py
├── debug_problema_x.py
└── ...
```

**✅ BIEN:**
```
CR COMMERCE/
└── (solo scripts Golden Templates en raíz)

# Scripts temporales:
/temp/ (carpeta temporal, no commiteada, en .gitignore)
```

**Acción:** Si necesitas probar algo, crea carpeta `/temp/` local y NO la commitees.

---

### **Regla 2: NO Múltiples Versiones del Mismo Script**

**❌ MAL:**
```
generar_reporte_pdd.py
generar_reporte_pdd_v2.py
generar_reporte_pdd_v3.py
generar_reporte_pdd_final.py
generar_reporte_pdd_final_REAL.py  <-- ¿Cuál uso?
```

**✅ BIEN:**
```
generar_golden_pdd_mla_tipificacion.py  <-- Único, actual
```

**Acción:** Cuando mejores un script, **REEMPLAZA** el archivo, no crees v2. Git ya guarda el historial.

---

### **Regla 3: NO Reportes HTML en Raíz**

**❌ MAL:**
```
CR COMMERCE/
├── reporte-test-1.html
├── reporte-test-2.html
├── reporte-final.html
└── ...  (30+ reportes)
```

**✅ BIEN:**
```
CR COMMERCE/
└── output/
    └── rca/
        └── post-compra/
            └── pdd/
                └── golden-pdd-mla-nov-dic-2025.html
```

**Acción:** TODOS los outputs van a `/output/`. NUNCA en raíz.

---

### **Regla 4: Consolidar Changelogs**

**❌ MAL:**
```
CHANGELOG_BASE_FILTERS.md
CHANGELOG_CONTACT_DATE.md
CHANGELOG_v3.5.md
CHANGELOG_v3.6.md
CHANGELOG_v3.7_FEATURE_A.md
CHANGELOG_v3.7_FEATURE_B.md
CHANGELOG_v3.8.md
...
```

**✅ BIEN:**
```
CHANGELOG.md                      # Histórico consolidado
CHANGELOG_v4.0_HARD_METRICS.md   # Último release importante
```

**Acción:** Cuando hagas un release importante, consolida info en `CHANGELOG.md` y elimina changelogs viejos.

---

### **Regla 5: `.cursorrules` Máximo 600 Líneas**

**❌ MAL:**
```
.cursorrules con 1,500 líneas:
- Ejemplos SQL completos
- Listas exhaustivas
- Historia del proyecto
- Contenido duplicado de docs
```

**✅ BIEN:**
```
.cursorrules con ~450 líneas:
- Reglas críticas concisas
- Referencias a docs detallados
- Quick reference table
- Protocol claro
```

**Acción:** Revisión trimestral. Si crece >600 líneas, simplificar.

---

## 📋 Checklist Mensual de Mantenimiento

### **Primera semana de cada mes:**

- [ ] **Revisar carpeta raíz** - ¿Hay scripts nuevos que deberían moverse?
- [ ] **Revisar /output/** - ¿Hay reportes viejos que eliminar?
- [ ] **Verificar .cursorrules** - ¿Líneas < 600? ¿Contenido relevante?
- [ ] **Actualizar CHANGELOG.md** - ¿Cambios del mes anterior documentados?
- [ ] **Revisar scripts Golden Templates** - ¿Todos usando v4.0 hard metrics?

---

## 🗂️ Organización de Archivos por Tipo

### **Scripts de Producción (Golden Templates):**
**Ubicación:** Raíz del repositorio  
**Naming:** `generar_golden_{commerce_group}_{site}.py`  
**Ejemplos:**
```
✅ generar_golden_pdd_mla_tipificacion.py
✅ generar_golden_pnr_mlb.py
✅ generar_cr_generales_compra_mla.py
```

---

### **Scripts de Hard Metrics:**
**Ubicación:** `/metrics/eventos/`  
**Naming:** Descriptivo y claro  
**Ejemplos:**
```
✅ generar_correlaciones.py
✅ ejemplo_uso.py
```

---

### **Scripts Experimentales/Testing:**
**Ubicación:** `/temp/` (local, NO commitear)  
**Acción:** Eliminar después de validar  
**Ejemplos:**
```
/temp/
├── test_nueva_logica.py
├── validar_datos_diciembre.py
└── debug_evento_nuevo.py

# Agregar a .gitignore:
/temp/
```

---

### **Reportes Generados:**
**Ubicación:** `/output/rca/{business_unit}/{commerce_group}/`  
**Naming:** `golden-{commerce_group}-{site}-{periodo}.html`  
**Ejemplos:**
```
/output/
└── rca/
    ├── post-compra/
    │   ├── pdd/
    │   │   └── golden-pdd-mla-nov-dic-2025.html
    │   └── pnr/
    │       └── golden-pnr-mlb-nov-dic-2025.html
    ├── marketplace/
    └── shipping/
```

---

### **Documentación:**
**Ubicación:** `/docs/` o `/metrics/`  
**Regla:** Un doc por tema  
**Ejemplos:**
```
/docs/
├── COMMERCE_GROUPS_REFERENCE.md
├── DATE_FIELD_RULE.md
├── GOLDEN_TEMPLATES.md
└── ...

/metrics/
├── GUIA_USUARIO.md
├── COMPARATIVA.md
└── eventos/
    ├── CUANDO_REGENERAR.md
    └── FUENTE_EVENTOS.md
```

---

## 🚨 Señales de Alerta (Revisar Urgente)

### **🔴 Alerta Roja - Acción Inmediata:**

**1. Más de 10 scripts Python en raíz**
```bash
ls *.py | wc -l
# Si resultado > 10 → LIMPIAR AHORA
```

**2. `.cursorrules` > 700 líneas**
```bash
wc -l .cursorrules
# Si resultado > 700 → SIMPLIFICAR AHORA
```

**3. Más de 5 reportes HTML en raíz**
```bash
ls *.html | wc -l
# Si resultado > 0 → ELIMINAR AHORA
```

---

### **🟡 Alerta Amarilla - Revisar Pronto:**

**1. Carpeta /output/ > 100 MB**
```bash
du -sh output/
# Si resultado > 100M → Eliminar reportes viejos
```

**2. Más de 3 changelogs separados**
```bash
ls CHANGELOG*.md | wc -l
# Si resultado > 3 → Consolidar
```

**3. Scripts con nombre "test_", "validar_", "debug_" en raíz**
```bash
ls test_*.py validar_*.py debug_*.py
# Si encuentra alguno → Mover a /temp/ o eliminar
```

---

## 📝 Proceso de Creación de Nuevo Script

### **Paso 1: Definir Tipo**
- ¿Es un Golden Template de producción? → Raíz
- ¿Es parte del sistema hard metrics? → `/metrics/eventos/`
- ¿Es experimental/temporal? → `/temp/` (local, no commitear)

### **Paso 2: Naming Convention**
**Golden Template:** `generar_golden_{commerce_group}_{site}.py`  
**Hard Metrics:** `generar_{metrica}.py` o `ejemplo_{uso}.py`  
**Temporal:** `temp_{descripcion}.py` (en /temp/)

### **Paso 3: Crear y Probar**
```bash
# Si es temporal
mkdir -p temp/
nano temp/test_nueva_feature.py
# Probar, validar

# Si funciona y es para producción
mv temp/test_nueva_feature.py generar_golden_nueva_feature.py
# Documentar en README y CHANGELOG
```

### **Paso 4: Cleanup**
```bash
# Al final del día/semana
rm -rf temp/  # Eliminar todos los temporales
```

---

## 🔄 Workflow de Actualización de Script Existente

### **❌ NUNCA HAGAS:**
```bash
cp generar_golden_pdd_mla.py generar_golden_pdd_mla_v2.py
nano generar_golden_pdd_mla_v2.py
# Ahora tienes 2 scripts ❌
```

### **✅ SIEMPRE HAZ:**
```bash
# Git ya guarda el historial, no necesitas v2
nano generar_golden_pdd_mla.py
# Modificar directamente
git add generar_golden_pdd_mla.py
git commit -m "feat: add hard metrics to PDD MLA script"
# Solo 1 script, historial en Git ✅
```

---

## 📊 Métricas de Salud del Repositorio

### **Target Ideal (post-limpieza v4.0):**

| Métrica | Target | Actual (v4.0) | Status |
|---------|--------|---------------|--------|
| Scripts Python raíz | ≤ 10 | 6 | ✅ |
| `.cursorrules` líneas | ≤ 600 | 450 | ✅ |
| Changelogs | ≤ 3 | 2 | ✅ |
| HTML en raíz | 0 | 0 | ✅ |
| Carpeta /output/ | < 50 MB | ~5 MB | ✅ |

### **Revisión Trimestral:**
```bash
# Generar reporte de salud
echo "=== REPORTE DE SALUD DEL REPO ==="
echo "Scripts Python en raíz: $(ls *.py 2>/dev/null | wc -l)"
echo ".cursorrules líneas: $(wc -l < .cursorrules)"
echo "Changelogs: $(ls CHANGELOG*.md | wc -l)"
echo "HTML en raíz: $(ls *.html 2>/dev/null | wc -l)"
echo "Tamaño /output/: $(du -sh output/ | cut -f1)"
```

---

## 🎓 Cultura de Limpieza

### **Principios del Equipo:**

1. **"Deja el repo más limpio de como lo encontraste"**
   - Antes de commitear, revisa si hay archivos temporales
   - Elimina scripts viejos que ya no uses

2. **"Si lo probaste y funciona, elimina el script de prueba"**
   - No dejes `test_X.py` por "las dudas"
   - Git guarda todo, puedes recuperarlo

3. **"Documenta o elimina"**
   - Si un script no tiene documentación y no lo usas hace 3+ meses → Eliminar
   - Si es importante → Documentar en README

4. **"Un script, un propósito"**
   - No crear 5 scripts que hacen casi lo mismo
   - Consolidar funcionalidad similar en 1 script

---

## 🔧 Herramientas de Limpieza Automática

### **Script: `cleanup.sh` (opcional)**
```bash
#!/bin/bash
# cleanup.sh - Elimina archivos temporales comunes

echo "🧹 Limpieza automática iniciada..."

# Eliminar carpeta temp
if [ -d "temp" ]; then
    echo "Eliminando /temp/..."
    rm -rf temp/
fi

# Eliminar reportes HTML en raíz
html_count=$(ls *.html 2>/dev/null | wc -l)
if [ $html_count -gt 0 ]; then
    echo "⚠️  Encontrados $html_count reportes HTML en raíz"
    echo "¿Eliminar? (y/n)"
    read response
    if [ "$response" = "y" ]; then
        rm *.html
        echo "✅ Eliminados"
    fi
fi

# Reportar scripts de testing en raíz
test_scripts=$(ls test_*.py validar_*.py debug_*.py 2>/dev/null)
if [ ! -z "$test_scripts" ]; then
    echo "⚠️  Scripts de testing encontrados en raíz:"
    echo "$test_scripts"
    echo "Considera moverlos a /temp/ o eliminarlos"
fi

echo "✅ Limpieza completada"
```

**Uso:**
```bash
chmod +x cleanup.sh
./cleanup.sh
```

---

## 📚 Referencias

- **Limpieza v4.0:** `LIMPIEZA_v4.0_SUMMARY.md`
- **Estructura ideal:** `README.md` sección "Estructura del Repositorio"
- **Best practices:** `docs/GUIDELINES.md`
- **Coding standards:** `docs/CODING_STANDARDS.md`

---

## 🎯 Checklist de Pre-Commit

Antes de hacer commit, verifica:

- [ ] ¿Eliminé scripts temporales que creé?
- [ ] ¿Hay archivos `.html` en raíz? → Moverlos a /output/
- [ ] ¿Actualicé CHANGELOG.md si es un cambio importante?
- [ ] ¿Los nombres de archivos siguen la convención?
- [ ] ¿La documentación está actualizada?
- [ ] ¿Eliminé versiones viejas de scripts que modifiqué?

---

## 💡 Tips Finales

1. **Usa `/temp/` libremente** - Pero NO la commitees
2. **Git es tu backup** - No necesitas `script_v1.py`, `script_v2.py`
3. **Revisa el repo cada viernes** - 10 minutos de limpieza previenen caos
4. **Pregunta antes de commitear basura** - "¿Esto lo usará alguien más?"
5. **Documenta lo importante, elimina lo temporal**

---

**Última actualización:** Enero 2026  
**Versión:** 1.0  
**Mantenedor:** CR Analytics Team  

**Recuerda:** Un repositorio limpio = un equipo feliz 🎉
