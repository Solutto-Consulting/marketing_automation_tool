# Implementation Plan: SC Marketing Automation Tool

## Plan Metadata
- **Module Name**: sc_marketing_automation_tool
- **Spec Path**: /home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool/docs/Technical-specs-v2025-sep-04.md
- **Target Path**: /home/gilsonrincon/development/odoo18/custom-addons/sc_marketing_automation_tool
- **Last Updated**: 2025-09-04T19:30:00Z
- **Odoo Version**: 18.0
- **Planning Mode**: Odoo – Planner (Read-Only)

---

## 1. Scope & Goals

### Business Objective
Create an AI-powered content management tool that automates blog post translation using OpenAI's Agent SDK, replacing manual Odoo translation workflows with asynchronous background processing.

### Success Criteria
- ✅ Administrators can select multiple blog posts for translation in one action
- ✅ Translation requests are processed asynchronously without blocking the UI
- ✅ Full status tracking and error management for all translation tasks
- ✅ Support for multiple target languages with custom AI instructions
- ✅ Complete audit trail of translation attempts per blog post
- ✅ Integration with OpenAI Agent SDK (openai-agents library)

### Out of Scope
- Translation of other content types (only blog.post in v1)
- Real-time translation (asynchronous only)
- Custom AI models (OpenAI only)
- Multi-company translation workflows (single company focus)

---

## 2. Domain & Data Model Plan

### 2.1 New Model: sc.translation.task
**Purpose**: Track individual translation requests with full lifecycle management

**Fields**:
```python
class ScTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _description = 'AI Translation Task'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Core fields
    name = fields.Char(string='Task Name', required=True, tracking=True)
    blog_post_id = fields.Many2one('blog.post', string='Blog Post', required=True, ondelete='cascade')
    target_lang_id = fields.Many2one('res.lang', string='Target Language', required=True)
    system_instructions = fields.Text(string='AI Instructions', help="Custom instructions for AI translation")
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='draft', required=True, tracking=True)
    
    error_message = fields.Text(string='Error Details', readonly=True)
    
    # Translation data
    original_content = fields.Json(string='Original Content', readonly=True)
    translated_content = fields.Json(string='Translated Content', readonly=True)
    
    # Audit fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    processed_date = fields.Datetime(string='Processed Date', readonly=True)
    processing_duration = fields.Float(string='Processing Time (seconds)', readonly=True)
```

**Computed Fields**:
```python
@api.depends('blog_post_id.name', 'target_lang_id.name')
def _compute_name(self):
    for record in self:
        if record.blog_post_id and record.target_lang_id:
            record.name = f"Translate '{record.blog_post_id.name}' to {record.target_lang_id.name}"

@api.depends('state', 'error_message')
def _compute_status_display(self):
    # For badge widget display with appropriate colors
```

**Constraints**:
```python
@api.constrains('blog_post_id', 'target_lang_id')
def _check_duplicate_translation(self):
    # Prevent duplicate active translations for same post+language
    
@api.constrains('target_lang_id')
def _check_published_language(self):
    # Ensure target language is website published
```

### 2.2 Inherited Model: blog.post
**Purpose**: Add translation tracking capabilities to blog posts

**Added Fields**:
```python
class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    translation_task_ids = fields.One2many('sc.translation.task', 'blog_post_id', string='Translation Tasks')
    translation_in_progress = fields.Boolean(string='Translation in Progress', default=False, compute='_compute_translation_status', store=True)
    last_translation_date = fields.Datetime(string='Last Translation', compute='_compute_last_translation')
    translation_task_count = fields.Integer(string='Translation Tasks', compute='_compute_translation_count')
```

**Methods**:
```python
@api.depends('translation_task_ids.state')
def _compute_translation_status(self):
    # Check if any task is in draft or in_progress state

def action_view_translation_tasks(self):
    # Smart button action to view related translation tasks
    
def reset_translation_status(self):
    # Reset translation_in_progress flag (for error recovery)
```

### 2.3 Configuration Model: res.config.settings
**Purpose**: OpenAI API configuration and model selection

**Added Fields**:
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    sc_openai_api_key = fields.Char(string='OpenAI API Key', password=True, config_parameter='sc_marketing_automation.openai_api_key')
    sc_openai_organization_id = fields.Char(string='OpenAI Organization ID', config_parameter='sc_marketing_automation.openai_org_id')
    sc_openai_model = fields.Selection(selection='_get_openai_models', string='OpenAI Model', default='gpt-4o', config_parameter='sc_marketing_automation.openai_model')
    
    def _get_openai_models(self):
        # Dynamic model list from OpenAI API with fallback
        return [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo')
        ]
```

### 2.4 Wizard Model: sc.translate.blog.post.wizard
**Purpose**: User interface for initiating translations

**Fields**:
```python
class ScTranslateBlogPostWizard(models.TransientModel):
    _name = 'sc.translate.blog.post.wizard'
    _description = 'Blog Post Translation Wizard'
    
    target_lang_id = fields.Many2one('res.lang', string='Target Language', required=True, domain=[('website_published', '=', True)])
    system_instructions = fields.Text(string='AI Instructions', placeholder="Optional: Provide specific tone, style, or formatting instructions...")
    blog_post_ids = fields.Many2many('blog.post', string='Selected Blog Posts')
    
    def action_translate(self):
        # Main wizard action - create translation tasks
