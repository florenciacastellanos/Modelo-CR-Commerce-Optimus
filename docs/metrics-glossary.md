# 📊 Glosario de Métricas - Contact Rate Analysis

## Métricas Principales

### Contact Rate (CR)

**Definición:** Tasa de contacto de clientes respecto a un driver de negocio.

**Fórmula:**
```
CR = (Incoming Cases / Driver) × 100
```

**Unidad:** Puntos porcentuales (pp)

**Rango típico:** 0.5 - 15.0 pp

**Interpretación:** 
- CR = 5.0 pp → De cada 100 eventos (driver), 5 generan contacto
- CR más bajo = Mejor (menos problemas)
- CR más alto = Peor (más problemas)

**Ejemplo:**
```
Incoming Cases: 150
Driver: 10,000 órdenes
CR = (150 / 10,000) × 100 = 1.5 pp
```

---

### Incoming Cases

**Definición:** Total de casos reportados por clientes que ingresan al sistema de soporte.

**Fuentes:**
- `BT_CX_INCOMING_CR`: Casos incoming normales
- `BT_CX_CLAIMS_CR`: Casos de claims/conflictos

**Cálculo en SQL:**
```sql
SUM(CANT_CASES) AS INCOMING_CASES
```

**Filtros aplicados:**
- `FLAG_EXCLUDE_NUMERATOR_CR = 0`
- Queues NO excluidas
- Processes NO excluidos
- CI_REASONS NO excluidos

**Segmentación:**
- **Incoming No Conflict:** De tabla `BT_CX_INCOMING_CR`
- **Incoming Conflict:** De tabla `BT_CX_CLAIMS_CR`

---

### Driver

**Definición:** Métrica de negocio que representa el volumen de eventos susceptibles de generar contactos.

**Ejemplos por Commerce Group:**

| Commerce Group | Driver Típico | Unidad |
|----------------|---------------|--------|
| PDD | Órdenes cerradas | Órdenes |
| PNR | Órdenes cerradas | Órdenes |
| ME Distribución | Shipments entregados | Envíos |
| ME PreDespacho | Shipments despachados | Envíos |
| ME Drivers | Envíos asignados | Asignaciones |
| Pre Venta | Listados activos | Publicaciones |
| Pagos | Transacciones | Transacciones |
| Cuenta | Usuarios activos | Usuarios |

**Configuración:**
- Manual por Site y Periodo
- Sin driver configurado → No se puede calcular CR
- Valor = 0 → CR = NULL

**Validación:**
- Debe ser > 0
- Debe ser coherente con volumen de negocio
- Comparar con periodos anteriores

---

### Variación Absoluta (pp)

**Definición:** Diferencia absoluta entre CR actual y CR anterior.

**Fórmula:**
```
Variación (pp) = CR_actual - CR_anterior
```

**Unidad:** Puntos porcentuales (pp)

**Interpretación:**
- Variación > 0 → Empeoramiento (más contactos)
- Variación < 0 → Mejora (menos contactos)
- Variación = 0 → Sin cambio

**Ejemplo:**
```
CR Enero: 5.2 pp
CR Febrero: 6.8 pp
Variación: 6.8 - 5.2 = +1.6 pp
```

**Significancia:**
- |Variación| > 0.5 pp → Cambio notable
- |Variación| > 1.0 pp → Cambio significativo
- |Variación| > 2.0 pp → Cambio crítico

---

### Variación Relativa (%)

**Definición:** Diferencia porcentual entre CR actual y CR anterior.

**Fórmula:**
```
Variación (%) = ((CR_actual - CR_anterior) / CR_anterior) × 100
```

**Unidad:** Porcentaje (%)

**Interpretación:**
- Variación > 0% → Incremento relativo
- Variación < 0% → Disminución relativa
- Variación ±20% → Cambio fuerte (threshold)

**Ejemplo:**
```
CR Enero: 5.2 pp
CR Febrero: 6.8 pp
Variación: ((6.8 - 5.2) / 5.2) × 100 = +30.8%
```

**Significancia:**
- |Variación| > 10% → Cambio notable
- |Variación| > 20% → Cambio significativo (STRONG_VARIATION)
- |Variación| > 50% → Cambio crítico

---

### Volume Impact

**Definición:** Impacto en volumen absoluto de casos debido a variación de CR.

**Fórmula:**
```
Impact = (Variación_pp / 100) × Driver_actual
```

**Unidad:** Casos

**Interpretación:**
- Impact > 0 → Casos adicionales generados
- Impact < 0 → Casos evitados
- Mide impacto operacional real

