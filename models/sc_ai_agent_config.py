from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ScAiAgentConfig(models.Model):
    """AI Agent Configuration Management"""
    _name = 'sc.ai.agent.config'
    _description = 'AI Agent Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'agent_type, sequence, name'
    
    name = fields.Char(
        string="Agent Name",
        required=True,
        tracking=True,
        help="Descriptive name for this agent configuration"
    )
    
    agent_type = fields.Selection([
        ('research', 'Content Research Agent'),
        ('generation', 'Content Generation Agent'),
    ], string="Agent Type", required=True, tracking=True, help="Type of AI agent")
    
    model = fields.Selection(
        selection='_get_openai_models',
        string="OpenAI Model",
        required=True,
        default='gpt-4o',
        tracking=True,
        help="OpenAI model to use for this agent"
    )
    
    instructions = fields.Text(
        string="System Instructions",
        required=True,
        tracking=True,
        help="Detailed instructions that define the agent's behavior and capabilities"
    )
    
    default_query = fields.Text(
        string="Default Query Template",
        help="Default query template for this agent (use {today} for date placeholders)"
    )
    
    is_default = fields.Boolean(
        string="Default Agent",
        tracking=True,
        help="Set as the default agent for this type",
        default=False
    )
    
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Deactivate to hide this agent configuration"
    )
    
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order for agent selection"
    )
    
    # Usage tracking
    last_used = fields.Datetime(
        string="Last Used",
        help="When this agent configuration was last used"
    )
    
    usage_count = fields.Integer(
        string="Usage Count",
        default=0,
        help="Number of times this agent has been used"
    )
    
    # Metadata
    created_by = fields.Many2one(
        'res.users',
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True
    )
    
    notes = fields.Text(
        string="Notes",
        help="Additional notes about this agent configuration"
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
    def get_default_agent(self, agent_type):
        """Get the default agent configuration for a given type"""
        agent = self.search([
            ('agent_type', '=', agent_type),
            ('is_default', '=', True),
            ('active', '=', True)
        ], limit=1)
        
        if not agent:
            # Try to get any active agent of this type
            agent = self.search([
                ('agent_type', '=', agent_type),
                ('active', '=', True)
            ], limit=1)
        
        return agent
    
    @api.model
    def get_agent_instructions(self, agent_type):
        """Get instructions for the default agent of given type"""
        agent = self.get_default_agent(agent_type)
        return agent.instructions if agent else ""
    
    @api.model
    def get_agent_model(self, agent_type):
        """Get model for the default agent of given type"""
        agent = self.get_default_agent(agent_type)
        return agent.model if agent else 'gpt-4o'
    
    @api.model
    def get_default_query(self, agent_type):
        """Get default query for the default agent of given type"""
        agent = self.get_default_agent(agent_type)
        return agent.default_query if agent else ""
    
    def action_use_agent(self):
        """Track agent usage"""
        self.ensure_one()
        self.write({
            'last_used': fields.Datetime.now(),
            'usage_count': self.usage_count + 1
        })
    
    def action_set_as_default(self):
        """Set this agent as default for its type"""
        self.ensure_one()
        
        # Remove default flag from other agents of same type
        other_defaults = self.search([
            ('agent_type', '=', self.agent_type),
            ('is_default', '=', True),
            ('id', '!=', self.id)
        ])
        other_defaults.write({'is_default': False})
        
        # Set this agent as default
        self.is_default = True
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Agent set as default for %s') % dict(self._fields['agent_type'].selection)[self.agent_type],
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_duplicate(self):
        """Duplicate this agent configuration"""
        self.ensure_one()
        copy = self.copy({
            'name': _('%s (Copy)') % self.name,
            'is_default': False,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Agent Configuration'),
            'res_model': 'sc.ai.agent.config',
            'res_id': copy.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.constrains('is_default', 'agent_type', 'active')
    def _check_single_default_per_type(self):
        """Ensure only one default agent per type"""
        for record in self:
            if record.is_default and record.active:
                other_defaults = self.search([
                    ('agent_type', '=', record.agent_type),
                    ('is_default', '=', True),
                    ('active', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_defaults:
                    raise ValidationError(
                        _('Only one agent can be set as default for each agent type.')
                    )
    
    @api.model
    def create_default_agents(self):
        """Create default agent configurations if none exist"""
        
        # Research Agent Default
        if not self.search([('agent_type', '=', 'research')]):
            self.create({
                'name': 'Default Research Agent',
                'agent_type': 'research',
                'model': 'gpt-4o',
                'is_default': True,
                'instructions': """You are a content research agent specialized in finding relevant, recent articles and news for content marketing.

Your task is to search the web for articles related to the given topic and return a structured list of content ideas.

For each article you find, provide:
1. The article title
2. The full URL to the article
3. The publication date (if available)
4. A concise summary highlighting the key points and why it would be valuable for content creation

Focus on:
- Recent articles (preferably within the last 6 months)
- Authoritative sources and industry publications
- Trending topics and emerging insights
- Actionable information that can inspire blog content

Return your findings as a JSON list with the specified structure.""",
                'default_query': "Find recent articles about digital marketing trends and best practices published after {today}",
                'notes': 'Default configuration for content research tasks'
            })
        
        # Generation Agent Default
        if not self.search([('agent_type', '=', 'generation')]):
            self.create({
                'name': 'Default Content Generation Agent',
                'agent_type': 'generation',
                'model': 'gpt-4o',
                'is_default': True,
                'instructions': """You are a professional content writer specialized in creating engaging blog posts for business audiences.

Your task is to create a complete blog post based on the provided source content and user requirements.

Generate a comprehensive blog post with:
1. An engaging, SEO-friendly title
2. Well-structured HTML content with proper headings, paragraphs, and formatting
3. A compelling meta description for SEO
4. Relevant keywords for content optimization

Content Guidelines:
- Write in a professional yet engaging tone
- Use clear headings and subheadings (H2, H3)
- Include actionable insights and practical advice
- Aim for 800-1500 words depending on the topic
- Ensure content is original and adds value beyond the source material
- Include a strong introduction and conclusion

Return your response as a JSON object with the specified structure containing title, content, meta_description, and keywords.""",
                'notes': 'Default configuration for blog content generation'
            })
        
        _logger.info("Default AI agent configurations created successfully")
