# Herramienta de Gestión de Contenido para Odoo (sc_marketing_automation_tool)

[![Versión de Odoo](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![Licencia](https://img.shields.io/badge/Licencia-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Descripción General

La **Herramienta de Gestión de Contenido para Odoo** es una plataforma integral de **automatización de contenido impulsada por IA** que cuenta con agentes de IA especializados para la investigación y generación de contenido. Esta herramienta optimiza el flujo de trabajo de creación de contenido desde la ideación hasta la publicación.

## Características Principales (v18.0.1.0.1)

### 🤖 **Estrategia de Contenido Basada en Agentes**
- **Agente de Investigación de Contenido**: Descubrimiento de temas impulsado por IA usando capacidades de búsqueda web
- **Agente de Generación de Contenido**: Creación completa de publicaciones de blog a partir de ideas de investigación
- **Generación de Imágenes con IA**: Imágenes profesionales de portada de blog usando el modelo gpt-image-1

### 📊 **Monitoreo y Optimización de Uso**
- **Seguimiento Integral de Uso**: Monitoreo unificado para generación de texto e imágenes
- **Panel de Control Avanzado**: Panel interactivo con desglose diario y tendencias
- **Optimización de Costos Mejorada**: Desglose de uso de tokens y seguimiento de costos de generación de imágenes
- **Almacenamiento de Datos Persistente**: Retención de datos mejorada y análisis histórico
- **Seguimiento Específico por Operación**: Monitoreo dedicado para investigación, generación y generación de imágenes de contenido

### ⚙️ **Configuración Centralizada**
- **Configuraciones de Automatización de Marketing**: Sección de configuración dedicada para todos los agentes de IA
- **Gestión de Modelos Estática**: Definiciones de modelos centralizadas y confiables independientes de llamadas API
- **Configuración de Generación de Imágenes**: Configuraciones integrales para tamaño, calidad, formato
- **Configuración Específica por Agente**: Configuraciones especializadas para cada tipo de agente de IA
- **Seguridad Mejorada**: Gestión mejorada de credenciales y controles de acceso

### 🔄 **Procesamiento Multi-Agente en Segundo Plano**
- **Trabajos Cron Especializados**: Procesamiento independiente para investigación y generación
- **Gestión de Tareas Mejorada**: Seguimiento integral de estado en todos los tipos de agentes
- **Manejo de Errores Mejorado**: Patrones de error específicos por agente y mecanismos de recuperación

## Especificaciones Técnicas

### Dependencias
- **Módulos de Odoo**: base, website, website_blog, mail
- **Librería Externa**: openai-agents (SDK de Python para integración con OpenAI)
- **Versión de Python**: 3.9+ (requerido por openai-agents)

### Modelos Principales
- **sc.content.idea**: Gestiona ideas de contenido generadas por el agente de investigación
- **sc.content.generation.task**: Rastrea tareas de generación de contenido de blog
- **sc.openai.request.log**: Monitoreo integral de uso de API de OpenAI
- **sc.openai.model.statistics**: Estadísticas agregadas de uso por modelo
- **sc.openai.models**: Gestión centralizada de modelos OpenAI disponibles
- **res.config.settings** (extendido): Gestión centralizada de configuración de Automatización de Marketing

## Instalación

1. **Instalar Dependencias Externas**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Instalar Módulo**:
   - Coloque el módulo en su ruta de addons de Odoo
   - Actualice la lista de aplicaciones en Odoo
   - Instale el módulo "Herramienta de Gestión de Contenido"

3. **Configuración**:
   - Navegue a Configuración > Configuración General > Herramientas de IA para Marketing
   - Configure sus credenciales de API de OpenAI
   - Seleccione el modelo de IA deseado para traducciones

## Uso

1. **Configurar Ajustes de OpenAI**:
   - Vaya a Configuración > Configuración General
   - Desplácese a la sección "Herramientas de IA para Marketing"
   - Ingrese su Clave de API de OpenAI y ID de Organización
   - Seleccione su modelo de OpenAI preferido

2. **Traducir Artículos de Blog**:
   - Navegue a Sitio Web > Blog > Artículos de Blog
   - Seleccione uno o más artículos de blog
   - Haga clic en Acción > "Traducir con IA"
   - Elija el idioma objetivo y proporcione instrucciones opcionales
   - Monitoree el progreso de traducción en Automatización de Marketing > Tareas de Traducción

3. **Monitorear Tareas de Traducción**:
   - Acceda a Automatización de Marketing > Traducción de Contenido > Tareas de Traducción
   - Vea el estado, gestione errores y reinicie tareas fallidas
   - Rastree el historial de traducción para cada artículo de blog

## Características de la Versión v18.0.1.0.0

### ✅ Funcionalidades Incluidas (Septiembre 2025)
- **Integración OpenAI Completa**: SDK openai-agents con configuración segura
- **Selección Dinámica de Modelos**: Carga automática desde API OpenAI con respaldos
- **Asistente de Traducción**: Interfaz modal con instrucciones del sistema personalizables
- **Procesamiento Asíncrono**: Trabajos cron cada 5 minutos para tareas en segundo plano
- **Gestión Integral de Tareas**: Estados de seguimiento con capacidades de reinicio manual
- **Vistas Kanban**: Agrupación por estado (cumplimiento Odoo 18.0)
- **Integración Chatter**: Seguimiento de cambios en tareas de traducción
- **Controles de Seguridad**: Grupos de marketing con acceso basado en roles
- **Soporte i18n**: Traducción completa al español
- **Documentación Completa**: Guías funcionales y técnicas bilingües

### 🔧 Aspectos Técnicos Destacados
- **Cumplimiento Odoo 18.0**: Vistas `<list>` modernas, atributos condicionales apropiados
- **Anclajes Estables**: Herencia de configuración usando selectores xpath estables 
- **Gestión de Credenciales**: Almacenamiento seguro con campos de contraseña
- **Validación de Entrada**: Filtros de dominio apropiados para idiomas publicados

### ⚠️ Limitaciones de v18.0.1.0.0
- Procesamiento limitado a 10 tareas por ciclo cron (cada 5 minutos)
- Sin reintento automático para fallas de API
- Reinicio manual requerido para recuperación de errores
- Reporte básico de errores sin diagnósticos avanzados

**Nota**: Características avanzadas disponibles en versiones posteriores (18.0.1.1.0+).

## Documentación

### Navegación de Idiomas
- **Documentación en Inglés**: [README.md](README.md)
- **Documentación en Español**: Este archivo (README.es.md)

### Guías Detalladas (v18.0.1.0.0)
- **Guía Funcional EN**: [docs/functional/guide.en.md](docs/functional/guide.en.md)
- **Guía Funcional ES**: [docs/functional/guide.es.md](docs/functional/guide.es.md)
- **Guía Técnica EN**: [docs/technical/guide.en.md](docs/technical/guide.en.md)
- **Guía Técnica ES**: [docs/technical/guide.es.md](docs/technical/guide.es.md)
- **Plan de Implementación**: [docs/plan/PLAN.md](docs/plan/PLAN.md)
- **Registro de Cambios**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

## Información del Desarrollador

**Autor**: Gilson Rincón, CEO y Fundador  
**Empresa**: Solutto Consulting LLC  
**Email**: support@soluttoconsulting.com  
**Sitio Web**: https://soluttoconsulting.com

## Soporte

Para soporte técnico, solicitudes de características o reportes de errores, por favor contacte:
- **Email**: support@soluttoconsulting.com
- **Sitio Web**: https://soluttoconsulting.com

## Licencia

Este módulo está licenciado bajo la Licencia Pública General Menor de GNU v3.0 (LGPL-3).  
Vea [LICENSE](LICENSE) para más detalles.

## Información de Versión

- **Versión del Módulo**: 18.0.1.0.0
- **Versión de Odoo**: 18.0 Community
- **Última Actualización**: Septiembre 2025

---

*Este módulo sigue los estándares de desarrollo y mejores prácticas de Solutto Consulting para Odoo 18.0.*