**Ejemplo:**
```
Variación: +1.6 pp
Driver actual: 10,000 órdenes
Impact: (1.6 / 100) × 10,000 = +160 casos
```

**Uso:**
- Priorizar iniciativas por impacto
- Cuantificar ROI de mejoras
- Planificar capacidad

---

## Métricas de Detección de Patrones

### Spike (Pico)

**Definición:** Aumento súbito y anormal de CR.

**Criterio:**
```
CR_actual > Rolling_Average × 1.5
```

**Threshold:** 150% del promedio rolling (7 días)

**Interpretación:**
- Indica problema puntual
- Requiere investigación inmediata
- Puede ser evento externo

**Ejemplo:**
```
Rolling Avg: 5.0 pp
CR del día: 8.5 pp
8.5 > 5.0 × 1.5 (7.5) → NO es spike

CR del día: 11.0 pp
11.0 > 5.0 × 1.5 (7.5) → SÍ es spike
```

---

### Drop (Caída)

**Definición:** Disminución súbita y anormal de CR.

**Criterio:**
```
CR_actual < Rolling_Average × 0.5
```

**Threshold:** 50% del promedio rolling (7 días)

**Interpretación:**
- Puede indicar mejora real
- O problema en data collection
- Validar causa raíz

**Ejemplo:**
```
Rolling Avg: 5.0 pp
CR del día: 3.0 pp
3.0 > 5.0 × 0.5 (2.5) → NO es drop

CR del día: 2.0 pp
2.0 < 5.0 × 0.5 (2.5) → SÍ es drop
```

---

### Strong Variation

**Definición:** Cambio significativo mes a mes.

**Criterio:**
```
|Variación_%| > 20%
```

**Threshold:** ±20% MoM

**Interpretación:**
- Cambio estructural en CR
- Requiere análisis de drivers
- Posible tendencia sostenida

**Ejemplo:**
```
CR Mes 1: 5.0 pp
CR Mes 2: 6.5 pp
Variación: ((6.5 - 5.0) / 5.0) × 100 = +30%
30% > 20% → Strong Variation
```

---

### Concentration

**Definición:** Concentración anormal de volumen en días específicos.

**Criterio:**
```
Volumen en días críticos / Volumen total > 0.30
```

**Threshold:** 30% del volumen en días críticos

**Interpretación:**
- Distribución temporal anómala
- Posibles eventos puntuales
- Analizar días específicos

**Ejemplo:**
```
Volumen total mes: 1000 casos
Volumen en 3 días: 400 casos
400 / 1000 = 0.40 (40%)
40% > 30% → Concentration detectada
```

---

## Métricas de Volumen

### Total Cases

**Definición:** Total de casos en el periodo.

**Cálculo:**
```sql
SUM(CANT_CASES) AS TOTAL_CASES
```

**Uso:** Análisis de volumen absoluto.

---

### Unique Cases

**Definición:** Casos únicos (distintos CAS_CASE_ID).

**Cálculo:**
```sql
COUNT(DISTINCT CAS_CASE_ID) AS UNIQUE_CASES
```

**Uso:** Validar duplicados.

---

### Unique Customers

**Definición:** Clientes únicos afectados.

**Cálculo:**
```sql
COUNT(DISTINCT CUS_CUST_ID) AS UNIQUE_CUSTOMERS
```

**Uso:** Medir alcance en base de usuarios.

---

### Cases per Customer

**Definición:** Promedio de casos por cliente.

**Cálculo:**
```sql
SUM(CANT_CASES) / COUNT(DISTINCT CUS_CUST_ID) AS CASES_PER_CUSTOMER
```

**Interpretación:**
- > 1.5 → Clientes con múltiples casos (churn risk)
- ~ 1.0 → Un caso por cliente (normal)

---

## Métricas de Distribución

### Distribution by Process

**Definición:** Distribución de casos por proceso.

**Cálculo:**
```sql
SELECT 
    PROCESS_NAME,
    SUM(CANT_CASES) AS CASES,
    SUM(CANT_CASES) / (SELECT SUM(CANT_CASES) FROM BASE) AS PCT
FROM BASE
GROUP BY PROCESS_NAME
ORDER BY CASES DESC
```

---

### Distribution by Commerce Group

**Definición:** Distribución de casos por Commerce Group.

**Cálculo:**
```sql
SELECT 
    AGRUP_COMMERCE,
    SUM(CANT_CASES) AS CASES,
    SUM(CANT_CASES) / (SELECT SUM(CANT_CASES) FROM BASE) AS PCT
FROM BASE
GROUP BY AGRUP_COMMERCE
ORDER BY CASES DESC
```

