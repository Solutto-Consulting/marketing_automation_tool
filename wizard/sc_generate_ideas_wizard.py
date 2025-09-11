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
    
    blog_id = fields.Many2one(
        'blog.blog',
        string="Target Blog",
        required=True,
        help="The blog where generated content ideas will be associated"
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
    
    agent_model = fields.Char(
        string="Agent Model",
        default="gpt-4o-mini",
        required=True,
        help="OpenAI model to use for content research"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions",
        help="Custom instructions for the content research agent"
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
    def default_get(self, fields_list):
        """Set default values from configuration"""
        defaults = super().default_get(fields_list)
        
        # Get default values from research agent configuration
        agent_config = self.env['sc.ai.agent.config'].get_default_agent('research')
        
        default_query = agent_config.default_query if agent_config else 'Find recent articles about digital marketing trends and best practices published after {today}'
        default_agent_model = agent_config.model if agent_config else 'gpt-4o'
        default_instructions = agent_config.instructions if agent_config else ''
        
        if 'query' in fields_list:
            defaults['query'] = default_query
        if 'agent_model' in fields_list:
            defaults['agent_model'] = default_agent_model  
        if 'agent_instructions' in fields_list:
            defaults['agent_instructions'] = default_instructions
            
        return defaults
    
    @api.constrains('num_ideas')
    def _check_num_ideas(self):
        """Validate number of ideas"""
        for record in self:
            if record.num_ideas < 1:
                raise ValidationError(_("Number of ideas must be at least 1"))
            if record.num_ideas > 20:
                raise ValidationError(_("Maximum 20 ideas can be generated at once"))
    
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
            'agent_model': self.agent_model,
            'agent_instructions': self.agent_instructions or '',
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
