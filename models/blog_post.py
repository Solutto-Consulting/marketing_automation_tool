from odoo import fields, models

class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    translation_task_ids = fields.One2many(
        'sc.translation.task',
        'blog_post_id',
        string="Translation Tasks",
        help="All translation tasks associated with this blog post"
    )
    
    translation_in_progress = fields.Boolean(
        string="Translation in Progress",
        default=False,
        help="Indicates if a translation for this post is currently queued or in progress"
    )
    
    translation_task_count = fields.Integer(
        string="Translation Tasks Count",
        compute='_compute_translation_task_count',
        store=True
    )
    
    def _compute_translation_task_count(self):
        """Compute the number of translation tasks"""
        for post in self:
            post.translation_task_count = len(post.translation_task_ids)
    
    def action_translate_with_ai(self):
        """Launch the AI translation wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Translate with AI',
            'res_model': 'sc.translate.blog.post.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_blog_post_ids': [(6, 0, self.ids)],
            },
        }
