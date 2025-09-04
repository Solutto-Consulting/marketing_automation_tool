# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ScTranslateBlogPostWizard(models.TransientModel):
    """Wizard for initiating blog post translations"""
    
    _name = 'sc.translate.blog.post.wizard'
    _description = 'Blog Post Translation Wizard'
    
    target_lang_id = fields.Many2one(
        'res.lang',
        string='Target Language',
        required=True,
        domain=[('website_published', '=', True)],
        help="Select the target language for translation"
    )
    
    system_instructions = fields.Text(
        string='AI Instructions',
        placeholder="Optional: Provide specific tone, style, or formatting instructions...",
        help="Optional instructions to guide the AI's translation approach"
    )
    
    blog_post_ids = fields.Many2many(
        'blog.post',
        string='Selected Blog Posts',
        help="Blog posts to be translated"
    )
    
    blog_post_count = fields.Integer(
        string='Number of Posts',
        compute='_compute_blog_post_count',
        help="Total number of blog posts selected for translation"
    )
    
    estimated_cost = fields.Char(
        string='Estimated Cost',
        compute='_compute_estimated_cost',
        help="Estimated cost for translation based on content length"
    )
    
    @api.depends('blog_post_ids')
    def _compute_blog_post_count(self):
        """Compute the number of selected blog posts"""
        for wizard in self:
            wizard.blog_post_count = len(wizard.blog_post_ids)
    
    @api.depends('blog_post_ids', 'target_lang_id')
    def _compute_estimated_cost(self):
        """Compute estimated cost for translation"""
        for wizard in self:
            if not wizard.blog_post_ids:
                wizard.estimated_cost = _("No posts selected")
                continue
            
            # Simple estimation based on content length
            total_chars = 0
            for post in wizard.blog_post_ids:
                content_length = len(post.name or '') + len(post.content or '')
                total_chars += content_length
            
            # Rough estimation: ~4 chars per token, GPT-4o costs vary
            estimated_tokens = total_chars // 4
            
            if estimated_tokens < 1000:
                wizard.estimated_cost = _("Low cost (< $0.01)")
            elif estimated_tokens < 10000:
                wizard.estimated_cost = _("Moderate cost (< $0.10)")
            else:
                wizard.estimated_cost = _("Higher cost (> $0.10)")
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        defaults = super().default_get(fields_list)
        
        # Get selected blog posts from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids and 'blog_post_ids' in fields_list:
            defaults['blog_post_ids'] = [(6, 0, active_ids)]
        
        return defaults
    
    @api.constrains('target_lang_id')
    def _check_target_language(self):
        """Validate target language is website published"""
        for wizard in self:
            if wizard.target_lang_id and not wizard.target_lang_id.website_published:
                raise ValidationError(_(
                    "Selected language '%s' is not published on the website. "
                    "Please select a published language."
                ) % wizard.target_lang_id.name)
    
    def action_translate(self):
        """Main action to initiate translation for selected blog posts"""
        self.ensure_one()
        
        if not self.blog_post_ids:
            raise UserError(_("Please select at least one blog post to translate."))
        
        # Check OpenAI configuration
        config = self.env['res.config.settings'].get_openai_config()
        if not config.get('api_key'):
            raise UserError(_(
                "OpenAI API key is not configured. "
                "Please configure it in Settings > General Settings > AI Marketing Tools."
            ))
        
        created_tasks = []
        skipped_posts = []
        
        for post in self.blog_post_ids:
            # Check if translation is already in progress
            if post.translation_in_progress:
                skipped_posts.append(post.name)
                continue
            
            # Check for existing active task for this language
            existing_task = self.env['sc.translation.task'].search([
                ('blog_post_id', '=', post.id),
                ('target_lang_id', '=', self.target_lang_id.id),
                ('state', 'in', ['draft', 'in_progress'])
            ], limit=1)
            
            if existing_task:
                skipped_posts.append(post.name)
                continue
            
            # Create translation task
            task = self.env['sc.translation.task'].create({
                'blog_post_id': post.id,
                'target_lang_id': self.target_lang_id.id,
                'system_instructions': self.system_instructions,
                'company_id': self.env.company.id,
            })
            
            created_tasks.append(task)
            
            # Set blog post translation flag
            post.translation_in_progress = True
            
            # Log task creation
            task.message_post(
                body=_("Translation task created for '%s' to %s") % (
                    post.name, self.target_lang_id.name
                ),
                message_type='notification'
            )
        
        # Prepare result message
        messages = []
        if created_tasks:
            messages.append(_(
                "Created %d translation task(s) successfully."
            ) % len(created_tasks))
        
        if skipped_posts:
            messages.append(_(
                "Skipped %d blog post(s) that already have active translations: %s"
            ) % (len(skipped_posts), ', '.join(skipped_posts[:3])))
        
        if not created_tasks and not skipped_posts:
            raise UserError(_("No blog posts were processed. Please check your selection."))
        
        # Show notification
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Translation Tasks Created"),
                'message': ' '.join(messages),
                'type': 'success' if created_tasks else 'warning',
            }
        }
        
        # If tasks were created, also offer to view them
        if created_tasks:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Translation Tasks'),
                'res_model': 'sc.translation.task',
                'view_mode': 'list,form',
                'domain': [('id', 'in', [t.id for t in created_tasks])],
                'context': {
                    'search_default_state_draft': 1,
                },
            }
        
        return notification
    
    def action_preview_content(self):
        """Preview content that will be translated"""
        self.ensure_one()
        
        if not self.blog_post_ids:
            raise UserError(_("Please select blog posts first."))
        
        # Prepare content preview
        content_preview = []
        for post in self.blog_post_ids[:5]:  # Limit to first 5 posts
            preview = {
                'name': post.name,
                'content_length': len(post.content or ''),
                'has_subtitle': bool(post.subtitle),
                'has_meta_title': bool(post.website_meta_title),
                'has_meta_description': bool(post.website_meta_description),
            }
            content_preview.append(preview)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Content Preview'),
            'res_model': 'sc.translate.blog.post.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'preview_mode': True,
                'content_preview': content_preview,
            },
        }
