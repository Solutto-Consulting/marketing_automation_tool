# Herramienta de Gestión de Contenido para Odoo (sc_marketing_automation_tool)

[![Versión de Odoo](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![Versión](https://img.shields.io/badge/Versión-18.0.1.0.1-green.svg)](https://github.com/Solutto-Consulting/marketing_automation_tool)
[![Licencia](https://img.shields.io/badge/Licencia-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Descripción General

La **Herramienta de Gestión de Contenido para Odoo v18.0.1.0.1** es una plataforma integral de **automatización de contenido impulsada por IA** que cuenta con agentes de IA especializados para la investigación y generación de contenido. Esta herramienta optimiza el flujo de trabajo de creación de contenido desde la ideación hasta la publicación.

**🌍 [English Version](README.md) | 📚 [Documentación Completa](docs/)**

## Características Principales (v18.0.1.0.1)

### 🤖 **Estrategia de Contenido Basada en Agentes**
- **Agente de Investigación de Contenido**: Descubrimiento de temas impulsado por IA usando capacidades de búsqueda web
- **Agente de Generación de Contenido**: Creación completa de publicaciones de blog a partir de ideas de investigación
- **Generación de Imágenes con IA**: Imágenes profesionales de portada de blog usando el modelo gpt-image-1
- **Instrucciones Configurables**: Prompts del sistema personalizables para cada tipo de agente

### 📊 **Monitoreo y Análisis de Uso**
- **Seguimiento Integral de Uso**: Monitoreo en tiempo real para todas las operaciones de la API de OpenAI
- **Panel de Control Interactivo**: Análisis visuales con desgloses diarios y seguimiento de costos
- **Monitoreo Específico por Operación**: Seguimiento dedicado para investigación, generación y creación de imágenes
- **Herramientas de Optimización de Costos**: Análisis de uso de tokens y monitoreo de presupuesto

### ⚙️ **Configuración Empresarial**
- **Configuraciones Centralizadas**: Panel de configuración dedicado para Automatización de Marketing
- **Gestión de Modelos Estática**: Definiciones de modelos confiables independientes de la disponibilidad de la API
- **Marco de Seguridad**: Gestión mejorada de credenciales y controles de acceso
- **Soporte Multi-Empresa**: Configuraciones dependientes de la empresa y aislamiento de datos

### 🔄 **Procesamiento en Segundo Plano**
- **Procesamiento Asíncrono de Tareas**: Ejecución no bloqueante para todas las operaciones de contenido
- **Trabajos Cron Inteligentes**: Procesadores separados para tareas de investigación y generación
- **Recuperación de Errores**: Manejo integral de errores con mecanismos de reintento
- **Gestión de Estados**: Estados de tareas claros con pistas de auditoría

## Documentación

### 📖 Guías de Usuario
- **[Guía Funcional (Español)](docs/functional/guide.es.md)**: Flujos de trabajo y características para usuarios finales
- **[Functional User Guide (English)](docs/functional/guide.en.md)**: End-user workflows and features

### 🔧 Documentación Técnica
- **[Guía Técnica para Desarrolladores (Español)](docs/technical/guide.es.md)**: Arquitectura, patrones de desarrollo e integración de APIs
- **[Technical Developer Guide (English)](docs/technical/guide.en.md)**: Architecture, development patterns, and API integration

### 📋 Recursos Adicionales
- **[Matriz de Cobertura de Características](docs/coverage-matrix.md)**: Mapeo completo de características a documentación
- **[Historial de Versiones](docs/CHANGELOG.md)**: Historial detallado de versiones y actualizaciones de características
- **[Plan de Desarrollo](docs/plan/PLAN.md)**: Hoja de ruta del proyecto y estado de implementación

## Inicio Rápido

### 1. Instalación
```bash
# Clonar o copiar módulo al directorio de addons personalizados
cp -r sc_marketing_automation_tool /ruta/a/odoo/custom-addons/

# Instalar dependencias Python
pip install openai-agents>=0.2.9

# Instalar módulo en Odoo
./odoo-bin -d tu_base_datos -i sc_marketing_automation_tool
```

### 2. Configuración
1. Navegar a **Configuración > Configuración General > Herramienta de Automatización de Marketing**
2. Ingresar sus credenciales de la API de OpenAI
3. Configurar instrucciones de agentes IA para su estrategia de contenido
4. Probar la conexión y comenzar a crear contenido

### 3. Flujo de Trabajo de Contenido
1. **Investigación**: Crear tareas de investigación de contenido para descubrir temas en tendencia
2. **Revisión**: Aprobar ideas de contenido descubiertas para generación
3. **Generar**: Lanzar generación de contenido para ideas aprobadas
4. **Publicar**: Revisar y publicar artículos de blog generados

## Matriz de Características por Versión

### ✅ Características Actuales (v18.0.1.0.1)

#### **Estrategia de Contenido**
- ✅ Agente de Investigación de Contenido con capacidades de búsqueda web
- ✅ Agente de Generación de Contenido para creación de artículos de blog
- ✅ Generación de imágenes impulsada por IA con modelo gpt-image-1
- ✅ Flujo de trabajo multi-agente desde investigación hasta publicación
- ✅ Sistema de aprobación y revisión de ideas de contenido

#### **Monitoreo y Análisis**
- ✅ Seguimiento integral de uso de OpenAI
- ✅ Panel de control interactivo con análisis de costos
- ✅ Informes de desglose diario y análisis de tendencias
- ✅ Monitoreo específico por operación (investigación/generación/imágenes)

#### **Arquitectura Técnica**
- ✅ Integración con SDK de Agentes OpenAI (v0.2.9+)
- ✅ Procesamiento asíncrono en segundo plano
- ✅ Gestión de configuración centralizada
- ✅ Seguridad mejorada y manejo de errores

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
