from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ScGenerateContentWizard(models.TransientModel):
    _name = 'sc.generate.content.wizard'
    _description = 'Blog Content Generation Wizard'

    name = fields.Char(
        string="Wizard Name",
        default="Blog Content Generation",
        readonly=True
    )

    content_idea_id = fields.Many2one(
        'sc.content.idea',
        string="Content Idea",
        required=True,
        domain="[('state', '=', 'approved')]",
        help="Select the content idea to use as source for blog generation"
    )
    
    blog_id = fields.Many2one(
        'blog.blog',
        string="Target Blog",
        required=True,
        help="The blog where the post will be created"
    )
    
    target_word_count = fields.Integer(
        string="Target Word Count",
        required=True,
        default=800,
        help="Approximate word count for the generated blog post"
    )
    
    agent_model = fields.Char(
        string="Agent Model",
        default="gpt-4o-mini",
        required=True,
        help="OpenAI model to use for content generation"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions",
        help="Custom instructions for the content generation agent"
    )
    
    auto_publish = fields.Boolean(
        string="Auto-publish after generation",
        default=False,
        help="Automatically publish the blog post after generation"
    )
    
    generate_meta_tags = fields.Boolean(
        string="Generate SEO meta tags",
        default=True,
        help="Generate SEO meta tags for the blog post"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string="State", default='draft', readonly=True)
    
    # Related fields from content idea
    content_idea_title = fields.Char(
        string="Idea Title",
        related='content_idea_id.name',
        readonly=True
    )
    
    content_idea_summary = fields.Text(
        string="Idea Summary",
        related='content_idea_id.summary',
        readonly=True
    )
    
    content_idea_source_domain = fields.Char(
        string="Source Domain",
        related='content_idea_id.domain_name',
        readonly=True
    )
    
    content_idea_word_count = fields.Integer(
        string="Idea Word Count",
        related='content_idea_id.word_count',
        readonly=True
    )
    
    content_idea_keywords = fields.Char(
        string="Keywords",
        related='content_idea_id.keywords',
        readonly=True
    )
    
    generated_blog_post_id = fields.Many2one(
        'blog.post',
        string="Generated Blog Post",
        readonly=True
    )
    
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
        
        # Get default agent model from settings
        default_agent_model = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.generation_agent_model', 
            'gpt-4o-mini'
        )
        
        # Get default agent instructions from settings
        default_instructions = self.env['ir.config_parameter'].sudo().get_param(
            'sc_marketing_automation_tool.generation_agent_instructions',
            ''
        )
        
        # Set default blog if only one exists
        if 'blog_id' in fields_list:
            blogs = self.env['blog.blog'].search([], limit=1)
            if blogs:
                defaults['blog_id'] = blogs.id
            
        # Get content idea from context
        if 'content_idea_id' in fields_list and self.env.context.get('default_content_idea_id'):
            defaults['content_idea_id'] = self.env.context['default_content_idea_id']
        
        if 'agent_model' in fields_list:
            defaults['agent_model'] = default_agent_model  
        if 'agent_instructions' in fields_list:
            defaults['agent_instructions'] = default_instructions
            
        return defaults
    
    @api.constrains('target_word_count')
    def _check_target_word_count(self):
        """Validate target word count"""
        for record in self:
            if record.target_word_count < 100:
                raise ValidationError(_("Target word count must be at least 100"))
            if record.target_word_count > 5000:
                raise ValidationError(_("Maximum target word count is 5000"))
    
    def action_generate_content(self):
        """Create a content generation task and queue it for processing"""
        self.ensure_one()
        
        if not self.content_idea_id:
            raise ValidationError(_("Please select a content idea"))
        
        # Update wizard state
        self.write({
            'state': 'processing',
            'processing_log': _("Content generation task created and queued for processing...")
        })
        
        # Create the generation task
        task = self.env['sc.content.generation.task'].create({
            'name': _("Blog Generation: %s") % self.content_idea_id.name,
            'content_idea_id': self.content_idea_id.id,
            'user_prompt': self.agent_instructions or '',
            'target_blog_id': self.blog_id.id,
            'agent_model': self.agent_model,
            'agent_instructions': self.agent_instructions or '',
            'state': 'draft',  # Will be picked up by cron job
        })
        
        # Log the task creation
        task.message_post(
            body=_("Content generation task created via wizard. Queued for processing by generation agent.")
        )
        
        # Update wizard state
        self.write({
            'state': 'done',
            'processing_log': _("Task created successfully. Task ID: %s") % task.id
        })
        
        # Return action to view the created task
        return {
            'type': 'ir.actions.act_window',
            'name': _('Content Generation Task'),
            'res_model': 'sc.content.generation.task',
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
    
    def action_open_blog_post(self):
        """Open the generated blog post"""
        self.ensure_one()
        if not self.generated_blog_post_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Blog Post'),
            'res_model': 'blog.post',
            'res_id': self.generated_blog_post_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
