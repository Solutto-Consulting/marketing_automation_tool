# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BlogPost(models.Model):
    """Extend blog.post with translation tracking capabilities"""
    
    _inherit = 'blog.post'
    
    # Translation tracking fields
    translation_task_ids = fields.One2many(
        'sc.translation.task', 
        'blog_post_id', 
        string='Translation Tasks',
        help="All translation tasks for this blog post"
    )
    
    translation_in_progress = fields.Boolean(
        string='Translation in Progress', 
        default=False,
        compute='_compute_translation_status',
        store=True,
        help="Indicates if there are pending or active translation tasks"
    )
    
    last_translation_date = fields.Datetime(
        string='Last Translation',
        compute='_compute_last_translation',
        help="Date of the most recent translation completion"
    )
    
    translation_task_count = fields.Integer(
        string='Translation Tasks',
        compute='_compute_translation_count',
        help="Total number of translation tasks for this blog post"
    )
    
    completed_translation_count = fields.Integer(
        string='Completed Translations',
        compute='_compute_translation_count',
        help="Number of successfully completed translations"
    )
    
    @api.depends('translation_task_ids.state')
    def _compute_translation_status(self):
        """Check if any translation task is in draft or in_progress state"""
        for record in self:
            pending_tasks = record.translation_task_ids.filtered(
                lambda t: t.state in ('draft', 'in_progress')
            )
            record.translation_in_progress = bool(pending_tasks)
    
    @api.depends('translation_task_ids.processed_date')
    def _compute_last_translation(self):
        """Get the date of the most recent completed translation"""
        for record in self:
            completed_tasks = record.translation_task_ids.filtered(
                lambda t: t.state == 'done' and t.processed_date
            )
            if completed_tasks:
                record.last_translation_date = max(completed_tasks.mapped('processed_date'))
            else:
                record.last_translation_date = False
    
    @api.depends('translation_task_ids')
    def _compute_translation_count(self):
        """Compute total and completed translation task counts"""
        for record in self:
            record.translation_task_count = len(record.translation_task_ids)
            record.completed_translation_count = len(
                record.translation_task_ids.filtered(lambda t: t.state == 'done')
            )
    
    def action_view_translation_tasks(self):
        """Open translation tasks related to this blog post"""
        self.ensure_one()
        
        action = {
            'name': _('Translation Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'sc.translation.task',
            'view_mode': 'list,form',
            'domain': [('blog_post_id', '=', self.id)],
            'context': {
                'default_blog_post_id': self.id,
                'search_default_blog_post_id': self.id,
            },
        }
        
        if len(self.translation_task_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.translation_task_ids.id,
            })
        
        return action
    
    def action_open_translation_wizard(self):
        """Open translation wizard for selected blog posts"""
        blog_post_ids = self.env.context.get('active_ids', [])
        if not blog_post_ids:
            blog_post_ids = self.ids
        
        return {
            'name': _('Translate Blog Posts'),
            'type': 'ir.actions.act_window',
            'res_model': 'sc.translate.blog.post.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_blog_post_ids': [(6, 0, blog_post_ids)],
                'active_ids': blog_post_ids,
            },
        }
    
    def reset_translation_status(self):
        """Reset translation_in_progress flag (for error recovery)"""
        for record in self:
            record.translation_in_progress = False
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Translation status has been reset for %d blog post(s).") % len(self),
                'type': 'success',
            }
        }
