# Guía Técnica: Herramienta de Gestión de Contenido para Odoo v18.0.1.0.0

## Tabla de Contenidos
1. [Descripción General de la Arquitectura](#descripción-general-de-la-arquitectura)
2. [Estructura del Módulo](#estructura-del-módulo)
3. [Modelos de Datos](#modelos-de-datos)
4. [Puntos de Integración](#puntos-de-integración)
5. [Implementación de API](#implementación-de-api)
6. [Marco de Seguridad](#marco-de-seguridad)
7. [Gestión de Configuración](#gestión-de-configuración)
8. [Procesamiento en Segundo Plano](#procesamiento-en-segundo-plano)
9. [Manejo de Errores](#manejo-de-errores)
10. [Implementación Específica de la Versión](#implementación-específica-de-la-versión)
11. [Pautas de Desarrollo](#pautas-de-desarrollo)
12. [Marco de Pruebas](#marco-de-pruebas)

---

## Descripción General de la Arquitectura

La Herramienta de Gestión de Contenido para Odoo v18.0.1.0.0 implementa una arquitectura modular para la traducción de contenido impulsada por IA, construida sobre los estándares de Odoo 18.0 e integrada con los modelos de lenguaje de OpenAI.

### Componentes del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Interfaz Usuario│    │ Lógica Negocio  │    │  APIs Externas  │
│                 │    │                 │    │                 │
│ • Lista Posts   │    │ • Tareas de     │    │ • API OpenAI    │
│   Blog          │◄──►│   Traducción    │◄──►│ • Lista Modelos │
│ • Asistente     │    │ • Gestor Tareas │    │ • Ejecución     │
│   Traducción    │    │ • Trabajos Cron │    │   Traducción    │
│ • Vistas Tareas │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Capa de Datos  │
                    │                 │
                    │ • sc.translation│
                    │   .task         │
                    │ • blog.post     │
                    │   (extendido)   │
                    │ • res.config    │
                    │   .settings     │
                    └─────────────────┘
```

### Principios de Diseño Clave (v18.0.1.0.0)
- **Cumplimiento Odoo 18.0**: Sintaxis de vista moderna y atributos condicionales
- **Procesamiento Asíncrono**: Ejecución de traducción no bloqueante
- **Recuperación de Errores**: Capacidades de reinicio manual de tareas
- **Seguridad Primero**: Almacenamiento cifrado de credenciales y controles de acceso
- **Extensibilidad**: Base para futuras características de automatización

---

## Estructura del Módulo

### Organización de Archivos
```
sc_marketing_automation_tool/
├── __init__.py                    # Inicialización del módulo
├── __manifest__.py                # Manifiesto del módulo (v18.0.1.0.0)
├── models/
│   ├── __init__.py
│   ├── res_config_settings.py     # Configuración OpenAI
│   ├── sc_translation_task.py     # Modelo de tarea de traducción
│   └── blog_post.py               # Extensiones de post de blog
├── wizard/
│   ├── __init__.py
│   └── sc_translate_blog_post_wizard.py  # Asistente de traducción
├── views/
│   ├── res_config_settings_views.xml     # UI de configuración
│   ├── sc_translation_task_views.xml     # Vistas de gestión de tareas
│   ├── blog_post_views.xml               # Mejoras de post de blog
│   └── sc_translate_blog_post_wizard_views.xml  # UI del asistente
├── security/
│   ├── ir.model.access.csv        # Controles de acceso a modelos
│   └── security.xml               # Grupos y reglas de registro
├── data/
│   ├── ir_actions_server.xml      # Acciones de servidor
│   ├── ir_cron.xml                # Trabajos programados
│   └── menu.xml                   # Estructura de menú
├── i18n/
│   └── es_ES.po                   # Traducciones al español
├── docs/                          # Documentación
└── requirements.txt               # Dependencias externas
```

### Matriz de Dependencias
| Dependencia | Tipo | Propósito | Restricción de Versión |
|-------------|------|-----------|------------------------|
| base | Núcleo Odoo | Modelos base | 18.0+ |
| website | Núcleo Odoo | Integración sitio web | 18.0+ |
| website_blog | Núcleo Odoo | Modelo post de blog | 18.0+ |
| mail | Núcleo Odoo | Integración chatter | 18.0+ |
| openai-agents | Externa | SDK OpenAI | 0.2.9+ |

---

## Modelos de Datos

### sc.translation.task

**Propósito**: Rastrea solicitudes individuales de traducción y su estado de ejecución.

```python
class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'Tarea de Traducción IA'
    _inherit = ['mail.thread']  # Integración chatter
    _order = 'create_date desc'

    # Campos Principales
    name = fields.Char(string='Nombre de Tarea', required=True)
    blog_post_id = fields.Many2one('blog.post', required=True, ondelete='cascade')
    target_lang_id = fields.Many2one('res.lang', required=True)
    system_instructions = fields.Text(string='Instrucciones del Sistema')
    
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
