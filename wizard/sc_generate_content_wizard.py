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
        string="Content Idea (Optional)",
        domain="[('state', '=', 'approved')]",
        help="Select the content idea to use as source for blog generation (optional)"
    )
    
    # Alternative content input (when not using a content idea)
    custom_topic = fields.Char(
        string="Custom Topic",
        help="Topic or title for the blog post (used when not selecting a content idea)"
    )
    
    custom_instructions = fields.Text(
        string="Content Instructions",
        help="Detailed instructions for content generation (used when not selecting a content idea)"
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
    
    # Agent configuration
    agent_config_id = fields.Many2one(
        'sc.ai.agent.config',
        string="AI Agent Configuration",
        domain=[('active', '=', True)],
        help="Select the AI agent configuration to use for content generation"
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
        help="Additional custom instructions for this specific generation task"
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
    
    # Image Generation Options
    generate_cover_image = fields.Boolean(
        string="Generate Cover Image",
        default=True,
        help="Automatically generate a cover image for the blog post using DALL-E"
    )
    
    image_prompt_override = fields.Text(
        string="Custom Image Prompt",
        help="Optional: Custom prompt for image generation. If empty, will be generated from the article content."
    )
    
    image_size = fields.Selection(
        selection=[
            ('1024x1024', '1024x1024 (Square)'),
            ('1024x1792', '1024x1792 (Portrait)'),
            ('1792x1024', '1792x1024 (Landscape)'),
            ('512x512', '512x512 (Square - DALL-E 2)'),
            ('256x256', '256x256 (Square - DALL-E 2)'),
        ],
        string="Image Size",
        help="Size for the generated cover image"
    )
    
    image_quality = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('hd', 'HD (Higher detail)'),
        ],
        string="Image Quality",
        help="Quality for the generated image (DALL-E 3 only)"
    )
    
    image_style = fields.Selection(
        selection=[
            ('vivid', 'Vivid (Hyper-real and dramatic)'),
            ('natural', 'Natural (Less hyper-real)'),
        ],
        string="Image Style",
        help="Visual style for the generated image (DALL-E 3 only)"
    )
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string="Language",
        required=True,
        default='_get_default_website_language',
        help="The language for the generated article (uses website default language)"
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
    def _get_default_website_language(self):
        """Get the default language from the website configuration"""
        try:
            # Get the current website or the first website
            website = self.env['website'].get_current_website()
            if not website:
                website = self.env['website'].search([], limit=1)
            
            # Return the website's default language if available
            if website and website.default_lang_id:
                return website.default_lang_id.id
        except Exception as e:
            # Log warning but don't fail
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Could not get website default language: {e}")
        
        # Fallback to English if website not found or error
        try:
            return self.env.ref('base.lang_en').id
        except Exception:
            # Ultimate fallback - first available language
            lang = self.env['res.lang'].search([], limit=1)
            return lang.id if lang else False

    @api.model
    def default_get(self, fields_list):
        """Set default values from configuration"""
        defaults = super().default_get(fields_list)
        
        # Get default values from generation agent configuration
        agent_config = self.env['sc.ai.agent.config'].get_default_agent('generation')
        
        default_agent_model = agent_config.model if agent_config else 'gpt-4o'
        default_instructions = agent_config.instructions if agent_config else ''
        
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
    
    @api.constrains('agent_config_id')
    def _check_agent_config(self):
        """Validate agent configuration selection"""
        for record in self:
            if not record.agent_config_id:
                raise ValidationError(_("Please select an AI Agent Configuration"))
    
    @api.constrains('content_idea_id', 'custom_topic', 'custom_instructions')
    def _check_content_source(self):
        """Validate that either content idea or custom content is provided"""
        for record in self:
            has_content_idea = bool(record.content_idea_id)
            has_custom_content = bool(record.custom_topic and record.custom_instructions)
            
            if not has_content_idea and not has_custom_content:
                raise ValidationError(_(
                    "Please provide either:\n"
                    "• A Content Idea, OR\n"
                    "• Custom Topic AND Content Instructions"
                ))
            
            if has_content_idea and has_custom_content:
                raise ValidationError(_(
                    "Please choose only one option:\n"
                    "• Content Idea, OR\n"
                    "• Custom Topic + Instructions"
                ))
    
    def action_generate_content(self):
        """Create a content generation task and queue it for processing"""
        self.ensure_one()
        
        # Determine content source and task name
        if self.content_idea_id:
            task_name = _("Blog Generation: %s") % self.content_idea_id.name
            content_source = "content_idea"
        else:
            task_name = _("Blog Generation: %s") % self.custom_topic
            content_source = "custom"
        
        # Update wizard state
        self.write({
            'state': 'processing',
            'processing_log': _("Content generation task created and queued for processing...")
        })
        
        # Prepare task values
        task_values = {
            'name': task_name,
            'target_blog_id': self.blog_id.id,
            'target_lang_id': self.target_lang_id.id,
            'target_word_count': self.target_word_count,
            'agent_config_id': self.agent_config_id.id,
            'user_prompt': self.custom_agent_instructions or '',
            'auto_publish': self.auto_publish,
            'generate_meta_tags': self.generate_meta_tags,
            'state': 'draft',
            # Image generation configuration
            'generate_cover_image': self.generate_cover_image,
            'image_prompt_override': self.image_prompt_override,
            'image_size': self.image_size,
            'image_quality': self.image_quality,
            'image_style': self.image_style,
        }
        
        # Add content source specific fields
        if self.content_idea_id:
            task_values['content_idea_id'] = self.content_idea_id.id
        else:
            # For custom content, we'll store the topic and instructions
            task_values['custom_topic'] = self.custom_topic
            task_values['custom_instructions'] = self.custom_instructions
        
        # Create the generation task
        task = self.env['sc.content.generation.task'].create(task_values)
        
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
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from system configuration"""
        result = super().default_get(fields_list)
        
        # Get image generation defaults from config parameters
        config = self.env['ir.config_parameter'].sudo()
        
        if 'image_size' in fields_list:
            result['image_size'] = config.get_param(
                'sc_marketing_automation_tool.image_default_size',
                '1024x1024'
            )
            
        if 'image_quality' in fields_list:
            result['image_quality'] = config.get_param(
                'sc_marketing_automation_tool.image_default_quality',
                'standard'
            )
            
        if 'image_style' in fields_list:
            result['image_style'] = config.get_param(
                'sc_marketing_automation_tool.image_default_style',
                'vivid'
            )
        
        return result