```

---

## 3. Security Plan

### 3.1 Access Groups
```csv
# security/groups.xml
<record id="group_marketing_automation_user" model="res.groups">
    <field name="name">Marketing Automation: User</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="users" eval="[(4, ref('base.user_admin'))]"/>
</record>

<record id="group_marketing_automation_manager" model="res.groups">
    <field name="name">Marketing Automation: Manager</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('group_marketing_automation_user'))]"/>
    <field name="users" eval="[(4, ref('base.user_admin'))]"/>
</record>
```

### 3.2 Access Control Lists (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sc_translation_task_user,sc.translation.task.user,model_sc_translation_task,group_marketing_automation_user,1,0,0,0
access_sc_translation_task_manager,sc.translation.task.manager,model_sc_translation_task,group_marketing_automation_manager,1,1,1,1
access_sc_translate_blog_post_wizard_user,sc.translate.blog.post.wizard.user,model_sc_translate_blog_post_wizard,group_marketing_automation_user,1,1,1,1
```

### 3.3 Record Rules
```xml
<!-- Company-specific access rule -->
<record id="translation_task_company_rule" model="ir.rule">
    <field name="name">Translation Task: Multi-Company</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
</record>

<!-- Manager can see all tasks, users only their own -->
<record id="translation_task_user_rule" model="ir.rule">
    <field name="name">Translation Task: User Access</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="groups" eval="[(4, ref('group_marketing_automation_user'))]"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
</record>
```

### 3.4 Field-Level Security
- **API Key**: Password field, only accessible to system administrators
- **Error Messages**: Read-only, manager-level access required
- **Translation Content**: Protected from unauthorized modification

---

## 4. UI & Views Plan (Odoo 18.0)

### 4.1 Menu Structure
```xml
<menuitem id="menu_marketing_automation_root" name="Marketing Automation" sequence="85"/>
    <menuitem id="menu_content_translation" name="Content Translation" parent="menu_marketing_automation_root" sequence="10"/>
        <menuitem id="menu_translation_tasks" name="Translation Tasks" parent="menu_content_translation" sequence="10" action="action_sc_translation_task"/>
```

### 4.2 Translation Task Views

**List View (Odoo 18.0 compliant)**:
```xml
<record id="view_sc_translation_task_list" model="ir.ui.view">
    <field name="name">sc.translation.task.list</field>
    <field name="model">sc.translation.task</field>
    <field name="arch" type="xml">
        <list string="Translation Tasks" default_order="create_date desc">
            <field name="name"/>
            <field name="blog_post_id"/>
            <field name="target_lang_id"/>
            <field name="state" widget="badge" 
                   decoration-info="state in ('draft', 'in_progress')"
                   decoration-success="state == 'done'"
                   decoration-danger="state == 'error'"/>
            <field name="create_date"/>
            <field name="processed_date"/>
            <field name="company_id" column_invisible="not context.get('show_company')"/>
        </list>
    </field>
</record>
```

**Form View with Chatter**:
```xml
<record id="view_sc_translation_task_form" model="ir.ui.view">
    <field name="name">sc.translation.task.form</field>
    <field name="model">sc.translation.task</field>
    <field name="arch" type="xml">
        <form string="Translation Task">
            <header>
                <button name="action_reset_to_draft" type="object" string="Reset to Draft" 
                        invisible="state != 'error'" class="btn-secondary"/>
                <field name="state" widget="statusbar" statusbar_visible="draft,in_progress,done"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1><field name="name" readonly="1"/></h1>
                </div>
                <group>
                    <group>
                        <field name="blog_post_id" readonly="state != 'draft'"/>
                        <field name="target_lang_id" readonly="state != 'draft'"/>
                        <field name="company_id" groups="base.group_multi_company"/>
                    </group>
                    <group>
                        <field name="create_date"/>
                        <field name="processed_date" readonly="1"/>
                        <field name="processing_duration" readonly="1"/>
                    </group>
                </group>
                <notebook>
                    <page string="Instructions" name="instructions">
                        <field name="system_instructions" readonly="state != 'draft'"/>
                    </page>
                    <page string="Error Details" name="error_details" invisible="state != 'error'">
                        <field name="error_message" readonly="1"/>
                    </page>
                    <page string="Content" name="content" invisible="state in ('draft', 'in_progress')">
                        <group>
                            <group string="Original Content">
                                <field name="original_content" widget="json" readonly="1"/>
                            </group>
                            <group string="Translated Content">
                                <field name="translated_content" widget="json" readonly="1"/>
                            </group>
                        </group>
                    </page>
                </notebook>
            </sheet>
            <chatter/>
        </form>
    </field>
</record>
```

