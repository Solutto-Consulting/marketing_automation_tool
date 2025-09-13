# Technical Guide: Content Management Tool for Odoo v18.0.1.0.1

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Agent-Based Architecture](#agent-based-architecture)
3. [Module Structure](#module-structure)
4. [Data Models](#data-models)
5. [Integration Points](#integration-points)
6. [OpenAI Agents SDK Implementation](#openai-agents-sdk-implementation)
7. [API Implementation](#api-implementation)
8. [Security Framework](#security-framework)
9. [Configuration Management](#configuration-management)
10. [Multi-Agent Background Processing](#multi-agent-background-processing)
11. [Error Handling](#error-handling)
12. [Version-Specific Implementation](#version-specific-implementation)
13. [Development Guidelines](#development-guidelines)
14. [Testing Framework](#testing-framework)

---

## Architecture Overview

The Content Management Tool for Odoo v18.0.1.0.1 implements a sophisticated **multi-agent architecture** for AI-powered content strategy, representing a significant evolution from the translation-focused v18.0.1.0.0 to a comprehensive content management platform.

### System Components (v18.0.1.0.1)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface │    │  Agent Layer    │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Agent Config  │    │ • Research      │    │ • OpenAI API    │
│ • Content Ideas │◄──►│   Agent         │◄──►│ • WebSearchTool │
│ • Generation    │    │ • Generation    │    │ • Usage API     │
│   Wizards       │    │   Agent         │    │ • Models API    │
│ • Image Config  │    │ • Image Gen     │    │ • Direct Images │
│ • Usage Monitor │    │   Agent         │    │   API (gpt-i-1) │
│ • Task Mgmt     │    │ • Translation   │    └─────────────────┘
└─────────────────┘    │   Agent         │             │
         │              └─────────────────┘             │
         └───────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │                 │
                    │ • sc.content    │
                    │   .idea         │
                    │ • sc.content    │
                    │   .idea.task    │
                    │ • sc.content    │
                    │   .generation   │
                    │   .task         │
                    │ • Image Utils   │
                    │ • Static Files  │
                    │ • sc.openai     │
                    │   .usage        │
                    │   .snapshot     │
                    │ • Enhanced      │
                    │   Settings      │
                    └─────────────────┘
```

### Key Design Principles (v18.0.1.0.1)
- **Multi-Agent Architecture**: Specialized AI agents for research, generation, image creation, and translation
- **OpenAI Agents SDK Integration**: Leveraging structured AI responses and WebSearchTool
- **Direct Images API**: Native gpt-image-1 integration for advanced image generation
- **Centralized Settings Architecture**: Dedicated Marketing Automation configuration section
- **Asynchronous Multi-Agent Processing**: Independent cron jobs for each agent type
- **Static File Management**: Web-accessible image storage and URL generation
- **Structured AI Responses**: JSON-based content generation with defined schemas
- **Enhanced Error Recovery**: Agent-specific error handling and recovery mechanisms
- **Security First**: Enhanced credential storage and agent-specific access controls
- **Extensibility**: Scalable foundation for additional AI agents and automation features

---

## Agent-Based Architecture

### Agent Specialization Pattern

v18.0.1.0.1 implements a **specialized agent pattern** where each AI agent has a dedicated purpose, configuration, and processing pipeline:

```python
# Agent Types and Responsibilities
CONTENT_RESEARCH_AGENT = {
    'purpose': 'Topic discovery and content idea generation',
    'tools': ['WebSearchTool'],
    'output': 'Structured JSON list of content ideas',
    'model': 'Configurable (default: gpt-4o)',
    'cron': 'Research processor (every 5 minutes)'
}

CONTENT_GENERATION_AGENT = {
    'purpose': 'Complete blog post creation from ideas',
    'tools': ['Standard OpenAI completion'],
    'output': 'Structured blog post data (title, content, meta)',
    'model': 'Configurable (default: gpt-4o)',
    'cron': 'Generation processor (every 5 minutes)'
}

IMAGE_GENERATION_AGENT = {
    'purpose': 'AI-powered blog cover image creation',
    'tools': ['OpenAI Direct Images API'],
    'output': 'Generated images with web-accessible URLs',
    'model': 'gpt-image-1 (latest image generation model)',
    'integration': 'Embedded in content generation workflow'
}

TRANSLATION_AGENT = {
    'purpose': 'Enhanced blog post translation',
    'tools': ['OpenAI Agents SDK'],
    'output': 'Translated content with preserved structure',
    'model': 'Configurable (default: gpt-4o)',
    'cron': 'Translation processor (every 5 minutes)'
}
```

### Agent Communication Pattern

```
Research Agent Output → Content Ideas Database
         ↓
User Selection + Generation Request
         ↓
Generation Agent Input → Blog Post Creation
         ↓
Image Generation Agent → Cover Image Creation (if enabled)
         ↓
Optional Translation → Multi-language Content
```

### Configuration Isolation

Each agent maintains isolated configuration to prevent cross-agent interference:

```xml
<!-- Settings Architecture -->
<page string="Content Research Agent">
    <group name="research_config">
        <field name="sc_research_agent_model"/>
        <field name="sc_research_agent_instructions"/>
        <field name="sc_research_agent_default_query"/>
    </group>
</page>

<page string="Content Generation Agent">
    <group name="generation_config">
        <field name="sc_generation_agent_model"/>
        <field name="sc_generation_agent_instructions"/>
    </group>
</page>

<page string="Image Generation Settings">
    <group name="image_config">
        <field name="sc_enable_cover_image_generation"/>
        <field name="sc_image_size"/>
        <field name="sc_image_quality"/>
        <field name="sc_image_output_format"/>
        <field name="sc_image_background"/>
        <field name="sc_image_moderation"/>
        <field name="sc_image_partial_images"/>
    </group>
</page>
```

---

## Module Structure

### Enhanced File Organization (v18.0.1.0.1)
```
sc_marketing_automation_tool/
├── __init__.py                    # Module initialization
├── __manifest__.py                # Module manifest (v18.0.1.0.1)
├── models/
│   ├── __init__.py
│   ├── res_config_settings.py     # Enhanced OpenAI + Agent configuration
│   ├── sc_translation_task.py     # Enhanced translation task model
│   ├── sc_content_idea.py         # NEW: Content idea model
│   ├── sc_content_idea_task.py    # NEW: Research task tracking
│   ├── sc_content_generation_task.py  # NEW: Generation task tracking
│   ├── sc_openai_usage_snapshot.py    # NEW: Usage monitoring
│   ├── sc_ai_agent_config.py      # NEW: Agent configuration
│   └── blog_post.py               # Blog post extensions
├── wizard/
│   ├── __init__.py
│   ├── sc_translate_blog_post_wizard.py     # Enhanced translation wizard
│   ├── sc_generate_ideas_wizard.py         # NEW: Research wizard
│   ├── sc_generate_content_wizard.py       # NEW: Generation wizard
│   └── sc_content_preview_wizard.py        # NEW: Content preview
├── views/
│   ├── res_config_settings_views.xml       # Enhanced configuration UI
│   ├── sc_translation_task_views.xml       # Enhanced task views
│   ├── sc_content_idea_views.xml           # NEW: Content idea views
│   ├── sc_content_idea_task_views.xml      # NEW: Research task views
│   ├── sc_content_generation_task_views.xml # NEW: Generation task views
│   ├── sc_openai_usage_views.xml           # NEW: Usage monitoring views
│   ├── blog_post_views.xml                 # Enhanced blog views
│   └── menu_views.xml                      # NEW: Centralized menu structure
├── security/
│   ├── ir.model.access.csv        # Enhanced model access controls
│   └── sc_marketing_automation_tool_security.xml  # Enhanced groups and rules
├── data/
│   ├── server_actions.xml          # Enhanced server actions
│   ├── ir_cron_data.xml           # Multi-agent cron jobs
│   └── sc_ai_agent_config_data.xml # NEW: Default agent configurations
├── i18n/
│   └── es_ES.po                   # Enhanced Spanish translations
├── docs/                          # Comprehensive documentation
└── external_dependencies/
    └── requirements.txt           # OpenAI Agents SDK (>=0.2.9)
```

### Dependencies Matrix
| Dependency | Type | Purpose | Version Constraint |
|------------|------|---------|-------------------|
| base | Odoo Core | Foundation models | 18.0+ |
| website | Odoo Core | Website integration | 18.0+ |
| website_blog | Odoo Core | Blog post model | 18.0+ |
| mail | Odoo Core | Chatter integration | 18.0+ |
| openai-agents | External | OpenAI SDK | 0.2.9+ |

---

## Data Models

### sc.translation.task

**Purpose**: Tracks individual translation requests and their execution status.

```python
class SCTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'AI Translation Task'
    _inherit = ['mail.thread']  # Chatter integration
    _order = 'create_date desc'

    # Core Fields
    name = fields.Char(string='Task Name', required=True)
    blog_post_id = fields.Many2one('blog.post', required=True, ondelete='cascade')
    target_lang_id = fields.Many2one('res.lang', required=True)
    system_instructions = fields.Text(string='System Instructions')
    
    # Status Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'), 
        ('done', 'Done'),
        ('error', 'Error')
    ], default='draft', required=True, tracking=True)
    
    error_message = fields.Text(string='Error Details')
```

**Key Methods**:
- `action_reset_to_draft()`: Reset failed tasks for retry
- `_get_translation_data()`: Extract blog post content for translation
- `_update_blog_post_translations()`: Apply translated content (v18.0.1.0.0 implementation)

### blog.post (Extended)

**Purpose**: Enhanced blog post model with translation tracking capabilities.

```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    # Translation Tracking
    translation_task_ids = fields.One2many(
        'sc.translation.task', 'blog_post_id',
        string='Translation Tasks'
    )
    translation_in_progress = fields.Boolean(
        string='Translation in Progress', 
        default=False,
        help="Indicates if translation tasks are queued or running"
    )
    
    # Computed Fields
    translation_count = fields.Integer(
        string='Translation Count',
        compute='_compute_translation_count'
    )
```

### res.config.settings (Extended)

**Purpose**: Centralized OpenAI configuration management.

```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # OpenAI Configuration
    sc_openai_api_key = fields.Char(
        string='OpenAI API Key',
        config_parameter='sc_marketing_automation_tool.openai_api_key',
        password=True
    )
    sc_openai_organization_id = fields.Char(
        string='OpenAI Organization ID',
        config_parameter='sc_marketing_automation_tool.openai_organization_id'
    )
    sc_openai_model = fields.Selection(
        selection='_get_openai_models',
        string='OpenAI Model',
        config_parameter='sc_marketing_automation_tool.openai_model',
        default='gpt-4o'
    )
```

---

## Integration Points

### OpenAI Agents SDK Integration

**Version Support**: openai-agents 0.2.9+

```python
# Core Integration Pattern (v18.0.1.0.0)
import asyncio
from agents import Agent, Runner

async def perform_ai_translation(model_name, system_instructions, prompt):
    """
    Execute AI translation using OpenAI Agents SDK.
    
    Args:
        model_name (str): OpenAI model identifier
        system_instructions (str): AI behavior guidance
        prompt (str): Translation request content
        
    Returns:
        str: Translated content as JSON string
    """
    agent = Agent(
        name="Odoo Blog Translator",
        instructions=system_instructions or "Translate content accurately while preserving formatting and structure.",
        model=model_name
    )
    
    result = await Runner.run(agent, prompt)
    return result.final_output
```

### Environment Configuration

**Required Environment Variables**:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-...                    # From Odoo configuration
OPENAI_ORGANIZATION=org-...              # From Odoo configuration (optional)

# Odoo Configuration
ODOO_DATABASE=your_database_name
ODOO_CONF_FILE=/path/to/odoo.conf
```

---

## API Implementation

### Dynamic Model Selection

**Endpoint**: OpenAI v1/models API  
**Purpose**: Populate available models in configuration dropdown

```python
def _get_openai_models(self):
    """
    Fetch available OpenAI models from API.
    
    Returns:
        list: Tuples of (model_id, model_name) for Selection field
    """
    try:
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.openai_api_key'
        )
        
        if not api_key:
            return self._get_fallback_models()
            
        # API call implementation
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
        _logger.warning(f"Failed to fetch OpenAI models: {e}")
        
    return self._get_fallback_models()

def _get_fallback_models(self):
    """Fallback models when API is unavailable."""
    return [
        ('gpt-4o', 'gpt-4o'),
        ('gpt-4-turbo', 'gpt-4-turbo'),
        ('gpt-3.5-turbo', 'gpt-3.5-turbo'),
    ]
```

### Translation Data Structure

**JSON Schema for Translation Requests**:
```json
{
    "name": "Blog post title",
    "subtitle": "Blog post subtitle", 
    "content": "<p>Blog post HTML content</p>",
    "website_meta_title": "SEO title",
    "website_meta_description": "SEO description",
    "website_meta_keywords": "keyword1, keyword2"
}
```

### Image Generation API Implementation

#### OpenAI Direct Images API Integration

The module implements **gpt-image-1** model integration using OpenAI's Direct Images API (not the Responses API). This provides access to the latest image generation capabilities.

**API Endpoint**: `https://api.openai.com/v1/images/generations`  
**Model**: `gpt-image-1` (latest image generation model)  
**Implementation**: `utils/openai_responses_image_utils.py`

#### Core Image Generation Class

```python
class OpenAIDirectImagesGenerator:
    """
    Direct Images API implementation for gpt-image-1 model.
    
    This implementation uses client.images.generate() directly
    rather than the Responses API for maximum compatibility.
    """
    
    def __init__(self, api_key, organization_id=None):
        """Initialize Direct Images API client."""
        self.client = openai.OpenAI(
            api_key=api_key,
            organization=organization_id
        )
    
    def generate_image(self, prompt, **kwargs):
        """
        Generate image using gpt-image-1 model.
        
        Args:
            prompt (str): Image description prompt
            **kwargs: gpt-image-1 specific parameters
            
        Returns:
            tuple: (image_data, web_url, file_path)
        """
        # Parameter mapping for gpt-image-1
        params = self._get_image_generation_params(kwargs)
        
        try:
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                **params
            )
            
            # Process response and save to static directory
            return self._process_image_response(response, prompt)
            
        except Exception as e:
            _logger.error(f"Image generation failed: {e}")
            raise
```

#### Parameter Mapping and Validation

```python
def _get_image_generation_params(self, config):
    """
    Map configuration to gpt-image-1 API parameters.
    
    Args:
        config (dict): User configuration from settings
        
    Returns:
        dict: API-compatible parameters
    """
    # Size parameter mapping
    size_mapping = {
        '1024x1024': '1024x1024',
        '1536x1024': '1536x1024', 
        '1024x1536': '1024x1536',
        '1792x1024': '1792x1024',  # gpt-image-1 specific
    }
    
    # Quality parameter mapping (gpt-image-1 specific)
    quality_mapping = {
        'auto': 'auto',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'standard': 'standard'  # fallback for compatibility
    }
    
    params = {
        'size': size_mapping.get(config.get('size', '1024x1024'), '1024x1024'),
        'quality': quality_mapping.get(config.get('quality', 'auto'), 'auto'),
        'output_format': config.get('output_format', 'png'),
        'background': config.get('background', 'auto'),
        'moderation': config.get('moderation', 'auto'),
    }
    
    # Handle partial_images parameter (0-3)
    partial_images = config.get('partial_images', 0)
    if 0 <= partial_images <= 3:
        params['partial_images'] = partial_images
        
    return params
```

#### Static File Management

The image generation system implements proper static file handling for web accessibility:

```python
def _save_image_to_disk(self, image_data, prompt, output_format):
    """
    Save generated image to module static directory.
    
    Args:
        image_data (bytes): Raw image data
        prompt (str): Generation prompt for filename
        output_format (str): Image format (png, jpeg, webp)
        
    Returns:
        tuple: (local_path, web_url)
    """
    # Create static directory structure
    static_dir = os.path.join(
        get_module_path('sc_marketing_automation_tool'),
        'static', 'src', 'img', 'generated'
    )
    os.makedirs(static_dir, exist_ok=True)
    
    # Generate web-accessible filename
    safe_prompt = self._sanitize_filename(prompt)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"blog_cover_{safe_prompt}_{timestamp}.{output_format}"
    
    # Save file with proper permissions
    file_path = os.path.join(static_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(image_data)
    
    # Generate web URL for Odoo static file serving
    web_url = f"/sc_marketing_automation_tool/static/src/img/generated/{filename}"
    
    return file_path, web_url
```

#### Integration with Content Generation

```python
def _generate_and_save_cover_image(self):
    """
    Generate cover image as part of content generation workflow.
    
    Called from sc_content_generation_task model when
    generate_cover_image is enabled.
    """
    if not self.generate_cover_image:
        return
        
    try:
        # Extract configuration from settings
        config_settings = self.env['res.config.settings'].create({})
        image_config = {
            'size': config_settings.sc_image_size,
            'quality': config_settings.sc_image_quality,
            'output_format': config_settings.sc_image_output_format,
            'background': config_settings.sc_image_background,
            'moderation': config_settings.sc_image_moderation,
            'partial_images': config_settings.sc_image_partial_images,
        }
        
        # Generate descriptive prompt from blog content
        image_prompt = self._create_image_prompt()
        
        # Use Direct Images API utility
        generator = create_responses_image_generator()
        image_data, web_url, file_path = generator.generate_image(
            image_prompt, **image_config
        )
        
        # Update blog post with generated image
        if self.generated_blog_post_id:
            self.generated_blog_post_id.cover_properties = json.dumps({
                'background-image': f'url({web_url})',
                'resize_class': 'o_record_has_cover'
            })
            
        # Store generation metadata
        self.write({
            'image_generation_status': 'completed',
            'generated_image_path': web_url,
            'image_generation_prompt': image_prompt,
        })
        
        _logger.info(f"Successfully generated cover image using gpt-image-1")
        
    except Exception as e:
        self.write({
            'image_generation_status': 'failed',
            'image_generation_error': str(e)
        })
        _logger.error(f"Image generation failed: {e}")
```

#### Error Handling and Recovery

```python
class ImageGenerationError(Exception):
    """Custom exception for image generation failures."""
    pass

def handle_image_generation_errors(func):
    """Decorator for image generation error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except openai.RateLimitError as e:
            raise ImageGenerationError(f"API rate limit exceeded: {e}")
        except openai.InvalidRequestError as e:
            raise ImageGenerationError(f"Invalid request parameters: {e}")
        except openai.AuthenticationError as e:
            raise ImageGenerationError(f"Authentication failed: {e}")
        except Exception as e:
            raise ImageGenerationError(f"Unexpected error: {e}")
    return wrapper
```

#### Usage Tracking Integration

Image generation usage is tracked separately from text-based operations:

```python
def _track_image_generation_usage(self, response):
    """
    Track image generation usage for cost monitoring.
    
    Note: Image generation costs are typically per-image
    rather than per-token like text operations.
    """
    usage_data = {
        'operation_type': 'image_generation',
        'model': 'gpt-image-1',
        'images_generated': 1,
        'estimated_cost': self._calculate_image_cost(response),
        'timestamp': fields.Datetime.now(),
    }
    
    # Integrate with existing usage monitoring
    self.env['sc.openai.usage.snapshot']._record_usage(usage_data)
```

---

## Security Framework

### Access Control Groups

```xml
<!-- security/security.xml -->
<record id="group_marketing_manager" model="res.groups">
    <field name="name">Marketing Manager</field>
    <field name="category_id" ref="base.module_category_marketing"/>
</record>

<record id="group_marketing_user" model="res.groups">
    <field name="name">Marketing User</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('group_marketing_manager'))]"/>
</record>
```

### Model Access Control

```csv
# security/ir.model.access.csv
id,name,model_id/id,group_id/id,perm_read,perm_write,perm_create,perm_unlink
access_sc_translation_task_manager,sc.translation.task.manager,model_sc_translation_task,group_marketing_manager,1,1,1,1
access_sc_translation_task_user,sc.translation.task.user,model_sc_translation_task,group_marketing_user,1,0,1,0
```

### Record Rules

```xml
<!-- Multi-company security (if applicable) -->
<record id="rule_translation_task_company" model="ir.rule">
    <field name="name">Translation Task Company Rule</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```

---

## Configuration Management

### Settings View Implementation

**Reference Pattern**: Based on core Odoo settings inheritance

```xml
<!-- views/res_config_settings_views.xml -->
<record id="res_config_settings_view_form_inherit_sc" model="ir.ui.view">
    <field name="name">res.config.settings.form.inherit.sc</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base_setup.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//setting[@id='partner_autocomplete']" position="after">
            <setting id="sc_ai_marketing_tools" string="AI Marketing Tools">
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

**Core Reference Used**:
- **File**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anchor**: `//setting[@id='partner_autocomplete']` (stable selector)
- **Position**: `after` (safe insertion point)

---

## Background Processing

### Cron Job Configuration

```xml
<!-- data/ir_cron.xml -->
<record id="ir_cron_process_translation_tasks" model="ir.cron">
    <field name="name">Process Translation Tasks</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="state">code</field>
    <field name="code">model._cron_process_translation_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

### Processing Logic (v18.0.1.0.0)

```python
@api.model
def _cron_process_translation_tasks(self):
    """
    Background processor for translation tasks.
    Processes up to 10 draft tasks per execution.
    """
    tasks = self.search([('state', '=', 'draft')], limit=10)
    
    for task in tasks:
        try:
            # Update status to prevent duplicate processing
            task.state = 'in_progress'
            self.env.cr.commit()
            
            # Get configuration
            config = self._get_openai_config()
            if not config:
                task._handle_error("OpenAI configuration not found")
                continue
                
            # Prepare translation data
            translation_data = task._get_translation_data()
            prompt = task._build_translation_prompt(translation_data)
            
            # Execute AI translation
            translated_content = asyncio.run(
                perform_ai_translation(
                    config['model'],
                    task.system_instructions,
                    prompt
                )
            )
            
            # Apply translation
            task._update_blog_post_translations(translated_content)
            task.state = 'done'
            
        except Exception as e:
            task._handle_error(str(e))
            
        finally:
            self.env.cr.commit()
```

---

## Error Handling

### Error Categories (v18.0.1.0.0)

| Error Type | Handling Strategy | Recovery Method |
|------------|------------------|-----------------|
| API Configuration | Immediate failure | Fix configuration, reset task |
| API Rate Limits | Graceful delay | Wait and retry manually |
| Content Too Large | Size validation | Reduce content, retry |
| Network Timeout | Exception handling | Check connectivity, retry |
| JSON Parse Error | Format validation | Review AI output, retry |

### Error Recovery Pattern

```python
def _handle_error(self, error_message):
    """
    Standard error handling for translation tasks.
    
    Args:
        error_message (str): Description of the error
    """
    self.write({
        'state': 'error',
        'error_message': error_message
    })
    
    # Reset blog post status
    self.blog_post_id.translation_in_progress = False
    
    # Log error for debugging
    _logger.error(
        f"Translation task {self.id} failed: {error_message}"
    )
```

---

## Version-Specific Implementation

### Odoo 18.0 Standards Compliance

**List Views**:
```xml
<!-- ✅ CORRECT: Use <list> for Odoo 18.0 -->
<field name="arch" type="xml">
    <list string="Translation Tasks">
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

**Conditional Attributes**:
```xml
<!-- ✅ CORRECT: Modern conditional syntax -->
<button name="action_reset_to_draft" 
        string="Reset to Draft"
        type="object"
        invisible="state != 'error'"
        class="btn-secondary"/>
```

**Kanban Views**:
```xml
<!-- ✅ MANDATORY: default_group_by for Kanban -->
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

### Chatter Integration

```xml
<!-- Blog Post form with chatter -->
<form string="Blog Post">
    <sheet>
        <!-- Form content -->
    </sheet>
    <!-- ✅ REQUIRED: Chatter at end of form when using mail.thread -->
    <chatter/>
</form>
```

---

## Development Guidelines

### Code Standards

1. **Python Standards**:
   - Follow PEP 8 style guidelines
   - Use type hints where applicable
   - Implement proper exception handling
   - Add comprehensive docstrings

2. **XML Standards**:
   - Use modern Odoo 18.0 syntax
   - Implement stable xpath selectors
   - Follow consistent naming conventions
   - Include proper field labels and help text

3. **JavaScript Standards**:
   - Not applicable for v18.0.1.0.0 (server-side only)

### Testing Guidelines (v18.0.1.0.0)

**Note**: Unit testing implementation is planned for future versions.

```python
# Future testing structure
class TestTranslationTask(common.TransactionCase):
    def setUp(self):
        super(TestTranslationTask, self).setUp()
        self.translation_task = self.env['sc.translation.task']
        
    def test_task_creation(self):
        """Test translation task creation logic."""
        # Implementation pending
        pass
        
    def test_cron_processing(self):
        """Test background processing with mocked API calls."""
        # Implementation pending
        pass
```

---

## Testing Framework

### Manual Testing Checklist (v18.0.1.0.0)

#### Configuration Testing
- [ ] OpenAI API key validation
- [ ] Dynamic model loading
- [ ] Fallback model selection
- [ ] Organization ID handling

#### Translation Workflow Testing  
- [ ] Blog post selection
- [ ] Wizard functionality
- [ ] Task creation
- [ ] Background processing
- [ ] Error handling
- [ ] Task reset functionality

#### UI/UX Testing
- [ ] Settings page integration
- [ ] Task list views
- [ ] Kanban view grouping
- [ ] Form view layout
- [ ] Chatter integration

#### Security Testing
- [ ] Access control enforcement
- [ ] Password field masking
- [ ] Multi-company isolation
- [ ] Permission boundaries

---

## External References

### Core Implementation References
- **Base Settings Pattern**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anchor Used**: `//setting[@id='partner_autocomplete']` (stable selector)
- **Mail Integration**: Standard Odoo `mail.thread` and `mail.activity.mixin` patterns

### Official Documentation
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **SDK Documentation**: https://github.com/openai/openai-agents-python/blob/main/docs/quickstart.md
- **API Reference**: https://platform.openai.com/docs/api-reference
- **Odoo 18.0 Developer Guide**: https://www.odoo.com/documentation/18.0/developer/

### Version Dependencies
- **openai-agents**: 0.2.9+ (pinned in requirements.txt)
- **Python**: 3.9+ (required by openai-agents)
- **Odoo**: 18.0 Community or Enterprise

---

*Technical Documentation Version: 18.0.1.0.0 | Last Updated: September 2025*
