# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BlogPostTranslationWizard(models.TransientModel):
    _name = 'blog.post.translation.wizard'
    _description = 'Blog Post Translation Wizard'

    post_ids = fields.Many2many(
        'blog.post',
        string='Blog Posts',
        required=True,
        help="Blog posts to be sent for translation"
    )
    
    target_lang = fields.Many2one(
        'res.lang',
        string='Target Language',
        required=True,
        domain=[('active', '=', True)],
        help="Language to translate the blog posts to"
    )
    
    post_count = fields.Integer(
        string='Number of Posts',
        compute='_compute_post_count'
    )

    @api.depends('post_ids')
    def _compute_post_count(self):
        """Compute number of selected posts"""
        for wizard in self:
            wizard.post_count = len(wizard.post_ids)

    @api.onchange('target_lang')
    def _onchange_target_lang(self):
        """Validate target language selection"""
        if self.target_lang:
            # Get current user's language
            current_lang = self.env.context.get('lang', 'en_US')
            
            # Check if target language is different from current language
            if self.target_lang.code == current_lang:
                return {
                    'warning': {
                        'title': _('Same Language Warning'),
                        'message': _('You have selected the same language as the current system language. Please select a different target language for translation.')
                    }
                }

    def action_send_to_translate(self):
        """Send selected blog posts to translation service"""
        self.ensure_one()
        
        if not self.post_ids:
            raise UserError(_("Please select at least one blog post to translate."))
        
        if not self.target_lang:
            raise UserError(_("Please select a target language for translation."))
        
        # Get current user's language
        current_lang = self.env.context.get('lang', 'en_US')
        
        # Validate target language is different from source
        if self.target_lang.code == current_lang:
            raise UserError(_("Target language cannot be the same as the source language. Please select a different language."))
        
        # Check for posts already in progress
        posts_in_progress = self.post_ids.filtered(lambda p: p.translation_status == 'in_progress')
        if posts_in_progress:
            post_names = ', '.join(posts_in_progress.mapped('name'))
            raise UserError(_("The following articles are already being translated:\n%s\n\nPlease wait for the translation process to complete.") % post_names)
        
        success_count = 0
        failed_posts = []
        
        # Send each post to translation service
        for post in self.post_ids:
            try:
                post.send_to_translation_service(self.target_lang.code)
                success_count += 1
            except Exception as e:
                failed_posts.append(f"{post.name}: {str(e)}")
        
        # Prepare result message
        if success_count == len(self.post_ids):
            # All posts sent successfully
            message = _("Successfully sent %d article(s) to translation service for %s.") % (success_count, self.target_lang.name)
            notification_type = 'success'
        elif success_count > 0:
            # Some posts sent successfully, some failed
            message = _("Sent %d out of %d article(s) to translation service.\n\nFailed articles:\n%s") % (
                success_count, len(self.post_ids), '\n'.join(failed_posts)
            )
            notification_type = 'warning'
        else:
            # All posts failed
            message = _("Failed to send any articles to translation service:\n%s") % '\n'.join(failed_posts)
            notification_type = 'danger'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': notification_type,
                'message': message,
                'sticky': True if notification_type == 'danger' else False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super(BlogPostTranslationWizard, self).default_get(fields_list)
        
        # Get post IDs from context
        if 'post_ids' in fields_list:
            active_ids = self.env.context.get('active_ids', [])
            if active_ids:
                res['post_ids'] = [(6, 0, active_ids)]
        
        return res
