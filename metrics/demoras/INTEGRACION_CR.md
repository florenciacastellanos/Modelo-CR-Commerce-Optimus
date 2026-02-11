# Integración de Métricas de Demoras con Contact Rate

## 🎯 Propósito

Este documento analiza **cómo las métricas de demoras en Shipping se relacionan con variaciones de Contact Rate** y define en qué procesos pueden usarse como hard data para diagnóstico.

---

## 📊 Estado Actual

**⚠️ DOCUMENTO EN CONSTRUCCIÓN**

Este análisis se desarrollará en colaboración con el equipo para:

1. **Identificar correlaciones** entre métricas de demoras y picos de CR
2. **Definir procesos aplicables** donde demoras son causa raíz
3. **Establecer umbrales** de alerta (ej: si delays >30%, esperamos pico de CR)
4. **Crear casos de uso** específicos por proceso

---

## 🔗 Hipótesis de Correlación (A Validar)

### Hipótesis 1: Delays en Lead Time → Picos en "¿Dónde está mi pedido?"

**Métrica:** `SHIPMENTS_LT_DELAY`

**Proceso CR:** ME Distribución - Despacho

**Tipificaciones esperadas:**
- "¿Dónde está mi pedido?"
- "Demora en entrega"
- "Producto no llega"

**Análisis pendiente:**
- Correlación temporal (¿cuántos días después del delay aumenta CR?)
- Threshold de activación (¿cuántos delays generan pico significativo?)
- Variación por site (¿MLA más sensible que MLB?)

---

### Hipótesis 2: Custom Offsets → Contactos por cambio de promesa

**Métrica:** `CO_ST_SHIPMENTS`, `BUFF_*`

**Proceso CR:** ME Distribución - Despacho

**Tipificaciones esperadas:**
- "Cambio de fecha de entrega"
- "Promesa incumplida"
- "Demora no comunicada"

**Análisis pendiente:**
- ¿Todo custom offset genera contacto o solo si no hay notificación?
- ¿Buffering automático (CAP_*) genera menos contactos que manual (CO_ST)?

---

### Hipótesis 3: Shipments estancados → Contactos por falta de tracking

**Métrica:** `SHIPMENTS_ESTANCADOS` (TM_LT_DEV_TYPE = NULL)

**Proceso CR:** ME Distribución - PreDespacho

**Tipificaciones esperadas:**
- "Sin actualización de tracking"
- "Pedido no avanza"
- "Shipment pendiente"

**Análisis pendiente:**
- ¿Cuántos días sin actualización dispara contacto?
- ¿Varía por picking type? (FF vs XD vs DS)

---

## 🧪 Metodología de Validación (Próximos Pasos)

### Paso 1: Análisis Histórico

**Objetivo:** Identificar períodos con picos de CR y correlacionarlos con métricas de demoras.

**Método:**
```python
# 1. Obtener histórico de CR (últimos 6 meses)
cr_historico = cargar_incoming_historico(
    commerce_group='ME Distribución',
    site='MLA',
    periodo='2025-07-01 to 2026-01-01'
)

# 2. Obtener histórico de demoras (mismos períodos)
demoras_historico = ejecutar_query_demoras(
    site='MLA',
    fecha_inicio='2025-07-01',
    fecha_fin='2026-01-01',
    granularidad='WEEK'
)

# 3. Calcular correlaciones
from scipy.stats import pearsonr

correlacion_delays = pearsonr(
    demoras_historico['SHIPMENTS_LT_DELAY'],
    cr_historico['INCOMING_CASES']
)

print(f"Correlación delays-CR: {correlacion_delays[0]:.3f} (p-value: {correlacion_delays[1]:.4f})")
```

**Output esperado:** Coeficiente de correlación + p-value para validar significancia.

---

### Paso 2: Análisis de Casos Específicos

**Objetivo:** Validar con ejemplos reales de picos de CR.

**Método:**
```python
# Identificar pico de CR en período específico
pico_cr = identificar_pico(
    site='MLA',
    proceso='ME Distribución - Despacho',
    fecha='2025-11-15'  # Ejemplo: Black Friday
)

# Obtener métricas de demoras del mismo período
demoras_pico = obtener_demoras(
    site='MLA',
    fecha_inicio='2025-11-10',
    fecha_fin='2025-11-20',
    granularidad='DAY'
)

# Analizar si hubo aumento de delays previo al pico
comparar_delays(demoras_pico, baseline_normal)
```

**Validación cualitativa:** Muestrear conversaciones del pico y buscar menciones de demoras.

---

### Paso 3: Definición de Umbrales

**Objetivo:** Establecer thresholds que activen alertas.

**Ejemplo:**
```python
# Definir umbral basado en desviación estándar
umbral_delays = {
    'MLA': {
        'mean': 15000,  # Shipments con delay promedio
        'std': 3000,    # Desviación estándar
        'threshold': 15000 + 1.5 * 3000  # Mean + 1.5 std
    }
}

# Alerta si delays superan umbral
if shipments_lt_delay > umbral_delays['MLA']['threshold']:
    enviar_alerta(
        mensaje="⚠️ Delays en MLA superan umbral - posible pico de CR",
        datos={'delays': shipments_lt_delay, 'threshold': umbral_delays['MLA']['threshold']}
    )
```

---

## 📋 Procesos Aplicables (A Confirmar)

