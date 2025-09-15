# Documentación Funcional: Content Management Tool v18.0.1.0.1

## 📚 Documentos Disponibles

### Guías de Usuario
- 🇺🇸 **[Guía Funcional Completa (Inglés)](guide.en.md)** - Manual completo para usuarios finales
- 🇪🇸 **[Guía Funcional Completa (Español)](guide.es.md)** - Manual completo para usuarios finales en español

### Navegación Rápida
- 📖 **[Índice Principal](../README.md)** - Volver al índice principal de documentación
- ⚙️ **[Documentación Técnica](../technical/README.md)** - Para desarrolladores
- 📑 **[CHANGELOG](../CHANGELOG.md)** - Registro de cambios y versiones

## Resumen del Módulo v18.0.1.0.1

### Capacidades Principales
- 🤖 **Agente de Investigación de Contenido**: Descubrimiento de temas con IA usando búsqueda web
- ✍️ **Agente de Generación de Contenido**: Creación automatizada de artículos de blog
- 🖼️ **Generación de Imágenes con IA**: Imágenes profesionales para portadas de blog
- 📊 **Monitoreo de Uso**: Dashboard para seguimiento de costos y uso de OpenAI
- ⚙️ **Configuración Centralizada**: Sección dedicada de Marketing Automation
- 🌐 **Sistema de Traducción**: Traducción mejorada con OpenAI Agents SDK

### Beneficios Clave
- ⏰ **Ahorro de Tiempo**: Automatización de creación y traducción de contenido
- 🎯 **Consistencia de Calidad**: Modelos de IA profesionales para calidad consistente
- 📈 **Escalabilidad**: Manejo de múltiples tareas simultáneamente con procesamiento en segundo plano
- 🔧 **Flexibilidad**: Instrucciones personalizables para tono y estilo específicos
- 📋 **Seguimiento**: Visibilidad completa del progreso e historial de tareas

## Roles de Usuario y Permisos

### Marketing Manager
- Acceso completo a todas las funcionalidades
- Puede configurar ajustes de OpenAI y agentes
- Puede gestionar y eliminar tareas de todos los tipos
- Can retry failed translations

### Marketing User
- Can initiate translations for blog posts
- Can view translation tasks and history
- Limited to read and create permissions

## Getting Started

### Prerequisites

1. **OpenAI Account**: You need an active OpenAI account with API access
2. **API Credits**: Ensure sufficient OpenAI API credits for translation usage
3. **Blog Content**: Have blog posts created in Odoo Website Blog module

### Initial Setup

1. **Configure OpenAI Settings**
   - Navigate to Settings > General Settings
   - Scroll to "AI Marketing Tools" section
   - Enter your OpenAI API Key
   - Optionally enter your Organization ID
   - Select your preferred AI model (default: GPT-4o)
   - Save settings

2. **Verify Language Setup**
   - Go to Settings > Languages
   - Ensure target languages are installed and active
   - Only active languages will appear in translation options

## Using the Translation Feature

### Step 1: Select Blog Posts

1. Navigate to Website > Blog > Blog Posts
2. Use list view to see multiple posts
3. Select one or more blog posts using checkboxes
4. Click the "Action" dropdown menu
5. Select "Translate with AI"

### Step 2: Configure Translation

1. **Target Language**: Select the language you want to translate to
2. **AI Instructions** (Optional): Provide specific guidance for the AI:
   - Tone preferences (formal, casual, professional)
   - Target audience considerations
   - Industry-specific terminology
   - Style guidelines

### Step 3: Monitor Progress

1. **Translation Tasks**: Go to Marketing Automation > Content Translation > Translation Tasks
2. **Task Status**: Monitor translation progress:
   - **Draft**: Task created, waiting for processing
   - **In Progress**: AI translation in progress
   - **Done**: Translation completed successfully
   - **Error**: Translation failed (see error details)

### Step 4: Review Results

1. **Blog Post History**: Open the translated blog post
2. **Translation History Tab**: View all translation attempts
3. **Content Review**: Check translated content for accuracy
4. **Manual Adjustments**: Make any necessary edits to the translated content

## Advanced Features

### Custom AI Instructions

Enhance translation quality with specific instructions:

**Example Instructions:**
- "Translate in a formal, professional tone suitable for business executives"
- "Use technical terminology appropriate for software developers"
- "Maintain a conversational, friendly tone for general readers"
- "Include cultural context relevant to the target language region"

### Error Recovery

When translations fail:

1. **View Error Details**: Click on failed task to see error message
2. **Reset to Draft**: Use "Reset to Draft" button to retry
3. **Modify Instructions**: Adjust AI instructions if needed
4. **Contact Support**: For persistent issues, contact technical support

### Bulk Translation Management

- **Multiple Languages**: Create tasks for multiple target languages simultaneously
- **Batch Processing**: System processes multiple tasks automatically
- **Priority Handling**: Tasks processed in creation order
- **Resource Management**: Maximum 10 tasks processed every 5 minutes

## Best Practices

### Content Preparation

1. **Complete Content**: Ensure blog posts have all content filled before translation
2. **Clear Structure**: Use proper headings and paragraph structure
3. **Metadata**: Include SEO metadata (title, description, keywords) for translation

### AI Instructions

1. **Be Specific**: Provide clear, specific instructions rather than vague guidance
2. **Target Audience**: Always specify the target audience for better context
3. **Cultural Sensitivity**: Consider cultural nuances for international audiences
4. **Terminology**: Specify industry terms or preferred translations

### Quality Control

1. **Review Translations**: Always review AI-generated translations
2. **Cultural Adaptation**: Adjust content for cultural relevance
3. **SEO Optimization**: Verify translated SEO metadata is appropriate
4. **Consistency Check**: Ensure consistency across related content

## Troubleshooting

### Common Issues and Solutions

**Issue**: "OpenAI API key not configured"
- **Solution**: Configure API key in Settings > General Settings > AI Marketing Tools

**Issue**: Translation tasks stuck in "Draft" status
- **Solution**: Check cron job is running, verify API key validity

**Issue**: Poor translation quality
- **Solution**: Provide more specific AI instructions, try different AI model

**Issue**: "Translation in Progress" flag not clearing
- **Solution**: Reset task to draft or contact administrator

### Performance Tips

1. **Batch Size**: Translate similar content together for consistency
2. **Timing**: Schedule bulk translations during off-peak hours
3. **Monitoring**: Regularly check translation task status
4. **Cleanup**: Archive or delete old completed tasks periodically

## Integration with Odoo Modules

### Website Blog
- Seamless integration with blog post management
- Translation history tracked per post
- Status indicators for translation progress

### Website
- Respects website language settings
- Integrates with multi-language website features
- Maintains SEO metadata across languages

### Mail/Chatter
- Translation tasks include chatter for communication
- Activity tracking for task management
- Notification system for status updates

## Reporting and Analytics

### Translation Metrics
- Number of tasks completed per period
- Success/failure rates
- Average processing time
- Most translated content types

### Usage Analytics
- User activity in translation features
- Popular target languages
- Peak usage times
- Error pattern analysis

## Support and Maintenance

### Regular Maintenance
- Monitor API usage and costs
- Review and clean up old translation tasks
- Update AI instructions based on quality feedback
- Keep OpenAI model selection current

### Getting Help
- Technical issues: Check error messages in task details
- Feature requests: Contact Solutto Consulting
- Training: Request user training sessions
- Support: Email support@soluttoconsulting.com

---

*This module is developed by Solutto Consulting LLC and follows Odoo best practices for marketing automation.*
