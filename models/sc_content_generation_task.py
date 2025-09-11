from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ScContentGenerationTask(models.Model):
    _name = 'sc.content.generation.task'
    _description = 'Content Generation Task Tracking for Blog Posts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string="Task Name",
        required=True,
        tracking=True,
        help="Descriptive name for this generation task"
    )
    
    content_idea_id = fields.Many2one(
        'sc.content.idea',
        string="Source Idea",
        ondelete='cascade',
        help="The content idea used as source for generation (optional)"
    )
    
    # Alternative content input (when not using a content idea)
    custom_topic = fields.Char(
        string="Custom Topic",
        help="Topic or title for the blog post (used when not selecting a content idea)"
    )
    
    custom_instructions = fields.Text(
        string="Custom Instructions",
        help="Detailed instructions for content generation (used when not selecting a content idea)"
    )
    
    user_prompt = fields.Text(
        string="Additional Instructions",
        help="Additional instructions from the user for content generation"
    )
    
    target_word_count = fields.Integer(
        string="Target Word Count",
        default=800,
        help="Approximate word count for the generated blog post"
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
    
    generated_blog_post_id = fields.Many2one(
        'blog.post',
        string="Generated Blog Post",
        ondelete='set null',
        help="The resulting blog post created by the agent"
    )
    
    target_blog_id = fields.Many2one(
        'blog.blog',
        string="Target Blog",
        required=True,
        help="The blog where the post will be created"
    )
    
    target_author_id = fields.Many2one(
        'res.partner',
        string="Author",
        help="The author for the generated blog post"
    )
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string="Language",
        required=True,
        default=lambda self: self.env.ref('base.lang_en'),
        help="The language for the generated article"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'), 
        ('done', 'Done'),
        ('error', 'Error'),
    ], string="State", required=True, default='draft', tracking=True)
    
    error_message = fields.Text(
        string="Error Details",
        tracking=True,
        help="Stores error details when task fails"
    )
    
    # Execution tracking fields
    started_at = fields.Datetime(
        string="Started At",
        help="When the task processing started"
    )
    
    completed_at = fields.Datetime(
        string="Completed At",
        help="When the task was completed"
    )
    
    duration = fields.Float(
        string="Duration (minutes)",
        compute='_compute_duration',
        store=True,
        help="Task execution duration in minutes"
    )
    
    # Agent configuration at execution time
    agent_model = fields.Char(
        string="Agent Model Used",
        help="OpenAI model used for this task"
    )
    
    agent_instructions = fields.Text(
        string="Agent Instructions Used",
        help="System instructions used for this task"
    )
    
    # Content preview fields (computed from source idea)
    source_title = fields.Char(
        string="Source Title",
        related='content_idea_id.name',
        readonly=True
    )
    
    source_summary = fields.Text(
        string="Source Summary",
        related='content_idea_id.summary',
        readonly=True
    )
    
    source_url = fields.Char(
        string="Source URL",
        related='content_idea_id.url',
        readonly=True
    )
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        """Compute task execution duration"""
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at - record.started_at
                record.duration = delta.total_seconds() / 60.0  # Convert to minutes
            else:
                record.duration = 0.0
    
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
                    "• Custom Topic AND Custom Instructions"
                ))
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-generate task name"""
        for vals in vals_list:
            if not vals.get('name'):
                if vals.get('content_idea_id'):
                    idea = self.env['sc.content.idea'].browse(vals['content_idea_id'])
                    vals['name'] = _("Blog post generation for: %s") % (idea.name or 'Untitled')
                elif vals.get('custom_topic'):
                    vals['name'] = _("Blog post generation: %s") % vals['custom_topic']
                else:
                    vals['name'] = _("Blog post generation task")
        return super().create(vals_list)
    
    def action_start_processing(self):
        """Mark task as ready for processing by cron job"""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft tasks can be started"))
            record.write({
                'state': 'draft',  # Cron will pick it up
            })
            record.message_post(body=_("Task queued for processing"))
    
    def action_retry(self):
        """Reset task to draft state for retry"""
        for record in self:
            if record.state not in ['error', 'done']:
                raise ValidationError(_("Only error or done tasks can be retried"))
            record.write({
                'state': 'draft',
                'error_message': False,
                'started_at': False,
                'completed_at': False,
                'generated_blog_post_id': False,
            })
            record.message_post(body=_("Task reset for retry"))
    
    def action_view_blog_post(self):
        """View the generated blog post"""
        self.ensure_one()
        if not self.generated_blog_post_id:
            raise ValidationError(_("No blog post has been generated yet"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Blog Post'),
            'res_model': 'blog.post',
            'res_id': self.generated_blog_post_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _mark_in_progress(self):
        """Mark task as in progress"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'started_at': fields.Datetime.now(),
            'error_message': False,
        })
        self.message_post(body=_("Content generation started"))
    
    def _mark_done(self, blog_post_id):
        """Mark task as completed successfully"""
        self.ensure_one()
        self.write({
            'state': 'done',
            'completed_at': fields.Datetime.now(),
            'generated_blog_post_id': blog_post_id,
        })
        self.message_post(body=_("Content generation completed successfully"))
    
    def _mark_error(self, error_message):
        """Mark task as failed with error message"""
        self.ensure_one()
        self.write({
            'state': 'error',
            'error_message': error_message,
            'completed_at': fields.Datetime.now(),
        })
        self.message_post(body=_("Content generation failed: %s") % error_message)