**Kanban View with default_group_by**:
```xml
<record id="view_sc_translation_task_kanban" model="ir.ui.view">
    <field name="name">sc.translation.task.kanban</field>
    <field name="model">sc.translation.task</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" class="o_kanban_small_column">
            <field name="name"/>
            <field name="blog_post_id"/>
            <field name="target_lang_id"/>
            <field name="state"/>
            <field name="create_date"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <div class="oe_kanban_content">
                            <div class="o_kanban_record_title">
                                <field name="name"/>
                            </div>
                            <div class="o_kanban_record_body">
                                <field name="blog_post_id"/>
                                <br/>
                                <i class="fa fa-language"/> <field name="target_lang_id"/>
                            </div>
                            <div class="o_kanban_record_bottom">
                                <div class="oe_kanban_bottom_left">
                                    <field name="create_date" widget="date"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### 4.3 Blog Post Enhancement
**Form View Addition**:
```xml
<record id="view_blog_post_form_translation" model="ir.ui.view">
    <field name="name">blog.post.form.translation</field>
    <field name="model">blog.post</field>
    <field name="inherit_id" ref="website_blog.view_blog_post_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[hasclass('oe_button_box')]" position="inside">
            <button name="action_view_translation_tasks" type="object" class="oe_stat_button" icon="fa-language" invisible="translation_task_count == 0">
                <field name="translation_task_count" widget="statinfo" string="Translations"/>
            </button>
        </xpath>
        <xpath expr="//notebook" position="inside">
            <page string="Translation History" name="translation_history">
                <field name="translation_task_ids" readonly="1">
                    <list string="Translation Tasks">
                        <field name="target_lang_id"/>
                        <field name="state" widget="badge"/>
                        <field name="create_date"/>
                        <field name="processed_date"/>
                    </list>
                </field>
            </page>
        </xpath>
    </field>
</record>
```

### 4.4 Server Action
```xml
<record id="action_translate_blog_posts" model="ir.actions.server">
    <field name="name">Translate with AI</field>
    <field name="model_id" ref="website_blog.model_blog_post"/>
    <field name="binding_model_id" ref="website_blog.model_blog_post"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">
        action = records.action_open_translation_wizard()
    </field>
</record>
```

### 4.5 Wizard Views
```xml
<record id="view_sc_translate_blog_post_wizard_form" model="ir.ui.view">
    <field name="name">sc.translate.blog.post.wizard.form</field>
    <field name="model">sc.translate.blog.post.wizard</field>
    <field name="arch" type="xml">
        <form string="Translate Blog Posts">
            <group>
                <field name="target_lang_id" required="1"/>
                <field name="system_instructions" placeholder="Optional: Specify tone, style, or special instructions for the AI translator..."/>
                <field name="blog_post_ids" invisible="1"/>
            </group>
            <footer>
                <button name="action_translate" type="object" string="Translate" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

### 4.6 Settings View
```xml
<record id="view_general_configuration_translation" model="ir.ui.view">
    <field name="name">res.config.settings.view.form.inherit.translation</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[hasclass('settings')]" position="inside">
            <div class="app_settings_block" data-string="AI Marketing Tools" string="AI Marketing Tools" data-key="sc_marketing_automation">
                <h2>OpenAI Configuration</h2>
                <div class="row mt16 o_settings_container">
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sc_openai_api_key"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sc_openai_api_key"/>
                            <div class="text-muted">Your OpenAI API key for AI translation services</div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sc_openai_organization_id"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sc_openai_organization_id"/>
                            <div class="text-muted">Optional: Your OpenAI Organization ID</div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6 o_setting_box">
                        <div class="o_setting_left_pane">
                            <field name="sc_openai_model"/>
                        </div>
                        <div class="o_setting_right_pane">
                            <label for="sc_openai_model"/>
                            <div class="text-muted">OpenAI model to use for translations</div>
                        </div>
                    </div>
                </div>
            </div>
        </xpath>
    </field>
</record>
```

---

## 5. Integration & Services

### 5.1 OpenAI Agent SDK Integration

**Environment Setup**:
- **Library**: `openai-agents` (pip install openai-agents)
- **Version**: Latest stable version (to be pinned in requirements.txt)
- **Authentication**: API key from environment variables or Odoo settings
- **Rate Limits**: Implement exponential backoff (2^retry_count seconds, max 60s)
- **Timeouts**: 120 seconds per translation request
- **Error Handling**: Comprehensive error taxonomy with user-friendly messages

**Core Integration Service**:
```python
# utils/openai_service.py
import asyncio
import os
import json
from agents import Agent, Runner
from odoo import api, models, fields, _

class OpenAITranslationService:
    """Service class for OpenAI Agent SDK integration"""
    
    def __init__(self, api_key, organization_id=None, model='gpt-4o'):
        # Set environment variables for OpenAI SDK
        os.environ['OPENAI_API_KEY'] = api_key
        if organization_id:
            os.environ['OPENAI_ORG_ID'] = organization_id
        self.model = model
    
    async def translate_blog_content(self, content_json, source_lang, target_lang, system_instructions=""):
        """
        Translate blog content using OpenAI Agent SDK
        
        Args:
            content_json (dict): Blog post content fields
            source_lang (str): Source language code
            target_lang (str): Target language code  
            system_instructions (str): Custom AI instructions
            
        Returns:
            dict: Translated content with same structure
            
        Raises:
            OpenAIError: For API-related errors
            ValidationError: For content validation errors
        """
        
        # Prepare system instructions
        base_instructions = f"""
        You are a professional translator specializing in blog content translation.
        Translate the provided JSON content from {source_lang} to {target_lang}.
        
        Rules:
        1. Maintain the exact JSON structure
        2. Translate only the VALUES, never the KEYS
        3. Preserve HTML tags and formatting
        4. Adapt cultural references appropriately
        5. Maintain the original tone and style unless specified otherwise
        
        {system_instructions}
        """
        
        # Build translation prompt
        prompt = f"""
        Translate the values in the following JSON object from {source_lang} to {target_lang}.
        Respond ONLY with the translated JSON object, maintaining the exact same key structure.
        
        JSON to translate:
        {json.dumps(content_json, indent=2)}
        """
        
        # Create agent and execute translation
        agent = Agent(
            name="Odoo Blog Translator",
            instructions=base_instructions,
            model=self.model
        )
        
        result = await Runner.run(agent, prompt)
        
        # Parse and validate response
        try:
            translated_content = json.loads(result.final_output)
            return translated_content
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
```