| Proceso CR | Métrica de Demoras Relacionada | Prioridad | Estado |
|------------|--------------------------------|-----------|--------|
| **ME Distribución - Despacho** | `SHIPMENTS_LT_DELAY`, `SHIPMENTS_HT_DELAY` | 🔴 Alta | A validar |
| **ME Distribución - PreDespacho** | `SHIPMENTS_ESTANCADOS` | 🟡 Media | A validar |
| **ME Distribución - Despacho** | `CO_ST_SHIPMENTS`, `BUFF_*` | 🟡 Media | A validar |
| **ME Distribución - Despacho** | `SHIPMENTS_VENTANA` | 🟢 Baja | A validar |

**Notas:**
- **Alta prioridad:** Correlación esperada fuerte (>0.6)
- **Media prioridad:** Correlación esperada moderada (0.3-0.6)
- **Baja prioridad:** Correlación esperada débil (<0.3) o difícil de medir

---

## 🔍 Casos de Uso Propuestos

### Caso de Uso 1: Diagnóstico Automático de Picos

**Escenario:** CR de ME Distribución - Despacho sube +0.15 pp en MLA

**Flujo automatizado:**
```python
# 1. Detectar pico
if delta_cr > 0.10:
    # 2. Obtener métricas de demoras del período
    demoras = obtener_demoras(site, periodo_actual)
    
    # 3. Comparar con período anterior
    if demoras['SHIPMENTS_LT_DELAY'] > demoras_anterior['SHIPMENTS_LT_DELAY'] * 1.3:
        # 4. Incluir en reporte como causa probable
        agregar_hallazgo(
            titulo="Aumento de delays en Lead Time",
            metrica=f"+{delta_delays} shipments con delay",
            evidencia="Ver análisis de conversaciones para validar"
        )
```

**Beneficio:** Identificar causa raíz automáticamente, sin análisis manual.

---

### Caso de Uso 2: Alertas Proactivas

**Escenario:** Delays superan umbral antes de que aumente CR

**Flujo:**
```python
# Monitoreo diario
if shipments_lt_delay > umbral:
    enviar_alerta(
        destinatarios=['equipo_shipping', 'equipo_cx'],
        mensaje="⚠️ Delays en aumento - posible pico de CR en próximos días",
        recomendacion="Preparar comunicación proactiva a usuarios afectados"
    )
```

**Beneficio:** Actuar antes de que se generen contactos (reducir incoming).

---

### Caso de Uso 3: Análisis Comparativo Cross-Site

**Escenario:** ¿Por qué MLA tiene más CR que MLB si tienen similar volumen?

**Análisis:**
```python
# Comparar métricas de demoras
comparacion = pd.DataFrame({
    'Site': ['MLA', 'MLB'],
    'CR (pp)': [0.85, 0.62],
    'Delay Rate': [0.18, 0.12],  # % de shipments con delay
    'CO Rate': [0.25, 0.15]      # % con custom offset
})

# Conclusión: MLA tiene mayor delay rate y CO rate → explica CR más alto
```

**Beneficio:** Identificar diferencias operativas entre sites que impactan CR.

---

## 🛠️ Herramientas de Integración (A Desarrollar)

### Herramienta 1: Dashboard de Correlación

**Objetivo:** Visualizar en tiempo real la relación entre demoras y CR.

**Features:**
- Gráfico: CR vs Delays (últimos 3 meses)
- Coeficiente de correlación actualizado semanalmente
- Alertas cuando correlación supera threshold

---

### Herramienta 2: Reporte Enriquecido

**Objetivo:** Incluir métricas de demoras automáticamente en reportes de CR.

**Sección agregada:**
```
## Análisis de Demoras (Hard Data)

**Período Actual vs Anterior:**
- Delays en Lead Time: +1,234 shipments (+15%)
- Custom Offsets: +567 shipments (+8%)
- Shipments estancados: +89 shipments (+3%)

**Correlación con incoming:**
- Delays explican ~45% de la variación de incoming (correlación: 0.67)
- Mayor impacto en tipificación "¿Dónde está mi pedido?" (+890 casos)
```

---

### Herramienta 3: Simulador de Impacto

**Objetivo:** Estimar cuánto bajaría CR si se reducen delays.

**Cálculo:**
```python
# Basado en correlación histórica
coeficiente = 0.67  # De análisis histórico
reduccion_delays = 1000  # Shipments

impacto_cr_estimado = (reduccion_delays / driver_total) * 100 * coeficiente
print(f"Reducir {reduccion_delays} delays → CR baja ~{impacto_cr_estimado:.3f} pp")
```

---

## 📚 Próximos Pasos

1. **Validación de correlaciones** (análisis histórico 6 meses)
2. **Definición de umbrales** por site y proceso
3. **Implementación de alertas** proactivas
4. **Integración en reportes** Golden Template
5. **Pre-cálculo mensual** (generar Parquets automáticos)

---

## 📋 Checklist de Integración

Antes de usar demoras en diagnóstico de CR:

- [ ] Validar que existe correlación estadísticamente significativa (p-value < 0.05)
- [ ] Confirmar que período de demoras coincide con período de incoming
- [ ] Verificar que granularidad (MONTH/WEEK/DAY) es consistente
- [ ] Incluir análisis cualitativo (conversaciones) para validar hipótesis
- [ ] Declarar en footer si se usan hard metrics o estimaciones

---

## 📞 Contacto para Validación

Para colaborar en la validación de correlaciones o proponer nuevos análisis:

**Equipo:** CR Commerce Analytics  
**Documento:** `INTEGRACION_CR.md` (este archivo)  
**Última actualización:** 2026-01-29

---

**Versión:** 0.1 (DRAFT)  
**Estado:** 🚧 EN CONSTRUCCIÓN  
**Próxima revisión:** Post-validación histórica
