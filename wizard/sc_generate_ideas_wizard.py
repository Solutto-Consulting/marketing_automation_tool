from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ScGenerateIdeasWizard(models.TransientModel):
    _name = 'sc.generate.ideas.wizard'
    _description = 'Content Ideas Generation Wizard'

    name = fields.Char(
        string="Wizard Name",
        default="Content Ideas Generation",
        readonly=True
    )
    
    query = fields.Text(
        string="Search Query",
        required=True,
        help="Describe what kind of content ideas you want to generate"
    )
    
    num_ideas = fields.Integer(
        string="Number of Ideas",
        required=True,
        default=5,
        help="How many content ideas to generate (1-20)"
    )
    
    # Agent configuration
    agent_config_id = fields.Many2one(
        'sc.ai.agent.config',
        string="AI Agent Configuration",
        domain=[('active', '=', True), ('agent_type', '=', 'research')],
        help="Select the AI agent configuration to use for content research"
    )
    
    agent_model = fields.Selection(
        selection='_get_openai_models',
        string="Agent Model",
        related='agent_config_id.model',
        readonly=True,
        help="OpenAI model from selected agent configuration"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions",
        related='agent_config_id.instructions',
        readonly=True,
        help="Instructions from selected agent configuration"
    )
    
    custom_agent_instructions = fields.Text(
        string="Additional Instructions",
        help="Additional custom instructions for this specific research task"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string="State", default='draft', readonly=True)
    
    processing_log = fields.Text(
        string="Processing Log",
        readonly=True
    )
    
    error_message = fields.Text(
        string="Error Message", 
        readonly=True
    )
    
    @api.model
    def _get_openai_models(self):
        """Get available OpenAI models from settings"""
        try:
            config_settings = self.env['res.config.settings']
            return config_settings._get_openai_models()
        except:
            # Fallback models if settings not available
            return [
                ('gpt-4o', 'GPT-4o'),
                ('gpt-4-turbo', 'GPT-4 Turbo'),
                ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
            ]
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from configuration"""
        defaults = super().default_get(fields_list)
        
        # Get default values from research agent configuration
        agent_config = self.env['sc.ai.agent.config'].get_default_agent('research')
        
        if agent_config:
            if 'agent_config_id' in fields_list:
                defaults['agent_config_id'] = agent_config.id
            if 'query' in fields_list and agent_config.default_query:
                # Replace {today} placeholder with current date
                import datetime
                today = datetime.date.today().strftime('%Y-%m-%d')
                defaults['query'] = agent_config.default_query.replace('{today}', today)
            
        return defaults
    
    @api.constrains('num_ideas')
    def _check_num_ideas(self):
        """Validate number of ideas"""
        for record in self:
            if record.num_ideas < 1:
                raise ValidationError(_("Number of ideas must be at least 1"))
            if record.num_ideas > 20:
                raise ValidationError(_("Maximum 20 ideas can be generated at once"))
    
    @api.constrains('agent_config_id')
    def _check_agent_config(self):
        """Validate agent configuration selection"""
        for record in self:
            if not record.agent_config_id:
                raise ValidationError(_("Please select an AI Agent Configuration"))
            if record.agent_config_id.agent_type != 'research':
                raise ValidationError(_("Please select a Content Research agent"))
    
    def action_open_agent_config(self):
        """Open the agent configuration form"""
        if not self.agent_config_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Agent Configuration'),
            'res_model': 'sc.ai.agent.config',
            'res_id': self.agent_config_id.id,
            'view_mode': 'form',
            'target': 'new',  # Open in modal
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }
    
    def action_generate_ideas(self):
        """Create a content idea task and queue it for processing"""
        self.ensure_one()
        
        # Update wizard state
        self.write({
            'state': 'processing',
            'processing_log': _("Task created and queued for processing...")
        })
        
        # Create the task record
        task = self.env['sc.content.idea.task'].create({
            'name': _("Research Task: %s") % (self.query[:50] + "..." if len(self.query) > 50 else self.query),
            'search_query': self.query,
            'requested_ideas': self.num_ideas,
            'agent_config_id': self.agent_config_id.id,
            'user_prompt': self.custom_agent_instructions or '',
            'state': 'draft',  # Will be picked up by cron job
        })
        
        # Log the task creation
        task.message_post(
            body=_("Task created via wizard. Queued for processing by research agent.")
        )
        
        # Update wizard state
        self.write({
            'state': 'done',
            'processing_log': _("Task created successfully. Task ID: %s") % task.id
        })
        
        # Return action to view the created task
        return {
            'type': 'ir.actions.act_window',
            'name': _('Content Research Task'),
            'res_model': 'sc.content.idea.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_reset(self):
        """Reset wizard to draft state"""
        self.write({
            'state': 'draft',
            'processing_log': '',
            'error_message': ''
        })
        return {'type': 'ir.actions.act_window_close'}
