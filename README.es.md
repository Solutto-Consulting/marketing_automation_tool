# Herramienta de Gestión de Contenido para Odoo (sc_marketing_automation_tool)

[![Versión de Odoo](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![Licencia](https://img.shields.io/badge/Licencia-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Descripción General

La **Herramienta de Gestión de Contenido para Odoo** mejora y automatiza las actividades de marketing dentro del ecosistema Odoo mediante la integración de Inteligencia Artificial para procesos de traducción de contenido. Este módulo proporciona a los administradores herramientas poderosas para optimizar los flujos de trabajo de traducción de artículos de blog utilizando los modelos de lenguaje avanzados de OpenAI.

## Características Principales

- **Integración con OpenAI**: Configuración centralizada para credenciales de API de OpenAI y selección de modelos
- **Traducción Masiva de Blogs**: Acción de servidor en artículos de blog para traducción simultánea de múltiples artículos
- **Traducción Potenciada por IA**: Aprovecha los modelos de lenguaje de OpenAI para traducción de contenido de alta calidad
- **Asistente Intuitivo**: Interfaz fácil de usar para seleccionar idiomas objetivo y proporcionar instrucciones a la IA
- **Procesamiento Asíncrono**: Procesamiento de traducción en segundo plano para evitar bloqueos de la interfaz
- **Gestión de Tareas**: Seguimiento integral y gestión de estado para solicitudes de traducción
- **Manejo de Errores**: Gestión robusta de errores con capacidades de reinicio de tareas
- **Soporte Multi-idioma**: Internacionalización incorporada con soporte de traducción al español

## Especificaciones Técnicas

### Dependencias
- **Módulos de Odoo**: base, website, website_blog, mail
- **Librería Externa**: openai-agents (SDK de Python para integración con OpenAI)
- **Versión de Python**: 3.9+ (requerido por openai-agents)

### Modelos Principales
- **sc.translation.task**: Rastrea solicitudes de traducción y su estado
- **blog.post** (extendido): Mejorado con capacidades de seguimiento de traducción
- **res.config.settings** (extendido): Gestión de configuración de OpenAI

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

## Documentación

### Navegación de Idiomas
- **Documentación en Inglés**: [README.md](README.md)
- **Documentación en Español**: Este archivo (README.es.md)

### Guías Detalladas
- **Documentación Funcional**: [docs/functional/](docs/functional/)
- **Documentación Técnica**: [docs/technical/](docs/technical/)
- **Plan de Implementación**: [docs/plan/PLAN.md](docs/plan/PLAN.md)

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