**Async Cron Integration**:
```python
# models/translation_task.py (cron method)
def _process_translation_tasks(self):
    """Cron method to process pending translation tasks"""
    
    tasks = self.search([('state', '=', 'draft')], limit=10)
    
    for task in tasks:
        try:
            # Update to in_progress with commit
            task.write({'state': 'in_progress'})
            self.env.cr.commit()
            
            # Execute translation
            result = self._execute_translation_async(task)
            
            # Update with results
            task.write({
                'state': 'done',
                'translated_content': result,
                'processed_date': fields.Datetime.now()
            })
            
        except Exception as e:
            task.write({
                'state': 'error',
                'error_message': str(e)
            })
            
        # Reset blog post flag if no more pending tasks
        if not task.blog_post_id.translation_task_ids.filtered(lambda t: t.state in ('draft', 'in_progress')):
            task.blog_post_id.translation_in_progress = False
    
def _execute_translation_async(self, task):
    """Execute async translation in sync context"""
    
    # Get OpenAI configuration
    config = self.env['ir.config_parameter'].sudo()
    api_key = config.get_param('sc_marketing_automation.openai_api_key')
    org_id = config.get_param('sc_marketing_automation.openai_org_id')
    model = config.get_param('sc_marketing_automation.openai_model', 'gpt-4o')
    
    if not api_key:
        raise ValueError(_("OpenAI API key not configured"))
    
    # Prepare content for translation
    post = task.blog_post_id
    content = {
        'name': post.name,
        'subtitle': post.subtitle or '',
        'content': post.content or '',
        'website_meta_title': post.website_meta_title or '',
        'website_meta_description': post.website_meta_description or '',
        'website_meta_keywords': post.website_meta_keywords or ''
    }
    
    # Store original content
    task.original_content = content
    
    # Initialize service and run translation
    service = OpenAITranslationService(api_key, org_id, model)
    
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            service.translate_blog_content(
                content, 
                'English',  # Assuming source is English
                task.target_lang_id.name,
                task.system_instructions
            )
        )
        return result
    finally:
        loop.close()
```

