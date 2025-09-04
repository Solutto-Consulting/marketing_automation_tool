# SC Marketing Automation Tool - Technical Guide

## Table of Contents

1. [Module Overview](#module-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Data Models](#data-models)
4. [External Integrations](#external-integrations)
5. [Security Implementation](#security-implementation)
6. [Asynchronous Processing](#asynchronous-processing)
7. [Configuration Management](#configuration-management)
8. [API Endpoints](#api-endpoints)
9. [Error Handling & Logging](#error-handling--logging)
10. [Testing Strategy](#testing-strategy)
11. [Performance Optimization](#performance-optimization)
12. [Deployment & Maintenance](#deployment--maintenance)

## Module Overview

### Module Metadata
- **Name**: `sc_marketing_automation_tool`
- **Version**: 18.0.1.0.0
- **Category**: Marketing
- **Author**: Solutto Consulting LLC
- **Developer**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)
- **Odoo Version**: 18.0+

### Dependencies
The module requires the following Odoo modules:
```python
'depends': [
    'base',
    'website_blog',
    'mail',  # Required for chatter functionality
    'queue_job',  # For asynchronous processing
]
```

### External Dependencies
The module integrates with the **OpenAI Agents Python SDK v0.2.9**:
```bash
# Installation command
pip install openai-agents==0.2.9

# Environment variables required
export OPENAI_API_KEY=sk-your-api-key-here
```

**Note**: The OpenAI API key must be configured as an environment variable for authentication.

## Architecture & Design Patterns

### Core Architecture
The module follows Odoo 18.0 architectural patterns with these key components:

1. **Translation Task Model** (`sc.translation.task`)
   - Central orchestrator for translation operations
   - Manages translation state and progress tracking
   - Handles batch processing and queue management

2. **Blog Post Extension** (`blog.post` inheritance)
   - Extends core blog functionality
   - Adds translation-related fields and methods
   - Maintains backward compatibility

3. **Configuration Manager** (`ir.config_parameter`)
   - Manages OpenAI API settings
   - Stores translation preferences
   - Handles multi-company configurations

4. **Asynchronous Processor** (Queue Job integration)
   - Background translation execution
   - Progress tracking and error recovery
   - Rate limiting and retry mechanisms

### Design Patterns Used

#### 1. Factory Pattern
```python
class TranslationTaskFactory:
    """Factory for creating translation tasks based on content type."""
    
    @staticmethod
    def create_task(content_type, source_content, target_language):
        if content_type == 'blog_post':
            return BlogPostTranslationTask(source_content, target_language)
        elif content_type == 'bulk_content':
            return BulkTranslationTask(source_content, target_language)
        # Additional content types...
```

#### 2. Observer Pattern
```python
class TranslationObserver:
    """Observer for translation progress updates."""
    
    def update_progress(self, task_id, progress_data):
        # Update UI components
        # Send notifications
        # Log progress events
```

#### 3. Strategy Pattern
```python
class TranslationStrategy:
    """Strategy pattern for different translation approaches."""
    
    def execute_translation(self, content, target_language):
        raise NotImplementedError
        
class OpenAITranslationStrategy(TranslationStrategy):
    def execute_translation(self, content, target_language):
        # OpenAI-specific implementation
```

## Data Models

### sc.translation.task

#### Core Fields
```python
class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'AI-Powered Translation Task Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    
    # Core identification
    name = fields.Char(
        string='Task Name',
        required=True,
        help="Descriptive name for the translation task"
    )
    
    # Multi-company support
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help="Company this task belongs to"
    )
    
    # Translation configuration
    source_language = fields.Selection(
        [('en', 'English'), ('es', 'Spanish'), ('fr', 'French')],
        string='Source Language',
        required=True,
        default='en'
    )
    
    target_language = fields.Selection(
        [('en', 'English'), ('es', 'Spanish'), ('fr', 'French')],
        string='Target Language',
        required=True
    )
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Progress tracking
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True
    )
    
    # Content references
    blog_post_ids = fields.Many2many(
        'blog.post',
        string='Blog Posts',
        domain="[('company_id', '=', company_id)]",
        check_company=True
    )
    
    # Results and logs
    result_data = fields.Text(
        string='Translation Results',
        help="JSON data containing translation results"
    )
    
    error_log = fields.Text(
        string='Error Log',
        help="Detailed error information for debugging"
    )
```

#### Computed Fields
```python
@api.depends('blog_post_ids', 'state')
def _compute_progress(self):
    """Calculate translation progress based on completed items."""
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

#### Business Logic Methods
```python
def start_translation(self):
    """Initiate the translation process."""
    self.ensure_one()
    
    if self.state != 'draft':
        raise UserError(_("Only draft tasks can be started"))
        
    if not self.blog_post_ids:
        raise UserError(_("No blog posts selected for translation"))
    
    # Validate OpenAI configuration
    self._validate_openai_config()
    
    # Update state and queue the job
    self.write({'state': 'queued'})
    
    # Queue the translation job
    self.with_delay()._process_translation_async()
    
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _("Translation Started"),
            'message': _("Translation task has been queued for processing"),
            'type': 'success',
        }
    }

def _validate_openai_config(self):
    """Validate OpenAI API configuration."""
    api_key = self.env['ir.config_parameter'].sudo().get_param(
        'sc_marketing_automation.openai_api_key'
    )
    
    if not api_key:
        raise UserError(_(
            "OpenAI API key not configured. "
            "Please configure it in Settings > Marketing Automation."
        ))
    
    # Additional validation logic...
```

### blog.post (Extended)

#### Added Fields
```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    # Translation status tracking
    translation_status = fields.Selection([
        ('not_translated', 'Not Translated'),
        ('pending', 'Translation Pending'),
        ('in_progress', 'Translation In Progress'),
        ('completed', 'Translation Completed'),
        ('failed', 'Translation Failed')
    ], string='Translation Status', default='not_translated')
    
    # Original content backup
    original_content = fields.Html(
        string='Original Content',
        help="Backup of original content before translation"
    )
    
    # Translation metadata
    translated_by_ai = fields.Boolean(
        string='Translated by AI',
        default=False,
        help="Indicates if this post was translated using AI"
    )
    
    translation_task_id = fields.Many2one(
        'sc.translation.task',
        string='Translation Task',
        help="Associated translation task"
    )
    
    # Language tracking
    content_language = fields.Selection([
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French')
    ], string='Content Language', default='en')
```

## External Integrations

### OpenAI Agents Python SDK Integration

#### Configuration
```python
# Environment Variables Required
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_AGENTS_DONT_LOG_TOOL_DATA = "1"  # For security
```

#### Authentication Setup
```python
from agents import set_default_openai_key

def setup_openai_client(self):
    """Configure OpenAI client with proper authentication."""
    api_key = self.env['ir.config_parameter'].sudo().get_param(
        'sc_marketing_automation.openai_api_key'
    )
    
    if not api_key:
        raise UserError(_("OpenAI API key not configured"))
    
    # Set the API key for the session
    set_default_openai_key(api_key)
    
    return True
```

#### Translation Agent Configuration
```python
from agents import Agent, Runner
import asyncio

class OpenAITranslationService:
    """Service class for OpenAI translation operations."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize the translation agent."""
        self.translation_agent = Agent(
            name="Blog Translation Agent",
            instructions="""
            You are a professional content translator specializing in blog posts.
            
            Instructions:
            1. Maintain the original HTML structure and formatting
            2. Preserve all HTML tags and attributes
            3. Translate only the text content, not HTML elements
            4. Keep the tone and style appropriate for the target audience
            5. Ensure SEO-friendly translations
            6. Maintain technical terminology accuracy
            
            Requirements:
            - Preserve all <p>, <h1>-<h6>, <ul>, <ol>, <li> tags
            - Keep all class and id attributes intact
            - Translate meta descriptions and alt texts
            - Maintain link structures and URLs
            """,
            model="gpt-4o-mini"  # Cost-effective model for translation
        )
    
    async def translate_content(self, content, target_language, source_language='en'):
        """Translate blog post content."""
        try:
            prompt = f"""
            Translate the following blog post content from {source_language} to {target_language}.
            
            Source Content:
            {content}
            
            Target Language: {target_language}
            
            Requirements:
            - Maintain all HTML formatting
            - Preserve technical accuracy
            - Use appropriate tone for the target audience
            - Keep SEO considerations in mind
            """
            
            result = await Runner.run(self.translation_agent, prompt)
            return result.final_output
            
        except Exception as e:
            _logger.error(f"Translation failed: {str(e)}")
            raise UserError(_(f"Translation failed: {str(e)}"))
```

#### Rate Limiting & Error Handling
```python
import time
from functools import wraps

def rate_limit_decorator(calls_per_minute=60):
    """Decorator to implement rate limiting for API calls."""
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

@rate_limit_decorator(calls_per_minute=20)  # Conservative rate limiting
def make_translation_request(self, content, target_language):
    """Make rate-limited translation request."""
    return self.openai_service.translate_content(content, target_language)
```

#### Retry Mechanism
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
    """Translation call with exponential backoff retry."""
    try:
        return await self.openai_service.translate_content(content, target_language)
    except Exception as e:
        _logger.warning(f"Translation attempt failed: {str(e)}")
        raise
```

## Security Implementation

### Multi-Company Security Rules
```xml
<!-- Record Rule for Translation Tasks -->
<record id="translation_task_company_rule" model="ir.rule">
    <field name="name">Translation Task: Multi-Company</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Access Control Lists (ACLs)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_translation_task_user,sc.translation.task.user,model_sc_translation_task,base.group_user,1,1,1,0
access_translation_task_manager,sc.translation.task.manager,model_sc_translation_task,website_blog.group_blog_manager,1,1,1,1
```

### API Key Security
```python
class MarketingAutomationConfig(models.TransientModel):
    _name = 'marketing.automation.config.settings'
    _inherit = 'res.config.settings'
    
    openai_api_key = fields.Char(
        string='OpenAI API Key',
        help="API key for OpenAI services",
        config_parameter='sc_marketing_automation.openai_api_key'
    )
    
    @api.model
    def set_values(self):
        """Override to add API key validation."""
        super().set_values()
        
        # Validate API key format
        if self.openai_api_key and not self.openai_api_key.startswith('sk-'):
            raise UserError(_("Invalid OpenAI API key format"))
    
    def test_openai_connection(self):
        """Test OpenAI API connectivity."""
        if not self.openai_api_key:
            raise UserError(_("Please enter an API key first"))
        
        try:
            # Test connection logic
            self._test_api_connection()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Connection Successful"),
                    'message': _("OpenAI API connection is working correctly"),
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_(f"Connection failed: {str(e)}"))
```

## Asynchronous Processing

### Queue Job Integration
```python
from odoo.addons.queue_job.job import job

class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    # ... other code ...
    
    @job(default_channel='root.translation')
    def _process_translation_async(self):
        """Asynchronous translation processing."""
        try:
            self.write({'state': 'processing'})
            
            # Process each blog post
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
            _logger.error(f"Translation task {self.id} failed: {str(e)}")
    
    def _translate_single_post(self, blog_post):
        """Translate a single blog post."""
        try:
            blog_post.write({'translation_status': 'in_progress'})
            
            # Backup original content
            if not blog_post.original_content:
                blog_post.original_content = blog_post.content
            
            # Perform translation
            translated_content = self._call_openai_translation(
                blog_post.content,
                self.target_language,
                self.source_language
            )
            
            # Update blog post
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

### Cron Job for Progress Monitoring
```xml
<!-- Cron Job for Translation Progress Monitoring -->
<record id="cron_translation_progress_monitor" model="ir.cron">
    <field name="name">Translation Progress Monitor</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="state">code</field>
    <field name="code">model._monitor_translation_progress()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

## Configuration Management

### System Parameters
```python
# Default configuration parameters
DEFAULT_CONFIG = {
    'sc_marketing_automation.openai_api_key': '',
    'sc_marketing_automation.default_model': 'gpt-4o-mini',
    'sc_marketing_automation.max_retry_attempts': '3',
    'sc_marketing_automation.rate_limit_per_minute': '20',
    'sc_marketing_automation.timeout_seconds': '30',
    'sc_marketing_automation.enable_content_backup': 'True'
}
```

### Multi-Company Configuration
```python
def get_company_config(self, param_name):
    """Get configuration parameter for current company."""
    company_param = f"{param_name}.company_{self.env.company.id}"
    
    # Try company-specific parameter first
    value = self.env['ir.config_parameter'].sudo().get_param(company_param)
    
    # Fall back to global parameter
    if not value:
        value = self.env['ir.config_parameter'].sudo().get_param(param_name)
    
    return value
```

## API Endpoints

### REST API for Translation Management
```python
from odoo import http
from odoo.http import request

class TranslationAPIController(http.Controller):
    
    @http.route('/api/translation/status/<int:task_id>', 
                type='json', auth='user', methods=['GET'])
    def get_translation_status(self, task_id):
        """Get translation task status via API."""
        try:
            task = request.env['sc.translation.task'].browse(task_id)
            
            if not task.exists():
                return {'error': 'Task not found', 'code': 404}
            
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
        """Start translation task via API."""
        try:
            blog_post_ids = kwargs.get('blog_post_ids', [])
            target_language = kwargs.get('target_language')
            
            if not blog_post_ids or not target_language:
                return {'error': 'Missing required parameters', 'code': 400}
            
            task = request.env['sc.translation.task'].create({
                'name': f"API Translation to {target_language}",
                'target_language': target_language,
                'blog_post_ids': [(6, 0, blog_post_ids)]
            })
            
            task.start_translation()
            
            return {
                'status': 'success',
                'data': {
                    'task_id': task.id,
                    'message': 'Translation started successfully'
                }
            }
            
        except Exception as e:
            return {'error': str(e), 'code': 500}
```

## Error Handling & Logging

### Comprehensive Error Management
```python
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class TranslationErrorHandler:
    """Centralized error handling for translation operations."""
    
    @staticmethod
    def handle_openai_error(error, context=""):
        """Handle OpenAI-specific errors."""
        error_messages = {
            'RateLimitError': _("Rate limit exceeded. Please try again later."),
            'AuthenticationError': _("Invalid API key. Please check configuration."),
            'APIConnectionError': _("Connection failed. Please check internet connection."),
            'InvalidRequestError': _("Invalid request format."),
            'ServiceUnavailableError': _("OpenAI service is temporarily unavailable.")
        }
        
        error_type = type(error).__name__
        user_message = error_messages.get(error_type, _("An unexpected error occurred."))
        
        # Log detailed error for debugging
        _logger.error(f"OpenAI Error [{context}]: {error_type} - {str(error)}")
        
        # Return user-friendly message
        return user_message
    
    @staticmethod
    def log_translation_error(task_id, error, blog_post_id=None):
        """Log translation errors with context."""
        context = {
            'task_id': task_id,
            'blog_post_id': blog_post_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': fields.Datetime.now()
        }
        
        _logger.error(f"Translation Error: {context}")
        
        # Store in database for audit trail
        request.env['sc.translation.error.log'].sudo().create({
            'task_id': task_id,
            'blog_post_id': blog_post_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_context': json.dumps(context)
        })
```

### Health Check System
```python
def system_health_check(self):
    """Perform system health check for translation service."""
    health_status = {
        'overall': 'healthy',
        'components': {}
    }
    
    # Check OpenAI API connectivity
    try:
        self._test_openai_connection()
        health_status['components']['openai'] = 'healthy'
    except Exception as e:
        health_status['components']['openai'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'degraded'
    
    # Check queue job service
    try:
        queue_jobs = self.env['queue.job'].search([
            ('state', 'in', ['pending', 'enqueued', 'started']),
            ('channel', 'like', 'translation')
        ])
        health_status['components']['queue'] = f'healthy ({len(queue_jobs)} jobs)'
    except Exception as e:
        health_status['components']['queue'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'unhealthy'
    
    return health_status
```

## Testing Strategy

### Unit Tests
```python
from odoo.tests import tagged, TransactionCase
from unittest.mock import patch, MagicMock

@tagged('post_install', '-at_install')
class TestSCTranslationTask(TransactionCase):
    """Test suite for SC Translation Task functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create test data
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'name': 'Test Post',
            'content': '<p>This is a test blog post content.</p>',
            'blog_id': self.test_blog.id,
        })
        
        self.translation_task = self.env['sc.translation.task'].create({
            'name': 'Test Translation Task',
            'source_language': 'en',
            'target_language': 'es',
            'blog_post_ids': [(6, 0, [self.test_post.id])]
        })
    
    def test_translation_task_creation(self):
        """Test translation task creation."""
        self.assertEqual(self.translation_task.state, 'draft')
        self.assertEqual(len(self.translation_task.blog_post_ids), 1)
        self.assertEqual(self.translation_task.progress_percentage, 0.0)
    
    @patch('odoo.addons.sc_marketing_automation_tool.models.translation_task.OpenAITranslationService')
    def test_translation_process(self, mock_openai):
        """Test translation process with mocked OpenAI service."""
        # Mock OpenAI response
        mock_openai.return_value.translate_content.return_value = '<p>Este es el contenido de una publicación de blog de prueba.</p>'
        
        # Start translation
        self.translation_task.start_translation()
        
        # Verify state change
        self.assertEqual(self.translation_task.state, 'queued')
    
    def test_multi_company_security(self):
        """Test multi-company access control."""
        company_2 = self.env['res.company'].create({
            'name': 'Test Company 2',
        })
        
        # Create task in different company
        task_company_2 = self.translation_task.with_company(company_2)
        
        # Test company isolation
        self.assertNotEqual(
            self.translation_task.company_id,
            company_2
        )
```

### Integration Tests
```python
@tagged('post_install', '-at_install', 'external_api')
class TestOpenAIIntegration(TransactionCase):
    """Integration tests for OpenAI API (requires valid API key)."""
    
    def setUp(self):
        super().setUp()
        self.api_key = os.environ.get('OPENAI_API_KEY_TEST')
        if not self.api_key:
            self.skipTest("No test API key provided")
    
    def test_openai_connection(self):
        """Test real OpenAI API connection."""
        service = OpenAITranslationService(self.api_key)
        
        # Test simple translation
        result = service.translate_content(
            "<p>Hello world</p>",
            "es",
            "en"
        )
        
        self.assertIn("<p>", result)
        self.assertIn("</p>", result)
```

### Performance Tests
```python
@tagged('performance')
class TestTranslationPerformance(TransactionCase):
    """Performance tests for translation operations."""
    
    def test_bulk_translation_performance(self):
        """Test performance with multiple blog posts."""
        import time
        
        # Create multiple test posts
        posts = []
        for i in range(10):
            post = self.env['blog.post'].create({
                'name': f'Test Post {i}',
                'content': f'<p>Test content {i}</p>' * 100,  # Longer content
                'blog_id': self.test_blog.id,
            })
            posts.append(post.id)
        
        # Create bulk translation task
        task = self.env['sc.translation.task'].create({
            'name': 'Bulk Performance Test',
            'source_language': 'en',
            'target_language': 'es',
            'blog_post_ids': [(6, 0, posts)]
        })
        
        # Measure processing time
        start_time = time.time()
        # Simulate processing...
        end_time = time.time()
        
        processing_time = end_time - start_time
        self.assertLess(processing_time, 60)  # Should complete within 60 seconds
```

## Performance Optimization

### Database Optimization
```python
# Optimized queries for large datasets
def get_pending_translations(self, limit=100):
    """Get pending translations with optimized query."""
    return self.env['sc.translation.task'].search([
        ('state', '=', 'queued')
    ], limit=limit, order='create_date ASC')

# Batch processing for improved performance
def process_translations_batch(self, batch_size=10):
    """Process translations in batches to optimize memory usage."""
    tasks = self.get_pending_translations(limit=batch_size)
    
    for task in tasks:
        try:
            task._process_translation_async()
        except Exception as e:
            _logger.error(f"Batch processing error for task {task.id}: {str(e)}")
            continue
```

### Caching Strategy
```python
from functools import lru_cache

class TranslationCache:
    """Translation result caching to reduce API calls."""
    
    @lru_cache(maxsize=1000)
    def get_cached_translation(self, content_hash, target_language):
        """Get cached translation result."""
        return self.env['sc.translation.cache'].search([
            ('content_hash', '=', content_hash),
            ('target_language', '=', target_language)
        ], limit=1)
    
    def cache_translation_result(self, content, target_language, result):
        """Cache translation result for future use."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        self.env['sc.translation.cache'].create({
            'content_hash': content_hash,
            'target_language': target_language,
            'original_content': content,
            'translated_content': result,
            'cache_date': fields.Datetime.now()
        })
```

## Deployment & Maintenance

### Installation Instructions
```bash
# 1. Install Python dependencies
pip install openai-agents==0.2.9

# 2. Set environment variables
export OPENAI_API_KEY=sk-your-api-key-here
export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1

# 3. Update Odoo addon path
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --addons-path=odoo-src/addons,enterprise,themes,custom-addons

# 4. Install the module
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  -d your_database -i sc_marketing_automation_tool
```

### Configuration Steps
1. **Navigate to Settings > Marketing Automation**
2. **Enter OpenAI API Key**
3. **Configure translation preferences**
4. **Test API connection**
5. **Set up queue job channels**

### Maintenance Tasks
```bash
# Weekly maintenance script
#!/bin/bash

# Clean old translation logs
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --shell -d your_database << EOF
env['sc.translation.task'].search([
    ('create_date', '<', fields.Date.today() - relativedelta(months=3))
]).unlink()
EOF

# Optimize translation cache
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --shell -d your_database << EOF
env['sc.translation.cache'].search([
    ('cache_date', '<', fields.Date.today() - relativedelta(weeks=2))
]).unlink()
EOF
```

### Monitoring & Alerts
```python
def setup_monitoring_alerts(self):
    """Configure monitoring alerts for translation service."""
    
    # Monitor failed translations
    failed_tasks = self.env['sc.translation.task'].search_count([
        ('state', '=', 'failed'),
        ('create_date', '>=', fields.Datetime.now() - timedelta(hours=24))
    ])
    
    if failed_tasks > 5:  # Alert threshold
        self._send_admin_alert(
            f"High failure rate: {failed_tasks} failed translations in 24h"
        )
    
    # Monitor API usage
    api_calls_today = self._get_api_usage_count()
    if api_calls_today > 1000:  # Usage threshold
        self._send_admin_alert(
            f"High API usage: {api_calls_today} calls today"
        )
```

### Troubleshooting Guide
1. **Translation failures**: Check API key configuration and network connectivity
2. **Queue job issues**: Verify queue_job module installation and configuration
3. **Performance problems**: Review batch size settings and database indices
4. **Memory issues**: Implement content size limits and processing batches
5. **Rate limiting**: Adjust rate limit parameters and implement backoff strategies

---

## Support & Documentation

For additional technical support, contact:
- **Developer**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)
- **Company**: Solutto Consulting LLC
- **Documentation**: See [User Guide](../functional/guide.en.md)
- **API Reference**: [OpenAI Agents Python SDK](https://github.com/openai/openai-agents-python)
