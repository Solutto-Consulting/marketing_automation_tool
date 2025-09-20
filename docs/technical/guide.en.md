# Technical Developer Guide: Content Management Tool v18.0.1.0.1

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Core Models Reference](#core-models-reference)
4. [API Integration Patterns](#api-integration-patterns)
5. [View and Interface Development](#view-and-interface-development)
6. [Background Processing](#background-processing)
7. [Security Implementation](#security-implementation)
8. [Customization and Extension](#customization-and-extension)
9. [Testing and Quality Assurance](#testing-and-quality-assurance)
10. [Deployment and Maintenance](#deployment-and-maintenance)

---

## Architecture Overview

### System Architecture

The Content Management Tool v18.0.1.0.1 follows a modular, agent-based architecture designed for scalability and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Settings UI  │  Wizards  │  Views (List/Form/Kanban)      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Content Ideas │ Generation Tasks │ Agent Configs │ Utils   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Integration Layer                          │
├─────────────────────────────────────────────────────────────┤
│     OpenAI Agents SDK    │    Web Content Reader           │
│     Request Logging      │    Usage Monitoring             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   External Services                         │
├─────────────────────────────────────────────────────────────┤
│      OpenAI API          │      Web Search APIs            │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

#### 1. Agent-Based Processing
- **Content Research Agent**: Specialized for web search and content discovery
- **Content Generation Agent**: Optimized for blog post creation and formatting
- **Configurable Instructions**: Customizable behavior per agent via system prompts

#### 2. Model Methods First
All business logic is implemented in model methods rather than server actions:
```python
# In models, not server actions
@api.model
def action_process_research_tasks(self):
    """Process pending research tasks in background"""
    tasks = self.search([('state', '=', 'draft')], limit=10)
    for task in tasks:
        task._process_research_task()
```

#### 3. Async Background Processing
- **Cron Jobs**: Separate processing for research and generation tasks
- **State Management**: Clear state transitions (draft → in_progress → done/error)
- **Error Isolation**: Individual task failures don't affect batch processing

#### 4. Comprehensive Logging
- **Request Logging**: All OpenAI API calls logged with cost tracking
- **Error Tracking**: Detailed error capture for troubleshooting
- **Usage Monitoring**: Real-time cost and usage analytics

### Module Dependencies

#### Core Odoo Dependencies
- `base`: Core Odoo framework
- `mail`: Chatter and threading support
- `website`: Website and blog integration
- `website_blog`: Blog post creation and management

#### External Dependencies
- `openai-agents` (>=0.2.9): OpenAI Agents SDK for AI operations
- Python standard libraries: `json`, `logging`, `datetime`, `requests`

---

## Development Environment Setup

### Prerequisites

#### System Requirements
- Python 3.8+ with pip
- Odoo 18.0 Community or Enterprise
- Git for version control
- Text editor with Python support

#### API Access
- OpenAI API account with organization access
- API key with sufficient usage limits
- (Optional) Admin API key for usage monitoring

### Installation Steps

#### 1. Clone and Setup Module
```bash
# Navigate to custom addons directory
cd /path/to/odoo/custom-addons

# Clone or copy the module
cp -r /source/sc_marketing_automation_tool .

# Install Python dependencies
pip install -r sc_marketing_automation_tool/requirements.txt
```

#### 2. Install Dependencies
```bash
# Install OpenAI Agents SDK
pip install openai-agents>=0.2.9

# Install additional requirements if needed
pip install requests beautifulsoup4 lxml
```

#### 3. Configure Odoo
```bash
# Update Odoo with new module
./odoo-bin -d your_database -i sc_marketing_automation_tool --stop-after-init

# Or upgrade existing installation
./odoo-bin -d your_database -u sc_marketing_automation_tool --stop-after-init
```

#### 4. Configure API Credentials
1. Navigate to Settings > General Settings > Marketing Automation Tool
2. Enter OpenAI API key and organization ID
3. Test connection using provided validation
4. Configure AI agent instructions

### Development Tools

#### Recommended IDE Setup
- **VS Code** with Python extension
- **PyCharm** with Odoo plugin
- **Vim/Emacs** with Python syntax highlighting

#### Debugging Configuration
```python
# Add to odoo config for development
[options]
log_level = debug
log_handler = :DEBUG
dev_mode = reload,qweb,werkzeug,xml
```

#### Testing Environment
```bash
# Run tests for the module
./odoo-bin -d test_database --test-enable --test-tags sc_marketing_automation_tool --stop-after-init
```

---

## Core Models Reference

### Content Idea Model (`sc.content.idea`)

#### Purpose
Stores discovered content ideas from research tasks with metadata and approval status.

#### Fields Reference
```python
class ScContentIdea(models.Model):
    _name = 'sc.content.idea'
    _description = 'Content Idea'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Core Fields
    title = fields.Char(string='Article Title', required=True, tracking=True)
    url = fields.Char(string='Source URL', required=True)
    published_date = fields.Date(string='Publication Date')
    summary = fields.Text(string='Summary', required=True)
    
    # Workflow Fields  
    state = fields.Selection([
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('used', 'Used for Content'),
        ('archived', 'Archived')
    ], default='pending', tracking=True)
    
    # Relationships
    research_task_id = fields.Many2one('sc.content.idea.task', 
                                      string='Research Task', 
                                      ondelete='cascade')
    generation_task_ids = fields.One2many('sc.content.generation.task', 
                                         'content_idea_id',
                                         string='Generation Tasks')
```

#### Key Methods
```python
def action_approve(self):
    """Approve content idea for generation"""
    self.state = 'approved'
    self.message_post(body="Content idea approved for generation")

def action_reject(self):
    """Reject content idea"""
    self.state = 'rejected'
    self.message_post(body="Content idea rejected")

def action_generate_content(self):
    """Launch content generation wizard for this idea"""
    return {
        'type': 'ir.actions.act_window',
        'name': 'Generate Content',
        'res_model': 'sc.generate.content.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_content_idea_id': self.id}
    }
```

### Content Research Task Model (`sc.content.idea.task`)

#### Purpose
Manages background research tasks that generate multiple content ideas.

#### State Management
```python
state = fields.Selection([
    ('draft', 'Draft'),           # Created, queued for processing
    ('in_progress', 'Processing'), # Currently being processed
    ('done', 'Completed'),        # Successfully completed
    ('error', 'Error')            # Failed with error
], default='draft', tracking=True)
```

#### Processing Logic
```python
def _process_research_task(self):
    """Process research task using OpenAI Agents SDK"""
    try:
        self.state = 'in_progress'
        
        # Initialize research agent
        agent_config = self.env['sc.ai.agent.config'].get_research_agent()
        
        # Execute web search and analysis
        ideas_data = self._execute_research_with_agent(agent_config)
        
        # Create content ideas from results
        self._create_ideas_from_results(ideas_data)
        
        self.state = 'done'
        self.processed_date = fields.Datetime.now()
        
    except Exception as e:
        self.state = 'error'
        self.error_message = str(e)
        _logger.error(f"Research task {self.id} failed: {e}")
```

### Content Generation Task Model (`sc.content.generation.task`)

#### Purpose
Handles blog post generation from content ideas or custom topics.

#### Generation Flow
```python
def _process_generation_task(self):
    """Generate blog post content using AI agent"""
    try:
        self.state = 'in_progress'
        
        # Get generation agent configuration
        agent_config = self.env['sc.ai.agent.config'].get_generation_agent()
        
        # Prepare generation context
        context = self._prepare_generation_context()
        
        # Generate content using OpenAI
        blog_data = self._generate_content_with_agent(agent_config, context)
        
        # Create blog post
        blog_post = self._create_blog_post(blog_data)
        
        self.generated_blog_post_id = blog_post.id
        self.state = 'done'
        
    except Exception as e:
        self.state = 'error'
        self.error_message = str(e)
```

### AI Agent Configuration Model (`sc.ai.agent.config`)

#### Purpose
Stores AI agent configurations with customizable instructions and model settings.

#### Configuration Structure
```python
class ScAiAgentConfig(models.Model):
    _name = 'sc.ai.agent.config'
    _description = 'AI Agent Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    agent_type = fields.Selection([
        ('research', 'Content Research'),
        ('generation', 'Content Generation')
    ], required=True)
    
    model_id = fields.Many2one('sc.openai.models', string='OpenAI Model')
    instructions = fields.Text(string='Agent Instructions', required=True)
    
    # Configuration parameters
    temperature = fields.Float(string='Temperature', default=0.7)
    max_tokens = fields.Integer(string='Max Tokens', default=2000)
    
    @api.model
    def get_research_agent(self):
        """Get active research agent configuration"""
        return self.search([('agent_type', '=', 'research')], limit=1)
    
    @api.model  
    def get_generation_agent(self):
        """Get active generation agent configuration"""
        return self.search([('agent_type', '=', 'generation')], limit=1)
```

### Usage Monitoring Models

#### Request Log Model (`sc.openai.request.log`)
```python
class ScOpenaiRequestLog(models.Model):
    _name = 'sc.openai.request.log'
    _description = 'OpenAI Request Log'
    _order = 'create_date desc'

    model_name = fields.Char(string='Model Name', required=True)
    prompt_tokens = fields.Integer(string='Prompt Tokens', default=0)
    completion_tokens = fields.Integer(string='Completion Tokens', default=0)
    total_tokens = fields.Integer(string='Total Tokens', compute='_compute_total_tokens')
    cost = fields.Float(string='Cost', digits=(12, 6))
    success = fields.Boolean(string='Success', default=True)
    
    # Relationships
    related_task_id = fields.Reference([
        ('sc.content.idea.task', 'Research Task'),
        ('sc.content.generation.task', 'Generation Task')
    ], string='Related Task')
```

---

## API Integration Patterns

### OpenAI Agents SDK Integration

#### Agent Initialization
```python
from openai_agents import Agent, WebSearchTool

def _initialize_research_agent(self, config):
    """Initialize research agent with web search capabilities"""
    agent = Agent(
        model=config.model_id.name,
        instructions=config.instructions,
        tools=[WebSearchTool()],
        temperature=config.temperature
    )
    return agent
```

#### Error Handling Pattern
```python
def _safe_api_call(self, func, *args, **kwargs):
    """Wrapper for safe OpenAI API calls with retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            
            # Log successful request
            self._log_api_request(success=True, **result.usage)
            
            return result
            
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                continue
            raise
            
        except openai.AuthenticationError as e:
            _logger.error(f"OpenAI authentication failed: {e}")
            raise UserError("OpenAI API authentication failed. Please check your API key.")
            
        except Exception as e:
            # Log failed request
            self._log_api_request(success=False, error=str(e))
            raise
```

#### Usage Tracking
```python
def _log_api_request(self, model_name, prompt_tokens, completion_tokens, 
                    cost=None, success=True, error=None):
    """Log API request for monitoring and cost tracking"""
    
    self.env['sc.openai.request.log'].create({
        'model_name': model_name,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'cost': cost or self._calculate_cost(model_name, prompt_tokens, completion_tokens),
        'success': success,
        'error_message': error,
        'related_task_id': f"{self._name},{self.id}" if hasattr(self, 'id') else False,
        'create_date': fields.Datetime.now()
    })
```

### Web Content Scraping

#### Content Reader Implementation
```python
class WebContentReader(models.Model):
    _name = 'web.content.reader'
    _description = 'Web Content Reader Utility'

    def extract_content(self, url, max_length=5000):
        """Extract clean text content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Content Management Tool)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Extract text content
            text = soup.get_text()
            
            # Clean and truncate
            clean_text = ' '.join(text.split())
            return clean_text[:max_length]
            
        except Exception as e:
            _logger.warning(f"Failed to extract content from {url}: {e}")
            return ""
```

### Configuration Management

#### Settings Integration
```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # OpenAI Configuration
    openai_api_key = fields.Char(
        string='OpenAI API Key',
        config_parameter='sc_marketing_automation_tool.openai_api_key'
    )
    openai_organization_id = fields.Char(
        string='OpenAI Organization ID', 
        config_parameter='sc_marketing_automation_tool.openai_organization_id'
    )
    
    @api.model
    def get_openai_client(self):
        """Get configured OpenAI client instance"""
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.openai_api_key'
        )
        organization_id = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.openai_organization_id'
        )
        
        if not api_key:
            raise UserError("OpenAI API key not configured")
            
        return openai.OpenAI(
            api_key=api_key,
            organization=organization_id
        )
```

---

## View and Interface Development

### Odoo 18.0 View Standards

#### List View Pattern
```xml
<!-- Always use <list> instead of <tree> in Odoo 18.0 -->
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

#### Form View with Chatter
```xml
<record id="view_sc_content_idea_form" model="ir.ui.view">
    <field name="name">sc.content.idea.form</field>
    <field name="model">sc.content.idea</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_approve" type="object" string="Approve" 
                        class="btn-primary" invisible="state != 'pending'"/>
                <button name="action_reject" type="object" string="Reject"
                        invisible="state != 'pending'"/>
                <field name="state" widget="statusbar" 
                       statusbar_visible="pending,approved,used"/>
            </header>
            <sheet>
                <group>
                    <group>
                        <field name="title"/>
                        <field name="url" widget="url"/>
                        <field name="published_date"/>
                    </group>
                    <group>
                        <field name="research_task_id"/>
                        <field name="create_date"/>
                    </group>
                </group>
                <notebook>
                    <page string="Summary">
                        <field name="summary" widget="text"/>
                    </page>
                    <page string="Generation Tasks">
                        <field name="generation_task_ids">
                            <list>
                                <field name="name"/>
                                <field name="state"/>
                                <field name="create_date"/>
                            </list>
                        </field>
                    </page>
                </notebook>
            </sheet>
            <!-- Chatter integration for mail.thread -->
            <chatter/>
        </form>
    </field>
</record>
```

#### Kanban View with Groups
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

### Settings UI Implementation

#### Stable Anchor Pattern
```xml
<record id="res_config_settings_view_form_inherit_sc" model="ir.ui.view">
    <field name="name">res.config.settings.form.inherit.sc</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base_setup.res_config_settings_view_form"/>
    <field name="arch" type="xml">
        <!-- Use stable anchor from core examples -->
        <xpath expr="//setting[@id='account_setting_payment_terms']" position="after">
            <setting id="sc_marketing_automation_setting" string="Marketing Automation Tool">
                <div class="content-group">
                    <div class="mt16">
                        <field name="openai_api_key" password="True"/>
                        <label for="openai_api_key" class="o_light_label"/>
                        <div class="text-muted">
                            Your OpenAI API key for AI-powered content automation.
                        </div>
                    </div>
                    <div class="mt16">
                        <field name="openai_organization_id"/>
                        <label for="openai_organization_id" class="o_light_label"/>
                        <div class="text-muted">
                            Optional: Your OpenAI organization ID for usage tracking.
                        </div>
                    </div>
                </div>
            </setting>
        </xpath>
    </field>
</record>
```

### Wizard Development

#### Generation Wizard Pattern
```python
class ScGenerateContentWizard(models.TransientModel):
    _name = 'sc.generate.content.wizard'
    _description = 'Content Generation Wizard'

    content_idea_id = fields.Many2one('sc.content.idea', string='Content Idea')
    custom_topic = fields.Char(string='Custom Topic')
    target_blog_id = fields.Many2one('blog.blog', string='Target Blog', required=True)
    user_prompt = fields.Text(string='Additional Instructions')
    word_count_target = fields.Integer(string='Target Word Count', default=800)
    
    def action_generate_content(self):
        """Create generation task and return to task list"""
        task_vals = {
            'name': self.custom_topic or self.content_idea_id.title,
            'content_idea_id': self.content_idea_id.id,
            'custom_topic': self.custom_topic,
            'target_blog_id': self.target_blog_id.id,
            'user_prompt': self.user_prompt,
            'word_count_target': self.word_count_target,
            'state': 'draft'
        }
        
        task = self.env['sc.content.generation.task'].create(task_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generation Tasks',
            'res_model': 'sc.content.generation.task',
            'view_mode': 'list,form',
            'domain': [('id', '=', task.id)]
        }
```

---

## Background Processing

### Cron Job Configuration

#### Research Processing Cron
```xml
<record id="cron_process_research_tasks" model="ir.cron">
    <field name="name">Process Content Research Tasks</field>
    <field name="model_id" ref="model_sc_content_idea_task"/>
    <field name="state">code</field>
    <field name="code">model.action_process_research_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```

#### Generation Processing Cron
```xml
<record id="cron_process_generation_tasks" model="ir.cron">
    <field name="name">Process Content Generation Tasks</field>
    <field name="model_id" ref="model_sc_content_generation_task"/>
    <field name="state">code</field>
    <field name="code">model.action_process_generation_tasks()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```

### Processing Implementation

#### Batch Processing Pattern
```python
@api.model
def action_process_research_tasks(self):
    """Process research tasks in batches"""
    # Get pending tasks (limit for performance)
    pending_tasks = self.search([
        ('state', '=', 'draft')
    ], limit=10, order='create_date asc')
    
    for task in pending_tasks:
        try:
            task._process_research_task()
            self.env.cr.commit()  # Commit each task individually
        except Exception as e:
            self.env.cr.rollback()  # Rollback only this task
            _logger.error(f"Failed to process research task {task.id}: {e}")
            task.write({
                'state': 'error',
                'error_message': str(e)
            })
            self.env.cr.commit()
```

#### State Management
```python
def _process_research_task(self):
    """Process single research task with state management"""
    if self.state != 'draft':
        return  # Already processed or processing
        
    try:
        # Update state before processing
        self.write({'state': 'in_progress'})
        self.env.cr.commit()
        
        # Perform actual processing
        self._execute_research()
        
        # Mark as completed
        self.write({
            'state': 'done',
            'processed_date': fields.Datetime.now()
        })
        
    except Exception as e:
        # Mark as failed
        self.write({
            'state': 'error',
            'error_message': str(e)
        })
        raise
```

### Error Handling and Recovery

#### Retry Mechanism
```python
def action_retry(self):
    """Retry failed task"""
    if self.state != 'error':
        raise UserError("Only failed tasks can be retried")
        
    self.write({
        'state': 'draft',
        'error_message': False,
        'processed_date': False
    })
    
    # Log retry action
    self.message_post(body="Task reset for retry")
```

#### Monitoring and Alerts
```python
@api.model
def check_stuck_tasks(self):
    """Check for tasks stuck in processing state"""
    cutoff_time = fields.Datetime.now() - timedelta(hours=1)
    
    stuck_tasks = self.search([
        ('state', '=', 'in_progress'),
        ('write_date', '<', cutoff_time)
    ])
    
    for task in stuck_tasks:
        task.write({
            'state': 'error',
            'error_message': 'Task stuck in processing state - timed out'
        })
        
    if stuck_tasks:
        _logger.warning(f"Found {len(stuck_tasks)} stuck tasks")
```

---

## Security Implementation

### Access Control Lists (ACL)

#### Model Permissions
```csv
# ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sc_content_idea_manager,sc.content.idea manager,model_sc_content_idea,group_marketing_manager,1,1,1,1
access_sc_content_idea_user,sc.content.idea user,model_sc_content_idea,group_marketing_user,1,1,1,0
access_sc_content_idea_task_manager,sc.content.idea.task manager,model_sc_content_idea_task,group_marketing_manager,1,1,1,1
access_sc_content_idea_task_user,sc.content.idea.task user,model_sc_content_idea_task,group_marketing_user,1,1,1,0
access_sc_content_generation_task_manager,sc.content.generation.task manager,model_sc_content_generation_task,group_marketing_manager,1,1,1,1
access_sc_content_generation_task_user,sc.content.generation.task user,model_sc_content_generation_task,group_marketing_user,1,1,1,0
```

#### Security Groups
```xml
<!-- Security Groups -->
<record id="group_marketing_user" model="res.groups">
    <field name="name">Marketing User</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>

<record id="group_marketing_manager" model="res.groups">
    <field name="name">Marketing Manager</field>
    <field name="category_id" ref="base.module_category_marketing"/>
    <field name="implied_ids" eval="[(4, ref('group_marketing_user'))]"/>
</record>
```

### Record Rules

#### User Data Isolation
```xml
<record id="rule_content_idea_user" model="ir.rule">
    <field name="name">Content Ideas: Users can see their own ideas</field>
    <field name="model_id" ref="model_sc_content_idea"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_marketing_user'))]"/>
</record>

<record id="rule_content_idea_manager" model="ir.rule">
    <field name="name">Content Ideas: Managers can see all ideas</field>
    <field name="model_id" ref="model_sc_content_idea"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_marketing_manager'))]"/>
</record>
```

#### Multi-Company Support
```xml
<record id="rule_content_idea_company" model="ir.rule">
    <field name="name">Content Ideas: Multi-company</field>
    <field name="model_id" ref="model_sc_content_idea"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>
</record>
```

### API Security

#### Credential Management
```python
def _get_openai_credentials(self):
    """Secure credential retrieval"""
    ICPSudo = self.env['ir.config_parameter'].sudo()
    
    api_key = ICPSudo.get_param('sc_marketing_automation_tool.openai_api_key')
    if not api_key:
        raise UserError("OpenAI API key not configured")
        
    # Mask key in logs
    masked_key = api_key[:7] + '...' + api_key[-4:] if len(api_key) > 11 else '***'
    _logger.info(f"Using OpenAI API key: {masked_key}")
    
    return {
        'api_key': api_key,
        'organization_id': ICPSudo.get_param('sc_marketing_automation_tool.openai_organization_id')
    }
```

#### Input Validation
```python
@api.constrains('openai_api_key')
def _check_api_key_format(self):
    """Validate API key format"""
    for record in self:
        if record.openai_api_key and not record.openai_api_key.startswith('sk-'):
            raise ValidationError("OpenAI API key must start with 'sk-'")

@api.constrains('openai_organization_id')  
def _check_organization_id_format(self):
    """Validate organization ID format"""
    for record in self:
        if record.openai_organization_id and not record.openai_organization_id.startswith('org-'):
            raise ValidationError("OpenAI Organization ID must start with 'org-'")
```

---

## Customization and Extension

### Agent Configuration Customization

#### Custom Agent Instructions
```python
class ScAiAgentConfig(models.Model):
    _inherit = 'sc.ai.agent.config'
    
    # Add industry-specific fields
    industry_focus = fields.Selection([
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'), 
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('retail', 'Retail')
    ], string='Industry Focus')
    
    target_audience = fields.Selection([
        ('b2b', 'Business to Business'),
        ('b2c', 'Business to Consumer'),
        ('technical', 'Technical Professionals'),
        ('general', 'General Audience')
    ], string='Target Audience')
    
    @api.onchange('industry_focus', 'target_audience')
    def _onchange_context_fields(self):
        """Update instructions based on context"""
        if self.industry_focus and self.target_audience:
            self.instructions = self._generate_context_instructions()
            
    def _generate_context_instructions(self):
        """Generate context-aware instructions"""
        base_instructions = self.instructions or ""
        
        context_additions = []
        
        if self.industry_focus:
            context_additions.append(f"Focus on {self.industry_focus} industry topics and terminology.")
            
        if self.target_audience:
            context_additions.append(f"Write for a {self.target_audience} audience.")
            
        return base_instructions + "\n\n" + "\n".join(context_additions)
```

### Model Extensions

#### Add Custom Fields to Existing Models
```python
class ScContentIdea(models.Model):
    _inherit = 'sc.content.idea'
    
    # Add custom fields
    content_category = fields.Selection([
        ('blog_post', 'Blog Post'),
        ('case_study', 'Case Study'),
        ('whitepaper', 'Whitepaper'),
        ('news', 'News Article')
    ], string='Content Category', default='blog_post')
    
    seo_keywords = fields.Char(string='SEO Keywords')
    target_word_count = fields.Integer(string='Target Word Count', default=800)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')
    
    # Add computed fields
    days_since_published = fields.Integer(
        string='Days Since Published',
        compute='_compute_days_since_published'
    )
    
    @api.depends('published_date')
    def _compute_days_since_published(self):
        """Calculate days since publication"""
        today = fields.Date.today()
        for record in self:
            if record.published_date:
                delta = today - record.published_date
                record.days_since_published = delta.days
            else:
                record.days_since_published = 0
```

### Custom Workflow Extensions

#### Approval Workflow
```python
class ScContentIdea(models.Model):
    _inherit = 'sc.content.idea'
    
    # Add approval workflow
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision_required', 'Revision Required')
    ], string='Approval State', default='draft')
    
    approver_id = fields.Many2one('res.users', string='Approver')
    approval_notes = fields.Text(string='Approval Notes')
    
    def action_submit_for_approval(self):
        """Submit idea for approval"""
        self.approval_state = 'submitted'
        
        # Notify approvers
        approvers = self.env.ref('sc_marketing_automation_tool.group_marketing_manager').users
        self.message_notify(
            partner_ids=approvers.mapped('partner_id').ids,
            subject=f"Content idea approval required: {self.title}",
            body=f"Content idea '{self.title}' has been submitted for approval."
        )
    
    def action_approve_idea(self):
        """Approve content idea"""
        self.write({
            'approval_state': 'approved',
            'state': 'approved',
            'approver_id': self.env.user.id
        })
        
        # Notify submitter
        self.message_post(
            body=f"Content idea approved by {self.env.user.name}",
            message_type='notification'
        )
```

### Integration Extensions

#### External CMS Integration
```python
class ScContentGenerationTask(models.Model):
    _inherit = 'sc.content.generation.task'
    
    # Add external publishing options
    external_cms = fields.Selection([
        ('wordpress', 'WordPress'),
        ('drupal', 'Drupal'),
        ('contentful', 'Contentful')
    ], string='External CMS')
    
    external_post_id = fields.Char(string='External Post ID')
    
    def action_publish_to_external_cms(self):
        """Publish to external CMS"""
        if not self.external_cms:
            raise UserError("No external CMS configured")
            
        if self.external_cms == 'wordpress':
            self._publish_to_wordpress()
        elif self.external_cms == 'drupal':
            self._publish_to_drupal()
        elif self.external_cms == 'contentful':
            self._publish_to_contentful()
    
    def _publish_to_wordpress(self):
        """Publish content to WordPress via REST API"""
        wp_config = self.env['ir.config_parameter'].sudo()
        wp_url = wp_config.get_param('sc_marketing.wordpress_url')
        wp_user = wp_config.get_param('sc_marketing.wordpress_user')
        wp_password = wp_config.get_param('sc_marketing.wordpress_password')
        
        if not all([wp_url, wp_user, wp_password]):
            raise UserError("WordPress configuration incomplete")
            
        # Prepare post data
        post_data = {
            'title': self.generated_blog_post_id.name,
            'content': self.generated_blog_post_id.content,
            'status': 'draft',
            'excerpt': self.generated_blog_post_id.subtitle or ''
        }
        
        # Make API call
        response = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts",
            json=post_data,
            auth=(wp_user, wp_password)
        )
        
        if response.status_code == 201:
            post_id = response.json().get('id')
            self.external_post_id = str(post_id)
            self.message_post(body=f"Successfully published to WordPress (ID: {post_id})")
        else:
            raise UserError(f"WordPress publish failed: {response.text}")
```

---

## Testing and Quality Assurance

### Unit Testing Framework

#### Test Structure
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from unittest.mock import patch, MagicMock

class TestContentIdea(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.ContentIdea = self.env['sc.content.idea']
        self.ResearchTask = self.env['sc.content.idea.task']
        
        # Create test data
        self.research_task = self.ResearchTask.create({
            'name': 'Test Research Task',
            'search_query': 'test query',
            'number_of_suggestions': 5
        })
        
    def test_content_idea_creation(self):
        """Test content idea creation"""
        idea = self.ContentIdea.create({
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'summary': 'Test summary',
            'research_task_id': self.research_task.id
        })
        
        self.assertEqual(idea.state, 'pending')
        self.assertEqual(idea.title, 'Test Article')
        
    def test_content_idea_approval(self):
        """Test content idea approval workflow"""
        idea = self.ContentIdea.create({
            'title': 'Test Article',
            'url': 'https://example.com/test', 
            'summary': 'Test summary',
            'research_task_id': self.research_task.id
        })
        
        # Test approval
        idea.action_approve()
        self.assertEqual(idea.state, 'approved')
        
        # Test rejection  
        idea.action_reject()
        self.assertEqual(idea.state, 'rejected')
```

#### Mock External APIs
```python
class TestOpenAIIntegration(TransactionCase):
    
    @patch('openai_agents.Agent')
    def test_research_task_processing(self, mock_agent):
        """Test research task processing with mocked OpenAI"""
        # Mock OpenAI response
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance
        
        mock_response = {
            'ideas': [
                {
                    'title': 'Test Article 1',
                    'url': 'https://example.com/1',
                    'summary': 'Test summary 1',
                    'published_date': '2023-01-01'
                },
                {
                    'title': 'Test Article 2', 
                    'url': 'https://example.com/2',
                    'summary': 'Test summary 2',
                    'published_date': '2023-01-02'
                }
            ]
        }
        
        mock_agent_instance.run.return_value = mock_response
        
        # Create and process research task
        task = self.env['sc.content.idea.task'].create({
            'name': 'Test Task',
            'search_query': 'test query',
            'number_of_suggestions': 2
        })
        
        task._process_research_task()
        
        # Verify results
        self.assertEqual(task.state, 'done')
        self.assertEqual(len(task.generated_idea_ids), 2)
        
        # Verify mock was called correctly
        mock_agent.assert_called_once()
        mock_agent_instance.run.assert_called_once()
```

### Integration Testing

#### API Integration Tests
```python
class TestAPIIntegration(TransactionCase):
    
    def test_openai_authentication(self):
        """Test OpenAI API authentication"""
        # Set up test credentials
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation_tool.openai_api_key', 
            'sk-test-key'
        )
        
        # Test credential retrieval
        config = self.env['res.config.settings'].create({})
        credentials = config._get_openai_credentials()
        
        self.assertEqual(credentials['api_key'], 'sk-test-key')
        
    def test_invalid_api_key_handling(self):
        """Test handling of invalid API key"""
        # Clear API key
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation_tool.openai_api_key', 
            ''
        )
        
        config = self.env['res.config.settings'].create({})
        
        with self.assertRaises(UserError):
            config._get_openai_credentials()
```

### Performance Testing

#### Load Testing
```python
class TestPerformance(TransactionCase):
    
    def test_bulk_idea_creation(self):
        """Test bulk creation of content ideas"""
        import time
        
        # Create research task
        task = self.env['sc.content.idea.task'].create({
            'name': 'Bulk Test Task',
            'search_query': 'bulk test',
            'number_of_suggestions': 100
        })
        
        # Measure bulk creation time
        start_time = time.time()
        
        ideas_data = []
        for i in range(100):
            ideas_data.append({
                'title': f'Test Article {i}',
                'url': f'https://example.com/{i}',
                'summary': f'Test summary {i}',
                'research_task_id': task.id
            })
        
        ideas = self.env['sc.content.idea'].create(ideas_data)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Performance assertion (should create 100 ideas in under 5 seconds)
        self.assertLess(creation_time, 5.0)
        self.assertEqual(len(ideas), 100)
```

### Quality Assurance Checklist

#### Code Quality Standards
- [ ] All methods have docstrings
- [ ] Error handling implemented for external API calls
- [ ] Input validation on user-facing fields
- [ ] Logging implemented for debugging
- [ ] Tests cover main functionality paths
- [ ] Security rules properly implemented

#### Odoo Standards Compliance
- [ ] List views use `<list>` tag (not `<tree>`)
- [ ] Kanban views have `default_group_by`
- [ ] Models with mail integration include `<chatter/>`
- [ ] Settings use stable anchors from core examples
- [ ] ACL files properly formatted
- [ ] Menu hierarchy follows Odoo conventions

---

## Deployment and Maintenance

### Production Deployment

#### Deployment Checklist
- [ ] Backup existing database
- [ ] Install/upgrade module in staging environment
- [ ] Run full test suite
- [ ] Configure production API credentials
- [ ] Verify cron jobs are active
- [ ] Test core workflows end-to-end
- [ ] Monitor logs for errors

#### Environment Configuration
```bash
# Production deployment script
#!/bin/bash

# Backup database
pg_dump odoo_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Update module
./odoo-bin -d odoo_production -u sc_marketing_automation_tool --stop-after-init

# Run tests
./odoo-bin -d odoo_production --test-enable --test-tags sc_marketing_automation_tool --stop-after-init

# Start production server
./odoo-bin -c /etc/odoo/odoo.conf
```

### Monitoring and Maintenance

#### System Health Monitoring
```python
@api.model
def system_health_check(self):
    """Comprehensive system health check"""
    health_status = {
        'openai_connection': self._test_openai_connection(),
        'pending_tasks': self._count_pending_tasks(),
        'error_rate': self._calculate_error_rate(),
        'disk_usage': self._check_disk_usage(),
        'last_successful_run': self._get_last_successful_run()
    }
    
    # Log health status
    _logger.info(f"System health check: {health_status}")
    
    # Send alerts if needed
    if health_status['error_rate'] > 0.1:  # More than 10% error rate
        self._send_alert("High error rate detected")
        
    if health_status['pending_tasks'] > 100:  # Too many pending tasks
        self._send_alert("High number of pending tasks")
        
    return health_status
```

#### Performance Monitoring
```python
@api.model
def performance_metrics(self):
    """Collect performance metrics"""
    metrics = {
        'avg_research_time': self._avg_processing_time('sc.content.idea.task'),
        'avg_generation_time': self._avg_processing_time('sc.content.generation.task'),
        'success_rate': self._success_rate(),
        'api_cost_today': self._api_cost_today(),
        'active_users': self._count_active_users()
    }
    
    # Store metrics for trending
    self.env['sc.system.metrics'].create({
        'date': fields.Date.today(),
        'metrics_data': json.dumps(metrics)
    })
    
    return metrics
```

### Troubleshooting Tools

#### Diagnostic Commands
```python
@api.model
def diagnose_task_issues(self, task_id=None):
    """Diagnose task processing issues"""
    if task_id:
        tasks = self.browse(task_id)
    else:
        # Get recent failed tasks
        tasks = self.search([
            ('state', '=', 'error'),
            ('create_date', '>', fields.Datetime.now() - timedelta(days=1))
        ])
    
    diagnosis = []
    for task in tasks:
        task_diagnosis = {
            'task_id': task.id,
            'error_message': task.error_message,
            'last_attempt': task.write_date,
            'retry_count': task.retry_count or 0,
            'possible_causes': self._analyze_error(task.error_message),
            'suggested_actions': self._suggest_fixes(task.error_message)
        }
        diagnosis.append(task_diagnosis)
    
    return diagnosis
```

#### Log Analysis
```python
@api.model
def analyze_error_patterns(self, days=7):
    """Analyze error patterns from logs"""
    cutoff_date = fields.Datetime.now() - timedelta(days=days)
    
    error_logs = self.env['sc.openai.request.log'].search([
        ('success', '=', False),
        ('create_date', '>', cutoff_date)
    ])
    
    error_patterns = {}
    for log in error_logs:
        error_type = self._categorize_error(log.error_message)
        if error_type not in error_patterns:
            error_patterns[error_type] = {
                'count': 0,
                'examples': []
            }
        error_patterns[error_type]['count'] += 1
        if len(error_patterns[error_type]['examples']) < 3:
            error_patterns[error_type]['examples'].append({
                'timestamp': log.create_date,
                'message': log.error_message[:200]
            })
    
    return error_patterns
```

### Backup and Recovery

#### Data Backup Strategy
```python
@api.model
def backup_critical_data(self):
    """Backup critical configuration and data"""
    backup_data = {
        'timestamp': fields.Datetime.now().isoformat(),
        'agent_configs': self.env['sc.ai.agent.config'].search_read([]),
        'system_settings': self._export_system_settings(),
        'active_tasks': self.env['sc.content.idea.task'].search_read([
            ('state', 'in', ['draft', 'in_progress'])
        ]),
        'recent_logs': self.env['sc.openai.request.log'].search_read([
            ('create_date', '>', fields.Datetime.now() - timedelta(days=30))
        ])
    }
    
    # Store backup
    backup_file = f"/tmp/sc_marketing_backup_{fields.Date.today()}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    _logger.info(f"Backup completed: {backup_file}")
    return backup_file
```

#### Recovery Procedures
```python
@api.model
def restore_from_backup(self, backup_file):
    """Restore system from backup file"""
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
            
        # Restore agent configurations
        for config_data in backup_data['agent_configs']:
            existing = self.env['sc.ai.agent.config'].search([
                ('name', '=', config_data['name'])
            ])
            if existing:
                existing.write(config_data)
            else:
                self.env['sc.ai.agent.config'].create(config_data)
        
        # Restore system settings
        self._import_system_settings(backup_data['system_settings'])
        
        _logger.info("System restored from backup successfully")
        
    except Exception as e:
        _logger.error(f"Backup restore failed: {e}")
        raise UserError(f"Restore failed: {e}")
```

---

## External References

### Core Odoo Examples
- **Settings UI Patterns**: `odoo-src/odoo/addons/base/views/res_config_settings_views.xml`
- **Mail Thread Integration**: `odoo-src/addons/mail/models/mail_thread.py`
- **Cron Job Examples**: `odoo-src/addons/base/data/ir_cron_data.xml`
- **Security Rule Patterns**: `odoo-src/addons/base/security/ir_rule.xml`

### External API Documentation
- **OpenAI Agents SDK**: [https://github.com/openai/openai-agents](https://github.com/openai/openai-agents) (v0.2.9+)
- **OpenAI API Reference**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- **Usage API Endpoints**: [https://platform.openai.com/docs/api-reference/usage](https://platform.openai.com/docs/api-reference/usage)

### Python Libraries
- **Requests**: HTTP client for web scraping and API calls
- **BeautifulSoup4**: HTML parsing for content extraction
- **JSON**: Data serialization for API responses

### Rate Limits and Best Practices
- **API Rate Limits**: Tier-based limits per OpenAI subscription level
- **Retry Policies**: Exponential backoff with maximum 3 attempts
- **Timeout Settings**: 30-60 seconds for content generation requests
- **Error Handling**: Comprehensive error categorization and user feedback

---

*Technical documentation version: 18.0.1.0.1 | Last updated: September 20, 2025*
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

## User Experience Enhancements (v18.0.1.0.1)

The latest version introduces significant improvements to the user interface and workflow experience, focusing on consistency, usability, and immediate feedback.

### Wizard Experience Improvements

#### Consistent Agent Selection Patterns
- **Agent Type Filtering**: All wizards now implement domain filtering for appropriate agent types
  - Research wizards filter to `agent_type='research'` only
  - Generation wizards filter to `agent_type='generation'` only
  - Translation wizards use enhanced agent selection patterns

#### Enhanced Field Display
- **Truncated Display**: Long agent model names and instructions are truncated with ellipsis
  - Prevents layout breaking with very long configuration text
  - Maintains visual consistency across different agent configurations
  - Uses CSS styling for proper overflow handling: `style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"`

#### Direct Configuration Access
- **Configure Buttons**: Added quick access buttons next to agent selection fields
  - Opens agent configuration form in new window/tab
  - Provides immediate access to modify agent settings without losing wizard context
  - Implements standard Odoo button styling: `class="btn btn-sm btn-outline-secondary ms-2"`

### Enhanced Action Button Experience

#### Automatic Page Refresh Implementation
```python
def action_execute_immediately(self):
    """Execute task with automatic page refresh"""
    try:
        # Process the task
        self._process_task()
        
        # Return reload action instead of boolean
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
    except Exception as e:
        # Return reload with error notification
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'next': {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Task Execution Failed'),
                        'message': str(e),
                        'type': 'danger'
                    }
                }
            }
        }
```

#### Benefits of Auto-Refresh Pattern
- **Eliminates Manual Refresh**: Users no longer need to manually refresh pages to see task status updates
- **Immediate Feedback**: Task state changes are visible immediately after action completion
- **Better User Experience**: Reduces friction in task management workflows
- **Consistent Behavior**: Same pattern implemented across all task models (content generation, ideas, translation)

### Multiple Article Generation from Content Ideas

#### Enhanced Content Idea Reusability
```python
class ScContentIdea(models.Model):
    _name = 'sc.content.idea'
    
    generation_tasks_count = fields.Integer(
        string="Generation Tasks",
        compute='_compute_generation_tasks_count',
        help="Number of blog posts generated from this idea"
    )
    
    generated_blog_posts = fields.One2many(
        'blog.post',
        'source_content_idea_id',
        string="Generated Blog Posts",
        help="Blog posts generated from this content idea"
    )
```

#### Technical Implementation
- **Task Counting**: Computed fields track how many articles have been generated from each idea
- **Usage Statistics**: Enhanced views show utilization metrics for content ideas
- **Workflow Integration**: Seamless integration between content ideas and generation tasks

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

### Static Model Management (v18.0.1.0.1)

**Architecture**: Centralized static model definitions  
**Purpose**: Provide consistent, reliable model selection across all components

```python
# models/sc_openai_models.py
class ScOpenaiModels(models.AbstractModel):
    """
    Centralized OpenAI Models Configuration
    
    This class provides a single source of truth for all OpenAI models
    supported by the Marketing Automation Tool. It ensures consistency
    across all model selection fields throughout the system.
    """
    _name = 'sc.openai.models'
    _description = 'OpenAI Models Configuration'

    @api.model
    def get_text_models(self):
        """Get supported text models for content generation and research."""
        return [
            ('gpt-5', 'GPT-5'),
            ('gpt-5-mini', 'GPT-5 Mini'),
            ('gpt-5-nano', 'GPT-5 Nano'),
            ('gpt-4.1', 'GPT-4.1'),
            ('gpt-4.1-mini', 'GPT-4.1 Mini'),
            ('gpt-4.1-nano', 'GPT-4.1 Nano'),
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4o-mini', 'GPT-4o Mini'),
        ]

    @api.model
    def get_image_models(self):
        """Get supported image generation models."""
        return [
            ('gpt-image-1', 'GPT Image-1'),
        ]

    @api.model
    def get_all_models(self):
        """Get all supported models (text + image)."""
        return self.get_text_models() + self.get_image_models()
```

### Integration Pattern

All model selection fields throughout the system use centralized methods:

```python
# Usage in any model
class SomeModel(models.Model):
    _name = 'some.model'
    
    def _get_model_selection(self):
        """Get model selection from centralized configuration."""
        return self.env['sc.openai.models'].get_text_models()
    
    model_field = fields.Selection(
        selection='_get_model_selection',
        string='AI Model',
        required=True,
        default='gpt-4o'
    )
```

### Benefits of Static Model Management

#### Reliability
- **No API Dependencies**: Model selection doesn't require external API calls
- **Consistent Performance**: No delays from network requests during configuration
- **Failure Resistant**: Works regardless of OpenAI API availability

#### Consistency
- **Unified Selection**: Same model options across all configuration screens
- **Version Control**: Model definitions tracked in code repository
- **Predictable Behavior**: No variation based on API response differences

#### Maintenance
- **Centralized Updates**: Single location to add/remove supported models
- **Easy Testing**: Reliable model lists for development and testing environments
- **Performance**: Faster form loading without external API calls

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

#### Critical Fixes Applied (v18.0.1.0.1)

**OpenAI Client Initialization Fix**

The previous implementation had a critical error when initializing the OpenAI client with organization settings:

```python
# ❌ Previous incorrect implementation (caused setter error)
self._client = OpenAI(api_key=api_key)
if org_id:
    self._client.default_headers = {"OpenAI-Organization": str(org_id)}  # ERROR: no setter
```

**Root Cause**: The `default_headers` property in newer versions of the OpenAI Python library does not have a setter, causing the error: `property 'default_headers' of 'OpenAI' object has no setter`

**Resolution Applied**: 
```python
# ✅ Corrected implementation (v18.0.1.0.1)
if org_id:
    self._client = OpenAI(
        api_key=api_key,
        organization=str(org_id)  # Pass during initialization
    )
else:
    self._client = OpenAI(api_key=api_key)
```

**Validation with Official OpenAI Documentation**
- Confirmed `gpt-image-1` is a valid and recommended model for image generation
- Validated all gpt-image-1 specific parameters: `background`, `moderation`, `output_format`, `partial_images`
- Ensured compliance with official OpenAI API examples and best practices

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

#### Usage Tracking Integration (Enhanced v18.0.1.0.1)

Image generation usage is now fully integrated with the centralized monitoring system:

```python
def generate_image_with_context(self, prompt, article_title="", **options):
    """
    Generate image with comprehensive monitoring integration.
    
    This method now includes complete request logging with timing,
    token usage, and error tracking.
    """
    start_time = time.time()
    
    try:
        # Generate image using OpenAI API
        response = self.client.images.generate(
            model='gpt-image-1',
            prompt=prompt,
            **options
        )
        
        # Calculate response time
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Extract token usage from response
        usage = response.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        total_tokens = input_tokens + output_tokens
        
        # Log successful generation
        self.env['sc.openai.request.log'].sudo().create_log_entry(
            model_name='gpt-image-1',
            operation_type='image_generation',
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            response_time_ms=response_time_ms,
            status='success',
            related_model='blog.post',
            related_record_name=article_title[:100]
        )
        
        return response
        
    except Exception as e:
        # Calculate response time for failed request
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Log failed generation
        self.env['sc.openai.request.log'].sudo().create_log_entry(
            model_name='gpt-image-1',
            operation_type='image_generation',
            prompt_tokens=0,
            completion_tokens=0,
            response_time_ms=response_time_ms,
            status='error',
            error_message=str(e)[:500],
            related_model='blog.post',
            related_record_name=article_title[:100]
        )
        
        raise
```

#### Operation Type Configuration Fix

The monitoring system required an update to support image generation tracking:

```python
# models/sc_openai_request_log.py
operation_type = fields.Selection([
    ('translation', 'Content Translation'),
    ('generation', 'Content Generation'),
    ('image_generation', 'Image Generation'),  # Added in v18.0.1.0.1
    ('analysis', 'Content Analysis'),
    ('research', 'Web Research'),
    ('other', 'Other Operation'),
], string='Operation Type', required=True, index=True)
```

#### Benefits of Enhanced Image Monitoring

- **Complete Tracking**: All image generation operations logged with detailed metrics
- **Performance Analysis**: Response time measurement for optimization
- **Cost Attribution**: Token usage and cost tracking for budget management
- **Error Analysis**: Comprehensive error logging for troubleshooting
- **Content Integration**: Direct linking to blog posts for context

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
