# SC Marketing Automation Tool - Guía Técnica

## Tabla de Contenidos

1. [Descripción General del Módulo](#descripción-general-del-módulo)
2. [Arquitectura y Patrones de Diseño](#arquitectura-y-patrones-de-diseño)
3. [Modelos de Datos](#modelos-de-datos)
4. [Integraciones Externas](#integraciones-externas)
5. [Implementación de Seguridad](#implementación-de-seguridad)
6. [Procesamiento Asíncrono](#procesamiento-asíncrono)
7. [Gestión de Configuración](#gestión-de-configuración)
8. [Endpoints de API](#endpoints-de-api)
9. [Manejo de Errores y Logging](#manejo-de-errores-y-logging)
10. [Estrategia de Pruebas](#estrategia-de-pruebas)
11. [Optimización de Rendimiento](#optimización-de-rendimiento)
12. [Despliegue y Mantenimiento](#despliegue-y-mantenimiento)

## Descripción General del Módulo

### Metadatos del Módulo
- **Nombre**: `sc_marketing_automation_tool`
- **Versión**: 18.0.1.0.0
- **Categoría**: Marketing
- **Autor**: Solutto Consulting LLC
- **Desarrollador**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)
- **Versión de Odoo**: 18.0+

### Dependencias
El módulo requiere los siguientes módulos de Odoo:
```python
'depends': [
    'base',
    'website_blog',
    'mail',  # Requerido para funcionalidad de chatter
    'queue_job',  # Para procesamiento asíncrono
]
```

### Dependencias Externas
El módulo se integra con el **OpenAI Agents Python SDK v0.2.9**:
```bash
# Comando de instalación
pip install openai-agents==0.2.9

# Variables de entorno requeridas
export OPENAI_API_KEY=sk-tu-clave-api-aqui
```

**Nota**: La clave API de OpenAI debe configurarse como variable de entorno para la autenticación.

## Arquitectura y Patrones de Diseño

### Arquitectura Central
El módulo sigue los patrones arquitectónicos de Odoo 18.0 con estos componentes clave:

1. **Modelo de Tareas de Traducción** (`sc.translation.task`)
   - Orquestador central para operaciones de traducción
   - Gestiona estado y seguimiento de progreso de traducción
   - Maneja procesamiento en lotes y gestión de colas

2. **Extensión de Publicación de Blog** (herencia de `blog.post`)
   - Extiende funcionalidad central del blog
   - Añade campos y métodos relacionados con traducción
   - Mantiene compatibilidad hacia atrás

3. **Gestor de Configuración** (`ir.config_parameter`)
   - Gestiona configuraciones de API de OpenAI
   - Almacena preferencias de traducción
   - Maneja configuraciones multi-empresa

4. **Procesador Asíncrono** (integración Queue Job)
   - Ejecución de traducción en segundo plano
   - Seguimiento de progreso y recuperación de errores
   - Limitación de velocidad y mecanismos de reintento

### Patrones de Diseño Utilizados

#### 1. Patrón Factory
```python
class TranslationTaskFactory:
    """Factory para crear tareas de traducción basadas en tipo de contenido."""
    
    @staticmethod
    def create_task(content_type, source_content, target_language):
        if content_type == 'blog_post':
            return BlogPostTranslationTask(source_content, target_language)
        elif content_type == 'bulk_content':
            return BulkTranslationTask(source_content, target_language)
        # Tipos de contenido adicionales...
```

#### 2. Patrón Observer
```python
class TranslationObserver:
    """Observer para actualizaciones de progreso de traducción."""
    
    def update_progress(self, task_id, progress_data):
        # Actualizar componentes UI
        # Enviar notificaciones
        # Registrar eventos de progreso
```

#### 3. Patrón Strategy
```python
class TranslationStrategy:
    """Patrón strategy para diferentes enfoques de traducción."""
    
    def execute_translation(self, content, target_language):
        raise NotImplementedError
        
class OpenAITranslationStrategy(TranslationStrategy):
    def execute_translation(self, content, target_language):
        # Implementación específica de OpenAI
```

## Modelos de Datos

### sc.translation.task

#### Campos Principales
```python
class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'Gestión de Tareas de Traducción con IA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    
    # Identificación principal
    name = fields.Char(
        string='Nombre de Tarea',
        required=True,
        help="Nombre descriptivo para la tarea de traducción"
    )
    
    # Soporte multi-empresa
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        help="Empresa a la que pertenece esta tarea"
    )
    
    # Configuración de traducción
    source_language = fields.Selection(
        [('en', 'Inglés'), ('es', 'Español'), ('fr', 'Francés')],
        string='Idioma Origen',
        required=True,
        default='en'
    )
    
    target_language = fields.Selection(
        [('en', 'Inglés'), ('es', 'Español'), ('fr', 'Francés')],
        string='Idioma Destino',
        required=True
    )
    
    # Seguimiento de estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('queued', 'En Cola'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    
    # Seguimiento de progreso
    progress_percentage = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress',
        store=True
    )
    
    # Referencias de contenido
    blog_post_ids = fields.Many2many(
        'blog.post',
        string='Publicaciones de Blog',
        domain="[('company_id', '=', company_id)]",
        check_company=True
    )
    
    # Resultados y logs
    result_data = fields.Text(
        string='Resultados de Traducción',
        help="Datos JSON que contienen resultados de traducción"
    )
    
    error_log = fields.Text(
        string='Log de Errores',
        help="Información detallada de errores para depuración"
    )
```

#### Campos Calculados
```python
@api.depends('blog_post_ids', 'state')
def _compute_progress(self):
    """Calcular progreso de traducción basado en elementos completados."""
    for record in self:
        if not record.blog_post_ids:
            record.progress_percentage = 0.0
            continue
            
        total_posts = len(record.blog_post_ids)
        completed_posts = len(record.blog_post_ids.filtered(
            lambda p: p.translation_status == 'completed'
        ))
        
        if total_posts > 0:
            record.progress_percentage = (completed_posts / total_posts) * 100.0
        else:
            record.progress_percentage = 0.0
```

#### Métodos de Lógica de Negocio
```python
def start_translation(self):
    """Iniciar el proceso de traducción."""
    self.ensure_one()
    
    if self.state != 'draft':
        raise UserError(_("Solo las tareas en borrador pueden iniciarse"))
        
    if not self.blog_post_ids:
        raise UserError(_("No hay publicaciones de blog seleccionadas para traducción"))
    
    # Validar configuración de OpenAI
    self._validate_openai_config()
    
    # Actualizar estado y poner en cola el trabajo
    self.write({'state': 'queued'})
    
    # Poner en cola el trabajo de traducción
    self.with_delay()._process_translation_async()
    
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _("Traducción Iniciada"),
            'message': _("La tarea de traducción ha sido puesta en cola para procesamiento"),
            'type': 'success',
        }
    }

def _validate_openai_config(self):
    """Validar configuración de API de OpenAI."""
    api_key = self.env['ir.config_parameter'].sudo().get_param(
        'sc_marketing_automation.openai_api_key'
    )
    
    if not api_key:
        raise UserError(_(
            "Clave API de OpenAI no configurada. "
            "Por favor configúrela en Configuración > Marketing Automation."
        ))
    
    # Lógica de validación adicional...
```

### blog.post (Extendido)

#### Campos Añadidos
```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    # Seguimiento de estado de traducción
    translation_status = fields.Selection([
        ('not_translated', 'No Traducido'),
        ('pending', 'Traducción Pendiente'),
        ('in_progress', 'Traducción en Progreso'),
        ('completed', 'Traducción Completada'),
        ('failed', 'Traducción Fallida')
    ], string='Estado de Traducción', default='not_translated')
    
    # Respaldo de contenido original
    original_content = fields.Html(
        string='Contenido Original',
        help="Respaldo del contenido original antes de la traducción"
    )
    
    # Metadatos de traducción
    translated_by_ai = fields.Boolean(
        string='Traducido por IA',
        default=False,
        help="Indica si esta publicación fue traducida usando IA"
    )
    
    translation_task_id = fields.Many2one(
        'sc.translation.task',
        string='Tarea de Traducción',
        help="Tarea de traducción asociada"
    )
    
    # Seguimiento de idioma
    content_language = fields.Selection([
        ('en', 'Inglés'),
        ('es', 'Español'),
        ('fr', 'Francés')
    ], string='Idioma del Contenido', default='en')
```

## Integraciones Externas

### Integración con OpenAI Agents Python SDK

#### Configuración
```python
# Variables de Entorno Requeridas
OPENAI_API_KEY = "sk-tu-clave-api-aqui"
OPENAI_AGENTS_DONT_LOG_TOOL_DATA = "1"  # Para seguridad
```

#### Configuración de Autenticación
```python
from agents import set_default_openai_key

def setup_openai_client(self):
    """Configurar cliente OpenAI con autenticación apropiada."""
    api_key = self.env['ir.config_parameter'].sudo().get_param(
        'sc_marketing_automation.openai_api_key'
    )
    
    if not api_key:
        raise UserError(_("Clave API de OpenAI no configurada"))
    
    # Establecer la clave API para la sesión
    set_default_openai_key(api_key)
    
    return True
```

#### Configuración del Agente de Traducción
```python
from agents import Agent, Runner
import asyncio

class OpenAITranslationService:
    """Clase de servicio para operaciones de traducción de OpenAI."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.setup_agent()
    
    def setup_agent(self):
        """Inicializar el agente de traducción."""
        self.translation_agent = Agent(
            name="Agente de Traducción de Blog",
            instructions="""
            Eres un traductor profesional de contenido especializado en publicaciones de blog.
            
            Instrucciones:
            1. Mantén la estructura HTML original y el formato
            2. Preserva todas las etiquetas HTML y atributos
            3. Traduce solo el contenido de texto, no los elementos HTML
            4. Mantén el tono y estilo apropiado para la audiencia objetivo
            5. Asegura traducciones amigables para SEO
            6. Mantén la precisión de terminología técnica
            
            Requisitos:
            - Preserva todas las etiquetas <p>, <h1>-<h6>, <ul>, <ol>, <li>
            - Mantén todos los atributos class e id intactos
            - Traduce meta descripciones y textos alt
            - Mantén estructuras de enlaces y URLs
            """,
            model="gpt-4o-mini"  # Modelo costo-efectivo para traducción
        )
    
    async def translate_content(self, content, target_language, source_language='en'):
        """Traducir contenido de publicación de blog."""
        try:
            prompt = f"""
            Traduce el siguiente contenido de publicación de blog de {source_language} a {target_language}.
            
            Contenido Origen:
            {content}
            
            Idioma Destino: {target_language}
            
            Requisitos:
            - Mantén todo el formato HTML
            - Preserva la precisión técnica
            - Usa tono apropiado para la audiencia objetivo
            - Mantén consideraciones SEO en mente
            """
            
            result = await Runner.run(self.translation_agent, prompt)
            return result.final_output
            
        except Exception as e:
            _logger.error(f"Traducción falló: {str(e)}")
            raise UserError(_(f"Traducción falló: {str(e)}"))
```

#### Limitación de Velocidad y Manejo de Errores
```python
import time
from functools import wraps

def rate_limit_decorator(calls_per_minute=60):
    """Decorador para implementar limitación de velocidad para llamadas API."""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit_decorator(calls_per_minute=20)  # Limitación conservadora de velocidad
def make_translation_request(self, content, target_language):
    """Hacer solicitud de traducción con limitación de velocidad."""
    return self.openai_service.translate_content(content, target_language)
```

#### Mecanismo de Reintento
```python
import backoff
from openai import OpenAI

@backoff.on_exception(
    backoff.expo,
    (ConnectionError, TimeoutError),
    max_tries=3,
    base=2,
    factor=2
)
async def robust_translation_call(self, content, target_language):
    """Llamada de traducción con reintento de backoff exponencial."""
    try:
        return await self.openai_service.translate_content(content, target_language)
    except Exception as e:
        _logger.warning(f"Intento de traducción falló: {str(e)}")
        raise
```

## Implementación de Seguridad

### Reglas de Seguridad Multi-Empresa
```xml
<!-- Regla de Registro para Tareas de Traducción -->
<record id="translation_task_company_rule" model="ir.rule">
    <field name="name">Tarea de Traducción: Multi-Empresa</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Listas de Control de Acceso (ACLs)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_translation_task_user,sc.translation.task.user,model_sc_translation_task,base.group_user,1,1,1,0
access_translation_task_manager,sc.translation.task.manager,model_sc_translation_task,website_blog.group_blog_manager,1,1,1,1
```

### Seguridad de Clave API
```python
class MarketingAutomationConfig(models.TransientModel):
    _name = 'marketing.automation.config.settings'
    _inherit = 'res.config.settings'
    
    openai_api_key = fields.Char(
        string='Clave API de OpenAI',
        help="Clave API para servicios de OpenAI",
        config_parameter='sc_marketing_automation.openai_api_key'
    )
    
    @api.model
    def set_values(self):
        """Override para añadir validación de clave API."""
        super().set_values()
        
        # Validar formato de clave API
        if self.openai_api_key and not self.openai_api_key.startswith('sk-'):
            raise UserError(_("Formato de clave API de OpenAI inválido"))
    
    def test_openai_connection(self):
        """Probar conectividad de API de OpenAI."""
        if not self.openai_api_key:
            raise UserError(_("Por favor ingrese una clave API primero"))
        
        try:
            # Lógica de prueba de conexión
            self._test_api_connection()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Conexión Exitosa"),
                    'message': _("La conexión API de OpenAI está funcionando correctamente"),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f"Conexión falló: {str(e)}"))
```

## Procesamiento Asíncrono

### Integración con Queue Job
```python
from odoo.addons.queue_job.job import job

class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    # ... otro código ...
    
    @job(default_channel='root.translation')
    def _process_translation_async(self):
        """Procesamiento asíncrono de traducción."""
        try:
            self.write({'state': 'processing'})
            
            # Procesar cada publicación de blog
            for blog_post in self.blog_post_ids:
                self._translate_single_post(blog_post)
                
            self.write({'state': 'completed'})
            self._send_completion_notification()
            
        except Exception as e:
            self.write({
                'state': 'failed',
                'error_log': str(e)
            })
            self._send_error_notification(str(e))
            _logger.error(f"Tarea de traducción {self.id} falló: {str(e)}")
    
    def _translate_single_post(self, blog_post):
        """Traducir una sola publicación de blog."""
        try:
            blog_post.write({'translation_status': 'in_progress'})
            
            # Respaldar contenido original
            if not blog_post.original_content:
                blog_post.original_content = blog_post.content
            
            # Realizar traducción
            translated_content = self._call_openai_translation(
                blog_post.content,
                self.target_language,
                self.source_language
            )
            
            # Actualizar publicación de blog
            blog_post.write({
                'content': translated_content,
                'translation_status': 'completed',
                'translated_by_ai': True,
                'content_language': self.target_language,
                'translation_task_id': self.id
            })
            
        except Exception as e:
            blog_post.write({'translation_status': 'failed'})
            raise
```

### Cron Job para Monitoreo de Progreso
```xml
<!-- Cron Job para Monitoreo de Progreso de Traducción -->
<record id="cron_translation_progress_monitor" model="ir.cron">
    <field name="name">Monitor de Progreso de Traducción</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="state">code</field>
    <field name="code">model._monitor_translation_progress()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

## Gestión de Configuración

### Parámetros del Sistema
```python
# Parámetros de configuración por defecto
DEFAULT_CONFIG = {
    'sc_marketing_automation.openai_api_key': '',
    'sc_marketing_automation.default_model': 'gpt-4o-mini',
    'sc_marketing_automation.max_retry_attempts': '3',
    'sc_marketing_automation.rate_limit_per_minute': '20',
    'sc_marketing_automation.timeout_seconds': '30',
    'sc_marketing_automation.enable_content_backup': 'True'
}
```

### Configuración Multi-Empresa
```python
def get_company_config(self, param_name):
    """Obtener parámetro de configuración para empresa actual."""
    company_param = f"{param_name}.company_{self.env.company.id}"
    
    # Intentar parámetro específico de empresa primero
    value = self.env['ir.config_parameter'].sudo().get_param(company_param)
    
    # Recurrir a parámetro global
    if not value:
        value = self.env['ir.config_parameter'].sudo().get_param(param_name)
    
    return value
```

## Endpoints de API

### API REST para Gestión de Traducción
```python
from odoo import http
from odoo.http import request

class TranslationAPIController(http.Controller):
    
    @http.route('/api/translation/status/<int:task_id>', 
                type='json', auth='user', methods=['GET'])
    def get_translation_status(self, task_id):
        """Obtener estado de tarea de traducción vía API."""
        try:
            task = request.env['sc.translation.task'].browse(task_id)
            
            if not task.exists():
                return {'error': 'Tarea no encontrada', 'code': 404}
            
            return {
                'status': 'success',
                'data': {
                    'id': task.id,
                    'name': task.name,
                    'state': task.state,
                    'progress': task.progress_percentage,
                    'source_language': task.source_language,
                    'target_language': task.target_language
                }
            }
            
        except Exception as e:
            return {'error': str(e), 'code': 500}
    
    @http.route('/api/translation/start', 
                type='json', auth='user', methods=['POST'])
    def start_translation(self, **kwargs):
        """Iniciar tarea de traducción vía API."""
        try:
            blog_post_ids = kwargs.get('blog_post_ids', [])
            target_language = kwargs.get('target_language')
            
            if not blog_post_ids or not target_language:
                return {'error': 'Parámetros requeridos faltantes', 'code': 400}
            
            task = request.env['sc.translation.task'].create({
                'name': f"Traducción API a {target_language}",
                'target_language': target_language,
                'blog_post_ids': [(6, 0, blog_post_ids)]
            })
            
            task.start_translation()
            
            return {
                'status': 'success',
                'data': {
                    'task_id': task.id,
                    'message': 'Traducción iniciada exitosamente'
                }
            }
            
        except Exception as e:
            return {'error': str(e), 'code': 500}
```

## Manejo de Errores y Logging

### Gestión Integral de Errores
```python
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class TranslationErrorHandler:
    """Manejo centralizado de errores para operaciones de traducción."""
    
    @staticmethod
    def handle_openai_error(error, context=""):
        """Manejar errores específicos de OpenAI."""
        error_messages = {
            'RateLimitError': _("Límite de velocidad excedido. Por favor intente más tarde."),
            'AuthenticationError': _("Clave API inválida. Por favor verifique la configuración."),
            'APIConnectionError': _("Conexión falló. Por favor verifique la conexión a internet."),
            'InvalidRequestError': _("Formato de solicitud inválido."),
            'ServiceUnavailableError': _("Servicio de OpenAI temporalmente no disponible.")
        }
        
        error_type = type(error).__name__
        user_message = error_messages.get(error_type, _("Ocurrió un error inesperado."))
        
        # Registrar error detallado para depuración
        _logger.error(f"Error OpenAI [{context}]: {error_type} - {str(error)}")
        
        # Retornar mensaje amigable para usuario
        return user_message
    
    @staticmethod
    def log_translation_error(task_id, error, blog_post_id=None):
        """Registrar errores de traducción con contexto."""
        context = {
            'task_id': task_id,
            'blog_post_id': blog_post_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': fields.Datetime.now()
        }
        
        _logger.error(f"Error de Traducción: {context}")
        
        # Almacenar en base de datos para auditoría
        request.env['sc.translation.error.log'].sudo().create({
            'task_id': task_id,
            'blog_post_id': blog_post_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_context': json.dumps(context)
        })
```

### Sistema de Verificación de Salud
```python
def system_health_check(self):
    """Realizar verificación de salud del sistema para servicio de traducción."""
    health_status = {
        'overall': 'saludable',
        'components': {}
    }
    
    # Verificar conectividad API de OpenAI
    try:
        self._test_openai_connection()
        health_status['components']['openai'] = 'saludable'
    except Exception as e:
        health_status['components']['openai'] = f'no saludable: {str(e)}'
        health_status['overall'] = 'degradado'
    
    # Verificar servicio de queue job
    try:
        queue_jobs = self.env['queue.job'].search([
            ('state', 'in', ['pending', 'enqueued', 'started']),
            ('channel', 'like', 'translation')
        ])
        health_status['components']['queue'] = f'saludable ({len(queue_jobs)} trabajos)'
    except Exception as e:
        health_status['components']['queue'] = f'no saludable: {str(e)}'
        health_status['overall'] = 'no saludable'
    
    return health_status
```

## Estrategia de Pruebas

### Pruebas Unitarias
```python
from odoo.tests import tagged, TransactionCase
from unittest.mock import patch, MagicMock

@tagged('post_install', '-at_install')
class TestSCTranslationTask(TransactionCase):
    """Suite de pruebas para funcionalidad de SC Translation Task."""
    
    def setUp(self):
        super().setUp()
        
        # Crear datos de prueba
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Blog de Prueba',
        })
        
        self.test_post = self.env['blog.post'].create({
            'name': 'Publicación de Prueba',
            'content': '<p>Este es el contenido de una publicación de blog de prueba.</p>',
            'blog_id': self.test_blog.id,
        })
        
        self.translation_task = self.env['sc.translation.task'].create({
            'name': 'Tarea de Traducción de Prueba',
            'source_language': 'en',
            'target_language': 'es',
            'blog_post_ids': [(6, 0, [self.test_post.id])]
        })
    
    def test_translation_task_creation(self):
        """Probar creación de tarea de traducción."""
        self.assertEqual(self.translation_task.state, 'draft')
        self.assertEqual(len(self.translation_task.blog_post_ids), 1)
        self.assertEqual(self.translation_task.progress_percentage, 0.0)
    
    @patch('odoo.addons.sc_marketing_automation_tool.models.translation_task.OpenAITranslationService')
    def test_translation_process(self, mock_openai):
        """Probar proceso de traducción con servicio OpenAI simulado."""
        # Simular respuesta de OpenAI
        mock_openai.return_value.translate_content.return_value = '<p>Este es el contenido de una publicación de blog de prueba.</p>'
        
        # Iniciar traducción
        self.translation_task.start_translation()
        
        # Verificar cambio de estado
        self.assertEqual(self.translation_task.state, 'queued')
    
    def test_multi_company_security(self):
        """Probar control de acceso multi-empresa."""
        company_2 = self.env['res.company'].create({
            'name': 'Empresa de Prueba 2',
        })
        
        # Crear tarea en empresa diferente
        task_company_2 = self.translation_task.with_company(company_2)
        
        # Probar aislamiento de empresa
        self.assertNotEqual(
            self.translation_task.company_id,
            company_2
        )
```

### Pruebas de Integración
```python
@tagged('post_install', '-at_install', 'external_api')
class TestOpenAIIntegration(TransactionCase):
    """Pruebas de integración para API de OpenAI (requiere clave API válida)."""
    
    def setUp(self):
        super().setUp()
        self.api_key = os.environ.get('OPENAI_API_KEY_TEST')
        if not self.api_key:
            self.skipTest("No se proporcionó clave API de prueba")
    
    def test_openai_connection(self):
        """Probar conexión real de API de OpenAI."""
        service = OpenAITranslationService(self.api_key)
        
        # Probar traducción simple
        result = service.translate_content(
            "<p>Hola mundo</p>",
            "es",
            "en"
        )
        
        self.assertIn("<p>", result)
        self.assertIn("</p>", result)
```

### Pruebas de Rendimiento
```python
@tagged('performance')
class TestTranslationPerformance(TransactionCase):
    """Pruebas de rendimiento para operaciones de traducción."""
    
    def test_bulk_translation_performance(self):
        """Probar rendimiento con múltiples publicaciones de blog."""
        import time
        
        # Crear múltiples publicaciones de prueba
        posts = []
        for i in range(10):
            post = self.env['blog.post'].create({
                'name': f'Publicación de Prueba {i}',
                'content': f'<p>Contenido de prueba {i}</p>' * 100,  # Contenido más largo
                'blog_id': self.test_blog.id,
            })
            posts.append(post.id)
        
        # Crear tarea de traducción en lotes
        task = self.env['sc.translation.task'].create({
            'name': 'Prueba de Rendimiento en Lotes',
            'source_language': 'en',
            'target_language': 'es',
            'blog_post_ids': [(6, 0, posts)]
        })
        
        # Medir tiempo de procesamiento
        start_time = time.time()
        # Simular procesamiento...
        end_time = time.time()
        
        processing_time = end_time - start_time
        self.assertLess(processing_time, 60)  # Debe completarse en 60 segundos
```

## Optimización de Rendimiento

### Optimización de Base de Datos
```python
# Consultas optimizadas para grandes conjuntos de datos
def get_pending_translations(self, limit=100):
    """Obtener traducciones pendientes con consulta optimizada."""
    return self.env['sc.translation.task'].search([
        ('state', '=', 'queued')
    ], limit=limit, order='create_date ASC')

# Procesamiento en lotes para mejor rendimiento
def process_translations_batch(self, batch_size=10):
    """Procesar traducciones en lotes para optimizar uso de memoria."""
    tasks = self.get_pending_translations(limit=batch_size)
    
    for task in tasks:
        try:
            task._process_translation_async()
        except Exception as e:
            _logger.error(f"Error de procesamiento en lotes para tarea {task.id}: {str(e)}")
            continue
```

### Estrategia de Caché
```python
from functools import lru_cache

class TranslationCache:
    """Caché de resultados de traducción para reducir llamadas API."""
    
    @lru_cache(maxsize=1000)
    def get_cached_translation(self, content_hash, target_language):
        """Obtener resultado de traducción en caché."""
        return self.env['sc.translation.cache'].search([
            ('content_hash', '=', content_hash),
            ('target_language', '=', target_language)
        ], limit=1)
    
    def cache_translation_result(self, content, target_language, result):
        """Almacenar resultado de traducción en caché para uso futuro."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        self.env['sc.translation.cache'].create({
            'content_hash': content_hash,
            'target_language': target_language,
            'original_content': content,
            'translated_content': result,
            'cache_date': fields.Datetime.now()
        })
```

## Despliegue y Mantenimiento

### Instrucciones de Instalación
```bash
# 1. Instalar dependencias de Python
pip install openai-agents==0.2.9

# 2. Establecer variables de entorno
export OPENAI_API_KEY=sk-tu-clave-api-aqui
export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1

# 3. Actualizar ruta de addons de Odoo
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --addons-path=odoo-src/addons,enterprise,themes,custom-addons

# 4. Instalar el módulo
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  -d tu_base_datos -i sc_marketing_automation_tool
```

### Pasos de Configuración
1. **Navegar a Configuración > Marketing Automation**
2. **Ingresar Clave API de OpenAI**
3. **Configurar preferencias de traducción**
4. **Probar conexión API**
5. **Configurar canales de queue job**

### Tareas de Mantenimiento
```bash
# Script de mantenimiento semanal
#!/bin/bash

# Limpiar logs de traducción antiguos
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --shell -d tu_base_datos << EOF
env['sc.translation.task'].search([
    ('create_date', '<', fields.Date.today() - relativedelta(months=3))
]).unlink()
EOF

# Optimizar caché de traducción
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --shell -d tu_base_datos << EOF
env['sc.translation.cache'].search([
    ('cache_date', '<', fields.Date.today() - relativedelta(weeks=2))
]).unlink()
EOF
```

### Monitoreo y Alertas
```python
def setup_monitoring_alerts(self):
    """Configurar alertas de monitoreo para servicio de traducción."""
    
    # Monitorear traducciones fallidas
    failed_tasks = self.env['sc.translation.task'].search_count([
        ('state', '=', 'failed'),
        ('create_date', '>=', fields.Datetime.now() - timedelta(hours=24))
    ])
    
    if failed_tasks > 5:  # Umbral de alerta
        self._send_admin_alert(
            f"Alta tasa de fallos: {failed_tasks} traducciones fallidas en 24h"
        )
    
    # Monitorear uso de API
    api_calls_today = self._get_api_usage_count()
    if api_calls_today > 1000:  # Umbral de uso
        self._send_admin_alert(
            f"Alto uso de API: {api_calls_today} llamadas hoy"
        )
```

### Guía de Solución de Problemas
1. **Fallos de traducción**: Verificar configuración de clave API y conectividad de red
2. **Problemas de queue job**: Verificar instalación y configuración del módulo queue_job
3. **Problemas de rendimiento**: Revisar configuración de tamaño de lote y índices de base de datos
4. **Problemas de memoria**: Implementar límites de tamaño de contenido y lotes de procesamiento
5. **Limitación de velocidad**: Ajustar parámetros de límite de velocidad e implementar estrategias de backoff

---

## Soporte y Documentación

Para soporte técnico adicional, contactar:
- **Desarrollador**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)
- **Empresa**: Solutto Consulting LLC
- **Documentación**: Ver [Guía de Usuario](../functional/guide.es.md)
- **Referencia API**: [OpenAI Agents Python SDK](https://github.com/openai/openai-agents-python)
