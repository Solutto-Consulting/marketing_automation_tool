# Guía Funcional del Usuario: Herramienta de Gestión de Contenido para Odoo v18.0.1.0.1

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Primeros Pasos](#primeros-pasos)
3. [Configuración de IA](#configuración-de-ia)
4. [Agente de Investigación de Contenido](#agente-de-investigación-de-contenido)
5. [Agente de Generación de Contenido](#agente-de-generación-de-contenido)
6. [Flujo de Trabajo de Traducción de Blogs](#flujo-de-trabajo-de-traducción-de-blogs)
7. [Monitoreo de Uso](#monitoreo-de-uso)
8. [Gestión de Tareas](#gestión-de-tareas)
9. [Solución de Problemas](#solución-de-problemas)
10. [Mejores Prácticas](#mejores-prácticas)
11. [Características Específicas de la Versión](#características-específicas-de-la-versión)

---

## Descripción General

La Herramienta de Gestión de Contenido para Odoo v18.0.1.0.1 introduce potentes capacidades de **estrategia de contenido basada en agentes**, evolucionando más allá de la simple traducción hacia la investigación y generación proactiva de contenido. Esta versión representa una evolución importante en la gestión de contenido impulsada por IA para Odoo.

### Características Principales en v18.0.1.0.1
- ✅ **Agente de Investigación de Contenido**: Descubrimiento de temas impulsado por IA usando búsqueda web
- ✅ **Agente de Generación de Contenido**: Creación automatizada de publicaciones de blog a partir de ideas de investigación
- ✅ **Generación de Imágenes Impulsada por IA**: Imágenes de portada profesionales usando el modelo gpt-image-1
- ✅ **Monitoreo Integral de Uso**: Seguimiento completo para generación de texto e imágenes
- ✅ **Gestión Centralizada de Modelos**: Definiciones estáticas de modelos con selección unificada
- ✅ **Configuración Mejorada**: Sección dedicada de configuración de Automatización de Marketing
- ✅ **Sistema de Traducción Mejorado**: Mejorado con OpenAI Agents SDK
- ✅ **Procesamiento Multi-Agente en Segundo Plano**: Trabajos cron separados para cada agente
- ✅ **Respuestas de IA Estructuradas**: Generación de contenido basada en JSON con esquemas definidos

### Contexto de la Versión
Esta documentación cubre las características disponibles en la **versión 18.0.1.0.1** (Septiembre 2025). Esto representa una expansión significativa desde la v18.0.1.0.0 centrada en traducción hacia una plataforma integral de estrategia de contenido.

---

## Primeros Pasos

### Requisitos Previos
- Odoo 18.0 Community o Enterprise
- Acceso de administrador para configurar los ajustes de OpenAI
- Cuenta válida de OpenAI API con acceso a organización
- Dependencia OpenAI Agents SDK (>=0.2.9)
- Módulo de Blog instalado y configurado

### Lista de Verificación de Configuración Inicial
1. ✅ Instalar el módulo de Herramienta de Gestión de Contenido
2. ✅ Configurar las credenciales de OpenAI API en ajustes de Automatización de Marketing
3. ✅ Configurar el Agente de Investigación de Contenido
4. ✅ Configurar los ajustes del Agente de Generación de Contenido
5. ✅ Verificar que el monitoreo de uso de OpenAI esté funcional
6. ✅ Probar el pipeline completo de contenido desde investigación hasta publicación

### Nuevo en v18.0.1.0.1: Arquitectura Basada en Agentes
Esta versión introduce dos agentes de IA especializados que trabajan juntos para crear un pipeline completo de estrategia de contenido:

- **Agente de Investigación de Contenido**: Descubre temas de tendencia y genera ideas de contenido
- **Agente de Generación de Contenido**: Crea borradores completos de publicaciones de blog a partir de ideas de investigación
- **Agente de Traducción Mejorado**: Capacidades de traducción mejoradas con mejor manejo de errores

---

## Configuración de IA

### Ubicación de Configuración Centralizada
Toda la configuración de IA se ha trasladado de Ajustes Generales a una sección dedicada:

**Navegación**: Ajustes → Automatización de Marketing

Este nuevo enfoque centralizado proporciona mejor organización y configuración dedicada para cada agente de IA.

### Acceso a los Ajustes de Configuración

**Navegación**: Ajustes → Ajustes Generales → Herramientas de Marketing IA

**Nota**: Esta sección aparece en la página de Ajustes Generales después de instalar el módulo.

### Campos de Configuración

#### 1. Clave API de OpenAI (Requerida)
### Campos de Configuración

#### 1. Configuración General de OpenAI
- **Clave API de OpenAI** (Requerida): Autentica todas las solicitudes a los servicios de OpenAI
- **ID de Organización OpenAI** (Opcional): Vincula las solicitudes a su organización para seguimiento de uso
- **Modelo OpenAI** (Requerido): Modelo predeterminado para tareas de traducción (gpt-4o recomendado)

#### 2. Configuración del Agente de Investigación de Contenido
- **Modelo del Agente de Investigación**: Modelo específico para tareas de investigación de contenido
- **Instrucciones del Agente de Investigación**: Instrucciones del sistema que guían el comportamiento de descubrimiento de temas
- **Consulta de Búsqueda Predeterminada**: Plantilla de consulta de búsqueda prellenada con soporte de marcadores de posición

#### 3. Configuración del Agente de Generación de Contenido
- **Modelo del Agente de Generación**: Modelo específico para creación de publicaciones de blog
- **Instrucciones del Agente de Generación**: Instrucciones del sistema para estilo y estructura de escritura de blog

### Carga Dinámica de Modelos
El sistema obtiene automáticamente los modelos de OpenAI disponibles cuando tiene una clave API válida configurada. Cada agente puede usar diferentes modelos optimizados para sus tareas específicas.

### Consejos de Configuración
- Use **gpt-4o** para investigación y generación de la más alta calidad
- Use **gpt-3.5-turbo** para operaciones más rápidas y rentables
- Personalice las instrucciones del agente para que coincidan con la voz de su marca y el estilo de contenido

---

## Agente de Investigación de Contenido

El Agente de Investigación de Contenido utiliza capacidades de búsqueda web para descubrir temas de tendencia y generar ideas de contenido relevantes para su blog.

### Flujo de Trabajo de Investigación

#### Paso 1: Acceder a Ideas de Contenido
1. Navegue a **Automatización de Marketing → Ideas de Contenido → Todas las Ideas**
2. Haga clic en el botón **Generar Ideas de Contenido** para abrir el asistente

#### Paso 2: Configurar Solicitud de Investigación
- **Consulta de Búsqueda**: Ingrese o modifique los términos de búsqueda (soporta marcador de posición {today})
- **Número de Sugerencias**: Especifique cuántas ideas generar (predeterminado: 5)
- **Consulta de Ejemplo**: "Últimas tendencias en marketing digital {today}"

#### Paso 3: Procesamiento en Segundo Plano
- El sistema crea una tarea de investigación y la procesa en segundo plano
- Monitoree el progreso en **Automatización de Marketing → Ideas de Contenido → Tareas de Generación**
- Las tareas progresan a través de: Borrador → En Progreso → Hecho/Error

#### Paso 4: Revisar Ideas Generadas
Cada idea generada incluye:
- **Título**: Titular del artículo fuente
- **URL**: Enlace a la fuente original
- **Fecha de Publicación**: Cuándo se publicó la fuente
- **Resumen**: Resumen generado por IA de puntos clave

### Mejores Prácticas de Investigación
- Use consultas de búsqueda específicas y dirigidas para mejores resultados
- Incluya marcadores de posición de fecha como {today} para contenido oportuno
- Revise la credibilidad de la fuente antes de usar las ideas
- Personalice las instrucciones del agente de investigación para el enfoque de su industria

---

## Agente de Generación de Contenido

El Agente de Generación de Contenido toma ideas de investigación y crea borradores completos de publicaciones de blog listos para revisión y publicación.

### Flujo de Trabajo de Generación

#### Paso 1: Acceder a Generación de Contenido
1. Navegue a **Sitio Web → Blogs → Publicaciones de Blog**
2. Haga clic en el botón **Generar Contenido** en el encabezado
3. Esto abre el asistente de generación de contenido

#### Paso 2: Configurar Solicitud de Generación
- **Idea de Contenido**: Seleccione de las ideas de investigación generadas previamente
- **Solicitud del Usuario**: Agregue instrucciones o requisitos específicos
- **Blog Objetivo**: Elija en qué blog publicar
- **Autor**: Seleccione el autor de la publicación
- **Idioma**: Establezca el idioma del contenido

#### Paso 3: Procesamiento en Segundo Plano
- El sistema crea una tarea de generación para procesamiento en segundo plano
- Monitoree el progreso en **Automatización de Marketing → Generación de Contenido → Tareas de Generación**
- Las tareas incluyen pipeline completo de creación de contenido

#### Paso 4: Revisar Contenido Generado
Las publicaciones de blog generadas incluyen:
- **Título**: Titular optimizado basado en investigación
- **Contenido**: Contenido completo de publicación de blog formateado en HTML
- **Meta Descripción**: Descripción optimizada para SEO
- **Palabras Clave**: Etiquetas relevantes para descubrimiento
- **Estado de Publicación**: Inicialmente guardado como borrador no publicado

### Mejores Prácticas de Generación
- Proporcione solicitudes de usuario claras y específicas para mejores resultados
- Revise y edite el contenido generado antes de publicar
- Personalice las instrucciones del agente de generación para una voz de marca consistente
- Use tareas de generación para rastrear el pipeline de creación de contenido

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

## Monitoreo de Uso

La función de Monitoreo de Uso proporciona información sobre el consumo de la API de OpenAI, ayudándole a rastrear costos y optimizar el uso en todos los agentes de IA.

### Acceso al Panel de Uso

**Navegación**: Automatización de Marketing → Uso de OpenAI

### Características del Panel

#### 1. Estadísticas de Uso
- **Consumo Diario de Tokens**: Tokens de solicitud, tokens de finalización y totales
- **Seguimiento de Costos**: Monitorear patrones de gasto de API
- **Tendencias de Uso**: Vista histórica de 30 días con gráficos

#### 2. Sincronización Manual de Datos
- **Botón Obtener Datos Más Recientes**: Actualizar manualmente las estadísticas de uso
- **Sincronización Automática**: Trabajo cron diario actualiza datos de uso automáticamente
- **Rango de Datos**: Hasta 90 días de datos históricos de uso

#### 3. Análisis de Uso
- **Desglose por Agente**: Ver qué agentes consumen más tokens
- **Optimización de Costos**: Identificar oportunidades para reducir costos de API
- **Patrones de Uso**: Rastrear horarios pico de uso y tendencias

### Entendiendo las Métricas de Uso

#### Tipos de Tokens
- **Tokens de Solicitud**: Texto de entrada enviado a OpenAI (su contenido e instrucciones)
- **Tokens de Finalización**: Respuestas generadas por IA (traducciones, contenido, ideas)
- **Tokens Totales**: Suma de tokens de solicitud y finalización para facturación

#### Consejos de Gestión de Costos
- Monitorear uso diario para mantenerse dentro de los límites de presupuesto
- Usar gpt-3.5-turbo para operaciones rentables cuando la calidad lo permita
- Optimizar instrucciones de agentes para reducir el uso de tokens de solicitud
- Revisar patrones de uso para identificar oportunidades de optimización

### Mejores Prácticas de Monitoreo de Uso
- Revisar el panel de uso semanalmente para rastrear gastos
- Configurar alertas internas basadas en consumo diario de tokens
- Revisar eficiencia de agentes y optimizar instrucciones regularmente
- Usar datos de uso para tomar decisiones informadas sobre selección de modelos

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
