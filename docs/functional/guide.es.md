# Guía Funcional del Usuario: Herramienta de Gestión de Contenido para Odoo v18.0.1.0.0

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Primeros Pasos](#primeros-pasos)
3. [Configuración de IA](#configuración-de-ia)
4. [Flujo de Trabajo de Traducción de Blogs](#flujo-de-trabajo-de-traducción-de-blogs)
5. [Gestión de Tareas](#gestión-de-tareas)
6. [Solución de Problemas](#solución-de-problemas)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Características Específicas de la Versión](#características-específicas-de-la-versión)

---

## Descripción General

La Herramienta de Gestión de Contenido para Odoo v18.0.1.0.0 es la primera versión estable que proporciona capacidades de traducción de publicaciones de blog impulsadas por IA. Esta versión introduce el flujo de trabajo principal de traducción utilizando la integración con OpenAI y establece las bases para la gestión automatizada de contenido.

### Características Principales en v18.0.1.0.0
- ✅ Integración con API de OpenAI con configuración segura
- ✅ Capacidades de traducción masiva de publicaciones de blog
- ✅ Asistente de traducción fácil de usar
- ✅ Procesamiento en segundo plano para tareas de traducción
- ✅ Seguimiento de tareas de traducción y gestión de estado
- ✅ Manejo de errores y capacidades de reinicio de tareas
- ✅ Soporte multiidioma (Inglés/Español)

### Contexto de la Versión
Esta documentación cubre las características disponibles en la **versión 18.0.1.0.0** (Septiembre 2025). Las características avanzadas de traducción y correcciones de corrupción se introdujeron en versiones posteriores.

---

## Primeros Pasos

### Requisitos Previos
- Odoo 18.0 Community o Enterprise
- Acceso de administrador para configurar los ajustes de OpenAI
- Cuenta válida de OpenAI API y credenciales
- Módulo de Blog instalado y configurado

### Lista de Verificación de Configuración Inicial
1. ✅ Instalar el módulo de Herramienta de Gestión de Contenido
2. ✅ Configurar las credenciales de OpenAI API en ajustes
3. ✅ Verificar que las publicaciones de blog estén disponibles para traducción
4. ✅ Probar el flujo de trabajo de traducción con contenido de muestra

---

## Configuración de IA

### Acceso a los Ajustes de Configuración

**Navegación**: Ajustes → Ajustes Generales → Herramientas de Marketing IA

**Nota**: Esta sección aparece en la página de Ajustes Generales después de instalar el módulo.

### Campos de Configuración

#### 1. Clave API de OpenAI (Requerida)
- **Campo**: Clave API SC OpenAI
- **Tipo**: Campo de contraseña (entrada oculta)
- **Propósito**: Autentica las solicitudes a los servicios de OpenAI
- **Seguridad**: Nunca comparta o exponga esta clave

#### 2. ID de Organización OpenAI (Opcional)
- **Campo**: ID de Organización SC OpenAI
- **Tipo**: Campo de texto
- **Propósito**: Vincula las solicitudes a su organización de OpenAI
- **Nota**: Recomendado para el seguimiento de uso a nivel organizacional

#### 3. Selección de Modelo IA (Requerida)
- **Campo**: Modelo SC OpenAI
- **Tipo**: Menú desplegable de selección
- **Predeterminado**: gpt-4o
- **Opciones Disponibles**:
  - gpt-4o (Recomendado)
  - gpt-4-turbo
  - gpt-3.5-turbo
  - Modelos adicionales cargados dinámicamente desde la API de OpenAI

### Carga Dinámica de Modelos
El sistema obtiene automáticamente los modelos de OpenAI disponibles cuando tiene una clave API válida configurada. Si la API no está disponible, se proporcionan modelos de respaldo.

### Consejos de Configuración
- Use **gpt-4o** para traducciones de la más alta calidad
- Use **gpt-3.5-turbo** para traducciones más rápidas y rentables
- El ID de organización ayuda a rastrear el uso entre equipos

---

## Flujo de Trabajo de Traducción de Blogs

### Paso 1: Seleccionar Publicaciones de Blog

1. Navegue a **Sitio Web → Blogs → Publicaciones de Blog**
2. Use la vista de lista para ver todas las publicaciones de blog disponibles
3. Seleccione una o más publicaciones de blog usando las casillas de verificación
4. Haga clic en el menú desplegable **Acción** en el menú superior

### Paso 2: Lanzar el Asistente de Traducción

1. Desde el menú Acción, seleccione **"Traducir con IA"**
2. El asistente de traducción se abre en un diálogo modal
3. El asistente muestra el contexto de las publicaciones de blog seleccionadas

### Paso 3: Configurar la Traducción

#### Selección de Idioma Objetivo
- **Campo**: Idioma Objetivo
- **Opciones**: Solo idiomas publicados en el sitio web
- **Requisito**: Al menos un idioma debe estar activo

#### Instrucciones del Sistema (Opcional)
- **Campo**: Instrucciones del Sistema
- **Propósito**: Guiar el estilo y tono de la traducción IA
- **Ejemplos**:
  - "Mantener tono profesional de negocios"
  - "Usar lenguaje casual y amigable"
  - "Preservar terminología técnica"
  - "Adaptar referencias culturales para audiencia local"

### Paso 4: Ejecutar la Traducción

1. Haga clic en el botón **"Traducir"** para iniciar el proceso
2. El asistente se cierra y regresa a la lista de publicaciones de blog
3. Las tareas de traducción se crean en estado "Borrador"
4. El procesamiento en segundo plano comienza automáticamente

### Paso 5: Monitorear el Progreso

Las tareas de traducción se procesan de forma asíncrona:

- **Borrador**: Tarea creada, esperando procesamiento
- **En Progreso**: La traducción IA está ejecutándose
- **Completada**: Traducción completada exitosamente
- **Error**: La traducción falló (ver detalles del error)

---

## Gestión de Tareas

### Acceso a las Tareas de Traducción

**Navegación**: Automatización de Marketing → Traducción de Contenido → Tareas de Traducción

### Vista de Lista de Tareas

La lista de tareas muestra:
- **Nombre de Tarea**: Nombre descriptivo con publicación de blog e idioma
- **Publicación de Blog**: Enlace a la publicación de blog original
- **Idioma Objetivo**: Idioma de destino para la traducción
- **Estado**: Estado actual de la tarea con codificación de colores
  - 🔵 Borrador/En Progreso (Azul)
  - 🟢 Completada (Verde)
  - 🔴 Error (Rojo)

### Detalles de la Tarea

Haga clic en cualquier tarea para ver información detallada:
- Configuración completa de la tarea
- Mensajes de error (si aplica)
- Marcas de tiempo de creación y finalización
- Instrucciones del sistema utilizadas

### Acciones de Tareas

#### Reiniciar a Borrador
- **Disponible**: Solo para tareas en estado "Error"
- **Propósito**: Permite reintentar traducciones fallidas
- **Efecto**: Cambia el estado de vuelta a "Borrador" para reprocesamiento

**Nota**: Use esta acción cuando los problemas de la API de OpenAI se resuelvan o la configuración se corrija.

### Historial de Tareas

Desde cualquier formulario de publicación de blog:
1. Abra el registro de la publicación de blog
2. Navegue a la pestaña **"Historial de Traducción"**
3. Vea todos los intentos de traducción para esa publicación
4. Rastree el estado de traducción a lo largo del tiempo

---

## Solución de Problemas

### Problemas Comunes

#### 1. Tareas de Traducción Atascadas en "Borrador"
**Síntomas**: Las tareas permanecen en estado borrador por períodos extendidos

**Posibles Causas**:
- Credenciales de OpenAI API no configuradas
- Clave API inválida o expirada
- Problemas de conectividad de red
- Trabajo cron no ejecutándose

**Soluciones**:
- Verificar configuración de API en Ajustes
- Verificar estado de cuenta OpenAI y créditos
- Reiniciar servidor Odoo para restablecer trabajos cron
- Verificar registros del servidor para errores específicos

#### 2. La Traducción Falla con Errores de API
**Síntomas**: Las tareas pasan a estado "Error" con mensajes relacionados con API

**Posibles Causas**:
- Límites de velocidad de API excedidos
- Créditos de OpenAI insuficientes
- Selección de modelo inválida
- Contenido demasiado grande para procesamiento

**Soluciones**:
- Esperar el restablecimiento del límite de velocidad (típicamente 1 minuto)
- Agregar créditos a la cuenta de OpenAI
- Cambiar a modelo disponible (gpt-3.5-turbo)
- Dividir contenido grande en publicaciones más pequeñas

#### 3. Calidad de Traducción Pobre
**Síntomas**: Las traducciones son incorrectas o inapropiadas

**Posibles Causas**:
- Instrucciones del sistema subóptimas
- Selección de modelo incorrecta
- Contenido fuente complejo

**Soluciones**:
- Refinar instrucciones del sistema con orientación específica
- Actualizar al modelo gpt-4o para mejor calidad
- Probar primero con contenido más simple
- Proporcionar instrucciones específicas del contexto

### Referencia de Mensajes de Error

| Mensaje de Error | Significado | Solución |
|------------------|-------------|----------|
| "Clave API no configurada" | Credenciales de OpenAI faltantes | Configurar clave API en Ajustes |
| "Modelo no disponible" | Modelo seleccionado no disponible | Elegir modelo diferente |
| "Límite de velocidad excedido" | Demasiadas solicitudes de API | Esperar y reintentar |
| "Contenido demasiado largo" | Publicación de blog excede límites de API | Reducir longitud del contenido |

---

## Mejores Prácticas

### Preparación de Contenido
1. **Revisar Contenido Fuente**: Asegurar que las publicaciones de blog originales estén completas y bien formateadas
2. **Optimizar Longitud**: Mantener publicaciones bajo 4000 palabras para mejores resultados
3. **Limpiar Formato**: Remover HTML excesivo o caracteres especiales
4. **Probar Incrementalmente**: Comenzar con publicaciones más cortas para validar configuración

### Estrategia de Traducción
1. **Planificación de Idiomas**: Priorizar idiomas objetivo basados en necesidades de audiencia
2. **Procesamiento por Lotes**: Agrupar contenido similar para traducciones consistentes
3. **Revisión de Calidad**: Siempre revisar traducciones IA antes de publicar
4. **Respaldo Original**: Mantener contenido original seguro (automático en esta versión)

### Pautas de Instrucciones del Sistema
1. **Ser Específico**: Proporcionar instrucciones claras y detalladas
2. **Incluir Contexto**: Mencionar industria, audiencia y propósito
3. **Establecer Tono**: Especificar estilo formal, casual, técnico o conversacional
4. **Adaptación Cultural**: Solicitar consideraciones culturales locales

### Optimización de Rendimiento
1. **Programar Traducciones**: Ejecutar durante horas de menor tráfico para procesamiento más rápido
2. **Monitorear Recursos**: Rastrear uso y costos de API
3. **Lotes Inteligentes**: Procesar 5-10 publicaciones a la vez para rendimiento óptimo
4. **Mantenimiento Regular**: Reiniciar tareas fallidas y limpiar las completadas

---

## Características Específicas de la Versión

### Nuevo en v18.0.1.0.0 (Septiembre 2025)
- **Lanzamiento Inicial**: Primera versión estable con funcionalidad principal de traducción
- **Integración OpenAI**: Integración completa con SDK openai-agents
- **Procesamiento en Segundo Plano**: Traducción asíncrona con gestión de trabajos cron
- **Seguimiento de Tareas**: Gestión integral de estado y manejo de errores
- **Implementación de Seguridad**: Controles de acceso apropiados y gestión de credenciales
- **Soporte Bilingüe**: Traducciones de interfaz en inglés y español
- **Documentación**: Documentación funcional y técnica completa

### Aspectos Destacados de la Arquitectura
- **Cumplimiento Odoo 18.0**: Usa vistas `<list>` modernas y condicionales apropiadas
- **Integración de Correo**: Soporte de chatter para tareas de traducción
- **Vistas Kanban**: Agrupación significativa por estado de tarea
- **Anclajes Estables**: Herencia de configuración principal del módulo base_setup

### Limitaciones Conocidas en v18.0.1.0.0
- Procesamiento de traducción limitado a 10 tareas por ciclo cron
- Sin mecanismo de reintento automático para fallas de API
- Reinicio manual de tareas requerido para recuperación de errores
- Reporte de errores básico sin diagnósticos detallados

**Nota**: Las características mejoradas y mejoras están disponibles en versiones posteriores (18.0.1.1.0+).

---

## Referencias Externas

### Implementación de Configuración Principal
- **Referencia**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anclaje Usado**: `//setting[@id='partner_autocomplete']` con `position="after"`
- **Patrón**: Selectores xpath estables siguiendo estándares de Odoo 18.0

### Documentación Oficial
- **SDK OpenAI Agents**: https://github.com/openai/openai-agents-python
- **Documentación API OpenAI**: https://platform.openai.com/docs
- **Sistema de Traducción Odoo 18.0**: https://www.odoo.com/documentation/18.0/

---

*Versión de Documentación: 18.0.1.0.0 | Última Actualización: Septiembre 2025*
