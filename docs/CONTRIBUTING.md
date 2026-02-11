# 🤝 Contributing to Contact Rate Analysis

¡Gracias por tu interés en contribuir! Este documento proporciona guías para contribuir al repositorio.

---

## 📋 Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [Cómo Contribuir](#cómo-contribuir)
3. [Estructura del Repositorio](#estructura-del-repositorio)
4. [Estándares de Código](#estándares-de-código)
5. [Process de Pull Request](#proceso-de-pull-request)
6. [Reportar Bugs](#reportar-bugs)
7. [Sugerir Mejoras](#sugerir-mejoras)

---

## 📜 Código de Conducta

Este proyecto adhiere a un código de conducta profesional. Al participar, se espera que mantengas un ambiente respetuoso y colaborativo.

---

## 🚀 Cómo Contribuir

### Tipos de Contribuciones

1. **Nuevas Queries SQL** → Agregar a `/sql/`
2. **Nuevos Cálculos** → Agregar a `/calculations/`
3. **Nueva Documentación** → Agregar a `/docs/`
4. **Nuevas Constantes** → Agregar a `/config/`
5. **Nuevos Tests** → Agregar a `/tests/`
6. **Corrección de Bugs** → Fix en el archivo correspondiente

---

## 📂 Estructura del Repositorio

Antes de contribuir, familiarízate con la estructura:

```
contact-rate-analysis/
├── docs/          ← Documentación de negocio y técnica
├── sql/           ← Queries SQL de BigQuery
├── calculations/  ← Lógica de cálculos en Python
├── config/        ← Configuraciones y constantes
├── scripts/       ← Scripts de producción
├── templates/     ← Templates reutilizables
├── validations/   ← Casos de prueba
├── tests/         ← Unit tests
└── test/          ← Outputs de pruebas
```

Ver `STRUCTURE.md` para detalles completos.

---

## 💻 Estándares de Código

### Python
- **PEP 8** compliant
- **Docstrings** en todas las funciones
- **Type hints** donde sea apropiado
- Ver `docs/CODING_STANDARDS.md` para detalles

### SQL
- **CTEs** con nombres en MAYÚSCULAS
- **Indentación** de 4 espacios
- **Comentarios** explicativos
- Ver `docs/CODING_STANDARDS.md` para detalles

### Markdown
- **Headers** jerárquicos (H1 → H2 → H3)
- **Code blocks** con lenguaje especificado
- **Links** descriptivos

---

## 🔄 Proceso de Pull Request

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/contact-rate-analysis.git
cd contact-rate-analysis
```

### 2. Crear Branch

```bash
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b fix/correccion-bug
```

**Nomenclatura de branches**:
- `feature/nombre-feature` para nuevas funcionalidades
- `fix/nombre-bug` para correcciones
- `docs/nombre-doc` para documentación
- `refactor/nombre` para refactorización

### 3. Hacer Cambios

- Sigue los estándares de código
- Agrega tests si aplica
- Actualiza documentación si aplica

### 4. Commit

```bash
git add .
git commit -m "feat: descripción breve del cambio"
```

**Formato de commits** (Conventional Commits):
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (no afectan lógica)
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

### 5. Push y Pull Request

```bash
git push origin feature/nueva-funcionalidad
```

Luego crea un Pull Request en GitHub con:
- **Título descriptivo**
- **Descripción detallada** del cambio
- **Referencias** a issues relacionados
- **Screenshots** si aplica

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. Verifica que el bug no esté ya reportado
2. Asegúrate de usar la última versión
3. Revisa `docs/TROUBLESHOOTING.md`

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Ejecutar '...'
2. Con parámetros '...'
3. Ver error

**Comportamiento Esperado**
Qué debería suceder.

**Comportamiento Actual**
Qué está sucediendo.

**Contexto**
- Versión: [ej: 3.0.0]
- Site: [ej: MLA]
- Commerce Group: [ej: PDD]
- Dimensión: [ej: PROCESS_NAME]

**Logs/Screenshots**
Si aplica, agregar logs o screenshots.
```

---

## 💡 Sugerir Mejoras

### Template de Feature Request

```markdown
**Descripción de la Mejora**
Descripción clara de la funcionalidad propuesta.

**Problema que Resuelve**
¿Qué problema o necesidad aborda?

**Solución Propuesta**
¿Cómo funcionaría la mejora?

**Alternativas Consideradas**
¿Qué otras soluciones consideraste?

**Contexto Adicional**
Cualquier información relevante.
```

---

## ✅ Checklist de Contribución

Antes de enviar tu Pull Request, verifica:

### Código
- [ ] Sigue los estándares de código (`docs/CODING_STANDARDS.md`)
- [ ] Incluye docstrings/comentarios
- [ ] Pasa los tests existentes
- [ ] Agrega nuevos tests si aplica
- [ ] No hay código comentado innecesario
- [ ] No hay TODOs sin resolver

### Documentación
- [ ] Actualiza `README.md` si aplica
- [ ] Actualiza `CHANGELOG.md`
- [ ] Actualiza documentación técnica si aplica
- [ ] Agrega ejemplos de uso si aplica

### Tests
- [ ] Todos los tests pasan (`pytest tests/ -v`)
- [ ] Coverage no disminuye
- [ ] Tests nuevos para nueva funcionalidad

### Git
- [ ] Commits siguen Conventional Commits
- [ ] Branch tiene nombre descriptivo
- [ ] Pull Request tiene descripción clara

---

## 📚 Recursos

- **Coding Standards**: `docs/CODING_STANDARDS.md`
- **Guidelines**: `docs/GUIDELINES.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **API Reference**: `docs/API_REFERENCE.md`

---

## 🎯 Áreas de Contribución Prioritarias

### Alta Prioridad
- Tests para `calculations/`
- Validación de Commerce Groups faltantes (3/15)
- Documentación de casos de uso
- Optimización de queries

### Media Prioridad
- Nuevas dimensiones de análisis
- Templates adicionales
- Mejoras en reportes HTML
- CI/CD con GitHub Actions

### Baja Prioridad
- Notebooks interactivos
- Dashboard web
- API REST

---

## 📞 Contacto

Para preguntas o dudas:
- Abre un **Issue** en GitHub
- Revisa la **documentación** en `/docs/`
- Consulta el **FAQ.md**

---

**¡Gracias por contribuir! 🎉**

Tu aporte ayuda a mejorar el análisis de Contact Rate para todo el equipo de Commerce.