### 5.2 Cron Job Configuration
```xml
<record id="cron_process_translation_tasks" model="ir.cron">
    <field name="name">Process Translation Tasks</field>
    <field name="model_id" ref="model_sc_translation_task"/>
    <field name="state">code</field>
    <field name="code">model._process_translation_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

### 5.3 External API Requirements

**OpenAI Agent SDK**:
- **Base URL**: Handled by SDK (https://api.openai.com/v1/)
- **Authentication**: Bearer token (API key)
- **Rate Limits**: 
  - GPT-4: 500 requests/minute, 30,000 tokens/minute
  - GPT-3.5: 3,000 requests/minute, 160,000 tokens/minute
- **Backoff Strategy**: Exponential backoff with jitter
- **Timeout**: 120 seconds per request
- **Retry Logic**: 3 attempts with exponential backoff

**Environment Variables**:
- `OPENAI_API_KEY`: Stored in Odoo config parameters
- `OPENAI_ORG_ID`: Optional, stored in Odoo config parameters

**Error Taxonomy**:
- **401 Unauthorized**: Invalid API key
- **429 Rate Limited**: Implement backoff and retry
- **500 Server Error**: Temporary failure, retry
- **Content Policy Violation**: Log and mark as error
- **Token Limit Exceeded**: Split content or use smaller model

---

## 6. Files & Scaffolding Map

```
sc_marketing_automation_tool/
├── __init__.py                          # Import models, wizards, utils
├── __manifest__.py                      # Module manifest with dependencies
├── models/
│   ├── __init__.py                      # Import all models
│   ├── res_config_settings.py          # OpenAI configuration
│   ├── sc_translation_task.py          # Main translation task model
│   ├── blog_post.py                     # blog.post inheritance
│   └── res_lang.py                      # Language model enhancements (if needed)
├── wizard/
│   ├── __init__.py                      # Import wizards
│   └── sc_translate_blog_post_wizard.py # Translation wizard
├── views/
│   ├── sc_translation_task_views.xml   # Task list, form, kanban views
│   ├── blog_post_views.xml             # Blog post form inheritance
│   ├── res_config_settings_views.xml   # Settings page configuration
│   └── sc_translate_blog_post_wizard_views.xml # Wizard views
├── data/
│   ├── ir_cron_data.xml                # Cron job configuration
│   ├── ir_actions_server_data.xml      # Server actions
│   └── menu_data.xml                   # Menu structure
├── security/
│   ├── ir.model.access.csv             # Access control lists
│   ├── groups.xml                      # Security groups
│   └── record_rules.xml                # Record-level security
├── utils/
│   ├── __init__.py                     # Import utility modules
│   ├── openai_service.py               # OpenAI Agent SDK integration
│   └── translation_helpers.py         # Helper functions
├── static/
│   └── description/
│       ├── icon.png                    # Module icon
│       └── index.html                  # Module description
├── i18n/
│   └── es_ES.po                        # Spanish translations
├── docs/
│   ├── INDEX.md                        # Documentation index
│   ├── README.md                       # Module overview and quick start
│   ├── technical/
│   │   ├── api-reference.md            # API documentation
│   │   ├── architecture.md             # System architecture
│   │   ├── development-guide.md        # Developer guidelines
│   │   ├── database-schema.md          # Database documentation
│   │   ├── integration-guide.md        # OpenAI integration guide
│   │   └── troubleshooting.md          # Technical troubleshooting
│   ├── functional/
│   │   ├── user-guide.md               # Complete user manual
│   │   ├── business-processes.md       # Business workflow documentation
│   │   ├── configuration-guide.md      # System configuration
│   │   ├── roles-permissions.md        # User roles and access control
│   │   ├── reports-guide.md            # Reports and analytics
│   │   └── faq.md                      # Frequently asked questions
│   ├── plan/
│   │   └── PLAN.md                     # This implementation plan
│   └── assets/
│       └── images/                     # Screenshots and diagrams
├── tests/
│   ├── __init__.py                     # Import test modules
│   ├── test_translation_task.py        # Unit tests for translation tasks
│   ├── test_blog_post_inheritance.py   # Tests for blog post enhancements
│   ├── test_wizard.py                  # Wizard functionality tests
│   ├── test_openai_integration.py      # OpenAI service tests (with mocking)
│   └── test_security.py               # Security and access control tests
└── requirements.txt                    # Python dependencies (openai-agents)
```

---

## 7. Testing Plan

### 7.1 Unit Tests

**Translation Task Model Tests** (`test_translation_task.py`):
```python
@tagged('post_install', '-at_install')
class TestScTranslationTask(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.blog_post = self.env['blog.post'].create({
            'name': 'Test Blog Post',
            'content': '<p>Test content</p>'
        })
        self.lang_es = self.env['res.lang'].create({
            'name': 'Spanish',
            'code': 'es_ES',
            'website_published': True
        })
    
    def test_translation_task_creation(self):
        """Test basic translation task creation"""
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.blog_post.id,
            'target_lang_id': self.lang_es.id,
            'system_instructions': 'Test instructions'
        })
        self.assertEqual(task.state, 'draft')
        self.assertTrue(task.name)  # Should be computed
        
    def test_duplicate_translation_constraint(self):
        """Test constraint preventing duplicate translations"""
        # Create first task
        self.env['sc.translation.task'].create({
            'blog_post_id': self.blog_post.id,
            'target_lang_id': self.lang_es.id
        })
        
        # Attempt to create duplicate should raise error
        with self.assertRaises(ValidationError):
            self.env['sc.translation.task'].create({
                'blog_post_id': self.blog_post.id,
                'target_lang_id': self.lang_es.id
            })
```

**OpenAI Integration Tests** (`test_openai_integration.py`):
```python
@tagged('post_install', '-at_install')
class TestOpenAIIntegration(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Mock OpenAI responses
        self.mock_openai_response = {
            'name': 'Publicación de prueba',
            'content': '<p>Contenido de prueba</p>'
        }
    
    @patch('asyncio.run')
    @patch('sc_marketing_automation_tool.utils.openai_service.OpenAITranslationService')
    def test_translation_execution(self, mock_service, mock_asyncio):
        """Test translation execution with mocked OpenAI"""
        mock_asyncio.return_value = self.mock_openai_response
        
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.blog_post.id,
            'target_lang_id': self.lang_es.id
        })
        
        # Execute translation
        result = task._execute_translation_async(task)
        self.assertEqual(result['name'], 'Publicación de prueba')
```

### 7.2 Integration Tests

**Wizard Integration** (`test_wizard.py`):
```python
def test_wizard_translation_workflow(self):
    """Test complete wizard to translation workflow"""
    # Create wizard
    wizard = self.env['sc.translate.blog.post.wizard'].create({
        'target_lang_id': self.lang_es.id,
        'system_instructions': 'Professional tone'
    })
    
    # Set context with selected blog posts
    wizard = wizard.with_context(active_ids=[self.blog_post.id])
    
    # Execute translation
    wizard.action_translate()
    
    # Verify task creation
    task = self.env['sc.translation.task'].search([
        ('blog_post_id', '=', self.blog_post.id),
        ('target_lang_id', '=', self.lang_es.id)
    ])
    self.assertEqual(len(task), 1)
    self.assertEqual(task.system_instructions, 'Professional tone')
