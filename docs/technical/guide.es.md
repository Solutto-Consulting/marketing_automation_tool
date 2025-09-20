# Guía Técnica para Desarrolladores: Herramienta de Gestión de Contenido v18.0.1.0.1

## Tabla de Contenidos
1. [Visión General de la Arquitectura](#visión-general-de-la-arquitectura)
2. [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
3. [Referencia de Modelos Principales](#referencia-de-modelos-principales)
4. [Patrones de Integración de API](#patrones-de-integración-de-api)
5. [Desarrollo de Vistas e Interfaces](#desarrollo-de-vistas-e-interfaces)
6. [Procesamiento en Segundo Plano](#procesamiento-en-segundo-plano)
7. [Implementación de Seguridad](#implementación-de-seguridad)
8. [Personalización y Extensión](#personalización-y-extensión)
9. [Pruebas y Aseguramiento de Calidad](#pruebas-y-aseguramiento-de-calidad)
10. [Despliegue y Mantenimiento](#despliegue-y-mantenimiento)

---

## Visión General de la Arquitectura

### Arquitectura del Sistema

La Herramienta de Gestión de Contenido v18.0.1.0.1 sigue una arquitectura modular basada en agentes diseñada para escalabilidad y mantenibilidad.

```
┌─────────────────────────────────────────────────────────────┐
│                   Capa de Interfaz de Usuario               │
├─────────────────────────────────────────────────────────────┤
│  IU Configuración │  Asistentes │  Vistas (Lista/Form/Kanban)│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Capa de Lógica de Negocio                 │
├─────────────────────────────────────────────────────────────┤
│  Ideas Contenido │ Tareas Generación │ Config Agentes │ Utils│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Capa de Integración                      │
├─────────────────────────────────────────────────────────────┤
│     SDK Agentes OpenAI    │    Lector Contenido Web        │
│     Registro Solicitudes  │    Monitoreo Uso               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Servicios Externos                      │
├─────────────────────────────────────────────────────────────┤
│      API OpenAI          │      APIs Búsqueda Web         │
└─────────────────────────────────────────────────────────────┘
```

### Patrones de Diseño Clave

#### 1. Procesamiento Basado en Agentes
- **Agente de Investigación de Contenido**: Especializado en búsqueda web y descubrimiento de contenido
- **Agente de Generación de Contenido**: Optimizado para creación y formato de artículos de blog
- **Instrucciones Configurables**: Comportamiento personalizable por agente vía prompts del sistema

#### 2. Métodos de Modelo Primero
Toda la lógica de negocio se implementa en métodos de modelo en lugar de acciones del servidor

#### 3. Procesamiento Asíncrono en Segundo Plano
- **Trabajos Cron**: Procesamiento separado para tareas de investigación y generación
- **Gestión de Estados**: Transiciones claras de estado (draft → in_progress → done/error)
- **Aislamiento de Errores**: Fallos individuales de tareas no afectan el procesamiento por lotes

#### 4. Registro Integral
- **Registro de Solicitudes**: Todas las llamadas a la API de OpenAI registradas con seguimiento de costos
- **Seguimiento de Errores**: Captura detallada de errores para resolución de problemas
- **Monitoreo de Uso**: Análisis en tiempo real de costos y uso

### Dependencias del Módulo

#### Dependencias Principales de Odoo
- `base`: Framework principal de Odoo
- `mail`: Soporte para chatter y hilos
- `website`: Integración de sitio web y blog
- `website_blog`: Creación y gestión de artículos de blog

#### Dependencias Externas
- `openai-agents` (>=0.2.9): SDK Agentes OpenAI para operaciones IA
- Librerías estándar de Python: `json`, `logging`, `datetime`, `requests`
---

## Configuración del Entorno de Desarrollo

### Prerrequisitos

#### Requisitos del Sistema
- Python 3.8+ con pip
- Odoo 18.0 Community o Enterprise
- Git para control de versiones
- Editor de texto con soporte Python

#### Acceso a API
- Cuenta API OpenAI con acceso de organización
- Clave API con límites de uso suficientes
- (Opcional) Clave API de administrador para monitoreo de uso

### Pasos de Instalación

#### 1. Clonar y Configurar Módulo
```bash
# Navegar al directorio de addons personalizados
cd /ruta/a/odoo/custom-addons

# Clonar o copiar el módulo
cp -r /fuente/sc_marketing_automation_tool .

# Instalar dependencias Python
pip install -r sc_marketing_automation_tool/requirements.txt
```

#### 2. Instalar Dependencias
```bash
# Instalar SDK Agentes OpenAI
pip install openai-agents>=0.2.9

# Instalar requisitos adicionales si es necesario
pip install requests beautifulsoup4 lxml
```

#### 3. Configurar Odoo
```bash
# Actualizar Odoo con nuevo módulo
./odoo-bin -d tu_base_datos -i sc_marketing_automation_tool --stop-after-init

# O actualizar instalación existente
./odoo-bin -d tu_base_datos -u sc_marketing_automation_tool --stop-after-init
```

#### 4. Configurar Credenciales API
1. Navegar a Configuración > Configuración General > Herramienta de Automatización de Marketing
2. Ingresar clave API OpenAI e ID de organización
3. Probar conexión usando validación proporcionada
4. Configurar instrucciones de agentes IA

---

## Referencia de Modelos Principales

### Modelo de Idea de Contenido (`sc.content.idea`)

#### Propósito
Almacena ideas de contenido descubiertas desde tareas de investigación con metadatos y estado de aprobación.

#### Campos Principales
```python
class ScContentIdea(models.Model):
    _name = 'sc.content.idea'
    _description = 'Idea de Contenido'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Campos Principales
    title = fields.Char(string='Título del Artículo', required=True, tracking=True)
    url = fields.Char(string='URL Fuente', required=True)
    published_date = fields.Date(string='Fecha de Publicación')
    summary = fields.Text(string='Resumen', required=True)
    
    # Campos de Flujo de Trabajo  
    state = fields.Selection([
        ('pending', 'Pendiente de Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('used', 'Usado para Contenido'),
        ('archived', 'Archivado')
    ], default='pending', tracking=True)
```

### Modelo de Tarea de Investigación de Contenido (`sc.content.idea.task`)

#### Propósito
Gestiona tareas de investigación en segundo plano que generan múltiples ideas de contenido.

#### Gestión de Estados
```python
state = fields.Selection([
    ('draft', 'Borrador'),           # Creado, en cola para procesamiento
    ('in_progress', 'Procesando'),   # Actualmente siendo procesado
    ('done', 'Completado'),          # Completado exitosamente
    ('error', 'Error')               # Falló con error
], default='draft', tracking=True)
```

### Modelo de Tarea de Generación de Contenido (`sc.content.generation.task`)

#### Propósito
Maneja la generación de artículos de blog desde ideas de contenido o temas personalizados.

#### Campos Clave
```python
class ScContentGenerationTask(models.Model):
    _name = 'sc.content.generation.task'
    _description = 'Tarea de Generación de Contenido'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre de Tarea', required=True)
    content_idea_id = fields.Many2one('sc.content.idea', string='Idea de Contenido')
    custom_topic = fields.Char(string='Tema Personalizado')
    target_blog_id = fields.Many2one('blog.blog', string='Blog Objetivo', required=True)
    generated_blog_post_id = fields.Many2one('blog.post', string='Artículo Generado')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'Procesando'),
        ('done', 'Completado'),
        ('error', 'Error')
    ], default='draft', tracking=True)
```

### Modelo de Configuración de Agente IA (`sc.ai.agent.config`)

#### Propósito
Almacena configuraciones de agentes IA con instrucciones personalizables y configuraciones de modelo.

#### Estructura de Configuración
```python
class ScAiAgentConfig(models.Model):
    _name = 'sc.ai.agent.config'
    _description = 'Configuración de Agente IA'

    name = fields.Char(string='Nombre de Configuración', required=True)
    agent_type = fields.Selection([
        ('research', 'Investigación de Contenido'),
        ('generation', 'Generación de Contenido')
    ], required=True)
    
    model_id = fields.Many2one('sc.openai.models', string='Modelo OpenAI')
    instructions = fields.Text(string='Instrucciones del Agente', required=True)
    
    # Parámetros de configuración
    temperature = fields.Float(string='Temperatura', default=0.7)
    max_tokens = fields.Integer(string='Tokens Máximos', default=2000)
```

---

## Patrones de Integración de API

### Integración SDK Agentes OpenAI

#### Inicialización de Agente
```python
from openai_agents import Agent, WebSearchTool

def _initialize_research_agent(self, config):
    """Inicializar agente de investigación con capacidades de búsqueda web"""
    agent = Agent(
        model=config.model_id.name,
        instructions=config.instructions,
        tools=[WebSearchTool()],
        temperature=config.temperature
    )
    return agent
```

#### Patrón de Manejo de Errores
```python
def _safe_api_call(self, func, *args, **kwargs):
    """Envolvente para llamadas seguras a API OpenAI con lógica de reintento"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            
            # Registrar solicitud exitosa
            self._log_api_request(success=True, **result.usage)
            
            return result
            
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Retroceso exponencial
                continue
            raise
            
        except openai.AuthenticationError as e:
            _logger.error(f"Autenticación OpenAI falló: {e}")
            raise UserError("Autenticación API OpenAI falló. Por favor verifique su clave API.")
            
        except Exception as e:
            # Registrar solicitud fallida
            self._log_api_request(success=False, error=str(e))
            raise
```

---

## Desarrollo de Vistas e Interfaces

### Estándares de Vistas Odoo 18.0

#### Patrón de Vista Lista
```xml
<!-- Siempre usar <list> en lugar de <tree> en Odoo 18.0 -->
<record id="view_sc_content_idea_list" model="ir.ui.view">
    <field name="name">sc.content.idea.list</field>
    <field name="model">sc.content.idea</field>
    <field name="arch" type="xml">
        <list default_order="create_date desc">
            <field name="title"/>
            <field name="published_date"/>
            <field name="state" decoration-info="state=='pending'" 
                               decoration-success="state=='approved'"
                               decoration-danger="state=='rejected'"/>
            <field name="create_date"/>
        </list>
    </field>
</record>
```

#### Vista Kanban con Grupos
```xml
<record id="view_sc_content_generation_task_kanban" model="ir.ui.view">
    <field name="name">sc.content.generation.task.kanban</field>
    <field name="model">sc.content.generation.task</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" class="o_kanban_small_column">
            <field name="name"/>
            <field name="content_idea_id"/>
            <field name="target_blog_id"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-card">
                    <div class="oe_kanban_content">
                        <div class="oe_kanban_details">
                            <strong><field name="name"/></strong>
                            <div t-if="record.content_idea_id.raw_value">
                                Idea: <field name="content_idea_id"/>
                            </div>
                            <div>
                                Blog: <field name="target_blog_id"/>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

## Procesamiento en Segundo Plano

### Configuración de Trabajos Cron

#### Cron de Procesamiento de Investigación
```xml
<record id="cron_process_research_tasks" model="ir.cron">
    <field name="name">Procesar Tareas de Investigación de Contenido</field>
    <field name="model_id" ref="model_sc_content_idea_task"/>
    <field name="state">code</field>
    <field name="code">model.action_process_research_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```

#### Procesamiento por Lotes
```python
@api.model
def action_process_research_tasks(self):
    """Procesar tareas de investigación en lotes"""
    # Obtener tareas pendientes (límite para rendimiento)
    pending_tasks = self.search([
        ('state', '=', 'draft')
    ], limit=10, order='create_date asc')
    
    for task in pending_tasks:
        try:
            task._process_research_task()
            self.env.cr.commit()  # Confirmar cada tarea individualmente
        except Exception as e:
            self.env.cr.rollback()  # Retroceder solo esta tarea
            _logger.error(f"Falló procesar tarea de investigación {task.id}: {e}")
```

---

## Implementación de Seguridad

### Listas de Control de Acceso (ACL)

#### Permisos de Modelo
```csv
# ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sc_content_idea_manager,sc.content.idea manager,model_sc_content_idea,group_marketing_manager,1,1,1,1
access_sc_content_idea_user,sc.content.idea user,model_sc_content_idea,group_marketing_user,1,1,1,0
```

#### Grupos de Seguridad
```xml
<record id="group_marketing_user" model="res.groups">
    <field name="name">Usuario de Marketing</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## Personalización y Extensión

### Extensión de Configuración de Agentes

#### Campos Personalizados
```python
class ScAiAgentConfig(models.Model):
    _inherit = 'sc.ai.agent.config'
    
    # Agregar campos específicos de industria
    industry_focus = fields.Selection([
        ('technology', 'Tecnología'),
        ('healthcare', 'Salud'), 
        ('finance', 'Finanzas'),
        ('education', 'Educación'),
        ('retail', 'Comercio Minorista')
    ], string='Enfoque Industrial')
```

---

## Pruebas y Aseguramiento de Calidad

### Marco de Pruebas Unitarias

#### Estructura de Pruebas
```python
from odoo.tests.common import TransactionCase

class TestContentIdea(TransactionCase):
    
    def test_content_idea_creation(self):
        """Probar creación de idea de contenido"""
        idea = self.env['sc.content.idea'].create({
            'title': 'Artículo de Prueba',
            'url': 'https://ejemplo.com/prueba',
            'summary': 'Resumen de prueba'
        })
        
        self.assertEqual(idea.state, 'pending')
        self.assertEqual(idea.title, 'Artículo de Prueba')
```

---

## Despliegue y Mantenimiento

### Lista de Verificación de Despliegue
- [ ] Respaldar base de datos existente
- [ ] Instalar/actualizar módulo en entorno de staging
- [ ] Ejecutar suite completa de pruebas
- [ ] Configurar credenciales API de producción
- [ ] Verificar que trabajos cron estén activos
- [ ] Probar flujos de trabajo principales de extremo a extremo
- [ ] Monitorear logs para errores

### Herramientas de Monitoreo

#### Verificación de Salud del Sistema
```python
@api.model
def system_health_check(self):
    """Verificación integral de salud del sistema"""
    health_status = {
        'openai_connection': self._test_openai_connection(),
        'pending_tasks': self._count_pending_tasks(),
        'error_rate': self._calculate_error_rate(),
        'last_successful_run': self._get_last_successful_run()
    }
    
    # Registrar estado de salud
    _logger.info(f"Verificación de salud del sistema: {health_status}")
    
    return health_status
```

---

## Referencias Externas

### Ejemplos del Núcleo de Odoo
- **Patrones de IU de Configuraciones**: `odoo-src/odoo/addons/base/views/res_config_settings_views.xml`
- **Integración Mail Thread**: `odoo-src/addons/mail/models/mail_thread.py`
- **Ejemplos de Trabajos Cron**: `odoo-src/addons/base/data/ir_cron_data.xml`
- **Patrones de Reglas de Seguridad**: `odoo-src/addons/base/security/ir_rule.xml`

### Documentación de API Externa
- **SDK Agentes OpenAI**: [https://github.com/openai/openai-agents](https://github.com/openai/openai-agents) (v0.2.9+)
- **Referencia API OpenAI**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- **Endpoints API de Uso**: [https://platform.openai.com/docs/api-reference/usage](https://platform.openai.com/docs/api-reference/usage)

### Librerías Python
- **Requests**: Cliente HTTP para web scraping y llamadas API
- **BeautifulSoup4**: Análisis HTML para extracción de contenido
- **JSON**: Serialización de datos para respuestas API

### Límites de Tasa y Mejores Prácticas
- **Límites de Tasa API**: Límites basados en nivel según nivel de suscripción OpenAI
- **Políticas de Reintento**: Retroceso exponencial con máximo 3 intentos
- **Configuraciones de Timeout**: 30-60 segundos para solicitudes de generación de contenido
- **Manejo de Errores**: Categorización integral de errores y retroalimentación al usuario

---

*Versión de documentación técnica: 18.0.1.0.1 | Última actualización: 20 de septiembre, 2025*
    
    # Gestión de Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'), 
        ('done', 'Completada'),
        ('error', 'Error')
    ], default='draft', required=True, tracking=True)
    
    error_message = fields.Text(string='Detalles del Error')
```

**Métodos Clave**:
- `action_reset_to_draft()`: Reinicia tareas fallidas para reintento
- `_get_translation_data()`: Extrae contenido del post de blog para traducción
- `_update_blog_post_translations()`: Aplica contenido traducido (implementación v18.0.1.0.0)

### blog.post (Extendido)

**Propósito**: Modelo de post de blog mejorado con capacidades de seguimiento de traducción.

```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    # Seguimiento de Traducción
    translation_task_ids = fields.One2many(
        'sc.translation.task', 'blog_post_id',
        string='Tareas de Traducción'
    )
    translation_in_progress = fields.Boolean(
        string='Traducción en Progreso', 
        default=False,
        help="Indica si hay tareas de traducción en cola o ejecutándose"
    )
    
    # Campos Calculados
    translation_count = fields.Integer(
        string='Cantidad de Traducciones',
        compute='_compute_translation_count'
    )
```

### res.config.settings (Extendido)

**Propósito**: Gestión centralizada de configuración de OpenAI.

```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Configuración OpenAI
    sc_openai_api_key = fields.Char(
        string='Clave API OpenAI',
        config_parameter='sc_marketing_automation_tool.openai_api_key',
        password=True
    )
    sc_openai_organization_id = fields.Char(
        string='ID Organización OpenAI',
        config_parameter='sc_marketing_automation_tool.openai_organization_id'
    )
    sc_openai_model = fields.Selection(
        selection='_get_openai_models',
        string='Modelo OpenAI',
        config_parameter='sc_marketing_automation_tool.openai_model',
        default='gpt-4o'
    )
```

---

## Puntos de Integración

### Integración SDK OpenAI Agents

**Soporte de Versión**: openai-agents 0.2.9+

```python
# Patrón de Integración Principal (v18.0.1.0.0)
import asyncio
from agents import Agent, Runner

async def perform_ai_translation(model_name, system_instructions, prompt):
    """
    Ejecuta traducción IA usando SDK OpenAI Agents.
    
    Args:
        model_name (str): Identificador del modelo OpenAI
        system_instructions (str): Orientación de comportamiento IA
        prompt (str): Contenido de solicitud de traducción
        
    Returns:
        str: Contenido traducido como cadena JSON
    """
    agent = Agent(
        name="Traductor Blog Odoo",
        instructions=system_instructions or "Traduce contenido con precisión preservando formato y estructura.",
        model=model_name
    )
    
    result = await Runner.run(agent, prompt)
    return result.final_output
```

### Configuración de Entorno

**Variables de Entorno Requeridas**:
```bash
# Configuración API OpenAI
OPENAI_API_KEY=sk-...                    # Desde configuración Odoo
OPENAI_ORGANIZATION=org-...              # Desde configuración Odoo (opcional)

# Configuración Odoo
ODOO_DATABASE=nombre_tu_base_datos
ODOO_CONF_FILE=/ruta/a/odoo.conf
```

---

## Implementación de API

### Selección Dinámica de Modelos

**Endpoint**: API OpenAI v1/models  
**Propósito**: Poblar modelos disponibles en menú desplegable de configuración

```python
def _get_openai_models(self):
    """
    Obtiene modelos OpenAI disponibles desde API.
    
    Returns:
        list: Tuplas de (model_id, model_name) para campo Selection
    """
    try:
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.openai_api_key'
        )
        
        if not api_key:
            return self._get_fallback_models()
            
        # Implementación de llamada API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json().get('data', [])
            gpt_models = [
                (model['id'], model['id']) 
                for model in models 
                if model['id'].startswith('gpt-')
            ]
            return sorted(gpt_models)
            
    except Exception as e:
        _logger.warning(f"Error al obtener modelos OpenAI: {e}")
        
    return self._get_fallback_models()

def _get_fallback_models(self):
    """Modelos de respaldo cuando API no está disponible."""
    return [
        ('gpt-4o', 'gpt-4o'),
        ('gpt-4-turbo', 'gpt-4-turbo'),
        ('gpt-3.5-turbo', 'gpt-3.5-turbo'),
    ]
```

### Estructura de Datos de Traducción

**Esquema JSON para Solicitudes de Traducción**:
```json
{
    "name": "Título del post de blog",
    "subtitle": "Subtítulo del post de blog", 
    "content": "<p>Contenido HTML del post de blog</p>",
    "website_meta_title": "Título SEO",
    "website_meta_description": "Descripción SEO",
    "website_meta_keywords": "palabra1, palabra2"
}
```

---

## Marco de Seguridad

### Grupos de Control de Acceso

```xml
<!-- security/security.xml -->
<record id="group_marketing_manager" model="res.groups">
    <field name="name">Gerente de Marketing</field>
    <field name="category_id" ref="base.module_category_marketing"/>
</record>

<record id="group_marketing_user" model="res.groups">
    <field name="name">Usuario de Marketing</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('group_marketing_manager'))]"/>
</record>
```

### Control de Acceso a Modelos

```csv
# security/ir.model.access.csv
id,name,model_id/id,group_id/id,perm_read,perm_write,perm_create,perm_unlink
access_sc_translation_task_manager,sc.translation.task.manager,model_sc_translation_task,group_marketing_manager,1,1,1,1
access_sc_translation_task_user,sc.translation.task.user,model_sc_translation_task,group_marketing_user,1,0,1,0
```

### Reglas de Registro

```xml
<!-- Seguridad multi-empresa (si aplica) -->
<record id="rule_translation_task_company" model="ir.rule">
    <field name="name">Regla Empresa Tarea Traducción</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```

---

## Gestión de Configuración

### Implementación de Vista de Configuración

**Patrón de Referencia**: Basado en herencia de configuración principal de Odoo

```xml
<!-- views/res_config_settings_views.xml -->
<record id="res_config_settings_view_form_inherit_sc" model="ir.ui.view">
    <field name="name">res.config.settings.form.inherit.sc</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base_setup.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//setting[@id='partner_autocomplete']" position="after">
            <setting id="sc_ai_marketing_tools" string="Herramientas Marketing IA">
                <div class="content-group">
                    <div class="mt16">
                        <field name="sc_openai_api_key" password="True"/>
                        <label for="sc_openai_api_key" class="o_light_label"/>
                    </div>
                    <div class="mt16">
                        <field name="sc_openai_organization_id"/>
                        <label for="sc_openai_organization_id" class="o_light_label"/>
                    </div>
                    <div class="mt16">
                        <field name="sc_openai_model"/>
                        <label for="sc_openai_model" class="o_light_label"/>
                    </div>
                </div>
            </setting>
        </xpath>
    </field>
</record>
```

**Referencia Principal Usada**:
- **Archivo**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anclaje**: `//setting[@id='partner_autocomplete']` (selector estable)
- **Posición**: `after` (punto de inserción seguro)

---

## Procesamiento en Segundo Plano

### Configuración de Trabajo Cron

```xml
<!-- data/ir_cron.xml -->
<record id="ir_cron_process_translation_tasks" model="ir.cron">
    <field name="name">Procesar Tareas de Traducción</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="state">code</field>
    <field name="code">model._cron_process_translation_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

### Lógica de Procesamiento (v18.0.1.0.0)

```python
@api.model
def _cron_process_translation_tasks(self):
    """
    Procesador en segundo plano para tareas de traducción.
    Procesa hasta 10 tareas en borrador por ejecución.
    """
    tasks = self.search([('state', '=', 'draft')], limit=10)
    
    for task in tasks:
        try:
            # Actualizar estado para prevenir procesamiento duplicado
            task.state = 'in_progress'
            self.env.cr.commit()
            
            # Obtener configuración
            config = self._get_openai_config()
            if not config:
                task._handle_error("Configuración OpenAI no encontrada")
                continue
                
            # Preparar datos de traducción
            translation_data = task._get_translation_data()
            prompt = task._build_translation_prompt(translation_data)
            
            # Ejecutar traducción IA
            translated_content = asyncio.run(
                perform_ai_translation(
                    config['model'],
                    task.system_instructions,
                    prompt
                )
            )
            
            # Aplicar traducción
            task._update_blog_post_translations(translated_content)
            task.state = 'done'
            
        except Exception as e:
            task._handle_error(str(e))
            
        finally:
            self.env.cr.commit()
```

---

## Manejo de Errores

### Categorías de Error (v18.0.1.0.0)

| Tipo de Error | Estrategia de Manejo | Método de Recuperación |
|---------------|---------------------|------------------------|
| Configuración API | Falla inmediata | Corregir configuración, reiniciar tarea |
| Límites Velocidad API | Retraso elegante | Esperar y reintentar manualmente |
| Contenido Muy Grande | Validación tamaño | Reducir contenido, reintentar |
| Timeout Red | Manejo excepción | Verificar conectividad, reintentar |
| Error Parse JSON | Validación formato | Revisar salida IA, reintentar |

### Patrón de Recuperación de Errores

```python
def _handle_error(self, error_message):
    """
    Manejo estándar de errores para tareas de traducción.
    
    Args:
        error_message (str): Descripción del error
    """
    self.write({
        'state': 'error',
        'error_message': error_message
    })
    
    # Reiniciar estado del post de blog
    self.blog_post_id.translation_in_progress = False
    
    # Registrar error para depuración
    _logger.error(
        f"Tarea de traducción {self.id} falló: {error_message}"
    )
```

---

## Implementación Específica de la Versión

### Cumplimiento Estándares Odoo 18.0

**Vistas de Lista**:
```xml
<!-- ✅ CORRECTO: Usar <list> para Odoo 18.0 -->
<field name="arch" type="xml">
    <list string="Tareas de Traducción">
        <field name="name"/>
        <field name="blog_post_id"/>
        <field name="target_lang_id"/>
        <field name="state" widget="badge" 
               decoration-info="state in ('draft', 'in_progress')"
               decoration-success="state == 'done'"
               decoration-danger="state == 'error'"/>
    </list>
</field>
```

**Atributos Condicionales**:
```xml
<!-- ✅ CORRECTO: Sintaxis condicional moderna -->
<button name="action_reset_to_draft" 
        string="Reiniciar a Borrador"
        type="object"
        invisible="state != 'error'"
        class="btn-secondary"/>
```

**Vistas Kanban**:
```xml
<!-- ✅ OBLIGATORIO: default_group_by para Kanban -->
<kanban default_group_by="state" class="o_kanban_small_column">
    <field name="state"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div class="oe_kanban_content">
                    <div><strong><field name="name"/></strong></div>
                    <div><field name="blog_post_id"/></div>
                    <div><field name="target_lang_id"/></div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

### Integración Chatter

```xml
<!-- Formulario Post Blog con chatter -->
<form string="Post de Blog">
    <sheet>
        <!-- Contenido del formulario -->
    </sheet>
    <!-- ✅ REQUERIDO: Chatter al final del formulario cuando se usa mail.thread -->
    <chatter/>
</form>
```

---

## Pautas de Desarrollo

### Estándares de Código

1. **Estándares Python**:
   - Seguir pautas de estilo PEP 8
   - Usar anotaciones de tipo donde aplique
   - Implementar manejo apropiado de excepciones
   - Agregar docstrings comprehensivos

2. **Estándares XML**:
   - Usar sintaxis moderna de Odoo 18.0
   - Implementar selectores xpath estables
   - Seguir convenciones de nomenclatura consistentes
   - Incluir etiquetas de campo apropiadas y texto de ayuda

3. **Estándares JavaScript**:
   - No aplica para v18.0.1.0.0 (solo lado servidor)

### Pautas de Pruebas (v18.0.1.0.0)

**Nota**: La implementación de pruebas unitarias está planificada para versiones futuras.

```python
# Estructura de pruebas futura
class TestTranslationTask(common.TransactionCase):
    def setUp(self):
        super(TestTranslationTask, self).setUp()
        self.translation_task = self.env['sc.translation.task']
        
    def test_task_creation(self):
        """Probar lógica de creación de tarea de traducción."""
        # Implementación pendiente
        pass
        
    def test_cron_processing(self):
        """Probar procesamiento en segundo plano con llamadas API simuladas."""
        # Implementación pendiente
        pass
```

---

## Marco de Pruebas

### Lista de Verificación de Pruebas Manuales (v18.0.1.0.0)

#### Pruebas de Configuración
- [ ] Validación clave API OpenAI
- [ ] Carga dinámica de modelos
- [ ] Selección de modelo de respaldo
- [ ] Manejo ID organización

#### Pruebas de Flujo de Trabajo de Traducción  
- [ ] Selección de posts de blog
- [ ] Funcionalidad del asistente
- [ ] Creación de tareas
- [ ] Procesamiento en segundo plano
- [ ] Manejo de errores
- [ ] Funcionalidad de reinicio de tareas

#### Pruebas UI/UX
- [ ] Integración página de configuración
- [ ] Vistas de lista de tareas
- [ ] Agrupación vista kanban
- [ ] Diseño vista formulario
- [ ] Integración chatter

#### Pruebas de Seguridad
- [ ] Aplicación control de acceso
- [ ] Enmascarado campo contraseña
- [ ] Aislamiento multi-empresa
- [ ] Límites de permisos

---

## Referencias Externas

### Referencias de Implementación Principal
- **Patrón Configuración Base**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anclaje Usado**: `//setting[@id='partner_autocomplete']` (selector estable)
- **Integración Correo**: Patrones estándar Odoo `mail.thread` y `mail.activity.mixin`

### Documentación Oficial
- **SDK OpenAI Agents**: https://github.com/openai/openai-agents-python
- **Documentación SDK**: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md
- **Referencia API**: https://platform.openai.com/docs/api-reference
- **Guía Desarrollador Odoo 18.0**: https://www.odoo.com/documentation/18.0/developer/

### Dependencias de Versión
- **openai-agents**: 0.2.9+ (fijado en requirements.txt)
- **Python**: 3.9+ (requerido por openai-agents)
- **Odoo**: 18.0 Community o Enterprise

---

*Versión Documentación Técnica: 18.0.1.0.0 | Última Actualización: Septiembre 2025*