---

### Distribution by User Type

**Definición:** Distribución de casos por tipo de usuario.

**Cálculo:**
```sql
SELECT 
    PROCESS_GROUP_ECOMMERCE,
    SUM(CANT_CASES) AS CASES,
    ROUND(100.0 * SUM(CANT_CASES) / SUM(SUM(CANT_CASES)) OVER (), 2) AS PCT
FROM BASE
GROUP BY PROCESS_GROUP_ECOMMERCE
```

**Distribución esperada:**
- Comprador: ~70%
- Vendedor: ~25%
- Cuenta: ~5%
- Driver: Variable

---

## Métricas Temporales

### Daily Average

**Definición:** Promedio diario de casos.

**Cálculo:**
```
Daily Avg = Total Cases / Días del periodo
```

---

### Weekly Average

**Definición:** Promedio semanal de casos.

**Cálculo:**
```
Weekly Avg = Total Cases / Semanas del periodo
```

---

### Rolling Average (7 días)

**Definición:** Promedio móvil de 7 días.

**Cálculo:**
```python
df['rolling_avg_7d'] = df['cases'].rolling(window=7, min_periods=3).mean()
```

**Uso:** Suavizar fluctuaciones diarias, detectar tendencias.

---

## Métricas de Calidad

### Automation Rate

**Definición:** Porcentaje de casos resueltos automáticamente.

**Cálculo:**
```sql
SELECT 
    SUM(CASE WHEN FLAG_AUTO = 1 THEN CANT_CASES ELSE 0 END) / SUM(CANT_CASES) AS AUTO_RATE
FROM BASE
```

**Interpretación:**
- Auto Rate alto → Buena automatización
- Auto Rate bajo → Oportunidad de mejora

---

### Conflict Rate

**Definición:** Porcentaje de casos que son claims/conflictos.

**Cálculo:**
```sql
SELECT 
    SUM(INCOMING_CONFLICT) / SUM(CANT_CASES) AS CONFLICT_RATE
FROM BASE
```

**Interpretación:**
- Conflict Rate alto → Problemas graves
- Conflict Rate bajo → Problemas menores

---

## Thresholds y Límites

### MIN_CASES_THRESHOLD

**Valor:** 100 casos (default)

**Uso:** Filtrar dimensiones con volumen insuficiente.

**Aplicación:**
```sql
HAVING SUM(CANT_CASES) >= 100
```

---

### MIN_SAMPLE_SIZE

**Valor:** 50 casos

**Uso:** Tamaño mínimo de muestra para análisis estadístico.

---

### MAX_SAMPLE_SIZE

**Valor:** 5,000 casos

**Uso:** Tamaño máximo de muestra para performance.

---

### SPIKE_THRESHOLD_MULTIPLIER

**Valor:** 1.5 (150%)

**Uso:** Detectar spikes en CR.

---

### DROP_THRESHOLD_MULTIPLIER

**Valor:** 0.5 (50%)

**Uso:** Detectar drops en CR.

---

### STRONG_VARIATION_PCT

**Valor:** 20%

**Uso:** Detectar variaciones fuertes MoM.

---

### CONCENTRATION_THRESHOLD_PCT

**Valor:** 30%

**Uso:** Detectar concentración temporal anómala.

---

## Fórmulas Avanzadas

### Weighted CR

**Definición:** CR ponderado por volumen de sites/groups.

**Fórmula:**
```
Weighted_CR = Σ(CR_i × Volume_i) / Σ(Volume_i)
```

---

### CR Contribution

**Definición:** Contribución de una dimensión al CR total.

**Fórmula:**
```
Contribution = (Incoming_dimension / Incoming_total) × 100
```

---

### CR Trend (Linear)

**Definición:** Tendencia lineal de CR en el tiempo.

**Cálculo:** Regresión lineal sobre serie temporal de CR.

**Interpretación:**
- Slope > 0 → Tendencia creciente (empeora)
- Slope < 0 → Tendencia decreciente (mejora)

---

## Referencias

- **Contexto de negocio:** `/docs/business-context.md`
- **Cálculos:** `/calculations/contact-rate.py`
- **Constantes:** `/config/business-constants.py`
- **Patrones:** `/calculations/pattern-detection.py`

---

**Última actualización:** Enero 2026  
**Versión:** 2.5 (Commerce)  
**Source:** V37.ipynb