```

### 7.3 Performance Tests
- **Bulk Translation**: Test with 50+ blog posts
- **Concurrent Processing**: Multiple cron job executions
- **Memory Usage**: Large content translation
- **API Rate Limiting**: Backoff and retry mechanisms

### 7.4 Test Data Setup
```python
# tests/common.py
class TranslationTestCase(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blog = cls.env['blog.blog'].create({'name': 'Test Blog'})
        cls.blog_posts = cls.env['blog.post'].create([
            {
                'name': f'Test Post {i}',
                'blog_id': cls.blog.id,
                'content': f'<p>Test content {i}</p>'
            } for i in range(5)
        ])
        cls.languages = cls.env['res.lang'].create([
            {'name': 'Spanish', 'code': 'es_ES', 'website_published': True},
            {'name': 'French', 'code': 'fr_FR', 'website_published': True}
        ])
```

### 7.5 Test Execution Commands
```bash
# Run all tests
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf --test-enable --test-tags sc_marketing_automation_tool --stop-after-init

# Run specific test class
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf --test-enable --test-tags sc_marketing_automation_tool.test_translation_task --stop-after-init

# Run with coverage
coverage run --source=custom-addons/sc_marketing_automation_tool odoo-src/odoo-bin -c config/solutto-consulting.conf --test-enable --test-tags sc_marketing_automation_tool --stop-after-init
```

---

## 8. i18n & Documentation Plan

### 8.1 Spanish Translation (es_ES.po)

**Required Translations**:
```po
# Translation Task Model
msgid "AI Translation Task"
msgstr "Tarea de Traducción IA"

msgid "Translation Tasks"
msgstr "Tareas de Traducción"

msgid "Target Language"
msgstr "Idioma Destino"

msgid "AI Instructions"
msgstr "Instrucciones para IA"

msgid "Status"
msgstr "Estado"

msgid "Draft"
msgstr "Borrador"

msgid "In Progress"
msgstr "En Progreso"

msgid "Completed"
msgstr "Completado"

msgid "Error"
msgstr "Error"

# Wizard
msgid "Translate Blog Posts"
msgstr "Traducir Publicaciones del Blog"

msgid "Translate with AI"
msgstr "Traducir con IA"

# Settings
msgid "AI Marketing Tools"
msgstr "Herramientas de Marketing IA"

msgid "OpenAI Configuration"
msgstr "Configuración OpenAI"

msgid "OpenAI API Key"
msgstr "Clave API de OpenAI"

# Error Messages
msgid "OpenAI API key not configured"
msgstr "Clave API de OpenAI no configurada"

msgid "Translation failed: %s"
msgstr "Traducción falló: %s"
```

### 8.2 Documentation Structure

**Technical Documentation** (`docs/technical/`):
- **API Reference**: Complete method documentation for all models
- **Architecture Guide**: OpenAI integration patterns and async processing
- **Development Guide**: Setting up development environment, debugging
- **Database Schema**: Complete field documentation and relationships
- **Integration Guide**: OpenAI Agent SDK setup and configuration
- **Troubleshooting**: Common issues and solutions

**Functional Documentation** (`docs/functional/`):
- **User Guide**: Step-by-step instructions for all user roles
- **Business Processes**: Translation workflow documentation
- **Configuration Guide**: OpenAI setup and model selection
- **Roles & Permissions**: Security groups and access levels
- **FAQ**: Common questions and answers

**Quick Start README** (`README.md`):
- Installation instructions
- Configuration steps
- Basic usage examples
- Links to complete documentation

---

## 9. Risks & Open Questions

### 9.1 Technical Risks
1. **OpenAI API Rate Limits**: Risk of hitting rate limits during bulk operations
   - **Mitigation**: Implement exponential backoff and process in smaller batches
   
2. **Async Processing in Odoo**: Complexity of running async code in sync Odoo context
   - **Mitigation**: Use asyncio.run() with proper event loop management
   
3. **Large Content Translation**: Token limits for very large blog posts
   - **Mitigation**: Content chunking for oversized posts
   
4. **JSON Parsing Reliability**: AI might return invalid JSON
   - **Mitigation**: Robust error handling and retry logic

### 9.2 Business Risks
1. **Translation Quality**: AI translations might not meet quality standards
   - **Mitigation**: Allow custom instructions and manual review process
   
2. **Cost Management**: Unexpected OpenAI API costs
   - **Mitigation**: Usage monitoring and rate limiting
   
3. **Content Policy Violations**: Some content might violate OpenAI policies
   - **Mitigation**: Pre-screening and graceful error handling

### 9.3 Open Questions
1. **Q1**: Should we support other AI providers besides OpenAI?
   - **Answer Needed**: Define scope for v1 vs future versions
   
2. **Q2**: How should we handle partial translation failures?
   - **Answer Needed**: Retry specific fields or entire translation?
   
3. **Q3**: Should translations automatically update the blog post or require manual approval?
   - **Answer Needed**: Define approval workflow requirements
   
4. **Q4**: What happens to translation tasks when blog posts are deleted?
   - **Answer**: Already planned - using ondelete='cascade'

---

## 10. Milestones & PR Strategy

### Milestone 1: Core Infrastructure (Week 1)
**Scope**: Foundation models, security, basic views
- [ ] Create `__manifest__.py` with all dependencies including `"mail"`
- [ ] Implement `sc.translation.task` model with chatter integration
- [ ] Implement `blog.post` inheritance with translation tracking
- [ ] Create security groups and access control lists
- [ ] Basic list/form views for translation tasks (using `<list>` tags)
- [ ] Initial menu structure

**PR Criteria**:
- All models pass `test_access_rights`
- Views render without errors
- Menu navigation works
- Basic CRUD operations functional

### Milestone 2: Wizard & UI Enhancement (Week 1)
**Scope**: Translation wizard and enhanced UI
- [ ] Implement `sc.translate.blog.post.wizard`
- [ ] Create server action for "Translate with AI"
- [ ] Enhance blog post form with translation history
- [ ] Implement kanban view with `default_group_by="state"`
- [ ] Add smart buttons and stat info
- [ ] Wizard form with proper validations

**PR Criteria**:
- Wizard creates translation tasks correctly
- Server action appears in blog post list view
- All views follow Odoo 18.0 standards (`<list>`, conditional UI)
- Kanban view groups by state properly

### Milestone 3: OpenAI Integration (Week 2)
**Scope**: Core translation functionality
- [ ] Install and configure `openai-agents` dependency
- [ ] Implement `OpenAITranslationService` utility class
- [ ] Create async translation execution method
- [ ] Implement cron job for processing tasks
- [ ] Add comprehensive error handling
- [ ] Configuration settings integration

**PR Criteria**:
- Translation tasks process from draft to done/error
- OpenAI Agent SDK integration works correctly
- Cron job processes tasks asynchronously
- Error states handled gracefully
- Configuration settings functional

### Milestone 4: Advanced Features (Week 2)
**Scope**: Enhanced functionality and validation
- [ ] Implement retry mechanisms and rate limiting
- [ ] Add content validation and preprocessing
- [ ] Enhance error messages and logging
- [ ] Implement bulk operation optimizations
- [ ] Add progress tracking and duration logging
- [ ] Smart button for viewing related tasks

**PR Criteria**:
- Rate limiting prevents API overuse
- Bulk translations handle large datasets
- Error messages are user-friendly
- Performance is acceptable for 50+ posts

### Milestone 5: Testing & Documentation (Week 3)
**Scope**: Comprehensive testing and documentation
- [ ] Unit tests for all models (85%+ coverage)
- [ ] Integration tests for complete workflows
- [ ] Performance tests for bulk operations
- [ ] Mock OpenAI responses for reliable testing
- [ ] Complete Spanish translation (`es_ES.po`)
- [ ] Technical and functional documentation

**PR Criteria**:
- All tests pass consistently
- Test coverage meets standards
- Spanish translations 100% complete
- Documentation is comprehensive and accurate

### Milestone 6: Production Hardening (Week 3)
**Scope**: Security, monitoring, and deployment readiness
- [ ] Security audit and penetration testing
- [ ] Performance optimization and monitoring
- [ ] Production configuration validation
- [ ] Backup and recovery procedures
- [ ] User acceptance testing
- [ ] Final documentation review

**PR Criteria**:
- Security scan passes all checks
- Performance meets production standards
- User acceptance criteria satisfied
- Documentation approved by stakeholders

---

## 11. Acceptance Checklist

### Core Functionality
- [ ] Administrators can select multiple blog posts for translation
- [ ] Translation wizard allows language and instruction selection
- [ ] Translation tasks are created and processed asynchronously
- [ ] OpenAI Agent SDK integration works correctly
- [ ] Translation status is tracked throughout the process
- [ ] Error handling provides meaningful feedback
- [ ] Blog posts show translation history

### Odoo 18.0 Compliance
- [ ] All list views use `<list>` tags (never `<tree>`)
- [ ] Conditional UI uses `invisible`/`readonly`/`required` attributes
- [ ] Kanban view defines meaningful `default_group_by="state"`
- [ ] Chatter integration included with `<chatter/>` tag
- [ ] Mail dependency added to `__manifest__.py`
- [ ] No legacy `attrs` or `visibility` containers used

### Security & Access Control
- [ ] Security groups defined with appropriate inheritance
- [ ] Access control lists protect all models
- [ ] Record rules enforce company-specific access
- [ ] API keys stored securely with password=True
- [ ] User roles follow least privilege principle

### Multi-Company & Internationalization
- [ ] Company-dependent fields and security rules implemented
- [ ] Spanish translation file (`es_ES.po`) is 100% complete
- [ ] All user-facing strings use `_()` translation function
- [ ] Multi-company context switching works correctly

### Documentation & Testing
- [ ] Complete technical documentation in `docs/technical/`
- [ ] Complete functional documentation in `docs/functional/`
- [ ] README.md provides clear getting started guide
- [ ] Unit tests achieve 85%+ code coverage
- [ ] Integration tests validate complete workflows
- [ ] Performance tests validate bulk operations

### External Integration
- [ ] OpenAI Agent SDK dependency properly managed
- [ ] API rate limiting and backoff implemented
- [ ] Error taxonomy covers all API response types
- [ ] Timeout and retry mechanisms functional
- [ ] Environment variables handled securely

---

## 12. Plan Diff & Sync Notes

**Plan Creation**: This is the initial implementation plan for `sc_marketing_automation_tool`. No previous plan exists for comparison.

**Key Planning Decisions**:
- Chose OpenAI Agent SDK over direct API calls per specification requirements
- Implemented async processing with cron jobs for scalability
- Added comprehensive error handling and rate limiting
- Included chatter integration for audit trail
- Planned Spanish translation from day one per Solutto standards

**Specification Compliance**:
- ✅ All requirements from Technical-specs-v2025-sep-04.md addressed
- ✅ OpenAI Agent SDK integration planned as mandatory requirement
- ✅ Asynchronous background processing implemented
- ✅ Multi-language support with website published language filtering
- ✅ Complete audit trail and error management

---

## 13. Chatter Integration Plan

**Models Requiring Chatter**:
- `sc.translation.task`: Full chatter integration for audit trail

**Implementation Details**:
```python
class ScTranslationTask(models.Model):
    _name = 'sc.translation.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter
    
    # Tracked fields for automatic messages
    state = fields.Selection(..., tracking=True)
    name = fields.Char(..., tracking=True)
```

**Manifest Dependencies**:
```python
# __manifest__.py
'depends': ['base', 'website', 'website_blog', 'mail'],  # Mail dependency added
```

**Form View Integration**:
```xml
<form string="Translation Task">
    <!-- ... form content ... -->
    </sheet>
    <chatter/>  <!-- Chatter placement at end of form -->
</form>
```

**Automatic Messages**:
- State changes automatically logged
- Manual messages for error details
- Activity scheduling for failed translations

---

## 14. External Libraries & API Research

### OpenAI Agents SDK Integration

**Library Details**:
- **Official Repository**: https://github.com/openai/openai-agents-python
- **Documentation**: https://github.com/openai/openai-agents-python/tree/main/docs
- **Installation**: `pip install openai-agents`
- **Version Strategy**: Use latest stable version, pin in requirements.txt

**Key SDK Features for Our Use Case**:
- **Agent Creation**: `Agent(name, instructions, model)` for translation tasks
- **Runner Execution**: `await Runner.run(agent, prompt)` for async execution
- **Error Handling**: Built-in error types and response validation
- **Model Support**: GPT-4o, GPT-4-turbo, GPT-3.5-turbo

**Authentication & Configuration**:
- **Environment Variables**: `OPENAI_API_KEY`, `OPENAI_ORG_ID`
- **Rate Limits**: Handled by SDK with appropriate backoff
- **Timeouts**: Configurable per request (default 120s for translations)

**Integration Patterns**:
```python
# Basic pattern from SDK docs
agent = Agent(
    name="Odoo Blog Translator",
    instructions="You are a professional translator...",
    model="gpt-4o"
)

result = await Runner.run(agent, translation_prompt)
translated_content = result.final_output
```

**Odoo Async Integration**:
```python
# Sync-to-async bridge for Odoo cron
def _execute_translation_async(self, task):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(self._translate_content(task))
    finally:
        loop.close()
```

**Error Handling & Resilience**:
- **API Errors**: 401 (auth), 429 (rate limit), 500 (server error)
- **Content Errors**: JSON parsing, token limits, policy violations
- **Network Errors**: Timeout, connection failures
- **Retry Strategy**: Exponential backoff (2^n seconds, max 60s)

**Cost Management**:
- **Token Estimation**: Pre-calculate costs for large content
- **Model Selection**: User configurable (GPT-4o default, 3.5-turbo for cost)
- **Usage Monitoring**: Log token usage per translation

---

## Progress Checklist

### ☐ Milestone 1: Core Infrastructure
- [ ] Scaffold module structure
- [ ] Implement core models with chatter
- [ ] Create security framework
- [ ] Basic views (list/form) with Odoo 18.0 compliance

### ☐ Milestone 2: Wizard & UI Enhancement  
- [ ] Translation wizard implementation
- [ ] Server action integration
- [ ] Enhanced blog post views
- [ ] Kanban view with proper grouping

### ☐ Milestone 3: OpenAI Integration
- [ ] OpenAI Agent SDK integration
- [ ] Async translation processing
- [ ] Cron job implementation
- [ ] Configuration settings

### ☐ Milestone 4: Advanced Features
- [ ] Rate limiting and retry logic
- [ ] Bulk operation optimization
- [ ] Enhanced error handling
- [ ] Progress tracking

### ☐ Milestone 5: Testing & Documentation
- [ ] Comprehensive test suite
- [ ] Spanish translation completion
- [ ] Technical documentation
- [ ] Functional documentation

### ☐ Milestone 6: Production Hardening
- [ ] Security audit
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Final documentation review

---

## Plan Changelog

### 2025-09-04T19:30:00Z - Initial Plan Creation
- **Created comprehensive implementation plan** for sc_marketing_automation_tool
- **External Research**: 
  - OpenAI Agents Python SDK (https://github.com/openai/openai-agents-python) - Latest version
  - Agent creation patterns with `Agent(name, instructions, model)`
  - Async execution via `Runner.run()` for translation workflows
  - Built-in error handling and rate limiting capabilities
- **Key Architectural Decisions**:
  - Async processing with cron jobs for scalability
  - OpenAI Agent SDK integration as specified
  - Chatter integration for audit trail
  - Comprehensive error handling with user-friendly messages
- **Odoo 18.0 Compliance**: All views planned with `<list>` tags, conditional UI attributes, and kanban `default_group_by`
- **Solutto Standards**: Spanish translation, documentation structure, and security patterns planned from start
